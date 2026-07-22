# G3T: Gravity Aligned Coordinate Frames Simplify Pointmap Processing (arXiv preprint (2026-05))

![g3t — architecture](https://arxiv.org/html/2605.27372v1/x3.png)

_Model architecture (원논문 Fig. 3)_

## 📋 Overview

- **Authors**: Bharath Raj Nagoor Kani, Noah Snavely
- **Institution**: Cornell University
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.27372) | [Project Page](https://g3t-paper.github.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: Fine-tunes VGGT to predict pointmaps in upright, gravity-aligned coordinate frames instead of camera-centric ones, reducing the rotation needed to relate pointmaps to a 1-DoF yaw and enabling a more robust submap-based reconstruction pipeline (G3T-Long).

## 🎯 Key Contributions

1. **Gravity-aligned pointmap prediction**: Instead of predicting pointmaps in the camera frame of the first image (as VGGT does), G3T predicts them in an upright, gravity-aligned frame that shares a common vertical (y) axis across viewpoints.
2. **Reduced rotational degrees of freedom**: Camera-frame pointmaps are related by a 7-DoF `Sim(3)` pose; gravity-aligned pointmaps are related by a 5-DoF `Sim_y(3)` pose whose rotation is restricted to a 1-DoF rotation about the y-axis (see Figure 2).
3. **G3T model**: Fine-tuned from the open-source VGGT with a modified point head (outputs gravity-frame pointmaps) plus two new camera heads — a local camera head (gravity-to-camera rotation + intrinsics) and a relative camera head (1-DoF relative yaw + translation).
4. **GA-Procrustes**: A gravity-aligned variant of Procrustes alignment (Algorithm 2) that constrains rotation to the xz-plane, producing a 5-DoF `Sim_y(3)` pose.
5. **G3T-Long**: A submap-based incremental 3D reconstruction pipeline extending VGGT-Long, restricting chunk alignment and global optimization to `Sim_y(3)` for reduced drift.

## 🔧 Technical Details

### Coordinate systems

A camera-frame pointmap `X^C` relates to a gravity-aligned (upright) pointmap `X^G` via roll and pitch rotations that make the y-axis gravity-aligned: `X^G = Rx Rz X^C`, where `Rz` and `Rx` are roll and pitch rotations. Applying only roll and pitch (not yaw) uniquely determines a gravity-aligned frame for a given image; the gravity frame shares the same origin as the camera frame.

### Architecture (builds on VGGT)

G3T keeps VGGT's aggregator, depth head, and point head architectures unchanged, with two key modifications (Figure 3):

- **Point head**: Now outputs pointmaps in the gravity frame of the first image `X^{G1} = {X_i^{G1}}` rather than its camera frame.
- **Local camera head**: Outputs `G^l = {G_i^l}` with `G_i^l ∈ R^6` — a rotation quaternion `q_i^l ∈ R^4` (gravity-to-camera rotation) and field of view `f_i^l ∈ R^2` (intrinsics).
- **Relative camera head**: Outputs `G^r = {G_i^r}` with `G_i^r ∈ R^5` — rotation parameters `q_i^r ∈ R^2` (1-DoF relative yaw w.r.t. the first frame; the y and w quaternion components) and translation `t_i^r ∈ R^3`. Both new heads are initialized from VGGT's pre-trained camera head. The track head is ignored.

### GA-Procrustes and submap reconstruction

Standard Procrustes (Algorithm 1) yields a 7-DoF `Sim(3)` pose `π(s, R, t)`. GA-Procrustes (Algorithm 2) projects points to the xz-plane before SVD and re-lifts the result as a y-axis rotation, yielding a 5-DoF `Sim_y(3)` pose `π_y(s, R_y, t)`. G3T-Long replaces Procrustes with GA-Procrustes in chunk alignment (Eq. 3) and redefines VGGT-Long's global optimization over `sim_y(3)` — the 5-dimensional Lie algebra of `Sim_y(3)`, reduced from the 7-dimensional `sim(3)` (Eq. 4).

### Training

- Fine-tune the **entire** VGGT architecture (no weights frozen), using the same losses as VGGT but with gravity-aligned ground-truth points; predicted and ground-truth pointmaps are normalized independently within each batch (as in DUSt3R).
- **Compute**: 8 A100 GPUs, 40 epochs, 1000 data samples per epoch (~1 week).
- **Batching**: 2–12 views per scene, max 96 images per GPU, gradient accumulation of 4, cosine LR schedule starting at 1e-6 after 1 warmup epoch.
- **Datasets (fine-tuning)**: MegaDepth, Hypersim, ARKitScenes, DL3DV, TartanAir — gravity-aligned via COLMAP's `model_orientation_aligner` where scenes are not naturally upright.

### Camera-to-gravity estimation and submap hyperparameters

- Camera-to-gravity rotation is estimated two ways: **Local Head** (directly from `G^l`) and **Procrustes** (on pointmap outputs). Procrustes-based camera-to-gravity uses a RANSAC loop of 5,000 iterations sampling 50,000 corresponding points from the top 50% by joint confidence, with inliers defined as L2 error < 0.05.
- Submap reconstruction: maximum chunk size 25 frames, 7 overlapping frames between adjacent chunks, loop chunk size 3.

## 📊 Results

### Camera-to-gravity rotation estimation

원논문 Table 1. Rotation error `R_err` (degrees, ↓), Mean/Median across 1/4/8 input views, on three datasets unseen during training. Baseline is GeoCalib (multi-image optimization).

| Dataset | Method     | 1V Mean ↓ | 1V Med ↓ | 4V Mean ↓ | 4V Med ↓ | 8V Mean ↓ | 8V Med ↓ |
| ------- | ---------- | --------- | -------- | --------- | -------- | --------- | -------- |
| 7Scenes | GeoCalib   | 6.78      | 3.07     | 6.60      | 2.79     | 6.56      | 2.75     |
| 7Scenes | Procrustes | 2.00      | 1.73     | 1.87      | 1.59     | 1.88      | 1.64     |
| 7Scenes | Local Head | 1.92      | 1.68     | 1.78      | 1.54     | 1.78      | 1.49     |
| NRGBD   | GeoCalib   | 2.61      | 1.91     | 2.28      | 1.50     | 2.19      | 1.30     |
| NRGBD   | Procrustes | 1.47      | 0.71     | 1.32      | 0.60     | 1.26      | 0.50     |
| NRGBD   | Local Head | 1.33      | 0.63     | 1.21      | 0.46     | 1.13      | 0.40     |
| ETH3D   | GeoCalib   | 2.24      | 0.73     | 2.22      | 0.71     | 2.21      | 0.72     |
| ETH3D   | Procrustes | 1.96      | 1.08     | 1.95      | 1.00     | 1.85      | 1.03     |
| ETH3D   | Local Head | 1.62      | 0.60     | 1.11      | 0.55     | 1.05      | 0.57     |

G3T-based methods (Local Head in particular) outperform GeoCalib on most metrics; the paper notes the 1-view mean error on 7Scenes and NRGBD is reduced by more than half. One exception recorded in the source: at 1 view on ETH3D, GeoCalib's median (0.73) is lower than Procrustes' (1.08), though Local Head (0.60) is still better. The full `R_acc` @1°/@2°/@5° columns exist in Table 1 but are not reproduced here.

### Multi-view pointmap errors

원논문 Table 2. Structure metrics on three unseen datasets. ACC ↓, COMP ↓, NC ↑. Subscript P = pointmaps from the point head, D = pointmaps by unprojecting depth with estimated cameras.

| Model | 7Sc ACC ↓ | 7Sc COMP ↓ | 7Sc NC ↑ | NR ACC ↓ | NR COMP ↓ | NR NC ↑ | ETH ACC ↓ | ETH COMP ↓ | ETH NC ↑ |
| ----- | --------- | ---------- | -------- | -------- | --------- | ------- | --------- | ---------- | -------- |
| VGGTP | 0.029     | 0.034      | 0.796    | 0.024    | 0.019     | 0.921   | 0.191     | 0.191      | 0.890    |
| VGGTD | 0.031     | 0.032      | 0.753    | 0.022    | 0.018     | 0.913   | 0.209     | 0.174      | 0.880    |
| G3TP  | 0.028     | 0.032      | 0.793    | 0.026    | 0.021     | 0.907   | 0.188     | 0.181      | 0.892    |
| G3TD  | 0.026     | 0.029      | 0.780    | 0.026    | 0.021     | 0.900   | 0.194     | 0.165      | 0.882    |

G3T retains structure quality comparable to VGGT while adding uprightness (some values favor VGGT, e.g. NRGBD ACC/COMP/NC).

### Submap reconstruction on TUM RGBD — pose metrics

원논문 Table 3. Absolute pose error per chunk in each model's ambient frame (camera frame for VGGT-Long, gravity frame for G3T-Long). APE_R (rotation, degrees ↓), APE_t (translation, metres ↓), δy (median vertical-translation error, metres ↓). N = number of overlapping chunks.

| Sequence (N)   | VGGT-Long APE_R ↓ | G3T-Long APE_R ↓ | VGGT-Long APE_t ↓ | G3T-Long APE_t ↓ | VGGT-Long δy ↓ | G3T-Long δy ↓ |
| -------------- | ----------------- | ---------------- | ----------------- | ---------------- | -------------- | ------------- |
| fr1/360 (8)    | 16.320            | 19.309           | 0.050             | 0.056            | 0.018          | 0.009         |
| fr1/desk (6)   | 2.313             | 1.434            | 0.025             | 0.012            | 0.005          | 0.008         |
| fr1/desk2 (7)  | 1.553             | 5.192            | 0.037             | 0.031            | 0.009          | 0.015         |
| fr1/room (15)  | 4.276             | 3.502            | 0.179             | 0.178            | 0.029          | 0.033         |
| fr1/plant (13) | 2.963             | 1.429            | 0.053             | 0.036            | 0.018          | 0.016         |
| fr1/teddy (16) | 4.732             | 1.948            | 0.083             | 0.056            | 0.045          | 0.016         |
| fr3/loh1 (28)  | 4.289             | 3.964            | 0.326             | 0.170            | 0.160          | 0.023         |
| fr2/ps1 (24)   | 5.924             | 3.482            | 0.444             | 0.255            | 0.224          | 0.032         |
| fr2/ps21 (18)  | 13.845            | 3.512            | 0.553             | 0.235            | 0.358          | 0.032         |
| fr2/ps31 (25)  | 15.228            | 6.381            | 0.947             | 0.220            | 0.368          | 0.029         |

G3T-Long generally lowers APE_R and APE_t and shows much smaller, more stable δy (vertical drift). Losses are recorded too: on fr1/360 and fr1/desk2 G3T-Long has higher APE_R, and fr1/360 has higher APE_t. (`loh` = long_office_household, `ps` = pioneer_slam.)

### Submap reconstruction on TUM RGBD — structure metrics

원논문 Table 4. ACC ↓, COMP ↓, NC ↑, same 10 sequences.

| Sequence (N)   | VGGT-Long ACC ↓ | G3T-Long ACC ↓ | VGGT-Long COMP ↓ | G3T-Long COMP ↓ | VGGT-Long NC ↑ | G3T-Long NC ↑ |
| -------------- | --------------- | -------------- | ---------------- | --------------- | -------------- | ------------- |
| fr1/360 (8)    | 0.057           | 0.043          | 0.071            | 0.058           | 0.701          | 0.714         |
| fr1/desk (6)   | 0.009           | 0.009          | 0.012            | 0.011           | 0.628          | 0.616         |
| fr1/desk2 (7)  | 0.014           | 0.013          | 0.016            | 0.015           | 0.619          | 0.606         |
| fr1/room (15)  | 0.046           | 0.040          | 0.043            | 0.035           | 0.664          | 0.662         |
| fr1/plant (13) | 0.032           | 0.024          | 0.041            | 0.033           | 0.619          | 0.621         |
| fr1/teddy (16) | 0.028           | 0.021          | 0.044            | 0.036           | 0.594          | 0.602         |
| fr3/loh1 (28)  | 0.064           | 0.024          | 0.044            | 0.021           | 0.606          | 0.647         |
| fr2/ps1 (24)   | 0.111           | 0.059          | 0.048            | 0.036           | 0.663          | 0.705         |
| fr2/ps21 (18)  | 0.196           | 0.069          | 0.140            | 0.067           | 0.700          | 0.731         |
| fr2/ps31 (25)  | 0.272           | 0.084          | 0.201            | 0.068           | 0.678          | 0.748         |

G3T-Long outperforms VGGT-Long on structure metrics in most cases (a few NC values favor VGGT-Long, e.g. fr1/desk, fr1/desk2).

### Supplementary results (not tabulated here)

- **Table 5**: Camera-to-gravity results on held-out Hypersim and TartanAir scenes (synthetic, naturally gravity-aligned, not processed with `model_orientation_aligner`); the paper reports trends consistent with Table 1.
- **Tables 6–7**: Depthmap-unprojection variants of Tables 3–4; the paper reports trends consistent with the point-head results.
- **Figure 8**: Effect of number of overlapping frames (O=3/7/15) on pose and structure metrics, averaged over the 10 sequences — 그림 8, 수치 미인쇄 (plotted only).

## 💡 Insights & Impact

- **Coordinate frame as a design choice**: The paper argues the near-universal choice of the first camera's frame is convenient but not optimal; gravity-aligned frames resolve the "first image defines the frame" asymmetry by agreeing on a shared vertical axis.
- **Structure priors reduce the alignment problem**: Restricting inter-pointmap rotation from 3-DoF to 1-DoF (yaw) makes chunk alignment and global optimization more robust and reduces drift, especially vertical drift (δy).
- **General, not VGGT-specific**: While instantiated on VGGT and VGGT-Long, the authors state gravity-aligned frames can be applied to other camera-centric methods.
- **Downstream readiness**: Upright predictions are natively suitable for visualization or simulation without extra post-processing, and the authors suggest tasks favoring uprightness (physically based simulation, spatial reasoning) may benefit.
- **Limitations**: G3T can fail on scenes with ambiguous structural cues — e.g. close-up images of floors/walls, or horizontally rotated images of vertically-aligned objects (Figure 5).

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The base model G3T fine-tunes; provides the aggregator, depth head, and point head, and the camera-centric pointmap prediction G3T reframes.
- **[DUSt3R](dust3r.md)**: Introduced pixel-aligned pointmap prediction and the first-camera-frame convention; G3T follows its independent per-batch pointmap normalization.
- **[MASt3R](mast3r.md)**: Cited as follow-up extending pointmap prediction to metric space.
- **[π³ (pi3)](../reconstruction/pi3.md)**: Cited as achieving input-ordering invariance but still predicting in an arbitrary frame that does not exploit natural scene priors — contrasted with G3T's world-centric frame.
- **[Fast3R](../reconstruction/fast3r.md)**: Cited among direct feed-forward multi-view prediction methods.
- **VGGT-Long** (arXiv 2507.16443, not in this collection): The chunk-based long-sequence pipeline that G3T-Long extends with `Sim_y(3)`-constrained alignment.

## 📚 Key Takeaways

1. **Gravity, not the first camera, defines the frame**: G3T predicts upright pointmaps, cutting the rotation relating pointmaps from a 7-DoF `Sim(3)` to a 5-DoF `Sim_y(3)` (1-DoF yaw).
2. **Cheap to obtain**: Realized by fine-tuning the entire open-source VGGT (8 A100s, 40 epochs, ~1 week) with two redesigned camera heads and a gravity-frame point head.
3. **Better camera-to-gravity estimation**: The Local Head beats the GeoCalib baseline on most metrics, more than halving 1-view mean rotation error on 7Scenes and NRGBD (Table 1).
4. **More robust long reconstruction**: G3T-Long generally improves TUM RGBD pose (Table 3) and structure metrics (Table 4) over VGGT-Long, with markedly lower vertical drift — while the paper honestly records the sequences where it does not.
5. **A general idea**: Gravity alignment is presented as applicable to other camera-centric pointmap methods, not just VGGT.

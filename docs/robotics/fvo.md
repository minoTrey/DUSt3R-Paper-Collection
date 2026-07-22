# FVO: Fast Visual Odometry with Transformers (arXiv preprint)

![fvo — architecture](https://arxiv.org/html/2510.03348v3/figures/teaser.png)

_Fast Visual Odometry Pipeline (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Vladimir Yugay, Duy-Kien Nguyen, Theo Gevers, Cees G. M. Snoek, Martin R. Oswald
- **Institution**: University of Amsterdam
- **Venue**: arXiv preprint (2025-10)
- **Note**: The publication venue could not be confirmed from any primary source (GitHub badge, OpenReview, CVF openaccess, or arXiv comment). This entry should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2510.03348) | [Project Page](https://vladimiryugay.github.io/fvo)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: Recasts monocular visual odometry as direct relative pose regression with a factorized time–space transformer, trained on camera poses alone, with confidence-weighted aggregation over overlapping windows replacing bundle adjustment entirely.

## 🎯 Key Contributions

1. **No bundle adjustment, no calibration**: The pipeline regresses relative poses directly, removing both post-optimization and the requirement for camera intrinsics.
2. **Metric scale from data**: Because the model is trained on pose supervision across diverse datasets rather than inheriting a frozen scale-ambiguous 3D backend, it estimates trajectories in metric space — the paper reports unaligned ATE precisely to make this checkable.
3. **Self-supervised confidence**: Heteroscedastic uncertainty gives per-prediction rotation and translation confidences learned without confidence labels.
4. **Confidence-aware inference module**: Overlapping windows produce multiple estimates of the same relative pose, fused by a weighted Fréchet mean on SO(3) for rotation and a weighted average for translation.
5. **Speed**: Almost 2× faster than the fastest baselines, measured across all ScanNet videos on an NVIDIA RTX 3090.

## 🔧 Technical Details

### Architecture

A frozen CroCo backbone trained within the DUSt3R framework (300M parameters, patched with flash-attention) extracts per-image tokens. A decoder of L identical layers applies, in order: multi-head **temporal** attention (across frames at the same spatial location), multi-head **spatial** attention (within each frame), and a feed-forward network. Learnable camera embeddings are concatenated to the image features and propagated through the spatial attention layers only — injecting them into temporal attention was found to degrade performance.

### Pose head

A single linear projection on the camera embeddings outputs a 14-dimensional vector per consecutive frame pair: a 3×3 rotation matrix, a 3-vector translation, and two confidence scalars `c_R, c_t`. The raw rotation is projected onto SO(3) by solving the special orthogonal Procrustes problem via SVD. Translations are normalized using training-set mean and standard deviation.

### Uncertainty-aware loss

The rotation loss is geodesic on SO(3); the translation loss is L1. They are combined with heteroscedastic uncertainty:

```text
L = L_rot·exp(−c_R) + c_R + L_trans·exp(−c_t) + c_t
```

The paper explicitly reports that DUSt3R's per-pixel confidence formulation was detrimental to pose learning, motivating this alternative.

### Inference aggregation

A video of N frames is decomposed into overlapping windows of size K. Confidences become normalized weights `w̃ ∝ exp(−c)`; the fused rotation is the weighted Fréchet mean under geodesic distance and the fused translation the weighted mean. The global trajectory is then sequential composition of fused relative transforms.

### Training

12 alternating time–space attention blocks (200M parameters), 8 input views at 224×224, AdamW, 250 epochs, cosine schedule with initial LR 1e-5 and 30-epoch warmup. 5 days on 12 NVIDIA RTX H100 GPUs. Training data: ARKitScenes (primary), ScanNet, 7-Scenes, TartanAir, and KITTI. TUM RGB-D is held out entirely and used zero-shot.

## 📊 Results

### Pose estimation accuracy

원논문 Table 1. ATE is unaligned; ATE_aligned applies rigid alignment and scale correction. ✗ marks failure.

| Method                        | ARKit ATE ↓ | ARKit ATE_al ↓ | ScanNet ATE ↓ | ScanNet ATE_al ↓ |
| ----------------------------- | ----------- | -------------- | ------------- | ---------------- |
| _Requires calibration and BA_ |             |                |               |                  |
| ORB-SLAM3                     | 2.58        | 1.08           | 1.91          | 1.07             |
| DPVO                          | 5.48        | 0.49           | 1.75          | **0.17**         |
| LeapVO                        | 28.31       | 0.89           | 10.84         | 0.74             |
| _No calibration or BA_        |             |                |               |                  |
| TSFormer                      | 285.22      | 141.34         | 285.22        | 105.21           |
| CUT3R                         | 2.42        | 0.67           | 4.85          | 0.38             |
| VGGT                          | 2.94        | 2.26           | 1.56          | 1.08             |
| MASt3R-SLAM-VO                | 0.60        | 0.28           | 0.99          | 0.22             |
| FVO (Ours)                    | **0.54**    | **0.26**       | **0.34**      | **0.16**         |

| Method         | KITTI ATE ↓ | KITTI ATE_al ↓ | TUM ATE ↓ | TUM ATE_al ↓ |
| -------------- | ----------- | -------------- | --------- | ------------ |
| ORB-SLAM3      | 217.06      | 80.81          | 1.65      | 0.80         |
| DPVO           | 194.55      | 9.74           | 0.94      | **0.10**     |
| LeapVO         | 211.80      | 48.86          | ✗         | ✗            |
| TSFormer       | 140.10      | 15.77          | 200.87    | 0.82         |
| CUT3R          | 112.36      | 17.92          | 0.51      | 0.87         |
| VGGT           | 205.67      | 45.07          | 1.61      | 1.05         |
| MASt3R-SLAM-VO | ✗           | ✗              | 1.21      | 0.83         |
| FVO (Ours)     | **50.31**   | **8.47**       | **0.47**  | 0.19         |

TUM is zero-shot for FVO (and not in any baseline's training set). FVO wins unaligned ATE on all four datasets, but **loses aligned ATE to DPVO on TUM (0.19 vs 0.10)** and on ScanNet DPVO is very close (0.17 vs 0.16).

### Inference module ablation

원논문 Table 2. Small FVO variant, ScanNet.

| Method            | ATE [m] ↓ |
| ----------------- | --------- |
| DUSt3R Confidence | 1.33      |
| No Confidence     | 1.21      |
| Ours              | **1.04**  |

### Attention ablation

원논문 Table 3. T/S = time–space attention; CamTok = camera-token integration; PF = per-frame tokens.

| Method              | ATE [m] ↓ |
| ------------------- | --------- |
| Full attn.          | 1.41      |
| T/S + CamTok (PF)   | 1.11      |
| T/S + CamTok (T+S)  | 1.08      |
| T/S + CamTok (Ours) | **1.04**  |

The paper reports the chosen formulation at **163 GFLOPs vs 380 GFLOPs** for the full-attention baseline.

### Rotation representation ablation

원논문 Table 4.

| Method             | ATE [m] ↓ |
| ------------------ | --------- |
| Euler angles       | 1.23      |
| Quaternion         | 1.19      |
| Plücker rays       | 1.17      |
| 6D                 | 1.12      |
| SO(3) Proj. (Ours) | **1.04**  |

### Backbone ablation

원논문 Table 5. All backbones are ViT-Large, ~300M parameters.

| Method         | ATE [m] ↓ |
| -------------- | --------- |
| DINOv2         | 1.67      |
| DINOv3         | 1.53      |
| DINOv2_VGGT    | 1.31      |
| CroCoV2        | 1.30      |
| CroCoV2_DUSt3R | **1.04**  |

### Runtime and scaling

Runtime is reported only as Figure 4 (a plot with no printed values), measured over all ScanNet videos on an NVIDIA RTX 3090 with VGGT's depth, pointmap, and tracking heads disabled for fairness. The paper's stated result is that FVO achieves **almost a 2× speedup** over existing methods. Scaling curves with respect to ARKit data proportion and decoder depth (Figure 6) likewise carry no printed values; the paper reports that ATE decreases monotonically in both.

## 💡 Insights & Impact

### Unaligned ATE as an honesty metric

The paper argues that reporting only Sim(3)-aligned ATE is impractical for deployment where ground truth is unavailable, and reports both. The gap between the two columns is where the scale story lives: DPVO's aligned ScanNet ATE is 0.17 but its unaligned ATE is 1.75, a ~10× discrepancy that reveals it does not recover scale. FVO's 0.34 vs 0.16 is a much smaller gap.

### Large 3D models are not visual odometry models

CUT3R and VGGT are trained on ScanNet and ARKitScenes yet drift substantially over long sequences (Table 1). They are optimized for sparse-view reconstruction, chunked into 30- and 90-frame segments here per the VGGT authors' suggestion, with poses composed sequentially. The lesson is that pose supervision on video is a different objective from dense sparse-view geometry.

### Backbone architecture, not backbone scale

Table 5 is the most interesting ablation: at matched parameter count and comparable training data, the matching-focused CroCoV2_DUSt3R encoder beats DINOv2_VGGT by a wide margin (1.04 vs 1.31). The paper concludes that architecture, not data scale, is the primary driver of pose accuracy here.

### Confidence correlates with accuracy

Stratifying test trajectories into five equal-sized confidence bins shows median translation error decreasing monotonically from the least to the most confident bin (Figure 5, no printed values), validating the self-supervised uncertainty.

### Limitations

The authors do not claim general dataset coverage. FVO is trained primarily in static environments, so dynamic settings may degrade performance.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md) — provides the CroCo-based encoder training framework; its per-pixel confidence formulation is explicitly rejected for pose learning
- [CroCo v2](../foundation/croco-v2.md) — the backbone architecture
- [VGGT](../reconstruction/vggt.md) — evaluated as a baseline; drifts over long sequences
- [CUT3R](../dynamic/cut3r.md) — evaluated as a baseline
- [MASt3R-SLAM](../reconstruction/mast3r-slam.md) — the MASt3R-SLAM-VO baseline, which suffers scale ambiguity and fails on KITTI
- [Reloc3R](../pose/reloc3r.md) — related pose-regression-from-DUSt3R-priors work

## 📚 Key Takeaways

1. **Direct pose regression can replace bundle adjustment** for monocular VO, given a strong pretrained encoder and enough pose-supervised video.
2. **Pose-only supervision widens the training pool.** No dense 3D annotation is needed, which is why FVO can train across ARKitScenes, ScanNet, 7-Scenes, TartanAir, and KITTI.
3. **The backbone choice dominates.** CroCoV2_DUSt3R beats DINOv2_VGGT at equal size — matching-oriented pretraining transfers better to pose than generic or multi-task 3D pretraining.
4. **The 2× speed claim is measured on ScanNet videos on an RTX 3090** against the fastest baselines; the underlying runtime figure exists only as a plot.
5. **FVO does not dominate everywhere** — DPVO still wins aligned ATE on TUM.

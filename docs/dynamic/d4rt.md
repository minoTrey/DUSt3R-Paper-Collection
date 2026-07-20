# D4RT: Efficiently Reconstructing Dynamic Scenes One Query at a Time (CVPR 2026)

## 📋 Overview

- **Authors**: Chuhan Zhang, Guillaume Le Moing, Skanda Koppula, Ignacio Rocco, Liliane Momeni, Junyu Xie, Shuyang Sun, Rahul Sukthankar, Joëlle K. Barral, Raia Hadsell, Zoubin Ghahramani, Andrew Zisserman, Junlin Zhang, Mehdi S. M. Sajjadi
- **Institution**: Google DeepMind, University College London, University of Oxford
- **Venue**: CVPR 2026
- **Award**: Best Paper, Oral
- **Links**: [Paper](https://arxiv.org/abs/2512.08924) | [Project Page](https://d4rt-paper.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A single encoder–decoder transformer that turns 4D reconstruction into point queries — depth, point clouds, 3D tracks, and full camera parameters are all decoded through one interface, with each query processed independently.

## 🎯 Key Contributions

1. **Query-based 4D decoding**: A query is `q = (u, v, t_src, t_tgt, t_cam)` and the decoder returns a single 3D position `P = D(q, F)`. Varying the fields of this tuple recovers point tracks, point clouds, depth maps, extrinsics, and intrinsics from one model (원논문 Table 1).
2. **Full space–time disentanglement**: The source timestep, target timestep, and camera reference frame need not coincide, so the model can express any point at any time in any frame's coordinates — including reference frames other than the first.
3. **Independent queries**: Queries do not attend to each other. This makes training cheap (only a small query subset is decoded per step) and inference trivially parallel. The authors report empirically observed major performance drops when self-attention between queries was enabled in early experiments.
4. **Dense tracking of all pixels**: Algorithm 1 uses a `T × H × W` occupancy grid so new tracks are only seeded from unvisited pixels, giving an adaptive speedup between 5–15× depending on motion complexity, versus the naive `O(T²HW)` query count.
5. **Broad empirical gains**: State-of-the-art on TAPVid-3D tracking, video depth, point cloud reconstruction, and camera pose across the paper's benchmark suite (see Results for the specific cells where it does not lead).

## 🔧 Technical Details

### Architecture

- **Encoder**: ViT-g variant, 40 layers, spatio-temporal patch size 2×16×16, with interleaved local frame-wise and global self-attention layers. Produces a Global Scene Representation `F = E(V) ∈ R^{N×C}` that is computed once and then held fixed.
- **Decoder**: an 8-layer cross-attention transformer. Parameter counts are 1 B for the encoder and 144 M for the decoder.
- **Aspect ratio**: video is resized to a fixed square resolution; the original aspect ratio is embedded into a separate token.

### Query construction

A query token adds the Fourier feature embedding of `(u, v)` to learned discrete timestep embeddings for `t_src`, `t_tgt`, and `t_cam`. Crucially, the query is also augmented with an embedding of the local **9×9 pixel RGB patch** centered at `(u, v)`. The paper attributes dramatic gains to this patch (Table 7) — it supplies low-level cues that most related work handles with specialized modules such as DPT skip connections.

### Deriving cameras from queries

Extrinsics and intrinsics are not separate heads. For relative pose between frames `i, j`, the model builds two query sets on a coarse `(h, w)` grid:

```text
q_{i,k} = (u_k, v_k, i, i, i)     q_{j,k} = (u_k, v_k, i, i, j)
```

These describe the same 3D points in two reference frames, so the rigid transform follows from Umeyama's algorithm (a 3×3 SVD). Intrinsics assume a pinhole model with principal point at (0.5, 0.5) and take the median over grid estimates of `f_x = p_z(u − 0.5)/p_x`, `f_y = p_z(v − 0.5)/p_y`. Distorted models (e.g. fisheye) can be added with a non-linear refinement step.

### Training

- Primary loss: L1 on normalized 3D positions, with both prediction and target normalized by their mean depths and passed through `sign(x)·log(1+|x|)` to dampen far points.
- Auxiliary losses: L1 on 2D image-space coordinates, cosine similarity on 3D surface normals, binary cross-entropy on target-point visibility, L1 on point motion, plus a `−log(c)` confidence penalty.
- Setup: 48-frame clips at 256×256, 2048 random queries per step, 500 k steps with AdamW, local batch size 1 across 64 TPU chips, totaling just over 2 days. Implemented in Kauldron.
- Training mixture: BlendedMVS, Co3Dv2, Dynamic Replica, Kubric, MVS-Synth, PointOdyssey, ScanNet++, ScanNet, TartanAir, VirtualKitti, Waymo Open, plus internal datasets.

## 📊 Results

### 4D reconstruction and tracking on TAPVid-3D

원논문 Table 4, camera-coordinate 3D tracking. Upper block is without ground-truth intrinsics, lower block with them.

| w/ GT intrin. | Method                  | DriveTrack AJ ↑ | DriveTrack APD3D ↑ | ADT AJ ↑  | ADT APD3D ↑ | PStudio AJ ↑ | PStudio APD3D ↑ |
| ------------- | ----------------------- | --------------- | ------------------ | --------- | ----------- | ------------ | --------------- |
| ✗             | CoTracker3 + UniDepthV2 | 0.038           | 0.062              | 0.102     | 0.146       | 0.119        | 0.176           |
| ✗             | CoTracker3 + VGGT       | 0.129           | 0.189              | 0.132     | 0.190       | 0.045        | 0.070           |
| ✗             | SpatialTrackerV2        | 0.064           | 0.100              | 0.260     | 0.342       | 0.097        | 0.152           |
| ✗             | **D4RT**                | **0.257**       | **0.345**          | 0.240     | 0.319       | **0.138**    | **0.186**       |
| ✓             | CoTracker3 + UniDepthV2 | 0.147           | 0.225              | 0.173     | 0.254       | 0.205        | 0.311           |
| ✓             | CoTracker3 + VGGT       | 0.245           | 0.342              | 0.175     | 0.250       | 0.215        | 0.318           |
| ✓             | DELTA                   | 0.170           | 0.238              | 0.199     | 0.258       | 0.175        | 0.261           |
| ✓             | SpatialTrackerV2        | 0.195           | 0.275              | 0.303     | 0.404       | 0.175        | 0.270           |
| ✓             | **D4RT**                | **0.304**       | **0.410**          | **0.307** | **0.408**   | **0.372**    | **0.498**       |

**Honest reading**: without ground-truth intrinsics, D4RT does _not_ lead on ADT — SpatialTrackerV2 is ahead on AJ (0.260 vs 0.240) and APD3D (0.342 vs 0.319). D4RT's Occlusion Accuracy on ADT (0.926) is also below the 0.936 shared by the CoTracker3 rows and SpatialTrackerV2. With ground-truth intrinsics D4RT leads every cell shown.

원논문 Table 4, world-coordinate 3D tracking. PStudio is omitted by the authors because it has no camera motion.

| w/ GT intrin. | Method            | DriveTrack APD3D ↑ | DriveTrack L1 ↓ | ADT APD3D ↑ | ADT L1 ↓  |
| ------------- | ----------------- | ------------------ | --------------- | ----------- | --------- |
| ✗             | St4RTrack         | 0.020              | 0.499           | 0.062       | 0.839     |
| ✗             | CoTracker3 + VGGT | 0.205              | 0.170           | 0.192       | 0.736     |
| ✗             | SpatialTrackerV2  | 0.101              | 0.139           | **0.336**   | 0.238     |
| ✗             | **D4RT**          | **0.373**          | **0.020**       | 0.319       | **0.096** |
| ✓             | CoTracker3 + VGGT | 0.292              | 0.160           | 0.234       | 0.755     |
| ✓             | SpatialTrackerV2  | 0.201              | 0.117           | 0.378       | 0.263     |
| ✓             | **D4RT**          | **0.470**          | **0.017**       | **0.398**   | **0.093** |

Again, in the no-intrinsics setting SpatialTrackerV2 edges D4RT on ADT APD3D (0.336 vs 0.319), though D4RT more than halves the L1 error there.

### Video depth and point map estimation

원논문 Table 5. `S` = scale-only alignment, `SS` = scale-and-shift alignment.

| Method           | Sintel PC L1 ↓ | ScanNet PC L1 ↓ | Sintel AbsRel (S) ↓ | Sintel AbsRel (SS) ↓ | ScanNet AbsRel (S) ↓ | ScanNet AbsRel (SS) ↓ |
| ---------------- | -------------- | --------------- | ------------------- | -------------------- | -------------------- | --------------------- |
| MegaSaM          | 1.531          | 0.072           | 0.342               | 0.249                | 0.050                | 0.047                 |
| VGGT             | 1.582          | 0.063           | 0.318               | 0.247                | 0.044                | 0.040                 |
| MapAnything      | 1.718          | 0.064           | 0.397               | 0.306                | 0.043                | 0.035                 |
| SpatialTrackerV2 | 1.375          | 0.036           | 0.209               | 0.175                | 0.027                | 0.025                 |
| π³               | 1.139          | 0.030           | 0.241               | 0.163                | 0.021                | 0.019                 |
| **D4RT**         | **0.768**      | **0.028**       | **0.171**           | **0.148**            | **0.020**            | **0.018**             |

원논문 Table 5, remaining depth benchmarks.

| Method           | KITTI AbsRel (S) ↓ | KITTI AbsRel (SS) ↓ | Bonn AbsRel (S) ↓ | Bonn AbsRel (SS) ↓ |
| ---------------- | ------------------ | ------------------- | ----------------- | ------------------ |
| MegaSaM          | 0.109              | 0.101               | 0.056             | 0.056              |
| VGGT             | 0.094              | 0.067               | 0.055             | 0.051              |
| MapAnything      | 0.096              | 0.090               | 0.076             | 0.049              |
| SpatialTrackerV2 | 0.075              | 0.064               | 0.042             | 0.978              |
| π³               | 0.055              | 0.053               | **0.033**         | **0.032**          |
| **D4RT**         | 0.055              | **0.051**           | 0.036             | 0.036              |

**Honest reading**: D4RT beats VGGT on every depth and point-cloud cell in Table 5. Against π³ it wins on Sintel, ScanNet, and KITTI (SS), **ties** π³ on KITTI AbsRel (S) at 0.055, and **loses** on both Bonn columns (0.036 vs 0.033 scale-only, 0.036 vs 0.032 scale-and-shift). The paper's own wording is "top-tier performance," not a clean sweep.

### Camera pose estimation

원논문 Table 6. Sintel uses the 14-sequence subset; ATE/RPE reported after Sim(3) alignment.

| Method           | Sintel ATE ↓ | Sintel RPE-T ↓ | Sintel RPE-R ↓ | ScanNet ATE ↓ | ScanNet RPE-T ↓ | ScanNet RPE-R ↓ | Re10K Pose AUC ↑ |
| ---------------- | ------------ | -------------- | -------------- | ------------- | --------------- | --------------- | ---------------- |
| MegaSaM          | 0.074        | 0.030          | **0.126**      | 0.029         | 0.016           | 0.839           | 71.0             |
| VGGT             | 0.168        | 0.056          | 0.428          | 0.016         | 0.012           | 0.316           | 70.2             |
| MapAnything      | 0.202        | 0.089          | 2.383          | 0.023         | 0.016           | 0.438           | 68.7             |
| SpatialTrackerV2 | 0.126        | 0.053          | 1.052          | 0.018         | 0.012           | 0.324           | 75.7             |
| π³               | 0.086        | 0.039          | 0.248          | 0.015         | 0.010           | **0.291**       | 78.7             |
| **D4RT**         | **0.065**    | **0.024**      | **0.126**      | **0.014**     | **0.010**       | 0.302           | **83.5**         |

**Honest reading**: D4RT beats VGGT on all seven pose cells. Against π³ it wins Sintel ATE/RPE-T/RPE-R, ScanNet ATE, and Re10K Pose AUC; it **ties** π³ on ScanNet RPE-T (0.010) and **loses** on ScanNet RPE-R (0.302 vs 0.291). It also only ties MegaSaM on Sintel RPE-R.

### 3D tracking throughput

원논문 Table 3. Maximum number of full-video 3D point tracks producible while holding a target FPS, on a single A100. For D4RT each track is `T` independent decoder queries.

| Method           | 60 FPS  | 24 FPS    | 10 FPS    | 1 FPS      |
| ---------------- | ------- | --------- | --------- | ---------- |
| DELTA            | 0       | 5         | 408       | 5,770      |
| SpatialTrackerV2 | 29      | 84        | 219       | 2,290      |
| **D4RT**         | **550** | **1,570** | **3,890** | **40,180** |

The paper states D4RT is **18–300× faster** than these methods on this benchmark.

### Speed claims stated by the paper

- Figure 3 caption: D4RT achieves **200+ FPS** pose estimation, **9× faster than VGGT** and **100× faster than MegaSaM**, with pose accuracy defined as `1 − error` averaged over ATE/RTE/RPE on Sintel and ScanNet, throughput in FPS on an A100. To make the comparison fair the authors _removed_ the baselines' decoding heads unrelated to camera estimation, making the baselines faster. Figure 3 itself is a scatter plot; beyond the caption's ratios and the "0.475"/"0.9"/"0.8"/"0.7" axis annotations, no per-method numbers are printed, so no further values are transcribed here.
- Dense tracking (Alg. 1): **5–15×** adaptive speedup over the naive approach.

### Ablations

원논문 Table 7. ViT-L model, Sintel, with and without the local appearance patch in the decoder query.

| w/ local appear. patch | AbsRel (S) ↓ | AbsRel (SS) ↓ | ATE ↓     | RPE-T ↓   | RPE-R ↓   |
| ---------------------- | ------------ | ------------- | --------- | --------- | --------- |
| ✗                      | 0.366        | 0.306         | 0.173     | 0.031     | 0.262     |
| ✓                      | **0.302**    | **0.257**     | **0.091** | **0.028** | **0.245** |

원논문 Table 9. Backbone scaling, Sintel.

| Backbone size | AbsRel (S) ↓ | AbsRel (SS) ↓ | ATE ↓     | RPE-T ↓   | RPE-R ↓   |
| ------------- | ------------ | ------------- | --------- | --------- | --------- |
| ViT-B         | 0.319        | 0.232         | 0.145     | 0.034     | 0.266     |
| ViT-L         | 0.256        | 0.214         | 0.073     | 0.027     | 0.191     |
| ViT-H         | 0.226        | 0.173         | **0.070** | 0.028     | 0.186     |
| ViT-g         | **0.191**    | **0.168**     | 0.078     | **0.026** | **0.160** |

Note that ATE is best at ViT-H (0.070) rather than ViT-g (0.078); the paper describes the improvement as "particularly in depth estimation and RPE-R."

원논문 Table 8. Auxiliary loss removal, reported as deltas from the D4RT row (AbsRel(S) 0.302, AbsRel(SS) 0.257, ATE 0.091, RPE-T 0.028, RPE-R 0.245).

| Removed loss     | ΔAbsRel (S) | ΔAbsRel (SS) | ΔATE   | ΔRPE-T | ΔRPE-R |
| ---------------- | ----------- | ------------ | ------ | ------ | ------ |
| w/o 2D position  | +0.071      | +0.063       | +0.002 | +0.002 | -0.028 |
| w/o normal       | +0.043      | +0.026       | +0.003 | +0.003 | -0.022 |
| w/o displacement | +0.011      | +0.007       | +0.011 | +0.003 | +0.007 |
| w/o visibility   | -0.003      | -0.025       | +0.012 | +0.011 | +0.022 |
| w/o confidence   | +0.002      | -0.025       | +0.126 | +0.061 | +0.115 |

The signs make the trade-off explicit: dropping the 2D-position and normal losses actually _lowers_ RPE-R while badly hurting depth, and dropping visibility improves scale-and-shift depth while degrading all three pose metrics. Confidence weighting is what dominates pose quality.

## 💡 Insights & Impact

### Why the query interface matters

The dominant feed-forward line (VGGT, π³, MapAnything) attaches a dense per-frame decoder head per task. That design pays full decoding cost even when only a handful of 3D points are needed, and it locks the output to a per-pixel grid in a fixed reference frame. D4RT's decoder is _sparse by construction_: cost scales linearly with the number of points requested, not with `T × H × W`. Training benefits too — 2048 queries per step suffice to supervise a 1 B-parameter encoder.

### Correspondence is the missing capability, not accuracy

The paper's Table 2 capability matrix argues that MegaSaM, DUSt3R, VGGT, and π³ all fail to provide dynamic correspondence at all, regardless of how accurate their static geometry is. Figure 4's qualitative comparison makes the failure concrete: MegaSaM repeats the swan across the accumulated point cloud, π³ fails to reconstruct the flower entirely, and SpatialTrackerV2 leaves gaps behind occluders because it can only track from one frame.

### Where it still trails

The honest picture from the tables is that D4RT is not uniformly ahead. SpatialTrackerV2 remains stronger on ADT when intrinsics are unknown, and π³ remains stronger on Bonn depth and marginally on ScanNet rotation error. What D4RT does deliver unambiguously is the combination — dynamic correspondence _and_ competitive static geometry _and_ an order-of-magnitude throughput advantage in the same model.

### Limitations acknowledged or implied

- The occupancy-grid speedup is data-dependent (5–15×), so worst-case dense tracking cost is not bounded tightly.
- The reported "18–300×" and "9×" ratios are measured under the paper's specific protocols (A100, baselines stripped of unrelated heads); they are not general-purpose speedup guarantees.
- Training relies on internal datasets alongside the public mixture, which complicates exact reproduction.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the global-attention encoder D4RT builds on, but with separate per-task decoder heads that D4RT replaces.
- [π³](../reconstruction/pi3.md) — the strongest pure-reconstruction baseline in Tables 5 and 6, and the one D4RT does not fully dominate.
- [DUSt3R](../foundation/dust3r.md) — the pairwise pointmap formulation that established the feed-forward paradigm.
- [MapAnything](../reconstruction/mapanything.md) — compared in Tables 5 and 6.
- [Dynamic Point Maps](../dynamic/dynamic-point-maps.md) — DPM, cited as a pairwise 3D-tracking approach D4RT contrasts with.
- [CUT3R](../dynamic/cut3r.md) — a streaming alternative in the dynamic feed-forward line.
- [MonST3R](../dynamic/monst3r.md) — earlier dynamic extension of the pointmap paradigm.
- [Any4D](../dynamic/any4d.md) — related unified 4D reconstruction work.

## 📚 Key Takeaways

1. **Decoding is the bottleneck, not encoding.** By making the decoder a per-point function rather than a per-frame head, D4RT decouples inference cost from output resolution and unlocks 40,180 full-video tracks at 1 FPS on one A100 (원논문 Table 3).
2. **One tuple, six tasks.** `(u, v, t_src, t_tgt, t_cam)` covers point tracks, point clouds, depth maps, extrinsics, and intrinsics without a single task-specific head (원논문 Table 1).
3. **A 9×9 RGB patch replaces DPT skip connections.** Table 7 shows the local appearance embedding cutting Sintel ATE from 0.173 to 0.091 — a simpler mechanism for preserving low-level detail than the usual encoder–decoder skips.
4. **The SOTA claim is broad but not total.** D4RT beats VGGT on every reported depth, point-cloud, and pose cell, but loses to π³ on Bonn depth and ScanNet RPE-R, and to SpatialTrackerV2 on ADT tracking when intrinsics are unknown.
5. **Confidence weighting carries the cameras.** The auxiliary-loss ablation shows removing the confidence term inflates Sintel ATE by +0.126 — by far the largest single effect in Table 8.

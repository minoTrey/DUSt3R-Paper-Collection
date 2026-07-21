# TrajVG: 3D Trajectory-Coupled Visual Geometry Learning (arXiv preprint (2026-02))

## 📋 Overview

- **Authors**: Xingyu Miao, Weiguang Zhao, Tao Lu, Linning Xu, Mulin Yu, Yang Long*, Jiangmiao Pang, Junting Dong\*† (\* Corresponding author, † Project lead)
- **Institution**: Durham University, University of Liverpool, Shanghai AI Lab
- **Venue**: arXiv preprint (2026-02)
- **Links**: [Paper](https://arxiv.org/abs/2602.04439) | [Project Page](https://xingy038.github.io/TrajVG/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward multi-frame reconstruction framework that makes cross-frame 3D correspondence an explicit prediction by adding a 3D tracking branch that estimates camera-coordinate trajectories, coupling sparse tracks, per-frame local point maps, and relative camera poses through bidirectional consistency and static-anchored pose objectives, with a self-supervised variant using only pseudo 2D tracks.

## 🎯 Key Contributions

1. **3D tracking as explicit correspondence**: A multi-frame reconstruction pipeline that predicts per-frame camera-coordinate 3D trajectories, elevating cross-frame correspondence from an implicit byproduct of dense regression to an explicit prediction that links per-view point maps, directly improving point-map fusion and relative pose estimation.
2. **Two complementary consistency terms**: Bidirectional trajectory–pointmap consistency with controlled gradient flow (stop-gradient routing), plus a pose consistency objective driven by static track anchors that suppresses gradients from dynamic regions, forcing outputs to agree across frames and stabilizing optimization in dynamic scenes.
3. **Semi-supervised in-the-wild training**: The same coupling constraints are reformulated into self-supervised objectives using only pseudo 2D tracks from an off-the-shelf tracker, enabling unified mixed-supervision training and improving generalization.

## 🔧 Technical Details

### Motivation

Feed-forward multi-frame reconstruction models degrade on videos with object motion. Reference-frame approaches (e.g., VGGT) anchor predictions to a fixed world reference and struggle under multiple motions, while local-frame approaches (e.g., π³) predict scale-invariant per-view point maps but fuse them solely through the estimated camera pose, which can drift and cause cross-frame misalignment (duplicated surfaces). TrajVG introduces trajectory-based 3D correspondences as geometric tie points to enforce explicit coupling.

### Method

- **Camera-coordinate trajectories**: Tracks are predicted in each frame's camera coordinate system rather than a fixed world frame. In a world frame, static points have a trivial time-invariant solution that makes tracking gradients insensitive to correspondence errors; camera-space prediction forces the branch to explain viewpoint-induced geometric changes.
- **3D tracking branch**: Conditioned on multi-frame visual features and current geometric predictions. Query points are initialized by bilinearly sampling the first-frame pointmap; the branch predicts a camera-coordinate trajectory p̂ₜ,ᵢ ∈ ℝ³ and visibility v̂ₜ,ᵢ ∈ [0,1] per frame.
- **Tracking–pointmap bidirectional consistency (L_cons)**: A Huber penalty enforces agreement between the tracked 3D point and the pointmap value at the tracked pixel. Stop-gradient splits it into two terms — one updates the pointmap branch (tracks detached), the other updates the tracking branch (samples detached) — avoiding unstable branch-chasing and degenerate averaging.
- **Camera consistency from static anchors (L_cam)**: A binary static mask (from ground-truth 3D trajectory displacement < τ_static) isolates rigid background. Reprojecting static samples into a common anchor camera frame drives pose updates only from rigid-consistent points; stop-gradient routes the first term to update only pose and the second to update only the tracked 3D points.
- **Self-supervision (L_self-sup.)**: For unlabeled videos, dense pseudo 2D tracks (e.g., from CoTracker3) sample the predicted point maps to obtain camera-frame 3D observations, reusing L_cons and the anchor consistency term. The second term of the camera objective is dropped since no pose ground truth exists.

### Training

Three-stage strategy initialized from a frozen pretrained **π³ backbone** (not trained from scratch). Stage 1 trains the 3D tracking branch on a large set of mostly static datasets (CO3DV2, TartanAir, ScanNet, ScanNet++, BlendedMVS, Waymo, etc.). Stage 2 mixes in Sekai (in-the-wild) and finetunes the backbone jointly with the point-map and camera branches. Stage 3 freezes the backbone, point-map, and camera branches and trains the confidence module and 3D tracking branch with an internal dynamic 3D tracking dataset.

## 📊 Results

TrajVG (reported as "Our"/"Ours") is evaluated on 3D tracking, camera pose, point-map reconstruction, video depth, and monocular depth. It does not win on every metric — e.g., it trails π³ on DTU point-map accuracy and on Sintel ATE/monocular-Sintel depth.

### 3D Point Tracking — TAPVid-3D (MegaSAM-lifted rows)

원논문 Table 1. AJ3D↑ / APD3D↑ / OA↑ (higher is better). "+ M" = MegaSAM depth; TrajVG's model is "Our + M". A tracking-specific variant (backbone frozen, tracking branch fine-tuned) is used.

| Method              | ADT AJ3D↑ | ADT APD3D↑ | ADT OA↑  | Drive AJ3D↑ | Drive APD3D↑ | Drive OA↑ | PStudio AJ3D↑ | PStudio APD3D↑ | PStudio OA↑ |
| ------------------- | --------- | ---------- | -------- | ----------- | ------------ | --------- | ------------- | -------------- | ----------- |
| CoTracker3 + M      | 20.4      | 30.1       | 89.8     | 14.1        | 20.3         | 88.5      | 17.4          | 27.2           | 85.0        |
| SpatialTracker + M  | 15.9      | 23.8       | 90.1     | 7.7         | 13.5         | 85.2      | 15.3          | 25.2           | 78.1        |
| SpatialTracker2 + M | 22.3      | 32.2       | 93.7     | 15.8        | 23.0         | 90.0      | 18.2          | 28.6           | 87.3        |
| DELTA + M           | 21.0      | 29.3       | 89.7     | 14.6        | 22.2         | 88.1      | 17.7          | 27.3           | 81.4        |
| TAPIP3D + M         | 21.6      | 31.0       | 90.4     | 14.6        | 21.3         | 82.2      | 18.1          | 27.7           | 85.5        |
| **Our + M**         | **23.1**  | **32.5**   | **93.8** | **17.8**    | **25.2**     | **92.2**  | **18.2**      | **28.8**       | 86.3        |

TrajVG leads most subsets; on PStudio OA it trails SpatialTracker2 + M (86.3 vs 87.3).

### Camera Pose — RealEstate10K & Co3Dv2

원논문 Table 2. RRA@30↑ / RTA@30↑ / AUC@30↑ (ratio of angular accuracy under 30° error, higher is better).

| Method | RE10K RRA@30↑ | RE10K RTA@30↑ | RE10K AUC@30↑ | Co3Dv2 RRA@30↑ | Co3Dv2 RTA@30↑ | Co3Dv2 AUC@30↑ |
| ------ | ------------- | ------------- | ------------- | -------------- | -------------- | -------------- |
| Fast3R | 99.05         | 81.86         | 61.68         | 97.49          | 91.11          | 73.43          |
| CUT3R  | 99.82         | 95.10         | 81.47         | 96.19          | 92.69          | 75.82          |
| FLARE  | 99.69         | 95.23         | 80.01         | 96.38          | 93.76          | 73.99          |
| VGGT   | 99.97         | 93.13         | 77.62         | 98.96          | 97.13          | **88.59**      |
| π³     | 99.99         | **95.62**     | 85.90         | 99.05          | **97.33**      | 88.41          |
| Our    | **99.99**     | 95.58         | **86.60**     | **99.14**      | 96.80          | 86.00          |

TrajVG sets new best AUC@30/RRA@30 on RealEstate10K and best RRA@30 on Co3Dv2, but trails on Co3Dv2 AUC@30 (86.00 vs VGGT 88.59) and RealEstate10K RTA@30 (95.58 vs π³ 95.62).

### Camera Pose — Sintel, TUM-dynamics, ScanNet

원논문 Table 3. ATE↓ / RPE trans↓ / RPE rot↓ (lower is better).

| Method | Sintel ATE↓ | Sintel RPEt↓ | Sintel RPEr↓ | TUM ATE↓  | TUM RPEt↓ | TUM RPEr↓ | ScanNet ATE↓ | ScanNet RPEt↓ | ScanNet RPEr↓ |
| ------ | ----------- | ------------ | ------------ | --------- | --------- | --------- | ------------ | ------------- | ------------- |
| Fast3R | 0.371       | 0.298        | 13.75        | 0.090     | 0.101     | 1.425     | 0.155        | 0.123         | 3.491         |
| CUT3R  | 0.217       | 0.070        | 0.636        | 0.047     | 0.015     | 0.451     | 0.094        | 0.022         | 0.629         |
| Aether | 0.189       | 0.054        | 0.694        | 0.092     | 0.012     | 1.106     | 0.176        | 0.028         | 1.204         |
| FLARE  | 0.207       | 0.090        | 3.015        | 0.026     | 0.013     | 0.475     | 0.064        | 0.023         | 0.971         |
| VGGT   | 0.167       | 0.062        | 0.491        | 0.012     | 0.010     | 0.311     | 0.035        | 0.015         | 0.382         |
| π³     | **0.074**   | 0.040        | 0.282        | 0.014     | 0.009     | 0.312     | 0.031        | 0.013         | **0.347**     |
| Our    | 0.108       | **0.038**    | **0.274**    | **0.011** | **0.008** | **0.307** | **0.030**    | **0.013**     | 0.351         |

TrajVG ranks first on TUM-dynamics across all metrics and attains lowest ATE on ScanNet and lowest Sintel RPE (trans & rot); Sintel ATE (0.108) is slightly higher than π³ (0.074).

### Point Map Estimation — DTU

원논문 Table 4. Acc.↓ / Comp.↓ (lower better), N.C.↑ (higher better); keyframes every 5 images.

| Method | Acc. Mean↓ | Acc. Med↓ | Comp. Mean↓ | Comp. Med↓ | N.C. Mean↑ | N.C. Med↑ |
| ------ | ---------- | --------- | ----------- | ---------- | ---------- | --------- |
| Fast3R | 3.340      | 1.919     | 2.929       | 1.125      | 0.671      | 0.755     |
| CUT3R  | 4.742      | 2.600     | 3.400       | 1.316      | 0.679      | 0.764     |
| FLARE  | 2.541      | 1.468     | 3.174       | 1.420      | 0.684      | 0.774     |
| VGGT   | 1.338      | 0.779     | 1.896       | 0.992      | 0.676      | 0.766     |
| π³     | **1.198**  | 0.646     | **1.849**   | 0.607      | 0.678      | 0.768     |
| Our    | 1.435      | **0.762** | 2.119       | **0.621**  | **0.678**  | **0.769** |

On DTU, TrajVG trails π³ on Acc. Mean and Comp. Mean.

### Point Map Estimation — ETH3D

원논문 Table 4. Keyframes every 5 images.

| Method | Acc. Mean↓ | Acc. Med↓ | Comp. Mean↓ | Comp. Med↓ | N.C. Mean↑ | N.C. Med↑ |
| ------ | ---------- | --------- | ----------- | ---------- | ---------- | --------- |
| Fast3R | 0.832      | 0.691     | 0.978       | 0.683      | 0.667      | 0.766     |
| CUT3R  | 0.617      | 0.525     | 0.747       | 0.579      | 0.754      | 0.848     |
| FLARE  | 0.464      | 0.338     | 0.664       | 0.395      | 0.744      | 0.864     |
| VGGT   | 0.280      | 0.185     | 0.305       | 0.182      | 0.853      | 0.950     |
| π³     | 0.194      | 0.131     | 0.210       | 0.128      | 0.883      | 0.969     |
| Our    | **0.173**  | **0.117** | **0.200**   | **0.124**  | **0.887**  | **0.970** |

TrajVG is best across all ETH3D metrics.

### Video Depth Estimation — scale alignment

원논문 Table 6. Abs Rel↓ / δ<1.25↑; per-sequence single-scale alignment.

| Method  | Sintel AbsRel↓ | Sintel δ↑ | Bonn AbsRel↓ | Bonn δ↑   | KITTI AbsRel↓ | KITTI δ↑  |
| ------- | -------------- | --------- | ------------ | --------- | ------------- | --------- |
| DUSt3R  | 0.662          | 0.434     | 0.151        | 0.839     | 0.143         | 0.814     |
| MonST3R | 0.399          | 0.519     | 0.072        | 0.957     | 0.107         | 0.884     |
| CUT3R   | 0.417          | 0.507     | 0.078        | 0.937     | 0.122         | 0.876     |
| VGGT    | 0.299          | 0.638     | 0.057        | 0.966     | 0.062         | 0.969     |
| π³      | 0.233          | 0.664     | 0.049        | 0.975     | **0.038**     | **0.986** |
| Our     | **0.220**      | **0.717** | **0.036**    | **0.979** | 0.040         | 0.984     |

### Video Depth Estimation — scale & shift alignment

원논문 Table 6. Abs Rel↓ / δ<1.25↑; per-sequence scale-and-shift alignment.

| Method | Sintel AbsRel↓ | Sintel δ↑ | Bonn AbsRel↓ | Bonn δ↑   | KITTI AbsRel↓ | KITTI δ↑  |
| ------ | -------------- | --------- | ------------ | --------- | ------------- | --------- |
| VGGT   | 0.230          | 0.678     | 0.052        | 0.969     | 0.052         | 0.968     |
| π³     | 0.210          | **0.726** | 0.043        | 0.975     | **0.037**     | **0.985** |
| Our    | **0.188**      | 0.723     | **0.037**    | **0.980** | **0.037**     | 0.983     |

TrajVG achieves lowest Abs Rel on Sintel (0.220) and Bonn (0.036) under scale-only alignment; on KITTI it ties/trails π³, and Sintel δ under scale&shift (0.723) is marginally below π³ (0.726).

### Monocular Depth Estimation

원논문 Table 7. Abs Rel↓ / δ<1.25↑; per-image scale alignment, zero-shot.

| Method  | Sintel AbsRel↓ | Sintel δ↑ | Bonn AbsRel↓ | Bonn δ↑   | KITTI AbsRel↓ | KITTI δ↑ | NYU AbsRel↓ | NYU δ↑    |
| ------- | -------------- | --------- | ------------ | --------- | ------------- | -------- | ----------- | --------- |
| MonST3R | 0.402          | 0.525     | 0.069        | 0.954     | 0.098         | 0.895    | 0.094       | 0.887     |
| CUT3R   | 0.418          | 0.520     | 0.058        | 0.967     | 0.097         | 0.914    | 0.081       | 0.914     |
| VGGT    | 0.335          | 0.599     | 0.053        | 0.970     | 0.082         | 0.947    | 0.056       | 0.951     |
| MoGe1   | 0.273          | **0.695** | 0.050        | 0.976     | 0.054         | 0.977    | 0.055       | 0.952     |
| π³      | 0.277          | 0.614     | 0.044        | 0.976     | 0.060         | 0.971    | 0.054       | 0.956     |
| Our     | 0.297          | 0.617     | **0.037**    | **0.979** | 0.058         | 0.967    | **0.051**   | **0.958** |

Best on Bonn and NYU-v2; second-best overall on Sintel and KITTI (e.g., Sintel Abs Rel 0.297 trails π³ 0.277 and MoGe1 0.273).

### Ablation — Joint Training (ETH3D)

원논문 Table 8. Effect of the 3D tracking branch and coupling losses; Acc.↓ / Comp.↓ / N.C.↑.

| w. 3D-Trk | w. L_cons | w. L_cam | w. L_self-sup. | Acc.↓     | Comp.↓    | N.C.↑     |
| --------- | --------- | -------- | -------------- | --------- | --------- | --------- |
| ✗         | ✗         | ✗        | ✗              | 0.177     | 0.201     | 0.888     |
| ✓         | ✗         | ✗        | ✗              | 0.175     | 0.199     | 0.887     |
| ✓         | ✗         | ✓        | ✓              | 0.172     | 0.198     | 0.890     |
| ✓         | ✓         | ✗        | ✓              | 0.173     | 0.200     | 0.887     |
| ✓         | ✓         | ✓        | ✗              | 0.170     | 0.196     | 0.889     |
| ✓         | ✓         | ✓        | ✓              | **0.168** | **0.192** | **0.891** |

### Ablation — Tracking Branch (DynamicReplica)

원논문 Table 10. AJ3D↑ / APD3D↑ / OA↑.

| Setting                        | AJ3D↑    | APD3D↑   | OA↑      |
| ------------------------------ | -------- | -------- | -------- |
| Base (only 3D track branch)    | 49.8     | 65.7     | 83.4     |
| + L_cons                       | 57.4     | 70.1     | 84.1     |
| + L_cons + L_cam               | 59.1     | 72.3     | 85.0     |
| + L_cons + L_cam + L_self-sup. | **59.5** | **72.5** | **85.1** |

### Ablation — Semi-supervised Training (Sekai)

원논문 Table 9. ATE↓ / RPE trans↓ / RPE rot↓.

| Setting         | ATE↓       | RPE trans↓ | RPE rot↓   |
| --------------- | ---------- | ---------- | ---------- |
| w. L_self-sup.  | **0.0101** | **0.0051** | **0.2515** |
| wo. L_self-sup. | 0.0154     | 0.0103     | 0.4413     |

## 💡 Insights & Impact

- **Correspondence as a first-class signal**: Making 3D correspondence an explicit trajectory prediction turns correspondence errors into direct training signals for both geometry and pose, rather than leaving cross-view coupling implicit as in MASt3R, St4RTrack, and VGGT.
- **Camera-space beats world-space for static-dominated data**: Because most training data is static (ScanNet, CO3D), world-frame trajectories collapse to trivial time-invariant solutions; predicting in per-frame camera coordinates keeps tracking gradients informative.
- **Gradient routing prevents residual absorption**: Stop-gradient in L_cons/L_cam stops the pointmap and tracking branches from chasing each other or averaging to a degenerate compromise, and confines pose updates to rigid static anchors.
- **Auxiliary tracking helps geometry**: Enabling the 3D tracking branch alone already improves ETH3D point maps (Table 8), consistent with VGGT's observation that jointly predicting multiple 3D quantities benefits point-map quality.
- **Self-supervision is data-distribution dependent**: L_self-sup. gives only a modest gain on ETH3D (distribution gap) but consistently improves both global trajectory accuracy and relative pose on in-the-wild Sekai (Table 9).

## 🔗 Related Work

- **[π³](../reconstruction/pi3.md)**: Permutation-equivariant, local-frame per-view point maps; TrajVG initializes from and freezes the π³ backbone and adopts a π³-like third training stage.
- **[VGGT](../reconstruction/vggt.md)**: Reference-frame (fixed world) feed-forward geometry transformer; a key baseline and motivation for TrajVG's explicit-coupling design.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: Pairwise pointmap regression foundations; MASt3R adds a dense feature/matching head.
- **[CUT3R](./cut3r.md)** / **[Fast3R](../reconstruction/fast3r.md)**: Streaming/many-view feed-forward reconstruction baselines compared on pose, point map, and depth.
- **[MonST3R](./monst3r.md)**: Dynamic-scene geometry baseline in the depth comparisons.
- **[MoGe](../reconstruction/moge.md)**: Specialized monocular geometry estimator compared on monocular depth.

## 📚 Key Takeaways

1. **Explicit 3D trajectories** act as geometric tie points that couple sparse tracks, dense point maps, and relative poses, addressing drift and duplicated structure in local-frame fusion.
2. **Two coupling losses with controlled gradient flow** (bidirectional L_cons + static-anchored L_cam) turn correspondence into active supervision for geometry and pose.
3. **Semi-supervised extension** transfers the same constraints to in-the-wild videos using only pseudo 2D tracks, improving generalization.
4. **State-of-the-art or competitive** across 3D tracking (TAPVid-3D), pose (RealEstate10K/Co3Dv2/TUM/ScanNet), point maps (ETH3D/7-Scenes), and video depth (Sintel/Bonn), while honestly trailing π³ on DTU point-map accuracy, Sintel ATE, and monocular Sintel depth.

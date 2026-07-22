# C4D: 4D Made from 3D through Dual Correspondences (ICCV 2025)

![c4d — architecture](https://arxiv.org/html/2510.14960/x2.png)

_Overview of C4D (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Shizun Wang, Zhenxiang Jiang, Xingyi Yang, Xinchao Wang
- **Institution**: National University of Singapore, The University of Hong Kong
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2510.14960) | [Project Page](https://littlepure2333.github.io/C4D)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: An optimization-side upgrade that turns any pretrained DUSt3R-family 3D model into a 4D reconstructor by adding two temporal correspondences — short-term optical flow and long-term point tracking — plus a dynamic-aware point tracker whose mobility prediction drives motion masks.

## 🎯 Key Contributions

1. **C4D framework**: Upgrades the current 3D reconstruction formulation to 4D by incorporating two temporal correspondences, without fine-tuning the 3D backbone. It applies to DUSt3R, MASt3R, and MonST3R weights alike.
2. **Dynamic-aware Point Tracker (DynPT)**: A point tracker that not only tracks points but also predicts whether a point is **dynamic in world coordinates** — distinguishing camera-induced apparent motion from true object motion.
3. **Correspondence-guided motion mask prediction**: Combines DynPT's static-point predictions with optical flow via fundamental-matrix epipolar geometry, aggregated over multiple adjacent frames.
4. **Correspondence-aided optimization**: Three additional objectives — Camera Movement Alignment (CMA), Camera Trajectory Smoothness (CTS), and Point Trajectory Smoothness (PTS) — added to DUSt3R's global alignment.

## 🔧 Technical Details

### Base 3D Formulation

C4D builds on the DUSt3R paradigm. Given a video with `T` frames, a scene graph `G` is built where each edge is an image pair `(Iⁿ, Iᵐ)`. A ViT `Φ` outputs two dense pointmaps and confidence maps per pair, which are then fused by global alignment (GA) into world-coordinate pointmaps plus poses `P` and scales `σ`. A sparse sliding-window scene graph is used to reduce cost, following prior work.

The failure mode C4D targets: global alignment assumes multi-view consistency, which moving objects violate.

### DynPT: Mobility-Aware Tracking

Architecturally derived from CoTracker, with a key change. Where CoTracker uses only a CNN to extract features, DynPT uses **both a CNN extractor and a 3D-aware ViT encoder**, then iteratively updates four quantities `M` times through a transformer:

- Position `P`
- Confidence `C`
- Visibility `V`
- **Mobility `M`** — the new output

Training details:

- Trained on the training sets of **panning MOVi-E and MOVi-F** from Kubric, chosen for non-trivial camera movement and motion blur.
- Confidence supervision: whether the predicted position lies within **12 pixels** of ground truth.
- Mobility labels are generated from Kubric's per-frame world-coordinate `positions` annotation: if an object's temporal position difference exceeds a threshold (e.g. **0.01**), all its tracking points are labeled dynamic. The authors note Kubric's own `is dynamic` label is insufficient — it only records whether an object was stationary or tossed at the _initial_ frame, missing objects that start moving after a collision.
- Inference queries a sparse point set in a sliding window. Query sampling divides the image into **20 × 20 pixel grids**, taking one maximum-gradient point plus one random point per grid, so sampling is not biased purely toward high-gradient areas.

### Motion Mask via Epipolar Geometry

1. Take DynPT's predicted **static** points `{P_t^j}` and, via optical flow `F^{t→t′}`, their correspondences in another frame.
2. Estimate the fundamental matrix between the two frames with **Least Median of Squares** — no camera intrinsics required, and robust to outliers.
3. Because `F` was estimated from static points only, it captures pure camera motion. Applying it to _all_ correspondences gives an epipolar error map; large error means the epipolar constraint is violated, i.e. a dynamic region. In practice the **Sampson error** is used as a first-order approximation accounting for scale and orientation.
4. Threshold to get a per-pair motion mask.
5. **Multi-frame union**: A two-frame mask is insufficient over longer horizons — e.g. a walking person's standing foot stays still before lifting off. C4D computes masks over all adjacent-frame pairs in the scene graph that include frame `t` and takes their union as the final mask `M_t`.

### Correspondence-Aided Optimization

The optimization objective extends global alignment:

```text
X̂ = arg min  w_GA · L_GA(X, σ, P) + w_CMA · L_CMA(X)
            + w_CTS · L_CTS(X) + w_PTS · L_PTS(X)
```

- **CMA (Camera Movement Alignment)**: Encourages the estimated ego-motion field to be consistent with optical flow in **static regions** — which is why mask quality matters so much (MonST3R uses CMA too, but with a weaker mask).
- **CTS (Camera Trajectory Smoothness)**: A standard visual-odometry term penalizing abrupt changes in camera rotation and translation between consecutive frames.
- **PTS (Point Trajectory Smoothness)**: Within a local temporal window, 2D tracks visible throughout the window are lifted to 3D and smoothed by a 1D convolution with **adaptive weights** that are reduced for outlier points based on temporal deviation. Smoothed points act as control points; a linear blend of control-point displacements, weighted by proximity, propagates to all other points, yielding dense smoothed pointmaps `X̃_t`. The loss is an L1 distance between global and smoothed pointmaps.

## 📊 Results

### Camera Pose Estimation Across 3D/4D Formulations

원논문 Table 1. C4D replaces Global Alignment as the optimization formulation, using the same 3D model weights.

| 3D Weights | Formulation      | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | TUM-dyn. ATE ↓ | TUM-dyn. RPE rot ↓ | ScanNet ATE ↓ | ScanNet RPE rot ↓ |
| ---------- | ---------------- | ------------ | ------------------ | ---------------- | -------------- | ------------------ | ------------- | ----------------- |
| DUSt3R     | Global Alignment | 0.416        | 0.216              | 18.038           | 0.127          | 2.033              | 0.060         | 0.751             |
| DUSt3R     | C4D              | 0.334        | 0.154              | 0.948            | 0.093          | 0.906              | 0.064         | 0.570             |
| MASt3R     | Global Alignment | 0.437        | 0.329              | 12.760           | 0.084          | 1.245              | 0.073         | 0.706             |
| MASt3R     | C4D              | 0.448        | 0.199              | 1.730            | 0.048          | 0.671              | 0.067         | 0.467             |
| MonST3R    | Global Alignment | 0.158        | 0.099              | 1.924            | 0.099          | 1.912              | 0.075         | 0.707             |
| MonST3R    | C4D (Ours)       | 0.103        | 0.040              | 0.705            | 0.071          | 0.897              | 0.061         | 0.538             |

The largest effect is on rotation: Sintel RPE rot on DUSt3R weights drops from 18.038 to 0.948. Reported honestly, C4D does **not** win everywhere — Sintel ATE on MASt3R weights gets slightly worse (0.437 → 0.448), and ScanNet ATE on DUSt3R weights gets slightly worse (0.060 → 0.064).

### Video Depth Estimation Across 3D/4D Formulations

원논문 Table 2. Scale-and-shift-invariant depth.

| 3D Weights | Formulation      | Sintel Abs Rel ↓ | Sintel RMSE ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ---------- | ---------------- | ---------------- | ------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| DUSt3R     | Global Alignment | 0.502            | 5.141         | 54.9            | 0.149          | 84.4          | 0.129           | 84.2           |
| DUSt3R     | C4D (Ours)       | 0.478            | 5.052         | 57.9            | 0.143          | 84.7          | 0.126           | 85.0           |
| MASt3R     | Global Alignment | 0.370            | 4.669         | 57.8            | 0.174          | 78.4          | 0.092           | 89.8           |
| MASt3R     | C4D (Ours)       | 0.379            | 4.756         | 58.3            | 0.168          | 78.6          | 0.092           | 89.7           |
| MonST3R    | Global Alignment | 0.335            | 4.467         | 57.5            | 0.065          | 96.2          | 0.090           | 90.6           |
| MonST3R    | C4D (Ours)       | 0.327            | 4.465         | 60.7            | 0.061          | 96.5          | 0.089           | 90.6           |

Again mixed on MASt3R weights: Sintel Abs Rel and RMSE both degrade slightly (0.370 → 0.379, 4.669 → 4.756) while δ<1.25 improves.

### Camera Pose vs. Specialized Methods

원논문 Table 3. `C4D-M` denotes C4D with MonST3R's model weights. `†` marks methods requiring ground-truth camera intrinsics as input; C4D estimates intrinsics and poses from monocular video alone.

| Category           | Method       | Sintel ATE ↓ | Sintel RPE rot ↓ | TUM-dyn. ATE ↓ | TUM-dyn. RPE rot ↓ | ScanNet ATE ↓ | ScanNet RPE rot ↓ |
| ------------------ | ------------ | ------------ | ---------------- | -------------- | ------------------ | ------------- | ----------------- |
| Pose only          | DROID-SLAM † | 0.175        | 1.912            | -              | -                  | -             | -                 |
| Pose only          | DPVO †       | 0.115        | 1.975            | -              | -                  | -             | -                 |
| Pose only          | ParticleSfM  | 0.129        | 0.535            | -              | -                  | 0.136         | 0.836             |
| Pose only          | LEAP-VO †    | 0.089        | 1.250            | 0.068          | 1.686              | 0.070         | 0.535             |
| Joint depth & pose | Robust-CVD   | 0.360        | 3.443            | 0.153          | 3.528              | 0.227         | 7.374             |
| Joint depth & pose | CasualSAM    | 0.141        | 0.615            | 0.071          | 1.712              | 0.158         | 1.618             |
| Joint depth & pose | MonST3R      | 0.109        | 0.737            | 0.104          | 1.037              | 0.068         | 0.545             |
| Joint depth & pose | C4D-M (Ours) | 0.103        | 0.705            | 0.071          | 0.897              | 0.061         | 0.538             |

LEAP-VO still has the lowest Sintel ATE (0.089), and ParticleSfM the lowest Sintel RPE rot (0.535) — both are pose-only specialists, and LEAP-VO requires GT intrinsics.

### Video Depth vs. Specialized Methods

원논문 Table 4. Two alignment protocols. The authors argue the **scale-only** setting is the more meaningful one, since a depth shift distorts x, y, z non-uniformly and warps recovered shape.

| Alignment           | Category               | Method           | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ------------------- | ---------------------- | ---------------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| Per-seq scale&shift | Single-frame depth     | Marigold         | 0.532            | 51.5            | 0.091          | 93.1          | 0.149           | 79.6           |
| Per-seq scale&shift | Single-frame depth     | DepthAnything-V2 | 0.367            | 55.4            | 0.106          | 92.1          | 0.140           | 80.4           |
| Per-seq scale&shift | Video depth            | DepthCrafter     | 0.292            | 69.7            | 0.075          | 97.1          | 0.110           | 88.1           |
| Per-seq scale&shift | Joint video depth&pose | MonST3R          | 0.335            | 58.5            | 0.063          | 96.2          | 0.157           | 73.8           |
| Per-seq scale&shift | Joint video depth&pose | C4D-M (Ours)     | 0.327            | 60.7            | 0.061          | 96.5          | 0.089           | 90.6           |
| Per-seq scale       | Video depth            | DepthCrafter     | 0.692            | 53.5            | 0.217          | 57.6          | 0.141           | 81.8           |
| Per-seq scale       | Joint video depth&pose | MonST3R          | 0.345            | 55.8            | 0.065          | 96.2          | 0.159           | 73.5           |
| Per-seq scale       | Joint video depth&pose | C4D-M (Ours)     | 0.338            | 58.1            | 0.063          | 96.4          | 0.091           | 90.6           |

Under scale & shift alignment DepthCrafter is ahead on Sintel (0.292 / 69.7) and Bonn δ<1.25 (97.1); C4D's clear advantage is on KITTI and under scale-only alignment.

### Point Tracking

원논문 Table 5. `D-ACC` is dynamic accuracy on Kubric.

| Method       | MOVi-E D-ACC ↑ | Pan. MOVi-E D-ACC ↑ | MOVi-F D-ACC ↑ | DAVIS AJ ↑ | DAVIS < δ_avg^x ↑ | DAVIS OA ↑ | Kinetics AJ ↑ | Kinetics OA ↑ |
| ------------ | -------------- | ------------------- | -------------- | ---------- | ----------------- | ---------- | ------------- | ------------- |
| RAFT         | -              | -                   | -              | 30.0       | 46.3              | 79.6       | 34.5          | 79.7          |
| TAP-Net      | -              | -                   | -              | 38.4       | 53.1              | 82.3       | 46.6          | 85.0          |
| PIPs         | -              | -                   | -              | 39.9       | 56.0              | 81.3       | 39.1          | 82.9          |
| MFT          | -              | -                   | -              | 47.3       | 66.8              | 77.8       | 39.6          | 72.7          |
| TAPIR        | -              | -                   | -              | 56.2       | 70.0              | 86.5       | 49.6          | 85.0          |
| CoTracker    | -              | -                   | -              | 61.8       | 76.1              | 88.3       | 49.6          | 83.3          |
| DynPT (Ours) | 87.9           | 94.1                | 91.5           | 61.6       | 75.4              | 87.4       | 47.8          | 82.3          |

Reported honestly: DynPT does **not** beat CoTracker on TAP-Vid — it is slightly behind on every DAVIS and Kinetics column. The paper's own framing is "comparable performance with SOTA methods" while additionally solving the harder mobility-prediction problem, which no prior TAP method does.

### Ablation on Optimization Objectives

원논문 Table 6, Sintel.

| Method     | ATE ↓ | RPE t ↓ | RPE r ↓ | Abs Rel ↓ | RMSE ↓ | δ<1.25 ↑ |
| ---------- | ----- | ------- | ------- | --------- | ------ | -------- |
| w/o CMA    | 0.140 | 0.051   | 0.905   | 0.335     | 4.501  | 0.582    |
| w/o CTS    | 0.131 | 0.058   | 1.348   | 0.322     | 4.442  | 0.608    |
| w/o PTS    | 0.103 | 0.040   | 0.705   | 0.327     | 4.465  | 0.607    |
| C4D (Ours) | 0.103 | 0.040   | 0.705   | 0.327     | 4.459  | 0.609    |

Note the honest reading the paper itself gives: removing PTS changes pose metrics not at all and depth metrics only marginally. PTS is justified instead by temporal smoothness, which these metrics cannot capture — the paper shows y-t depth slices (Figure 5) as the evidence and does not claim a numeric win.

### Motion Segmentation on DAVIS2016

원논문 Table 7. Evaluated **without** Hungarian matching between predicted and ground-truth motion masks.

| Method    | IoU ↑ |
| --------- | ----- |
| Ours      | 47.89 |
| MonST3R   | 31.57 |
| FlowP-SAM | 42.23 |

### DynPT Architecture Ablation

원논문 Table 8. `CE` = CNN encoder only, `3E` = 3D-aware encoder only.

| Method  | MOVi-E D-ACC ↑ | Pan. MOVi-E D-ACC ↑ | MOVi-F D-ACC ↑ | DAVIS AJ ↑ | DAVIS OA ↑ | Kinetics AJ ↑ | Kinetics OA ↑ |
| ------- | -------------- | ------------------- | -------------- | ---------- | ---------- | ------------- | ------------- |
| DynPT   | 87.9           | 94.1                | 91.5           | 61.6       | 87.4       | 47.8          | 82.3          |
| CE only | 82.6           | 90.4                | 86.8           | 60.6       | 86.8       | 46.2          | 81.7          |
| 3E only | 85.4           | 92.2                | 90.4           | 42.4       | 73.4       | 38.9          | 70.4          |

The two encoders are complementary in different directions: 3E-only is better than CE-only on Kubric dynamic accuracy but collapses on real-world TAP-Vid tracking. Combining them wins on both.

## 💡 Insights & Impact

### Upgrading, Not Retraining

The design decision that distinguishes C4D from MonST3R is stated explicitly: MonST3R explores pointmap-based dynamic reconstruction **by fine-tuning DUSt3R** on dynamic data, whereas C4D **directly uses pretrained pointmap weights** and complements them with correspondence-guided optimization. Table 1 and Table 2 are structured to make this claim testable — the same optimization swap is applied on top of three different backbones, and it helps in most cells regardless of which.

### Mobility Is a Different Problem from Tracking

Every prior TAP method predicts position and occlusion in _image_ space; none predicts whether a point moves in _world_ coordinates. That distinction is what a motion mask actually needs, since a static point can move across the image purely from camera motion. DynPT pays a small tracking-accuracy cost for taking on this harder objective, which the paper acknowledges rather than hides.

### The Motion Mask Is the Bottleneck for CMA

The paper notes MonST3R also uses the CMA objective — so C4D's pose advantage over MonST3R does not come from a new loss but from a **better mask feeding the same loss**. This reframes dynamic reconstruction: the optimization machinery was already adequate; the dynamic/static segmentation was not.

### Static-Point-Only Fundamental Matrix

Estimating `F` exclusively from predicted-static correspondences is an elegant bootstrap: `F` then encodes camera motion uncontaminated by moving objects, so the epipolar error it induces on _all_ correspondences becomes a clean dynamic detector. The multi-frame union then covers the case of temporarily-stationary dynamic objects.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md) — the base 3D formulation and global alignment C4D extends; also used as one of the three tested weight sets
- [MASt3R](../foundation/mast3r.md) — second tested backbone
- [MonST3R](monst3r.md) — the closest prior work and primary baseline; fine-tunes DUSt3R for dynamics, where C4D keeps weights frozen. C4D-M uses MonST3R weights
- [CUT3R](cut3r.md) — an alternative recurrent formulation for dynamic streams
- [Easi3R](easi3r.md) — another training-free approach to dynamic scenes via attention
- [Align3R](align3r.md), [D²USt3R](d2ust3r.md) — related dynamic pointmap alignment work
- [Dynamic Point Maps](dynamic-point-maps.md), [Stereo4D](stereo4d.md) — 4D pointmap representations
- [MASt3R-SfM](../foundation/mast3r-sfm.md) — the sparse scene-graph construction C4D follows

## 📚 Key Takeaways

1. **The 3D→4D gap can be closed at the optimization layer.** C4D adds no backbone training and still improves DUSt3R, MASt3R, and MonST3R weights on most pose and depth metrics.
2. **Rotation is where dynamics hurt most.** Sintel RPE rot on DUSt3R weights falls from 18.038 to 0.948 — an order of magnitude larger effect than on ATE.
3. **World-coordinate mobility ≠ image-space tracking.** DynPT introduces mobility as a fourth predicted quantity alongside position, confidence, and visibility.
4. **Mask quality, not loss design, drives the MonST3R gap.** Both methods use CMA; C4D's advantage comes from a better motion mask (DAVIS2016 IoU 47.89 vs 31.57).
5. **PTS is not justified by the metrics.** Removing it leaves pose metrics identical and depth nearly identical; its value is temporal smoothness visible only in y-t depth slices, and the paper says so.
6. **Mobility prediction costs a little tracking accuracy.** DynPT trails CoTracker on all TAP-Vid columns while gaining a capability CoTracker lacks.

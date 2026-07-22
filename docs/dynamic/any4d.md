# Any4D: Unified Feed-Forward Metric 4D Reconstruction (arXiv preprint)

![any4d — architecture](https://arxiv.org/html/2512.10935/x6.png)

_Figure S.1: 4-View training is key to enabling multi-frame generalization during inference (원논문 Fig. 99)_

## 📋 Overview

- **Authors**: Jay Karhade, Nikhil Keetha, Yuchen Zhang, Tanisha Gupta, Akash Sharma, Sebastian Scherer, Deva Ramanan
- **Institution**: Carnegie Mellon University
- **Venue**: arXiv preprint (2025-12)
- **Links**: [Paper](https://arxiv.org/abs/2512.10935) | [Project Page](https://any-4d.github.io/)
- **Verification**: PREPRINT (2026-07-20)
- **TL;DR**: A multi-view transformer that predicts dense metric-scale 4D reconstruction — geometry, camera poses, and allocentric scene flow — for N frames in a single feed-forward pass, optionally conditioned on depth, IMU poses, or Radar Doppler.

## 🎯 Key Contributions

1. **Dense Metric-Scale 4D**: Predicts a global metric scale factor together with per-view geometry and motion, unlike prior work that reconstructs only up to scale or only sparse tracks.
2. **Factored 4D Representation**: Egocentric factors (ray directions, scale-normalized ray depth) in local camera coordinates plus allocentric factors (forward scene flow, camera pose) in a world frame. This factoring is what allows training on datasets with only partial annotations.
3. **Flexible Multi-Modal Inputs**: RGB plus optional depth from RGB-D sensors, camera poses from IMUs, camera intrinsics, and Doppler velocity from radar.
4. **Single-Pass N-View Inference**: All concurrent methods require multiple feed-forward passes to infer motion; Any4D does one pass over all frames.
5. **New Allocentric Benchmarks**: Repurposes TAPVID-3D, Dynamic Replica, LSFOdyssey, VKITTI-2, and Kubric-4D into allocentric 3D tracking and dense scene flow benchmarks.

## 🔧 Technical Details

### Core Innovation: Factoring the 4D Output

```text
Prior 4D models: pointmaps (+ optional 2D tracker), up-to-scale, RGB-only
Any4D:           (s̃, {R̃ᵢ, D̃ᵢ, T̃ᵢ, F̃ᵢ}) = Any4D(I, O)
```

Predictions comprise a metric scaling factor `s̃ ∈ ℝ`, per-view ray directions `R̃ᵢ` and
scale-normalized ray depth `D̃ᵢ` (egocentric), and per-view forward scene flow `F̃ᵢ` from the first
view plus camera pose `T̃ᵢ = [pᵢ, qᵢ]` (allocentric). Metric geometry is recomposed as
`G̃ᵢ = s̃ · T̃ᵢ · R̃ᵢ · D̃ᵢ`, allocentric motion as `M̃ᵢ = s̃ · F̃ᵢ`, and geometry after motion as
`G̃′ᵢ = G̃ᵢ + M̃ᵢ`.

### Architecture

- **RGB encoder**: DINOv2 ViT-Large, layer-normalized final-layer patch features (1024-dim).
- **Depth encoder**: shallow CNN, with the normalization factor computed independently per local view.
- **Doppler encoder**: CNN, with the normalization factor computed from the first-view pointmap and shared globally.
- **Intrinsics**: encoded as ray directions through a CNN mapping 3 channels into the 1024-dim latent space.
- **Poses**: two 4-layer MLPs for rotation and translation; the translation normalization factor is global across views, and a positional encoding marks the reference view.
- **Metric scale token**: depth scale and pose scale are converted to log-scale and encoded by a 4-layer MLP.
- All encodings are **summed** into a per-view embedding and flattened into tokens, plus a learnable metric-scale token.
- **Backbone**: alternating-attention transformer, 12 blocks, 12 heads, latent dim 768, MLP ratio 4 (ViT-Base scale). No 2D RoPE; Flash Attention for efficiency.
- **Heads**: a geometry DPT head (ray directions, up-to-scale ray depths, confidence masks), a motion DPT head (allocentric forward scene flow), an average-pooling CNN pose decoder, and an MLP metric-scale decoder.

### Losses

Scale-agnostic quantities use plain regression: `L_rays` (L1 on ray directions) and `L_rotation`
(quaternion double-cover min). Scale-dependent quantities are supervised scale-invariantly by
dividing by a ground-truth scale `z` and a prediction-derived scale `z̃`, with
`f_log(x) = (x/‖x‖) log(1 + ‖x‖)` for numerical stability, giving `L_trans`, `L_depth`, `L_pm`, and
`L_sf`. Because the scene-flow loss is dominated by static points, a static–dynamic mask `M` derived
from the ground truth **upweights dynamic regions by 10×**. Metric scale is supervised in log space
with a stop-gradient so it does not perturb other predictions.

Total: `L = L_trans + L_rot + L_rays + L_depth + L_sf + L_mask`.

### Training

- Initialized from the public MapAnything checkpoint; the Doppler encoder and scene-flow DPT decoder are learned from scratch.
- Learning rates: 1e-5 network, 5e-7 DINOv2 image encoder, 1e-4 scene-flow DPT decoder. 10-epoch warmup, 100 epochs total, ~120k gradient steps on 8 H100 GPUs.
- Mixed static + dynamic data: BlendedMVS, MegaDepth, ScanNet++, VKITTI2, Waymo-DriveTrack, GCD-Kubric, CoTracker3-Kubric, Dynamic Replica, PointOdyssey. Scene flow supervision comes only from CoTracker3-Kubric, PointOdyssey, and Dynamic Replica.
- Multi-modal conditioning applied with probability 0.7; each individual modality independently dropped with probability 0.5.
- Up to 4 views sampled per batch. Doppler velocity is simulated as the radial component of egocentric scene flow.

## 📊 Results

### Sparse 3D Point Tracking

원논문 Table 1. EPE ↓, APD ↑ for dynamic points; EPE ↓, inlier ratio τ ↑ at 0.1m for scene flow.
Runtime is measured on an H100 with 50 input frames. Split by dataset.

**Runtime and Drive Track**

| Method                   | Runtime (s) ↓ | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑   |
| ------------------------ | ------------- | ---------- | ---------- | -------- | -------- |
| MonST3R + CoTracker3     | 146.40        | 16.81      | 0.44       | 21.87    | 0.06     |
| MASt3R + CoTracker3      | 13.82         | 17.16      | 1.22       | 20.01    | 0.20     |
| VGGT + CoTracker3        | 2.31          | 8.30       | 4.80       | 11.69    | 0.77     |
| MapAnything + CoTracker3 | 0.73          | 9.42       | 2.45       | 12.88    | 0.43     |
| St4RTrack                | 1.12          | 11.82      | 1.03       | 14.63    | 0.10     |
| SpatialTrackerV2         | 11.56         | 5.45       | 4.48       | 10.63    | 0.10     |
| **Any4D**                | **0.50**      | **3.89**   | **7.81**   | **3.14** | **1.83** |

**Dynamic Replica**

| Method                   | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑    |
| ------------------------ | ---------- | ---------- | -------- | --------- |
| MonST3R + CoTracker3     | 0.81       | 43.34      | 0.18     | 25.99     |
| MASt3R + CoTracker3      | 0.40       | 57.72      | 0.23     | 53.98     |
| VGGT + CoTracker3        | 0.26       | 69.12      | 0.06     | 89.37     |
| MapAnything + CoTracker3 | 0.25       | 70.51      | 0.06     | **89.59** |
| St4RTrack                | 0.17       | 80.87      | 0.07     | 77.90     |
| SpatialTrackerV2         | 0.69       | 62.34      | 0.06     | 83.66     |
| **Any4D**                | **0.07**   | **93.44**  | **0.05** | 86.99     |

**LSFOdyssey**

| Method                   | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑    |
| ------------------------ | ---------- | ---------- | -------- | --------- |
| MonST3R + CoTracker3     | 0.61       | 50.96      | 0.41     | 43.64     |
| MASt3R + CoTracker3      | 0.83       | 45.95      | 0.62     | 41.10     |
| VGGT + CoTracker3        | 0.47       | 59.21      | 0.22     | 74.11     |
| MapAnything + CoTracker3 | 0.63       | 35.51      | 0.51     | 58.00     |
| St4RTrack                | 0.56       | 48.11      | 0.25     | 38.31     |
| SpatialTrackerV2         | 0.34       | 68.37      | **0.09** | **78.75** |
| **Any4D**                | **0.27**   | **71.70**  | 0.10     | 71.41     |

**PStudio**

| Method                   | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑    |
| ------------------------ | ---------- | ---------- | -------- | --------- |
| MonST3R + CoTracker3     | 0.51       | 51.87      | 0.52     | 21.06     |
| MASt3R + CoTracker3      | 0.43       | 54.11      | 0.43     | 14.69     |
| VGGT + CoTracker3        | 0.26       | 69.34      | 0.17     | 45.77     |
| MapAnything + CoTracker3 | 0.63       | 50.85      | 0.35     | **58.01** |
| St4RTrack                | 0.41       | 53.12      | 0.21     | 28.46     |
| SpatialTrackerV2         | **0.21**   | **74.46**  | **0.14** | 50.70     |
| **Any4D**                | 0.27       | 67.43      | 0.19     | 33.57     |

Honest reading: Any4D does **not** sweep this benchmark. On LSFOdyssey scene flow it loses to
SpatialTrackerV2 on both EPE and τ; on Dynamic Replica scene-flow τ it loses to MapAnything and VGGT
compositions; and on PStudio it loses to SpatialTrackerV2 on every metric and to MapAnything on
scene-flow τ. Its clear wins are Drive Track and Dynamic Replica dynamic points, plus runtime. The
paper states Any4D is 15× faster than SpatialTrackerV2, the closest performing method.

### Dense Scene Flow

원논문 Table 2. Split by dataset.

**Kubric-4D Dynamic Camera**

| Method                 | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑    |
| ---------------------- | ---------- | ---------- | -------- | --------- |
| MonST3R + SEA-RAFT     | 5.23       | 2.20       | 3.73     | 14.69     |
| MASt3R + SEA-RAFT      | 6.35       | 1.92       | 1.45     | 13.95     |
| VGGT + SEA-RAFT        | 11.80      | 3.60       | 11.76    | 14.53     |
| MapAnything + SEA-RAFT | 17.65      | 2.67       | 17.70    | 9.16      |
| St4RTrack              | 2.44       | 5.79       | 1.70     | 11.83     |
| **Any4D**              | **1.13**   | **18.14**  | **0.17** | **83.38** |

**Kubric-4D Static Camera**

| Method                 | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑    |
| ---------------------- | ---------- | ---------- | -------- | --------- |
| MonST3R + SEA-RAFT     | 2.26       | 6.80       | 1.16     | 61.79     |
| MASt3R + SEA-RAFT      | 2.85       | 7.58       | 1.26     | 53.62     |
| VGGT + SEA-RAFT        | 1.92       | 15.01      | 0.78     | 86.54     |
| MapAnything + SEA-RAFT | 2.82       | 19.99      | 1.75     | 73.33     |
| St4RTrack              | 2.61       | 6.53       | 0.72     | 20.51     |
| **Any4D**              | **1.23**   | 19.53      | **0.10** | **87.51** |

MapAnything + SEA-RAFT edges out Any4D on APD here (19.99 vs 19.53).

**VKITTI-2**

| Method                 | Dyn. EPE ↓ | Dyn. APD ↑ | SF EPE ↓ | SF τ ↑    |
| ---------------------- | ---------- | ---------- | -------- | --------- |
| MonST3R + SEA-RAFT     | 12.31      | 0.44       | 1.21     | 12.93     |
| MASt3R + SEA-RAFT      | 12.25      | 2.50       | 13.05    | 10.20     |
| VGGT + SEA-RAFT        | 6.57       | 2.61       | 0.70     | 37.63     |
| MapAnything + SEA-RAFT | 8.46       | 2.42       | 1.32     | 13.78     |
| St4RTrack              | 14.71      | 0.00       | 0.97     | 3.37      |
| **Any4D**              | **4.97**   | **11.70**  | **0.04** | **93.08** |

The paper summarizes that Any4D outperforms baselines by 2–3× on average on APD, and by more on
scene-flow metrics.

### Video Depth

원논문 Table 3. Absolute relative error (rel ↓) and inlier ratio at 1.25 (δ₁.₂₅ ↑).

| Category                  | Method           | Avg rel ↓ | Avg δ ↑   | Bonn rel ↓ | Bonn δ ↑  | KITTI rel ↓ | KITTI δ ↑ | Sintel rel ↓ | Sintel δ ↑ |
| ------------------------- | ---------------- | --------- | --------- | ---------- | --------- | ----------- | --------- | ------------ | ---------- |
| Video Depth               | DepthCrafter     | 0.15      | 85.23     | 0.07       | 97.90     | 0.11        | 88.50     | 0.27         | 69.30      |
| Video Depth               | VDA              | 0.17      | 86.90     | 0.05       | 98.20     | 0.08        | 95.10     | 0.37         | 67.40      |
| Feed-Forward + Iter. Opt. | DUSt3R           | 0.26      | 75.83     | 0.17       | 83.50     | 0.12        | 84.90     | 0.48         | 59.10      |
| Feed-Forward + Iter. Opt. | MonST3R          | 0.16      | 82.73     | 0.06       | 95.40     | 0.08        | 93.40     | 0.34         | 59.40      |
| Feed-Forward + Iter. Opt. | MegaSAM          | 0.10      | 87.97     | 0.04       | 97.70     | 0.07        | 91.60     | 0.18         | **74.60**  |
| Feed-Forward + Iter. Opt. | SpatialTrackerV2 | **0.09**  | **88.80** | **0.03**   | **98.80** | **0.05**    | **97.30** | 0.20         | 70.30      |
| Single-Step Feed-Forward  | CUT3R            | 0.21      | 80.30     | 0.07       | 95.00     | 0.10        | 89.90     | 0.47         | 56.00      |
| Single-Step Feed-Forward  | VGGT             | 0.13      | 85.85     | 0.07       | 97.27     | 0.09        | 94.37     | 0.24         | 65.90      |
| Single-Step Feed-Forward  | MapAnything      | 0.14      | 84.97     | 0.09       | 94.77     | 0.09        | 94.26     | 0.25         | 65.87      |
| Single-Step Feed-Forward  | **Any4D**        | 0.13      | 86.28     | 0.07       | 97.27     | 0.09        | 93.97     | 0.24         | 67.59      |

Video depth is the honest weak spot: Any4D leads only within the single-step feed-forward group, and
even there it ties VGGT on average rel (0.13) and on KITTI rel (0.09), and is behind VGGT on KITTI
δ₁.₂₅ (93.97 vs 94.37). Optimization-based methods remain well ahead.

### Multi-Modal Inputs

원논문 Table 4. "Geometry" indicates depth, intrinsics, and poses.

| Any4D Inputs                    | Kubric-4D Static Dyn. EPE ↓ | Kubric APD ↑ | Kubric SF EPE ↓ | Kubric SF τ ↑ | LSFOdyssey Dyn. EPE ↓ | LSFOdyssey APD ↑ | LSFOdyssey SF EPE ↓ | LSFOdyssey SF τ ↑ |
| ------------------------------- | --------------------------- | ------------ | --------------- | ------------- | --------------------- | ---------------- | ------------------- | ----------------- |
| Images Only                     | 1.17                        | 21.33        | 0.11            | 86.25         | 0.28                  | 71.47            | 0.12                | 68.03             |
| Images + Geometry               | **0.23**                    | 80.18        | **0.09**        | 86.26         | **0.19**              | 80.80            | 0.12                | 68.71             |
| Images + Doppler                | 1.17                        | 21.70        | 0.12            | 86.90         | 0.29                  | 71.26            | **0.11**            | 70.32             |
| **Images + Geometry + Doppler** | **0.23**                    | **81.72**    | **0.09**        | **87.27**     | **0.19**              | **81.10**        | **0.11**            | **71.37**         |

Geometry mainly helps 3D points (APD 21.33 → 80.18 on Kubric); Doppler mainly helps scene flow.

### Choice of Motion Representation

원논문 Table 5.

| Representation Type        | Kubric Dyn. EPE ↓ | Kubric APD ↑ | Kubric SF EPE ↓ | Kubric SF τ ↑ | LSFO Dyn. EPE ↓ | LSFO APD ↑ | LSFO SF EPE ↓ | LSFO SF τ ↑ |
| -------------------------- | ----------------- | ------------ | --------------- | ------------- | --------------- | ---------- | ------------- | ----------- |
| Backprojected 2D Flow      | 2.14              | 19.44        | 1.16            | 75.69         | 0.49            | 57.21      | 0.27          | 70.11       |
| 3D Points After Motion     | 1.24              | 17.33        | 0.58            | 21.84         | **0.24**        | 69.30      | 0.38          | 21.87       |
| Egocentric Scene Flow      | 1.26              | 19.43        | 0.12            | 85.37         | **0.24**        | 71.80      | 0.14          | 65.13       |
| **Allocentric Scene Flow** | **1.23**          | **19.53**    | **0.10**        | **87.51**     | **0.24**        | **73.95**  | **0.10**      | **71.46**   |

Predicting allocentric motion directly is best not only for scene flow but also for dynamic
pointmaps after motion, compared to St4RTrack's "3D points after motion" parameterization.

### View-Count Generalization

원논문 Figure S.1. Any4D trained with 2 views degrades in scene-flow EPE as the number of inference
views grows, whereas the 4-view-trained model stays stable up to 64 views. The paper concludes that
4-view training is critical for multi-view generalization.

## 💡 Insights & Impact

### Factoring is a data strategy, not just an architecture choice

The egocentric/allocentric split lets each loss term be applied only where annotation exists. That is
what permits training on metric-scale 3D datasets without motion labels alongside non-metric datasets
with motion labels — the paper is explicit that scene-flow supervision comes from only three of the
nine training datasets.

### Metric scale as a separate predicted quantity

Rather than baking metric scale into the geometry head, Any4D predicts a single scalar `s̃` with a
stop-gradient in its loss, so metric supervision cannot corrupt the scale-invariant geometry and
motion learning. This is the mechanism behind "metric-scale outputs" without sacrificing training on
up-to-scale data.

### The dynamic-region upweighting

A scene-flow loss averaged over all pixels is dominated by static background. Any4D computes a
static–dynamic mask from ground truth and weights dynamic regions 10× — the paper calls this crucial.

### Where it wins and where it does not

Any4D is decisively ahead on **dense** scene flow (Table 2, all three benchmarks) and on runtime
(0.50s vs 11.56s for SpatialTrackerV2). On **sparse** 3D tracking it splits results with
SpatialTrackerV2, losing PStudio outright and LSFOdyssey scene flow. On video depth it is merely
competitive within its own single-pass category. The honest framing is: the first method to make
dense metric 4D practical at this speed, not a uniform accuracy leader.

## 🔗 Related Work

- [MonST3R](monst3r.md) — the dynamic DUSt3R extension used here as a composed baseline (with CoTracker3 and SEA-RAFT); requires post-hoc optimization to establish correspondences.
- [Dynamic Point Maps](dynamic-point-maps.md) and [V-DPM](v-dpm.md) — the alternative line that encodes motion inside the point-map representation itself, rather than as a separate factored scene-flow output.
- [VGGT](../reconstruction/vggt.md) — the alternating-attention design Any4D inherits, and a baseline in every table.
- [CUT3R](cut3r.md) — streaming single-step feed-forward baseline in the video-depth comparison.
- [Easi3R](easi3r.md) — related attention-based dynamic decomposition on top of DUSt3R-family models.

## 📚 Key Takeaways

1. **A factored 4D output (egocentric depth/rays + allocentric flow/pose + a global metric scale) lets one model train on datasets with wildly different annotation coverage.**
2. **Allocentric scene flow is the right parameterization**: it beats egocentric flow, backprojected 2D flow, and "3D points after motion" on both scene-flow and dynamic-point metrics.
3. **Optional modalities pay off predictably** — geometry for 3D points, Doppler for scene flow, both together best.
4. **Speed is the standout result**: 0.50s for 50 frames on an H100, which the paper reports as 15× faster than SpatialTrackerV2.
5. **Not a clean sweep.** SpatialTrackerV2 still wins PStudio and LSFOdyssey scene flow; optimization-based methods still win video depth. The claimed 2–3× advantage is specific to dense scene flow APD.

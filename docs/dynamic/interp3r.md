# Interp3R: Continuous-time 3D Geometry Estimation with Frames and Events (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Shuang Guo, Filbert Febryanto, Lei Sun, Guillermo Gallego
- **Institution**: TU Berlin; Robotics Institute Germany; INSAIT, Sofia University "St. Kliment Ohridski"; Einstein Center Digital Future and SCIoI Excellence Cluster
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.14528)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first method to extend pointmap-based models to continuous-time 3D geometry estimation, using asynchronous event data to interpolate pointmaps at arbitrary time instants between frames and jointly recover depth and camera poses via coarse-to-fine global alignment.

## 🎯 Key Contributions

1. **Continuous-time pointmap interpolation**: Extends pointmap models (DUSt3R/MonST3R/Align3R) to estimate depth and camera poses at arbitrary time instants τ ∈ (0,1) between frames, by interpolating pointmaps from bidirectional events.
2. **Plug-and-play compatibility**: Works with different frame-based pointmap backbones (demonstrated with Align3R and MonST3R) without retraining the backbone.
3. **Synthetic-only training, strong generalization**: Trained solely on PointOdyssey, yet generalizes across synthetic and real-world benchmarks, outperforming two-stage (2D VFI → 3D geometry) baselines.

## 🔧 Technical Details

### Pairwise Pointmap Interpolation

- A frozen pointmap model (Align3R by default) produces source pointmaps `(X00, X01)` and confidences from an image pair `(I0, I1)`.
- Interp3R interpolates pointmaps `(X0→τ, X1→τ)` from forward events `E0→τ` and reversed backward events `E1→τ` (voxelized, shared event encoder), fused with pointmap/confidence ViT features via **zero convolution** so that before training it exactly reproduces the source pointmaps (training stability).
- **Explicit time encoding**: conditions prediction heads on target time τ, giving more constant performance across interpolation times vs. implicit temporal truncation.
- Training loss: confidence-aware scale-invariant 3D regression (DUSt3R-style), summed over both temporal directions; only the Interp3R component is trained.

### Coarse-to-Fine Global Alignment

- **Coarse**: align Align3R source pointmaps to recover Θ0, Θ1 (as in Align3R).
- **Fine**: align Interp3R interpolated pointmaps with source pointmaps to solve for Θτ (Θ0, Θ1 still refined). Symmetrizing pairs yields four confidence-weighted pointmaps fused at t=τ.
- 300 Adam iterations per stage (LR 0.01, linear decay); flow loss (RAFT) only in coarse stage.

### Training

- Six NVIDIA RTX A6000, total batch 12, 50 epochs, AdamW LR 0.0001; trained only on PointOdyssey; triplets (t=0, τ, 1) spanning 2–10 frames, 20,000 triplets sampled per epoch.

## 📊 Results

### Model Capability Comparison (원논문 Table 1)

원논문 Table 1. FF=Feed-forward ViT, Diff=Diffusion, PM=Pointmap-based; F=Frames, E=Events.

| Method             | Year | Type | Input | Video | Pose | Dynamic Scene | Continuous-time |
| ------------------ | ---- | ---- | ----- | ----- | ---- | ------------- | --------------- |
| VideoDepthAnything | 2025 | FF   | F     | ✓     | ✗    | ✓             | ✗               |
| DepthAnything-v3   | 2025 | FF   | F     | ✓     | ✓    | ✓             | ✗               |
| ChronoDepth        | 2024 | Diff | F     | ✓     | ✗    | ✓             | ✗               |
| DepthCrafter       | 2025 | Diff | F     | ✓     | ✗    | ✓             | ✗               |
| DUSt3R             | 2024 | PM   | F     | ✓     | ✓    | ✗             | ✗               |
| MonST3R            | 2025 | PM   | F     | ✓     | ✓    | ✓             | ✗               |
| Align3R            | 2025 | PM   | F     | ✓     | ✓    | ✓             | ✗               |
| EAG3R              | 2025 | PM   | E+F   | ✓     | ✓    | ✓             | ✗               |
| Interp3R (Ours)    | 2026 | PM   | E+F   | ✓     | ✓    | ✓             | ✓               |

### Depth — PointOdyssey (원논문 Table 2)

원논문 Table 2 (일부). Abs Rel↓, δ<1.25↑. Skipped frames만 평가.

| Method       | s1 AbsRel ↓ | s1 δ ↑    | s3 AbsRel ↓ | s3 δ ↑    | s7 AbsRel ↓ | s7 δ ↑    | s15 AbsRel ↓ | s15 δ ↑   |
| ------------ | ----------- | --------- | ----------- | --------- | ----------- | --------- | ------------ | --------- |
| RIFE         | 0.097       | 0.925     | 0.106       | 0.911     | 0.146       | 0.891     | 0.196        | 0.846     |
| TimeLens     | 0.087       | 0.925     | 0.099       | 0.912     | 0.142       | 0.858     | 0.215        | 0.777     |
| VDM-EVFI     | 0.108       | 0.889     | 0.113       | 0.875     | 0.118       | 0.861     | 0.137        | 0.839     |
| **Interp3R** | **0.069**   | **0.948** | **0.067**   | **0.952** | **0.074**   | **0.948** | **0.099**    | **0.896** |

### Depth — Sintel (원논문 Table 2)

원논문 Table 2 (일부). skip=7의 δ에서 VDM-EVFI(0.559)가 Interp3R(0.534)보다 높다.

| Method       | s1 AbsRel ↓ | s1 δ ↑    | s3 AbsRel ↓ | s3 δ ↑    | s7 AbsRel ↓ | s7 δ ↑    | s15 AbsRel ↓ | s15 δ ↑   |
| ------------ | ----------- | --------- | ----------- | --------- | ----------- | --------- | ------------ | --------- |
| RIFE         | 0.381       | 0.538     | 0.478       | 0.532     | 0.515       | 0.522     | 0.580        | 0.507     |
| TimeLens     | 0.377       | 0.548     | 0.441       | 0.545     | 0.530       | 0.496     | 0.595        | 0.453     |
| VDM-EVFI     | 0.366       | 0.542     | 0.390       | 0.553     | 0.397       | **0.559** | 0.424        | 0.543     |
| **Interp3R** | **0.338**   | **0.591** | **0.335**   | **0.575** | **0.370**   | 0.534     | **0.420**    | **0.556** |

### Depth — Bonn (원논문 Table 2)

원논문 Table 2 (일부). VDM-EVFI가 δ 대부분과 skip=15 AbsRel에서 Interp3R보다 낫다(반쪽 지표만 최고).

| Method       | s1 AbsRel ↓ | s1 δ ↑    | s3 AbsRel ↓ | s3 δ ↑    | s7 AbsRel ↓ | s7 δ ↑    | s15 AbsRel ↓ | s15 δ ↑   |
| ------------ | ----------- | --------- | ----------- | --------- | ----------- | --------- | ------------ | --------- |
| RIFE         | 0.075       | 0.956     | 0.079       | 0.952     | 0.098       | 0.932     | 0.157        | 0.886     |
| TimeLens     | 0.077       | 0.956     | 0.082       | 0.949     | 0.104       | 0.922     | 0.226        | 0.758     |
| VDM-EVFI     | 0.074       | **0.959** | 0.076       | **0.955** | 0.076       | **0.956** | **0.076**    | **0.956** |
| **Interp3R** | **0.069**   | 0.954     | **0.070**   | 0.946     | **0.067**   | 0.955     | 0.078        | 0.939     |

### Depth — TUM (원논문 Table 2)

원논문 Table 2 (일부).

| Method       | s1 AbsRel ↓ | s1 δ ↑    | s3 AbsRel ↓ | s3 δ ↑    | s7 AbsRel ↓ | s7 δ ↑    | s15 AbsRel ↓ | s15 δ ↑   |
| ------------ | ----------- | --------- | ----------- | --------- | ----------- | --------- | ------------ | --------- |
| RIFE         | 0.110       | 0.876     | 0.114       | 0.874     | 0.130       | 0.856     | 0.169        | 0.807     |
| TimeLens     | 0.112       | 0.872     | 0.116       | 0.868     | 0.133       | 0.827     | 0.189        | 0.730     |
| VDM-EVFI     | 0.133       | 0.824     | 0.128       | 0.828     | 0.130       | 0.834     | 0.134        | 0.828     |
| **Interp3R** | **0.103**   | **0.879** | **0.101**   | **0.880** | **0.101**   | **0.880** | **0.101**    | **0.881** |

### Camera Pose (원논문 Table 3)

원논문 Table 3. ATE↓, RTE↓, RRE↓. Interp3R는 모든 데이터셋·skip에서 RRE 최고이나, Sintel의 RTE(예: skip=15에서 VDM 0.118 vs Ours 0.202)에서는 뒤진다.

| Dataset | Method       | skip | ATE ↓     | RTE ↓     | RRE ↓     |
| ------- | ------------ | ---- | --------- | --------- | --------- |
| Sintel  | VDM-EVFI     | 1    | 0.319     | 0.127     | 1.314     |
| Sintel  | VDM-EVFI     | 15   | 0.379     | **0.118** | 1.496     |
| Sintel  | **Interp3R** | 1    | **0.224** | 0.111     | **0.907** |
| Sintel  | **Interp3R** | 3    | **0.263** | 0.150     | **0.916** |
| Sintel  | **Interp3R** | 7    | **0.284** | 0.179     | **0.921** |
| Sintel  | **Interp3R** | 15   | **0.302** | 0.202     | **1.079** |
| Bonn    | **Interp3R** | 1    | **0.007** | **0.006** | **0.424** |
| Bonn    | **Interp3R** | 15   | **0.009** | **0.006** | **0.494** |
| TUM     | VDM-EVFI     | 15   | 0.006     | 0.003     | 0.450     |
| TUM     | **Interp3R** | 1    | 0.009     | 0.004     | **0.226** |
| TUM     | **Interp3R** | 15   | 0.010     | 0.005     | **0.325** |

On Bonn, Interp3R achieves the best ATE/RTE/RRE at every skip; on TUM, camera translation is tiny for all methods (ATE ≈ 0.006–0.012) so rotation (RRE) dominates, where Interp3R is consistently lowest. VDM-EVFI relies on a >3B-parameter video diffusion model.

### Ablation — Depth on PointOdyssey (원논문 Table 4)

원논문 Table 4. Abs Rel↓, δ<1.25↑.

| Method             | s1 AbsRel ↓ | s1 δ ↑    | s3 AbsRel ↓ | s3 δ ↑    | s7 AbsRel ↓ | s7 δ ↑    | s15 AbsRel ↓ | s15 δ ↑   |
| ------------------ | ----------- | --------- | ----------- | --------- | ----------- | --------- | ------------ | --------- |
| w/o events         | 0.073       | 0.945     | 0.078       | 0.942     | 0.100       | 0.926     | 0.153        | 0.855     |
| w/o time encoding  | 0.107       | 0.901     | 0.104       | 0.909     | 0.106       | 0.913     | 0.117        | 0.898     |
| MonST3R + Interp3R | 0.090       | 0.915     | 0.090       | 0.910     | 0.097       | 0.883     | 0.108        | 0.876     |
| Align3R + Interp3R | **0.069**   | **0.948** | **0.067**   | **0.952** | **0.074**   | **0.948** | **0.099**    | **0.896** |

Without events, depth degrades rapidly as skip grows (0.073 → 0.153 AbsRel), showing event motion cues are vital at large frame gaps. Without time encoding, accuracy drops and the pose ablation (원논문 Table 5) shows RRE on Sintel spiking (0.909 → 2.731 at skip=7). The MonST3R + Interp3R variant confirms plug-and-play compatibility.

## 💡 Insights & Impact

- Pointmap-based models are limited to discrete capture times; events fill the "blind time" between frames for temporally continuous depth and pose.
- Zero-convolution fusion progressively transports source pointmaps to target time, preserving the backbone's priors and training stability.
- Two-stage baselines (2D VFI → 3D) amplify interpolation artifacts at object edges; direct 3D interpolation avoids this.

## 🔗 Related Work

- Backbone options [DUSt3R](../foundation/dust3r.md), [MonST3R](monst3r.md), [Align3R](align3r.md); closest event-aided method [EAG3R](eag3r.md); also cites [Stereo4D](stereo4d.md) and [Depth Anything 3](../reconstruction/depth-anything-3.md).

## 📚 Key Takeaways

1. First continuous-time pointmap framework: recovers depth and pose at arbitrary sub-frame instants from frames + events.
2. Outperforms two-stage VFI→3D baselines on most depth/pose metrics, with honest reporting that VDM-EVFI (a >3B diffusion model) wins several Bonn δ and Sintel RTE numbers.
3. Plug-and-play across pointmap backbones and generalizes to real data despite synthetic-only training.

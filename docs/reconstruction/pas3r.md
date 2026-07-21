# PAS3R: Pose-Adaptive Streaming 3D Reconstruction for Long Video Sequences (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Lanbo Xu, Liang Guo, Caigui Jiang, Cheng Wang
- **Institution**: State Key Laboratory of Human-Machine Hybrid Augmented Intelligence, Institute of Artificial Intelligence and Robotics, Xi'an Jiaotong University; University of East Anglia
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.21436) | [Project Page](https://pas-3r.github.io/PAS3R.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A streaming monocular reconstruction framework that dynamically modulates the state-update learning rate by inter-frame camera motion and image frequency, adds trajectory-consistent training objectives (ATE/RPE/acceleration) and a lightweight online stabilization module, improving long-sequence stability while staying competitive on short sequences.

## 🎯 Key Contributions

1. **Pose-adaptive state update**: Frame importance is estimated from inter-frame camera displacement and image frequency cues, so frames with large viewpoint change exert stronger influence while low-motion frames preserve historical geometry.
2. **Trajectory-consistent training**: Relative pose and acceleration regularization (ATE + RPE + acceleration constraints) improve temporal coherence and reduce trajectory drift in long sequences.
3. **Online spatiotemporal stabilization**: A lightweight inference-time module (One-Euro filtering + Slerp for trajectory, bilateral spatial filtering for point clouds) suppresses jitter and geometric artifacts without increasing memory.

## 🔧 Technical Details

### Pose-Adaptive Modulation

In the Test-Time Training view, the state update is S_t = S_{t−1} − β∇(S_{t−1}, X_t) with β a learning rate. PAS3R computes a camera displacement score s₁ = w₁Δx + w₂Δq (translation and rotation magnitudes) and an image-quality score s₂ from a high-pass-filtered Discrete Fourier Transform of the grayscale frame, combining them as s = s₁·s₂ (clipped at 1.0) to set the per-frame learning-rate weight.

### Trajectory-Consistent Losses

The pose loss combines Absolute Trajectory Error (ATE), Relative Pose Error (RPE), and an acceleration stabilization constraint (penalizing second-order trajectory differences), each weighted. The total loss adds a confidence-aware 3D regression loss and an RGB loss (following CUT3R).

### Online Stabilization

Temporal: One-Euro filtering of predicted translations and Slerp of rotation quaternions. Spatial: online bilateral filtering of point clouds to smooth planar regions while preserving edges.

### Setup

Constant-memory streaming compatible with CUT3R/TTT3R architectures; experiments on a server with 8 NVIDIA RTX 4090 GPUs. Baselines: CUT3R, TTT3R, IVGGT, Mem4D.

## 📊 Results

Pose on ScanNet, Sintel, TUM-dynamic; depth on Sintel, Bonn, KITTI; reconstruction on 7-Scenes. Long-horizon behavior (up to 1000 frames) is emphasized via curves (Figs. 6–8, values not printed in text).

### Camera Pose — Short Sequences

원논문 Table 1 (Sintel, Tum). Lower is better; bold = best in source.

| Method   | Sintel ATE↓ | RPE trans↓ | RPE rot↓ | Tum ATE↓  | RPE trans↓ | RPE rot↓  |
| -------- | ----------- | ---------- | -------- | --------- | ---------- | --------- |
| Mem4D    | 0.263       | 0.091      | 0.812    | 0.061     | 0.020      | 0.517     |
| CUT3R    | 0.209       | 0.071      | 0.632    | 0.047     | 0.015      | 0.448     |
| TTT3R    | 0.210       | 0.090      | 0.730    | 0.029     | 0.013      | 0.379     |
| IVGGT    | 0.237       | 0.096      | 0.806    | 0.027     | 0.012      | **0.313** |
| **Ours** | 0.211       | **0.053**  | 0.688    | **0.027** | **0.011**  | 0.475     |

PAS3R attains the best translational RPE on both datasets and ties the best ATE on Tum, but its rotational RPE is higher than the best baseline in some cases (e.g., Tum 0.475 vs IVGGT 0.313).

### Depth — Short Sequences

원논문 Table 2 (Sintel, Bonn, Kitti). Abs Rel lower is better, δ higher is better.

| Method   | Sintel AbsRel↓ | Sintel δ↑ | Bonn AbsRel↓ | Bonn δ↑  | Kitti AbsRel↓ | Kitti δ↑ |
| -------- | -------------- | --------- | ------------ | -------- | ------------- | -------- |
| Mem4D    | 0.520          | 43.1      | 0.072        | 95.7     | 0.140         | 82.0     |
| CUT3R    | 0.432          | 47.0      | 0.077        | 93.8     | 0.122         | 87.6     |
| TTT3R    | 0.406          | 48.8      | 0.069        | 95.4     | 0.114         | 90.6     |
| IVGGT    | **0.329**      | **66.0**  | **0.059**    | **97.4** | 0.185         | 69.8     |
| **Ours** | 0.407          | 48.7      | 0.064        | 96.6     | **0.115**     | **91.4** |

IVGGT leads on Sintel and Bonn Abs Rel; PAS3R is best on KITTI δ<1.25 and competitive elsewhere, showing long-sequence stability gains do not compromise short-sequence accuracy.

### Ablation

원논문 Table 3. Tum (1000 frames), Bonn (500 frames), 7-Scene (400 frames).

| Method                             | ATE↓    | RPE trans↓  | RPE rot↓ | AbsRel↓    | δ<1.25↑ | Acc↓      | Comp↓ | NC↑       |
| ---------------------------------- | ------- | ----------- | -------- | ---------- | ------- | --------- | ----- | --------- |
| w/o pose-adaptive state update     | 0.10854 | 0.00374     | 0.46871  | 0.0757     | 95.24   | 0.048     | 0.028 | 0.563     |
| w/o trajectory-consistent training | 0.05616 | 0.00459     | 0.59215  | 0.0710     | 95.35   | 0.023     | 0.021 | 0.562     |
| w/o spatiotemporal stabilization   | 0.04980 | 0.01138     | 0.61098  | 0.0710     | 95.36   | 0.019     | 0.019 | 0.561     |
| Full Method                        | 0.05214 | **0.00354** | 0.52595  | **0.0709** | 95.35   | **0.018** | 0.021 | **0.564** |

Removing the stabilization module slightly improves some isolated metrics (e.g., 7-Scene Acc 0.019) but degrades overall trajectory stability, showing its complementary role.

## 💡 Insights & Impact

- **Geometric novelty as update signal**: PAS3R argues that a frame's influence should scale with the geometric novelty it introduces, unlike attention/similarity-driven updates (TTT3R) that ignore the magnitude of viewpoint change.
- **Original-space depth alignment**: PAS3R performs best in the original (un-aligned) depth setting, indicating its predicted geometry is already well aligned with ground truth without post-hoc scaling.
- **Stability over long horizons**: The reported advantage grows with sequence length — competing methods drift while PAS3R's trajectory error grows more slowly.
- **Limitations**: Current benchmarks provide limited coverage of diverse long video streams, and rotational trajectory accuracy can be further improved.

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The recurrent-state streaming base whose loss definitions PAS3R inherits and whose update mechanism it improves.
- **[TTT3R](ttt3r.md)**: Introduced cross-attention learning rates; PAS3R adds explicit pose-based modulation.
- **[InfiniteVGGT](infinitevggt.md)**: KV-cache long-sequence baseline (referred to as IVGGT).
- **[DUSt3R](../foundation/dust3r.md)**, **[VGGT](vggt.md)**, **[Fast3R](fast3r.md)**: Feed-forward reconstruction foundations discussed for their online limitations.
- **[MUSt3R](must3r.md)**: A DUSt3R multi-view extension cited among follow-ups.

## 📚 Key Takeaways

1. PAS3R modulates streaming state updates by camera motion and image-frequency cues so novel viewpoints influence the state more strongly and stable frames preserve history.
2. Trajectory-consistent training (ATE/RPE/acceleration) plus online One-Euro/Slerp/bilateral stabilization improve long-horizon coherence at constant memory.
3. It achieves the best translational RPE on Sintel/Tum and best KITTI depth δ while remaining competitive elsewhere; rotational RPE remains a weak point.
4. Long-sequence stability is the primary advantage, with short-sequence performance preserved.

# DriveVGGT: Calibration-Constrained Visual Geometry Transformers for Multi-Camera Autonomous Driving (arXiv preprint (2025-11))

![drivevggt — architecture](https://arxiv.org/html/2511.22264v2/x1.png)

_Model Comparisons (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Xiaosong Jia, Yanhao Liu, Yu Hong, Renqiu Xia, Junqi You, Bin Sun, Zhihui Hao, Junchi Yan
- **Institution**: Shanghai Jiao Tong University; Shanghai Innovation Institute; Institute of Trustworthy Embodied AI, Fudan University; Li Auto Inc.
- **Venue**: arXiv preprint (2025-11)
- **Links**: [Paper](https://arxiv.org/abs/2511.22264) | [Code](https://github.com/SII-skyboard/DriveVGGT)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A scale-aware VGGT variant for multi-camera autonomous driving that bakes in three domain priors — sparse spatial overlap, calibrated geometric constraints, and rigid extrinsic constancy — via a Temporal Video Attention module, a Multi-camera Consistency Attention module, and factorized pose/ego-motion heads, cutting inference latency by 49.3% while improving pose and depth over vanilla VGGT on long sequences.

## 🎯 Key Contributions

1. **AD-prior-aware framework**: Explicitly integrates three autonomous-driving priors that vanilla VGGT ignores — minimal multi-view overlap, absolute inter-camera calibration, and rigidly fixed camera extrinsics.
2. **Temporal Video Attention (TVA)**: Processes each camera stream independently in the temporal domain, avoiding the O((M×T)²) cost of global attention over non-overlapping cross-view regions.
3. **Multi-camera Consistency Attention (MCA)**: Injects calibrated relative-pose embeddings and uses spatiotemporal window attention to fuse cross-view information at linear complexity, with a scale head for absolute metric-scale reconstruction.
4. **Factorized decoding**: Splits pose decoding into a sequential pose head and an ego-motion head (via factorized pooling) so predicted trajectories stay physically consistent with the rigid sensor rig.

## 🔧 Technical Details

### Architecture (three-stage pipeline)

- **TVA**: for M cameras each with N frames, attention runs only within a camera's own stream, producing sequential pose tokens aligned to that camera's first frame plus depth tokens.
- **Relative pose embedding**: camera translations are zero-mean normalized across the rig; a 10-D vector P_cam(j) = concat(T_norm, R, K) per camera is projected by a small MLP into a static geometric reference token (computed once per sensor configuration).
- **MCA**: fuses TVA features with the calibrated pose embeddings, then applies spatiotemporal window attention over a temporal window of size 2k+1 across all M cameras (O(M·W·N²·d) vs global O(M·N²·d)). Factorized pooling averages sequential pose tokens across cameras per frame (ego-motion) and averages relative pose tokens over time (extrinsics).
- **Prediction heads**: reuses the VGGT camera head as a Relative Pose Head (time-invariant extrinsics/intrinsics) and a Sequential Pose Head (per-frame extrinsics), composed as G_global = G_seq × G_rel; a DPT depth head; and a Scale Head that estimates scale = Avg(Σ_j T_real^rel(j) / T_norm^rel(j)) to convert normalized geometry to metric.

### Training

- Loss L_total = λ₁·L_depth + λ₂·(L_rel + L_seq) with λ₁ = 0.1, λ₂ = 1.0; L_depth uses depth + gradient + uncertainty terms (as VGGT), pose losses use Huber.
- nuScenes (1,000 scenes; 700 train / 150 val; keyframes at 2 Hz), images resized 1600×900 → 518×280. Dense depth GT built by a two-stage LiDAR densification pipeline (spatiotemporal point aggregation + depth completion). Training: 3–10 frames × multi-camera (18–60 images) for 20 epochs (1000 iters/epoch, LR 2e-4), then freeze aggregator and fine-tune 5 epochs at LR 1e-5. Window size k = 3 (window = 3).
- DriveVGGT is a plugin: it wraps either VGGT or fastVGGT as the TVA base geometry transformer — reported as DriveVGGT(VGGT) and DriveVGGT(fastVGGT).

## 📊 Results

Evaluated on nuScenes at 15 / 25 / 35 frames (90 / 150 / 210 images). Baselines VGGT, StreamVGGT, fastVGGT; relative-pose embedding is added to VGGT and fastVGGT to isolate its effect.

### Multi-camera pose estimation (AUC↑)

원논문 Table 1. DriveVGGT(VGGT) is best, especially at 210 images. Adding relative poses degrades vanilla VGGT and fastVGGT but improves DriveVGGT. StreamVGGT runs OOM beyond 15 frames.

| Method              | Rel poses | f15 AUC30 | f25 AUC30 | f35 AUC30 | f35 AUC15 |
| ------------------- | --------- | --------- | --------- | --------- | --------- |
| VGGT                | ✗         | 0.8531    | 0.7866    | 0.6871    | 0.5477    |
| StreamVGGT          | ✗         | 0.7005    | OOM       | OOM       | OOM       |
| fastVGGT            | ✗         | 0.8246    | 0.7707    | 0.6830    | 0.5357    |
| VGGT                | ✓         | 0.8164    | 0.7403    | 0.6445    | 0.5002    |
| fastVGGT            | ✓         | 0.7915    | 0.7321    | 0.6477    | 0.4976    |
| **DriveVGGT(VGGT)** | ✓         | 0.8635    | 0.8010    | 0.7200    | 0.5811    |
| DriveVGGT(fastVGGT) | ✓         | 0.8534    | 0.7844    | 0.6995    | 0.5510    |

### Multi-camera depth estimation (Abs Rel↓ / δ3↑)

원논문 Table 2. DriveVGGT(fastVGGT) is best on Abs Rel at 35 frames (long sequences); at 15 frames StreamVGGT has the lowest Abs Rel.

| Method                  | Rel | f15 AbsRel/δ3 | f25 AbsRel/δ3 | f35 AbsRel/δ3 |
| ----------------------- | --- | ------------- | ------------- | ------------- |
| VGGT                    | ✗   | 0.3666/0.8791 | 0.3654/0.8817 | 0.3605/0.8858 |
| StreamVGGT              | ✗   | 0.3636/0.8811 | OOM           | OOM           |
| fastVGGT                | ✗   | 0.3684/0.8782 | 0.3693/0.8794 | 0.3660/0.8825 |
| VGGT                    | ✓   | 0.3718/0.8779 | 0.3700/0.8805 | 0.3647/0.8844 |
| fastVGGT                | ✓   | 0.3655/0.8784 | 0.3691/0.8795 | 0.3658/0.8826 |
| DriveVGGT(VGGT)         | ✓   | 0.3805/0.8747 | 0.3705/0.8825 | 0.3601/0.8892 |
| **DriveVGGT(fastVGGT)** | ✓   | 0.3655/0.8854 | 0.3601/0.8894 | 0.3539/0.8935 |

### Inference time (ms↓)

원논문 Table 3. DriveVGGT(VGGT) at 35 frames is 4907 ms vs VGGT's 9666 ms (~49.3% reduction). DriveVGGT(fastVGGT) is slower than DriveVGGT(VGGT) because fastVGGT's token-aggregation adds overhead when each per-camera batch is small (see note).

| Method              | f15  | f25  | f35  |
| ------------------- | ---- | ---- | ---- |
| VGGT                | 2268 | 5241 | 9666 |
| StreamVGGT          | 6916 | OOM  | OOM  |
| fastVGGT            | 1950 | 3341 | 4949 |
| **DriveVGGT(VGGT)** | 1836 | 3294 | 4907 |
| DriveVGGT(fastVGGT) | 2390 | 3823 | 5043 |

### Ablations

- **Components** (원논문 Table 4, frame=25): TVA-only baseline collapses on multi-camera (AUC 0.039); adding relative-pose embedding restores pose (AUC 0.7855); full DriveVGGT reaches AUC 0.8010 / AbsRel 0.3705.
- **Window size** (원논문 Table 5, frame=25): k=3 (window 3) gives AUC 0.8010 at 3294 ms; larger windows give marginal AUC gains (size5 0.8033, size7 0.8087) at much higher cost (4924, 7263 ms), validating that global attention is unnecessary.
- **Scale head** (원논문 Table 6, frame=15): the least-squares alignment gives AbsRel 0.3805 / δ3 0.8747 while the scale-based method gives 0.3666 / 0.7412, indicating the predicted scale transforms depths to real-world scale.

## 💡 Insights & Impact

- The core argument is that vanilla VGGT's global attention is both inefficient and mismatched for AD rigs where cross-view overlap is minimal; decoupling intra-camera temporal continuity (TVA) from inter-camera consistency (MCA) removes the O((M×N)²) bottleneck and enables long sequences without OOM (StreamVGGT fails past 15 frames).
- Calibrated extrinsics are treated as first-class geometric priors, letting the model output absolute metric scale — but the relative-pose embedding only helps when the architecture is designed for it: injecting it into vanilla VGGT/fastVGGT degrades their pose accuracy, whereas DriveVGGT's factorized aggregation benefits.
- Being a plugin over any geometry transformer (VGGT or fastVGGT) makes it a general AD extension rather than a single model.

## 🔗 Related Work

- **[VGGT](./vggt.md)**: the global-attention baseline DriveVGGT restructures; used as both a base transformer and comparison.
- **[FastVGGT](./fastvggt.md)**: training-free accelerated VGGT, usable as DriveVGGT's TVA base and a baseline.
- **[StreamVGGT](./streamvggt.md)**: streaming VGGT with memory-cached causal attention; a baseline that hits OOM on long multi-camera sequences.
- **[DUSt3R](../foundation/dust3r.md)** / **[MonST3R](../dynamic/monst3r.md)** / **[Point3R](./point3r.md)** / **[π³](./pi3.md)**: feed-forward reconstruction lineage cited in related work.

## 📚 Key Takeaways

1. DriveVGGT specializes VGGT for multi-camera driving by encoding three AD priors — sparse overlap (TVA), calibrated constraints (MCA + scale head), and rigid extrinsics (factorized pose/ego heads).
2. It reduces 35-frame inference by ~49.3% (4907 ms vs VGGT's 9666 ms) while improving pose AUC and long-sequence depth over vanilla VGGT.
3. It works as a plugin over VGGT or fastVGGT; ablations show relative-pose embedding is essential to its multi-camera gains and a window of k=3 suffices, confirming global attention is unnecessary here.

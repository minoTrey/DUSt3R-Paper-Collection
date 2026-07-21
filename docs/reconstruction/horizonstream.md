# HorizonStream: Long-Horizon Attention for Streaming 3D Reconstruction (arXiv preprint)

## 📋 Overview

- **Authors**: Chong Cheng, Peilin Tao, Nanjie Yao, Guanzhi Ding, Xianda Chen, Yuansen Du, Xiaoyang Guo, Wei Yin, Weiqiang Ren, Qian Zhang, Zhengqing Chen, Hao Wang
- **Institution**: HKUST(GZ), Horizon Robotics, CASIA, CSU
- **Venue**: arXiv preprint (2026-05)
- **Note**: 자체 프로젝트 페이지 BibTeX가 arXiv preprint로 명시. <https://3dagentworld.github.io/horizonstream/>
- **Links**: [Paper](https://arxiv.org/abs/2605.23889) | [Project Page](https://3dagentworld.github.io/horizonstream/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: Formalizes streaming reconstruction as a "geometric evidence influence kernel" and factorizes it — channel-wise decaying linear attention for bounded multi-timescale long-range memory, gated local attention with spatiotemporal RoPE for short-range matching, and metric readout tokens for scale — trained on 48-frame clips and run on sequences beyond 10,000 frames.

## 🎯 Key Contributions

1. **A diagnostic framework**: The evidence influence kernel `K(t, i)` maps evidence at time i to its contribution at time t. Common long-sequence failures are recast as pathological kernel shapes — hard cutoffs (sliding windows), blockwise discontinuities (refresh mechanisms), spike-like attention sinks (causal softmax), and heavy tails (ungated recurrence).
2. **Kernel factorization** `K(t,i) = K_spatial(t,i) · K_time(t,i)`, mapping three requirements to three components.
3. **Geometric Linear Attention**: an O(1) recurrent state with _channel-wise_ learned exponential decay, so different geometric channels get different effective lifetimes.
4. **Geometric Local Attention**: head-wise reliability gating plus 3-axis (time, height, width) RoPE for within-window 3D matching, explicitly designed to suppress attention sinks.
5. **Metric Readout Tokens + relative pose fusion**: scale read from the high-retention channels of the persistent state; pose estimated by consensus over the window rather than by sequential keyframe chaining.

## 🔧 Technical Details

### The Core Argument

Streaming geometry is **temporally heterogeneous**: local 2D-3D correspondences are short-lived and quickly invalidated by motion, while global scale and scene structure must remain reliable over long horizons. Existing architectures organize history purely by recency and impose a uniform propagation rule on all evidence. The paper frames current designs as occupying two extremes of a retention spectrum — sliding windows force immediate forgetting, full attention retains everything permanently — with no bounded, flexible middle.

### Geometric Linear Attention

Derived from a discounted geometric state-estimation objective:

```text
J_t(S) = Σ_i ( Π_{j=i+1..t} γ_j ) ‖Sᵀk_i − v_i‖²,     K_time(t,i) = Π_{j=i+1..t} γ_j
```

With `γ_t ≡ 1` evidence never decays, causing heavy-tailed accumulation and state contamination. With `γ̄ = sup_t |γ_t| < 1` the influence of stale evidence is strictly bounded:

```text
‖qᵀ_t (Π_j γ_j) S_0‖ ≤ ‖q_t‖ · ‖S_0‖_F · γ̄^t → 0
```

The recursive form `J_t(S) = γ_t J_{t-1}(S) + ‖Sᵀk_t − v_t‖²` yields the fixed-state update `S_t = γ_t S_{t-1} + φ(k_t)ṽ_tᵀ`, `o_t = q_tᵀ S_t`.

**Channel-wise retention** replaces the scalar γ:

```text
γ_t = σ(W_γ x_t + b_γ) ∈ (0,1)^d,   S_t = diag(γ_t) S_{t-1} + φ(k_t) ṽ_tᵀ
τ^(c) = −1 / log γ̄^(c)
```

Low-γ channels rapidly revise transient correspondences; high-γ channels preserve structure and metric cues. The paper links this to Test-Time Training — per-frame TTT optimization is costly for ultra-long streams, while TTT with KV binding admits an equivalent linear-attention form — placing the update in the gated-linear-attention family.

### Geometric Local Attention

- **Head-wise output gating**: `g_h = σ(W_g x̄ + b_g)`, `ỹ_h = g_h · y_h`, where x̄ is the mean-pooled window feature. Downweights unreliable heads.
- **Spatiotemporal RoPE**: RoPE extended to three axes with `π = (t+1, y+1, x+1)`, query/key split into three parts and rotated per axis. The temporal index is **periodically reset** to avoid unbounded positional growth; MRT and pose tokens use `π = (0,0,0)`.

### Metric Readout and Pose

A learned token `z_metric` per frame participates in Geometric Linear Attention; a scale head predicts `ŝ = exp(g(z_metric))`, rescaling translation and depth (`t̂ = ŝ·t̂_raw`, `D̂ = ŝ·D̂_raw`). For pose, a transformer head attends jointly over pose tokens in the local window and estimates a consensus relative pose — explicitly avoiding sequential keyframe chaining, where composition errors accumulate. Depth comes from a DPT head with scale injection.

### Architecture and Training

- **ViT-L backbone** initialized from VGGT and DINOv2. Frame blocks do intra-frame self-attention; global blocks combine Geometric Local Attention with Geometric Linear Attention interleaved at specific depths.
- Loss: `L = λ_pose L_pose + λ_depth L_depth + λ_scale L_scale`. Depth loss is SmoothL1 with confidence weighting; scale loss applies only on metric-scale samples.
- Training mirrors streaming inference: **48-frame samples processed sequentially in 21-frame chunks**, with the linear-attention state propagating across chunks. **Pose prediction window W = 10.**
- **Stage 1: 64 A800 GPUs, 60k iterations. Stage 2: 64 H20 GPUs, 40k iterations** with more long-sequence data. AdamW at lr 2e-5, cosine schedule, 2000 warmup steps.
- **24 training datasets** (ScanNet++, Hypersim, Replica, 7Scenes, ARKitScenes, WildRGB-D, Waymo, vKITTI2, Mapillary, MegaDepth, BlendedMVS, DL3DV, CO3Dv2, TartanAir, PointOdyssey, OmniWorld, MatrixCity, and internal long-sequence data among others), temporal strides 1–8. Frames are randomly permuted within a chunk with probability 0.2 while cross-chunk order is preserved.
- **Optional loop closure**: revisited frame pairs retrieved from stored early-layer DINOv2 features, re-fed to estimate local geometric corrections, converted into loop constraints for pose graph optimization (inspired by VGGT-Long).

## 📊 Results

**Evaluation caveat carried from the paper**: vKITTI2, 7Scenes, and Waymo are in the training data (Waymo evaluation uses unseen segments). All sequences are evaluated at full length without subsampling.

### KITTI ATE ↓ — sequences 00–05

원논문 Table 1. "–" denotes OOM or repeated tracking failure. LoGeR\* is the optimization-based LoGeR variant. Sequence metadata: 00 (4542 fr, 3.7 km), 01 (1101 fr, 2.5 km), 02 (4661 fr, 5.1 km), 03 (801 fr, 0.6 km), 04 (271 fr, 0.4 km), 05 (2761 fr, 2.2 km).

| Method            | 00     | 01     | 02     | 03     | 04     | 05     |
| ----------------- | ------ | ------ | ------ | ------ | ------ | ------ |
| MASt3R-SLAM       | –      | 530.37 | –      | 18.87  | 88.98  | 159.43 |
| VGGT-SLAM         | –      | 607.16 | –      | 169.83 | 13.12  | –      |
| COLMAP            | 139.12 | 3.83   | 71.99  | 1.46   | 112.77 | 20.37  |
| MASt3R-SfM        | –      | 463.52 | –      | 15.80  | 41.44  | 150.39 |
| DPVO              | 113.11 | 16.60  | 113.01 | 2.46   | 0.98   | 59.34  |
| DROID-SLAM        | –      | 82.81  | –      | 3.20   | 1.47   | 73.50  |
| VGGT-Long         | 8.64   | 61.21  | 52.72  | 8.78   | 4.20   | 9.88   |
| FastVGGT          | –      | 705.39 | –      | 62.38  | 10.27  | 157.74 |
| LoGeR             | 54.98  | 36.57  | 36.20  | 4.27   | 1.62   | 33.41  |
| LoGeR\*           | 26.19  | 41.26  | 32.21  | 5.02   | 1.62   | 22.65  |
| LoGeR w/o refresh | 166.05 | 631.14 | 226.65 | 66.09  | 4.55   | 125.16 |
| CUT3R w/o refresh | 185.89 | 651.52 | 296.98 | 148.06 | 22.17  | 155.61 |
| CUT3R w/ refresh  | 190.38 | 90.59  | 264.39 | 20.40  | 7.31   | 92.25  |
| TTT3R w/o refresh | 190.93 | 546.84 | 218.77 | 105.28 | 11.62  | 153.12 |
| TTT3R w/ refresh  | 119.94 | 99.59  | 238.07 | 16.83  | 3.98   | 36.38  |
| STream3R          | 190.98 | 681.95 | 301.40 | 158.25 | 102.73 | 159.85 |
| StreamVGGT        | 191.93 | 653.06 | 303.35 | 157.50 | 108.24 | 160.46 |
| InfiniteVGGT      | 167.17 | 533.36 | 272.99 | 149.18 | 58.86  | 127.50 |
| LongStream        | 92.55  | 46.01  | 134.70 | 3.81   | 1.95   | 84.69  |
| Lingbot-map       | 30.80  | 64.74  | 82.29  | 2.49   | 0.85   | 16.55  |
| **Ours**          | 26.40  | 20.62  | 84.62  | 5.15   | 0.62   | 12.82  |
| **Ours w/ LC**    | 13.91  | 20.62  | 69.43  | 5.15   | 0.62   | 6.86   |

### KITTI ATE ↓ — sequences 06–10 and average

원논문 Table 1, continued. Sequence metadata: 06 (1101 fr, 1.2 km), 07 (1101 fr, 0.7 km), 08 (4071 fr, 3.2 km), 09 (1591 fr, 1.7 km), 10 (1201 fr, 0.9 km).

| Method            | 06     | 07    | 08     | 09     | 10     | Avg.      |
| ----------------- | ------ | ----- | ------ | ------ | ------ | --------- |
| MASt3R-SLAM       | 92.00  | –     | 263.75 | –      | 153.07 | 186.64    |
| VGGT-SLAM         | –      | –     | –      | –      | 211.82 | 250.48    |
| COLMAP            | 10.95  | 7.80  | 21.72  | 21.19  | 4.52   | 37.79     |
| MASt3R-SfM        | 136.14 | 71.69 | –      | 176.36 | 69.50  | 140.60    |
| DPVO              | 55.91  | 19.30 | 110.63 | 74.55  | 13.71  | 52.69     |
| DROID-SLAM        | 61.10  | 18.41 | 104.22 | 89.49  | 22.19  | 50.71     |
| VGGT-Long         | 4.67   | 2.66  | 72.98  | 31.84  | 27.71  | 25.94     |
| FastVGGT          | 124.43 | 69.27 | –      | 190.10 | 194.75 | 189.29    |
| LoGeR             | 11.78  | 13.33 | 22.92  | 17.89  | 8.06   | 21.91     |
| LoGeR\*           | 5.49   | 5.04  | 21.96  | 9.03   | 9.44   | 16.35     |
| LoGeR w/o refresh | 98.32  | 12.38 | 203.24 | 127.28 | 185.19 | 167.82    |
| CUT3R w/o refresh | 132.54 | 77.03 | 238.39 | 205.94 | 193.39 | 209.78    |
| CUT3R w/ refresh  | 67.54  | 22.48 | 145.08 | 67.42  | 40.00  | 91.62     |
| TTT3R w/o refresh | 132.94 | 70.95 | 180.57 | 211.01 | 133.00 | 177.73    |
| TTT3R w/ refresh  | 47.20  | 11.62 | 107.33 | 86.96  | 33.58  | 72.86     |
| STream3R          | 135.03 | 90.37 | 261.15 | 216.31 | 207.49 | 227.77    |
| StreamVGGT        | 133.71 | 89.00 | 263.95 | 216.69 | 209.80 | 226.15    |
| InfiniteVGGT      | 100.54 | 78.77 | 196.66 | 199.25 | 138.04 | 183.85    |
| LongStream        | 23.12  | 14.93 | 62.07  | 85.61  | 21.48  | 51.90     |
| Lingbot-map       | 6.27   | 8.92  | 39.32  | 17.99  | 7.96   | 25.29     |
| **Ours**          | 4.59   | 5.49  | 19.49  | 25.73  | 11.71  | 19.75     |
| **Ours w/ LC**    | 6.50   | 2.67  | 19.49  | 23.86  | 11.71  | **16.44** |

Two observations the numbers force. First, the refresh/no-refresh pairs are the paper's cleanest evidence: CUT3R goes 209.78 → 91.62 and TTT3R 177.73 → 72.86 with periodic reset, and LoGeR 167.82 → 21.91 — which the paper reads as state contamination rather than limited capacity. Second, HorizonStream's own weakest sequence is 02 (84.62, or 69.43 with loop closure), where VGGT-Long (52.72) and LoGeR (36.20) are far ahead; loop closure also _hurts_ on 06 (4.59 → 6.50).

### Cross-Dataset ATE (m) ↓ and Throughput

원논문 Table 2. vKITTI2, Waymo, and ScanNet++ are in-domain training datasets. "GT" in the COLMAP row is as printed in the original.

| Method         | Calib.-free | VKITTI2 | KITTI  | Oxford | ScanNet++ | TUM  | Waymo | FPS ↑ |
| -------------- | ----------- | ------- | ------ | ------ | --------- | ---- | ----- | ----- |
| MASt3R-SLAM    | ✓           | 81.55   | 186.64 | 37.73  | 0.47      | 0.08 | 7.63  | 7.40  |
| VGGT-SLAM      | ✓           | 19.23   | 250.48 | 31.00  | 0.29      | 0.12 | 7.43  | 15.80 |
| COLMAP         | ✓           | 9.59    | 37.79  | 15.57  | GT        | 0.19 | 25.63 | 0.20  |
| MASt3R-SfM     | ✓           | 49.48   | 140.60 | 32.13  | 1.50      | 0.39 | 3.95  | 0.30  |
| DPVO++         | ✗           | 0.38    | 52.69  | 34.03  | 0.91      | 0.10 | 1.35  | 19.30 |
| DROID-SLAM     | ✗           | 1.12    | 50.71  | 31.08  | 0.97      | 0.11 | 6.67  | 13.60 |
| VGGT-Long      | ✓           | 0.91    | 25.94  | 21.90  | 0.13      | 0.08 | 1.78  | 4.80  |
| FastVGGT       | ✓           | 21.52   | 189.29 | 36.58  | 1.56      | 0.42 | 1.28  | 14.20 |
| LoGeR          | ✓           | 1.66    | 21.91  | 18.70  | 0.50      | 0.07 | 0.96  | 16.0  |
| LoGeR\*        | ✓           | 2.45    | 16.35  | 15.79  | 0.43      | 0.08 | 0.55  | 9.1   |
| CUT3R          | ✓           | 47.66   | 209.78 | 32.44  | 1.27      | 0.54 | 9.40  | 19.90 |
| TTT3R          | ✓           | 24.18   | 177.73 | 36.21  | 0.55      | 0.31 | 3.49  | 22.00 |
| STream3R       | ✓           | 68.96   | 227.77 | 37.57  | 1.75      | 0.63 | 42.20 | 8.20  |
| StreamVGGT     | ✓           | 68.51   | 226.15 | 37.25  | 1.70      | 0.63 | 45.10 | 19.10 |
| InfiniteVGGT   | ✓           | 58.63   | 183.85 | 31.82  | 1.66      | 0.21 | 20.56 | 5.30  |
| LongStream     | ✓           | 1.61    | 51.90  | 19.82  | 0.49      | 0.08 | 0.74  | 17.10 |
| Lingbot-map    | ✓           | 1.30    | 25.29  | 15.46  | 0.52      | 0.04 | 1.66  | 11.9  |
| **Ours**       | ✓           | 0.94    | 19.75  | 9.38   | 0.40      | 0.04 | 0.46  | 13.20 |
| **Ours w/ LC** | ✓           | 0.94    | 16.44  | 8.71   | 0.40      | 0.04 | 0.46  | 10.45 |

Note that DPVO++ (calibrated, not calib.-free) still wins vKITTI2 at 0.38 versus 0.94, and VGGT-Long wins ScanNet++ at 0.13 versus 0.40. HorizonStream's strongest showing is Oxford Spires (9.38 / 8.71 versus 15.46 for the best baseline) and Waymo.

### VBR ATE ↓ — Ultra-Long Sequences

원논문 Table 3. Sequence lengths and trajectory distances: colosseo_0 (8815 fr, 1.45 km), campus_0 (12042 fr, 2.73 km), campus_1 (11671 fr, 2.95 km), pincio_0 (11142 fr, 1.27 km), spagna_0 (14141 fr, 1.56 km), diag_0 (10021 fr, 1.02 km), ciampino_1 (18846 fr, 5.20 km).

| Method           | colosseo_0 | campus_0 | campus_1 | pincio_0 | spagna_0 | diag_0 | ciampino_1 | Avg.      |
| ---------------- | ---------- | -------- | -------- | -------- | -------- | ------ | ---------- | --------- |
| VGGT-SLAM        | 101.00     | 93.51    | 71.74    | 66.42    | 57.00    | 33.64  | 124.10     | 78.20     |
| VGGT-Long w/o LC | 81.54      | 118.59   | 98.21    | 53.44    | 46.92    | 30.80  | 170.30     | 85.69     |
| VGGT-Long        | 39.56      | 118.59   | 98.21    | 53.44    | 50.27    | 30.80  | 172.13     | 80.43     |
| LoGeR            | 31.77      | 27.90    | 30.80    | 17.96    | 21.33    | 32.25  | 34.16      | 28.02     |
| LoGeR\*          | 55.32      | 13.27    | 16.79    | 9.18     | 18.32    | 29.45  | 34.32      | 25.24     |
| Pi3-Chunk        | 77.09      | 78.50    | 65.77    | 41.99    | 44.76    | 23.81  | 111.72     | 63.38     |
| CUT3R            | 82.63      | 42.25    | 43.16    | 46.65    | 44.62    | 28.62  | 175.83     | 66.25     |
| TTT3R            | 75.52      | 59.44    | 56.55    | 33.87    | 37.33    | 18.49  | 173.71     | 64.99     |
| InfiniteVGGT     | 83.91      | 123.65   | 100.00   | 70.73    | 56.25    | 31.58  | –          | 91.60     |
| LongStream       | 72.52      | 100.57   | 105.55   | 43.47    | 59.31    | 32.35  | 131.78     | 77.93     |
| Lingbot-map      | 16.70      | 23.61    | 10.37    | 29.37    | 24.29    | 24.12  | 64.24      | 27.53     |
| **Ours**         | 37.42      | 22.46    | 22.49    | 22.63    | 23.52    | 22.46  | 26.10      | 25.30     |
| **Ours w/ LC**   | 12.76      | 28.54    | 8.49     | 17.24    | 23.06    | 24.05  | 17.76      | **18.84** |

Read honestly: without loop closure, HorizonStream's 25.30 average is essentially tied with the **offline optimization-based** LoGeR\* at 25.24 — the offline method is marginally ahead. What distinguishes HorizonStream is consistency (no sequence above 37.42) versus Lingbot-map, which wins three individual sequences outright but blows up to 64.24 on the longest one. With loop closure, HorizonStream takes the average.

### Multi-View Reconstruction — Chamfer Distance ↓ and F1 ↑

원논문 Table 4. Note 7Scenes is part of the training data; the paper also flags that several baselines have inflated mean CD on 7Scenes due to large errors on Chess, Pumpkin, and RedKitchen.

| Method       | ETH3D CD ↓ | ETH3D F1@0.25 ↑ | Oxford CD ↓ | Oxford F1@4 ↑ | 7Sc CD ↓ | 7Sc F1@0.25 ↑ | TUM CD ↓ | TUM F1@0.25 ↑ |
| ------------ | ---------- | --------------- | ----------- | ------------- | -------- | ------------- | -------- | ------------- |
| VGGT-Long    | 0.24       | 0.84            | 6.37        | 0.72          | 6.31     | 0.70          | 0.87     | 0.75          |
| MASt3R-SLAM  | 0.89       | 0.31            | 14.59       | 0.35          | 6.32     | 0.71          | 0.10     | 0.92          |
| VGGT-SLAM    | 0.78       | 0.72            | 11.51       | 0.32          | 6.37     | 0.71          | 0.10     | 0.93          |
| FastVGGT     | 0.50       | 0.70            | 7.97        | 0.63          | 5.99     | 0.69          | 0.07     | 0.94          |
| LoGeR        | **0.09**   | **0.90**        | **1.92**    | 0.85          | 6.81     | 0.71          | **0.06** | **0.96**      |
| StreamVGGT   | 1.86       | 0.14            | 15.45       | 0.27          | 6.23     | 0.66          | 0.39     | 0.59          |
| STream3R     | 1.81       | 0.14            | 15.44       | 0.26          | 6.31     | 0.72          | 0.15     | 0.86          |
| CUT3R        | 0.41       | 0.60            | 8.22        | 0.41          | 6.35     | 0.48          | 1.51     | 0.32          |
| TTT3R        | 0.43       | 0.59            | 9.95        | 0.30          | 6.63     | 0.48          | 0.86     | 0.29          |
| InfiniteVGGT | 0.46       | 0.61            | 9.65        | 0.43          | 6.43     | 0.69          | 0.22     | 0.81          |
| LongStream   | 0.77       | 0.55            | 6.28        | 0.55          | **2.26** | 0.64          | 0.23     | 0.67          |
| Lingbot-map  | 0.37       | 0.68            | 8.69        | 0.43          | 6.33     | 0.72          | 0.08     | 0.94          |
| **Ours**     | 0.32       | 0.74            | 4.97        | **0.89**      | 2.98     | **0.93**      | 0.08     | 0.95          |

HorizonStream is best among **online** methods across these four benchmarks, but the offline LoGeR is ahead on ETH3D and TUM on both metrics, and LongStream has lower 7Scenes CD.

### Video Depth Estimation — KITTI

원논문 Table 5.

| Method       | Abs Rel ↓ | δ < 1.25 ↑ |
| ------------ | --------- | ---------- |
| DUSt3R-GA    | 0.144     | 81.3       |
| MASt3R-GA    | 0.183     | 74.5       |
| MonST3R-GA   | 0.168     | 74.4       |
| VGGT         | 0.061     | **97.0**   |
| Spann3R      | 0.198     | 73.7       |
| CUT3R        | 0.118     | 88.1       |
| Point3R      | 0.136     | 84.2       |
| StreamVGGT   | 0.173     | 72.1       |
| STream3R     | 0.080     | 94.7       |
| InfiniteVGGT | 0.170     | 78.6       |
| LoGeR        | 0.090     | 93.0       |
| LongStream   | 0.120     | 87.0       |
| Lingbot-map  | 0.098     | 90.7       |
| **Ours**     | **0.057** | 94.8       |

Best Abs Rel overall, but VGGT still leads on δ < 1.25 (97.0 vs 94.8) — the two metrics disagree, and the paper's own phrasing is that HorizonStream "approaches the best offline methods."

### Ablation — vKITTI2 ATE ↓ at Three Horizons

원논문 Table 6.

| Variant                             | 80f      | 200f     | 1000f    |
| ----------------------------------- | -------- | -------- | -------- |
| **Full model**                      | **0.42** | **0.71** | **1.20** |
| w/o Geometric Linear Attention      | 0.83     | 2.06     | 5.38     |
| w/o channel-wise gating             | 0.67     | 1.43     | 3.21     |
| replace with TTT-like fast weight   | 0.58     | 1.56     | 3.96     |
| w/o Geometric Local Attention       | 0.78     | 2.64     | 7.46     |
| w/o head-wise output gating         | 0.61     | 1.74     | 4.06     |
| w/o Geometric RoPE, 2D spatial only | 0.64     | 1.22     | 2.58     |
| w/o MRT                             | 0.55     | 1.32     | 3.34     |
| single-token pose, no aggregation   | 0.51     | 1.10     | 2.67     |

Every deficit widens sharply with horizon length — the whole design is about what happens at 1000 frames, not 80. Removing Geometric Local Attention is the single most damaging change at long horizon (7.46 vs 1.20), and replacing channel-wise retention with TTT-like fast weights costs more than removing the gating alone.

### Figure-Only Results

Fig. 6 contains three sub-plots: (a) learned retention spectra `τ = −1/log γ̄` across channels for layers 4, 11, 17, 23, with the y-axis spanning roughly 0.0–3.5; (b) a retention-band ablation replacing the learned spectrum with fixed short/medium/long bands; (c) long-sequence stability of head-wise gating and 3D RoPE. **(b) and (c) print no values**; the reported findings are that any fixed band degrades accuracy and that gating and RoPE are complementary, with removal of either causing error growth over time. The observation given for (a) is that Layer 4 shows broad mid-range retention while Layer 17 develops a sharper long-retention tail.

## 💡 Insights & Impact

### Recency Is Not Relevance

The paper's central reframing is that "recency is a poor proxy for geometric relevance in 3D." Recent evidence may already be invalid — a correspondence broken by motion — while older evidence (global scale, static structure) remains reliable. Every architecture that organizes memory by position in the stream inherits this mismatch, and no amount of window tuning fixes it because the right retention differs _per channel_, not per timestep.

### The Refresh Ablations Are the Best Evidence

Reporting refresh and no-refresh variants of CUT3R, TTT3R, and LoGeR side by side is the most persuasive part of the empirical case. The gaps (209.78→91.62, 177.73→72.86, 167.82→21.91 on KITTI average) show that these methods are held together by periodic amnesia. Discounting stale evidence achieves the same protection without discarding accumulated context at each boundary — which is what makes long-range revisit possible.

### A Bounded Kernel Is a Length-Independent Rule

Because the kernel is local and bounded, it defines a propagation rule that does not depend on sequence length and can be applied repeatedly. This is why 48-frame training generalizes to 10,000+ frames with constant memory and linear time — the model never encounters a regime it was not trained for, in the sense that matters.

### Author-Stated Limitations

1. Pose uses only a 10-frame window; a larger window might improve internal loop-closure ability.
2. On extremely long sequences with repeated revisits, the fixed-size recurrent state still misses fine-grained details.
3. Dynamic foreground objects can corrupt local geometric evidence.
4. The loop-closure module is parameterized separately and its optimization settings could be refined.

## 🔗 Related Work

- [LoGeR](./loger.md) — the chunk-wise hybrid-memory approach and the strongest offline comparison here; note the two papers reach related conclusions (bounded memory, multi-timescale retention) from different directions.
- [TTT3R](./ttt3r.md) — the closest architectural relative; HorizonStream's channel-wise gating is explicitly positioned against its scalar/frame-wise update, and its refresh algorithm is used for baseline evaluation.
- [CUT3R](../dynamic/cut3r.md) — the persistent recurrent state whose ungated form the kernel analysis calls heavy-tailed.
- [Stream3R](./stream3r.md), [StreamVGGT](./streamvggt.md) — the sliding-window / causal-mask designs whose hard-cutoff kernel is the paper's first pathology.
- [Point3R](./point3r.md) — explicit spatial pointer memory; a depth baseline.
- [FastVGGT](./fastvggt.md) — attention-map reuse for offline efficiency; a baseline that fails on long KITTI sequences.
- [VGGT](./vggt.md) — supplies the ViT-L initialization; still the δ<1.25 leader on KITTI depth.
- [VGGT-SLAM](./vggt-slam.md), [MASt3R-SLAM](./mast3r-slam.md) — optimization-based baselines.
- [Spann3R](./spann3r.md), [MonST3R](../dynamic/monst3r.md), [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [Pi3](./pi3.md) — the offline lineage surveyed in the related work.

## 📚 Key Takeaways

1. **The evidence influence kernel is a useful diagnostic.** It puts sliding windows, refresh schemes, causal softmax, and ungated recurrence on one axis and names each failure as a kernel shape.
2. **Retention should be learned per channel.** Correspondences, motion cues, structure, and metric scale need different lifetimes, and a fixed band for all of them measurably degrades accuracy.
3. **Bounded decay replaces periodic reset.** Refresh works by throwing away context; discounting keeps it while preventing contamination.
4. **Long-horizon claims should be read at long horizons.** The ablation gaps are ~1.5× at 80 frames and ~4–6× at 1000 frames.
5. **Streaming is closing on offline but has not passed it.** HorizonStream leads all online methods, ties the offline LoGeR\* on VBR average without loop closure, and still trails VGGT on KITTI δ<1.25 and LoGeR on ETH3D/TUM reconstruction.

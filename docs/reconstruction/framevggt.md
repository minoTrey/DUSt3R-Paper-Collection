# FrameVGGT: Coherence-Preserving Memory for Bounded Streaming Geometry (arXiv preprint (2026-03))

![framevggt — architecture](https://arxiv.org/html/2603.07690v3/x2.png)

_Pipeline of FrameVGGT (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Zhisong Xu, Takeshi Oishi
- **Institution**: Institute of Industrial Science, The University of Tokyo
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.07690)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free bounded-memory framework for streaming geometry that retains history as coherent frame-wise KV segments (plus a sparse anchor tier) instead of isolated tokens, preserving multi-view geometric context for stable long-horizon reconstruction, depth, and pose under fixed KV-cache budgets.

## 🎯 Key Contributions

1. **Retention granularity as a design axis**: Argues that bounded streaming geometry depends on how memory is organized, not just its size — coherent frame-level context beats fragmented token subsets.
2. **Diagnostics for token-level failure**: Identifies context thinning, spatio-temporal fragmentation, and directional concentration under token-level retention, with a directional-contrast statistic Δₖ and a variance-decomposition bound explaining why frame-level retention suppresses collapse.
3. **Two-tier memory**: A mid-term memory bank with farthest-first complementary segment selection in retrieval space, plus a sparse anchor tier for persistent long-range references (first frame always kept).
4. **Inference-time, no retraining**: Applied purely at inference under a resource-controlled protocol with fixed weights, sampling, and pipeline.

## 🔧 Technical Details

### Frame-Level Memory Units

- Each frame's per-layer KV segment is summarized by an ℓ2-normalized mean key (retrieval-space proxy) while the full KV entries are retained; inter-segment dissimilarity is cosine distance of mean keys.
- Mid-term bank keeps a subset minimizing the worst-case coverage gap (a farthest-first / k-center objective), approximated online by greedy farthest-first selection from the most recent segment. Selection is per-layer.

### Sparse Anchor Memory

- Anchor promotion gated by temporal spacing (gap G), a reliability score Φ(i) = qᵢ·sᵢ (confidence × Laplacian sharpness), and novelty ν(i) vs existing anchor pose signatures; FIFO applies only to historical anchors so the first-frame reference is never evicted.

### Protocol

- Mid-term capacity M swept over {12, 16, 20, 24}; timescale-separation diagnostic compares 24 mid-term + 0 anchor vs 20 mid-term + 4 anchor under equal budget. Baselines marked * are contemporaneous token-level streaming methods. Single NVIDIA RTX A6000 GPU.
- Reconstruction evaluated on 7-Scenes, NRGBD (up to 1000 frames, stride 2) and Long3D (2k–10k frames, point clouds downsampled to 2%).

## 📊 Results

### 3D Reconstruction on 7-Scenes & NRGBD (mean)

원논문 Table 1. Acc/Comp ↓, NC ↑. Mean 값만 발췌 (원문은 median 병기).

| Method       | 7Sc Acc ↓ | 7Sc Comp ↓ | 7Sc NC ↑  | NRGBD Acc ↓ | NRGBD Comp ↓ | NRGBD NC ↑ |
| ------------ | --------- | ---------- | --------- | ----------- | ------------ | ---------- |
| CUT3R        | 0.181     | 0.095      | 0.525     | 0.322       | 0.128        | 0.553      |
| Point3R      | 0.063     | 0.031      | 0.559     | 0.113       | 0.037        | 0.621      |
| TTT3R        | 0.060     | 0.028      | 0.560     | 0.161       | 0.093        | 0.602      |
| XStreamVGGT  | 0.105     | 0.048      | 0.556     | 0.128       | 0.043        | 0.621      |
| InfiniteVGGT | 0.041     | 0.024      | 0.561     | 0.078       | 0.035        | 0.647      |
| OVGGT*       | 0.033     | 0.020      | 0.560     | 0.056       | 0.032        | 0.635      |
| Ours (20)    | **0.027** | **0.018**  | 0.563     | 0.053       | 0.033        | 0.661      |
| Ours (24)    | 0.028     | 0.019      | **0.564** | 0.054       | **0.030**    | **0.670**  |

### 3D Reconstruction on Long3D (2k–10k frames)

원논문 Table 2. Best in bold.

| Method       | Acc ↓     | Accmed ↓  | Comp ↓    | Compmed ↓ | NC ↑      | NCmed ↑   |
| ------------ | --------- | --------- | --------- | --------- | --------- | --------- |
| CUT3R        | 3.217     | 2.235     | 1.605     | 1.351     | 0.500     | 0.491     |
| TTT3R        | 2.964     | 2.310     | 2.265     | 1.805     | 0.507     | 0.514     |
| InfiniteVGGT | 2.138     | 1.728     | **0.963** | **0.364** | 0.513     | 0.526     |
| OVGGT*       | 2.148     | 1.687     | 1.594     | 0.574     | 0.526     | 0.530     |
| Ours         | **1.698** | **1.331** | 1.032     | 0.433     | **0.536** | **0.540** |

### Video Depth on Bonn

원논문 Table 5.

| Method       | Abs Rel ↓  | δ < 1.25 ↑ |
| ------------ | ---------- | ---------- |
| CUT3R        | 0.0831     | 0.9402     |
| Point3R      | 0.0809     | 0.9513     |
| TTT3R        | 0.0752     | 0.9587     |
| XStreamVGGT  | 0.0807     | 0.9697     |
| InfiniteVGGT | 0.0560     | 0.9801     |
| OVGGT*       | 0.0658     | 0.9558     |
| Ours (24)    | **0.0512** | 0.9799     |

### Camera Pose on TUM

원논문 Table 7.

| Method       | ATE ↓      | RPEt ↓     | RPEr ↓    |
| ------------ | ---------- | ---------- | --------- |
| CUT3R        | 0.1089     | 0.0148     | 0.619     |
| Point3R      | 0.1387     | 0.0369     | 2.347     |
| TTT3R        | 0.0620     | 0.0147     | 0.618     |
| XStreamVGGT  | 0.0728     | 0.0262     | 0.580     |
| InfiniteVGGT | 0.0478     | 0.0138     | 0.350     |
| OVGGT*       | 0.0561     | 0.0215     | 0.448     |
| Ours (24)    | **0.0385** | **0.0133** | **0.336** |

## 💡 Insights & Impact

- **Coherence over capacity**: Frame-level retention preserves within-frame structure and cross-view compatibility, yielding better accuracy–memory frontiers than token-level baselines with much smaller footprints (1.9–3.7 GB for 12–24 blocks vs InfiniteVGGT 6.9 GB, XStreamVGGT 10.3 GB).
- **Complementary beats recent**: Recent-K ablations (Tables 4/6/8) show reserving memory for the latest frames degrades reconstruction, depth, and pose — complementary mid-term coverage matters more than adjacent-frame continuity.
- **Anchors help in degraded regimes**: Sparse anchors mainly improve robustness under blur, occlusion, or weak parallax; anchor-only baselines (FIFO/random/uniform) underperform.
- **Task sensitivity differs**: Video depth is less memory-sensitive (much support is local) than reconstruction and pose, which benefit more from added mid-term capacity with diminishing returns.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The streaming backbone family whose KV cache FrameVGGT bounds.
- **[CUT3R](../dynamic/cut3r.md)**, **[TTT3R](ttt3r.md)**, **[Point3R](point3r.md)**: Implicit-state and explicit-memory streaming baselines.
- **[Evict3R](evict3r.md)**: Token-level eviction cited as a contrasting granularity.
- **[Long3R](long3r.md)**, **[WinT3R](wint3r.md)**, **[VGGT-Long](vggt-long.md)**: Long-sequence / windowed / chunk-based streaming references.
- **[Depth Anything 3](depth-anything-3.md)**, **[MapAnything](mapanything.md)**: Cited feed-forward geometry models.

## 📚 Key Takeaways

1. FrameVGGT reframes bounded streaming geometry as a memory-organization problem: keep coherent frame-wise KV segments rather than fragmented tokens.
2. A farthest-first mid-term bank plus a gated sparse anchor tier preserves complementary multi-view coverage and long-range references under a fixed budget, with theory linking within-group dispersion to reduced attention concentration.
3. Across 7-Scenes/NRGBD/Long3D reconstruction, Bonn depth, and TUM pose, the method achieves the best accuracy–memory frontier at a fraction of the KV-cache footprint of token-level streaming baselines.

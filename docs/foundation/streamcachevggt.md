# StreamCacheVGGT: Streaming Visual Geometry Transformers with Robust Scoring and Hybrid Cache Compression (arXiv preprint 2026-04)

## 📋 Overview

- **Authors**: Xuanyi Liu, Chunan Yu, Deyi Ji, Qi Zhu, Lingyun Sun, Xuanfu Li, Jin Ma, Tianrun Chen, Lanyun Zhu
- **Institution**: KOKONI 3D, Moxin Technology; Peking University; Nanjing University of Science and Technology; University of Science and Technology of China; Zhejiang University; Huawei; Tongji University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.15237)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free framework for constant-cost O(1) streaming 3D reconstruction that replaces pure KV-cache eviction with two modules: Cross-Layer Consistency-Enhanced Scoring (CLCES) for noise-robust token importance, and Hybrid Cache Compression (HCC), a three-tier retain/merge/evict triage that fuses moderately important tokens instead of deleting them.

## 🎯 Key Contributions

1. **Diagnosis of pure eviction**: Two failure modes — single-layer scoring noise (FFN-residual proxies are susceptible to layer-specific activation noise under FlashAttention) and information destruction from binary token deletion (textureless tokens individually fall below threshold but collectively encode structural priors).
2. **CLCES**: Tracks a token's relative importance _rank_ across a sliding window of layers and, via order-statistical analysis against a uniform null, rewards rank-stability — multiplicatively fusing the consistency reward with the raw score so a token needs both base importance and cross-layer stability.
3. **HCC**: A three-tier triage (retain / merge / evict) that absorbs moderately salient tokens into retained anchors via importance-weighted nearest-neighbor assignment on the key-vector manifold, interpreted as a minimum-variance unbiased estimator of the underlying feature.
4. **Compatibility**: Fully integrates with Dynamic Anchor Protection (DAP) and strictly respects per-layer cache budgets.

## 🔧 Technical Details

### Pipeline

Per frame: (1) compute raw FFN-residual scores, (2) apply CLCES to obtain enhanced scores, (3) Gaussian spatial smoothing, (4) HCC three-tier triage, (5) enforce DAP protection. Enhanced score: `ŝ_i = s_i·(1 + λ·Cons_i)`; consistency `Cons_i = max(0, 1 − σ_i·√12)` where σ_i is the std of normalized ranks over the window. Fused key/value are score-weighted convex combinations; when multiple candidates map to one target, fusion is applied sequentially with the target score accumulated.

### Configuration

- CLCES window W = 5, consistency weight λ = 0.5; HCC merge ratio r_m = 0.15; cache budget B = 200K; smoothing α = 0.5; hybrid-scoring balance β = 0.5; DAP τ = 0.2, η = 0.05, K_max = 3.
- Frozen DINOv2 backbone; single Huawei Ascend 910B2 NPU.
- Evaluated on 7-Scenes, NRGBD, ETH3D, Bonn, KITTI; sequences of 100–1000 frames.

## 📊 Results

### 3D reconstruction on 7-Scenes (200 frames)

원논문 Table 1. Acc·Comp 낮을수록, NC 높을수록 좋음. OVGGT는 NC에서 근소 우위(0.5871 vs 0.5865 mean).

| Method       | Acc Mean ↓ | Acc Med ↓  | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑  | NC Med ↑   |
| ------------ | ---------- | ---------- | ----------- | ---------- | ---------- | ---------- |
| Spann3R      | 0.215      | 0.131      | 0.122       | 0.063      | 0.535      | 0.550      |
| CUT3R        | 0.087      | 0.048      | 0.045       | 0.014      | 0.566      | 0.601      |
| Point3R      | 0.041      | 0.019      | 0.023       | 0.006      | 0.579      | 0.622      |
| TTT3R        | 0.027      | 0.015      | 0.023       | 0.005      | 0.582      | 0.627      |
| StreamVGGT   | 0.038      | 0.014      | 0.029       | 0.007      | 0.583      | 0.628      |
| Evict3R†     | 0.037      | 0.013      | 0.027       | 0.007      | 0.584      | 0.631      |
| InfiniteVGGT | 0.046      | 0.016      | 0.031       | 0.008      | 0.582      | 0.627      |
| OVGGT        | 0.0237     | 0.0084     | 0.0214      | 0.0052     | **0.5871** | **0.6352** |
| Ours         | **0.0232** | **0.0080** | **0.0210**  | **0.0049** | 0.5865     | 0.6343     |

(Evict3R without budget matching runs OOM on this setting.)

### 3D reconstruction on NRGBD (100 frames)

원논문 Table 2. OVGGT가 Acc mean에서 근소 우위(0.0220 vs 0.0222); Ours는 Comp·NC 최고.

| Method       | Acc Mean ↓ | Acc Med ↓ | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑  | NC Med ↑   |
| ------------ | ---------- | --------- | ----------- | ---------- | ---------- | ---------- |
| Spann3R      | 0.111      | 0.069     | 0.045       | 0.015      | 0.636      | 0.733      |
| CUT3R        | 0.039      | 0.024     | 0.013       | 0.004      | 0.645      | 0.748      |
| Point3R      | 0.046      | 0.028     | 0.016       | 0.004      | 0.662      | 0.775      |
| TTT3R        | 0.031      | 0.019     | 0.012       | 0.004      | 0.650      | 0.756      |
| StreamVGGT   | 0.024      | 0.014     | 0.013       | 0.003      | 0.663      | 0.777      |
| Evict3R      | 0.025      | 0.015     | 0.013       | 0.003      | 0.664      | 0.781      |
| Evict3R†     | 0.031      | 0.020     | 0.013       | 0.003      | 0.665      | 0.791      |
| InfiniteVGGT | 0.035      | 0.022     | 0.014       | 0.003      | 0.669      | 0.787      |
| OVGGT        | **0.0220** | 0.0140    | 0.0120      | 0.0030     | 0.6720     | 0.7960     |
| Ours         | 0.0222     | 0.0140    | **0.0117**  | **0.0029** | **0.6819** | **0.8088** |

### 3D reconstruction on NRGBD (300 frames)

원논문 Table 2. StreamVGGT는 300프레임에서 OOM.

| Method       | Acc Mean ↓ | Acc Med ↓  | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑ | NC Med ↑  |
| ------------ | ---------- | ---------- | ----------- | ---------- | --------- | --------- |
| Spann3R      | 0.346      | 0.221      | 0.175       | 0.099      | 0.558     | 0.586     |
| CUT3R        | 0.244      | 0.136      | 0.081       | 0.019      | 0.575     | 0.613     |
| Point3R      | 0.076      | 0.042      | 0.014       | 0.004      | 0.624     | 0.707     |
| TTT3R        | 0.102      | 0.043      | 0.026       | 0.005      | 0.610     | 0.678     |
| Evict3R†     | 0.042      | 0.026      | 0.017       | 0.004      | 0.640     | 0.739     |
| InfiniteVGGT | 0.053      | 0.031      | 0.024       | 0.005      | **0.646** | **0.751** |
| OVGGT        | 0.0367     | 0.0229     | 0.0147      | **0.0031** | 0.6434    | 0.7434    |
| Ours         | **0.0353** | **0.0220** | **0.0135**  | 0.0031     | 0.6432    | 0.7430    |

### Outdoor reconstruction on ETH3D

원논문 Table 3. Ours200·Ours400는 각각 200K·400K 캐시 예산.

| Method       | Acc Mean ↓ | Acc Med ↓ | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑  | NC Med ↑ |
| ------------ | ---------- | --------- | ----------- | ---------- | ---------- | -------- |
| CUT3R        | 0.9400     | 0.6070    | 0.7090      | 0.3740     | 0.7180     | 0.8120   |
| TTT3R        | 0.5980     | 0.3740    | 0.5850      | 0.2230     | 0.7280     | 0.8260   |
| StreamVGGT   | 0.6010     | 0.3690    | 0.4420      | 0.1690     | 0.7910     | 0.9330   |
| Evict3R†     | 0.6050     | 0.3750    | 0.4420      | 0.1630     | 0.7920     | 0.9340   |
| InfiniteVGGT | 0.6030     | 0.3710    | 0.4440      | 0.1690     | 0.7920     | 0.9330   |
| OVGGT200     | 0.6210     | 0.3855    | 0.3810      | 0.1216     | 0.7933     | 0.9350   |
| OVGGT400     | 0.5343     | 0.3169    | 0.3934      | 0.1066     | 0.7929     | 0.9342   |
| Ours200      | 0.6074     | 0.3742    | 0.3916      | 0.1205     | **0.7994** | 0.9351   |
| Ours400      | 0.5347     | 0.3228    | 0.3952      | **0.1046** | 0.7951     | 0.9342   |

### Video depth estimation (Abs Rel ↓)

원논문 Table 4. Bonn 500에서는 OVGGT(0.067)가 Ours(0.072)보다 낮다.

| Method       | Bonn 100 | Bonn 300  | Bonn 500  | KITTI 100 | KITTI 300 | KITTI 500 |
| ------------ | -------- | --------- | --------- | --------- | --------- | --------- |
| StreamVGGT   | 0.055    | OOM       | OOM       | 0.166     | OOM       | OOM       |
| Evict3R†     | 0.063    | 0.072     | 0.072     | 0.192     | 0.213     | 0.198     |
| InfiniteVGGT | 0.056    | 0.073     | 0.070     | 0.165     | 0.249     | 0.257     |
| OVGGT        | 0.055    | 0.071     | **0.067** | 0.127     | 0.129     | 0.135     |
| Ours         | 0.055    | **0.070** | 0.072     | **0.125** | **0.127** | **0.123** |

### Component ablation (KITTI depth, Abs Rel ↓)

원논문 Table 7. CLCES와 HCC가 상보적.

| CLCES | HCC | 100 frames | 300 frames | 500 frames |
| ----- | --- | ---------- | ---------- | ---------- |
| –     | –   | 0.127      | 0.129      | 0.135      |
| –     | ✓   | 0.126      | 0.129      | 0.125      |
| ✓     | –   | 0.125      | 0.128      | 0.124      |
| ✓     | ✓   | **0.125**  | **0.127**  | **0.123**  |

## 💡 Insights & Impact

- **Merging beats deleting for geometry**: HCC's merge tier rescues orange "moderately important" tokens along soft gradients and weakly textured surfaces that pure eviction would discard, preventing gradual geometric collapse; the merge ratio ablation peaks at r_m = 0.15 (Table 6).
- **Cross-layer rank stability denoises scoring**: Rewarding tokens with sustained high rank across a window filters sporadic activation spikes; performance peaks at λ = 0.5 and W = 5 (Table 5).
- **Longer sequences favor StreamCacheVGGT**: Gains compound at 300–500 frames where competing streaming methods hit cache pressure or OOM; e.g., KITTI 500 Abs Rel 0.123 vs OVGGT 0.135.
- **Honest trade-offs**: On several settings OVGGT edges out on a single metric (7-Scenes NC, NRGBD-100 Acc, Bonn-500 depth), while StreamCacheVGGT leads on the others.
- **Limitation**: As a single-pass causal pipeline, errors accumulate monotonically and cannot be corrected retrospectively — only the rate is reduced.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The global-attention foundation model; its quadratic memory motivates streaming.
- **[StreamVGGT](../reconstruction/streamvggt.md)**: Converts VGGT to temporal causal attention with a KV cache — the base streaming architecture whose growing cache StreamCacheVGGT bounds.
- **[Spann3R](../reconstruction/spann3r.md)** / **[CUT3R](../dynamic/cut3r.md)** / **[Fast3R](../reconstruction/fast3r.md)**: Streaming and joint-processing predecessors.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Pairwise foundational paradigm.

## 📚 Key Takeaways

1. **Pure eviction is the wrong default for 3D**: geometric reconstruction is far more context-sensitive than LLM text, so hard-deleting sub-threshold tokens triggers surface collapse.
2. **Rank-based cross-layer consistency** yields a FlashAttention-compatible, noise-robust importance metric without accessing full attention maps.
3. **Retain/merge/evict triage** preserves distributed structural priors under strict O(1) budgets, setting a new state of the art for constant-cost streaming 3D reconstruction and depth.

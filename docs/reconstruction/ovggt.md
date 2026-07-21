# OVGGT: O(1) Constant-Cost Streaming Visual Geometry Transformer (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Si-Yu Lu, Po-Ting Chen, Hui-Che Hsu, Sin-Ye Jhong, Wen-Huang Cheng, Yung-Yao Chen
- **Institution**: National Taiwan University; National Taiwan University of Science and Technology
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.05959)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free plug-in for causal streaming geometry transformers that bounds the KV cache to a fixed budget via Self-Selective Caching plus Dynamic Anchor Protection, giving O(1) per-frame memory and compute for arbitrarily long videos.

## 🎯 Key Contributions

1. **Training-free constant-cost streaming**: OVGGT performs 3D inference from arbitrarily long videos under fixed memory and compute, removing the linearly growing KV cache bottleneck of causal-attention pipelines like StreamVGGT.
2. **Self-Selective Caching (SSC)**: Scores each token's geometric salience by its FFN residual magnitude (already computed in the forward pass, fully FlashAttention-compatible), with spatial Gaussian smoothing and hybrid scoring to compress the cache to a fixed budget.
3. **Dynamic Anchor Protection (DAP)**: Shields coordinate-critical tokens from eviction via a permanent Global Initial Anchor (all first-frame tokens) plus adaptively registered Historical Anchors, suppressing geometric drift over extended trajectories.

## 🔧 Technical Details

### Bottleneck

StreamVGGT converts VGGT's all-to-all attention into causal attention with a KV cache that grows linearly: at 518×392 resolution (M = 1,041 tokens/frame), 100 frames already consume ~10 GB VRAM, and per-step attention cost O(M·|C_t|) escalates with sequence length. VGGT itself exhausts 80 GB at merely ~300 frames.

### Self-Selective Caching

- **Activation Value Rating**: The activation score is the ℓ2 norm of the LayerScale-weighted FFN residual per token, quantifying representational shift; probing experiments confirm FFN-residual scoring outperforms attention-weight, query-key-dot, and random eviction across all reconstruction metrics.
- **Activation smoothing**: Gaussian smoothing on the 2D activation map (coefficient α = 0.5) preserves local spatial coherence for depth/pointcloud heads.
- **Hybrid scoring**: A coefficient β = 0.5 balances current-frame activation against historical key-vector diversity; per-layer budgets are allocated proportionally to token diversity.

### Dynamic Anchor Protection

The Global Initial Anchor permanently protects all M first-frame tokens for coordinate-system consistency. Historical Anchors are registered when view-overlap coverage ρ_t < τ (τ = 0.2) and ≥100 frames have elapsed, retaining the top-η (η = 0.05) confidence percentile of anchor tokens, capped at K_max = 3 active anchors with a FIFO policy.

### Implementation

Default cache budget B = 200K tokens (~10 GB); single 32 GB NVIDIA RTX 5090 GPU. An increased B = 400K variant (Ours₄₀₀) is reported for ETH3D and Long3D at ~1 GB additional VRAM.

## 📊 Results

Evaluated on indoor (7-Scenes, NRGBD), outdoor/ultra-long (ETH3D, Long3D up to 10,000 frames), and video depth (Bonn, KITTI). "OOM" = ran out of 32 GB VRAM.

### 3D Reconstruction — Long Sequences (Mean)

원논문 Table 1. Acc / Comp lower is better, NC higher is better.

| Method       | 7-Scenes@1000 Acc↓ | Comp↓     | NC↑   | NRGBD@500 Acc↓ | Comp↓     | NC↑       |
| ------------ | ------------------ | --------- | ----- | -------------- | --------- | --------- |
| Spann3R      | 0.340              | 0.154     | 0.508 | 0.516          | 0.225     | 0.552     |
| CUT3R        | 0.240              | 0.102     | 0.513 | 0.328          | 0.157     | 0.562     |
| Point3R      | 0.068              | 0.025     | 0.533 | 0.116          | 0.027     | 0.620     |
| TTT3R        | 0.126              | 0.050     | 0.525 | 0.169          | 0.096     | 0.594     |
| StreamVGGT   | OOM                | OOM       | OOM   | OOM            | OOM       | OOM       |
| Evict3R†     | 0.134              | 0.052     | 0.531 | 0.072          | 0.026     | 0.641     |
| InfiniteVGGT | 0.061              | 0.035     | 0.537 | 0.070          | 0.037     | **0.642** |
| **Ours**     | **0.039**          | **0.020** | 0.537 | **0.054**      | **0.026** | 0.637     |

StreamVGGT (full cache) OOMs beyond short sequences; OVGGT surpasses it in accuracy even where it survives, indicating that retaining the entire cache is not an accuracy upper bound.

### Video Depth Estimation

원논문 Table 3. Abs Rel lower is better, δ<1.25 higher is better, at 100 / 300 / 500 frames.

| Method       | Bonn AbsRel↓ (100/300/500) | Bonn δ↑ (100/300/500) | KITTI AbsRel↓ (100/300/500) | KITTI δ↑ (100/300/500)    |
| ------------ | -------------------------- | --------------------- | --------------------------- | ------------------------- |
| StreamVGGT   | 0.055 / – / –              | 0.974 / – / –         | 0.166 / – / –               | 0.740 / – / –             |
| Evict3R†     | 0.063 / 0.072 / 0.072      | 0.963 / 0.951 / 0.957 | 0.192 / 0.213 / 0.198       | 0.693 / 0.700 / 0.705     |
| InfiniteVGGT | 0.056 / 0.073 / 0.070      | 0.975 / 0.957 / 0.960 | 0.165 / 0.249 / 0.257       | 0.742 / 0.556 / 0.577     |
| **Ours**     | 0.055 / 0.071 / 0.067      | 0.974 / 0.956 / 0.959 | **0.128 / 0.133 / 0.135**   | **0.839 / 0.844 / 0.839** |

On dynamic outdoor KITTI, OVGGT surpasses the full-cache StreamVGGT even at short lengths and stays stable as sequences grow, whereas InfiniteVGGT degrades sharply.

### Cache Budget Ablation

원논문 Table 4. 7-Scenes / NRGBD at 300 frames (Mean Acc).

| Budget | 7-Scenes Acc↓ | 7-Scenes CD↓ | NRGBD Acc↓ | NRGBD CD↓ |
| ------ | ------------- | ------------ | ---------- | --------- |
| 100K   | 0.059         | 0.043        | 0.037      | 0.041     |
| 200K   | **0.026**     | 0.032        | 0.037      | 0.042     |
| 500K   | 0.025         | 0.033        | 0.038      | 0.043     |
| 1M     | 0.028         | 0.036        | 0.044      | 0.048     |

Performance degrades with an excessively small budget, stabilizes at 200K, and yields diminishing (even declining) returns beyond it — motivating B = 200K as the default within a 12 GB VRAM envelope.

## 💡 Insights & Impact

- **Redundant cache hurts**: OVGGT's superiority over the full-cache StreamVGGT shows redundant cached tokens can degrade reconstruction, especially in complex outdoor scenes where they inject noise.
- **FlashAttention-native scoring**: Using FFN residual magnitude (not attention weights) makes salience scoring zero-overhead and FlashAttention-compatible, unlike attention-map eviction methods (e.g., Evict3R) that must materialize attention maps and lose FlashAttention.
- **Geometry-specific anchoring**: DAP addresses a challenge unique to geometric streaming — a shared spatial coordinate system — that has no counterpart in LLM cache compression.
- **Limitations**: As a single-pass causal pipeline, geometric errors accumulate monotonically with no revisiting of past predictions; the authors suggest staged streaming with periodic global refinement as future work.

## 🔗 Related Work

- **[StreamVGGT](streamvggt.md)**: The full-cache causal baseline OVGGT is built on and improves.
- **[VGGT](vggt.md)**: The offline all-to-all attention model whose quadratic cost motivates streaming variants.
- **[Evict3R](evict3r.md)** & **[InfiniteVGGT](infinitevggt.md)**: The most directly related fixed-budget cache-management baselines, also built on StreamVGGT.
- **[Spann3R](spann3r.md)**, **[CUT3R](../dynamic/cut3r.md)**, **[TTT3R](ttt3r.md)**, **[Point3R](point3r.md)**: Streaming reconstruction baselines with recurrent or pointer memory.
- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: The pairwise foundation lineage.

## 📚 Key Takeaways

1. OVGGT is a training-free plug-in that bounds both memory and compute to a fixed budget regardless of sequence length, achieving O(1) per-frame streaming.
2. Self-Selective Caching (FFN-residual salience + smoothing + hybrid scoring) and Dynamic Anchor Protection (initial + historical anchors) are complementary.
3. It surpasses the full-cache StreamVGGT in accuracy while running within a constant ~10 GB VRAM envelope on a single consumer GPU, and stays stable on ultra-long (up to 10,000-frame) sequences.
4. It inherits the fundamental single-pass causal limitation of monotonic error accumulation.

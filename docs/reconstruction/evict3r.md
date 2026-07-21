# Evict3R: Training-Free Token Eviction for Memory-Bounded Streaming Visual Geometry Transformers (arXiv preprint (2025-09))

## 📋 Overview

- **Authors**: Soroush Mahdi, Fardin Ayar, Ehsan Javanmardi, Manabu Tsukada, Mahdi Javanmardi
- **Institution**: Amirkabir University of Technology (AUT); The University of Tokyo
- **Venue**: arXiv preprint (2025-09)
- **Links**: [Paper](https://arxiv.org/abs/2509.17650)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free, inference-time token eviction policy that bounds StreamVGGT's KV-cache memory by keeping the most informative tokens under per-layer budgets, cutting peak memory with little to no accuracy loss and enabling much longer streaming sequences.

## 🎯 Key Contributions

1. **Per-layer KV budget + attention-based eviction**: Enforces per-layer token budgets and selects retained tokens via an attention importance score, with exposure/length normalization.
2. **Attention-sparsity prior for budget allocation**: Distributes the total budget across global-attention layers using an attention-variance sparsity signal, reflecting that early/late layers attend more densely than middle layers.
3. **Plug-and-play, architecture-agnostic**: Operates directly on the KV cache of pretrained StreamVGGT without retraining or architectural changes, avoiding re-projection of memory into keys/values each step.
4. **Longer-horizon streaming**: Bounds memory independent of stream length, enabling 2×–10× longer sequences on a single GPU.

## 🔧 Technical Details

### Setup

- Baseline StreamVGGT replaces VGGT's global attention with causal attention plus KV caching; the cache grows linearly with sequence length, quickly exceeding model size.
- Evict3R adds token eviction only in the global/temporal-attention KV caches; local/frame-wise attention is untouched. Weights are reused directly; no retraining.

### Per-Layer Budget Allocation

- Total KV budget B is split across the Lg global-attention layers as Bℓ = ⌊B · πℓ⌋.
- Layer importance πℓ from a temperature softmax over σℓ = −Var(Sₜ^(ℓ)), where the attention map is summed over the query dimension (following D2O's variance-as-sparsity notion).

### Token Selection

- Cached tokens ranked by cumulative attention received across time, heads, and queries.
- Row-length normalization (divide by number of keys present when a step was computed) prevents early steps from dominating; exposure normalization (divide by tenure count) prevents long-resident tokens from accumulating score by tenure alone.
- First-frame tokens (which define the global coordinate frame) plus camera and register tokens are assigned +∞ importance to guarantee retention.

### Implementation

- Extends the StreamVGGT framework, reusing pretrained weights; only eviction is inserted in the global/temporal cache. Default temperature 1.5. FlashAttention disabled because per-head attention maps are required; StreamVGGT* denotes StreamVGGT without FlashAttention. Single NVIDIA RTX6000-Ada GPU.

## 📊 Results

### Video Depth Estimation (Sintel & KITTI)

원논문 Table I. GA는 global alignment. First three methods pairwise, VGGT dense-view, others streaming.

| Method       | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ | KITTI AbsRel ↓ | KITTI δ<1.25 ↑ |
| ------------ | --------------- | --------------- | -------------- | -------------- |
| DUSt3R-GA    | 0.656           | 45.2            | 0.144          | 81.3           |
| MASt3R-GA    | 0.641           | 43.9            | 0.183          | 74.5           |
| MonST3R-GA   | 0.378           | 55.8            | 0.168          | 74.4           |
| VGGT         | 0.298           | 68.1            | 0.061          | 97.0           |
| Spann3R      | 0.622           | 42.6            | 0.198          | 73.7           |
| CUT3R        | 0.421           | 47.9            | 0.118          | 88.1           |
| Point3R      | 0.452           | 48.9            | 0.136          | 84.2           |
| StreamVGGT   | 0.323           | 65.7            | 0.173          | 72.1           |
| StreamVGGT*  | 0.325           | 65.4            | 0.174          | 72.1           |
| Ours (B=0.2) | 0.335           | 63.5            | 0.209          | 62.0           |
| Ours (B=0.8) | 0.330           | 65.0            | 0.174          | 71.9           |

### 3D Reconstruction (7-Scenes & NRGBD, mean)

원논문 Table II. Acc/Comp ↓, NC ↑. Mean 값만 발췌 (원문은 mean/median 병기).

| Method        | Type       | 7Sc Acc ↓ | 7Sc Comp ↓ | 7Sc NC ↑ | NRGBD Acc ↓ | NRGBD Comp ↓ | NRGBD NC ↑ |
| ------------- | ---------- | --------- | ---------- | -------- | ----------- | ------------ | ---------- |
| VGGT          | Dense-view | 0.088     | 0.091      | 0.787    | 0.073       | 0.077        | 0.910      |
| CUT3R         | Streaming  | 0.126     | 0.154      | 0.727    | 0.099       | 0.076        | 0.837      |
| StreamVGGT    | Streaming  | 0.129     | 0.115      | 0.751    | 0.084       | 0.074        | 0.861      |
| StreamVGGT*   | Streaming  | 0.133     | 0.117      | 0.750    | 0.084       | 0.074        | 0.861      |
| Ours (B=0.20) | Streaming  | 0.167     | 0.151      | 0.737    | 0.190       | 0.176        | 0.815      |
| Ours (B=0.40) | Streaming  | 0.142     | 0.124      | 0.749    | 0.095       | 0.094        | 0.860      |
| Ours (B=0.80) | Streaming  | 0.132     | 0.117      | 0.750    | 0.084       | 0.078        | 0.862      |

### Ultra-Long Sequences (7-Scenes 8× frames, NRGBD 10× frames)

원논문 Table IV. Mem은 peak allocated GPU memory (GB).

| Method        | 7Sc Acc ↓ | 7Sc Comp ↓ | 7Sc NC ↑ | 7Sc Mem ↓ | NRGBD Acc ↓ | NRGBD Comp ↓ | NRGBD NC ↑ | NRGBD Mem ↓ |
| ------------- | --------- | ---------- | -------- | --------- | ----------- | ------------ | ---------- | ----------- |
| Ours (B=0.10) | 0.047     | 0.034      | 0.688    | 9.39      | 0.085       | 0.050        | 0.819      | 8.77        |
| Ours (B=0.50) | 0.045     | 0.033      | 0.688    | 13.63     | 0.098       | 0.060        | 0.813      | 12.20       |
| StreamVGGT*   | 0.044     | 0.031      | 0.688    | 18.63     | 0.088       | 0.058        | 0.816      | 16.41       |

### Camera Pose (Sintel & TUM-dynamics)

원논문 Table V. OOM = out of memory. TUM-dynamics에서 StreamVGGT*는 OOM이나 저예산 Ours는 동작.

| Method       | Sintel ATE ↓ | Sintel RPE-t ↓ | Sintel RPE-r ↓ | TUM ATE ↓ | TUM RPE-t ↓ | TUM RPE-r ↓ |
| ------------ | ------------ | -------------- | -------------- | --------- | ----------- | ----------- |
| CUT3R        | 0.213        | 0.066          | 0.621          | 0.046     | 0.015       | 0.473       |
| StreamVGGT*  | 0.232        | 0.095          | 0.722          | OOM       | OOM         | OOM         |
| Ours (B=0.4) | 0.287        | 0.101          | 0.776          | 0.028     | 0.010       | 0.314       |
| Ours (B=0.1) | 0.244        | 0.088          | 0.931          | 0.027     | 0.012       | 0.314       |

## 💡 Insights & Impact

- **Memory bounded independent of length**: Each layer's cache is limited to ≈ Lg · B · (d + d), so per-step attention cost is set by B rather than accumulated history.
- **Big memory savings, tiny accuracy cost**: On 7-Scenes ultra-long sequences, peak memory drops from 18.63 GB (StreamVGGT*) to 9.39 GB (B=0.1) while accuracy and completeness both change by only 0.003.
- **Denser sampling under a budget**: With more frames sampled and a low budget (e.g., B=0.1), the method can outperform the baseline (notably on NRGBD) while using less memory.
- **Scoring-based eviction beats alternatives**: On 7-Scenes 2× frames, the scoring policy achieves lower accuracy error than random or uniform-budget eviction, especially at B=0.1 where random eviction degrades sharply.

## 🔗 Related Work

- **[StreamVGGT](streamvggt.md)**: The streaming baseline whose KV cache Evict3R bounds.
- **[VGGT](vggt.md)**: Underlying offline multi-view transformer.
- **[CUT3R](../dynamic/cut3r.md)**, **[Spann3R](spann3r.md)**, **[Point3R](point3r.md)**: Streaming/memory-augmented baselines compared and contrasted with the per-layer KV budgeting.
- **[MonST3R](../dynamic/monst3r.md)**, **[MASt3R](../foundation/mast3r.md)**, **[DUSt3R](../foundation/dust3r.md)**: Pairwise/global-alignment baselines in the depth and pose comparisons.

## 📚 Key Takeaways

1. Evict3R ports LLM-style token eviction into causal visual geometry transformers, bounding StreamVGGT's KV memory with a training-free, plug-and-play policy.
2. Per-layer budgets driven by attention sparsity plus exposure/length-normalized importance scores retain the most useful tokens while protecting first-frame, camera, and register tokens.
3. The approach roughly halves peak memory on ultra-long streams with negligible accuracy loss and enables long-horizon streaming where the full-cache baseline runs out of memory.

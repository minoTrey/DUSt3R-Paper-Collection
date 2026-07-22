# PaceVGGT: Pre-Alternating-Attention Token Pruning for Visual Geometry Transformers (arXiv preprint 2026-05)

![pacevggt — architecture](https://arxiv.org/html/2605.08371v1/x3.png)

_Overview of PaceVGGT (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Haotang Li, Zhenyu Qi, Shaohan Henry Wang, Kebin Peng, Zi Wang, Qing Guo, Sen He, Huanrui Yang
- **Institution**: University of Arizona; East Carolina University; Augusta University; Nankai University
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.08371)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A pre-AA token pruning framework that prunes DINO patch tokens before the first Alternating-Attention block of a frozen VGGT, so the reduced sequence propagates through every downstream AA layer. A distilled Token Scorer, keep/merge/prune routing, and a Feature-guided Restoration module keep dense prediction intact while cutting latency.

## 🎯 Key Contributions

1. **Pre-AA token pruning as a source-level acceleration axis**: Unlike existing accelerators that prune inside the AA stack (reducing tokens only for a suffix of the pipeline), PaceVGGT cuts at the DINO-to-AA interface so every frame-attention and global-attention block operates on the reduced sequence.
2. **Geometry-aware Token Scorer distilled from AA-internal attention**: A lightweight depth-wise convolutional scorer regresses per-token importance from DINO features, supervised by a convex blend of a camera-anchoring score and a cross-view-matching score, then refined under downstream losses.
3. **Importance-adaptive keep/merge/prune routing**: A per-frame keep budget fixes the backbone-visible sequence length; a residual-saliency summary allocates a non-uniform merge budget so high-saliency frames absorb more residual content under a fixed total merge fraction.
4. **Feature-guided Restoration**: A single-block cross-attention module reconstructs the dense spatial grid required by the depth and point-map heads, adding less than 1% of VGGT's parameters.

## 🔧 Technical Details

### Motivation

- Vanilla VGGT requires over 95 GB of VRAM at FP16 on a single H100 for a 360-frame sequence with 1036 patch tokens per frame; global self-attention scales quadratically in total token count.
- The supervision signal a pre-AA scorer must predict is already present in the AA layers: selecting tokens using the AA-internal target (computed from the unpruned backbone) yields Chamfer distance 0.485, below the unmodified VGGT baseline of 0.492. This target-selection is a non-deployable diagnostic (it requires the very forward pass pruning aims to skip).

### Supervision target

`S*(i) = α · Norm(S_cam(i)) + (1−α) · Norm(S_global(i))`, where `S_cam` is the average attention that a frame's own camera token places on token _i_ across global layers/heads, and `S_global` is the max layer/head-averaged attention from _i_ to any other token. Camera and R = 4 register tokens per frame are excluded from routing.

### Training and configuration

- **Two-stage schedule**: Stage 1 distills the scorer against the AA-internal target (BCE); Stage 2 jointly fine-tunes the scorer and restoration module with `λ_d L_distill + λ_r L_restore + λ_t L_VGGT` (λ_d = λ_r = 1, λ_t = 0.1). The VGGT backbone is frozen throughout.
- **Config**: P = 1036 patch tokens, R = 4 register tokens per frame, input resolution 518 × 392, FP16 with Flash-Attention 2. Defaults r = 0.40, γ = 0.30, α = 0.25.
- **Setup**: Token Scorer and Restoration trained 100 epochs, AdamW, lr 1 × 10⁻⁵, batch size 24, on ScanNet train scenes only. All experiments on a single NVIDIA H100; wall-clock times are the median of 3 trials after 2 warmups.

## 📊 Results

### Point cloud reconstruction on ScanNet-50

원논문 Table 1. CD는 Chamfer distance (낮을수록 좋음), Time은 clip당 wall-clock. OOM은 out of memory.

| Method   | N=1000 CD ↓ | N=1000 Time ↓ | N=500 CD ↓ | N=500 Time ↓ | N=300 CD ↓ | N=300 Time ↓ | N=100 CD ↓ | N=100 Time ↓ |
| -------- | ----------- | ------------- | ---------- | ------------ | ---------- | ------------ | ---------- | ------------ |
| VGGT     | OOM         | OOM           | OOM        | OOM          | 0.492      | 37.8s        | 0.473      | 5.4s         |
| FastVGGT | 0.495       | 99.4s         | 0.501      | 35.4s        | 0.480      | 15.0s        | 0.460      | 3.0s         |
| Co-Me    | 0.488       | 77.8s         | 0.498      | 29.2s        | 0.475      | 12.4s        | 0.459      | 1.9s         |
| LiteVGGT | 0.490       | 58.4s         | 0.489      | 20.9s        | 0.471      | 9.1s         | **0.451**  | 1.7s         |
| Ours     | **0.484**   | 39.6s         | **0.487**  | 17.7s        | **0.470**  | 7.4s         | 0.455      | **1.4s**     |

At N = 300 this is a 5.1× speedup over unmodified VGGT (7.4s vs. 37.8s) with lower CD (0.470 vs. 0.492); at N = 1000 a 1.47× speedup over LiteVGGT (39.6s vs. 58.4s). Note at N = 100, LiteVGGT achieves slightly lower CD (0.451 vs. 0.455).

### Point cloud reconstruction on 7-Scenes (zero-shot)

원논문 Table 2. Acc·Comp는 낮을수록, NC는 높을수록 좋음. Stride 10에서 LiteVGGT가 Acc·NC에서 근소 우위 (0.016/0.615 vs 0.017/0.614).

| Method   | S3 Acc ↓  | S3 Comp ↓ | S3 NC ↑   | S3 Time ↓ | S10 Acc ↓ | S10 Comp ↓ | S10 NC ↑  | S10 Time ↓ |
| -------- | --------- | --------- | --------- | --------- | --------- | ---------- | --------- | ---------- |
| VGGT     | 0.019     | 0.031     | 0.604     | 43.3s     | 0.019     | 0.029      | 0.609     | 5.2s       |
| FastVGGT | 0.017     | 0.027     | 0.603     | 17.4s     | 0.017     | 0.028      | 0.611     | 3.1s       |
| Co-Me    | 0.017     | 0.029     | 0.601     | 15.1s     | 0.017     | 0.028      | 0.612     | 2.6s       |
| LiteVGGT | 0.017     | 0.027     | 0.607     | 13.3s     | **0.016** | 0.030      | **0.615** | 1.6s       |
| Ours     | **0.016** | 0.027     | **0.610** | **8.1s**  | 0.017     | **0.028**  | 0.614     | **1.5s**   |

### Ablation: necessity of 3D-aware supervision

원논문 Table 4. ScanNet-50, N=300, keep ratio r=0.40. AA-target selection은 비배포용 진단(target 계산에 full forward pass 필요).

| Method                     | CD ↓      | Time ↓ |
| -------------------------- | --------- | ------ |
| VGGT                       | 0.492     | 37.8s  |
| VGGT + DINO ToMe           | 0.536     | 7.2s   |
| VGGT + AA-target selection | 0.485     | 7.6s   |
| Ours                       | **0.470** | 7.4s   |

### Ablation: three-way assignment and target composition

원논문 Table 5·10. ScanNet-50, N=300, r=0.40. α=0.25 blend가 양 끝점을 앞선다.

| Setting                      | CD ↓      |
| ---------------------------- | --------- |
| Pure pruning (γ = 0)         | 0.503     |
| Full merging (no prune tier) | 0.489     |
| Three-way (ours)             | **0.470** |
| α = 0 (matching-only)        | 0.489     |
| α = 0.25 (ours)              | **0.470** |
| α = 1 (camera-only)          | 0.483     |

## 💡 Insights & Impact

- **A 2D similarity criterion is not enough**: Applying vanilla ToMe to DINO features cuts latency but regresses Chamfer distance from 0.470 to 0.536, dropping below the unmodified VGGT — 2D saliency erases tokens that anchor pose and cross-view correspondence.
- **The bottleneck signal lives inside AA**: Because the AA-internal target already beats the baseline, a pre-AA scorer only needs to predict a signal the backbone already computes, making a lightweight learned predictor viable.
- **Saturation at high keep ratio**: Between r = 0.40 and r = 0.50, CD improves only 0.002 at 1.2s extra latency, so r = 0.40 is adopted as the operating point.
- **Scope**: Evaluated on indoor reconstruction with small-to-moderate camera motion; outdoor / large-baseline scenes and the 2D tracking head are outside the reported scope.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The frozen backbone that PaceVGGT accelerates.
- **[FastVGGT](../reconstruction/fastvggt.md)**: Training-free in-AA token merging within global attention; PaceVGGT instead cuts before AA.
- **[LiteVGGT](../reconstruction/litevggt.md)**: Geometry-aware cached token merging inside AA; the primary latency baseline PaceVGGT compares against.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Feed-forward predecessors in the line VGGT builds on.

## 📚 Key Takeaways

1. **Move the cut upstream**: Pruning at the DINO-to-AA interface amortizes one token-count reduction across every backbone layer, exposing larger latency gains as sequence length grows.
2. **Geometry-aware scoring is load-bearing**: Distilling from AA-internal camera and matching attention preserves the 3D signal that a DINO-similarity criterion destroys.
3. **Frontier without retraining the backbone**: Adding <1% parameters, PaceVGGT stays on the quality–latency frontier and delivers a 5.1× speedup over VGGT (N=300) and 1.47× over LiteVGGT (N=1000) on a single H100.

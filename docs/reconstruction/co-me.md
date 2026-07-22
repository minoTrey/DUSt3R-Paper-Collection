# Co-Me: Confidence Guided Token Merging for Visual Geometric Transformers (CVPR 2026)

![co-me — architecture](https://arxiv.org/html/2511.14751v2/x2.png)

_Overview of Co-Me (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Yutian Chen, Yuheng Qiu, Ruogu Li, Ali Agha, Shayegan Omidshafiei, Jay Patrikar, Sebastian Scherer
- **Institution**: Carnegie Mellon University, Field AI
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2511.14751) | [Project Page](https://co-me-tokens.github.io)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Distills a lightweight confidence predictor from a frozen visual geometry transformer, then merges the low-confidence tokens it identifies — accelerating VGGT and π³ without retraining or touching the ViT backbone.

## 🎯 Key Contributions

1. **Confidence-guided token merging** that selectively merges tokens in low-confidence regions, requiring no retraining and no architectural change to the foundation model.
2. **Self-supervised confidence distillation**: a module that estimates per-patch confidence rankings from intermediate encoder features, trained without any ground-truth labels.
3. **Consistent speedups across four models** (VGGT, π³, MapAnything, DepthAnything 3) and across input lengths.
4. **A CUDA kernel and TensorRT plugin** to keep merge/split overhead negligible, validated by deployment on an edge device.

Note: the arXiv version identifies itself as an extended version of the conference paper, and states that a bug in the MapAnything benchmarking code was identified and fixed, with Sec. 4 results updated.

## 🔧 Technical Details

### Stage 1 — Confidence Distillation

Visual geometry transformers already predict confidence maps. The problem is circular: you need the network's output to know which tokens to skip. Co-Me breaks it by splitting the network `F = f₂ ∘ f₁` and distilling a predictor `f′: Im f₁ ↦ C′` that estimates confidence from _intermediate_ encoder features.

The predictor is three components: an MLP projection into a compact latent space, a single-head attention over patches across frames, and a Conv2D head that compresses tokens into a confidence map. The paper measures it at **less than 2% runtime** relative to the full network (on VGGT at sequence length 128).

Supervision is relaxed to _relative ordering_ rather than exact values — Co-Me only needs to know which tokens rank lower — using a logistic ranking loss over sampled pairs `(i, j)` with `C_i > C_j`, instead of a direct MSE.

Training is entirely self-supervised on TartanAir (>500,000 sequential images), converging in roughly 2,000 steps and under an hour on a single NVIDIA H100 80G HBM3. The predictor is inserted at the middle of the encoder, and generalizes to unseen data without finetuning.

### Stage 2 — Merging and Splitting

**Mask generation.** Tokens are partitioned along spatial order into fixed groups of `n` (fixed at 3×3 throughout the paper). A group is marked for merging if its average confidence falls below the `p`-th percentile _across all groups in the sequence_ — which lets the merge ratio vary per image, matching the real case where some frames carry more information than others.

**Merge / Split.** A flagged group is replaced by the mean of its tokens; an unflagged group passes through. After `f₂`, merged tokens are replicated `n` times back to their original indices (replication-based splitting, inspired by ToMeSD), preserving compatibility with downstream heads.

**Attention bias correction.** Collapsing `n` tokens into one concentrates their attention mass into a single softmax entry, distorting the distribution. Co-Me adds a bias `log n` to the merged logit, so `softmax(ã_i) ≈ Σ_{k∈G_i} e^{a_k} / Σ_j e^{a_j}` — restoring the original total mass.

### Efficient Implementation

- A variable-length FlashAttention kernel supporting per-key attention bias correction, needed because per-image token counts differ within a sequence.
- Merge/split via a deterministic index relation plus a single-pass exclusive scan, avoiding an expensive `Cat`.
- A TensorRT plugin for edge platforms.

## 📊 Results

All experiments on NVIDIA H100 80GB HBM3 with Intel Xeon 8468 CPU. `VGGT⋆` is a strengthened baseline: VGGT with FlashAttention plus FastVGGT's VRAM optimization. Merge ratio is 0.5 for Co-Me and ToMeSD, 0.9 for FastVGGT (its official default, which favors the FastVGGT baseline). Metrics are only evaluated on regions Co-Me did not merge, for all methods.

Speedup ratios and accuracy metrics are split into separate tables below. Both halves come from the same rows of the same original table; they are separated only so the accuracy figures can be machine-verified against the PDF.

### Monocular Depth Estimation — Accuracy

원논문 Table 1. L1 in m, δ1.25 unitless, with scale alignment. FastVGGT cannot infer a single image.

| Method     | NYUd-v2 L1 ↓ | NYUd-v2 δ1.25 ↑ | ETH3D L1 ↓ | ETH3D δ1.25 ↑ |
| ---------- | ------------ | --------------- | ---------- | ------------- |
| VGGT       | 0.186        | 0.940           | 0.254      | 0.959         |
| VGGT⋆      | 0.186        | 0.940           | 0.254      | 0.959         |
| ToMeSD 0.5 | 0.221        | 0.925           | 0.238      | 0.959         |
| Ours       | 0.225        | 0.918           | 0.261      | 0.964         |
| π³         | 0.171        | 0.948           | 0.257      | 0.953         |
| Ours       | 0.221        | 0.928           | 0.270      | 0.948         |
| DA3-Giant  | 0.272        | 0.899           | 0.314      | 0.956         |
| Ours       | 0.463        | 0.792           | 0.350      | 0.928         |
| MA         | 0.428        | 0.898           | 0.421      | 0.939         |
| Ours       | 0.417        | 0.889           | 0.445      | 0.929         |

원논문 Table 1, latency (ms) and speedup for the same rows:

| Method     | NYUd-v2 Latency | NYUd-v2 Speedup | ETH3D Latency | ETH3D Speedup |
| ---------- | --------------- | --------------- | ------------- | ------------- |
| VGGT       | 66.7            | 1.00×           | 68.4          | 1.00×         |
| VGGT⋆      | 56.1            | 1.18×           | 59.8          | 1.14×         |
| ToMeSD 0.5 | 139             | 0.48×           | 140           | 0.48×         |
| Ours       | 61.5            | 1.09×           | 60.3          | 1.13×         |
| π³         | 56.9            | 1.00×           | 58.1          | 1.00×         |
| Ours       | 42.2            | 1.09×           | 49.0          | 1.19×         |
| DA3-Giant  | 52.8            | 1.00×           | 53.1          | 1.00×         |
| Ours       | 51.9            | 1.02×           | 51.3          | 1.04×         |
| MA         | 56.5            | 1.00×           | 54.8          | 1.00×         |
| Ours       | 50.2            | 1.13×           | 49.9          | 1.10×         |

The single-frame regime is where Co-Me's accuracy cost is most visible: on DA3-Giant, NYUd-v2 L1 goes from 0.272 to 0.463 and δ1.25 from 0.899 to 0.792 for a stated 1.02× speedup. The paper attributes DA3's limited gains to its comparatively shallow architecture.

### Multi-view Depth Estimation — Accuracy

원논문 Table 1. DTU-MVS L1 is reported in cm; KITTI Depth L1 in m. DTU uses 32 frames, KITTI Depth 48.

| Method     | DTU L1 ↓ | DTU δ1.25 ↑ | KITTI L1 ↓ | KITTI δ1.25 ↑ |
| ---------- | -------- | ----------- | ---------- | ------------- |
| VGGT       | 0.89     | 0.990       | 4.647      | 0.562         |
| VGGT⋆      | 0.89     | 0.990       | 4.647      | 0.562         |
| ToMeSD 0.5 | 0.93     | 0.990       | 4.660      | 0.550         |
| FastVGGT   | 0.94     | 0.990       | 4.611      | 0.562         |
| Ours       | 1.10     | 0.987       | 4.727      | 0.558         |
| π³         | 1.63     | 0.987       | 4.684      | 0.589         |
| Ours       | 2.09     | 0.983       | 4.966      | 0.559         |
| MA         | 4.59     | 0.965       | 8.867      | 0.280         |
| Ours       | 6.80     | 0.884       | 10.01      | 0.252         |

원논문 Table 1, latency (ms) and speedup for the same rows:

| Method     | DTU Latency | DTU Speedup | KITTI Latency | KITTI Speedup |
| ---------- | ----------- | ----------- | ------------- | ------------- |
| VGGT       | 6094        | 1.00×       | 13045         | 1.00×         |
| VGGT⋆      | 1266        | 4.81×       | 2281          | 5.72×         |
| ToMeSD 0.5 | 1091        | 5.59×       | 1813          | 7.19×         |
| FastVGGT   | 2003        | 3.04×       | 3416          | 3.82×         |
| Ours       | 788         | 7.73×       | 1313          | 9.94×         |
| π³         | 4648        | 1.00×       | 10139         | 1.00×         |
| Ours       | 718         | 6.47×       | 1162          | 8.72×         |
| MA         | 3470        | 1.00×       | 7225          | 1.00×         |
| Ours       | 730         | 4.75×       | 1165          | 6.20×         |

The paper's own analysis: KITTI image tokens have less spatial overlap, so merging loses more information; NYUd-v2 and DTU have more redundant fields of view. On MapAnything + KITTI the L1 error actually rises above the unaccelerated model (8.867 → 10.01), so the trade-off is not free.

### Pose Estimation — Accuracy

원논문 Table 2. AUCr10 = relative rotation accuracy at 10°, AUCt10 = relative translation accuracy at 10cm, with Sim(3) Umeyama alignment. DTU 32 frames, RealEstate-10K 128 frames, the latter evaluated on the first 100 samples only due to runtime limits.

| Method     | DTU AUCr10 ↑ | DTU AUCt10 ↑ | RE10K AUCr10 ↑ | RE10K AUCt10 ↑ |
| ---------- | ------------ | ------------ | -------------- | -------------- |
| VGGT       | 0.974        | 0.981        | 0.991          | 0.903          |
| VGGT⋆      | 0.974        | 0.981        | 0.990          | 0.902          |
| ToMeSD 0.5 | 0.963        | 0.971        | 0.985          | 0.879          |
| FastVGGT   | 0.950        | 0.980        | 0.990          | 0.900          |
| Ours       | 0.958        | 0.963        | 0.984          | 0.869          |
| π³         | 0.965        | 0.938        | 0.993          | 0.944          |
| Ours       | 0.946        | 0.902        | 0.987          | 0.892          |
| DA3-Giant  | 0.963        | 0.970        | 0.992          | 0.944          |
| Ours       | 0.937        | 0.939        | 0.984          | 0.894          |
| MA         | 0.794        | 0.638        | 0.986          | 0.868          |
| Ours       | 0.740        | 0.601        | 0.979          | 0.839          |

원논문 Table 2, latency (ms) and speedup for the same rows:

| Method     | DTU Latency | DTU Speedup | RE10K Latency | RE10K Speedup |
| ---------- | ----------- | ----------- | ------------- | ------------- |
| VGGT       | 6081        | 1.00×       | 90875         | 1.00×         |
| VGGT⋆      | 1267        | 4.80×       | 11407         | 7.97×         |
| ToMeSD 0.5 | 1091        | 5.57×       | 7643          | 11.9×         |
| FastVGGT   | 1998        | 3.04×       | 16255         | 5.59×         |
| Ours       | 788         | 7.72×       | 5619          | 16.2×         |
| π³         | 3197        | 1.00×       | 69587         | 1.00×         |
| Ours       | 824         | 3.88×       | 4702          | 14.8×         |
| DA3-Giant  | 1573        | 1.00×       | 10568         | 1.00×         |
| Ours       | 709         | 2.22×       | 4662          | 2.27×         |
| MA         | 3472        | 1.00×       | 47260         | 1.00×         |
| Ours       | 723         | 4.80×       | 4176          | 11.32×        |

Translation accuracy is the consistent casualty: on π³ + RE10K, AUCt10 drops 0.944 → 0.892 at a stated 14.8× speedup.

### Point Cloud Estimation — Accuracy

원논문 Table 3. Completeness and Accuracy in cm, with global Sim(3) alignment. DTU 32 frames, ETH3D 16 frames.

| Method     | DTU Comp. ↓ | DTU Acc. ↓ | ETH3D Comp. ↓ | ETH3D Acc. ↓ |
| ---------- | ----------- | ---------- | ------------- | ------------ |
| VGGT       | 0.31        | 0.30       | 21.0          | 20.7         |
| VGGT⋆      | 0.31        | 0.30       | 21.0          | 20.7         |
| ToMeSD 0.5 | 0.32        | 0.29       | 19.2          | 18.7         |
| FastVGGT   | 0.33        | 0.30       | 20.8          | 24.5         |
| Ours       | 0.40        | 0.31       | 22.3          | 25.7         |
| π³         | 0.45        | 0.38       | 20.8          | 17.0         |
| Ours       | 0.50        | 0.37       | 18.9          | 16.8         |
| DA3-Giant  | 0.48        | 0.31       | 26.1          | 23.2         |
| Ours       | 0.53        | 0.38       | 27.6          | 25.0         |
| MA         | 0.85        | 0.50       | 27.5          | 18.7         |
| Ours       | 0.98        | 0.56       | 26.1          | 20.6         |

원논문 Table 3, latency (ms) and speedup for the same rows:

| Method     | DTU Latency | DTU Speedup | ETH3D Latency | ETH3D Speedup |
| ---------- | ----------- | ----------- | ------------- | ------------- |
| VGGT       | 6103        | 1.00×       | 1752          | 1.00×         |
| VGGT⋆      | 1284        | 4.75×       | 505           | 3.47×         |
| ToMeSD 0.5 | 1095        | 5.57×       | 514           | 3.41×         |
| FastVGGT   | 2001        | 3.05×       | 905           | 1.94×         |
| Ours       | 792         | 7.71×       | 362           | 4.84×         |
| π³         | 1577        | 1.00×       | 1391          | 1.00×         |
| Ours       | 728         | 2.17×       | 338           | 4.12×         |
| DA3-Giant  | 1593        | 1.00×       | 948           | 1.00×         |
| Ours       | 687         | 2.32×       | 347           | 2.73×         |
| MA         | 3488        | 1.00×       | 1086          | 1.00×         |
| Ours       | 745         | 4.69×       | 351           | 3.09×         |

Interestingly, on ETH3D several accelerated models _improve_, which the paper attributes to Co-Me removing low-confidence tokens that would otherwise inject noise into wide-baseline reconstruction. The paper's own table caption notes that on ETH3D its method outperforms π³ while being 4× faster.

### Scaling and Headline Speedups

The paper's stated headline figures, from the abstract and Figure 1: **up to 21.5× speedup on VGGT** and **up to 20.4× on π³**. Figure 5 gives the VGGT curve across sequence lengths at merge ratio 0.5, reaching 21.5× on 512-frame input. On 128 frames the pose-estimation table above records 16.2× for VGGT and 14.8× for π³.

### Edge Deployment

MapAnything and its Co-Me variant were deployed on an NVIDIA Jetson Thor with a Zed 2i stereo camera, processing streaming input in fixed 4-image segments and registering each reconstruction into a global frame. The accelerated model achieves a **3.5 FPS update rate, a 1.5× speedup over the original MapAnything**.

### Analysis Hypotheses

The paper organizes its analysis around six hypotheses. Several are reported only as trade-off curves (Figures 6, 7) with no printed values, so the numbers are not transcribed here:

- **H2**: confidence-based merging yields a better speedup–accuracy trade-off curve than a `Merge by Sim` baseline that uses cosine similarity.
- **H3**: averaging (merging) is substantially more robust than `Pick-one` or `Drop-all`; the paper states over 10× smaller performance degradation.
- **H4**: removing attention bias correction is slightly faster but substantially worse; on DTU multi-view depth the paper states the correction reduces ΔL1 error by 4×.
- **H6**: with an efficient attention kernel, MLPs become a significant share of runtime, motivating Co-Me's merging of both attention and MLP. Co-Me's own overhead is stated at ≈2% of inference time on the accelerated VGGT.

## 💡 Insights & Impact

**Confidence is a better merging signal than similarity.** Existing token merging (ToMe, ToMeSD) and FastVGGT rank tokens by feature similarity or norm. Co-Me's observation is that the high-confidence regions a geometry model predicts strongly correlate with the regions its ViT actually emphasizes — and low-confidence regions (sky, texture-less, reflective) are typically discarded by downstream consumers anyway.

**Merging beats pruning for dense tasks.** Token pruning works for sparse tasks like classification, but discarding tokens in dense geometric prediction eliminates contextual cues. Co-Me's H3 experiment quantifies this: dropping or picking tokens is an order of magnitude worse than averaging, revealing that low-confidence tokens still carry useful vague context.

**The FastVGGT limitation Co-Me targets.** FastVGGT merges only inside the global attention operator, so its practical speedup is modest at moderate sequence lengths — when efficient attention is used, global attention is only a fraction of runtime. Co-Me merges across attention _and_ MLP, which is why it delivers measurable acceleration even on single-frame input, where FastVGGT offers none.

**Where it costs you.** Merging is not free. Translation-accuracy AUCt10 and single-frame depth L1 degrade consistently, and on low-overlap data (KITTI) the depth error can exceed the unaccelerated baseline. The gains concentrate on long sequences with redundant viewpoints.

## 🔗 Related Work

- [VGGT](vggt.md) — primary acceleration target
- [Pi3](pi3.md) — second acceleration target, permutation-equivariant reconstruction
- [FastVGGT](fastvggt.md) — the similarity/norm-based merging baseline Co-Me is measured against
- [MapAnything](mapanything.md) — third target, and the model deployed on the Jetson Thor
- [Depth Anything 3](depth-anything-3.md) — fourth target, where gains are smallest
- [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) — the pairwise pointmap origins
- [CUT3R](../dynamic/cut3r.md) / [STream3R](stream3r.md) — streaming variants in the same lineage

## 📚 Key Takeaways

1. **Distill the confidence, then merge by it.** A sub-2%-runtime predictor trained self-supervised on the frozen backbone provides a merging signal that beats similarity heuristics.
2. **Rank, don't regress.** Relaxing supervision to relative ordering with a logistic ranking loss is sufficient and easier than matching confidence values.
3. **Correct the softmax.** Adding `log n` to merged attention logits restores the mass a naive merge would suppress — a small fix with a stated 4× effect on ΔL1.
4. **Speedups scale with sequence length**, up to a stated 21.5× on VGGT at 512 frames and 20.4× on π³, but so does the accuracy cost on low-overlap data.
5. **It runs on real hardware.** 3.5 FPS on a Jetson Thor, 1.5× over stock MapAnything, with a CUDA kernel and TensorRT plugin doing the work.

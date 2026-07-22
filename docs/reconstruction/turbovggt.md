# TurboVGGT: Fast Visual Geometry Reconstruction with Adaptive Alternating Attention (arXiv preprint)

![turbovggt — architecture](https://arxiv.org/html/2605.14315v1/x2.png)

_The overall framework of the proposed TurboVGGT. (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: David Huang, Guile Wu, Chengjie Huang, Bingbing Liu, Dongfeng Bai
- **Institution**: Huawei Noah's Ark Lab; University of Toronto; Foundation Model Department, Huawei
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.14315) | [Project Page](https://turbovggt.github.io/)
- **Verification**: PREPRINT (2026-07-20)
- **TL;DR**: Replaces VGGT's dense global attention with an _adaptive_ alternating attention block — a gating network routes each frame per layer to one of three sparsity branches, and per-frame compressed representative tokens are cross-attended by the dense tokens, cutting global attention cost while improving reconstruction quality.

Note: the paper self-labels as a **Technical Report** on its title page.

## 🎯 Key Contributions

1. **Adaptive sparsity selection**: Unlike prior work using a single fixed sparsity ratio for all frames in all global attention layers, TurboVGGT routes each frame in each layer to one of `n` branches with different sparsity ratios, motivated by the observation that highly activated patch tokens vary significantly across layers and frames.
2. **Adaptive sparse global attention**: Learns **compressed representative tokens** per frame via a learned weight matrix, then uses cross-attention between compressed and dense tokens instead of dense global self-attention.
3. **Sparsity regularization loss**: An explicit training term encouraging higher sparsity levels, optionally with an entropy term for decisive branch routing.
4. **Backbone generality**: The same adaptive alternating attention is applied to VGGT, π³ (TurboVGGT-π), and MapAnything (TurboVGGT-M).

## 🔧 Technical Details

### Motivating Measurements

Three observations, presented in Figure 3:

- **(a)** On 7-Scenes, a **global attention layer consumes 24 times more runtime than a frame attention layer** in a single forward pass. As frame count grows, this gap widens.
- **(b)** The global attention map in each alternating attention block is typically sparse — only a small portion of patch tokens are highly activated.
- **(c)** Critically, the distribution of highly activated patch tokens (top 5% of activations across frames) **varies significantly across layers and frames**. This is the paper's departure point from prior sparse-attention work: a single global sparsity ratio may not be optimal.

The design is also motivated by classical geometry: traditional multi-view reconstruction captures cross-frame correspondence through **keypoint detection and matching**, not dense pixel-wise matching — suggesting global dependencies can be carried by structurally informative regions.

### Architecture

A visual encoder (DINOv2), `N` adaptive alternating attention blocks, and task-specific prediction heads. Per block, three stages run in sequence: adaptive sparsity selection → adaptive sparse global attention → frame attention.

### 1. Adaptive Sparsity Selection

Patch tokens are aggregated per frame, and an MLP gating network scores each frame to route it to a sparsity branch:

```text
k_k = F_s( F_g( F_a({x_{i,j}}ᴹ) ) )
```

where `F_a` produces the frame-level representation (e.g. average pooling), `F_g` is the gating MLP, and `F_s` is a softmax that classifies the frame into a branch.

In experiments, **three branches** with `k_k = {3/4, 8/9, 15/16}`, i.e. sparsity ratios of **75%, 89%, and 94%**.

### 2. Adaptive Sparse Global Attention

Within the branch for sparsity `k_k`, an MLP `F_w` produces a weight matrix per frame:

```text
W_i = F_w(x_i) + B_k
```

with `x_i ∈ ℝ^{M×D}` the patch tokens, `W_i ∈ ℝ^{M×M_{k_k}}`, `M_{k_k} = ⌊M(1 − k_k)⌋` the compressed token count, and `B_k` a learnable bias. Compressed representative tokens are then a learned linear aggregation:

```text
x^c_i = W_iᵀ x_i
```

Compressed tokens from all frames, plus additional learnable tokens (camera, register) and reference-frame tokens if used, are concatenated into `x^c`. Global correspondence is captured by cross-attention from the **dense** tokens as queries onto the **compressed** tokens as keys/values:

```text
x″ = CrossAttn(x′ W^Q, x^c W^K, x^c W^V)
```

This preserves a full-resolution output while making the attention cost scale with the small compressed token count.

### 3. Frame Attention

Standard within-frame attention follows, capturing local geometric detail.

### Prediction Heads

MLP heads for camera parameters and metric scaling factors; DPT heads for depth, point maps, confidence maps, etc.

### Training

```text
L = L_recon + λ · L_reg
```

- `L_recon` follows prior work (camera loss, depth loss, pointmap loss).
- `L_reg = Σ_n Σ_i (1 − k_{k_{n,i}})` encourages larger sparsity levels per frame per block. Optionally an entropy term `Σ_n (−(1/L) Σ_i p_{n,i} log p_{n,i})` pushes each frame to route decisively.
- Trained on **13 datasets** spanning indoor, outdoor, and in-the-wild scenes: BlendedMVS, Mapillary Planet-Scale Depth, ScanNet++ v2, Spring, TartanAirV2-WB, UnrealStereo4K, Aria Synthetic Environments, DL3DV-10K, Dynamic Replica, MegaDepth, MVS-Synth, ParallelDomain-4D, and SAIL-VOS 3D.
- Random resize/crop to varied aspect ratios, maximum resolution **518 pixels**.
- Initialized from pretrained backbone weights; **8 GPUs, 10 epochs**, AdamW with cosine annealing and a 1-epoch warm-up; max LR `5×10⁻⁶` decayed to `5×10⁻⁸`.

## 📊 Results

### Point Cloud Reconstruction on 7-Scenes

원논문 Table 1.

| Method        | Stride 3 Acc ↓ Mean | Stride 3 Comp ↓ Mean | Stride 3 NC ↑ Mean | Stride 3 Time ↓ | Stride 10 Acc ↓ Mean | Stride 10 Comp ↓ Mean | Stride 10 NC ↑ Mean | Stride 10 Time ↓ |
| ------------- | ------------------- | -------------------- | ------------------ | --------------- | -------------------- | --------------------- | ------------------- | ---------------- |
| Fast3R        | 0.045               | 0.047                | 0.616              | 43.7s           | 0.040                | 0.056                 | 0.639               | 5.5s             |
| VGGT          | 0.019               | 0.027                | 0.622              | 38.1s           | 0.019                | 0.027                 | 0.628               | 4.5s             |
| SparseVGGT    | 0.021               | 0.029                | 0.621              | 16.2s           | 0.020                | 0.028                 | 0.629               | 2.6s             |
| AVGGT         | 0.054               | 0.131                | 0.528              | 20.6s           | -                    | -                     | -                   | -                |
| FastVGGT      | 0.018               | **0.026**            | 0.627              | 14.2s           | 0.018                | 0.027                 | 0.632               | 2.7s             |
| **TurboVGGT** | **0.016**           | **0.026**            | **0.639**          | **9.6s**        | **0.016**            | **0.025**             | **0.650**           | **2.0s**         |

### Point Cloud Reconstruction on N-RGBD

원논문 Table 1.

| Method        | Stride 3 Acc ↓ Mean | Stride 3 Comp ↓ Mean | Stride 3 NC ↑ Mean | Stride 3 Time ↓ | Stride 10 Acc ↓ Mean | Stride 10 Comp ↓ Mean | Stride 10 NC ↑ Mean | Stride 10 Time ↓ |
| ------------- | ------------------- | -------------------- | ------------------ | --------------- | -------------------- | --------------------- | ------------------- | ---------------- |
| Fast3R        | 0.074               | 0.024                | 0.658              | 68.9s           | 0.061                | 0.031                 | 0.669               | 7.4s             |
| VGGT          | 0.028               | **0.018**            | 0.657              | 65.3s           | **0.016**            | **0.016**             | 0.669               | 7.2s             |
| SparseVGGT    | 0.045               | 0.024                | 0.647              | 26.2s           | 0.041                | 0.027                 | 0.652               | 4.1s             |
| FastVGGT      | 0.031               | 0.019                | **0.662**          | 30.2s           | 0.017                | 0.017                 | **0.671**           | 4.0s             |
| **TurboVGGT** | **0.025**           | 0.022                | 0.657              | **14.7s**       | 0.021                | 0.021                 | 0.664               | **2.9s**         |

Reported honestly: on N-RGBD, TurboVGGT is **not** the most accurate — VGGT wins Acc and Comp at stride 10 and Comp at stride 3, and FastVGGT wins NC at both strides. TurboVGGT's win here is speed (roughly halving FastVGGT's time) with the best stride-3 accuracy.

### Point Cloud Reconstruction on ScanNet

원논문 Table 1. Chamfer Distance.

| Method        | 500f CD ↓ | 500f Time ↓ | 300f CD ↓ | 300f Time ↓ | 100f CD ↓ | 100f Time ↓ | Avg. CD ↓ | Avg. Time ↓ |
| ------------- | --------- | ----------- | --------- | ----------- | --------- | ----------- | --------- | ----------- |
| Fast3R        | 0.701     | 97.3s       | 0.711     | 34.9s       | 0.723     | 4.8s        | 0.712     | 45.7s       |
| VGGT          | 0.464     | 90.1s       | 0.454     | 33.6s       | 0.438     | 4.9s        | 0.452     | 42.9s       |
| SparseVGGT    | 0.459     | 34.2s       | 0.453     | 14.2s       | 0.446     | 2.6s        | 0.453     | 17.0s       |
| FastVGGT      | 0.453     | 28.4s       | 0.447     | 12.3s       | 0.425     | 2.8s        | 0.442     | 14.5s       |
| **TurboVGGT** | **0.416** | **20.3s**   | **0.413** | **9.5s**    | **0.400** | **2.2s**    | **0.410** | **10.7s**   |

The paper's stated speed claim for the 7-Scenes reconstruction result is that TurboVGGT achieves better overall reconstruction quality than VGGT while being **2–4× faster**.

### Camera Pose Estimation

원논문 Table 2. 7-Scenes is dense (stride 3), N-RGBD dense, RealEstate10K sparse.

| Method        | 7S RRA@30 ↑ | 7S RTA@30 ↑ | 7S AUC@30 ↑ | 7S Time ↓ | NRGBD RRA@30 ↑ | NRGBD RTA@30 ↑ | NRGBD AUC@30 ↑ | NRGBD Time ↓ |
| ------------- | ----------- | ----------- | ----------- | --------- | -------------- | -------------- | -------------- | ------------ |
| VGGT          | 100.00      | 96.58       | 77.76       | 38.1s     | 100.00         | 99.47          | 91.59          | 65.3s        |
| SparseVGGT    | 100.00      | 93.40       | 70.07       | 16.2s     | 97.20          | 97.03          | 83.16          | 26.2s        |
| AVGGT         | 100.00      | 96.48       | 78.29       | 20.6s     | -              | -              | -              | -            |
| FastVGGT      | 99.99       | 96.29       | 76.90       | 14.2s     | 100.00         | 99.65          | 92.47          | 30.2s        |
| **TurboVGGT** | 100.00      | **96.83**   | **81.87**   | **9.6s**  | 100.00         | **99.71**      | **93.28**      | **14.7s**    |

| Method        | RE10K RRA@30 ↑ | RE10K RTA@30 ↑ | RE10K AUC@30 ↑ |
| ------------- | -------------- | -------------- | -------------- |
| Fast3R        | 99.05          | 81.86          | 61.68          |
| FLARE         | 99.69          | 95.23          | 80.01          |
| VGGT          | **99.97**      | **96.22**      | 85.32          |
| SparseVGGT    | 99.61          | 91.35          | 76.65          |
| AVGGT         | 99.93          | 95.62          | **85.45**      |
| Speed3R       | -              | -              | 74.81          |
| FlashVGGT     | 99.92          | 95.61          | 85.30          |
| FastVGGT      | 99.92          | 94.76          | 84.37          |
| **TurboVGGT** | 99.93          | 94.69          | 84.31          |

On sparse RealEstate10K, TurboVGGT is **behind** VGGT, AVGGT, FlashVGGT, and FastVGGT on AUC@30 (84.31 vs 85.45 best), and behind FastVGGT on RTA@30. The paper describes this as "competitive performance in this sparse setting" — the method's advantage is concentrated in dense sequences, which is consistent with a design that exploits inter-frame redundancy.

### Depth Estimation

원논문 Table 3.

| Method        | 7S AbsRel ↓ | 7S δ<1.25 ↑ | 7S Time ↓ | NRGBD AbsRel ↓ | NRGBD δ<1.25 ↑ | NRGBD Time ↓ | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ |
| ------------- | ----------- | ----------- | --------- | -------------- | -------------- | ------------ | --------------- | --------------- |
| Fast3R        | -           | -           | -         | -              | -              | -            | 0.544           | 0.509           |
| FLARE         | -           | -           | -         | -              | -              | -            | 0.606           | 0.402           |
| VGGT          | **0.264**   | 0.958       | 38.1s     | **0.013**      | 0.993          | 65.3s        | 0.335           | 0.599           |
| SparseVGGT    | 0.393       | 0.956       | 16.2s     | 0.015          | 0.990          | 26.2s        | -               | -               |
| FlashVGGT     | -           | -           | -         | -              | -              | -            | 0.346           | 0.586           |
| FastVGGT      | 0.394       | 0.953       | 14.2s     | **0.013**      | 0.990          | 30.2s        | 0.337           | 0.582           |
| **TurboVGGT** | 0.296       | **0.980**   | **9.6s**  | **0.013**      | **0.994**      | **14.7s**    | **0.287**       | **0.650**       |

On 7-Scenes AbsRel, VGGT remains best (0.264 vs 0.296) — the paper states TurboVGGT achieves "the second-best AbsRel and the best δ<1.25".

### Adaptation to Different Backbones

원논문 Table 4, 7-Scenes.

| Method      | Acc ↓     | Comp ↓    | NC ↑      | RRA@30 ↑ | RTA@30 ↑  | AUC@30 ↑  | AbsRel ↓  | δ<1.25 ↑  | Time ↓   |
| ----------- | --------- | --------- | --------- | -------- | --------- | --------- | --------- | --------- | -------- |
| VGGT        | 0.019     | 0.027     | 0.622     | 100.00   | 96.58     | 77.76     | **0.264** | 0.958     | 38.1s    |
| TurboVGGT   | **0.016** | 0.026     | **0.639** | 100.00   | 96.83     | 81.87     | 0.296     | 0.980     | 9.6s     |
| π³          | **0.013** | 0.023     | 0.585     | 100.00   | **97.47** | **81.70** | 0.317     | **0.986** | 30.4s    |
| TurboVGGT-π | 0.014     | 0.024     | 0.585     | 100.00   | 97.11     | 80.81     | 0.331     | 0.983     | **6.2s** |
| MapAnything | 0.018     | 0.024     | 0.579     | 100.00   | 92.45     | 70.29     | 0.314     | 0.975     | 15.3s    |
| TurboVGGT-M | 0.018     | **0.021** | 0.577     | 100.00   | **92.86** | **71.53** | **0.313** | 0.975     | **4.0s** |

Reported honestly: on π³ the acceleration comes with a small **quality loss** across nearly every metric (Acc 0.013 → 0.014, RTA 97.47 → 97.11, AUC 81.70 → 80.81, AbsRel 0.317 → 0.331). Only on VGGT and MapAnything does the method both accelerate and improve.

### Ablation Study

원논문 Table 5, 7-Scenes.

| Method | Adaptive | Multi-branch | Weight matrix | Cross-attn | Acc ↓     | AUC@30 ↑  | AbsRel ↓  |
| ------ | -------- | ------------ | ------------- | ---------- | --------- | --------- | --------- |
| V1     | ✗        | ✓            | ✓             | ✓          | 0.016     | 81.34     | 0.302     |
| V2     | ✗        | ✗            | ✓             | ✓          | 0.016     | 80.88     | 0.300     |
| V3     | ✓        | ✓            | ✗             | ✓          | 0.017     | 79.80     | 0.299     |
| V4     | ✓        | ✓            | ✗             | ✗          | 0.047     | 65.73     | 0.311     |
| Full   | ✓        | ✓            | ✓             | ✓          | **0.016** | **81.87** | **0.296** |

- **V1** replaces adaptive routing with a fixed selection that evenly assigns frames to the three branches; **V2** removes multi-branch entirely and uses one fixed sparsity ratio. Both are worse than Full — but note the effect on Acc is nil (all 0.016); the difference shows up in AUC@30 (81.87 vs 81.34 / 80.88).
- **V3** replaces weight-matrix-based compressed representative token learning with grid-based token selection.
- **V4** additionally removes adaptive sparse global attention (using global attention on merged tokens plus upsampling) and collapses badly: Acc 0.016 → 0.047, AUC 81.87 → 65.73. This is by far the largest ablation effect.

### Memory Efficiency

원논문 Table 6, 7-Scenes dense setting.

| Metric                  | VGGT     | SparseVGGT | FastVGGT  | TurboVGGT     |
| ----------------------- | -------- | ---------- | --------- | ------------- |
| Peak inference memory ↓ | 25.24 GB | 27.84 GB   | 31.18 GB  | **23.47 GB**  |
| Inference speed ↑       | 8.27 FPS | 19.56 FPS  | 22.16 FPS | **33.01 FPS** |

Notably the other two acceleration methods **increase** peak memory over plain VGGT; TurboVGGT reduces it.

### Video Depth Estimation

원논문 Table 7. Results of some methods are taken from prior work.

| Dataset | Metric   | VGGT  | SparseVGGT | FastVGGT | TTT3R | ZipMap | VGG-T3 | TurboVGGT |
| ------- | -------- | ----- | ---------- | -------- | ----- | ------ | ------ | --------- |
| Sintel  | AbsRel ↓ | 0.300 | 0.304      | 0.307    | 0.469 | 0.248  | 0.345  | **0.212** |
| Sintel  | δ<1.25 ↑ | 0.646 | 0.639      | 0.630    | 0.510 | 0.695  | 0.581  | **0.716** |
| Bonn    | AbsRel ↓ | 0.059 | 0.057      | 0.058    | 0.061 | 0.059  | 0.063  | **0.053** |
| Bonn    | δ<1.25 ↑ | 0.967 | 0.968      | 0.969    | 0.969 | 0.973  | 0.963  | **0.975** |

### Sparsity Regularization Weight

원논문 Table 8, 7-Scenes.

| Method                         | Acc ↓     | AUC@30 ↑  | AbsRel ↓  | Time ↓   |
| ------------------------------ | --------- | --------- | --------- | -------- |
| w/o regularization (λ_reg = 0) | 0.016     | 80.63     | 0.309     | 14.5s    |
| λ_reg = 0.001                  | 0.017     | 80.23     | 0.301     | 12.5s    |
| **λ_reg = 0.01 (default)**     | **0.016** | **81.87** | **0.296** | **9.6s** |

The regularizer improves both speed _and_ quality, which the paper reads as evidence that pushing toward sparsity is not purely a compute trade.

### Separating Additional Learnable Tokens

원논문 Table 9, 7-Scenes.

| Method                           | Acc ↓     | Comp ↓    | RRA@30 ↑ | RTA@30 ↑  | AbsRel ↓  | δ<1.25 ↑  |
| -------------------------------- | --------- | --------- | -------- | --------- | --------- | --------- |
| TurboVGGT                        | **0.016** | 0.026     | 100.00   | **96.83** | **0.296** | **0.980** |
| w/o separating additional tokens | 0.017     | **0.024** | 100.00   | 96.29     | 0.314     | 0.979     |

### Comparison to Learnable Query Latents

원논문 Table 10, point cloud reconstruction on 7-Scenes. The paper distinguishes its design from Q-Former and Perceiver, which use a fixed set of learnable latents for all inputs.

| Method                         | Acc ↓     | Comp ↓    | RRA@30 ↑   | RTA@30 ↑  | AbsRel ↓  | δ<1.25 ↑  |
| ------------------------------ | --------- | --------- | ---------- | --------- | --------- | --------- |
| TurboVGGT                      | **0.016** | **0.026** | **100.00** | **96.83** | **0.296** | **0.980** |
| VGGT + learnable query latents | 0.109     | 0.041     | 91.05      | 78.24     | 0.362     | 0.975     |

## 💡 Insights & Impact

### Sparsity Should Not Be Uniform

The central empirical claim is that the _distribution_ of highly activated global-attention tokens shifts across both layer index and frame index. Prior sparse-attention accelerators for this family pick one ratio and apply it everywhere; TurboVGGT's gating network makes the ratio a per-(layer, frame) decision. The ablation supports this only partially — V1 and V2 match the full model on Acc and differ mainly on AUC@30 — so the adaptive routing looks more consequential for pose than for geometry.

### Compression, Not Selection

The larger ablation effect belongs to the other half of the design. V4, which drops adaptive sparse global attention altogether, is catastrophic (Acc 0.016 → 0.047). The learned weight matrix that _compresses_ rather than _selects_ tokens is what preserves quality — and Table 10 shows the naive alternative (fixed learnable query latents à la Q-Former/Perceiver) fails badly (Acc 0.109), so the per-frame, input-dependent compression is doing real work.

### Faster and Better on Dense Sequences

The unusual result is that TurboVGGT often beats the dense-attention VGGT it accelerates, not just other accelerators. The paper attributes this to the adaptive sparse global attention. The pattern is dataset-dependent, though: it holds on 7-Scenes and ScanNet (dense) and fails on sparse RealEstate10K, where TurboVGGT trails several baselines. That is exactly the signature of a method exploiting inter-frame redundancy — when there is little redundancy, there is little to exploit.

### Memory Direction Matters

SparseVGGT and FastVGGT both _raise_ peak memory above VGGT's while lowering runtime; TurboVGGT lowers both. For deployment on long sequences, where the failure mode is out-of-memory rather than latency, that distinction is significant.

## 🔗 Related Work

- [VGGT](vggt.md) — the default backbone and the method being accelerated
- [pi3](pi3.md) — alternative backbone (TurboVGGT-π); notably the one where acceleration costs quality
- [MapAnything](mapanything.md) — alternative backbone (TurboVGGT-M) and source of the 13-dataset training mixture
- [FastVGGT](fastvggt.md) — token-merging accelerator, the closest competitor across all tables
- [Sparse-VGGT](sparse-vggt.md) — block-sparse attention accelerator, compared throughout
- [Fast3R](fast3r.md) — parallel multi-view baseline
- [TTT3R](ttt3r.md) — compared in the video depth estimation table
- [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md) — the feed-forward lineage
- [S-VGGT](s-vggt.md) — frame-level partitioning, a complementary axis of acceleration
- [VGGT-Long](vggt-long.md), [StreamVGGT](streamvggt.md) — scalability by chunking and streaming rather than attention redesign

## 📚 Key Takeaways

1. **Global attention is ~24× the cost of frame attention** per layer on 7-Scenes — the paper's own measurement, and the reason the whole design targets that one component.
2. **The optimal sparsity ratio varies by layer and by frame.** A gating network routes each frame per layer to one of three branches at 75%, 89%, or 94% sparsity.
3. **Compression beats selection.** Learned per-frame weight matrices produce representative tokens; removing this stage collapses accuracy (0.016 → 0.047), and a Q-Former-style fixed latent set fares far worse (0.109).
4. **It reduces memory, unlike its competitors.** Peak inference memory 23.47 GB versus VGGT 25.24, SparseVGGT 27.84, FastVGGT 31.18.
5. **Gains are concentrated on dense sequences.** TurboVGGT leads on 7-Scenes, N-RGBD, and ScanNet, but trails several methods on sparse RealEstate10K pose AUC@30.
6. **Backbone transfer is not uniformly free.** On π³ the acceleration costs a small amount of quality on nearly every metric, while on VGGT and MapAnything it improves quality.
7. **The sparsity regularizer helps quality too** — λ_reg = 0.01 beats λ_reg = 0 on AUC@30, AbsRel, _and_ time.

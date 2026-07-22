# Speed3R: Sparse Feed-forward 3D Reconstruction Models (CVPR 2026)

![speed3r — architecture](https://arxiv.org/html/2603.08055v1/x2.png)

_Architecture (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Weining Ren, Xiao Tan, Kai Han
- **Institution**: The University of Hong Kong, Baidu AMU
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.08055) | [Project Page](https://visual-ai.github.io/speed3r/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Replaces the global full-attention layer in VGGT and π³ with a trainable dual-branch Global Sparse Attention (compress + select), reaching a 12.4× speedup at 1024 input images while staying close to the dense backbones.

## 🎯 Key Contributions

1. **Global Sparse Attention (GSA)**: A drop-in replacement for the global attention module, with a Compression Branch producing a coarse scene summary and a Selection Branch attending to top-k full-resolution tokens, fused by a learned gate.
2. **Trainable, not post-hoc**: Unlike FastVGGT (token merge/unmerge) and Block-Sparse VGGT (top-k attention), GSA is trained end-to-end, which the paper argues is why it tolerates far higher sparsity.
3. **Fused Triton kernel**: A streaming Top-K algorithm integrated into the FlashAttention workflow, so selection indices and compression output are produced in one pass without materializing the full score matrix.
4. **Two backbones validated**: Speed3R-VGGT (which must preserve VGGT's reference-frame/camera-token inductive bias) and Speed3R-π³ (which can drop register tokens entirely).
5. **Zero-shot test-time adaptation**: Raising top-k at inference beyond the training value improves long-sequence results without retraining.

## 🔧 Technical Details

### The two branches

Special tokens (camera tokens, registers) keep standard dense self-attention over all tokens — cheap because `M_spec` is small. Image tokens go through:

- **Compression Branch**: QKV are average-pooled with a non-overlapping `s × s` window, attention is computed entirely in the compressed space, and the coarse output is upsampled back by nearest-neighbor interpolation. A guide score matrix `S_guide = Q_comp K_compᵀ` falls out of the same computation.
- **Selection Branch**: `TopKSelect(·)` on `S_guide` picks the most relevant coarse regions per query; the corresponding full-resolution KV pairs form `K_sel, V_sel`, and attention runs only over those.
- **Gated aggregation**: `g = σ(W_g Q_img)`, `O_img = g ⊙ O_comp + (1 − g) ⊙ O_sel`.

### Backbone-specific adaptation

**Speed3R-VGGT**: VGGT designates frame 0 as a global reference. The Selection Branch attention set is therefore the concatenation of (i) a fixed global context set — all tokens from the reference frame plus frames sampled at 100-frame intervals — and (ii) the dynamically selected top-k windows from non-reference frames.

**Speed3R-π³**: π³ has neither a reference frame nor camera tokens, so GSA applies directly. The paper reports that π³'s register tokens can be omitted in the sparse variant without a performance drop.

### Distillation

Both variants are trained as students of their pre-trained dense teacher, with the teacher's depth and camera predictions as pseudo ground truth: `L_total = L_depth + λ L_camera`, using the original backbones' loss forms.

### Training setup

Seven datasets (ArkitScenes, ScanNet++, DL3DV, CO3D, Hypersim, WildRGBD, VirtualKitti2). Sparse weights initialized from the dense counterpart. 80 epochs × 800 steps, ~7 days on 8 NVIDIA H20 GPUs, LR 1e-5, gradient accumulation 4 for an effective batch of 32. Default config: 4×4 compression window, top-32 blocks. Inference benchmarked on a single H100.

## 📊 Results

### Two-view pose on ScanNet-1500

원논문 Table 1. AUC of pose error, higher is better.

| Method            | AUC@5 ↑   | AUC@10 ↑  | AUC@20 ↑  |
| ----------------- | --------- | --------- | --------- |
| VGGT              | **37.45** | **59.24** | **75.69** |
| Block Sparse-VGGT | 33.21     | 55.11     | 72.51     |
| FastVGGT-VGGT     | 33.59     | 56.21     | 73.47     |
| Speed3R-VGGT      | 37.02     | 59.11     | 75.62     |
| π³                | **38.76** | **61.57** | **77.61** |
| Block Sparse-π³   | 35.13     | 57.74     | 74.98     |
| FastVGGT-π³       | 34.87     | 58.31     | 75.51     |
| Speed3R-π³        | 36.97     | 59.83     | 76.38     |

Speed3R beats the training-free sparse baselines but **loses to both dense backbones** on this benchmark.

### Multi-view pose on RE10K and CO3Dv2

원논문 Table 2, ~10 images per scene.

| Method            | Sparse ratio (%) / anchors | RE10K AUC@30 ↑ | CO3Dv2 AUC@30 ↑ |
| ----------------- | -------------------------- | -------------- | --------------- |
| VGGT              | 0                          | 74.17          | **88.33**       |
| Block Sparse-VGGT | 75                         | 63.82          | 79.92           |
| SAIL-Recon        | 10 anchor                  | 74.31          | 87.63           |
| FastVGGT          | 82                         | 69.99          | 84.03           |
| Speed3R-VGGT      | 84                         | **74.81**      | 87.71           |
| π³                | 0                          | **87.37**      | **89.67**       |
| Block Sparse-π³   | 75                         | 75.39          | 80.72           |
| FastVGGT-π³       | 90                         | 86.04          | 86.39           |
| Speed3R-π³        | 94                         | 87.17          | 89.41           |

Speed3R-VGGT at 84% sparsity surpasses dense VGGT on RE10K (74.81 vs 74.17); Speed3R-π³ at 94% sparsity nearly matches dense π³ but does not exceed it.

### Long-sequence pose on Tanks & Temples

원논문 Table 3, ~300 images per scene.

| Method                  | RRA@5 ↑   | RTA@5 ↑   | AUC@30 ↑  | Time [s] ↓ |
| ----------------------- | --------- | --------- | --------- | ---------- |
| VGGT                    | **70.29** | **79.30** | **77.67** | 34.51      |
| Block Sparse-VGGT       | 66.83     | 71.29     | 74.15     | 10.79      |
| SAIL-Recon (100 anchor) | 69.72     | 75.16     | 75.70     | 53.02      |
| FastVGGT                | 69.28     | 77.98     | 76.29     | 15.98      |
| Speed3R-VGGT            | 69.51     | 77.81     | 76.57     | **6.55**   |
| π³                      | **72.14** | **81.26** | 79.63     | 22.32      |
| Block Sparse-π³         | 67.85     | 78.91     | 76.64     | 8.16       |
| FastVGGT-π³             | 69.78     | 79.51     | 77.76     | 11.96      |
| Speed3R-π³              | 70.72     | 80.72     | **79.77** | **4.19**   |

The paper states a **5.2× speedup over the dense VGGT baseline** and that Speed3R-π³ is **5.3× faster** than dense π³ on this benchmark. (The prose quotes 6.65s for Speed3R-VGGT while the table prints 6.55s; the table value is used here.)

### Pointmap estimation on DTU and ETH3D

원논문 Table 4, mean values only (the paper also reports medians).

| Method            | DTU Acc. ↓ | DTU Comp. ↓ | DTU N.C. ↑ | ETH3D Acc. ↓ | ETH3D Comp. ↓ | ETH3D N.C. ↑ |
| ----------------- | ---------- | ----------- | ---------- | ------------ | ------------- | ------------ |
| VGGT              | 1.403      | 2.566       | **0.658**  | 0.289        | 0.294         | 0.847        |
| Block Sparse-VGGT | 1.966      | 2.311       | 0.647      | 0.861        | 1.171         | 0.681        |
| FastVGGT-VGGT     | 1.466      | 2.385       | 0.654      | 0.510        | 0.580         | 0.788        |
| Speed3R-VGGT      | **1.426**  | **2.179**   | 0.657      | **0.295**    | **0.289**     | **0.853**    |
| π³                | **1.151**  | **1.793**   | **0.668**  | **0.194**    | 0.220         | 0.867        |
| Block Sparse-π³   | 2.434      | 2.714       | 0.664      | 0.313        | 0.439         | 0.816        |
| FastVGGT-π³       | 1.255      | 2.250       | 0.650      | 0.291        | 0.291         | 0.841        |
| Speed3R-π³        | 1.175      | 2.037       | 0.657      | 0.198        | **0.213**     | **0.878**    |

Speed3R is best among sparse methods on nearly all metrics, but **dense π³ still wins DTU Acc./Comp. and ETH3D Acc.**

### Latency by sequence length

원논문 Figure 4 table. Mean latency in seconds.

| Method          | 32   | 64   | 128  | 256   | 512   | 1024   |
| --------------- | ---- | ---- | ---- | ----- | ----- | ------ |
| Full Attn. (π³) | 0.50 | 1.31 | 3.97 | 13.41 | 50.01 | 202.39 |
| Block Sparse    | 0.46 | 0.85 | 1.69 | 3.77  | 9.64  | 29.58  |
| FastVGGT        | 0.44 | 0.88 | 1.96 | 4.95  | 14.13 | 45.49  |
| Ours            | 0.37 | 0.71 | 1.44 | 3.06  | 6.83  | 16.38  |

The **12.4× speedup** headline is stated for an input length of 1024 images against the full-attention π³ baseline.

### Ablations (Speed3R-π³)

원논문 Table 5. Trained 40 epochs with gradient accumulation 2, so absolute values differ from the flagship model.

| Variant                        | RE10K AUC@30 ↑ | T&T AUC@30 ↑ | Time [s] ↓ |
| ------------------------------ | -------------- | ------------ | ---------- |
| Base (4×4 window, top-32)      | 86.35          | 78.69        | 4.19       |
| (1) w/o Compress. Branch Value | 86.29          | 77.90        | 3.99       |
| (2) w/o Select. Branch         | 83.44          | 76.84        | 3.56       |
| (3) w/ register                | 86.39          | 78.57        | 4.25       |
| (4) Top-8                      | 85.37          | 78.17        | 3.72       |
| (6) Top-64                     | 86.42          | 78.90        | 4.64       |
| (7) 8×8 window                 | 86.49          | 78.71        | 5.27       |
| (8) w/o distillation           | 85.18          | 77.81        | 4.19       |

Removing the Selection Branch is the most damaging; removing distillation costs ~1.2 AUC on RE10K at identical runtime.

### Test-time adaptation on Tanks & Temples

원논문 Table 7. The model is trained at top-32; top-k is raised only at inference.

| Method               | RRA@5 ↑ | RTA@5 ↑   | AUC@30 ↑  | Time [s] ↓ |
| -------------------- | ------- | --------- | --------- | ---------- |
| π³ (dense)           | 72.14   | 81.26     | 79.63     | 22.32      |
| Speed3R-π³ (top-8)   | 69.73   | 77.60     | 78.21     | 3.72       |
| Speed3R-π³ (top-32)  | 70.72   | 80.72     | 79.77     | 4.19       |
| Speed3R-π³ (top-64)  | 71.60   | 81.54     | 80.10     | 4.64       |
| Speed3R-π³ (top-128) | 71.89   | **82.00** | **80.33** | 6.07       |

At top-64 and above the sparse model overtakes dense π³ on RTA@5 and AUC@30 while remaining several times faster — but never on RRA@5.

## 💡 Insights & Impact

### Trainable sparsity beats post-hoc sparsity

The consistent pattern across Tables 1–4 is that FastVGGT and Block-Sparse VGGT degrade noticeably at moderate sparsity, while Speed3R holds accuracy at 84–94% sparsity. The paper's explanation is that training-free methods cannot adapt the representation to the pruning, so aggressive pruning breaks it.

### Precision, not perception, is the hard part

The Discussion section is unusually candid: pose regression demands high numerical precision, unlike the probabilistic objectives of text or image generation where sparse attention has flourished. Speed3R matches dense models at AUC@30 but still underperforms at the stricter AUC@5 threshold. The authors also report that training the sparse model to comparable loss takes 1.12× less time than full attention, arguing the gap is a data/compute limitation rather than a capacity one.

### Sparsity as an inference-time dial

Test-time adaptation (Table 7) means one trained checkpoint spans a whole efficiency-accuracy curve. This is a practical property that merge-based methods with fixed ratios do not offer as cleanly.

### Cost of the design

The dual-branch GSA incurs a **15% memory overhead** versus full attention. The paper notes this is manageable — up to 1024 images on an 80GB GPU — and points to SAIL-Recon's strategy as a route past the memory ceiling.

## 🔗 Related Work

- [VGGT](vggt.md) and [π³](pi3.md) — the two backbones Speed3R sparsifies
- [FastVGGT](fastvggt.md) — the training-free token merge/unmerge baseline it consistently beats
- [DUSt3R](../foundation/dust3r.md) and [MASt3R](../foundation/mast3r.md) — the pairwise ancestors
- [CUT3R](../dynamic/cut3r.md) and [Spann3R](spann3r.md) — cited as the sequential-input extensions
- [Fast3R](fast3r.md) — cited among the multi-view feed-forward family

## 📚 Key Takeaways

1. **Sparse attention can be trained into a geometry model.** GSA reaches 84–94% sparsity with small accuracy loss where training-free pruning at 75% already degrades badly.
2. **The 12.4× number has a precise setting**: sequence length 1024, against full-attention π³, on an H100. At 300-image Tanks & Temples the paper claims 5.2× (VGGT) and 5.3× (π³).
3. **Speed3R does not beat its teachers in general.** It loses ScanNet-1500 AUC to both dense backbones and loses DTU accuracy to dense π³; it wins RE10K AUC@30 over dense VGGT and T&T AUC@30 over dense π³.
4. **Distillation carries real weight** — removing it costs accuracy at no runtime benefit (Table 5, row 8).
5. **Architecture dictates the adaptation.** VGGT's reference frame and register tokens must be protected inside the selection set; π³'s permutation-equivariant design lets the register tokens go.

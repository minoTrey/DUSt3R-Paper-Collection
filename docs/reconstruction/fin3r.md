# Fin3R: Fine-tuning Feed-forward 3D Reconstruction Models via Monocular Knowledge Distillation (NeurIPS 2025)

![fin3r — architecture](https://arxiv.org/html/2511.22429/x3.png)

_Pipeline of our method (원논문 Fig. 4)_

## 📋 Overview

- **Authors**: Weining Ren, Hongjun Wang, Xiao Tan, Kai Han
- **Institution**: Visual AI Lab, The University of Hong Kong; Department of Computer Vision Technology (VIS), Baidu Inc.
- **Venue**: NeurIPS 2025
- **Links**: [Paper](https://arxiv.org/abs/2511.22429) | [Project Page](https://visual-ai.github.io/fin3r)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A lightweight fine-tuning recipe that freezes the decoder and distills a monocular teacher into the image encoder through a re-normalised LoRA adapter, sharpening geometry in DUSt3R, MASt3R, CUT3R, and VGGT without changing test-time memory or latency.

## 🎯 Key Contributions

1. **Encoder-only distillation**: the decoder — which handles cross-view matching — is frozen, and only the shared image encoder is enriched with fine geometric detail distilled from a strong monocular teacher (MoGe) on large unlabeled data.
2. **Re-normalisation LoRA**: the diagnosis that single-view distillation inflates encoder feature norms beyond the frozen decoder's expected range, and a fix that rescales the LoRA-updated weight back to its original norm.
3. **Generality**: validated as a drop-in fine-tune across DUSt3R, MASt3R, CUT3R, and VGGT, adding only tiny LoRA weights.

## 🔧 Technical Details

### The two diagnosed problems

**Data scarcity.** Existing real-world datasets have noisy depth and pose labels and limited multi-view coverage, which caps how much fine detail the geometry heads can learn.

**Long-sequence degradation.** Pointmap regression to a reference frame has three compounding failure modes: (1) _coupled prediction_ — pose and depth estimation are entangled, so pose error is injected into the geometry heads; (2) _drift_ — error grows as views move away from the reference frame; (3) _scale uncertainty_ — the normalisation required for scale consistency erodes fine foreground boundaries along the epipolar line in non-reference views.

### Method

The pipeline mixes roughly 10% labeled multi-view data with roughly 90% unlabeled single-view data. The encoder carries a trainable LoRA adapter; the decoder and heads are frozen. Two supervisions run in parallel: monocular distillation from the teacher onto the self-view head, and pointmap regression on the multi-view portion.

### Feature re-normalisation

Naïve full-parameter encoder distillation improved single-view detail but damaged multi-view matching even with the decoder frozen. Figure 3 traces the cause: single-view distillation drives a continuous increase in encoder patch-token feature norms (VGGT average norm 9.61; LoRA only 10.53; LoRA+Replay 10.34; full method 9.73), pushing activations outside the frozen decoder's expected distribution. The fix rescales after each update:

```text
W' = (W + ΔW) · ‖W‖₂ / ‖W + ΔW‖₂
```

This preserves the original weight norm, and therefore the activation distribution the frozen decoder was trained against, while retaining LoRA's benefit. The authors note it is not guaranteed to address all feature shifts but was effective in most cases.

### Losses

Both terms are heteroscedastic, weighted by learned aleatoric uncertainty:

- Distillation: `L_distill^(i) = β_i^D ‖D_i − D̂_i‖₂² − λ log β_i^D`, with `D̂_i` the teacher pseudo-label.
- Pointmap: `L_pointmap^(i) = 1_mv(i)[ β_i^P ‖P_i − P_i^GT‖₂² − λ log β_i^P ]`, gated by an indicator that is 1 only for multi-view samples.

### Training setup

Teacher is MoGe. Since MoGe's depth is affine-invariant, the shift in the z-component is subtracted before applying DUSt3R's normalisation. DUSt3R uses 2-view data with distillation applied only to the view-1 pointmap head; CUT3R and VGGT use 2–8 views with supervision on the self-view or depth head. Each epoch samples 20,000 images from SA-1B, 1,000 from Hypersim, and 1,000 from TartanAir. 10 epochs on four NVIDIA L20 GPUs over a single day.

## 📊 Results

### Monocular depth estimation

원논문 Table 1, scale-invariant relative depth. Rel is lower-better, δ1 higher-better. The Average column across the paper's seven benchmarks:

| Method      | NYUv2 Rel↓ | KITTI Rel↓ | ETH3D Rel↓ | DDAD Rel↓ | Average Rel↓ | Average δ1↑ |
| ----------- | ---------- | ---------- | ---------- | --------- | ------------ | ----------- |
| DUSt3R      | 3.83       | 7.64       | 5.35       | 17.34     | 7.03         | 92.3        |
| DUSt3R+Ours | **3.68**   | **6.02**   | **4.41**   | **13.11** | **5.58**     | **94.8**    |
| CUT3R       | 3.73       | 7.20       | 4.69       | 15.62     | 6.46         | 92.9        |
| CUT3R+Ours  | **3.68**   | **5.93**   | **4.67**   | **13.12** | **5.59**     | **94.7**    |
| VGGT        | 3.14       | 5.83       | 3.64       | 13.74     | 5.77         | 94.0        |
| VGGT+Ours   | **3.10**   | **4.59**   | **3.07**   | **10.65** | **4.29**     | **96.7**    |

Every base model improves on the average, and no per-dataset regression appears in these columns.

### Relative camera pose (ScanNet1500)

원논문 Table 2. AUC at 5/10/20 degrees, higher better.

| Method          | AUC@5     | AUC@10    | AUC@20    |
| --------------- | --------- | --------- | --------- |
| Efficient LoFTR | 19.20     | 37.00     | 53.60     |
| ROMA            | 28.90     | 50.40     | 68.30     |
| NoPoSplat       | 31.80     | 53.80     | 71.70     |
| DUSt3R          | 31.61     | 53.77     | 70.99     |
| DUSt3R+Ours     | 33.73     | 55.67     | 72.66     |
| MASt3R          | 37.60     | 59.96     | 76.24     |
| MASt3R+Ours     | **37.93** | **60.21** | **76.68** |
| VGGT            | 28.40     | 47.36     | 61.51     |
| VGGT+Ours       | 35.21     | 56.70     | 72.80     |
| Reloc3r         | 34.79     | 58.37     | 75.56     |

The paper highlights that fine-tuned VGGT overtakes Reloc3r at the 5° threshold despite Reloc3r being a dedicated pose regressor.

### Multi-view pose estimation (RealEstate10k)

원논문 Table 3.

| Method      | RRA@5↑    | RTA@5↑    | AUC@30↑   |
| ----------- | --------- | --------- | --------- |
| DUSt3R      | 94.01     | 42.39     | 62.40     |
| DUSt3R+Ours | 95.41     | 47.07     | 64.81     |
| MASt3R      | 94.89     | 52.21     | 73.45     |
| MASt3R+Ours | 95.02     | 53.74     | 73.87     |
| CUT3R       | 96.66     | 61.66     | 78.95     |
| CUT3R+Ours  | **96.99** | **62.15** | **79.13** |
| VGGT        | 95.28     | 53.14     | 74.18     |
| VGGT+Ours   | 96.27     | 56.54     | 75.35     |

### Video depth estimation

원논문 Table 4.

| Method     | ETH3D rel↓ | T&T rel↓  | KITTI rel↓ | Sintel rel↓ | Bonn rel↓ |
| ---------- | ---------- | --------- | ---------- | ----------- | --------- |
| CUT3R      | **0.126**  | 0.209     | 0.123      | 0.428       | 0.077     |
| CUT3R+Ours | 0.130      | 0.180     | 0.112      | 0.406       | 0.062     |
| VGGT       | 0.044      | 0.137     | 0.072      | 0.301       | 0.052     |
| VGGT+Ours  | **0.041**  | **0.115** | **0.069**  | **0.252**   | **0.048** |

CUT3R+Ours regresses slightly on ETH3D (0.130 vs 0.126) while improving on the other four datasets. The paper also notes VGGT is not trained on dynamic datasets, so its Sintel ceiling may be a data limitation rather than a fine-tuning one.

### Multi-view pointmap regression (7-Scenes, NRGBD)

원논문 Table 5, mean values. Acc and Comp lower-better, NC (normal consistency) higher-better. DUSt3R uses global alignment; the others are feed-forward. Umeyama alignment is applied for the scale-invariant models.

| Method      | 7-Sc Acc↓ | 7-Sc Comp↓ | 7-Sc NC↑  | NRGBD Acc↓ | NRGBD Comp↓ | NRGBD NC↑ |
| ----------- | --------- | ---------- | --------- | ---------- | ----------- | --------- |
| DUSt3R      | 0.026     | 0.033      | 0.641     | 0.050      | 0.036       | 0.851     |
| DUSt3R+Ours | 0.024     | 0.029      | 0.641     | 0.043      | 0.030       | 0.863     |
| CUT3R       | **0.024** | 0.029      | 0.664     | **0.075**  | 0.046       | 0.828     |
| CUT3R+Ours  | 0.025     | 0.026      | 0.666     | **0.075**  | 0.043       | 0.833     |
| VGGT        | 0.017     | 0.024      | 0.645     | **0.019**  | **0.018**   | 0.914     |
| VGGT+Ours   | **0.012** | **0.023**  | **0.651** | 0.021      | 0.020       | **0.921** |

Two honest regressions: CUT3R+Ours is marginally worse on 7-Scenes Acc, and VGGT+Ours is worse on both NRGBD Acc and Comp while improving NC.

### Pointmap regression (DTU, ETH3D)

원논문 Table 6, mean values.

| Method    | DTU Acc.↓ | DTU Comp.↓ | DTU N.C.↑ | ETH3D Acc.↓ | ETH3D Comp.↓ | ETH3D N.C.↑ |
| --------- | --------- | ---------- | --------- | ----------- | ------------ | ----------- |
| Pi3       | 1.151     | **1.793**  | 0.668     | **0.194**   | 0.220        | **0.867**   |
| VGGT      | 1.187     | 2.229      | 0.694     | 0.290       | 0.371        | 0.839       |
| VGGT+Ours | **0.948** | 1.879      | **0.699** | 0.209       | **0.170**    | 0.861       |

Against the concurrent Pi3, the paper claims comparable performance at much lower fine-tuning cost — not a clean win: Pi3 retains DTU Completeness, ETH3D Accuracy, and ETH3D N.C.

### Ablations

원논문 Table 7. Distillation pipeline on VGGT. Rel/δ1 are mean monocular depth metrics; Acc is 7-Scenes accuracy.

| Label Supv. | Mono. Teacher | SA-1B | Rel ↓    | δ1 ↑     | Acc ↓     |
| ----------- | ------------- | ----- | -------- | -------- | --------- |
| ✗           | ✗             | ✗     | 5.68     | 94.1     | 0.017     |
| ✓           | ✗             | ✗     | 5.21     | 95.0     | 0.014     |
| ✗           | ✓             | ✗     | 5.00     | 95.3     | 0.013     |
| ✗           | ✓             | ✓     | **4.35** | **96.3** | **0.012** |

원논문 Table 8. Fine-tuning strategy on ScanNet relative pose with VGGT.

| Method                 | AUC@5     | AUC@10    | AUC@20    |
| ---------------------- | --------- | --------- | --------- |
| VGGT                   | 28.40     | 47.36     | 61.51     |
| (1) +Dec. Full         | 28.42     | 51.59     | 67.30     |
| (2) +Enc. Full         | 32.06     | 52.29     | 68.04     |
| (3) +Enc.&Dec. Full    | 26.35     | 45.90     | 60.02     |
| (4) +Enc. Lora         | 32.96     | 54.21     | 70.40     |
| (5) +Enc. Lora+Re-norm | **35.21** | **56.70** | **72.80** |

Row (3) is the key negative result: fine-tuning encoder and decoder together with monocular data drops _below_ the untouched VGGT baseline, confirming that decoder matching is what monocular data damages.

## 💡 Insights & Impact

### A clean division of labour

The paper's argument is architectural: feed-forward reconstruction models all share the shape _encoder → cross-view decoder → heads_, and the two things they are bad at come from different places. Blurry boundaries and over-smoothed fine structure are a _feature extraction_ deficiency, fixable with monocular data that is abundant and unlabeled. Cross-view matching is a _decoder_ capability learned from scarce multi-view supervision that monocular data actively degrades. Touching only the encoder therefore gets the upside without the downside — and the ablation shows that touching both is worse than touching nothing.

### Norm drift as the concrete failure mode

The most reusable technical contribution is not LoRA itself but the observation that the freezing boundary is leaky. A frozen decoder is only frozen with respect to its _weights_; the distribution of activations arriving at it can still shift. Feature-norm re-normalisation restores that implicit contract, and it is worth 2.25 AUC@5 over plain encoder LoRA.

### Cost profile

The whole recipe is 10 epochs on four L20 GPUs in a single day, adding only LoRA weights that leave test-time memory and latency virtually unchanged. That is a very different cost bracket from retraining a foundation model, and it is the basis for the claim of comparable results to Pi3 at a fraction of the resources.

### What it does not fix

Multi-view pointmap accuracy on NRGBD gets slightly worse for VGGT, and CUT3R regresses on ETH3D video depth. Improvements are concentrated in single-view detail and pose; genuinely multi-view geometry is preserved rather than uniformly improved, which is exactly what an encoder-only, decoder-frozen method should be expected to do.

## 🔗 Related Work

- [VGGT](./vggt.md) — the primary fine-tuning target and the strongest base model.
- [DUSt3R](../foundation/dust3r.md) and [MASt3R](../foundation/mast3r.md) — the two-view bases fine-tuned.
- [CUT3R](../dynamic/cut3r.md) — the recurrent base fine-tuned.
- [MoGe](./moge.md) — the monocular teacher supplying pseudo-labels.
- [pi3](./pi3.md) — the concurrent model compared against on DTU and ETH3D.
- [Reloc3r](../pose/reloc3r.md) — dedicated pose regressor overtaken at AUC@5 by fine-tuned VGGT.
- [Spann3R](./spann3r.md) — source of the 7-Scenes / NRGBD evaluation protocol.

## 📚 Key Takeaways

1. **Freeze the matcher, sharpen the extractor.** The encoder is where geometric detail is lost; the decoder is where multi-view consistency lives. Fine-tuning both together is worse than doing nothing (28.40 → 26.35 AUC@5).
2. **Frozen weights do not guarantee a frozen interface.** Feature-norm drift breaks a frozen decoder from the outside; re-normalising the LoRA-updated weight to its original norm is the fix.
3. **Unlabeled monocular data is a usable substitute** for the scarce, noisy multi-view supervision that limits these models — a monocular teacher on SA-1B beats training on dataset depth labels.
4. **Cheap and general.** One day on four L20s, applied unchanged to four different base models, with negligible inference overhead.
5. **Report the regressions.** NRGBD pointmap accuracy for VGGT and ETH3D video depth for CUT3R both get marginally worse.

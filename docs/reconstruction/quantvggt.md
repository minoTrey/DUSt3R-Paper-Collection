# QuantVGGT: Quantized Visual Geometry Grounded Transformer (ICLR 2026)

![quantvggt — architecture](https://arxiv.org/html/2509.21302v4/x2.png)

_Overview of proposed QuantVGGT (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Weilun Feng, Haotong Qin, Mingqiang Wu, Chuanguang Yang, Yuqi Li, Xiangqi Li, Zhulin An, Libo Huang, Yulun Zhang, Michele Magno, Yongjun Xu
- **Institution**: State Key Laboratory of AI Safety, Institute of Computing Technology, Chinese Academy of Sciences; University of Chinese Academy of Sciences; ETH Zürich; City College of New York, City University of New York; Shanghai Jiao Tong University
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2509.21302) | [Code](https://github.com/wlfeng0509/QuantVGGT)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: The first post-training quantization framework built for VGGT, combining Hadamard rotation with post-rotation channel smoothing and a noise-filtered, frame-aware calibration sampler to keep W4A4 accuracy near full precision.

## 🎯 Key Contributions

1. **First PTQ analysis of VGGT**, identifying two model-specific obstacles: data-independent special tokens (camera + register tokens) that produce heavy-tailed activations, and the semantic complexity of multi-view 3D data that destabilizes calibration sampling.
2. **Dual-Smoothed Fine-Grained Quantization (DSFQ)**: a pre-global Hadamard rotation that disperses outliers, followed by post-local channel-wise smoothing derived from the _rotated_ distribution.
3. **Noise-Filtered Diverse Sampling (NFDS)**: filters outlier calibration candidates using deep-layer statistics, then clusters the survivors by frame-wise correlation to VGGT's first frame.
4. **Deployment evidence**: real-hardware latency and memory measurements on a single RTX 4090, not just simulated quantization.

## 🔧 Technical Details

### Why VGGT resists standard PTQ

VGGT injects one camera token and four register tokens per frame, with a distinct set `t_f` for the first frame and a shared set `t_o` for the rest. These are _pretrained constants_, not encoded from input images, so their activation magnitudes sit far outside the regular patch-token distribution. In quantization, a handful of such extreme values monopolizes the available bins.

### Dual-Smoothed Fine-Grained Quantization

**Pre-Global-Rotation.** A random Hadamard matrix `H = Ĥ·diag(v)` with `H^T H = I` preserves the matmul, `XW^T = (XH)(WH)^T`, while the central-limit effect pushes the rotated values toward a Gaussian, flattening the heavy tail.

**Post-Local-Smooth.** Rotation only mitigates _global_ skew; per-channel variance survives. Rather than SmoothQuant's `c_i = max(|X_i|)^α / max(|W_i|)^(1−α)`, the scale is computed on the rotated distribution:

```text
ĉ_i = max(|X_i H|)^α / max(|W_i H|)^(1−α)      (α = 0.5)
```

Order matters: smoothing _after_ rotation is stable, because rotation-after-smoothing rearranges outliers across channels and weakens the scaling. The scales fold into neighboring normalization layers, so they cost nothing at runtime.

**Granularity.** Only the inner dimension `d_in` is summed in a matmul, so the outer dimension can carry finer scales: out-dimension-wise for weights, token-wise (dynamic) for activations.

### Noise-Filtered Diverse Sampling

Theorem 3.2 in the paper argues that a calibration set maximizes information when samples are drawn from sub-regions in proportion to their scale — in practice, cluster and sample uniformly within clusters.

1. **Filter**: per-sample mean and variance are collected across deep layers, converted to a robust z-score, and only the lowest `p` fraction is kept (`p = 0.2`).
2. **Cluster**: labels are a poor grouping signal for geometry scenes. Instead, exploiting VGGT's inductive bias of modeling frames _relative to the first frame_, a correlation vector `c_i ∈ R^{f−1}` of cosine similarities between frame 0 and each later frame is built and clustered with K-Means (`K = 8`).
3. **Sample**: uniformly inside each cluster — 40 samples drawn from a 400-sample pool.

## 📊 Results

### Camera Pose Estimation on CO3Dv2

원논문 Table 1. Selected rows; the paper also reports BRECQ, QDrop, DopQ-ViT, RepQ-ViT, and AWQ.

| Method      | Bit-Width (W/A) | 10f AUC@30 ↑ | 10f AUC@15 ↑ | 10f AUC@5 ↑ | 20f AUC@30 ↑ | 20f AUC@15 ↑ | 20f AUC@5 ↑ |
| ----------- | --------------- | ------------ | ------------ | ----------- | ------------ | ------------ | ----------- |
| Full Prec.  | 16/16           | 89.5         | 83.2         | 66.1        | 90.0         | 83.9         | 67.8        |
| RTN         | 8/8             | 88.1         | 80.7         | 60.3        | 88.1         | 80.6         | 60.2        |
| QuaRot      | 8/8             | 89.4         | 83.0         | 65.9        | 89.4         | 83.0         | 66.0        |
| QuantVGGT   | 8/8             | 89.4         | 83.1         | 66.1        | 89.6         | 83.2         | 66.0        |
| RTN         | 6/6             | 88.1         | 80.1         | 58.1        | 88.1         | 80.2         | 57.6        |
| QuaRot      | 6/6             | 89.0         | 81.8         | 62.5        | 89.1         | 81.9         | 62.6        |
| QuantVGGT   | 6/6             | 89.2         | 82.7         | 65.2        | 89.3         | 82.8         | 65.6        |
| RTN         | 4/4             | 77.7         | 63.9         | 31.4        | 75.8         | 60.7         | 26.5        |
| SmoothQuant | 4/4             | 75.4         | 60.1         | 25.8        | 75.4         | 60.1         | 25.5        |
| QuaRot      | 4/4             | 81.8         | 70.3         | 40.1        | 81.6         | 69.8         | 39.4        |
| QuantVGGT   | 4/4             | 86.9         | 78.7         | 57.3        | 88.2         | 80.2         | 58.9        |

**The loss is real.** At W8A8 QuantVGGT matches full precision on AUC@30 (89.4 vs 89.5, which the paper calls 99.9% preservation). At W4A4 it does not: AUC@30 drops from 89.5 to 86.9 at 10 frames, and the strict AUC@3 falls from 54.9 to 43.6. The paper's claim is that 88.2 out of 90.0 at 20 frames is "98% of the model's performance" — a genuine but non-trivial degradation, considerably smaller than QuaRot's.

### Point Map Estimation on DTU

원논문 Table 2. Calibration data comes entirely from CO3Dv2, so DTU is unseen during calibration.

| Method      | Bit-Width (W/A) | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ | N.C. Mean ↑ | N.C. Med. ↑ |
| ----------- | --------------- | ----------- | ----------- | ------------ | ------------ | ----------- | ----------- |
| Full Prec.  | 16/16           | 1.185       | 0.714       | 2.232        | 1.313        | 0.694       | 0.779       |
| RTN         | 8/8             | 1.216       | 0.730       | 2.237        | 1.310        | 0.687       | 0.773       |
| QuaRot      | 8/8             | 1.184       | 0.712       | 2.231        | 1.311        | 0.694       | 0.778       |
| QuantVGGT   | 8/8             | 1.182       | 0.710       | 2.215        | 1.276        | 0.700       | 0.788       |
| RTN         | 4/4             | 1.700       | 0.930       | 2.028        | 1.099        | 0.656       | 0.757       |
| SmoothQuant | 4/4             | 1.740       | 0.944       | 1.993        | 1.083        | 0.675       | 0.764       |
| GPTQ        | 4/4             | 1.442       | 0.899       | 1.997        | 1.068        | 0.675       | 0.761       |
| QuaRot      | 4/4             | 1.593       | 0.916       | 2.034        | 1.096        | 0.670       | 0.757       |
| QuantVGGT   | 4/4             | 1.282       | 0.743       | 1.992        | 1.068        | 0.681       | 0.774       |

At W4A4, Acc. Mean degrades from 1.185 to 1.282 and N.C. Mean from 0.694 to 0.681 — closer to full precision than any baseline, but still below it.

### Point Cloud Reconstruction (W4A4)

원논문 Table 3.

| Dataset  | Method      | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ | N.C. Mean ↑ | N.C. Med. ↑ |
| -------- | ----------- | ----------- | ----------- | ------------ | ------------ | ----------- | ----------- |
| 7-Scenes | Full Prec.  | 0.025       | 0.013       | 0.036        | 0.020        | 0.728       | 0.836       |
| 7-Scenes | SmoothQuant | 0.370       | 0.261       | 0.498        | 0.361        | 0.484       | 0.477       |
| 7-Scenes | QuaRot      | 0.030       | 0.016       | 0.042        | 0.022        | 0.701       | 0.800       |
| 7-Scenes | QuantVGGT   | 0.026       | 0.013       | 0.037        | 0.019        | 0.718       | 0.812       |
| NRGBD    | Full Prec.  | 0.015       | 0.009       | 0.017        | 0.007        | 0.878       | 0.969       |
| NRGBD    | SmoothQuant | 0.479       | 0.393       | 0.614        | 0.489        | 0.515       | 0.513       |
| NRGBD    | QuaRot      | 0.034       | 0.021       | 0.030        | 0.015        | 0.820       | 0.948       |
| NRGBD    | QuantVGGT   | 0.019       | 0.013       | 0.021        | 0.010        | 0.850       | 0.959       |

### Ablation: Quantization Architecture (W4A4, CO3Dv2)

원논문 Table 4. `Base` = naive quantization with no smoothing; `Scale-Rot.` = smooth first, then rotate.

| Method     | AUC@30 ↑ | AUC@15 ↑ | AUC@5 ↑ | AUC@3 ↑ |
| ---------- | -------- | -------- | ------- | ------- |
| Full Prec. | 89.5     | 83.2     | 66.1    | 54.9    |
| Base       | 76.9     | 61.5     | 23.9    | 9.7     |
| Rotation   | 83.6     | 72.3     | 46.3    | 32.5    |
| Scale      | 81.9     | 70.1     | 38.5    | 21.2    |
| Scale-Rot. | 86.7     | 78.5     | 56.8    | 42.9    |
| DSFQ       | 86.9     | 78.7     | 57.3    | 43.6    |

### Efficiency

원논문 Table 14 (memory / latency optimization ratios) and Table 8 (granularity).

| Bit-width (W/A) | Memory Opt. ↑ | Latency Opt. ↑ |
| --------------- | ------------- | -------------- |
| 16/16           | 1.00×         | 1.00×          |
| 8/8 (naive)     | 1.94×         | 2.19×          |
| 8/8 (ours)      | 1.93×         | 2.17×          |
| 4/4 (ours)      | 3.65×         | 2.49×          |

The abstract and Figure 1 state the headline as **3.7× memory reduction and 2.5× acceleration** at W4A4 while "maintaining reconstruction accuracy above 98% of its full-precision counterpart"; Table 8 lists the W4A4 configuration at 3.65× memory and 2.50× (static) / 2.49× (dynamic token-wise) latency. Latency was measured on a single NVIDIA RTX 4090 24G with CUDA 12.4, using CUTLASS on top of PyTorch for low-bit INT matmul.

원논문 Table 15 reports W4A4 latency optimization across sequence lengths: 2.47× at 10 frames, 2.49× at 20, 2.53× at 40, 2.55× at 80.

### Comparison with a Token-Compression Accelerator

원논문 Table 7, CO3Dv2.

| Method    | FLOPs (T) ↓ | AUC@30 ↑ | AUC@15 ↑ | AUC@5 ↑ | AUC@3 ↑ |
| --------- | ----------- | -------- | -------- | ------- | ------- |
| VGGT      | 5.84        | 89.5     | 83.2     | 66.1    | 54.9    |
| FastVGGT  | 1.68        | 82.7     | 71.3     | 39.2    | 25.1    |
| QuantVGGT | 1.40        | 86.9     | 78.7     | 57.3    | 43.6    |

The paper is careful to frame these as **orthogonal and in principle combinable**, not as a replacement.

### Generality: Fast3R Backbone (W4A4, 7-Scenes)

원논문 Table 6.

| Method      | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ | N.C. Mean ↑ | N.C. Med. ↑ |
| ----------- | ----------- | ----------- | ------------ | ------------ | ----------- | ----------- |
| Full Prec.  | 0.049       | 0.021       | 0.069        | 0.021        | 0.624       | 0.683       |
| SmoothQuant | 0.497       | 0.448       | 0.319        | 0.244        | 0.586       | 0.625       |
| QuaRot      | 0.312       | 0.258       | 0.149        | 0.080        | 0.593       | 0.637       |
| QuantVGGT   | 0.049       | 0.022       | 0.070        | 0.022        | 0.624       | 0.683       |

### Calibration Cost

원논문 Table 13. Compared to the baseline PTQ pipeline, QuantVGGT adds 0.2 GB GPU memory and 0.14 hours of GPU time, for a total PTQ process of 2.67 hours — runnable on a consumer RTX 4090.

## 💡 Insights & Impact

**Special tokens are the quantization bottleneck.** The paper's central empirical claim is that VGGT's data-independent camera and register tokens — the first five tokens of every frame — are systematically more salient than image tokens across layers. This is a structural property of the architecture, not a data artifact, which is why generic LLM/2D-ViT quantizers (SmoothQuant, QuaRot, GPTQ) transfer poorly.

**Rotation and smoothing are complementary, and order matters.** Rotation alone reaches 83.6 AUC@30, smoothing alone 81.9, and the correct composition 86.9. The ablation isolates the ordering effect: `Scale-Rot.` (86.7) versus `DSFQ` (86.9), with the paper attributing the gap to rotation rearranging outliers between channels and thereby diluting a pre-computed scale.

**Calibration diversity matters more than in 2D.** Because each 3D input sequence spans multiple non-identical views, a randomly drawn calibration set is both biased and high-variance. Clustering by first-frame correlation — a signal chosen to match VGGT's inductive bias, not a generic feature clustering — reduces both. The paper's Figure 5 reports mean and variance over five seeds for Random / Filtered / Clustered / NFDS; the printed mean±std annotations show NFDS at 86.9±0.22 against Random at 85.4±0.96.

**Practical framing.** The whole PTQ run fits on one consumer GPU in under three hours with no retraining, which is the point: QAT improves low-bit accuracy further (Table 5) but the paper notes the compute overhead is substantial.

## 🔗 Related Work

- [VGGT](vggt.md) — the 1.2B-parameter model being quantized
- [FastVGGT](fastvggt.md) — token-merging acceleration, compared as an orthogonal approach
- [Fast3R](fast3r.md) — second backbone used to show the method generalizes
- [DUSt3R](../foundation/dust3r.md) — the pointmap-regression foundation
- [MASt3R](../foundation/mast3r.md) — confidence-weighted refinement of DUSt3R
- [CUT3R](../dynamic/cut3r.md) — cited as a learning-based reconstruction line

## 📚 Key Takeaways

1. **Billion-scale 3D transformers can run at 4 bits**, but not with off-the-shelf LLM quantizers — VGGT's pretrained special tokens break the assumptions those methods make about activation distributions.
2. **Rotate globally, then smooth locally.** Computing the smoothing scale in the rotated space is what makes the two techniques compose rather than interfere.
3. **Calibration set construction is a first-class problem for multi-view data.** Filtering outliers and clustering by frame-relative structure cuts both the mean error and the seed-to-seed variance.
4. **Report the W4A4 loss honestly.** W8A8 is effectively lossless; W4A4 costs roughly 2.6 AUC@30 points on CO3Dv2 and 0.097 Acc. Mean on DTU. That is the price of 3.65× memory and ~2.5× latency.
5. **Quantization and token merging are orthogonal.** QuantVGGT reaches lower FLOPs than FastVGGT at higher accuracy, and the authors suggest combining them rather than choosing.

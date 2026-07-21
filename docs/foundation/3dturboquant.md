# 3DTurboQuant: Training-Free Near-Optimal Quantization for 3D Reconstruction Models (arXiv preprint (2026-04))

## 📋 Overview

- **Authors**: Jae Joong Lee
- **Institution**: Department of Computer Science, Purdue University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.05366)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free, data-oblivious quantizer for 3D reconstruction models. A single random rotation makes the high-dimensional parameter vectors (45-D spherical harmonics in 3DGS, 1024-D KV vectors in DUSt3R) follow a known Beta distribution, so a precomputed Lloyd-Max codebook is near-optimal (within 2.7× of the information-theoretic bound). Compresses 3DGS by 3.5× (−0.02 dB) and DUSt3R KV caches by 7.9× (39.7 dB pointmap fidelity), in seconds, with no per-scene training or calibration.

## 🎯 Key Contributions

1. **Dimension-dependent quantization criterion**: Predicts which parameters can be quantized and at what bit-width `b` before any experiment, from the dimension `d` alone. Coordinates at `d = 45` are independent enough for near-optimal scalar quantization at `b ≥ 3`; `d = 3` (positions) and `d = 4` (quaternions) are not. At `b = 3, d = 45` the bound predicts `Dmse ≤ 0.03` and the paper measures 0.033 on Lego (a 10% gap).
2. **Norm-separation bounds**: 3D parameters are not unit-norm (unlike the setting of TurboQuant). Separating the norm `γi = ‖f_i‖₂` and quantizing the direction yields per-element MSE of `γi² · (√3π/2) · 4⁻ᵇ`, giving a closed-form prediction of rendering quality vs. bit-width.
3. **Entry-grouping for low-dimensional features**: Instant-NGP hash entries have `df = 2`, below the independence threshold. Grouping `g = ⌈16/df⌉` entries into `deff = g·df ≥ 16` dimensions extends the method to NeRF feature grids.
4. **Composable compression with derived rates**: Rotation-based quantization composes multiplicatively with opacity pruning (retaining fraction `ρ`) and SH degree reduction (factor `r`), with a closed-form total ratio `(1/ρ)·32/(b·r + 56/dsh)`, yielding 5–8× total 3DGS compression without retraining.

## 🔧 Technical Details

### Core Insight: Rotation → Known Distribution → Precomputed Codebook

The paper builds on TurboQuant (Zandieh et al. 2025a). Multiplying a `d`-dimensional vector by a random orthogonal matrix `Π` (from QR of a Gaussian matrix) produces coordinates that are uniform on `S^{d-1}`, so each coordinate follows the Beta distribution `fX` with variance `1/d`. In high `d` these coordinates are nearly independent, so a Lloyd-Max scalar quantizer for `fX` — which depends only on `(d, b)` and is precomputed once — is near-optimal. The MSE upper bound is `Dmse ≤ (√3π/2)·4⁻ᵇ ≈ 2.72·4⁻ᵇ`, and the ratio to the information-theoretic lower bound `1/4ᵇ` is `√3π/2 ≈ 2.7`.

Per-bit theoretical `Dmse` values (Theorem 2): `b = 1, 2, 3, 4 → 0.36, 0.117, 0.03, 0.009`.

### Design Requirements

The quantizer is (i) data-oblivious (no training/calibration data), (ii) online (each vector quantized independently, enabling streaming and dynamic scenes), and (iii) computationally efficient (orders of magnitude faster than training). The pipeline is identical across all three model families — only the dimension `d` differs (3DGS `d = 45`, DUSt3R KV `d = 1024`, NeRF grouped hash `d = 32`).

### Per-Family Application

- **3DGS**: Quantize the SH rest coefficients `f_i ∈ R⁴⁵` (`l = 3`), which occupy 180 of 236 bytes per Gaussian (76%). Positions (`d = 3`), quaternions (`d = 4`), scales (`d = 3`), opacity, and DC color stay in float32 — they are only 56 bytes (24%) but highly sensitive and too low-dimensional for the Beta approximation. Global overhead: rotation matrix `Π ∈ R⁴⁵ˣ⁴⁵` (8.1 KB) + codebook, stored once.
- **DUSt3R KV cache**: Quantize each key/value row `∈ R^{1024}` at every layer via a forward-pass hook — no model modification or retraining. At `dkv = 1024`, `Var(y_j) = 1/1024 ≈ 10⁻³`, so `b = 3–4` bits suffice.
- **NeRF (Instant-NGP)**: `df = 2` is too low, so `g` consecutive hash entries are concatenated to `deff ≥ 16` before rotation, then unpacked for inference. Higher-dim NeRF features (TensoRF `df = 48`, K-Planes `df = 64`) need no grouping.

### Experimental Setup

- **Dataset**: Lego scene from NeRF Synthetic (100 train / 200 test views, 800×800).
- **Models**: 3DGS (official impl, 30K iters, SH degree 3, 232,743 Gaussians, 57.7 MB PLY); DUSt3R ViT-Large (571M params, 48 attention layers); Instant-NGP (nerfstudio, 20K iters).
- **Metrics**: rendering PSNR (3DGS, NeRF), 3D pointmap PSNR (DUSt3R), compression ratio, and wall-clock quantization time on a single NVIDIA GPU.

## 📊 Results

### 3DGS Spherical Harmonic Compression (Lego)

원논문 Table 1. Lego 232K Gaussians, baseline PSNR = 29.80 dB, 200 test views. Render time is constant (~0.8 s). PSNR·Compression은 높을수록, ∆PSNR 절대값·SH MSE는 낮을수록 좋다.

| Bits (b)        | PSNR (dB) | ∆PSNR (dB) | Compression | Quant Time | SH MSE  |
| --------------- | --------- | ---------- | ----------- | ---------- | ------- |
| fp32 (baseline) | 29.80     | 0.00       | 1.0×        | –          | –       |
| 1               | 29.31     | -0.49      | 4.1×        | 4.2 s      | 0.00199 |
| 2               | 29.68     | -0.12      | 3.8×        | 6.6 s      | 0.00063 |
| 3               | 29.78     | -0.02      | 3.5×        | 9.3 s      | 0.00018 |
| 4               | 29.80     | -0.00      | 3.3×        | 12.2 s     | 0.00005 |

Normalizing the measured SH MSE by `γ̄² ≈ 0.0055` gives per-unit-norm MSE 0.36, 0.11, 0.033, 0.009 for `b = 1–4`, matching the theoretical bounds (0.36, 0.117, 0.03, 0.009) within 10%; the bound is tightest at `b = 1` (0.93×) and loosest at `b = 4` (1.50×).

### 3DGS With Pruning (Lego)

원논문 Table 2. All configs training-free. τ: opacity threshold; SHl′: reduced SH degree. Ratio는 높을수록 좋으나 ∆PSNR 손실과 trade-off.

| Configuration                  | Gaussians | PSNR (dB) | ∆PSNR (dB) | Ratio |
| ------------------------------ | --------- | --------- | ---------- | ----- |
| TQ b = 3 (quant only)          | 232,743   | 29.78     | -0.02      | 3.5×  |
| TQ b = 3 + prune τ = 0.05      | 196,887   | 29.63     | -0.17      | 4.1×  |
| TQ b = 3 + prune τ = 0.1       | 173,482   | 28.98     | -0.82      | 4.7×  |
| TQ b = 3 + prune τ = 0.2       | 144,022   | 27.21     | -2.59      | 5.6×  |
| TQ b = 3 + SH1                 | 232,743   | 28.06     | -1.74      | 4.3×  |
| TQ b = 3 + prune τ = 0.3 + SH1 | 123,863   | 25.05     | -4.75      | 8.0×  |

### DUSt3R KV Cache Compression (ViT-Large, 571M params, 48 layers, dkv = 1024)

원논문 Table 3. 5 Lego test view pairs, baseline inference 0.14 s. Ptmap PSNR·KV Compress는 높을수록, 3D Point MSE·Inf. Time·Overhead는 낮을수록 좋다.

| Bits (b) | Ptmap PSNR (dB) | 3D Point MSE | KV Compress | Inf. Time | Overhead |
| -------- | --------------- | ------------ | ----------- | --------- | -------- |
| fp32     | ∞               | 0            | 1.0×        | 0.14 s    | –        |
| 1        | 16.52           | 0.01386      | 31.0×       | 1.04 s    | +0.90 s  |
| 2        | 16.52           | 0.01386      | 15.8×       | 1.85 s    | +1.72 s  |
| 3        | 29.30           | 0.00078      | 10.6×       | 0.94 s    | +0.81 s  |
| 4        | 39.68           | 0.00007      | 7.9×        | 1.67 s    | +1.53 s  |
| 5        | 49.65           | 0.000008     | 6.4×        | 2.32 s    | +2.19 s  |
| 8        | 52.81           | 0.000003     | 4.0×        | 11.62 s   | +11.48 s |

A sharp phase transition occurs between `b = 2` and `b = 3`: pointmap PSNR jumps from 16.5 dB to 29.3 dB (a 12.8 dB gain from one bit), and 3D point MSE drops ~18× (0.014 → 0.00078). At `b = 4`, the 7.9× KV compression shrinks a 2-view pair's cache from 100 MB to 13 MB, enabling 8× more views in the same GPU memory. Below `b = 3` the method effectively fails — `b = 1` and `b = 2` are stuck at 16.52 dB, which the paper attributes to nonlinear error amplification in DUSt3R's DPT decoder (an effective noise floor around `Dmse ≈ 0.05` per coordinate).

### NeRF Hash Grid Compression (Instant-NGP, Lego)

원논문 Table 4. Low ratios reflect the 2D per-entry feature dimension. PSNR·Hash Compress는 높을수록 좋다. 이 표는 이 방법이 열세인 지점이다.

| Bits (b) | PSNR (dB) | ∆PSNR (dB) | Hash Compress | Quant Time |
| -------- | --------- | ---------- | ------------- | ---------- |
| fp32     | 11.57     | 0.00       | 1.0×          | –          |
| 1        | 9.70      | -1.87      | 1.9×          | 0.18 s     |
| 2        | 10.54     | -1.04      | 1.8×          | 0.23 s     |
| 4        | 10.51     | -1.07      | 1.6×          | 0.91 s     |
| 8        | 10.49     | -1.08      | 1.3×          | 11.5 s     |

Compression is only 1.3–1.9× and the PSNR delta saturates at −1.07 dB for `b ≥ 2`: the bottleneck is the grouping-induced locality assumption, not quantization precision. The paper argues that for `df ≥ 16` representations (TensoRF `df = 48`, K-Planes `df = 64`) the method would run without grouping and reach 3–7×, but this is a projection, not a measured result.

### Comparison With Existing 3DGS Compression Methods

원논문 Table 5. Ratios relative to vanilla 3DGS. 이 방법은 압축비에서 학습 기반 기법에 크게 뒤진다(3.5× vs 20–185×) — 대신 학습·codebook·calibration이 전혀 없다. *HAC++ reports quality improvement over the vanilla baseline.

| Method               | Venue      | Compress | PSNR Loss  | Training | Time    |
| -------------------- | ---------- | -------- | ---------- | -------- | ------- |
| _Training-required_  |            |          |            |          |         |
| LightGaussian        | NeurIPS'24 | 15×      | 0.2–0.5 dB | Yes      | Hours   |
| ContextGS            | NeurIPS'24 | 20×      | 0.1–0.3 dB | Yes      | Hours   |
| C3DGS                | CVPR'24    | 31×      | 0.1–0.5 dB | Yes      | Hours   |
| SOGS                 | ECCV'24    | 17–42×   | 0.1–0.5 dB | Yes      | Hours   |
| FCGS                 | ICLR'25    | >20×     | ~0.1 dB    | Yes      | Seconds |
| CodecGS              | ICCV'25    | 76×      | ~0.2 dB    | Yes      | Hours   |
| HAC++                | TPAMI'25   | >100×    | ≤0 dB*     | Yes      | Hours   |
| OMG                  | NeurIPS'25 | 185×     | ~0.1 dB    | Yes      | Hours   |
| _Training-free_      |            |          |            |          |         |
| FlexGaussian         | ACM MM'25  | 19×      | <1 dB      | No       | Seconds |
| 3DTurboQuant b = 3   | –          | 3.5×     | 0.02 dB    | No       | 9s      |
| 3DTurboQuant + prune | –          | 5–8×     | 0.2–3 dB   | No       | 9s      |

Against the only other training-free method, FlexGaussian, 3DTurboQuant `b = 3` achieves much lower PSNR loss (0.02 dB vs. <1 dB) but at a lower ratio (3.5× vs. 19×), reflecting its absence of pruning; adding pruning reaches 5–8×.

## 💡 Insights & Impact

- **Dimension governs quantizability**: The clean rule `b > log₄ d` (equivalently `d·4⁻ᵇ ≪ 1`) predicts effectiveness. At `d = 1024` (DUSt3R), 3-bit gives 29.3 dB and 4-bit 39.7 dB; at `d = 45` (3DGS), 3-bit costs only −0.02 dB; at `d = 2` (Instant-NGP), even 8-bit still loses −1.08 dB. This is driven by the Beta variance `1/d`.
- **Where it wins**: high-dimensional parameter blocks (SH `d = 45`, KV `d = 1024`) with no per-scene training — compression in seconds, reportedly 1000×–10000× faster than the hours of fine-tuning learned methods need.
- **Where it loses**: (1) NeRF hash grids (`df = 2`) compress only 1.3–1.9× and saturate at −1.07 dB; (2) absolute 3DGS compression ratio (3.5×, or 5–8× with pruning) trails learned pipelines (20–185×) because the method provides only the quantization stage, not pruning/entropy coding; (3) DUSt3R KV quantization below `b = 3` collapses to 16.5 dB.
- **Stated limitations**: compresses storage, not rendering computation (inference speed unchanged); entry-grouping assumes spatial locality that may not hold for all hash layouts; the current implementation is CPU-side (a fused GPU kernel is future work, projected 10–100× faster); the DUSt3R KV overhead at `b = 4` is +1.53 s over a 0.14 s baseline.
- **Positioning**: proposes itself as a drop-in replacement for the learned-VQ stage inside existing pipelines (HAC++, CodecGS), matching or exceeding learned per-coordinate distortion (0.02 dB vs. 0.1–0.5 dB) while removing codebook training.

## 🔗 Related Work

- **[DUSt3R](dust3r.md)**: the transformer 3D reconstructor whose ViT-Large KV cache (dkv = 1024, 24 encoder / 48 total attention layers) 3DTurboQuant quantizes to 7.9× at 39.7 dB pointmap fidelity — the direct 3D-vision target of this paper.
- **[QuantVGGT](../reconstruction/quantvggt.md)**: closest peer for 3D-vision transformer quantization — W4A4 post-training quantization of the 1.2B VGGT with Hadamard rotation smoothing. Cited here as prior art; 3DTurboQuant differs by being fully data-oblivious with provable near-optimal MSE bounds.
- **[VGGT](../reconstruction/vggt.md)**: the VGGT foundation model that QuantVGGT and streaming-KV methods target; useful context for the KV-cache-compression thread this paper joins for DUSt3R.

The underlying quantizer is TurboQuant (Zandieh et al. 2025a); other cited KV-cache methods (KIVI, KVQuant, QJL, PolarQuant) and 3DGS/NeRF compressors (HAC++, CodecGS, CNC, SHACIRA) are calibration- or training-dependent and are not part of this collection.

## 📚 Key Takeaways

1. **A random rotation removes the need for learned codebooks**: for `d ∈ [16, 1024]`, rotated coordinates follow a known Beta distribution, so a precomputed Lloyd-Max quantizer is near-optimal (within 2.7× of the information-theoretic bound) with zero calibration data.
2. **One algorithm, three model families**: the same pipeline compresses 3DGS SH (`d = 45`, 3.5× at −0.02 dB), DUSt3R KV caches (`d = 1024`, 7.9× at 39.7 dB), and NeRF hash grids (`d = 2` grouped to 32, 1.3–1.9×) — only `d` changes.
3. **Dimension is the design variable**: `b > log₄ d` predicts feasibility a priori; low-`d` parameters (positions, quaternions, raw hash entries) must stay in float32.
4. **Honest trade-off**: near-optimal per-coordinate distortion and second-scale, training-free compression, but lower absolute ratios than learned pipelines and no rendering-speed gain — best used as the quantization stage inside larger compression systems.

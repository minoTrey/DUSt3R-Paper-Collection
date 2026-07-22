# QVGGT: Post-Training Quantized Visual Geometry Grounded Transformer (CVPR 2026)

![qvggt — architecture](https://arxiv.org/html/2605.31124v1/x2.png)

_Overview of QVGGT (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Zhizhen Pan, Hesong Wang, Huan Wang
- **Institution**: Westlake University; Beijing University of Posts and Telecommunications
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2605.31124) | [Project Page](https://ddsacu.github.io/QVGGT/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A three-stage post-training quantization (PTQ) framework that compresses the 1.26B-parameter VGGT to W4A16 via selective mixed-precision allocation, token filtering with PCA-based camera information compensation, and task-aware scale search — achieving near-lossless 3D geometry prediction with 3∼4.9× memory reduction.

## 🎯 Key Contributions

1. **Selective mixed-precision quantization**: A per-block sensitivity analysis reveals heterogeneous quantization sensitivity across VGGT's Alternating-Attention blocks; the most fragile blocks are kept at higher precision while the rest are quantized to 4 bits.
2. **Token filtering with Camera Information Compensation (CIC)**: High-variance camera and register tokens are excluded from activation calibration statistics, and their geometric cues are restored at inference via a PCA-derived global compensation token.
3. **Task-aware scale search**: Quantization scales are selected using multi-head prediction losses plus a cross-head geometric consistency objective (camera/depth/point), rather than layer reconstruction error alone.
4. **Near-lossless W4A16**: Preserves all 3D prediction heads while reducing model size by more than 75% and inference memory by 3∼4.9×.

## 🔧 Technical Details

### Motivation from sensitivity analysis

- The camera head shows the strongest and most volatile dependence on block precision; quantizing certain blocks introduces disproportionately large camera-pose errors while depth/point heads stay comparatively stable.
- Based on this, the 14th, 17th, and 23rd frame blocks and the 23rd global block are treated as sensitive — only their attention projection layer is quantized while the remaining weights stay at FP16; other blocks are quantized to INT4.
- Camera and register tokens (the sole inputs to the camera head) exhibit outlier activation magnitudes that dominate scale estimation, inflating dynamic range and amplifying quantization error.

### Camera Information Compensation

During calibration, activation statistics and scale search use image tokens only. A CIC token is synthesized from the calibration camera-token matrix via top-K PCA (K = 32 principal components), normalized to match patch-token norms, and appended to the token sequence at inference before the camera head.

### Task-aware objective

`L_task(s) = L_recon + L_camera + α·L_depth + β·L_point + L_geo`. The geometry-consistency loss `L_geom` penalizes disagreement between the point head's direct output and the point map reconstructed by unprojecting predicted depth with camera intrinsics/extrinsics. Following AWQ, a lightweight grid search over candidate scales replaces the reconstruction-only objective. (Main text sets α = β = 1; the supplementary implementation uses α = β = 0.1 for the depth/point head weights.)

### Setup

- Base model VGGT-1B; W4A16 with per-group weight quantization (group size = 128); 128 calibration images randomly sampled from CO3Dv2 and ScanNet.
- All experiments on a single RTX 4090 (24 GB) with PyTorch; PTQ is training-free, calibration takes ~2 hours.

## 📊 Results

### Camera pose estimation (10 random frames)

원논문 Table 1. AUC@30은 높을수록, Latency는 낮을수록 좋음. QuantVGGT는 CO3Dv2 latency 미보고("-"). GPTQ·AWQ는 W4A16에서 큰 성능 저하.

| Method       | W/A   | CO3Dv2 AUC@30 ↑ | CO3Dv2 Latency ↓ | Re10K AUC@30 ↑ | Re10K Latency ↓ |
| ------------ | ----- | --------------- | ---------------- | -------------- | --------------- |
| Baseline     | FP16  | 89.5            | 0.38s            | 85.3           | 0.37s           |
| SmoothQuant  | W8A8  | 87.9            | 0.62s            | 81.3           | 0.38s           |
| QuantVGGT    | W8A8  | 89.4            | -                | 84.9           | -               |
| QuantVGGT    | W4A16 | 89.2            | -                | 84.4           | -               |
| GPTQ         | W4A16 | 76.9            | 0.28s            | 75.6           | 0.27s           |
| AWQ          | W4A16 | 54.6            | 0.28s            | 59.2           | 0.28s           |
| QVGGT (ours) | W4A16 | 89.4            | **0.23s**        | 85.0           | **0.23s**       |

### 3D reconstruction on 7-Scenes

원논문 Table 2. Acc·Comp는 낮을수록, NC는 높을수록 좋음.

| Method       | W/A   | Acc Mean ↓ | Acc Med. ↓ | Comp Mean ↓ | Comp Med. ↓ | NC Mean ↑ | NC Med. ↑ |
| ------------ | ----- | ---------- | ---------- | ----------- | ----------- | --------- | --------- |
| Baseline     | FP16  | 0.030      | 0.019      | 0.034       | 0.039       | 0.847     | 0.928     |
| SmoothQuant  | W8A8  | 0.067      | 0.060      | 0.058       | 0.042       | 0.702     | 0.760     |
| GPTQ         | W4A16 | 0.051      | 0.033      | 0.053       | 0.025       | 0.802     | 0.880     |
| AWQ          | W4A16 | 0.043      | 0.023      | 0.054       | 0.024       | 0.819     | 0.914     |
| QVGGT (ours) | W4A16 | 0.031      | 0.019      | 0.035       | 0.021       | 0.849     | 0.927     |

### 3D reconstruction on NRGBD

원논문 Table 2.

| Method       | W/A   | Acc Mean ↓ | Acc Med. ↓ | Comp Mean ↓ | Comp Med. ↓ | NC Mean ↑ | NC Med. ↑ |
| ------------ | ----- | ---------- | ---------- | ----------- | ----------- | --------- | --------- |
| Baseline     | FP16  | 0.024      | 0.013      | 0.038       | 0.013       | 0.922     | 0.994     |
| SmoothQuant  | W8A8  | 0.062      | 0.052      | 0.066       | 0.054       | 0.769     | 0.778     |
| GPTQ         | W4A16 | 0.053      | 0.029      | 0.051       | 0.022       | 0.872     | 0.945     |
| AWQ          | W4A16 | 0.047      | 0.023      | 0.059       | 0.024       | 0.891     | 0.982     |
| QVGGT (ours) | W4A16 | 0.029      | 0.015      | 0.037       | 0.015       | 0.925     | 0.994     |

### Ablation: framework components

원논문 Table 3. Q: naive all-block quantization; S: selective mixed-precision; D: token filtering + CIC; T: task-aware scale search.

| Configuration | CO3Dv2 AUC@30 ↑ | NRGBD Acc Mean ↓ |
| ------------- | --------------- | ---------------- |
| Q             | 54.57           | 0.122            |
| S             | 80.76           | 0.057            |
| S + D         | 85.91           | 0.054            |
| S + D + T     | **89.39**       | **0.029**        |

### Efficiency

원논문 Table 5, 2 input frames, FP16 baseline로 정규화.

| Method       | W/A   | Memory ↑ | Latency ↓ |
| ------------ | ----- | -------- | --------- |
| Baseline     | FP16  | 1.00×    | 1.00×     |
| QuantVGGT    | W8A8  | 1.93×    | 2.17×     |
| QVGGT (ours) | W4A16 | 2.11×    | 1.93×     |

Peak-memory reduction over full-precision VGGT reaches 4.9× at one input frame and remains 3.7× at 30 input frames (본문 서술). The abstract further reports 3∼4.9× memory reduction and up to 2.8× real hardware speedup over FP32.

## 💡 Insights & Impact

- **Camera pose is the quantization stress test**: Because the camera head is the most fragile, protecting a handful of sensitive blocks (only their attention projection) recovers most of the accuracy lost to naive quantization — AUC@30 on CO3Dv2 jumps from 54.57 (naive) to 80.76 (selective).
- **Outlier tokens carry signal, not just noise**: Excluding camera/register tokens from calibration stabilizes scales but drops camera information; CIC recovers it — without CIC the model attains 84.51 AUC@30 on CO3Dv2, with CIC 89.39 (원논문 Table A2).
- **Generic LLM/ViT PTQ transfers poorly**: GPTQ and AWQ collapse under W4A16 (76.9 / 54.6 AUC@30 on CO3Dv2), underscoring that 3D geometry transformers need geometry-aware quantization.
- **Deployment**: The whole pipeline runs on a consumer RTX 4090 with ~2h calibration and no training, targeting UAV and mobile AR use.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The 1.26B-parameter model QVGGT compresses.
- **[QuantVGGT](../reconstruction/quantvggt.md)**: Concurrent PTQ-for-VGGT work; QVGGT is positioned as complementary (geometry/task-aware vs. distribution-oriented) and reports comparable or better accuracy at matched bit-widths.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Feed-forward regression predecessors VGGT unifies.

## 📚 Key Takeaways

1. **Heterogeneous block sensitivity is the key obstacle** to quantizing VGGT; selective mixed precision on a few sensitive blocks is essential.
2. **Camera/register token outliers must be filtered but compensated** — CIC resolves the trade-off between stable calibration and preserved pose cues.
3. **Task-aware, geometry-consistent scale search** aligns quantization with 3D prediction quality, yielding near-lossless W4A16 with >75% size reduction and 3∼4.9× less memory.

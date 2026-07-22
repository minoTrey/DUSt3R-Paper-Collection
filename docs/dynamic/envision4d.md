# Envision4D: Envisioning Visual Futures via Feed-forward 4D Gaussian Splatting for Autonomous Driving (arXiv preprint (2026-06))

![envision4d — architecture](https://arxiv.org/html/2606.10656v1/x2.png)

_Framework of Envision4D (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Qi Song, Yifei He, Chi Zhang, Zheng Fu, Xuhe Zhao, Mengmeng Yang, Kun Jiang, Rui Huang, Diange Yang
- **Institution**: Tsinghua University; The Chinese University of Hong Kong, Shenzhen
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.10656) | [Project Page](https://maggiesong7.github.io/research/Envision4D/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A fully self-supervised, future pose-free feed-forward 4D Gaussian Splatting framework for autonomous driving that jointly infers future camera poses (via iterative denoising) and time-conditioned non-linear motion, enabling robust future scene extrapolation without explicit motion guidance.

## 🎯 Key Contributions

1. **Self-supervised future pose-free 4DGS**: Dynamic scene extrapolation on continuous images without explicit motion guidance (optical flow, trackers, or dynamic masks) or predefined future cameras.
2. **Joint Pose-Motion Prediction**: A Future Pose Prediction module infers future cameras via iterative denoising, plus Conditioned Motion Lifting for time-conditioned non-linear velocities.
3. **In-layer Temporal Attention**: Temporal attention embedded inside the intermediate stages of a frozen VGGT encoder (vs. post-layer refinement) to propagate motion cues through deep priors.
4. **Progressive Training Strategy**: Geometric warm-up, self-exclusive motion rendering, and progressive extrapolation weighting to stabilize unsupervised motion learning against error accumulation.

## 🔧 Technical Details

### Backbone and Motion Representation

- Built on a **frozen VGGT** backbone (DINOv2 tokenization + 24 Alternating-Attention layers).
- **In-layer Temporal Attention** inserted at layers {4, 11, 17, 23}: `F_{l+1} = AA_{l+1}(TAttn(F_l))`, concatenating global and temporal tokens into motion tokens.
- **Time-conditioned motion warping**: `μ_{i→j} = μ_i + v_{i,j}·(j−i)`, replacing constant linear motion, for source-frame `i` to target-frame `j`.

### Future Pose Prediction

- Initializes `T_f` unknown future camera tokens by adding a learnable offset `δ` to the last observed camera token, then iteratively refines via shared self-attention blocks conditioned on 1D sinusoidal time embeddings, decoded by a frozen camera head. The self-attention block runs recurrently for 4 refinement passes (2 layers, 16 heads).

### Conditioned Motion Lifting

- Correlates each context token with `K = T_c + T_f − 1` alternative timestamps; future motion feature `m_{i,j,n} = E_j ⊙ f_{i,n}`, decoded by a DPT head into velocities.

### Training

- Losses: RGB rendering (`L_rgb = L_MSE + λ_lpips L_LPIPS`) plus self-distillation to frozen VGGT (`L_cam = ‖P − P_vggt‖₁`, `L_depth = ‖D − D_vggt‖₁`).
- Resolution 350×518, single A100, batch 2, 100K iterations, `T_c = T_f = 2` default; Adam + cosine schedule, LR 1×10⁻⁴, `λ_LPIPS = 0.05`, `λ_cam = 5.0`.

## 📊 Results

### Waymo — Render Quality, Speed, Capability (원논문 Table 1)

원논문 Table 1. Inference speed는 단일 A100 기준. ∗는 저자 재현. 원본 DGGT는 SSIM·D-RMSE에서 Ours보다 낫다(하지만 pose-free/unsup-dynamic이 아님).

| Method       | PSNR ↑    | SSIM ↑    | D-RMSE ↓ | Time ↓  | Pose-free | Unsup. Dynamic |
| ------------ | --------- | --------- | -------- | ------- | --------- | -------------- |
| PVG          | 22.38     | 0.661     | 13.01    | 27 min  | ×         | ✓              |
| DeformableGS | 25.29     | 0.761     | 14.79    | 29 min  | ×         | ✓              |
| DepthSplat   | 23.26     | 0.696     | 10.05    | 0.11 s  | ×         | ×              |
| NoPoSplat    | 24.31     | 0.751     | 9.08     | 23.22 s | ✓         | ×              |
| STORM        | 26.38     | 0.794     | 5.48     | 0.18 s  | ×         | ✓              |
| DGGT         | 27.41     | **0.846** | **3.47** | 0.39 s  | ✓         | ×              |
| STORM∗       | 26.19     | 0.798     | 6.13     | 0.12 s  | ×         | ✓              |
| DGGT∗        | 24.38     | 0.756     | 7.67     | 0.56 s  | ✓         | ×              |
| **Ours**     | **27.81** | 0.816     | 3.98     | 0.37 s  | ✓         | ✓              |

### nuScenes (원논문 Table 2)

원논문 Table 2. 결과는 원논문 수치 인용. DGGT는 LPIPS에서 Ours보다 낮다(더 좋음).

| Method   | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------- | --------- | --------- | --------- |
| STORM    | 24.54     | 0.784     | 0.267     |
| DGGT     | 26.63     | 0.813     | **0.122** |
| **Ours** | **26.86** | **0.815** | 0.164     |

### Camera Pose (원논문 Table 3)

원논문 Table 3. Waymo·nuScenes AUC@30↑. VGGT는 모든 target image를 입력받지만 Ours는 2프레임만으로 현재·미래 포즈를 예측.

| Method   | Future camera | Waymo AUC@30 ↑ | nuScenes AUC@30 ↑ |
| -------- | ------------- | -------------- | ----------------- |
| VGGT     | ×             | 78.58          | 76.99             |
| **Ours** | ✓             | **79.49**      | **78.03**         |

### Varying Context/Future Frames (원논문 Table 4)

원논문 Table 4. Ours at Tf=6가 STORM at Tf=2와 경쟁력 있음.

| Tc  | Tf  | STORM PSNR ↑ | Ours PSNR ↑ | STORM SSIM ↑ | Ours SSIM ↑ | STORM LPIPS ↓ | Ours LPIPS ↓ |
| --- | --- | ------------ | ----------- | ------------ | ----------- | ------------- | ------------ |
| 2   | 2   | 26.19        | **27.81**   | 0.798        | **0.816**   | 0.242         | **0.159**    |
| 2   | 4   | 25.55        | **26.87**   | 0.773        | **0.790**   | 0.263         | **0.170**    |
| 2   | 6   | 24.41        | **26.21**   | 0.753        | **0.771**   | 0.346         | **0.192**    |
| 3   | 6   | 24.62        | **26.46**   | 0.752        | **0.782**   | 0.302         | **0.187**    |

### Ablation (원논문 Table 5)

원논문 Table 5. Waymo. FP=Future Pose, CML=Conditioned Motion Lifting, Prog.=Progressive Training.

| FP  | CML | In-layer TAttn | Post-layer TAttn | Prog. | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| --- | --- | -------------- | ---------------- | ----- | --------- | --------- | --------- |
| ✓   | –   | –              | –                | ✓     | 25.41     | 0.796     | 0.198     |
| ✓   | ✓   | –              | –                | ✓     | 27.29     | 0.812     | 0.167     |
| ✓   | ✓   | –              | ✓                | ✓     | 28.01     | 0.824     | 0.158     |
| ✓   | ✓   | ✓              | –                | –     | 27.89     | 0.829     | 0.160     |
| ✓   | ✓   | ✓              | –                | ✓     | **28.83** | **0.849** | **0.145** |

## 💡 Insights & Impact

- Interpolation-centric feed-forward models suffer ghosting under large displacements; jointly predicting future poses and non-linear motion overcomes strict future priors.
- In-layer temporal attention beats post-layer refinement, showing deep integration of motion cues within frozen encoders helps.
- The model's Tf=6 long-horizon prediction surpasses STORM's Tf=2 short-term output in PSNR/LPIPS, evidencing robustness to error accumulation.

## 🔗 Related Work

- Backbone [VGGT](../reconstruction/vggt.md); compared/related to driving 4D methods [DGGT](dggt.md), [DynamicVGGT](dynamicvggt.md), and [V-DPM](v-dpm.md); STORM as primary re-implemented baseline.

## 📚 Key Takeaways

1. Future pose-free, self-supervised 4DGS enabling true predictive extrapolation for driving scenes.
2. State-of-the-art render quality under the challenging extrapolation setting, with honest reporting that the original DGGT retains higher SSIM/lower D-RMSE (Waymo) and lower LPIPS (nuScenes).
3. Joint pose-motion prediction plus a progressive training strategy stabilize unsupervised motion learning over long horizons.

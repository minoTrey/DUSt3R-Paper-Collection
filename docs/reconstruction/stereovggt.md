# StereoVGGT: A Training-Free Visual Geometry Transformer for Stereo Vision (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Ziyang Chen, Yansong Qu, You Shen, Xuan Cheng, Liujuan Cao
- **Institution**: Key Laboratory of Multimedia Trusted Perception and Efficient Computing, Ministry of Education of China, Xiamen University
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.29368)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free feature backbone for stereo vision that harnesses the frozen VGGT's latent camera-pose knowledge while mitigating its structural feature degradation via entropy-minimized weight merging and a Frame-Attention neck; the resulting stereo matching network ranks 1st among published methods on the KITTI non-occluded benchmark.

## 🎯 Key Contributions

1. **Camera-pose knowledge for stereo**: The paper argues that existing stereo backbones (VFMs, MDE models) lack camera-pose priors — a bottleneck, since focal length is decisive for the depth-to-disparity relation d = f·B/z — and incorporates a frozen VGGT that is explicitly trained on such geometric data.
2. **Entropy-Minimized Weight Merging (EMWM)**: A training-free, data-free strategy that merges VGGT, MoGe-2, and DINOv2 weights within their shared DINO architecture by minimizing weight-information entropy, deriving optimal per-layer merge coefficients.
3. **Feature neck design**: A dual-branch neck where VGGT Frame-Attention features (camera geometry) modulate MDE-neck features (fine spatial detail) via feature-wise subtraction (α = 0.2), balancing camera priors with structural integrity.

## 🔧 Technical Details

### Motivation

Applying VGGT directly to stereo vision underperforms: VGGT excessively degrades structural contours during feature extraction (lower SSIM between feature maps and inputs than DINOv2 or DAv2), a smoothing property that conflicts with stereo's need for pixel-accurate local structure. Yet a Levenberg–Marquardt FOV solver on features shows VGGT encodes camera knowledge far more precisely than DINOv2 or DAv2.

### EMWM

Following task arithmetic, θ_stereovggt = θ + λ_vggt·τ_vggt + λ_mde·τ_mde (τ = weight shifts from DINOv2). Per-layer coefficients are optimized by minimizing the entropy of a softmax-temperature distribution over merged weights (γ = 0.95), iteratively projected onto the simplex λ_vggt + λ_mde = 1, with convergence ε = 10⁻⁶ (max 20,000 iterations).

### Downstream Coupling

For stereo matching, StereoVGGT is kept frozen and only the disparity decoder is trained, plugged into IGEV-Stereo (replacing MobileNetV2). For stereo conversion, it replaces DAv2 in Mono2Stereo with a frozen Marigold VAE inpainting model, making the whole pipeline training-free. A hyperparameter α = 0.2 modulates the VGGT-neck contribution.

## 📊 Results

Stereo matching on KITTI and Scene Flow; stereo conversion on Mono2Stereo and Inria 3D Movie; monocular-setting disparity ablation on KITTI/ETH3D/Middlebury.

### KITTI Benchmark — Stereo Matching (3-pixel error)

원논문 Table 1. Percentage of outliers, lower is better.

| Feature Backbone | Method         | Non-occ all | fg   | bg   | All all  | fg   | bg   |
| ---------------- | -------------- | ----------- | ---- | ---- | -------- | ---- | ---- |
| MobileNet V2     | IGEV-Stereo    | 1.49        | 2.62 | 1.27 | 1.59     | 2.67 | 1.38 |
| DAv2             | MonSter        | 1.33        | 2.76 | 1.05 | 1.41     | 2.81 | 1.13 |
| DAv2             | PromptStereo   | 1.32        | 2.76 | 1.04 | 1.41     | 2.85 | 1.12 |
| VGGT             | (IGEV decoder) | 1.58        | 2.87 | 1.33 | 1.67     | 2.81 | 1.44 |
| **StereoVGGT**   | (IGEV decoder) | **1.31**    | 2.31 | 1.12 | **1.42** | 2.38 | 1.22 |

Under the same IGEV-Stereo decoder, StereoVGGT beats VGGT and MDE/VFM backbones, ranking 1st among all published methods on the KITTI non-occluded benchmark. On Scene Flow (원논문 Fig. 6, values printed in text), StereoVGGT reaches 1px = 4.9 and EPE = 0.43, best among backbone variants (VGGT 5.3/0.46, DAv2 5.1/0.44, MoGe-2 5.1/0.45).

### Stereo Conversion — Inria 3D Movie

원논문 Table 2. RMSE lower is better; SSIM/SIoU/PSNR higher is better.

| Disparity Stage | Method          | RMSE↓     | SSIM↑      | SIoU↑      | PSNR↑     |
| --------------- | --------------- | --------- | ---------- | ---------- | --------- |
| DPT-based       | StereoDiffusion | 9.345     | 0.2703     | 0.1941     | 28.75     |
| DepthCrafter    | StereoCrafter   | 7.392     | 0.5866     | 0.2656     | 29.71     |
| DAv2            | Mono2Stereo     | 6.857     | 0.7227     | 0.2859     | 31.53     |
| VGGT            | –               | 6.734     | 0.7082     | 0.2801     | 31.57     |
| Moge-2          | –               | 6.891     | 0.7247     | 0.2753     | 30.88     |
| **StereoVGGT**  | –               | **6.462** | **0.7343** | **0.2952** | **32.03** |

### Cross-Dataset Disparity (Monocular Setting)

원논문 Table 4. EPE, lower is better; using only left view + camera intrinsics.

| Type | Method         | KITTI EPE↓ | ETH3D EPE↓ | Middlebury EPE↓ |
| ---- | -------------- | ---------- | ---------- | --------------- |
| MDE  | Moge-2         | 6.74       | 4.84       | 18.11           |
| MDE  | DAv2           | 5.88       | 8.24       | 24.94           |
| 3R   | VGGT           | 13.07      | 13.11      | 18.71           |
| 3R   | fastVGGT       | 13.07      | 13.11      | 18.70           |
| —    | **StereoVGGT** | **2.71**   | **2.38**   | **15.14**       |

### Weight-Merging Ablation

원논문 Table 5 (ETH3D). Lower FOV error / EPE is better; higher SSIM is better.

| No. | DINO Weights | FOV x med.↓ | FOV y med.↓ | SSIM↑ | EPE↓     |
| --- | ------------ | ----------- | ----------- | ----- | -------- |
| 1   | DINOv2       | 80.3        | 65.8        | 0.965 | 20.6     |
| 2   | DAv2         | 73.7        | 60.0        | 0.965 | 7.38     |
| 3   | Moge-2       | 30.4        | 15.8        | 0.965 | 3.68     |
| 4   | VGGT         | 14.7        | 7.08        | 0.776 | 12.1     |
| 5   | Ours (EMWM)  | **3.88**    | **2.68**    | 0.964 | **2.38** |

VGGT alone gives the best raw camera-pose features (lowest FOV error before merging) but its low SSIM (0.776, severe degradation) yields poor disparity (EPE 12.1); EMWM preserves structural integrity (SSIM 0.964) while incorporating camera awareness, giving the best EPE.

## 💡 Insights & Impact

- **Complementary strengths**: VGGT encodes camera-geometry priors but degrades feature structure; MDE models/VFMs preserve structure but lack calibration awareness. StereoVGGT algebraically superposes both via weight merging.
- **Training-free versatility**: EMWM and the frozen neck make the backbone plug-in for stereo matching and conversion without retraining, achieving SOTA on multiple benchmarks.
- **Feature degradation as a measurable bottleneck**: Using SSIM between feature maps and inputs as a degradation proxy quantifies why raw VGGT features underperform for pixel-accurate stereo.
- **Limitations**: A substantial parameter footprint inherited from the 3D foundation architecture; model compression/distillation is future work.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The frozen geometry foundation supplying camera-pose knowledge.
- **[MoGe-2](moge-2.md)**: The MDE model whose weights are merged and which serves as a backbone baseline.
- **[fastVGGT](fastvggt.md)**: A VGGT-accelerating variant compared in the cross-dataset disparity table.
- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: The feed-forward geometry lineage referenced for VGGT's origins.

## 📚 Key Takeaways

1. StereoVGGT is a training-free stereo backbone that injects VGGT's camera-pose priors while repairing its structural feature degradation.
2. Entropy-Minimized Weight Merging fuses VGGT, MoGe-2, and DINOv2 weights per-layer with no data or training; a Frame-Attention neck balances geometry and detail.
3. It ranks 1st on KITTI non-occluded stereo matching and achieves SOTA stereo conversion on Inria 3D Movie and Mono2Stereo.
4. The main cost is a large parameter footprint, targeted for compression in future work.

# GARD: Geometry-Aware Representation Denoising for Robust Multi-view 3D Reconstruction (arXiv preprint (2026-05))

![gard — architecture](https://arxiv.org/html/2605.26230v1/x1.png)

_Geometry-Aware Representation Denoising (GARD) framework (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Jin Hyeon Kim, Jaeeun Lee, Claire Kim, Kyoungjin Oh, Paul Hyunbin Cho, Jaewon Min, Yeji Choi, Jihye Park, Hyunhee Park, Minkyu Park, Seungryong Kim
- **Institution**: KAIST AI; Samsung Electronics
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.26230) | [Code](https://github.com/cvlab-kaist/GARD)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A framework that performs diffusion-based multi-view restoration directly in the geometry-aware feature space of a frozen feed-forward reconstructor (Depth Anything 3), jointly recovering accurate 3D geometry and high-quality RGB images from degraded (motion-blurred) multi-view inputs via an auxiliary image decoder.

## 🎯 Key Contributions

1. **Restoration in geometry-aware feature space**: Instead of pixel-space or VAE-latent restoration, GARD denoises the intermediate multi-view features of a feed-forward reconstructor, preserving cross-view consistency and fine geometric detail.
2. **Multi-view diffusion denoiser**: A DiTDH-based denoiser (from RAE) with interleaved frame-level and global attention aggregates cross-view context to restore degraded features.
3. **Interpolated flow matching + attention alignment**: Uses the degraded latent (plus noise) as the source distribution and aligns the denoiser's attention maps with geometrically consistent correspondence maps.
4. **Joint geometry + image recovery**: A dedicated RGB decoder reconstructs high-quality images from the refined features alongside geometry, in a single forward pass without retraining the backbone.

## 🔧 Technical Details

### Framework

- Backbone: Depth Anything 3 (DA3-GIANT-1.1), multi-view encoder with L = 40 layers, hidden dim C = 1536. The GARD denoiser Sθ is inserted at layer K = 18; restored features propagate through remaining layers; feature levels M = {20, 28, 34, 40} feed the geometry decoder and the RGB decoder.
- The RGB decoder is adapted from a geometric-foundation-model repurposing work and fine-tuned; the backbone stays frozen.

### Training Objectives

- **Interpolated flow matching**: source is the noise-perturbed degraded latent z̃K = zK_deg + αε (α = 0.3), not pure Gaussian noise, retaining structural priors; velocity field target v* = zK_clean − z̃K_deg.
- **Attention alignment loss**: cross-entropy between the denoiser's global attention map (layer J = 9) and target correspondence maps from clean-input point clouds; total loss L = Lflow + λattn·Lattn (λattn = 1.0).
- Denoiser: DiTDH with encoder/decoder depths 8/6 and added global attention layers. V = 10 multi-view images for all evaluations. Evaluated under severe motion-blur degradation on the DA3 benchmark (HiRoom, ETH3D, DTU, 7Scenes, ScanNet++).

## 📊 Results

### Camera Pose Estimation (AUC↑) under Motion Blur

원논문 Table 1. HQ/LQ Input은 degradation 상·하한 참조.

| Model       | HiRoom A5 | HiRoom A30 | ETH3D A5 | ETH3D A30 | DTU A5 | DTU A30 | 7Sc A5 | 7Sc A30 | SN++ A5 | SN++ A30 |
| ----------- | --------- | ---------- | -------- | --------- | ------ | ------- | ------ | ------- | ------- | -------- |
| HQ Input    | 87.20     | 96.65      | 53.45    | 84.68     | 92.44  | 98.70   | 42.47  | 86.91   | 82.66   | 92.95    |
| LQ Input    | 4.10      | 32.90      | 16.72    | 61.38     | 20.83  | 66.43   | 7.55   | 51.39   | 34.55   | 71.02    |
| Restormer   | 3.69      | 26.68      | 16.51    | 57.68     | 21.08  | 67.80   | 24.94  | 75.12   | 39.20   | 76.12    |
| InstructIR  | 3.89      | 27.68      | 14.71    | 53.80     | 54.80  | 85.91   | 18.42  | 74.22   | 32.84   | 68.23    |
| MoCE-IR     | 2.88      | 28.60      | 21.73    | 63.25     | 45.85  | 84.61   | 16.38  | 65.20   | 38.64   | 72.99    |
| VRT         | 3.67      | 30.17      | 14.90    | 58.98     | 19.83  | 67.01   | 11.11  | 48.02   | 36.55   | 72.67    |
| VAEMVD      | 2.84      | 28.70      | 7.88     | 35.20     | 8.18   | 60.50   | 13.90  | 76.50   | 31.20   | 75.00    |
| GARD (Ours) | 12.00     | 67.22      | 35.75    | 74.68     | 62.24  | 92.37   | 35.55  | 84.73   | 56.44   | 87.45    |

### 3D Reconstruction (Overall↓ / F-score↑) under Motion Blur

원논문 Table 2. DTU는 Overall만 보고.

| Model       | HiRoom Ov ↓ | HiRoom F ↑ | ETH3D Ov ↓ | ETH3D F ↑ | DTU Ov ↓ | 7Sc Ov ↓ | 7Sc F ↑ | SN++ Ov ↓ | SN++ F ↑ |
| ----------- | ----------- | ---------- | ---------- | --------- | -------- | -------- | ------- | --------- | -------- |
| HQ Input    | 0.069       | 84.05      | 0.812      | 60.81     | 2.475    | 0.159    | 45.15   | 0.265     | 50.25    |
| LQ Input    | 1.634       | 11.74      | 1.564      | 37.50     | 6.611    | 0.363    | 18.40   | 0.335     | 24.13    |
| Restormer   | 0.842       | 11.21      | 2.116      | 33.97     | 7.272    | 0.388    | 27.92   | 0.326     | 30.45    |
| InstructIR  | 0.992       | 12.41      | 2.263      | 33.71     | 5.563    | 0.311    | 29.80   | 0.366     | 26.06    |
| VRT         | 1.289       | 9.45       | 1.493      | 35.14     | 7.570    | 0.538    | 19.53   | 0.319     | 26.72    |
| VAEMVD      | 0.750       | 11.26      | 2.046      | 25.64     | 7.745    | 0.259    | 28.16   | 0.343     | 28.38    |
| GARD (Ours) | 0.293       | 18.25      | 1.136      | 45.79     | 4.760    | 0.190    | 36.08   | 0.277     | 35.77    |

Note: GARD does not fully recover HQ-input quality (e.g., 7Scenes Overall 0.190 vs HQ 0.159), but leads all restoration baselines across datasets.

### Image Restoration (PSNR↑ / LPIPS↓)

원논문 Table 3에서 발췌 (대표 baseline + GARD).

| Model       | ETH3D PSNR | ETH3D LPIPS | DTU PSNR | DTU LPIPS | 7Sc PSNR | 7Sc LPIPS | SN++ PSNR | SN++ LPIPS |
| ----------- | ---------- | ----------- | -------- | --------- | -------- | --------- | --------- | ---------- |
| Restormer   | 20.97      | 0.672       | 17.73    | 0.588     | 21.30    | 0.428     | 21.50     | 0.415      |
| VAEMVD      | 21.37      | 0.638       | 20.54    | 0.434     | 21.74    | 0.404     | 21.19     | 0.379      |
| GARD (Ours) | 21.88      | 0.635       | 21.25    | 0.418     | 22.67    | 0.249     | 22.19     | 0.345      |

### Ablation on Training Components

원논문 Table 4. Interp. Flow = interpolated flow matching, Alignment = attention alignment. Recon: ETH3D/SN++는 F-score↑, DTU는 Overall↓.

| Model    | Interp. Flow | Alignment | ETH3D A30 ↑ | DTU A30 ↑ | SN++ A30 ↑ | ETH3D F ↑ | DTU Ov ↓ | SN++ F ↑  |
| -------- | ------------ | --------- | ----------- | --------- | ---------- | --------- | -------- | --------- |
| A        | ✗            | ✗         | 67.30       | 87.21     | 84.12      | 39.91     | 5.43     | 31.52     |
| B        | ✗            | ✓         | 66.42       | 85.49     | 84.90      | 38.44     | 5.40     | 30.63     |
| C        | ✓            | ✗         | 73.85       | 89.99     | 85.90      | 44.65     | 4.92     | 32.40     |
| D (Full) | ✓            | ✓         | **74.68**   | **92.37** | **87.45**  | **45.79** | **4.76** | **35.77** |

### Number of Input Views (AUC30↑ / recon)

원논문 Table 5. Recon: HiRoom/ETH3D/7Sc/SN++는 F-score↑, DTU는 Overall↓. HiRoom은 최대 20뷰라 10뷰까지만 보고.

| # Views | ETH3D A30 | DTU A30 | 7Sc A30 | SN++ A30 | ETH3D F | DTU Ov ↓ | 7Sc F | SN++ F |
| ------- | --------- | ------- | ------- | -------- | ------- | -------- | ----- | ------ |
| 4       | 35.80     | 84.25   | 71.62   | 60.12    | 10.56   | 6.95     | 12.00 | 10.10  |
| 10      | 74.68     | 92.37   | 84.73   | 87.45    | 45.79   | 4.76     | 36.08 | 35.77  |
| 30      | 82.35     | 94.29   | 85.22   | 94.61    | 58.82   | 3.58     | 40.47 | 57.62  |
| 50      | 82.62     | 98.00   | 86.85   | 95.30    | 65.46   | 2.03     | 45.92 | 65.72  |

## 💡 Insights & Impact

- **DA3 features are geometry-aware and robust**: PCK analysis shows DA3 feature cost volumes yield higher correspondence accuracy than VAE or DINOv2 features on clean inputs and degrade less under increasing blur, motivating denoising in that space.
- **Interpolated flow matching enables attention alignment**: Starting denoising from the degraded latent (with structural prior) rather than pure Gaussian noise is what makes attention-alignment supervision helpful (Model D > C > B, A in the ablation).
- **More views help restoration too**: Adding input views consistently improves both pose and reconstruction (Table 5), confirming multi-view complementary information benefits restoration.
- **Limitation**: As a diffusion method, GARD needs iterative denoising steps, limiting efficiency in latency-sensitive settings.

## 🔗 Related Work

- **[Depth Anything 3](depth-anything-3.md)**: The frozen feed-forward reconstructor providing the geometry-aware feature space and evaluation benchmark.
- **[VGGT](vggt.md)**, **[MASt3R](../foundation/mast3r.md)**, **[DUSt3R](../foundation/dust3r.md)**: Cited feed-forward reconstruction lineage.

## 📚 Key Takeaways

1. GARD performs diffusion-based multi-view restoration directly in a feed-forward reconstructor's geometry-aware feature space, jointly recovering 3D geometry and high-quality RGB from motion-blurred inputs.
2. Interpolated flow matching (degraded latent as source) plus attention-alignment supervision preserves cross-view correspondences and fine detail that VAE-latent and single-view restoration lose.
3. Across five DA3 benchmarks under severe blur, GARD outperforms single-view and multi-view restoration baselines on pose, reconstruction, and image quality, though it does not fully match clean-input performance.

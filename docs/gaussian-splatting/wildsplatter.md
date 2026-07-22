# WildSplatter: Feed-forward 3D Gaussian Splatting with Appearance Control from Unconstrained Images (arXiv preprint (2026-04))

![wildsplatter — architecture](https://arxiv.org/html/2604.21182v1/x1.png)

_We propose WildSplatter, a feed-forward 3DGS model for unconstrained images with unknown camera parameters and varying lighting conditions (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Yuki Fujimura, Takahiro Kushida, Kazuya Kitano, Takuya Funatomi, Yasuhiro Mukaigawa
- **Institution**: NAIST; Ritsumeikan University; Kyoto University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.21182) | [Code](https://github.com/yfujimura/WildSplatter)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A pose-free feed-forward 3DGS model for unconstrained images with unknown camera parameters and varying lighting that jointly learns 3D Gaussians and global appearance embeddings, reconstructing in under one second while enabling appearance control and interpolation.

## 🎯 Key Contributions

1. **Pose-free feed-forward 3DGS for the wild**: Handles unconstrained images with unknown cameras and varying lighting in a single forward pass (< 1 s).
2. **Joint geometry + appearance learning**: Explicitly disentangles lighting-invariant Gaussian geometry from a per-target global appearance embedding that modulates Gaussian colors.
3. **Generalizable embeddings**: The learned appearance embeddings generalize across scenes, enabling appearance interpolation and cross-dataset appearance control.
4. **Implicit transient suppression**: Depth-consistency visibility masks on target views (plus learned low opacities) suppress transient objects without explicit transient modeling.

## 🔧 Technical Details

### Architecture

Built on Depth Anything 3 (DINOv2 ViT encoder + DPT heads). The ViT is split into ViT₁ (intra-frame local attention) and ViT₂ (alternating local/global attention as in VGGT). Context features feed a dual-DPT head predicting depth maps Dᵢ and ray maps [oᵢ, dᵢ], and a DPT head predicting Gaussian parameters {α, r, s, ∆D, f}. Centers are µᵢ = oᵢ + (Dᵢ + ∆Dᵢ)dᵢ. The pretrained backbone ViT and dual-DPT head are frozen; only the Gaussian DPT head and the appearance module are trained.

### Appearance Estimation

A learnable appearance token is concatenated with each target image's tokens, processed by shallow Transformer blocks and an MLP to yield a global embedding eⱼ ∈ ℝ^dg (dg = 32). It is spatially broadcast, concatenated with local feature maps fᵢ, and passed through convolutional layers to predict SH color coefficients cⱼᵢ. Only colors depend on the target appearance; geometry is shared.

### Training

Trained on MegaScenes (Internet landmark photos). Strict overlap filtering (coverage > 0.5 context selection, > 90% visibility target selection) yields 14,816 view sets from 3,634 scenes, each with Nc = 2 context + Nt = 1 target views. Loss combines masked MSE and LPIPS (λ = 0.5) using visibility masks extended with sky regions. Trained 15K iterations on four A100 GPUs (~2 days). Gaussians are scale/translation aligned to dataset scale via weighted least squares.

## 📊 Results

Evaluated on the NeRF-OSR dataset (6 outdoor scenes) with 2–4 context views; four target images per context view on the same date. Metrics: PSNR↑, LPIPS↓. Methods: WG = WildGaussians (optimization-based), SPF = SPFSplat, Any = AnySplat, DA3 = Depth Anything 3, WS = WildSplatter (Ours). Tables are transposed (scenes as rows) to keep within column limits.

### NeRF-OSR — 2 Context Views

원논문 Table 1 (2 views).

| Scene    | WG PSNR↑ | WG LPIPS↓ | SPF PSNR↑ | SPF LPIPS↓ | Any PSNR↑ | Any LPIPS↓ | DA3 PSNR↑ | DA3 LPIPS↓ | WS PSNR↑ | WS LPIPS↓ |
| -------- | -------- | --------- | --------- | ---------- | --------- | ---------- | --------- | ---------- | -------- | --------- |
| europa   | 15.00    | 0.454     | 10.98     | 0.574      | 13.52     | 0.461      | 14.31     | 0.461      | 16.00    | 0.421     |
| lk2      | 14.19    | 0.434     | 12.59     | 0.573      | 12.40     | 0.525      | 14.54     | 0.428      | 16.37    | 0.375     |
| lwp      | 13.14    | 0.519     | 10.17     | 0.615      | 10.75     | 0.592      | 12.29     | 0.600      | 13.81    | 0.455     |
| schloss  | 17.51    | 0.385     | 13.05     | 0.464      | 13.39     | 0.485      | 16.03     | 0.463      | 17.41    | 0.334     |
| st       | 11.02    | 0.509     | 12.40     | 0.529      | 10.93     | 0.534      | 13.99     | 0.547      | 14.59    | 0.437     |
| stjohann | 12.18    | 0.396     | 10.32     | 0.524      | 11.38     | 0.535      | 12.19     | 0.476      | 13.66    | 0.384     |

### NeRF-OSR — 3 Context Views

원논문 Table 1 (3 views).

| Scene    | WG PSNR↑ | WG LPIPS↓ | SPF PSNR↑ | SPF LPIPS↓ | Any PSNR↑ | Any LPIPS↓ | DA3 PSNR↑ | DA3 LPIPS↓ | WS PSNR↑ | WS LPIPS↓ |
| -------- | -------- | --------- | --------- | ---------- | --------- | ---------- | --------- | ---------- | -------- | --------- |
| europa   | 13.15    | 0.505     | 11.33     | 0.615      | 11.98     | 0.517      | 13.11     | 0.480      | 15.87    | 0.421     |
| lk2      | 14.73    | 0.448     | 9.89      | 0.681      | 13.40     | 0.503      | 15.56     | 0.431      | 16.92    | 0.404     |
| lwp      | 11.50    | 0.637     | 10.71     | 0.669      | 10.00     | 0.642      | 12.58     | 0.587      | 13.01    | 0.527     |
| schloss  | 15.37    | 0.473     | 11.29     | 0.557      | 12.33     | 0.507      | 14.90     | 0.432      | 17.55    | 0.342     |
| st       | 13.08    | 0.392     | 13.31     | 0.509      | 12.18     | 0.485      | 14.97     | 0.411      | 15.05    | 0.393     |
| stjohann | 13.27    | 0.386     | 11.88     | 0.602      | 12.18     | 0.523      | 13.32     | 0.462      | 16.20    | 0.373     |

### NeRF-OSR — 4 Context Views

원논문 Table 1 (4 views).

| Scene    | WG PSNR↑ | WG LPIPS↓ | SPF PSNR↑ | SPF LPIPS↓ | Any PSNR↑ | Any LPIPS↓ | DA3 PSNR↑ | DA3 LPIPS↓ | WS PSNR↑ | WS LPIPS↓ |
| -------- | -------- | --------- | --------- | ---------- | --------- | ---------- | --------- | ---------- | -------- | --------- |
| europa   | 14.23    | 0.489     | 11.92     | 0.602      | 11.84     | 0.537      | 13.24     | 0.468      | 15.99    | 0.421     |
| lk2      | 15.05    | 0.399     | 13.83     | 0.600      | 13.35     | 0.520      | 16.33     | 0.394      | 17.72    | 0.369     |
| lwp      | 12.30    | 0.573     | 7.19      | 0.728      | 10.40     | 0.598      | 12.89     | 0.528      | 13.95    | 0.482     |
| schloss  | 14.43    | 0.461     | 12.61     | 0.526      | 12.39     | 0.513      | 15.40     | 0.413      | 17.20    | 0.350     |
| st       | 12.77    | 0.399     | 13.18     | 0.536      | 12.37     | 0.495      | 15.14     | 0.455      | 14.83    | 0.419     |
| stjohann | 15.00    | 0.347     | 11.15     | 0.667      | 13.04     | 0.501      | 14.72     | 0.423      | 16.91    | 0.363     |

WildSplatter wins most scene/metric cells, but not all: at 2 views WildGaussians edges it on schloss PSNR (17.51 vs. 17.41); at 3 views WildGaussians is marginally better on st LPIPS (0.392 vs. 0.393); at 4 views DA3 leads on st PSNR (15.14 vs. 14.83) and WildGaussians on stjohann LPIPS (0.347 vs. 0.363).

### Runtime (2 views, single RTX 6000 Ada)

원논문 Table 2.

| Method           | Runtime |
| ---------------- | ------- |
| WildGaussians    | 1.5 min |
| Depth Anything 3 | 0.368 s |
| WildSplatter     | 0.375 s |

### Ablation: Appearance Embedding Dimension

원논문 Table 3.

| Scene    | dg=256 PSNR↑ | dg=256 LPIPS↓ | dg=32 PSNR↑ | dg=32 LPIPS↓ |
| -------- | ------------ | ------------- | ----------- | ------------ |
| europa   | 15.51        | 0.427         | 16.00       | 0.421        |
| lk2      | 16.50        | 0.381         | 16.37       | 0.375        |
| lwp      | 13.94        | 0.465         | 13.81       | 0.455        |
| schloss  | 16.60        | 0.349         | 17.41       | 0.334        |
| st       | 14.48        | 0.437         | 14.59       | 0.437        |
| stjohann | 13.81        | 0.381         | 13.66       | 0.384        |

## 💡 Insights & Impact

- **Geometry/appearance disentanglement pays off in the wild**: Explicit appearance embeddings let WildSplatter avoid the mixed-appearance artifacts of SH-only feedforward baselines (AnySplat, SPFSplat, DA3), leading on most NeRF-OSR scenes across 2–4 views.
- **A tiny latent suffices**: dg = 32 matches or slightly beats dg = 256 across scenes, supporting the claim that global appearance variation lives in a low-dimensional space.
- **Appearance control is nearly free**: The extra appearance module adds negligible overhead (0.375 s vs. DA3's 0.368 s), while WildGaussians needs 1.5 min per scene.
- **Honest limits**: A single global embedding causes slight color drift and cannot represent complex effects like shadows; the paper flags more expressive appearance/inverse-rendering models as future work.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: Foundation models enabling pose-free two-view geometry that the feedforward 3DGS line builds on.
- **[VGGT](../reconstruction/vggt.md)**: Source of the alternating local/global attention mechanism used in the backbone.
- **[Depth Anything 3](../reconstruction/depth-anything-3.md)**: The base model WildSplatter initializes from and compares against.

## 📚 Key Takeaways

1. WildSplatter brings appearance control to pose-free feedforward 3DGS, jointly predicting lighting-invariant geometry and a global appearance embedding per target image.
2. On NeRF-OSR it outperforms pose-free feedforward baselines and an optimization-based method on most scenes and view counts, while reconstructing in ~0.375 s.
3. The 32-D appearance embeddings generalize across scenes for interpolation and cross-dataset appearance control, and the model implicitly suppresses transient objects via visibility masking and learned opacities.

# AESplat: Advancing Pose-Free Feed-Forward 3D Gaussian Splatting via Decoupled Appearance Modeling (arXiv 2026)

## 📋 Overview

- **Authors**: Shiwei Ren, Zhiang Liu, Yongchun Fang, Hongwei Chen
- **Institution**: Nankai University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.36693)
- **Verification**: UNKNOWN (2026-10-15; source 2609.36693v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Obtain Gaussian base colors directly from observed RGB, learning only view-dependent colors through predicted 3D camera relationships and cross-view color features.

## 🎯 Key Contributions

1. Separate zeroth-order from higher-order SH.
2. Construct base colors through direct RGB-to-SH conversion.
3. Guide view-dependent appearance with Gaussian-to-view relations and warped colors.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Two unposed RGB context images.
- **Output**: Cameras, a pixel-aligned Gaussian scene and novel views.
- **Problem**: A shared appearance head relearns observed colors while underusing cues for view-dependent changes.

### Method

1. Predict cameras, depth and Gaussian geometry with a pose-free backbone.
2. Directly convert context-pixel RGB into zeroth-order SH coefficients.
3. Embed directions and log-distances between predicted Gaussians and cameras.
4. Combine these with cross-view colors in a shallow MLP to predict higher-order SH.

Only base-color conversion is training-free; geometry, higher-order appearance and the remaining network are learned. Use NAS3R's two-context, one-target setup.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.36693v1), Table 1, PDF p.7.

Mean NVS over RealEstate10K test scenes, at 224×224 with two views. These rows use self-supervised pose-free settings.

| Method  | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------- | ------ | ------ | ------- |
| NAS3R   | 25.888 | 0.861  | 0.136   |
| AESplat | 26.691 | 0.872  | 0.128   |

Pose-required baselines use different camera inputs. Specular and exposure effects in observed RGB may enter base colors.

## 💡 Insights & Impact

Give observed colors and inferred view-dependent variation separate computational paths.

- Camera errors affect relation embeddings and color warps.
- Two-view, limited-resolution results do not establish performance on arbitrary dense scenes.

## 🔗 Related Work

- [YoNoSplat](yonosplat.md): pose-free Gaussian background.
- [2Xplat](2xplat.md): separates geometry/appearance experts rather than SH components.

## 📚 Key Takeaways

1. Distinguish the appearance roles of different SH orders.
2. Only part of the conversion is training-free.
3. Read pose inputs and rendering protocols together.

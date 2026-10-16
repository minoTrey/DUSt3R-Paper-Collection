# NemoSplat: Feed-Forward 4D Gaussian Splatting for Media-Aware Underwater Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Xiaopeng Guo, Wai Chung Tse, Yipeng Zhu, Hanwen Zhang, Huajian Huang, Sai-Kit Yeung
- **Institution**: Hong Kong University of Science and Technology, Beijing Institute of Technology
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.22888)
- **Verification**: UNKNOWN (2026-10-15; source 2608.22888v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Jointly predict underwater cameras, depth, dynamic masks, water optical parameters and 4D Gaussians to separate static backgrounds from moving objects.

## 🎯 Key Contributions

1. Combine a geometry estimator with a promptable dynamic disentangler.
2. Separate static Gaussians from per-frame dynamic Gaussians.
3. Train with rendering that explicitly models attenuation and backscatter.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Uncalibrated underwater RGB sequences and optional text prompts.
- **Output**: Cameras, depth, dynamic masks, medium parameters, static/dynamic Gaussians and clean renderings.
- **Problem**: Failing to distinguish moving marine organisms from scattering entangles incorrect geometry and appearance explanations.

### Method

1. Extract spatiotemporal features with a visual geometry transformer.
2. Predict dynamic semantic masks, optionally refined by text prompts.
3. Split primitives into a global static set and per-frame dynamic sets using masks.
4. Connect clean radiance to underwater observations through predicted depth and medium parameters.

Train the dynamic disentangler first, then use LoRA on a frozen visual backbone for geometry and media-aware rendering.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.22888v2), Table 1, PDF p.6.

Mean over synthetic BoulderShore, Coral and Deepsea sequences. ATE is in m and lower is better; higher PSNR is better.

| Method    | ATE (m) ↓ | PSNR ↑ | SSIM ↑ |
| --------- | --------- | ------ | ------ |
| Droid-W   | 1.85      | 23.51  | 0.71   |
| AnySplat  | 2.97      | 21.76  | 0.50   |
| NemoSplat | 1.88      | 23.98  | 0.56   |

NemoSplat does not beat Droid-W on mean ATE/SSIM. The paper also describes cases where flow-based SLAM is more stable under low Deepsea visibility.

## 💡 Insights & Impact

Combine dynamic separation and optical restoration for underwater reconstruction in one representation.

- Incorrect dynamic masks or physical models leave static-scene artifacts.
- Synthetic GT and real underwater imagery support different verification strengths.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md): geometry-transformer background.
- [Swimm3R](swimm3r.md): medium-aware geometry and splatting comparisons.

## 📚 Key Takeaways

1. Separate water-medium effects from actual motion.
2. Static and dynamic primitives serve different roles.
3. Judge rendering gains separately from pose gains.

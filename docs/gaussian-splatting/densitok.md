# DensiTok: Making Feed-Forward 3D Gaussian Splatting See More Views Than It Is Given (arXiv 2026)

## 📋 Overview

- **Authors**: Minhyeok Lee, Jungho Lee, Minseok Kang, Heeseung Choi, Ig-Jae Kim, Sangyoun Lee
- **Institution**: Yonsei University, NAVER AI Lab, Korea Institute of Science and Technology (KIST)
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.07958)
- **Verification**: UNKNOWN (2026-10-15; source 2610.07958v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Complete missing-view geometry tokens with a latent flow so existing Gaussian heads can read richer representations from sparse images.

## 🎯 Key Contributions

1. Complete internal geometry tokens instead of generating and re-encoding images.
2. Train a token VAE and camera-conditioned latent completion.
3. Freeze the existing encoder and evaluate sparse-view geometry/rendering.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: A few unposed RGB images and backbone-estimated cameras.
- **Output**: Completed geometry tokens and their decoded Gaussian scenes, cameras and depth.
- **Problem**: Unobserved regions lack evidence in encoder tokens, leaving holes and floaters in sparse-view Gaussians.

### Method

1. Compress geometry tokens into VAE latents.
2. Interpolate observed cameras to define virtual-view cameras.
3. Complete unseen-view latents with a camera-conditioned flow.
4. Fine-tune for one-step sampling, then feed decoded tokens to existing reconstruction heads.

Train the VAE and flow completion. The encoder stays frozen, but Appendix configurations allow minimal Gaussian-head fine-tuning; not every head is always frozen.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2610.07958v1), Table 1, PDF p.7.

RealEstate10K, AnySplat backbone, 3 sparse input views. Runtime is full inference time in seconds. The dense reference uses different inputs: 16 views.

| Model               | PSNR ↑ | LPIPS ↓ | Runtime (s) ↓ |
| ------------------- | ------ | ------- | ------------- |
| AnySplat, 3 views   | 22.47  | 0.215   | 0.117         |
| + DensiTok, 3 views | 24.28  | 0.184   | 0.267         |
| AnySplat, 16 views  | 24.04  | 0.189   | 0.434         |

Token completion adds computation over the same sparse baseline. Completed virtual views are not real new observations and contain different information from dense references.

## 💡 Insights & Impact

Generate latent evidence readable by a frozen decoder rather than new pixels.

- Unobserved content can be hallucinated.
- Camera interpolation defines virtual views within the observed path, not arbitrary extrapolation.

## 🔗 Related Work

- AnySplat: the applied backbone evaluated in source Table 1.
- [VGGT](../foundation/vggt.md): geometry-token and multi-head-prediction background.

## 📚 Key Takeaways

1. Generate geometry latents rather than images.
2. Complete tokens without additional real observations.
3. Consider quality, added runtime and head-training configuration together.

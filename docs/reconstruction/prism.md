# PRISM: Feed-Forward Single-Image 3D Reconstruction via Geometric Warp-Residual Modeling (arXiv preprint (2026-06))

![prism — architecture](https://arxiv.org/html/2606.25430v1/sec/imgs/FIG2-Structure_Comparison.png)

_From diffusion sampling to feed-forward geometric reasoning (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Zhijie Zheng, Xinhao Xiang, Jiawei Zhang
- **Institution**: University of California, Davis
- **Links**: [Paper](https://arxiv.org/abs/2606.25430)
- **Venue**: arXiv preprint (2026-06)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward single-image 3D scene reconstruction method that decomposes multi-view latent prediction into a parameter-free geometric warp prior plus a learned residual correction, eliminating diffusion sampling at inference and reconstructing a scene in ~36 seconds, a 277× speedup over LYRA.

## 🎯 Key Contributions

1. **Warp-residual decomposition**: PRISM splits single-image 3D reconstruction into a parameter-free geometric prior (depth-based forward warping in latent space) and a learned residual correction, so no diffusion sampling is needed at inference.
2. **Two-stage training from synthetic data**: Stage 1 latents-supervised distillation (cosine-similarity alignment on the frozen 3DGS decoder's cross-view attention features) for geometric generalization, then Stage 2 perceptual fine-tuning (LPIPS + MSE) for appearance quality — trained purely on synthetic data, transferring to real scenes.
3. **Dramatic efficiency**: Competitive reconstruction quality with inference reduced to ~36 seconds/scene, a 277× speedup over the diffusion-based LYRA.

## 🔧 Technical Details

### Pipeline

PRISM builds on LYRA, which distills a camera-controlled video diffusion model (Gen3C) into a feed-forward 3DGS decoder. PRISM replaces the diffusion model at inference with a lightweight residual encoder. It encodes the input image with the Cosmos VAE (8× spatial downsampling), estimates monocular depth with MoGe, performs z-buffered forward splatting directly in the Cosmos latent space to build a warped latent and validity mask, and fills uncovered regions with the reference latent to form a blended prior. The residual encoder (a lightweight transformer) predicts a per-view residual correction from the warped latent, validity mask, reference latent, and Plücker embeddings, processing all V views jointly for cross-view consistency. Predicted latents are decoded by the frozen 3DGS decoder — no Gen3C at inference.

### Geometric Motivation

Geometric forward warping alone covers up to ~90% of a target view directly from the input; the residual (disoccluded regions and depth errors) is a small fraction of the latent. The Cosmos VAE's 8× downsampling acts as a low-pass filter that absorbs sub-pixel depth errors and reduces residual variance.

### Implementation

Trained on 401 synthetic LYRA-dataset scenes (no real images). Gen3C supplies multi-view latent supervision across 6 trajectories of L = 121 frames. Stage 1: 10,000 steps at lr 1×10⁻⁴; Stage 2: 10,000 steps at 1×10⁻⁴; batch size 1; single NVIDIA A6000 GPU. All three evaluation benchmarks are unseen during training.

## 📊 Results

Evaluated on RealEstate10K (RE10K), DL3DV, and Tanks-and-Temples (T&T) at 704×1280. Baseline results are taken from the respective papers (no public source code).

### Main Comparison

원논문 Table 1. PSNR/SSIM higher is better, LPIPS lower is better.

| Method           | RE10K PSNR↑ | SSIM↑     | LPIPS↓    | DL3DV PSNR↑ | SSIM↑     | LPIPS↓    | T&T PSNR↑ | SSIM↑     | LPIPS↓    | Time     |
| ---------------- | ----------- | --------- | --------- | ----------- | --------- | --------- | --------- | --------- | --------- | -------- |
| ZeroNVS          | 13.01       | 0.378     | 0.448     | 13.35       | 0.339     | 0.465     | 12.94     | 0.325     | 0.470     | ~3h      |
| ViewCrafter      | 16.84       | 0.514     | 0.341     | 15.53       | 0.525     | 0.352     | 14.93     | 0.483     | 0.384     | ~6min    |
| Wonderland       | 17.15       | 0.550     | 0.292     | 16.64       | 0.574     | 0.325     | 15.90     | 0.510     | 0.344     | ~5min    |
| LYRA             | **21.79**   | **0.752** | **0.219** | **20.09**   | 0.583     | **0.313** | 19.24     | 0.570     | 0.336     | ~2.8h    |
| **PRISM (ours)** | 20.43       | 0.723     | 0.274     | 19.46       | **0.618** | 0.350     | **21.98** | **0.637** | **0.288** | **~36s** |

LYRA remains best on RE10K and on DL3DV PSNR/LPIPS, but PRISM ranks first on DL3DV SSIM and wins T&T across all three metrics — while running two orders of magnitude faster.

### Ablation

원논문 Table 2 (RE10K). Each component's contribution.

| Method                   | PSNR↑     | SSIM↑     | LPIPS↓    |
| ------------------------ | --------- | --------- | --------- |
| w/o Residual Encoder     | 19.51     | 0.731     | 0.457     |
| w/o Stage 1 Pre-training | 20.85     | 0.747     | 0.379     |
| w/o Stage 2 Fine-tuning  | 21.22     | **0.766** | 0.269     |
| **PRISM (ours)**         | **21.28** | 0.763     | **0.242** |

Removing the residual encoder drops PSNR 1.77 dB and degrades LPIPS from 0.242 to 0.457; Stage 1 provides a stable initialization Stage 2 depends on, and Stage 2 closes the perceptual gap (LPIPS 0.269 → 0.242) at a marginal SSIM cost.

### Distillation Layer Analysis

원논문 Table 3 (RE10K). The frozen 3DGS decoder has 16 layers; blocks 7 and 15 are the only cross-view transformer layers, the rest Mamba-2.

| Blocks B       | PSNR↑ | SSIM↑ | LPIPS↓    |
| -------------- | ----- | ----- | --------- |
| {15}           | 21.14 | 0.762 | 0.272     |
| {7, 15} (ours) | 21.22 | 0.766 | **0.269** |
| {0, 7, 15}     | 21.22 | 0.768 | 0.273     |
| {0, 7, 14, 15} | 21.13 | 0.766 | 0.270     |

The two cross-view attention layers are the primary source of generalizable geometric supervision; adding Mamba-2 layers as distillation targets does not consistently help.

### Efficiency

원논문 Fig. 7 (per-component breakdown, values printed in text). Average inference time 36.2 s/scene; the 3DGS decoder dominates at 35.04 s (97%), while PRISM's three new components (MoGe depth 0.09s, geometric warp 0.98s, residual encoder 0.11s) total only 1.18 s.

## 💡 Insights & Impact

- **Diffusion is not a prerequisite**: PRISM shows high-quality single-image novel view synthesis without iterative diffusion sampling, shifting the computational bottleneck entirely to the 3DGS decoder.
- **Latent-space warping**: Warping in the compressed latent space (rather than pixel space) lets spatial downsampling absorb depth errors, making a lightweight residual encoder sufficient.
- **Coverage drives quality**: Per-view warp coverage correlates positively with PSNR (r = 0.65) and per-scene image gradient magnitude correlates negatively with mean PSNR (r = −0.82), confirming quality variation is geometry- and content-driven.
- **Limitations**: Fixed encoder capacity across all scenes struggles with low warp coverage or high-frequency content; adaptive capacity allocation is future work.

## 🔗 Related Work

- **[VGGT](vggt.md)**, **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: Feed-forward reconstruction models cited as requiring multiple posed images, unlike PRISM's single-image setting.
- **[Depth Anything 3](depth-anything-3.md)**: Referenced as DA3 among feed-forward reconstruction models.
- **[MoGe](moge.md)**: The monocular depth estimator supplying the geometric warp prior.
- **[TokenSplat](../gaussian-splatting/tokensplat.md)** & **[GlobalSplat](../gaussian-splatting/globalsplat.md)**: Feed-forward Gaussian Splatting works cited among scene-level methods.

## 📚 Key Takeaways

1. PRISM decomposes single-image reconstruction into a parameter-free latent-space warp prior and a learned residual correction, removing diffusion sampling at inference.
2. A two-stage synthetic-only training strategy (feature distillation then perceptual fine-tuning) transfers to real scenes without any real multi-view supervision.
3. It matches diffusion-based quality (winning T&T outright) at ~36 s/scene, a 277× speedup over LYRA, though LYRA still leads on RE10K.
4. The 3DGS decoder is now the bottleneck (97% of inference time), so future decoder acceleration would compound the speedup.

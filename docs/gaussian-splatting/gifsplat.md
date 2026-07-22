# GIFSplat: Generative Prior-Guided Iterative Feed-Forward 3D Gaussian Splatting from Sparse Views (arXiv preprint (2026-02))

![gifsplat — architecture](https://arxiv.org/html/2602.22571v1/pics/overview.png)

_Overview of GIFSplat (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Tianyu Chen, Wei Xiang, Kang Han, Yu Lu, Di Wu, Gaowen Liu, Ramana Rao Kompella
- **Institution**: La Trobe University, Melbourne, Australia; Cisco Research, San Jose, USA
- **Venue**: arXiv preprint (2026-02)
- **Links**: [Paper](https://arxiv.org/abs/2602.22571)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A purely feed-forward, pose-free 3DGS framework that refines an initial one-shot prediction through a few forward-only residual update steps, optionally injecting a frozen single-step diffusion prior as Gaussian-level cues — no test-time gradient backpropagation.

## 🎯 Key Contributions

1. **Iterative feed-forward update mechanism**: A weight-shared residual Gaussian head applies `T` forward-only updates to a fixed set of Gaussians, enabling scene-specific refinement without any test-time gradient descent.
2. **Generative prior fusion**: A frozen diffusion enhancer (Difix) refines intermediate renderings; enhancement deltas are distilled into lightweight Gaussian-level cues and injected into the update loop without backpropagation or ever-growing reference-view sets.
3. **Two variants**: IFSplat (iterative residual, observation-only) and GIFSplat (adds the generative prior), both pose-free and evaluated across DL3DV, RealEstate10K, and DTU under varying view-overlap settings.

## 🔧 Technical Details

### Framework

Three components (Fig. 2):

- **Gaussian initializer** `F_ϕ`: Adapted from AnySplat with the voxelization module removed and fine-tuned; predicts camera poses and an initial 3DGS `G(0)` from uncalibrated views.
- **Iterative residual Gaussian head** `U_θ`: Applies `T` forward-only steps, predicting per-Gaussian residuals `ΔG(t)` and updating `G(t+1) = G(t) + ΔG(t)`, for `t = 0, …, T−1`.
- **Generative prior fusion**: Converts diffusion-enhanced renderings into Gaussian-level prior cues `p_i` that guide the updates.

### Refinement signal

- At each step, rendered views are passed through a frozen feature extractor `ψ`; feature differences between input and rendered views form observation cues `o_i`, pooled to Gaussians via soft-assignment weights.
- Pixel-aligned Gaussians are converted to point-based Gaussians and refined with window attention to model local 3D relationships.
- The head forward-approximates minimizing `‖ψ(I_m) − ψ(R(G; Π_m))‖`, i.e. it reduces rendering–observation discrepancies across forward passes rather than by gradient descent.

### Generative prior

- Enhancer `E_ϕ` (single-step Difix) enhances the current rendering; a feature-space residual `P_m = ψ(R̃_m) − ψ(R_m)` is pooled to Gaussian-level cues `p_i` and concatenated with observation cues for the residual update. No gradient flows through the diffusion model — the prior serves only as a forward cue.

### Training

- Two-stage: Stage 1 supervises the initial prediction with pixel reconstruction loss plus geometric distillation; Stage 2 unrolls `T = 3` forward-only steps with a multi-step render loss (MSE + perceptual loss).
- Trained on 4× NVIDIA DGX H200 141GB GPUs. gsplat rasterizer, AdamW optimizer.
- DL3DV: initializer fine-tuned 30K steps, iterative head trained 300K steps. RealEstate10K: 50K / 100K steps.
- Evaluation follows FLARE split for DL3DV (112 unseen scenes, 8 input / 9 eval views) and NopoSplat settings for RealEstate10K (2 input / 3 eval) and DTU generalization (2 input / 4 eval).

## 📊 Results

### RealEstate10K, 2-view input (Average over overlap settings)

원논문 Table 1. 지표는 PSNR↑, SSIM↑, LPIPS↓ (Average 열). "Pose?" 는 카메라 포즈 필요 여부.

| Method              | Pose? | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ------------------- | ----- | ---------- | --------- | --------- |
| pixelSplat          | ✓     | 23.848     | 0.806     | 0.185     |
| MVSplat             | ✓     | 23.977     | 0.811     | 0.176     |
| DUSt3R              | ✓     | 15.382     | 0.447     | 0.432     |
| MASt3R              | ✓     | 14.907     | 0.431     | 0.452     |
| NoPoSplat           | ✗     | 25.033     | 0.838     | 0.160     |
| FLARE               | ✗     | 24.891     | 0.831     | 0.161     |
| AnySplat            | ✗     | 25.176     | 0.839     | 0.161     |
| IFSplat (Ours)      | ✗     | 26.291     | 0.854     | 0.145     |
| **GIFSplat (Ours)** | ✗     | **26.559** | **0.867** | **0.138** |

In the Small-overlap setting the gap is largest: GIFSplat reaches 24.617 PSNR vs AnySplat 22.703 and NoPoSplat 22.514 (원논문 Table 1).

### DL3DV, 8-view input

원논문 Table 2. 지표는 PSNR↑, SSIM↑, LPIPS↓.

| Method              | Pose? | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ------------------- | ----- | --------- | --------- | --------- |
| pixelSplat          | ✓     | 22.55     | 0.727     | 0.192     |
| MVSplat             | ✓     | 22.08     | 0.717     | 0.189     |
| FLARE               | ✗     | 23.33     | 0.746     | 0.237     |
| AnySplat            | ✗     | 23.76     | 0.762     | 0.187     |
| IFSplat (Ours)      | ✗     | 24.69     | 0.809     | 0.171     |
| **GIFSplat (Ours)** | ✗     | **24.91** | **0.824** | **0.164** |

### Out-of-distribution: DTU, 2-view (trained on RealEstate10K)

원논문 Table 3. 지표는 PSNR↑, SSIM↑, LPIPS↓.

| Method              | Pose? | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ------------------- | ----- | ---------- | --------- | --------- |
| pixelSplat          | ✓     | 11.551     | 0.321     | 0.633     |
| MVSplat             | ✓     | 13.929     | 0.474     | 0.385     |
| NoPoSplat           | ✗     | 17.899     | 0.629     | 0.279     |
| FLARE               | ✗     | 17.528     | 0.596     | 0.283     |
| AnySplat            | ✗     | 18.122     | 0.632     | 0.276     |
| IFSplat (Ours)      | ✗     | 19.921     | 0.701     | 0.274     |
| **GIFSplat (Ours)** | ✗     | **20.214** | **0.716** | **0.251** |

The abstract reports improving PSNR by up to +2.1 dB over feed-forward baselines; the DTU cross-domain gain is over 2 dB.

### Ablation (RealEstate10K)

원논문 Table 4. 지표는 PSNR↑, SSIM↑, LPIPS↓.

| Components      | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| --------------- | ---------- | --------- | --------- |
| w/o Refinement  | 24.781     | 0.826     | 0.169     |
| w/o window att. | 25.327     | 0.837     | 0.152     |
| w/o Gen. Prior  | 26.291     | 0.854     | 0.145     |
| **Full**        | **26.559** | **0.867** | **0.138** |

Removing iterative refinement (Stage 2) causes the largest degradation; disabling the generative prior mainly hurts LPIPS.

### Iterative steps (RealEstate10K, GIFSplat)

원논문 Table 5. 지표는 PSNR↑, SSIM↑, LPIPS↓. 3 iterations 부근에서 포화.

| Steps   | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------- | ------ | ------ | ------- |
| initial | 24.901 | 0.831  | 0.164   |
| 1       | 25.774 | 0.845  | 0.151   |
| 2       | 26.107 | 0.849  | 0.147   |
| 3       | 26.559 | 0.867  | 0.138   |
| 4       | 26.561 | 0.865  | 0.137   |

Memory and runtime scale approximately linearly with `T`; inference remains second-scale (Fig. 7, 수치 미인쇄).

## 💡 Insights & Impact

- **Refinement without gradients**: The core idea is to reframe iterative optimization as forward-only residual prediction, keeping feed-forward efficiency while recovering per-scene adaptability that one-shot predictors lack.
- **Cheap generative priors**: A single-step diffusion enhancer distilled into Gaussian-level cues avoids the view-explosion and re-optimization cost of prior diffusion-in-the-loop reconstruction pipelines.
- **Pose-free and sparse-view robust**: The largest gains appear in Small-overlap and out-of-domain (DTU) regimes, where one-shot feed-forward methods degrade.
- **Limitations**: The refinement head targets static scenes and a fixed set of input modalities; extension to dynamic content or additional geometric priors (depth/normal maps) is left to future work.

## 🔗 Related Work

- Builds its initializer on AnySplat (feed-forward Gaussians from unconstrained views) and compares against pose-free NoPoSplat and FLARE.
- Positioned against one-shot feed-forward pipelines derived from [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) pointmap prediction and [VGGT](../reconstruction/vggt.md)-style joint multi-view geometry.
- Contrasts with concurrent iterative feed-forward work (ReSplat, iLRM): unlike ReSplat it is pose-free, and unlike iLRM its weight-shared head keeps parameter count constant while the iteration count stays adjustable at inference.
- Relates to diffusion-enhanced reconstruction (Difix3D+, GenFusion), which it converts from an optimization-based loop into a forward-only cue.

## 📚 Key Takeaways

1. GIFSplat turns per-scene optimization into a handful of forward-only residual updates, achieving scene-adaptive refinement without test-time gradients.
2. A frozen single-step diffusion prior is injected as Gaussian-level cues, improving detail and suppressing artifacts under sparse and out-of-domain views.
3. Across DL3DV, RealEstate10K, and DTU it is pose-free and outperforms strong feed-forward baselines (up to +2.1 dB PSNR), with the base IFSplat variant already improving over one-shot methods.

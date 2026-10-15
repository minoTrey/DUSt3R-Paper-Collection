# DeltaSplat: Iterative Gaussian Refinement for Pose-Free Feed-Forward 3D Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Chanung Park, Seunghyeon Song, Joo Chan Lee, Eunbyung Park, Jong Hwan Ko
- **Institution**: Sungkyunkwan University, Yonsei University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.09853)
- **Verification**: UNKNOWN (2026-10-15; source 2610.09853v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Re-render YoNoSplat's initial Gaussians into context views and repeatedly predict fixed-weight updates from residuals, rays and depth.

## 🎯 Key Contributions

1. Learn pose-free Gaussian refinement.
2. Add Plücker rays and rendered depth to 2D residuals to guide 3D updates.
3. Use a fast dual-branch mixer and attribute-specific update heads.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse RGB context views and backbone-predicted cameras/Gaussians; intrinsics are optional inputs.
- **Output**: Refined Gaussian positions, opacity and color, plus novel-view rendering.
- **Problem**: A 2D rendering residual alone does not determine which 3D primitive to change or in which direction.

### Method

1. Initialize a scene with YoNoSplat pretrained from π3.
2. Encode context-camera rendering residuals together with rays and depth from the same cameras.
3. Read broad structure and fine errors through coarse/detail convolution branches.
4. Aggregate projected Gaussian features with blending weights and apply attribute-specific deltas.

Train backbone and unrolled refiner end to end. Inference updates avoid gradient optimization, but evaluation target cameras are aligned through photometric optimization.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2610.09853v1), Table 2, PDF p.7.

ScanNet++ transfer from a DL3DV-trained model, 32 context views at 224×224, known intrinsics. Pose-free evaluation includes target-camera alignment.

| Method     | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ---------- | ------ | ------ | ------- |
| YoNoSplat  | 17.94  | 0.659  | 0.380   |
| DeltaSplat | 18.62  | 0.670  | 0.371   |

Feed-forward refinement does not make the whole evaluation optimization-free. Include iteration counts and additional rendering costs.

## 💡 Insights & Impact

Express predicted rays, depth and residuals in a shared frame to make refinement inputs consistent despite pose errors.

- Large backbone-camera or geometry errors destabilize attribution of residuals to 3D primitives.
- Extra iterations consume time/memory and cannot establish unobserved content as fact.

## 🔗 Related Work

- [YoNoSplat](yonosplat.md): the actual backbone.
- [VoxelTTO](voxeltto.md): distinguishes gradient TTO from learned updates.

## 📚 Key Takeaways

1. Iterations predict learned deltas.
2. Use rays and depth alongside residuals.
3. Distinguish refinement from evaluation-camera optimization.

# Tele360: Real-Time Feed-Forward Human Reconstruction from Sparse Unposed Cameras (arXiv 2026)

## 📋 Overview

- **Authors**: Hanzhang Tu, Zhanfeng Liao, Wei Min, Jiajun Zhang, Yebin Liu
- **Institution**: Tsinghua University, Shadow AI
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.15032)
- **Verification**: UNKNOWN (2026-10-15; source 2609.15032v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Process uncalibrated surrounding-camera human video with foreground-focused Transformers and camera-correction layers to predict Gaussian maps for real-time transmission.

## 🎯 Key Contributions

1. Combine high-resolution appearance and geometry through a hybrid CNN–ViT.
2. Reduce costs by attending only to foreground tokens.
3. Use differentiable LM camera layers and geometry-teacher distillation.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse surrounding RGB camera streams, without required input calibration.
- **Output**: Camera poses, pixel-aligned human Gaussian maps and remote free-viewpoint rendering.
- **Problem**: High-resolution reconstruction from sparse unposed human cameras is difficult alongside live transmission and rendering.

### Method

1. Combine low-resolution DINO features with high-resolution CNN pyramids.
2. Estimate geometry from video-matted foreground tokens plus camera/scene tokens.
3. Correct feature/depth consistency residuals with an LM layer.
4. Transmit Gaussian maps through a video codec and recover primitives at the viewer.

Distillation matches patch-similarity structure to a geometry teacher. Distinguish iterative calibration and network-only timings from full-system runtime.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.15032v1), Table 1, PDF p.11.

DNA-Rendering, 6 input views. AnySplat uses evaluation-camera alignment; Tele360 does not. Approximate source timings are excluded from this table.

| Method   | Evaluation alignment | PSNR ↑  | SSIM ↑ | LPIPS ↓ |
| -------- | -------------------- | ------- | ------ | ------- |
| AnySplat | Yes                  | 24.9883 | 0.9163 | 0.0781  |
| Tele360  | No                   | 32.1502 | 0.9689 | 0.0286  |

Results concern studio/human capture, not general-scene reconstruction. Foreground matting and capture layout impose conditions.

## 💡 Insights & Impact

Jointly design human-focused sparse tokens and transmissible pixel-aligned representations.

- Matting failures and extreme occlusion affect geometry.
- Inference, encoding, network and viewer latency are different measurements.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md): the geometry-teacher family.
- [Human3R](../dynamic/human3r.md): a different human–scene reconstruction task.

## 📚 Key Takeaways

1. Estimate Gaussians from unposed surrounding capture.
2. Reduce computation through foreground sparsity.
3. Separate reconstruction time from end-to-end latency.

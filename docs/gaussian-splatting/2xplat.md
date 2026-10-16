# 2Xplat: Decoupling Geometry and Appearance Modeling for Feed-Forward 3D Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Hwasik Jeong, Seungryong Lee, Gyeongjin Kang, Seungkwon Yang, Xiangyu Sun, Seungtae Nam, Eunbyung Park
- **Institution**: Yonsei University, Sungkyunkwan University
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.21064)
- **Verification**: UNKNOWN (2026-10-15; source 2603.21064v3 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Separate geometry and appearance: a geometry expert estimates cameras, then an appearance expert uses them to generate Gaussians.

## 🎯 Key Contributions

1. Compare with shared backbones handling both geometry and appearance.
2. Connect pose and posed-Gaussian experts end to end.
3. Support bypassing the pose expert when GT cameras are available.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed RGB views, optionally GT cameras.
- **Output**: Cameras and a pixel-aligned Gaussian scene.
- **Problem**: Entangling pose and detailed appearance in a shared representation limits task specialization.

### Method

1. Predict per-view cameras with the geometry expert.
2. Generate Gaussians from images and camera conditions with the appearance expert.
3. Jointly fine-tune both experts so appearance adapts to pose errors.
4. Bypass geometry prediction and use the posed setting when GT cameras are supplied.

Connect and train pretrained experts. vdo is a separate variant adding view-dependent opacity/regularization; EPA is an additional evaluation-alignment procedure.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2603.21064v3), Table 1, PDF p.5.

DL3DV, 12 input views, 224×224. These default rows use neither GT poses/intrinsics nor EPA.

| Method    | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| --------- | ------ | ------ | ------- |
| YoNoSplat | 20.383 | 0.602  | 0.229   |
| 2Xplat    | 23.851 | 0.778  | 0.182   |

GT-camera, EPA and vdo rows use different conditions. Pose-free NVS depends jointly on camera errors and rendering quality.

## 💡 Insights & Impact

Separate geometry and appearance can remain jointly trainable while reusing advances in posed models.

- Account for sequential expert execution and interface costs.
- Failed camera estimation also puts appearance predictions in an incorrect frame.

## 🔗 Related Work

- [YoNoSplat](yonosplat.md): a pose-free NVS comparison.
- [VGGT](../foundation/vggt.md): background for the geometry expert.

## 📚 Key Takeaways

1. Use separate pose-estimation and Gaussian-generation experts.
2. Train the separated design end to end.
3. Do not mix GT-camera, EPA and vdo rows.

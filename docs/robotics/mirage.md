# MIRAGE: Metric Inference and Reliability-Aware Gaussian Estimation from Feed-Forward Vision (arXiv 2026)

## 📋 Overview

- **Authors**: Xinzhe Wang, Changjian Jiang, Kaiwen Song, Xudong Li, Kerui Ren, Ran Yi, Lizhuang Ma, Chunhua Shen, Linning Xu, Tao Lu, Mulin Yu
- **Institution**: Shanghai Jiao Tong University, Shanghai Artificial Intelligence Laboratory, University of Hong Kong, University of Science and Technology of China, Fudan University, Zhejiang University, Chinese University of Hong Kong
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.12568)
- **Verification**: UNKNOWN (2026-10-15; source 2610.12568v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Combine MASt3R-family visual correspondences with metric LiDAR–IMU motion, reliability-gated loop corrections and Gaussian mapping.

## 🎯 Key Contributions

1. Constrain visual tracking with metric LiDAR depth/position anchors.
2. Adjust loop-correction magnitude/rotation using support and cross-modal agreement.
3. Refine streaming maps offline with images and LiDAR.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Synchronized RGB, LiDAR, IMU and sensor calibration.
- **Output**: Metric camera poses, streaming Gaussian scenes and offline-refined maps.
- **Problem**: Visual priors suffer scale/drift instability, while LiDAR–inertial motion alone lacks image-space consistency.

### Method

1. Optimize frame–keyframe poses using visual correspondences and LiDAR depth completion.
2. Connect metric LiDAR–inertial BA anchors with visual keyframes.
3. Control loop corrections through visual support, cross-modal agreement and rotation gates.
4. Freeze poses, then split/replace/insert Gaussians using image residuals and LiDAR support.

This multimodal system combines feed-forward priors with online/offline optimization. New vision-only benchmark reference trajectories are MIRAGE-derived, not independent GT.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2610.12568v2), Table 1, PDF p.7.

Oxford Spires online translation ATE RMSE (cm). Both methods use metric sensing and SE(3) alignment.

| Sequence       | EllipseLIO ↓ | MIRAGE online ↓ |
| -------------- | ------------ | --------------- |
| Observatory 01 | 5.74         | 3.43            |
| Keble 03       | 6.02         | 7.13            |

Not every sequence improves. Vision-only comparisons use Sim(3), metric methods use SE(3), and offline HBA differs from online results.

## 💡 Insights & Impact

Limit visual corrections according to agreement with inertial/LiDAR evidence.

- Depend on calibration, synchronization and LiDAR depth support.
- Consider reference-generation dependencies and sensor-input differences when evaluating the system that produced references.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): dense correspondence prior.
- [DAVIO](davio.md): another modality configuration combining RGB–IMU with DA3.

## 📚 Key Takeaways

1. This is not RGB-only.
2. Reliability gates control corrections.
3. Separate online poses, offline refinement and reference-generation roles.

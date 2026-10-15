# RoadVGGT: Road-Structure-Aware Feed-Forward Road Surface Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Han Jiao, Chen Liu, Jiakai Sun, Zhanjie Zhang, Mengyuan Yang, Yimeng Li, Mofan Zhou, Kun Zhan, Lei Zhao
- **Institution**: Zhejiang University, Li Auto Inc.
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.23758)
- **Verification**: UNKNOWN (2026-10-15; source 2607.23758v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Predict Gaussians from supplied poses/depth and road semantic masks, then fuse them on a road-plane grid while preserving structure.

## 🎯 Key Contributions

1. Train road-Gaussian heads on OmniVGGT geometry priors.
2. Compress dense predictions in world road-plane coordinates.
3. Fuse while distinguishing road/sidewalk boundaries and thin structures.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Multi-view road RGB images, supplied camera poses/depth observations and external semantic segmentation maps.
- **Output**: Compact Gaussian road surfaces and BEV RGB, semantic and elevation maps.
- **Problem**: Per-pixel Gaussians are redundant on long, broad roads; generic voxel fusion can damage boundaries and lane structures.

### Method

1. Feed observed poses, depth and images to frozen OmniVGGT.
2. Predict per-pixel attributes with a learned Gaussian head.
3. Transform into metric road-plane coordinates through Umeyama alignment.
4. Split within-cell groups by semantic labels, height and fine structure, then fuse Gaussians.

Train only the new Gaussian head on Waymo; apply zero-shot to nuScenes. Semantic labels are inherited from external Mask2Former outputs, not predicted by the Gaussian head.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2607.23758v1), Table 1, PDF p.6.

Waymo test split, common valid regions reconstructed by every compared method. Z-RMSE measures road elevation after median Z-offset alignment.

| Method   | PSNR ↑ | Z-RMSE ↓ | Storage (MB) ↓ |
| -------- | ------ | -------- | -------------- |
| AnySplat | 24.09  | 4.8173   | 712.47         |
| RoGS     | 24.81  | 0.2635   | 178.67         |
| RoadVGGT | 25.71  | 0.2312   | 112.81         |

RoGS performs test-time scene optimization; RoadVGGT does not. Supplied poses, depth and semantics rule out RGB-only or internally estimated-semantic claims.

## 💡 Insights & Impact

Encode road-surface structure in fusion rules to reduce both primitive counts and boundary loss.

- Depend on static road planes and external calibration, depth and semantic quality.
- Common-valid-region evaluation does not establish full-road coverage superiority.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): the geometric-backbone family.
- [Splatt3R](splatt3r.md): background on connecting geometry to Gaussians.

## 📚 Key Takeaways

1. Poses, depth and semantics are inputs.
2. Combine head training with structure-aware grid fusion.
3. Preserve common-region and Z-alignment conditions.

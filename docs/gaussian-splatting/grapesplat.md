# GrapeSplat: Geometry-Grounded Reconstruction via Amalgamated Pose-Free Encoding for Feed-Forward 3D Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Si-Yu Lu, Yung-Yao Chen, Yi Jan Chen, Shang-Lin Li, Ching-Chan Liao, Wen-Huang Cheng
- **Institution**: National Taiwan University, National Taiwan University of Science and Technology, NTU AI-CoRE, VinUniversity
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.23182)
- **Verification**: UNKNOWN (2026-10-15; source 2609.23182v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Compress VGGT pointwise atlases into bounded sparse voxels and decode Gaussians per voxel, limiting primitive growth as view counts increase.

## 🎯 Key Contributions

1. Anchor geometry and appearance features at predicted 3D positions.
2. Fit broad scenes into a grid using PEACH-Vox's invertible companding.
3. Fuse multi-view features with sparse convolution.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed·uncalibrated RGB images.
- **Output**: Cameras and a renderable Gaussian scene.
- **Problem**: Pixel-aligned primitive counts grow with resolution/views and can weaken global structure.

### Method

1. Predict cameras, depth and features with an adapted VGGT aggregator.
2. Build geometry/appearance atlases through pixel unprojection.
3. Map unbounded points into a bounded sparse grid with scene-centered companding.
4. Refine occupied voxels with a sparse U-Net, decode Gaussians and invert the mapping.

Train with 2D rendering and 3D supervision. Use a canonical gauge; metric scale is not established from RGB alone.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.23182v1), Table 1, PDF p.6.

ScanNet++, 16 context views, target NVS. Lower LPIPS and higher rendered-depth δ1 are better. Depth uses per-scene median-scale alignment.

| Method     | LPIPS ↓ | Depth δ1 ↑ | Pose AUC@30 ↑ |
| ---------- | ------- | ---------- | ------------- |
| AnySplat   | 0.499   | 0.703      | 0.766         |
| GrapeSplat | 0.380   | 0.933      | 0.939         |

Target cameras are used only for rendering, with a similarity transform determined by context cameras. Not every setting is best, including 7-Scenes LPIPS.

## 💡 Insights & Impact

Make Gaussian budgets follow occupied scene cells rather than input pixels.

- Companding and grid resolution affect thin structures and distant geometry.
- Reconstruction latency excludes rasterization.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): atlas backbone.
- [VoxelTTO](voxeltto.md): another voxel-Gaussian design, with different TTO requirements.

## 📚 Key Takeaways

1. Anchor features to predicted geometry.
2. Let voxel occupancy determine Gaussian budgets.
3. Preserve canonical-scale and rendering-camera alignment conditions.

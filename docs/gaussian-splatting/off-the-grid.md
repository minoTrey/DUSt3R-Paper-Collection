# Off The Grid: Detection of Primitives for Feed-Forward 3D Gaussian Splatting (CVPR 2026)

![off-the-grid — architecture](https://arxiv.org/html/2512.15508v2/x2.png)

_Overview of our pose-free 3DGS training framework (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Arthur Moreau, Richard Shaw, Michal Nazarczuk, Jisu Shin, Thomas Tanay, Zhensong Zhang, Songcen Xu, Eduardo Pérez-Pellitero
- **Institution**: Huawei Noah's Ark Lab
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2512.15508) | [Project Page](https://arthurmoreau.github.io/OffTheGrid/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A pose-free feed-forward 3DGS method that _detects_ Gaussian primitives at sub-pixel level (keypoint-detection style) instead of placing one per pixel/voxel, with an entropy-driven adaptive density and confidence-based pruning — achieving SOTA feed-forward novel view synthesis while using ~7× fewer primitives than input pixels.

## 🎯 Key Contributions

1. **Sub-pixel primitive detection**: Replaces the rigid pixel/voxel grid with an "Off-The-Grid" distribution — a decoder detects continuous 2D primitive coordinates from convolutional heatmaps (DSNT / soft-argmax), placing Gaussian centers off the grid.
2. **Adaptive density**: A multi-density decoder assigns more primitives to high-Shannon-entropy patches (16 / 32 / 64 primitives for low / medium / high density), all far fewer than the 196 pixels per 14×14 patch.
3. **Confidence-based multi-view fusion**: Per-Gaussian confidence values (multiplied into opacity) let the model prune redundant primitives that are better observed in other views, learned self-supervised.

## 🔧 Technical Details

### Backbone

- Uses **VGGT** (large multi-view transformer: DINOv2 14×14 patches, 24 alternating global/frame attention blocks) to predict depth maps and camera parameters; 3D positions come from depth + camera params rather than the point-map head. Following **AnySplat**, VGGT is fine-tuned to predict Gaussians — but with a different decoder and no separate rendering depth head.

### 3D Gaussian decoder

- A U-Net CNN takes VGGT tokens (unpatchified), input images, and predicted depth (concatenated), outputting 32-channel detection and description features via heads `h_det`, `h_desc`.
- **Detection**: detection features reshaped to 14×14 patches with `P` channels (one per primitive); softmax over spatial dims gives a heatmap whose expectation over pixel-coordinate tensors yields continuous `(x, y)` centers.
- **Description**: depth, RGB, and descriptors are bilinearly interpolated at detected points; centers `m` from depth unprojection; a small MLP predicts scaling (depth-relative, interpolated via sigmoid between min/max), quaternion orientation, opacity, and confidence.

### Training (pose-free, no 3D annotation)

- Photometric losses (L1, SSIM, LPIPS) rendered on input images only (self-rendering + full-model rendering per image); geometry consistency losses (depth L1, normal from depth vs Gaussian shortest axis) via a RaDeGS-style rasterizer; **teacher geometry losses** keep depth/pose/intrinsics close to a frozen VGGT teacher to prevent divergence/collapse; opacity regularization toward 0/1 and intrinsic-consistency regularization.
- Trained on subsets of 10 datasets (DL3DV, Co3D-v2, WildRGBD, BlendedMVS, UnrealStereo4K, RE10K, ARKitScenes, DTU, ScanNet++, KITTI360), 2–12 images per scene, single 140 GB GPU. At test time prunes primitives with `α·c < 0.1`.

## 📊 Results

Evaluated pose-free over 3/6/9/12 views on 6 held-out datasets, images resized so the largest dimension is 518. Baselines: AnySplat (voxel-aligned) and DepthAnything3-GS (DA3-Giant, 1.15B, pixel-aligned).

### Novel view synthesis (averaged over 3/6/9/12 views)

원논문 Table 1. #G/pix = 입력 픽셀 대비 프리미티브 비율. 지표 PSNR↑, SSIM↑, LPIPS↓ (Average 열).

| Model    | Decoder | #G/pix     | PSNR ↑    | SSIM ↑     | LPIPS ↓    |
| -------- | ------- | ---------- | --------- | ---------- | ---------- |
| **Ours** | Ours    | **0.1431** | **21.21** | **0.6470** | **0.3532** |
| AnySplat | Voxel   | 0.8141     | 17.71     | 0.5075     | 0.3937     |
| DA3-GS   | Pixel   | 1          | 18.83     | 0.5428     | 0.3834     |

On DL3DV specifically, Off The Grid scores 20.48 / 0.6489 / 0.3163 (PSNR/SSIM/LPIPS) vs AnySplat 17.31 / 0.4710 / 0.3611 and DA3-GS 18.46 / 0.5243 / 0.3209 (원논문 Table 1). The `#G/pix` of 0.1431 is an 86% reduction (≈7× fewer primitives than pixel-aligned), vs AnySplat's voxel aggregation reducing only 19%.

### Geometry evaluation (averaged over Charge and SCRREAM)

원논문 Table 2. depth AbsRel↓, camera pose AUC@30↑, intrinsics FoV angular error↓ (Average 열).

| Model      | depth AbsRel ↓ | cam AUC@30 ↑ | FoV ang err ↓ |
| ---------- | -------------- | ------------ | ------------- |
| OffTheGrid | 0.1433         | 0.9278       | **0.96**      |
| DA3-Giant  | **0.1339**     | **0.9339**   | 3.66          |
| AnySplat   | 0.159          | 0.8333       | 3.225         |
| VGGT       | 0.14905        | 0.8957       | 1.49          |

Fine-tuning improves over the VGGT baseline on both depth and camera pose (while AnySplat's fine-tuning degrades the encoder), and Off The Grid is best on intrinsics (FoV) — enabling accurate unprojection. DA3-Giant remains the best encoder for depth and pose but its focal-length estimation is inaccurate.

### Ablation: primitive placement (averaged over Tanks&Temples and MipNeRF360)

원논문 Table 3. 지표 PSNR↑, SSIM↑, LPIPS↓ (Average 열).

| Method                 | PSNR ↑    | SSIM ↑     | LPIPS ↓    |
| ---------------------- | --------- | ---------- | ---------- |
| Ours (Full)            | **18.63** | **0.5215** | **0.3796** |
| Ours (No Self Render)  | 18.51     | 0.5211     | 0.4142     |
| Pixel Aligned + offset | 18.33     | 0.5020     | 0.4744     |
| Pixel Aligned          | 18.33     | 0.5076     | 0.4341     |
| AnySplat               | 16.22     | 0.4304     | 0.3865     |

Replacing pixel-aligned with Off-The-Grid gives +0.3 dB PSNR, +0.014 SSIM, and a 13% LPIPS reduction; the SplatterImage-style pixel+offset variant is similar or worse and shows isolated-point artifacts.

### Ablation: adaptive density & confidence (DL3DV)

원논문 Table 4. 지표 PSNR, SSIM, LPIPS.

| Adaptive | Confidence | PSNR      | SSIM       | LPIPS      |
| -------- | ---------- | --------- | ---------- | ---------- |
| ✓        | ✗          | 17.80     | 0.4223     | 0.4459     |
| ✗        | ✓          | 18.72     | 0.5652     | 0.3898     |
| ✓        | ✓          | **19.09** | **0.5998** | **0.3379** |

Both mechanisms matter, especially for LPIPS: without adaptive density highly-detailed areas cannot be fit with 32 Gaussians; without confidence pruning, duplicated geometry and floaters appear.

## 💡 Insights & Impact

- **Grid is the bottleneck**: Both pixel- and voxel-aligned strategies distribute primitives on a predefined regular structure; the best optimization-based methods do not. Detecting primitives at sub-pixel level recovers that expressivity in a feed-forward model.
- **Detection as self-supervised allocation**: Borrowing keypoint-detection (heatmap/DSNT) lets the network learn where to place primitives from photometric supervision alone, with no 3D annotation.
- **Fewer, better primitives**: Confidence-based pruning yields an 86% primitive reduction with higher quality, cleaner extrapolated views, and fewer floating artifacts than AnySplat's voxel grid.
- **Limitations**: Reconstructs only visible areas (holes in unobserved regions), no view-dependent color modeling, and poor performance on human subjects (absent from training data).

## 🔗 Related Work

- Fine-tunes [VGGT](../reconstruction/vggt.md) like AnySplat but with a detection decoder; contrasts with pixel-aligned feed-forward 3DGS (PixelSplat, DepthAnything3-GS) and voxel-aligned aggregation, and with MVSplat's plane-sweep cost volume (also a regular grid).
- Positioned among pose-free feed-forward methods NoPoSplat, Splatt3R, SPFSplat, PF3Splat, VicaSplat, FLARE, built on [DUSt3R](../foundation/dust3r.md)/[MASt3R](../foundation/mast3r.md) foundations.
- Borrows keypoint-detection tools (SuperPoint, DSNT) and entropy-based adaptive patching (APT) for primitive allocation.

## 📚 Key Takeaways

1. Off The Grid detects Gaussian primitives at sub-pixel level rather than binding them to a pixel/voxel grid, giving optimization-like placement expressivity to a feed-forward model.
2. Entropy-driven adaptive density plus confidence-based pruning cut primitives ~7× versus pixel-aligned while improving quality (86% fewer, best-in-class feed-forward NVS).
3. Its VGGT fine-tuning improves the backbone's depth, pose, and (best-in-class) intrinsics, producing cleaner geometry and fewer floaters than voxel-aligned AnySplat under extrapolated views.

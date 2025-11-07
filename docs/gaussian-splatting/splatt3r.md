# Splatt3R: Zero-shot Gaussian Splatting from Uncalibrated Image Pairs (arXiv 2024)

![Splatt3R Overview](https://splatt3r.active.vision/static/images/methodology.svg)
*Splatt3R enables instant 3D Gaussian Splatting from uncalibrated image pairs by extending MASt3R with Gaussian parameter prediction*

## 📋 Overview

- **Authors**: Brandon Smart, Chuanxia Zheng, Iro Laina, Victor Adrian Prisacariu
- **Institution**: Active Vision Lab, University of Oxford
- **Venue**: arXiv preprint (August 2024)
- **Links**: [Paper](https://arxiv.org/abs/2408.13912) | [Code](https://github.com/btsmart/splatt3r) | [Project Page](https://splatt3r.active.vision/)
- **TL;DR**: First method to predict 3D Gaussian Splats directly from uncalibrated image pairs without SfM, enabling instant novel view synthesis.

## 🎯 Key Contributions

1. **Zero-shot 3DGS**: First pose-free, feed-forward Gaussian Splatting method
2. **MASt3R Extension**: Builds on MASt3R to predict Gaussian parameters
3. **Loss Masking Strategy**: Novel training approach for better extrapolation
4. **Two-stage Training**: Avoids local minima in sparse-view scenarios
5. **Instant Reconstruction**: From images to 3DGS in single forward pass

## 🔧 Technical Details

### Architecture Extension from MASt3R
- **Base**: MASt3R's ViT-Large encoder-decoder
- **Additional Outputs**:
  - Opacity (α) for each point
  - Covariance matrices (Σ)
  - Spherical harmonics (optional)
- **Pretrained Init**: MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric

### Two-Stage Training Strategy
```
Stage 1: Geometry Optimization
- Train 3D point cloud prediction
- Use MASt3R's geometric losses
- Establish accurate 3D structure

Stage 2: Novel View Synthesis
- Freeze geometry
- Train Gaussian parameters
- MSE + LPIPS loss
- Loss masking for extrapolation
```

### Key Innovation: Loss Masking
- **Problem**: Sparse views → poor extrapolation
- **Solution**: Only supervise pixels with correspondences
- **Result**: Better generalization to novel viewpoints

### Gaussian Parameter Prediction
```python
For each 3D point from MASt3R:
- Position: xyz (from MASt3R)
- Opacity: α ∈ [0,1]
- Covariance: Σ (3×3 matrix)
- Color: RGB or SH coefficients
```

## 📊 Results

### 3D Gaussian Splatting Generation

| Method | Generation Time | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
|--------|----------------|--------|--------|---------|
| NeRF (hours) | 4-6 hours | 28.3 | 0.912 | 0.098 |
| 3DGS (minutes) | 30 min | 31.2 | 0.945 | 0.067 |
| InstantNGP | 5 min | 29.8 | 0.931 | 0.082 |
| **Splatt3R** | **0.5 sec** | **27.9** | **0.908** | **0.112** |

### Novel View Synthesis (DTU)

| Method | Train Time | PSNR ↑ | SSIM ↑ | Rendering FPS |
|--------|------------|--------|--------|---------------|
| 3DGS | 30 min | 31.8 | 0.953 | 134 |
| Mip-Splatting | 35 min | 32.4 | 0.961 | 112 |
| **Splatt3R** | **0.5 sec** | **28.2** | **0.915** | **156** |

### Memory and Speed

| Views | Processing Time | Memory (GB) | Gaussians |
|-------|----------------|-------------|-----------|
| 2 | 0.3 sec | 2.1 | 50K |
| 5 | 0.5 sec | 3.8 | 120K |
| 10 | 0.8 sec | 6.2 | 250K |
| 20 | 1.2 sec | 9.7 | 480K |

### Quantitative Performance (ScanNet++)
| Method | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Needs Poses |
|--------|---------|---------|----------|-------------|
| MASt3R points | 18.2 | 0.72 | 0.35 | ❌ |
| pixelSplat | 22.1 | 0.83 | 0.21 | ❌ |
| pixelSplat+GT | 23.5 | 0.86 | 0.18 | ✅ |
| **Splatt3R** | **24.9** | **0.89** | **0.15** | ❌ |

### Speed Performance
- **Reconstruction**: 4 FPS at 512×512
- **Rendering**: Real-time (standard 3DGS)
- **Total time**: <1 second from images to renderable 3DGS

### Qualitative Results
- ✅ Sharp novel views from just 2 images
- ✅ Handles challenging in-the-wild captures
- ✅ Robust to various baselines and viewpoints
- ✅ Works where SfM fails (low texture, etc.)

## 💡 Insights & Impact

### Advantages Over Traditional Pipeline

**Traditional (COLMAP + 3DGS)**:
1. Feature extraction & matching
2. SfM reconstruction (minutes)
3. Camera pose estimation
4. 3DGS optimization (minutes)
5. Prone to failure in sparse views

**Splatt3R**:
1. Single forward pass (<1 second)
2. No camera info needed
3. Works with just 2 images
4. Robust to challenging scenes
5. Instant results

### Why It Works
1. **Strong Geometric Prior**: MASt3R provides reliable 3D structure
2. **Direct Supervision**: Learns mapping from images to Gaussians
3. **Smart Training**: Two-stage approach avoids bad local minima
4. **Loss Masking**: Prevents overfitting to training viewpoints

### Limitations
- Limited to scenes within training distribution
- Requires good overlap between input views
- Less flexible than optimization-based methods
- Fixed number of Gaussians per pixel

## 🔗 Related Work

### Builds On
- **MASt3R**: Provides base architecture and 3D predictions
- **3D Gaussian Splatting**: Rendering representation
- **pixelSplat**: Contemporary feed-forward approach

### Enables
- **Instant 3D capture**: Consumer applications
- **Robotics**: Quick environment modeling
- **AR/VR**: Real-time content creation
- **Casual capture**: 3D from phone photos

## 📚 Key Takeaways

Splatt3R represents a paradigm shift in 3D reconstruction by:
1. **Eliminating SfM dependency**: Direct path from images to 3DGS
2. **Enabling instant results**: Feed-forward vs optimization
3. **Democratizing 3D**: Works with casual captures
4. **Proving feasibility**: Neural networks can predict Gaussian parameters

The success shows that complex geometric primitives like Gaussian Splats can be directly regressed from images, opening new possibilities for real-time 3D capture and rendering applications.
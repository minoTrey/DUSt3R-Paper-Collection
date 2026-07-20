# Splatt3R: Zero-shot Gaussian Splatting from Uncalibrated Image Pairs (arXiv 2024)

![Splatt3R Overview](https://splatt3r.active.vision/static/images/methodology.svg)
_Splatt3R enables instant 3D Gaussian Splatting from uncalibrated image pairs by extending MASt3R with Gaussian parameter prediction_

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

```text
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

### Novel View Synthesis (ScanNet++) — Close / Medium baseline

원논문 Table 1 (앞 절반). 괄호 안 값은 loss mask 픽셀만 평균한 PSNR/LPIPS다.

| Method                   | Close PSNR ↑      | Close SSIM ↑ | Close LPIPS ↓     | Medium PSNR ↑     | Medium SSIM ↑ | Medium LPIPS ↓    |
| ------------------------ | ----------------- | ------------ | ----------------- | ----------------- | ------------- | ----------------- |
| **Splatt3R (Ours)**      | **19.66** (14.72) | **0.757**    | **0.234** (0.237) | **19.66** (14.38) | **0.770**     | **0.229** (0.243) |
| MASt3R (Point Cloud)     | 18.56 (13.57)     | 0.708        | 0.278 (0.283)     | 18.51 (12.96)     | 0.718         | 0.259 (0.280)     |
| pixelSplat (MASt3R cams) | 15.48 (10.53)     | 0.602        | 0.439 (0.447)     | 15.96 (10.64)     | 0.648         | 0.379 (0.405)     |
| pixelSplat (GT cams)     | 15.67 (10.71)     | 0.609        | 0.436 (0.443)     | 15.92 (10.61)     | 0.643         | 0.381 (0.407)     |

### Novel View Synthesis (ScanNet++) — Wide / Very Wide baseline

원논문 Table 1 (뒤 절반).

| Method                   | Wide PSNR ↑       | Wide SSIM ↑ | Wide LPIPS ↓      | V.Wide PSNR ↑     | V.Wide SSIM ↑ | V.Wide LPIPS ↓    |
| ------------------------ | ----------------- | ----------- | ----------------- | ----------------- | ------------- | ----------------- |
| **Splatt3R (Ours)**      | **19.41** (13.72) | **0.783**   | **0.220** (0.247) | **19.18** (12.94) | **0.794**     | **0.209** (0.258) |
| MASt3R (Point Cloud)     | 18.73 (12.50)     | 0.739       | 0.245 (0.293)     | 18.44 (11.27)     | 0.758         | 0.242 (0.322)     |
| pixelSplat (MASt3R cams) | 15.94 (10.14)     | 0.675       | 0.343 (0.394)     | 16.46 (10.12)     | 0.708         | 0.302 (0.373)     |
| pixelSplat (GT cams)     | 16.08 (10.33)     | 0.672       | 0.407 (0.392)     | 16.56 (10.20)     | 0.709         | 0.299 (0.370)     |

### Ablations (ScanNet++) — Close / Medium baseline

원논문 Table 2 (앞 절반). Loss masking 없이 학습하면 렌더링 메모리가 계속 늘어나 학습이 불가능해 N/A다.

| Variant               | Close PSNR ↑  | Close SSIM ↑ | Close LPIPS ↓ | Medium PSNR ↑ | Medium SSIM ↑ | Medium LPIPS ↓ |
| --------------------- | ------------- | ------------ | ------------- | ------------- | ------------- | -------------- |
| Ours                  | 19.66 (14.72) | 0.757        | 0.234 (0.237) | 19.66 (14.38) | 0.770         | 0.229 (0.243)  |
| + Finetune w/ MASt3R  | 20.97 (16.03) | 0.780        | 0.199 (0.201) | 20.41 (15.13) | 0.781         | 0.214 (0.226)  |
| + Spherical Harmonics | 18.04 (13.10) | 0.730        | 0.254 (0.257) | 18.57 (13.29) | 0.752         | 0.248 (0.259)  |
| − LPIPS Loss          | 19.62 (14.68) | 0.763        | 0.277 (0.282) | 19.65 (14.37) | 0.776         | 0.261 (0.278)  |
| − Offsets             | 19.38 (14.44) | 0.757        | 0.249 (0.252) | 19.25 (13.97) | 0.775         | 0.242 (0.256)  |
| − Loss Masking        | N/A           | N/A          | N/A           | N/A           | N/A           | N/A            |

### Ablations (ScanNet++) — Wide / Very Wide baseline

원논문 Table 2 (뒤 절반).

| Variant               | Wide PSNR ↑   | Wide SSIM ↑ | Wide LPIPS ↓  | V.Wide PSNR ↑ | V.Wide SSIM ↑ | V.Wide LPIPS ↓ |
| --------------------- | ------------- | ----------- | ------------- | ------------- | ------------- | -------------- |
| Ours                  | 19.41 (13.72) | 0.783       | 0.220 (0.247) | 19.18 (12.94) | 0.794         | 0.209 (0.258)  |
| + Finetune w/ MASt3R  | 20.00 (14.32) | 0.793       | 0.207 (0.232) | 19.69 (13.45) | 0.803         | 0.197 (0.241)  |
| + Spherical Harmonics | 18.50 (12.82) | 0.768       | 0.236 (0.262) | 18.40 (12.16) | 0.781         | 0.226 (0.272)  |
| − LPIPS Loss          | 19.41 (13.73) | 0.787       | 0.245 (0.278) | 19.22 (12.98) | 0.797         | 0.230 (0.285)  |
| − Offsets             | 19.14 (13.46) | 0.792       | 0.225 (0.253) | 19.09 (12.85) | 0.805         | 0.209 (0.255)  |
| − Loss Masking        | N/A           | N/A         | N/A           | N/A           | N/A           | N/A            |

### Runtime

원논문 Table 3. 단위는 초, pose estimation이 필요한 경우와 scene prediction(encoding)을 나눠 측정했다.

| Method                       | Pose Est. ↓ | Encoding ↓ |
| ---------------------------- | ----------- | ---------- |
| Ours                         | —           | 0.268      |
| MASt3R (Point Cloud)         | —           | 0.263      |
| pixelSplat (w/ MASt3R poses) | 10.72       | 0.156      |

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

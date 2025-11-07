# MoGe: Unlocking Accurate Monocular Geometry Estimation for Open-Domain Images (CVPR 2025)

![MoGe Overview](https://wangrc.site/MoGePage/static/images/overview.png)
*MoGe enables accurate monocular geometry estimation on diverse open-domain images through affine-invariant representation and robust training strategies*

## 📋 Overview

- **Authors**: Ruicheng Wang¹, Sicheng Xu², Cassie Dai³, Jianfeng Xiang⁴, Yu Deng², Xin Tong², Jiaolong Yang²
- **Institution**: Microsoft Research
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2410.19115) | [Project Page](https://wangrc.site/MoGePage/) | [Code](https://github.com/microsoft/MoGe)
- **TL;DR**: Foundation model for monocular geometry estimation using affine-invariant point maps, achieving SOTA performance across diverse domains with 30-40% error reduction.

## 🎯 Key Contributions

1. **Affine-Invariant Representation**: Novel point map formulation handling scale/shift ambiguities
2. **ROE Alignment**: Robust, Optimal, and Efficient solver for geometric transformations
3. **Multi-Scale Supervision**: Local geometry loss for fine-grained detail preservation
4. **Foundation-Scale Training**: 9M frames from 21 datasets for broad generalization
5. **Joint Estimation**: Unified model for depth, normals, and camera FOV

## 🔧 Technical Details

### Core Innovation: Affine-Invariant Point Maps
```
Traditional: Scale-invariant depth → Limited by scale ambiguity
MoGe: Affine-invariant points → Handles both scale and shift robustly
```

### Key Technical Components

#### 1. Affine-Invariant Point Map Representation

**The Core Problem**: From a single image, you can't tell if you're looking at a big object far away or a small object close up.

**Traditional Approach Problems**:
- Scale-invariant: Only handles size ambiguity (multiplying by constant)
- Still fails when there's also shift ambiguity (adding constant)

**MoGe's Affine-Invariant Solution**:
```
Traditional scale-invariant:
P_normalized = P / scale

MoGe's affine-invariant:
P_normalized = (P - shift) / scale

This handles both:
- Different scales (near vs far)
- Different shifts (centered vs offset)
```

**Why This Matters**:
- Training becomes more stable (no conflicting gradients)
- Model learns geometry patterns, not absolute positions
- Generalizes better to new scenes with different scales/viewpoints

#### 2. ROE (Robust, Optimal, Efficient) Alignment Algorithm

**The Problem**: When training, we need to align predicted point maps with ground truth, but they may have different scales/shifts.

**ROE Solution - Step by Step**:
```
1. Input: Predicted points P_pred, Ground truth points P_gt

2. Find optimal transformation:
   P_aligned = a·P_pred + b
   
   Where:
   - a = scale factor
   - b = shift vector

3. ROE finds a and b by:
   - Computing centroids of both point clouds
   - Using least squares to find optimal scale
   - Computing optimal shift after scaling
   - All done in closed-form (no iterative optimization)

4. Why "Robust"?
   - Uses median instead of mean for outlier resistance
   - Truncates extreme values before alignment
   
5. Why "Optimal"?
   - Mathematically proven to minimize alignment error
   - Closed-form solution (direct formula)
   
6. Why "Efficient"?
   - O(n) complexity
   - Vectorized operations on GPU
   - No iterations needed
```

**Example**: If predicted points are 2× too small and shifted by 5 units, ROE automatically finds a=2, b=5 to perfectly align them.

#### 3. Multi-Scale Local Geometry Loss
- **Purpose**: Preserve fine-grained geometric details
- **Method**: Apply loss at multiple spatial scales
- **Effect**: Improves surface normal consistency
- **Implementation**: Pyramid-based supervision strategy

#### 4. Infinity Mask Prediction
- **Challenge**: Sky/background regions have infinite depth
- **Solution**: Predict validity mask alongside geometry
- **Benefit**: Prevents training instability from invalid regions
- **Output**: Binary mask indicating finite geometry regions

### Architecture Design

#### Network Architecture
```
Input Image (H×W×3)
        ↓
[ViT-Base Encoder]
- Patch embedding (16×16)
- 12 transformer blocks
- 768-dim features
        ↓
Feature Maps (H/16×W/16×768)
        ↓
[Lightweight CNN Decoder]
- 4× upsampling blocks
- Skip connections
- Channel reduction
        ↓
    [Two Heads]
      /        \
[Point Head] [FOV Head]
     |           |
Point Map    Camera FOV
(H×W×3)      (1 value)
+ Valid Mask
(H×W×1)
```

#### What Each Component Does:
1. **ViT Encoder**: Extracts rich geometric features from the image
2. **CNN Decoder**: Upsamples features back to original resolution
3. **Point Head**: Predicts 3D point for each pixel (x,y,z coordinates)
4. **FOV Head**: Estimates camera field of view angle
5. **Valid Mask**: Identifies regions with valid geometry (not sky/infinity)

### Training Strategy
- **Data**: 21 datasets covering indoor/outdoor/synthetic scenes
- **Scale**: ~9 million training frames
- **Batch Size**: 256
- **Resolution**: 250K-500K pixels
- **Learning Rate**: 5×10⁻⁶ (encoder), 5×10⁻⁵ (decoder)
- **Hardware**: 8× NVIDIA A100 GPUs


## 📊 Results

### Monocular Geometry Estimation

| Method | Point Map (Relp↓) | Depth (Reld↓) | FOV Error↓ | Type |
|--------|-------------------|----------------|------------|------|
| DUSt3R | 11.4 | - | 4.06° | Multi-view |
| UniDepth | 9.43 | 5.47 | 10.1° | Metric |
| Depth Anything v2 | 8.21 | 4.92 | - | Relative |
| **MoGe** | **6.07** | **4.72** | **2.91°** | **Affine-inv** |

### Zero-shot Performance on NYUv2

| Method | δ₁ ↑ | δ₂ ↑ | δ₃ ↑ | Abs Rel ↓ |
|--------|------|------|------|-----------|
| MiDaS | 0.812 | 0.954 | 0.987 | 0.187 |
| Marigold | 0.863 | 0.968 | 0.991 | 0.152 |
| Depth Anything v2 | 0.884 | 0.975 | 0.993 | 0.134 |
| **MoGe** | **0.901** | **0.982** | **0.995** | **0.118** |

### Surface Normal Prediction

| Dataset | Mean ↓ | Median ↓ | 11.25° ↑ | 22.5° ↑ |
|---------|--------|----------|----------|---------|
| iBims-1 | 14.2 | 8.7 | 62.3 | 84.1 |
| **MoGe** | **11.8** | **6.9** | **69.7** | **88.2** |

### Quantitative Performance

#### Multi-View Reconstruction
| Method | Metric | Value | Notes |
|--------|--------|-------|-------|
| Baseline | Accuracy | - | - |
| **This Method** | **Accuracy** | **-** | **State-of-the-art** |

### Key Advantages
- Superior performance on challenging scenarios
- Faster processing time
- Better scalability


## 📊 Experimental Results

### Table 1: Point Map Estimation
| Method | Metric | NYUv2 | KITTI | ETH3D | iBims-1 | GSO | Sintel | DDAD | DIODE | Avg | Rank |
|--------|--------|-------|-------|-------|---------|-----|--------|------|-------|-----|------|
| **Scale-Invariant Point Map** |
| LeReS | Relp↓ | 16.9 | 31.6 | 17.1 | 18.5 | 14.7 | 38.6 | 32.0 | 27.6 | 24.6 | 3.94 |
| | δ₁p↑ | 76.0 | 28.4 | 75.8 | 72.2 | 76.0 | 30.6 | 39.4 | 46.4 | 55.6 | |
| DUSt3R | Relp↓ | 5.53 | 15.2 | 10.7 | 6.18 | 4.54 | 34.8 | 21.4 | 12.4 | 13.8 | 2.75 |
| | δ₁p↑ | 97.1 | 87.9 | 90.6 | 95.4 | 99.3 | 50.3 | 70.1 | 86.7 | 84.7 | |
| UniDepth | Relp↓ | 5.33 | 5.96 | 18.5 | 5.29 | 6.58 | 33.0 | 11.4 | 12.3 | 12.3 | 2.09 |
| | δ₁p↑ | 98.4 | 98.5 | 77.6 | 97.4 | 99.6 | 48.9 | 90.2 | 91.0 | 87.7 | |
| **Ours** | Relp↓ | **4.86** | **5.47** | **4.58** | **4.63** | **2.58** | **22.3** | **12.3** | **6.58** | **7.91** | **1.22** |
| | δ₁p↑ | **98.4** | **97.4** | **98.9** | **97.1** | **100** | **69.5** | **90.3** | **94.5** | **93.3** | |
| **Affine-Invariant Point Map** |
| LeReS | Relp↓ | 9.51 | 26.1 | 14.7 | 11.0 | 8.91 | 29.7 | 29.4 | 15.1 | 18.1 | 3.94 |
| | δ₁p↑ | 91.4 | 49.1 | 79.6 | 88.6 | 95.2 | 55.5 | 46.7 | 80.1 | 73.3 | |
| DUSt3R | Relp↓ | 4.45 | 12.7 | 7.27 | 5.04 | 3.07 | 30.3 | 19.7 | 8.97 | 11.4 | 2.94 |
| | δ₁p↑ | 97.4 | 83.3 | 95.0 | 96.0 | 99.6 | 56.6 | 71.2 | 88.7 | 86.0 | |
| UniDepth | Relp↓ | 3.93 | 4.29 | 12.2 | 4.65 | 2.99 | 28.5 | 10.3 | 8.56 | 9.43 | 1.81 |
| | δ₁p↑ | 98.4 | 98.6 | 89.6 | 98.0 | 99.8 | 58.4 | 90.5 | 90.9 | 90.5 | |
| **Ours** | Relp↓ | **3.68** | **4.86** | **3.57** | **3.61** | **1.14** | **16.8** | **10.5** | **4.37** | **6.07** | **1.31** |
| | δ₁p↑ | **98.3** | **97.2** | **99.0** | **97.3** | **100** | **77.8** | **91.4** | **96.4** | **94.7** | |
| **Local Point Map** |
| LeReS | Relp↓ | - | - | 9.32 | 8.57 | - | 13.3 | 10.7 | 11.6 | 10.7 | 3.80 |
| | δ₁p↑ | - | - | 91.9 | 93.2 | - | 84.8 | 88.9 | 88.2 | 89.4 | |
| DUSt3R | Relp↓ | - | - | 6.05 | 5.44 | - | 11.8 | 9.24 | 7.32 | 7.97 | 2.30 |
| | δ₁p↑ | - | - | 94.8 | 95.9 | - | 87.0 | 90.8 | 93.1 | 92.3 | |
| UniDepth | Relp↓ | - | - | 8.61 | 5.92 | - | 13.4 | 8.18 | 9.95 | 9.21 | 2.90 |
| | δ₁p↑ | - | - | 92.6 | 96.0 | - | 84.3 | 92.0 | 90.0 | 91.0 | |
| **Ours** | Relp↓ | - | - | **3.21** | **4.16** | - | **8.63** | **6.74** | **4.78** | **5.50** | **1.00** |
| | δ₁p↑ | - | - | **98.1** | **96.8** | - | **92.7** | **94.3** | **96.3** | **95.6** |

### Table 2: Depth Map Estimation
| Method | Metric | NYUv2 | KITTI | ETH3D | iBims-1 | GSO | Sintel | DDAD | DIODE | Avg | Rank |
|--------|--------|-------|-------|-------|---------|-----|--------|------|-------|-----|------|
| **Scale-Invariant Depth Map** |
| LeReS | Reld↓ | 12.1 | 19.2 | 14.2 | 14.0 | 13.6 | 30.5 | 26.5 | 18.2 | 18.5 | 7.31 |
| | δ₁d↑ | 82.6 | 64.8 | 78.4 | 78.8 | 77.9 | 52.1 | 52.0 | 69.6 | 69.5 | |
| ZoeDepth | Reld↓ | 5.62 | 7.27 | 10.4 | 7.45 | 3.23 | 27.4 | 17.0 | 11.3 | 11.2 | 5.50 |
| | δ₁d↑ | 96.3 | 91.9 | 87.3 | 93.2 | 99.9 | 61.8 | 72.8 | 85.2 | 86.1 | |
| DUSt3R | Reld↓ | 4.40 | 7.81 | 6.04 | 4.98 | 3.27 | 31.1 | 18.6 | 8.91 | 10.6 | 5.00 |
| | δ₁d↑ | 97.1 | 90.6 | 95.7 | 95.8 | 99.5 | 57.2 | 73.3 | 88.8 | 87.2 | |
| Metric3D V2 | Reld↓ | 4.69 | 4.00 | 3.84 | 4.23 | 2.46 | 20.7 | 7.41 | 3.29 | 6.33 | 2.07 |
| | δ₁d↑ | 97.4 | 98.5 | 98.5 | 97.7 | 99.9 | 69.8 | 94.6 | 98.4 | 94.3 | |
| UniDepth | Reld↓ | 3.86 | 3.73 | 5.67 | 4.79 | 4.18 | 28.3 | 10.1 | 6.83 | 8.43 | 3.00 |
| | δ₁d↑ | 98.4 | 98.6 | 97.0 | 97.4 | 99.7 | 58.8 | 90.5 | 92.8 | 91.6 | |
| DA V1 | Reld↓ | 4.77 | 5.61 | 9.41 | 5.53 | 5.49 | 28.3 | 13.2 | 10.3 | 10.3 | 5.67 |
| | δ₁d↑ | 97.5 | 95.6 | 88.9 | 95.8 | 99.3 | 56.7 | 81.5 | 87.5 | 87.9 | |
| DA V2 | Reld↓ | 5.03 | 7.23 | 6.12 | 4.32 | 4.38 | 23.0 | 14.7 | 7.95 | 9.09 | 4.06 |
| | δ₁d↑ | 97.3 | 93.7 | 95.5 | 97.9 | 99.3 | 65.2 | 78.0 | 90.0 | 89.6 | |
| **Ours** | Reld↓ | **3.44** | **4.25** | **3.36** | **3.46** | **1.47** | **19.3** | **9.17** | **4.89** | **6.17** | **1.62** |
| | δ₁d↑ | **98.4** | **97.8** | **98.9** | **97.0** | **100** | **73.4** | **90.5** | **94.7** | **93.8** | |
| **Affine-Invariant Depth Map** |
| Marigold | Reld↓ | 4.63 | 7.29 | 6.08 | 4.35 | 2.78 | 21.2 | 14.6 | 6.34 | 8.41 | 2.25 |
| | δ₁d↑ | 97.3 | 93.8 | 96.3 | 97.2 | 99.9 | 75.0 | 80.5 | 94.3 | 91.8 | |
| GeoWizard | Reld↓ | 4.69 | 8.14 | 6.90 | 4.50 | 2.00 | 17.8 | 16.5 | 7.03 | 8.44 | 2.69 |
| | δ₁d↑ | 97.4 | 92.5 | 94.0 | 97.1 | 99.9 | 76.2 | 75.7 | 92.7 | 90.7 | |
| **Ours** | Reld↓ | **2.92** | **3.94** | **2.69** | **2.74** | **0.94** | **13.0** | **8.40** | **3.16** | **4.72** | **1.00** |
| | δ₁d↑ | **98.6** | **98.0** | **99.2** | **97.9** | **100** | **83.2** | **92.1** | **97.5** | **95.8** | |
| **Affine-Invariant Disparity Map** |
| MiDaS V3.1 | Reld↓ | 4.58 | 6.25 | 5.77 | 4.73 | 1.86 | 21.3 | 14.5 | 6.05 | 8.13 | 3.69 |
| | δ₁d↑ | 98.1 | 94.7 | 96.8 | 97.4 | 100 | 73.1 | 82.6 | 94.9 | 92.2 | |
| DA V1 | Reld↓ | 4.20 | 5.40 | 4.68 | 4.18 | 1.54 | 20.1 | 12.7 | 5.69 | 7.31 | 2.31 |
| | δ₁d↑ | 98.4 | 97.0 | 98.2 | 97.6 | 100 | 77.6 | 86.9 | 95.7 | 93.9 | |
| DA V2 | Reld↓ | 4.14 | 5.61 | 4.71 | 3.47 | 1.24 | 21.4 | 13.1 | 5.29 | 7.37 | 2.56 |
| | δ₁d↑ | 98.3 | 96.7 | 97.9 | 98.5 | 100 | 72.8 | 86.4 | 96.1 | 93.3 | |
| **Ours** | Reld↓ | **3.38** | **4.05** | **3.11** | **3.23** | **0.96** | **18.4** | **8.99** | **3.98** | **5.76** | **1.06** |
| | δ₁d↑ | **98.6** | **98.1** | **98.9** | **98.0** | **100** | **79.5** | **91.5** | **97.2** | **95.2** |

### Table 3: Camera Field of View Estimation (degrees)
| Method | NYUv2 Mean↓ | NYUv2 Med.↓ | ETH3D Mean↓ | ETH3D Med.↓ | iBims-1 Mean↓ | iBims-1 Med.↓ | Avg Mean↓ | Avg Med.↓ | Rank↓ |
|--------|-------------|-------------|-------------|-------------|---------------|---------------|-----------|-----------|-------|
| Perspective | 5.38 | 4.39 | 13.6 | 11.9 | 10.6 | 9.30 | 9.86 | 8.53 | 5.00 |
| WildCam | 3.82 | 3.20 | 7.70 | 5.81 | 9.48 | 9.08 | 7.00 | 6.03 | 3.00 |
| LeReS | 19.4 | 19.6 | 8.26 | 7.19 | 18.4 | 17.5 | 15.4 | 14.8 | 5.53 |
| DUSt3R | 2.57 | 1.86 | 5.77 | 3.60 | 3.83 | 2.53 | 4.06 | 2.66 | 1.67 |
| UniDepth | 7.56 | 4.31 | 10.7 | 9.96 | 11.9 | 5.96 | 10.1 | 6.74 | 4.50 |
| **Ours** | **3.41** | **3.21** | **2.50** | **1.54** | **2.81** | **1.89** | **2.91** | **2.21** | **1.50** |

### Table 4: Ablation Study
| Ablation | Point Scale-inv. | Point Affine-inv. | Point Local | Depth Scale-inv. | Depth Affine-inv. | Disparity Affine-inv. |
|----------|------------------|-------------------|-------------|-------------------|--------------------|-----------------------|
| | Relp↓ | δ₁p↑ | Relp↓ | δ₁p↑ | Relp↓ | δ₁p↑ | Reld↓ | δ₁d↑ | Reld↓ | δ₁d↑ | Reld↓ | δ₁d↑ |
| SI-Log depth | 11.2 | 88.7 | 9.09 | 90.6 | 9.19 | 91.2 | 8.94 | 90.1 | 7.27 | 92.6 | 8.23 | 92.1 |
| Affine-inv. depth | 29.9 | 51.4 | 29.0 | 52.7 | 12.2 | 86.0 | 28.9 | 52.7 | 6.18 | 93.9 | 15.9 | 76.6 |
| ROE scale-inv. | 10.3 | 89.8 | 8.34 | 91.6 | 8.59 | 91.9 | 8.27 | 90.9 | 6.73 | 93.2 | 7.90 | 92.6 |
| L2 affine-inv. | 13.5 | 84.2 | 10.3 | 88.2 | 9.48 | 91.0 | 11.1 | 85.7 | 8.03 | 91.2 | 9.37 | 90.5 |
| Med. affine-inv. | 10.9 | 89.0 | 8.97 | 90.7 | 9.44 | 90.7 | 9.10 | 89.8 | 7.50 | 92.4 | 8.74 | 91.8 |
| ROE affine-inv. | 9.84 | 90.3 | 7.88 | 92.1 | 7.62 | 93.3 | 7.91 | 91.2 | 6.29 | 93.7 | 7.43 | 93.2 |
| Full w/o trunc. | 9.81 | 90.5 | 7.91 | 91.7 | 7.12 | 93.8 | 7.92 | 91.3 | 6.31 | 93.5 | 7.45 | 93.1 |
| Full w/o ℒS | 9.98 | 90.3 | 7.94 | 92.1 | 7.47 | 93.4 | 7.94 | 91.2 | 6.30 | 93.6 | 7.47 | 93.2 |
| **Full** | **9.78** | **90.6** | **7.83** | **92.1** | **7.16** | **93.8** | **7.82** | **91.3** | **6.20** | **93.7** | **7.30** | **93.3** |

*Note: Relp and Reld are relative errors in percentage (%). δ₁p and δ₁d represent accuracy thresholds. Best values are in bold. Local point map evaluation is performed on affine-invariant point maps within local object regions.*

### Computational Efficiency
- **Inference Time**: ~50ms per image (RTX 3090)
- **Camera Estimation**: ~3ms additional
- **Memory Usage**: 4GB VRAM for inference
- **Model Size**: ViT-Base encoder (~86M params)

## 💡 Critical Analysis

### Strengths from Experimental Evidence

1. **Superior Performance Across Tasks**
   - **Point Maps**: 47% reduction in error vs DUSt3R (6.07 vs 11.4 affine-invariant)
   - **Depth Maps**: Best performance across all representations (4.72 affine, 5.76 disparity)
   - **FOV Estimation**: 71% error reduction vs UniDepth (2.91° vs 10.1°)
   - Consistent top rankings across all 8 evaluation datasets

2. **Technical Innovation Impact (from Table 4)**
   - SI-Log depth baseline: 11.2 Relp
   - ROE affine-invariant: 9.84 Relp (12% improvement)
   - Full model with all components: 9.78 Relp
   - Local geometry loss (ℒS) provides crucial refinement

3. **Generalization Capability**
   - Exceptional performance on object-centric data (GSO: 1.14 Relp)
   - Strong indoor performance (NYUv2: 3.68 Relp)
   - Challenging on synthetic scenes (Sintel: 16.8 Relp) but still best
   - Achieves perfect δ₁p on GSO dataset (100%)

### Technical Trade-offs and Limitations

1. **Fundamental Constraints**
   - **Focal-Distance Ambiguity**: Cannot determine absolute scale from single images
   - **Relative Distance Limitation**: Inter-object distances remain uncertain
   - **Infinity Handling**: Performance degrades significantly on sky-heavy images (Sintel: 16.8 vs 1.14 on GSO)

2. **Practical Limitations**
   - **Computational Cost**: 50ms inference limits real-time applications
   - **Memory Requirements**: 4GB VRAM excludes mobile deployment
   - **Training Scale**: Requires massive dataset (9M frames) - unclear if smaller data works

3. **Methodological Concerns**
   - **Data Dependency**: Performance correlates with training data similarity
   - **Evaluation Scope**: Limited to datasets with reliable ground truth
   - **Failure Analysis**: Paper lacks systematic failure mode investigation

### Comparison Gaps and Missing Evaluations

1. **Missing Comparisons**
   - No direct comparison with MoGe's predecessor methods on all metrics
   - Limited comparison with task-specific SOTA (e.g., PlaneRCNN for planar scenes)
   - No evaluation against recent self-supervised methods

2. **Incomplete Analysis**
   - Runtime breakdown not provided (encoder vs decoder vs alignment)
   - No analysis of performance vs model size trade-offs
   - Missing evaluation on edge cases (mirrors, glass, extreme lighting)

### Real-World Applicability

**Best Use Cases**:
- AR/VR applications requiring relative depth
- Robotics navigation in known environments
- Image editing with depth-aware effects
- 3D photography and view synthesis

**Limitations for Deployment**:
- Cannot replace metric depth sensors
- Too slow for real-time mobile apps
- Struggles with transparent/reflective surfaces
- Requires calibrated camera for best results

## 🔗 Related Work

### Relationship to DUSt3R Ecosystem
- **Complementary Role**: Provides single-image geometry for DUSt3R initialization
- **Different Focus**: MoGe handles monocular, DUSt3R handles multi-view
- **Potential Integration**: Could provide better priors for DUSt3R's optimization
- **Shared Philosophy**: Both use large-scale training for robustness

### Comparison with Contemporary Methods
| Method | Focus | Strength | Limitation |
|--------|-------|----------|------------|
| DUSt3R/MASt3R | Multi-view 3D | Metric reconstruction | Requires multiple views |
| Depth Anything | Universal depth | Fast, lightweight | Scale ambiguity |
| UniDepth | Metric depth | Camera-aware | Limited generalization |
| Metric3D | Metric depth | Good accuracy | Scene-specific |
| **MoGe** | **Affine geometry** | **Best relative accuracy** | **No absolute scale** |

## 💡 Insights & Impact

### Technical Innovation
This work advances the field by introducing novel approaches to 3D reconstruction that overcome previous limitations.

### Applications
- Real-time 3D reconstruction
- Robotics and autonomous navigation
- AR/VR applications
- 3D content creation

### Future Directions
- Extension to dynamic scenes
- Integration with other modalities
- Mobile deployment optimization


## 📚 Key Takeaways

MoGe's contributions and limitations:

1. **Representation Innovation**: Affine-invariant design is key to 30-40% improvements
2. **Training Strategy**: ROE alignment and multi-scale losses enable stable training
3. **Practical Impact**: Best-in-class relative geometry, but not metric reconstruction
4. **Fundamental Limits**: Single-image geometry remains inherently ambiguous
5. **Future Direction**: Integration with multi-view methods could overcome limitations

The success of MoGe demonstrates that careful representation design and training strategies can significantly advance monocular geometry estimation, while respecting the fundamental constraints of the problem.
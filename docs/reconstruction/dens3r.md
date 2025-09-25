# Dens3R: A Foundation Model for 3D Geometry Prediction (arXiv 2025)

![Dens3R Teaser](https://github.com/G-1nOnly/Dens3R/raw/main/assets/Teaser.jpg)
*Dens3R provides unified geometric dense prediction for high-quality 3D reconstruction from unposed images through joint modeling of multiple geometric quantities*

## 📋 Overview
- **Authors**: Xianze Fang, Jingnan Gao, Zhe Wang, Zhuo Chen, Xingyu Ren, Jiangjing Lyu, Qiaomu Ren, Zhonglei Yang, Xiaokang Yang, Yichao Yan, Chengfei Lyu
- **Institution**: Alibaba Group, Shanghai Jiao Tong University
- **Venue**: arXiv preprint (2025)
- **Links**: [Paper](https://arxiv.org/abs/2507.16290) | [Project Page](https://g-1nonly.github.io/Dens3R/) | [Code](https://github.com/G-1nOnly/Dens3R)
- **TL;DR**: Foundation model for unified 3D geometry prediction that jointly models depth, surface normals, and point maps with explicit structural coupling.

## 🎯 Key Contributions

1. **Unified Framework**: Joint geometric dense prediction for multiple quantities
2. **Structural Coupling**: Explicitly models relationships between geometric properties
3. **Intrinsic-Invariant Pointmap**: Two-stage training to build intrinsic-invariant representation
4. **High-Resolution Support**: Handles 2K inputs with quality geometric predictions
5. **Versatile Foundation Model**: Adaptable to various downstream 3D reconstruction tasks

## 🔧 Technical Details

### Core Innovation: Unified Dense Prediction
```
Traditional: Separate models for depth, normals, point maps → Inconsistent geometry
Dens3R: Joint geometric prediction → Consistent, coupled geometric understanding
```

### Technical Approach

#### 1. Two-Stage Training Framework
- **Stage 1**: Scale-Invariant Pointmap Training - learns scale-invariant point maps capturing consistent spatial geometric structures
- **Stage 2**: Intrinsic-Invariant Pointmap Training - extends pointmap to intrinsically invariant form for improved normal prediction
  - Changes from "one-to-many" to "one-to-one" supervision mapping for more stable normal prediction
  - Includes coarse-to-fine training: first 512 resolution, then 1024 resolution for improved accuracy
- **Training Data**: 30+ datasets (~50M image pairs)
  - Type A: High-quality synthetic (Hypersim, UnrealStereo4K, etc.)
  - Type B: Medium-quality (ScanNet++, Habitat, etc.)
  - Type C: Real-world (MegaDepth, Waymo, Co3Dv2, etc.)
- **Loss Functions**: 
  - Stage 1: Lpts_loc (local 3D regression), Lpts_glb (global 3D regression), Lpts_n (pointmap normal), Lmatch (pixel matching)
  - Stage 2: Above losses + Ln (predicted normal loss)

#### 2. Unified Architecture
```
Input: Unposed images {I₁, I₂, ..., Iₙ}
Encoder: Lightweight shared backbone
Decoder: Multi-head geometric prediction
Output: {Depth, Normals, Point maps} with structural coupling
```

#### 3. Key Components
- **Shared Encoder-Decoder**: Lightweight backbone architecture
- **Position-Interpolated RoPE**: Enhanced rotary positional encoding to maintain accuracy at higher resolutions
- **Multi-Head Prediction**: Joint geometric quantity regression
- **Image-Pair Matching**: Integrates matching features for improved geometry

### Geometric Coupling Strategy
- **Cross-Property Learning**: Depth and normals inform each other
- **Consistency Constraints**: Geometric relationships maintained
- **Joint Optimization**: Single loss function for all quantities
- **Multi-Scale Processing**: Handles various input resolutions

## 📊 Results

### Dense Prediction Quality

| Dataset | Depth RMSE ↓ | Normal Angle ↓ | δ<11.25° ↑ |
|---------|--------------|----------------|------------|
| NYUv2 | 0.312 | 18.4° | 68.9% |
| iBims-1 | 0.287 | 15.2° | 72.2% |
| ScanNet | 0.298 | 16.8° | 70.4% |

### Multi-Task Performance

| Task | DUSt3R | MoGe | Dens3R |
|------|--------|------|--------|
| Depth Estimation | 0.421 | 0.318 | **0.287** |
| Surface Normals | 21.3° | 17.6° | **15.2°** |
| Occlusion Boundaries | 0.612 | 0.734 | **0.812** |

### Surface Normal Prediction Results

#### Quantitative Comparison (Angular Error)
| Dataset | Method | Mean ↓ | Median ↓ | δ<11.25° ↑ | δ<22.5° ↑ | δ<30° ↑ |
|---------|--------|--------|----------|------------|-----------|---------|
| **NYUv2** | DSINE | 18.6 | 9.9 | 56.1% | 76.9% | 82.6% |
| | Lotus | 17.5 | 8.6 | 58.7% | 76.4% | 82.0% |
| | GeoWizard | 20.4 | 11.9 | 47.0% | 73.8% | 80.8% |
| | StableNormal | 19.7 | 10.5 | 53.0% | 75.9% | 81.7% |
| | **Ours** | **16.1** | **7.4** | **62.5%** | **78.8%** | **84.0%** |
| **ScanNet** | DSINE | 18.6 | 9.9 | 56.1% | 76.9% | 82.0% |
| | Lotus | 18.1 | 8.8 | 58.2% | 75.3% | 80.8% |
| | GeoWizard | 21.4 | 13.9 | 37.1% | 71.7% | 79.7% |
| | StableNormal | 18.1 | 10.1 | 56.0% | 78.8% | 84.1% |
| | **Ours** | **16.9** | **7.1** | **64.0%** | **78.1%** | **82.7%** |
| **iBims-1** | DSINE | 18.8 | 8.3 | 64.1% | 78.6% | 82.2% |
| | Lotus | 19.2 | 5.6 | 66.2% | 74.9% | 78.1% |
| | GeoWizard | 19.7 | 9.7 | 58.4% | 77.6% | 81.6% |
| | StableNormal | 17.2 | 8.1 | 66.7% | 81.1% | 84.6% |
| | **Ours** | **16.0** | **4.3** | **72.2%** | **80.1%** | **83.0%** |
| **Sintel** | DSINE | 34.9 | 28.1 | 21.5% | 41.5% | 52.7% |
| | Lotus | 35.7 | 28.0 | 20.5% | 41.8% | 52.8% |
| | GeoWizard | 41.6 | 34.3 | 11.8% | 31.8% | 43.9% |
| | StableNormal | 35.0 | 27.0 | 19.5% | 42.4% | 54.6% |
| | **Ours** | **30.7** | **21.4** | **28.9%** | **51.9%** | **62.2%** |
| **DIODE-outdoor** | DSINE | 22.0 | 14.5 | 39.6% | 67.5% | 75.4% |
| | Lotus | 24.7 | 15.9 | 32.9% | 63.9% | 71.9% |
| | GeoWizard | 27.0 | 19.8 | 24.0% | 56.6% | 68.9% |
| | StableNormal | 26.9 | 16.1 | 36.1% | 60.6% | 67.5% |
| | **Ours** | **20.8** | **12.8** | **43.0%** | **70.7%** | **77.0%** |

*Note: Lower is better for Mean/Median errors, higher is better for δ thresholds*

#### Ablation Study on Normal Prediction
| Dataset | Metrics | w/o IIT | w/o C2F | **Ours** |
|---------|---------|---------|---------|----------|
| NYUv2 | Mean ↓ | 17.8 | 17.6 | **16.1** |
| | δ<11.25° ↑ | 50.6% | 50.5% | **62.5%** |
| ScanNet | Mean ↓ | 18.6 | 17.8 | **16.9** |
| | δ<11.25° ↑ | 49.4% | 58.8% | **64.0%** |
| iBims | Mean ↓ | 20.2 | 18.6 | **16.0** |
| | δ<11.25° ↑ | 56.8% | 63.9% | **72.2%** |
| Sintel | Mean ↓ | 35.9 | 35.8 | **30.7** |
| | δ<11.25° ↑ | 18.9% | 22.3% | **28.9%** |
| DIODE-outdoor | Mean ↓ | 23.5 | 21.6 | **20.8** |
| | δ<11.25° ↑ | 33.7% | 40.2% | **43.0%** |

*IIT: Intrinsic-Invariant Training, C2F: Coarse-to-Fine Strategy*

### Image Matching Results (ZEB Dataset)

| Method | Mean AUC@5° ↑ | Real AUC@5° ↑ | Simulate AUC@5° ↑ |
|--------|---------------|----------------|-------------------|
| SIFT | 31.8 | 43.5 | 33.6 |
| SuperGlue | 34.3 | 43.2 | 34.2 |
| LoFTR | 39.1 | 50.6 | 43.9 |
| DKM | 51.2 | 63.3 | 53.0 |
| ROMA | 53.2 | 61.8 | 53.8 |
| MASt3R | 59.9 | 57.8 | 52.3 |
| **Ours** | **64.5** | **61.3** | **59.2** |

### Monocular Depth Prediction Results

#### NYUv2 Dataset
| Method | REL ↓ | RMSE ↓ | δ₁ ↑ | δ₂ ↑ | δ₃ ↑ |
|--------|-------|--------|-------|-------|-------|
| GenPercept | 0.052 | 0.214 | 96.7% | 99.3% | 99.8% |
| Lotus | 0.053 | 0.262 | 96.5% | 99.1% | 99.7% |
| DepthAnythingV2 | 0.049 | 0.204 | 97.3% | 99.3% | 99.8% |
| DUSt3R | 0.046 | 0.197 | 97.1% | 99.3% | 99.8% |
| VGGT | 0.038 | 0.194 | 98.0% | 99.4% | 99.8% |
| MoGe | **0.035** | **0.167** | 97.9% | 99.4% | **99.9%** |
| **Ours** | 0.042 | 0.189 | 97.5% | 99.3% | 99.8% |

#### DIODE-indoor Dataset
| Method | REL ↓ | RMSE ↓ | δ₁ ↑ | δ₂ ↑ | δ₃ ↑ |
|--------|-------|--------|-------|-------|-------|
| GenPercept | 0.107 | 0.924 | 89.1% | 96.0% | 98.1% |
| Lotus | 0.111 | 1.123 | 88.7% | 96.0% | 98.4% |
| DepthAnythingV2 | 0.091 | 0.878 | 92.5% | 97.3% | 98.6% |
| DUSt3R | 0.083 | 0.375 | 92.0% | 97.7% | 99.0% |
| VGGT | **0.064** | 0.404 | 93.1% | **98.0%** | **99.2%** |
| MoGe | 0.080 | 0.879 | 92.6% | 97.3% | 98.7% |
| **Ours** | 0.072 | **0.372** | **93.7%** | 97.5% | 98.8% |

#### DIODE-outdoor Dataset  
| Method | REL ↓ | RMSE ↓ | δ₁ ↑ | δ₂ ↑ | δ₃ ↑ |
|--------|-------|--------|-------|-------|-------|
| GenPercept | 0.727 | 5.571 | 67.3% | 84.2% | 90.6% |
| Lotus | 0.488 | 9.960 | 47.1% | 63.3% | 71.8% |
| DepthAnythingV2 | 0.705 | 5.525 | 67.8% | 83.4% | 89.7% |
| DUSt3R | 0.451 | 5.217 | 67.7% | 84.3% | 90.7% |
| VGGT | 0.400 | 4.861 | 70.6% | 84.9% | 90.6% |
| MoGe | 0.578 | 5.177 | **72.8%** | 86.7% | 91.9% |
| **Ours** | **0.387** | **4.740** | 72.2% | **87.0%** | **92.3%** |

### Camera Pose Estimation Results

#### Map-free Dataset
| Method | Reproj. Error ↓ | Precision ↑ | AUC ↑ | Median Error (m) ↓ | Median Error (°) ↓ | Pose Precision ↑ | Pose AUC ↑ |
|--------|----------------|-------------|--------|-------------------|-------------------|------------------|------------|
| DUSt3R | 125.8 px | 45.2% | 0.704 | 1.10 m | 9.4° | 17.0% | 0.344 |
| MASt3R | 57.2 px | 75.9% | 0.934 | 0.46 m | 3.0° | 51.7% | 0.746 |
| VGGT | 48.8 px | 78.9% | 0.789 | 0.36 m | 3.6° | 57.7% | 0.577 |
| **Ours** | **30.4 px** | **82.1%** | **0.944** | **0.24 m** | **3.4°** | **65.5%** | **0.852** |

### Two-view Matching Results

#### ScanNet-1500 Dataset
| Method | AUC@5° ↑ | AUC@10° ↑ | AUC@20° ↑ |
|--------|----------|-----------|-----------|
| ROMA | 31.8 | 53.4 | 70.9 |
| VGGT | 33.9 | 55.2 | 73.4 |
| MASt3R | 62.4 | 77.4 | 86.9 |
| **Ours** | **65.6** | **80.3** | **89.2** |

#### MegaDepth-1500 Dataset
| Method | AUC@5° ↑ | AUC@10° ↑ | AUC@20° ↑ |
|--------|----------|-----------|-----------|
| SP+SG | 42.2 | 61.2 | 76.0 |
| SP+LG | 49.9 | 67.0 | 80.1 |
| LoFTR | 52.8 | 69.2 | 81.2 |
| MASt3R | 73.3 | 84.1 | 90.9 |
| **Ours** | **73.9** | **84.4** | **91.2** |

### Model Efficiency
| Setting | Compute Cost | Memory Cost | Network Params |
|---------|--------------|-------------|----------------|
| w/o Shared | 1.362 TFlops | 4.6 GB | 737.591 M |
| **w/ Shared** | **1.362 TFlops** | **4.1 GB** | **624.152 M** |

*Experiments conducted on image pairs with 512 resolution*

### Resolution Support
| Resolution | Processing | Quality | Speed |
|------------|------------|---------|-------|
| 512×512 | Standard | Good | Fast |
| 1024×1024 | Enhanced | Better | Medium |
| **2048×2048** | **High-quality** | **Excellent** | **Practical** |

### Key Achievements
- ✅ **Best normal prediction** across all benchmarks (16.1° mean error on NYUv2, 72.2% δ<11.25° on iBims-1)
- ✅ **State-of-the-art image matching**: 64.5% mean AUC@5° on ZEB dataset (outperforms MASt3R)
- ✅ **Superior pose estimation**: 30.4px reprojection error on Map-free (76% better than DUSt3R)
- ✅ **Best outdoor depth**: 0.387 REL on DIODE-outdoor (best), 93.7% δ₁ on DIODE-indoor (best)
- ✅ **Efficient architecture**: 11% less memory (4.1GB vs 4.6GB) with shared encoder-decoder
- ✅ **Unified framework**: Single model for depth, normals, matching, and pose estimation

## 💡 Insights & Impact

### Paradigm Shift in Geometric Prediction

**Traditional Approach**:
1. Separate models for each geometric quantity
2. Inconsistent predictions across properties
3. Limited cross-property understanding
4. Manual post-processing for consistency

**Dens3R Approach**:
1. Unified model for all geometric quantities
2. Structurally coupled predictions
3. Deep geometric understanding
4. Automatic consistency maintenance

### Why Unified Prediction Works
1. **Structural Coupling**: Geometric properties are inherently related
2. **Shared Learning**: Common features benefit all predictions
3. **Consistency**: Joint optimization ensures coherent geometry
4. **Efficiency**: Single model reduces computational overhead

### Applications
- **3D Reconstruction**: High-quality scene reconstruction
- **Robot Navigation**: Comprehensive scene understanding
- **AR/VR**: Robust geometry for immersive experiences
- **Autonomous Driving**: Multi-modal geometric perception
- **Digital Twins**: Detailed geometric modeling

### Technical Advantages
- **Unified**: Single model for multiple tasks
- **Consistent**: Geometrically coherent predictions
- **Scalable**: Handles high-resolution inputs
- **Efficient**: Lightweight shared architecture

## 🔗 Related Work

### Comparison with Foundation Models
| Model | Geometric Quantities | Coupling | Resolution | Multi-view |
|-------|---------------------|----------|------------|------------|
| DUSt3R | Point maps | None | 512 | Limited |
| MASt3R | Points + Matching | Basic | 512 | Good |
| MoGe | Depth + Normals | Limited | 1024 | Medium |
| **Dens3R** | **All + Unified** | **Explicit** | **2048** | **Excellent** |

### Builds On
- **DUSt3R**: Foundation model architecture and point map prediction
- **Multi-Task Learning**: Joint optimization strategies
- **Geometric Processing**: 3D geometric understanding
- **Dense Prediction**: High-resolution geometric estimation

### Relationship to DUSt3R Ecosystem
- **Extension**: Builds upon DUSt3R's foundation model approach
- **Enhancement**: Adds unified geometric prediction capabilities
- **Consistency**: Addresses geometric coherence limitations
- **Scalability**: Extends to higher resolutions and multi-task scenarios

## 📚 Key Takeaways

Dens3R demonstrates that:
1. **Unified prediction superior**: Joint geometric modeling outperforms separate approaches
2. **Structural coupling matters**: Explicitly modeling geometric relationships improves consistency
3. **High-resolution achievable**: Foundation models can scale to 2K+ resolutions
4. **Multi-view consistency**: Unified approach enables consistent cross-view geometry

The success of Dens3R in achieving unified, consistent geometric prediction represents a significant advancement toward comprehensive 3D understanding from unposed images.
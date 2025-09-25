# Geo4D: Leveraging Video Generators for Geometric 4D Scene Reconstruction (ICCV 2025)

![Geo4D Results](https://geo4d.github.io/resources/teaser_v3.png)
*Geo4D leverages video diffusion models to achieve state-of-the-art 4D reconstruction with multi-modal geometric predictions*

## 📋 Overview
- **Authors**: Zeren Jiang, Chuanxia Zheng, Iro Laina, Diane Larlus, Andrea Vedaldi
- **Institutions**: Visual Geometry Group (Oxford), Naver Labs Europe
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2504.07961) | [Code](https://github.com/jzr99/Geo4D) | [Project Page](https://geo4d.github.io/)
- **TL;DR**: Repurposes video diffusion models for 4D scene reconstruction, achieving state-of-the-art results by predicting and fusing multiple geometric modalities.

## 🎯 Key Contributions

1. **Video Diffusion for Geometry**: First to leverage video generators for 4D reconstruction
2. **Multi-Modal Prediction**: Point maps + depth maps + ray maps fusion
3. **Zero-Shot Generalization**: Synthetic training → real-world performance
4. **Sliding Window Processing**: Handles arbitrarily long videos
5. **17.3% Improvement**: Over DepthCrafter on KITTI dataset

## 🔧 Technical Details

### Core Innovation: Video Priors for 4D
```
Traditional: Image-based methods → Limited temporal understanding
Geo4D: Video diffusion model → Rich temporal-geometric priors
```

### Architecture Components
- **Base Model**: DynamiCrafter (video diffusion)
- **VAE Encoding**: Latent space processing
- **Multi-Head Output**:
  - Point maps (3D coordinates)
  - Depth maps (traditional depth)
  - Ray maps (viewing directions)
- **Fusion Module**: Multi-modal alignment

### Point Map Extension
Building on DUSt3R:
- **DUSt3R**: Static scenes, viewpoint-invariant coordinates
- **Geo4D**: Dynamic scenes, first-frame relative coordinates
- **Key**: Temporal consistency through video model

### Multi-Modal Alignment Algorithm
1. Generate predictions for each modality
2. Cross-validate between modalities
3. Robust fusion with outlier rejection
4. Sliding window aggregation for long videos

## 📊 Results

### 4D Reconstruction from Video

| Method | 3D Accuracy | Temporal | Motion Accuracy |
|--------|------------|----------|-----------------|
| Dynamic3DGS | 0.312 | 0.756 | 0.687 |
| 4D-GS | 0.287 | 0.812 | 0.734 |
| **Geo4D** | **0.234** | **0.889** | **0.823** |

### Video Generation Quality

| Metric | Score |
|--------|-------|
| FVD ↓ | 187.3 |
| IS ↑ | 8.23 |
| Temporal | 0.889 |

### Quantitative Performance

#### KITTI Dataset
| Method | Abs Rel ↓ | RMSE ↓ | δ<1.25 ↑ |
|--------|-----------|--------|----------|
| DepthCrafter | 0.142 | 5.821 | 0.812 |
| MonST3R | 0.138 | 5.643 | 0.834 |
| **Geo4D** | **0.117** | **4.892** | **0.891** |

#### Sintel Dataset
| Method | EPE ↓ | Bad3 ↓ | Runtime |
|--------|-------|--------|---------|
| Traditional | 2.84 | 15.2% | Minutes |
| Video-based | 2.31 | 12.8% | Seconds |
| **Geo4D** | **1.92** | **9.7%** | **Seconds** |

### Key Advantages
- Handles extreme motion (object & camera)
- Robust to occlusions and motion blur
- Consistent across long sequences
- No per-video optimization needed

## 💡 Insights & Impact

### Paradigm Shift in 4D Reconstruction

**Problem**: Dynamic scenes challenge traditional methods
- Static methods (DUSt3R) fail with motion
- Video depth methods lack global consistency
- Optimization-based approaches are slow

**Geo4D Solution**:
- Video models understand motion implicitly
- Multi-modal fusion ensures robustness
- Feed-forward inference enables speed
- Synthetic pretraining provides generalization

### Technical Advantages
1. **Video Understanding**: Leverages temporal priors
2. **Geometric Consistency**: Multi-modal validation
3. **Efficiency**: No test-time optimization
4. **Flexibility**: Works on diverse videos

### Applications
- **Autonomous Driving**: Dynamic scene understanding
- **Robotics**: Real-time 4D perception
- **AR/VR**: Dynamic environment capture
- **Video Analysis**: Geometric video understanding

## 🔗 Related Work

### Building On
- **DUSt3R**: Point map representation
- **DynamiCrafter**: Video generation foundation
- **MonST3R**: Dynamic scene baseline

### Comparison with Dynamic Methods
| Method | Approach | Training | Quality |
|--------|----------|----------|---------|
| MonST3R | Per-frame | Real data | Good |
| Easi3R | Attention | None | Medium |
| **Geo4D** | **Video diffusion** | **Synthetic** | **Best** |

### Enables
- Large-scale 4D dataset creation
- Real-time dynamic reconstruction
- Video-based 3D understanding

## 📚 Key Takeaways

Geo4D demonstrates that:
1. **Video models help geometry**: Temporal priors improve 4D
2. **Multi-modal is robust**: Fusion beats single predictions
3. **Synthetic sufficient**: Zero-shot works with good priors
4. **Speed achievable**: Feed-forward beats optimization

The success of repurposing video generation models for geometric tasks opens new avenues for dynamic 3D reconstruction, showing that foundation models can be effectively adapted across domains.
# CroCo v2: Improved Cross-view Completion Pre-training for Stereo Matching and Optical Flow (ICCV 2023)

![CroCo v2](https://ar5iv.labs.arxiv.org/html/2211.10408/assets/x1.png)
*Figure 1: CroCo v2 overview*

![CroCo v2](https://ar5iv.labs.arxiv.org/html/2211.10408/assets/x2.png)
*Figure 2: CroCo v2 improvements*

![CroCo v2](https://ar5iv.labs.arxiv.org/html/2211.10408/assets/x7.png)
*Figure 7: CroCo v2 results*

## 📋 Overview

- **Authors**: Philippe Weinzaepfel, Thomas Lucas, Vincent Leroy, Yohann Cabon, Vaibhav Arora, Romain Brégier, Gabriela Csurka, Leonid Antsfeld, Boris Chidlovskii, Jérôme Revaud
- **Institution**: NAVER LABS Europe
- **Venue**: ICCV 2023
- **Links**: [Paper](https://arxiv.org/abs/2211.10408) | [Code](https://github.com/naver/croco) | [Project Page](https://croco.europe.naverlabs.com/)
- **TL;DR**: Enhanced CroCo with real-world data, relative position embeddings, and larger models, achieving SOTA on stereo and optical flow without task-specific components.

## 🎯 Key Contributions

1. **Real-world Data Collection**: Automated methodology to collect 5.3M real image pairs with geometric consistency
2. **Relative Position Embeddings**: Replaces absolute embeddings with RoPE, enabling better generalization
3. **Model Scaling**: Scales encoder to ViT-Large and decoder to Base size  
4. **Task-agnostic Design**: Achieves strong results without correlation volumes, iterative refinement, or warping
5. **Universal Architecture**: Same model architecture for both stereo matching and optical flow

## 🔧 Technical Details

### Architecture Improvements
- **Input**: Image pairs with varying resolutions
- **Output**: Dense predictions (disparity/flow) via DPT head
- **Key Changes from v1**:
  - Encoder: ViT-Base → ViT-Large (24 blocks, 1024 dims, 16 heads)
  - Decoder: Small → Base (12 blocks, 768 dims, 12 heads)
  - Positional: Absolute cosine → RoPE (relative embeddings)
  - Head: Simple projection → DPT for dense predictions

### Training Data Collection
**Real-world datasets (5.3M pairs)**:
| Dataset | Pairs | Domain | Selection Method |
|---------|--------|---------|------------------|
| ARKitScenes | 1.07M | Indoor | Relative pose + co-visibility |
| MegaDepth | 2.01M | Landmarks | SfM reconstruction |
| 3DStreetView | 0.66M | Street views | GPS + visual overlap |
| IndoorVL | 1.59M | Indoor public | Frame sampling |

**Total**: 7.1M pairs (5.3M real + 1.82M synthetic)

### Training Strategy
- **Pre-training**: Cross-view completion on 7.1M pairs
- **Masking**: 90% of first image patches
- **Batch size**: 512
- **Optimizer**: AdamW
- **Augmentations**: Basic augmentations (crops, color)

## 📊 Results

### Stereo Matching Performance

#### Ablation Study (Middlebury)
| Configuration | bad@2.0 ↓ |
|--------------|----------|
| CroCo (cosine) | 26.3 |
| + RoPE | 25.3 |
| + real-world pairs | 20.7 |
| + larger decoder | 17.1 |
| + larger encoder (CroCo v2) | **15.5** |

#### Benchmark Results
| Dataset | Metric | CroCo-Stereo |
|---------|--------|-------------|
| KITTI 2015 | D1-all ↓ | **1.59** |
| ETH3D | bad@1.0 noc ↓ | **0.99** |
| Spring | 1px error ↓ | **7.13** |

### Optical Flow Performance

#### Ablation Study (MPI-Sintel Clean)
| Configuration | EPE ↓ |
|--------------|-------|
| CroCo (cosine) | 2.07 |
| + RoPE | 2.13 |
| + real-world pairs | 1.76 |
| + larger decoder | 1.51 |
| + larger encoder (CroCo v2) | **1.43** |

#### Benchmark Results
| Dataset | Split/Metric | CroCo-Flow |
|---------|-------------|------------|
| MPI-Sintel | Clean EPE ↓ | **1.09** |
| MPI-Sintel | Final EPE ↓ | **2.44** |
| KITTI | F1-all ↓ | **3.64** |
| Spring | EPE ↓ | **0.498** |

### Key Achievement
First pure transformer method to achieve SOTA without:
- Correlation volumes
- Iterative refinement
- Multi-scale processing
- Task-specific architectures

## 💡 Insights & Impact

### Advantages over CroCo v1
1. **Generalization**: Real-world training data dramatically improves performance
2. **Flexibility**: RoPE enables handling arbitrary resolutions and aspect ratios
3. **Scalability**: Larger models yield substantial performance gains
4. **Simplicity**: Achieves SOTA without complex task-specific components

### Limitations
1. **Data Requirements**: Needs geometric metadata (poses/depth) for pair selection
2. **Computational Cost**: Larger transformer models increase inference time
3. **Training Resources**: Requires significant GPU resources for pre-training

### Impact on DUSt3R Development
- **Architectural Foundation**: DUSt3R adopts the scaled encoder-decoder design
- **Data Strategy**: Validates using diverse real-world data for 3D tasks
- **Unified Approach**: Reinforces viability of general architectures for geometric vision
- **Pre-training Benefits**: Shows strong representations transfer to various 3D tasks

## 🔗 Related Work

### Evolution Path
- **CroCo** (NeurIPS 2022): Original cross-view completion
- **CroCo v2** (ICCV 2023): This work
- **DUSt3R** (CVPR 2024): Extends to uncalibrated 3D reconstruction
- **MASt3R** (ECCV 2024): Further unification of 3D tasks

### Contemporary Methods
- **RAFT-Stereo**: Correlation-based stereo matching
- **GMFlow**: Global matching for optical flow
- **CRAFT**: Cross-attention for stereo and flow

## 📚 Key Takeaways

CroCo v2 significantly advances the cross-view completion paradigm by:
1. Demonstrating that real-world data collection at scale is crucial
2. Proving transformers can match/exceed specialized architectures
3. Showing relative position embeddings improve geometric understanding
4. Validating that unified models can excel at multiple dense prediction tasks

The transition from synthetic-only (v1) to real-world training (v2) and the architectural improvements directly influenced DUSt3R's design, particularly in handling uncalibrated images and producing dense 3D predictions.
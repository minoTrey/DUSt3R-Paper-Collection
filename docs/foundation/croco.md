# CroCo: Self-Supervised Pre-training for 3D Vision Tasks by Cross-View Completion (NeurIPS 2022)

![CroCo Overview](https://ar5iv.labs.arxiv.org/html/2210.10716/assets/x1.png)

*Figure 1: CroCo cross-view completion task*

![CroCo Architecture](https://ar5iv.labs.arxiv.org/html/2210.10716/assets/x2.png)

*Figure 2: CroCo reconstruction examples*

![CroCo Architecture](https://ar5iv.labs.arxiv.org/html/2210.10716/assets/x3.png)

*Figure 3: CroCo architecture*

## 📋 Overview
- **Authors**: Philippe Weinzaepfel, Vincent Leroy, Thomas Lucas, Romain Brégier, Yohann Cabon, Vaibhav Arora, Leonid Antsfeld, Boris Chidlovskii, Gabriela Csurka, Jérôme Revaud
- **Institution**: NAVER LABS Europe
- **Venue**: NeurIPS 2022
- **Links**: [Paper](https://arxiv.org/abs/2210.10716) | [Code](https://github.com/naver/croco) | [Project Page](https://croco.europe.naverlabs.com/)
- **TL;DR**: Self-supervised pre-training method that learns 3D-aware representations by reconstructing masked image regions using cross-view information.

## 🎯 Key Contributions

1. **Cross-View Completion Pretext Task**: Novel self-supervised approach that masks one image and reconstructs it using both visible parts and a second view
2. **3D Vision-Oriented Pre-training**: Unlike semantic-focused methods (MAE), specifically designed for geometric understanding
3. **Unified Architecture**: Single model handles both monocular (encoder only) and binocular tasks (full encoder-decoder)
4. **State-of-the-art 3D Performance**: Achieves 85.6% δ₁ accuracy on NYUv2 depth estimation, surpassing all previous self-supervised methods
5. **Synthetic Pre-training Success**: Demonstrates effectiveness of simulator-based training on 1.82M image pairs

## 🔧 Technical Details

### Architecture
- **Input**: Two images of the same scene (different viewpoints)
- **Output**: Reconstructed RGB patches for masked regions
- **Components**:
  - Encoder: ViT-Base/16 (12 blocks, 768 dims, 12 heads) - processes each image independently
  - Decoder: 8 transformer blocks (512 dims, 16 heads) - reconstructs masked patches
  - Two decoder variants tested:
    - **CrossBlock**: Uses cross-attention between views (better performance)
    - **CatBlock**: Simple concatenation of features

### Key Design Choices
- **High masking ratio**: 90% (much higher than typical MIM)
- **Patch size**: 16×16 on 224×224 images
- **Loss**: Simple MSE on RGB values
- **Optimal co-visibility**: ~50% overlap between views

### Training
- **Dataset**: 1.82M synthetic indoor image pairs from Habitat simulator
- **Sources**: Habitat simulator datasets
  - Multiple indoor scene datasets
  - Total: 1.82M synthetic image pairs
- **Epochs**: 400 with cosine LR schedule
- **Hardware**: 4 GPUs (A100 or V100)
- **Batch size**: 256 (64 per GPU × 4 GPUs)
- **Training time**: ~10 days (A100) or ~15 days (V100)
- **Learning rate**: Following MAE's scaling rule
- **Augmentations**: Homography and color jittering

## 📊 Results

**Model Details**: All results use CroCo (ViT-Base encoder) pre-trained on synthetic data (400 epochs) then fine-tuned on target datasets.

### Quantitative Performance

#### Monocular Depth Estimation (NYUv2)
| Method | Pretrain Data | δ₁ ↑ | δ₂ ↑ | δ₃ ↑ | REL ↓ | RMS ↓ | log₁₀ ↓ |
|--------|---------------|-------|-------|-------|--------|--------|----------|
| DINO | IN1K | 0.668 | - | - | - | - | - |
| MAE | IN1K | 0.796 | 0.954 | 0.989 | 0.129 | 0.497 | 0.055 |
| MultiMAE | IN1K | 0.830 | 0.964 | 0.991 | 0.116 | 0.455 | 0.050 |
| MAE | Habitat | 0.790 | - | - | - | - | - |
| **CroCo** | **Habitat** | **0.856** | **0.972** | **0.994** | **0.106** | **0.424** | **0.046** |

*Note: δᵢ represents accuracy at threshold 1.25ⁱ*

#### Other Monocular Tasks  
| Task | Dataset | Metric | CroCo | MAE (Habitat) | MAE (IN1K) |
|------|---------|--------|--------|---------------|-------------|
| 3D Tasks | Taskonomy | L1 Loss ↓ | **33.00** | 35.65 | 36.09 |
| 3D Tasks | Taskonomy | Avg Rank ↓ | **1.25** | 2.88 | 2.13 |
| Segmentation | ADE20k | mIoU ↑ | 40.6 | 40.3 | 46.1 |
| Classification | ImageNet | Top-1 ↑ | 37.0% | 32.5% | 68.0% |

#### Binocular Tasks
| Task | Dataset | Split | CroCo | MAE (Habitat) | Random Init |
|------|---------|-------|--------|---------------|-------------|
| Optical Flow | MPI-Sintel | Clean | **3.00** | 4.63 | 18.81 |
| Optical Flow | MPI-Sintel | Final | **3.60** | 5.24 | 18.97 |

#### Relative Pose Estimation (7-Scenes)
| Method | Chess | Fire | Heads | Office | Pumpkin | Kitchen | Stairs | Average |
|--------|-------|------|-------|--------|---------|---------|--------|----------|
| MAE (Habitat) | 13.2cm, 9.44° | 32.0cm, 15.10° | 16.0cm, 16.75° | 24.8cm, 11.54° | 25.4cm, 10.62° | 29.4cm, 13.32° | 32.8cm, 14.88° | 24.8cm, 13.09° |
| **CroCo** | **2.4cm, 2.81°** | **4.0cm, 3.86°** | **3.1cm, 4.00°** | **3.4cm, 2.53°** | **4.9cm, 2.79°** | **5.5cm, 3.72°** | **11.7cm, 4.53°** | **5.0cm, 3.46°** |

*Note: CroCo achieves competitive results without task-specific design or temporal fusion*

### Qualitative Results
- Sharp depth predictions with fine details
- Accurate optical flow estimation
- Robust cross-view matching capabilities
- Effective on both synthetic and real images

## 💡 Insights & Impact

### Strengths
1. **Geometric Understanding**: Forces model to reason about 3D structure through cross-view constraint
2. **Versatility**: Single pre-trained model for diverse 3D tasks (depth, flow, pose)
3. **Efficiency**: Faster fine-tuning convergence compared to semantic pre-training
4. **No Camera Calibration**: Works with uncalibrated image pairs

### Limitations
1. **Semantic Performance**: Lower on high-level tasks (ImageNet 37.0% vs MAE 68.0%)
2. **Indoor Scene Bias**: Pre-training only on synthetic indoor environments
3. **RGB Reconstruction**: Not designed for photorealistic reconstruction
4. **Two-View Constraint**: Requires image pairs during pre-training

### Impact on the Field
- **Foundation for DUSt3R**: Cross-view understanding → uncalibrated 3D reconstruction
- **Inspired Follow-ups**: CroCo v2 and subsequent 3D vision models
- **Paradigm Shift**: From semantic to geometric pre-training objectives
- **Synthetic Data Validation**: Demonstrated effectiveness of Habitat simulator pre-training

## 🔗 Related Work

### Building on CroCo
- **CroCo v2** (ICCV 2023): Enhanced version for stereo and optical flow
- **DUSt3R** (CVPR 2024): Extended to end-to-end 3D reconstruction
- **MASt3R** (ECCV 2024): Unified 3D-aware matching and reconstruction

### Contemporary Approaches
- **MAE**: Masked autoencoding for semantic understanding
- **MultiMAE**: Multi-modal masked autoencoding
- **DINO**: Self-supervised vision transformer

## 📚 Key Takeaways

CroCo demonstrated that:
1. **Cross-view completion** is an effective self-supervised task for learning 3D-aware representations
2. **Synthetic data pre-training** (Habitat) can outperform ImageNet pre-training on 3D tasks
3. **Single architecture** can handle both monocular and binocular vision tasks effectively
4. **Geometric pre-training** offers advantages over semantic pre-training for 3D understanding

The model achieves state-of-the-art results on depth estimation (85.6% on NYUv2) and competitive performance on optical flow and relative pose estimation, establishing a new paradigm for 3D vision pre-training.
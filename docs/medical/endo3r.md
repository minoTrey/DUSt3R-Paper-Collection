# Endo3R: Unified Online Reconstruction from Dynamic Monocular Endoscopic Video (arXiv 2025)

![Endo3R Pipeline](https://wrld.github.io/Endo3R/static/images/pipeline.jpg)
*Endo3R achieves real-time 3D reconstruction from monocular endoscopy using dual memory architecture for surgical applications*

## 📋 Overview

- **Authors**: Jiaxin Guo, Wenzhen Dong, Tianyu Huang, Hao Ding, Ziyi Wang, Haomin Kuang, Qi Dou, Yun-hui Liu
- **Institutions**: The Chinese University of Hong Kong (CUHK), Hong Kong Centre For Logistics Robotics, Johns Hopkins University, Shanghai Jiao Tong University
- **Venue**: MICCAI 2025 (Oral) | arXiv preprint (submitted April 2025)
- **Links**: [Paper](https://arxiv.org/html/2504.03198v1) | [Project Page](https://wrld.github.io/Endo3R/)
- **TL;DR**: First unified 3D surgical foundation model for online scale-consistent reconstruction from monocular endoscopy at 19.17 FPS without calibration.

## 🎯 Key Contributions

1. **Unified Surgical Foundation Model**: Single model for depth, pose, and 3D reconstruction
2. **Dual Memory Mechanism**: Handles both dynamic changes and long-term consistency
3. **Uncertainty-aware Filtering**: Sampson distance-based token selection
4. **Real-time Performance**: 19.17 FPS for surgical applications
5. **Self-supervised Learning**: No ground truth depth/poses required

## 🔧 Technical Details

### Core Innovation: Dual Memory Architecture
```
Short-term Memory:
- Captures dynamic surgical changes
- Handles instrument motion
- Adapts to tissue deformation

Long-term Memory:
- Maintains spatial consistency
- Preserves global structure
- Enables scale-consistent reconstruction
```

### Key Technical Components

#### 1. Uncertainty-aware Token Filtering
- Uses Sampson distance to measure geometric uncertainty
- Filters unreliable tokens before memory update
- Crucial for handling specular reflections and occlusions

#### 2. Dynamic-aware Flow Loss
- Novel loss function for surgical dynamics
- Handles tissue deformation naturally
- Maintains temporal consistency

#### 3. Online Processing Pipeline
1. Frame pair extraction from video
2. DUSt3R-based feature encoding
3. Dual memory update with uncertainty filtering
4. Scale-consistent 3D reconstruction
5. Real-time output at 19+ FPS

### Adaptations from DUSt3R
- **Memory Extension**: Adds temporal reasoning
- **Uncertainty Modeling**: Critical for medical safety
- **Dynamic Handling**: Addresses deformable tissues
- **Efficiency Optimization**: Achieves real-time performance

## 📊 Results

### Quantitative Performance

#### Depth Estimation (SCARED Dataset)
| Method | Abs Rel ↓ | Sq Rel ↓ | RMSE ↓ | δ<1.25 ↑ |
|--------|-----------|----------|---------|-----------|
| MonoDepth2 | 0.172 | 2.451 | 8.642 | 76.8% |
| EndoSLAM | 0.098 | 0.872 | 5.128 | 89.2% |
| **Endo3R** | **0.071** | **0.512** | **3.921** | **93.7%** |

#### Pose Estimation
| Dataset | ATE ↓ | RPE Trans ↓ | RPE Rot ↓ |
|---------|--------|-------------|-----------|
| Hamlyn | **0.042** | **0.018** | **0.021** |
| SCARED | **0.038** | **0.015** | **0.019** |

### Zero-shot Generalization
- Strong performance on unseen datasets
- Robust to different endoscope types
- Handles various surgical procedures

## 💡 Insights & Impact

### Medical Domain Challenges Addressed

1. **Dynamic Deformation**: Dual memory handles tissue motion
2. **Limited Texture**: Geometric priors compensate
3. **Specular Reflections**: Uncertainty filtering removes artifacts
4. **No Calibration**: Self-supervised approach
5. **Real-time Needs**: Optimized for surgical speed

### Clinical Relevance
- **Intraoperative Guidance**: Real-time 3D visualization
- **Measurement Accuracy**: Scale-consistent depth
- **Safety Enhancement**: Uncertainty quantification
- **Training Tool**: Realistic surgical simulation

### Technical Advantages
- **End-to-end**: No complex pipeline
- **Robust**: Handles challenging surgical scenes
- **Efficient**: Practical for OR deployment
- **Generalizable**: Works across procedures

### Limitations
- Monocular only (no stereo endoscopy yet)
- Requires continuous video stream
- Memory footprint for long procedures
- Limited to rigid endoscope motion

## 🔗 Related Work

### Builds On
- **DUSt3R**: Base architecture
- **Surgical SLAM**: Domain knowledge
- **Medical Vision**: Clinical requirements

### Enables Future Work
- Multi-modal fusion (RGB + other sensors)
- Instrument tracking integration
- AR surgical overlay
- Tissue classification

## 📚 Key Takeaways

Endo3R demonstrates that:
1. **Foundation models adapt to medical domains**: With proper modifications
2. **Real-time is achievable**: 19+ FPS meets surgical needs
3. **Self-supervision works**: Overcomes lack of medical ground truth
4. **Uncertainty matters**: Critical for medical safety

The success of Endo3R in surgical applications validates the potential of adapting general 3D reconstruction methods to highly specialized medical domains, opening new possibilities for computer-assisted surgery.
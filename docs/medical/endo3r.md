# Endo3R: Unified Online Reconstruction from Dynamic Monocular Endoscopic Video (MICCAI 2025)

![Endo3R Pipeline](https://wrld.github.io/Endo3R/static/images/pipeline.jpg)
_Endo3R achieves real-time 3D reconstruction from monocular endoscopy using dual memory architecture for surgical applications_

## 📋 Overview

- **Authors**: Jiaxin Guo, Wenzhen Dong, Tianyu Huang, Hao Ding, Ziyi Wang, Haomin Kuang, Qi Dou, Yun-hui Liu
- **Institution**: The Chinese University of Hong Kong (CUHK), Hong Kong Centre For Logistics Robotics, Johns Hopkins University, Shanghai Jiao Tong University
- **Venue**: MICCAI 2025
- **Award**: Oral
- **Links**: [Paper](https://arxiv.org/abs/2504.03198) | [Project Page](https://wrld.github.io/Endo3R/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: First unified 3D surgical foundation model for online scale-consistent reconstruction from monocular endoscopy at 19.17 FPS without calibration.

## 🎯 Key Contributions

1. **Unified Surgical Foundation Model**: Single model for depth, pose, and 3D reconstruction
2. **Dual Memory Mechanism**: Handles both dynamic changes and long-term consistency
3. **Uncertainty-aware Filtering**: Sampson distance-based token selection
4. **Real-time Performance**: 19.17 FPS for surgical applications
5. **Self-supervised Learning**: No ground truth depth/poses required

## 🔧 Technical Details

### Core Innovation: Dual Memory Architecture

```text
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

#### Depth Estimation — SCARED

원논문 Table 1 (상단). 320×256 해상도, SCARED 공식 train/test split.

| Method     | Abs Rel ↓ | Sq Rel ↓  | RMSE ↓    | RMSE log ↓ | δ<1.25 ↑  | FPS ↑     |
| ---------- | --------- | --------- | --------- | ---------- | --------- | --------- |
| Monodepth2 | 0.432     | 3.548     | 4.704     | 0.431      | 0.425     | 22.05     |
| Endo-SfM   | 0.241     | 0.865     | 2.286     | 0.267      | 0.585     | 7.33      |
| AF-SfM     | 0.257     | 0.960     | 2.162     | 0.291      | 0.573     | 3.17      |
| EndoDAC    | 0.242     | 0.934     | 2.014     | 0.275      | 0.584     | **31.79** |
| Transfer   | 0.297     | 1.207     | 2.561     | 0.319      | 0.561     | 9.37      |
| DA-V2      | 0.313     | 1.425     | 2.839     | 0.453      | 0.508     | 4.18      |
| VDA        | 0.291     | 1.186     | 2.447     | 0.296      | 0.647     | 6.86      |
| Endo DM    | 0.203     | 0.651     | 2.063     | 0.245      | 0.612     | 14.58     |
| MonST3R    | 0.198     | 0.539     | 1.965     | 0.234      | 0.626     | 18.68     |
| **Endo3R** | **0.124** | **0.227** | **1.209** | **0.135**  | **0.839** | 19.17     |

#### Depth Estimation — Hamlyn (zero-shot)

원논문 Table 1 (하단). 학습에 쓰지 않은 Hamlyn 22개 영상 전체에 대한 cross-dataset 검증.

| Method     | Abs Rel ↓ | Sq Rel ↓  | RMSE ↓     | RMSE log ↓ | δ<1.25 ↑  | FPS ↑     |
| ---------- | --------- | --------- | ---------- | ---------- | --------- | --------- |
| Monodepth2 | 0.379     | 9.318     | 20.472     | 0.403      | 0.439     | 22.05     |
| Endo-SfM   | 0.252     | 4.335     | 14.430     | 0.268      | 0.628     | 7.33      |
| AF-SfM     | 0.286     | 5.715     | 15.895     | 0.301      | 0.508     | 3.17      |
| EndoDAC    | 0.275     | 5.557     | 15.669     | 0.288      | 0.519     | **31.79** |
| Transfer   | 0.281     | 5.790     | 15.936     | 0.312      | 0.504     | 9.37      |
| DA-V2      | 0.334     | 7.713     | 19.548     | 0.362      | 0.461     | 4.18      |
| VDA        | 0.315     | 7.492     | 19.231     | 0.347      | 0.476     | 6.86      |
| Endo DM    | 0.216     | 4.639     | 14.799     | 0.273      | 0.619     | 14.58     |
| MonST3R    | 0.198     | 4.193     | 15.221     | 0.241      | 0.645     | 18.68     |
| **Endo3R** | **0.170** | **3.139** | **11.569** | **0.196**  | **0.707** | 19.17     |

#### Pose Estimation (SCARED)

원논문 Table 2. 5-frame 평가. ATE·RPEt 단위는 mm, RPEr은 도(degree).

| Method     | ATE ↓     | RPEr ↓    | RPEt ↓    |
| ---------- | --------- | --------- | --------- |
| Endo-SfM   | 0.157     | 0.252     | 0.259     |
| AF-SfM     | 0.125     | 0.235     | 0.241     |
| EndoDAC    | 0.124     | 0.223     | 0.233     |
| Robust     | 0.131     | 0.241     | 0.245     |
| **Endo3R** | **0.112** | **0.201** | **0.228** |

#### Ablation (SCARED)

원논문 Table 3.

| Setting        | Abs Rel ↓ | RMSE ↓    | δ<1.25 ↑  |
| -------------- | --------- | --------- | --------- |
| Baseline       | 0.198     | 1.965     | 0.626     |
| w/ Uncertainty | 0.165     | 1.654     | 0.720     |
| w/ L_dep       | 0.153     | 1.486     | 0.772     |
| w/ L_Dflow     | **0.124** | **1.209** | **0.839** |

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

- **[DUSt3R](../foundation/dust3r.md)**: Base architecture
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

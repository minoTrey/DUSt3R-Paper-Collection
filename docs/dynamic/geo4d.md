# Geo4D: Leveraging Video Generators for Geometric 4D Scene Reconstruction (ICCV 2025)

![Geo4D Results](https://geo4d.github.io/resources/teaser_v3.png)
_Geo4D leverages video diffusion models to achieve state-of-the-art 4D reconstruction with multi-modal geometric predictions_

## 📋 Overview

- **Authors**: Zeren Jiang, Chuanxia Zheng, Iro Laina, Diane Larlus, Andrea Vedaldi
- **Institution**: Visual Geometry Group (Oxford), Naver Labs Europe
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

```text
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

### Video Depth Estimation

원논문 Table 1. MonST3R의 평가 프로토콜을 따름. DepthCrafter\*는 v1.0.1 결과.

| Category           | Method            | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ------------------ | ----------------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| Single-frame depth | Marigold          | 0.532            | 51.5            | 0.091          | 93.1          | 0.149           | 79.6           |
| Single-frame depth | Depth-Anything-V2 | 0.367            | 55.4            | 0.106          | 92.1          | 0.140           | 80.4           |
| Video depth        | NVDS              | 0.408            | 48.3            | 0.167          | 76.6          | 0.253           | 58.8           |
| Video depth        | ChronoDepth       | 0.687            | 48.6            | 0.100          | 91.1          | 0.167           | 75.9           |
| Video depth        | DepthCrafter\*    | 0.270            | 69.7            | 0.071          | 97.2          | 0.104           | 89.6           |
| Depth & pose       | Robust-CVD        | 0.703            | 47.8            | —              | —             | —               | —              |
| Depth & pose       | CasualSAM         | 0.387            | 54.7            | 0.169          | 73.7          | 0.246           | 62.2           |
| Depth & pose       | MonST3R           | 0.335            | 58.5            | 0.063          | 96.4          | 0.104           | 89.5           |
| Depth & pose       | **Geo4D**         | **0.205**        | **73.5**        | **0.059**      | **97.2**      | **0.086**       | **93.7**       |

### Camera Pose Estimation

원논문 Table 2. MonST3R와 동일한 프로토콜(Sintel 동적 14개 시퀀스, TUM-dynamics 앞 90프레임/stride 3).

| Method     | Sintel ATE ↓ | Sintel RPE-T ↓ | Sintel RPE-R ↓ | TUM ATE ↓ | TUM RPE-T ↓ | TUM RPE-R ↓ |
| ---------- | ------------ | -------------- | -------------- | --------- | ----------- | ----------- |
| Robust-CVD | 0.360        | 0.154          | 3.443          | 0.153     | 0.026       | 3.528       |
| CasualSAM  | 0.141        | 0.035          | 0.615          | 0.071     | 0.010       | 1.712       |
| MonST3R    | **0.108**    | **0.042**      | 0.732          | **0.063** | **0.009**   | 1.217       |
| Geo4D      | 0.185        | 0.063          | **0.547**      | 0.073     | 0.020       | **0.635**   |

회전 오차(RPE-R)는 Geo4D가 가장 좋고, 병진(ATE·RPE-T)은 MonST3R와 비슷한 수준이다.

### Ablation: Geometric Modality (Sintel)

원논문 Table 3. 학습 시 멀티모달 감독과 추론 시 멀티모달 정렬의 효과.

| Training modality | Inference modality | Abs Rel ↓ | δ<1.25 ↑ | ATE ↓     | RPE trans ↓ | RPE rot ↓ |
| ----------------- | ------------------ | --------- | -------- | --------- | ----------- | --------- |
| Point             | Point              | 0.232     | 71.3     | 0.335     | 0.076       | 0.731     |
| Point+Disp+Ray    | Point              | 0.223     | 72.5     | 0.237     | 0.070       | 0.566     |
| Point+Disp+Ray    | Disparity          | 0.211     | 73.4     | —         | —           | —         |
| Point+Disp+Ray    | Ray                | —         | —        | 0.268     | 0.192       | 1.476     |
| Point+Disp+Ray    | **All three**      | **0.205** | **73.5** | **0.185** | **0.063**   | **0.547** |

### Ablation: Sliding Window Stride (Sintel)

원논문 Table 4. 성능과 속도의 트레이드오프. 본 논문은 stride 4를 채택했다.
동일 설정에서 MonST3R는 프레임당 2.41초로, Geo4D가 1.27배 빠르다.

| Stride | s / frame | Abs Rel ↓ | δ<1.25 ↑ | ATE ↓ | RPE trans ↓ | RPE rot ↓ |
| ------ | --------- | --------- | -------- | ----- | ----------- | --------- |
| 15     | 0.92      | 0.213     | 72.4     | 0.210 | 0.092       | 0.574     |
| 8      | 1.24      | 0.212     | 72.8     | 0.222 | 0.074       | 0.524     |
| **4**  | **1.89**  | **0.205** | **73.5** | 0.185 | 0.063       | 0.547     |
| 2      | 3.26      | 0.204     | 72.9     | 0.181 | 0.058       | 0.518     |

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

| Method    | Approach            | Training      | Quality  |
| --------- | ------------------- | ------------- | -------- |
| MonST3R   | Per-frame           | Real data     | Good     |
| Easi3R    | Attention           | None          | Medium   |
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

# LargeSpatialModel: End-to-end Unposed Images to Semantic 3D (NeurIPS 2024)

![LargeSpatialModel Pipeline](https://largespatialmodel.github.io/static/images/teaser.png)
_LargeSpatialModel creates semantic 3D representations directly from unposed images through end-to-end learning_

## 📋 Overview

- **Authors**: Zhiwen Fan, Jian Zhang, Wenyan Cong, Peihao Wang, Renjie Li, Kwan-Yee Lin, Shijie Zhou, Achuta Kadambi, Zhangyang Wang
- **Institution**: University of Texas at Austin, UCLA, Hong Kong University of Science and Technology
- **Venue**: NeurIPS 2024
- **Links**: [Paper](https://arxiv.org/abs/2410.18956) | [Project Page](https://largespatialmodel.github.io/) | [Code](https://github.com/VITA-Group/LargeSpatialModel)
- **TL;DR**: End-to-end framework that transforms unposed images directly into semantic 3D scene representations without requiring camera poses or traditional SfM pipelines.

## 🎯 Key Contributions

1. **End-to-End Learning**: Direct unposed images to semantic 3D
2. **Pose-Free Training**: No camera pose requirements
3. **Semantic 3D Output**: Rich semantic scene understanding
4. **Large-Scale Model**: Foundation model scale architecture
5. **Unified Framework**: Single model for multiple 3D tasks

## 🔧 Technical Details

### Core Innovation: Unposed to Semantic 3D

```text
Traditional: Images → SfM → Poses → 3D reconstruction → Semantics
LargeSpatialModel: Unposed images → End-to-end → Semantic 3D
```

### Technical Approach

#### 1. End-to-End Architecture

- Direct transformation from images to 3D
- Implicit pose estimation within the model
- Joint geometric and semantic learning
- Large-scale transformer architecture

#### 2. Spatial Understanding Module

```text
Input: Unposed image collection {I₁, I₂, ..., Iₙ}
Process: Spatial relationship learning + Semantic understanding
Output: Semantic 3D scene representation S(x,y,z) = {geometry, semantics}
```

#### 3. Key Components

- **Image Encoder**: Multi-view feature extraction
- **Spatial Reasoning**: Implicit pose and geometry
- **Semantic Decoder**: 3D semantic prediction
- **End-to-End Loss**: Joint optimization

### Architecture Design

- **Transformer Backbone**: Scalable attention mechanism
- **Multi-Task Learning**: Joint pose, geometry, semantics
- **Large-Scale Training**: Foundation model approach
- **Efficient Inference**: Direct image-to-3D pipeline

## 📊 Results

### Quantitative Comparison on 3D Tasks (ScanNet)

원논문 Table 1. LSM(Ours)만 SfM 전처리가 필요 없다.
`rel`은 Absolute Relative depth error, `τ`는 threshold 1.03 inlier ratio.

| Model          | SfM Time ↓ | Per-Scene Time ↓ | Src mIoU ↑ | Src Acc. ↑ | rel ↓    | τ ↑       | Tgt mIoU ↑ | Tgt Acc. ↑ |
| -------------- | ---------- | ---------------- | ---------- | ---------- | -------- | --------- | ---------- | ---------- |
| LSeg (2D)      | N/A        | N/A              | **0.5278** | 0.7654     | –        | –         | **0.5281** | 0.7612     |
| NeRF-DFF       | 20.52s     | 1min2s           | 0.4540     | 0.7173     | 27.68    | 9.61      | 0.4037     | 0.6755     |
| Feature-3DGS   | 20.52s     | 18min36s         | 0.4453     | 0.7276     | 12.95    | 21.07     | 0.4223     | 0.7174     |
| pixelSplat     | 20.52s     | 0.064s           | –          | –          | –        | –         | –          | –          |
| **LSM (Ours)** | **None**   | **0.108s**       | 0.5034     | **0.7740** | **3.38** | **67.77** | 0.5078     | **0.7686** |

Novel-view synthesis 부분 (같은 Table 1의 Target View 열):

| Model          | PSNR ↑    | SSIM ↑     | LPIPS ↓    |
| -------------- | --------- | ---------- | ---------- |
| NeRF-DFF       | 19.86     | 0.6650     | 0.3629     |
| Feature-3DGS   | 24.49     | 0.8132     | 0.2293     |
| pixelSplat     | **24.89** | **0.8392** | **0.1641** |
| **LSM (Ours)** | 24.39     | 0.8072     | 0.2506     |

### Replica Dataset

원논문 Table 4. `None`은 해당 모델이 그 지표를 산출하지 못함을 뜻한다.

| Model          | Offline SfM      | mIoU ↑   | rel ↓    | PSNR ↑    |
| -------------- | ---------------- | -------- | -------- | --------- |
| pixelSplat     | Required         | None     | 20.14    | **26.28** |
| Splatter Image | Required         | None     | None     | 12.37     |
| **LSM (Ours)** | **Not Required** | **0.51** | **4.91** | 23.10     |

### Ablation: Design Choices

원논문 Table 2. 이 표의 segmentation 지표는 LSeg 결과를 ground-truth로 삼는다.

| Exp ID | Model                                | mIoU ↑     | Acc. ↑     | PSNR ↑    | SSIM ↑     |
| ------ | ------------------------------------ | ---------- | ---------- | --------- | ---------- |
| [1]    | Baseline                             | 0.4562     | 0.6940     | 24.00     | 0.7981     |
| [2]    | [1] + Fuse Encoder Feat.             | 0.5410     | 0.8083     | 23.67     | 0.7876     |
| [3]    | [1] + Fuse LSeg Feat.                | 0.5586     | 0.8505     | 23.85     | 0.7902     |
| [4]    | [1] + [2] + [3] + Multi-scale Fusion | **0.6042** | **0.8681** | **24.39** | **0.8072** |

### Inference Time Breakdown

원논문 Table 3.

| Module                           | Inference Time (s) |
| -------------------------------- | ------------------ |
| Dense Geometry Prediction (§3.1) | 0.029              |
| Point-wise Aggregation (§3.2)    | 0.046              |
| Feature Lifting (§3.3)           | 0.019              |
| **Total**                        | **0.096**          |

### Key Achievements

- ✅ SfM 전처리 없이 end-to-end — 전체 0.108s vs Feature-3DGS의 18분 36초 + SfM 20.52s
- ✅ Depth에서 압도적: rel 3.38, τ 67.77 (per-scene 최적화 방식들의 12.95 / 21.07 대비)
- ✅ 2D LSeg에 근접한 segmentation을 view-consistent하게 달성
- ✅ NVS는 pixelSplat에 근소하게 뒤지지만 pixelSplat은 GT 카메라 파라미터를 요구한다

## 💡 Insights & Impact

### Paradigm Shift in 3D Scene Understanding

**Traditional Pipeline**:

1. Structure from Motion (SfM)
2. 3D reconstruction
3. Semantic segmentation
4. Multiple error-prone stages

**LargeSpatialModel**:

1. Direct image input
2. End-to-end learning
3. Joint semantic 3D output
4. Single optimized pipeline

### Why End-to-End Works

1. **Joint Optimization**: All components optimized together
2. **Error Propagation**: Eliminates intermediate error accumulation
3. **Rich Features**: Learned representations capture more information
4. **Task Synergy**: Geometry and semantics mutually beneficial

### Applications

- **Autonomous Navigation**: Scene understanding for robots
- **AR/VR**: Real-time semantic 3D mapping
- **Smart Cities**: Urban scene analysis
- **Digital Twins**: Semantic building models
- **Robotics**: Environment understanding

### Advantages Over Traditional Methods

- **Simplified Pipeline**: Single model vs multi-stage
- **Better Semantics**: Joint learning improves understanding
- **Robust**: Less sensitive to pose estimation failures
- **Efficient**: Faster end-to-end inference

## 🔗 Related Work

### Comparison with 3D Understanding Methods

| Aspect    | SfM+Seg      | NeRF+Seg  | 3D-GS+Seg | LargeSpatialModel |
| --------- | ------------ | --------- | --------- | ----------------- |
| Pipeline  | Multi-stage  | Two-stage | Two-stage | End-to-end        |
| Pose Req. | Yes          | Yes       | Yes       | No                |
| Semantics | Post-process | Limited   | Limited   | Native            |
| Speed     | Slow         | Medium    | Fast      | Fast              |

### Builds On

- **Foundation Models**: Large-scale learning paradigms
- **Multi-View Geometry**: 3D understanding from images
- **Semantic Segmentation**: Scene understanding techniques
- **End-to-End Learning**: Joint optimization approaches

### Relationship to DUSt3R Ecosystem

- **Different Focus**: Semantic understanding vs geometric reconstruction
- **Complementary**: Could enhance DUSt3R with semantics
- **Shared Philosophy**: End-to-end learning approach
- **Potential Integration**: Semantic-aware geometric reconstruction

## 📚 Key Takeaways

LargeSpatialModel demonstrates that:

1. **End-to-end works**: Direct learning outperforms pipelines
2. **Semantics and geometry synergize**: Joint learning improves both
3. **Pose-free is possible**: Implicit pose learning is effective
4. **Scale matters**: Large models enable complex spatial reasoning

The success in creating semantic 3D representations directly from unposed images represents a major advancement toward unified 3D scene understanding systems.

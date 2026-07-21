# POMATO: Marrying Pointmap Matching with Temporal Motion for Dynamic 3D Reconstruction (ICCV 2025)

![POMATO Architecture](https://github.com/wyddmw/POMATO/blob/main/assets/teaser.png?raw=true)
_POMATO combines explicit pointmap matching with temporal motion modeling for dynamic scene reconstruction_

## 📋 Overview

- **Authors**: Songyan Zhang, Yongtao Ge, Jinyuan Tian, Guangkai Xu, Hao Chen, Chen Lv, Chunhua Shen
- **Institution**: Nanyang Technological University, Zhejiang University, The University of Adelaide
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2504.05692) | [Code](https://github.com/wyddmw/POMATO) | [Project Page](Coming Soon)
- **TL;DR**: Unified framework combining pointmap matching with temporal motion modeling to enable accurate dynamic 3D reconstruction by addressing DUSt3R's limitations in handling moving scenes.

## 🎯 Key Contributions

1. **Unified Matching in 3D Space**: Explicit pixel-to-3D correspondences
2. **Temporal Motion Module**: Scale-consistent dynamic motion learning
3. **Two-Stage Training**: Geometry first, then temporal dynamics
4. **Multi-Task Framework**: Depth, tracking, pose, and segmentation
5. **No External Dependencies**: Self-contained architecture

## 🔧 Technical Details

### Core Innovation: Explicit Matching + Temporal Motion

```text
DUSt3R: Implicit matching → Limited to static scenes
POMATO: Explicit 3D matching + Temporal module → Dynamic scenes
```

### Architecture Components

- **Stage 1: Pairwise Training**
  - Learn fundamental geometry
  - Establish matching capacity
  - Build on DUSt3R foundation

- **Stage 2: Sequential Training**
  - Add temporal motion module
  - Learn dynamic motions
  - Ensure scale consistency

### Key Design Choices

- **Explicit Relationships**: Direct pixel-to-3D mapping
- **Unified Coordinates**: Consistent 3D space across frames
- **Scale Preservation**: Temporal consistency mechanism
- **End-to-End**: No external tracking required

### Technical Innovations

1. Maps RGB pixels to 3D pointmaps for both static/dynamic regions
2. Establishes explicit matching within unified coordinate system
3. Learns motion features along temporal dimension
4. Maintains DUSt3R's feed-forward efficiency

## 📊 Results

### Video Depth Estimation

원논문 Table 1. "GA"는 global alignment 필요, "Onl."은 online 방식.

| Alignment      | Method     | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ | Bonn AbsRel ↓ | Bonn δ<1.25 ↑ | KITTI AbsRel ↓ | KITTI δ<1.25 ↑ |
| -------------- | ---------- | --------------- | --------------- | ------------- | ------------- | -------------- | -------------- |
| Per-seq. scale | DUSt3R-GA  | 0.656           | 45.2            | 0.155         | 83.3          | 0.144          | 81.3           |
| Per-seq. scale | MASt3R-GA  | 0.641           | 43.9            | 0.252         | 70.1          | 0.183          | 74.5           |
| Per-seq. scale | MonST3R-GA | **0.378**       | **55.8**        | **0.067**     | **96.3**      | 0.168          | 74.4           |
| Per-seq. scale | Spann3R    | 0.622           | 42.6            | 0.144         | 81.3          | 0.198          | 73.7           |
| Per-seq. scale | CUT3R      | 0.421           | 47.9            | 0.078         | 93.7          | 0.118          | 88.1           |
| Per-seq. scale | **POMATO** | 0.416           | 53.6            | 0.074         | 96.1          | **0.085**      | **93.3**       |
| + shift        | MonST3R-GA | **0.335**       | **58.5**        | **0.063**     | 96.4          | 0.104          | 89.5           |
| + shift        | CUT3R      | 0.466           | 56.2            | 0.111         | 88.3          | **0.075**      | **94.3**       |
| + shift        | **POMATO** | 0.345           | 57.9            | 0.072         | **96.5**      | 0.084          | 93.4           |

### 3D Point Tracking (APD ↑)

원논문 Table 2. L-12/L-24는 각각 12·24프레임 구간 내 추적.
SpatialTracker\* 는 GT camera intrinsic을 추가로 쓰는 3D 트래킹 전용 네트워크다.

| Method           | PointOdyssey L-12 | L-24      | ADT L-12  | L-24      | PStudio L-12 | L-24      | Mean L-12 | L-24      |
| ---------------- | ----------------- | --------- | --------- | --------- | ------------ | --------- | --------- | --------- |
| SpatialTracker\* | 20.46             | 20.71     | 21.64     | 20.67     | **30.41**    | **25.87** | 24.17     | 22.42     |
| DUSt3R           | 19.03             | 19.03     | 29.02     | 25.55     | 9.72         | 6.50      | 19.26     | 17.03     |
| MASt3R           | 16.58             | 17.35     | 27.36     | 26.46     | 11.78        | 8.09      | 18.57     | 17.30     |
| MonST3R          | 27.31             | 27.92     | 28.30     | 26.13     | 16.50        | 11.06     | 24.03     | 21.70     |
| **POMATO**       | **33.20**         | **33.58** | **31.57** | **28.22** | 24.59        | 19.79     | **29.79** | **27.20** |

### Camera Pose Estimation

원논문 Table 4. 40프레임 구간 평가.

| Method     | TUM ATE ↓ | TUM RPE trans ↓ | TUM RPE rot ↓ | Bonn ATE ↓ | Bonn RPE trans ↓ | Bonn RPE rot ↓ |
| ---------- | --------- | --------------- | ------------- | ---------- | ---------------- | -------------- |
| DUSt3R     | 0.025     | 0.013           | 2.361         | 0.030      | 0.025            | 2.522          |
| MASt3R     | 0.027     | 0.015           | 1.910         | 0.031      | 0.025            | 2.478          |
| MonST3R    | 0.021     | **0.006**       | 1.142         | **0.025**  | 0.021            | 2.120          |
| CUT3R      | 0.023     | 0.016           | 0.510         | 0.028      | 0.033            | 2.569          |
| **POMATO** | **0.020** | 0.010           | **0.509**     | 0.037      | **0.016**        | **1.782**      |

RPE rot에서 MonST3R 대비 TUM 55.4%, Bonn 13.3% 개선 (원논문 4.4절).

### Ablation: Temporal Motion Module

원논문 Table 3. Tracking은 12프레임 기준.

| Temporal Length | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ | Bonn AbsRel ↓ | KITTI AbsRel ↓ | PointOdyssey APD ↑ | ADT APD ↑ | PStudio APD ↑ |
| --------------- | --------------- | --------------- | ------------- | -------------- | ------------------ | --------- | ------------- |
| Pair-wise       | 0.548           | 46.2            | 0.087         | 0.113          | 32.06              | 29.87     | 23.10         |
| 6 frames        | 0.436           | 51.3            | 0.076         | **0.085**      | 32.69              | 30.93     | 24.52         |
| **12 frames**   | **0.416**       | **53.6**        | **0.075**     | 0.086          | **33.20**          | **31.57** | **24.59**     |

### Ablation: Pointmap Matching Head (Head₃)

원논문 Table 5.

| Method       | Bonn ATE ↓ | Bonn RPE trans ↓ | Bonn RPE rot ↓ | PointOdyssey APD ↑ | ADT APD ↑ | PStudio APD ↑ |
| ------------ | ---------- | ---------------- | -------------- | ------------------ | --------- | ------------- |
| W/O Head₃    | 0.040      | **0.015**        | **1.721**      | 29.10              | 29.62     | 16.94         |
| **W/ Head₃** | **0.037**  | 0.016            | 1.782          | **32.06**          | **29.87** | **23.10**     |

실내 평가 데이터셋은 움직임·시점 변화가 작아 ATE 개선폭이 작지만, 3D 트래킹에서는
PStudio APD가 16.94 → 23.10으로 크게 오른다.

### Supported Tasks

| Task                | Description                 | Advantage        |
| ------------------- | --------------------------- | ---------------- |
| Video Depth         | Temporally consistent depth | Handles motion   |
| 3D Tracking         | Point tracking in 3D        | Occlusion robust |
| Pose Estimation     | Camera pose recovery        | Dynamic scenes   |
| Motion Segmentation | Dynamic mask prediction     | Unified output   |

## 💡 Insights & Impact

### Solving Dynamic Scene Challenges

**Problem**: DUSt3R excels at static but fails with motion

- Implicit matching ambiguous for moving objects
- No temporal understanding
- Scale inconsistency across frames

**POMATO Solution**:

- Explicit 3D matching relationships
- Dedicated temporal motion module
- Unified coordinate system
- Scale-consistent reconstruction

### Technical Advantages

1. **Unified Framework**: Single model for multiple dynamic tasks
2. **No External Dependencies**: Self-contained architecture
3. **Two-Stage Efficiency**: Leverages pre-trained geometry
4. **Explicit Better**: Direct matching more robust

### Applications

- **Autonomous Vehicles**: Dynamic scene understanding
- **Robotics**: Real-time motion perception
- **AR/VR**: Dynamic environment reconstruction
- **Video Analysis**: 3D motion tracking
- **Content Creation**: Dynamic 3D from video

## 🔗 Related Work

### Building On

- **[DUSt3R](../foundation/dust3r.md)**: Pointmap representation foundation
- **Feed-forward 3D**: End-to-end paradigm
- **Video Understanding**: Temporal modeling

### Comparison with Dynamic Methods

| Method                | Approach     | Matching     | Temporal |
| --------------------- | ------------ | ------------ | -------- |
| [MonST3R](monst3r.md) | Per-frame    | Implicit     | Limited  |
| [D²USt3R](d2ust3r.md) | 4D pointmaps | Implicit     | Yes      |
| **POMATO**            | **Unified**  | **Explicit** | **Yes**  |

### Enables

- Better dynamic reconstruction methods
- Unified video 3D understanding
- Real-time dynamic applications

## 📚 Key Takeaways

POMATO demonstrates that:

1. **Explicit beats implicit**: Direct matching improves dynamics
2. **Temporal essential**: Motion modules crucial for video
3. **Two-stage works**: Leverage existing geometry knowledge
4. **Unified better**: Single framework for multiple tasks

The marriage of pointmap matching with temporal motion represents a significant advancement in dynamic 3D reconstruction, showing how DUSt3R's foundations can be effectively extended for complex real-world scenarios.

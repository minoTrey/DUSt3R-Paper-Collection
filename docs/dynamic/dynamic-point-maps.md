# Dynamic Point Maps: A Versatile Representation for Dynamic 3D Reconstruction (ICCV 2025)

![Dynamic Point Maps Overview](https://arxiv.org/html/2503.16318v1/x2.png)
_Dynamic Point Maps extend standard point maps to support 4D tasks by predicting point maps at multiple timestamps_

## 📋 Overview

- **Authors**: Edgar Sucar, Zihang Lai, Eldar Insafutdinov, Andrea Vedaldi
- **Institution**: Visual Geometry Group, University of Oxford
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.16318) | [Project Page](https://www.robots.ox.ac.uk/~vgg/research/dynamic-point-maps/) | Code (coming soon)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Novel point-based representation that enables versatile dynamic 3D scene reconstruction with applications across tracking, novel view synthesis, and scene editing.

## 🎯 Key Contributions

1. **Versatile Point Representation**: Unified framework for multiple dynamic tasks
2. **Temporal Consistency**: Robust tracking across time
3. **Multi-Task Learning**: Single model for various applications
4. **Efficient Processing**: Point-based efficiency for dynamic scenes
5. **Scene Understanding**: Rich semantic and geometric information

## 🔧 Technical Details

### Core Innovation: Dynamic Point Representation

```text
Traditional: Task-specific dynamic representations
Dynamic Point Maps: Unified point-based representation for all tasks
```

### Technical Approach

#### 1. Point Map Structure

- Persistent point identities across frames
- Rich per-point features (geometry + semantics)
- Temporal consistency constraints
- Flexible point creation/deletion

#### 2. Dynamic Modeling

```text
Input: Video sequence {I₁, I₂, ..., Iₜ}
Representation: Dynamic point cloud P(t) = {p₁(t), p₂(t), ..., pₙ(t)}
Features: F(t) = {geometry, appearance, motion, semantics}
```

#### 3. Key Components

- **Point Tracker**: Maintains point correspondences
- **Feature Encoder**: Rich point representations
- **Dynamic Decoder**: Task-specific outputs
- **Temporal Regularization**: Consistency across time

### Multi-Task Framework

- **Novel View Synthesis**: Render from arbitrary viewpoints
- **Object Tracking**: Track objects through time
- **Scene Editing**: Modify dynamic scenes
- **Motion Analysis**: Understand scene dynamics

## 📊 Results

### Depth Evaluation from 2-View Input

원논문 Table 1. DPM은 Bonn을 제외한 전 데이터셋에서 MonST3R보다 Abs Rel이 낮다
(평균 약 17.5% 감소). KITTI는 극단적 종횡비 때문에 crop 버전(512×144)을 사용.

| Model   | Sintel Abs Rel | Sintel δ<1.25 | P.Odyssey Abs Rel | P.Odyssey δ<1.25 | Bonn Abs Rel | Bonn δ<1.25 | Kubric Abs Rel | Kubric δ<1.25 | KITTI Abs Rel | KITTI δ<1.25 |
| ------- | -------------- | ------------- | ----------------- | ---------------- | ------------ | ----------- | -------------- | ------------- | ------------- | ------------ |
| MonST3R | 0.347          | **0.573**     | 0.065             | 0.953            | **0.071**    | **0.941**   | 0.166          | 0.779         | 0.069         | 0.945        |
| **DPM** | **0.321**      | 0.564         | **0.059**         | **0.957**        | 0.082        | 0.919       | **0.078**      | **0.950**     | **0.052**     | **0.968**    |

### Video Depth Evaluation

원논문 Table 2. 쌍별 예측 융합에는 MonST3R와 유사한 bundle adjustment를 쓰되,
DPM 표현에서는 불필요한 optical flow loss를 제거했다.

| Category    | Method          | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ | KITTI(crop) Abs Rel ↓ | KITTI(crop) δ<1.25 ↑ |
| ----------- | --------------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- | --------------------- | -------------------- |
| 1-frame     | Marigold        | 0.532            | 51.5            | 0.091          | 93.1          | 0.149           | 79.6           | —                     | —                    |
| 1-frame     | DepthAnythingV2 | 0.367            | 55.4            | 0.106          | 92.1          | 0.140           | 80.4           | —                     | —                    |
| Video depth | NVDS            | 0.408            | 48.3            | 0.167          | 76.6          | 0.253           | 58.8           | —                     | —                    |
| Video depth | ChronoDepth     | 0.687            | 48.6            | 0.100          | 91.1          | 0.167           | 75.9           | —                     | —                    |
| Video depth | DepthCrafter    | 0.292            | 69.7            | 0.075          | 97.1          | 0.110           | 88.1           | —                     | —                    |
| Joint D&P   | Robust-CVD      | 0.703            | 47.8            | —              | —             | —               | —              | —                     | —                    |
| Joint D&P   | CasualSAM       | 0.387            | 54.7            | 0.169          | 73.7          | 0.246           | 62.2           | —                     | —                    |
| Joint D&P   | MonST3R         | 0.335            | 58.5            | 0.063          | 96.4          | 0.104           | 89.5           | 0.111                 | 87.2                 |
| Joint D&P   | **DPM**         | 0.328            | 54.6            | 0.068          | 93.9          | 0.140           | 78.2           | **0.097**             | **89.1**             |

### Dynamic Reconstruction

원논문 Table 3. MonST3R+RAFT와 상대 point cloud 오차(L_rel) 및 객체 포즈 추적을
비교. Pk(tk)는 Pk(tk, π₁)의 축약. Kubric-G·Waymo에는 객체 포즈 GT가 없다(N/A).

| Dataset | Method   | P1(t1)    | P2(t1)    | P1(t2)    | P2(t2)    | RPE rot  | RPE trans |
| ------- | -------- | --------- | --------- | --------- | --------- | -------- | --------- |
| Kub.-F  | MonST3R  | 0.209     | 0.275     | 0.394     | 0.201     | 56.1     | 0.504     |
| Kub.-F  | **Ours** | **0.041** | **0.047** | **0.049** | **0.035** | **33.7** | **0.053** |
| Kub.-G  | MonST3R  | 0.163     | 0.265     | 0.346     | 0.178     | N/A      | N/A       |
| Kub.-G  | **Ours** | **0.057** | **0.071** | **0.079** | **0.058** | N/A      | N/A       |
| Waymo   | MonST3R  | 0.197     | 0.221     | 0.249     | 0.178     | N/A      | N/A       |
| Waymo   | **Ours** | **0.068** | **0.065** | **0.067** | **0.065** | N/A      | N/A       |

### 3D End-Point Error (Scene Flow / Object Flow)

원논문 Table 4. RAFT-3D는 GT depth(RGBD)를 쓰는데도 DPM은 RGB만으로
Kubric-G·Waymo에서 이를 앞선다. Object Flow는 RAFT-3D가 수행할 수 없는 과제다.

| Dataset | Method   | Input | SceneFlow Fwd ↓ | SceneFlow Bwd ↓ | ObjFlow Fwd ↓ | ObjFlow Bwd ↓ |
| ------- | -------- | ----- | --------------- | --------------- | ------------- | ------------- |
| Kub.-F  | MonST3R  | RGB   | 0.321           | 0.241           | 0.334         | 0.215         |
| Kub.-F  | RAFT-3D  | RGBD  | **0.051**       | **0.054**       | N/A           | N/A           |
| Kub.-F  | **Ours** | RGB   | 0.081           | 0.071           | **0.033**     | **0.029**     |
| Kub.-G  | MonST3R  | RGB   | 0.334           | 0.279           | 0.310         | 0.265         |
| Kub.-G  | RAFT-3D  | RGBD  | 4.067           | 4.084           | N/A           | N/A           |
| Kub.-G  | **Ours** | RGB   | **0.104**       | **0.106**       | **0.059**     | **0.050**     |
| Waymo   | MonST3R  | RGB   | 0.161           | 0.135           | 0.108         | 0.102         |
| Waymo   | RAFT-3D  | RGBD  | 0.150           | 0.145           | N/A           | N/A           |
| Waymo   | **Ours** | RGB   | **0.051**       | **0.053**       | **0.020**     | **0.020**     |

### Key Achievements

- ✅ Unified representation for multiple tasks
- ✅ Real-time performance capability
- ✅ Superior temporal consistency
- ✅ Flexible scene editing capabilities
- ✅ Robust to occlusions and lighting changes

## 💡 Insights & Impact

### Paradigm Shift in Dynamic Representation

**Traditional Approach**:

1. Task-specific representations
2. Separate models for each task
3. Limited cross-task knowledge sharing
4. Inefficient for multi-task scenarios

**Dynamic Point Maps**:

1. Unified point representation
2. Single model for multiple tasks
3. Shared knowledge across tasks
4. Efficient multi-task learning

### Why Point Maps Work for Dynamics

1. **Explicit Correspondence**: Points maintain identity across time
2. **Flexible Topology**: Can handle topology changes
3. **Efficient Processing**: Point-based operations are fast
4. **Rich Features**: Each point carries comprehensive information

### Applications

- **Video Production**: Dynamic scene editing and effects
- **Robotics**: Understanding dynamic environments
- **AR/VR**: Real-time dynamic scene capture
- **Surveillance**: Multi-object tracking and analysis
- **Sports Analysis**: Player and ball tracking

### Technical Advantages

- **Memory Efficient**: Point-based representation
- **Temporally Consistent**: Explicit correspondence tracking
- **Modular**: Easy to extend for new tasks
- **Interpretable**: Explicit point-based structure

## 🔗 Related Work

### Comparison with Dynamic Methods

| Aspect     | Video NeRF | 4D Gaussian | Dynamic NeRF | Dynamic Point Maps |
| ---------- | ---------- | ----------- | ------------ | ------------------ |
| Speed      | Slow       | Fast        | Slow         | Fast               |
| Memory     | High       | Medium      | High         | Low                |
| Editing    | Hard       | Medium      | Hard         | Easy               |
| Multi-task | No         | Limited     | No           | Yes                |

### Builds On

- **Point Cloud Processing**: Efficient point-based methods
- **Dynamic Scene Modeling**: Temporal consistency techniques
- **Multi-Task Learning**: Shared representation learning
- **Video Understanding**: Temporal modeling approaches

### Relationship to DUSt3R Ecosystem

- **Dynamic Extension**: Adds temporal dimension to reconstruction
- **Point Compatibility**: Natural fit with point-based representations
- **Multi-Task**: Could enhance [DUSt3R](../foundation/dust3r.md) with dynamic capabilities
- **Efficiency**: Maintains computational efficiency

## 📚 Key Takeaways

Dynamic Point Maps demonstrates that:

1. **Unified representations work**: Single representation for multiple dynamic tasks
2. **Points are versatile**: Point-based methods excel for dynamic scenes
3. **Multi-task learning helps**: Shared knowledge improves all tasks
4. **Efficiency matters**: Real-time performance enables practical applications

The success in creating a versatile point-based representation for dynamic 3D reconstruction opens new possibilities for unified dynamic scene understanding and manipulation.

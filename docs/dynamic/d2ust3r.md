# D²USt3R: Enhancing 3D Reconstruction with 4D Pointmaps for Dynamic Scenes (arXiv preprint)

![D²USt3R Teaser](https://cvlab-kaist.github.io/DDUSt3R/assets/1_teaser.png)
_D²USt3R extends DUSt3R to 4D pointmaps, accurately establishing dense correspondence in both static and dynamic regions_

## 📋 Overview

- **Authors**: Jisang Han, Honggyu An, Jaewoo Jung, Takuya Narihira, Junyoung Seo, Kazumi Fukuda, Chaehyun Kim, Sunghwan Hong, Yuki Mitsufuji, Seungryong Kim
- **Institution**: KAIST AI, Sony AI, Korea University
- **Venue**: arXiv preprint
- **Links**: [Paper](https://arxiv.org/abs/2504.06264) | [Code](https://github.com/cvlab-kaist/DDUSt3R) | [Project Page](https://cvlab-kaist.github.io/DDUSt3R/)
- **TL;DR**: Extends DUSt3R from 3D to 4D pointmaps, enabling accurate reconstruction of dynamic scenes through spatio-temporal correspondence.

## 🎯 Key Contributions

1. **4D Pointmap Representation**: First to extend DUSt3R's 3D pointmaps to 4D (space + time)
2. **Spatio-temporal Correspondence**: Unified handling of spatial and temporal relationships
3. **Optical Flow Integration**: Incorporates flow and cycle consistency for dynamics
4. **Feed-forward Efficiency**: Maintains DUSt3R's efficient architecture
5. **Dynamic Scene Handling**: Accurate reconstruction with moving objects

## 🔧 Technical Details

### Core Innovation: 3D → 4D Extension

```text
DUSt3R: (X, Y, Z) pointmaps for static scenes
D²USt3R: (X, Y, Z, T) pointmaps for dynamic scenes
```

### Key Technical Components

#### 1. 4D Pointmap Regression

- Extends spatial coordinates with temporal dimension
- Captures object motion trajectories
- Maintains per-pixel dense predictions

#### 2. Spatio-temporal Matching

- **Spatial**: Traditional 3D geometry constraints
- **Temporal**: Optical flow and motion consistency
- **Joint**: Unified optimization framework

#### 3. Cycle Consistency

- Enforces temporal coherence
- Handles occlusions and disocclusions
- Improves dynamic object tracking

### Architecture Modifications

- **Base**: DUSt3R transformer architecture
- **Extensions**:
  - Temporal encoding layers
  - Flow prediction heads
  - 4D coordinate regression
- **Efficiency**: Still feed-forward, no iterative optimization

## 📊 Results

### Multi-Frame Depth Estimation — TUM-Dynamics & Bonn

원논문 Table 3 (일부). 전체 장면과 동적 영역을 나눠 평가한다. 동적 영역 평가는
동적 부분이 식별 가능한 경우에만 수행. \*: 본 논문과 동일 데이터셋으로 재현.

| Category           | Method          | TUM All AbsRel ↓ | TUM All δ1 ↑ | TUM Dyn AbsRel ↓ | TUM Dyn δ1 ↑ | Bonn All AbsRel ↓ | Bonn All δ1 ↑ | Bonn Dyn AbsRel ↓ | Bonn Dyn δ1 ↑ |
| ------------------ | --------------- | ---------------- | ------------ | ---------------- | ------------ | ----------------- | ------------- | ----------------- | ------------- |
| Single-frame depth | DepthAnythingv2 | **0.098**        | **89.0**     | —                | —            | 0.073             | 93.8          | —                 | —             |
| Single-frame depth | Marigold        | 0.205            | 72.3         | —                | —            | 0.066             | 96.4          | —                 | —             |
| Multi-frame depth  | DUSt3R          | 0.176            | 76.5         | 0.221            | 71.3         | 0.135             | 82.4          | 0.127             | 83.7          |
| Multi-frame depth  | MASt3R          | 0.165            | 79.0         | 0.199            | 73.8         | 0.183             | 77.5          | 0.167             | 79.5          |
| Multi-frame depth  | MonST3R         | 0.145            | 81.2         | 0.152            | 79.2         | 0.068             | 94.4          | 0.066             | 94.9          |
| Multi-frame depth  | MonST3R\*       | 0.159            | 81.0         | 0.181            | 76.5         | 0.076             | 93.9          | 0.071             | 94.4          |
| Multi-frame depth  | **D²USt3R**     | 0.142            | 83.9         | **0.148**        | **82.9**     | **0.060**         | **95.8**      | **0.059**         | **95.7**      |

### Multi-Frame Depth Estimation — Sintel & KITTI

원논문 Table 3 (나머지). 이 두 데이터셋에서는 D²USt3R가 최고가 아니다.

| Method      | Sintel All AbsRel ↓ | Sintel All δ1 ↑ | Sintel Dyn AbsRel ↓ | Sintel Dyn δ1 ↑ | KITTI AbsRel ↓ | KITTI δ1 ↑ |
| ----------- | ------------------- | --------------- | ------------------- | --------------- | -------------- | ---------- |
| DUSt3R      | 0.370               | 58.5            | 0.672               | 54.9            | 0.076          | 93.6       |
| MASt3R      | 0.330               | 57.3            | **0.528**           | **54.4**        | **0.050**      | **96.8**   |
| MonST3R     | 0.345               | 56.2            | 0.525               | 46.9            | 0.070          | 95.0       |
| MonST3R\*   | 0.349               | 52.5            | 0.565               | 36.9            | 0.103          | 90.9       |
| **D²USt3R** | **0.324**           | 57.5            | 0.568               | 48.0            | 0.104          | 90.7       |

### Single-Frame Depth Estimation

원논문 Table 4. \*: 본 논문과 동일 데이터셋으로 재현.

| Method      | Bonn AbsRel ↓ | Bonn δ1 ↑ | Sintel AbsRel ↓ | Sintel δ1 ↑ | KITTI AbsRel ↓ | KITTI δ1 ↑ | NYU-v2 AbsRel ↓ | NYU-v2 δ1 ↑ | TUM AbsRel ↓ | TUM δ1 ↑ |
| ----------- | ------------- | --------- | --------------- | ----------- | -------------- | ---------- | --------------- | ----------- | ------------ | -------- |
| DUSt3R      | 0.141         | 82.5      | 0.424           | **58.7**    | 0.112          | 86.3       | **0.080**       | **90.7**    | 0.176        | 76.8     |
| MASt3R      | 0.142         | 82.0      | 0.354           | 57.9        | **0.076**      | **93.2**   | 0.129           | 84.9        | 0.160        | 78.7     |
| MonST3R     | 0.076         | 93.9      | 0.345           | 56.5        | 0.101          | 89.3       | 0.091           | 88.8        | **0.147**    | 81.1     |
| MonST3R\*   | 0.083         | 93.6      | 0.387           | 50.6        | 0.143          | 85.0       | 0.084           | 90.1        | 0.163        | 79.1     |
| **D²USt3R** | **0.065**     | **95.2**  | **0.340**       | 58.4        | 0.131          | 86.2       | 0.085           | 90.1        | 0.150        | **82.9** |

### Camera Pose Estimation

원논문 Table 5. \*: 본 논문과 동일 데이터셋으로 재현.

| Method      | Sintel Rot Avg ↓ | Sintel Rot Med ↓ | Sintel Trans Avg ↓ | Sintel Trans Med ↓ | TUM Rot Avg ↓ | TUM Rot Med ↓ | TUM Trans Avg ↓ | TUM Trans Med ↓ |
| ----------- | ---------------- | ---------------- | ------------------ | ------------------ | ------------- | ------------- | --------------- | --------------- |
| DUSt3R      | 6.15             | 4.51             | 0.29               | 0.26               | 2.36          | 0.98          | **0.013**       | **0.01**        |
| MASt3R      | **4.71**         | 3.40             | **0.23**           | **0.19**           | 2.83          | 1.13          | 0.06            | 0.03            |
| MonST3R     | 4.90             | **2.30**         | 0.26               | 0.22               | 1.88          | 1.39          | 0.019           | 0.01            |
| MonST3R\*   | 8.50             | 2.61             | 0.27               | 0.23               | **1.76**      | 1.40          | 0.02            | 0.01            |
| **D²USt3R** | 6.96             | 2.67             | 0.26               | 0.22               | 1.80          | 1.41          | 0.03            | 0.02            |

| Method      | ScanNet Rot Avg ↓ | ScanNet Rot Med ↓ | ScanNet Trans Avg ↓ | ScanNet Trans Med ↓ |
| ----------- | ----------------- | ----------------- | ------------------- | ------------------- |
| DUSt3R      | **0.74**          | **0.54**          | 0.11                | 0.08                |
| MASt3R      | 0.85              | 0.64              | **0.05**            | **0.04**            |
| MonST3R     | 0.94              | 0.79              | 0.10                | 0.08                |
| MonST3R\*   | **0.74**          | 0.58              | 0.10                | 0.08                |
| **D²USt3R** | 0.75              | 0.57              | 0.08                | 0.06                |

### Pointmap Alignment in Dynamic Objects

원논문 Table 6. Flow End-Point Error (EPE) ↓. Croco-Flow는 Sintel로 학습했기에
Sintel 평가에서 회색 처리(비교 대상 제외)됐다.

| Method                   | Sintel-Clean | Sintel-Final | KITTI    |
| ------------------------ | ------------ | ------------ | -------- |
| DUSt3R                   | 30.96        | 35.11        | 14.19    |
| MASt3R                   | 39.37        | 39.50        | 13.27    |
| MonST3R                  | 38.47        | 41.92        | 14.91    |
| MonST3R\*                | 37.47        | 40.58        | 14.58    |
| **D²USt3R**              | **16.19**    | **25.31**    | **8.91** |
| Croco-Flow (Sintel 학습) | 3.31         | 4.28         | 13.24    |
| SEA-RAFT                 | 5.21         | 13.18        | 4.43     |
| D²USt3R + Flow head      | 9.25         | 12.77        | 3.57     |

### Ablation: Training Strategy

원논문 Table 7. 전체 fine-tuning보다 디코더와 head만 학습하는 편이 낫다.

| Method                      | TUM AbsRel ↓ | TUM δ1 ↑ | Bonn AbsRel ↓ | Bonn δ1 ↑ |
| --------------------------- | ------------ | -------- | ------------- | --------- |
| Full finetune               | 0.161        | 77.0     | 0.081         | 91.9      |
| **Finetune decoder & head** | **0.142**    | **83.9** | **0.060**     | **95.8**  |

### Key Achievements

- ✅ First 4D extension of DUSt3R
- ✅ Handles complex object motions
- ✅ Maintains feed-forward efficiency
- ✅ Works on various dynamic datasets
- ✅ No camera calibration needed

## 💡 Insights & Impact

### Solving Dynamic Scene Challenges

**Traditional DUSt3R Limitations**:

1. Assumes static scenes
2. Fails with moving objects
3. No temporal reasoning
4. Limited to snapshots

**D²USt3R Solutions**:

1. 4D representation captures motion
2. Explicit dynamic modeling
3. Temporal consistency built-in
4. Works on video sequences

### Technical Advantages

- **Unified Framework**: Space and time in single model
- **No Motion Segmentation**: Handles all pixels equally
- **Robust to Complex Motion**: Non-rigid, multi-object
- **Maintains Simplicity**: Still feed-forward

### Applications

- **Video Understanding**: Full 4D reconstruction
- **Robotics**: Dynamic environment mapping
- **AR/VR**: Real-world capture with motion
- **Autonomous Driving**: Moving object reconstruction
- **Sports Analysis**: Dynamic scene capture

### Limitations

- Increased computational cost (4D vs 3D)
- Requires temporal sequences (not single images)
- Memory scales with sequence length
- Limited by motion complexity

## 🔗 Related Work

### Comparison with Other Dynamic Methods

- **MonST3R**: Simple per-frame approach
- **Easi3R**: Training-free motion extraction
- **CUT3R**: Recurrent state tracking
- **D²USt3R**: Unified 4D representation

### Builds On

- **DUSt3R**: Base 3D architecture
- **Optical Flow**: Motion estimation
- **4D Representations**: Spatio-temporal modeling

## 📚 Key Takeaways

D²USt3R demonstrates that:

1. **4D is natural**: Extending to time dimension is logical
2. **Unified is better**: Joint spatio-temporal beats separate
3. **Feed-forward scales**: Efficiency maintained with complexity
4. **Dynamic world needs dynamic models**: Static assumptions limit real-world use

The extension from 3D to 4D pointmaps represents a crucial advancement for practical applications where the world isn't static, maintaining DUSt3R's elegance while adding essential temporal reasoning capabilities.

# Easi3R: Estimating Disentangled Motion from DUSt3R Without Training (ICCV 2025)

![Easi3R Pipeline](https://easi3r.github.io/static/images/fig_pipe.png)
_Easi3R extracts motion information from DUSt3R's attention maps without any additional training_

## 📋 Overview

- **Authors**: Xingyu Chen, Yue Chen, Yuliang Xiu, Andreas Geiger, Anpei Chen
- **Institution**: MPI-IS, University of Tübingen, ETH Zürich
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.24391) | [Code](https://github.com/Inception3D/Easi3R) | [Project Page](https://easi3r.github.io/)
- **TL;DR**: Training-free method that extracts dynamic motion from DUSt3R's attention maps, enabling 4D reconstruction without any additional training.

## 🎯 Key Contributions

1. **Training-Free Motion Extraction**: Discovers motion information implicit in DUSt3R's attention
2. **Attention Disentanglement**: Separates camera and object motion from cross-attention
3. **Epipolar Geometry Exploitation**: Uses geometric constraints for motion segmentation
4. **Zero-Shot Performance**: Outperforms trained methods without any training
5. **4D Reconstruction**: Enables dynamic scene understanding from static model

## 🔧 Technical Details

### Core Innovation: Attention Mining

```text
DUSt3R attention → Motion information already exists
Easi3R → Extract and disentangle without training
```

### Technical Approach

#### 1. Attention Analysis

- Cross-attention in DUSt3R encodes motion implicitly
- Low attention → Epipolar geometry violation → Motion
- High attention → Static correspondences
- Aggregation reveals motion patterns

#### 2. Four Semantic Attention Maps

1. **Camera motion map**: Global ego-motion
2. **Object motion map**: Moving objects
3. **Static region map**: Background
4. **Occlusion map**: Visibility changes

#### 3. Motion Disentanglement Process

```python
# Conceptual flow
cross_attention = dust3r.get_attention(frame1, frame2)
motion_maps = aggregate_attention(cross_attention)
camera_motion, object_motion = disentangle(motion_maps)
dynamic_mask = extract_moving_regions(object_motion)
```

#### 4. Integration Pipeline

- Extract attention from pre-trained DUSt3R
- Aggregate across spatial/temporal dimensions
- Apply epipolar filtering
- Optional: Refine with SAM2
- Generate 4D pointmaps

### Key Design Principles

- **No Training**: Pure inference-time adaptation
- **No Architecture Changes**: Uses vanilla DUSt3R
- **Geometric Grounding**: Epipolar constraints guide segmentation
- **Modular**: Can enhance any DUSt3R variant

## 📊 Results

### Dynamic Object Segmentation on DAVIS

원논문 Table 1. JM = IoU mean, JR = IoU recall. Flow는 optical flow 사용 여부.
`w/ SAM2`는 출력을 SAM2 프롬프트로 쓴 강화 설정이다. 열 폭 제한으로 두 표로 나눴다.

| Method                       | Flow | D16 JM ↑ (w/o) | D16 JR ↑ (w/o) | D16 JM ↑ (w/) | D16 JR ↑ (w/) | D17 JM ↑ (w/o) | D17 JR ↑ (w/o) | D17 JM ↑ (w/) | D17 JR ↑ (w/) |
| ---------------------------- | ---- | -------------- | -------------- | ------------- | ------------- | -------------- | -------------- | ------------- | ------------- |
| DUSt3R                       | ✓    | 42.1           | 45.7           | 58.5          | 63.4          | 35.2           | 35.3           | 48.7          | 50.2          |
| MonST3R                      | ✓    | 40.9           | 42.2           | 64.3          | 73.3          | 38.6           | 38.2           | 56.4          | 59.6          |
| DAS3R                        | ✗    | 41.6           | 39.0           | 54.2          | 55.8          | 43.5           | 42.1           | 57.4          | 61.3          |
| Easi3R<sub>dust3r</sub>      | ✗    | 53.1           | 60.4           | 67.9          | 71.4          | 49.0           | 56.4           | 60.1          | 65.3          |
| **Easi3R<sub>monst3r</sub>** | ✗    | **57.7**       | **71.6**       | **70.7**      | **79.9**      | **56.5**       | **68.6**       | **67.9**      | **76.1**      |

| Method                       | Flow | DAVIS-all JM ↑ (w/o) | DAVIS-all JR ↑ (w/o) | DAVIS-all JM ↑ (w/) | DAVIS-all JR ↑ (w/) |
| ---------------------------- | ---- | -------------------- | -------------------- | ------------------- | ------------------- |
| DUSt3R                       | ✓    | 35.9                 | 34.0                 | 47.6                | 48.7                |
| MonST3R                      | ✓    | 36.7                 | 34.3                 | 51.9                | 54.1                |
| DAS3R                        | ✗    | 43.4                 | 38.7                 | 53.9                | 54.8                |
| Easi3R<sub>dust3r</sub>      | ✗    | 44.5                 | 49.6                 | 54.7                | 60.6                |
| **Easi3R<sub>monst3r</sub>** | ✗    | **53.0**             | **63.4**             | **63.1**            | **72.6**            |

Flow 없이도 동적 마스크 레이블로 명시적으로 학습한 DAS3R을 넘어선다.

### Camera Pose Estimation: Easi3R를 붙였을 때의 이득

원논문 Table 2. 같은 백본에 Easi3R를 얹은 전후 비교 (plug-and-play).

| Method                      | Flow | DyCheck ATE ↓ | DyCheck RTE ↓ | DyCheck RRE ↓ | ADT ATE ↓ | ADT RTE ↓ | ADT RRE ↓ | TUM ATE ↓ | TUM RTE ↓ | TUM RRE ↓ |
| --------------------------- | ---- | ------------- | ------------- | ------------- | --------- | --------- | --------- | --------- | --------- | --------- |
| DUSt3R                      | ✗    | 0.035         | 0.030         | 2.323         | 0.042     | 0.025     | 1.212     | 0.100     | 0.087     | 2.692     |
| Easi3R<sub>dust3r</sub>     | ✗    | 0.029         | 0.025         | 1.774         | 0.040     | 0.021     | 0.880     | 0.093     | 0.076     | 2.366     |
| DUSt3R                      | ✓    | 0.029         | 0.021         | 1.875         | 0.076     | 0.030     | 0.974     | 0.071     | 0.067     | 3.711     |
| **Easi3R<sub>dust3r</sub>** | ✓    | **0.021**     | **0.014**     | **1.092**     | 0.042     | **0.015** | 0.655     | **0.070** | **0.061** | **2.361** |
| MonST3R                     | ✗    | 0.040         | 0.034         | 1.820         | 0.045     | 0.024     | 0.759     | 0.183     | 0.148     | 6.985     |
| Easi3R<sub>monst3r</sub>    | ✗    | 0.038         | 0.032         | 1.736         | 0.045     | 0.024     | 0.715     | 0.184     | 0.149     | 6.311     |
| MonST3R                     | ✓    | 0.033         | 0.024         | 1.501         | 0.055     | 0.025     | 0.776     | 0.170     | 0.155     | 6.455     |
| Easi3R<sub>monst3r</sub>    | ✓    | 0.030         | 0.021         | 1.390         | **0.039** | 0.016     | **0.640** | 0.168     | 0.150     | 5.925     |

### Camera Pose Estimation: SOTA 비교

원논문 Table 3.

| Method                      | Flow | DyCheck ATE ↓ | DyCheck RTE ↓ | DyCheck RRE ↓ | ADT ATE ↓ | ADT RTE ↓ | ADT RRE ↓ | TUM ATE ↓ | TUM RTE ↓ | TUM RRE ↓ |
| --------------------------- | ---- | ------------- | ------------- | ------------- | --------- | --------- | --------- | --------- | --------- | --------- |
| DUSt3R                      | ✗    | 0.035         | 0.030         | 2.323         | 0.042     | 0.025     | 1.212     | 0.100     | 0.087     | 2.692     |
| CUT3R                       | ✗    | 0.029         | 0.020         | 1.383         | 0.084     | 0.025     | **0.490** | 0.079     | 0.088     | 10.41     |
| MonST3R                     | ✓    | 0.033         | 0.024         | 1.501         | 0.055     | 0.025     | 0.776     | 0.170     | 0.155     | 6.455     |
| DAS3R                       | ✓    | 0.033         | 0.022         | 1.467         | 0.040     | 0.017     | 0.685     | 0.173     | 0.157     | 8.341     |
| Easi3R<sub>monst3r</sub>    | ✓    | 0.030         | 0.021         | 1.390         | **0.039** | 0.016     | 0.640     | 0.168     | 0.150     | 5.925     |
| **Easi3R<sub>dust3r</sub>** | ✓    | **0.021**     | **0.014**     | **1.092**     | 0.042     | **0.015** | 0.655     | **0.070** | **0.061** | **2.361** |

### Point Cloud Reconstruction (DyCheck): Easi3R의 이득

원논문 Table 4.

| Method                      | Flow | Acc. Mean ↓ | Acc. Median ↓ | Comp. Mean ↓ | Comp. Median ↓ | Dist. Mean ↓ | Dist. Median ↓ |
| --------------------------- | ---- | ----------- | ------------- | ------------ | -------------- | ------------ | -------------- |
| DUSt3R                      | ✗    | 0.802       | 0.595         | 1.950        | 0.815          | 0.353        | 0.233          |
| Easi3R<sub>dust3r</sub>     | ✗    | 0.772       | 0.596         | 1.813        | 0.757          | 0.336        | 0.219          |
| DUSt3R                      | ✓    | 0.738       | 0.599         | 1.669        | 0.678          | 0.313        | 0.196          |
| **Easi3R<sub>dust3r</sub>** | ✓    | **0.703**   | **0.589**     | **1.474**    | **0.586**      | **0.301**    | **0.186**      |
| MonST3R                     | ✗    | 0.855       | 0.693         | 1.916        | 1.035          | 0.398        | 0.295          |
| Easi3R<sub>monst3r</sub>    | ✗    | 0.846       | 0.660         | 1.840        | 0.983          | 0.390        | 0.290          |
| MonST3R                     | ✓    | 0.851       | 0.689         | 1.734        | 0.958          | 0.353        | 0.254          |
| Easi3R<sub>monst3r</sub>    | ✓    | 0.834       | 0.643         | 1.661        | 0.916          | 0.350        | 0.255          |

### Point Cloud Reconstruction (DyCheck): SOTA 비교

원논문 Table 5.

| Method                      | Flow | Acc. Mean ↓ | Acc. Median ↓ | Comp. Mean ↓ | Comp. Median ↓ | Dist. Mean ↓ | Dist. Median ↓ |
| --------------------------- | ---- | ----------- | ------------- | ------------ | -------------- | ------------ | -------------- |
| DUSt3R                      | ✗    | 0.802       | 0.595         | 1.950        | 0.815          | 0.353        | 0.233          |
| CUT3R                       | ✗    | **0.458**   | **0.342**     | 1.633        | 0.792          | 0.326        | 0.229          |
| MonST3R                     | ✓    | 0.851       | 0.689         | 1.734        | 0.958          | 0.353        | 0.254          |
| DAS3R                       | ✓    | 1.772       | 1.438         | 2.503        | 1.548          | 0.475        | 0.352          |
| Easi3R<sub>monst3r</sub>    | ✓    | 0.834       | 0.643         | 1.661        | 0.916          | 0.350        | 0.255          |
| **Easi3R<sub>dust3r</sub>** | ✓    | 0.703       | 0.589         | **1.474**    | **0.586**      | **0.301**    | **0.186**      |

## 💡 Insights & Impact

### Why This Works

**Hidden Knowledge in DUSt3R**:

1. DUSt3R learns view transformations implicitly
2. Attention encodes geometric relationships
3. Violations indicate motion
4. No explicit motion supervision needed

### Practical Advantages

- **Zero Training Cost**: Immediate deployment
- **Universal**: Works with any DUSt3R checkpoint
- **Efficient**: Minimal computational overhead
- **Flexible**: Adapts to various motion types

### Comparison with Other Dynamic Methods

| Method     | Training | Motion Type      | Architecture  |
| ---------- | -------- | ---------------- | ------------- |
| MonST3R    | Required | Per-frame        | Modified      |
| D²USt3R    | Required | Deformable       | Modified      |
| CUT3R      | Required | Recurrent        | New model     |
| **Easi3R** | **None** | **Disentangled** | **Unchanged** |

### Applications

- **4D Content Creation**: From casual videos
- **Motion Analysis**: Scientific observation
- **Robotics**: Dynamic scene understanding
- **AR/VR**: Real-time environment tracking
- **Research**: Understanding model capabilities

## 🔗 Related Work

### Building On

- **[DUSt3R](../foundation/dust3r.md)**: Base architecture (unchanged)
- **Attention Mechanisms**: Information extraction
- **Epipolar Geometry**: Motion constraints

### Enables

- Training-free dynamic extensions
- Attention-based motion understanding
- Reinterpretation of existing models

### Comparison with MonST3R

- [MonST3R](monst3r.md): Trained, modified architecture
- Easi3R: Training-free, attention mining
- Both: Enable 4D reconstruction
- Easi3R advantage: No training, better accuracy

## 📚 Key Takeaways

Easi3R demonstrates that:

1. **Motion is already there**: DUSt3R implicitly encodes dynamics
2. **Training-free is possible**: Careful analysis beats brute force
3. **Attention tells stories**: Cross-attention reveals motion
4. **Simplicity wins**: No modifications needed

The success of Easi3R in extracting high-quality motion information without any training represents a paradigm shift in how we approach dynamic scene reconstruction, showing that sometimes the best features are the ones already learned.

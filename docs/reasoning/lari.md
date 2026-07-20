# LaRI: Layered Ray Intersections for Single-view 3D Geometric Reasoning (arXiv preprint)

![LaRI Teaser](https://raw.githubusercontent.com/ruili3/lari/main/assets/teaser.jpg)
_LaRI models multiple surface layers along camera rays, enabling reasoning about occluded geometry from single images_

## 📋 Overview

- **Authors**: Rui Li, Biao Zhang, Zhenyu Li, Federico Tombari, Peter Wonka
- **Institution**: KAUST and affiliates
- **Venue**: arXiv preprint (2025)
- **Links**: [Paper](https://arxiv.org/abs/2504.18424) | [Code](https://github.com/ruili3/lari) | [Demo](https://huggingface.co/spaces/ruili3/LaRI)
- **TL;DR**: Models multiple surface layers along camera rays from single images, enabling reasoning about occluded geometry with only 17% of parameters compared to large generative models.

## 🎯 Key Contributions

1. **Layered Point Maps**: Novel multi-surface representation along rays
2. **Ray Stopping Index**: Predicts valid intersections per pixel/layer
3. **Extreme Efficiency**: 17% parameters, 4% training data vs SOTA
4. **Unified Framework**: Single model for objects and scenes
5. **Occlusion Reasoning**: Sees beyond visible surfaces

## 🔧 Technical Details

### Core Innovation: Layered Ray Intersections

```text
Traditional: Single image → One depth/surface
LaRI: Single image → Multiple surfaces along each ray
```

### Architecture Design

#### 1. Layered Representation

- **Multiple Depths**: K surfaces per ray (K=4 typical)
- **Ray Parameterization**: Points along viewing rays
- **Occlusion Modeling**: Explicitly handles hidden surfaces
- **Compact Output**: Efficient multi-layer encoding

#### 2. Ray Stopping Index

```python
# Conceptual approach
for each_pixel:
    ray_surfaces = predict_K_intersections(pixel)
    valid_mask = predict_stopping_index(pixel)
    output = ray_surfaces[:valid_mask]
```

#### 3. Network Components

- **Backbone**: Efficient encoder (MoGe-based)
- **Decoder**: Lightweight heads for layers
- **Stopping Predictor**: Validity classification
- **Single Pass**: No iterative refinement

### Training Strategy

- **Synthetic Data**: Objaverse for objects
- **Real Data**: 3D-FRONT, ScanNet++ for scenes
- **Data Efficiency**: Only 4% of typical requirements
- **Initialization**: Pre-trained MoGe weights

## 📊 Results

### Object-Level Comparison on GSO

원논문 Table 1. View-aligned GT 설정 (scale-shift 정렬만 필요, 실제 응용에 부합).

| Method   | CD ↓      | FS@0.1 ↑  | FS@0.05 ↑ | FS@0.02 ↑ |
| -------- | --------- | --------- | --------- | --------- |
| SF3D     | 0.037     | 0.913     | 0.738     | 0.487     |
| SPAR3D   | 0.038     | 0.912     | 0.745     | 0.486     |
| TRELLIS  | 0.027     | 0.959     | 0.853     | 0.608     |
| **LaRI** | **0.025** | **0.966** | **0.894** | **0.643** |

원논문 Table 1. Canonical GT 설정 (brute-force search + ICP 정렬).

| Method   | CD ↓      | FS@0.1 ↑  | FS@0.05 ↑ | FS@0.02 ↑ |
| -------- | --------- | --------- | --------- | --------- |
| SF3D     | 0.036     | 0.916     | 0.754     | 0.513     |
| SPAR3D   | 0.037     | 0.916     | 0.759     | 0.506     |
| TRELLIS  | **0.027** | **0.960** | **0.856** | **0.611** |
| **LaRI** | 0.029     | 0.948     | 0.840     | 0.601     |

### Scene-Level Comparison on SCRREAM

원논문 Table 2. Visible / Unseen / Overall 영역별 평가. `-`는 unseen 영역을
추론할 수 없는 방법.

| Method      | Visible CD ↓ | Visible FS@0.05 ↑ | Unseen CD ↓ | Unseen FS@0.05 ↑ | Overall CD ↓ | Overall FS@0.05 ↑ |
| ----------- | ------------ | ----------------- | ----------- | ---------------- | ------------ | ----------------- |
| Metric3D-v2 | 0.063        | 0.534             | -           | -                | 0.086        | 0.473             |
| DepthPro    | 0.055        | 0.603             | -           | -                | 0.079        | 0.535             |
| DUSt3R      | 0.059        | 0.653             | -           | -                | 0.086        | 0.565             |
| MoGe        | **0.035**    | **0.786**         | -           | -                | **0.063**    | **0.668**         |
| CUT3R (i-5) | 0.071        | 0.658             | 0.192       | 0.238            | 0.091        | 0.543             |
| **LaRI**    | 0.057        | 0.589             | **0.077**   | **0.494**        | 0.059        | 0.590             |

### Efficiency

원논문 Table 5. 위 4행은 object-level, 아래 4행은 depth/point map 계열 비교.

| Method   | Params (M) | Inf. Time (ms) | FS@0.05 ↑ |
| -------- | ---------- | -------------- | --------- |
| SF3D     | 1006.0     | 123.1          | 0.738     |
| SPAR3D   | 2026.3     | 904.8          | 0.745     |
| TRELLIS  | 1795.7     | 733.7          | 0.853     |
| **LaRI** | **314.2**  | **31.5**       | **0.894** |
| DepthPro | 951.9      | 220.3          | 0.535     |
| DUSt3R   | 571.1      | 100.1          | 0.565     |
| MoGe     | 341.2      | 41.08          | 0.668     |
| **LaRI** | **314.1**  | **31.5**       | 0.590     |

### Ablation: LaRI Map Layer 수

원논문 Table 3. L = 5가 기본 설정.

| L     | GSO CD ↓  | GSO FS@0.1 ↑ | GSO FS@0.05 ↑ | SCRREAM CD ↓ | SCRREAM FS@0.1 ↑ | SCRREAM FS@0.05 ↑ |
| ----- | --------- | ------------ | ------------- | ------------ | ---------------- | ----------------- |
| 3     | 0.072     | 0.752        | 0.527         | 0.061        | 0.822            | **0.590**         |
| **5** | **0.025** | 0.966        | **0.894**     | **0.059**    | **0.825**        | **0.590**         |
| 8     | 0.027     | **0.967**    | 0.882         | 0.061        | 0.813            | 0.575             |

## 💡 Insights & Impact

### Paradigm Shift in Single-View 3D

**Traditional Limitations**:

- Only visible surfaces captured
- No reasoning about occlusions
- Limited scene understanding
- Requires multiple views for completeness

**LaRI Solution**:

- Multiple surfaces from one view
- Explicit occlusion modeling
- Complete scene reasoning
- Efficient single-pass inference

### Technical Advantages

1. **Layer-wise Understanding**: Natural occlusion handling
2. **Parameter Efficiency**: 83% reduction vs SOTA
3. **Data Efficiency**: 96% less training data
4. **Unified Architecture**: Objects and scenes

### Applications

- **Robotics**: Grasp planning for occluded objects
- **AR/VR**: Complete scene understanding
- **Autonomous Driving**: Hidden object awareness
- **3D Editing**: Manipulate occluded regions
- **Scene Completion**: Fill-in hidden areas

### Comparison with DUSt3R Ecosystem

| Aspect     | DUSt3R           | LaRI              |
| ---------- | ---------------- | ----------------- |
| Input      | Multi-view       | Single-view       |
| Output     | Single surface   | Multiple layers   |
| Focus      | Visible geometry | Complete geometry |
| Efficiency | Moderate         | High              |
| Occlusions | Limited          | Explicit          |

## 🔗 Related Work

### Building On

- **MoGe**: Monocular geometry estimation
- **Depth Estimation**: Single-view 3D
- **Amodal Perception**: Reasoning about occlusions
- **Efficient Architectures**: Lightweight models

### Enables

- Single-view complete reconstruction
- Efficient amodal reasoning
- Real-time occlusion handling
- Mobile 3D understanding

### Within Scene Reasoning

- Complements multi-view methods
- Enables new single-view applications
- Pushes efficiency boundaries
- Advances occlusion understanding

## 📚 Key Takeaways

LaRI demonstrates that:

1. **Layers matter**: Multiple surfaces crucial for understanding
2. **Efficiency possible**: 83% fewer parameters still works
3. **Single-view sufficient**: Can reason about occlusions
4. **Data efficiency**: Smart representations need less data

The introduction of layered ray intersections represents a fundamental advance in single-view 3D reasoning, showing that we can understand complete geometry including occlusions without requiring multiple views or massive models.

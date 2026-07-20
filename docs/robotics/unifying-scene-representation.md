# Unifying Scene Representation and Hand-Eye Calibration with 3D Foundation Models (RA-L 2024)

![Unified Framework Overview](https://arxiv.org/html/2404.11683v1/extracted/2404.11683v1/fig1.png)
_Unified framework for joint scene representation and hand-eye calibration using 3D foundation models without external markers_

## 📋 Overview

- **Authors**: Weiming Zhi, Haozhan Tang, Tianyi Zhang, Matthew Johnson-Roberson
- **Institution**: Carnegie Mellon University, University of Michigan
- **Venue**: RA-L 2024
- **Note**: 게재본 제목은 "Unifying Representation and Calibration With 3D Foundation Models"로
  arXiv 프리프린트와 다르다. RA-L 9(10):8953-8960, DOI
  [10.1109/LRA.2024.3451396](https://doi.org/10.1109/LRA.2024.3451396). ICRA 2025에서 발표.
- **Links**: [Paper](https://arxiv.org/abs/2404.11683) | [Published (IEEE)](https://ieeexplore.ieee.org/document/10659118/) | [Code](https://github.com/tomtang502/arm_3d_reconstruction)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Unified framework that simultaneously performs scene representation learning and hand-eye calibration using 3D foundation models for improved robotic perception and manipulation.

## 🎯 Key Contributions

1. **Unified Framework**: Joint scene representation and hand-eye calibration
2. **Foundation Model Integration**: Leverages 3D foundation models for robotics
3. **Simultaneous Optimization**: Co-optimization of representation and calibration
4. **Robotic Application**: Practical deployment for manipulation tasks
5. **Calibration-Free**: Reduces need for extensive manual calibration

## 🔧 Technical Details

### Core Innovation: Joint Optimization

```text
Traditional: Separate calibration → Scene representation → Manual alignment
Unified: Joint optimization → Automatic alignment → Robust performance
```

### Technical Approach

#### 1. Unified Optimization Framework

- Joint learning of scene representation and camera-robot calibration
- 3D foundation model as geometric backbone
- End-to-end optimization strategy
- Automatic parameter estimation

#### 2. Hand-Eye Calibration Integration

```text
Input: Robot poses + Camera images
Foundation Model: 3D scene understanding
Joint Optimization: Representation + Calibration parameters
Output: Calibrated system + Scene representation
```

#### 3. Key Components

- **3D Foundation Backbone**: DUSt3R or similar for geometry
- **Calibration Estimator**: Hand-eye transformation learning
- **Scene Encoder**: Rich 3D scene representation
- **Joint Loss**: Unified optimization objective

### Robotic Integration

- **Manipulation Planning**: 3D-aware motion planning
- **Perception**: Robust scene understanding
- **Calibration**: Automatic camera-robot alignment
- **Adaptation**: Dynamic recalibration capability

## 📊 Results

> 아래 수치는 `docs/papers/unifying_scene_representation.pdf`(arXiv 2404.11683v1) 기준이다.
> RA-L 게재본은 제목과 표 구성이 다를 수 있다.

### Hand-Eye Calibration: JCR vs COLMAP + Calibration

원논문 Table I. δt / δR은 캘리브레이션 잔차(residual, 낮을수록 좋음).
COLMAP은 이미지 수가 적으면 일부 포즈만 복원해 발산(NA)한다.

| Scene                | Images | Ours 수렴 | Ours δt | Ours δR | COLMAP 수렴 | COLMAP δt | COLMAP δR | COLMAP 복원 포즈 |
| -------------------- | ------ | --------- | ------- | ------- | ----------- | --------- | --------- | ---------------- |
| Light Tabletop (8개) | 10     | ✓         | 0.0420  | 0.0655  | ✗           | NA        | NA        | 2                |
| Light Tabletop (8개) | 12     | ✓         | 0.0419  | 0.0657  | ✗           | NA        | NA        | 2                |
| Light Tabletop (8개) | 15     | ✓         | 0.0396  | 0.0513  | ✗           | NA        | NA        | 2                |
| Light Tabletop (7개) | 10     | ✓         | 0.0208  | 0.0519  | ✓           | 0.0412    | 1.27      | 5                |
| Light Tabletop (7개) | 12     | ✓         | 0.0317  | 0.0623  | ✓           | 0.0412    | 1.27      | 5                |
| Light Tabletop (7개) | 15     | ✓         | 0.0357  | 0.0701  | ✓           | 0.0469    | 0.0662    | 10               |
| Dark Tabletop        | 10     | ✓         | 0.0310  | 0.0732  | ✗           | NA        | NA        | 4                |
| Dark Tabletop        | 12     | ✓         | 0.0536  | 0.0742  | ✗           | NA        | NA        | 4                |
| Dark Tabletop        | 15     | ✓         | 0.0414  | 0.0818  | ✓           | 0.0454    | 0.0503    | 10               |

### Scale Recovery: 물체 높이 오차

원논문 Fig. 4(a). 복원된 물체 높이와 실측값의 백분율 오차 (낮을수록 좋음).

| Images    | Tape | Box  | Mug  | Toolbox |
| --------- | ---- | ---- | ---- | ------- |
| 8 images  | 7.8% | 8.6% | 1.2% | 1.2%    |
| 10 images | 2.5% | 2.9% | 3.1% | 0.7%    |

10장을 쓰면 모든 물체의 높이 오차가 최대 3.1%로, 스케일이 정확히 복원됨을 보인다.

## 💡 Insights & Impact

### Paradigm Shift in Robotic Perception

**Traditional Approach**:

1. Manual hand-eye calibration
2. Separate scene representation
3. Error propagation between stages
4. Brittle to environmental changes

**Unified Framework**:

1. Automatic calibration learning
2. Joint representation optimization
3. End-to-end error handling
4. Adaptive to environmental changes

### Why Joint Optimization Works

1. **Error Compensation**: Joint learning compensates for individual errors
2. **Geometric Consistency**: 3D foundation models ensure consistency
3. **End-to-End**: Holistic optimization improves overall system
4. **Adaptability**: Dynamic adjustment to changes

### Applications

- **Industrial Automation**: Flexible manufacturing systems
- **Service Robotics**: Adaptive home/office robots
- **Medical Robotics**: Precise surgical systems
- **Field Robotics**: Outdoor manipulation tasks
- **Research Platforms**: Simplified robot setup

### Technical Advantages

- **Unified**: Single framework for multiple tasks
- **Automatic**: Reduced manual calibration effort
- **Robust**: Better handling of uncertainties
- **Adaptable**: Dynamic recalibration capability

## 🔗 Related Work

### Comparison with Calibration Methods

| Method             | Approach       | Accuracy | Setup Time | Robustness    |
| ------------------ | -------------- | -------- | ---------- | ------------- |
| Manual Calibration | Grid-based     | Good     | Hours      | Poor          |
| Auto Calibration   | Optimization   | Better   | Minutes    | Medium        |
| Learning-based     | Neural         | Good     | Fast       | Good          |
| **Unified**        | **Foundation** | **Best** | **Fast**   | **Excellent** |

### Builds On

- **Hand-Eye Calibration**: Camera-robot alignment techniques
- **3D Foundation Models**: Geometric understanding capabilities
- **Scene Representation**: 3D scene encoding methods
- **Robotic Perception**: Vision-based manipulation systems

### Relationship to DUSt3R Ecosystem

- **Foundation Integration**: Natural use of 3D foundation models
- **Robotic Extension**: Extends geometric understanding to robotics
- **Practical Impact**: Real-world deployment of foundation models
- **System Integration**: Shows how to integrate with robotic systems

## 📚 Key Takeaways

Unifying Scene Representation demonstrates that:

1. **Joint optimization superior**: Combined learning outperforms separate stages
2. **Foundation models practical**: 3D foundations enhance robotic systems
3. **Calibration automation**: Manual calibration can be largely automated
4. **End-to-end benefits**: Holistic approaches improve overall performance

The success in unifying scene representation and calibration using 3D foundation models represents a significant step toward more practical and robust robotic systems.

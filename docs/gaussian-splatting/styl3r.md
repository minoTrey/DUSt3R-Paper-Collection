# Styl3R: Instant 3D Stylized Reconstruction for Arbitrary Scenes and Styles (NeurIPS 2025)

![Styl3R Teaser](https://nickisdope.github.io/Styl3R/static/images/pipeline_v4.png)
_Styl3R achieves instant 3D stylized reconstruction from sparse unposed images and arbitrary style references in less than a second_

## 📋 Overview

- **Authors**: Peng Wang, Xiang Liu, Peidong Liu
- **Institution**: Zhejiang University, Westlake University
- **Venue**: NeurIPS 2025
- **Links**: [Paper](https://arxiv.org/abs/2505.21060) | [Project Page](https://nickisdope.github.io/Styl3R/) | [Code](https://github.com/WU-CVGL/Styl3R)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Real-time 3D stylized reconstruction system that applies artistic styles to 3D scenes during reconstruction, enabling instant stylized 3D content creation.

## 🎯 Key Contributions

1. **Instant Stylization**: Real-time 3D style transfer during reconstruction
2. **Arbitrary Scenes**: Works with diverse scene types and geometries
3. **Arbitrary Styles**: Supports wide range of artistic styles
4. **3D Consistency**: Maintains style coherence across viewpoints
5. **Unified Pipeline**: Single framework for reconstruction and stylization

## 🔧 Technical Details

### Core Innovation: 3D-Aware Style Transfer

```text
Traditional: 3D reconstruction → Post-process stylization → Inconsistencies
Styl3R: Style-aware 3D reconstruction → Consistent stylized 3D
```

### Technical Approach

#### 1. Style-Aware Reconstruction

- Joint optimization of geometry and style
- 3D-consistent style application
- Multi-view style coherence
- Real-time processing capability

#### 2. Stylization Pipeline

```text
Input: Images + Style reference
Process: Style-aware 3D reconstruction
Output: Stylized 3D scene representation
```

#### 3. Key Components

- **Style Encoder**: Extracts style features from reference
- **3D Reconstructor**: Geometry-aware scene building
- **Style Integrator**: Applies style to 3D representation
- **Consistency Enforcer**: Maintains multi-view coherence

### Style Transfer Architecture

- **Feature Extraction**: Multi-scale style features
- **3D Integration**: Geometric style application
- **Temporal Consistency**: Stable style across frames
- **Quality Control**: Maintains reconstruction accuracy

## 📊 Results

### Multi-view Consistency (RE10K)

원논문 Table 2. RAFT 광학 흐름으로 이전 프레임을 워핑해 타깃과 비교한 consistency
지표다. Short-range는 인접 뷰, Long-range는 7프레임 떨어진 뷰 사이. Stylization
Time은 IO를 제외한 처리 시간이다.

| Type | Method            | Short LPIPS↓ | Short RMSE↓ | Long LPIPS↓ | Long RMSE↓ | Stylization Time |
| ---- | ----------------- | ------------ | ----------- | ----------- | ---------- | ---------------- |
| 2D   | AdaIN             | 0.163        | 0.063       | 0.323       | 0.111      | **0.004 s**      |
| 2D   | AdaAttN           | 0.224        | 0.071       | 0.331       | 0.098      | 0.024 s          |
| 2D   | StyTr2            | 0.167        | 0.059       | 0.315       | 0.098      | 0.029 s          |
| 3D   | StyleRF           | 0.062        | 0.021       | 0.172       | 0.042      | 90 mins          |
| 3D   | StyleGaussian     | 0.048        | 0.022       | 0.137       | 0.043      | 132 mins         |
| 3D   | ARF               | 0.093        | 0.038       | 0.217       | 0.070      | 12 mins          |
| 3D   | **Styl3R (Ours)** | **0.044**    | 0.022       | **0.107**   | **0.038**  | 0.147 s          |

3D 베이스라인들은 dense posed input과 per-scene(또는 per-style) 최적화를 쓰는 유리한
조건인데도 Styl3R이 consistency에서 앞선다. 처리 시간은 분 단위 → 0.147초다.

### Novel View Synthesis (RE10K)

원논문 Table 3. `*`는 Styl3R과 동일하게 0차 spherical harmonics를 쓴 설정
(원 NoPoSplat은 4차가 기본). Ours는 stylization fine-tuning 전, Ours-stylization은 후.

| Method           | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ---------------- | ---------- | --------- | --------- |
| pixelSplat       | 23.848     | 0.806     | 0.185     |
| MVSplat          | 23.977     | 0.811     | 0.176     |
| NoPoSplat        | **25.033** | **0.838** | **0.160** |
| NoPoSplat*       | 24.836     | 0.832     | 0.166     |
| Ours             | 24.871     | 0.837     | 0.165     |
| Ours-stylization | 24.055     | 0.820     | 0.179     |

stylization fine-tuning은 NVS 품질을 약간 희생한다 (PSNR 24.871 → 24.055).

### 방법론 비교 (정성)

원논문 Table 1. 수치가 아닌 능력 매트릭스다.

| Method            | Sparse View | Scene Zero-shot | Style Zero-shot | View Consistency | Pose Free | Fast Inference |
| ----------------- | ----------- | --------------- | --------------- | ---------------- | --------- | -------------- |
| 2D Methods        | -           | ✓               | ✓               | ✗                | -         | ✓              |
| StyleRF           | ✗           | ✗               | ✓               | ✓                | ✗         | ✗              |
| StyleGaussian     | ✗           | ✗               | ✓               | ✓                | ✗         | ✗              |
| ARF               | ✗           | ✗               | ✗               | ✓                | ✗         | ✗              |
| **Styl3R (Ours)** | ✓           | ✓               | ✓               | ✓                | ✓         | ✓              |

### Cross-dataset Generalization

원논문 Figure 4 (Tanks and Temples). 수치 표가 아니라 정성 비교다 — per-scene 최적화가
필요한 StyleRF·StyleGaussian을 능가하고, per-scene 및 per-style 최적화까지 요구하는
ARF와 대등한 zero-shot 결과를 out-of-distribution 데이터에서 얻는다.

## 💡 Insights & Impact

### Paradigm Shift in 3D Stylization

**Traditional Approach**:

1. Separate reconstruction and stylization
2. 2D style transfer with 3D inconsistencies
3. Post-processing required
4. Limited real-time capability

**Styl3R Approach**:

1. Joint reconstruction and stylization
2. 3D-aware style application
3. Direct stylized output
4. Real-time processing

### Why 3D-Aware Stylization Works

1. **Geometric Understanding**: Style respects 3D structure
2. **Multi-View Consistency**: Coherent across viewpoints
3. **Real-Time Processing**: Efficient joint optimization
4. **Style Preservation**: Maintains artistic integrity

### Applications

- **Content Creation**: Stylized 3D environments
- **Game Development**: Artistic 3D assets
- **VR/AR**: Immersive stylized experiences
- **Digital Art**: 3D artistic expression
- **Architecture**: Stylized building visualization

### Technical Advantages

- **Real-Time**: Instant stylized reconstruction
- **Consistent**: 3D-coherent stylization
- **Versatile**: Multiple scenes and styles
- **Unified**: Single pipeline approach

## 🔗 Related Work

### Comparison with Stylization Methods

| Aspect      | 2D Style Transfer | 3D Post-process | Neural Style | Styl3R    |
| ----------- | ----------------- | --------------- | ------------ | --------- |
| Consistency | Poor              | Medium          | Medium       | Excellent |
| Speed       | Fast              | Slow            | Medium       | Fast      |
| Quality     | High              | Variable        | Good         | High      |
| 3D Aware    | No                | Limited         | Limited      | Yes       |

### Builds On

- **Neural Style Transfer**: 2D stylization techniques
- **3D Reconstruction**: Scene geometry understanding
- **Real-Time Rendering**: Efficient processing methods
- **Multi-View Synthesis**: Consistent view generation

### Relationship to [DUSt3R](../foundation/dust3r.md) Ecosystem

- **3D Foundation**: Leverages geometric understanding
- **Style Extension**: Adds artistic capabilities
- **Real-Time**: Maintains efficiency focus
- **Unified**: Single-pipeline philosophy

## 📚 Key Takeaways

Styl3R demonstrates that:

1. **Joint optimization works**: Reconstruction + stylization together is better
2. **3D awareness crucial**: Geometric understanding improves style consistency
3. **Real-time possible**: Efficient methods enable instant stylization
4. **Versatility achievable**: Single method for diverse scenes and styles

The success in achieving real-time 3D-consistent stylized reconstruction opens new possibilities for creative 3D content generation and artistic expression.

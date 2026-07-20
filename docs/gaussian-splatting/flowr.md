# FlowR: Flowing from Sparse to Dense 3D Reconstructions (ICCV 2025)

![FlowR Teaser](https://tobiasfshr.github.io/pub/flowr/teaser.gif)
_FlowR uses flow matching to generate high-quality additional views, bridging the gap between sparse and dense 3D scene captures_

## 📋 Overview

- **Authors**: Tobias Fischer¹'², Samuel Rota Bulò², Yung-Hsu Yang¹, Nikhil Keetha²'³, Lorenzo Porzi², Norman Müller², Katja Schwarz², Jonathon Luiten², Marc Pollefeys¹, Peter Kontschieder²
- **Institution**: ¹ETH Zurich, ²Meta Reality Labs Zurich, ³Carnegie Mellon University
- **Venue**: ICCV 2025
- **Award**: Highlight
- **Links**: [Paper](https://arxiv.org/abs/2504.01647) | [Project Page](https://tobiasfshr.github.io/pub/flowr/) | Code (coming soon)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Novel approach that flows from sparse to dense 3D reconstructions using Gaussian splatting techniques for high-quality scene representation.

## 🎯 Key Contributions

1. **Sparse-to-Dense Flow**: Progressive densification approach
2. **Gaussian Splatting Integration**: Leverages 3D Gaussian representations
3. **Flow-Based Reconstruction**: Uses flow techniques for scene building
4. **Quality Enhancement**: Improves reconstruction density and quality
5. **Efficient Pipeline**: Streamlined sparse-to-dense workflow

## 🔧 Technical Details

### Core Innovation: Flow-Based Densification

```text
Traditional: Static sparse reconstruction → Limited detail
FlowR: Sparse → Flow-guided densification → Dense reconstruction
```

### Technical Approach

#### 1. Flow-Guided Reconstruction

- Progressive point densification using flow
- Gaussian splatting for efficient representation
- Quality-aware densification strategy
- Temporal consistency maintenance

#### 2. Sparse-to-Dense Pipeline

```text
Input: Sparse 3D points from DUSt3R/similar
Flow: Guided densification process
Output: Dense 3D Gaussian representation
```

#### 3. Key Components

- **Flow Estimator**: Guides densification process
- **Gaussian Manager**: Handles 3D Gaussian primitives
- **Quality Assessment**: Ensures reconstruction fidelity
- **Progressive Builder**: Iterative densification

### Integration with Foundation Models

- **Input Compatibility**: Works with DUSt3R outputs
- **Gaussian Representation**: Efficient 3D primitives
- **Flow Guidance**: Smart densification strategy
- **Quality Control**: Maintains reconstruction accuracy

## 📊 Results

### Sparse-View 3D Reconstruction (DL3DV140)

원논문 Table 1. † 공식 코드 + GT pose, FlowR++는 test view까지 생성 모델로 정제한 변형.

| Method          | 12-view PSNR ↑ | 12-view SSIM ↑ | 12-view LPIPS ↓ | 24-view PSNR ↑ | 24-view SSIM ↑ | 24-view LPIPS ↓ |
| --------------- | -------------- | -------------- | --------------- | -------------- | -------------- | --------------- |
| Splatfacto      | 16.71          | 0.528          | 0.478           | 22.17          | 0.738          | 0.309           |
| InstantSplat†   | 20.47          | 0.698          | 0.297           | 19.57          | 0.710          | 0.326           |
| ViewCrafter\*   | 19.19          | 0.638          | 0.375           | 21.95          | 0.734          | 0.298           |
| FlowR (Initial) | 20.86          | 0.715          | 0.333           | 24.30          | 0.818          | 0.252           |
| **FlowR**       | **22.43**      | **0.766**      | **0.280**       | **25.13**      | **0.836**      | **0.212**       |
| FlowR++         | 22.60          | 0.793          | 0.261           | 25.33          | 0.863          | 0.193           |

### Dense-View 3D Reconstruction (ScanNet++ validation)

원논문 Table 2. 공식 train/test split 사용.

| Method          | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| --------------- | --------- | --------- | --------- |
| Splatfacto      | 22.41     | 0.843     | 0.352     |
| GANeRF          | 23.95     | 0.856     | 0.306     |
| FlowR (Initial) | 23.84     | 0.860     | 0.331     |
| **FlowR**       | **24.11** | **0.870** | **0.303** |
| GANeRF w/ GAN   | 24.01     | 0.860     | 0.291     |
| FlowR++         | 24.90     | 0.922     | 0.250     |

### Dense-View 3D Reconstruction (Nerfbusters)

원논문 Table 3. Coverage는 test trajectory에서 학습 시 관측된 3D 점 중
재구성된 픽셀 비율. \*opacity thresholding 적용.

| Method          | PSNR ↑    | SSIM ↑    | LPIPS ↓   | Coverage ↑ |
| --------------- | --------- | --------- | --------- | ---------- |
| Splatfacto      | 16.17     | 0.529     | 0.375     | 0.924      |
| Nerfacto        | 17.00     | 0.527     | 0.380     | 0.896      |
| Nerfbusters     | 17.99     | 0.606     | 0.250     | 0.630      |
| FlowR (Initial) | 17.02     | 0.567     | 0.365     | **0.932**  |
| **FlowR**       | **18.31** | **0.607** | **0.337** | **0.932**  |
| FlowR\*         | 18.94     | 0.780     | 0.181     | 0.680      |

## 💡 Insights & Impact

### Paradigm Shift in Densification

**Traditional Approach**:

1. Fixed reconstruction density
2. Static point representation
3. Limited quality control
4. Expensive dense methods

**FlowR Approach**:

1. Progressive densification
2. Flow-guided process
3. Quality-aware building
4. Efficient dense results

### Why Flow-Based Works

1. **Progressive Building**: Incremental quality improvement
2. **Guided Process**: Smart densification decisions
3. **Gaussian Efficiency**: Fast rendering and processing
4. **Quality Control**: Maintains reconstruction fidelity

### Technical Advantages

- **Adaptive Density**: Adjusts to scene complexity
- **Quality Focus**: Prioritizes important regions
- **Efficient Representation**: Gaussian primitives
- **Progressive**: Builds quality incrementally

## 🔗 Related Work

### Comparison with Densification Methods

| Method        | Approach        | Quality  | Efficiency | Control       |
| ------------- | --------------- | -------- | ---------- | ------------- |
| Voxel Grids   | Fixed           | Good     | Poor       | Limited       |
| Point Clouds  | Static          | Medium   | Good       | Basic         |
| Neural Fields | Implicit        | High     | Poor       | Good          |
| **FlowR**     | **Flow-guided** | **High** | **Good**   | **Excellent** |

### Builds On

- **3D Gaussian Splatting**: Efficient 3D representation
- **Flow Estimation**: Guidance for densification
- **Progressive Methods**: Incremental building approaches
- **Foundation Models**: DUSt3R and related work

### Enables

- High-quality dense reconstructions
- Efficient sparse-to-dense workflows
- Quality-controlled densification
- Practical 3D scene building

## 📚 Key Takeaways

FlowR demonstrates that:

1. **Flow guidance helps**: Smart densification improves quality
2. **Progressive works**: Incremental building is effective
3. **Gaussian efficiency**: 3D Gaussians enable practical dense reconstruction
4. **Quality control matters**: Guided processes produce better results

The flow-based approach to sparse-to-dense reconstruction represents an important step toward practical high-quality 3D scene building.

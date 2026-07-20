# Dust to Tower: Coarse-to-Fine Photo-Realistic Scene Reconstruction from Sparse Uncalibrated Images (arXiv preprint)

![Dust to Tower Pipeline](https://arxiv.org/html/2412.19518v1/x1.png)
_Dust to Tower achieves photo-realistic scene reconstruction through a coarse-to-fine approach with CCM, CADA, and WIGI modules_

## 📋 Overview

- **Authors**: Xudong Cai, Yongcai Wang, Zhaoxin Fan, Deng Haoran, Shuo Wang, Wanting Li, Deying Li, Lun Luo, Minhang Wang, Jintao Xu
- **Institution**: Renmin University of China, Beijing Key Laboratory of Traffic Data Analysis and Mining
- **Venue**: arXiv preprint (2024)
- **Links**: [Paper](https://arxiv.org/abs/2412.19518) | Project Page (not available) | Code (coming soon)
- **TL;DR**: Coarse-to-fine reconstruction pipeline that transforms sparse uncalibrated images into photo-realistic 3D scenes using progressive refinement strategies.

## 🎯 Key Contributions

1. **Coarse-to-Fine Strategy**: Progressive refinement for optimal quality
2. **Uncalibrated Input**: Works with sparse images without camera parameters
3. **Photo-Realistic Results**: High-quality visual reconstruction
4. **Progressive Pipeline**: Multi-stage optimization approach
5. **Robust Framework**: Handles challenging sparse-view scenarios

## 🔧 Technical Details

### Core Innovation: Progressive Scene Building

```text
Traditional: Single-stage reconstruction → Limited quality/robustness
Dust to Tower: Coarse stage (k₁ steps) → Fine stage (K₂ steps) → Photo-realistic results
```

### Technical Approach

#### 1. Two-Stage Optimization

- **Coarse Stage**: Train the coarse 3DGS model and DUSt3R-initialized poses using only the
  training views for k₁ steps, with loss `Lc = Lrgb(I, Ĩ) + λd·Ldepth(D̃, Dm)`
- **Fine Stage**: Use the updated input image poses to run WIGI, producing `Kp × (N − 1)`
  images at novel viewpoints; refine the 3DGS for K₂ steps with
  `Lf = Lc + λpseudo·Lrgb(Îp, Ĩp)`

#### 2. Coarse-to-Fine Architecture

```text
Input: Sparse uncalibrated images {I₁, I₂, ..., Iₙ}
Coarse: CCM builds a coarse 3DGS + poses from DUSt3R
Fine:   CADA-aligned depths → WIGI warping & inpainting → refined 3DGS
Output: High-quality 3D scene representation
```

#### 3. Key Components

- **CCM (Coarse Construction Module)**: Efficiently constructs the coarse 3DGS model
- **CADA (Confidence Aware Depth Alignment)**: Aligns mono-depth predictions with coarse
  depth estimates to improve warping accuracy
- **WIGI (Warped Image-Guided Inpainting)**: Generates multi-view consistent images at
  novel viewpoints via image warping and inpainting
- **Joint Optimization**: Poses and 3DGS optimized together

### Optimization Details

- **Depth Prior**: Mono-depths Dm used as a geometry prior via Pearson correlation on
  inverse depth, a loose constraint that avoids scale discrepancies
- **Pose Refinement**: ∆T updated by stochastic gradient descent alongside scene optimization
- **Ablation Evidence**: Removing the coarse-to-fine strategy degrades RPEt from 0.8068 to
  1.0384 (원논문 Table 5)

## 📊 Results

### Quantitative Performance

논문은 Tanks and Temples, MipNeRF360, CO3D V2 세 데이터셋에서 3/6/12 views로 평가합니다. 아래는 각 데이터셋의 3 views 결과이며, 6/12 views 결과는 원논문 Table 1–3을 참고하십시오.

#### Tanks and Temples (3 views)

원논문 Table 1.

| Category     | Method       | PSNR ↑    | SSIM ↑    | LPIPS ↓   | Time ↓  |
| ------------ | ------------ | --------- | --------- | --------- | ------- |
| Sparse       | FSGS         | 21.66     | 0.719     | 0.263     | 3m 47s  |
| Sparse       | DNGaussian   | 17.31     | 0.534     | 0.400     | 1m 52s  |
| Sparse       | 3DGS         | 16.17     | 0.558     | 0.366     | 4m 16s  |
| Unpose       | CF-3DGS      | 14.23     | 0.402     | 0.454     | 1m 7s   |
| Unpose       | Nope-NeRF    | 16.30     | 0.469     | 0.589     | 2h 22m  |
| Unconstraint | InstantSplat | 21.90     | 0.749     | 0.218     | 23s     |
| Unconstraint | COGS         | 18.56     | 0.569     | 0.299     | 50m 8s  |
| Unconstraint | **Ours**     | **23.39** | **0.776** | **0.164** | **41s** |

#### MipNeRF360 (3 views)

원논문 Table 2.

| Category     | Method       | PSNR ↑    | SSIM ↑    | LPIPS ↓   | Time ↓  |
| ------------ | ------------ | --------- | --------- | --------- | ------- |
| Sparse       | FSGS         | 12.33     | 0.261     | 0.637     | 3m 17s  |
| Sparse       | DNGaussian   | 11.37     | 0.235     | 0.694     | 2m 45s  |
| Sparse       | 3DGS         | 11.56     | 0.188     | 0.625     | 6m 41s  |
| Unpose       | CF-3DGS      | 12.70     | 0.227     | 0.594     | 1m 10s  |
| Unpose       | Nope-NeRF    | 14.43     | 0.304     | 0.702     | 2h 12m  |
| Unconstraint | InstantSplat | 13.77     | 0.285     | 0.551     | 23s     |
| Unconstraint | COGS         | 12.48     | 0.204     | 0.593     | 1h 7m   |
| Unconstraint | **Ours**     | **14.99** | **0.331** | **0.524** | **45s** |

#### CO3D V2 (3 views)

원논문 Table 3.

| Category     | Method       | PSNR ↑    | SSIM ↑    | LPIPS ↓   | Time ↓  |
| ------------ | ------------ | --------- | --------- | --------- | ------- |
| Sparse       | FSGS         | 17.99     | 0.731     | 0.438     | 4m 47s  |
| Sparse       | DNGaussian   | 15.17     | 0.703     | 0.476     | 5m 3s   |
| Sparse       | 3DGS         | 16.10     | 0.662     | 0.458     | 8m 29s  |
| Unpose       | CF-3DGS      | 16.27     | 0.713     | 0.445     | 3m 30s  |
| Unconstraint | InstantSplat | 18.15     | 0.741     | 0.362     | 30s     |
| Unconstraint | COGS         | 16.10     | 0.669     | 0.455     | 14m 39s |
| Unconstraint | **Ours**     | **19.79** | **0.771** | **0.345** | **59s** |

### Ablation Study

원논문 Table 5. Tanks and Temples 데이터셋, 3 training views 기준입니다.

| Variant                         | PSNR ↑    | SSIM ↑     | RPEt ↓     | RPEr ↓     |
| ------------------------------- | --------- | ---------- | ---------- | ---------- |
| (a) w/o CADA                    | 22.89     | 0.7632     | 0.8253     | 0.4189     |
| (b) w/o WIGI                    | 22.18     | 0.7511     | 0.8101     | 0.4175     |
| (c) w/o Inpainting              | 22.29     | 0.7550     | 0.8223     | 0.4162     |
| (d) w/o Mask Clean              | 22.90     | 0.7666     | 0.8122     | 0.4193     |
| (e) w/o Joint Optimization      | 22.69     | 0.7547     | 1.4681     | 0.4526     |
| (f) w/o Coarse-to-Fine Strategy | 22.85     | 0.7621     | 1.0384     | 0.4261     |
| **Full**                        | **23.39** | **0.7762** | **0.8068** | **0.4159** |

### Key Achievements

- ✅ 세 데이터셋 모두에서 3 views 기준 최고 PSNR/SSIM/LPIPS
- ✅ Nope-NeRF·COGS 대비 수 분~수 시간이 아닌 1분 내외의 최적화 시간
- ✅ Robust to sparse uncalibrated input
- ✅ 논문에 따르면 ATE에서 비교 방법 대비 order of magnitude 수준으로 정확 (Table 4)

## 💡 Insights & Impact

### Paradigm Shift in Scene Reconstruction

**Traditional Single-Stage**:

1. Direct optimization to final quality
2. Often gets stuck in local minima
3. Difficult convergence with sparse views
4. Limited robustness to initialization

**Dust to Tower Coarse-to-Fine**:

1. Progressive optimization strategy
2. Better global optimization through stages
3. Robust convergence with guidance
4. Stable improvement across stages

### Why Coarse-to-Fine Works

1. **Progressive Learning**: Easier optimization in stages
2. **Better Initialization**: Each stage initializes the next
3. **Stable Convergence**: Reduces optimization difficulties
4. **Quality Control**: Ensures consistent improvement

### Applications

- **Cultural Heritage**: High-quality monument reconstruction
- **Architecture**: Building documentation and visualization
- **Film Production**: Scene reconstruction for VFX
- **Virtual Tourism**: Immersive location experiences
- **Urban Planning**: City-scale reconstruction

### Technical Advantages

- **Progressive**: Systematic quality improvement
- **Robust**: Handles challenging sparse scenarios
- **Uncalibrated**: No camera parameter requirements
- **Photo-realistic**: High visual quality output

## 🔗 Related Work

### Comparison with Sparse-View Methods

논문의 카테고리 구분(원논문 Table 1–3)에 따른 정성 비교입니다. 수치는 위 Results 섹션을 참조하십시오.

| Category     | Representative Methods   | Requires Poses | Notes                                         |
| ------------ | ------------------------ | -------------- | --------------------------------------------- |
| Sparse       | FSGS, DNGaussian, 3DGS   | Yes            | Depth/geometry priors on given camera poses   |
| Unpose       | CF-3DGS, Nope-NeRF       | No             | Rely on dense input; struggle in sparse views |
| Unconstraint | InstantSplat, COGS       | No             | Sparse and uncalibrated input                 |
| Unconstraint | **Dust to Tower (Ours)** | **No**         | **Coarse-to-fine with CADA + WIGI**           |

### Builds On

- **Progressive Optimization**: Multi-stage learning strategies
- **Sparse-View Reconstruction**: Limited view reconstruction techniques
- **Photo-realistic Rendering**: High-quality view synthesis
- **Uncalibrated Methods**: Camera-free reconstruction approaches

### Relationship to DUSt3R Ecosystem

- **Progressive Philosophy**: Shares multi-stage optimization approach
- **Quality Focus**: Emphasis on high-quality reconstruction
- **Sparse-View**: Handles limited input scenarios
- **Foundation Integration**: Could leverage DUSt3R for initialization

## 📚 Key Takeaways

Dust to Tower demonstrates that:

1. **Progressive works**: Multi-stage optimization significantly improves quality
2. **Coarse-to-fine effective**: Systematic refinement achieves better results
3. **Uncalibrated possible**: High quality achievable without camera parameters
4. **Robustness matters**: Progressive approach handles challenging scenarios

The success in achieving photo-realistic reconstruction through progressive refinement represents an important advancement in making high-quality 3D reconstruction more robust and practical for real-world applications.

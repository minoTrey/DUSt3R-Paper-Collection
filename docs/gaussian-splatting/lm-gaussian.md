# LM-Gaussian: Boost Sparse-view 3D Gaussian Splatting with Large Model Priors (arXiv 2024)

![LM-Gaussian Pipeline](https://hanyangyu1021.github.io/lm-gaussian.github.io/static/images/overall.png)
_LM-Gaussian leverages large model priors to enhance sparse-view 3D Gaussian splatting for high-quality novel view synthesis_

## 📋 Overview

- **Authors**: Hanyang Yu, Xiaoxiao Long, Ping Tan
- **Institution**: Hong Kong University of Science and Technology, Light Illusions
- **Venue**: arXiv preprint (2024)
- **Links**: [Paper](https://arxiv.org/abs/2409.03456) | [Project Page](https://hanyangyu1021.github.io/lm-gaussian.github.io/) | [Code](https://github.com/hanyangyu1021/LMGaussian)
- **TL;DR**: Enhances sparse-view 3D Gaussian splatting by incorporating priors from large foundation models, achieving high-quality novel view synthesis from limited input views.

## 🎯 Key Contributions

1. **Large Model Integration**: Leverages foundation model priors for 3D reconstruction
2. **Sparse-View Enhancement**: Improves quality with limited input views
3. **Prior-Guided Optimization**: Uses semantic and geometric priors
4. **High-Quality Results**: Superior novel view synthesis quality
5. **Efficient Framework**: Maintains 3D Gaussian splatting efficiency

## 🔧 Technical Details

### Core Innovation: Foundation Model Priors for 3DGS

```text
Traditional 3DGS: Limited views → Poor reconstruction quality
LM-Gaussian: Limited views + Large model priors → High-quality reconstruction
```

### Technical Approach

#### 1. Prior Integration Strategy

- Depth priors from monocular depth estimation models
- Semantic priors from vision-language models
- Geometric consistency from foundation models
- Multi-modal prior fusion

#### 2. Enhanced 3DGS Pipeline

```text
Input: Sparse views {I₁, I₂, ..., Iₙ} (n < 10)
Priors: Depth maps, semantic features, geometric constraints
Process: Prior-guided Gaussian optimization
Output: High-quality 3D Gaussian representation
```

#### 3. Key Components

- **Prior Extractor**: Extracts multi-modal priors from foundation models
- **Gaussian Initializer**: Better initialization using priors
- **Prior-Guided Loss**: Incorporates prior knowledge in optimization
- **Quality Regularizer**: Ensures consistency with priors

### Foundation Model Integration

원논문이 실제로 사용한 large model prior:

- **Stereo prior**: DUSt3R — 초기 point cloud 및 카메라 포즈 복원
- **Mono depth/normal prior**: Marigold — depth·normal 정규화용
- **Image diffusion prior**: LoRA로 파인튜닝한 ControlNet — Gaussian Repair
- **Video diffusion prior**: 렌더링 결과의 장면 향상(scene enhancement)

## 📊 Results

### Tanks&Temples: 입력 뷰 수별 정량 비교

원논문 Table II (Tanks&Temples 부분).

| Method          | 4 views SSIM↑ | 4 views PSNR↑ | 4 views LPIPS↓ | 8 views SSIM↑ | 8 views PSNR↑ | 8 views LPIPS↓ | 16 views SSIM↑ | 16 views PSNR↑ | 16 views LPIPS↓ |
| --------------- | ------------- | ------------- | -------------- | ------------- | ------------- | -------------- | -------------- | -------------- | --------------- |
| FreeNeRF        | 0.2525        | 10.29         | 0.6025         | 0.2800        | 11.24         | 0.5400         | 0.3925         | 15.66          | 0.4375          |
| SparseNeRF      | 0.2625        | 10.35         | 0.6600         | 0.3000        | 11.45         | 0.5700         | 0.4600         | 16.20          | 0.4375          |
| DNGaussian      | 0.3025        | 11.59         | 0.6375         | 0.3200        | 12.67         | 0.5900         | 0.5025         | 16.69          | 0.4475          |
| Scaffold-GS     | 0.3275        | 11.13         | 0.5600         | 0.4900        | 13.93         | 0.4675         | 0.5625         | 18.10          | 0.3600          |
| Splatfield      | 0.3250        | 10.79         | 0.5975         | 0.5725        | 14.17         | 0.5150         | 0.5725         | 18.60          | 0.3300          |
| CoR-GS          | 0.3850        | 12.82         | 0.5550         | 0.4925        | 14.90         | 0.4075         | 0.5950         | 18.00          | 0.3725          |
| InstantSplat    | 0.4025        | 13.65         | 0.5425         | 0.5300        | 16.46         | 0.3700         | 0.6050         | 19.28          | 0.3450          |
| **LM-Gaussian** | **0.4600**    | **14.68**     | **0.4725**     | **0.6205**    | **18.40**     | **0.2412**     | **0.6875**     | **20.54**      | **0.2300**      |

### MipNeRF360: 입력 뷰 수별 정량 비교

원논문 Table II (MipNeRF360 부분).

| Method          | 4 views SSIM↑ | 4 views PSNR↑ | 4 views LPIPS↓ | 8 views SSIM↑ | 8 views PSNR↑ | 8 views LPIPS↓ | 16 views SSIM↑ | 16 views PSNR↑ | 16 views LPIPS↓ |
| --------------- | ------------- | ------------- | -------------- | ------------- | ------------- | -------------- | -------------- | -------------- | --------------- |
| FreeNeRF        | 0.2575        | 9.92          | 0.7250         | 0.2950        | 11.67         | 0.6275         | 0.3275         | 14.86          | 0.5500          |
| SparseNeRF      | 0.2850        | 10.06         | 0.7075         | 0.3050        | 11.78         | 0.6400         | 0.3525         | 15.11          | 0.5150          |
| DNGaussian      | 0.3375        | 11.14         | 0.6375         | 0.3525        | 12.46         | 0.6550         | 0.3775         | 15.96          | 0.4800          |
| Scaffold-GS     | 0.3250        | 11.92         | 0.6550         | 0.3225        | 14.30         | 0.5525         | 0.4325         | 18.25          | 0.3825          |
| Splatfield      | 0.3475        | 10.52         | 0.6175         | 0.3250        | 13.41         | 0.5700         | 0.4425         | 17.49          | 0.4225          |
| CoR-GS          | 0.4025        | 14.55         | 0.6675         | 0.3925        | 15.75         | 0.5975         | 0.4975         | 18.60          | 0.3575          |
| InstantSplat    | 0.4025        | 14.41         | 0.5450         | 0.4700        | 16.57         | 0.4125         | 0.5125         | 18.33          | 0.3425          |
| **LM-Gaussian** | **0.4400**    | **15.18**     | **0.5350**     | **0.5475**    | **17.49**     | **0.3300**     | **0.5800**     | **19.22**      | **0.3000**      |

### LLFF (3 input views)

원논문 Table III.

| Methods         | PSNR ↑    | LPIPS ↓   | SSIM ↑    |
| --------------- | --------- | --------- | --------- |
| PixelNeRF       | 15.17     | 0.612     | 0.338     |
| MVSNeRF         | 16.88     | 0.427     | 0.484     |
| DietNeRF        | 14.94     | 0.496     | 0.370     |
| RegNeRF         | 18.08     | 0.396     | 0.487     |
| FreeNeRF        | 18.63     | 0.328     | 0.512     |
| SparseNeRF      | 18.52     | 0.335     | 0.527     |
| DNGaussian      | 18.32     | 0.314     | 0.535     |
| Splatfield      | 17.94     | 0.402     | 0.499     |
| Scaffold-GS     | 18.88     | 0.309     | 0.567     |
| CoR-GS          | 18.91     | 0.292     | 0.594     |
| InstantSplat    | 19.33     | 0.242     | 0.628     |
| **LM-Gaussian** | **19.63** | **0.228** | **0.644** |

### Ablation: 초기화 방식 (Horse 장면, 16-view)

원논문 Table IV.

| Initialization              | PSNR ↑    | LPIPS ↓   | SSIM ↑    |
| --------------------------- | --------- | --------- | --------- |
| Colmap                      | 13.42     | 0.558     | 0.192     |
| DUSt3R                      | 17.12     | 0.328     | 0.546     |
| **Proposed Initialization** | **18.04** | **0.304** | **0.576** |

### Ablation: 모듈별 기여도 (Horse 장면, 16-view)

원논문 Table V. BA = Background-Aware Depth-guided Initialization.

| BA  | Regularization | Refinement | PSNR ↑    | LPIPS ↓   | SSIM ↑    |
| --- | -------------- | ---------- | --------- | --------- | --------- |
| ×   | ×              | ×          | 13.42     | 0.558     | 0.192     |
| ✓   | ×              | ×          | 18.04     | 0.304     | 0.576     |
| ✓   | ✓              | ×          | 21.32     | 0.145     | 0.731     |
| ✓   | ✓              | ✓          | **22.04** | **0.119** | **0.776** |

### Ablation: 정규화 항목별 효과

원논문 Table VI. multi-depth / cosine-normal / weighted point-render 정규화를 개별 검증.

| Depth | Normal | Virtual-view | PSNR ↑    | LPIPS ↓   | SSIM ↑    |
| ----- | ------ | ------------ | --------- | --------- | --------- |
| ×     | ×      | ×            | 18.04     | 0.304     | 0.576     |
| ✓     | ×      | ×            | 19.74     | 0.205     | 0.634     |
| ✓     | ✓      | ×            | 20.02     | 0.188     | 0.665     |
| ✓     | ✓      | ✓            | **21.32** | **0.145** | **0.731** |

## 💡 Insights & Impact

### Paradigm Shift in Sparse-View 3DGS

**Traditional 3DGS**:

1. Relies purely on multi-view consistency
2. Struggles with sparse input views
3. Limited geometric understanding
4. Poor novel view synthesis quality

**LM-Gaussian**:

1. Leverages foundation model knowledge
2. Excels with limited input views
3. Rich geometric and semantic understanding
4. High-quality novel view synthesis

### Why Large Model Priors Work

1. **Rich Knowledge**: Foundation models capture extensive visual knowledge
2. **Geometric Understanding**: Better depth and structure estimation
3. **Semantic Awareness**: Object and scene understanding
4. **Consistency**: Multi-view geometric constraints

### Applications

- **Content Creation**: High-quality 3D from few photos
- **VR/AR**: Immersive experiences from limited capture
- **Digital Twins**: Efficient 3D digitization
- **Mobile 3D**: Quality reconstruction on resource-constrained devices
- **Film Production**: Quick 3D asset creation

### Technical Advantages

- **Prior Integration**: Seamless foundation model incorporation
- **Quality Boost**: Significant improvement over baseline
- **Efficiency**: Maintains 3DGS speed advantages
- **Generalization**: Works across diverse scenes

## 🔗 Related Work

### Comparison with Sparse-View Methods

원논문이 Table II·III에서 직접 비교한 방법들: PixelNeRF, MVSNeRF, DietNeRF,
RegNeRF, FreeNeRF, SparseNeRF, DNGaussian, Splatfield, Scaffold-GS, CoR-GS,
InstantSplat. 정량 수치는 위 `## 📊 Results` 표 참조.

### Builds On

- **3D Gaussian Splatting**: Efficient 3D representation
- **Foundation Models**: Large-scale pre-trained knowledge
- **Sparse-View NeRF**: Limited view reconstruction techniques
- **Multi-Modal Learning**: Vision-language model integration

### Relationship to DUSt3R Ecosystem

- **Complementary**: Enhances sparse reconstruction quality
- **Foundation Synergy**: Both leverage pre-trained knowledge
- **Quality Focus**: Shared goal of high-quality 3D
- **Efficiency**: Maintains real-time performance

## 📚 Key Takeaways

LM-Gaussian demonstrates that:

1. **Foundation models help 3D**: Large model priors significantly improve reconstruction
2. **Sparse views sufficient**: Quality 3D possible with very few inputs
3. **Multi-modal benefits**: Combining different priors works synergistically
4. **Efficiency preserved**: Quality gains don't sacrifice speed

The success in integrating large model priors with 3D Gaussian splatting represents a significant advancement in making high-quality 3D reconstruction practical with minimal input requirements.

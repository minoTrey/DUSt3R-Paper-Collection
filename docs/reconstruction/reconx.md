# ReconX: Reconstruct Any Scene from Sparse Views with Video Diffusion Model (IEEE TIP 2026)

![ReconX Pipeline](https://liuff19.github.io/ReconX/static/images/teaser.png)
_ReconX leverages video diffusion models to reconstruct complete 3D scenes from just a few input views, generating missing viewpoints through learned priors_

## 📋 Overview

- **Authors**: Fangfu Liu, Wenqiang Sun, Hanyang Wang, Yikai Wang, Haowen Sun, Junliang Ye, Jun Zhang, Yueqi Duan
- **Institution**: Tsinghua University, Hong Kong University of Science and Technology, Beijing Normal University
- **Venue**: IEEE TIP 2026
- **Links**: [Paper](https://arxiv.org/abs/2408.16767) | [Project Page](https://liuff19.github.io/ReconX/) | Code (coming soon)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Novel 3D reconstruction approach that uses video diffusion models to generate missing viewpoints from sparse input views, enabling high-quality scene reconstruction.

## 🎯 Key Contributions

1. **Video Diffusion for 3D**: First to use video diffusion for sparse-view reconstruction
2. **View Synthesis Integration**: Generates missing views to densify sparse inputs
3. **End-to-End Pipeline**: Unified framework from sparse views to 3D scene
4. **High-Quality Results**: Superior reconstruction from minimal input views
5. **General Applicability**: Works across diverse scene types and objects

## 🔧 Technical Details

### Core Innovation: Diffusion-Driven Reconstruction

```text
Traditional: Sparse views → Direct 3D reconstruction (limited quality)
ReconX: Sparse views → Video diffusion → Dense views → High-quality 3D
```

### Technical Approach

#### 1. Video Diffusion Integration

- Leverages pre-trained video diffusion models
- Generates plausible intermediate viewpoints
- Maintains temporal and spatial consistency
- Handles complex scene dynamics

#### 2. Sparse-to-Dense Pipeline

```text
Input: Sparse views {I₁, I₂, ..., Iₙ}
Step 1: Video diffusion generates intermediate views
Step 2: Dense view set reconstruction
Output: Complete 3D scene representation
```

#### 3. Key Components

- **View Synthesis Module**: Video diffusion-based generation
- **Consistency Enforcement**: Multi-view geometric constraints
- **3D Reconstruction**: Neural scene representation
- **Quality Refinement**: Post-processing for final output

### Architecture Design

- **Diffusion Backbone**: Pre-trained video generation model
- **View Conditioning**: Sparse view guidance mechanism
- **Geometric Awareness**: 3D-consistent generation
- **Multi-Scale Processing**: Handles different scene scales

## 📊 Results

### Two-View NVS — Easy Set (원논문 Table I)

원논문 TABLE I. 입력 시점 각도 변화가 작은 경우, 2뷰 입력 → 3개 novel view 렌더링.

| Method     | RE10K PSNR ↑ | RE10K SSIM ↑ | RE10K LPIPS ↓ | ACID PSNR ↑ | ACID SSIM ↑ | ACID LPIPS ↓ |
| ---------- | ------------ | ------------ | ------------- | ----------- | ----------- | ------------ |
| pixelNeRF  | 20.43        | 0.589        | 0.550         | 20.97       | 0.547       | 0.533        |
| GPNR       | 24.11        | 0.793        | 0.255         | 25.28       | 0.764       | 0.332        |
| AttnRend   | 24.78        | 0.820        | 0.213         | 26.88       | 0.799       | 0.218        |
| MuRF       | 26.10        | 0.858        | 0.143         | 28.09       | 0.841       | 0.155        |
| pixelSplat | 25.89        | 0.858        | 0.142         | 28.14       | 0.839       | 0.150        |
| MVSplat    | 26.39        | 0.839        | 0.128         | 28.25       | 0.843       | 0.144        |
| **ReconX** | **28.31**    | **0.912**    | **0.088**     | **28.84**   | **0.891**   | **0.101**    |

### Hard Set & Cross-Dataset 일반화 (원논문 Table II)

원논문 TABLE II. Hard Set은 입력 시점 각도 변화가 큰 경우, Cross Set은 학습에
쓰지 않은 데이터셋으로의 일반화.

| Split | Method     | Dataset A     | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ----- | ---------- | ------------- | --------- | --------- | --------- |
| Hard  | pixelSplat | ACID          | 16.83     | 0.476     | 0.494     |
| Hard  | MVSplat    | ACID          | 16.49     | 0.466     | 0.486     |
| Hard  | **ReconX** | ACID          | **24.53** | **0.847** | **0.083** |
| Hard  | pixelSplat | RealEstate10K | 19.62     | 0.730     | 0.270     |
| Hard  | MVSplat    | RealEstate10K | 19.97     | 0.732     | 0.245     |
| Hard  | **ReconX** | RealEstate10K | **23.70** | **0.867** | **0.143** |
| Cross | pixelSplat | LLFF          | 11.42     | 0.312     | 0.611     |
| Cross | MVSplat    | LLFF          | 11.60     | 0.353     | 0.425     |
| Cross | **ReconX** | LLFF          | **21.05** | **0.768** | **0.178** |
| Cross | pixelSplat | DTU           | 12.89     | 0.382     | 0.560     |
| Cross | MVSplat    | DTU           | 13.94     | **0.473** | **0.385** |
| Cross | **ReconX** | DTU           | **19.78** | 0.476     | 0.378     |

### Sparse-View 재구성 — 입력 뷰 수에 따른 성능 (원논문 Table III)

원논문 TABLE III에서 PSNR만 발췌 (SSIM/LPIPS는 원논문 참조).

| Dataset          | Method     | 2-view    | 3-view    | 6-view    | 9-view    |
| ---------------- | ---------- | --------- | --------- | --------- | --------- |
| Mip-NeRF 360     | 3DGS       | 10.36     | 10.86     | 12.48     | 13.10     |
| Mip-NeRF 360     | SparseNeRF | 11.47     | 11.67     | 14.79     | 14.90     |
| Mip-NeRF 360     | DNGaussian | 10.81     | 11.13     | 12.20     | 13.01     |
| Mip-NeRF 360     | **ReconX** | **13.37** | **16.66** | **18.72** | **18.17** |
| Tank and Temples | 3DGS       | 9.57      | 10.15     | 11.48     | 12.50     |
| Tank and Temples | SparseNeRF | 9.23      | 9.55      | 12.24     | 12.74     |
| Tank and Temples | DNGaussian | 10.23     | 11.25     | 12.92     | 13.01     |
| Tank and Temples | **ReconX** | **14.28** | **15.38** | **16.27** | **18.38** |
| DL3DV            | 3DGS       | 9.46      | 10.97     | 13.34     | 14.99     |
| DL3DV            | SparseNeRF | 9.14      | 10.89     | 12.15     | 12.89     |
| DL3DV            | DNGaussian | 10.10     | 11.10     | 12.65     | 13.46     |
| DL3DV            | **ReconX** | **13.60** | **14.97** | **17.45** | **18.59** |

### Mip-NeRF 360 — 생성 기반 방법과의 비교 (원논문 Table IV)

원논문 TABLE IV.

| Method      | 3v PSNR ↑ | 3v LPIPS ↓ | 6v PSNR ↑ | 6v LPIPS ↓ | 9v PSNR ↑ | 9v LPIPS ↓ |
| ----------- | --------- | ---------- | --------- | ---------- | --------- | ---------- |
| Zip-NeRF    | 12.77     | 0.705      | 13.61     | 0.663      | 14.30     | 0.633      |
| ZeroNVS     | 14.44     | 0.680      | 15.51     | 0.663      | 15.99     | 0.655      |
| ReconFusion | 15.50     | 0.585      | 16.93     | 0.544      | 18.19     | 0.511      |
| CAT3D       | 16.62     | 0.515      | 17.72     | 0.482      | 18.67     | 0.460      |
| **ReconX**  | **17.16** | **0.407**  | **19.20** | **0.378**  | **20.13** | **0.356**  |

### Ablation (원논문 Table V)

원논문 TABLE V. RealEstate10K 기준.

| Video diff. | Structure cond. | DUSt3R init. | Conf-aware opt. | LPIPS loss | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ----------- | --------------- | ------------ | --------------- | ---------- | --------- | --------- | --------- |
| -           | -               | ✓            | -               | -          | 17.34     | 0.527     | 0.259     |
| ✓           | -               | ✓            | -               | -          | 19.70     | 0.789     | 0.229     |
| ✓           | -               | ✓            | ✓               | ✓          | 25.13     | 0.901     | 0.131     |
| ✓           | ✓               | -            | ✓               | ✓          | 27.11     | 0.908     | 0.113     |
| ✓           | ✓               | ✓            | -               | ✓          | 27.83     | 0.897     | 0.097     |
| ✓           | ✓               | ✓            | ✓               | -          | 27.47     | 0.906     | 0.111     |
| ✓           | ✓               | ✓            | ✓               | ✓          | **28.31** | **0.912** | **0.088** |

## 💡 Insights & Impact

### Paradigm Shift in Sparse Reconstruction

**Traditional Methods**:

1. Direct geometric reconstruction
2. Limited by sparse observations
3. Poor hole filling
4. Geometric artifacts

**ReconX Approach**:

1. Content-aware view generation
2. Leverages learned scene priors
3. Natural scene completion
4. High-quality results

### Why Video Diffusion Works

1. **Rich Priors**: Learned from massive video datasets
2. **Temporal Consistency**: Natural view transitions
3. **Content Understanding**: Semantic scene awareness
4. **Generative Power**: Plausible view synthesis

### Applications

- **VR/AR Content Creation**: Immersive scene capture
- **Digital Heritage**: Preserve sites from few photos
- **Robotics**: Environment understanding
- **Film Production**: Scene reconstruction for VFX
- **E-commerce**: Product visualization

### Limitations

- Depends on diffusion model quality
- Computational overhead from generation
- May hallucinate non-existent details
- Limited by training data distribution

## 🔗 Related Work

### Comparison with Reconstruction Methods

| Aspect         | MVS   | NeRF   | 3DGS   | ReconX    |
| -------------- | ----- | ------ | ------ | --------- |
| Input          | Dense | Medium | Medium | Sparse    |
| Quality        | Good  | High   | High   | High      |
| Speed          | Fast  | Slow   | Fast   | Medium    |
| Generalization | Poor  | Poor   | Poor   | Excellent |

### Builds On

- **Video Diffusion Models**: Temporal generation frameworks
- **Sparse-View Reconstruction**: Classical geometric methods
- **Neural Scene Representation**: NeRF and variants
- **View Synthesis**: Novel view generation techniques

### Relationship to [DUSt3R](../foundation/dust3r.md) Ecosystem

- **Complementary**: Different approach to sparse reconstruction
- **Enhanced**: Uses generative priors vs geometric only
- **Broader**: Handles more diverse scene types
- **Future**: Potential integration opportunities

## 📚 Key Takeaways

ReconX demonstrates that:

1. **Generative models help**: Learned priors improve sparse reconstruction
2. **Video understanding transfers**: Temporal models work for 3D
3. **View synthesis matters**: Generated views enhance reconstruction
4. **End-to-end works**: Unified pipeline achieves better results

The integration of video diffusion models into 3D reconstruction represents a significant advancement in handling extremely sparse input scenarios, opening new possibilities for practical 3D capture applications.

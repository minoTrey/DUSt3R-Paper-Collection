# Amodal3R: Amodal 3D Reconstruction from Occluded 2D Images (ICCV 2025)

![Amodal3R Teaser](https://sm0kywu.github.io/Amodal3R/images/overview.png)
_Amodal3R reconstructs complete 3D objects from partially occluded views using conditional generation and occlusion-aware attention_

## 📋 Overview

- **Authors**: Tianhao Wu, Chuanxia Zheng, Frank Guan, Andrea Vedaldi, Tat-Jen Cham
- **Institution**: S-Lab NTU, Visual Geometry Group Oxford, Singapore Institute of Technology
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.13439) | [Project Page](https://sm0kywu.github.io/Amodal3R/) | [Code](https://github.com/Sm0kyWu/Amodal3R)
- **TL;DR**: Novel approach for amodal 3D reconstruction that recovers complete 3D object shapes from partially occluded 2D images using advanced reasoning techniques.

## 🎯 Key Contributions

1. **Amodal Reconstruction**: Recovers complete shapes from partial observations
2. **Occlusion Handling**: Robust to object occlusions and partial visibility
3. **3D Reasoning**: Advanced spatial reasoning for shape completion
4. **Multi-View Integration**: Combines information across occluded views
5. **Complete Shape Recovery**: Predicts full 3D geometry from incomplete data

## 🔧 Technical Details

### Core Innovation: Amodal 3D Understanding

```text
Traditional: Visible parts only → Incomplete reconstruction
Amodal3R: Partial observations → Complete 3D shape reasoning
```

### Technical Approach

#### 1. Amodal Reasoning Framework

- Predicts complete object shapes from partial views
- Handles various occlusion patterns
- Integrates multi-view information
- Learns shape priors for completion

#### 2. Occlusion-Aware Pipeline

```text
Input: Occluded 2D images {I₁, I₂, ..., Iₙ}
Process: Amodal reasoning + Shape completion
Output: Complete 3D object reconstruction
```

#### 3. Key Components

- **Occlusion Detector**: Identifies occluded regions
- **Shape Completer**: Predicts missing geometry
- **Amodal Reasoner**: Infers complete object shapes
- **Multi-View Integrator**: Combines partial observations

### Amodal Understanding

- **Shape Priors**: Learned object shape distributions
- **Geometric Reasoning**: Spatial relationship understanding
- **Completion Strategy**: Smart hole filling approaches
- **Consistency Enforcement**: Multi-view geometric constraints

## 📊 Results

### Amodal 3D Reconstruction on GSO

원논문 Table 1. V-num은 입력 뷰 수, 2D-Comp는 전처리로 쓴 2D 완성 방법.
Amodal3R은 2D 완성 없이 직접 처리한다.

| Method           | V-num | 2D-Comp        | FID ↓     | KID(%) ↓ | CLIP ↑   | P-FID ↓  | COV(%) ↑  | MMD(‰) ↓ |
| ---------------- | ----- | -------------- | --------- | -------- | -------- | -------- | --------- | -------- |
| GaussianAnything | 1     | pix2gestalt    | 92.26     | 1.30     | 0.74     | 34.69    | 35.92     | 5.03     |
| Real3D           | 1     | pix2gestalt    | 91.21     | 2.02     | 0.75     | 23.92    | 19.61     | 9.21     |
| TRELLIS          | 1     | pix2gestalt    | 58.82     | 5.87     | 0.76     | 26.43    | 31.65     | 4.17     |
| **Amodal3R**     | 1     | –              | 30.64     | 0.35     | 0.81     | 7.69     | **39.61** | 3.62     |
| LaRa             | 4     | pix2gestalt    | 172.84    | 4.54     | 0.70     | 66.34    | 24.56     | 8.11     |
| LaRa             | 4     | pix2gestalt+MV | 97.53     | 2.63     | 0.75     | 21.80    | 26.21     | 8.61     |
| TRELLIS          | 4     | pix2gestalt    | 65.69     | 6.92     | 0.78     | 24.64    | 32.33     | 4.26     |
| TRELLIS          | 4     | pix2gestalt+MV | 60.37     | 1.85     | 0.83     | 19.68    | 31.75     | 4.21     |
| **Amodal3R**     | 4     | –              | **26.27** | **0.22** | **0.84** | **5.03** | 38.74     | **3.61** |

### Amodal 3D Reconstruction on Toys4K

원논문 Table 2. 설정은 Table 1과 동일하고 데이터셋만 다르다.

| Method           | V-num | 2D-Comp        | FID ↓     | KID(%) ↓ | CLIP ↑   | P-FID ↓  | COV(%) ↑  | MMD(‰) ↓ |
| ---------------- | ----- | -------------- | --------- | -------- | -------- | -------- | --------- | -------- |
| GaussianAnything | 1     | pix2gestalt    | 57.17     | 1.22     | 0.80     | 21.97    | 33.56     | 7.23     |
| Real3D           | 1     | pix2gestalt    | 59.92     | 1.63     | 0.79     | 23.31    | 24.35     | 9.53     |
| TRELLIS          | 1     | pix2gestalt    | 43.05     | 6.83     | 0.80     | 26.04    | 26.28     | 6.87     |
| **Amodal3R**     | 1     | –              | 23.45     | **0.42** | 0.83     | 5.00     | 37.09     | 5.89     |
| LaRa             | 4     | pix2gestalt    | 123.52    | 3.61     | 0.75     | 45.91    | 27.89     | 9.67     |
| LaRa             | 4     | pix2gestalt+MV | 75.33     | 4.14     | 0.80     | 13.00    | 24.82     | 10.93    |
| TRELLIS          | 4     | pix2gestalt    | 46.34     | 8.77     | 0.81     | 28.76    | 25.35     | 7.13     |
| TRELLIS          | 4     | pix2gestalt+MV | 43.00     | 7.53     | 0.81     | 24.41    | 26.55     | 7.05     |
| **Amodal3R**     | 4     | –              | **20.93** | 0.50     | **0.85** | **3.78** | **39.03** | **5.75** |

### Ablation: Mask Conditioning Design

원논문 Table 3. GSO 단일 뷰 기준.

| Method                          | FID ↓     | KID(%) ↓ | COV(%) ↑  | MMD(‰) ↓ |
| ------------------------------- | --------- | -------- | --------- | -------- |
| Naive conditioning              | 31.96     | 0.49     | 37.96     | 3.61     |
| w/ only mask-weighted attention | **30.53** | 0.38     | 36.90     | 3.69     |
| w/ only occlusion-aware layer   | 31.77     | 0.57     | **40.19** | **3.51** |
| **Full model (Ours)**           | 30.64     | **0.35** | 39.61     | 3.62     |

### Applications

- **Robotics**: Object manipulation with partial visibility
- **Autonomous Driving**: Vehicle detection behind obstacles
- **AR/VR**: Complete scene understanding
- **Medical Imaging**: Organ reconstruction from partial scans
- **Industrial Inspection**: Hidden defect detection

## 💡 Insights & Impact

### Paradigm Shift in Occlusion Handling

**Traditional Reconstruction**:

1. Only reconstructs visible parts
2. Poor handling of occlusions
3. Incomplete object understanding
4. Limited practical applicability

**Amodal3R Approach**:

1. Reconstructs complete objects
2. Robust occlusion handling
3. Full shape understanding
4. Practical real-world application

### Why Amodal Reasoning Works

1. **Shape Priors**: Learned object shape knowledge
2. **Contextual Understanding**: Scene-level reasoning
3. **Multi-View Integration**: Combines partial information
4. **Geometric Consistency**: Physical plausibility constraints

### Technical Advantages

- **Complete Reconstruction**: Full object shape recovery
- **Occlusion Robust**: Handles various occlusion patterns
- **Multi-View**: Leverages multiple viewpoints
- **Prior-Informed**: Uses learned shape knowledge

## 🔗 Related Work

### Comparison with Occlusion Methods

| Method           | Approach       | Completeness | Robustness | Applications  |
| ---------------- | -------------- | ------------ | ---------- | ------------- |
| Inpainting       | 2D completion  | Poor         | Limited    | Basic         |
| Partial Recon    | Visible only   | Incomplete   | Medium     | Limited       |
| Shape Completion | Single view    | Good         | Medium     | Research      |
| **Amodal3R**     | **Multi-view** | **Complete** | **High**   | **Practical** |

### Builds On

- **Amodal Perception**: Understanding complete objects
- **Shape Completion**: 3D shape inference techniques
- **Multi-View Geometry**: Geometric reasoning
- **Deep Learning**: Neural shape priors

### Enables

- Robust object reconstruction
- Complete scene understanding
- Practical occlusion handling
- Real-world 3D applications

## 📚 Key Takeaways

Amodal3R demonstrates that:

1. **Complete understanding possible**: Amodal reasoning enables full reconstruction
2. **Occlusion not limiting**: Partial views sufficient for complete shapes
3. **Priors are powerful**: Learned shape knowledge crucial
4. **Multi-view helps**: Combining partial observations works

The advancement in amodal 3D reconstruction represents a significant step toward robust real-world 3D understanding systems.

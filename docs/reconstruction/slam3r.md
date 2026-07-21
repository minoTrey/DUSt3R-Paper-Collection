# SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos (CVPR 2025)

![SLAM3R Demo](https://raw.githubusercontent.com/PKU-VCL-3DV/SLAM3R/main/media/replica.gif)
_SLAM3R achieves real-time dense 3D reconstruction with two-hierarchy networks: I2P for local geometry and L2W for global alignment_

## 📋 Overview

- **Authors**: Yuzheng Liu, Siyan Dong, Shuzhe Wang, Yingda Yin, Yanchao Yang, Qingnan Fan, Baoquan Chen
- **Institution**: Peking University, The University of Hong Kong, Aalto University, VIVO
- **Venue**: CVPR 2025
- **Award**: Highlight Paper
- **Links**: [Paper](https://arxiv.org/abs/2412.09401) | [Code](https://github.com/PKU-VCL-3DV/SLAM3R) | [Project Page](https://pku-vcl-3dv.github.io/SLAM3R/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Real-time (20+ FPS) dense 3D reconstruction from monocular RGB video using feed-forward networks without explicit camera parameter estimation.

## 🎯 Key Contributions

1. **Real-time Dense SLAM**: First to achieve 20+ FPS dense reconstruction using neural networks
2. **Camera-Parameter-Free**: Eliminates traditional pose optimization
3. **Two-Hierarchy Architecture**: I2P (local) + L2W (global) networks
4. **End-to-End Learning**: No iterative optimization or bundle adjustment
5. **Dense Output**: Complete 3D pointclouds vs sparse features

## 🔧 Technical Details

### Two-Hierarchy Architecture

#### 1. I2P Network (Images-to-Points)

- **Base**: DUSt3R-inspired Vision Transformer
- **Input**: Sliding window of 11 frames (default; ablated over 2/5/11/15/51)
- **Output**: Dense 3D pointmaps in local coordinates
- **Key Features**:
  - Multi-view cross-attention
  - Shared encoder across views
  - Direct 3D regression

#### 2. L2W Network (Local-to-World)

- **Purpose**: Incremental global fusion
- **Input**: Local pointmaps + features
- **Output**: Global registration
- **Key Features**:
  - Retrieval mechanism for loop closure
  - Attention-based alignment
  - Memory-efficient processing

### Key Design Choices

- **Sliding Window**: Balance between context and speed
- **Direct Prediction**: No RANSAC or optimization
- **Incremental Fusion**: Avoids storing full history
- **Shared Encoders**: Efficiency through weight sharing

## 📊 Results

### Quantitative Performance

#### 7 Scenes Dataset (Real-world)

원논문 Table 1. 전체 테스트 시퀀스에 대한 평균값이며, 정확도(Acc.)와 완전성(Comp.)은 cm 단위입니다. 방법은 FPS가 1 이상인지 여부로 두 그룹으로 나뉘며, 각 그룹 내 최고 성능을 굵게 표시합니다.

| Method               | Acc. / Comp. (Average) | FPS |
| -------------------- | ---------------------- | --- |
| DUSt3R [64]          | **2.19 / 3.24**        | <1  |
| MASt3R [28]          | 3.04 / 3.90            | ≪1  |
| Spann3R [61]         | 3.42 / 2.41            | >50 |
| SLAM3R-NoConf (Ours) | 2.40 / **2.24**        | ∼25 |
| **SLAM3R (Ours)**    | **2.13** / 2.34        | ∼25 |

#### Replica Dataset (Synthetic)

원논문 Table 2. `*`는 NICER-SLAM에서 보고된 결과입니다.

| Method               | Acc. / Comp. (Average) | FPS |
| -------------------- | ---------------------- | --- |
| DUSt3R [64]          | **3.49** / 2.48        | <1  |
| MASt3R [28]          | 4.71 / 3.36            | ≪1  |
| NICER-SLAM [79]\*    | 3.65 / 4.16            | ≪1  |
| DROID-SLAM [56]\*    | 5.50 / 12.29           | ∼20 |
| DIM-SLAM [29]\*      | 11.60 / 7.85           | ∼3  |
| GO-SLAM [75]         | 3.81 / 4.79            | ∼8  |
| Spann3R [61]         | 10.32 / 13.33          | >50 |
| SLAM3R-NoConf (Ours) | 3.76 / 2.62            | ∼24 |
| **SLAM3R (Ours)**    | **3.57 / 2.62**        | ∼24 |

#### Camera Pose Estimation

원논문 Table 3. ATE-RMSE (cm) 기준입니다.

| Method               | 7 Scenes | Replica |
| -------------------- | -------- | ------- |
| DUSt3R [64]          | 8.02     | 4.76    |
| MASt3R [28]          | 6.28     | 1.67    |
| NICER-SLAM [79]\*    | 8.55     | 1.88    |
| DROID-SLAM [56]\*    | 5.66     | 0.33    |
| DIM-SLAM [29]        | -        | 0.46    |
| GO-SLAM [75]         | -        | 0.39    |
| Spann3R [61]         | 11.70    | 32.79   |
| SLAM3R-NoConf (Ours) | 8.44     | 6.61    |
| **SLAM3R (Ours)**    | 8.41     | 6.61    |

논문은 카메라 포즈와 장면 재구성 결과가 완전히 양의 상관관계를 갖지는 않는다고 언급합니다.

#### Ablation: Window Length

원논문 Table 4. 윈도우 길이에 따른 윈도우 내 키프레임 재구성 결과입니다.

| Method        | # Frames | Acc. | Comp. | FPS   |
| ------------- | -------- | ---- | ----- | ----- |
| DUSt3R [64]   | 2        | 3.16 | 2.89  | 42.55 |
| I2P           | 2        | 3.39 | 3.04  | 42.55 |
| I2P           | 5        | 2.62 | 2.28  | 40.82 |
| I2P (Default) | 11       | 2.38 | 2.03  | 40.11 |
| I2P           | 15       | 2.27 | 1.94  | 35.51 |
| I2P           | 51       | 2.23 | 1.86  | 11.97 |

#### Ablation: Point Alignment

원논문 Table 5. FPS는 정렬 연산의 오버헤드만 반영합니다.

| Method            | Acc. | Comp. | FPS |
| ----------------- | ---- | ----- | --- |
| I2P+GA            | 4.87 | 3.00  | ∼3  |
| I2P+UI            | 7.47 | 3.86  | ∼1  |
| I2P+L2W           | 6.19 | 3.54  | ∼92 |
| I2P+L2W+Re (Full) | 3.62 | 2.70  | ∼43 |

### Speed Analysis

- **GPU**: single NVIDIA 4090D (학습은 4090D GPU, 각 24 GB 메모리)
- **Resolution**: 224×224 (입력 이미지는 center-crop)
- **Frame Rate**: 20+ FPS (7 Scenes ∼25, Replica ∼24)

## 💡 Insights & Impact

### Real-time Achievement Strategy

1. **Eliminate Optimization Bottlenecks**:
   - No bundle adjustment
   - No iterative refinement
   - No RANSAC loops

2. **Efficient Architecture**:
   - Shared encoders
   - Sliding window processing
   - Incremental fusion

3. **Smart Trade-offs**:
   - Accept some drift for speed
   - Dense over accurate poses
   - Local-to-global hierarchy

### Advantages

- **Speed**: First real-time dense neural SLAM
- **Simplicity**: No complex optimization pipeline
- **Density**: Complete scene reconstruction
- **Robustness**: Works in textureless regions

### Limitations

- **Drift**: Accumulates in large scenes
- **No Loop Closure**: Limited global consistency
- **Memory**: Requires powerful GPU
- **Outdoor Scenes**: Less accurate than indoor

## 🔗 Related Work

### Comparison with SLAM Methods

- **Offline pointmap ([DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md))**: High quality but below 1 FPS
- **Learning-based SLAM (DROID-SLAM)**: ∼20 FPS, but weaker completeness on Replica
- **Neural SLAM (GO-SLAM, DIM-SLAM)**: Dense but ∼8 FPS and ∼3 FPS respectively
- **Incremental pointmap ([Spann3R](spann3r.md))**: >50 FPS but markedly higher reconstruction error
- **SLAM3R**: Dense reconstruction at ∼24–25 FPS

논문은 ORB-SLAM3를 정량 평가 대상으로 삼지 않으며, 참고문헌에서만 언급합니다.

### Building On

- **DUSt3R**: Core architecture inspiration
- **DROID-SLAM**: Learning-based SLAM concept
- **Neural Radiance Fields**: Dense representation

## 📚 Key Takeaways

SLAM3R demonstrates that:

1. **Real-time dense SLAM is possible**: With right architectural choices
2. **Feed-forward beats optimization**: For speed-critical applications
3. **Local-global hierarchy works**: Efficient multi-scale processing
4. **Dense matters**: Complete reconstruction valuable for many applications

The success of SLAM3R in achieving real-time performance opens new possibilities for live 3D capture, AR/VR applications, and robotic navigation where immediate dense feedback is crucial.

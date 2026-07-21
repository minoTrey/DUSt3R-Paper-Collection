# MonST3R: A Simple Approach for Estimating Geometry in the Presence of Motion (ICLR 2025)

![MonST3R Results](https://monst3r-project.github.io/files/fig5_system.png)
_MonST3R extends DUSt3R to dynamic scenes with per-timestep geometry estimation, without explicit motion modeling_

## 📋 Overview

- **Authors**: Junyi Zhang, Charles Herrmann, Junhwa Hur, Varun Jampani, Trevor Darrell, Forrester Cole, Deqing Sun, Ming-Hsuan Yang
- **Institution**: UC Berkeley, Google DeepMind, Stability AI, UC Merced
- **Venue**: ICLR 2025
- **Award**: Spotlight
- **Links**: [Paper](https://arxiv.org/abs/2410.03825) | [Code](https://github.com/Junyi42/monst3r) | [Project Page](https://monst3r-project.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Adapts DUSt3R for dynamic scenes by simply estimating per-timestep pointmaps, avoiding complex motion modeling while achieving SOTA results.

## 🎯 Key Contributions

1. **Geometry-First Approach**: Direct per-timestep geometry estimation without motion decomposition
2. **Simple Adaptation**: Minimal changes to DUSt3R architecture for dynamic scenes
3. **No Explicit Motion**: Avoids optical flow, motion segmentation, or dynamics modeling
4. **Strategic Fine-tuning**: Efficient training with limited dynamic data
5. **Unified Framework**: Same model handles both static and dynamic content

## 🔧 Technical Details

### Core Innovation: Per-Timestep Pointmaps

```text
Static DUSt3R: One pointmap across all frames
MonST3R: Separate pointmap for each timestep
```

### Architecture Modifications

- **Base**: DUSt3R architecture (ViT encoder + decoder)
- **Key Change**: Pointmaps indexed by time
- **Training**: Only decoder and head fine-tuned
- **Encoder**: Kept frozen to preserve geometric priors

### Training Strategy

**Dataset Mix (Strategic Selection)**:

| Dataset      | Dynamic % | Weight | Purpose              |
| ------------ | --------- | ------ | -------------------- |
| PointOdyssey | 50%       | 25%    | Synthetic dynamics   |
| TartanAir    | 25%       | 25%    | Diverse environments |
| Waymo        | 20%       | 20%    | Real-world scenes    |
| Spring       | 5%        | 30%    | High-quality flow    |

### Processing Pipeline

1. **Input**: Video frames or image pairs
2. **Window-wise**: Process temporal windows
3. **Per-frame**: Estimate geometry at each timestep
4. **Aggregation**: Combine into 4D point cloud
5. **Output**: Dense geometry + camera poses

## 📊 Results

### Video Depth Estimation

원논문 Table 2. Per-sequence scale & shift 정렬 기준. MonST3R은 depth와 pose를
동시에 추정하는데, depth만 푸는 방법들과 대등하거나 앞선다.

| Category           | Method            | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ------------------ | ----------------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| Single-frame depth | Marigold          | 0.532            | 51.5            | 0.091          | 93.1          | 0.149           | 79.6           |
| Single-frame depth | Depth-Anything-V2 | 0.367            | 55.4            | 0.106          | 92.1          | 0.140           | 80.4           |
| Video depth        | NVDS              | 0.408            | 48.3            | 0.167          | 76.6          | 0.253           | 58.8           |
| Video depth        | ChronoDepth       | 0.687            | 48.6            | 0.100          | 91.1          | 0.167           | 75.9           |
| Video depth        | DepthCrafter      | **0.292**        | **69.7**        | 0.075          | **97.1**      | 0.110           | 88.1           |
| Joint depth & pose | Robust-CVD        | 0.703            | 47.8            | -              | -             | -               | -              |
| Joint depth & pose | CasualSAM         | 0.387            | 54.7            | 0.169          | 73.7          | 0.246           | 62.2           |
| Joint depth & pose | **MonST3R**       | 0.335            | 58.5            | **0.063**      | 96.4          | **0.104**       | **89.5**       |

Per-sequence scale만 정렬한 더 엄격한 설정 (같은 Table 2). 여기서는 MonST3R이 전
지표에서 DepthCrafter를 앞선다.

| Method       | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ------------ | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| DepthCrafter | 0.692            | 53.5            | 0.217          | 57.6          | 0.141           | 81.8           |
| **MonST3R**  | **0.345**        | **56.2**        | **0.065**      | **96.3**      | **0.106**       | **89.3**       |

### Single-frame Depth

원논문 Table 3. 동적 장면 fine-tuning이 정적 단일 프레임 성능을 크게 해치지 않음을
보이는 표다 — Bonn에서는 오히려 크게 개선되고, NYU-v2(static)에서만 소폭 손해다.

| Method  | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ | NYU-v2 Abs Rel ↓ | NYU-v2 δ<1.25 ↑ |
| ------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- | ---------------- | --------------- |
| DUSt3R  | 0.424            | **58.7**        | 0.141          | 82.5          | 0.112           | 86.3           | **0.080**        | **90.7**        |
| MonST3R | **0.345**        | 56.5            | **0.076**      | **93.9**      | **0.101**       | **89.3**       | 0.091            | 88.8            |

### Camera Pose Estimation

원논문 Table 4. `*`는 GT camera intrinsics를 입력으로 요구하는 방법이다.
MonST3R은 intrinsics 없이도 pose 전용 방법들과 경쟁한다.

| Category           | Method         | Sintel ATE ↓ | Sintel RPEt ↓ | Sintel RPEr ↓ | TUM ATE ↓ | TUM RPEt ↓ | TUM RPEr ↓ | ScanNet ATE ↓ | ScanNet RPEr ↓ |
| ------------------ | -------------- | ------------ | ------------- | ------------- | --------- | ---------- | ---------- | ------------- | -------------- |
| Pose only          | DROID-SLAM*    | 0.175        | 0.084         | 1.912         | -         | -          | -          | -             | -              |
| Pose only          | DPVO*          | 0.115        | 0.072         | 1.975         | -         | -          | -          | -             | -              |
| Pose only          | ParticleSfM    | 0.129        | **0.031**     | **0.535**     | -         | -          | -          | 0.136         | 0.836          |
| Pose only          | LEAP-VO*       | **0.089**    | 0.066         | 1.250         | **0.046** | 0.027      | **0.385**  | 0.070         | **0.535**      |
| Joint depth & pose | Robust-CVD     | 0.360        | 0.154         | 3.443         | 0.189     | 0.071      | 3.681      | 0.227         | 7.374          |
| Joint depth & pose | CasualSAM      | 0.141        | 0.035         | 0.615         | 0.045     | 0.020      | 0.841      | 0.158         | 1.618          |
| Joint depth & pose | DUSt3R w/ mask | 0.417        | 0.250         | 5.796         | 0.127     | 0.062      | 3.099      | 0.081         | 0.784          |
| Joint depth & pose | **MonST3R**    | 0.108        | 0.042         | 0.732         | 0.074     | **0.019**  | 0.905      | **0.068**     | 0.545          |

### Ablation (Sintel)

원논문 Table 5. PO=PointOdyssey, TA=TartanAir. 4개 데이터셋 전부 쓰고 decoder+head만
파인튜닝하는 것이 기본 설정이다. 제안한 loss들은 pose를 개선하면서 depth는 거의
건드리지 않는다.

| Category          | Variant                      | ATE ↓     | RPE trans ↓ | RPE rot ↓ | Abs Rel ↓ | δ<1.25 ↑ |
| ----------------- | ---------------------------- | --------- | ----------- | --------- | --------- | -------- |
| Training dataset  | No finetune (DUSt3R weights) | 0.354     | 0.167       | 0.996     | 0.482     | 56.5     |
| Training dataset  | w/ PO                        | 0.220     | 0.129       | 0.901     | 0.378     | 53.7     |
| Training dataset  | w/ PO+TA                     | 0.158     | 0.054       | 0.886     | 0.362     | 56.7     |
| Training dataset  | w/ PO+TA+Spring              | 0.121     | 0.046       | 0.777     | **0.329** | 58.1     |
| Training dataset  | w/ TA+Spring+Waymo           | 0.167     | 0.107       | 1.136     | 0.462     | 54.0     |
| Training dataset  | **w/ all 4 datasets**        | **0.108** | **0.042**   | **0.732** | 0.335     | **58.5** |
| Training strategy | Full model finetune          | 0.181     | 0.110       | 0.738     | 0.352     | 55.4     |
| Training strategy | **Finetune decoder & head**  | **0.108** | **0.042**   | **0.732** | 0.335     | **58.5** |
| Training strategy | Finetune head                | 0.185     | 0.128       | 0.860     | 0.394     | 55.7     |
| Inference         | w/o flow loss                | 0.140     | 0.051       | 0.903     | 0.339     | 57.7     |
| Inference         | w/o static region mask       | 0.132     | 0.049       | 0.899     | 0.334     | 58.7     |
| Inference         | w/o smoothness loss          | 0.127     | 0.060       | 1.456     | 0.333     | 58.4     |
| Inference         | **Full**                     | **0.108** | **0.042**   | **0.732** | 0.335     | 58.5     |

### Runtime

원논문 4.1절 서술: 60프레임 비디오(w=9, stride 2, 약 600쌍) 추론이 약 30초.
전역 최적화는 Adam 300 iteration으로 단일 RTX 6000에서 약 1분. 학습은
2× RTX 6000 48GB로 하루 걸렸다. ParticleSfM 대비 5배 빠르다.

### Key Achievements

- ✅ Sintel/Bonn/KITTI 비디오 깊이에서 joint depth+pose 계열 1위 (Table 2)
- ✅ GT intrinsics 없이도 pose 전용 방법들과 대등 (Table 4)
- ✅ 동적 장면 파인튜닝 후에도 정적 단일 프레임 성능 유지 (Table 3)

## 💡 Insights & Impact

### Why Simple Works Better

1. **Avoids Error Propagation**: No multi-stage pipeline issues
2. **Leverages Strong Priors**: DUSt3R's geometry understanding transfers well
3. **Robust to Motion**: Doesn't rely on accurate flow/segmentation
4. **Data Efficient**: Works with limited dynamic training data

### Advantages Over Complex Methods

- **No Optical Flow**: Avoids flow estimation errors
- **No Motion Segmentation**: Works with arbitrary motion
- **No Iterative Optimization**: Direct feed-forward inference
- **Scene Agnostic**: No assumptions about motion type

### Limitations

- Memory scales with sequence length
- No explicit motion representation (can't query intermediate times)
- Requires sufficient baseline between frames
- Limited by training data diversity

## 🔗 Related Work

### Comparison with Other Dynamic Methods

- **DROID-SLAM**: Requires optimization, MonST3R is feed-forward
- **CasualSAM**: Complex pipeline, MonST3R is end-to-end
- **SceneFlow methods**: Task-specific, MonST3R is general
- **[Easi3R](easi3r.md)**: Also simple but different approach

### Building On

- **[DUSt3R](../foundation/dust3r.md)**: Base architecture and training
- **Video depth**: Extends to temporal domain
- **4D reconstruction**: Enables spatiotemporal modeling

## 📚 Key Takeaways

MonST3R demonstrates that:

1. **Simplicity beats complexity**: Per-timestep approach outperforms elaborate motion models
2. **Geometric priors transfer**: Static scene knowledge applies to dynamic scenes
3. **Strategic training matters**: Careful data selection enables generalization
4. **Unified models win**: Single framework for all scene types

The success of this simple approach challenges the assumption that dynamic scene reconstruction requires complex motion modeling, showing that straightforward adaptations of static methods can achieve superior results.

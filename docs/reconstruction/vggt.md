# VGGT: Visual Geometry Grounded Transformer (CVPR 2025)

![VGGT Architecture](https://vgg-t.github.io/resources/architecture_v4.png)
_VGGT unifies all geometric tasks in a single transformer: ~0.2s inference vs DUSt3R ~7s, MASt3R ~9s (원논문 Table 1·2)_

## 📋 Overview

- **Authors**: Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, David Novotny
- **Institution**: Meta GenAI, Zhejiang University
- **Venue**: CVPR 2025
- **Award**: Best Paper Award
- **Links**: [Paper](https://arxiv.org/abs/2503.11651) | [Code](https://github.com/facebookresearch/vggt) | [Project Page](https://vgg-t.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Unified transformer that jointly estimates camera parameters, depth, 3D pointmaps, and point tracks in one forward pass. ~0.2s 추론 (DUSt3R ~7s, MASt3R ~9s).

## 🎯 Key Contributions

1. **Unified Framework**: Single model for all geometric tasks (first of its kind)
2. **End-to-End Learning**: No post-processing or optimization needed
3. **Extreme Speed**: ~0.2s 추론 (원논문 Table 1·2). DUSt3R ~7s, MASt3R ~9s 대비.
4. **Scalability**: Handles 1-200+ views (vs DUSt3R's ~32 limit)
5. **Generalization**: Works on paintings, drawings, even single images

## 🔧 Technical Details

### Core Innovation: True Unified 3D Vision

```text
Traditional: Task1 → Task2 → Task3 → Optimization
VGGT: Images → Transformer → All outputs simultaneously
```

### Architecture (1.2B Parameters)

- **Image Tokenization**: DINOv2 backbone
- **Camera Tokens**: Appended for parameter prediction
- **Alternating-Attention (AA)**:
  - Frame-wise self-attention
  - Global cross-frame attention
  - Efficient multi-view processing
- **Dual Heads**:
  - Camera head: Intrinsics + Extrinsics
  - DPT head: Depth + Pointmaps + Tracks

### Joint Estimation Outputs

1. **Camera Parameters**:
   - Intrinsics: Focal length, principal point
   - Extrinsics: Rotation, translation
2. **Dense Geometry**:
   - Depth maps
   - 3D pointmaps
3. **Correspondences**:
   - Point tracks across frames

### Training Strategy

- **Multi-task Loss**: Carefully balanced weights
- **Scale**: 160K iterations on 64 A100 GPUs
- **Datasets**: Diverse 3D-annotated data
- **Key**: No geometry optimization during inference

## 📊 Results

### Dense MVS Estimation on DTU

원논문 Table 2. 지표는 Accuracy / Completeness / 그 평균인 Overall(Chamfer distance).

| Method                 | Acc. ↓    | Comp. ↓   | Overall ↓ | Time      |
| ---------------------- | --------- | --------- | --------- | --------- |
| DUSt3R                 | 1.167     | 0.842     | 1.005     | ~7s       |
| MASt3R                 | 0.968     | 0.684     | 0.826     | ~9s       |
| **VGGT (Point)**       | 0.901     | 0.518     | 0.709     | **~0.2s** |
| **VGGT (Depth + Cam)** | **0.873** | **0.482** | **0.677** | **~0.2s** |

### Camera Pose Estimation

원논문 Table 1. 10프레임 무작위 샘플, 두 지표 모두 높을수록 좋다.
Re10K로 학습한 방법은 없다.

| Method                  | Re10K (unseen) AUC@30 ↑ | CO3Dv2 AUC@30 ↑ | Time      |
| ----------------------- | ----------------------- | --------------- | --------- |
| Colmap+SPSG             | 45.2                    | 25.3            | ~15s      |
| PixSfM                  | 49.4                    | 30.1            | >20s      |
| PoseDiff                | 48.0                    | 66.5            | ~7s       |
| DUSt3R                  | 67.7                    | 76.7            | ~7s       |
| MASt3R                  | 76.4                    | 81.8            | ~9s       |
| VGGSfM v2               | 78.9                    | 83.4            | ~10s      |
| MV-DUSt3R               | 71.3                    | 69.5            | ~0.6s     |
| CUT3R                   | 75.3                    | 82.8            | ~0.6s     |
| FLARE                   | 78.8                    | 83.3            | ~0.5s     |
| Fast3R                  | 72.7                    | 82.5            | ~0.2s     |
| **VGGT (Feed-Forward)** | 85.3                    | 88.2            | **~0.2s** |
| **VGGT (with BA)**      | **93.5**                | **91.8**        | ~1.8s     |

### 추론 시간

원논문 Table 1·2가 보고하는 값. 배속은 원논문이 명시하지 않은 파생값이라 적지 않는다.

| Method   | Time      |
| -------- | --------- |
| DUSt3R   | ~7s       |
| MASt3R   | ~9s       |
| **VGGT** | **~0.2s** |

### Point Map Estimation on ETH3D

원논문 Table 3. 본문 서술 기준으로 VGGT는 Overall 점수를 DUSt3R의 **1.741에서
0.382로** 낮춘다. 전체 표는 PDF 2단 레이아웃에서 깨끗이 추출되지 않아 옮기지
않았다 — 필요하면 원논문 Table 3을 직접 확인할 것.

### Ablation: Attention 구조 (ETH3D)

원논문 Table 6. Alternating-Attention이 VGGT가 채택한 설계다.

| Attention                  | Acc. ↓    | Comp. ↓   | Overall ↓ |
| -------------------------- | --------- | --------- | --------- |
| Cross-Attention            | 1.287     | 0.835     | 1.061     |
| Global Self-Attention Only | 1.032     | 0.621     | 0.827     |
| **Alternating-Attention**  | **0.901** | **0.518** | **0.709** |

## 💡 Insights & Impact

### Paradigm Shift in 3D Vision

**Before VGGT**:

- Separate models for each task
- Complex pipelines
- Iterative optimization
- Limited scalability

**With VGGT**:

- Single unified model
- Direct prediction
- No optimization
- Extreme scalability

### Why VGGT Succeeds

1. **Shared Representation**: Joint learning improves all tasks
2. **Transformer Power**: Attention captures global relationships
3. **End-to-End Training**: Holistic optimization
4. **Minimal Bias**: Learns from data, not hand-crafted rules

### Unique Capabilities

- **Single Image**: Works where DUSt3R fails
- **Non-overlapping Views**: Handles disjoint cameras
- **Artistic Images**: Generalizes to paintings/drawings
- **Extreme Efficiency**: Real-time applications possible

### Applications

- **Instant 3D Capture**: Consumer devices
- **Robotics**: Real-time scene understanding
- **AR/VR**: Live environment mapping
- **Content Creation**: Quick 3D from images
- **Cultural Heritage**: Artwork digitization

## 🔗 Related Work

### Evolution from DUSt3R

| Aspect       | DUSt3R      | VGGT          |
| ------------ | ----------- | ------------- |
| Tasks        | 3D only     | All geometric |
| Speed        | ~7s         | ~0.2s         |
| Scale        | ~32 views   | 200+ views    |
| Architecture | Specialized | Unified       |
| Post-process | Required    | None          |

### Comparison with Other Extensions

- **MUSt3R**: Memory for scale → VGGT: Direct scale
- **Fast3R**: Speed focus → VGGT: Speed + quality
- **Test3R**: Test-time adapt → VGGT: Direct generalization

## 📚 Key Takeaways

VGGT represents a breakthrough by:

1. **Unifying all geometric tasks**: Camera, depth, 3D, tracking
2. **Achieving extreme speed**: ~0.2s vs DUSt3R ~7s / MASt3R ~9s
3. **Scaling beyond limits**: 200+ views easily
4. **Generalizing broadly**: Art, single images, any domain

As the CVPR 2025 Best Paper, VGGT sets a new standard for 3D vision, showing that unified end-to-end learning can surpass specialized pipelines in both quality and efficiency. This marks the beginning of a new era in geometric computer vision.

# VGGT: Visual Geometry Grounded Transformer (CVPR 2025)

![VGGT Architecture](https://vgg-t.github.io/resources/architecture_v4.png)
_이미지별 attention과 프레임 간 attention을 번갈아 수행한 특징에서 카메라·깊이·pointmap·추적 정보를 예측한다._

## 📋 Overview

- **Authors**: Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, David Novotny
- **Institution**: Visual Geometry Group, University of Oxford, Meta AI
- **Venue**: CVPR 2025
- **Award**: Best Paper Award
- **Links**: [Paper](https://arxiv.org/abs/2503.11651) | [Code](https://github.com/facebookresearch/vggt) | [Project Page](https://vgg-t.github.io/)
- **Verification**: CONFIRMED (venue: existing verdict 2026-07-20; 방법·결과 PDF 재검토 2026-10-15)
- **TL;DR**: 여러 RGB 이미지를 함께 처리해 카메라·깊이·3D pointmap과 추적용 특징을 예측한다. 정답 카메라 입력 없이 공통 좌표계의 기하를 추론하며 선택적으로 BA로 보정할 수 있다.

## 🎯 Key Contributions

1. **Joint Geometry**: 하나의 특징 백본에서 여러 기하 작업을 함께 학습한다.
2. **Alternating-Attention**: 이미지 안의 관계와 이미지 사이의 관계를 번갈아 처리한다.
3. **Direct Multi-View Prediction**: 쌍별 pointmap을 별도로 정렬하는 과정을 기본 추론에서 줄인다.
4. **Reusable Features**: 별도 tracking module과 downstream task에 특징을 제공한다.

## 🔧 Technical Details

### Input and Output

- **Input**: 하나 이상의 RGB 이미지. 기본 추론은 함께 받은 이미지 집합을 처리한다.
- **Output**: 카메라 회전·이동·시야각, 깊이 맵, pointmap, 추적용 특징과 query point의 2D 궤적.
- **Coordinates**: 첫 카메라를 기준으로 한다. Principal point는 이미지 중심으로 가정한다 (§3.1).

### Architecture

```text
RGB 이미지 → DINOv2 초기화 토큰
           → 이미지별 self-attention ↔ 전체 프레임 self-attention
           → camera head / DPT dense heads / query-based tracking module
```

카메라 헤드는 회전·이동·시야각을 예측한다.
DPT 헤드는 깊이·pointmap과 dense tracking feature를 출력한다.
CoTracker2 기반 tracking module은 query point와 이 특징으로 프레임별 대응 위치를 구한다 (§3.2).
따라서 DPT가 query 없이 모든 point track을 직접 출력한다고 설명하면 부정확하다.

### Inference Scope

기본 결과는 feed-forward 추론이다. 논문은 선택적으로 bundle adjustment(BA)를 추가한 결과도 보고한다.
BA는 카메라와 대응점의 재투영 오차를 줄이는 최적화다.
프레임 간 전역 attention의 비용은 이미지 수에 따라 증가하므로 긴 영상에는 chunking·streaming 등의 후속 방법이 필요하다.
"DUSt3R 최대 32장"이나 "모든 도메인에서 일반화"라는 고정 한계·보장은 원문 근거가 없어 제거했다.

## 📊 Results

### Point Map Estimation on ETH3D

[arXiv 2503.11651v1 PDF](https://arxiv.org/pdf/2503.11651v1), Table 3, PDF p.7.
지표는 Acc / Comp / Overall이다. DUSt3R·MASt3R는 global alignment를 사용한다.
VGGT는 point head 직접 출력과 depth+camera 역투영을 구분한다. 이 표는 DTU가 아니다.

| Method                 | Acc. ↓    | Comp. ↓   | Overall ↓ | Time      |
| ---------------------- | --------- | --------- | --------- | --------- |
| DUSt3R                 | 1.167     | 0.842     | 1.005     | ~7s       |
| MASt3R                 | 0.968     | 0.684     | 0.826     | ~9s       |
| **VGGT (Point)**       | 0.901     | 0.518     | 0.709     | **~0.2s** |
| **VGGT (Depth + Cam)** | **0.873** | **0.482** | **0.677** | **~0.2s** |

### Camera Pose Estimation

원논문 Table 1. 10프레임 무작위 샘플, 두 지표 모두 높을수록 좋다.
Re10K로 학습한 방법은 없다. 시간은 단일 H100에서 이 프로토콜로 측정한 값이다.

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

원논문 Table 1·3이 보고하는 값. 프레임 수와 처리 경로가 다른 임의의 실행 시간으로 일반화하지 않는다. 배속은 원논문이 명시하지 않은 파생값이라 적지 않는다.

| Method   | Time      |
| -------- | --------- |
| DUSt3R   | ~7s       |
| MASt3R   | ~9s       |
| **VGGT** | **~0.2s** |

### Dense MVS Estimation on DTU

원논문 Table 2, PDF p.7. 단위는 mm다. 위 ETH3D 결과와 별개다.
MASt3R 행은 정답 카메라를 사용하고 DUSt3R·VGGT 행은 사용하지 않는다.

| Method | GT Cameras | Acc. ↓ | Comp. ↓ | Overall ↓ |
| ------ | ---------- | ------ | ------- | --------- |
| DUSt3R | No         | 2.677  | 0.805   | 1.741     |
| MASt3R | Yes        | 0.403  | 0.344   | 0.374     |
| VGGT   | No         | 0.389  | 0.374   | 0.382     |

### Ablation: Attention 구조 (ETH3D)

원논문 Table 5, PDF p.8. Alternating-Attention이 VGGT가 채택한 설계다.

| Attention                  | Acc. ↓    | Comp. ↓   | Overall ↓ |
| -------------------------- | --------- | --------- | --------- |
| Cross-Attention            | 1.287     | 0.835     | 1.061     |
| Global Self-Attention Only | 1.032     | 0.621     | 0.827     |
| **Alternating-Attention**  | **0.901** | **0.518** | **0.709** |

## 💡 Insights & Impact

이 논문은 카메라와 깊이를 따로 추정한 뒤 맞추는 부담을 공동 학습으로 줄인다.
Depth+camera를 역투영한 점군이 point head의 직접 출력보다 좋은 경우도 있어 출력 경로를 구분해야 한다.
빠른 초기 예측은 BA의 초기값으로도 사용할 수 있다. 선택적 최적화가 무의미해졌다는 뜻은 아니다.

정답 카메라 사용 여부, 정렬 방법, 이미지 수가 다른 결과는 직접 순위로 비교하지 않는다.
시각 예시는 다양한 입력의 가능성을 보여주지만 모든 그림·센서·동적 장면의 정확성을 보장하지 않는다.

## 🔗 Related Work

### Evolution from DUSt3R

| Aspect       | [DUSt3R](../foundation/dust3r.md) | VGGT          |
| ------------ | --------------------------------- | ------------- |
| Tasks        | 3D only                           | All geometric |
| Speed        | ~7s                               | ~0.2s         |
| Scale        | ~32 views                         | 200+ views    |
| Architecture | Specialized                       | Unified       |
| Post-process | Required                          | None          |

### Comparison with Other Extensions

- **[MUSt3R](must3r.md)**: Memory for scale → VGGT: Direct scale
- **[Fast3R](fast3r.md)**: Speed focus → VGGT: Speed + quality
- **[Test3R](test3r.md)**: Test-time adapt → VGGT: Direct generalization

## 📚 Key Takeaways

1. 공통 백본이 카메라·깊이·pointmap·추적에 필요한 정보를 함께 학습한다.
2. 기본 feed-forward 경로와 BA를 추가한 경로를 구분한다.
3. ETH3D의 pointmap 평가와 DTU의 MVS 평가는 다른 표다.
4. 긴 영상의 비용과 첫 프레임 기준 좌표계를 고려해 후속 방법을 선택한다.

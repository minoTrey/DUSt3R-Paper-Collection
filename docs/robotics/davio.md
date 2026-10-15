# DAVIO: Dense Monocular-Inertial SLAM with Feed-Forward Initialization and Pose-Conditioned Mapping (arXiv 2026)

## 📋 Overview

- **Authors**: Jaafar Mahmoud, Arthur Movsesyan, Mikhail Iumanov, Sergey Kolyubin
- **Institution**: ITMO University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.27702)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.27702v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: DA3 geometry와 IMU로 VIO를 빨리 초기화하고, 이후 metric VIO pose를 DA3에 조건으로 넣어 gravity-consistent dense map을 만든다.

## 🎯 Key Contributions

1. 작은 image window와 preintegrated IMU의 feature-free initialization을 구성한다.
2. Buffered replay로 OpenVINS에 초기 상태를 전달한다.
3. Viewing-ray depth scale과 gravity-preserving submap graph를 보정한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 단안 RGB camera와 IMU; camera–IMU calibration.
- **Output**: Metric VIO state·camera trajectory, gravity-aligned dense map.
- **Problem**: 초기 VIO는 충분한 parallax를 기다리며, geometry foundation model만으로는 metric scale·gravity를 얻지 못한다.

### Method

1. DA3의 초기 camera·geometry와 IMU preintegration으로 scale·velocity·gravity·bias를 푼다.
2. Conditioning 검사와 robust solve를 통과한 상태를 OpenVINS에 replay한다.
3. 추적 중 metric pose로 DA3 mapping window를 조건화한다.
4. Camera baseline은 유지하고 ray 방향 depth scale과 gravity-preserving graph만 보정한다.

사전학습 DA3와 visual–inertial estimation을 연결한 시스템이다. Map graph는 output map frame을 바꾸며 동작 중 VIO filter 자체와 구분된다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.27702v1), Table II, PDF p.6.

EuRoC의 132개 ten-second initialization windows. Success는 window 안에서 ATE 0.5m 미만 궤적을 발행한 수, Tq는 실패 penalty를 포함한 median 시간이다.

| Initializer | Success | Tq (s) ↓ | ATE (m) ↓ |
| ----------- | ------- | -------- | --------- |
| OpenVINS    | 111/132 | 3.87     | 0.042     |
| DAVIO       | 109/132 | 2.66     | 0.044     |

초기 발행 시간은 빨라지지만 성공 수와 median ATE는 baseline보다 좋지 않다. Mapping 결과는 동일 pose 비교·자체 odometry·GT pose 조건을 분리한다.

## 💡 Insights & Impact

추론 geometry가 관성 초기화를 돕고, 이후 관성의 metric pose가 다시 geometry 모델을 돕는다.

- IMU calibration·motion excitation·conditioning에 의존한다.
- 조기 초기화와 높은 성공률은 같은 목표가 아니다.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): 초기화·mapping에 공통 사용.
- [MASt3R-Fusion](mast3r-fusion.md): visual–inertial mapping 비교 맥락.

## 📚 Key Takeaways

1. RGB-only가 아니라 IMU를 받는다.
2. 초기 geometry와 metric VIO가 양방향으로 연결된다.
3. Startup·tracking·mapping 결과를 분리한다.

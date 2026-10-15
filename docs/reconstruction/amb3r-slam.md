# AMB3R-SLAM: Kilometer-scale SLAM with Hierarchical Backend (arXiv 2026)

## 📋 Overview

- **Authors**: Hengyi Wang, Lourdes Agapito
- **Institution**: University College London
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.19518)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.19518v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 가벼운 geometry frontend와 큰 모델의 장기 문맥 backend를 결합하여 긴 영상의 상대 pose 오차를 여러 거리 수준에서 보정한다.

## 🎯 Key Contributions

1. 고빈도 frontend와 저빈도 장기 문맥 mapping을 분리한다.
2. 겹치는 submap의 짧은 범위 제약과 장거리 제약을 결합한다.
3. 단안·스테레오·LiDAR 입력 조건을 각각 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간순 영상; 구성에 따라 단안, 스테레오 또는 LiDAR를 이용한다.
- **Output**: 전역적으로 연결된 궤적과 장면 geometry.
- **Problem**: 짧은 문맥의 odometry 오차가 긴 주행에서 누적되고 모든 프레임을 큰 모델로 처리하기 어렵다.

### Method

1. 기본 frontend는 DA3-Small로 지역 geometry를 추정한다. 논문 이름을 AMB3R backbone 사용과 동일시하면 안 된다.
2. 겹치는 local submap의 span-2 edge로 가까운 범위의 오차를 보정한다.
3. 큰 DA3 backend의 sparse long-context 예측으로 중간 거리 제약을 만든다.
4. Loop closure와 전역 정렬로 먼 시점의 상태를 연결한다.

대형 모델의 geometry prior를 추론에 이용하는 시스템이다. 모델별 frontend FPS와 전체 SLAM 지연은 구분해야 한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.19518v1), Table 2, PDF p.5.

KITTI 평균 ATE(m). 아래 행은 모두 단안 조건이며 offline과 online 처리는 구분하였다.

| Method     | Processing        | Mean ATE (m) ↓ |
| ---------- | ----------------- | -------------- |
| Scal3R     | Offline           | 14.55          |
| Glob3R     | Offline           | 13.21          |
| LoGeR      | Online            | 18.65          |
| AMB3R-SLAM | Online, monocular | 13.11          |

같은 표의 스테레오 12.15m와 LiDAR 0.95m는 추가 입력 조건이므로 단안 개선량으로 제시하지 않는다. 단안 sequence 01은 55.91m로 Scal3R 45.29m보다 나쁘다.

## 💡 Insights & Impact

모든 프레임에서 큰 모델을 실행하는 대신 장기 문맥이 필요한 시점에만 큰 모델의 제약을 추가한다.

- 정적 장면 geometry 가정과 loop 연결의 신뢰성이 중요하다.
- 입력 modality와 online/offline 차이가 있으므로 평균 한 개로 방법 전체의 우열을 단정할 수 없다.

## 🔗 Related Work

- [VGGT](vggt.md): feed-forward geometry 계열.
- [Depth Anything 3](depth-anything-3.md): 기본 geometry 모델 계열.

## 📚 Key Takeaways

1. 작은 frontend와 큰 backend의 역할을 구분한다.
2. 이름만 보고 AMB3R 모델 사용이라고 해석하지 않는다.
3. 단안·스테레오·LiDAR 수치를 분리한다.

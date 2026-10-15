# On-the-Fly3R: Towards Robust Online 3D Reconstruction with Feed-Forward 3R Models for Large-Scale UAV Scenarios (arXiv 2026)

## 📋 Overview

- **Authors**: Zhe Shen, Liyuan Lou, Yifei Yu, Guanbo Wang, Quanjian Ji, Xin Wang, Zongqian Zhan
- **Institution**: Wuhan University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.00923)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.00923v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Retrieval로 관련 UAV 이미지를 모아 소규모 3D 추론을 반복하고, 전역 지도에 넣기 전에 정렬을 검사·거절·재시도한다.

## 🎯 Key Contributions

1. 약한 순서 또는 무순서 이미지에서 동적으로 subset을 만든다.
2. Confidence-weighted Sim(3)과 validation–retry를 결합한다.
3. Retrieval loop closure와 pose graph로 긴 범위 drift를 조정한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: UAV RGB 이미지 stream; 강한 시간 연속성은 요구하지 않는다.
- **Output**: 수락된 이미지의 camera pose와 dense 지도 및 coverage.
- **Problem**: 관련 없는 view가 한 chunk에 들어가면 잘못된 geometry가 이후 지도 전체로 전파된다.

### Method

1. SupScene descriptor로 과거 reference를 검색한다.
2. Reference overlap과 시각적 유사도를 만족하는 query만 batch에 모은다.
3. 공유 reference의 pointmap을 confidence-weighted robust Sim(3)으로 정렬한다.
4. 일관성 검사를 통과하지 못하면 해당 update를 거절하고 다른 subset으로 재시도한다.
5. 검색한 loop edge를 GTSAM pose graph에 넣는다.

Pi3·Pi3X·VGGT-Omega 등 기존 3R 모델을 감싸는 시스템이다. 수락하지 못한 frame이 있으므로 오차와 coverage를 함께 보고한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.00923v1), Table II, PDF p.6.

6개 UAV 장면에서 Pi3X 구성으로 수락한 공통 frame 집합에 대한 macro-average. ATE는 m, ARE/RTE/RRE는 원문 정의의 angular error이다. 아래는 ATE만 발췌했다.

| Method              | Common-frame ATE (m) ↓ |
| ------------------- | ---------------------- |
| LingBot-Map         | 205.62                 |
| MERG3R              | 124.42                 |
| On-the-Fly3R (Pi3X) | 18.56                  |

공통 집합은 전체 입력의 95.39%다. 따라서 전체 frame 성공을 뜻하지 않으며, 반환된 pose만 평가하는 Table I와도 다르다.

## 💡 Insights & Impact

좋지 않은 지역 예측을 지도에 넣지 않는 결정도 geometry 모델 자체의 정확도만큼 중요하다.

- Coverage가 낮아질 수 있고 retrieval 실패를 완전히 제거하지 못한다.
- 재시도·정렬·PGO 비용이 있으며 한 번의 network forward만으로 끝나지 않는다.

## 🔗 Related Work

- [GeoFF3D](geoff3d.md): 위치 prior와 공간 분할을 이용하는 UAV 방법.
- [VGGT](vggt.md): 지원 backbone 계열.

## 📚 Key Takeaways

1. 무순서 입력을 retrieval로 지역화한다.
2. 검증하지 못한 update는 거절할 수 있다.
3. 오차와 coverage를 반드시 함께 읽는다.

# UniSim-SLAM: Feed-Forward SLAM with Unified Sim(3) Optimization (arXiv 2026)

## 📋 Overview

- **Authors**: Inha Lee, Dongjae Jeong, Junhee Lee, Kyungdon Joo
- **Institution**: Ulsan National Institute of Science and Technology (UNIST)
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.01706)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.01706v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 빠른 두 시점 추적과 주기적인 다중 시점 submap을 하나의 Sim(3) 그래프로 묶어, 카메라 보정값 없이 생기는 지역별 크기 차이를 줄인다.

## 🎯 Key Contributions

1. 두 시점 frontend와 다중 시점 backend를 서로 다른 주기로 실행한다.
2. Keyframe과 submap의 pose·scale을 함께 최적화한다.
3. 두 수준을 잇는 bridge와 깊이 통계 기반 scale anchor를 사용한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 보정되지 않은 단안 RGB 영상. 평가에서 깊이 센서를 입력으로 사용하지 않는다.
- **Output**: 카메라 궤적과 서로 정렬된 dense submap.
- **Problem**: 독립적으로 예측한 pointmap은 서로 다른 좌표계와 scale을 가지며, 매 프레임 다중 시점 추론을 하면 지연이 커진다.

### Method

1. 두 시점 모델로 인접 keyframe의 지역 geometry와 상대 이동을 빠르게 추정한다.
2. 겹치는 keyframe으로 구성한 submap에서 다중 시점 geometry를 주기적으로 예측한다.
3. View–view, view–submap bridge, submap 간 제약을 동일 그래프에 넣는다.
4. 깊이 통계와 scale 제약으로 두 수준의 gauge 차이를 조정하고 Sim(3) 상태를 최적화한다.

추론 시에는 사전학습 geometry 모델과 그래프 최적화를 결합한다. 실험의 submap 크기는 16, overlap은 2이며 keyframe stride는 데이터셋별로 다르다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.01706v1), Tables 1–2, PDF p.11.

GT intrinsics가 없는 조건의 평균 ATE(m). Evo와 Umeyama Sim(3) 정렬을 사용한다. 보정된 카메라를 쓰는 다른 행과 섞지 않았다.

| Dataset   | VGGT-SLAM | ViSTA-SLAM | UniSim-SLAM |
| --------- | --------- | ---------- | ----------- |
| TUM RGB-D | 0.061     | 0.052      | 0.032       |
| 7-Scenes  | 0.037     | 0.049      | 0.020       |

평균은 낮아지지만 TUM plant는 UniSim 0.029m, VGGT-SLAM 0.023m로 반대이다. 전체 파이프라인에는 최적화 비용이 있다.

## 💡 Insights & Impact

지역 예측을 잘하는 모델이라도 지역 간 좌표계의 연결은 별도 문제다. 이 논문의 중심은 그 연결을 두 수준에서 동시에 조정하는 것이다.

- 장면별 평균 개선이 모든 시퀀스의 개선을 뜻하지 않는다.
- Submap overlap과 geometry 예측 품질에 의존하며, loop closure 실패 가능성이 남는다.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md): 다중 시점 geometry 예측 배경.
- [MASt3R](../foundation/mast3r.md): 두 시점 geometry와 matching 계열.

## 📚 Key Takeaways

1. 입력은 RGB이며 출력은 궤적과 지도다.
2. 빠른 추적과 느린 다중 시점 보정을 bridge로 연결한다.
3. ATE의 정렬 방식과 camera 조건을 함께 읽는다.

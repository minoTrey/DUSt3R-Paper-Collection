# F$^2$ SLAM: Turning Feed-Forward Geometry into Persistent Factors for SLAM (arXiv 2026)

## 📋 Overview

- **Authors**: Zhisong Xu, Fan Zhu, Jiawei Qian, Ziyu Chen, Zhenjun Zhao, Javier Civera
- **Institution**: University of Tokyo, Tohoku University, University of Science and Technology of China, University of Zaragoza
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.05207)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.05207v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 빠른 DROID 추적 그래프에 느린 Flow3r의 geometry 예측을 일관성 검사 후 주입하여 동일한 pose·depth 상태를 보정한다.

## 🎯 Key Contributions

1. 서로 다른 속도의 두 추론 stream을 결합한다.
2. 별도 submap이 아니라 지속되는 factor graph를 갱신한다.
3. Support state의 일관성을 확인한 뒤 target과 weight를 바꾼다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 단안 RGB 영상과 선택적으로 주어진 camera intrinsics.
- **Output**: 카메라 궤적, inverse-depth map, 구성에 따라 intrinsics 추정.
- **Problem**: 빠른 local tracking은 drift가 누적되고 느린 geometry 모델의 예측을 검증 없이 넣으면 현재 상태와 충돌한다.

### Method

1. DROID-Net이 고빈도 tracking과 factor graph를 유지한다.
2. 저빈도 stream에서 DINO feature와 Flow3r를 사용해 pose·depth·displacement confidence를 예측한다.
3. 지원 상태의 일관성을 검사해 사용할 예측을 선택한다.
4. 기존 graph의 target과 weight를 갱신하고 같은 pose·inverse-depth 변수에 dense BA를 수행한다.

사전학습 예측과 graph 최적화를 결합한다. State validation threshold와 최적화 objective의 weight는 역할이 다르다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.05207v1), Table 1, PDF p.6; Table 2, PDF p.7.

평균 ATE(m). Calibrated는 GT intrinsics 사용, uncalibrated는 intrinsics가 주어지지 않는 조건이다.

| Dataset  | Intrinsics   | DROID-SLAM | F2SLAM |
| -------- | ------------ | ---------- | ------ |
| TUM      | Calibrated   | 0.038      | 0.029  |
| TUM      | Uncalibrated | 0.163      | 0.027  |
| 7-Scenes | Calibrated   | 0.050      | 0.053  |
| 7-Scenes | Uncalibrated | 0.078      | 0.051  |

7-Scenes의 calibrated 조건에서는 오히려 평균 ATE가 증가한다. Camera 조건을 숨기면 큰 개선처럼 보일 수 있으므로 각 행을 구분했다.

## 💡 Insights & Impact

새 geometry를 만드는 것뿐 아니라 기존 tracker의 상태와 충돌하지 않게 반영하는 방법이 중요하다.

- BA를 포함하므로 전체 시스템이 최적화 없는 feed-forward 방식은 아니다.
- 일관성 gate가 좋은 제약을 버리거나 나쁜 예측을 받아들일 수 있다.

## 🔗 Related Work

- [DROID 계열과 연결되는 MASt3R](../foundation/mast3r.md): 학습 matching·geometry 배경.
- [VGGT](../reconstruction/vggt.md): geometry 모델을 SLAM에 연결하는 비교 맥락.

## 📚 Key Takeaways

1. 빠른 tracker와 느린 geometry stream의 상태를 공유한다.
2. 예측을 검증한 뒤 기존 graph에 넣는다.
3. 보정값 유무에 따른 결과를 분리한다.

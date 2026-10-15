# Pow3R-SLAM: Real-Time RGB-D SLAM with 3D Reconstruction Priors (arXiv 2026)

## 📋 Overview

- **Authors**: Christopher Kolios, Ishaan Mehta, Sasa Janjic, Yeganeh Bahoo, Sajad Saeedi
- **Institution**: Toronto Metropolitan University, University of Windsor, University College London
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.38054)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.38054v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Pow3R의 depth-conditioned pointmap을 MASt3R-SLAM 계열 최적화에 연결하고, 선택적으로 센서 깊이 ICP를 번갈아 사용한다.

## 🎯 Key Contributions

1. 센서 depth로 pointmap의 metric scale과 geometry를 안내한다.
2. Encoder token과 confidence로 retrieval·loop 연결을 재구성한다.
3. Neural keyframe 사이에서 point-to-plane ICP를 사용하는 hybrid 구성을 비교한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: RGB와 정렬된 depth 영상 및 camera calibration.
- **Output**: 카메라 궤적과 keyframe 기반 dense 지도.
- **Problem**: RGB만으로 추정한 pointmap은 scale과 표면 geometry가 불안정할 수 있고 매 프레임 neural 추론은 비싸다.

### Method

1. Pow3R가 RGB와 depth conditioning으로 pointmap을 예측한다. 센서 depth 자체를 단순 누적하는 방식은 아니다.
2. MASt3R-SLAM의 projective matching·second-order backend를 depth anchor와 함께 사용한다.
3. Matching head가 없는 Pow3R에 맞춰 encoder token·confidence 기반 retrieval을 구성한다.
4. Hybrid에서는 번갈아 오는 프레임에 depth ICP를 사용한다. ICP 프레임은 keyframe이나 지도 확장에 쓰지 않는다.

사전학습 Pow3R와 추론 시 tracking·최적화를 사용한다. 평가의 7-Scenes 영상은 color–depth를 다시 정렬한 입력이며 원래 입력의 misregistration과 구분해야 한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.38054v1), Table I, PDF p.5; Table II, PDF p.6.

아래는 Sim(3) 정렬한 keyframe 평균 ATE(m). 동일 논문에서 재실행한 MASt3R-SLAM과 비교한다.

| Dataset             | MASt3R-SLAM | Pow3R-SLAM | Hybrid |
| ------------------- | ----------- | ---------- | ------ |
| TUM fr1             | 0.030       | 0.027      | 0.025  |
| Registered 7-Scenes | 0.048       | 0.044      | 0.048  |
| Replica             | 0.0153      | 0.0087     | 0.0096 |

7-Scenes stairs에서는 0.016/0.044/0.062m로 baseline이 더 좋다. ETH3D 결과는 baseline 완료 16개와 제안법 완료 14개의 평균이므로 완료 수를 숨긴 단순 비교를 피해야 한다.

## 💡 Insights & Impact

Depth는 network conditioning, scale, backend anchor라는 서로 다른 경로로 쓰인다. Hybrid의 속도 이득은 모든 프레임에서 dense map을 갱신하는 결과가 아니다.

- 센서 depth 품질과 color–depth 정렬이 필요하다.
- Tracking 실패와 완료 시퀀스 수를 평균 오차와 함께 보아야 한다.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): 기반 SLAM의 matching 계열.
- [Pow3R](../reconstruction/pow3r.md): depth-conditioned geometry 모델.

## 📚 Key Takeaways

1. 출력 지도는 모델이 예측한 pointmap을 사용한다.
2. ICP 프레임은 지도 keyframe과 역할이 다르다.
3. 입력 정렬과 완료 수가 성능 해석을 바꾼다.

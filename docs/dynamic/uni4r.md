# Marrying Optimal Transport and ODEs for Unified Continuous-Time 4D Reconstruction and Tracking (arXiv 2026)

## 📋 Overview

- **Authors**: Liying Yang, Hao Mo, Jialun Liu, Chen Liu, Xinxing Yu, Chenhao Guan, Hui Ma, Xiao Cao, Ajian Liu, Yanyan Liang
- **Institution**: Macau University of Science and Technology, University of Queensland, Great Bay University, Tsinghua University, National University of Singapore, Institute of Automation Chinese Academy of Sciences
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.09613)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.09613v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 연속 시간 velocity field를 학습하고 ODE로 적분하여 integer frame 사이에서도 pointmap과 point trajectory를 예측한다.

## 🎯 Key Contributions

1. 4D reconstruction과 tracking을 같은 continuous velocity로 연결한다.
2. OT 기반 anchor feature의 flow-matching decoder를 구성한다.
3. Integer GT만으로 fractional time을 학습하는 integral consistency를 사용한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간 정보가 있는 RGB 영상 sequence와 tracking query.
- **Output**: 임의 timestamp의 world-coordinate pointmap·3D trajectory.
- **Problem**: Frame별 예측이나 임의 interpolation은 중간 시간의 운동·표면 구조를 일관되게 유지하기 어렵다.

### Method

1. Global velocity branch가 sequence의 anchor feature를 추출한다.
2. Optimal transport 경로와 flow matching으로 velocity feature를 학습한다.
3. Reconstruction feature·time embedding을 local velocity predictor에 결합한다.
4. ODE solver로 velocity를 적분해 정수 시간의 GT pointmap과 맞추는 loss를 준다.

Point Odyssey·Dynamic Replica·Kubric의 정수 timestamp supervision을 사용한다. 중간 시간 결과는 추가 GT velocity를 직접 준 것이 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.09613v2), Table 2, PDF p.6.

World-coordinate 4D reconstruction, global median scaling 후 APD/EPE. PO는 Point Odyssey다. 아래 방법들은 feed-forward block의 행이다.

| Dataset      | Method    | APD ↑ | EPE ↓ |
| ------------ | --------- | ----- | ----- |
| PO           | St4RTrack | 78.73 | 0.241 |
| PO           | Uni4R     | 80.71 | 0.222 |
| TUM-Dynamics | St4RTrack | 83.42 | 0.185 |
| TUM-Dynamics | Uni4R     | 84.36 | 0.181 |

연속 시간 kinematic metric은 별도 benchmark이며, 표의 정수시간 reconstruction 결과와 섞지 않는다. Solver step에 따라 정확도·시간이 달라진다.

## 💡 Insights & Impact

점 위치를 시간마다 독립적으로 회귀하지 않고 같은 velocity field가 reconstruction과 tracking을 설명하게 한다.

- ODE integration error와 잘못된 velocity가 누적될 수 있다.
- 임의 timestamp 출력이 실제 fractional-time GT를 충분히 관측했다는 뜻은 아니다.

## 🔗 Related Work

- [MonST3R](monst3r.md): dynamic geometry 비교 계열.
- [V-DPM](v-dpm.md): reconstruction·tracking 비교 모델.

## 📚 Key Takeaways

1. 연속 velocity를 적분해 중간 frame을 예측한다.
2. Integer supervision과 integral consistency를 결합한다.
3. 정렬·solver 조건을 결과와 함께 적는다.

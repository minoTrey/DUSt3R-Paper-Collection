# Noctif3R: Feed-Forward Monocular Real-Time SLAM for Photon-Limited Scenes on Embedded Hardware (arXiv 2026)

## 📋 Overview

- **Authors**: Mihir Chauhan, Aditya Uday Abhang, Kevin Biju Mathew, Aniket Bera
- **Institution**: Purdue University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.21114)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.21114v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 저조도 pointmap tracking에 명시적인 match gate를 두고 embedded backend 비용을 줄인다. 잘못된 궤적을 계속 출력하지 않는 대신 coverage를 잃는 한계를 측정한다.

## 🎯 Key Contributions

1. 완성된 궤적과 실제 motion 정보를 가진 궤적을 구분한다.
2. Tracking과 mapping 해상도를 분리해 embedded 비용을 줄인다.
3. 빛이 거의 없는 영상에서 중지·실패를 명시적으로 보고한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 단안 low-light RGB frame과 capture timestamp. Depth·stereo·IMU는 사용하지 않는다.
- **Output**: 추적 가능한 구간의 pose와 pointmap 지도; gate 실패 시 중단할 수 있다.
- **Problem**: 매우 어두운 영상에서 모델이 그럴듯하지만 motion 정보가 없는 full-length trajectory를 출력할 수 있다.

### Method

1. MASt3R-SLAM 계열 low-light pointmap frontend로 대응점을 예측한다.
2. Match gate를 통과한 관측에서 상대 Sim(3)를 푼다.
3. Pose graph와 retrieval edge를 Gauss–Newton으로 보정한다.
4. Mapping·tracking 해상도와 backend 계산을 분리해 memory·latency를 줄인다.

Low-light geometry weight를 사용하는 deployment·측정 연구다. 실시간이라는 제목을 일반 영상의 일정 FPS 보장으로 해석하지 않는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.21114v1), Table I, PDF p.3.

Synthetic tripod-still chapel −10dB, Jetson AGX Orin MAXN, arm별 3회. ATE는 m가 아니라 no-information ceiling 대비 percentage다.

| Measure              | Previous deployment | NOCTIF3R |
| -------------------- | ------------------- | -------- |
| Poses/s ↑            | 2.512               | 3.204    |
| ATE (% of ceiling) ↓ | 21.47               | 20.70    |
| Peak CUDA (GiB) ↓    | 20.70               | 10.95    |
| Energy/pose (J) ↓    | 14.84               | 10.47    |

낮은 error와 좁은 coverage를 함께 보고한다. 대부분 frame이 완전히 검은 실제 robot 영상에서는 모든 제안 구성이 밝은 시작 뒤 멈췄으며 darkness 해결을 주장하지 않는다.

## 💡 Insights & Impact

잘못된 추정을 계속 내는 실패와 출력을 중단하는 실패는 로봇에서 다른 의미를 갖는다.

- Tracking loss가 사실상 복구되지 않는 구간이 있고 coverage가 좁다.
- Synthetic noise ladder·display gain·실제 delivered frame을 구분해야 한다.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): pointmap matching 계열.
- [VGGT-SLAM](../reconstruction/vggt-slam.md): 저조도 비교 시스템.

## 📚 Key Takeaways

1. Gate는 오류뿐 아니라 coverage를 바꾼다.
2. Backend 비용이 embedded 속도를 제한한다.
3. 완전히 어두운 실영상의 실패도 결과다.

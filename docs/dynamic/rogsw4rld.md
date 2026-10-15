# RoGSW4RLD: Feed-Forward 4D Gaussian Lifting for Robot World Model Rollouts (arXiv 2026)

## 📋 Overview

- **Authors**: Jin Hyun Kim, Min Young Kim, Soohwan Song, Daekyum Kim
- **Institution**: Korea University, Dongguk University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.35311)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.35311v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 여러 camera의 robot rollout을 calibration·robot mesh·관절 상태로 함께 lift하여 metric 4D Gaussian field로 만든다.

## 🎯 Key Contributions

1. 독립 camera별 재구성 대신 view·time token을 함께 처리한다.
2. Robot mesh와 forward kinematics로 metric geometry·motion을 안내한다.
3. 고정 weight의 recurrent rendering-feedback refinement를 추가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 동기화된 recorded/generated RGB rollout, calibrated camera trajectory·intrinsics, robot mesh·joint/gripper state.
- **Output**: 임의 query time·view에서 render할 수 있는 metric 4D Gaussian scene.
- **Problem**: Video world model의 서로 다른 camera 영상을 따로 복원해 합치면 robot motion과 scale이 일치하지 않는다.

### Method

1. MoVieS/VGGT 계열 backbone에 camera·time encoding과 LoRA를 적용한다.
2. Robot-support pixel의 depth를 mesh로 anchor한다.
3. FK displacement를 motion head에 넣어 shared Gaussian field를 만든다.
4. Stage 2는 rendering feedback과 time-shared correction으로 위치·appearance를 recurrent하게 정제한다.

두 단계 모두 inference weight는 고정이며 per-scene gradient optimization이 아니다. 새로운 행동 dynamics를 학습하는 world model이 아니라 기존 rollout의 4D lifting이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.35311v1), Table 1, PDF p.8.

Recorded observations 256 clips. Novel-view PSNR·LPIPS와 robot displacement EPE(mm). 아래는 제안법 두 단계의 비교다.

| Configuration | Novel PSNR ↑ | Novel LPIPS ↓ | Robot EPE (mm) ↓ | Time (s) ↓ |
| ------------- | ------------ | ------------- | ---------------- | ---------- |
| Stage 1       | 15.52        | 0.363         | 8.6              | 0.59       |
| Stage 1+2     | 16.08        | 0.371         | 8.6              | 9.08       |

Refinement은 PSNR을 높이지만 LPIPS는 나빠지고 robot EPE는 변하지 않는다. Metric 결과는 calibration·mesh·joint input을 전제로 한다.

## 💡 Insights & Impact

Vision rollout을 시공간 질의가 가능한 representation으로 바꾸되 robot의 알려진 geometry를 활용한다.

- 동기화·hand–eye calibration·robot model 오차에 의존한다.
- Generated rollout의 물리적 진실성을 reconstruction이 보장하지 않는다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): MoVieS backbone의 기반 계열.
- [Uni4R](uni4r.md): 다른 continuous-time geometry 구성.

## 📚 Key Takeaways

1. Camera·robot state가 주어진 metric lifting이다.
2. World-model rollout 자체를 새로 예측하지 않는다.
3. Refinement의 지표·시간 trade-off를 보존한다.

# 4D-HOF: Hand-Object Flow Matching for Feed-Forward 4D Interaction Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Shiqi Li, Sean Cho, Yijie Li, Fengzhi Guo, Bowen Wen, Cheng Zhang
- **Institution**: Texas A&M University, NVIDIA
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.08782)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.08782v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 여러 foundation model의 거친 손·물체 초기 상태를 conditional flow로 옮겨 interaction을 정제하고 생성 과정 안에서 physical·2D guidance를 적용한다.

## 🎯 Key Contributions

1. 순수 noise 대신 구조 있는 HOI 초기화에서 transport를 시작한다.
2. Point-cloud·image feature로 조건부 temporal flow를 학습한다.
3. Contact·penetration·관측 evidence로 test-time guidance한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 처음 보는 object와 손이 상호작용하는 단안 RGB 영상.
- **Output**: 시간별 hand MANO·object mesh pose와 4D interaction.
- **Problem**: 초기 hand·object estimate는 각각 그럴듯해도 상대 translation·contact가 맞지 않는다.

### Method

1. MoGe-3·SAM3 등으로 depth·camera·mask를 추정한다.
2. WiLoR hand와 생성 object·FoundationPose로 초기 HOI state를 만든다.
3. PTv3 point feature·DINOv2 image feature·temporal DiT로 conditional bridge velocity를 학습한다.
4. Flow 중간 state에 physical·image-space guidance를 적용한다.

HO-Cap·OakInk·SHOWMe 등에서 perturbed state→GT transport를 학습한다. DUSt3R backbone 수정 논문은 아니며 monocular geometry model을 초기화에 직접 사용하는 응용이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.08782v1), Table 1, PDF p.7.

HO3D-v3의 선택한 18 sequence, AGILE protocol. MPJPE mm, hand-relative CD cm², contact accuracy percentage다.

| Method | Hand-relative CD (cm²) ↓ | Contact accuracy (%) ↑ | Hand MPJPE (mm) ↓ |
| ------ | ------------------------ | ---------------------- | ----------------- |
| AGILE  | 15.81                    | Not reported           | 3.92              |
| 4D-HOF | 5.98                     | 97.27                  | 4.40              |

Hand MPJPE는 AGILE보다 나쁘다. AGILE code가 없어 원문 보고값과 비교하며 object shape는 ICP 정렬 뒤 평가하는 별도 지표다.

## 💡 Insights & Impact

강한 초기화에서 interaction만 고치면 무작위 생성보다 transport 문제를 좁힐 수 있다.

- 초기 object 생성·mask·depth 모델의 오류와 비용이 남는다.
- Guidance gradient·여러 사전모델을 포함하므로 단일 geometry network의 속도로 요약하면 안 된다.

## 🔗 Related Work

- [EgoFound3R](egofound3r.md): 손 geometry·interaction을 공동 예측하는 다른 방법.
- [DUSt3R](../foundation/dust3r.md): 응용 범위를 비교할 dense geometry 배경.

## 📚 Key Takeaways

1. 거친 HOI state를 학습 flow로 정제한다.
2. 주요 이득은 interaction이며 모든 hand metric이 최고는 아니다.
3. 초기화·guidance 비용을 전체 시간에 포함한다.

# FFVO: A Feedforward Pose Decoder for Long-Horizon Visual Odometry (arXiv 2026)

## 📋 Overview

- **Authors**: Meng-Li Shih, Shih-Yang Su, Yuliang Zou, Hao Xiang, Haidong Zhu, Vincent Casser, Brian Curless, Dmitry Kalenichenko, Mingxing Tan, Dragomir Anguelov
- **Institution**: Waymo LLC, University of Washington, Google DeepMind
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.13733)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.13733v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: π3의 geometry feature는 고정하고 시간 계층 구조를 갖는 camera decoder를 학습하여 주행 영상의 visual odometry를 예측한다.

## 🎯 Key Contributions

1. Geometry 표현을 보존하면서 camera branch를 별도로 학습한다.
2. 지역·전역 temporal attention으로 짧은 이동과 긴 궤적을 함께 다룬다.
3. 중간 trajectory supervision과 camera augmentation의 영향을 분리해 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 주행 RGB 영상 sequence.
- **Output**: 프레임별 카메라 궤적.
- **Problem**: 일반 3D 모델의 pose head가 주행 영상의 작은 이동과 긴 시간 의존성을 충분히 학습하지 못한다.

### Method

1. π3 geometry feature aggregator를 고정한다.
2. Compact camera token에 지역·전역 temporal decoder를 적용한다.
3. Camera branch를 처음부터 학습하고 중간 단계 궤적에도 supervision을 준다.
4. FFVO-Long에서는 window별 결과에 VGGT-Long 기반 trajectory 후처리를 추가한다.

Camera decoder의 학습이 필요하다. FFVO-Long의 후처리가 있는 긴 영상 결과와 기본 FFVO의 직접 예측은 구분한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.13733v1), Table 1, PDF p.6.

Waymo Open Dataset(WOD) 평가. ATE와 translation RPE는 m, rotation RPE는 degree이며 낮을수록 좋다.

| Method                    | ATE (m) ↓ | RPE trans (m) ↓ | RPE rot (°) ↓ |
| ------------------------- | --------- | --------------- | ------------- |
| π3                        | 1.150     | 0.156           | 0.113         |
| π3 fine-tuned             | 1.170     | 0.332           | 0.125         |
| FFVO without augmentation | 0.714     | 0.118           | 0.124         |
| FFVO                      | 0.862     | 0.114           | 0.128         |

Augmentation은 이 표에서 translation RPE를 낮추지만 ATE와 rotation RPE는 개선하지 않는다. 별도 PDD 결과는 비공개 데이터이므로 공개 재현성에 한계가 있다.

## 💡 Insights & Impact

Geometry backbone의 일반 표현을 그대로 두고 시간적 pose 추정 부분을 특화한다.

- 주행 도메인 학습과 camera 구성의 영향을 받는다.
- ATE·RPE가 동시에 좋아지는 것은 아니며, 긴 영상 후처리의 계산도 고려해야 한다.

## 🔗 Related Work

- [π3](../foundation/pi3.md): 고정 feature backbone.
- [VGGT](../foundation/vggt.md): 장기 trajectory 처리 계열의 배경.

## 📚 Key Takeaways

1. 입력 영상에서 카메라 궤적을 출력한다.
2. 학습 대상은 주로 temporal camera branch다.
3. Augmentation 효과를 지표별로 읽는다.

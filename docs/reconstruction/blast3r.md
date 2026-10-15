# BLASt3R: Bundle Adjustment of Any Image Set with Multi-View Matching and Monocular Priors (arXiv 2026)

## 📋 Overview

- **Authors**: Vincent Leroy, Philippe Weinzaepfel, Lojze Zust, Yohann Cabon, Jérome Revaud
- **Institution**: NAVER LABS Europe
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.05210)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.05210v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 학습한 다중 시점 대응점과 조절 가능한 깊이 prior를 bundle adjustment에서 결합하여, 순서 없는 이미지 재구성과 온라인 SLAM을 처리한다.

## 🎯 Key Contributions

1. 메모리를 재사용하는 다중 시점 dense matching을 학습한다.
2. 단안 pointmap prior를 affine log-depth 형태로 조절한다.
3. 대규모 dense 행렬을 직접 만들지 않는 효율적인 BA solver를 구성한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 순서 없는 RGB 이미지 또는 시간순 영상.
- **Output**: 카메라 pose와 정렬된 dense geometry.
- **Problem**: 학습 geometry의 장면 일반화 오류와 전통 matching·BA의 비용을 함께 줄여야 한다.

### Method

1. CroCo로 초기화한 matcher가 query에서 저장된 여러 view로 dense flow를 예측한다.
2. 대응점을 track으로 연결하고 단안 모델의 pointmap을 geometry prior로 넣는다.
3. 깊이 prior의 log-depth scale과 shift를 조절해 장면의 관측과 맞춘다.
4. CUDA 기반 implicit Schur 방식으로 pose·geometry 변수를 최적화한다.

Matcher 학습과 추론 시 최적화가 모두 있다. 따라서 전체 방법을 한 번의 feed-forward 추론이라고 부를 수 없다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.05210v1), Table 2, PDF p.8.

ETH3D SLAM의 8개 시퀀스 subset에서 Sim(3) 정렬한 평균 ATE(cm). ETH3D MVS의 mAA와 다른 실험이다.

| Method       | Mean ATE (cm) ↓ |
| ------------ | --------------- |
| Spann3R      | 16.8            |
| MUSt3R (224) | 10.0            |
| MUSt3R (512) | 4.2             |
| VIPE         | 1.8             |
| BLASt3R      | 1.2             |

이 평균의 해상도와 시퀀스 subset을 함께 보존해야 한다. MVS 성능이나 임의 길이 영상의 처리속도와 직접 비교할 수 없다.

## 💡 Insights & Impact

Pointmap을 고정된 정답으로 취급하지 않고 matching 관측에 맞춰 변형할 수 있는 prior로 쓴다.

- 전용 matcher의 학습과 BA 계산이 필요하다.
- 메모리와 대응점 품질에 영향을 받으며, 8개 subset의 평균을 전체 SLAM benchmark로 일반화하면 안 된다.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): pointmap prior의 배경.
- [MUSt3R](must3r.md): 다중 시점 예측과 비교 대상.

## 📚 Key Takeaways

1. 대응점과 geometry prior를 BA에서 결합한다.
2. 온라인과 순서 없는 재구성을 모두 다루지만 최적화는 남는다.
3. SLAM ATE와 MVS 지표를 구분한다.

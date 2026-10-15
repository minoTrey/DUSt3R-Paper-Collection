# GRF-Recon: Global Ray-Field Optimization for Long-Sequence Feed-forward Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Enpeng Li, Yunzhou Zhang, Zhiyao Zhang, Dexuan Lyu, Chenyu Wang, Chiyuan Cui, Cheng Cheng
- **Institution**: Northeastern University, China
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.20012)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.20012v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: DA3에 단안 geometry prior를 증류하고, chunk의 pose뿐 아니라 ray와 depth의 일관성을 전역 최적화한다.

## 🎯 Key Contributions

1. MoGe teacher의 geometry를 LoRA로 주입한다.
2. Ray·gradient·photometric 신호를 함께 써 sparse 대응점을 만든다.
3. Chunk 안팎의 geometry 제약을 trajectory stitching과 함께 최적화한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 긴 단안 RGB 영상; camera intrinsics를 미리 주지 않는 구성.
- **Output**: 긴 카메라 궤적과 정렬된 point cloud.
- **Problem**: Chunk pose만 맞추면 각 chunk 내부의 geometry 오류와 ray 불일치가 남는다.

### Method

1. MoGe 단안 teacher를 사용해 DA3를 LoRA로 보정한다.
2. 예측 pose·depth로 대응 후보의 검색 범위를 제한한다.
3. Ray distance, gradient similarity, patch photometric error로 matching하고 양방향 검증한다.
4. DINOv2 descriptor로 keyframe·loop를 고른 뒤 ray 제약과 pose를 함께 최적화한다.

LoRA adaptation은 학습 단계이며 ray-field·graph refinement는 추론 단계의 최적화다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.20012v1), Table 2, PDF p.10.

KITTI monocular, Sim(3) 정렬 ATE RMSE(m). 평균에서 고속 sequence 01을 제외한다. 아래 행은 모두 uncalibrated 조건이다.

| Method        | Mean ATE excluding seq.01 (m) ↓ |
| ------------- | ------------------------------- |
| VGGT-Long     | 19.78                           |
| Pi-Long       | 19.01                           |
| DA3-Streaming | 12.72                           |
| GRF-Recon     | 7.18                            |

제외한 sequence 01의 GRF-Recon ATE는 76.52m다. 평균 7.18m만으로 모든 KITTI sequence에서 낮은 오차라고 해석하면 안 된다.

## 💡 Insights & Impact

학습 prior를 개선하는 단계와 여러 view의 물리적 일관성을 강제하는 단계를 함께 사용한다.

- Teacher 오류가 증류될 수 있다.
- Loop·matching·global optimization에 의존하며 평균에서 제외한 어려운 sequence가 있다.

## 🔗 Related Work

- [Depth Anything 3](depth-anything-3.md): 보정하는 backbone.
- [VGGT](vggt.md): long-sequence 비교 계열.

## 📚 Key Takeaways

1. DA3의 prior 개선과 ray 최적화는 다른 단계다.
2. Pose뿐 아니라 geometry를 함께 묶는다.
3. KITTI 평균의 sequence 제외 조건을 보존한다.

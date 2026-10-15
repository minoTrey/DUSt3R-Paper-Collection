# Feed-Forward Multi-view Multi-person Reconstruction with Contrastive Human-Aware 3D Representation (arXiv 2026)

## 📋 Overview

- **Authors**: Yuanwang Yang, Buzhen Huang, Zongxuan Ren, Jing Huang, Kun Li
- **Institution**: Tianjin University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.00745)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.00745v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT로 초기화한 공통 3D feature 공간에 여러 사람의 관측을 모으고 instance contrastive learning으로 camera·association·SMPL을 함께 예측한다.

## 🎯 Key Contributions

1. Human-aware view-agnostic 3D representation을 유지한다.
2. 같은 사람의 cross-view·cross-modal feature를 contrastive하게 정렬한다.
3. Camera와 여러 사람의 articulated shape를 공동 추정한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Calibration이 없는 여러 RGB view.
- **Output**: Camera parameter, 사람별 SMPL body·pose와 공통 scene 배치.
- **Problem**: 가려진 사람이 많으면 2D에서 cross-view matching과 사람 ID를 연결하기 어렵다.

### Method

1. VGGT의 depth·camera·feature·confidence로 pixel을 3D로 옮긴다.
2. 공간 이웃을 confidence-weighted soft aggregation으로 융합한다.
3. 동일 사람의 geometry·appearance·semantic feature를 가까이, 다른 사람은 멀리 학습한다.
4. Human-aware 3D feature에서 camera와 body parameter를 feed-forward로 회귀한다.

Human instance·body·camera supervision을 사용하는 학습 방법이다. 3D 표현 초기화의 사전학습 prior와 추가 contrastive 학습을 구분한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.00745v1), Table 1, PDF p.16.

OcMotion human reconstruction, MPJPE 계열 단위 m. CA는 camera-aligned, PA는 사람별 Procrustes-aligned error이며 서로 다른 성질을 측정한다.

| Method   | CA-MPJPE (m) ↓ | PA-MPJPE (m) ↓ |
| -------- | -------------- | -------------- |
| HSfM     | 0.35           | 0.05           |
| Proposed | 0.19           | 0.04           |

OcMotion 표는 심한 물체 가림을 포함한 single-person 조건이다. Multi-person 공간 관계는 별도 EgoHumans 표와 group alignment를 보아야 한다. 원문 일부 alignment 설명의 명칭이 혼동되므로 정렬 대상도 함께 적었다.

## 💡 Insights & Impact

카메라·사람 matching을 순차 해결하는 대신 공통 3D 공간의 instance feature로 함께 추정한다.

- 초기 depth·camera와 사람 body prior의 오류가 전파될 수 있다.
- 정렬 후 관절 오차만으로 절대 사람 배치 정확성을 판단할 수 없다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 3D feature 초기화.
- [Human3R](human3r.md): 사람 중심 reconstruction 비교 맥락.

## 📚 Key Takeaways

1. 영상 관측을 사람별 공통 3D 공간에 모은다.
2. Contrastive learning이 cross-view identity를 돕는다.
3. Person·group·camera alignment를 구분한다.

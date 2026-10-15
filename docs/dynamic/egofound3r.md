# EgoFound3R: End-to-End Egocentric Hand Reconstruction in World Space with Point-Wise Interaction Attributes (arXiv 2026)

## 📋 Overview

- **Authors**: Hongming Fu, Jingcheng Shi, Wenjia Wang, Binhua Zuo, Bo Zhao
- **Institution**: Shanghai Jiao Tong University, QuicRobot, Rutgers University, University of Hong Kong
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.01210)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.01210v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Frozen VGGT-Ω에 손의 root·joint·surface query를 넣어 scene과 같은 metric frame의 손 geometry·visibility·contact·distance를 함께 예측한다.

## 🎯 Key Contributions

1. 구조화한 hand prompt로 scene geometry prior를 재사용한다.
2. 명시적인 hand point와 interaction attribute를 함께 decode한다.
3. 손과 scene의 update rate를 분리해 계산량을 조절한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Egocentric RGB video.
- **Output**: World-space hand geometry와 point별 visibility·contact·surface distance, camera·scene scale.
- **Problem**: 손 crop만으로는 occlusion·camera motion을 해결하기 어렵고 여러 모델을 연결하면 scale과 처리량이 불안정하다.

### Method

1. VGGT-Ω의 shared DINOv3 feature에서 hand prompt를 만든다.
2. Bidirectional temporal transformer로 양손 정보를 교환한다.
3. 빠른 hand observation을 느린 scene anchor에 pooling해 전달한다.
4. Hand decoder·scene head·metric head로 공통 world frame의 출력을 얻는다.

Backbone을 고정하고 prompt·adapter·prediction head를 학습한다. Camera GT를 쓰는 †·‡ 행은 default와 구분한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.01210v2), Table 2, PDF p.7.

TACO joint-level contact prediction. 원문은 geometry-based baseline이 GT geometry를 받으며 contact convention도 다르다고 명시한다.

| Method     | Precision ↑ | Recall ↑ | F1 ↑  |
| ---------- | ----------- | -------- | ----- |
| ContactOpt | 0.557       | 0.197    | 0.259 |
| EgoFound3R | 0.654       | 0.777    | 0.697 |

Contact 성능이 world placement 정확성을 직접 뜻하지 않는다. HOI4D world-space MPJPE는 큰 오차가 남으므로 camera-frame·aligned 결과와 섞지 않는다.

## 💡 Insights & Impact

손의 local geometry를 scene 문맥 안에서 읽고 interaction label도 같은 point에 연결한다.

- Metric scale·camera 추정 오류가 world-space 손에 전파된다.
- Multi-rate interpolation과 contact 정의가 결과에 영향을 준다.

## 🔗 Related Work

- [VGGT-Ω](../reconstruction/vggt-omega.md): frozen backbone.
- [WildHSR](wildhsr.md): 사람 전체의 metric scene reconstruction.

## 📚 Key Takeaways

1. Geometry와 interaction attribute를 함께 출력한다.
2. 손·scene을 다른 rate로 계산한다.
3. Contact와 world placement를 별도로 평가한다.

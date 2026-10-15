# RIGOR: Rig-Informed Geometry for Omnidirectional Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Tingjun Huang, Dmitry Rudshin, Mathieu Meyer, Pietro Bonazzi, Marc Pollefeys, Emilia Szymańska
- **Institution**: ETH Zürich, Hilti AG
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.13504)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.13504v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 중력 정렬 panorama를 알려진 virtual rig의 perspective view로 나누고 frozen DA3 예측을 rig 제약·loop graph로 보정한다.

## 🎯 Key Contributions

1. Panorama 전용 재학습 없이 DA3를 사용한다.
2. Known co-centered view rotation으로 지역 예측을 repair한다.
3. Cyclic retrieval·joint geometric verification으로 loop를 검증한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Gravity-aligned panorama sequence와 알려진 virtual-view rotation, dynamic/device mask.
- **Output**: 긴 camera trajectory와 fused dense point cloud.
- **Problem**: 반복 구조·약한 texture의 긴 construction-site 영상에서 지역 geometry와 global drift가 불일치한다.

### Method

1. Panorama를 같은 optical center의 여러 perspective view로 렌더링한다.
2. Frozen DA3를 overlapping block에 적용한다.
3. Virtual-rig consistency를 검사하고 수락한 pose·pointmap correction을 적용한다.
4. Capture-level retrieval·검증한 loop를 Sim(3) graph에서 최적화하고 owner-point fusion한다.

Panorama-specific learned training은 없지만 gravity alignment·known virtual rig와 graph 최적화가 필요하다. Co-centered rig는 stereo parallax나 metric scale을 직접 주지 않는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.13504v2), Table 2, PDF p.7.

Hilti–Trimble–Oxford: trajectory 30개, LiDAR geometry 29개 median. ATE는 SE(3) 정렬, ROI geometry는 GT-assisted Sim(3)+scale-adjusting ICP 평가다.

| Method     | ATE (m) ↓ | ROI CD (m) ↓ | F@25cm ↑ |
| ---------- | --------- | ------------ | -------- |
| DA3-Legacy | 2.704     | 0.155        | 0.833    |
| RIGOR      | 2.312     | 0.132        | 0.873    |

Cloud alignment는 reconstructed shape를 평가하며 metric scale·absolute map placement를 검증하지 않는다. 모든 run에서 ATE가 좋아진 것은 아니다.

## 💡 Insights & Impact

알려진 capture 구조를 모델 재학습 대신 prediction repair와 loop 검증에 활용한다.

- Gravity leveling·virtual rig 가정이 어긋나면 correction이 불안정하다.
- 어려운 일부 baseline은 정량 비교 대신 정성 보고되어 선택 범위를 고려해야 한다.

## 🔗 Related Work

- [Depth Anything 3](depth-anything-3.md): frozen predictor.
- [MEOW](meow.md): camera adaptation을 학습하는 다른 접근.

## 📚 Key Takeaways

1. 가상 rig의 상대 회전은 알지만 baseline은 없다.
2. 지역 repair와 전역 loop 최적화를 결합한다.
3. Trajectory와 cloud의 정렬 protocol이 다르다.

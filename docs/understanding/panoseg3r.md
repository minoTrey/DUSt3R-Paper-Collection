# PanoSeg3R: Feed-Forward 3D Semantic Segmentation for Panoramic Images with an Automatic Data Curation Pipeline (arXiv 2026)

## 📋 Overview

- **Authors**: Heechan Yoon, Dongki Jung, Phuc Nguyen, Ming Lin, Dinesh Manocha
- **Institution**: University of Maryland, College Park
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.22687)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.22687v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Wid3R의 panoramic ray geometry에 semantic query decoder와 low-level ERP feature를 더하고 자동 생성한 panorama label로 학습한다.

## 🎯 Key Contributions

1. Perspective cubemap 변환 없이 panorama를 공동 처리한다.
2. 공유 semantic query와 text embedding으로 mask·class를 예측한다.
3. Foundation-model pipeline으로 pseudo semantic annotation을 확장한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 서로 겹치는 multi-view equirectangular RGB panorama.
- **Output**: Geometry와 view-consistent semantic mask·3D semantic point cloud.
- **Problem**: Perspective model을 panorama 조각에 적용하면 경계와 넓은 시야의 semantic·geometry consistency가 깨질 수 있다.

### Method

1. Wid3R로 ray·radial distance·multi-view feature를 추출한다.
2. 공유 query decoder가 scene semantic instance를 정제한다.
3. Circular-padding image stem을 DPT feature에 넣어 ERP 세부 정보를 보완한다.
4. SigLIP class embedding으로 mask를 분류하고 geometry에 semantic을 투영한다.

공식 semantic GT와 자동 pseudo-label을 함께 쓴다. Pseudo-label의 VLM 검증이 수동 GT와 동일한 보장은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.22687v1), Table 2, PDF p.5.

ScanNet++ scene-level 3D semantic segmentation. Perspective baseline은 panorama를 여섯 cubemap face로 바꿔 평가한다.

| Method           | 3D mIoU ↑ | 3D mAcc ↑ |
| ---------------- | --------- | --------- |
| PanSt3R, cubemap | 9.26      | 12.12     |
| PanoSeg3R        | 17.28     | 22.56     |

2D segmentation에서는 모든 panorama-specific model보다 높지 않다. 3D 평가는 point cloud 정렬 protocol을 포함하므로 absolute placement 평가와 다르다.

## 💡 Insights & Impact

Panoramic geometry에 맞는 feature와 supervision을 semantic prediction까지 유지한다.

- Pseudo-label의 class 혼동과 ERP distortion이 남는다.
- 주로 실내 panorama benchmark이며 야외·다른 camera model 전이는 별도 문제다.

## 🔗 Related Work

- [IGGT](iggt.md): perspective instance geometry 비교.
- [MEOW](../reconstruction/meow.md): 혼합 camera geometry와 다른 semantic task.

## 📚 Key Takeaways

1. 실제 backbone은 Wid3R다.
2. ERP 세부 feature와 query mask를 결합한다.
3. Pseudo-label 학습과 GT 평가를 구분한다.

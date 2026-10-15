# NemoSplat: Feed-Forward 4D Gaussian Splatting for Media-Aware Underwater Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Xiaopeng Guo, Wai Chung Tse, Yipeng Zhu, Hanwen Zhang, Huajian Huang, Sai-Kit Yeung
- **Institution**: Hong Kong University of Science and Technology, Beijing Institute of Technology
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.22888)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.22888v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 수중 영상에서 camera·depth·동적 mask·물의 광학 parameter와 4D Gaussian을 함께 예측해 정적 배경과 움직이는 물체를 분리한다.

## 🎯 Key Contributions

1. Geometry estimator와 promptable dynamic disentangler를 결합한다.
2. 정적 Gaussian과 frame별 동적 Gaussian을 구분한다.
3. Attenuation·backscatter를 명시한 rendering으로 학습한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Calibration 없는 수중 RGB sequence와 선택적 text prompt.
- **Output**: Camera·depth·dynamic mask·medium parameter, 정적/동적 Gaussian과 clean rendering.
- **Problem**: 움직이는 해양 생물과 산란을 구분하지 않으면 geometry와 appearance가 서로 잘못 설명된다.

### Method

1. Visual geometry transformer가 spatiotemporal feature를 추출한다.
2. Dynamic semantic mask를 예측하고 필요하면 text prompt로 정교화한다.
3. Mask로 전체 primitive를 global static set과 frame별 dynamic set으로 나눈다.
4. 예측 depth와 medium parameter로 clean radiance를 수중 관측과 연결한다.

Dynamic disentangler를 먼저 학습한 뒤 frozen visual backbone에 LoRA를 사용해 geometry·media-aware rendering을 학습한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.22888v2), Table 1, PDF p.6.

BoulderShore·Coral·Deepsea의 synthetic sequence 평균. ATE는 m이며 낮을수록, PSNR은 높을수록 좋다.

| Method    | ATE (m) ↓ | PSNR ↑ | SSIM ↑ |
| --------- | --------- | ------ | ------ |
| Droid-W   | 1.85      | 23.51  | 0.71   |
| AnySplat  | 2.97      | 21.76  | 0.50   |
| NemoSplat | 1.88      | 23.98  | 0.56   |

NemoSplat은 이 평균에서 Droid-W보다 ATE·SSIM이 좋지 않다. Deepsea의 낮은 visibility에서 flow 기반 SLAM이 더 안정적인 경우도 원문이 설명한다.

## 💡 Insights & Impact

수중 reconstruction의 동적 분리와 optical restoration을 하나의 representation에 결합한다.

- Dynamic mask·물리 model이 틀리면 정적 scene에 artifact가 남는다.
- Synthetic GT와 실제 수중 영상 결과의 검증 강도는 다르다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): geometry transformer 배경.
- [Swimm3R](swimm3r.md): medium-aware geometry와 splatting 비교 맥락.

## 📚 Key Takeaways

1. 수중 medium과 실제 motion을 분리한다.
2. 정적·동적 primitive의 역할이 다르다.
3. Rendering 개선과 pose 개선을 따로 판단한다.

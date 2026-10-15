# WAT3R: Feedforward Underwater 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Jiayi Xu, Jiahao Lu, Ziqiang Zheng, Yihao Tan, Yaolong Zhu, Yuan Liu, Sai-Kit Yeung
- **Institution**: Hong Kong University of Science and Technology, Chinese University of Hong Kong, Peking University
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.21023)
- **Verification**: UNKNOWN (2026-10-15; 원문 2607.21023v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 수중 영상의 감쇠·산란을 geometry와 함께 모델링하고 복원된 clean view의 일관성으로 pose를 적응시키는 feed-forward 재구성이다.

## 🎯 Key Contributions

1. π3 계열 geometry branch에 degradation adaptation을 연결한다.
2. 물리적인 수중 영상 생성으로 supervised adaptation 데이터를 만든다.
3. 실제 영상에서는 clean-view warping으로 pose를 보정한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 수중 RGB 이미지 여러 장 또는 영상.
- **Output**: Pixel-aligned pointmap, camera pose, depth, clean image와 물의 광학 parameter.
- **Problem**: 색 감쇠와 backscatter가 view 간 feature 일관성을 깨뜨려 육상 geometry model이 실패한다.

### Method

1. Geometry branch와 clean-image·water-parameter head가 feature를 공유한다.
2. GT geometry가 있는 영상에 물리 효과를 합성하여 point·camera·radiometric supervision을 준다.
3. 실제 수중 sequence에서 예측 depth·pose로 clean image를 warp한다.
4. Occlusion·동적 영역을 masking하며 clean-view photometric consistency로 camera prediction을 적응시킨다.

합성 supervised 적응 뒤 실제 데이터의 self-supervised 적응을 수행한다. 수중 광학식은 완벽한 hard constraint가 아니라 soft regularization이다. 기존 Wat3R(2607.08772)와 다른 저자의 별개 논문이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2607.21023v1), Table 1, PDF p.7.

FLSea-Canyons multi-view depth, scale-only alignment. δ는 GT 대비 비율 오차가 threshold 안인 pixel 비율이다.

| Method | AbsRel ↓ | δ < 1.25 ↑ |
| ------ | -------- | ---------- |
| π3     | 0.0891   | 0.9613     |
| DA3    | 0.0943   | 0.9345     |
| WAT3R  | 0.0725   | 0.9726     |

SQUID의 scale-and-shift 조건에서는 모든 metric이 최고는 아니다. USOD10K의 depth reference는 센서 GT가 아니라 DPT pseudo-depth다.

## 💡 Insights & Impact

색 복원을 별도 전처리로만 취급하지 않고 geometry 적응의 supervision으로 연결한다.

- 단순화한 water model이 실제 산란을 모두 설명하지 못한다.
- Pseudo-depth 결과를 물리적인 depth 정확성 검증으로 해석하면 안 된다.

## 🔗 Related Work

- [π3](pi3.md): geometry branch의 기반.
- [Swimm3R](../gaussian-splatting/swimm3r.md): SfM·splatting까지 연결하는 다른 수중 방법.

## 📚 Key Takeaways

1. 동명 Wat3R와 arXiv ID로 구분한다.
2. Clean-view 일관성이 pose 적응을 돕는다.
3. Alignment와 reference depth의 출처를 보존한다.

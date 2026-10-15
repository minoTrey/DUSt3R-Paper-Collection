# AESplat: Advancing Pose-Free Feed-Forward 3D Gaussian Splatting via Decoupled Appearance Modeling (arXiv 2026)

## 📋 Overview

- **Authors**: Shiwei Ren, Zhiang Liu, Yongchun Fang, Hongwei Chen
- **Institution**: Nankai University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.36693)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.36693v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Gaussian의 기본 색은 관측 RGB에서 직접 얻고, 시점 의존 색만 예측 camera의 3D 관계와 cross-view color를 읽는 head로 학습한다.

## 🎯 Key Contributions

1. SH zeroth-order와 higher-order를 분리한다.
2. 직접 RGB-to-SH 변환으로 base color를 만든다.
3. Gaussian-to-view 관계와 warped color로 view-dependent appearance를 안내한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 두 unposed RGB context images.
- **Output**: Camera·pixel-aligned Gaussian scene과 novel view.
- **Problem**: View-independent·dependent appearance를 같은 head로 예측하면 관측 색을 다시 학습하고 시점 변화 단서를 충분히 쓰지 못한다.

### Method

1. Pose-free backbone이 camera·depth·Gaussian geometry를 예측한다.
2. 각 context pixel RGB를 zeroth-order SH coefficient로 직접 변환한다.
3. 예측 Gaussian과 camera 사이 방향·log-distance를 embedding한다.
4. Cross-view color와 함께 shallow MLP에 넣어 higher-order SH를 예측한다.

Base color 변환만 training-free이며 geometry·higher-order appearance와 나머지 network는 학습한다. NAS3R setup의 두 context·한 target을 사용한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.36693v1), Table 1, PDF p.7.

RealEstate10K test-scene 평균 NVS, 224×224 two-view setting. 아래는 self-supervised pose-free 행이다.

| Method  | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------- | ------ | ------ | ------- |
| NAS3R   | 25.888 | 0.861  | 0.136   |
| AESplat | 26.691 | 0.872  | 0.128   |

Pose-required baseline과 다른 camera 정보 조건이다. 관측 RGB의 specular·exposure 성분도 base color에 들어갈 수 있다.

## 💡 Insights & Impact

이미 관측한 색과 추론해야 할 view-dependent variation에 서로 다른 경로를 준다.

- 예측 camera 오차가 relation embedding·color warp에 영향을 준다.
- 두 view·제한된 resolution의 결과를 임의 dense scene으로 확대하면 안 된다.

## 🔗 Related Work

- [YoNoSplat](yonosplat.md): pose-free Gaussian 배경.
- [2Xplat](2xplat.md): geometry·appearance expert 분리와는 다른 SH 분리.

## 📚 Key Takeaways

1. SH 차수별 appearance 역할을 구분한다.
2. 일부 변환만 training-free다.
3. 입력 pose 조건과 rendering protocol을 함께 읽는다.

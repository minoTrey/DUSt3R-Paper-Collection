# DensiTok: Making Feed-Forward 3D Gaussian Splatting See More Views Than It Is Given (arXiv 2026)

## 📋 Overview

- **Authors**: Minhyeok Lee, Jungho Lee, Minseok Kang, Heeseung Choi, Ig-Jae Kim, Sangyoun Lee
- **Institution**: Yonsei University, NAVER AI Lab, Korea Institute of Science and Technology (KIST)
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.07958)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.07958v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Sparse 이미지에서 빠진 view의 geometry token을 latent flow로 보완하고 기존 Gaussian head가 더 풍부한 representation을 읽도록 한다.

## 🎯 Key Contributions

1. 이미지 생성·재인코딩 대신 내부 geometry token을 보완한다.
2. Token VAE와 camera-conditioned latent completion을 학습한다.
3. 기존 encoder를 고정하며 sparse-view의 geometry·rendering을 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 적은 수의 unposed RGB 이미지와 backbone이 추정한 camera.
- **Output**: 보완된 geometry token, 이를 해독한 Gaussian scene·camera·depth.
- **Problem**: 입력에 보이지 않은 영역은 encoder token에 근거가 없어 sparse-view Gaussian이 구멍·floaters를 만든다.

### Method

1. Geometry token을 VAE latent로 압축한다.
2. 관측 camera 사이를 interpolation하여 virtual-view camera를 정한다.
3. Camera-conditioned flow가 미관측 view latent를 보완한다.
4. 한 단계 sampling으로 fine-tuning한 뒤 decoder가 복원한 token을 기존 reconstruction head로 전달한다.

VAE·flow completion을 학습한다. Encoder는 고정하지만 원문 Appendix의 구성에 따라 Gaussian head의 최소 fine-tuning을 허용하므로 모든 설정의 head가 항상 frozen이라고 단정하지 않는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.07958v1), Table 1, PDF p.7.

RealEstate10K, AnySplat backbone의 sparse input 3 views. Runtime은 표의 전체 inference 초 단위다. Dense reference는 16 views로 다른 입력이다.

| Model               | PSNR ↑ | LPIPS ↓ | Runtime (s) ↓ |
| ------------------- | ------ | ------- | ------------- |
| AnySplat, 3 views   | 22.47  | 0.215   | 0.117         |
| + DensiTok, 3 views | 24.28  | 0.184   | 0.267         |
| AnySplat, 16 views  | 24.04  | 0.189   | 0.434         |

추가 token completion은 같은 sparse baseline보다 계산이 늘어난다. 보완된 virtual view는 실제 새 관측이 아니며 dense reference와 입력 정보량이 다르다.

## 💡 Insights & Impact

새 pixel을 생성하는 대신 frozen decoder가 이해할 수 있는 latent evidence를 생성한다.

- 보이지 않은 내용은 hallucination 가능성이 남는다.
- Camera interpolation은 관측 경로 안의 virtual view에 한정되며 임의 extrapolation 결과가 아니다.

## 🔗 Related Work

- AnySplat: 원문 Table 1에서 평가한 적용 backbone.
- [VGGT](../reconstruction/vggt.md): geometry token과 multi-head 예측 배경.

## 📚 Key Takeaways

1. 생성 대상은 이미지가 아니라 geometry latent다.
2. 추가 실제 관측 없이 token을 보완한다.
3. 품질·추가 시간·head 학습 설정을 함께 본다.

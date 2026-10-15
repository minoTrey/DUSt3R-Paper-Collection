# Many Eyes, One World: Feed-Forward 3D Reconstruction from Mixed Cameras (arXiv 2026)

## 📋 Overview

- **Authors**: Qiaoge Li, Yifan Zhan, Haijun Yang, Haiyang Liu, Yiyi Cai, Chenchi Luo
- **Institution**: China Mobile Research Institute, University of Tokyo
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.35658)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.35658v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Perspective·fisheye·panorama가 섞인 이미지를 camera-type label 없이 함께 처리하도록 MapAnything을 합성 데이터로 적응시킨다.

## 🎯 Key Contributions

1. 여러 projection을 섞은 LENSCOPE 학습 tuple을 생성한다.
2. 전체 시야를 보존하는 resize와 aspect-ratio embedding을 사용한다.
3. 혼합 camera의 pose·metric pointmap과 laser benchmark를 제공한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 여러 종류 camera의 RGB 이미지 tuple. Calibration·distortion·camera-type label·pose는 주지 않는다.
- **Output**: 공통 좌표계의 camera pose와 metric pointmap.
- **Problem**: Perspective 중심 학습과 cropping은 full panorama·혼합 projection의 관측을 손상시킨다.

### Method

1. Procedural 실내 scene에서 정확한 ray·depth·pose를 렌더링한다.
2. Camera를 다시 샘플링한 뒤 covisibility graph가 연결된 tuple을 선택한다.
3. Cropping 없이 공통 tensor 크기로 바꾸고 원래 aspect ratio를 embedding으로 전달한다.
4. Panorama 경계의 circular padding, solid-angle weighting과 ray likelihood로 MapAnything을 적응시킨다.

Perspective-pretrained MapAnything에서 시작하며 이후 adaptation은 synthetic tuple만 쓴다. 전체 학습이 synthetic-only라는 뜻은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.35658v1), Table 2, PDF p.8.

Stanford 2D3DS 88개 heterogeneous tuple(3–24 views). Pose metric은 tuple별 계산 후 평균이며 ATE는 Sim(3) 정렬이다.

| Method      | Camera label input | mAA@30 ↑ | ATE ↓ |
| ----------- | ------------------ | -------- | ----- |
| MapAnything | None               | 16.4     | 1.48  |
| MEOW        | None               | 80.4     | 0.62  |
| Wid3R       | Class per view     | 54.3     | 0.83  |

Tuple 평균과 모든 pair를 pooled한 평균은 다르다. 원문은 많은 view의 tuple에서는 Wid3R보다 낮으며 metric scale도 GT보다 짧게 추정하는 한계를 명시한다.

## 💡 Insights & Impact

새 backbone보다 데이터의 projection 다양성·overlap 검증·입력 처리로 혼합 camera를 다룬다.

- 적응 학습은 실내·짧은 tuple 중심이며 긴 sequence에 취약하다.
- Sim(3) 정렬 성능은 metric scale 정확도를 검증하지 않는다.

## 🔗 Related Work

- [VGGT](vggt.md): perspective geometry 비교 모델.
- [DUSt3R](../foundation/dust3r.md): pointmap 예측의 배경.

## 📚 Key Takeaways

1. Camera 종류 label 없이 혼합 관측을 처리한다.
2. 합성 데이터로 적응하지만 pretrained model을 사용한다.
3. Pose 정렬 점수와 metric scale을 구분한다.

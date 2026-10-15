# Topometric Autonomous Vehicle Localization by Combining Visual Embeddings and Feed-Forward 3D Models (arXiv 2026)

## 📋 Overview

- **Authors**: Eulogio Quemada-Torres, Alberto Jaenal, Francisco-Angel Moreno, Javier Gonzalez-Jimenez
- **Institution**: University of Malaga, University of Zaragoza
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.06021)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.06021v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 장소 검색의 확률 belief로 reference를 고르고 DA3의 지역 pose 추정을 particle filter에 결합해 appearance 변화 속의 planar localization을 수행한다.

## 🎯 Key Contributions

1. Descriptor cluster와 metric pose를 결합한 topometric map을 만든다.
2. Sequential belief로 FF3D reference를 선택한다.
3. Appearance·geometry likelihood를 log-space에서 융합한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Georeferenced map image·pose, query RGB sequence와 odometry.
- **Output**: Map 좌표의 SE(2) 위치·yaw와 장소 belief.
- **Problem**: VPR은 compact하지만 metric 위치가 거칠고 단일 retrieval의 aliasing이 큰 pose 오류로 이어진다.

### Method

1. Offline descriptor를 clustering하고 diverse reference image를 남긴다.
2. Odometry로 particle을 전파하고 appearance likelihood를 계산한다.
3. Belief에 맞는 reference들과 query에 DA3를 적용해 metric pose를 추정한다.
4. 정규화한 log-likelihood를 합쳐 particle weight·pose를 갱신한다.

기본 descriptor는 MixVPR, geometry는 DA3-Large다. 기존 georeferenced map과 odometry를 쓰는 localization 시스템이며 RGB-only map 생성 모델은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.06021v1), Table 2, PDF p.9.

4Seasons의 동일 map·query·post-initialization frame. Particle 방법은 seed별 run을 평균한다. AUC는 position·yaw tolerance를 함께 줄여 적분한 값이다.

| Method              | Mean position (m) ↓ | Median position (m) ↓ | AUC ↑ |
| ------------------- | ------------------- | --------------------- | ----- |
| VPR + FF3D          | 1.404               | 0.144                 | 0.897 |
| Topometric proposal | 0.268               | 0.173                 | 0.864 |

큰 오차를 줄여 평균은 낮지만 median·AUC는 direct baseline보다 나쁘다. Map size는 model checkpoint를 제외한 online 파일 크기다.

## 💡 Insights & Impact

Sequential uncertainty가 잘못 고른 reference의 큰 오류를 줄이는 반면 순간적인 정밀도와 trade-off가 있다.

- Georeferenced map·odometry와 planar pose 가정이 필요하다.
- 모든 지표에서 우수하지 않으며 dataset별 tolerance가 다르다.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): 지역 metric pose 추정에 사용.
- [Reloc3r](reloc3r.md): 다른 feed-forward localization 접근.

## 📚 Key Takeaways

1. 검색과 metric geometry를 확률 filter에서 연결한다.
2. 평균·median·tail을 함께 본다.
3. 지도와 odometry 입력을 명시한다.

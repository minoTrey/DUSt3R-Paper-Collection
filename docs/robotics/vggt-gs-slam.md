# VGGT-GS SLAM: Uncalibrated Monocular Gaussian Splatting SLAM with Feed-Forward Priors (arXiv 2026)

## 📋 Overview

- **Authors**: Yuhang Han, Hao Wang, Jiaxi Cao, Xingyu Liu
- **Institution**: National University of Singapore
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.19628)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.19628v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT pose·depth prior를 Gaussian submap으로 초기화하고 camera calibration과 distortion까지 rendering 기반 BA로 함께 보정한다.

## 🎯 Key Contributions

1. Pose·Gaussian·공유 intrinsics·distortion을 공동 최적화한다.
2. Gaussian covariance를 활용해 인접 submap scale을 조정한다.
3. Loop candidate는 Gaussian matching으로 검증한 뒤 전역 graph에 넣는다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Calibration이 주어지지 않는 단안 RGB 영상. 센서 depth는 사용하지 않는다.
- **Output**: 카메라 궤적, camera calibration, Gaussian submap과 novel-view rendering.
- **Problem**: 부정확한 calibration을 고정하면 오차가 geometry로 흡수되고 submap별 scale이 달라진다.

### Method

1. VGGT로 window의 camera·depth·confidence를 예측한다.
2. Depth에서 Gaussian을 초기화하고 submap-shared intrinsics를 추정한다.
3. Analytic calibration Jacobian을 사용해 radial–tangential distortion과 pose·Gaussian을 joint BA한다.
4. Gaussian-native matching으로 scale을 정렬하고 loop를 검증한 뒤 Sim(3) graph를 최적화한다.

기존 geometry prior와 per-scene 최적화를 결합한다. Non-keyframe pose도 고정된 local map에서 최적화하므로 keyframe 처리 시간만으로 전체 속도를 주장하면 안 된다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.19628v1), Tables I–II, PDF p.5.

Uncalibrated RGB-only 평균 ATE RMSE(m). TUM은 지정한 9개 sequence, 7-Scenes는 sequence 01 구성이다.

| Dataset              | VGGT-SLAM 2.0 | VGGT-GS SLAM |
| -------------------- | ------------- | ------------ |
| TUM RGB-D            | 0.041         | 0.030        |
| 7-Scenes sequence 01 | 0.067         | 0.055        |

RGB-D는 dataset 이름이며 depth 입력을 뜻하지 않는다. 일부 baseline은 원문 보고값이고 다른 행은 재실행이므로 단일 hardware의 순수 비교로 간주하면 안 된다.

## 💡 Insights & Impact

Feed-forward prior는 초기값이며 photometric evidence가 camera와 지도 양쪽을 수정한다.

- BA와 Gaussian refinement 비용이 있으며 최적화 없는 시스템이 아니다.
- 정적 장면과 충분한 photometric 관측을 가정하며 calibration의 관측 가능성은 camera motion에 영향을 받는다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 초기 geometry prior.
- [VGGT-SLAM](../reconstruction/vggt-slam.md): submap 구조의 배경.

## 📚 Key Takeaways

1. RGB-only 입력으로 depth prior를 예측한다.
2. Calibration과 geometry를 함께 보정한다.
3. Loop 검증과 loop transform 교체는 다르다.

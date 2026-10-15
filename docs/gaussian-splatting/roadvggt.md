# RoadVGGT: Road-Structure-Aware Feed-Forward Road Surface Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Han Jiao, Chen Liu, Jiakai Sun, Zhanjie Zhang, Mengyuan Yang, Yimeng Li, Mofan Zhou, Kun Zhan, Lei Zhao
- **Institution**: Zhejiang University, Li Auto Inc.
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.23758)
- **Verification**: UNKNOWN (2026-10-15; 원문 2607.23758v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 제공된 pose·depth와 도로 semantic mask를 이용해 Gaussian을 예측하고 도로 평면 grid에서 구조를 보존하며 융합한다.

## 🎯 Key Contributions

1. OmniVGGT의 geometry prior에 road Gaussian head를 학습한다.
2. World road-plane 좌표에서 dense prediction을 압축한다.
3. 도로·인도 경계와 가는 구조를 구분해 fusion한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 다중 도로 RGB 영상, 제공된 camera pose·depth 관측, 외부 semantic segmentation map.
- **Output**: Compact Gaussian road surface와 BEV RGB·semantic·elevation map.
- **Problem**: Pixel별 Gaussian은 길고 넓은 도로에서 중복이 많으며 일반 voxel fusion은 경계·차선 구조를 손상한다.

### Method

1. Frozen OmniVGGT에 관측 pose·depth와 이미지를 넣는다.
2. 학습 Gaussian head가 pixel별 attribute를 예측한다.
3. Umeyama alignment로 metric road-plane 좌표에 옮긴다.
4. Semantic label·높이·fine structure에 따라 cell 내부 group을 나눈 뒤 Gaussian을 융합한다.

Waymo에서 새 Gaussian head만 학습하고 nuScenes에는 zero-shot 적용한다. Semantic label은 Gaussian head가 예측하는 값이 아니라 외부 Mask2Former 결과에서 상속한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2607.23758v1), Table 1, PDF p.6.

Waymo test split, 비교 방법이 모두 복원한 공통 valid 영역. Z-RMSE는 median Z-offset alignment 후 road elevation error다.

| Method   | PSNR ↑ | Z-RMSE ↓ | Storage (MB) ↓ |
| -------- | ------ | -------- | -------------- |
| AnySplat | 24.09  | 4.8173   | 712.47         |
| RoGS     | 24.81  | 0.2635   | 178.67         |
| RoadVGGT | 25.71  | 0.2312   | 112.81         |

RoGS는 test-time scene optimization을 수행하고 RoadVGGT는 하지 않는다. 제공된 pose·depth·semantic 입력이 있으므로 RGB-only 또는 자체 semantics 추정 결과로 주장할 수 없다.

## 💡 Insights & Impact

도로의 실제 표면 구조를 fusion 규칙에 반영해 primitive 수와 boundary 손실을 함께 줄인다.

- 정적 도로 평면과 외부 calibration·depth·semantic 품질에 의존한다.
- 공통 valid 영역 평가만으로 전체 도로 coverage 우열을 알 수 없다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 기하 backbone 계열.
- [Splatt3R](splatt3r.md): geometry에서 Gaussian으로 연결하는 배경.

## 📚 Key Takeaways

1. Pose·depth·semantics가 입력이다.
2. Head 학습과 구조별 grid fusion을 결합한다.
3. 공통 평가 영역과 Z alignment를 보존한다.

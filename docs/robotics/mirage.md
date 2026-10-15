# MIRAGE: Metric Inference and Reliability-Aware Gaussian Estimation from Feed-Forward Vision (arXiv 2026)

## 📋 Overview

- **Authors**: Xinzhe Wang, Changjian Jiang, Kaiwen Song, Xudong Li, Kerui Ren, Ran Yi, Lizhuang Ma, Chunhua Shen, Linning Xu, Tao Lu, Mulin Yu
- **Institution**: Shanghai Jiao Tong University, Shanghai Artificial Intelligence Laboratory, University of Hong Kong, University of Science and Technology of China, Fudan University, Zhejiang University, Chinese University of Hong Kong
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.12568)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.12568v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: MASt3R 계열 visual correspondence를 LiDAR–IMU의 metric motion과 묶고 reliability에 따라 loop correction을 조절하여 Gaussian mapping을 수행한다.

## 🎯 Key Contributions

1. LiDAR metric depth·position anchor로 visual tracking을 구속한다.
2. Support·cross-modal agreement에 따라 loop correction 크기·회전을 조절한다.
3. Streaming map을 image·LiDAR로 offline 정제한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 동기화된 RGB·LiDAR·IMU와 sensor calibration.
- **Output**: Metric camera pose, streaming Gaussian scene와 offline refined map.
- **Problem**: Visual prior는 scale·drift가 불안정하고 LiDAR–inertial motion만으로는 image-space consistency가 부족하다.

### Method

1. Visual correspondence와 LiDAR depth completion으로 frame–keyframe pose를 최적화한다.
2. LiDAR–inertial BA의 metric anchor와 visual keyframe을 연결한다.
3. Loop correction은 visual support·cross-modal agreement와 rotation gate로 제어한다.
4. Pose를 고정한 뒤 image residual·LiDAR support로 Gaussian split·replace·insert를 수행한다.

기존 feed-forward prior와 online·offline 최적화를 연결한 multimodal 시스템이다. 새 vision-only benchmark의 reference trajectory도 MIRAGE-derived이며 독립 GT와 구분한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.12568v2), Table 1, PDF p.7.

Oxford Spires, online translational ATE RMSE(cm). 두 방법 모두 metric sensing이며 SE(3) alignment 조건이다.

| Sequence       | EllipseLIO ↓ | MIRAGE online ↓ |
| -------------- | ------------ | --------------- |
| Observatory 01 | 5.74         | 3.43            |
| Keble 03       | 6.02         | 7.13            |

모든 sequence에서 개선하지 않는다. Vision-only 비교는 Sim(3), metric 방법은 SE(3) alignment이며 offline HBA 값은 online 값과 별도다.

## 💡 Insights & Impact

Visual correction이 도움이 되는 정도를 관성·LiDAR와의 합의로 제한한다.

- Calibration·synchronization·LiDAR depth support에 의존한다.
- Reference를 만든 시스템을 평가할 때 reference 생성의 의존성과 sensor 입력 차이를 고려해야 한다.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): dense correspondence prior.
- [DAVIO](davio.md): RGB–IMU와 DA3를 연결하는 다른 modality 구성.

## 📚 Key Takeaways

1. RGB-only 방법이 아니다.
2. Reliability gate가 correction을 조절한다.
3. Online pose·offline refinement·reference 생성 역할을 구분한다.

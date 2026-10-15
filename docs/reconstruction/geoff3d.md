# GeoFF3D: Coordinate-Anchored Feed-Forward Reconstruction for Large-Scale UAV Mapping (arXiv 2026)

## 📋 Overview

- **Authors**: Xiang Yang, Yongli Wang, Yunsheng Zhang, Jun Li, Hao Chen, Haifeng Li
- **Institution**: Central South University, National University of Defense Technology
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.28288)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.28288v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 항공 영상과 지리 좌표 prior로 중력 방향이 고정된 metric pointmap을 예측하고 공간별 chunk를 계층적으로 합친다.

## 🎯 Key Contributions

1. GNSS translation anchor를 예측 좌표계 안에 넣는다.
2. 촬영 순서 대신 지상 footprint로 chunk를 나눈다.
3. 공유 view의 depth prior와 중력 보존 정렬로 seam을 줄인다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: UAV RGB 이미지, georeferenced camera translation과 공간 분할에 필요한 위치·방향 정보; 선택적 geometry prior.
- **Output**: 공통 Z-up metric 좌표계의 camera pose와 dense pointmap.
- **Problem**: 거의 직선인 UAV 궤적은 사후 Sim(3) 정렬의 기울기를 충분히 구속하지 못한다.

### Method

1. Pi3X에서 초기화한 모델에 translation anchor를 넣어 world-frame geometry를 학습한다.
2. 지상 footprint가 가까운 영상을 overlapping chunk로 묶는다.
3. 장면 중심에서 바깥으로 처리하며 공유 view의 depth와 가능한 intrinsics를 cache로 전달한다.
4. Chunk를 중력 방향을 보존하는 변환으로 계층적으로 합친다.

UAVFF3D와 BlendedMVS에서 local·world·pose·gravity supervision을 사용한다. 평가 prior는 GT 위치·방향에 잡음을 더해 생성되므로 RGB-only와 동일한 조건이 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.28288v1), Tables 1–2, PDF p.6.

Aerial block 9개와 UAVScenes 긴 sequence의 평균 F@5. F@5는 5m threshold의 reconstruction F-score이며 높을수록 좋다.

| Evaluation         | Pi3X + SLRF | GeoFF3D |
| ------------------ | ----------- | ------- |
| Nine aerial blocks | 0.829       | 0.877   |
| UAVScenes          | 0.687       | 0.848   |

두 방법은 같은 noisy pose prior를 사용한다. UAVScenes의 accuracy/completeness(m)는 Pi3X+SLRF 6.05/4.40, GeoFF3D 4.14/2.28이다.

## 💡 Insights & Impact

좌표계는 마지막 정렬 단계뿐 아니라 모델의 예측 대상과 학습 손실에서 결정할 수 있다.

- GNSS·IMU prior 오차와 공간 overlap에 의존한다.
- GT를 교란한 prior의 실험이 실제 센서 오류 분포를 모두 대표하지 않는다.

## 🔗 Related Work

- [π3](pi3.md): permutation-equivariant geometry의 배경.
- [On-the-Fly3R](on-the-fly3r.md): 다른 UAV 확장 전략.

## 📚 Key Takeaways

1. RGB-only가 아니라 위치 prior를 받는다.
2. 중력 방향과 metric scale을 예측 단계에 넣는다.
3. 공간 chunking과 prior 공유가 모델 확장을 담당한다.

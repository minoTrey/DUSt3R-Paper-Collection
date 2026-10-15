# GeoRay: Gauge-Aware Feed-Forward Satellite 3D Reconstruction in the Geodetic Frame (arXiv 2026)

## 📋 Overview

- **Authors**: Zhe Dong, Wanqing Wu, Yuzhe Sun, Haochen Jiang, Yuchen Ma, Lecheng Ren, Tianzhu Liu, Yanfeng Gu
- **Institution**: Harbin Institute of Technology, 54th Research Institute China Electronics Technology Group Corporation, State Key Laboratory of Comprehensive PNT Network and Equipment Technology, University of Manchester
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.29680)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.29680v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 위성 RPC camera의 ray를 따라 feature를 비교하고 상대 지형과 절대 고도 datum을 분리해 지리 좌표계의 surface height를 예측한다.

## 🎯 Key Contributions

1. Frozen perspective feature를 native RPC ray에 적응시킨다.
2. Height–datum gauge를 명시적으로 분리한다.
3. 절대 오차·coverage·relief를 함께 평가하는 SatGauge protocol을 정의한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 위성 이미지, RPC metadata와 선언된 개수의 height control; zero-control 구성도 지원한다.
- **Output**: 절대 geodetic frame의 DSM height와 uncertainty.
- **Problem**: Perspective scene에서 잘 작동하는 feature와 정렬 metric은 위성의 절대 고도·센서 bias 문제를 가릴 수 있다.

### Method

1. Ray-consistent adapter로 RPC height hypothesis의 feature matching을 학습한다.
2. Relative relief와 absolute datum을 분리해 수직 원점 이동에 일관된 예측을 만든다.
3. Monocular·multi-view relief를 calibrated inverse-variance로 융합한다.
4. 제공한 control budget에 맞춰 datum을 조정하되 test reference에서 height range를 가져오지 않는다.

Frozen backbone 위 adapter·height 추정 부분을 학습한다. Registration 이후 진단 점수와 절대 좌표계 점수를 분리한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.29680v1), Table IV, PDF p.9.

Ground control 없는 held-out US3D 26 tiles. Abs. MAE는 정렬 전 m, coverage는 absolute frame의 percentage다.

| Method   | Absolute MAE (m) ↓ | Coverage (%) ↑ |
| -------- | ------------------ | -------------- |
| SatMVS   | 8.16               | 90.1           |
| Sat-MVSF | 4.70               | 12.4           |
| GeoRay   | 2.99               | 91.9           |

Table IV의 일부 foundation-model 행은 test-reference calibration을 사용하여 primary ranking에서 제외된다. PAGc는 diagnostic alignment 뒤의 completeness-aware 지표라 absolute MAE와 역할이 다르다.

## 💡 Insights & Impact

고도를 정렬해 맞춘 결과와 실제 지도 좌표의 고도를 맞춘 결과는 다르다. Gauge와 평가 계약을 함께 설계한다.

- 다른 sensor·도시로 전이하면 absolute error가 커진다.
- RPC·control·훈련 통계의 정보량을 숨기면 비교가 성립하지 않는다.

## 🔗 Related Work

- [VGGT](vggt.md): perspective geometry foundation model의 배경.
- [GeoFF3D](geoff3d.md): UAV coordinate anchoring과 다른 satellite RPC 문제.

## 📚 Key Takeaways

1. Native RPC ray와 absolute datum을 다룬다.
2. Control budget과 reference leakage를 명시한다.
3. 오차가 낮아도 coverage를 함께 읽는다.

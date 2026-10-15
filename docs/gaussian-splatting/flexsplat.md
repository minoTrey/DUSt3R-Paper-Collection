# FlexSplat: Flexible Feed-Forward 3D Gaussian Splatting without Point Cloud Correspondence (arXiv 2026)

## 📋 Overview

- **Authors**: Amir Sabbaghziarani, Hanting Ye, Maria Gorlatova, Yi Ding
- **Institution**: Georgia Institute of Technology/Georgia State University/Emory University TReNDS, Georgia State University, Duke University, University of Tennessee Knoxville
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.07937)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.07937v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Camera·depth를 함께 예측하는 geometry frontend와 query Gaussian decoder를 학습해 calibration 없는 object-centric NVS를 수행한다.

## 🎯 Key Contributions

1. 입력 camera pose가 필요한 query-based Gaussian decoder를 확장한다.
2. Depth-guided primitive와 multi-view deformable attention을 결합한다.
3. Primitive 수를 image resolution에서 분리한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 하나 또는 여러 object-centric RGB view. Camera pose·GT depth는 입력하지 않는다.
- **Output**: Camera·depth와 compact Gaussian set, held-out view rendering.
- **Problem**: Query Gaussian은 compact하지만 camera가 주어져야 attention의 관측 위치를 정할 수 있다.

### Method

1. Geometry transformer로 view별 camera·depth를 예측한다.
2. 예측 depth로 Gaussian query의 3D 위치를 안내한다.
3. 여러 view의 deformable attention으로 하나의 Gaussian set에 evidence를 모은다.
4. Uncertainty-weighted depth consistency와 rendering supervision으로 공동 학습한다.

Objaverse-LVIS multi-view와 ShapeNet-SRN single-view 설정을 구분한다. 평가 rendering camera를 맞추기 위해 global similarity alignment를 사용한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.07937v1), Table 1, PDF p.8.

ShapeNet-SRN single-view NVS의 Cars category 평균. 네 view GSO 실험과 다른 설정이다.

| Method       | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------------ | ------ | ------ | ------- |
| LeanGaussian | 25.00  | 0.930  | 0.075   |
| FlexSplat    | 25.09  | 0.920  | 0.079   |

PSNR은 조금 높지만 SSIM·LPIPS는 LeanGaussian보다 좋지 않다. Camera 입력 조건도 다르므로 모든 지표의 동일 조건 최고 성능이라고 주장하지 않는다.

## 💡 Insights & Impact

Camera를 사전에 고정하는 대신 rendering task에 맞춰 geometry frontend와 Gaussian decoder를 공동 적응시킨다.

- Object-centric 데이터의 결과이며 넓은 비정형 scene에 대한 보장은 없다.
- Predicted camera 오류가 attention과 geometry 양쪽에 전파될 수 있다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): geometry transformer 배경.
- [Splatt3R](splatt3r.md): pointmap 기반 Gaussian prediction.

## 📚 Key Takeaways

1. Camera는 입력이 아니라 추정 대상이다.
2. Gaussian budget은 pixel 수와 분리된다.
3. 단일·다중 view protocol과 지표별 trade-off를 읽는다.

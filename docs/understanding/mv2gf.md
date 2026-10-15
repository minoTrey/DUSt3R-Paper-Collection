# MV2GF: Multi-view Pedestrian Detection with a Visual Geometric Foundation Model (arXiv 2026)

## 📋 Overview

- **Authors**: Taiga Yamane, Satoshi Suzuki, Ryo Masumura, Shota Orihashi, Tomohiro Tanaka, Mana Ihori, Naoki Makishima
- **Institution**: NTT Human Informatics Laboratories
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.20639)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.20639v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: DA3의 multi-view feature·pointmap을 pedestrian detector에 연결해 camera 배치가 바뀌어도 덜 왜곡되는 BEV feature를 만든다.

## 🎯 Key Contributions

1. Task feature와 foundation geometry feature를 결합한다.
2. Pointmap으로 pixel feature를 3D 위치에 놓는다.
3. 새 camera configuration으로의 detection 전이를 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 다중 RGB camera image와 camera parameter.
- **Output**: Pedestrian 위치의 BEV detection map.
- **Problem**: 평면 projection의 shadow-like distortion을 학습한 detector는 새로운 camera 배치로 일반화하기 어렵다.

### Method

1. DA3 Giant와 task ResNet의 여러 scale feature를 결합한다.
2. Foundation pointmap을 이용해 image feature를 voxel에 배치한다.
3. Voxel feature를 spatial aggregation·height pooling으로 BEV에 모은다.
4. Task head가 pedestrian 위치를 예측한다.

GMVD-D training split으로 학습한다. Foundation model이 있다는 이유로 camera calibration이 전혀 필요 없다고 해석하면 안 된다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.20639v1), Table 1, PDF p.10.

모두 GMVD-D로 학습하고 training과 다른 camera configuration에서 평가한 MODA. Higher is better이며 일반 3D reconstruction 지표가 아니다.

| Test dataset | MSMVD | MV2GF |
| ------------ | ----- | ----- |
| GMVD-D       | 80.2  | 84.8  |
| MVPerception | 81.8  | 86.5  |
| Wildtrack    | 85.7  | 87.9  |

Wildtrack recall은 제안법이 항상 최고는 아니다. 동일 camera split인 GMVD-S와 unseen configuration split을 구분해야 한다.

## 💡 Insights & Impact

평면에 투영하며 생기는 왜곡을 후처리로 학습하기보다 predicted 3D 위치에 feature를 배치한다.

- Pointmap depth와 calibration 오차가 BEV 위치에 전파된다.
- Pedestrian task·camera configuration의 평가 범위를 벗어난 보장은 없다.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): geometry feature·pointmap backbone.
- [Map-Det3D](map-det3d.md): metric object box detection과 다른 출력.

## 📚 Key Takeaways

1. 출력은 pedestrian BEV map이다.
2. 3D pointmap이 projection을 안내한다.
3. Unseen camera configuration의 split을 명시한다.

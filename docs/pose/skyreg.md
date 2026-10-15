# Pixel-wise Geo-registration of Drone and Satellite Images (arXiv 2026)

## 📋 Overview

- **Authors**: Qingyang Liu, David G Shatwell, Parth Parag Kulkarni, Mubarak Shah
- **Institution**: University of Central Florida
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.28891)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.28891v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Drone–satellite pair의 3D geometry·camera를 예측해 query pixel을 georeferenced reference로 warp하고 pixel별 GPS를 얻는다.

## 🎯 Key Contributions

1. Camera center localization과 dense pixel geo-registration을 구분한다.
2. 평면 homography 대신 3D lift·reprojection을 사용한다.
3. LiDAR·SfM 기반 dense geodetic supervision과 held-out geographic split을 제공한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Metadata 없는 drone query RGB와 georeferenced reference image·camera·geodetic map; 선택적 DEM.
- **Output**: Query pixel별 GPS coordinate와 reference-frame warp.
- **Problem**: 기울어진 drone view의 건물·지형 parallax는 한 개 homography나 camera-center retrieval로 설명하기 어렵다.

### Method

1. Feed-forward geometry backbone으로 pointmap·intrinsics·relative camera를 예측한다.
2. Query pixel을 3D로 lift한다.
3. Reference camera로 재투영한 위치에서 geodetic map을 보간한다.
4. Valid pixel의 지리 좌표와 image-level median GPS를 별도로 계산한다.

SkyReg-Train의 dense depth·pose·GPS supervision으로 학습한다. 실제 drone raw footage만의 benchmark가 아니라 Google Earth 기반 query·SfM/LiDAR supervision을 포함한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.28891v1), Table 2, PDF p.13.

Held-out Urban/Suburban pixel-wise georegistration. 각 image의 pixel GPS error median을 구한 뒤 mean GE(m)를 보고한다. Camera-center error와 다르다.

| Method | Urban GE (m) ↓ | Suburban GE (m) ↓ |
| ------ | -------------- | ----------------- |
| RoMa   | 133.06         | 112.10            |
| SkyReg | 44.88          | 21.34             |

Reference image의 위치·camera 정보는 제공된다. Query RGB만으로 지구 전체에서 위치를 찾는 방법은 아니다.

## 💡 Insights & Impact

Reference의 geodetic frame을 3D warp로 query 전체에 전달해 location을 pixel 단위로 확장한다.

- Reference 선택·GPS map·depth와 camera 예측 품질에 의존한다.
- 큰 error tail과 실제 센서 domain gap이 남아 benchmark 평균만으로 정밀 측량을 보장하지 않는다.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): pairwise pointmap formulation의 배경.
- [GeoRay](../reconstruction/georay.md): satellite absolute height와 다른 task.

## 📚 Key Takeaways

1. 출력은 camera 한 점이 아니라 dense GPS다.
2. Georeferenced reference가 입력이다.
3. Pixel GE와 image-level localization을 구분한다.

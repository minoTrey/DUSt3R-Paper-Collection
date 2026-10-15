# MV2GF: Multi-view Pedestrian Detection with a Visual Geometric Foundation Model (arXiv 2026)

## 📋 Overview

- **Authors**: Taiga Yamane, Satoshi Suzuki, Ryo Masumura, Shota Orihashi, Tomohiro Tanaka, Mana Ihori, Naoki Makishima
- **Institution**: NTT Human Informatics Laboratories
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.20639)
- **Verification**: UNKNOWN (2026-10-15; source 2608.20639v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Connect DA3 multi-view features/pointmaps to pedestrian detectors, building less distorted BEV features under camera-layout changes.

## 🎯 Key Contributions

1. Combine task features with foundation geometry features.
2. Place pixel features at 3D locations through pointmaps.
3. Evaluate detection transfer to new camera configurations.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Multi-camera RGB images and camera parameters.
- **Output**: Pedestrian-location BEV detection maps.
- **Problem**: Detectors learning planar-projection shadow distortions struggle with new camera layouts.

### Method

1. Combine multi-scale DA3 Giant and task-ResNet features.
2. Place image features into voxels with foundation pointmaps.
3. Aggregate voxel features into BEV through spatial aggregation/height pooling.
4. Predict pedestrian positions with task heads.

Train on GMVD-D splits. A foundation model does not imply calibration is unnecessary.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.20639v1), Table 1, PDF p.10.

All methods train on GMVD-D and evaluate MODA on different camera configurations. Higher is better; this is not a generic 3D-reconstruction metric.

| Test dataset | MSMVD | MV2GF |
| ------------ | ----- | ----- |
| GMVD-D       | 80.2  | 84.8  |
| MVPerception | 81.8  | 86.5  |
| Wildtrack    | 85.7  | 87.9  |

Proposed Wildtrack recall is not always best. Separate same-camera GMVD-S from unseen-configuration splits.

## 💡 Insights & Impact

Place features at predicted 3D locations rather than learning to compensate planar-projection distortions afterward.

- Pointmap-depth and calibration errors propagate to BEV positions.
- Results do not establish guarantees beyond the tested pedestrian/camera configurations.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): geometry feature·pointmap backbone.
- [Map-Det3D](map-det3d.md): metric object-box detection has different outputs.

## 📚 Key Takeaways

1. Output pedestrian BEV maps.
2. Guide projection with 3D pointmaps.
3. Specify unseen-camera-configuration splits.

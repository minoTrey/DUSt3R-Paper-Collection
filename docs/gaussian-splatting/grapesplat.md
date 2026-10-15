# GrapeSplat: Geometry-Grounded Reconstruction via Amalgamated Pose-Free Encoding for Feed-Forward 3D Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Si-Yu Lu, Yung-Yao Chen, Yi Jan Chen, Shang-Lin Li, Ching-Chan Liao, Wen-Huang Cheng
- **Institution**: National Taiwan University, National Taiwan University of Science and Technology, NTU AI-CoRE, VinUniversity
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.23182)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.23182v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT 기반 point-wise atlas를 bounded sparse voxel로 압축하고 voxel당 Gaussian을 decode해 view 수가 늘어도 primitive 수 증가를 제한한다.

## 🎯 Key Contributions

1. Geometry·appearance feature를 예측 3D 위치에 anchor한다.
2. PEACH-Vox의 가역 companding으로 넓은 scene을 grid에 넣는다.
3. Sparse convolution으로 multi-view feature를 융합한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed·uncalibrated RGB images.
- **Output**: Camera와 renderable Gaussian scene.
- **Problem**: Pixel-aligned primitive 수는 해상도·view 수에 따라 늘고 global structure는 약해질 수 있다.

### Method

1. Adapted VGGT aggregator가 camera·depth·feature를 예측한다.
2. Pixel unprojection으로 geometry·appearance atlas를 만든다.
3. Scene-centered companding으로 unbounded point를 bounded sparse grid에 배치한다.
4. Sparse U-Net이 occupied voxel을 정제하고 Gaussian을 decode한 뒤 inverse mapping한다.

2D rendering과 3D supervision으로 학습한다. Metric scale을 RGB만으로 확정한 것이 아니라 canonical gauge를 사용한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.23182v1), Table 1, PDF p.6.

ScanNet++, context 16 views, target NVS. LPIPS는 낮을수록 좋고 rendered-depth δ1은 높을수록 좋다. Depth는 per-scene median scale alignment다.

| Method     | LPIPS ↓ | Depth δ1 ↑ | Pose AUC@30 ↑ |
| ---------- | ------- | ---------- | ------------- |
| AnySplat   | 0.499   | 0.703      | 0.766         |
| GrapeSplat | 0.380   | 0.933      | 0.939         |

Target camera는 rendering에만 사용하며 context camera로 정한 similarity transform을 적용한다. 7-Scenes LPIPS 등 모든 조건의 최고 결과는 아니다.

## 💡 Insights & Impact

Gaussian budget이 입력 pixel 수보다 occupied scene cells를 따르게 만든다.

- Companding·grid resolution이 가는 구조와 distant geometry에 영향을 준다.
- Reconstruction latency는 rasterization을 제외한 시간이다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): atlas backbone.
- [VoxelTTO](voxeltto.md): voxel Gaussian의 다른 구성과 TTO 차이.

## 📚 Key Takeaways

1. 예측 geometry에 feature를 anchor한다.
2. Voxel occupancy가 Gaussian budget을 결정한다.
3. Canonical scale과 rendering camera 정렬을 보존한다.

# VoxelTTO: Voxel-Aligned Feed-Forward 3D Gaussian Splatting with Test-Time Optimization (arXiv 2026)

## 📋 Overview

- **Authors**: Yibin Zhao, Yihan Pan, Yangwen Li, Jun Nan, Jianjun Yi
- **Institution**: East China University of Science and Technology, Shanghai Open University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.21498)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.21498v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Geometry feature를 voxel로 모아 Gaussian을 예측하고, camera prior가 있을 때 LoRA를 test-time 최적화하여 rendering camera의 불일치를 줄인다.

## 🎯 Key Contributions

1. Pixel마다 Gaussian을 만드는 대응을 끊는다.
2. Sparse 3D U-Net으로 voxel feature를 정제한다.
3. Frozen backbone의 LoRA에 pose supervision TTO를 적용한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 여러 RGB 이미지와 선택적 camera parameter.
- **Output**: Voxel-aligned Gaussian scene, camera·RGB-D rendering.
- **Problem**: Pixel-aligned primitive의 과도한 overlap과 예측 camera 오차가 held-out rendering을 악화시킨다.

### Method

1. Frozen VFM의 depth·camera·confidence와 dense feature를 추출한다.
2. Confidence-weighted center·feature를 voxel로 aggregate한다.
3. Sparse 3D U-Net 뒤 geometry·appearance branch로 여러 primitive를 decode한다.
4. Camera가 주어지면 LoRA를 pose supervision으로 보정하고 stochastic solid volume rendering을 사용한다.

Reconstruction module의 offline 학습과 scene별 LoRA TTO는 다르다. Camera prior 없는 설정을 camera-supervised TTO와 동일 조건으로 비교하면 안 된다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.21498v1), Table 1, PDF p.7.

Replica test-view RGB NVS. Input-view 재현 점수가 아니며 아래 행은 제안법의 TTO ablation이다.

| Configuration | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------------- | ------ | ------ | ------- |
| Without TTO   | 25.83  | 0.827  | 0.196   |
| With TTO      | 28.54  | 0.876  | 0.172   |

TAT input views에서는 TTO로 PSNR이 낮아지는 결과도 있다. Test-view 개선을 모든 view·dataset의 일괄 개선으로 서술하지 않는다.

## 💡 Insights & Impact

Representation을 voxel로 바꾸는 개선과 camera prior에 적응하는 최적화의 효과를 나누어 확인한다.

- Pose supervision 또는 camera prior의 품질에 의존한다.
- TTO 계산이 추가되며 optimization-free 성능과 혼동하면 안 된다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): frozen visual geometry model 배경.
- [AVSplat](avsplat.md): voxel fusion의 다른 개선.

## 📚 Key Takeaways

1. Voxel feature에서 Gaussian을 decode한다.
2. TTO는 LoRA에 camera supervision을 넣는 단계다.
3. Input·test view 점수를 분리한다.

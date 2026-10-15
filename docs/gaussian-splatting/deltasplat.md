# DeltaSplat: Iterative Gaussian Refinement for Pose-Free Feed-Forward 3D Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Chanung Park, Seunghyeon Song, Joo Chan Lee, Eunbyung Park, Jong Hwan Ko
- **Institution**: Sungkyunkwan University, Yonsei University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.09853)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.09853v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: YoNoSplat 초기 Gaussian을 context view에 다시 render하고 residual·ray·depth로 고정 weight의 update를 반복 예측한다.

## 🎯 Key Contributions

1. Pose-free Gaussian refinement를 학습한다.
2. 2D residual에 Plücker ray·rendered depth를 더해 3D update를 안내한다.
3. 빠른 dual-branch mixer와 attribute별 update head를 구성한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse RGB context views와 backbone이 예측한 camera·Gaussian; intrinsics는 선택적으로 제공한다.
- **Output**: 정제한 Gaussian의 위치·opacity·color와 novel-view rendering.
- **Problem**: 2D rendering residual만으로는 어떤 3D primitive를 어느 방향으로 고칠지 결정하기 어렵다.

### Method

1. π3에서 사전학습한 YoNoSplat으로 초기 scene을 만든다.
2. Context camera로 render한 residual과 같은 camera의 ray·depth를 인코딩한다.
3. Coarse·detail convolution branch로 넓은 구조와 세부 오차를 읽는다.
4. Projected Gaussian feature를 blending weight로 모아 attribute별 delta를 적용한다.

Backbone과 unrolled refiner를 end-to-end 학습한다. Inference update에는 gradient optimization을 쓰지 않지만 평가 target camera는 photometric optimization으로 맞춘다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.09853v1), Table 2, PDF p.7.

DL3DV-trained model의 ScanNet++ 전이, 32 context views 224×224, known intrinsics. Pose-free 평가 target camera alignment가 포함된다.

| Method     | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ---------- | ------ | ------ | ------- |
| YoNoSplat  | 17.94  | 0.659  | 0.380   |
| DeltaSplat | 18.62  | 0.670  | 0.371   |

Refinement 자체가 feed-forward라는 것과 전체 평가에 최적화가 없다는 것은 다르다. 반복 횟수·추가 rendering 비용을 함께 보아야 한다.

## 💡 Insights & Impact

현재 예측의 ray·depth와 residual을 같은 좌표계에 두어 pose 오차가 있어도 일관된 refinement 입력을 만든다.

- Backbone camera·geometry가 크게 틀리면 residual의 3D 귀속도 불안정하다.
- 추가 반복은 시간·memory를 쓰며 원래 관측되지 않은 내용을 확정하지 못한다.

## 🔗 Related Work

- [YoNoSplat](yonosplat.md): 실제 backbone.
- [VoxelTTO](voxeltto.md): gradient TTO와 학습 update의 차이.

## 📚 Key Takeaways

1. 반복은 학습한 delta 예측이다.
2. Residual만이 아니라 ray·depth를 함께 쓴다.
3. Refinement와 평가 camera 최적화를 구분한다.

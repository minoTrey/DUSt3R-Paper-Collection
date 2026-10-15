# 2Xplat: Decoupling Geometry and Appearance Modeling for Feed-Forward 3D Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Hwasik Jeong, Seungryong Lee, Gyeongjin Kang, Seungkwon Yang, Xiangyu Sun, Seungtae Nam, Eunbyung Park
- **Institution**: Yonsei University, Sungkyunkwan University
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.21064)
- **Verification**: UNKNOWN (2026-10-15; 원문 2603.21064v3 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Geometry expert가 camera를 추정하고 별도 appearance expert가 그 camera를 받아 Gaussian을 생성하도록 작업을 분리한다.

## 🎯 Key Contributions

1. 한 backbone에 geometry·appearance를 모두 얹는 설계와 비교한다.
2. Pose expert와 posed Gaussian expert를 end-to-end 연결한다.
3. GT camera가 있으면 pose expert를 우회하는 구성을 지원한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed RGB view; 선택적으로 GT camera.
- **Output**: Camera와 pixel-aligned Gaussian scene.
- **Problem**: 공유 representation 안에서 pose 추정과 세밀한 appearance 생성이 얽히면 각 작업의 특화가 어렵다.

### Method

1. Geometry expert가 view별 camera를 예측한다.
2. Appearance expert가 이미지와 camera 조건으로 Gaussian을 만든다.
3. 두 expert를 joint fine-tuning해 pose 오차에 대한 appearance branch의 적응을 유도한다.
4. GT camera가 제공되면 geometry prediction을 건너뛰어 posed 조건으로 실행한다.

사전학습 expert를 연결해 학습한다. vdo는 view-dependent opacity·regularization을 추가한 별도 variant이고 EPA는 추가 평가 정렬 절차다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2603.21064v3), Table 1, PDF p.5.

DL3DV 12 input views, 224×224. 아래는 GT pose·intrinsics를 입력하지 않고 EPA도 적용하지 않은 기본 행이다.

| Method    | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| --------- | ------ | ------ | ------- |
| YoNoSplat | 20.383 | 0.602  | 0.229   |
| 2Xplat    | 23.851 | 0.778  | 0.182   |

GT camera·EPA·vdo를 사용하는 행은 다른 조건이다. Camera 오류와 rendering 품질이 함께 영향을 주는 pose-free NVS 결과다.

## 💡 Insights & Impact

Geometry와 appearance를 분리해도 joint 학습으로 연결할 수 있으며, posed 모델의 발전을 재사용하기 쉽다.

- 두 expert의 연속 실행과 interface 비용을 고려해야 한다.
- Camera 추정이 실패하면 appearance expert도 잘못된 좌표계에서 예측한다.

## 🔗 Related Work

- [YoNoSplat](yonosplat.md): pose-free NVS 비교 방법.
- [VGGT](../reconstruction/vggt.md): geometry expert 설계의 배경.

## 📚 Key Takeaways

1. Pose 추정과 Gaussian 생성을 별도 expert로 둔다.
2. 분리 설계지만 end-to-end 학습한다.
3. GT camera·EPA·vdo 행을 섞지 않는다.

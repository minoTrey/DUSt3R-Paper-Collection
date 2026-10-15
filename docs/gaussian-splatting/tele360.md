# Tele360: Real-Time Feed-Forward Human Reconstruction from Sparse Unposed Cameras (arXiv 2026)

## 📋 Overview

- **Authors**: Hanzhang Tu, Zhanfeng Liao, Wei Min, Jiajun Zhang, Yebin Liu
- **Institution**: Tsinghua University, Shadow AI
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.15032)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.15032v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Calibration 없는 주변 camera의 사람 영상을 foreground 중심 Transformer와 camera 보정 layer로 처리해 실시간 전송 가능한 Gaussian map을 예측한다.

## 🎯 Key Contributions

1. Hybrid CNN–ViT로 고해상도 appearance와 geometry를 결합한다.
2. Foreground token만 attention해 비용을 줄인다.
3. Differentiable LM camera layer와 geometry teacher 증류를 사용한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse surrounding RGB camera stream; 입력 calibration은 필요하지 않다.
- **Output**: Camera pose, pixel-aligned human Gaussian map과 원격 free-viewpoint rendering.
- **Problem**: Sparse unposed camera의 사람을 고해상도로 복원하면서 live 전송·rendering까지 처리하기 어렵다.

### Method

1. Low-resolution DINO feature와 high-resolution CNN pyramid를 결합한다.
2. Video matting foreground 안의 token과 camera·scene token으로 geometry를 추정한다.
3. Feature·depth consistency residual을 LM layer로 보정한다.
4. Gaussian map을 video codec으로 전송하고 viewer에서 primitive로 복원한다.

Geometry teacher와 patch similarity 구조를 맞추는 distillation을 포함한다. Calibration layer의 반복 계산과 network-only timing을 전체 시스템 시간과 구분한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.15032v1), Table 1, PDF p.11.

DNA-Rendering, 6 input views. AnySplat은 평가 camera alignment를 사용하고 Tele360은 사용하지 않는다. 원문의 대략적 timing은 아래 표에서 제외했다.

| Method   | Evaluation alignment | PSNR ↑  | SSIM ↑ | LPIPS ↓ |
| -------- | -------------------- | ------- | ------ | ------- |
| AnySplat | Yes                  | 24.9883 | 0.9163 | 0.0781  |
| Tele360  | No                   | 32.1502 | 0.9689 | 0.0286  |

Studio·human capture의 결과이며 일반 scene reconstruction으로 확대하면 안 된다. Foreground matting과 capture 배치의 조건이 있다.

## 💡 Insights & Impact

사람 중심 sparse token과 전송 가능한 pixel-aligned representation을 함께 설계한다.

- Matting 실패와 극심한 가림이 geometry에 영향을 준다.
- Inference·encoding·network·viewer latency는 서로 다른 시간이다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): geometry teacher 계열.
- [Human3R](../dynamic/human3r.md): 다른 human-scene reconstruction 문제.

## 📚 Key Takeaways

1. Unposed surrounding capture에서 Gaussian을 추정한다.
2. Foreground sparsity로 계산을 줄인다.
3. Reconstruction 시간과 end-to-end latency를 구분한다.

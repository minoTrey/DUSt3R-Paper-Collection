# Pose-Free Feed-Forward 3D Inpainting via Learnable Mask Attention and Support Token Refinement (arXiv 2026)

## 📋 Overview

- **Authors**: Jingyi Pan, Dan Xu, Qiong Luo
- **Institution**: Hong Kong University of Science and Technology Guangzhou, Hong Kong University of Science and Technology
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.11857)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.11857v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: DA3가 masked multi-view를 안정적으로 읽도록 attention을 학습하고, 관측 근거가 빈 곳에는 생성한 support token을 선택적으로 다시 넣어 3D inpainting한다.

## 🎯 Key Contributions

1. Layer별 mask suppression을 feature에 맞춰 갱신한다.
2. Rendered opacity로 blind spot을 찾는다.
3. Diffusion support view의 token을 confidence-weighted 방식으로 주입한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed RGB source images, masked region과 reference view.
- **Output**: Camera·완성 geometry와 inpainted Gaussian scene.
- **Problem**: Masked token은 pose·geometry 대응을 오염시키며 심한 가림은 한 번의 network pass에 충분한 evidence를 주지 못한다.

### Method

1. DA3 attention의 key-side bias를 mask로 초기화한다.
2. 학습 layer가 suppression을 점진적으로 조절한다.
3. 초기 Gaussian을 render해 masked 영역의 낮은 opacity를 찾는다.
4. SDEdit·IP-Adapter 기반 support view를 만들고 blind-spot confidence에 따라 token을 다시 주입한다.

Unmasked DA3 teacher의 depth pseudo-GT와 rendering loss로 적응한다. Support generation이 켜지는 경우는 기본 한 번의 forward와 시간·정보가 다르다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.11857v1), Table 1, PDF p.6.

SPIn-NeRF benchmark, novel-view image metric. 아래는 per-scene optimization baseline과 FreeInpaint의 보고값이며 camera 준비·pipeline 단계가 다르다.

| Method      | PSNR ↑ | LPIPS ↓ |
| ----------- | ------ | ------- |
| GScream     | 16.85  | 0.3644  |
| FreeInpaint | 17.79  | 0.2819  |

기본 forward의 약 0.4초와 support refinement 약 1.8초는 구분한다. 생성한 support는 실제 새 관측이 아니다.

## 💡 Insights & Impact

신뢰할 관측의 좌표 anchor를 보존하면서 missing region의 참여 강도와 생성 evidence를 조절한다.

- Diffusion prior가 실제 hidden geometry와 다른 내용을 만들 수 있다.
- Opacity confidence는 사실성이나 물리적 정확성의 확률이 아니다.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): backbone·teacher.
- [DensiTok](densitok.md): 생성 evidence를 token으로 연결하는 다른 접근.

## 📚 Key Takeaways

1. Mask가 pose·geometry를 오염시키지 않도록 학습한다.
2. Blind spot에만 support token을 보충한다.
3. 생성·재추론 비용을 single-pass 시간과 구분한다.

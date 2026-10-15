# GATOR: Generative and Agentic 3D Object Reconstruction From Casual Images (arXiv 2026)

## 📋 Overview

- **Authors**: Qirui Wu, Stan Birchfield, Hesam Rabeti, Angel X. Chang, Bowen Wen
- **Institution**: NVIDIA, Simon Fraser University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.11215)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.11215v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: RGB·mask·Pi3X pointmap을 함께 읽는 object generator 뒤에 관측 기반 edit–render–review agent를 연결해 scene-aligned textured asset을 정제한다.

## 🎯 Key Contributions

1. Patch-aligned modality mixer로 target과 scene을 구분한다.
2. Structure·geometry·appearance 생성에 text condition을 별도로 넣는다.
3. 생성 asset을 초기값으로 agent가 구조·texture를 수정한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Casual RGB images, target mask·category/caption과 추정 camera·pointmap.
- **Output**: 완성 textured object asset과 scene-relative pose.
- **Problem**: 완성 object 생성은 가려진 면을 만들 수 있지만 clutter 속 target 배치·구조·문자 texture가 관측과 어긋날 수 있다.

### Method

1. Pi3X로 camera·depth를 추정하고 RGB·mask·pointmap feature를 patch 단위로 섞는다.
2. TRELLIS.2 계열 cascade에서 structure·geometry·appearance를 생성한다.
3. Stage-specific semantic adapter로 category·caption을 조건화한다.
4. 생성 asset을 agent에 주고 관측과 render를 비교해 targeted edit를 반복한다.

Generative adaptation과 inference-time agent refinement는 별도다. Geometry backbone을 새로 학습한 논문과 구분되는 직접 conditioning 응용이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.11215v1), Table 1, PDF p.7.

Toys4K four-view object reconstruction. 거리 CD는 reference diameter로 normalize하며 geometry alignment와 공유 lighting protocol을 사용한다.

| Method     | Normalized CD ↓ | Normal consistency ↑ | F1 ↑  | PSNR ↑ |
| ---------- | --------------- | -------------------- | ----- | ------ |
| Pixal3D-MV | 0.011           | 0.783                | 0.701 | 17.18  |
| GATOR      | 0.009           | 0.801                | 0.757 | 17.60  |

두 방법은 Pi3X geometry estimate를 공유한다. Agent 없는 generator·agent-only baseline·full framework의 시간 budget은 따로 비교해야 한다.

## 💡 Insights & Impact

Geometry-conditioned generation이 instance별 초기값을 제공하면 agent가 관측에 근거한 구체적 수정에 집중할 수 있다.

- 숨은 면은 생성 prior이며 실제 object 내부를 측정한 것이 아니다.
- Agent·proprietary 모델·도구 budget에 따라 재현성과 runtime이 달라진다.

## 🔗 Related Work

- [π3](../reconstruction/pi3.md): Pi3X geometry conditioning 계열.
- [SPOON](spoon.md): 생성 object를 scene layout에 연결하는 다른 framework.

## 📚 Key Takeaways

1. Geometry model은 object 생성의 조건을 제공한다.
2. Generative 초기화 뒤 agent가 수정한다.
3. 정규화 거리와 시간 budget을 보존한다.

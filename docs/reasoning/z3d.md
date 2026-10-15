# Zero-Shot Novel Depth Synthesis Using 3D Foundation Models Scene Representations (arXiv 2026)

## 📋 Overview

- **Authors**: Denis M. Akola, David F. Fouhey
- **Institution**: New York University, Tandon School of Engineering, Courant Institute of Mathematical Sciences
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.04174)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.04174v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 3D foundation model의 scene token에서 target camera의 latent를 조건부 생성하고 기존 depth head로 보이지 않은 시점의 geometry를 예측한다.

## 🎯 Key Contributions

1. Layered-depth probe로 hidden surface 정보를 분석한다.
2. Pointmap 대신 geometry token 공간에서 diffusion한다.
3. Source token·relative target pose를 조건으로 novel depth를 생성한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Source RGB view와 source 대비 target camera pose.
- **Output**: 관측하지 않은 target view의 depth·pointmap.
- **Problem**: Visible-surface reconstruction만으로는 이동할 새 시점에서 가려진 구조를 질의하기 어렵다.

### Method

1. Frozen VGGT 또는 WorldMirror로 source token을 추출한다.
2. Source의 여러 layer를 context로 쓰고 target의 선택한 layer token을 noise에서 생성한다.
3. Pose encoder와 DiT cross-attention으로 target geometry를 조건화한다.
4. 샘플링한 representation을 DPT head로 depth에 decode한다.

Diffusion·pose conditioning은 대규모 multi-view 자료로 학습한다. 제목의 zero-shot은 새로운 dataset 전이를 가리키며 학습이 없다는 뜻이 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.04174v1), Table 3, PDF p.13.

One source → one target novel-view depth. 아래는 VGGT direct-depth baseline과 Z3D-VGGT의 out-of-domain AbsRel이다.

| Dataset  | VGGT-DD ↓ | Z3D-VGGT ↓ |
| -------- | --------- | ---------- |
| DTU      | 0.022     | 0.012      |
| 7-Scenes | 0.274     | 0.260      |
| NRGBD    | 0.192     | 0.260      |

NRGBD에서는 더 나쁘다. Point-cloud accuracy·completeness와 depth metric은 별도 표이며 생성의 사실성을 한 지표로 확정할 수 없다.

## 💡 Insights & Impact

Geometry backbone의 표현을 새로운 view의 latent 생성 공간으로 재사용한다.

- Overlap이 적으면 fine geometry가 악화된다.
- 숨은 surface는 plausible completion이며 실제로 관측한 정답이 아니다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md), [WorldMirror](../reconstruction/worldmirror.md): backbone.
- [JUSt3R](../reconstruction/just3r.md): pointmap flow와 다른 latent 생성.

## 📚 Key Takeaways

1. Source token과 target pose로 새 depth를 생성한다.
2. Zero-shot과 training-free를 구분한다.
3. Domain별 실패와 completeness trade-off를 보존한다.

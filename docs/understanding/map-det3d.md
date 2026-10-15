# Map-Det3D: Metric Feed-Forward 3D Reconstruction Prior for Multi-view 3D Object Detection from Streaming Inputs (arXiv 2026)

## 📋 Overview

- **Authors**: Yung-Hsu Yang, Luigi Piccinelli, Samuel Rota Bulò, Sunghwan Hong, Denis Rozumny, Johannes Schönberger, Zuria Bauer, Hermann Blum, Peter Kontschieder, Marc Pollefeys
- **Institution**: ETH Zürich, Meta Reality Labs Zürich, University of Bonn
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.12179)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.12179v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 짧은 RGB temporal window를 MapAnything의 metric 3D feature로 바꾸고 DETR-style decoder가 object box를 직접 3D에서 예측한다.

## 🎯 Key Contributions

1. Metric reconstruction prior를 streaming detection에 사용한다.
2. Object-aware multi-view feature를 fine-tuning한다.
3. Camera intrinsics·pose conditioning의 효과를 분리한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 현재와 과거 RGB frame의 causal window; 구성에 따라 camera intrinsics·pose.
- **Output**: Metric 3D object boxes.
- **Problem**: 2D detection을 depth로 lift하면 작은 거리 오류가 3D box 위치 오류로 크게 나타난다.

### Method

1. 시간상 여러 frame을 서로 다른 view로 처리한다.
2. MapAnything의 geometry·scale encoder로 공통 metric representation을 만든다.
3. Object-centric feature를 학습하며 multi-view transformer를 적응시킨다.
4. DETR-style query decoder가 2D box lifting 없이 3D box를 직접 회귀한다.

Detection supervision으로 fine-tuning한다. Camera conditioning이 있는 결과와 없는 결과를 분리한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.12179v1), Table 1, PDF p.10.

CA-1M validation AP15 ablation. 아래 두 행 모두 multi-view·scale head·multi-view transformer를 학습하며 K/Pose 입력만 다르다.

| Configuration           | K/Pose input | AP15 ↑ |
| ----------------------- | ------------ | ------ |
| Adapted metric backbone | Neither      | 17.2   |
| Adapted metric backbone | Both         | 21.2   |

그냥 multi-view만 추가한 frozen prior는 큰 이득이 없었다. Camera pose 입력으로 얻은 차이를 RGB-only 학습 효과로 주장하지 않는다.

## 💡 Insights & Impact

좋은 dense geometry 표현이 바로 object detection feature가 되는 것은 아니므로 task-specific 적응이 필요하다.

- Metric scale prior와 camera domain shift에 영향을 받는다.
- 추가 pose·intrinsics 정보가 비교 성능에 중요한 역할을 한다.

## 🔗 Related Work

- [MapAnything](../reconstruction/mapanything.md): metric backbone.
- [MV2GF](mv2gf.md): pointmap으로 pedestrian BEV를 만드는 별도 task.

## 📚 Key Takeaways

1. Metric 3D 공간에서 box를 직접 decode한다.
2. 학습 대상과 temporal context 효과를 분리한다.
3. Camera input 유무를 표 옆에 보존한다.

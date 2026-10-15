# RelationVGGT: Visual Geometry Transformers for 3D Spatial Relation Segmentation (arXiv 2026)

## 📋 Overview

- **Authors**: Minsu Kim, Jaesung Choe, Jiwoo Lee, Yu-Chiang Frank Wang, Seon Joo Kim
- **Institution**: Yonsei University, NVIDIA
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.00970)
- **Verification**: UNKNOWN (2026-10-15; 원문 2610.00970v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Subject mask와 관계 문장을 받아 여러 이미지에서 그 관계에 해당하는 target을 찾으며 Pi3 geometry token과 DINOv2 semantics를 결합한다.

## 🎯 Key Contributions

1. Target category 없이 spatial relation segmentation을 정의한다.
2. Subject-conditioned cross-view relation transformer를 학습한다.
3. VLM·LLM annotation pipeline으로 relation label을 만든다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed RGB views, reference subject mask, relational text query. Target category 이름은 주지 않는다.
- **Output**: View별 target segmentation mask와 3D visualization.
- **Problem**: Object category 검색만으로는 특정 물체의 위·옆·아래에 있는 대상을 구분하기 어렵다.

### Method

1. Frozen DINOv2와 Pi3 encoder token을 추출한다. 이름과 달리 실제 geometry feature는 Pi3다.
2. Input mixer로 semantic·geometry feature를 결합한다.
3. Subject mask 조건의 relation transformer가 target별 relation embedding을 만든다.
4. BERT query와 dense feature의 similarity로 mask를 얻는다.

ScanNet++ 기반 자동 relation annotation으로 학습한다. Per-scene NeRF·Gaussian 최적화 없이 mask를 예측한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2610.00970v2), Table 1, PDF p.8.

Replica·LERF·ScanNet++ relation segmentation mIoU. RelationField는 target category retrieval 정보가 있고 † variant는 relation-only다.

| Method        | Replica ↑ | LERF ↑ | ScanNet++ ↑ |
| ------------- | --------- | ------ | ----------- |
| RelationField | 0.326     | 0.276  | 0.307       |
| RelationVGGT  | 0.446     | 0.254  | 0.445       |

LERF에서는 RelationField보다 낮다. Subject mask와 relational query를 제공하는 조건이며 무조건적인 scene 이해 정확도를 뜻하지 않는다.

## 💡 Insights & Impact

3D foundation feature는 explicit scene representation을 최적화하지 않고도 관계에 따른 view-consistent mask를 만드는 prior가 된다.

- 자동 relation annotation과 language ambiguity의 영향을 받는다.
- 가까이 붙은 작은 object가 많은 장면에서 성능이 낮다.

## 🔗 Related Work

- [π3](../reconstruction/pi3.md): 실제 geometry encoder.
- [GroupForward](groupforward.md): instance scene graph를 사용하는 다른 관계 접근.

## 📚 Key Takeaways

1. 이름보다 실제 backbone을 확인한다.
2. Category 대신 subject·relation으로 target을 지정한다.
3. Target 정보가 다른 baseline 조건을 명시한다.

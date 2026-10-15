# CGGT: Curve-Grounded Geometry Transformer for 3D Parametric Curve Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Zhirui Gao, Renjiao Yi, Yunfan Ye, Ruizhen Hu, Chenyang Zhu, Wei Chen, Kai Xu
- **Institution**: National University of Defense Technology, Hunan University, Shenzhen University, Institute of AI for Industries Chinese Academy of Sciences
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.14521)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.14521v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT·DINO feature로 여러 view의 동일 curve를 찾아 2D mask를 예측하고, 이를 3D parametric wireframe으로 fitting한다.

## 🎯 Key Contributions

1. Camera·edge map이 없는 sparse view에서 curve instance를 grounding한다.
2. Curve-aware masked attention과 depth enhancement를 사용한다.
3. Line·Bézier·ellipse를 compact primitive로 최적화한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse unposed RGB 이미지.
- **Output**: 편집 가능한 3D parametric curve·wireframe.
- **Problem**: Dense surface reconstruction과 CAD에서 수정 가능한 구조 curve 복원은 다른 출력 문제다.

### Method

1. VGGT geometry token이 DINO appearance feature를 cross-attention으로 읽는다.
2. Depth-aware pixel decoder와 curve query가 view 간 curve mask·class를 예측한다.
3. 예측 pose·depth로 curve pixel을 3D로 lift한다.
4. RANSAC 초기화 뒤 3D/2D consistency·endpoint·regularity를 최적화한다.

Wireframe-100K로 curve grounding을 학습하며 최종 curve fitting은 추론 시 최적화다. 제목의 feed-forward 범위는 grounding 부분이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.14521v1), Table 1, PDF p.8.

ABC-NEF, 15 input images. F10·F20·F30은 원문 threshold 설정의 curve F-score이며 단위를 임의로 cm로 바꾸지 않았다.

| Method        | Edge preprocessing | F10 ↑ | F20 ↑ | F30 ↑ |
| ------------- | ------------------ | ----- | ----- | ----- |
| CurveGaussian | Required           | 71.5  | 76.6  | 79.0  |
| CGGT          | Not required       | 74.5  | 93.8  | 96.2  |

Geometry·pose noise에 민감하며 sparse-view와 real-object 결과는 별도 표다. 곡선 primitive의 정확도를 dense surface 정확도로 해석하지 않는다.

## 💡 Insights & Impact

Foundation geometry를 중간 좌표·depth prior로 사용해 CAD형 출력으로 연결한다.

- VGGT pose·depth 오차가 curve lifting과 fitting에 전파된다.
- Parametric primitive 가정으로 표현하기 어려운 곡선·장면은 한계가 있다.

## 🔗 Related Work

- [VGGT](vggt.md): geometry encoder.
- [DUSt3R](../foundation/dust3r.md): dense pointmap과 다른 출력 비교.

## 📚 Key Takeaways

1. 출력은 표면 point cloud가 아니라 편집 가능한 curve다.
2. 학습 grounding 뒤 parametric fitting이 있다.
3. Curve metric의 원문 threshold를 보존한다.

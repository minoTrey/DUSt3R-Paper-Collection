# SPOON: Towards Coherent Compositional 3D Scene Generation from Uncalibrated Multi-view Images (arXiv 2026)

## 📋 Overview

- **Authors**: Guibiao Liao, Mochu Xiang, Heng Li, Ken Deng, Zijie Wang, Guanbin Li, Ping Tan, Shenghua Gao, Yizhou Yu
- **Institution**: University of Hong Kong, Shenzhen Loop Area Institute, Hong Kong University of Science and Technology, Sun Yat-sen University, TranscEngram
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.39590)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.39590v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT-Ω scene geometry로 object generator의 pose 가설을 안내하고 선택한 뒤 camera·object layout을 함께 최적화해 compositional scene을 만든다.

## 🎯 Key Contributions

1. Geometry-derived surface bridge로 pose flow를 안내한다.
2. View별 pose 가설을 geometry 기준으로 routing한다.
3. Object·camera의 전역 rendering consistency를 최적화한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 여러 uncalibrated RGB image와 object instance mask.
- **Output**: 완성 object asset과 공통 scene의 object·camera layout.
- **Problem**: 각 view의 object 생성은 그럴듯해도 서로 다른 pose 가설을 독립적으로 놓으면 scene이 일관되지 않는다.

### Method

1. VGGT-Ω로 scene pointmap·camera를 추정한다.
2. SAM3D multi-view flow의 canonical object surface와 masked scene surface를 연결한다.
3. Flow time에 맞춘 geometry endpoint로 pose 생성을 안내한다.
4. Geometry-aware routing으로 가설을 선택하고 object Sim(3)·camera pose를 joint rendering loss로 조정한다.

기존 geometry·object generator를 활용하는 inference framework다. 최종 joint optimization이 있어 전체 파이프라인은 최적화 없는 단일 forward가 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.39590v1), Table 1, PDF p.7.

ARSG-110K, 4 input views. CDS/CDO는 scene/object Chamfer distance, box IoU는 layout을 측정한다. 원문 정규화 수치를 metric 거리로 바꾸지 않았다.

| Method   | Scene CD ↓ | Object CD ↓ | Box IoU ↑ |
| -------- | ---------- | ----------- | --------- |
| MV-SAM3D | 0.063      | 0.113       | 0.585     |
| SPOON    | 0.055      | 0.093       | 0.662     |

Object pose를 유지한 평가라 shape와 placement 오류가 함께 반영된다. Single-view baseline과 multi-view 입력의 정보량 차이를 보존한다.

## 💡 Insights & Impact

좋은 object generator를 scene으로 묶는 핵심은 새 shape 생성만이 아니라 object–camera의 공통 pose reasoning이다.

- Instance mask·재구성 surface·generator 오류가 연결된다.
- 관측되지 않은 shape와 texture는 생성 prior이며 실제 scene을 보장하지 않는다.

## 🔗 Related Work

- [VGGT-Ω](../reconstruction/vggt-omega.md): scene geometry guide.
- [FIRE3D](../reconstruction/fire3d.md): 다른 object-compositional reconstruction.

## 📚 Key Takeaways

1. 입력 instance mask가 필요하다.
2. Guide·route·reconcile이 layout을 연결한다.
3. Generative asset과 관측 geometry를 구분한다.

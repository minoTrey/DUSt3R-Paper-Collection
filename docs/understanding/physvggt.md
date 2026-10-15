# PhysVGGT: Feed-Forward Dense Physical Property Estimation from A Single Image (arXiv 2026)

## 📋 Overview

- **Authors**: Sneha Paul, Guile Wu, Bingbing Liu, Dongfeng Bai
- **Institution**: Huawei Noah’s Ark Lab, Concordia University, Huawei Foundation Model Department
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.18920)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.18920v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Geometry token에서 마찰·경도·탄성·밀도의 dense map과 object mass를 추정하며 학습 시 material pseudo-label과 catalog weight를 사용한다.

## 🎯 Key Contributions

1. 물성을 per-pixel prediction으로 구성한다.
2. Property 간 latent attention으로 상관관계를 학습한다.
3. Object mass는 별도 global head로 회귀한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Single RGB image.
- **Output**: Friction·Shore hardness·Young modulus·density map과 object mass.
- **Problem**: 단안 외형만으로 물성을 정확히 알 수 없으며 scene 최적화·VLM 질의 기반 방법은 추론 비용이 크다.

### Method

1. Frozen geometry encoder token을 DPT dense feature로 바꾼다.
2. Shared encoder–decoder와 cross-property coupling으로 property feature를 교환한다.
3. Property별 head로 dense map을 예측한다.
4. Token pooling과 MLP로 catalog-supervised mass를 예측한다.

SAM2 part·VLM material/hardness label·engineering lookup/empirical relation으로 dense supervision을 만든다. 물성 전체를 직접 측정한 GT는 아니며 mass는 ABO catalog에서 별도로 얻는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.18920v1), Table 1, PDF p.7.

ABO-500의 held-out 100 test objects. ADE는 kg, ALDE는 log error, MnRE는 min-of-ratio score로 높을수록 좋다.

| Method   | ADE (kg) ↓ | ALDE ↓ | MnRE ↑ |
| -------- | ---------- | ------ | ------ |
| AURA     | 8.33       | 0.582  | 0.634  |
| PhysVGGT | 4.73       | 0.574  | 0.655  |

Mass 표와 NeRF2Physics의 sparse friction·hardness 측정은 다른 benchmark다. Predicted friction으로 계산한 grasp force는 실제 접촉 실험의 안전 보장이 아니다.

## 💡 Insights & Impact

단안 이미지의 물성 출력은 측정이라기보다 geometry·material prior에 근거한 추정임을 분명히 해야 한다.

- Pseudo-label과 material table의 가정이 출력에 포함된다.
- 숨은 재료·속이 빈 구조·실제 접촉 조건은 외형만으로 식별하기 어렵다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): geometry-aware representation 배경.
- [IGGT](iggt.md): geometry feature를 다른 dense task로 확장하는 맥락.

## 📚 Key Takeaways

1. Dense property와 global mass는 별도 branch다.
2. Label이 측정인지 pseudo-label인지 구분한다.
3. Benchmark 추정을 실제 물성 측정으로 표현하지 않는다.

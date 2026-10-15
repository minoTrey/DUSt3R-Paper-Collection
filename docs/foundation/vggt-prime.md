# VGGT-Prime: Compute-Adaptive Mixture-of-Heads for Efficient Visual Geometry Transformers (arXiv 2026)

## 📋 Overview

- **Authors**: Abteen Arab, Guile Wu, Chengjie Huang, Dongfeng Bai
- **Institution**: Huawei Noah’s Ark Lab, University of British Columbia
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.23733)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.23733v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT의 모든 attention head를 같은 비용으로 계산하지 않고, 입력별 중요도에 따라 평균 pooling·근사 attention·정확한 attention으로 배분한다.

## 🎯 Key Contributions

1. Token 중복 대신 head의 역할 중복을 분석한다.
2. 가벼운 router가 세 계산 모드를 고른다.
3. Teacher latent 증류로 저비용 surrogate를 학습한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 여러 RGB 이미지.
- **Output**: 기존 VGGT 계열의 camera·depth·pointmap 예측.
- **Problem**: Global attention의 일부 head는 거의 균일하거나 query별 차이가 작지만 모두 비싼 attention을 계산한다.

### Method

1. Head saliency를 attention entropy와 query diversity에 연결한다.
2. 중요도가 낮은 head는 mean pooling으로, 중간 head는 pooled query surrogate로 처리한다.
3. 기하 대응에 중요한 head에는 exact softmax attention을 유지한다.
4. Frozen teacher latent의 residual을 증류한 뒤 soft routing으로 fine-tuning한다.

Router·surrogate 학습과 fine-tuning이 필요하며 training-free pruning이 아니다. Token merging과 결합한 설정은 기본 모델과 구분한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.23733v1), Table 1, PDF p.7.

ScanNet 500-view point-cloud reconstruction. Summed Chamfer distance(CD)는 낮을수록 좋고 time은 해당 실험의 초 단위 추론 시간이다.

| Method     | CD ↓  | Time (s) ↓ |
| ---------- | ----- | ---------- |
| VGGT       | 0.442 | 90.1       |
| FastVGGT   | 0.437 | 28.4       |
| VGGT-Prime | 0.441 | 19.2       |

이 조건에서 runtime은 줄지만 FastVGGT보다 CD가 낮지는 않다. 논문의 최대 speedup을 모든 dataset·view 수에 적용하면 안 된다.

## 💡 Insights & Impact

모든 head를 제거하거나 보존하는 이진 선택 대신 필요한 계산의 정밀도를 조절한다.

- Router 오판과 distillation error가 geometry를 손상시킬 수 있다.
- 속도는 view 수·hardware·token merging 구성에 따라 달라진다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 원래 backbone.
- [FastVGGT](../reconstruction/fastvggt.md): token 중복을 줄이는 비교 방법.

## 📚 Key Takeaways

1. Head별 계산 모드를 입력에 맞춰 고른다.
2. 학습이 필요한 가속 방법이다.
3. 최대 속도와 특정 benchmark 결과를 구분한다.

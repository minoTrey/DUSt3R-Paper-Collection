# Generating Multi-view Adversarial Examples for Visual Geometry Grounded Transformer (arXiv 2026)

## 📋 Overview

- **Authors**: Qi Song, Ziyuan Luo, Haoliang Han, Renjie Wan
- **Institution**: Hong Kong Baptist University
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.20748)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.20748v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT에 대한 다중 view perturbation의 영향을 분석하고, view 간 관계를 학습한 generator로 재구성 변화를 평가한다.

## 🎯 Key Contributions

1. 한 장의 고정 perturbation과 scene별 반복 최적화의 차이를 비교한다.
2. View 간 attention을 사용하는 generator를 연구한다.
3. Clean·perturbed geometry의 차이를 view 수별로 측정한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 다중 RGB view와 사전학습 VGGT.
- **Output**: Perturbed 이미지와 그에 대한 geometry 변화 평가.
- **Problem**: 단일 이미지의 robustness 평가만으로 다중 view geometry 모델의 취약성을 설명하기 어렵다.

### Method

1. Generator가 여러 view를 함께 읽는다.
2. View 내부와 view 사이 attention으로 정보 교환을 수행한다.
3. Dense head로 이미지별 perturbation을 예측하고 학습된 generator를 새 scene에 적용한다.
4. Clean과 perturbed VGGT point cloud 사이의 shifted Chamfer distance를 비교한다.

Generator 학습에는 VGGT output 변화 supervision이 필요하다. 한 단계라는 말은 학습 후 생성 시점에 해당하며 학습 비용을 포함하지 않는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.20748v1), Table 1, PDF p.10.

CO3D, 4 input views. Shifted CD는 clean output과 perturbed output의 차이이며 값이 클수록 geometry 교란이 크다. GT reconstruction error나 attack success percentage가 아니다.

| Perturbation      | Shifted CD ↑ |
| ----------------- | ------------ |
| Gaussian noise    | 0.666        |
| UAP               | 0.675        |
| AP, 20 iterations | 1.892        |
| MVAP-G            | 2.016        |

이 표만으로 실제 물리 촬영이나 모든 geometry backbone에 대한 취약성을 확정할 수 없다. 숫자는 지정된 VGGT·dataset·perturbation 조건에 한정된다.

## 💡 Insights & Impact

Geometry output이 서로 일관되어 보여도 입력 perturbation에 robust하다는 보장은 없다.

- Shifted CD는 GT 정확성 저하를 직접 측정하지 않는다.
- 평가 모델과 데이터 조건 밖의 전이·물리적 재현은 별도로 확인해야 한다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 평가 대상.
- [Confidence Audit](confidence-audit.md): 다른 종류의 reliability 분석.

## 📚 Key Takeaways

1. 다중 view 관계를 고려한 robustness 평가다.
2. Clean과 perturbation output 차이를 측정한다.
3. 수치를 실제 환경의 실패 확률로 바꾸지 않는다.

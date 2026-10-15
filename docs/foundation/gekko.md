# Revisiting Cross-View Completion: Self-Supervised Pre-Training via Reconstruction Error Comparison (arXiv 2026)

## 📋 Overview

- **Authors**: Thibaut Loiseau, Guillaume Bourmaud, Vincent Lepetit
- **Institution**: LIGM, École Nationale des Ponts et Chaussées, IP Paris, Université Gustave Eiffel, CNRS; Université de Bordeaux, Bordeaux INP, IMS
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.01530)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.01530v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 다른 view를 보았을 때 reconstruction error가 얼마나 줄어드는지를 학습하여, 3D 정답 없이 cross-view feature와 co-visibility 표현을 개선한다.

## 🎯 Key Contributions

1. Cross-view completion과 masked autoencoding error를 비교한다.
2. 상대 개선 map 예측을 추가 supervision으로 사용한다.
3. 동일 architecture·data·schedule의 CroCo baseline과 비교한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 일부 patch를 가린 target RGB 이미지와 reference RGB 이미지.
- **Output**: 복원 이미지, relative-improvement map, downstream geometry용 feature.
- **Problem**: 서로 보이지 않는 영역의 cross-view completion은 사실상 단안 복원으로 퇴화하여 binocular signal이 약하다.

### Method

1. 같은 masked target을 reference와 함께, 또 reference 없이 복원한다.
2. MAE error 대비 cross-view error 감소 비율을 pseudo-target으로 만든다.
3. 공유 모델이 두 복원 작업과 improvement map을 함께 예측한다.
4. Monocular error가 이미 작은 영역은 상대 개선의 신뢰성이 낮다는 점을 고려한다.

모델은 scratch에서 self-supervised pretraining한다. Downstream pose·pointmap probe의 supervised 학습은 pretraining과 별도다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.01530v1), Table 1, PDF p.6.

ScanNet-50으로 사전학습한 Base 모델, ETH3D zero-shot correspondence AEPE. Encoder·decoder feature를 각각 평가한다.

| Feature | CroCo-B AEPE ↓ | Gekko-B AEPE ↓ |
| ------- | -------------- | -------------- |
| Encoder | 78.4           | 60.8           |
| Decoder | 101.9          | 80.8           |

이 결과는 동일 조건으로 재학습한 CroCo와 비교한 것이며 공개 checkpoint 전체의 순위가 아니다. Improvement map은 완벽한 co-visibility 정답이 아니라 proxy다.

## 💡 Insights & Impact

Reference가 실제로 도움이 되었는지를 복원 error 차이로 측정하면 3D annotation 없이 binocular supervision을 만들 수 있다.

- Uniform·반복 영역에서는 MAE error가 작아 proxy가 불안정할 수 있다.
- Pretraining feature 성능과 최종 multi-view system 성능은 다른 평가다.

## 🔗 Related Work

- [CroCo](croco.md): cross-view completion baseline.
- [DUSt3R](dust3r.md): 학습 feature를 geometry로 연결하는 배경.

## 📚 Key Takeaways

1. 두 복원 error의 상대 차이를 학습한다.
2. 3D 정답 없는 사전학습과 downstream supervision을 분리한다.
3. Proxy의 실패 영역을 함께 본다.

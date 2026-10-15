# OTT3R: Multi-View 3D Reconstruction and Fast Dataset Generation at 1% Compute (arXiv 2026)

## 📋 Overview

- **Authors**: Brandon Leblanc, Charalambos Poullis
- **Institution**: Concordia University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.36374)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.36374v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: π3의 pointmap·pose를 미리 cache한 pseudo-label로 작은 multi-view student를 학습하고, 일반 모델과 도메인 특화 모델의 차이를 평가한다.

## 🎯 Key Contributions

1. 큰 teacher 추론을 offline cache로 분리한다.
2. 작은 student에 geometry·pose·confidence를 함께 증류한다.
3. 일반화 성능과 domain specialization의 효과를 명시적으로 분리한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 보정되지 않은 RGB 이미지 집합.
- **Output**: Dense pointmap, camera pose, confidence 및 pseudo-label corpus.
- **Problem**: 큰 3D 모델의 학습·추론 비용이 크며, 작은 모델은 낯선 장면의 pose에서 정확도가 크게 떨어진다.

### Method

1. π3 teacher로 source corpus의 pointmap·confidence·SE(3) pose를 한 번 계산해 저장한다.
2. 이 cache에서 여러 view group을 읽어 student만 학습한다.
3. Point·normal·pairwise relative camera·confidence loss를 결합한다.
4. 목적 도메인의 cache로 특화 student를 별도 학습한다.

Teacher에서 생성한 supervision을 사용한다. Teacher 계산을 제외한 student 비용과 전체 cache 생성 비용은 구분해야 한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.36374v1), Table 1, PDF p.10.

7-Scenes, π3 protocol의 accuracy/completeness(cm), student 입력 518×224. General은 zero-shot, domain은 7-Scenes 특화다.

| Model         | Accuracy (cm) ↓ | Completeness (cm) ↓ | FPS ↑ |
| ------------- | --------------- | ------------------- | ----- |
| π3 teacher    | 1.52            | 2.03                | 40    |
| OTT3R general | 10.16           | 34.84               | 273   |
| OTT3R domain  | 6.16            | 2.84                | 274   |

일반 student는 teacher를 대체하지 못한다. COLMAP 비교는 더 큰 입력 해상도와 완료 scene만 평가한 조건이며, CO3D student pose 표는 GT 정확도가 아니라 teacher와의 일치도를 측정한다.

## 💡 Insights & Impact

저비용 student의 실제 활용 범위는 압축률보다 도메인 특화와 pose 일반화 능력에 좌우된다.

- Teacher 오류가 pseudo-label에 남는다.
- 특화 모델의 성능을 zero-shot 일반 성능으로 제시하면 안 된다.

## 🔗 Related Work

- [π3](../reconstruction/pi3.md): teacher.
- [DUSt3R](dust3r.md): pointmap 기반 재구성 배경.

## 📚 Key Takeaways

1. Teacher 계산을 cache로 amortize한다.
2. 작은 모델은 빠르지만 OOD geometry 품질이 크게 낮다.
3. Teacher agreement와 GT 평가를 구분한다.

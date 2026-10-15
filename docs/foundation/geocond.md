# GeoCond: A Conditioning-Aware Reliability Adapter for Feed-Forward 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: David Ahmedt-Aristizabal, Mohammad Ali Armin, Russell Tsuchida, Lars Petersson
- **Institution**: CSIRO, Monash University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.18465)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.18465v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 고정된 FF3D 모델의 예측에서 시차·overlap 등 기하 conditioning을 읽어 pose 신뢰도와 refinement gate를 학습한다. Confidence가 높아도 BA를 실행하는 것이 항상 유리하지 않다.

## 🎯 Key Contributions

1. **Pose-Level Reliability**: 픽셀 confidence와 상대 pose가 잘 결정되는지를 구분한다.
2. **Supervision Choices**: frame-order orbit variance, 정답 pose error 또는 독립 pose graph cycle residual로 head를 학습한다.
3. **Selective Refinement**: 모든 결과에 BA를 적용하지 않고 유지·보정·제외 등의 판단에 신뢰도를 사용한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 고정 백본이 예측한 camera·depth·pointmap과 그 기하 관계.
- **Output**: 상대 pose uncertainty와 refinement 실행 gate. 기본 head의 추론은 한 번의 백본 실행을 읽는다.
- **Problem**: Low parallax·low overlap·큰 상대 회전에서는 pose가 약하게 결정된다. Pixel confidence는 이를 충분히 설명하지 못하며, 잘못된 BA가 초기 pose를 더 나쁘게 만들 수 있다.

### Method

1. 예측 geometry에서 pose의 conditioning을 나타내는 scalar 특징을 구성한다.
2. 학습 시 여러 frame permutation의 orbit variance를 teacher로 쓰거나 정답·cycle supervision을 선택한다.
3. 작은 head가 불확실성을 예측하고, FF 결과와 refinement의 선택에 필요한 gate를 학습한다.
4. 기본 배포 head와 여러 번 백본을 실행하는 teacher·정답으로 선택하는 oracle을 구분해 평가한다.

원문 §3–4. 백본을 고정해도 head supervision의 종류에 따라 정답 사용 여부가 다르다. 아래는 7-Scenes+MegaUnScene으로 학습하고 scene-disjoint indoor/OOD test에 적용한 Table 3이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.18465v1), Table 3, PDF p.6.

AUSE는 uncertainty의 오류 순위 품질이며 낮을수록 좋다. Final AUC@30은 refinement 결정 뒤의 pose 성능이다. 같은 split의 값만 묶었다. 대시는 해당 행이 이 지표를 보고하지 않는다는 뜻이다.

| Method                 | Indoor AUSE ↓ | Outdoor/OOD AUSE ↓ | Indoor AUC@30 ↑ | Outdoor/OOD AUC@30 ↑ |
| ---------------------- | ------------- | ------------------ | --------------- | -------------------- |
| Native VGGT confidence | 0.19          | 0.32               | —               | —                    |
| GeoCond one-pass       | 0.17          | 0.20               | 53.5            | 58.4                 |
| Feed-forward always    | —             | —                  | 51.6            | 60.3                 |
| BA always              | —             | —                  | 53.6            | 38.4                 |
| Orbit teacher          | 0.17          | 0.16               | —               | —                    |

Gate는 OOD에서 BA-always의 큰 악화를 줄이지만 FF-always의 60.3보다 낮은 58.4다. 따라서 "항상 초기 예측보다 개선"이라고 말할 수 없다. Table 2의 indoor 매우 낮은 overlap·큰 회전 bin에서도 uncertainty ranking이 악화될 수 있다.

## 💡 Insights & Impact

높은 confidence, 낮은 pose error, BA의 성공 가능성은 같은 개념이 아니다. 후처리 실행 여부를 별도 예측 문제로 다룬 점이 실용적이다.

- 학습 supervision·split·teacher를 바꾸면 수치의 의미가 달라진다. 논문의 여러 실험을 하나의 결과로 합치지 않는다.
- Gate도 domain shift와 잘못된 예측 conditioning에 영향을 받는다. 불확실성 순위 개선이 metric calibration이나 최종 pose 우위를 보장하지 않는다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 주요 고정 백본.
- [Trust3R](trust3r.md), [ReVar3R](../reconstruction/revar3r.md): 학습형·반복 추론형 uncertainty와의 관계.

## 📚 Key Takeaways

1. Pose의 기하 conditioning과 pixel confidence를 구분한다.
2. Head의 추론 비용과 teacher를 만드는 비용을 따로 읽는다.
3. BA 회피의 이점과 FF baseline 대비 손실을 함께 보고한다.

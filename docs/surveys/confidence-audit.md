# A Calibration Audit of Confidence in Feed-Forward 3D Reconstruction Models (arXiv 2026)

## 📋 Overview

- **Authors**: Nanxing Nick Deng, Qing Cheng, Niclas Zeller, Daniel Cremers
- **Institution**: Technical University of Munich, Munich Center for Machine Learning, Karlsruhe University of Applied Sciences
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.29705)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.29705v3 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: FF3D confidence가 오답의 순위를 매기는 능력과 실제 오차 크기를 나타내는 능력을 분리해 감사한다. Confidence에서 읽은 uncertainty는 ranking이 좋아도 과신될 수 있다.

## 🎯 Key Contributions

1. **Four-Property Audit**: ranking·전체 크기·confidence 구간별 slope·확률 coverage를 분리한다.
2. **Released-Model Comparison**: 여러 백본과 데이터셋을 같은 감사 정의로 평가한다.
3. **Rank-Preserving Calibration**: 두 상수의 power-law 보정과 단일 scale·bin별 보정의 차이를 비교한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 공개 FF3D 모델의 예측 pointmap·confidence와 평가용 정답 geometry.
- **Output**: uncertainty의 ranking·크기·slope·coverage 진단과 선택적 사후 보정 상수.
- **Problem**: Confidence는 학습 loss의 가중치로 최적화된다. 이것이 곧 확률적으로 보정된 오차 크기라는 가정은 별도로 검증해야 한다.

### Method

1. Loss가 암시하는 confidence-to-uncertainty 관계로 native uncertainty를 읽는다.
2. 픽셀을 confidence 구간으로 나누고 실제 geometry error와의 ranking·크기·slope를 비교한다.
3. 확률 구간의 nominal coverage와 실제 coverage를 구분해 장면 단위 전이 여부를 확인한다.
4. Calibration 장면에서 power-law 상수 두 개를 적합하고 분리한 장면에서 평가한다. 순위를 바꾸지 않는 단조 변환을 유지한다.

원문 §3–6. 7개 백본·13개 데이터셋·168개 setting을 조사한다. 사후 보정은 정답이 있는 calibration split을 필요로 하며, 모델 자체를 재학습한 결과가 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.29705v3), Table 2, PDF p.7.

각 setting에서 데이터셋의 장면을 calibration/test로 나눈 뒤 얻은 지표의 median이다. Level·slope의 목표는 1, nominal coverage는 0.90이다. In-band는 held-out 장면의 실제 coverage가 nominal에 가까운 비율이다. 행 간 차이는 특정 장면의 개선량이 아니다.

| Correction               | Overall Level (target 1) | Slope (target 1) | Coverage (target 0.90) | In-Band ↑ |
| ------------------------ | ------------------------ | ---------------- | ---------------------- | --------- |
| Native                   | 2.41                     | 0.65             | 0.570                  | 0.000     |
| One scalar per model     | 1.41                     | 0.65             | 0.917                  | 0.133     |
| Power law, two constants | 1.11                     | 0.99             | 0.905                  | 0.333     |

Power law는 전체 크기·slope를 개선하지만 held-out 장면 coverage가 모두 올바른 것은 아니다. 순위 자체를 개선하는 보정도 아니다. 원문에서 level의 배율 표기를 이 표에서는 숫자만 적었다.

## 💡 Insights & Impact

가장 나쁜 점을 먼저 제거하는 작업과 uncertainty로 서로 다른 점·장면의 잔차를 가중하는 작업은 요구하는 성질이 다르다. Ranking 성능만 보고 metric uncertainty로 사용하면 과신을 놓칠 수 있다.

- 정답 정렬·validity·loss normalization에 따라 uncertainty와 error의 관계가 달라진다.
- 데이터셋 단위 보정이 개별 장면·프레임의 확률 coverage를 보장하지 않는다. Calibration 데이터가 없으면 같은 보정 성능을 전제할 수 없다.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [VGGT](../reconstruction/vggt.md): confidence를 제공하는 감사 대상.
- [ReVar3R](../reconstruction/revar3r.md), [GeoCond](../foundation/geocond.md): 다른 신뢰도 신호를 만드는 방법.

## 📚 Key Takeaways

1. 순위와 오차 크기의 calibration은 다르다.
2. 한 개 scale이 confidence 전 범위의 slope 오류를 고치지는 못한다.
3. 보정 후에도 장면별 coverage 실패를 확인한다.

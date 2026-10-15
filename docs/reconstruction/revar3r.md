# ReVar3R: Gauge-Aware Perturbation Uncertainty for Feed-Forward 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Sammam Mahdi, Fariha Binta Salim, Rakin Bin Rabbani, Aniqua Nusrat Zereen
- **Institution**: BRAC University, Mahidol University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.07883)
- **Verification**: UNKNOWN (2026-10-15; arXiv v1 원문 확인, 학회 게재 여부 미확인)
- **TL;DR**: 입력을 조금 바꿔 여러 번 예측한 pointmap을 같은 좌표계로 정렬한 뒤 분산을 구한다. 좌표계 변화 때문에 커지는 분산을 실제 예측 불안정성과 구분한다.

## 🎯 Key Contributions

1. **Gauge Contamination**: 좌표계의 미세한 회전·축척 차이가 원점에서 먼 점의 분산을 키운다는 항을 유도한다.
2. **Align Before Variance**: 고정된 재구성 모델의 반복 출력을 먼저 정렬한다. 네트워크 가중치나 별도 불확실성 헤드를 학습하지 않는다.
3. **Separate Supervision Levels**: 정답 없이 계산하는 Core와 정답이 있는 보류 데이터로 조정하는 융합·보정 단계를 구분한다.
4. **Explicit Failure Cases**: 안정적으로 반복되는 오답과 도메인 간 보정 실패를 한계로 보고한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 같은 장면의 겹치는 다중 시점 이미지와 고정된 VGGT·π³·MASt3R 중 하나.
- **Output**: 예측한 각 3D 점의 불확실성 점수. 점수를 오류 크기로 보정하려면 추가 정답 데이터가 필요하다.
- **Gauge**: 동일한 장면도 회전·이동·축척이 다른 좌표계로 표현할 수 있는 자유도다. Sim(3)는 이 세 변환을 함께 나타낸다.

예를 들어 두 실행이 같은 벽을 올바르게 예측해도 좌표계가 조금 회전하면 먼 벽의 좌표 차이는 커진다.
이 차이를 그대로 분산으로 계산하면 실제로 불안정한 점을 찾기 어렵다.

### Alignment and Aggregation

```text
원본 다중 시점 이미지
  → 밝기 변화 또는 시점 순서 변경 → 같은 고정 모델로 반복 추론
  → 예측끼리 robust Sim(3) 정렬 → 점별 공분산의 trace
  → 불확실성 순위 → 선택적 융합·오류 크기 보정
```

§4는 Umeyama similarity fit으로 정렬을 시작한다.
잔차가 큰 대응을 반복적으로 제외하고 정렬을 다시 계산한다.
이 내부 정렬은 예측끼리 수행하며 정답 pointmap을 사용하지 않는다.
평가용 정답 정렬은 별도 단계다. 기본 평가의 시점별 정렬은 장면 전체의 정렬보다 더 많은 자유도를 허용한다 (§6.2).

기본 설정은 perturbation 계열마다 5회 예측하며 기준 예측을 공유해 총 9회 모델을 실행한다 (§5).
Core는 정렬된 단일 계열의 분산이다.
Full은 여러 점수를 융합하고 내장 confidence도 사용할 수 있다.
Full의 가중치와 오류 크기 보정은 보류한 정답 데이터로 정한다. "재학습 없음"이 "모든 단계가 정답 불필요"를 뜻하지 않는다.

## 📊 Results

### Ranking Error and Label Use

[arXiv v1 PDF](https://arxiv.org/pdf/2610.07883v1), §6.3, PDF p.7 및 Appendix C, Table 4.
VGGT·π³·MASt3R와 7-Scenes·DTU·ETH3D·BlendedMVS·TUM·KITTI의 조합을 평가한다.
각 조건은 겹치는 5-view set으로 구성한다 (§5).
AUSE는 불확실성 순위로 점을 제거할 때 정답 오류 순위와의 차이를 요약하며 낮을수록 좋다.

| Variant                             | Held-Out Labels | Conditions with Lower AUSE than Built-In Confidence |
| ----------------------------------- | --------------- | --------------------------------------------------- |
| Aligned single-family Core          | 불필요          | 11/18                                               |
| Equal-weight fusion                 | 불필요          | 12/18                                               |
| Fitted fusion weights               | 필요            | 14/18                                               |
| Full, including built-in confidence | 필요            | 15/18                                               |

이 횟수는 조건별 승리의 기술 통계다. 유의성 검정 결과가 아니다 (§5).
Full 결과를 Core만의 결과로 읽으면 안 된다.

Appendix C, Table 5 (PDF p.16)의 조건별 AUSE를 일부 발췌했다.
Full이 Core보다 항상 좋은 것은 아니며, 기존 confidence보다 나쁜 조건도 남는다.

| Backbone / Dataset  | Built-In AUSE ↓ | Core AUSE ↓ | Full AUSE ↓ |
| ------------------- | --------------- | ----------- | ----------- |
| VGGT / 7-Scenes     | 0.712           | 0.536       | 0.491       |
| VGGT / BlendedMVS   | 0.786           | 0.276       | 0.407       |
| π³ / ETH3D          | 0.528           | 0.522       | 0.593       |
| MASt3R / BlendedMVS | 0.282           | 0.659       | 0.367       |

### Cost and Limitations

논문은 단일 추론 헤드 대비 약 10배의 지연을 보고한다 (§7, Appendix D.9).
학습형 Trust3R와의 비교에서는 224 px MASt3R와 동일한 유효 점을 사용한다 (§6.5).
따라서 이 비교를 각 백본의 원래 해상도에서 수행한 전체 조건과 합치지 않는다.

BlendedMVS의 π³·MASt3R 조건과 ETH3D의 π³ 조건에서는 내장 confidence보다 AUSE가 높다 (§6.3).
정답이 필요한 보정은 다른 도메인으로 잘 이전되지 않는다.
고정 예산의 novel-view synthesis에서도 개선을 확인하지 못했다 (§7).

## 💡 Insights & Impact

핵심은 "분산이 크다"와 "오답이다"를 구분하는 것이다.
이 방법은 같은 예측의 좌표 표현이 흔들리는 효과를 줄이고 남은 불안정성을 측정한다.
모든 실행이 같은 잘못된 형상을 예측하면 분산이 낮다. 이 점수만으로 정확성을 보장할 수 없다.

정렬한 일반 입력 잡음 앙상블도 강한 비교 대상이다 (§6.2, Table 8).
따라서 개선을 perturbation 종류만의 효과로 설명하지 않는다.
한 장면의 여러 view set은 서로 상관되므로 표본 독립성과 유의성 해석에도 주의가 필요하다 (§5).

## 🔗 Related Work

- **[VGGT](vggt.md), [π³](pi3.md), [MASt3R](../foundation/mast3r.md)**: 동일한 절차를 적용하는 고정 재구성 백본이다.
- **[Trust3R](../foundation/trust3r.md)**: 정답으로 학습한 불확실성 헤드다. 재추론 비용·보정·도메인 이전 사이의 선택을 비교한다.
- **[DUSt3R](../foundation/dust3r.md)**: pointmap과 confidence를 함께 예측하는 계열의 출발점이다. 내장 confidence와 실제 오류의 관계를 추가로 검토할 필요가 있다.

## 📚 Key Takeaways

1. 여러 pointmap의 분산을 계산하기 전에 좌표계를 맞춘다.
2. Core와 정답으로 조정한 Full 결과를 구분한다.
3. 불안정성 점수는 안정적으로 반복되는 오답을 검출하지 못한다.
4. 추가 추론 비용과 도메인별 실패를 함께 고려한다.

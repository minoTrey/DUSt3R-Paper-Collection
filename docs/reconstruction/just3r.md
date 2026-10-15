# From Feed-Forward to Flow: Unifying Reconstruction and Generation Is Easier Than You Think (arXiv 2026)

## 📋 Overview

- **Authors**: Haoru Wang, Qianfan Shen, Kai Ye, Wenzheng Chen, Baoquan Chen
- **Institution**: Peking University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.32761)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.32761v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: DUSt3R에 noisy pointmap과 flow time을 더해 동일 checkpoint가 한 단계 재구성과 여러 단계 geometry 생성을 수행하게 한다.

## 🎯 Key Contributions

1. Clean-target prediction으로 재구성과 flow 생성을 통합한다.
2. 모호한 경계에서 평균 예측이 만드는 veil·flying pixel을 분석한다.
3. JUSt3R와 NVS용 JiT-LVSM으로 geometry·appearance를 각각 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 두 RGB 이미지와 flow 단계의 noisy target pointmap.
- **Output**: 공통 좌표계 pointmap. 여러 단계에서는 하나의 plausible surface를 샘플링한다.
- **Problem**: 모호한 foreground/background 경계에서 단일 regression은 실제 표면 사이의 평균 깊이를 만들 수 있다.

### Method

1. DUSt3R backbone을 유지하고 noisy target embedding과 time-conditioned adaLN을 넣는다.
2. Confidence-weighted pointmap regression으로 clean target을 예측하도록 학습한다.
3. 한 단계에서는 직접 예측 endpoint를 사용한다.
4. 여러 단계에서는 context encoding을 재사용하며 noise-to-data flow를 적분한다.

DUSt3R의 학습 데이터·schedule을 유지한 controlled 재학습 baseline과 비교한다. 배포 checkpoint는 별도 참고 행이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.32761v1), Table 3, PDF p.7.

NYU-v2 zero-shot depth. AbsRel·veil·flying rate는 낮을수록 좋다. Veil은 GT depth discontinuity 사이에 예측이 떨어지는 비율이다.

| Method            | AbsRel ↓ | Veil ↓ | Flying ↓ |
| ----------------- | -------- | ------ | -------- |
| Retrained DUSt3R  | 0.075    | 0.215  | 0.047    |
| JUSt3R, one step  | 0.070    | 0.219  | 0.037    |
| JUSt3R, ten steps | 0.071    | 0.186  | 0.023    |

여러 단계는 표면 artifact를 줄이지만 한 단계보다 AbsRel이 낮지는 않다. TUM·Bonn 등에서는 depth error가 더 커지므로 생성의 선명함을 정답 일치와 동일시하면 안 된다.

## 💡 Insights & Impact

평균 오차가 낮은 표면과 실제 표면처럼 보이는 표면은 다를 수 있다. 두 종류 지표를 함께 평가한다.

- 모호한 입력에서는 선명하지만 실제 scene과 다른 geometry를 생성할 수 있다.
- 여러 단계 추론은 추가 계산을 요구하며 veil 감소만으로 올바른 표면 선택을 보장하지 않는다.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): geometry backbone과 controlled baseline.
- [VGGT](vggt.md): 직접 geometry regression의 비교 맥락.

## 📚 Key Takeaways

1. 동일 모델의 추론 단계 수로 동작을 바꾼다.
2. Pointwise depth와 경계 구조를 따로 측정한다.
3. 선명한 생성이 항상 관측 정답은 아니다.

# S4VY: Segment Anything in Feed-Forward 4D Visual Geometry (arXiv 2026)

## 📋 Overview

- **Authors**: Jingdong Zhang, Xin Li, Jan Kautz, Wenping Wang, Chris Choy
- **Institution**: Texas A&M University, NVIDIA
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.36875)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.36875v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT-Ω visual geometry 위의 persistent object query가 모든 관측의 instance mask를 묶고, 별도 language grounder·critic이 원하는 instance를 고른다.

## 🎯 Key Contributions

1. Prompt 없이 class-agnostic instance를 먼저 분리한다.
2. Space-time query로 시간·view의 identity를 묶는다.
3. Active tree search·dual-stream grounder·critic으로 language selection을 구성한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: RGB observations; 선택적으로 point·box 또는 natural-language query.
- **Output**: 관측 전체의 persistent instance mask와 선택한 target mask.
- **Problem**: 순차 memory 기반 mask propagation만으로 큰 view 변화와 긴 4D 관측 공간을 다루기 어렵다.

### Method

1. VGGT-Ω feature에 space-time query decoder를 붙인다.
2. 각 object query가 관측 전체의 동일 entity mask를 출력한다.
3. Point·box encoder가 발견된 query를 선택한다.
4. Language harness가 relevant frame을 탐색하고 두 후보 stream을 독립 critic으로 비교한다.

Segmenter·prompt encoder·language grounder·critic을 분리 학습한다. 단일 geometry network만으로 모든 language inference를 끝내는 것은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.36875v2), Table 2, PDF p.10.

Target prompt·first-frame GT 없는 class-agnostic segmentation. DAVIS의 4D metric은 GT·prediction을 같은 추정 depth·camera로 lift한 결과이며 실제 3D GT와 다르다.

| Method | DAVIS 4D-IoU ↑ | DAVIS 4D-SR ↑ | DAVIS J&F ↑ |
| ------ | -------------- | ------------- | ----------- |
| IGGT4D | 0.543          | 0.667         | 0.604       |
| S4VY   | 0.715          | 0.914         | 0.803       |

표의 latency는 A100에서 지정 관측 수의 clip 처리 시간이다. Language harness의 모든 호출 비용과 동일하지 않다.

## 💡 Insights & Impact

일관된 instance discovery와 prompt에 의한 선택을 분리하면 관측 순서에 덜 의존하는 segmentation을 구성할 수 있다.

- Estimated geometry로 만든 4D metric은 geometry 오류를 직접 검증하지 못한다.
- Agentic language 선택은 VLM 판단·frame 탐색 실패의 영향을 받는다.

## 🔗 Related Work

- [VGGT-Ω](../reconstruction/vggt-omega.md): geometry backbone.
- [IGGT4D](iggt4d.md): streaming geometry-instance 비교 모델.

## 📚 Key Takeaways

1. 먼저 instance를 찾고 prompt로 고른다.
2. Persistent query가 view와 시간을 연결한다.
3. Pseudo-3D 평가와 실제 geometry GT를 구분한다.

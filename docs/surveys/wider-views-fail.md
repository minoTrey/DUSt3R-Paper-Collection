# When Wider Views Fail: Stress-Testing Feed-Forward 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Daisy Li, Kyle Gao, Quanyun Wu, Hanna Chomko, John S. Zelek, Jonathan Li
- **Institution**: University of Waterloo, Aalto University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.24839)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.24839v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 같은 이미지 수에서도 카메라가 둘러보는 각도 범위를 넓히면 FF3D가 일관된 건물 대신 중복 형상을 만들 수 있다. 중복을 제거하지 않고 전체 예측을 한 번에 정렬해 실패를 측정한다.

## 🎯 Key Contributions

1. **Controlled View Span**: 두 도시 장면에서 이미지 수를 고정하고 관측 각도 범위를 바꾼다.
2. **Failure-Aware Alignment**: 여러 복제 건물을 따로 정렬하거나 지우지 않고 하나의 Sim(3)를 전체 예측에 적용한다.
3. **Reference-Bias Disclosure**: 평가 기준이 VGGT-Ω로 만든 pseudo-reference임을 명시한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Google Earth Studio로 만든 두 건물 장면의 orbit 이미지와 평가할 VGGT·π3X·VGGT-Ω.
- **Output**: 각 view span의 pointcloud 및 reference와의 distance·precision·recall·F-score.
- **Problem**: 짧은 궤적의 국소 정합이 좋아도 넓은 범위의 시점을 공동 처리하면 전역 형상이 붕괴할 수 있다. 부분별 정렬은 이 실패를 숨긴다.

### Method

1. 각 장면에서 서로 다른 angular span의 궤적을 만들고 각 궤적에서 같은 수의 이미지를 샘플링한다.
2. 전체 orbit의 더 많은 이미지로 VGGT-Ω pseudo-reference를 만들고 중심 건물을 수동 분리한다.
3. 예측의 모든 복제 형상을 남긴 채 coarse registration과 trimmed ICP로 하나의 similarity transform을 구한다.
4. Reference bounding-box diagonal로 거리를 정규화하고 동일 threshold의 surface precision·recall을 계산한다.

재학습한 새 복원기가 아니라 세 공개 모델의 stress test다. §3에서 각 궤적 10장, pseudo-reference 70장과 전체 42개 복원 case를 사용한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.24839v1), Table 1 and §3, PDF pp.2–3.

아래는 Toronto Scene I의 F-score(%)다. Surface threshold는 pseudo-reference bounding-box diagonal의 0.01이다. 정답 laser geometry에 대한 정확도 표가 아니라 학습 모델 reference와의 일치도를 측정한다.

| Model  | 30° Span F-score ↑ | 360° Span F-score ↑ |
| ------ | ------------------ | ------------------- |
| VGGT   | 77.47              | 23.69               |
| π3X    | 85.59              | 14.87               |
| VGGT-Ω | 81.03              | 86.05               |

π3X는 좁은 범위에서 좋지만 넓은 범위에서는 크게 악화된다. VGGT-Ω의 우위에는 같은 모델이 pseudo-reference를 만든 편향이 포함될 수 있다. Table 2의 다른 장면과 동일한 실제 정답 평가로 합치지 않는다.

## 💡 Insights & Impact

이미지 수만 늘리거나 줄이는 실험으로는 view span 변화의 실패를 충분히 이해하기 어렵다. 결과 점군의 복제·전역 붕괴를 포함해 평가해야 한다.

- 두 장면과 합성 capture에 한정된 stress test다. 실제 건물·센서·모든 장면에 대한 순위로 일반화할 수 없다.
- 수동 segmentation과 pseudo-reference가 결과에 영향을 준다. VGGT-Ω를 절대 ground truth로 해석하면 안 된다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md), [VGGT-Ω](../reconstruction/vggt-omega.md), [π³](../reconstruction/pi3.md): 관련 복원 모델 계열.
- [E3D-Bench](e3d-bench.md): 조건을 통제해 모델을 비교하는 평가 방향.

## 📚 Key Takeaways

1. 같은 입력 장수에서도 view span이 난도를 바꾼다.
2. 분리된 복제 형상을 제거하면 실패를 과소평가할 수 있다.
3. Pseudo-reference에 대한 일치도와 실제 기하 정확도를 구분한다.

# XPos3R: Cross-Modal Transformer for Intraoperative 2D/3D Registration (arXiv 2026)

## 📋 Overview

- **Authors**: Shiyan Su, Ruyi Zha, Hongdong Li, Xuelian Cheng, Zongyuan Ge
- **Institution**: Monash University, Australian National University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.10733)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.10733v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 2D X-ray와 3D CT를 비대칭 encoder·cross-attention으로 연결해 patient-specific 재학습 없이 초기 registration pose를 추정한다.

## 🎯 Key Contributions

1. 이미지·volume별 encoder를 가진 cross-modal geometry regression을 제시한다.
2. Anatomy-specific synthetic data로 대규모 학습한다.
3. Feed-forward pose와 선택적 differentiable TTO를 분리 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 수술 중 2D X-ray와 수술 전 3D CT volume.
- **Output**: CT와 X-ray camera 사이의 rigid registration pose.
- **Problem**: 환자마다 재학습하는 regression은 준비 시간이 필요하고 모달리티가 다른 영상의 feature 대응도 어렵다.

### Method

1. RayDINO로 X-ray를, 3D CNN으로 CT를 token화한다.
2. X-ray query가 CT key/value를 읽는 단방향 cross-attention을 적용한다.
3. Pooling한 image-centric feature에서 회전·이동을 회귀한다.
4. 선택적으로 DiffDRR intensity optimization으로 초기 pose를 보정한다.

합성 X-ray·volume 쌍으로 학습한 patient-agnostic 모델이다. 의료기기 배포나 임상 유효성을 입증한 실험으로 확대 해석하지 않는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.10733v1), Table 1, PDF p.9.

DeepFluoro, X-ray별 mean ± standard deviation. TRE·PE는 mm, Tintra는 초다. 두 행 모두 pretrained XPos3R이며 TTO 유무만 다르다.

| Configuration      | TRE (mm) ↓   | PE (mm) ↓    | Tintra (s) ↓ |
| ------------------ | ------------ | ------------ | ------------ |
| Feed-forward       | 24.16 ± 6.24 | 7.412 ± 3.11 | 1.52         |
| Feed-forward + TTO | 3.288 ± 8.31 | 0.448 ± 0.94 | 2.93         |

작은 registration error는 TTO를 포함한 결과다. 평균과 표준편차를 함께 보존해 실패 tail을 숨기지 않았다.

## 💡 Insights & Impact

DUSt3R에서 영감을 받은 geometry learning을 homogeneous RGB pair가 아닌 X-ray·CT 정합으로 옮긴다.

- Synthetic-to-real·해부학적 도메인 전이의 한계가 남는다.
- Benchmark 정확도는 임상 안전성·성공률을 직접 뜻하지 않는다.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): geometry regression의 개념적 배경이며 그대로 쓰는 RGB backbone은 아니다.
- [Endo3R](endo3r.md): 다른 의료 geometry 문제.

## 📚 Key Takeaways

1. 입력은 RGB pair가 아니라 X-ray와 CT다.
2. 환자별 재학습과 test-time 최적화는 다르다.
3. TTO 시간과 오차 분포를 함께 읽는다.

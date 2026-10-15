# SAMV-DUSt3R: Instance-Centric 3D Scene Decoupling from Sparse Multi-Views (arXiv 2026)

## 📋 Overview

- **Authors**: Langxu Zhao, Zuan Gu, Yingdan Zhang, Pengfei Zhao, Tianhan Gao
- **Institution**: Northeastern University, Shenyang
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.11279)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.11279v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: SAM2 target mask를 MV-DUSt3R의 attention에 넣고 reference view를 학습해 선택하여 장면에서 지정 object의 3D geometry를 분리한다.

## 🎯 Key Contributions

1. Mask feature로 reconstruction token을 안내한다.
2. Spatial RankGNN으로 reference view를 선택한다.
3. Object-centric confidence loss로 target pointmap을 학습한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse RGB view와 prompt에서 얻은 SAM2 object mask. Camera calibration은 요구하지 않는다.
- **Output**: 선택한 target instance의 pointmap·3D reconstruction.
- **Problem**: 장면 전체를 복원한 뒤 target을 잘라내면 물체 경계와 view별 정보가 충분히 활용되지 않는다.

### Method

1. Mask CNN feature를 token에 맞는 형태로 바꾼다.
2. Cross Flow Mask Block에서 geometry token이 mask feature에 attention한다.
3. SfM covisibility로 만든 ranking supervision으로 좋은 reference를 예측한다.
4. Target 영역의 pointmap·confidence를 학습하고 분리된 object를 후속 rendering에 사용한다.

RankGNN과 mask-guided geometry를 별도로 학습한다. NVS 평가는 출력 point cloud로 3DGS를 학습하므로 geometry network 한 번의 비용과 다르다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.11279v1), Table I, PDF p.5.

DTU, 4 input views 224×224. 원문은 CD·accuracy·completeness를 10배로 표시한다. 아래는 원문 표시값을 그대로 옮겼으며 원래 DTU 단위로 되돌리지 않았다.

| Method      | Displayed CD ↓ | Displayed Acc. ↓ | Displayed Comp. ↓ |
| ----------- | -------------- | ---------------- | ----------------- |
| MV-DUSt3R   | 4.3            | 9.9              | 9.4               |
| SAMV-DUSt3R | 2.4            | 6.2              | 6.3               |

원문의 SSIM·LPIPS도 별도 scaling이 있어 일반 0–1 표와 직접 비교하면 안 된다. Full-image NVS는 target 외 영역의 오차를 포함하므로 masked 결과와 다르다.

## 💡 Insights & Impact

Object mask를 사후 필터가 아니라 geometry를 만드는 과정의 조건으로 사용한다.

- SAM2 mask 품질과 대부분 view에 target이 보인다는 조건에 의존한다.
- Ranking accuracy의 tolerance 조건과 변환된 지표 scale을 보존해야 한다.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): pointmap 배경.
- [IGGT](iggt.md): instance geometry의 다른 접근.

## 📚 Key Takeaways

1. Target mask가 reconstruction attention을 안내한다.
2. Reference 선택도 학습한다.
3. 표의 scaling과 후속 3DGS 비용을 구분한다.

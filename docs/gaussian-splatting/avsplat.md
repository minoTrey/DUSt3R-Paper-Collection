# AVSplat: Dense-View Feed-Forward 3D Gaussian Splatting with Assist-View Preconditioning (arXiv 2026)

## 📋 Overview

- **Authors**: Muyu Xu, Fangneng Zhan, Yu Wei, Hanspeter Pfister, Shijian Lu
- **Institution**: Nanyang Technological University, Harvard University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.05925)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.05925v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 많은 입력 view에서 attention이 희석되는 문제를 assist-view 문맥으로 줄이고, crowded voxel의 Gaussian feature를 temperature-aware fusion한다.

## 🎯 Key Contributions

1. 관련성·다양성을 고려해 assist view를 고른다.
2. Global aggregation 전에 cached scene feature로 view를 precondition한다.
3. Occupancy·confidence에 따라 voxel fusion의 attribution을 조절한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 다수의 unposed RGB view.
- **Output**: Camera와 fused Gaussian scene, novel-view image.
- **Problem**: 더 많은 view를 넣어도 무관한 token과 voxel 평균화 때문에 rendering이 오히려 흐려질 수 있다.

### Method

1. 작은 assist-view 집합의 feature를 cache한다.
2. 각 입력 view가 이 문맥을 먼저 읽어 correspondence를 안정화한다.
3. VGGT-style global aggregation으로 geometry·Gaussian feature를 예측한다.
4. Voxel occupancy와 point confidence에 따른 temperature로 fusion weight를 조절한다.

AnySplat 계열을 확장하여 DL3DV로 학습한다. Assist view는 새로 생성한 이미지가 아니라 입력 중 선택한 문맥이다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.05925v1), Table 1, PDF p.10.

DL3DV dense input NVS. PSNR·SSIM은 높을수록 좋다. 동일 view 수끼리 비교한다.

| Views | Method   | PSNR ↑ | SSIM ↑ |
| ----- | -------- | ------ | ------ |
| 32    | AnySplat | 21.05  | 0.680  |
| 32    | AVSplat  | 21.54  | 0.710  |
| 64    | AnySplat | 21.14  | 0.684  |
| 64    | AVSplat  | 21.67  | 0.717  |

Sparse 3-view DL3DV PSNR은 AVSplat이 더 낮고 다른 dataset의 모든 metric도 단조 개선하지는 않는다. Positive view scaling은 지정 실험에서의 경향이다.

## 💡 Insights & Impact

입력 view 수를 늘리는 것과 각 view의 관련 문맥을 보존하는 것은 다른 문제다.

- Assist-view 선택이 실패하면 correspondence를 잘못 안내할 수 있다.
- 더 많은 view의 전체 계산·memory 비용을 함께 고려해야 한다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): geometry aggregation 배경.
- [DensiTok](densitok.md): 실제 입력 view 문맥 대신 미관측 token을 생성하는 다른 접근.

## 📚 Key Takeaways

1. 입력 중 유용한 view를 먼저 문맥으로 읽는다.
2. Dense voxel 평균을 adaptive하게 만든다.
3. View scaling과 단일 조건의 최고 점수를 구분한다.

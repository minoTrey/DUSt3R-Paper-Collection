# GroupForward: Building Referable 3D Scenes via Instance-Grouped Feed-Forward Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Qijian Tian, Zimeng Wu, Xuhong Wang, Lizhuang Ma, Xin Tan
- **Institution**: Shanghai Jiao Tong University, Beihang University, Shanghai Artificial Intelligence Laboratory, East China Normal University
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.17535)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.17535v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Gaussian마다 큰 semantic feature를 저장하는 대신 instance embedding으로 3D object를 묶고, group별 의미와 관계를 이용해 언어 지시를 해석한다.

## 🎯 Key Contributions

1. Geometry·appearance·instance embedding을 feed-forward로 예측한다.
2. Instance prototype으로 semantic feature를 집계한다.
3. 3D scene graph와 VLM을 연결한 referential reasoning을 구성한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse unposed·uncalibrated RGB view; 지시 작업에서는 referring expression도 입력한다.
- **Output**: Instance-grouped Gaussian scene, semantic rendering, 지시한 object의 3D group·mask.
- **Problem**: 같은 종류의 여러 object를 category feature만으로 구분하기 어렵고 Gaussian별 고차원 semantics는 비싸다.

### Method

1. Shared encoder 뒤 geometry decoder와 Gaussian decoder로 camera·depth·primitive를 예측한다.
2. Compact instance embedding으로 view 간 Gaussian을 clustering한다.
3. 입력 view의 open-vocabulary feature를 group별 prototype으로 모은다.
4. Scene graph에서 후보를 검색하고 VLM이 구조·외형·관계를 함께 읽어 목표 group을 고른다.

Gauge-aligned self-rendering과 rendering-consistent instance learning을 단계적으로 학습한다. VLM reasoning은 reconstruction network의 한 head와 동일한 작업이 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.17535v1), Table II, PDF p.7.

ScanNet novel-view semantic segmentation·NVS, 4 input views. mIoU와 PSNR은 높을수록 좋다.

| Method       | mIoU ↑ | PSNR ↑ |
| ------------ | ------ | ------ |
| Uni3R        | 0.5443 | 25.32  |
| GroupForward | 0.5868 | 27.14  |

이 표는 category segmentation·rendering이며 referring-expression 성공률은 별도 Table IV다. Semantic model 교체에 따라 성능도 달라진다.

## 💡 Insights & Impact

지시 가능한 scene의 기본 단위를 pixel이나 category가 아니라 지속적인 3D instance로 만든다.

- Clustering 오류가 semantics와 지시 결과에 전파된다.
- VLM·semantic feature 모델의 오류와 추가 비용이 남는다.

## 🔗 Related Work

- [IGGT](iggt.md): instance-grounded geometry 배경.
- [Splatt3R](../gaussian-splatting/splatt3r.md): feed-forward Gaussian 배경.

## 📚 Key Takeaways

1. Compact embedding으로 Gaussian을 object별로 묶는다.
2. Semantics를 instance 단위로 전달한다.
3. Segmentation과 지시 이해의 평가를 구분한다.

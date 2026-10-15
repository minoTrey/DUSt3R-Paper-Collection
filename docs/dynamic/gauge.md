# GAUGE: Group-Wise View-Inconsistency Rectification for Feed-Forward 4D Tracking (arXiv 2026)

## 📋 Overview

- **Authors**: Zhuoqian Feng, Weixing Chen, Ziliang Chen, Yang Liu, Liang Lin
- **Institution**: Sun Yat-sen University, Pengcheng Laboratory, X-Era AI Lab
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.32596)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.32596v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 3D tracking의 잔여 오차를 motion group별 radial scale·translation으로 보정한다. 학습은 없지만 sparse metric anchor와 camera center가 추가 입력이다.

## 🎯 Key Contributions

1. 전역 정렬 뒤에도 남는 group별 view inconsistency를 분석한다.
2. Displacement direction·공간 연결성으로 motion group을 만든다.
3. 적은 metric anchor로 group별 보정량을 구한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 이미 예측·전역 정렬된 3D trajectory·visibility, camera center와 sparse GT 3D anchor.
- **Output**: 보정한 3D point trajectory.
- **Problem**: 서로 다른 동적 object는 다른 radial bias를 가져 단일 global scale로 모두 고칠 수 없다.

### Method

1. 점의 displacement direction과 공간 이웃으로 group을 분리한다.
2. Anchor와 예측 거리의 robust ratio로 radial scale을 구한다.
3. Camera center를 기준으로 frame별 scale을 적용하고 group translation을 보정한다.
4. Degenerate group에는 별도 center·fallback을 쓰고 불안정한 보정은 남겨둔다.

Tracker weight는 바꾸지 않는다. Training-free는 RGB만으로 self-supervised metric 보정한다는 뜻이 아니다. 평가 camera center는 GT extrinsics에서 얻는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.32596v1), Table 2, PDF p.7.

PointOdyssey, 기본 anchor budget 5%. DQS는 dynamic query screening, Full은 첫 frame visible 전체 query다. D4RT는 공개 reimplementation을 평가했다.

| D4RT configuration | DQS EPE ↓ | Full EPE ↓ |
| ------------------ | --------- | ---------- |
| Base               | 0.1812    | 0.1930     |
| + GAUGE            | 0.1269    | 0.1597     |

다른 tracker의 Full 조건에서는 오차나 AJ가 악화되기도 한다. Dynamic group의 개선을 static background 전체에 일반화하지 않는다.

## 💡 Insights & Impact

2D 관측이 약하게 구속하는 radial 방향에 보정 자유도를 제한해 sparse anchor를 효율적으로 사용한다.

- Metric anchor와 camera 정보의 추가 비용·가용성을 전제로 한다.
- Motion grouping·저시차·static group의 모델 가정이 실패할 수 있다.

## 🔗 Related Work

- [D4RT](d4rt.md), [V-DPM](v-dpm.md): 보정 대상 tracker 계열.
- [Uni4R](uni4r.md): continuous motion 자체를 학습하는 접근.

## 📚 Key Takeaways

1. Post-hoc 보정이며 tracker 학습이 아니다.
2. GT anchor·camera 입력을 숨기지 않는다.
3. Dynamic·전체 query protocol을 구분한다.

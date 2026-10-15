# Scal3R: Learning Efficient Multi-Relative Pose Query for Scalable Online 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Chin-Yang Lin, Yang-Che Sun, Cheng Sun, Fu-En Yang, Min-Hung Chen, Yen-Yu Lin, Wei-Chen Chiu, Yu-Lun Liu
- **Institution**: National Yang Ming Chiao Tung University, NVIDIA
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.04201)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.04201v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 고정 첫 프레임 기준의 전역 pose 대신 여러 reference에 대한 상대 pose를 query하여 긴 영상의 drift를 줄인다.

## 🎯 Key Contributions

1. Frozen backbone에 상대 pose query를 추가한다.
2. Image token이 query token을 보지 않는 비대칭 attention을 사용한다.
3. 여러 상대 제약을 online pose graph와 loop closure로 통합한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Intrinsics 없는 RGB 영상과 저장된 reference token.
- **Output**: 전역 연결된 카메라 pose와 backbone의 pointmap.
- **Problem**: 학습 범위를 벗어난 긴 이동에서 전역 pose head는 무너져도 지역 depth는 비교적 안정적일 수 있다.

### Method

1. CUT3R 또는 STream3R backbone을 고정한다.
2. Query token은 image feature를 읽되 image의 key/value 표현에는 들어가지 않게 한다.
3. 각 token이 현재 frame에서 한 reference로의 상대 회전·이동을 예측한다.
4. Keyframe buffer의 다중 reference 제약과 loop edge를 pose graph에서 최적화한다.

TartanAir의 4-view sample로 query·head를 학습한다. 야외 실험에는 streaming state reset도 사용하므로 query만 추가한 결과로 해석하면 안 된다. 2604.08542의 동명 Scal3R와 저자·방법이 다르다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.04201v1), Table 1, PDF p.10.

KITTI calibration-free RGB-only 평가의 평균 ATE. 표의 단위는 m이며 낮을수록 좋다. 실패·OOM이 있는 방법의 평균은 완료 sequence만의 값일 수 있다.

| Method            | Mean ATE (m) ↓ |
| ----------------- | -------------- |
| CUT3R             | 207.2          |
| TTT3R             | 182.2          |
| Scal3R (CUT3R)    | 69.7           |
| Scal3R (STream3R) | 70.8           |

원문의 추가 비교에서는 LongStream이 더 낮은 ATE를 얻는다. 이 결과를 절대적인 모든 방법의 최고 성능이라고 요약하지 않는다.

## 💡 Insights & Impact

긴 궤적 전체를 한 번에 회귀하기보다 backbone의 지역 geometry를 보존하며 상대 제약을 추출한다.

- 추가 query 학습과 pose graph 최적화가 필요하다.
- Reference 선택과 loop closure 오류는 전역 결과에 영향을 준다.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md): frozen streaming backbone.
- [Scal3R (2604.08542)](scal3r.md): 별개의 동명 논문.

## 📚 Key Takeaways

1. 동명 논문을 arXiv ID로 구분한다.
2. Image geometry를 보존하면서 상대 pose만 학습한다.
3. 전역 일관성은 pose graph가 담당한다.

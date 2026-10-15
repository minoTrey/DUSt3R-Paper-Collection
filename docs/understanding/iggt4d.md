# IGGT4D: Streaming 4D Instance-Grounded Geometry Transformer (arXiv 2026)

## 📋 Overview

- **Authors**: Zhengyu Zou, Hao Li, Kuixuan Jiao, Liu Liu, Tingyang Xiao, Xiaolin Zhou, Fangzhou Hong, Zhizhong Su, Dingwen Zhang, Ziwei Liu
- **Institution**: Horizon Robotics, Nanyang Technological University, Institute of Artificial Intelligence Hefei Comprehensive National Science Center
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.19228)
- **Verification**: UNKNOWN (2026-10-15; 원문 2607.19228v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: DA3를 causal streaming 모델로 확장하고 depth·ray·instance feature를 함께 예측해 움직이는 장면의 geometry와 object identity를 유지한다.

## 🎯 Key Contributions

1. Geometry와 instance를 공동 예측하는 causal Transformer를 구성한다.
2. Streaming instance codebook으로 frame 사이 object ID를 연결한다.
3. Geometry·pose·시간 일관 mask를 갖춘 InsScene4D 학습 자료를 구축한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간순 RGB frame과 선택적 camera pose.
- **Output**: Camera motion, depth·ray geometry, 시간적으로 연결한 instance mask·embedding.
- **Problem**: Geometry만 유지하는 streaming 모델은 같은 object가 이동·가림·재등장할 때 identity를 놓친다.

### Method

1. DA3의 view attention에 causal mask를 적용한다.
2. Camera·cross-view KV cache로 과거 문맥을 재사용한다.
3. Tri-DPT가 depth·ray·instance feature를 geometry-aware attention으로 함께 해독한다.
4. Frame 내부 mask를 clustering한 뒤 global codebook과 연결하고 feature center를 면적 가중치로 갱신한다.

Geometry와 temporally consistent instance supervision으로 학습한다. GT pose를 넣는 실험과 예측 pose만 쓰는 실험을 분리해야 한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2607.19228v1), Table 1, PDF p.7.

DA3 protocol, HiRoom·ETH3D·7Scenes·ScanNet++ 평균. 아래 F1은 predicted poses(w/o p.) 조건이며 높을수록 좋다.

| Method      | Processing | Pose AUC@30 ↑ | Reconstruction F1 ↑ |
| ----------- | ---------- | ------------- | ------------------- |
| LingBot-Map | Streaming  | 0.8647        | 0.5228              |
| IGGT4D      | Streaming  | 0.8924        | 0.6678              |
| DA3         | Offline    | 0.9352        | 0.7430              |

Streaming 비교에서는 개선하지만 offline DA3보다 모든 평균이 높은 것은 아니다. GT-pose 조건은 일부 모델에 추론 입력으로도 pose를 제공한다.

## 💡 Insights & Impact

시간 일관 instance representation을 geometry와 함께 갱신하면 단순한 frame별 segmentation을 넘어선다.

- Codebook association이 반복 object·재등장에서 틀릴 수 있다.
- Causal 처리와 offline full attention은 미래 정보 이용 조건이 다르다.

## 🔗 Related Work

- [IGGT](iggt.md): instance-grounded geometry 배경.
- [Depth Anything 3](../reconstruction/depth-anything-3.md): 기반 모델.

## 📚 Key Takeaways

1. 영상의 geometry와 object identity를 함께 출력한다.
2. 과거 cache와 codebook의 역할은 다르다.
3. Predicted/GT pose와 online/offline 조건을 분리한다.

# LG-VLN: A Zero-Shot Vision-and-Language Navigation Framework with LangGraph State Orchestration (arXiv 2026)

## 📋 Overview

- **Authors**: Jianhe Zhao, Yanhua Qiu, Zhiyu Zhang, Zibo Zhao, Jinhua Xie
- **Institution**: Wuhan University; Huazhong University of Science and Technology
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.15098)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.15098v1 방법·표·소속 검토, 독립 게재 근거 미확인; 다른 제목·저자의 Crossref 후보는 배제)
- **TL;DR**: 단안 RGB와 언어 지시에서 VGGT 기하·CleanDIFT 대응 특징을 함께 사용해 지도와 pose를 갱신하고, LangGraph 상태 전이로 이동·회전·정지 및 실패 복구를 실행한다.

## 🎯 Key Contributions

1. VGGT의 기하 confidence와 CleanDIFT의 의미 유사도로 프레임 간 대응점을 거른 뒤 Sim(3) 정합으로 지도와 pose를 갱신한다.
2. 같은 CleanDIFT 특징을 언어 조건의 semantic value map에도 사용한다.
3. 지시 해석·지각·지도·계획·행동·복구를 지속 상태를 공유하는 LangGraph 실행 그래프로 연결한다.

새로운 geometry backbone을 학습한 논문이 아니라, 기존 백본 위의 정합·지도화·navigation 응용이다.
기하 입력 ablation과 pose 오차 평가가 있으므로 단순한 외부 도구 호출로만 분류해서는 안 된다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간순 단안 RGB 관측, 자연어 이동 지시, metric 초기화를 위한 알려진 카메라 설치 높이.
- **Output**: 이동·좌회전·우회전·정지 행동. 내부 상태로 pose, 누적 point cloud, 점유·통과 가능성·의미 value map을 유지한다.
- **Problem**: 별개의 기하·의미 표현은 프레임 간 대응과 목표 위치의 일관성을 잃기 쉽다. 긴 지시에서는 잘못된 탐지·정체·계획 실패를 추적하고 복구해야 한다.

### Geometry and Shared Features

1. VGGT가 RGB에서 상대 깊이·pointmap·confidence를 예측한다. 초기 회전 관측에서 바닥 평면을 맞추고 알려진 카메라 높이와 비교해 공통 scale을 정한다 (§3.4.1, Appendix A.3).
2. 인접 프레임의 후보 대응점에서 CleanDIFT cosine similarity와 VGGT confidence가 낮은 쌍을 제거한다 (§3.4.2).
3. RANSAC 초기값 뒤 confidence·의미 유사도 가중 robust objective로 Sim(3)를 보정한다. Scale 변화에는 제한을 두고, 정합이 실패한 프레임은 지도 융합에서 제외한다 (§3.4.3).
4. 같은 CleanDIFT 특징의 목표 reference 유사도와 BLIP-2의 image–text relevance를 결합해 semantic value를 만든다. 이력을 추정 pose로 재투영하고 world-aligned bird's-eye-view 지도에 누적한다 (§3.6–3.7).

Pointmap을 바로 행동으로 바꾸는 단일 forward 모델이 아니다. 사전학습 모델 추론, 대응점 필터링, robust 정합, 지도 갱신과 계획을 결합한다.

### Navigation and Training Scope

LangGraph는 현재 하위 지시·pose·지도·행동 이력·복구 상태를 유지하고 조건에 따라 실행 경로를 바꾼다.
Grounding DINO와 SAM2는 목표 영역을 찾고, semantic waypoint를 고른 뒤 FMM이 지역 경로를 계산한다.
Zero-shot은 R2R-CE 학습 split으로 navigation 정책을 학습하거나 task-specific fine-tuning하지 않았다는 뜻이다.
사용하는 시각·언어 백본은 이미 사전학습되어 있다 (§4.1).

## 📊 Results

**Source**: [arXiv 2609.15098v1 PDF](https://arxiv.org/pdf/2609.15098v1), Tables 3–4 (PDF p.15), Table 6 (p.17), Table 7 (p.19).

### Geometry Inputs and Navigation

Habitat-Sim / Matterport3D의 R2R-CE val-unseen에서 장면별로 선택한 고정 550 episode subset이다.
초기 scale 회전 관측은 행동 예산과 평가 궤적에서 제외한다. 이후 150 low-level actions를 사용하며 성공 거리 기준은 3.0m다 (§4.1).
동일 semantic·planning 모듈에서 기하 입력만 바꾼 Table 3이다. SR·SPL은 %, NE는 m다.

| Geometry setting | Depth          | Pose      | SR ↑ | SPL ↑ | NE (m) ↓ |
| ---------------- | -------------- | --------- | ---- | ----- | -------- |
| Oracle           | GT             | GT        | 24.9 | 17.7  | 6.80     |
| Hybrid           | VGGT predicted | GT        | 24.2 | 15.2  | 7.04     |
| LG-VLN           | Predicted      | Predicted | 21.3 | 12.1  | 7.85     |

GT depth·pose는 Oracle/Hybrid 진단 조건에만 해당한다. 기본 navigation은 이를 입력받지 않지만 알려진 카메라 높이와 초기 관측 절차에 의존한다.

### Pose Registration

같은 subset의 Table 7. ATE는 GT 궤적과 Sim(3) 정렬한 뒤의 위치 RMSE이며 RTE는 연속 프레임의 상대 translation RMSE다.
각 episode의 RMSE를 평균한다. CleanDIFT 외 기하 RANSAC 정합 조건을 맞춘 비교다 (§4.7).

| Correspondence filtering | ATE RMSE (m) ↓ | RTE RMSE (m) ↓ |
| ------------------------ | -------------- | -------------- |
| Without CleanDIFT        | 0.322          | 0.150          |
| With CleanDIFT           | 0.318          | 0.092          |

지역 상대 이동 오차는 줄지만 ATE 변화는 작다. 이 표를 전역 drift 해결이나 모든 기하 task의 개선으로 일반화하지 않는다.

### Scale and Runtime Limits

Table 6의 valid GT pixels에서 프레임별 AbsRel을 계산하고 프레임 평균·중앙값을 모았다.
고정 초기 scale은 실제 navigation 조건이며, 프레임별 median alignment는 GT를 쓰는 사후 진단이다.

| AbsRel aggregation | Fixed initial scale ↓ | Per-frame GT median alignment ↓ |
| ------------------ | --------------------- | ------------------------------- |
| Mean               | 0.5874                | 0.0493                          |
| Median             | 0.2643                | 0.0319                          |

사후 정렬 열을 배포 시 metric depth 정확도로 사용하면 안 된다. 고정 scale 오차가 여전히 크다.

Table 4의 모듈별 call 시간. NVIDIA RTX 5090, Intel Xeon Platinum 8470Q, Ubuntu 22.04 환경이다 (§4.1, §4.4).
아래 값은 end-to-end FPS가 아니며 event-driven semantic 호출 주기와 후보 수가 다르다.

| Module                | Time per call (ms) | Invocation                              |
| --------------------- | ------------------ | --------------------------------------- |
| VGGT                  | 178                | Every frame                             |
| CleanDIFT             | 179                | Every frame                             |
| Grounding DINO + SAM2 | 602                | Semantic update triggered               |
| BLIP-2 ITM            | 52–72              | Per short-text candidate when triggered |
| GTM + FMM             | 86                 | Map fusion and local planning           |

## 💡 Insights & Impact

이 논문은 언어 navigation이 geometry의 소비자일 뿐 아니라, 의미 특징으로 대응점을 거르고 pose 오차를 평가하는 직접 응용임을 보여준다.
Topometric localization이나 물성 head 응용과 마찬가지로 백본 개선과 응용 계층의 기여를 구분해 읽는다.

- 전체 R2R-CE split이나 실제 로봇의 결과가 아닌 고정 simulation subset이다. 초기 회전·scale calibration의 비용도 navigation 평가에서 빠진다.
- 알려진 카메라 높이, 관측 가능한 바닥과 안정적인 ground-plane fitting에 의존한다. 단안 RGB만으로 절대 scale이 자동 결정되는 것은 아니다.
- Table 2의 CleanDIFT 제거는 value-map 신호 제거이며 geometry filtering 전체 제거와 다르다. Pose filtering 효과는 Table 7에서 별도로 본다.
- 단일 실행의 SR 차이로 강한 통계적 결론을 내릴 수 없다는 원문 한계가 있다 (PDF p.20). Sim(3) 정렬 ATE도 절대 metric scale 정확도를 보장하지 않는다.
- LangGraph의 독립 효과를 이 요약의 기하 ablation만으로 입증할 수 없다. 실험을 재현하지 않았다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): 사용한 geometry backbone.
- [VGGT-SLAM](../reconstruction/vggt-slam.md): 원문이 참조하는 dense RGB SLAM·Sim(3) backend 맥락.
- [Topometric FF3D localization](../pose/topometric-ff3d.md): 학습 기하를 localization에 결합하는 다른 직접 응용.
- [PhysVGGT](../understanding/physvggt.md): geometry feature에서 downstream 예측 head를 학습하는 응용.

## 📚 Key Takeaways

1. 입력은 RGB·언어·카메라 높이이며 출력은 행동과 지속 지도 상태다.
2. VGGT 예측에 CleanDIFT 대응 필터·robust Sim(3) 정합을 추가한다.
3. 지역 pose 개선, 고정 scale의 한계, 초기 관측 제외 조건을 함께 읽는다.

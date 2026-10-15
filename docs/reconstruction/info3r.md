# Info3R: Information-Adaptive Test-Time Training for 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Sunghyun Baek, Hanna Bae, Minchan Kwon, Junmo Kim
- **Institution**: Korea Advanced Institute of Science and Technology (KAIST)
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.21938)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.21938v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 재귀 3D 모델의 상태를 매 프레임 같은 강도로 갱신하지 않는다. 새 정보량으로 update를 조절하고 포화한 상태를 reset한 뒤 좌표계를 다시 연결한다.

## 🎯 Key Contributions

1. **Information-Aware Update**: 반복적인 프레임과 새로운 관측에 다른 상태 갱신 강도를 준다.
2. **Dynamic State Reset**: 누적 update와 confidence를 보고 상태의 새 정보 수용 능력을 회복한다.
3. **Anchor-to-World Alignment**: reset으로 바뀐 기준 좌표계를 기존 world에 연결한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간순 RGB 영상과 학습된 streaming reconstruction 모델.
- **Output**: 프레임별 camera pose·depth·pointmap과 연결된 장면. 미래 프레임 없이 상태를 순차 갱신한다.
- **Problem**: 긴 영상에서 내부 상태가 반복 관측에 소모되거나 포화하면 새로운 장면을 수용하기 어렵다. 무조건 reset하면 새 예측의 좌표계가 기존 지도와 끊어진다.

### Method

1. 현재 프레임의 redundancy와 정보량을 평가해 test-time state update의 강도를 바꾼다.
2. 누적 상태 변화와 예측 confidence를 함께 사용해 reset 시점을 정한다.
3. Reset 전후의 anchor 관계를 world 좌표계에 맞춰 이전 pointmap과 새 pointmap을 연결한다.
4. 동일한 재귀 복원 경로에서 pose·depth·점군을 평가한다. 상태 update와 네트워크 사전학습을 구분한다.

원문 §III–IV의 구현은 CUT3R 기반이며 TTT3R의 긴 시퀀스 구성 프로토콜을 따른다. 단일 RTX 4090에서 평가한 설정이다. 다른 백본에 같은 효과가 난다고 일반화하지 않는다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.21938v1), Tables II–III, PDF p.5.

아래 pose 표는 TUM·ScanNet의 1,000프레임 조건이다. ATE는 궤적 오차이고 RPE trans/rot는 상대 이동·회전 오차다. 원문 표의 수치를 유지하며 이 표에 명시하지 않은 거리 단위를 추정해 붙이지 않았다.

| Dataset | Method | ATE ↓ | RPE trans ↓ | RPE rot ↓ |
| ------- | ------ | ----- | ----------- | --------- |
| TUM     | TTT3R  | 0.117 | 0.010       | 0.480     |
| TUM     | Info3R | 0.061 | 0.011       | 0.508     |
| ScanNet | TTT3R  | 0.394 | 0.039       | 1.162     |
| ScanNet | Info3R | 0.176 | 0.023       | 0.595     |

TUM에서는 ATE가 좋아져도 두 RPE가 모두 좋아지지는 않는다. Table III의 KITTI 50프레임 AbsRel도 TTT3R 0.105, Info3R 0.115로 악화된다. 긴 시퀀스 개선을 모든 길이·지표의 우위로 읽지 않는다.

## 💡 Insights & Impact

정보를 더 많이 저장하는 것과 현재 상태가 새 관측을 학습할 수 있는지는 다른 문제다. 상태 선택·reset·기하 정렬을 함께 설계해 긴 시퀀스의 붕괴를 줄이려 한다.

- Reset trigger와 anchor 정렬이 불안정하면 전역 일관성에 영향을 준다.
- 상대 pose·깊이·전역 궤적은 다른 지표이며, ATE 개선만으로 전체 재구성 품질을 보장하지 않는다.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md): 재귀 기하 모델의 기반.
- [TTT3R](ttt3r.md): test-time state 학습의 직접 비교 대상.
- [Slot3R](slot3r.md): 저장·읽기 구조를 바꾸는 다른 streaming 접근.

## 📚 Key Takeaways

1. 반복적인 프레임과 새로운 프레임에 다른 update를 준다.
2. 상태 reset에는 좌표계 재연결이 필요하다.
3. 길이별·지표별 결과와 악화 조건을 함께 본다.

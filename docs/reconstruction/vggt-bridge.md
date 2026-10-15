# VGGT-Bridge: Beyond Sequential Pose Graphs via Coarse-Stride Skip Edges (ACCV 2026)

## 📋 Overview

- **Authors**: Sungjae Choi, Hanna Bae, Sunghyun Baek, Junmo Kim
- **Institution**: KAIST
- **Venue**: ACCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2610.06594)
- **Verification**: LIKELY (2026-10-15; arXiv comment의 Accepted to ACCV 2026, 독립 proceedings 확인 전)
- **TL;DR**: 고정된 VGGT로 긴 영상을 나누어 복원한 뒤, 듬성듬성 뽑은 프레임 묶음으로 먼 구간을 직접 연결한다. 일부 묶음을 역순으로 처리해 누적 축척 편향을 보정한다.

## 🎯 Key Contributions

1. **Coarse-Stride Skip Edges**: 인접 구간뿐 아니라 멀리 떨어진 구간 사이에도 제약을 만든다.
2. **Reverse Anchoring**: 일부 coarse chunk의 입력 순서를 뒤집어 첫 프레임 기준의 축척 편향을 반대 방향으로 만든다.
3. **Loop-Aware Policy**: 이미 재방문 연결이 있는 구간에서는 역순 제약과 기존 연결이 충돌하지 않도록 방향을 선택한다.
4. **Training-Free Graph Extension**: VGGT를 재학습하지 않는다. 후처리 pose graph 최적화는 여전히 수행한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 긴 RGB 영상. 카메라 내부 파라미터를 입력하지 않는 조건을 평가한다.
- **Output**: 공통 좌표계로 정렬한 카메라 궤적과 밀집 3D 재구성.
- **Chunk**: 한 번에 VGGT에 넣는 프레임 묶음이다. Fine chunk는 연속 프레임, coarse chunk는 일정 간격으로 뽑은 프레임이다.
- **Problem**: 인접 묶음만 연결하면 작은 정렬 오차가 긴 궤적을 따라 누적된다. 실제 재방문이 없는 구간에는 loop closure가 없다.

### Graph Construction

```text
연속 프레임 묶음 → VGGT → 인접 구간 연결
넓은 범위의 샘플 묶음 → 같은 VGGT → 먼 구간의 skip edge
기존 loop edge + 인접 edge + skip edge → Sim(3) pose graph 최적화
```

§3의 절차는 다음과 같다.

1. Fine·coarse chunk에 공통으로 포함된 프레임의 점군을 Sim(3)로 정렬한다. Sim(3)는 회전·이동·축척을 포함한다.
2. 하나의 coarse chunk가 겹치는 fine chunk 중 가장 멀리 떨어진 두 구간을 직접 연결한다.
3. Loop가 적은 구간의 선택된 coarse chunk는 프레임 역순으로 추론한다. 출력은 원래 시간순으로 되돌려 정렬한다.
4. Loop가 많은 구간은 정순을 유지한다. 모든 연결을 Cauchy 잔차 가중치가 있는 pose graph에서 함께 최적화한다.

KITTI·Virtual KITTI는 chunk 크기 75와 겹침 30, Waymo는 60과 24를 사용한다 (§4.1).
Coarse stride는 3과 5이며, 적응적 순서 선택은 stride 3에 적용한다.
역순 처리와 전체 그래프 최적화를 포함하므로 인과적 스트리밍 모델로 분류하지 않는다.

## 📊 Results

### Trajectory Accuracy

[arXiv v1 PDF](https://arxiv.org/pdf/2610.06594v1), Tables 1–3, PDF pp.9–10.
지표는 정답 궤적에 Sim(3) Umeyama 정렬한 **이동 ATE RMSE (m)**다.
SwiftVGGT의 별도 full-transformation 지표와 혼합하지 않는다 (§4.1).
SwiftVGGT와 VGGT-Bridge는 동일한 VGGT 체크포인트·chunk 구성으로 비교한다.

| Dataset / Evaluation Set                        | SwiftVGGT ATE ↓ | VGGT-Bridge ATE ↓ | Source  |
| ----------------------------------------------- | --------------- | ----------------- | ------- |
| KITTI Odometry, 00–10 평균                      | 31.53           | 22.61             | Table 1 |
| Waymo Open, 선택한 9개 segment 평균             | 1.557           | 1.401             | Table 2 |
| Virtual KITTI, 5개 scene·6개 appearance variant | 2.495           | 2.027             | Table 3 |

평균 개선이 모든 시퀀스의 개선을 뜻하지는 않는다.
KITTI 00에서는 SwiftVGGT가 9.92 m, VGGT-Bridge가 13.74 m다 (Table 1).
전체 Waymo 데이터셋에 대한 결과로 확대 해석하지 않는다.

### Efficiency

Table 6, PDF p.13. 단일 RTX 4090에서 KITTI Odometry 전체 처리 시간을 비교한다 (§4.1).

| Method      | Total Time (s) ↓ | FPS ↑ | Mean ATE (m) ↓ |
| ----------- | ---------------- | ----- | -------------- |
| VGGT-Long   | 7,611            | 3.0   | 24.85          |
| SwiftVGGT   | 2,583            | 9.0   | 31.53          |
| VGGT-Bridge | 3,883            | 6.0   | 22.61          |

추가 coarse 추론 때문에 SwiftVGGT보다 느리다. 이 시간은 재학습 비용이 아니라 재구성과 정렬 비용이다.

## 💡 Insights & Impact

이 방법은 네트워크의 영상 이해 능력을 바꾸기보다, 지역 예측을 연결하는 구조를 바꾼다.
실제로 같은 장소를 재방문하지 않아도 넓은 범위의 겹침 관측으로 먼 구간을 제약한다.

보정은 VGGT의 첫 프레임 축척 편향과 coarse·fine 구간의 정렬 품질에 의존한다.
Appendix J는 VGGT의 큰 예측 오류와 loop 검출 실패가 skip edge에 전파될 수 있다고 밝힌다.
주로 정적 장면을 가정하며, 주요 평가는 주행 장면이다. 다른 센서·실내·동적 장면에 대한 보장은 아니다.

## 🔗 Related Work

- **[VGGT](vggt.md)**: 지역 카메라·깊이·점군을 제공하는 고정 모델이다.
- **[VGGT-Long](vggt-long.md)**: 긴 영상을 겹치는 묶음으로 나누고 loop closure로 정렬하는 선행 방법이다.
- **SwiftVGGT**: 단일 SVD 정렬과 내부 특징 기반 loop detection을 사용하는 직접 비교 기반이다. 별도 문서는 아직 없다.
- **[VGGT-SLAM](vggt-slam.md)**: 학습한 시각 기하와 그래프 제약을 결합하는 관련 계열이다.
- **[Slot3R](slot3r.md)**: 추론 메모리를 바꾸는 접근이다. VGGT-Bridge는 묶음 사이의 그래프를 바꾼다.

## 📚 Key Takeaways

1. 긴 영상에서는 지역 재구성뿐 아니라 연결 그래프가 누적 오차를 좌우한다.
2. 입력 순서의 편향은 보정 신호로 사용할 수 있지만 loop 조건에 맞춰 적용해야 한다.
3. 추가 연결은 비용이 든다. 정확도 개선과 처리 시간을 함께 비교한다.
4. 학습 없이 적용하더라도 그래프 최적화가 필요한 전체 파이프라인이다.

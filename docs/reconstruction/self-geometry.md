# Self-Geometry: GT-Free and Plug-and-Play Test-Time Adaptation for Geometrically Consistent 3D Vision Foundation Models (arXiv 2026)

## 📋 Overview

- **Authors**: Seokhyun Youn, Dahyeon Kye, Sung-Ho Bae, Jihyong Oh
- **Institution**: Chung-Ang University, Kyung Hee University
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.10708)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.10708v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 테스트 장면의 2D 대응을 정답 대신 사용해 고정된 3D 모델의 LoRA만 적응시킨다. 깊이와 pose의 reprojection 제약에 깊이 독립적인 epipolar 제약을 더한다.

## 🎯 Key Contributions

1. **Explicit Geometry TTA**: 출력끼리의 자기일치에만 의존하지 않고 외부 2D matcher의 대응을 supervision으로 쓴다.
2. **Gradient Disentanglement**: pose와 depth를 함께 바꾸는 제약과 pose만 바꾸는 제약의 gradient 충돌을 줄인다.
3. **Angular Sampling**: 회전 거리로 다양한 관측을 선택해 전체 view 집합을 매번 처리하는 비용을 줄인다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 같은 장면의 RGB 이미지 집합과 기학습 VGGT·π³·DA3 중 하나. 정답 pose·depth는 적응 입력이 아니다.
- **Output**: 장면에 적응한 camera pose·depth·pointmap. 초기 모델 추론 외에 장면별 최적화가 필요하다.
- **Problem**: 예측된 pointmap끼리만 맞추면 초기 오답이 서로 일치할 수 있다. Reprojection 하나만으로는 pose와 depth의 여러 조합을 구별하기 어렵다.

### Method

1. 외부 matcher로 2D pseudo-correspondence를 얻고 epipolar·multi-view 잔차로 오대응을 거른다.
2. Multi-View Consistency는 source depth와 pose로 역투영한 점이 target 대응 픽셀에 도달하도록 한다.
3. Epipolar Consistency는 depth 없이 pose가 만드는 epipolar line과 대응점의 거리를 줄인다.
4. MVC gradient에서 EC gradient 방향 성분을 제거한다. 두 목적의 역할을 분리하면서 합성 손실을 최적화한다.
5. 회전 SO(3) 거리의 bin 점유·entropy로 target view를 고르고 각 bin의 neighbor를 샘플링한다. QKV에 삽입한 LoRA만 갱신한다.

§III–IV. 기학습 가중치는 고정하고 장면마다 adapter를 적응한다. "GT-free"는 정답 기하를 쓰지 않는다는 뜻이며 matcher·기학습 모델·계산 비용이 없는 것은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.10708v2), Table II, PDF p.7.

DA3 평가 프로토콜로 장면당 최대 100프레임을 샘플링한다. 아래는 VGGT와 VGGT-Ours의 pose AUC@3/AUC@30(회전·이동 pose error의 도 단위 threshold)을 발췌했다. 정답 camera를 쓰는 posed geometry F1과 다른 결과다.

| Dataset   | Variant       | AUC@3 ↑ | AUC@30 ↑ |
| --------- | ------------- | ------- | -------- |
| 7Scenes   | VGGT          | 0.25    | 0.86     |
| 7Scenes   | Self-Geometry | 0.28    | 0.87     |
| ETH3D     | VGGT          | 0.20    | 0.76     |
| ETH3D     | Self-Geometry | 0.27    | 0.83     |
| ScanNet++ | VGGT          | 0.56    | 0.94     |
| ScanNet++ | Self-Geometry | 0.54    | 0.94     |
| HiRoom    | VGGT          | 0.51    | 0.88     |
| HiRoom    | Self-Geometry | 0.47    | 0.85     |

평균 개선이 모든 모델·데이터셋의 개선을 뜻하지 않는다. 위 VGGT의 ScanNet++ AUC@3와 HiRoom 결과는 악화된다. Table III의 posed/unposed F1은 분리해서 읽어야 한다.

## 💡 Insights & Impact

기하 제약을 추가하는 것만큼 어느 변수에 어떤 gradient를 줄 것인지가 중요하다. Confidence나 초기 일치성만으로 신뢰성을 판단하지 않고 대응점 기반 제약을 추가한 접근이다.

- 외부 matcher가 반복적으로 틀리거나 overlap이 부족하면 pseudo-supervision도 잘못될 수 있다.
- 장면별 TTA 시간과 adapter 관리가 필요하다. 짧은 feed-forward 추론 시간과 전체 적응 시간을 합쳐 설명하면 안 된다.

## 🔗 Related Work

- [VGGT](vggt.md), [π³](pi3.md), [Depth Anything 3](depth-anything-3.md): 적응 대상 백본.
- [Free-Geometry](free-geometry.md), [Fin3R](fin3r.md): 테스트 장면에 모델을 적응하는 선행 방향.

## 📚 Key Takeaways

1. 입력 대응을 pose-only와 pose+depth 제약으로 분리한다.
2. 정답 기하 없이도 장면 적응은 가능하지만 추가 추론·최적화 비용이 있다.
3. 평균 성능과 데이터셋별 악화를 함께 확인한다.

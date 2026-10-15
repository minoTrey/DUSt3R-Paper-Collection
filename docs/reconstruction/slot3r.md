# Slot3R: Set-Associative Spatial Memory for Streaming 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Xiyuan Zhang, Yanming Yang, Kaiyuan Xu, Ruibo Li, Chi Zhang
- **Institution**: Westlake University, University of Illinois Urbana-Champaign, Nanyang Technological University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.12282) | [Project Page](https://ashleyxyz.github.io/Slot-3R/)
- **Verification**: UNKNOWN (2026-10-15; arXiv v1 원문 확인, 학회 게재 여부 미확인)
- **TL;DR**: Point3R의 학습된 가중치를 유지하고 공간 메모리만 바꾼다. 같은 위치의 서로 다른 관측을 별도 슬롯에 보존하고, 매 프레임에는 제한된 메모리만 읽는다.

## 🎯 Key Contributions

1. **Separate Address and Identity**: 공간적으로 가깝다는 이유만으로 특징을 평균하면 다른 표면이나 관측 방향의 정보가 섞인다. 위치는 저장 주소를 정하고 특징 유사도는 병합 여부를 정한다.
2. **Set-Associative Memory**: 하나의 공간 주소에 여러 위치·특징 상태를 저장한다. 신뢰도와 특징 유사도로 삽입·병합·교체를 결정한다.
3. **Bounded Decoder Readout**: 전체 저장소와 디코더가 읽는 토큰 수를 분리한다. 저장소 전체의 크기가 일정하다는 뜻은 아니다.
4. **Training-Free Retrofit**: Point3R를 재학습하지 않고 추론 시 메모리 관리 절차를 바꾼다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간순 RGB 영상. 현재 프레임을 처리할 때 이후 프레임은 사용하지 않는다.
- **Output**: 프레임별 카메라 자세, 깊이 맵, 공통 좌표계의 pointmap. Pointmap은 픽셀마다 대응하는 3D 좌표를 담는다.
- **Problem**: Point3R의 패치별 위치는 넓은 영상 영역을 요약한다. 가까운 위치의 특징도 서로 다른 표면을 나타낼 수 있다.

### Memory Update and Readout

```text
현재 RGB → 고정된 Point3R 인코더
         → 지역 메모리 + 전역 앵커 검색 → 디코더 → 자세·깊이·pointmap
         → 새 위치·특징 후보 → 신뢰도 검사 → 슬롯 병합·삽입·교체
```

원논문 §3.2–3.4의 절차는 다음과 같다.

1. 구면 좌표를 구간으로 나누는 해시로 관측의 공간 주소를 정한다.
2. 낮은 신뢰도의 후보를 프레임 내 분위수 기준으로 제외한다.
3. 같은 주소의 특징과 충분히 유사하고 신뢰도가 높은 후보는 병합한다. 다른 특징은 별도 슬롯에 넣거나 낮은 신뢰도 슬롯을 교체한다.
4. 이전 프레임 pointmap을 현재 패치 위치의 근사값으로 사용해 주변 메모리를 찾는다. 이 근사값은 정확한 픽셀 대응이 아니다.
5. 지역 후보에 전역 앵커를 더하고 읽기 예산 이내의 토큰만 디코더에 전달한다.

기본 설정은 주소당 8개 슬롯, 전역 앵커 128개, 읽기 예산 640개 토큰이다 (§4.1).
선택 기능인 VPC는 별도 관측 방향 메모리로 자세 질의를 보완한다. 아래 표는 VPC를 제외한 Core 결과다.

## 📊 Results

### Point-Cloud Reconstruction

[arXiv v1 PDF](https://arxiv.org/pdf/2610.12282v1), Table 1, PDF p.7.
각 시퀀스에서 두 프레임마다 샘플링한다 (`k=2`). 표는 500개 샘플 프레임 조건을 발췌했다.
Acc는 예측 점의 표면 정확도 오차, Comp는 완전성 오차, NC는 법선 일관성이다.
거리 단위는 이 표에 명시되지 않아 임의로 붙이지 않았다.

| Dataset    | Method      | Acc ↓  | Comp ↓ | NC ↑   |
| ---------- | ----------- | ------ | ------ | ------ |
| 7Scenes    | Point3R     | 0.0745 | 0.0265 | 0.5510 |
| 7Scenes    | Slot3R Core | 0.0275 | 0.0158 | 0.5790 |
| NeuralRGBD | Point3R     | 0.2106 | 0.0706 | 0.6025 |
| NeuralRGBD | Slot3R Core | 0.0589 | 0.0236 | 0.6728 |

### Runtime and Evaluation Limits

Table 1의 Avg. FPS는 300–500 프레임 조건에서 완료된 실행의 평균이다.
단일 RTX 4090 24 GB에서 측정하며 데이터 로딩과 지표 계산은 제외한다 (§4.1).

| Dataset    | Point3R Avg. FPS ↑ | Slot3R Core Avg. FPS ↑ |
| ---------- | ------------------ | ---------------------- |
| 7Scenes    | 16.77              | 19.17                  |
| NeuralRGBD | 18.01              | 19.02                  |

평가 코드는 시퀀스 전체를 먼저 인코딩한 뒤 인과적 디코딩을 수행한다.
따라서 이 속도를 센서 입력부터 출력까지의 실제 온라인 지연으로 해석하면 안 된다.
Table 2에서는 정렬한 상대 깊이는 개선되지만 Bonn·KITTI의 metric-scale AbsRel은 악화된다.
Table 3에서도 Core의 ATE 개선이 모든 상대 자세 오차의 개선을 뜻하지는 않는다.

## 💡 Insights & Impact

이 논문의 실용적 질문은 "같은 장소를 다시 보았을 때 무엇을 합칠 것인가"다.
위치가 비슷한 모든 관측을 합치는 대신, 같은 장소에 서로 다른 증거를 남긴다.
이렇게 남긴 증거를 모두 읽지 않고 필요한 부분만 선택한다.

전체 메모리는 새 공간을 관측할수록 증가한다 (§5).
고정된 슬롯 수·공간 구간·읽기 예산은 장면과 이동 방식에 따라 제약이 될 수 있다.
논문은 Point3R에 적용한 결과를 검증했다. 다른 백본에서 같은 효과가 난다는 근거는 아직 없다.

## 🔗 Related Work

- **[Point3R](point3r.md)**: 변경 대상인 공간 포인터 메모리와 고정 백본을 제공한다.
- **[Spann3R](spann3r.md)**: 과거 특징을 메모리에 보존하는 선행 접근이다.
- **[CUT3R](../dynamic/cut3r.md)**: 고정된 재귀 상태로 과거 관측을 요약한다.
- **[InfiniteVGGT](infinitevggt.md)**: 시간순 캐시를 사용하는 비교 대상이다. Slot3R는 공간 주소별 상태를 관리한다.
- **[MUSt3R](must3r.md)**: 저장된 특징의 선택이 계산량과 재구성 품질을 함께 좌우한다는 점에서 연결된다.

## 📚 Key Takeaways

1. 같은 위치와 같은 관측 상태는 다르다. 특징을 합치기 전에 내용의 일치 여부를 확인한다.
2. 전체 저장량과 프레임별 읽기 비용은 별도로 관리할 수 있다.
3. 고정된 읽기 예산은 전체 메모리의 상한을 보장하지 않는다.
4. 점군·깊이·자세·속도는 각각의 평가 조건으로 판단해야 한다.

# MUSt3R: Multi-view Network for Stereo 3D Reconstruction (CVPR 2025)

![MUSt3R Architecture](https://raw.githubusercontent.com/naver/must3r/main/assets/overview.jpg)
_공식 구현의 overview 그림. 현재 RGB 프레임은 층별 latent memory를 읽고 전역·로컬 pointmap을 예측한다._

## 📋 Overview

- **Authors**: Yohann Cabon, Lucas Stoffl, Leonid Antsfeld, Gabriela Csurka, Boris Chidlovskii, Jérôme Revaud, Vincent Leroy
- **Institution**: NAVER LABS Europe, ENS Paris-Saclay
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.01661) | [Code](https://github.com/naver/must3r) | [Project Page](https://europe.naverlabs.com/research/publications/must3r-multi-view-network-for-stereo-3d-reconstruction/)
- **Verification**: CONFIRMED (venue: cached DBLP verdict 2026-07-20; 방법·결과 PDF 재검토 2026-10-15)
- **TL;DR**: 여러 이미지가 공통 좌표계의 pointmap을 내도록 DUSt3R의 디코더를 대칭화한다. 각 층의 과거 특징을 메모리에 저장하고 필요한 프레임만 추가해 많은 뷰를 처리한다.

## 🎯 Key Contributions

1. **Shared Decoder**: 모든 뷰가 하나의 디코더 가중치를 공유한다.
2. **Multi-Layer Memory**: 새 이미지는 이전에 계산한 층별 특징을 재사용한다.
3. **3D Feedback**: 마지막 층의 3D 정보를 앞쪽 층의 메모리에 전달한다.
4. **Online and Offline Modes**: 순차 예측과 메모리를 만든 뒤 다시 예측하는 rendering 경로를 지원한다.
5. **Memory Selection**: 새로 관측한 공간을 기준으로 메모리에 넣을 프레임을 선택한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 시간순 영상 또는 순서 없는 RGB 이미지 집합. 네트워크에 카메라 보정값을 입력하지 않는다.
- **Output**: 각 이미지의 공통 좌표계 pointmap과 confidence. 이후 focal·카메라 pose를 복원할 수 있다.
- **Problem**: 모든 이미지 쌍을 DUSt3R로 예측하면 쌍의 수와 정렬 비용이 증가한다.

### Memory and Rendering

```text
첫 이미지들 → 공유 인코더·디코더 → 층별 메모리
새 이미지 → 메모리에 cross-attention → 공통 좌표계 pointmap
          → 발견한 새 공간이 충분하면 메모리에 추가
선택적 rendering → 전체 메모리를 읽어 기존 이미지도 다시 예측
```

여기서 rendering은 메모리에서 입력 이미지의 pointmap을 다시 추론하는 단계다.
새 RGB 이미지를 합성한다는 뜻이 아니다 (§3.3).
MUSt3R-C는 인과적 경로이며, 기본 MUSt3R 결과는 rendering과 최소 Laplacian smoothing을 포함한다 (§5.1).

초기 모델은 CroCo v2에서 학습한 대칭 DUSt3R이고, 이후 다중 뷰 학습에서 인코더를 고정한다 (§4).
논문 평가 체크포인트와 이후 공식 저장소에서 갱신한 체크포인트의 설정은 다르다.
아래 결과는 arXiv v1 논문에 대응한다.

### Complexity and Limits

메모리는 저장한 이미지 수에 따라 증가한다 (§3.4).
새 프레임이 모든 누적 토큰을 읽으면 프레임당 attention 비용도 증가한다.
따라서 메모리 크기의 선형 증가를 전체 시퀀스 계산량의 무조건적인 O(N) 보장으로 해석하면 안 된다.
프레임 선택은 비용을 줄이지만 무제한 뷰·상수 메모리를 보장하지 않는다.

## 📊 Results

**Source**: [arXiv 2503.01661v1 PDF](https://arxiv.org/pdf/2503.01661v1).
오래된 문서의 중복 표와 잘못 묶인 다단 헤더를 제거하고 아래처럼 프로토콜별로 정리했다.
전체 비교 방법·세부 시퀀스·보충 결과는 원문의 해당 표에서 확인할 수 있다.

### Uncalibrated Visual Odometry: TUM RGB

Table 1, PDF p.6. 아래 세 방법은 dense unconstrained (U) 조건이다.
ATE RMSE의 단위는 cm이며 낮을수록 좋다. 평균 오류를 FPS로 읽으면 안 된다.
이 표는 11개 시퀀스의 VO 평가다.

| TUM Sequence | Spann3R ATE ↓ | MUSt3R-C ATE ↓ | MUSt3R ATE ↓ |
| ------------ | ------------- | -------------- | ------------ |
| fr1/360      | 20.7          | 8.9            | 7.8          |
| fr1/desk     | 16.1          | 5.1            | 4.0          |
| fr1/desk2    | 28.3          | 7.1            | 4.6          |
| fr1/plant    | 57.4          | 5.4            | 4.0          |
| fr1/room     | 84.8          | 13.4           | 9.9          |
| fr1/rpy      | 6.1           | 5.2            | 4.3          |
| fr1/teddy    | 92.4          | 6.9            | 4.2          |
| fr1/xyz      | 2.1           | 2.7            | 1.3          |
| fr2/xyz      | 4.4           | 1.7            | 1.2          |
| fr3/desk     | 20.7          | 15.6           | 15.3         |
| fr3/long     | 193.9         | 5.9            | 4.3          |
| Average      | 47.9          | 7.1            | 5.5          |

§5.1의 속도 측정은 NVIDIA V100에서 수행했다.
Spann3R 4.8 FPS, MUSt3R-C 11.1 FPS, MUSt3R 8.4 FPS다.
Spann3R의 47.9는 평균 ATE(cm)이며 47.9 FPS가 아니다.

### TUM RGB-D: All Evaluation Categories

Table 2, PDF p.7. 전체 46개 test scene을 여섯 범주로 평가한다.
각 셀은 ATE RMSE(cm)의 **mean (median)**이다. 위 11개 시퀀스 평균과 다른 모집단이다.

| Category   | Spann3R      | MUSt3R-C   | MUSt3R     |
| ---------- | ------------ | ---------- | ---------- |
| Test       | 4.1(4.0)     | 3.9(3.8)   | 3.8(3.8)   |
| Handheld   | 60.1(28.3)   | 7.2(7.1)   | 6.2(5.8)   |
| Robot      | 122.8(115.6) | 37.4(32.6) | 20.6(14.6) |
| Structure  | 32.7(6.8)    | 5.2(5.0)   | 3.9(3.6)   |
| Dynamic    | 88.3(76.6)   | 39.1(12.7) | 29.1(10.8) |
| 3D Objects | 80.9(61.2)   | 32.0(7.1)  | 22.7(5.6)  |
| Avg        | 64.8(48.7)   | 20.8(11.4) | 14.4(7.4)  |

### ETH3D SLAM

Table 5, PDF p.8. 선택한 8개 궤적의 ATE RMSE(cm)와 FPS를 구분한다.

| Method   | Mean ATE (cm) ↓ | FPS ↑ |
| -------- | --------------- | ----- |
| Spann3R  | 16.8            | 6.1   |
| MUSt3R-C | 11.2            | 11.8  |
| MUSt3R   | 10.0            | 8.7   |

### Point-Cloud Reconstruction

Table 6, PDF p.9. Spann3R 평가 프로토콜의 **mean** 결과만 아래에 발췌했다.
Acc·Comp는 거리 오차이며 NC는 법선 일관성이다.
데이터셋 간 거리 단위를 이 요약에서 동일하게 가정하지 않는다.
모든 이미지를 메모리에 반영하고 rendering한 점군을 평가한다 (§5.3).

| Dataset    | Method     | Mean Acc ↓ | Mean Comp ↓ | Mean NC ↑ |
| ---------- | ---------- | ---------- | ----------- | --------- |
| 7Scenes    | DUSt3R-224 | 0.029      | 0.028       | 0.668     |
| 7Scenes    | Spann3R    | 0.034      | 0.024       | 0.664     |
| 7Scenes    | MUSt3R-224 | 0.028      | 0.027       | 0.665     |
| 7Scenes    | MUSt3R-512 | 0.026      | 0.027       | 0.617     |
| NeuralRGBD | DUSt3R-224 | 0.054      | 0.032       | 0.802     |
| NeuralRGBD | Spann3R    | 0.069      | 0.029       | 0.778     |
| NeuralRGBD | MUSt3R-224 | 0.062      | 0.031       | 0.788     |
| NeuralRGBD | MUSt3R-512 | 0.048      | 0.020       | 0.768     |
| DTU        | DUSt3R-224 | 2.296      | 2.158       | 0.747     |
| DTU        | Spann3R    | 4.785      | 2.743       | 0.721     |
| DTU        | MUSt3R-224 | 3.256      | 2.193       | 0.715     |
| DTU        | MUSt3R-512 | 3.261      | 1.965       | 0.661     |

Table 6의 속도·메모리는 A100에서 측정했다. 앞의 V100 VO 속도와 합치지 않는다.
Rendering 최대 batch는 MUSt3R-224에서 10, MUSt3R-512에서 5다.
DUSt3R는 complete pair graph를 사용한다. 구현과 attention kernel도 메모리 차이에 영향을 준다 (§5.3).

| Method     | FPS ↑ | GPU Memory (원문 G 표기) ↓ |
| ---------- | ----- | -------------------------- |
| DUSt3R-224 | 0.74  | 38.1                       |
| Spann3R    | 27.38 | 5.0                        |
| MUSt3R-224 | 40.41 | 4.1                        |
| MUSt3R-512 | 12.10 | 8.1                        |

§5.3은 MUSt3R-224의 naive attention 구현이 5.2G를 사용한다고도 밝힌다.
4.1G와 5.0G 차이를 메모리 알고리즘만의 효과로 단정할 수 없다.

### Additional Evaluations

원문 Table 3은 수직 FoV 오류(도), Table 4는 scale 오류, Table 7은 10-view 상대 pose,
Table 8은 정답 pose·intrinsics 없이 median normalization한 multi-view depth를 평가한다.
Appendix Tables 11–12에는 전체 TUM·ETH3D 결과가 있다.
기존 문서의 33–37열 병합 헤더 표 대신 이 원본 표를 참조한다.
이 조건들을 위 점군·VO 결과와 혼합한 단일 성능 순위는 만들지 않는다.

## 💡 Insights & Impact

이 논문은 과거 이미지의 디코더 특징을 저장해 쌍별 재계산을 줄인다.
다만 오래된 기준 뷰에서 멀어질 때 품질이 저하될 수 있다 (§5.5).
메모리 추가 기준·입력 순서·rendering 여부에 따라 비용과 품질이 달라진다.

결과는 모든 지표의 동시 개선을 뜻하지 않는다.
예를 들어 Table 6에서 MUSt3R-512의 7Scenes NC는 MUSt3R-224보다 낮다.
VO와 점군 평가의 하드웨어·경로가 다르므로 하나의 FPS를 일반적인 처리 속도로 쓰지 않는다.

공식 코드는 [MUSt3R Non-Commercial License](https://github.com/naver/must3r/blob/main/LICENSE)를 명시한다.
체크포인트 데이터 관련 조건은 공식 [NOTICE](https://github.com/naver/must3r/blob/main/NOTICE)에 있다.
이 요약은 해당 문서의 존재와 명칭만 기록한다. 컬렉션의 라이선스 조건을 새로 정하지 않는다.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: 쌍별 pointmap 회귀의 기반이다.
- **[MASt3R](../foundation/mast3r.md)**: 대응점 특징을 추가하는 방향이다. MUSt3R의 메모리 확장과 목적이 다르다.
- **[Spann3R](spann3r.md)**: 직접 비교하는 공간 메모리 방법이다. ATE와 FPS를 별도로 읽어야 한다.
- **[VGGT](vggt.md)**: 여러 뷰를 공동 attention으로 처리하는 다른 접근이다.
- **[Slot3R](slot3r.md)**: 공간 주소의 상태 보존과 제한된 메모리 읽기를 다루는 후속 논문이다.

## 📚 Key Takeaways

1. 입력은 여러 RGB 이미지이고 주요 출력은 공통 좌표계의 pointmap이다.
2. 저장한 층별 특징과 3D feedback으로 새 뷰를 처리한다.
3. 메모리의 선형 증가가 전체 계산량의 선형 보장은 아니다.
4. Rendering 여부, 해상도, 하드웨어와 평가 프로토콜을 속도·정확도 수치와 함께 읽는다.

# DUSt3R: Geometric 3D Vision Made Easy (CVPR 2024)

![DUSt3R Architecture](https://github.com/naver/dust3r/raw/main/assets/dust3r_archi.jpg)
_두 이미지의 pointmap을 첫 카메라 좌표계로 함께 예측한다. 여러 쌍을 합칠 때는 별도 global alignment를 수행한다._

## 📋 Overview

- **Authors**: Shuzhe Wang, Vincent Leroy, Yohann Cabon, Boris Chidlovskii, Jérôme Revaud
- **Institution**: Aalto University, NAVER LABS Europe
- **Venue**: CVPR 2024
- **Links**: [Paper](https://arxiv.org/abs/2312.14132) | [Code](https://github.com/naver/dust3r) | [Project Page](https://dust3r.europe.naverlabs.com/)
- **Verification**: CONFIRMED (venue: cached DBLP verdict 2026-07-20; 방법·결과 PDF 재검토 2026-10-15)
- **TL;DR**: 보정 정보가 없는 두 RGB 이미지에서 픽셀별 3D 좌표와 confidence를 예측한다. 여러 이미지의 전체 복원은 쌍별 예측을 최적화로 정렬한다.

## 🎯 Key Contributions

1. **Shared-Frame Pointmaps**: 두 이미지의 픽셀별 3D 좌표를 같은 카메라 좌표계로 예측한다.
2. **Uncalibrated Pair Input**: 쌍별 네트워크는 카메라 내부 파라미터나 상대 pose를 입력으로 요구하지 않는다.
3. **Confidence-Weighted Supervision**: 정답 3D 좌표에 대한 회귀와 confidence를 함께 학습한다.
4. **Global Alignment**: 서로 다른 쌍의 예측을 공통 장면으로 정렬한다. 이 단계는 반복 최적화다.

## 🔧 Technical Details

### Input and Output

- **Input**: 겹치는 장면을 담은 두 RGB 이미지.
- **Output**: 두 pointmap과 confidence map. Pointmap은 이미지의 각 픽셀에 대응하는 3D 좌표를 저장한다.
- **Coordinates**: 두 pointmap 모두 첫 번째 카메라 좌표계에 놓인다. 절대 축척은 일반적으로 정해지지 않는다.

### Architecture and Training

공유 ViT 인코더는 각 이미지를 토큰으로 바꾼다. 두 디코더는 cross-attention으로 서로의 정보를 교환한다.
회귀 헤드는 두 이미지의 pointmap과 confidence를 출력한다 (§3.1).

CroCo의 자기지도 사전학습과 DUSt3R의 3D 지도 학습을 구분해야 한다.
DUSt3R는 깊이·카메라 정보에서 구성한 정답 pointmap으로 학습한다 (§3.2, Appendix B).
Confidence loss는 어려운 영역의 회귀 오차를 조절한다. Confidence로 만든 pseudo-label만 사용하는 자기지도 학습이 아니다.

### From a Pair to a Scene

```text
두 RGB → 쌍별 pointmap·confidence
여러 이미지 → 선택한 쌍마다 예측 → global alignment 최적화 → 공통 장면
```

§3.3은 쌍별 예측의 회전·이동·축척과 전역 pointmap을 맞춘다.
필요한 작업에 따라 pointmap에서 focal·pose·픽셀 대응을 추출한다.
따라서 전체 다중 시점 파이프라인을 항상 "단 한 번의 forward"나 "최적화 없음"으로 설명하면 부정확하다.

## 📊 Results

**Source**: [arXiv 2312.14132v3 PDF](https://arxiv.org/pdf/2312.14132v3).
DUSt3R-512는 긴 변 기준 512 해상도와 여러 종횡비를 사용한다. 모든 입력이 정사각형이라는 뜻은 아니다.

### DTU Dataset (3D Reconstruction)

원논문 Table 4, PDF p.9. 단위는 mm다. DUSt3R는 정답 카메라 없이 복원하며, 다른 행은 정답 카메라를 사용한다.
Table 3의 깊이 평가와 다른 프로토콜이다.

| Method         | Type              | Accuracy ↓ | Completeness ↓ | Overall ↓ |
| -------------- | ----------------- | ---------- | -------------- | --------- |
| Gipuma         | Traditional+GT    | 0.283      | 0.873          | 0.578     |
| MVSNet         | Learning+GT       | 0.396      | 0.527          | 0.462     |
| CVP-MVSNet     | Learning+GT       | 0.296      | 0.406          | 0.351     |
| **DUSt3R-512** | **No GT cameras** | **2.677**  | **0.805**      | **1.741** |

_Note: DUSt3R operates without calibration or GT depth, making direct comparison complex._

### Multi-view Pose Estimation (CO3Dv2)

Table 2 right 및 Table 5. 무작위 10프레임을 사용하고 global alignment 후 상대 자세를 평가한다.

| Metric    | DUSt3R-512 (w/ GA) | Description                   |
| --------- | ------------------ | ----------------------------- |
| RRA@15 ↑  | 96.2%              | Relative Rotation Accuracy    |
| RTA@15 ↑  | 86.8%              | Relative Translation Accuracy |
| mAA(30) ↑ | 76.7%              | Mean Average Accuracy         |

### Visual Localization (7-Scenes)

Table 1 및 Appendix Table 6. 중앙 이동·회전 오차다. 2D matching 경로와 정답 focal을 사용한 결과다.
따라서 이 표는 카메라 정보를 전혀 쓰지 않는 pose regression 결과가 아니다.

| Scene   | Trans. Error (cm) ↓ | Rot. Error (°) ↓ | Model      |
| ------- | ------------------- | ---------------- | ---------- |
| Chess   | 3                   | 0.97             | DUSt3R-512 |
| Fire    | 3                   | 0.95             | DUSt3R-512 |
| Heads   | 2                   | 1.37             | DUSt3R-512 |
| Office  | 3                   | 1.01             | DUSt3R-512 |
| Pumpkin | 4                   | 1.14             | DUSt3R-512 |
| Kitchen | 4                   | 1.34             | DUSt3R-512 |
| Stairs  | 11                  | 2.84             | DUSt3R-512 |

### Visual Localization (Cambridge Landmarks)

Table 1 및 Appendix Table 6의 같은 2D matching 경로다. 중앙 오차를 보고한다.

| Scene          | Trans. Error (cm) ↓ | Rot. Error (°) ↓ | Model      |
| -------------- | ------------------- | ---------------- | ---------- |
| St. Facade     | 6                   | 0.26             | DUSt3R-512 |
| Old Hospital   | 17                  | 0.33             | DUSt3R-512 |
| King's College | 11                  | 0.20             | DUSt3R-512 |
| St. Mary's     | 7                   | 0.24             | DUSt3R-512 |
| Great Court    | 38                  | 0.16             | DUSt3R-512 |

### Multi-view Depth Estimation

Table 3, PDF p.9의 (d) 조건. 정답 pose·깊이 범위를 입력하지 않고 정답 깊이와 median scale 정렬한다.
Rel과 inlier ratio는 원문 백분율 표기다. Inlier threshold는 **1.03**이다.
ScanNet은 같은 도메인의 학습 데이터를 사용한 행으로 원문에서 괄호로 표시된다.

| Dataset         | Rel. Error (%) ↓ | Inlier τ@1.03 (%) ↑ | Model          |
| --------------- | ---------------- | ------------------- | -------------- |
| KITTI           | 9.11             | 39.49               | DUSt3R-512     |
| ScanNet         | 4.93             | 60.20               | DUSt3R-512     |
| ETH3D           | 2.91             | 76.91               | DUSt3R-512     |
| DTU             | 3.52             | 69.33               | DUSt3R-512     |
| Tanks & Temples | 3.17             | 76.68               | DUSt3R-512     |
| **Average**     | **4.73**         | **64.52**           | **DUSt3R-512** |

### Qualitative Results

원논문 Fig. 1·7 등은 다양한 영상의 예시를 보여준다.
두 장에서 점군을 예측할 수 있지만, 가려진 표면까지 완전하거나 모든 반사·저텍스처 장면에서 정확하다는 보장은 아니다.

## 💡 Insights & Impact

학습한 3D 사전 지식으로 카메라 보정과 대응점 탐색의 부담을 줄인 것이 핵심이다.
그러나 네트워크의 쌍별 추론, 전역 정렬, localization의 기하 계산은 다른 단계다.
각 단계의 시간과 입력 조건을 합쳐 설명하면 실제 사용 비용을 오해할 수 있다.

정답 카메라를 사용하는 MVS와 DUSt3R의 무보정 복원은 같은 조건의 순위표가 아니다.
가려진 영역·학습 분포 밖 장면·축척의 모호성도 남는다.
이 문서는 출처를 특정할 수 없던 H100의 40 ms 주장과 일반적인 완료 시간 비교를 제거했다.

## 🔗 Related Work

### Direct Extensions

- **Efficiency**: [Fast3R](../reconstruction/fast3r.md), [SLAM3R](../reconstruction/slam3r.md), [Spann3R](../reconstruction/spann3r.md) (speed improvements)
- **Quality**: [MASt3R](mast3r.md), [VGGT](../reconstruction/vggt.md), [π³](../reconstruction/pi3.md) (Pi3) (improved accuracy)
- **Scale**: [REGIST3R](../reconstruction/regist3r.md), [ReconX](../reconstruction/reconx.md), [Light3R-SfM](../reconstruction/light3r-sfm.md) (larger scenes)
- **Applications**: [Splatt3R](../gaussian-splatting/splatt3r.md), [Dust-GS](../gaussian-splatting/dust-gs.md) (Gaussian Splatting), [RIG3R](../robotics/rig3r.md) (robotics)

### Research Directions Enabled

1. **Dynamic Reconstruction**: [MonST3R](../dynamic/monst3r.md), [POMATO](../dynamic/pomato.md), [D²USt3R](../dynamic/d2ust3r.md), [Stereo4D](../dynamic/stereo4d.md)
2. **Neural Rendering**: Splatt3R, [PreF3R](../gaussian-splatting/pref3r.md), [InstantSplat](../gaussian-splatting/instantsplat.md)
3. **Scene Understanding**: [PE3R](../understanding/pe3r.md), [MEt3R](../understanding/met3r.md), [LargeSpatialModel](../understanding/largespatialmodel.md)
4. **Robotics**: RIG3R, [GraphSeg](../robotics/graphseg.md), SLAM3R

## 📚 Key Takeaways

1. 입력은 이미지 쌍이고 직접 출력은 두 pointmap과 confidence다.
2. CroCo 사전학습과 DUSt3R의 3D 지도 학습은 다르다.
3. 여러 쌍의 전체 장면 복원에는 global alignment가 필요하다.
4. 보정 입력·축척 정렬·데이터셋 조건을 확인하고 수치를 비교한다.

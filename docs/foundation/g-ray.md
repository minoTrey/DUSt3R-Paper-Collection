# G-ray: Ray-Level Relative Geometric Position Encoding in Multi-View Vision Transformers under Camera Heterogeneity (arXiv 2026)

## 📋 Overview

- **Authors**: Shuo Zhang, Xin Su, Wei Wang, Jun Liu, Xinrui Zeng, Yongsen Chen, Chenjie Wang, Guibo Zhu, Jinqiao Wang, Bin Luo, Liangpei Zhang
- **Institution**: Wuhan University, Institute of Automation Chinese Academy of Sciences, Wuhan AI Research, Rongyun Robot
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.15018)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.15018v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 서로 다른 projection의 이미지 좌표 대신 camera-local ray angle로 상대 positional encoding을 만들어 혼합 camera의 attention을 일관되게 한다.

## 🎯 Key Contributions

1. Ray-level rotary phase를 정의한다.
2. 기존 RoPE·GTA·RayRoPE와 결합 가능한 표현을 제시한다.
3. 외부 calibration과 추정 calibration 조건을 나누어 평가한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 여러 RGB 이미지와 view별 calibrated ray map; 별도 구성에서는 AnyCalib로 ray를 추정한다.
- **Output**: 연결한 모델의 pointmap·depth·pose 또는 novel view.
- **Problem**: 같은 실제 ray 관계라도 projection과 FoV가 다르면 image-plane 위치의 상대 phase가 달라진다.

### Method

1. Camera-local ray를 각도 좌표로 표현한다.
2. 두 ray의 상대 각도에 따라 attention rotary phase를 구성한다.
3. 기존 position encoding과 결합해 projection을 넘어 같은 ray 관계를 전달한다.
4. Pinhole로 학습한 reconstruction 모델을 mixed-projection 평가에 적용한다.

Encoding 자체에 추가 learned parameter가 없다는 의미이며 전체 모델이 학습 없이 작동한다는 뜻은 아니다. External calibration 사용 여부를 명시해야 한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.15018v2), Table I, PDF p.10.

ScanNet++·PandaSet·ETH3D mixed-projection 50-view 평균. 아래 두 행은 모두 외부 calibration을 받으며 point relative error는 낮을수록 좋다.

| Method                       | Point relative error ↓ | Ray error (°) ↓ | Depth relative error ↓ |
| ---------------------------- | ---------------------- | --------------- | ---------------------- |
| MapAnything, calibrated rays | 0.1372                 | 2.11            | 0.1199                 |
| G-ray, calibrated rays       | 0.0744                 | 0.38            | 0.0744                 |

Calibration을 AnyCalib 추정으로 바꾸면 G-ray point error는 0.1347이다. Calibration 없는 VGGT와 calibrated G-ray를 같은 입력 조건이라고 비교하면 안 된다.

## 💡 Insights & Impact

Camera 종류 이름보다 pixel이 실제로 바라보는 ray를 attention의 기하 기준으로 사용한다.

- Ray calibration 품질이 성능에 직접 영향을 준다.
- Pinhole 학습에서 mixed camera로의 전이는 평가 범위 안의 결과이며 모든 lens·scene을 보장하지 않는다.

## 🔗 Related Work

- [MEOW](../reconstruction/meow.md): camera label 없는 mixed-camera adaptation과 입력 조건이 다르다.
- [VGGT](../reconstruction/vggt.md): multi-view attention의 배경.

## 📚 Key Takeaways

1. Ray를 positional encoding의 기준으로 쓴다.
2. 추가 parameter가 없다는 것과 training-free는 다르다.
3. Calibration 조건을 결과 옆에 적는다.

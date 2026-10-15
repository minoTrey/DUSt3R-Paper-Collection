# WildHSR: Metric Feed-Forward 4D People-Scene Reconstruction from a 3D Foundation Model (arXiv 2026)

## 📋 Overview

- **Authors**: Jerrin Bright, John Zelek
- **Institution**: University of Waterloo
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.29106)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.29106v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: VGGT-Ω의 up-to-scale geometry에 metric scale readout과 사람 identity readout을 더해 영상의 사람·scene·camera를 공통 metric frame으로 연결한다.

## 🎯 Key Contributions

1. 사람 body ruler로 web video의 scale pseudo-label을 만든다.
2. 중간 query–key feature에서 person correspondence를 읽는다.
3. Metric pelvis motion과 dustbin-aware association으로 identity를 연결한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 움직이는 단안 RGB 영상.
- **Output**: Metric camera·scene, persistent 사람 track·SMPL-X body.
- **Problem**: Up-to-scale geometry에는 절대 scale과 여러 window를 잇는 사람 identity가 빠져 있다.

### Method

1. VGGT-Ω window feature에 작은 LoRA와 Scale Readout을 연결한다.
2. Offline body·keypoint pseudo-label로 scale을 사전학습하고 실제 metric annotation으로 보정한다.
3. Pelvis readout과 human token을 cross-attention으로 결합한다.
4. 중간 correspondence·pelvis motion·confidence로 Sinkhorn association을 계산하고 window를 합친다.

Web-video pseudo supervision 뒤 RICH·3DPW의 exact metric training split으로 fine-tuning한다. Body ruler·teacher를 inference 입력으로 다시 쓰는 방식과 다르다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.29106v1), Table 4, PDF p.8.

Held-out 3DPW, 14-joint camera-frame error와 mesh PVE, 단위 mm. PA-MPJPE는 사람별 similarity alignment를 제거한 값이다.

| Method  | PA-MPJPE ↓ | MPJPE ↓ | PVE ↓ |
| ------- | ---------- | ------- | ----- |
| SHOW    | 41.0       | 67.7    | 78.7  |
| WildHSR | 38.7       | 65.2    | 74.4  |

이 표는 world placement를 평가하지 않는다. EMDB·RICH의 global motion 표에서는 일부 optimization 방법보다 W error가 높고 RICH RTE도 항상 최고는 아니다.

## 💡 Insights & Impact

하나의 foundation feature에서 geometry의 scale과 사람의 correspondence를 서로 다른 readout으로 얻는다.

- 훈련에서 사용한 exact metric supervision을 숨기면 zero-shot metric 추정으로 오해할 수 있다.
- 가림·다중 사람 association·window 연결의 오류가 남는다.

## 🔗 Related Work

- [VGGT-Ω](../reconstruction/vggt-omega.md): 기반 representation.
- [Human3R](human3r.md): human-scene reconstruction 비교.

## 📚 Key Takeaways

1. Scale과 identity가 별도 missing output이다.
2. Pseudo-label 뒤 exact metric 학습이 있다.
3. Local body와 global placement 점수를 구분한다.

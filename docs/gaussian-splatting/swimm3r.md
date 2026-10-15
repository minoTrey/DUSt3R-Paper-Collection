# Swimm3R: Splatting with Medium-aware SfM for Underwater 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Minseong Kweon, Junaed Sattar
- **Institution**: University of Minnesota–Twin Cities
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.00950)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.00950v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: MASt3R의 육상 geometry prior를 수중으로 증류하고, 물의 감쇠·산란을 고려한 Beta Splatting으로 지도와 rendering을 최적화한다.

## 🎯 Key Contributions

1. Geometry·descriptor feature를 수중 LoRA student에 증류한다.
2. Physics head가 attenuation·backscatter·veiling light를 예측한다.
3. Beta primitive와 scattering-aware gradient로 수중 scene을 최적화한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 보정되지 않은 수중 RGB 영상.
- **Output**: Pose·복원 point cloud·medium parameter와 최적화된 Beta primitive scene.
- **Problem**: 수중 광학 효과가 SfM 초기화를 무너뜨리고 splatting의 geometry gradient도 왜곡한다.

### Method

1. 깨끗한 영상 teacher의 MASt3R feature를 raw underwater student로 증류한다.
2. Physics head로 물을 통과한 영상과 복원 영상을 연결한다.
3. 예측 geometry로 Beta primitive를 초기화한다.
4. Scattering-aware geometric gradient와 medium field를 scene별로 최적화한다.

수중 adaptation 학습과 별도의 per-scene splatting 최적화가 있다. 전체 시스템이 feed-forward 한 번으로 끝나는 것은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.00950v1), Table II, PDF p.5.

FLSea test sequence의 depth·pose 평가. RRA/RTA@15와 mAA(30)는 percentage이며 높을수록 좋다.

| Method     | AbsRel ↓ | RRA@15 ↑ | RTA@15 ↑ | mAA(30) ↑ |
| ---------- | -------- | -------- | -------- | --------- |
| MASt3R-SfM | 0.2247   | 77.47    | 86.81    | 66.83     |
| Swimm3R    | 0.2132   | 79.19    | 88.43    | 69.67     |

Barbados의 geometry GT는 없으며 일부 pose reference는 GLUEMAP이다. 더 많은 point 수가 실제 표면 정확도를 직접 증명하지 않는다.

## 💡 Insights & Impact

Geometry adaptation과 medium-aware rendering을 연속 단계로 연결하되 각각의 supervision과 평가를 구분한다.

- Optical model과 복원 teacher의 오차를 함께 받을 수 있다.
- 작은 수중 영상 benchmark의 결과이며 모든 수중 조건을 포괄하지 않는다.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): feature·matching prior.
- [WAT3R](../reconstruction/wat3r-feedforward.md): 별도 수중 feed-forward adaptation.

## 📚 Key Takeaways

1. SfM prior와 splatting 최적화가 두 단계다.
2. Geometry·optics를 함께 적응한다.
3. 센서 GT와 대체 reference를 구분한다.

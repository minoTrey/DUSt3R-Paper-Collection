# FIRE3D: Feed-forward Interactive 3D Scene Reconstruction Within A Minute (arXiv 2026)

## 📋 Overview

- **Authors**: Hongchi Xia, Tianhang Cheng, Wei-Chiu Ma, Shenlong Wang
- **Institution**: University of Illinois Urbana-Champaign, Cornell University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.08848)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.08848v2 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: RGB에서 추정한 posed RGB-D를 instance별로 해석하고 compact flow generator로 편집 가능한 object mesh·texture와 scene 배치를 생성한다.

## 🎯 Key Contributions

1. 외부 instance mask 없이 object를 내부 parsing한다.
2. Compact hierarchical latent로 여러 object를 병렬 생성한다.
3. Geometry·material·배치를 갖는 compositional scene을 출력한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 사용자 RGB 이미지 또는 영상. Core network에는 Pi3X로 추정한 posed RGB-D 관측을 전달한다.
- **Output**: Object별 pose·bounding box·amodal mesh·texture와 background scene.
- **Problem**: Point cloud는 보이는 면을 복원하지만 물체를 독립적으로 이동·편집할 수 있는 완성 asset과 다르다.

### Method

1. Pi3X로 camera와 pointmap을 추정한다.
2. 관측 feature를 3D로 lift해 instance validity·pose·mask를 예측한다.
3. 각 instance를 canonicalize한다.
4. Cascaded flow matching으로 structure·shape·material latent를 생성하고 object asset으로 decode한다.

Scene parser와 generative model을 별도 학습한다. Feed-forward는 per-scene 최적화가 없다는 뜻이며 generative sampling·전처리 비용은 존재한다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.08848v2), Table 4, PDF p.8.

Held-out 3D-Front single-image scene-aligned reconstruction. CD는 cm, F1은 1cm threshold다.

| Method   | CD (cm) ↓ | F1 ↑ | Normal consistency ↑ |
| -------- | --------- | ---- | -------------------- |
| SceneGen | 14.90     | 0.06 | 0.58                 |
| FIRE3D   | 11.24     | 0.10 | 0.66                 |

제목의 1분은 지정한 RGB video·instance 수·hardware·전처리 포함 timing protocol의 결과다. Network-only 또는 object당 시간과 섞지 않는다. GT instance와 inferred instance의 결과 차이도 크다.

## 💡 Insights & Impact

직접 관측된 표면 reconstruction을 object completion·material generation으로 연결해 interactable asset을 만든다.

- 가려진 geometry·texture는 생성 prior에 의존한다.
- 잘못된 instance parsing과 Pi3X geometry가 뒤 단계로 전파된다.

## 🔗 Related Work

- [π3](pi3.md): Pi3X 전처리 계열.
- [Amodal3R](../reasoning/amodal3r.md): 보이지 않은 shape completion의 비교 맥락.

## 📚 Key Takeaways

1. RGB 전처리와 core posed RGB-D 입력을 구분한다.
2. 개별 편집 가능한 object asset이 출력이다.
3. 생성한 숨은 면을 실제 관측으로 보지 않는다.

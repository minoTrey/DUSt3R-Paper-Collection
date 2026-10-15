# RoMa-Ω: What Feed-Forward 3D Models Know About Image Matching (arXiv 2026)

## 📋 Overview

- **Authors**: David Nordström, Xinyue Zhang, Thibaut Loiseau, Vincent Lepetit, Fredrik Kahl
- **Institution**: Chalmers University of Technology, ShanghaiTech University, LIGM / École des Ponts / Université Gustave Eiffel / CNRS
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.09507)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.09507v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: FF3D의 내부 특징·pointmap·camera가 matching에 제공하는 정보를 따로 분석한다. VGGT-Ω의 선택된 특징 위에 RoMa형 matcher를 학습하면 단순 zero-shot matching보다 강한 대응을 얻는다.

## 🎯 Key Contributions

1. **Three Matching Probes**: patch feature, raw 3D prediction, 학습한 full matcher를 분리 평가한다.
2. **Feature Selection**: reconstruction의 마지막 층이 항상 좋은 correspondence descriptor는 아니라는 점을 분석한다.
3. **RoMa-Ω**: RoMa v2의 DINO 특징 기반을 선택된 VGGT-Ω representation으로 교체한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 이미지 쌍과 고정된 FF3D representation. 학습된 matching head 또는 raw geometric matching 경로를 선택한다.
- **Output**: dense correspondences와 confidence. Pose·localization 평가는 이 대응과 기하 solver를 사용한다.
- **Problem**: 정확한 pointmap을 예측하는 네트워크가 그대로 좋은 zero-shot image matcher라고 단정할 수 없다. 깊은 층의 특징은 오히려 대응 구별 능력이 낮을 수 있다.

### Method

1. FF3D의 층별 patch feature를 zero-shot matching으로 조사한다.
2. 예측 depth warping·3D mutual nearest neighbors·직접 camera pose를 다른 경로로 평가한다.
3. 좋은 representation 층을 선택해 RoMa v2의 feature backbone 대신 사용한다.
4. 학습한 matcher를 다양한 촬영 조건·dense matching·pose·map-free localization에서 평가한다.

원문 §3–5. RoMa-Ω는 새 matching head 학습을 포함하며 zero-shot 결과와 다르다. Map-free localization에는 별도 DA3 metric depth를 사용하는 조건도 있다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.09507v1), Table 2, PDF p.12.

WxBS와 HardMatch는 mAA@10px, RUBIK은 relative-pose AUC@20°다. 단위·task가 달라 세 열의 크기를 서로 비교하지 않는다. VGGT-Ω 행은 raw 모델 비교다.

| Method  | WxBS mAA@10px ↑ | HardMatch mAA@10px ↑ | RUBIK AUC@20° ↑ |
| ------- | --------------- | -------------------- | --------------- |
| VGGT-Ω  | 29.0            | 20.2                 | 84.3            |
| RoMa    | 72.6            | 48.1                 | 75.4            |
| RoMa v2 | 64.8            | 46.5                 | 85.6            |
| RoMa-Ω  | 72.9            | 50.0                 | 88.0            |

Raw FF3D의 좋은 camera pose만으로 극단적인 이미지 쌍의 matching 성능을 설명할 수 없다. §5.6에서는 RoMa-Ω가 비교한 dense dataset 대부분에서 개선되지만 동적 FlyingThings3D에서는 RoMa v2보다 낮다.

## 💡 Insights & Impact

3D representation과 correspondence supervision은 상호 보완적이다. 기하 모델의 모든 layer·출력이 matching 목적에 똑같이 적합한 것은 아니다.

- 학습형 matcher와 학습 없이 얻은 3D 대응의 정확도·비용을 혼합하면 안 된다.
- 동적 장면과 훈련에서 드문 극단 조건에서 일반화가 제한될 수 있다. Localization은 depth와 robust solver까지 포함한 시스템 결과다.

## 🔗 Related Work

- [MASt3R](mast3r.md): 기하와 descriptor matching을 함께 학습한 선행 방향.
- [VGGT-Ω](../reconstruction/vggt-omega.md): RoMa-Ω가 선택한 representation의 기반.
- [VGGT](../reconstruction/vggt.md): camera·pointmap·tracking output을 구분하는 것이 중요하다.

## 📚 Key Takeaways

1. 복원 정확도와 zero-shot matching 정확도는 같은 성질이 아니다.
2. 특징 layer와 matching head를 함께 선택해야 한다.
3. Raw geometry와 학습형 matcher의 결과를 분리해서 읽는다.

# Colon3R: Cross-Domain 3D Reconstruction from Monocular Colonoscopic Video (arXiv 2026)

## 📋 Overview

- **Authors**: Zhihao Xing, Yingyu Wang, Liang Zhao, Shoudong Huang
- **Institution**: 원문에 기관명 미기재; 저자 소속은 별도 확인 필요
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.23961)
- **Verification**: UNKNOWN (2026-10-15; 원문 2609.23961v3 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: Phantom·simulation으로 학습한 VGGT를 unlabeled 실제 대장내시경 영상에 teacher–student 방식으로 적응시키면서 source geometry 손실을 억제한다.

## 🎯 Key Contributions

1. Source geometry supervision을 적응 중에도 유지한다.
2. Scale stability·support gate로 EMA teacher 갱신을 제한한다.
3. Sequence·pair·pixel 수준 reliability로 cross-view supervision을 조절한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 단안 colonoscopy RGB sequence. 학습에는 labeled phantom·simulation과 unlabeled in-vivo 영상.
- **Output**: Camera·depth·pointmap과 multi-view reconstruction.
- **Problem**: 실제 조직 변형·specularity·적은 overlap 때문에 source-only 모델과 무제한 pseudo-label 적응이 모두 실패할 수 있다.

### Method

1. VGGT에서 source-supervised camera·depth·pointmap prior를 학습한다.
2. Frozen backbone의 late attention LoRA와 head를 source/target별로 다른 범위에서 갱신한다.
3. Teacher의 cross-view pseudo supervision에 계층적 reliability를 적용한다.
4. 신뢰할 support와 scale 안정성을 만족할 때만 EMA teacher를 갱신한다.

In-vivo target의 geometric GT를 사용하지 않는 semi-supervised domain adaptation이다. 모든 supervision이 없는 방법은 아니다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2609.23961v3), Table II, PDF p.7.

Adaptation ablation. In-vivo CV는 unweighted cross-view consistency residual로 실제 GT error가 아니다. C3VD depth Rel은 source-domain retention을 측정한다.

| Variant         | In-vivo CV ↓ | C3VD depth Rel ↓ |
| --------------- | ------------ | ---------------- |
| Fine-tuned VGGT | 0.0764       | 0.0608           |
| Uniform EMA     | 0.0435       | 0.0862           |
| Colon3R         | 0.0479       | 0.0675           |

Uniform EMA가 CV만 보면 더 낮고 source fine-tuned 모델이 C3VD depth만 보면 더 낮다. 제안법은 두 목표의 balance이며 in-vivo absolute geometry 정확성을 입증한 값은 아니다.

## 💡 Insights & Impact

Target 일관성 하나를 최소화하면 geometry prior를 망가뜨릴 수 있어 adaptation과 retention을 함께 본다.

- In-vivo dense GT가 없어 실제 geometry 정확성을 직접 정량 검증하지 못한다.
- Quasi-rigid reliability가 큰 조직 변형을 완전히 모델링하지 않는다.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): source backbone.
- [Endo3R](endo3r.md): endoscopic geometry 비교.

## 📚 Key Takeaways

1. Source label과 unlabeled target을 함께 쓴다.
2. Teacher update 자체를 gate한다.
3. Consistency residual과 실제 GT error를 혼동하지 않는다.

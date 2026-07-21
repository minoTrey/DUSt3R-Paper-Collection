# Muskie: Multi-view Masked Image Modeling for 3D Vision Pre-training (arXiv preprint 2025-11)

## 📋 Overview

- **Authors**: Wenyu Li, Sidun Liu, Peng Qiao, Yong Dou, Tongrui Hu
- **Institution**: National University of Defense Technology
- **Venue**: arXiv preprint (2025-11)
- **Links**: [Paper](https://arxiv.org/abs/2511.18115) | [Project Page](https://leo-frank.github.io/Muskie/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A native multi-view vision backbone pre-trained with Multi-view Masked Image Modeling. By reconstructing heavily masked patches in one view from other views, it learns view-consistent, 3D-aware features without any 3D supervision.

## 🎯 Key Contributions

1. **Multi-view completion pretext task**: Extends single-view Masked Image Modeling (MIM) to the multi-view domain — reconstruct masked regions in one view using visible content from other views, forcing the model to discover geometric correspondences without 3D annotations.
2. **Aggressive masking strategy**: High masking ratios plus spatially concentrated blocks (rectangular / elliptical) make single-view reconstruction nearly impossible, shifting the model from contextual to geometric reasoning.
3. **Native multi-view architecture**: Stacked Alternating-Attention blocks (following VGGT) that treat all views equally and preserve permutation equivariance, augmented with Rotary Positional Embeddings (RoPE); a lightweight linear head is discarded after pre-training.
4. **Backbone utility**: Using Muskie as the feature extractor consistently improves downstream 3D reconstruction and camera pose estimation over state-of-the-art frame-wise backbones (DINOv2, DINOv3, MAE).

## 🔧 Technical Details

### Pretext task

Given a set of views of the same scene, each view is split into non-overlapping patches; a large fraction of patches across all views is masked. The objective is to reconstruct the original pixel values of all masked patches from the remaining visible patches. Reconstructing a heavily masked patch in one view requires identifying the corresponding patch in another view — implicitly learning cross-view geometric correspondence.

### Masking principles (to eliminate single-view shortcuts)

1. **High masking ratio** — considerably higher than the 75% used in MAE.
2. **Spatially concentrated masks** — rectangular and elliptical region masks rather than only random per-patch masking.
3. **Reference views** — a subset of views is kept unmasked to serve as reference.

### Architecture and training

- **Backbone**: stacked Alternating-Attention (AA) blocks alternating frame-wise and global attention; global attention operates across views via cross-view query–key interactions.
- **Objective**: confidence-aware L2 loss; each masked patch produces a reconstructed value and a confidence score normalized to [0, 1]. ε and λ are set to 0.1 in all experiments.
- **Training data**: mixture of Co3Dv2, BlendedMVG, ARKitScenes, DL3DV, MegaDepth, ScanNet++, HyperSim, Waymo, RealEstate10K.
- **Setup**: AdamW, learning rate 2 × 10⁻⁴, cosine decay, 2-epoch warm-up; 400 epochs with 200K image groups per epoch; input views randomly varied between 2 and 8; mixed resolutions 224 / 384 / 512.
- **Model sizes**: Muskie-B (ViT-Base) and Muskie-L (ViT-Large), trained on 8 A100 GPUs (~two weeks for Muskie-L, one week for Muskie-B).

## 📊 Results

### Zero-shot correspondence on NAVI (objects)

원논문 Table 2. ATE는 낮을수록, Acc@k는 높을수록 좋다. Muskie-L의 3D ATE 2.38 cm는 DINOv3 대비 36% error reduction으로 본문에 기술됨.

| Method   | Pixel ATE ↓ | Pixel @5 ↑ | Pixel @10 ↑ | 3D ATE ↓ | 3D @2 ↑   | 3D @5 ↑   |
| -------- | ----------- | ---------- | ----------- | -------- | --------- | --------- |
| MAE      | 81.24       | 14.63      | 19.11       | 5.25     | 54.73     | 78.19     |
| DINOv2   | 53.31       | 16.94      | 26.29       | 4.24     | 69.97     | 84.23     |
| DINOv3   | 41.15       | 17.23      | 27.95       | 3.76     | 74.89     | 87.11     |
| Muskie-B | 42.54       | 19.48      | 31.95       | 2.93     | 75.90     | 89.17     |
| Muskie-L | **29.42**   | **22.29**  | **39.21**   | **2.38** | **82.74** | **91.87** |

### Zero-shot correspondence on ScanNet (scenes)

원논문 Table 3. CroCov2가 Pixel ATE에서 Muskie-B를 앞선다 (25.92 vs 33.77).

| Method   | Pixel ATE ↓ | Pixel @5 ↑ | Pixel @10 ↑ | 3D ATE ↓  | 3D @2 ↑   | 3D @5 ↑   |
| -------- | ----------- | ---------- | ----------- | --------- | --------- | --------- |
| MAE      | 104.94      | 22.07      | 25.18       | 62.70     | 24.01     | 28.51     |
| CroCov2  | **25.92**   | **34.20**  | **55.93**   | 29.84     | **38.16** | **58.02** |
| DINOv2   | 72.11       | 23.42      | 29.22       | 49.09     | 27.13     | 34.29     |
| DINOv3   | 55.78       | 24.66      | 33.54       | 42.58     | 29.49     | 41.69     |
| Muskie-B | 33.77       | 31.41      | 47.67       | 31.67     | 35.03     | 51.14     |
| Muskie-L | 24.68       | 33.83      | 52.96       | **27.82** | 37.52     | 56.60     |

### 3D reconstruction downstream (backbone swap in π³ pipeline)

원논문 Table 1, 7Scenes 벤치마크 (사전학습·다운스트림 학습에 미포함). 본문: Muskie-L이 DINOv2 대비 camera pose AUC@30을 8.514 → 47.345로, pointmap ||L1|| error를 0.074 → 0.035로 개선.

| Method    | AUC@30 ↑   | Pointmap Acc ↓ | Comp ↓    | Overall ↓ | ‖L1‖ ↓    |
| --------- | ---------- | -------------- | --------- | --------- | --------- |
| MAE-L     | 4.536      | 0.055          | 0.107     | 0.081     | 0.129     |
| DINOv2-L  | 8.514      | 0.039          | 0.042     | 0.041     | 0.074     |
| DINOv3-L  | 9.826      | 0.050          | 0.092     | 0.071     | 0.115     |
| Muskie-B  | 31.231     | 0.039          | 0.041     | 0.040     | 0.051     |
| Muskie-L  | **47.345** | **0.025**      | **0.028** | **0.027** | **0.035** |
| π³ (ref.) | 64.069     | 0.014          | 0.016     | 0.015     | 0.022     |

### Ablation: pre-training vs. architecture

원논문 Table 4. 7Scenes·NRGBD 평균. 사전학습이 성능 향상의 주 요인이고 아키텍처 단독 기여는 미미함을 보여준다.

| Configuration | AUC@5 ↑ | AUC@15 ↑ | AUC@30 ↑   | Pointmap Acc ↓ | Comp ↓ | L1 ↓   |
| ------------- | ------- | -------- | ---------- | -------------- | ------ | ------ |
| w/o pre-train | 0.021   | 0.598    | 3.760      | 0.0718         | 0.1123 | 0.1484 |
| w pre-train   | 2.671   | 18.305   | **37.413** | **0.0461**     | 0.0543 | 0.0639 |

## 💡 Insights & Impact

- **Correspondence gains transfer to geometry**: The confidence-aware reconstruction task learns cross-view correspondence cues that directly improve downstream pointmap and pose estimation, even when the π³ decoder is simplified from 36 layers to a lightweight 4-layer version.
- **Smaller model beats larger frame-wise backbones**: Muskie-B consistently surpasses DINOv2-L and DINOv3-L across nearly all metrics, indicating that multi-view pre-training matters more than raw single-view capacity.
- **Multi-view context helps**: Correspondence accuracy on a fixed pair improves as more context views are added (Table 5), with the largest gains in high-precision metrics such as 3D@1cm.
- **Failure mode**: When reference views share no overlap with the target view, the multi-view task degenerates to single-view MIM and reconstruction becomes blurry with low confidence (Fig. 8, 수치 미인쇄).

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Source of the Alternating-Attention design; Muskie removes VGGT's primary/secondary view distinction and enforces permutation equivariance.
- **[π³](../reconstruction/pi3.md)**: Reference reconstruction pipeline used to evaluate Muskie as a backbone.
- **[CroCo](croco.md)**: Adapts MIM to stereo/dual-view completion; Muskie generalizes cross-view completion beyond the pairwise structure.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Feed-forward reconstruction context for the downstream tasks Muskie targets.

## 📚 Key Takeaways

1. **Multi-view completion as pretext** learns 3D-aware features without depth, pose, or any 3D annotation.
2. **Aggressive masking removes single-view shortcuts**, forcing genuine cross-view geometric reasoning.
3. **As a drop-in backbone**, Muskie improves downstream 3D reconstruction and pose estimation over DINOv2/DINOv3/MAE, with Muskie-B often beating larger frame-wise baselines.
4. **Pre-training, not architecture, drives the gains** — the architecture-only variant contributes negligibly.

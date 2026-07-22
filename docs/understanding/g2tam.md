# G2TAM: Geometry Grounded Track Anything Model (ICML 2026)

![g2tam — architecture](https://arxiv.org/html/2607.03789v1/figures/model_v4.jpeg)

_Overview of G2TAM (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Chenming Zhu, Peizhou Cao, Jingli Lin, Wenbo Hu, Yunlong Ran, Jiangmiao Pang, Tai Wang, Xihui Liu
- **Institution**: HKU; Shanghai AI Lab; BUAA; SJTU; UCLA; ZJU
- **Venue**: ICML 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.03789) | [Project Page](https://zcmax.github.io/projects/G2TAM/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A unified end-to-end framework for promptable instance tracking in 3D from unordered RGB images or videos — it uses spatially aligned geometric representations (built on π³) as an implicit memory, fusing text/visual prompts into a shared geometric-semantic space via a cross-modal spatial encoder to jointly reconstruct geometry and predict instance-consistent masks without explicit temporal memory banks.

## 🎯 Key Contributions

1. **Geometry as implicit memory**: The first framework to unify appearance and geometry within a latent, spatially aligned feature space that serves as persistent memory for identity reasoning — avoiding explicit memory banks and post-hoc "Tracking-by-Mapping" pipelines that suffer error propagation.
2. **Cross-modal spatial encoder**: An early-fusion design embedding text/visual prompts directly into a unified geometric-semantic representation, ensuring recognition and identity reasoning are grounded in the same spatial structure.
3. **InsTrack dataset & PIST task**: A large-scale promptable instance tracking dataset (856 training, 50 validation scenes on ScanNet++ splits) and the Promptable Instance Spatial Tracking benchmark, plus a Geometry & Mask decoder for joint reconstruction and mask prediction.

## 🔧 Technical Details

### Architecture (built on π³)

- **Prompt encoders**: Visual prompts (points/boxes) become tokens via random-Fourier positional encoding plus a learnable type embedding; text prompts are encoded by CLIP into a single token.
- **Cross-modal spatial encoder**: Each image is embedded into vision tokens via a DINOv2 backbone; a composite sequence `Zi = [Vi; Tp,i; R]` (vision, prompt, register tokens) is processed through alternating intra-view self-attention and global cross-view attention. Visual prompts are frame-specific (null-prompt embeddings elsewhere); text tokens are inserted into every frame as global context.
- **Geometry & mask decoders**: The geometry decoder (inherited from π³) predicts camera pose, pixel-aligned 3D point map, and confidence; the mask decoder (adapted from SAM) predicts instance masks, with an extra token/MLP head predicting target presence per frame.
- Training minimizes a weighted sum of segmentation loss and geometry loss (point reconstruction, confidence, normal, camera pose).

## 📊 Results

### Promptable Instance Spatial Tracking (InsTrack val)

원논문 Table 1. Spatial mIoU / Spatial Success Rate (higher better); reconstruction Abs. Rel (lower better) and τ (higher better).

| Method      | Text (S-mIoU/S-SR) | Visual (S-mIoU/S-SR) | Overall (S-mIoU/S-SR) | Abs. Rel ↓ | τ ↑   |
| ----------- | ------------------ | -------------------- | --------------------- | ---------- | ----- |
| ReferFormer | 37.6 / 43.7        | – / –                | 37.6 / 43.7           | –          | –     |
| ReferDINO   | 41.7 / 48.2        | – / –                | 41.7 / 48.2           | –          | –     |
| Cutie-base  | – / –              | 42.7 / 51.9          | 42.7 / 51.9           | –          | –     |
| SAM2        | – / –              | 47.6 / 53.1          | 47.6 / 53.1           | –          | –     |
| VGGT        | – / –              | – / –                | – / –                 | 2.67       | 85.87 |
| Pi3 (π³)    | – / –              | – / –                | – / –                 | 2.54       | 86.72 |
| **G2TAM**   | 72.3 / 77.6        | 75.8 / 81.2          | 74.3 / 80.1           | 2.51       | 86.91 |

G2TAM reaches 74.3 overall S-mIoU vs SAM2's 47.6 (visual), while also improving reconstruction over π³ and VGGT.

### 3D Visual Grounding (zero-shot, top-1 accuracy)

원논문 Table 2. Acc@0.25 / Acc@0.5 without ground-truth proposals. Higher is better.

| Method       | SR3D @0.25 | SR3D @0.5 | NR3D @0.25 | NR3D @0.5 | ScanRefer @0.25 | ScanRefer @0.5 |
| ------------ | ---------- | --------- | ---------- | --------- | --------------- | -------------- |
| 3D-VisTA     | 56.5       | 51.5      | 47.7       | 42.2      | 51.0            | 46.2           |
| VLM-Grounder | –          | –         | 48.0       | –         | 51.6            | 32.8           |
| **G2TAM**    | 57.2       | 48.7      | 51.4       | 45.8      | 56.2            | 45.7           |

G2TAM leads on NR3D and ScanRefer and maintains a smaller Acc@0.25→Acc@0.5 gap (10.5 on ScanRefer vs VLM-Grounder's 18.8), but 3D-VisTA — trained and evaluated on the same data — remains higher on SR3D Acc@0.5 (51.5 vs 48.7).

### Semi-Supervised VOS (J&F / G)

원논문 Table 4. Higher is better.

| Method    | MOSE val | DAVIS 2017 | SA-V val | SA-V test | YTVOS 2019 |
| --------- | -------- | ---------- | -------- | --------- | ---------- |
| SAM 2     | 75.2     | 89.4       | 75.8     | 76.7      | 87.8       |
| **G2TAM** | 77.8     | 89.9       | 76.8     | 77.6      | 89.1       |

The largest gain is on MOSE (heavy occlusion): 75.2 → 77.8.

### Monocular Depth (Abs Rel ↓ / δ<1.25 ↑)

원논문 Table 8. Scale-invariant monocular depth on additional datasets.

| Method    | Sintel AbsRel ↓ | Sintel δ ↑ | KITTI AbsRel ↓ | KITTI δ ↑ | NYU-v2 AbsRel ↓ | NYU-v2 δ ↑ |
| --------- | --------------- | ---------- | -------------- | --------- | --------------- | ---------- |
| VGGT      | 0.335           | 0.599      | 0.082          | 0.947     | 0.056           | 0.951      |
| Pi3       | 0.277           | 0.614      | 0.060          | 0.971     | 0.054           | 0.956      |
| **G2TAM** | 0.275           | 0.616      | 0.059          | 0.973     | 0.052           | 0.959      |

## 💡 Insights & Impact

- **Geometry stabilizes tracking under viewpoint change**: Conventional appearance-driven VOS models fall below 50 S-mIoU under large viewpoint changes / long occlusions, whereas geometry-grounded implicit memory maintains identity — and joint training improves segmentation by 4.0% over a segmentation-only variant.
- **Early fusion beats late fusion**: Injecting text at the encoding stage (cross-modal spatial encoder) outperforms a late-fusion SegPi3 baseline (72.3 vs 61.8 on InsTrack Text), and injecting text globally across all frames is best.
- **Explicit memory is not uniformly helpful**: Adding a SAM2-style explicit memory bank helps some VOS splits but degrades others, suggesting geometry-aligned implicit memory already captures most of the benefit. G2TAM adds moderate overhead over SAM2 (4 GB / 21.6 FPS vs 3 GB / 30.2 FPS) for its extra capabilities.

## 🔗 Related Work

- **[π³ / Pi3](../reconstruction/pi3.md)**: The permutation-equivariant reconstruction backbone G2TAM builds on and extends with segmentation.
- **[VGGT](../reconstruction/vggt.md)** & **[DUSt3R](../foundation/dust3r.md)**: Feed-forward geometry foundations compared for reconstruction/depth.
- **[MonST3R](../dynamic/monst3r.md)** & **[Fast3R](../reconstruction/fast3r.md)**: Related feed-forward geometry models in the monocular-depth comparison.

## 📚 Key Takeaways

1. G2TAM treats spatially aligned geometry as implicit memory, unifying reconstruction and promptable instance tracking in 3D without explicit temporal memory banks.
2. A cross-modal spatial encoder with early prompt fusion enables text/point/box prompting; joint reconstruction+segmentation training yields robust cross-view identity, reaching 74.3 overall S-mIoU vs SAM2's 47.6.
3. Beyond tracking, G2TAM sets strong zero-shot 3D visual grounding, semi-supervised/referring VOS, and monocular depth results, though it does not dominate every metric (e.g. 3D-VisTA on SR3D Acc@0.5).

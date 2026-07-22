# Flow3r: Factored Flow Prediction for Scalable Visual Geometry Learning (CVPR 2026)

![flow3r — architecture](https://arxiv.org/html/2602.20157/x1.png)

_Mechanisms for flow prediction (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Zhongxiao Cong, Qitao Zhao, Minsik Jeon, Shubham Tulsiani
- **Institution**: Carnegie Mellon University
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2602.20157) | [Project Page](https://flow3r-project.github.io/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A framework that augments feed-forward visual geometry learning with dense 2D correspondence ("flow") supervision from ~800K unlabeled videos, using a factored flow prediction module (source-view geometry latents conditioned on target-view camera latents) that directly guides geometry/pose learning and extends naturally to dynamic scenes.

## 🎯 Key Contributions

1. **Factored flow prediction**: Predicts flow between two images using geometry latents from one view and pose latents from the other, providing stronger geometry/pose supervision than tracking-style or projection-based flow.
2. **Scalable learning from unlabeled video**: Uses pseudo-ground-truth 2D flow (from a UFM teacher) to supervise ~800K unlabeled videos alongside labeled 3D data, without geometry/pose labels.
3. **Dynamic-scene generalization**: The learned factored flow implicitly captures both camera motion and scene motion, enabling in-the-wild dynamic reconstruction where labeled data is scarce.
4. **Backbone-agnostic gains**: Integrates into π³ and VGGT backbones, with state-of-the-art results across eight static/dynamic benchmarks.

## 🔧 Technical Details

### Factored Flow vs. Alternatives

- **Flow as visual correspondence (tracking)**: VGGT-style matching head over pairwise patch features — encourages discriminative features but does not aid geometry/pose learning.
- **Flow from explicit camera+scene geometry (projective)**: Analytically projects pointmaps into the target view; restricted to static scenes and sensitive to geometric errors.
- **Factored flow (Ours)**: `F̂_{i→j} = Φ_flow(g_i, c_j)` — modulates source geometry latents `g_i` by target camera latents `c_j`, decoded by a DPT head; bypasses explicit decoding, robust, and handles dynamic scenes.

### Architecture and Supervision

- Built on permutation-equivariant π³ (primary) and VGGT backbones; DINOv2 encoder, multi-view transformer, camera + geometry heads.
- **Labeled data**: supervise cameras and geometry (`L_sup = Σ λ_cam L_cam + λ_geo L_geo`); π³-style local-coordinate/optimal-alignment losses.
- **Flow supervision**: robust Charbonnier regression against pseudo-GT correspondences (UFM teacher) on both labeled and unlabeled data.
- **Two-stage training**: (1) freeze backbone, train the appended flow head on labeled data; (2) unfreeze, end-to-end finetune on labeled + unlabeled data.
- **Data**: ~34K labeled sequences across 11 datasets; ~800K unlabeled video sequences from Kinetics-700, SpatialVID, EPIC-Kitchens.

## 📊 Results

### Flow Mechanism Comparison (원논문 Table 1)

원논문 Table 1. Static=ScanNet++, Dynamic=OmniWorld. Static의 RRA/RTA는 [0,1], Dynamic은 백분율 표기(원문 그대로).

| Model Variant   | St RRA@30 ↑ | St RTA@30 ↑ | St CD ↓   | St MSE ↓  | Dy RRA@30 ↑ | Dy RTA@30 ↑ | Dy CD ↓   | Dy MSE ↓  |
| --------------- | ----------- | ----------- | --------- | --------- | ----------- | ----------- | --------- | --------- |
| 3d-sup          | 0.7500      | 0.6929      | 0.030     | 0.088     | 66.01       | 62.37       | 0.105     | 0.637     |
| flow-projective | 0.6700      | 0.4572      | 0.033     | 0.088     | 61.23       | 56.12       | 0.158     | 0.710     |
| flow-tracking   | 0.7438      | 0.7021      | 0.030     | 0.089     | 68.56       | 62.95       | 0.107     | 0.628     |
| flow-factored   | **0.7700**  | **0.7366**  | **0.026** | **0.078** | **76.26**   | **68.84**   | **0.103** | **0.598** |

### Dynamic Datasets — Kinetics700 & EPIC-KITCHENS (원논문 Table 2)

원논문 Table 2 (일부). RPE trans↓, RPE rot↓, MSE↓, f-score@5↑.

| Method | K700 trans ↓ | K700 rot ↓ | K700 MSE ↓ | K700 f-score ↑ | EPIC trans ↓ | EPIC rot ↓ | EPIC MSE ↓ | EPIC f-score ↑ |
| ------ | ------------ | ---------- | ---------- | -------------- | ------------ | ---------- | ---------- | -------------- |
| DUSt3R | 0.063        | 9.343      | 0.366      | 0.533          | 0.110        | 8.492      | 0.312      | 0.528          |
| CUT3R  | 0.027        | 1.988      | 0.303      | 0.573          | 0.081        | 4.709      | 0.338      | 0.493          |
| VGGT   | 0.038        | 1.392      | 0.347      | 0.479          | 0.049        | 3.025      | 0.220      | 0.617          |
| π³     | 0.023        | 1.006      | 0.267      | 0.585          | 0.043        | 3.025      | 0.200      | 0.620          |
| Flow3r | **0.018**    | **0.830**  | **0.256**  | **0.599**      | **0.037**    | **2.729**  | **0.199**  | **0.622**      |

### Dynamic Datasets — Sintel & Bonn (원논문 Table 2)

원논문 Table 2 (일부). Sintel MSE에서는 π³(0.267)이 Flow3r(0.404)보다 낮고, Bonn RPE rot에서는 VGGT(6.021)가 Flow3r(6.262)보다 낮다.

| Method | Sintel trans ↓ | Sintel rot ↓ | Sintel MSE ↓ | Sintel f-score ↑ | Bonn trans ↓ | Bonn rot ↓ | Bonn MSE ↓ | Bonn f-score ↑ |
| ------ | -------------- | ------------ | ------------ | ---------------- | ------------ | ---------- | ---------- | -------------- |
| DUSt3R | 0.179          | 15.166       | 0.622        | 0.271            | 0.113        | 6.384      | 0.116      | 0.800          |
| CUT3R  | 0.128          | 1.998        | 0.676        | 0.217            | 0.095        | 6.349      | 0.088      | 0.899          |
| VGGT   | 0.086          | 1.220        | 0.595        | 0.311            | 0.096        | **6.021**  | 0.082      | 0.884          |
| π³     | 0.066          | 1.122        | **0.523**    | 0.317            | 0.095        | 6.240      | 0.076      | 0.905          |
| Flow3r | **0.058**      | **0.920**    | 0.426        | **0.404**        | **0.094**    | 6.262      | **0.052**  | **0.954**      |

### Static Datasets — Co3Dv2 & Scannet (원논문 Table 3)

원논문 Table 3 (일부). RTA@30↑, AUC@30↑, MSE↓, f-score@5↑. Co3Dv2 AUC에서 π³(90.53)이, Scannet RTA/AUC에서 VGGT(93.71/71.37)가 Flow3r보다 높다.

| Method | Co3D RTA ↑ | Co3D AUC ↑ | Co3D MSE ↓ | Co3D f-score ↑ | ScNet RTA ↑ | ScNet AUC ↑ | ScNet MSE ↓ | ScNet f-score ↑ |
| ------ | ---------- | ---------- | ---------- | -------------- | ----------- | ----------- | ----------- | --------------- |
| DUSt3R | 90.68      | 68.11      | 0.223      | 0.783          | 57.14       | 31.56       | 0.092       | 0.831           |
| CUT3R  | 90.68      | 68.11      | 0.278      | 0.737          | 71.39       | 42.30       | 0.132       | 0.740           |
| VGGT   | 97.27      | 87.62      | 0.151      | 0.874          | **93.71**   | **71.37**   | 0.053       | 0.931           |
| π³     | 97.49      | **90.53**  | 0.151      | 0.874          | 91.14       | 69.39       | 0.058       | 0.930           |
| Flow3r | **97.62**  | 90.41      | **0.150**  | **0.876**      | 92.89       | 71.00       | **0.053**   | **0.943**       |

### Static Datasets — NRGBD & 7-Scenes (원논문 Table 3)

원논문 Table 3 (일부).

| Method | NRGBD RTA ↑ | NRGBD AUC ↑ | NRGBD MSE ↓ | NRGBD f-score ↑ | 7Sc RTA ↑ | 7Sc AUC ↑ | 7Sc MSE ↓ | 7Sc f-score ↑ |
| ------ | ----------- | ----------- | ----------- | --------------- | --------- | --------- | --------- | ------------- |
| DUSt3R | 93.25       | 76.04       | 0.063       | 0.865           | 76.59     | 55.07     | 0.170     | 0.714         |
| CUT3R  | 95.63       | 76.90       | 0.075       | 0.808           | 81.15     | 59.72     | 0.183     | 0.695         |
| VGGT   | 99.21       | 93.13       | 0.032       | 0.964           | 86.51     | 69.77     | 0.182     | 0.665         |
| π³     | 99.20       | 90.40       | 0.021       | 0.983           | 87.69     | 71.80     | 0.169     | 0.737         |
| Flow3r | **99.60**   | **94.40**   | **0.018**   | **0.992**       | **91.66** | **75.76** | **0.102** | **0.807**     |

### Scaling with Unlabeled Videos (원논문 Table 4)

원논문 Table 4. OmniWorld(labeled) + SpatialVID(unlabeled). RRA@30↑, RTA@30↑, CD↓, MSE↓.

| Labeled      | Unlabeled      | RRA@30 ↑ | RTA@30 ↑ | CD ↓  | MSE ↓ |
| ------------ | -------------- | -------- | -------- | ----- | ----- |
| OmniWorld 1K | –              | 66.01    | 62.37    | 0.105 | 0.637 |
| OmniWorld 1K | SpatialVID 3K  | 76.26    | 68.84    | 0.103 | 0.598 |
| OmniWorld 1K | SpatialVID 10K | 78.45    | 68.82    | 0.077 | 0.560 |
| OmniWorld 1K | SpatialVID 20K | 81.12    | 71.21    | 0.075 | 0.532 |
| OmniWorld 4K | –              | 78.68    | 70.26    | 0.080 | 0.565 |

Notably, 1K labeled + 20K unlabeled (81.12 RRA@30) outperforms 4K labeled alone (78.68 RRA@30). A further ablation (원논문 Table 5) on both VGGT and π³ backbones disentangles multi-task learning from unlabeled data, concluding the primary gains stem from incorporating unlabeled videos via flow supervision. (Table 5의 개별 셀은 PDF 2단 레이아웃에서 열이 뒤섞여 옮기지 않음.)

## 💡 Insights & Impact

- Tracking-style flow supervision (as in VGGT) yields accurate flow but little geometry/pose benefit; factored flow is a better supervisory signal even though it is suboptimal for standalone flow estimation.
- Projection-based flow can degrade performance due to instability from errors in decoded cameras/depth.
- Flow supervision from unlabeled video scales visual geometry learning, with the largest gains on in-the-wild dynamic scenes; gains also transfer to static benchmarks.

## 🔗 Related Work

- Backbone [Pi3 (π³)](../reconstruction/pi3.md); also integrated with [VGGT](../reconstruction/vggt.md); foundation [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md).
- Dynamic-scene baselines [CUT3R](cut3r.md), [MonST3R](monst3r.md), [StreamVGGT](../reconstruction/streamvggt.md); optimization-based [ViPE](../robotics/vipe.md) cited.

## 📚 Key Takeaways

1. Factored flow prediction turns cheap 2D correspondences into effective supervision for both camera motion and scene geometry.
2. Enables scalable training from ~800K unlabeled videos, achieving SOTA across eight static/dynamic benchmarks — with honest reporting that π³/VGGT still win a few individual metrics (Sintel MSE, Bonn RPE rot, ScanNet RTA/AUC, Co3Dv2 AUC).
3. Unlabeled video via flow supervision beats simply adding more labeled data (1K+20K > 4K labeled).

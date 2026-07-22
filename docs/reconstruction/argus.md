# Argus: Metric Panoramic 3D Reconstruction for Indoor Scenes (arXiv preprint (2026-06))

![argus — architecture](https://arxiv.org/html/2606.30047v3/x2.png)

_Overview of Argus (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Xi Li, Linyuan Li, Yan Wu, Tong Rao, Kai Zhang, Xinchen Hui, Cihui Pan
- **Institution**: Realsee, China; Quanzhou University of Information Engineering, China
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.30047) | [Project Page](https://argus-paper.realsee.ai) | [Dataset](https://dataset.realsee.ai)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward network for metric panoramic (ERP) 3D reconstruction of indoor scenes, trained on the new large-scale Realsee3D dataset (10K scenes, 299K panoramic viewpoints), using a learned covisibility module to pick the optimal reference view and an overcomplete geometric factorization supervision to decompose pixel-to-world mapping into individually supervised sub-steps.

## 🎯 Key Contributions

1. **Realsee3D dataset**: A large-scale indoor panoramic RGB-D dataset with metric annotations — 10,000 scenes (1,000 real, 9,000 synthetic), 95,962 rooms, 299,073 panoramic viewpoints.
2. **Argus network**: A data-driven feed-forward model for metric panoramic 3D reconstruction from unordered indoor panoramas in a single forward pass.
3. **Covisibility-based reference view learning**: A learnable module that predicts inter-view connectivity to dynamically anchor the metric world frame at the geometrically optimal reference view, suppressing global pose drift from degenerate (corner/boundary) viewpoints while retaining approximate permutation equivariance.
4. **Overcomplete geometric factorization supervision**: Decomposes forward and inverse pixel-to-world transformations under the panoramic model into interpretable sub-steps, each supervised independently and jointly across coordinate frames to boost multi-task synergy.

## 🔧 Technical Details

### Architecture

- DINOv2 produces patch tokens. Covisibility tokens are added per view and processed by a lightweight **Covisibility Transformer** (Lc = 2 alternating-attention layers) → MLP → covisibility scores; the argmax view becomes the reference frame (its tokens swapped with the fixed first-frame slot for permutation-invariance).
- The aggregated tokens pass through a **Geometry Transformer** (Lg = 24 alternating-attention layers). Camera poses are regressed by an MLP as a 9-D vector per view (3-D translation, 4-D quaternion, 2 confidence scores for rotation and translation); depth and point maps across coordinate systems come from distinct DPT heads, each with a pixel-wise confidence channel.
- Depth head uses exp(·) for positivity; point-map heads use an inverse-log transform f(x) = sign(x)·(exp(|x|)−1); confidences use 1 + exp(·) (lower bound 1).

### Panoramic geometric factorization

- For W×H ERP panoramas, pixels map to spherical (θ, ϕ) to form unit-sphere points P_u; the pixel-to-world map is decomposed into supervised steps: Φ_{D→CP} (P_c = D⊙P_u), Φ_{CP→RP} (P_r = R·P_c), Φ_{RP→WP} (P_w = P_r + t), and their inverses, plus Φ_{CP→D} (D = ‖P_c‖₂).
- The fixed ERP projection removes focal/depth intrinsic ambiguity, enabling direct metric prediction without a separate scale module; ground-truth scale is normalized (e.g. divide by s = 10) during supervision.

### Training

- Losses: covisibility (BCE), camera (confidence-weighted quaternion + translation L1), depth (aleatoric-uncertainty L2 + gradient), multiple point-map losses (camera/rotated/world coords), and a geometry joint loss enforcing cross-branch consistency. Total: L = 0.1·L_covis + 5.0·L_cam + L_d + L_cp + L_rp + L_wp + L_joint; confidence regularization weight α = 0.2.
- AdamW, 99K iterations, cosine schedule peak LR 5e-5 with 9.9K warmup, 2–28 random views per batch, ERP resized to 560×280 then poles cropped (top/bottom 15%) to 560×196, on 24 H20 (141GB) GPUs over 36 hours; BF16, gradient checkpointing, grad-norm clip 1.0. Model has 1.31 billion parameters.
- Baselines are VGGT, MapAnything (V1.1.1, image-only) and π³ finetuned on Realsee3D (denoted VGGT360, MapAnything360, π³360); COLMAP/OpenMVG were too slow to be usable and were omitted.

## 📊 Results

### Realsee3D dataset scale

원논문 Table 1.

| Dataset               | Type               | Scenes | Rooms  | Unique Viewpoints | Images  |
| --------------------- | ------------------ | ------ | ------ | ----------------- | ------- |
| Stanford2D3D          | Real               | 6      | 270    | 1,413             | 1,413   |
| Matterport3D          | Real               | 90     | 2,056  | 10,800            | 10,800  |
| ZInD                  | Real (Unfurnished) | 1,524  | –      | 71,474            | 71,474  |
| Structured3D          | Synthetic          | 3,500  | 21,835 | 21,835            | 196,515 |
| Realsee3D (Real)      | Real (Furnished)   | 1,000  | 9,483  | 24,263            | 24,263  |
| Realsee3D (Synthetic) | Synthetic          | 9,000  | 86,479 | 274,810           | 274,810 |
| Realsee3D (Total)     | Hybrid             | 10,000 | 95,962 | 299,073           | 299,073 |

### Camera pose estimation

원논문 Table 2. Argus achieves the best metric pose accuracy (ATE↓, A.R.↑) on both subsets and leads AUC on the synthetic subset. On the real subset, π³360 shows marginally higher relative metrics (RRA/RTA/AUC), which the authors attribute to its stronger pre-training prior. A.R. = share of scenes with all rotation errors < 10° and translation errors < 0.5 m.

| Subset    | Method         | AUC@5↑ | AUC@10↑ | ATE↓  | A.R.↑ |
| --------- | -------------- | ------ | ------- | ----- | ----- |
| Real      | VGGT360        | 67.89  | 83.00   | –     | –     |
| Real      | MapAnything360 | 72.66  | 85.37   | 0.134 | 94.0  |
| Real      | π³360          | 72.39  | 85.92   | –     | –     |
| Real      | **Ours**       | 71.88  | 85.52   | 0.096 | 98.2  |
| Synthetic | VGGT360        | 91.10  | 95.38   | –     | –     |
| Synthetic | MapAnything360 | 90.84  | 95.11   | 0.087 | 99.3  |
| Synthetic | π³360          | 93.46  | 96.58   | –     | –     |
| Synthetic | **Ours**       | 94.44  | 97.29   | 0.027 | 99.8  |

The paper states Argus reduces ATE vs MapAnything360 by 28% on the real subset and 69% on the synthetic subset.

### Multi-view depth estimation

원논문 Table 3 (IRLS alignment). Argus outperforms all baselines on every metric. δ1 = δ<1.03, δ2 = δ<1.25.

| Subset    | Method         | AbsRel↓ | δ1↑   | RMSE↓ | MAE↓  |
| --------- | -------------- | ------- | ----- | ----- | ----- |
| Real      | VGGT360        | 0.051   | 64.22 | 0.445 | 0.119 |
| Real      | MapAnything360 | 0.063   | 54.75 | 0.541 | 0.126 |
| Real      | π³360          | 0.053   | 58.63 | 0.454 | 0.129 |
| Real      | **Ours**       | 0.048   | 70.22 | 0.401 | 0.102 |
| Synthetic | VGGT360        | 0.025   | 86.60 | 0.158 | 0.035 |
| Synthetic | MapAnything360 | 0.034   | 76.47 | 0.165 | 0.042 |
| Synthetic | π³360          | 0.033   | 78.14 | 0.192 | 0.052 |
| Synthetic | **Ours**       | 0.019   | 91.42 | 0.138 | 0.027 |

### Point map reconstruction

원논문 Table 4 (ICP alignment, Mean values). Acc.↓ / Comp.↓ / Normal Consistency↑.

| Subset    | Method         | Acc.↓ | Comp.↓ | N.C.↑ |
| --------- | -------------- | ----- | ------ | ----- |
| Real      | VGGT360        | 0.058 | 0.074  | 0.884 |
| Real      | MapAnything360 | 0.082 | 0.127  | 0.829 |
| Real      | π³360          | 0.058 | 0.078  | 0.868 |
| Real      | **Ours**       | 0.058 | 0.062  | 0.894 |
| Synthetic | VGGT360        | 0.023 | 0.016  | 0.923 |
| Synthetic | MapAnything360 | 0.038 | 0.053  | 0.880 |
| Synthetic | π³360          | 0.030 | 0.018  | 0.888 |
| Synthetic | **Ours**       | 0.018 | 0.014  | 0.943 |

### Efficiency

원논문 Table 5. Runtime and peak GPU memory vs number of input frames (excludes the 4.64GB pretrained-model load; BF16 inference).

| # Images    | 1    | 2    | 4    | 8    | 16   | 32   | 64   | 128   |
| ----------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ----- |
| Runtime (s) | 0.11 | 0.13 | 0.18 | 0.32 | 0.66 | 1.47 | 3.67 | 10.55 |
| Memory (GB) | 2.05 | 2.24 | 2.60 | 3.38 | 3.54 | 3.88 | 4.55 | 7.22  |

The extra cross-coordinate DPT heads can be disabled at inference (optimal performance needs only pose and depth heads), so multi-head supervision adds zero inference overhead.

### Ablation (synthetic subset)

원논문 Table 6. Removing reference-view learning more than doubles ATE (0.027 → 0.060); dropping L_joint raises AbsRel 0.035 → 0.047 and ATE 0.027 → 0.049; removing all three point-map losses (L_cp & L_rp & L_wp) is worst (AbsRel 0.075, RMSE 0.169). Removing L_cp alone hurts more than removing L_rp alone.

| Method                      | AbsRel↓ | δ1↑   | RMSE↓ | ATE↓  |
| --------------------------- | ------- | ----- | ----- | ----- |
| Full                        | 0.035   | 91.24 | 0.139 | 0.027 |
| w/o reference view learning | 0.037   | 90.45 | 0.142 | 0.060 |
| w/o L_joint                 | 0.047   | 90.71 | 0.158 | 0.049 |
| w/o L_cp                    | 0.055   | 89.90 | 0.161 | 0.047 |
| w/o L_rp                    | 0.045   | 90.55 | 0.159 | 0.051 |
| w/o L_cp & L_rp             | 0.055   | 89.75 | 0.160 | 0.048 |
| w/o L_cp & L_rp & L_wp      | 0.075   | 88.52 | 0.169 | 0.061 |

## 💡 Insights & Impact

- Addresses a genuine gap: mainstream feed-forward models (VGGT etc.) are trained on perspective RGB-D and degrade severely on panoramas, largely for lack of large-scale metric panoramic training data — which Realsee3D supplies.
- The learned covisibility anchor tackles the specific failure of heuristic reference selection in sparse unordered capture: a boundary/corner anchor causes global pose drift; picking a well-connected central view stabilizes the metric world frame (ablation: ATE halves).
- The fixed ERP projection removes intrinsic ambiguity, making direct metric prediction feasible without a separate scale-estimation module.
- Acknowledged limitations: indoor-focused training limits zero-shot generalization to unbounded outdoor/aerial scenes, and memory scaling limits reconstruction from very large panorama sets (hundreds to thousands of views).

## 🔗 Related Work

- **[VGGT](./vggt.md)**: alternating-attention multi-view backbone Argus builds on (initialized from VGGT weights; VGGT360 is a finetuned baseline).
- **[MapAnything](./mapanything.md)**: universal metric feed-forward reconstruction with prior inputs; a main baseline (MapAnything360).
- **[π³](./pi3.md)**: permutation-equivariant design for unordered inputs, contrasted with Argus's learned covisibility anchor; a main baseline (π³360).
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: foundational feed-forward pointmap regression and its SfM extension cited as lineage.
- **[Pow3R](./pow3r.md)** / **[TTT3R](./ttt3r.md)**: cited among recent feed-forward reconstruction works.

## 📚 Key Takeaways

1. Argus brings feed-forward metric 3D reconstruction to panoramic (ERP) indoor scenes, enabled by the new 299K-viewpoint Realsee3D dataset.
2. A learned covisibility module anchors the metric world frame at the optimal reference view, cutting pose drift on sparse unordered captures (ablation halves ATE).
3. Overcomplete geometric factorization supervision decomposes pixel-to-world mapping into individually supervised sub-steps that boost training-time multi-task synergy at zero inference cost, yielding best overall pose, depth and point-map metrics on Realsee3D — with the one exception that π³360 edges Argus on real-subset relative pose metrics.

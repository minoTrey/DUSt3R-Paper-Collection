# VGTW: Visual Geometry Transformer in the Wild — Distractor-Free 3D Reconstruction (arXiv preprint 2026-06)

## 📋 Overview

- **Authors**: Tianbo Pan, Xingyi Yang, Shizun Wang, Xinchao Wang
- **Institution**: National University of Singapore; The Hong Kong Polytechnic University
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.22787) | [Project Page](https://tianbo-pan.github.io/vgt-w/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An end-to-end framework that fine-tunes feed-forward reconstruction backbones (VGGT, π³) to isolate and suppress transient-distractor regions in attention, directly outputting clean, distractor-free point clouds with only 2D mask supervision.

## 🎯 Key Contributions

1. **Distractor-free feed-forward reconstruction**: VGTW reconstructs static 3D scenes from in-the-wild images containing transient distractors (moving people, objects), where static-scene-assuming methods fail.
2. **Distractor-aware Training (DAT)**: A strategy that fine-tunes the attention mechanism to separate clean features from distractor-contaminated ones, guided by a Distractor Suppression Loss and a Cross-View Consistency Loss.
3. **RobustNeRF-Mask dataset**: A new public dataset of multi-view images with pixel-perfect distractor masks to train and evaluate the auxiliary mask prediction head.
4. **2D-only supervision, no extra 3D labels**: Because supervision is purely 2D, the model learns to identify distractors without any additional 3D supervision, stays computationally efficient, and is compatible with existing backbones.

## 🔧 Technical Details

### Problem analysis: attention is sufficient to remove distractors

The authors observe that standard attention "leaks" to distractor regions: when querying a static region, high attention weight is assigned to distractor pixels, so the model treats distractor content as valid scene structure. Masking attention to ground-truth distractor regions removes them, motivating the approach.

### Distractor-aware Training (DAT)

DAT fine-tunes attention to suppress distractor influence, using two objectives: a Distractor Suppression Loss (`Lsupp`) that penalizes attention to distractors, and a Cross-View Consistency Loss (`Lcons`) that reinforces consistency of stable scene components across views. An auxiliary mask prediction head (`headmask`) is trained on the RobustNeRF-Mask dataset. The resulting network directly outputs a clean, distractor-free point cloud.

VGTW is applied as a wrapper over two backbones: VGTW(VGGT) and VGTW(π³).

## 📊 Results

Metrics: accuracy (Acc↓), completeness (Comp↓), normal consistency (NC↑), after Umeyama alignment. 10 images randomly sampled per evaluation, mixing clean and distractor-containing images. Values below are the per-dataset Averages.

### Point map estimation on NeRF On-the-go (unseen)

원논문 Table 1 (Average columns).

| Method     | Acc↓  | Comp↓ | NC↑   |
| ---------- | ----- | ----- | ----- |
| DUSt3R     | 0.037 | 0.080 | 0.747 |
| MaSt3R     | 0.045 | 0.157 | 0.692 |
| Fast3R     | 0.041 | 0.069 | 0.680 |
| VGGT       | 0.041 | 0.146 | 0.640 |
| VGTW(VGGT) | 0.033 | 0.117 | 0.704 |
| π³         | 0.051 | 0.074 | 0.709 |
| VGTW(π³)   | 0.027 | 0.060 | 0.692 |

VGTW improves Acc/Comp over its VGGT and π³ backbones; DUSt3R retains the best NC on this unseen set.

### Point map estimation on RobustNeRF

원논문 Table 2 (Average columns).

| Method     | Acc↓  | Comp↓ | NC↑   |
| ---------- | ----- | ----- | ----- |
| DUSt3R     | 0.031 | 0.068 | 0.696 |
| MaSt3R     | 0.038 | 0.388 | 0.616 |
| Fast3R     | 0.034 | 0.105 | 0.660 |
| VGGT       | 0.021 | 0.045 | 0.684 |
| VGTW(VGGT) | 0.011 | 0.025 | 0.740 |
| π³         | 0.017 | 0.016 | 0.754 |
| VGTW(π³)   | 0.010 | 0.010 | 0.718 |

VGTW(π³) yields the lowest Acc and Comp; π³ keeps the best NC.

### Depth estimation on RobustNeRF

원논문 Table 3 (Average columns). Abs Rel lower is better; δ<1.25 higher is better.

| Method     | Abs Rel↓ | δ<1.25↑ |
| ---------- | -------- | ------- |
| DUSt3R     | 0.123    | 82.6    |
| MaSt3R     | 0.299    | 63.9    |
| Fast3R     | 0.196    | 65.6    |
| VGGT       | 0.111    | 81.1    |
| VGTW(VGGT) | 0.062    | 94.5    |
| π³         | 0.061    | 95.1    |
| VGTW(π³)   | 0.041    | 97.3    |

### Depth estimation on NeRF On-the-go (unseen), by occlusion level

원논문 Table 4 (averaged across scenes). Abs Rel↓, δ<1.25↑.

| Method     | Low Abs Rel↓ | Low δ↑ | Med Abs Rel↓ | Med δ↑ | High Abs Rel↓ | High δ↑ |
| ---------- | ------------ | ------ | ------------ | ------ | ------------- | ------- |
| DUSt3R     | 0.339        | 59.5   | 0.142        | 78.7   | 0.071         | 90.6    |
| Fast3R     | 0.524        | 47.8   | 0.155        | 76.4   | 0.119         | 81.2    |
| VGGT       | 0.500        | 45.5   | 0.246        | 58.7   | 0.252         | 64.7    |
| VGTW(VGGT) | 0.346        | 55.9   | 0.125        | 82.2   | 0.220         | 71.1    |
| π³         | 0.531        | 48.1   | 0.201        | 67.5   | 0.120         | 81.4    |
| VGTW(π³)   | 0.405        | 52.7   | 0.152        | 74.9   | 0.076         | 88.1    |

On this unseen dataset DUSt3R is best in low and high occlusion; VGTW(VGGT) leads in medium occlusion and VGTW(π³) leads in high occlusion among the transformer backbones.

### Ablation on RobustNeRF (point map)

원논문 Table 5 (RobustNeRF columns). Overall = average of Acc and Comp.

| Configuration              | Acc↓  | Comp↓ | Overall↓ | NC↑   |
| -------------------------- | ----- | ----- | -------- | ----- |
| none                       | 0.021 | 0.045 | 0.033    | 0.684 |
| + Lsupp                    | 0.021 | 0.034 | 0.028    | 0.694 |
| + Lsupp + Lcons            | 0.011 | 0.025 | 0.018    | 0.740 |
| + Lsupp + Lcons + headmask | 0.011 | 0.025 | 0.018    | 0.740 |

`Lsupp` improves Comp/Overall; `Lcons` further improves Acc and NC. On RobustNeRF the mask head gives smaller additional gains because distractors are limited (원논문 본문).

## 💡 Insights & Impact

- **Suppress in attention, not in geometry**: The core finding is that attention leakage to distractors is what corrupts static-scene reconstruction, and masking/suppressing that attention is sufficient to remove distractors.
- **Backbone-agnostic wrapper**: DAT improves both VGGT and π³, showing it generalizes across feed-forward reconstruction transformers.
- **Honest trade-off**: On the unseen NeRF On-the-go set, DUSt3R still wins several NC and low/high-occlusion depth columns; VGTW's clearest gains are in Acc/Comp and on RobustNeRF.

## 🔗 Related Work

- **[VGGT](vggt.md)** and **[π³ (pi3)](pi3.md)**: The two feed-forward backbones VGTW wraps with distractor-aware training.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**, **[Fast3R](fast3r.md)**: Feed-forward reconstruction baselines compared against.

## 📚 Key Takeaways

1. VGTW turns distractor removal into an attention-suppression problem, learned with only 2D mask supervision on the new RobustNeRF-Mask dataset.
2. Applied to VGGT and π³, it lowers Acc/Comp on both NeRF On-the-go and RobustNeRF and roughly halves depth Abs Rel on RobustNeRF.
3. The suppression and cross-view consistency losses drive most of the gain; the mask head helps more when distractors are abundant.

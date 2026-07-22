# Wat3R: Underwater 3D Geometry Learning without Annotations (ECCV 2026)

![wat3r — architecture](https://arxiv.org/html/2607.08772v1/x9.png)

_Figure A2: Synthetic underwater rendering examples (원논문 Fig. 99)_

## 📋 Overview

- **Authors**: Jiangwei Ren, Xingyu Jiang, Zijie Song, Wei Xu, Hongkai Lin, Dingkang Liang, Xiang Bai
- **Institution**: Huazhong University of Science and Technology
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.08772) | [Code](https://github.com/LSXI7/Wat3R)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A cross-domain semi-supervised (Mean Teacher) framework that adapts feed-forward reconstruction models (VGGT) from air to underwater scenes using only unlabeled real underwater video, with a cross-view consistency loss and the new Water3D benchmark.

## 🎯 Key Contributions

1. **First semi-supervised VGGT-based underwater framework**: Adapts a feed-forward reconstruction model to complex underwater environments leveraging only unlabeled real videos, with no annotated underwater 3D data.
2. **Cross-view consistency loss**: Integrates geometric cues from other related views to compensate for information degradation (light attenuation, scattering) in the current view.
3. **Water3D dataset**: A diverse underwater multi-view benchmark with comprehensive annotations (42 real scenes), built for geometric-task evaluation.

## 🔧 Technical Details

### Mean Teacher semi-supervised paradigm

The framework follows a Mean Teacher design: the teacher produces stable pseudo-labels for depth, camera parameters, and point maps to supervise the student. The student is updated by backpropagation; the teacher is an exponential moving average (EMA) of the student. Weak augmentations feed the teacher, strong (sequence-level) augmentations the student.

### Losses

Training combines (1) a supervised loss following VGGT on synthetic underwater data (computed against ground truth, using Huber loss), (2) a per-view consistency loss using teacher predictions {gᵗ, Dᵗ, Pᵗ} as pseudo-labels, and (3) a cross-view consistency loss enforcing agreement across views. A static mask `M_static` further filters unreliable regions.

### Training

4× NVIDIA RTX 4090 GPUs, 19,200 steps with a 1,000-step warm-up; peak LR 5×10⁻⁶ (ViT backbone) and 5×10⁻⁵ (head); unlabeled:labeled ratio 1:3; first 6,400 steps labeled-only, then unsupervised weight λu ramps to 0.5 at step 12,800; 2–12 images sampled per iteration, longest side resized to 518 px; gradient checkpointing + bfloat16.

## 📊 Results

### Multi-view depth estimation (Shuffle 10-view)

원논문 Table 1, Shuffle 10-view protocol. Rel/log10/RMSE lower is better; δ1 higher is better. Shaded two-stage rows enhance images first, then run VGGT.

| Methods       | Sea-thru Rel↓ | Sea-thru δ1↑ | Sea-thru log10↓ | Sea-thru RMSE↓ | FLSea Rel↓ | FLSea δ1↑ | FLSea log10↓ | FLSea RMSE↓ |
| ------------- | ------------- | ------------ | --------------- | -------------- | ---------- | --------- | ------------ | ----------- |
| Fast3r        | 0.277         | 0.713        | 0.083           | 0.631          | 0.290      | 0.529     | 0.141        | 1.355       |
| MapAnything   | 0.216         | 0.800        | 0.060           | 0.454          | 0.146      | 0.841     | 0.061        | 0.798       |
| π3            | 0.185         | 0.909        | 0.044           | 0.358          | 0.139      | 0.856     | 0.053        | 0.837       |
| DA3           | 0.187         | 0.892        | 0.046           | 0.333          | 0.141      | 0.851     | 0.056        | 0.872       |
| VGGT          | 0.190         | 0.891        | 0.047           | 0.380          | 0.137      | 0.849     | 0.059        | 0.760       |
| VGGT+Semi-UIR | 0.201         | 0.846        | 0.052           | 0.387          | 0.136      | 0.861     | 0.056        | 0.784       |
| **Wat3R**     | 0.167         | 0.946        | 0.038           | 0.290          | 0.119      | 0.885     | 0.048        | 0.720       |

Two-stage underwater-image-enhancement pipelines (VGGT+Semi-UIR/PSPL) do not reliably help; Wat3R is best on both datasets. The paper reports similar gains under the Full Subsequence (100 ordered frames) protocol (Wat3R Sea-thru Rel 0.170, δ1 0.953).

### Point map estimation on Water3D

원논문 Table 2. Accuracy/Completeness/Overall, lower is better.

| Methods           | Acc Mean↓ | Acc Median↓ | Comp Mean↓ | Comp Median↓ | Overall Mean↓ | Overall Median↓ |
| ----------------- | --------- | ----------- | ---------- | ------------ | ------------- | --------------- |
| Fast3r            | 1.216     | 0.531       | 2.444      | 0.784        | 1.830         | 0.658           |
| MapAnything       | 0.643     | 0.284       | 0.666      | 0.277        | 0.655         | 0.281           |
| π3                | 0.491     | 0.168       | 0.413      | 0.184        | 0.452         | 0.176           |
| DA3               | 0.679     | 0.187       | 0.528      | 0.160        | 0.604         | 0.174           |
| VGGT              | 0.486     | 0.193       | 0.762      | 0.191        | 0.624         | 0.192           |
| Wat3R (Point)     | 0.444     | 0.148       | 0.409      | 0.165        | 0.427         | 0.157           |
| Wat3R (Depth+Cam) | 0.446     | 0.162       | 0.366      | 0.143        | 0.406         | 0.153           |

### Camera pose estimation on SeaThru-NeRF

원논문 Table 3. AUC higher is better.

| Methods     | AUC@5°↑ | AUC@15°↑ | AUC@30°↑ |
| ----------- | ------- | -------- | -------- |
| Fast3r      | 0.040   | 0.239    | 0.498    |
| π3          | 0.216   | 0.635    | 0.809    |
| DA3         | 0.731   | 0.901    | 0.950    |
| MapAnything | 0.074   | 0.458    | 0.707    |
| VGGT        | 0.392   | 0.707    | 0.843    |
| **Wat3R**   | 0.540   | 0.820    | 0.906    |

Here DA3 achieves the best pose AUC across all thresholds (its depth-ray representation is well suited to underwater geometry); Wat3R is second and clearly improves over its VGGT base (AUC@5° 0.392 → 0.540).

### Monocular depth estimation

원논문 Table 4. Rel lower is better; δ1 higher is better. DAv2 is a monocular-depth specialist.

| Methods     | FLSea-VI Rel↓ | FLSea-VI δ1↑ | FLSea-St Rel↓ | FLSea-St δ1↑ | SQUID Rel↓ | SQUID δ1↑ | Sea-thru Rel↓ | Sea-thru δ1↑ |
| ----------- | ------------- | ------------ | ------------- | ------------ | ---------- | --------- | ------------- | ------------ |
| DAv2        | 0.069         | 0.958        | 0.134         | 0.849        | 0.099      | 0.900     | 0.089         | 0.940        |
| MapAnything | 0.086         | 0.951        | 0.146         | 0.837        | 0.104      | 0.898     | 0.104         | 0.960        |
| π3          | 0.081         | 0.944        | 0.148         | 0.831        | 0.234      | 0.640     | 0.113         | 0.949        |
| DA3         | 0.090         | 0.936        | 0.154         | 0.824        | 0.151      | 0.802     | 0.111         | 0.950        |
| VGGT        | 0.107         | 0.888        | 0.159         | 0.809        | 0.194      | 0.703     | 0.113         | 0.942        |
| **Wat3R**   | 0.061         | 0.971        | 0.120         | 0.886        | 0.107      | 0.893     | 0.090         | 0.976        |

Wat3R leads the general/underwater feed-forward models despite having no single-image supervision; the monocular specialist DAv2 remains slightly ahead on SQUID (Rel 0.099 / δ1 0.900).

### Ablation of components

원논문 Table 5. Multi-view depth; Rel lower is better, δ1 higher is better.

| Components                                     | Sea-thru Rel↓ | Sea-thru δ1↑ | FLSea Rel↓ | FLSea δ1↑ |
| ---------------------------------------------- | ------------- | ------------ | ---------- | --------- |
| VGGT (baseline)                                | 0.190         | 0.891        | 0.137      | 0.849     |
| + Syn Water                                    | 0.173         | 0.920        | 0.135      | 0.860     |
| + Syn + Real Video                             | 0.181         | 0.906        | 0.165      | 0.793     |
| + Syn + Real + Strong Aug                      | 0.172         | 0.936        | 0.126      | 0.871     |
| + Syn + Real + Aug + Lcross-view               | 0.167         | 0.949        | 0.126      | 0.869     |
| + Syn + Aug + Lcross-view + M_static (no Real) | 0.174         | 0.929        | 0.130      | 0.871     |
| **Wat3R (all)**                                | 0.167         | 0.946        | 0.119      | 0.885     |

Synthetic underwater rendering already improves over VGGT; real video plus strong augmentation and the cross-view consistency loss drive further gains.

## 💡 Insights & Impact

- **Annotation-free domain transfer**: Wat3R shows a strong air-trained feed-forward model can be adapted to underwater imaging purely from unlabeled real video via consistency-driven teacher-student learning.
- **Cross-view cues beat single-view enhancement**: Two-stage underwater-image-enhancement pipelines fail to reliably improve geometry, whereas exploiting multi-view geometric consistency does.
- **Representation matters for pose**: DA3's depth-ray formulation still wins underwater pose estimation, indicating room for geometry-representation improvements on top of Wat3R's adaptation.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The feed-forward backbone Wat3R adapts to underwater scenes.
- **[π³ (pi3)](pi3.md)**, **[Fast3R](fast3r.md)**, **[Depth Anything 3 (DA3)](depth-anything-3.md)**: Feed-forward reconstruction / depth baselines compared across underwater tasks.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: Foundational feed-forward reconstruction lineage.

## 📚 Key Takeaways

1. Wat3R adapts VGGT to underwater geometry with zero underwater annotations, using a Mean Teacher scheme and a cross-view consistency loss.
2. It is best on multi-view and monocular depth and on Water3D point maps, and second-best (behind DA3) on underwater camera pose.
3. The new Water3D benchmark (42 real scenes) supplies the missing evaluation resource for underwater geometric reconstruction.

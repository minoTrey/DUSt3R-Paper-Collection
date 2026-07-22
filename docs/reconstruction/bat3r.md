# BAT3R: Bootstrapping Articulated 3D Reconstruction from 2D Image Collections (ECCV 2026)

![bat3r — architecture](https://arxiv.org/html/2607.03891v1/x1.png)

_While effective, supervised approaches for 3D shape estimation from 2D images rely on the availability of large manually crafted and curated 3D shape… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Jakub Zadrozny, Oisin Mac Aodha, Hakan Bilen
- **Institution**: University of Edinburgh
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.03891) | [Project Page](https://jakubzadrozny.github.io/bat3r)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A training framework for single-image articulated 3D reconstruction that needs only one rigged canonical mesh per category plus an unannotated 2D image collection — it iteratively fits the canonical mesh to DualPM point-map predictions, renders the recovered articulations/viewpoints as new synthetic training data, and progressively improves the predictor, reaching performance comparable to DualPM which requires manually curated articulated 3D datasets.

## 🎯 Key Contributions

1. **BAT3R bootstrapping framework**: Automatically generates paired 2D–3D training data for category-centric image-to-3D shape prediction, removing the need for expensive, manually created articulated 3D training data — only a single rigged canonical mesh and an image collection are required.
2. **Iterative refinement**: Alternates between fitting the canonical mesh to point-cloud predictions on the 2D collection and rendering the fitted meshes into new self-annotated training pairs, progressively increasing pose complexity and closing the gap to fully supervised baselines.
3. **Comparable accuracy under far weaker supervision**: Despite orders-of-magnitude less 3D supervision, models trained this way approach fully supervised DualPM and outperform other category-specific and large foundation baselines.

## 🔧 Technical Details

### Reconstruction model (DualPM)

- Builds on DualPM: for each foreground pixel the network predicts K ray-surface intersection points, each with a posed point P_k(u) (camera frame) and a canonical point Q_k(u) (rest-pose frame). The posed map gives the reconstruction; the canonical map gives dense canonical↔posed correspondences that drive mesh fitting.
- Trained with a confidence-weighted regression loss L_DualPM = L_P + L_Q.

### Bootstrapping procedure

- **Initialization (Φ0)**: render the single canonical rigged mesh from many sampled camera viewpoints (heavy-tailed Student's t sampling to expose extreme viewpoints), with a hand-crafted or AI-generated texture and sampled environment maps, to train an initial weak predictor.
- **Inference + mesh fitting**: for each image, predict dual point clouds; subsample to 200 control points via topology-aware farthest-point sampling using a surface-grounded distance (Euclidean + geodesic). A Kabsch global rigid transform T_g initializes alignment, then articulation parameters θ (excess joint rotations) and per-bone scales S are optimized.
- **Fitting loss**: L = L_data (Huber, δ = 0.1) + λ_angle‖θ‖² + λ_vol·L_vol + λ_edge·L_edge + λ_scale·L_scale + λ_rep·L_rep. Bone scales S are auxiliary and discarded; the unscaled articulated mesh becomes the next iteration's training target. Self-repulsion (L_rep) prevents self-intersections from noisy early predictions.
- **Viewpoint augmentation**: fitted meshes are rendered from multiple novel viewpoints (lateral views fit better than frontal/rear) to build the next training set. Typically 4 refinement iterations.

### Data

- Synthetic: horse/cow/sheep using DualPM's exact splits and canonical assets (ground-truth articulations/poses withheld — recovered by the refinement).
- Real in-the-wild: ~11,000 horse images (MagicPony), ~19,000 chimpanzee (AP-10K + OpenApePose), ~21,000 elephant (Wild Elephant Dataset + YouTube frames).

## 📊 Results

Metric: RMS bi-directional Chamfer Distance (cm, ↓), under full rigid ICP alignment and model-view alignment (scale + translation only, penalizing bad camera pose). DualPM is the fully supervised upper bound.

### Animodel-Points (synthetic training)

원논문 Table 1. "Canonical" = trained only on canonical-mesh renders; "Ours (synt)" = trained on DualPM's synthetic image splits without accessing ground-truth articulations. Ours (synt) is second-best behind fully supervised DualPM and beats all other baselines.

| Method          | Horse RMS CD | Cow RMS CD   | Sheep RMS CD | Horse MV RMS CD |
| --------------- | ------------ | ------------ | ------------ | --------------- |
| A-CSM           | 11.75 ± 3.83 | 9.52 ± 2.41  | 9.24 ± 2.40  | 38.13 ± 13.89   |
| MagicPony       | 11.19 ± 3.08 | 10.29 ± 2.08 | –            | 20.82 ± 13.04   |
| Farm3D          | 11.34 ± 3.22 | 9.63 ± 2.02  | 11.01 ± 1.87 | 29.52 ± 15.73   |
| 3D-Fauna        | 11.86 ± 3.03 | 10.54 ± 2.26 | 9.61 ± 2.15  | 15.70 ± 6.82    |
| Trellis         | 6.93 ± 4.13  | 6.80 ± 3.24  | 5.91 ± 2.93  | 36.82 ± 16.02   |
| DualPM          | 4.30 ± 1.50  | 3.18 ± 1.06  | 3.30 ± 1.20  | 5.49 ± 1.75     |
| Canonical       | 7.88 ± 3.01  | 6.66 ± 2.31  | 6.62 ± 2.33  | 9.87 ± 4.55     |
| **Ours (synt)** | 5.65 ± 1.57  | 4.17 ± 1.15  | 4.35 ± 1.26  | 7.73 ± 2.06     |

### Horse-Robust (15,000 samples; male template train, female eval)

원논문 Table 2. Both Ours variants beat the large foundation models (Trellis.2, SAM-3D) despite far less 3D supervision; fully supervised DualPM remains best.

| Metric (cm) ↓ | Trellis.2 | SAM-3D | DualPM | Canonical | Ours (synt) | Ours (real) |
| ------------- | --------- | ------ | ------ | --------- | ----------- | ----------- |
| RMS CD        | 8.92      | 6.42   | 3.84   | 7.84      | 5.10        | 6.01        |
| MV RMS CD     | 40.03     | 8.71   | 5.42   | 10.83     | 7.92        | 8.37        |

### Ablation (Horse-Mixed, 18,000 samples)

원논문 Table 3. Each component adds gains; the full method reaches mCD 3.86, approaching the ground-truth-supervised DualPM (3.04). The Raw-image baseline (training on original images with imperfect estimated 3D) barely improves over init, showing strict 2D–3D consistency is essential.

| Variant                           | mCD (cm) | % (mCD>5cm) | ∆R (°) |
| --------------------------------- | -------- | ----------- | ------ |
| DualPM (ground-truth 3D)          | 3.04     | 4.00        | 2.21   |
| Random poses baseline             | 5.22     | 44.5        | 5.12   |
| Raw image baseline                | 6.96     | 64.4        | 8.38   |
| Canonical (base)                  | 10.04    | 92.0        | 12.23  |
| + Student's t camera sampling     | 7.24     | 68.4        | 7.51   |
| + Refinement (w/o fitting reg.)   | 5.59     | 55.1        | 6.73   |
| + Regularization in mesh fitting  | 4.85     | 35.0        | 5.89   |
| + Viewpoint augmentation ('Ours') | 3.86     | 11.3        | 3.49   |

The number-of-iterations study shows a large jump after the first iteration then a plateau approaching DualPM (그림 5, 반복별 정확한 수치 미인쇄).

## 💡 Insights & Impact

- The central insight is that exact ground-truth 3D annotations are not needed to improve the predictor: fitting a canonical rigged mesh to imperfect predictions yields a fully self-consistent 3D structure that supervises the next iteration, while the mesh's rigging guarantees anatomical plausibility.
- Real-world image diversity is a usable pose signal — "Ours (real)" improves from the canonical initialization toward the synthetic-trained version and beats large image-to-3D foundation models (SAM-3D, Trellis.2) that hallucinate limbs or produce over-symmetric "canonicalized" shapes on complex articulations.
- Honest limitations the authors state: a rigged canonical mesh is still required; a gap remains between real-image, synthetic-image, and ground-truth-3D training (Table 2); and the self-repulsion loss can hinder recovery of tightly compressed articulations where body parts rest against one another.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: the broader point-map-prediction paradigm for 3D reconstruction; BAT3R instead uses a category-specific _dual_ point map (DualPM) with canonical↔posed correspondences rather than scene-level pointmaps. (The paper's direct baselines — DualPM, MagicPony, 3D-Fauna, Farm3D, A-CSM, SAM-3D, Trellis — are category-specific articulated-reconstruction methods not in this collection.)

## 📚 Key Takeaways

1. BAT3R bootstraps articulated single-image 3D reconstruction from just one rigged canonical mesh plus a 2D image collection, iteratively fitting the mesh to DualPM point-map predictions to self-generate paired training data.
2. Mesh fitting (Kabsch init + articulation/bone-scale optimization with Huber data term and geometric regularizers, on 200 farthest-point control points) turns imperfect predictions into anatomically consistent supervision.
3. With orders-of-magnitude less 3D supervision it approaches fully supervised DualPM (Horse-Mixed mCD 3.86 vs 3.04) and outperforms foundation models like SAM-3D and Trellis.2 on Horse-Robust, while a real-vs-synthetic-vs-GT gap remains.

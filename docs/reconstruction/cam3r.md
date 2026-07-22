# CAM3R: Camera-Agnostic Model for 3D Reconstruction (arXiv preprint (2026-03))

![cam3r — architecture](https://arxiv.org/html/2603.22631v1/pipeline_image_corrected.jpg)

_CAM3R Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Namitha Guruprasad, Abhay Yadav, Cheng Peng, Rama Chellappa
- **Institution**: Johns Hopkins University, Baltimore, MD, USA; University of Virginia, Charlottesville, VA, USA
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.22631)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A camera-agnostic feed-forward two-view reconstruction model that handles pinhole, fisheye, and panoramic imagery without prior calibration — a Ray Module regresses per-pixel ray directions via spherical-harmonic coefficients, a Cross-view Module infers radial distance, pointmaps and relative pose, and a Ray-Aware Global Alignment fuses pairwise predictions into a globally consistent scene.

## 🎯 Key Contributions

1. **Unified camera-agnostic framework**: A feed-forward pipeline that jointly performs lens calibration and 3D reconstruction from unposed imagery across multiple camera geometries, even for heterogeneous pairs (e.g. fisheye-panorama).
2. **Decoupled supervision**: Separately supervises the Ray Module and Cross-view Module by jointly training rays, dense pointmaps, and relative poses across highly heterogeneous camera sources.
3. **Ray-Aware Global Alignment**: A global alignment that lifts pose/scale optimization into a ray-consistent 3D space (rather than the pinhole-assuming space of standard bundle adjustment), with scene-graph pruning for reliable edges.
4. **State-of-the-art on wide-FoV/cross-modal**: Large gains in challenging large-FoV and panoramic scenarios where pinhole-trained foundation models degrade or collapse.

## 🔧 Technical Details

### Two-view network

- **Ray Module (RM)**: a shared ViT-L encoder + two Transformer Ray-Encoder layers output spherical-harmonic (SH) coefficients (degree ≤ 3); an inverse SH transform reconstructs a continuous per-pixel ray directional field d_i(u) ∈ S², handling pinhole/fisheye/panoramic manifolds. Initialized from UniK3D's angular module.
- **Cross-view Module (CVM)**: a Siamese encoder + dual-block transformer decoder (self- + cross-attention) with DPT heads regressing per-pixel radial distance r_i and confidence σ_i, and a relative-pose network predicting P_{2→1} = {R ∈ SO(3), unit t̂ ∈ S²} with a relative scale s. Initialized from DUSt3R. Local pointmap X^{i,i}(u) = d_i(u)·r_i(u); the second view is mapped into the first's frame via P_{2→1}.

### Training objectives

- **Asymmetric Angular Loss** (quantile regression, heavier penalty for angular underestimation to avoid inward collapse toward narrow-FoV modes): L_A = β·L_AA^{0.7}(θ) + (1−β)·L_AA^{0.5}(ϕ).
- **Local Regression Loss** (scale-normalized MSE on local pointmaps) and **Relative Pose Loss** (SO(3) geodesic rotation + scale-anchored translation MSE). Total L = λ_A·L_A + λ_regr·L_regr + λ_pose·L_pose.

### Ray-Aware Global Alignment

- **Scene-graph pruning**: symmetric pose consistency (prune edges where R_ji vs R_ij^T deviate beyond τ_rot or translation directions misalign) + geometric overlap via 3D mutual-nearest-neighbors (discard edges with < 20% overlap).
- **Global consensus + optimization**: confidence-weighted consensus ray field D_i and median-aligned radial field R_i give per-image priors x_i = R_i·D_i; a multi-stage alternating optimizer solves for camera poses {P_i} and per-image scales {s_i} minimizing confidence-weighted 3D alignment error over pruned edges.

### Training configuration

- Two-phase curriculum: phase 1 on homogeneous pairs (CAM3R-homo), phase 2 adds heterogeneous pairs (final CAM3R). AdamW, initial LR 5×10⁻⁵ with linear warmup + cosine decay, images 512px long edge, 4 NVIDIA H200 GPUs; supplementary lists effective batch 32, weight decay 0.05, 300–500 epochs.
- Datasets (augmented to induce optical heterogeneity): 2D3DS and 360Loc (panoramic → synthesized fisheye/perspective), ADT (fisheye → synthesized perspective), MegaDepth (perspective), and CO3Dv2 (pinhole, held out zero-shot, with synthetic fisheye).

## 📊 Results

Baselines: DUSt3R, MASt3R, Pow3R, VGGT, π³.

### Two-view relative pose (Accuracy@15°↑)

원논문 Table 1. CAM3R is strongest overall and dominates the panoramic/cross-model cases (2D3DS, 360Loc) where DUSt3R/MASt3R collapse. On MegaDepth π³ has higher RRA (99.8 vs 96.8) but CAM3R higher RTA; on CO3Dv2 zero-shot MASt3R has higher RRA (98.4) but CAM3R's RTA (88.2) far exceeds all.

| Model      | 2D3DS RRA/RTA | MegaDepth RRA/RTA | CO3Dv2 (0-shot) RRA/RTA | 360Loc RRA/RTA | ADT RRA/RTA |
| ---------- | ------------- | ----------------- | ----------------------- | -------------- | ----------- |
| DUSt3R     | 10.6 / 6.0    | 95.6 / 80.8       | 94.7 / 43.1             | 0.0 / 0.0      | 91.0 / 63.6 |
| MASt3R     | 18.3 / 9.3    | 69.7 / 56.4       | 98.4 / 33.4             | 39.8 / 5.3     | 96.6 / 63.5 |
| Pow3R      | 7.5 / 6.0     | 96.2 / 74.2       | 95.8 / 38.3             | 0.0 / 0.0      | 96.6 / 79.2 |
| VGGT       | 11.8 / 11.0   | 98.0 / 88.2       | 90.9 / 29.4             | 37.8 / 11.1    | 92.7 / 82.9 |
| π³         | 16.8 / 11.4   | 99.8 / 93.3       | 90.7 / 22.7             | 38.5 / 13.0    | 97.5 / 93.8 |
| CAM3R-homo | 65.4 / 56.8   | 97.2 / 92.6       | 96.1 / 66.5             | 58.3 / 54.7    | 98.2 / 93.4 |
| **CAM3R**  | 97.7 / 94.3   | 96.8 / 94.2       | 97.5 / 88.2             | 96.0 / 91.0    | 99.0 / 95.0 |

### Multi-view relative pose (Accuracy@30° RRA/RTA, mAA@30↑)

원논문 Table 2. CAM3R (with Ray-Aware GA) has the highest average across most datasets; multi-view comparison is limited to VGGT and π³ (others degrade on heterogeneous optics). On MegaDepth π³ ties CAM3R on RRA (100.0 vs 96.6) but CAM3R has higher mAA. "CAM3R + DUSt3R GA" is the alignment ablation.

| Model              | 2D3DS mAA | MegaDepth mAA | CO3Dv2 (0-shot) mAA | 360Loc mAA | ADT mAA |
| ------------------ | --------- | ------------- | ------------------- | ---------- | ------- |
| VGGT               | 7.6       | 68.8          | 19.6                | 19.5       | 60.3    |
| π³                 | 9.6       | 73.4          | 22.7                | 17.8       | 75.8    |
| CAM3R + DUSt3R GA  | 38.8      | 68.5          | 46.1                | 55.5       | 70.8    |
| **CAM3R + Our GA** | 73.5      | 87.4          | 64.9                | 82.6       | 77.3    |

### Multi-view trajectory error (ATE RMSE↓)

원논문 Table 3. CAM3R + Our BA is best on 2D3DS, 360Loc, and ties ADT, but π³ has lower ATE on MegaDepth (0.6 vs 0.8) and CO3Dv2 (0.7 vs 1.1).

| Model              | 2D3DS | MegaDepth | CO3Dv2 (0-shot) | 360Loc | ADT |
| ------------------ | ----- | --------- | --------------- | ------ | --- |
| VGGT               | 3.8   | 0.7       | 1.3             | 6.3    | 0.5 |
| π³                 | 2.9   | 0.6       | 0.7             | 5.8    | 0.4 |
| CAM3R + DUSt3R BA  | 2.4   | 1.2       | 1.6             | 4.5    | 0.6 |
| **CAM3R + Our BA** | 1.8   | 0.8       | 1.1             | 2.7    | 0.4 |

### Ablations

- **Heterogeneous training** (원논문 Table 1): the phase-2 heterogeneous pairs lift two-view generalization markedly (CAM3R-homo → CAM3R, e.g. 2D3DS 65.4/56.8 → 97.7/94.3).
- **Architectural design** (원논문 Table S1): naively fine-tuning DUSt3R on distorted data is insufficient (2D3DS 17.8/10.9) vs the decoupled CAM3R (97.7/94.3), showing distorted-data exposure alone does not fix the entangled optimization.
- **Ray-Aware Global Alignment**: vs DUSt3R's global alignment it improves mAA (by nearly 35% on heterogeneous data) and reduces ATE by up to 40% (e.g. 360Loc 4.5 → 2.7).

## 💡 Insights & Impact

- Isolates why pinhole-trained foundation models fail on wide-angle optics: directly regressing the second view into the first frame forces the network to entangle non-linear intrinsic projection with scene geometry and pose. CAM3R's decoupling (rays via SH, distance via CVM) resolves this conflict.
- The asymmetric angular loss counters the training-data bias toward narrow-FoV pinhole modes, preventing "inward collapse" of predicted rays.
- Standard bundle adjustment assumes pixel distances map linearly to 3D distances (pinhole); the ray-aware optimizer instead operates in a ray-consistent 3D space, which is what enables robust drift suppression on panoramic/fisheye trajectories.
- Honest limits: on standard perspective data (MegaDepth, CO3Dv2 ATE) π³ remains competitive or better; the authors note the geometric and cross-view encoders are still separate and target a unified real-time backbone as future work.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: pointmap-regression foundation used to initialize the Cross-view Module and as a baseline; its pinhole assumption motivates CAM3R.
- **[MASt3R](../foundation/mast3r.md)** / **[Pow3R](./pow3r.md)**: DUSt3R-family baselines; Pow3R adds camera/scene priors.
- **[VGGT](./vggt.md)** / **[π³](./pi3.md)**: multi-view feed-forward baselines; π³ remains competitive on perspective data.

## 📚 Key Takeaways

1. CAM3R decouples camera geometry (a Ray Module regressing SH ray directions) from scene geometry (a Cross-view Module for radial distance, pointmaps, and pose) to reconstruct pinhole, fisheye, and panoramic imagery without calibration.
2. A Ray-Aware Global Alignment fuses pairwise predictions in a ray-consistent 3D space, improving heterogeneous mAA by ~35% and cutting ATE up to 40% over DUSt3R-style alignment.
3. It sets state-of-the-art on wide-FoV/cross-model two-view and multi-view benchmarks (e.g. 2D3DS 97.7/94.3 RRA/RTA where DUSt3R gives 10.6/6.0), while π³ stays competitive on standard perspective data.

# Wid3R: Wide Field-of-View 3D Reconstruction via Camera Model Conditioning (arXiv preprint 2026-02)

## 📋 Overview

- **Authors**: Dongki Jung, Jaehoon Choi, Adil Qureshi, Somi Jeong, Dinesh Manocha, Suyong Yeon
- **Institution**: University of Maryland, College Park; NAVER LABS
- **Venue**: arXiv preprint (2026-02)
- **Links**: [Paper](https://arxiv.org/abs/2602.05321) | [Project Page](https://jdk9405.github.io/Wid3R/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first multi-view feed-forward network that reconstructs 3D point maps and camera poses directly from distorted wide field-of-view imagery (fisheye and 360°), using a unified ray-based representation and per-view camera-model conditioning tokens.

## 🎯 Key Contributions

1. **Feed-forward reconstruction for distorted imagery**: The first multi-view feed-forward network that operates directly on fisheye and 360° images without explicit calibration or undistortion, jointly estimating dense point maps and camera poses.
2. **Unified ray-based representation**: A ray-based formulation that lets the network reason about scene geometry across diverse projection models.
3. **Camera model conditioning**: Per-view camera-model tokens that inform the network of the projection characteristics specific to each camera, improving generalization across camera types.

## 🔧 Technical Details

### Ray-based representation and camera tokens

Instead of assuming pinhole inputs, each view `i` carries a camera model token `Ci` and a pose `Ti ∈ R^{4×4}`; geometry is expressed in a unified ray-based local coordinate representation so the shared network handles pinhole, fisheye, and spherical projections together.

### Training

Adam optimizer on RTX A6000 / H100 GPUs, initial LR 5×10⁻⁵ with exponential decay; input resized to 518×336. The π³ encoder, feature aggregation module, and pose header are initialized from pretrained weights and all components trained end-to-end. Wid3R (ray-based modules) is compared against "Ours (π³)", the same wide-angle training data on the plain π³ architecture without the ray representation and camera tokens.

## 📊 Results

### Zero-shot pose estimation — accuracy (higher is better)

원논문 Table 2. RRA/RTA/AUC at 30° threshold.

| Method       | FIORD RRA↑ | FIORD RTA↑ | FIORD AUC↑ | Zip RRA↑ | Zip RTA↑ | Zip AUC↑ | S2D3D RRA↑ | S2D3D RTA↑ | S2D3D AUC↑ |
| ------------ | ---------- | ---------- | ---------- | -------- | -------- | -------- | ---------- | ---------- | ---------- |
| VGGT         | 82.34      | 84.01      | 44.63      | 64.42    | 65.29    | 20.68    | 19.30      | 33.14      | 2.60       |
| π³           | 85.48      | 87.42      | 48.35      | 82.65    | 86.66    | 40.94    | 19.94      | 31.99      | 2.06       |
| Ours (π³)    | 99.87      | 96.39      | 72.56      | 83.04    | 89.48    | 64.44    | 82.91      | 87.83      | 62.14      |
| Ours (Wid3R) | 100.0      | 93.38      | 68.20      | 93.34    | 95.15    | 74.61    | 94.05      | 93.29      | 79.93      |

The abstract highlights AUC@30° gains of up to +33.67 on Zip-NeRF (fisheye, over π³ 40.94→74.61) and +77.33 on Stanford2D3D (360°, over VGGT 2.60→79.93). On FIORD, Ours (π³) edges out Wid3R on RTA/AUC.

### Zero-shot pose estimation — errors (lower is better)

원논문 Table 3.

| Method       | FIORD ATE↓ | FIORD RPEt↓ | FIORD RPEr↓ | Zip ATE↓ | Zip RPEt↓ | Zip RPEr↓ | S2D3D ATE↓ | S2D3D RPEt↓ | S2D3D RPEr↓ |
| ------------ | ---------- | ----------- | ----------- | -------- | --------- | --------- | ---------- | ----------- | ----------- |
| VGGT         | 0.54       | 0.99        | 15.02       | 1.83     | 1.73      | 34.41     | 3.07       | 5.01        | 98.83       |
| π³           | 0.53       | 0.90        | 13.45       | 0.85     | 0.87      | 18.55     | 2.83       | 5.01        | 91.13       |
| Ours (π³)    | 0.32       | 0.51        | 3.99        | 0.85     | 0.67      | 12.93     | 1.43       | 2.21        | 32.94       |
| Ours (Wid3R) | 0.44       | 0.71        | 3.27        | 0.49     | 0.47      | 7.72      | 1.11       | 1.83        | 18.99       |

### Point map estimation (Mean values)

원논문 Table 5. Acc./Comp. lower is better; N.C. higher is better.

| Method       | ScanNet++ Acc↓ | ScanNet++ Comp↓ | ScanNet++ N.C.↑ | MP3D Acc↓ | MP3D Comp↓ | MP3D N.C.↑ | S2D3D Acc↓ | S2D3D Comp↓ | S2D3D N.C.↑ |
| ------------ | -------------- | --------------- | --------------- | --------- | ---------- | ---------- | ---------- | ----------- | ----------- |
| VGGT         | 0.135          | 0.068           | 0.704           | 0.327     | 1.756      | 0.530      | 0.387      | 2.115       | 0.536       |
| π³           | 0.086          | 0.037           | 0.739           | 0.315     | 1.308      | 0.539      | 0.380      | 0.745       | 0.557       |
| Ours (π³)    | 0.027          | 0.014           | 0.781           | 0.161     | 0.142      | 0.610      | 0.211      | 0.273       | 0.596       |
| Ours (Wid3R) | 0.018          | 0.012           | 0.803           | 0.094     | 0.087      | 0.790      | 0.197      | 0.172       | 0.729       |

### Large-scale localization on Matterport3D

원논문 Table 4, AUC@5° per scene and runtime. Wid3R registers all images in every scene (37/37, 20/20, 31/31).

| Method            | Scene1 AUC@5°↑ | Scene2 AUC@5°↑ | Scene3 AUC@5°↑ | Time   |
| ----------------- | -------------- | -------------- | -------------- | ------ |
| OpenMVG           | 1.10           | 0.37           | 52.82          | ~3min  |
| SPSG + COLMAP     | 15.79          | 29.88          | 85.01          | ~5min  |
| SphereGlue+COLMAP | 26.98          | 27.76          | 80.06          | ~5min  |
| DKM + COLMAP      | 27.70          | 16.36          | 85.56          | ~30min |
| EDM + IM360       | 69.05          | 44.16          | 84.37          | ~30min |
| Ours (Wid3R)      | 51.02          | 69.66          | 78.77          | ~3s    |

Wid3R is best on Scene2 and runs in ~3s (vs ~30min for the SfM-based EDM+IM360), while EDM+IM360 remains stronger on Scene1 and Scene3.

### Monocular 360° depth on Matterport3D

원논문 Table 6 (subset). Abs Rel/RMSE lower is better; δ1.25 higher is better. Wid3R is trained multi-view yet evaluated single-view.

| Method             | Abs Rel↓ | RMSE↓ | δ1.25↑ |
| ------------------ | -------- | ----- | ------ |
| Depth Anywhere (a) | 0.085    | -     | 0.917  |
| UniK3D (b)         | 0.315    | 0.649 | 0.858  |
| RPG360 (b)         | 0.203    | 0.667 | 0.859  |
| Ours (Wid3R)       | 0.227    | 0.562 | 0.948  |

Wid3R reaches the best δ1.25 (0.948) and RMSE (0.562) in this comparison but a higher Abs Rel than depth-specialized methods — "comparable" single-view 360° depth despite its multi-view design.

### Ablation on Stanford2D3D (Mean values)

원논문 Table 7. Point map metrics; Acc./Comp. lower is better, N.C. higher is better. Stanford2D3D (360°) is not in the training data.

| Configuration                      | Acc↓  | Comp↓ | N.C.↑ |
| ---------------------------------- | ----- | ----- | ----- |
| 360-only, token✓ (2~12 frames)     | 0.220 | 0.355 | 0.710 |
| Pinhole+360, token✓                | 0.254 | 0.166 | 0.698 |
| Fisheye+360, token✓                | 0.593 | 0.120 | 0.686 |
| All three, token✓                  | 0.248 | 0.146 | 0.706 |
| All three, token✗ (b)              | 0.284 | 0.152 | 0.680 |
| All three, token✓, 2~24 frames (c) | 0.197 | 0.172 | 0.729 |

Training with diverse camera models improves 360° geometry and reduces variance; camera-model tokens consistently help (token✓ > token✗); more frames per batch (2~24) further improves Acc and N.C.

## 💡 Insights & Impact

- **Handle distortion natively**: Rather than undistort-then-reconstruct, Wid3R encodes projection via a ray representation and camera-model tokens, letting one network span pinhole, fisheye, and 360° cameras.
- **Data diversity offsets scarce 360° labels**: 360° training data is <1% of the corpus; jointly training across camera models mitigates overfitting and stabilizes learning, more effective than pseudo-label or post-optimization workarounds.
- **Feed-forward speed at scale**: Producing large-scale 360° maps in ~3s versus ~30min for SfM pipelines makes wide-FoV mapping practical.

## 🔗 Related Work

- **[π³ (pi3)](pi3.md)**: The backbone Wid3R initializes and extends with ray-based modules and camera tokens.
- **[VGGT](vggt.md)**: Multi-view feed-forward baseline compared on pose and point maps.
- **[Fisheye3R](fisheye3r.md)**: Related feed-forward reconstruction targeting fisheye distortion.
- **[DUSt3R](../foundation/dust3r.md)**, **[Spann3R](spann3r.md)**: Foundational feed-forward reconstruction formulations discussed as lineage.

## 📚 Key Takeaways

1. Wid3R is the first feed-forward multi-view network to reconstruct point maps and poses directly from fisheye and 360° images.
2. A unified ray-based representation plus camera-model tokens yields large zero-shot pose gains (AUC@30° +33.67 on Zip-NeRF, +77.33 on Stanford2D3D) and the best wide-FoV point maps.
3. It localizes large-scale 360° scenes in ~3s, and ablations confirm both camera-model tokens and diverse-camera training are essential.

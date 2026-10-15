# VGGT: Visual Geometry Grounded Transformer (CVPR 2025)

![VGGT Architecture](https://vgg-t.github.io/resources/architecture_v4.png)
_Predict cameras, depth, pointmaps and tracking information from features alternating within-image and cross-frame attention._

## 📋 Overview

- **Authors**: Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, David Novotny
- **Institution**: Visual Geometry Group, University of Oxford, Meta AI
- **Venue**: CVPR 2025
- **Award**: Best Paper Award
- **Links**: [Paper](https://arxiv.org/abs/2503.11651) | [Code](https://github.com/facebookresearch/vggt) | [Project Page](https://vgg-t.github.io/)
- **Verification**: CONFIRMED (venue: existing verdict 2026-07-20; methods/results PDF re-reviewed 2026-10-15)
- **TL;DR**: Jointly process RGB images to predict cameras, depth, 3D pointmaps and tracking features. Infer shared-frame geometry without GT cameras, with optional BA refinement.

## 🎯 Key Contributions

1. **Joint Geometry**: Learn multiple geometric tasks through one feature backbone.
2. **Alternating-Attention**: Alternate within-image and cross-image relationships.
3. **Direct Multi-View Prediction**: Reduce separate pairwise-pointmap alignment in default inference.
4. **Reusable Features**: Supply features to separate tracking modules and downstream tasks.

## 🔧 Technical Details

### Input and Output

- **Input**: One or more RGB images; default inference jointly processes the provided set.
- **Output**: Camera rotation, translation and FoV; depth, pointmaps, tracking features and query-point 2D trajectories.
- **Coordinates**: Relative to the first camera; assume a centered principal point (§3.1).

### Architecture

```text
RGB images → DINOv2-initialized tokens
           → within-image self-attention ↔ all-frame self-attention
           → camera head / DPT dense heads / query-based tracking module
```

Camera heads predict rotation, translation and FoV.
DPT heads output depth, pointmaps and dense tracking features.
A CoTracker2-based module combines query points with these features to find framewise correspondences (§3.2).
DPT therefore does not directly output all tracks without queries.

### Inference Scope

Default results use feed-forward inference; the paper also reports optional bundle adjustment (BA).
BA optimizes cameras/correspondences to reduce reprojection errors.
Global cross-frame attention costs grow with image count, motivating chunking/streaming extensions for long videos.
Remove unsupported fixed limits such as DUSt3R maximum 32 images and guarantees of generalization to every domain.

## 📊 Results

### Point Map Estimation on ETH3D

[arXiv 2503.11651v1 PDF](https://arxiv.org/pdf/2503.11651v1), Table 3, PDF p.7.
Metrics are Acc / Comp / Overall. DUSt3R and MASt3R use global alignment.
Distinguish direct VGGT point-head outputs from depth/camera unprojection. This table is not DTU.

| Method                 | Acc. ↓    | Comp. ↓   | Overall ↓ | Time      |
| ---------------------- | --------- | --------- | --------- | --------- |
| DUSt3R                 | 1.167     | 0.842     | 1.005     | ~7s       |
| MASt3R                 | 0.968     | 0.684     | 0.826     | ~9s       |
| **VGGT (Point)**       | 0.901     | 0.518     | 0.709     | **~0.2s** |
| **VGGT (Depth + Cam)** | **0.873** | **0.482** | **0.677** | **~0.2s** |

### Camera Pose Estimation

원논문 Table 1. 10프레임 무작위 샘플, 두 지표 모두 높을수록 좋다.
No compared method trains on Re10K. Runtime is measured under this protocol on one H100.

| Method                  | Re10K (unseen) AUC@30 ↑ | CO3Dv2 AUC@30 ↑ | Time      |
| ----------------------- | ----------------------- | --------------- | --------- |
| Colmap+SPSG             | 45.2                    | 25.3            | ~15s      |
| PixSfM                  | 49.4                    | 30.1            | >20s      |
| PoseDiff                | 48.0                    | 66.5            | ~7s       |
| DUSt3R                  | 67.7                    | 76.7            | ~7s       |
| MASt3R                  | 76.4                    | 81.8            | ~9s       |
| VGGSfM v2               | 78.9                    | 83.4            | ~10s      |
| MV-DUSt3R               | 71.3                    | 69.5            | ~0.6s     |
| CUT3R                   | 75.3                    | 82.8            | ~0.6s     |
| FLARE                   | 78.8                    | 83.3            | ~0.5s     |
| Fast3R                  | 72.7                    | 82.5            | ~0.2s     |
| **VGGT (Feed-Forward)** | 85.3                    | 88.2            | **~0.2s** |
| **VGGT (with BA)**      | **93.5**                | **91.8**        | ~1.8s     |

### 추론 시간

Source Tables 1 and 3. Do not generalize timings to arbitrary frame counts/pipelines; unreported derived speedups are omitted.

| Method   | Time      |
| -------- | --------- |
| DUSt3R   | ~7s       |
| MASt3R   | ~9s       |
| **VGGT** | **~0.2s** |

### Dense MVS Estimation on DTU

Source Table 2, PDF p.7, in mm; separate from the ETH3D results above.
MASt3R uses GT cameras; DUSt3R and VGGT do not in these rows.

| Method | GT Cameras | Acc. ↓ | Comp. ↓ | Overall ↓ |
| ------ | ---------- | ------ | ------- | --------- |
| DUSt3R | No         | 2.677  | 0.805   | 1.741     |
| MASt3R | Yes        | 0.403  | 0.344   | 0.374     |
| VGGT   | No         | 0.389  | 0.374   | 0.382     |

### Ablation: Attention 구조 (ETH3D)

Source Table 5, PDF p.8. Alternating-Attention is VGGT's chosen design.

| Attention                  | Acc. ↓    | Comp. ↓   | Overall ↓ |
| -------------------------- | --------- | --------- | --------- |
| Cross-Attention            | 1.287     | 0.835     | 1.061     |
| Global Self-Attention Only | 1.032     | 0.621     | 0.827     |
| **Alternating-Attention**  | **0.901** | **0.518** | **0.709** |

## 💡 Insights & Impact

Joint learning reduces the burden of separately estimating and reconciling cameras and depth.
Depth/camera-unprojected clouds can outperform direct point-head outputs, so distinguish output paths.
Fast initial predictions can initialize BA; optional optimization is not made pointless.

Do not directly rank results with different GT-camera inputs, alignments or image counts.
Visual examples show varied-input possibilities, not guaranteed accuracy for all images, sensors or dynamic scenes.

## 🔗 Related Work

### Evolution from DUSt3R

| Aspect       | [DUSt3R](../foundation/dust3r.md) | VGGT          |
| ------------ | --------------------------------- | ------------- |
| Tasks        | 3D only                           | All geometric |
| Speed        | ~7s                               | ~0.2s         |
| Scale        | ~32 views                         | 200+ views    |
| Architecture | Specialized                       | Unified       |
| Post-process | Required                          | None          |

### Comparison with Other Extensions

- **[MUSt3R](must3r.md)**: Memory for scale → VGGT: Direct scale
- **[Fast3R](fast3r.md)**: Speed focus → VGGT: Speed + quality
- **[Test3R](test3r.md)**: Test-time adapt → VGGT: Direct generalization

## 📚 Key Takeaways

1. A shared backbone learns information for cameras, depth, pointmaps and tracking.
2. Separate default feed-forward and BA-augmented paths.
3. ETH3D pointmap and DTU MVS evaluations use different tables.
4. Consider long-video costs and first-frame coordinates when choosing extensions.

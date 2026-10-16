# Self-Geometry: GT-Free and Plug-and-Play Test-Time Adaptation for Geometrically Consistent 3D Vision Foundation Models (arXiv 2026)

## 📋 Overview

- **Authors**: Seokhyun Youn, Dahyeon Kye, Sung-Ho Bae, Jihyong Oh
- **Institution**: Chung-Ang University, Kyung Hee University
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.10708)
- **Verification**: UNKNOWN (2026-10-15; source 2608.10708v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Adapt only frozen-3D-model LoRA using test-scene 2D correspondences instead of GT; add depth-independent epipolar constraints to depth/pose reprojection.

## 🎯 Key Contributions

1. **Explicit Geometry TTA**: Supervise with external 2D-matcher correspondences rather than only output self-consistency.
2. **Gradient Disentanglement**: Reduce conflicts between pose/depth-changing constraints and pose-only constraints.
3. **Angular Sampling**: Select diverse observations by rotational distance to avoid processing every view each time.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Same-scene RGB images and pretrained VGGT, π³ or DA3. GT poses/depth are not adaptation inputs.
- **Output**: Scene-adapted cameras, depth and pointmaps. Per-scene optimization supplements initial inference.
- **Problem**: Predicted pointmaps can agree on the same initial error. Reprojection alone cannot distinguish all pose/depth combinations.

### Method

1. Obtain external-matcher 2D pseudo-correspondences and filter them with epipolar/multi-view residuals.
2. Multi-View Consistency projects source-depth/pose points onto target correspondence pixels.
3. Epipolar Consistency reduces pose-defined epipolar-line distances without depth.
4. Remove EC-direction components from MVC gradients, separating their roles while optimizing the combined loss.
5. Sample target views using SO(3)-distance-bin occupancy/entropy and neighboring views per bin. Update only QKV LoRA.

§III–IV. Freeze pretrained weights and adapt scene-specific adapters. GT-free means no GT geometry, not absence of matchers, pretrained models or computation.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.10708v2), Table II, PDF p.7.

Sample up to 100 frames per scene using DA3 protocols. These are VGGT/VGGT-Ours pose AUC@3/AUC@30 at degree thresholds on rotation/translation pose error, not posed-geometry F1 using GT cameras.

| Dataset   | Variant       | AUC@3 ↑ | AUC@30 ↑ |
| --------- | ------------- | ------- | -------- |
| 7Scenes   | VGGT          | 0.25    | 0.86     |
| 7Scenes   | Self-Geometry | 0.28    | 0.87     |
| ETH3D     | VGGT          | 0.20    | 0.76     |
| ETH3D     | Self-Geometry | 0.27    | 0.83     |
| ScanNet++ | VGGT          | 0.56    | 0.94     |
| ScanNet++ | Self-Geometry | 0.54    | 0.94     |
| HiRoom    | VGGT          | 0.51    | 0.88     |
| HiRoom    | Self-Geometry | 0.47    | 0.85     |

Mean gains do not hold for every model/dataset. VGGT ScanNet++ AUC@3 and HiRoom worsen above. Read Table III's posed/unposed F1 separately.

## 💡 Insights & Impact

Which variables receive which gradients matters alongside adding geometric constraints. Correspondence-based supervision goes beyond confidence or initial self-consistency.

- Repeated matcher errors or low overlap can corrupt pseudo-supervision.
- Scene-specific TTA and adapter management add costs. Do not combine short forward times with full adaptation times.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md), [π³](pi3.md), [Depth Anything 3](depth-anything-3.md): adapted backbones.
- [Free-Geometry](free-geometry.md), [Fin3R](fin3r.md): earlier test-scene adaptation approaches.

## 📚 Key Takeaways

1. Separate correspondence constraints into pose-only and pose-plus-depth paths.
2. Adaptation without GT geometry still adds inference and optimization costs.
3. Check dataset-specific regressions alongside mean performance.

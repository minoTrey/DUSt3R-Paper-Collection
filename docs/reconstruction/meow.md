# Many Eyes, One World: Feed-Forward 3D Reconstruction from Mixed Cameras (arXiv 2026)

## 📋 Overview

- **Authors**: Qiaoge Li, Yifan Zhan, Haijun Yang, Haiyang Liu, Yiyi Cai, Chenchi Luo
- **Institution**: China Mobile Research Institute, University of Tokyo
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.35658)
- **Verification**: UNKNOWN (2026-10-15; source 2609.35658v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Adapt MapAnything on synthetic data to jointly handle perspective, fisheye and panoramic images without camera-type labels.

## 🎯 Key Contributions

1. Generate LENSCOPE training tuples mixing projections.
2. Preserve full fields of view with resizing and aspect-ratio embeddings.
3. Provide mixed-camera pose/metric-pointmap evaluation and laser benchmarks.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Heterogeneous-camera RGB tuples without calibration, distortion, camera-type labels or poses.
- **Output**: Shared-frame camera poses and metric pointmaps.
- **Problem**: Perspective-focused training and cropping damage full-panorama and mixed-projection observations.

### Method

1. Render exact rays, depth and poses from procedural indoor scenes.
2. Resample cameras and select tuples with connected covisibility graphs.
3. Resize without cropping to a shared tensor shape and embed original aspect ratios.
4. Adapt MapAnything with panorama circular padding, solid-angle weights and ray likelihoods.

Start from perspective-pretrained MapAnything, then adapt only on synthetic tuples. The complete training history is not synthetic-only.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.35658v1), Table 2, PDF p.8.

Stanford 2D3DS, 88 heterogeneous tuples with 3–24 views. Compute pose metrics per tuple before averaging; ATE uses Sim(3) alignment.

| Method      | Camera label input | mAA@30 ↑ | ATE ↓ |
| ----------- | ------------------ | -------- | ----- |
| MapAnything | None               | 16.4     | 1.48  |
| MEOW        | None               | 80.4     | 0.62  |
| Wid3R       | Class per view     | 54.3     | 0.83  |

Tuple means differ from pooled all-pair means. The paper states weaker large-tuple performance than Wid3R and underestimated metric scale relative to GT.

## 💡 Insights & Impact

Handle mixed cameras through projection-diverse data, overlap validation and input processing rather than a new backbone.

- Adaptation focuses on indoor short tuples and struggles with long sequences.
- Sim(3)-aligned performance does not establish metric-scale accuracy.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md): a perspective-geometry comparison model.
- [DUSt3R](../foundation/dust3r.md): pointmap-prediction background.

## 📚 Key Takeaways

1. Process heterogeneous observations without camera-type labels.
2. Adapt on synthetic data while using pretrained models.
3. Distinguish aligned poses from metric scale.

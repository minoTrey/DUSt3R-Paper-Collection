# GRF-Recon: Global Ray-Field Optimization for Long-Sequence Feed-forward Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Enpeng Li, Yunzhou Zhang, Zhiyao Zhang, Dexuan Lyu, Chenyu Wang, Chiyuan Cui, Cheng Cheng
- **Institution**: Northeastern University, China
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.20012)
- **Verification**: UNKNOWN (2026-10-15; source 2609.20012v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Distill monocular geometry priors into DA3, then globally optimize ray/depth consistency as well as chunk poses.

## 🎯 Key Contributions

1. Inject MoGe-teacher geometry through LoRA.
2. Build sparse correspondences from ray, gradient and photometric signals.
3. Optimize within-/cross-chunk geometry constraints alongside trajectory stitching.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Long monocular RGB video without supplied camera intrinsics in this configuration.
- **Output**: Long camera trajectories and aligned point clouds.
- **Problem**: Aligning chunk poses alone leaves internal geometry errors and inconsistent rays.

### Method

1. Adapt DA3 with LoRA using a monocular MoGe teacher.
2. Restrict correspondence searches with predicted poses/depth.
3. Match using ray distances, gradient similarities and patch photometric errors, then verify bidirectionally.
4. Select keyframes/loops with DINOv2 descriptors and jointly optimize ray constraints and poses.

LoRA adaptation is training; ray-field and graph refinement are inference-time optimization.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.20012v1), Table 2, PDF p.10.

KITTI monocular Sim(3)-aligned ATE RMSE (m). Means exclude high-speed sequence 01. All rows are uncalibrated.

| Method        | Mean ATE excluding seq.01 (m) ↓ |
| ------------- | ------------------------------- |
| VGGT-Long     | 19.78                           |
| Pi-Long       | 19.01                           |
| DA3-Streaming | 12.72                           |
| GRF-Recon     | 7.18                            |

Excluded sequence 01 has GRF-Recon ATE of 76.52m. The 7.18m mean does not establish low error on all KITTI sequences.

## 💡 Insights & Impact

Combine improved learned priors with enforced physical consistency across views.

- Teacher errors can be distilled.
- Depend on loop matching and global optimization; the mean excludes a difficult sequence.

## 🔗 Related Work

- [Depth Anything 3](depth-anything-3.md): the adapted backbone.
- [VGGT](../foundation/vggt.md): long-sequence comparisons.

## 📚 Key Takeaways

1. DA3-prior adaptation and ray optimization are separate stages.
2. Connect geometry as well as poses.
3. Preserve the KITTI mean's sequence-exclusion condition.

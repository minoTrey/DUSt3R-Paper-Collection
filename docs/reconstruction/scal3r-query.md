# Scal3R: Learning Efficient Multi-Relative Pose Query for Scalable Online 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Chin-Yang Lin, Yang-Che Sun, Cheng Sun, Fu-En Yang, Min-Hung Chen, Yen-Yu Lin, Wei-Chen Chiu, Yu-Lun Liu
- **Institution**: National Yang Ming Chiao Tung University, NVIDIA
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.04201)
- **Verification**: UNKNOWN (2026-10-15; source 2609.04201v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Query relative poses to multiple references rather than regressing global pose against a fixed first frame, reducing long-video drift.

## 🎯 Key Contributions

1. Add relative-pose queries to a frozen backbone.
2. Use asymmetric attention that hides query tokens from image tokens.
3. Fuse relative constraints through online pose graphs and loop closure.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: RGB video without intrinsics and stored reference tokens.
- **Output**: Globally connected camera poses and backbone pointmaps.
- **Problem**: Global pose heads may fail beyond training-range motions while local depth remains relatively stable.

### Method

1. Freeze CUT3R or STream3R backbones.
2. Let query tokens read image features without entering image key/value representations.
3. Predict current-to-reference rotation and translation per token.
4. Optimize multi-reference keyframe-buffer constraints and loop edges in a pose graph.

Train queries/heads on TartanAir 4-view samples. Outdoor experiments also reset streaming states, so gains are not query-only. This differs in authors/method from the same-name Scal3R at 2604.08542.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.04201v1), Table 1, PDF p.10.

Mean KITTI ATE in calibration-free RGB-only evaluation, in m; lower is better. Means for methods with failures/OOM may include only completed sequences.

| Method            | Mean ATE (m) ↓ |
| ----------------- | -------------- |
| CUT3R             | 207.2          |
| TTT3R             | 182.2          |
| Scal3R (CUT3R)    | 69.7           |
| Scal3R (STream3R) | 70.8           |

Additional source comparisons give LongStream lower ATE. Do not call these results universally best across all methods.

## 💡 Insights & Impact

Extract relative constraints while preserving local backbone geometry instead of regressing whole long trajectories at once.

- Extra query training and pose-graph optimization are required.
- Reference selection and loop-closure errors affect global outputs.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md): frozen streaming backbone.
- [Scal3R (2604.08542)](scal3r.md): a distinct paper sharing the name.

## 📚 Key Takeaways

1. Distinguish same-name papers by arXiv ID.
2. Learn relative poses while preserving image geometry.
3. Pose graphs provide global consistency.

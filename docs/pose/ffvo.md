# FFVO: A Feedforward Pose Decoder for Long-Horizon Visual Odometry (arXiv 2026)

## 📋 Overview

- **Authors**: Meng-Li Shih, Shih-Yang Su, Yuliang Zou, Hao Xiang, Haidong Zhu, Vincent Casser, Brian Curless, Dmitry Kalenichenko, Mingxing Tan, Dragomir Anguelov
- **Institution**: Waymo LLC, University of Washington, Google DeepMind
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.13733)
- **Verification**: UNKNOWN (2026-10-15; source 2609.13733v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Freeze π3 geometry features and train a temporally hierarchical camera decoder to predict visual odometry from driving video.

## 🎯 Key Contributions

1. Preserve geometric representations while training a separate camera branch.
2. Model short motions and long trajectories through local/global temporal attention.
3. Evaluate intermediate trajectory supervision and camera augmentation separately.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Driving RGB video sequences.
- **Output**: Per-frame camera trajectories.
- **Problem**: Generic 3D-model pose heads insufficiently model small driving motions and long temporal dependencies.

### Method

1. Freeze the π3 geometry-feature aggregator.
2. Apply local/global temporal decoders to compact camera tokens.
3. Train the camera branch from scratch with intermediate trajectory supervision.
4. FFVO-Long adds VGGT-Long-based trajectory post-processing to window outputs.

The camera decoder requires training. Distinguish FFVO-Long's post-processed long-video results from basic FFVO's direct predictions.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.13733v1), Table 1, PDF p.6.

Waymo Open Dataset (WOD). ATE and translation RPE are in m; rotation RPE is in degrees. Lower is better.

| Method                    | ATE (m) ↓ | RPE trans (m) ↓ | RPE rot (°) ↓ |
| ------------------------- | --------- | --------------- | ------------- |
| π3                        | 1.150     | 0.156           | 0.113         |
| π3 fine-tuned             | 1.170     | 0.332           | 0.125         |
| FFVO without augmentation | 0.714     | 0.118           | 0.124         |
| FFVO                      | 0.862     | 0.114           | 0.128         |

Augmentation lowers translation RPE here but improves neither ATE nor rotation RPE. Separate PDD results use private data, limiting public reproducibility.

## 💡 Insights & Impact

Specialize temporal pose estimation while preserving general geometry-backbone representations.

- Driving-domain training and camera configurations affect performance.
- ATE/RPE do not necessarily improve together; include long-video post-processing costs.

## 🔗 Related Work

- [π3](../reconstruction/pi3.md): the frozen feature backbone.
- [VGGT](../reconstruction/vggt.md): background for long-trajectory processing.

## 📚 Key Takeaways

1. Output camera trajectories from input video.
2. Training mainly targets the temporal camera branch.
3. Read augmentation effects per metric.

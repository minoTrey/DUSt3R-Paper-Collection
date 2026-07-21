# AIM-SLAM: Dense Monocular SLAM via Adaptive and Informative Multi-View Keyframe Prioritization with Foundation Model (arXiv preprint 2026-03)

## 📋 Overview

- **Authors**: Jinwoo Jeon, Dong-Uk Seo, Eungchang Mason Lee, Hyun Myung
- **Institution**: KAIST (Korea Advanced Institute of Science and Technology)
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.05097) | [Project Page](https://aimslam.github.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A dense monocular SLAM framework that prioritizes a sparse, highly overlapping keyframe subset (via a SIGMA module using voxel overlap and information gain) and runs a joint multi-view Sim(3) optimization over VGGT pointmaps, achieving accurate uncalibrated pose estimation and dense reconstruction.

## 🎯 Key Contributions

1. **Adaptive informative multi-view prioritization (SIGMA)**: The Selective Information- and Geometric-aware Multi-view Adaptation module builds a sparse yet highly overlapping keyframe set; a stability criterion adaptively regulates its incorporation into the frontend visual odometry, ensuring geometric consistency and minimizing redundancy.
2. **Joint multi-view Sim(3) optimization**: A joint alignment across multiple views in foundation-model-based SLAM that requires no camera calibration.
3. **Extensive real-world validation**: Evaluations on public datasets for both pose estimation and dense reconstruction, with publicly released code and ROS integration.

## 🔧 Technical Details

### Foundation-model frontend

AIM-SLAM uses a pretrained VGGT to predict per-frame depth with confidence and a dense point cloud expressed in the first frame's coordinates. Keyframe pointmaps are fused via confidence-weighted averaging. The maximum VGGT input subset size `W` is set to 5.

### SIGMA keyframe prioritization

Rather than relying on the N most adjacent views (which contain redundant overlap), SIGMA retrieves candidate keyframes that maximize 3D scene overlap and information gain, adaptively determining the subset size. A stability test regulates adaptive activation; after each multi-view optimization, updated poses and confidences recurrently trigger re-ranking until convergence.

### Joint multi-view Sim(3) optimization

The frontend minimizes a hybrid reprojection residual (Eq. 5–6) using ray-normalization and pinhole projection with VGGT-estimated intrinsics `Ki`; because VGGT intrinsics are not perfectly calibrated, each pair adopts the intrinsics of its preceding keyframe. A backend pose-graph optimization (second-order IRLS) expands sequential and loop edges for global consistency.

### Runtime

On an NVIDIA RTX 3090 with input resized to 518 px, overall runtime is about 3 Hz (dominated by VGGT inference); excluding VGGT inference, the remaining components run at about 17 Hz.

## 📊 Results

### Camera pose accuracy on TUM RGB-D (ATE RMSE, m)

원논문 TABLE I. Lower is better. Calib. = uses camera intrinsics; Uncalib. = no intrinsics.

| Method                 | 360   | desk  | desk2 | floor | plant | room  | rpy   | teddy | xyz   | Avg.  |
| ---------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| DROID-SLAM (Calib.)    | 0.111 | 0.018 | 0.042 | 0.021 | 0.016 | 0.049 | 0.026 | 0.048 | 0.012 | 0.038 |
| MASt3R-SLAM (Calib.)   | 0.049 | 0.016 | 0.024 | 0.025 | 0.020 | 0.061 | 0.027 | 0.041 | 0.009 | 0.030 |
| DROID-SLAM (Uncalib.)  | 0.202 | 0.032 | 0.091 | 0.064 | 0.045 | 0.918 | 0.056 | 0.045 | 0.012 | 0.158 |
| MUSt3R-VO (Uncalib.)   | 0.078 | 0.040 | 0.046 | 0.091 | 0.040 | 0.099 | 0.043 | 0.042 | 0.013 | 0.055 |
| VGGT-Long (Uncalib.)   | 0.053 | 0.064 | 0.060 | 0.111 | 0.064 | 0.170 | 0.036 | 0.127 | 0.047 | 0.081 |
| VGGT-SLAM (Uncalib.)   | 0.071 | 0.025 | 0.040 | 0.141 | 0.023 | 0.102 | 0.030 | 0.034 | 0.014 | 0.053 |
| MASt3R-SLAM (Uncalib.) | 0.070 | 0.035 | 0.055 | 0.056 | 0.035 | 0.118 | 0.041 | 0.114 | 0.020 | 0.060 |
| **AIM-SLAM (ours)**    | 0.050 | 0.017 | 0.028 | 0.024 | 0.026 | 0.062 | 0.021 | 0.039 | 0.010 | 0.031 |

AIM-SLAM is the best uncalibrated method (Avg 0.031), surpassing calibrated DROID-SLAM (0.038) and matching calibrated MASt3R-SLAM (0.030).

### Camera pose accuracy on EuRoC (ATE RMSE, m — average)

원논문 TABLE II. Lower is better. † = average excludes divergent sequences.

| Method                 | Avg.   |
| ---------------------- | ------ |
| DROID-SLAM (Calib.)    | 0.022  |
| DPV-SLAM (Calib.)      | 0.024  |
| MASt3R-SLAM (Calib.)   | 0.041  |
| DROID-SLAM (Uncalib.)  | 0.970  |
| MUSt3R-VO (Uncalib.)   | 0.456† |
| VGGT-Long (Uncalib.)   | 0.367  |
| VGGT-SLAM (Uncalib.)   | 0.749† |
| MASt3R-SLAM (Uncalib.) | 0.164  |
| **AIM-SLAM (ours)**    | 0.072  |

On the aggressive-motion EuRoC benchmark AIM-SLAM has the best uncalibrated average (0.072), far ahead of the submap-based VGGT-SLAM/VGGT-Long and two-view MASt3R-SLAM.

### Dense reconstruction on EuRoC and TUM RGB-D

원논문 TABLE III. Accuracy/Completion/Chamfer, lower is better.

| Method              | EuRoC Acc.↓ | EuRoC Comp.↓ | EuRoC Chamfer↓ | TUM Acc.↓ | TUM Comp.↓ | TUM Chamfer↓ |
| ------------------- | ----------- | ------------ | -------------- | --------- | ---------- | ------------ |
| VGGT-Long           | 0.106       | 0.119        | 0.112          | 0.094     | 0.107      | 0.100        |
| VGGT-SLAM           | 0.246       | 0.216        | 0.231          | 0.109     | 0.127      | 0.118        |
| MASt3R-SLAM         | 0.108       | 0.072        | 0.090          | 0.097     | 0.113      | 0.105        |
| **AIM-SLAM (ours)** | 0.103       | 0.102        | 0.102          | 0.063     | 0.098      | 0.081        |

AIM-SLAM has the best Accuracy on both datasets and the best Completion/Chamfer on TUM; on EuRoC, MASt3R-SLAM retains the best Completion (0.072) and Chamfer (0.090), so AIM-SLAM is best-accuracy with competitive completion/chamfer there.

### Ablation

Increasing the maximum keyframe-subset size `W` improves pose accuracy but saturates beyond 4–5 views; the SIGMA module's advantage over recency-based selection is most evident on EuRoC's larger baselines and rapid viewpoint changes (원논문 Fig. 7, 곡선 수치 미인쇄).

## 💡 Insights & Impact

- **Prioritize views, don't just window them**: Submap/window SLAM built on foundation models over-relies on the N most adjacent (redundant) views; selecting informative, high-overlap keyframes better exploits multi-view geometry.
- **Uncalibrated accuracy**: Joint multi-view Sim(3) optimization over VGGT pointmaps yields calibrated-quality pose without intrinsics, even under EuRoC's aggressive motion.
- **Trade-off**: Focusing on a compact reliable-view subset improves pose stability and geometric accuracy but can slightly reduce dense surface coverage (completion) on some sequences.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The feed-forward geometry foundation model providing dense pointmaps.
- **[VGGT-SLAM](../reconstruction/vggt-slam.md)** and **[VGGT-Long](../reconstruction/vggt-long.md)**: Submap/window-based VGGT SLAM baselines that AIM-SLAM outperforms in the uncalibrated setting.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: Foundational reconstruction priors underlying MASt3R-SLAM.

## 📚 Key Takeaways

1. AIM-SLAM reframes foundation-model SLAM around adaptive, information-gain-driven keyframe prioritization (SIGMA) instead of adjacent-view windows.
2. It achieves the best uncalibrated pose accuracy on TUM (Avg 0.031) and EuRoC (Avg 0.072) and the best reconstruction Accuracy on both, with ROS-integrated code released.
3. A joint multi-view Sim(3) optimization over VGGT pointmaps delivers calibrated-level accuracy without intrinsics, running at ~3 Hz (≈17 Hz excluding VGGT).

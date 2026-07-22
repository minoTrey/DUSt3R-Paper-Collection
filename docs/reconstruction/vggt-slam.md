# VGGT-SLAM: Dense RGB SLAM Optimized on the SL(4) Manifold (NeurIPS 2025)

![vggt-slam — architecture](https://arxiv.org/html/2505.12549/extracted/6471271/fig/sim3_limited.png)

_VGGT-SLAM alignment of 6 submaps created from VGGT using Sim⁢(3)Sim3\mathrm{Sim}(3)roman_Sim ( 3 ) alignment (top) and… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Dominic Maggio, Hyungtae Lim, Luca Carlone
- **Institution**: Massachusetts Institute of Technology
- **Venue**: NeurIPS 2025
- **Links**: [Paper](https://arxiv.org/abs/2505.12549) | [Code](https://github.com/MIT-SPARK/VGGT-SLAM)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Builds a dense RGB SLAM system from VGGT submaps and argues that with uncalibrated cameras those submaps must be aligned by a 15-DOF projective transform, not a similarity transform — yielding the first factor graph SLAM system optimized on the SL(4) manifold.

## 🎯 Key Contributions

1. **Projective ambiguity as a SLAM problem**: Revisits the Projective Reconstruction Theorem — a scene reconstructed from uncalibrated cameras with no assumptions on motion or structure is determined only up to a 15-DOF projective transformation of the true geometry. Sim(3) submap alignment is therefore inadequate in the general uncalibrated case.
2. **SL(4) factor graph optimization**: Formulates submap alignment as MAP estimation over homographies H ∈ SL(4) (real 4×4 matrices with unit determinant), with a 15-dimensional tangent-space parameterization, adjoint-based Jacobians, and Levenberg-Marquardt solving.
3. **Correspondence-free homography estimation**: Because consecutive submaps share an identical frame by construction, dense point correspondences are available without matching. The homography is solved in closed form from the homogeneous system A_k h = 0 with a 5-point RANSAC solver, then normalized by the fourth root of the determinant to land on SL(4).
4. **Loop closure on SL(4)**: SALAD image descriptors retrieve candidate frames from earlier submaps; those frames are appended to the current submap so VGGT reconstructs them jointly, giving direct loop closure homographies with no correspondence estimation.
5. **Scaling VGGT beyond its memory ceiling**: On an RTX 4090 with 24 GB, VGGT is limited to approximately 60 frames. Submapping makes hundreds- or thousands-of-frames reconstruction feasible.

## 🔧 Technical Details

### Why SL(4) and not Sim(3)

For LIDAR-style point clouds, alignment lives in SE(3); if scale differs, Sim(3). But VGGT's point clouds come from uncalibrated cameras. The Projective Reconstruction Theorem states that if correspondences uniquely determine the fundamental matrix, the 3D points are recoverable only up to a 15-DOF homography — and this extends to reconstructions with more than two cameras. VGGT can _leverage learned scene priors_ to often produce near-metric reconstructions, but in the general case where those priors are unreliable, the residual ambiguity is projective.

Note this is not the familiar 8-DOF planar homography in SL(3); it is the 4×4 case in SL(4).

### Pipeline

```text
Keyframe selection : Lucas-Kanade disparity > τ_disparity
Submap assembly    : I ← {M_prior} ∪ I_latest ∪ I_loop     (|I_latest| ≤ w)
VGGT forward       : depth maps D, confidence maps C, camera poses
Point cloud X_S    : inverse-project D (not the 3D DPT head), prune conf < τ_conf
Relative H_ij      : 5-point RANSAC on A_k h = 0, normalize det to 1
Pose correction    : P_i = H_ij^{-1} P_j
Backend            : LM on SL(4) factor graph over odometry + loop closure edges
```

The cost minimized is

```text
Ĥ = argmin_{H ∈ SL(4)}  Σ_{(i,j) ∈ L}  || Log( H_i^{-1} H_j (H_j^i)^{-1} ) ||²_{Ω_ij}
```

with Ω set to identity, Jacobians J_i = −Ad_{H_i^{-1}H_j} and J_j = I₁₅ₓ₁₅, and updates applied on the group as H ← H Exp(δ̂).

The 3D point DPT head is deliberately not used: VGGT's own paper reports more accurate point clouds from inverse-projecting depth with camera-head projection matrices.

### Parameters and setup

w_loop = 1, τ_disparity = 25 pixels, τ_interval = 2, τ_desc = 0.8, τ_conf = 25%, 300 RANSAC iterations with threshold 0.01. NVIDIA GeForce RTX 4090 with AMD Ryzen Threadripper 7960X. Results are averaged over five runs due to RANSAC randomness. A Sim(3) variant of the same pipeline is reported as an ablation baseline.

## 📊 Results

### Camera trajectory error on 7-Scenes

원논문 Table 1. RMSE of ATE, 단위 m. 회색 행(Calib.)은 캘리브레이션된 내부 파라미터를 사용, \*는 uncalibrated 모드 평가.

| Method              | Calib. | chess | fire  | heads | office | pumpkin | kitchen | stairs | Avg   |
| ------------------- | ------ | ----- | ----- | ----- | ------ | ------- | ------- | ------ | ----- |
| NICER-SLAM          | ✓      | 0.033 | 0.069 | 0.042 | 0.108  | 0.200   | 0.039   | 0.108  | 0.086 |
| DROID-SLAM          | ✓      | 0.036 | 0.027 | 0.025 | 0.066  | 0.127   | 0.040   | 0.026  | 0.049 |
| MASt3R-SLAM         | ✓      | 0.053 | 0.025 | 0.015 | 0.097  | 0.088   | 0.041   | 0.011  | 0.047 |
| DROID-SLAM\*        |        | 0.047 | 0.038 | 0.034 | 0.136  | 0.166   | 0.080   | 0.044  | 0.078 |
| MASt3R-SLAM\*       |        | 0.063 | 0.046 | 0.029 | 0.103  | 0.114   | 0.074   | 0.032  | 0.066 |
| Ours (Sim(3), w=32) |        | 0.037 | 0.026 | 0.018 | 0.104  | 0.133   | 0.061   | 0.093  | 0.067 |
| Ours (SL(4), w=32)  |        | 0.036 | 0.028 | 0.018 | 0.103  | 0.133   | 0.058   | 0.093  | 0.067 |

On 7-Scenes VGGT-SLAM ties the best uncalibrated baseline (MASt3R-SLAM\* at 0.066 vs 0.067) rather than beating it, and the `stairs` sequence is a clear loss (0.093 vs 0.032).

### Camera trajectory error on TUM RGB-D

원논문 Table 2. RMSE of ATE, 단위 m. ×는 해당 시퀀스 실패.

| Method              | 360   | desk  | desk2 | floor | plant | room  | rpy   | teddy | xyz   | Avg       |
| ------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | --------- |
| DeepV2D             | 0.243 | 0.166 | 0.379 | 1.653 | 0.203 | 0.246 | 0.105 | 0.316 | 0.064 | 0.375     |
| DPV-SLAM++          | 0.132 | 0.018 | 0.029 | 0.050 | 0.022 | 0.096 | 0.032 | 0.098 | 0.010 | 0.054     |
| GO-SLAM             | 0.089 | 0.016 | 0.028 | 0.025 | 0.026 | 0.052 | 0.019 | 0.048 | 0.010 | 0.035     |
| DROID-SLAM          | 0.111 | 0.018 | 0.042 | 0.021 | 0.016 | 0.049 | 0.026 | 0.048 | 0.012 | 0.038     |
| MASt3R-SLAM         | 0.049 | 0.016 | 0.024 | 0.025 | 0.020 | 0.061 | 0.027 | 0.041 | 0.009 | 0.030     |
| DROID-SLAM\*        | 0.202 | 0.032 | 0.091 | 0.064 | 0.045 | 0.918 | 0.056 | 0.045 | 0.012 | 0.158     |
| MASt3R-SLAM\*       | 0.070 | 0.035 | 0.055 | 0.056 | 0.035 | 0.118 | 0.041 | 0.114 | 0.020 | 0.060     |
| Ours (Sim(3), w=32) | 0.123 | 0.040 | 0.055 | 0.254 | 0.022 | 0.088 | 0.041 | 0.032 | 0.016 | 0.074     |
| Ours (SL(4), w=32)  | 0.071 | 0.025 | 0.040 | 0.141 | 0.023 | 0.102 | 0.030 | 0.034 | 0.014 | **0.053** |

The SL(4) version is the best uncalibrated method overall at 0.053 m. The `floor` sequence (0.141) is the paper's acknowledged failure mode: it contains images viewing only the flat floor, which makes the homography degenerate and causes the reconstruction to diverge.

### Dense reconstruction on 7-Scenes

원논문 Table 3. 단위 m. @n은 n장마다 키프레임.

| Method              | Calib. | ATE ↓ | Acc. ↓    | Complet. ↓ | Chamfer ↓ |
| ------------------- | ------ | ----- | --------- | ---------- | --------- |
| DROID-SLAM          | ✓      | 0.049 | 0.141     | 0.048      | 0.094     |
| MASt3R-SLAM         | ✓      | 0.047 | 0.089     | 0.085      | 0.087     |
| Spann3R @20         | ✓      | N/A   | 0.069     | 0.047      | 0.058     |
| Spann3R @2          | ✓      | N/A   | 0.124     | 0.043      | 0.084     |
| MASt3R-SLAM\*       |        | 0.066 | 0.068     | **0.045**  | 0.056     |
| Ours (Sim(3), w=32) |        | 0.067 | **0.052** | 0.062      | 0.057     |
| Ours (SL(4), w=32)  |        | 0.067 | **0.052** | 0.058      | **0.055** |

VGGT-SLAM achieves the best accuracy and Chamfer distance; completeness is its weakest of the three, behind MASt3R-SLAM\*.

### Effect of submap size

원논문 Table 5 (부록). TUM RGB-D ATE RMSE, 단위 m.

| Method              | 360   | desk  | desk2 | floor | plant | room  | rpy   | teddy | xyz   | Avg   |
| ------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| Ours (Sim(3), w=32) | 0.123 | 0.040 | 0.055 | 0.254 | 0.022 | 0.088 | 0.041 | 0.032 | 0.016 | 0.074 |
| Ours (SL(4), w=8)   | 0.179 | 0.046 | 0.095 | 0.210 | 0.033 | 0.272 | 0.038 | 0.130 | 0.031 | 0.115 |
| Ours (SL(4), w=16)  | 0.147 | 0.032 | 0.087 | 0.158 | 0.027 | 0.150 | 0.037 | 0.069 | 0.035 | 0.083 |
| Ours (SL(4), w=32)  | 0.071 | 0.025 | 0.040 | 0.141 | 0.023 | 0.102 | 0.030 | 0.034 | 0.014 | 0.053 |

Larger submaps are consistently better: fewer submaps means fewer relative homographies and less opportunity for drift. The TUM `360` scene in particular is challenging at small w because smaller submaps are more likely to encounter approximately pure rotation, which reduces depth accuracy and raises the RANSAC outlier ratio.

원논문 Table 6 (부록). 7-Scenes dense reconstruction, 단위 m.

| Method              | ATE ↓ | Acc. ↓ | Complet. ↓ | Chamfer ↓ |
| ------------------- | ----- | ------ | ---------- | --------- |
| MASt3R-SLAM\*       | 0.066 | 0.068  | 0.045      | 0.056     |
| Ours (Sim(3), w=1)  | 0.070 | 0.066  | 0.051      | 0.059     |
| Ours (Sim(3), w=8)  | 0.067 | 0.054  | 0.056      | 0.055     |
| Ours (Sim(3), w=32) | 0.067 | 0.052  | 0.062      | 0.057     |
| Ours (SL(4), w=1)   | 0.090 | 0.080  | 0.068      | 0.074     |
| Ours (SL(4), w=8)   | 0.084 | 0.067  | 0.065      | 0.066     |
| Ours (SL(4), w=16)  | 0.075 | 0.061  | 0.063      | 0.060     |
| Ours (SL(4), w=32)  | 0.067 | 0.052  | 0.058      | 0.055     |

At w = 1 the SL(4) formulation is notably worse than Sim(3) — with only one keyframe per submap the extra 15 DOF have too little constraint and add drift.

### Ablations

Figure 3 reports three ablations qualitatively: (a) loop closures improve pose accuracy across w ∈ {8, 16, 32} with a tight spread over five runs, with paired t-test annotations for 10⁻³ < p ≤ 10⁻²; (b) the ATE reduction from loop closure grows as the number of submaps increases; (c) larger τ_conf raises dense reconstruction accuracy and lowers completion, with the 25% default balancing the two.

## 💡 Insights & Impact

### A geometry argument, not an engineering one

Most VGGT extensions attack memory or latency. VGGT-SLAM instead asks what group submaps actually live in, and answers with a classical multi-view geometry result. That the answer is SL(4) rather than Sim(3) is the paper's whole thesis, and it produces a genuinely new object: a factor graph optimized on a manifold nobody had used for SLAM.

### The extra DOF are not free

The results are refreshingly candid about this. Sim(3) performs comparably on most sequences precisely because VGGT's learned priors usually deliver near-metric reconstructions. SL(4)'s advantage appears in the harder cases (Fig. 1) and in the TUM average, but with small submaps (w = 1, w = 8) the added degrees of freedom actively hurt. Fifteen DOF also open a new drift mode — not just scale, rotation, and translation drift, but drift in _scene perspective_.

### Planar degeneracy is a real limitation

Estimating a full 15-DOF homography is degenerate when points are planar. The TUM `floor` scene demonstrates this concretely, and the paper flags robustness to the planar case as necessary future work, suggesting MASt3R-SLAM's ray-based matching as a possible remedy.

### Submapping as the standard workaround

The concrete number driving the design — VGGT limited to roughly 60 frames on a 24 GB RTX 4090 — is the same constraint that motivates [FastVGGT](fastvggt.md) and [StreamVGGT](streamvggt.md). VGGT-SLAM's answer is to keep VGGT unmodified and put the scaling in a classical SLAM backend.

## 🔗 Related Work

- [VGGT](vggt.md) — the reconstruction front end, used unmodified. VGGT-SLAM consumes its depth maps, confidence maps, and camera head outputs, deliberately skipping the 3D point DPT head.
- [MASt3R-SLAM](mast3r-slam.md) — the closest prior system and primary baseline in both calibrated and uncalibrated modes. VGGT-SLAM follows its evaluation protocol for dense reconstruction.
- [Spann3R](spann3r.md) — included in the dense reconstruction comparison at two keyframe rates.
- [DUSt3R](../foundation/dust3r.md) — the pairwise ancestor whose point clouds enabled pose recovery via 3-point RANSAC.
- [FastVGGT](fastvggt.md) / [StreamVGGT](streamvggt.md) — alternative answers to the same VGGT frame-count ceiling, via token merging and causal attention respectively rather than submapping.
- [Point3R](point3r.md) — benchmarks itself against MASt3R-SLAM on the same 7-Scenes mapping/tracking axes, from the feed-forward rather than the SLAM side.

## 📚 Key Takeaways

1. **Uncalibrated submaps are related by a projective transform, not a similarity transform.** This is a theorem, not a heuristic, and it invalidates the default Sim(3) assumption for feed-forward SLAM back ends.
2. **SL(4) optimization is tractable**: a 15-dimensional tangent space, adjoint Jacobians, and Levenberg-Marquardt give a working factor graph backend.
3. **Shared frames remove the correspondence problem.** By construction every pair of adjacent submaps contains an identical frame, so dense correspondences are free — for odometry and for loop closures alike.
4. **Larger submaps win.** w = 32 dominates w = 8 and w = 16 across TUM, and at w = 1 the SL(4) formulation is actively worse than Sim(3).
5. **Planar scenes break it.** The TUM `floor` divergence is the honest counterexample the paper leads with in its limitations.

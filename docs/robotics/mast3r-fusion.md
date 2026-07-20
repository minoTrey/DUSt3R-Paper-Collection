# MASt3R-Fusion: Integrating Feed-Forward Visual Model with IMU, GNSS for High-Functionality SLAM (arXiv preprint)

## 📋 Overview

- **Authors**: Yuxuan Zhou, Xingxing Li, Shengyu Li, Zhuohao Yan, Chunxi Xia, Shaoquan Feng
- **Institution**: School of Geodesy and Geomatics, Wuhan University
- **Venue**: arXiv preprint (2025-09)
- **Note**: The venue could not be confirmed from any primary source and should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2509.20757) | [Code](https://github.com/GREAT-WHU/MASt3R-Fusion)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: A multi-sensor SLAM framework that injects Sim(3)-based pointmap alignment constraints from MASt3R into a metric-scale SE(3) factor graph alongside IMU and GNSS, resolving the scale ambiguity that cripples visual-only feed-forward SLAM at kilometer scale.

## 🎯 Key Contributions

1. **Sim(3)-to-SE(3) bridging**: visual alignment constraints are expressed in Hessian form and folded into a universal metric-scale SE(3) factor graph, so scaleless pointmap regression can be fused probabilistically with metric sensors.
2. **Real-time visual-inertial SLAM** with metric-scale pose estimation and dense scene structure perception built directly on the feed-forward model.
3. **Hierarchical factor graph**: supports both real-time sliding-window optimization and global optimization with aggressive loop closures.
4. **Globally consistent SLAM with GNSS**, including geometry-based loop closure candidate filtering and full-information iterative optimization.
5. **Evaluation on public and self-collected data** — KITTI-360, SubT-MRS, and a self-collected Wuhan urban multi-sensor dataset — with open-source release.

The system is stated to handle arbitrarily long sequences on 8 GB of GPU memory.

## 🔧 Technical Details

### Two-view feed-forward front-end

MASt3R is used as the pointmap regressor. Two images are encoded independently, `F_i = F_enc(I_i)`, then jointly decoded:

```text
X_i^ij, X_j^ij, D_i^ij, D_j^ij = F_dec(F_i, F_j)
```

producing two `(H×W, 3)` pointmaps expressed in reference frame `i` plus two `(H×W, D)` descriptor maps.

### Three-stage data association

1. **Ray-proximity matching**: because both pointmaps live in frame `i`, dense correspondence is obtained by minimizing the angular distance between normalized 3D rays. Bilinear interpolation is used for retrieval and the pointmap gradient map drives efficient optimization. Correspondences with large depth residuals are then masked as invalid — this is how dynamic objects are rejected, _using_ the 3D structure awareness of the model.
2. **Descriptor refinement**: a neighborhood search (rather than continuous optimization, since descriptor maps lack smoothness) maximizes `d(D_i^ij[u_j^i], D_j^ij)`.
3. **Sub-pixel refinement**: the target descriptor map is bilinearly upsampled by a factor of 4 and the search repeated, which the paper reports contributes to better SLAM accuracy.

### Pose representation

Each frame carries a pointmap and a camera-to-world Sim(3) transform

```text
S_i = [[sR, t], [0, 1]] ∈ Sim(3)
```

where the scale `s` first normalizes camera-frame points to a unified scale before transforming to world coordinates. This Sim(3) state is what must be reconciled with the metric SE(3) states of the inertial and GNSS factors.

### Two distinctions from classical SLAM

The paper identifies exactly two things the feed-forward front-end changes: (1) **powerful 3D priors**, giving instant scaleless structure and thus a different visual-constraint construction than bundle adjustment; and (2) **aggressive data association**, where 3D awareness enables dense matching to survive extremely large viewpoint changes — including viewpoint differences exceeding 90° or fully opposite views, which the authors note surpasses what feature-based matching can do.

## 📊 Results

### Relative pose errors, KITTI-360

원논문 Table I. `t_rel` in %, `r_rel` in °/100 m. MASt3R-SLAM is visual-only, scaled with Sim(3) global alignment.

| Seq. | Desc.     | VINS-Fusion t/r | ORB-SLAM3 t/r | DM-VIO t/r    | MASt3R-SLAM t/r | DBA-Fusion t/r | MASt3R-Fusion t/r |
| ---- | --------- | --------------- | ------------- | ------------- | --------------- | -------------- | ----------------- |
| 0000 | Suburb    | 1.897 / 0.176   | 2.386 / 0.117 | 1.369 / 0.129 | 39.64 / 0.524   | 0.678 / 0.105  | 0.726 / 0.151     |
| 0002 | Suburb    | 1.006 / 0.199   | 1.309 / 0.215 | 0.724 / 0.183 | 43.88 / 0.600   | 0.577 / 0.174  | 0.504 / 0.145     |
| 0003 | Highway   | 2.754 / 0.088   | 7.044 / 0.151 | 1.146 / 0.111 | 21.59 / 0.488   | 1.041 / 0.114  | 0.406 / 0.079     |
| 0004 | Suburb    | 1.710 / 0.193   | 1.976 / 0.211 | 1.063 / 0.178 | 48.79 / 0.887   | 0.556 / 0.153  | 0.770 / 0.157     |
| 0005 | Suburb    | 1.187 / 0.219   | 1.414 / 0.227 | 0.729 / 0.224 | 32.50 / 0.799   | 0.619 / 0.209  | 0.544 / 0.208     |
| 0006 | Suburb    | 1.349 / 0.176   | 1.685 / 0.184 | 0.887 / 0.161 | 54.09 / 0.695   | 0.734 / 0.166  | 0.658 / 0.155     |
| 0009 | Suburb    | 1.596 / 0.144   | 2.407 / 0.184 | 1.379 / 0.136 | 54.58 / 0.570   | 0.846 / 0.136  | 0.631 / 0.144     |
| 0010 | Boulevard | 3.610 / 0.216   | 5.335 / 0.214 | 2.130 / 0.215 | 47.06 / 0.513   | 1.486 / 0.208  | 1.138 / 0.198     |

The paper reports the average RTE as **43.0% lower than DM-VIO and 17.7% lower than DBA-Fusion**. Note DBA-Fusion is still ahead on sequences 0000 and 0004. The visual-only MASt3R-SLAM effectively fails at this scale, with translation errors an order of magnitude larger.

### Absolute translation errors with loop closure, KITTI-360

원논문 Table II. Values in meters; VGGT-Long is visual-only, scaled with Sim(3) global alignment.

| Seq.    | VGGT-Long | ORB-SLAM3 | MASt3R-Fusion | Length (m) |
| ------- | --------- | --------- | ------------- | ---------- |
| 0000    | 103.64    | 26.03     | **2.13**      | 8361       |
| 0002    | 310.76    | 32.57     | **2.82**      | 11195      |
| 0003    | 26.46     | 28.63     | **0.70**      | 1368       |
| 0004    | 165.67    | 42.82     | **4.56**      | 8614       |
| 0005    | 234.48    | 10.37     | **1.28**      | 4561       |
| 0006    | 179.95    | 9.51      | **2.52**      | 7699       |
| 0009    | 135.23    | 6.95      | **1.90**      | 8677       |
| 0010    | 211.54    | 45.17     | **4.38**      | 3340       |
| ave (%) | 2.91      | 0.63      | **0.05**      | norm.      |

Average ATE relative to trajectory length reaches **0.05%** using only monocular visual-inertial data.

### SubT-MRS — generalization to caves and indoor/outdoor transitions

원논문 Table III, real-time VIO, absolute translation errors in meters.

| Seq.         | VINS | ORB  | DM-VIO | DBA  | MASt3R-Fusion | Length (m) |
| ------------ | ---- | ---- | ------ | ---- | ------------- | ---------- |
| handheld1    | 5.64 | 2.16 | 14.54  | 1.78 | **1.07**      | 394        |
| handheld2    | 2.32 | 2.42 | 4.94   | 2.09 | **1.13**      | 509        |
| overexposure | 2.61 | 1.27 | 2.97   | 1.85 | **0.99**      | 509        |
| ave (%)      | 0.80 | 0.42 | 1.74   | 0.41 | **0.23**      | norm.      |

원논문 Table IV, global SLAM with loop closure, ATE in meters. VGGT-Long is visual-only.

| Seq.          | VGGT-Long | ORB-SLAM3 | MASt3R-Fusion | Length (m) |
| ------------- | --------- | --------- | ------------- | ---------- |
| handheld1     | fail      | 1.48      | **0.26**      | 394        |
| handheld2     | fail      | 2.14      | **1.04**      | 395        |
| overexporsure | fail      | 1.07      | **0.43**      | 509        |
| ave (%)       | -         | 0.37      | **0.13**      | norm.      |

VGGT-Long fails on all three SubT-MRS sequences.

### Wuhan urban dataset — relative pose errors

원논문 Table V. `t_rel` in %, `r_rel` in °/100 m.

| Seq. | VINS-Fusion t/r | DBA-Fusion t/r | M-Fus. w/o loop t/r | M-Fus. w/ loop t/r |
| ---- | --------------- | -------------- | ------------------- | ------------------ |
| (a)  | 2.07 / 0.11     | 1.45 / 0.11    | 1.20 / 0.11         | **0.53 / 0.07**    |
| (b)  | 5.85 / 0.13     | 3.01 / 0.13    | 1.68 / 0.13         | **0.92 / 0.06**    |

### GNSS-integrated global positioning

원논문 Table VI. Horizontal position RMSEs in meters. "Real" uses GNSS RTK; "Simu." uses simulated GNSS with intermittent outages.

| Mode  | Seq. | GNSS RTK | VINS-Fusion | DBA-Fusion | M-Fus. w/o loop | M-Fus. w/ loop |
| ----- | ---- | -------- | ----------- | ---------- | --------------- | -------------- |
| Real  | (a)  | 4.36     | 2.54        | 0.78       | 0.24            | **0.21**       |
| Real  | (b)  | 1.46     | 0.62        | 0.24       | 0.13            | **0.09**       |
| Simu. | (a)  | -        | 2.84        | 3.20       | 0.69            | **0.37**       |
| Simu. | (b)  | -        | 9.66        | 2.94       | 1.02            | **0.46**       |

The paper notes that under 100-second GNSS outages the global factor graph still achieves mostly sub-meter trajectory smoothing, and that cross-temporal associations further reduce overall error.

### Qualitative 3D perception

Real-time metric-scale dense perception is compared against DBA-Fusion and Metric3D v2 (ViT-Large) in Figure 10 and reconstruction results in Figure 17. These are qualitative only — no numeric reconstruction metrics are reported, so none are transcribed here.

## 💡 Insights & Impact

### Scale is the wall for visual-only feed-forward SLAM

The clearest message in the paper is quantitative: MASt3R-SLAM records 21–55% relative translation error on KITTI-360 and VGGT-Long records 26–311 m ATE, while the same visual front-end fused with an IMU reaches 0.4–1.1% RTE and 0.7–4.6 m ATE. The failure is not in the pointmaps; it is in the unconstrained Sim(3) scale, and inertial measurements are exactly the right prior for fixing it.

### The multi-sensor community's tools were left on the table

The abstract's framing is that "the widely validated advantages of probabilistic multi-sensor information fusion are often discarded" in feed-forward pipelines. This paper is essentially an argument that DUSt3R-family front-ends should be treated as _measurement sources_ inside a factor graph, not as end-to-end replacements for one.

### Loop closure gets better, not just cheaper

The 3D-aware dense matching survives viewpoint differences beyond 90°, which means loop closures can fire when driving the _opposite direction_ down a road — a case where classical feature matching typically fails. That is what lets ATE/length reach 0.05% on kilometer-scale KITTI-360 sequences.

### Why VGGT-Long underperforms despite a stronger backbone

The authors attribute VGGT-Long's poor showing not to the model but to system dynamics: significant scale drift over large scenes makes global optimization difficult and makes the system sensitive to false loop closures, forcing conservative strategies. Adding IMU information is what allows the feed-forward model's potential to be realized.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md) — the two-view pointmap and descriptor front-end this system is built on.
- [MASt3R-SLAM](../reconstruction/mast3r-slam.md) — the visual-only predecessor whose pointmap-alignment practice is followed and whose scale failures motivate the work.
- [DUSt3R](../foundation/dust3r.md) — the originating pointmap regression paradigm.
- [VGGT](../reconstruction/vggt.md) — the backbone of the VGGT-Long baseline in Tables II and IV.
- [VGGT-SLAM](../reconstruction/vggt-slam.md) — a related SLAM system built on VGGT.
- [Unifying Scene Representation](../robotics/unifying-scene-representation.md) — related robotics-oriented reconstruction work in this collection.

## 📚 Key Takeaways

1. **Fusing IMU with a feed-forward front-end changes the accuracy regime, not just the numbers** — MASt3R-SLAM's 21.59–54.58% RTE on KITTI-360 collapses to 0.406–1.138% for MASt3R-Fusion (원논문 Table I).
2. **Average ATE/length of 0.05% on KITTI-360** with monocular visual-inertial input alone (원논문 Table II).
3. **The improvement is honest but not uniform**: DBA-Fusion still wins KITTI-360 sequences 0000 and 0004 on relative translation error.
4. **Sim(3) constraints in Hessian form** are the technical bridge that lets scaleless pointmaps participate in a metric SE(3) factor graph.
5. **GNSS gross errors are absorbed rather than propagated** — decimeter-level accuracy is maintained through RTK-degraded periods, and sub-meter smoothing survives 100-second simulated outages (원논문 Table VI).

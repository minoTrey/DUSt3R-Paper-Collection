# ScaRF-SLAM: Scale-Consistent Reconstruction with Feed-Forward Models and Classical Visual SLAM (arXiv preprint 2026-05)

![scarf-slam — architecture](https://arxiv.org/html/2606.00307v1/images/recon_demo.jpg)

_Top: A consistent two-floor dense reconstruction produced by our mapping module, including rooms visited multiple times (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Yuhao Zhang, Yifu Tao, Frank Dellaert, Maurice Fallon
- **Institution**: Oxford Robotics Institute, University of Oxford; College of Computing, Georgia Institute of Technology
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2606.00307) | [Code](https://github.com/ori-drs/ScaRF-SLAM)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A decoupled SLAM framework that uses classical feature-based SLAM (e.g. ORB-SLAM3) for robust low-latency tracking and a geometric foundation model (DepthAnything3) purely for dense mapping, enforcing scale consistency via lightweight frame- and submap-level scale optimization anchored to the SLAM poses.

## 🎯 Key Contributions

1. **Decoupled GFM mapping framework**: Instead of tightly coupling tracking and mapping in a single GFM pipeline, ScaRF-SLAM uses classical SLAM for tracking and a GFM only for mapping — preserving the maturity, sensor re-configurability (visual-inertial, multi-camera, fisheye) and low-latency pose estimation of classical systems.
2. **Scale correction + point-cloud fusion**: A frame-level and submap-level scale optimization (anchored to fixed SLAM poses) plus confidence-weighted projection-based fusion, robust to GFM degradation under small input batch sizes.
3. **Building-scale indoor dataset (ORI)**: A loop-rich, multi-floor fisheye dataset with LiDAR ground-truth trajectories and reconstruction, for evaluating dense visual SLAM.
4. **Real-world validation**: Evaluated on handheld device and a quadruped (ANYmal-D) with multi-session, multi-camera, multi-modal operation.

## 🔧 Technical Details

### Decoupled Pipeline

- A classical SLAM system provides instantaneous poses; recent posed keyframes are grouped into a batch, rectified to pinhole images, and fed to DepthAnything3 (DA3) for dense depth. Each batch defines a submap.
- DA3 predicts per-frame dense depth + confidence maps; when poses are provided, DA3 aligns its internal poses to the input via Sim(3) and overwrites intrinsics/poses with the inputs.

### Scale Optimization

- **Frame-level**: A per-frame scale variable `si` is optimized using sparse LightGlue matches with geometric verification, minimizing L2 distance between matched 3D points across the batch (solved with GTSAM), anchored to fixed SLAM poses `Ti`.
- **Submap-level**: A per-submap scale variable enforces global scale consistency using one overlapping frame between consecutive submaps; larger inter-submap baselines improve scale observability. A sliding-window strategy optimizes only the latest N submaps; global optimization triggers after loop closure.
- **Point-cloud fusion**: Correspondences are derived directly from predicted geometry (DA3 provides no matching features), then matched points are fused via confidence-weighted averaging.

### Adaptive Keyframe Selection & Map Update

- Keyframes selected on relative motion (`Δt > τt` or `ΔR > τR`); the translation threshold `τt` adapts to median scene depth, with range filtering `dmax = ατt` (α = 20).
- On loop closure, submaps are transformed by updated anchor poses and re-optimized.

## 📊 Results

### Monocular Tracking (ATE) on EuRoC

원논문 Table I. ATE (m), initialization phase excluded. ORB-SLAM3 is monocular; all methods use calibrated intrinsics and rectified images. Lower is better.

| Method        | MH01   | MH02   | MH03   | MH04   | MH05   |
| ------------- | ------ | ------ | ------ | ------ | ------ |
| DA3-Long      | 0.3481 | 0.5270 | 0.6023 | 0.3333 | 0.5918 |
| MASt3R-SLAM   | 0.0274 | 0.0291 | 0.0580 | 0.1180 | 0.0674 |
| VGGT-SLAM2    | 0.0614 | 0.0800 | 0.1284 | 0.6447 | 0.3560 |
| VGGT(D)-SLAM2 | 0.0962 | 0.0718 | 0.0620 | 0.3456 | 0.2246 |
| ORB-SLAM3\*   | 0.0206 | 0.0193 | 0.0298 | 0.0996 | 0.0459 |

On EuRoC with proper initialization, classical ORB-SLAM3 outperforms all fully GFM-enabled methods in tracking — the paper's motivation for decoupling tracking from GFM mapping.

### Chunk-wise Reconstruction Quality on ORI (Indoor)

원논문 Table III. Chunk length = 10 m, threshold = 3 cm, conf. percentile = 25%. Precision higher better, reconstruction error lower better. "Ours w/o Ext." disables pose inputs to DA3.

| Method           | R01 Prec.(%) ↑ | R01 Err.(m) ↓ | R05 Prec.(%) ↑ | R05 Err.(m) ↓ |
| ---------------- | -------------- | ------------- | -------------- | ------------- |
| Scal3R (Offline) | 50.32          | 0.0555        | 55.50          | 0.0661        |
| DA3-Long         | 65.64          | 0.0359        | 56.58          | 0.0481        |
| MASt3R-Fusion    | 62.97          | 0.0437        | 54.36          | 0.0781        |
| VGGT-SLAM2       | 19.85          | 0.1747        | 25.78          | 0.1513        |
| VGGT(D)-SLAM2    | 60.61          | 0.0391        | 52.38          | 0.0582        |
| Ours w/o Ext.    | 78.64          | 0.0230        | 81.94          | 0.0210        |
| **Ours**         | **81.06**      | **0.0216**    | **82.90**      | **0.0198**    |

Ours improves precision over other methods by 10%–20% while maintaining ~2 cm reconstruction error; with poses enabled it beats the "w/o Ext." variant, confirming the value of the decoupled pose-input design.

### Ablation: Scale Optimization Components (batch size = 6)

원논문 Table IV. Global precision (%) ↑ and reconstruction error (m) ↓; "Imp." is improvement relative to DepthAnything3.

| Method               | R01 Prec. ↑ | R04 Prec. ↑ | R01 Err. ↓ | R04 Err. ↓ |
| -------------------- | ----------- | ----------- | ---------- | ---------- |
| DepthAnything3       | 78.91       | 67.44       | 0.0224     | 0.0319     |
| Ours w/o Frame Opt.  | 82.52       | 81.32       | 0.0192     | 0.0200     |
| Ours w/o Submap Opt. | 83.38       | 74.83       | 0.0197     | 0.0262     |
| Ours w/o Points Fus. | 81.30       | 83.96       | 0.0201     | 0.0183     |
| **Ours**             | 81.81       | 84.88       | 0.0198     | 0.0178     |

Under batch size 6 the method achieves up to 17% absolute precision improvement over directly aggregating DA3 predictions; disabling either scale-optimization component degrades quality (e.g. R04).

### Runtime (batch size 6)

원논문 Table VII. Per-submap (6 frames) runtime in seconds; a submap takes ~1.5 s on average (Laptop), giving a maximum real-time keyframe rate of ~3.3 Hz.

| Platform | DA3 Infer. | LightGlue | Frm. Opt. | Points Fus. | Smp. Opt. |
| -------- | ---------- | --------- | --------- | ----------- | --------- |
| Laptop   | 0.9275     | 0.3196    | 0.0465    | 0.1014      | 0.1223    |
| Jetson   | 4.6413     | 1.4319    | 0.2023    | 0.2571      | 0.4302    |

## 💡 Insights & Impact

- **The bottleneck is pose reliability, not geometry generation**: The paper argues current GFMs are strong at dense geometry but their predictions are unreliable for accurate pose estimation; anchoring reconstruction to classical SLAM poses combines the strengths of both.
- **Robust to small batch sizes**: Because it optimizes only depth scales anchored to fixed poses (rather than Sim(3)/SL(4) alignment over noisy predictions), the framework is much less affected by reduced batch sizes (−1.60% precision vs −8.03% for direct DA3), important for memory-constrained robots.
- **System-level integration over tighter coupling**: Progress in learned geometry does not require replacing classical geometric pipelines — lightweight geometric constraints on top of learned predictions balance accuracy, efficiency and robustness.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)** & **[MASt3R](../foundation/mast3r.md)**: GFMs underlying compared fully-coupled SLAM systems (VGGT-SLAM2, MASt3R-SLAM/Fusion).
- **[MASt3R-SLAM](../reconstruction/mast3r-slam.md)**: The tightly-coupled GFM SLAM baseline contrasted against the decoupled design.
- **[VGGT-Long](../reconstruction/vggt-long.md)**: Temporal chunking for long sequences, adapted here as DA3-Long.
- **[MapAnything](../reconstruction/mapanything.md)**: Metric feed-forward GFM discussed among GFM-enabled SLAM.

## 📚 Key Takeaways

1. Decoupling tracking (classical SLAM) from mapping (GFM) yields more robust, practical dense SLAM than tightly-coupled GFM pipelines.
2. Frame- and submap-level scale optimization anchored to fixed SLAM poses enforces global scale consistency and is robust to small GFM batch sizes (up to 17% absolute precision gain over raw DA3).
3. Delivers ~2 cm reconstruction error per 10 m chunk indoors (10 cm per 30 m outdoors) with a 10%–20% precision improvement over existing methods, validated on a new LiDAR-ground-truth building-scale dataset and on real robots.

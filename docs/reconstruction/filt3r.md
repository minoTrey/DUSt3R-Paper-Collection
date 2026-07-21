# FILT3R: Latent State Adaptive Kalman Filter for Streaming 3D Reconstruction (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Seonghyun Jin, Jong Chul Ye
- **Institution**: KAIST AI
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.18493) | [Code](https://github.com/jinotter3/FILT3R)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free latent filtering layer that recasts a streaming reconstructor's recurrent state update as adaptive Kalman filtering in token space, maintaining a per-token variance and Kalman gain that balance memory retention against new observations for stable long-horizon depth, pose, and reconstruction.

## 🎯 Key Contributions

1. **Streaming update as stochastic state estimation**: Interprets the recurrent state as a belief and the decoder's candidate as a noisy measurement, casting the update as Kalman-style interpolation in latent token space.
2. **Adaptive process noise, fixed measurement noise**: Estimates process noise online from EMA-normalized temporal drift while keeping measurement noise a single fixed scalar r, avoiding the gain overshoot that fully-adaptive noise would cause.
3. **Training-free plug-in generalizing prior rules**: A lightweight, interpretable update that recovers uniform overwrite (CUT3R) and heuristic gating (TTT3R) as special cases, with theory showing O(1/t) gain decay in static scenes.
4. **Long-horizon stability**: Extends the effective memory horizon and reduces drift/forgetting beyond the training horizon across depth, pose, and reconstruction.

## 🔧 Technical Details

### Formulation

- State-space model in token space: sₜ = sₜ₋₁ + wₜ (process noise Qₜ), s̃ₜ = sₜ + vₜ (measurement noise R = r·I).
- Diagonal per-token variance pₜ ∈ ℝᴺ. Prediction p⁻ₜ = pₜ₋₁ + qₜ; Kalman gain kₜ = p⁻ₜ / (p⁻ₜ + r); update sₜ = sₜ₋₁ + kₜ ⊙ (s̃ₜ − sₜ₋₁); variance via scalar Joseph form pₜ = (1−kₜ)² ⊙ p⁻ₜ + r·kₜ².

### Adaptive Process Noise

- qₜ,ᵢ set by a sigmoid gate of a normalized drift score gₜ,ᵢ = Δₜ,ᵢ / Δ̂ₜ, where Δₜ,ᵢ is the L2 drift of consecutive candidate states and Δ̂ₜ is an EMA baseline of the stream's mean drift.
- Small drift → qₜ near q_min (stable, gain shrinks); large drift → q_max (scene change, gain rises). Gain clamped to [k_min, k_max]; EMA baseline clamped to a floor.

### Relation to Prior Rules

- Uniform overwrite (CUT3R): βₜ ≡ 1, equivalent to r = 0. Heuristic gates (TTT3R): instantaneous attention/change gate without propagated covariance. Fixed interpolation: a single point on the steady-state q/r curve.
- Drop-in replacement for the state update in a CUT3R-style recurrent architecture; all methods share identical backbone weights and inference code, changing only the online update.

## 📊 Results

### Long-horizon 3D Reconstruction on 7-Scenes (mean)

원논문 Table 1(a). Acc/Comp ↓, NC ↑. Mean 값만 발췌. Point3R는 length 1000에서 OOM.

| Method        | L300 Acc ↓ | L300 NC ↑ | L500 Acc ↓ | L500 NC ↑ | L1000 Acc ↓ | L1000 NC ↑ |
| ------------- | ---------- | --------- | ---------- | --------- | ----------- | ---------- |
| CUT3R         | 0.134      | 0.544     | 0.183      | 0.530     | 0.233       | 0.511      |
| Point3R       | 0.045      | 0.564     | 0.057      | 0.556     | OOM         | OOM        |
| TTT3R         | 0.040      | 0.566     | 0.066      | 0.551     | 0.145       | 0.525      |
| FILT3R (ours) | **0.020**  | **0.568** | **0.024**  | **0.559** | **0.054**   | **0.535**  |

### Long-horizon Camera Pose on TUM-RGBD

원논문 Table 2. ATEorig는 첫 프레임만 정렬해 누적 drift를 노출.

| Method        | T400 ATE ↓ | T400 ATEorig ↓ | T600 ATE ↓ | T600 ATEorig ↓ | T800 ATE ↓ | T800 ATEorig ↓ |
| ------------- | ---------- | -------------- | ---------- | -------------- | ---------- | -------------- |
| CUT3R         | 0.109      | 0.302          | 0.145      | 0.425          | 0.173      | 0.493          |
| TTT3R         | 0.055      | 0.128          | 0.084      | 0.176          | 0.097      | 0.214          |
| FILT3R (ours) | **0.033**  | **0.074**      | **0.042**  | **0.082**      | **0.057**  | **0.107**      |

### Long-horizon Video Depth on Bonn (metric scale)

원논문 Table 3.

| Method        | B300 AbsRel ↓ | B300 δ<1.25 ↑ | B400 AbsRel ↓ | B400 δ<1.25 ↑ | B500 AbsRel ↓ | B500 δ<1.25 ↑ |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| CUT3R         | 0.107         | 88.7          | 0.107         | 89.6          | 0.101         | 90.6          |
| TTT3R         | 0.108         | 90.1          | 0.104         | 91.2          | 0.100         | 92.1          |
| FILT3R (ours) | **0.093**     | **93.8**      | **0.090**     | **94.1**      | **0.089**     | **94.4**      |

### Short-horizon Depth (controlled streaming comparison)

원논문 Table 4. 동일 backbone 가중치, update rule만 상이.

| Align  | Method        | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ | Bonn AbsRel ↓ | Bonn δ<1.25 ↑ | KITTI AbsRel ↓ | KITTI δ<1.25 ↑ |
| ------ | ------------- | --------------- | --------------- | ------------- | ------------- | -------------- | -------------- |
| Scale  | CUT3R         | 0.421           | 47.9            | 0.078         | 93.7          | 0.118          | 88.1           |
| Scale  | TTT3R         | 0.405           | 48.9            | 0.069         | 95.4          | 0.114          | 90.4           |
| Scale  | FILT3R (ours) | 0.407           | **54.5**        | **0.061**     | **97.0**      | **0.110**      | **91.0**       |
| Metric | CUT3R         | 1.029           | 23.8            | 0.103         | 88.5          | 0.122          | 85.5           |
| Metric | TTT3R         | 0.977           | 24.5            | 0.090         | 94.2          | **0.110**      | **89.1**       |
| Metric | FILT3R (ours) | **0.772**       | **27.3**        | **0.067**     | **96.7**      | 0.115          | 88.8           |

Note: under metric-scale KITTI, TTT3R remains ahead of FILT3R (AbsRel 0.110 vs 0.115, δ<1.25 89.1 vs 88.8).

### Efficiency (500 frames, NRGBD 512×384)

원논문 Table 5. FILT3R avoids attention-map caching, matching CUT3R's footprint; TTT3R nearly doubles memory.

| Method            | Attn | FPS ↑     | Mem (MB) ↓ |
| ----------------- | ---- | --------- | ---------- |
| CUT3R             | –    | 25.27±.05 | 3503       |
| TTT3R             | ✓    | 24.69±.05 | 6294       |
| FILT3R (adpt. rₜ) | ✓    | 24.83±.04 | 6294       |
| FILT3R (ours)     | –    | 25.14±.04 | 3503       |

## 💡 Insights & Impact

- **Confidence accumulation extends memory**: In stable regimes the propagated variance contracts, shrinking the gain at rate O(1/t) so the filter averages over an ever-longer history; at scene transitions the process noise spikes and the gain reopens.
- **Fixed measurement noise is a stabilizing anchor**: Making both process and measurement noise adaptive causes co-excitation during transitions (drift ↑ and attention novelty simultaneously), overshooting the gain; the ablation's adaptive-rₜ variant worsens ATEorig (0.107 → 0.148) and adds memory.
- **Uncertainty propagation, not gain form, is key**: Removing variance propagation (reset-P) inflates ATEorig from 0.107 to 0.489; a tuned fixed-β EMA can lower ATE but sharply degrades rotation error (RPE-r 0.362 → 0.658).
- **Constant memory**: FILT3R keeps CUT3R's constant footprint while full-attention methods (VGGT, DA3) and Point3R grow with length (Point3R OOM beyond ~600 frames on 32 GB).

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The CUT3R-style recurrent backbone whose state update FILT3R replaces (uniform overwrite baseline).
- **[TTT3R](ttt3r.md)**: Heuristic confidence-scaling gate; primary adaptive baseline.
- **[Point3R](point3r.md)**: Explicit spatial-memory streaming baseline (OOM at length 1000).
- **[VGGT](vggt.md)** and **[Depth Anything 3](depth-anything-3.md)**: Full-attention references whose memory grows with sequence length.
- **[Spann3R](spann3r.md)**, **[StreamVGGT](streamvggt.md)**, **[WinT3R](wint3r.md)**: Streaming variants cited for long-horizon bounded-memory inference.

## 📚 Key Takeaways

1. FILT3R turns recurrent state updates into adaptive Kalman filtering in token space, deriving a per-token gain from propagated uncertainty rather than a hand-tuned forgetting rate.
2. Adaptive process noise (from EMA-normalized drift) with a single fixed measurement-noise scalar unifies and outperforms overwrite and heuristic-gate rules under identical frozen weights.
3. Across long-horizon 7-Scenes/NRGBD reconstruction, TUM pose, and Bonn depth, FILT3R reduces drift and forgetting while keeping CUT3R's constant memory; it trails TTT3R only on metric-scale KITTI depth.

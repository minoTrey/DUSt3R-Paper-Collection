# TTSA3R: Training-Free Temporal-Spatial Adaptive Persistent State for Streaming 3D Reconstruction (arXiv preprint 2026-01)

## 📋 Overview

- **Authors**: Zhijie Zheng, Xinhao Xiang, Jiawei Zhang
- **Institution**: University of California, Davis
- **Venue**: arXiv preprint (2026-01)
- **Links**: [Paper](https://arxiv.org/abs/2601.22615) | [Code](https://github.com/anonus2357/ttsa3r)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free framework that mitigates catastrophic forgetting in recurrent streaming 3D reconstruction (e.g. CUT3R) by combining a Temporal Adaptive Update Module and a Spatial Context Update Module to control per-token state updates.

## 🎯 Key Contributions

1. **Training-free adaptive framework**: TTSA3R alleviates the catastrophic forgetting of recurrent streaming models over long sequences without any retraining, working on top of a base recurrent architecture (CUT3R).
2. **Temporal Adaptive Update Module (TAUM)**: Analyzes state evolution patterns across frames to regulate update magnitude, preserving stable geometry while refining outdated regions.
3. **Spatial Context Update Module (SCUM)**: Localizes update-worthy spatial regions through observation-state alignment (attention) and scene dynamics (feature dissimilarity), preventing erroneous updates where prior observations lack spatial support.
4. **Complementary fusion**: The two signals are fused for fine-grained state-update control, giving the largest gains on extended sequences while remaining real-time.

## 🔧 Technical Details

### Base recurrent formulation

The decoder takes current-frame image features `Ft` and the previous global state `St−1 ∈ R^{N×C}` (N state tokens) and outputs new state tokens `S̃t` and multi-layer features `Dt`; a head produces geometric outputs `Xt, Tt, conft`. The persistent state is updated through masked integration.

### Temporal signal (TAUM)

TAUM tracks how each state token evolves across frames to distinguish converged/stable geometry from regions undergoing active refinement, and regulates the update magnitude accordingly.

### Spatial signal (SCUM)

Feature divergence is measured as `Dt = 1 − CosSim(Ft, Ft−1)` (Eq. 7). Decoder cross-attention maps between state-token queries and image-token keys/values are aggregated across `L` layers into `At` (Eq. 8). The spatial mask is `Mspat = σ(max_spat(At ⊙ Dt))` (Eq. 9): the element-wise product ensures high activation only where both attention and divergence are substantial.

All experiments run on a single NVIDIA A6000 GPU.

## 📊 Results

### Video depth estimation on short sequences (per-sequence scale)

원논문 Table 1. Abs Rel lower is better; δ<1.25 higher is better. "Optim/Stream/FA" = optimization / streaming / full-attention.

| Method     | Type   | Sintel Abs Rel↓ | Sintel δ<1.25↑ | Bonn Abs Rel↓ | Bonn δ<1.25↑ | KITTI Abs Rel↓ | KITTI δ<1.25↑ |
| ---------- | ------ | --------------- | -------------- | ------------- | ------------ | -------------- | ------------- |
| DUSt3R-GA  | Optim  | 0.656           | 45.2           | 0.155         | 83.3         | 0.144          | 81.3          |
| MonST3R-GA | Optim  | 0.378           | 55.8           | 0.067         | 96.3         | 0.168          | 74.4          |
| VGGT       | FA     | 0.287           | 66.1           | 0.055         | 97.1         | 0.070          | 96.5          |
| Spann3R    | Stream | 0.622           | 42.6           | 0.144         | 81.3         | 0.198          | 73.7          |
| CUT3R      | Stream | 0.421           | 47.9           | 0.078         | 93.7         | 0.118          | 88.1          |
| TTT3R      | Stream | 0.405           | 48.9           | 0.069         | 95.4         | 0.114          | 90.4          |
| StreamVGGT | Stream | 0.323           | 65.7           | 0.059         | 97.2         | 0.173          | 72.1          |
| **Ours**   | Stream | 0.401           | 50.0           | 0.064         | 96.5         | 0.110          | 91.2          |

TTSA3R is best among streaming methods on KITTI while competitive on Sintel and Bonn; the full-attention VGGT/StreamVGGT remain ahead on Sintel/Bonn δ.

### Camera pose estimation on short sequences

원논문 Table 2. All metrics lower is better, after Sim(3) alignment.

| Method    | Type   | Sintel ATE↓ | Sintel RPEt↓ | Sintel RPEr↓ | TUM ATE↓ | TUM RPEt↓ | TUM RPEr↓ | ScanNet ATE↓ | ScanNet RPEr↓ |
| --------- | ------ | ----------- | ------------ | ------------ | -------- | --------- | --------- | ------------ | ------------- |
| DUSt3R-GA | Optim  | 0.417       | 0.250        | 5.796        | 0.083    | 0.017     | 3.567     | 0.081        | 0.784         |
| MASt3R-GA | Optim  | 0.185       | 0.060        | 1.496        | 0.038    | 0.012     | 0.448     | 0.078        | 0.475         |
| Easi3R    | FA     | 0.110       | 0.042        | 0.758        | 0.105    | 0.022     | 1.064     | 0.061        | 0.525         |
| VGGT      | FA     | 0.172       | 0.062        | 0.471        | 0.012    | 0.010     | 0.310     | 0.035        | 0.377         |
| CUT3R     | Stream | 0.213       | 0.066        | 0.621        | 0.046    | 0.015     | 0.473     | 0.099        | 0.600         |
| TTT3R     | Stream | 0.210       | 0.090        | 0.722        | 0.028    | 0.013     | 0.380     | 0.064        | 0.637         |
| **Ours**  | Stream | 0.210       | 0.085        | 0.765        | 0.026    | 0.012     | 0.372     | 0.057        | 0.588         |

TTSA3R has the lowest ATE among streaming methods on TUM-dynamics (0.026) and ScanNet (0.057); the joint full-attention VGGT stays best overall on several pose columns.

### Ablation of components

원논문 Table 3, on Bonn (video depth) and TUM-dynamics (pose), with CUT3R as baseline.

| Configuration   | Bonn Abs Rel↓ | Bonn δ<1.25↑ | TUM ATE↓ | TUM RPE rot↓ |
| --------------- | ------------- | ------------ | -------- | ------------ |
| Baseline        | 0.078         | 93.7         | 0.046    | 0.473        |
| + TAUM          | 0.066         | 95.9         | 0.028    | 0.375        |
| + SCUM          | 0.074         | 94.1         | 0.040    | 0.415        |
| **Ours (both)** | 0.064         | 96.5         | 0.026    | 0.372        |

### Long-sequence robustness

On NRGBD (long sequences), as sequences extend from 50 to 250 frames, TTSA3R exhibits only a 1.33× error increase, compared with over 4× degradation for the baseline CUT3R (원논문 본문 및 Figure 6, 곡선 수치 미인쇄).

## 💡 Insights & Impact

- **Selective vs uniform updates**: Existing recurrent streaming methods apply identical update weights to all state tokens; TTSA3R shows that decoupling temporal (state evolution) and spatial (observation quality) signals yields fine-grained control that resists long-term drift.
- **Training-free upgrade path**: Because it needs no retraining, TTSA3R can be attached to an existing recurrent backbone, but its ceiling is bounded by the base architecture's representational capacity.
- **Limitations**: Performance degrades under severe occlusions where correspondence signals become unreliable (원논문 Limitations).

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The recurrent persistent-state backbone TTSA3R builds on and improves.
- **[VGGT](vggt.md)** and **[StreamVGGT](streamvggt.md)**: Full-attention / streaming baselines that set the upper bound on short sequences.
- **[Spann3R](spann3r.md)**: Spatial-memory streaming baseline compared against.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**, **[MonST3R](../dynamic/monst3r.md)**: Optimization-based (global-alignment) baselines.

## 📚 Key Takeaways

1. Catastrophic forgetting in recurrent streaming reconstruction stems from indiscriminate state updates; TTSA3R fixes this training-free by fusing temporal and spatial adaptive signals.
2. The largest gains appear on extended sequences (1.33× vs >4× error growth for CUT3R), while short-sequence accuracy stays competitive with state-of-the-art streaming methods.
3. Ablations confirm TAUM chiefly helps pose/trajectory consistency and SCUM helps spatial update targeting, with both together best.

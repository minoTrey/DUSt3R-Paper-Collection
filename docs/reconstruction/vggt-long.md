# VGGT-Long: Chunk it, Loop it, Align it, Pushing VGGT's Limits on Kilometer-scale Long RGB Sequences (ICRA 2026)

## 📋 Overview

- **Authors**: Kai Deng, Zexin Ti, Jiawei Xu, Jian Yang, Jin Xie
- **Institution**: Nankai University, Nanjing University
- **Venue**: ICRA 2026
- **Links**: [Paper](https://arxiv.org/abs/2507.16443) | [Code](https://github.com/DengKaiCQ/VGGT-Long)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A training-free system that extends VGGT to kilometer-scale monocular RGB streams by splitting them into overlapping chunks, aligning them with confidence-weighted Sim(3) estimation, and closing loops with a lightweight global optimization — no calibration, no depth supervision, no retraining.

## 🎯 Key Contributions

1. **Kilometer-scale monocular reconstruction from a foundation model**: The first system that successfully extends VGGT-family reconstruction to kilometer-scale unbounded outdoor sequences, without camera calibration or depth supervision.
2. **Chunk-and-align paradigm**: A simple pipeline that sidesteps the memory limitation of foundation models on long video, while keeping accuracy comparable to traditional SLAM methods.
3. **Sim(3) drift correction**: A loop-closure formulation that addresses the accumulated Sim(3) drift inherent to processing long sequences with a local model.
4. **Minimalist philosophy**: Demonstrates VGGT can serve as a robust front-end for a large-scale reconstruction system without a heavy SLAM back-end (no bundle adjustment, no pose graph over frames).
5. **Disk-backed memory management**: A streaming strategy that offloads intermediate chunk results to disk so that CPU RAM never has to hold the full reconstruction.

## 🔧 Technical Details

### Pipeline Stages

The system runs in four stages: chunking, chunk-wise alignment, loop closure, and global optimization.

### 1. Chunking

The input RGB stream is partitioned into `K` overlapping chunks with chunk size `L` and overlap size `O`; the k-th chunk spans frames `(k−1)(L−O)` to `(k−1)(L−O)+L`. Each chunk is processed independently by an unmodified VGGT.

### 2. Confidence-Aware Chunk Alignment

For each adjacent pair `(C_k, C_{k+1})`, the relative Sim(3) transform `S_{k,k+1}` is estimated from the overlapping frames using **Iteratively Reweighted Least Squares (IRLS)**, minimizing a weighted sum of squared residuals over corresponding 3D points. Each iteration solves a weighted Umeyama-style problem in closed form.

VGGT's own confidence output is used to downweight unreliable regions:

- Points below `0.75×` the mean confidence of the chunk are filtered out.
- Remaining low-confidence points get reduced IRLS weights.
- This suppresses moving vehicles and sky regions, which otherwise corrupt alignment in driving scenes.

### 3. Loop Detection and Loop-Centric Chunks

- A **Visual Place Recognition (VPR)** model produces a global descriptor `d_i` per frame.
- Nearest-neighbor search over descriptors flags a pair `(I_i, I_j)` as a loop candidate when cosine similarity exceeds a threshold `τ_s` **and** `|i − j| > Δt_min`.
- **Non-Maximum Suppression** keeps only the strongest match in each local time window.
- For each validated loop pair, frames around `i` and `j` are concatenated into a temporary batch and run through VGGT again, producing a **loop-centric chunk**. Because this batch contains temporally disjoint views of the same place, VGGT sees a much wider baseline than the sliding window ever provides.
- The loop constraint `S_ij` is obtained by chaining the alignments from the two original chunks into the loop-centric chunk.

### 4. Global Sim(3) Optimization

All chunk transforms are optimized jointly against two constraint types — sequential (adjacent) and loop (non-adjacent):

```text
{S*_k} = arg min  Σ_k ‖ log_Sim(3)(S⁻¹_{k,k+1} S⁻¹_k S_{k+1}) ‖²
                + Σ_{(i,j)∈L} ‖ log_Sim(3)(S⁻¹_ij S⁻¹_i S_j) ‖²
```

`log_Sim(3)(·)` maps to the 7-dimensional `sim(3)` tangent space so the problem is unconstrained, and is solved by **Levenberg–Marquardt**. Crucially the optimization is _chunk-wise_, not frame-wise — even KITTI sequences yield only dozens of Sim(3) variables, so convergence takes a few iterations at millisecond cost.

### System Notes

- Images are resized to 518-pixel width, preserving aspect ratio, following VGGT's convention.
- The VPR model runs over all images first and is then unloaded, freeing memory for VGGT.
- Intermediate chunk results are written to disk and selectively reloaded, converting RAM pressure into disk storage.
- Hardware: NVIDIA RTX 4090 (24 GiB) for most experiments; NVIDIA L20 (48 GiB) for chunk size ≥ 90.

## 📊 Results

### Camera Tracking on KITTI Odometry

원논문 Table 1. ATE RMSE [m] ↓. `Avg.*` is the mean excluding Seq 01 (a high-speed sequence with an atypical motion pattern). `OOM` = CUDA out-of-memory on a single RTX 4090; `TL` = tracking lost. LC = loop closure.

| Method                      | LC  | Calibration | Avg.       | Avg.\*     | 00    | 02     | 05     | 08     |
| --------------------------- | --- | ----------- | ---------- | ---------- | ----- | ------ | ------ | ------ |
| ORB-SLAM2 (w/ LC)           | ✓   | Required    | 54.816     | **9.464**  | 6.03  | 14.76  | 4.04   | 38.85  |
| LDSO                        | ✓   | Required    | **22.425** | 23.500     | 9.32  | 31.98  | 5.10   | 129.02 |
| DROID-SLAM                  | —   | Required    | 100.278    | 75.846     | 92.10 | 107.61 | 118.50 | 161.60 |
| DPV-SLAM++                  | ✓   | Required    | 25.749     | 27.138     | 8.30  | 39.64  | 5.74   | 110.90 |
| MASt3R-SLAM                 | ✓   | No Need     | /          | /          | TL    | TL     | TL     | TL     |
| CUT3R                       | ✗   | No Need     | /          | /          | OOM   | OOM    | OOM    | OOM    |
| Fast3R                      | ✗   | No Need     | /          | /          | OOM   | OOM    | OOM    | OOM    |
| VGGT                        | ✗   | No Need     | /          | /          | OOM   | OOM    | OOM    | OOM    |
| **VGGT-Long (Chunk = 30)**  | ✓   | No Need     | 44.713     | 39.564     | 9.06  | 99.95  | 10.20  | 139.79 |
| **VGGT-Long (Chunk = 60)**  | ✓   | No Need     | 26.358     | **19.298** | 8.06  | 34.16  | 9.15   | 63.15  |
| **VGGT-Long (Chunk = 90)**  | ✓   | No Need     | **22.718** | 20.938     | 11.97 | 49.85  | 9.88   | 66.27  |
| **VGGT-Long (Chunk = 120)** | ✓   | No Need     | 25.597     | 22.814     | 16.13 | 51.98  | 12.69  | 70.29  |

Only 4 of the 11 sequence columns are shown here for width; see the original Table 1 for the full breakdown. Sequence 00 is 3724.19 m over 4542 frames; Seq 02 is 5067.23 m over 4661 frames.

The headline observation is not that VGGT-Long wins every column — ORB-SLAM2 with calibration is better on `Avg.*` — but that **every calibration-free foundation-model baseline either runs out of memory or loses tracking**, while VGGT-Long completes all 11 sequences.

### Camera Tracking on Waymo Open Dataset

원논문 Table 2. ATE RMSE [m] ↓, ten ~200-frame segments.

| Method        | Calib.   | Avg.      | 163453191 | 183829460 | 315615587 | 346181117 | 371159869 | 520018670 |
| ------------- | -------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| DROID-SLAM    | Required | 4.396     | 3.705     | **0.301** | **0.447** | 8.653     | 9.320     | TL        |
| MASt3R-SLAM   | No Need  | 5.560     | 4.500     | 0.556     | 1.833     | 12.544    | 8.601     | 7.910     |
| CUT3R         | No Need  | 9.872     | 8.781     | 3.810     | 5.790     | 24.015    | 13.070    | 8.597     |
| Fast3R        | No Need  | /         | OOM       | OOM       | OOM       | OOM       | OOM       | OOM       |
| VGGT          | No Need  | /         | OOM       | OOM       | OOM       | OOM       | OOM       | OOM       |
| **VGGT-Long** | No Need  | **1.996** | **1.753** | 2.629     | 0.559     | **3.452** | **3.343** | **2.547** |

### Point Map Estimation on Waymo

원논문 Table 3. Ground truth is LiDAR. The authors explicitly caution that these numbers should be taken **as reference only**: the vehicle-mounted LiDAR scans below eye level, so its coverage is narrower than the RGB cameras', and structures such as the overpass in segment 371159869 are absent from the GT while the visual methods do reconstruct them.

| Method        | Calib.   | Accuracy ↓ (Avg.) | Completeness ↓ (Avg.) | Chamfer ↓ (Avg.) |
| ------------- | -------- | ----------------- | --------------------- | ---------------- |
| DROID-SLAM    | Required | 1.201             | 8.540                 | 4.870            |
| MASt3R-SLAM   | No Need  | 3.772             | 3.177                 | 3.474            |
| CUT3R         | No Need  | 3.884             | 6.801                 | 5.343            |
| **VGGT-Long** | No Need  | **1.182**         | **2.860**             | **2.021**        |

### Robustness on Virtual KITTI

원논문 Table 4. ATE RMSE [m] ↓, across Clone / Fog / Morning / Overcast / Rain / Sunset conditions.

| Method        | Calib.   | 01 Avg.    | 02 Avg.    | 06 Avg.    | 18 Avg.    | 20 Avg.    | All Avg.   |
| ------------- | -------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| DROID-SLAM    | Required | 1.1366     | **0.0640** | **0.0377** | 2.2046     | **4.1572** | **1.5200** |
| MASt3R-SLAM   | No Need  | /          | /          | /          | /          | /          | /          |
| CUT3R         | No Need  | 48.3618    | 20.1191    | 0.7724     | 17.1494    | 103.6918   | 38.0189    |
| Fast3R        | No Need  | /          | /          | /          | /          | /          | /          |
| VGGT          | No Need  | /          | /          | /          | /          | /          | /          |
| **VGGT-Long** | No Need  | **1.0490** | 0.7026     | 0.4377     | **1.3966** | 6.6830     | 2.0538     |

Reported honestly: calibrated DROID-SLAM has the better all-scene average (1.5200 vs 2.0538), and MASt3R-SLAM loses tracking on every Virtual KITTI condition. VGGT-Long's advantage is that it is stable across fog, rain, and sunset with no retraining or domain adaptation.

### Runtime

원논문 Table 5, chunk size = 75. All components run in almost real time. Disk I/O is excluded (≈25 ms to load and ≈95 ms to write per chunk on the authors' machine).

| Seq. | Frames | VPR Time / Frame | Chunk Process / Chunk | Chunk Align / Iter | LM Opt. (C++) / Iter | LM Opt. (Python) / Iter |
| ---- | ------ | ---------------- | --------------------- | ------------------ | -------------------- | ----------------------- |
| 00   | 4542   | 21.264 ms        | 2.811 s               | 0.284 s            | 1.249 ms             | 13.394 ms               |
| 05   | 2761   | 17.023 ms        | 2.614 s               | 0.273 s            | 0.862 ms             | 8.446 ms                |
| 06   | 1101   | 18.523 ms        | 2.728 s               | 0.278 s            | 0.436 ms             | 3.592 ms                |

The text summarizes chunk-wise processing at about 2.6–2.8 s per chunk and Sim(3) alignment at about 0.2 s, with the LM solver converging within 3 iterations on average at 0.4–1.3 ms/iter in C++ or 3.5–13 ms/iter in Python.

### Ablation

원논문 Table 6. ATE RMSE [m] ↓ on KITTI Seq 00 and 05. `LC` = loop closure, `IRLS` = iteratively reweighted least squares in chunk alignment, `Weight` = confidence-based weighting.

| LC  | IRLS | Weight | 00       | 05       |
| --- | ---- | ------ | -------- | -------- |
| ✗   | ✓    | ✓      | 58.69    | 36.01    |
| ✓   | ✗    | ✓      | 12.29    | 10.98    |
| ✓   | ✓    | ✗      | 11.28    | 10.13    |
| ✓   | ✓    | ✓      | **8.67** | **8.31** |

Disabling loop closure is by far the most damaging change, raising Seq 00 ATE to 58.69 m.

## 💡 Insights & Impact

### The Failure Mode Being Fixed

The paper's Figure 1 frames the problem sharply: on kilometer-scale outdoor sequences, prior work fails in one of two ways — **severe drift** (CUT3R, Fast3R) or **inability to finish the sequence at all** (MASt3R-SLAM tracking loss, VGGT out-of-memory). VGGT-Long targets the second failure directly and inherits a fix for the first from loop closure.

### Why the Minimalist Design Works

The authors explicitly diverge from the MASt3R-SLAM line of thought, which adds pose graph optimization and bundle adjustment as a SLAM back-end. Their argument is that the bottleneck of a strong foundation model is not its representational power but its **memory footprint**, which grows quadratically with input size. Once memory is handled by chunking, the only remaining error is Sim(3) drift between chunks — a low-dimensional problem with dozens of variables, not thousands. That is why a millisecond-scale LM solve suffices where a full SLAM back-end was assumed necessary.

### Diagnoses of Baseline Failures

- **MASt3R-SLAM**: On long straight roads with low scene variation, no new keyframes are generated for extended periods; when one finally is, the baseline is so wide that MASt3R feature matching fails, producing tracking loss.
- **CUT3R**: Its continuous state token is a compact global representation, analogous to NeRF, and struggles to hold the geometric detail of expansive outdoor scenes.

### Confidence as a Dynamic-Object Filter

An unexpected benefit: confidence-aware weighting suppresses fast-moving vehicles during alignment. The paper notes (Figure 4) that dense vehicle traffic is _not_ effectively filtered by the LiDAR ground truth, yet VGGT-Long handles it — a case where the visual method's failure mode is milder than the reference sensor's.

## 🔗 Related Work

- [VGGT](vggt.md) — the frozen backbone; VGGT-Long adds no training and modifies no weights
- [MASt3R](../foundation/mast3r.md) and [MASt3R-SLAM](mast3r-slam.md) — the SLAM-back-end alternative that VGGT-Long argues against
- [CUT3R](../dynamic/cut3r.md) — the recurrent-state baseline that drifts on long outdoor sequences
- [Fast3R](fast3r.md) — a multi-view feed-forward baseline that OOMs on all tested KITTI sequences
- [DUSt3R](../foundation/dust3r.md) — the origin of the pointmap formulation being chunked here
- [StreamVGGT](streamvggt.md), [Stream3R](stream3r.md), [Point3R](point3r.md) — alternative approaches to long streams via causal/streaming architectures rather than chunking
- [FastVGGT](fastvggt.md), [TTT3R](ttt3r.md) — other training-free modifications of the VGGT family
- [VGGT-SLAM](vggt-slam.md) — a submap-based SLAM system on the same backbone

## 📚 Key Takeaways

1. **Memory, not accuracy, was VGGT's limit on long sequences.** All three feed-forward baselines tested (VGGT, Fast3R, CUT3R) fail on KITTI with out-of-memory rather than with poor numbers.
2. **Chunk-level Sim(3) is a cheap global variable set.** Optimizing dozens of chunk transforms instead of thousands of frame poses turns global consistency into a millisecond problem.
3. **Loop closure carries the ablation.** Removing it raises KITTI Seq 00 ATE from 8.67 m to 58.69 m — a larger effect than IRLS and confidence weighting combined.
4. **Calibration-free is the real selling point.** Classic methods like ORB-SLAM2 still edge out VGGT-Long on some KITTI averages, but they require intrinsics; VGGT-Long does not, and still completes every sequence.
5. **Confidence outputs are reusable as robustness signals.** VGGT's per-point confidence, trained for reconstruction, doubles as a dynamic-object and sky mask during alignment.

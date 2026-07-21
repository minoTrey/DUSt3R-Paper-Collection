# Glob3R: Global Structure-from-Motion with 3D Foundation Models (arXiv preprint (2026-07))

## 📋 Overview

- **Authors**: Junyuan Deng, Heng Li, Kejie Qiu, Lingteng Qiu, Rui Peng, Weichao Shen, Weihao Yuan, Siyu Zhu, Zilong Dong, Ping Tan
- **Institution**: The Hong Kong University of Science and Technology; Tongyi Lab, Alibaba Group; Nanjing University; Fudan University
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.09225) | [Project Page](https://junyuandeng.github.io/Glob3r/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A global SfM-style pipeline built on a frozen Pi3X backbone augmented with a lightweight dense matching head; dense warps become sparse multi-view tracks that feed keyframe-based sliding-window association, motion averaging, and bundle adjustment for scalable, accurate reconstruction.

## 🎯 Key Contributions

1. **Foundation-model-guided global SfM**: Turns frozen feed-forward 3D predictions (poses, point maps, confidence) into optimizable geometric constraints, combining learned priors with classical global-SfM refinement.
2. **Dense warping matching head**: A lightweight head on Pi3X predicts coarse-to-fine image warps + confidence between keyframes and other views, converted into sparse but reliable multi-view feature tracks.
3. **Keyframe-based sliding-window association**: Overlapping (half-window) windows propagate tracks and relative poses across the full sequence and support both ordered sequences and retrieval-based pseudo-sequences for unordered sets.
4. **Frame-level global optimization**: Rotation averaging → translation averaging (via multi-view ray consistency) → bundle adjustment, refining every frame rather than stitching chunk boundaries.

## 🔧 Technical Details

### Architecture

Built on the permutation-equivariant Pi3X (π³) backbone, frozen along with its existing heads; only the matching head is fine-tuned. A transformer decoder + DPT predict coarse warps W_{a→B} and confidence p_{a→B} at stride 4 from a reference image to all targets, refined with residual warps/confidence at strides {4, 2, 1}. Training supervises the first-frame reference matches with GT 2D–2D warps (from projected GT point maps) using NLL + warping + confidence losses.

### Sliding-Window Association

Windows of N frames shift by N/2. Keyframes are selected by reprojecting each frame's point map onto existing keyframes and counting valid pixels n_t; a frame becomes a keyframe if n_t < τ_proj, with at least one keyframe in the overlap half. Sampled high-confidence pixels build tracks; local tracks merge into a pose graph (frames = nodes, edge weight = #valid tracks), and a maximum spanning tree initializes poses.

### Optimization

Robust rotation averaging fixes global rotations; camera centers and 3D points are recovered by enforcing points to lie on world-frame viewing rays (robust to inconsistent local scales). Bundle adjustment then refines poses, points, and (if uncalibrated) intrinsics/distortion by minimizing confidence-weighted reprojection error. Dense depth is rescaled to optimized sparse depths via RANSAC and fused into a global point cloud.

### Default settings

Sliding window N = 20, stride 10; N = 120 for T&T Auditorium/Courtroom, N = 200 for KITTI seq 02.

## 📊 Results

Evaluated on 19 Tanks & Temples (T&T) scenes, 9 TUM RGB-D sequences, 11 KITTI sequences, and 13 ETH3D scenes. T&T pose quality is measured indirectly via NeRF (Nerfacto) PSNR; TUM/KITTI report trajectory RMSE; ETH3D reports relative rotation/translation accuracy (RRA/RTA @ threshold).

### Tanks & Temples — NeRF PSNR↑ (pose quality)

원논문 Table 1 (일부 씬 + 평균 발췌; 씬 약칭: Chur.=Church, Court.=Courthouse, C.room=Courtroom, Play.=Playground).

| Method      | Barn      | Chur.     | Court.    | C.room    | Family | Museum    | Play.     | Temple    | Avg.      |
| ----------- | --------- | --------- | --------- | --------- | ------ | --------- | --------- | --------- | --------- |
| COLMAP      | 24.09     | **18.14** | 18.04     | 18.25     | 19.40  | 16.87     | 19.07     | 18.10     | 18.73     |
| GLOMAP      | 24.26     | 18.20     | **21.08** | 18.20     | 13.08  | 11.81     | 15.72     | 18.23     | 17.43     |
| AMB3R       | 20.08     | 15.98     | 15.64     | 15.58     | 19.50  | 15.97     | 18.04     | 15.74     | 16.97     |
| Scal3R      | 20.00     | 15.08     | 18.20     | 13.28     | 17.21  | 13.01     | 16.79     | 17.09     | 15.58     |
| DA3         | 21.78     | 16.51     | OOM       | 16.34     | 18.93  | 15.60     | 19.01     | 17.21     | 17.78     |
| Pi3X        | 21.22     | 17.01     | 16.74     | 17.23     | 18.89  | 15.56     | 18.20     | 16.83     | 17.62     |
| SAIL-Recon  | 23.50     | 17.00     | 15.09     | 17.40     | 20.60  | 15.40     | 20.30     | 17.80     | 18.55     |
| LingBot-Map | 18.54     | 15.44     | 14.43     | 15.65     | 17.60  | 14.62     | 17.18     | 15.28     | 16.11     |
| **Ours**    | **24.50** | 18.01     | 20.72     | **18.31** | 20.27  | **17.43** | **21.68** | **18.82** | **19.56** |

Glob3R has the best average PSNR, but not every scene: GLOMAP leads on Courthouse (21.08 vs. 20.72) and ties/edges on Church (18.20 vs. 18.01), and COLMAP is best on Church (18.14).

### TUM RGB-D — Trajectory RMSE (cm) ↓

원논문 Table 2.

| Method      | 360  | desk    | desk2   | floor   | plant   | room    | rpy     | teddy | xyz     | Avg.    |
| ----------- | ---- | ------- | ------- | ------- | ------- | ------- | ------- | ----- | ------- | ------- |
| DROID-SLAM  | 20.2 | 3.2     | 9.1     | 6.4     | 4.5     | 91.8    | 5.6     | 4.5   | 1.2     | 15.8    |
| MASt3R-SLAM | 7.0  | 3.5     | 5.5     | 5.6     | 3.5     | 11.8    | 4.1     | 11.4  | 2.0     | 6.0     |
| VGGT-SLAM   | 7.1  | 2.5     | 4.0     | 14.1    | 2.3     | 10.2    | 3.0     | 3.4   | 1.4     | 5.3     |
| AMB3R       | 4.6  | 1.9     | 2.8     | 3.2     | 2.9     | 5.8     | 2.3     | 3.7   | 1.1     | 3.2     |
| LingBot-Map | 6.3  | 2.8     | 4.4     | 5.9     | 4.4     | 9.2     | 2.4     | 3.6   | 1.1     | 4.4     |
| **Ours**    | 8.1  | **1.8** | **2.6** | **3.0** | **1.8** | **5.0** | **2.2** | 3.7   | **0.9** | **3.2** |

Glob3R ties AMB3R for the best average (3.2 cm) and wins most sequences, but AMB3R is better on 360 (4.6 vs. 8.1) and floor (3.2 vs. 3.0 — here Ours edges it), reflecting difficulty with frequent-rotation short trajectories.

### KITTI — Trajectory RMSE (m) ↓

원논문 Table 3 (일부 시퀀스 + 평균 발췌).

| Method      | 00       | 01        | 05       | 08        | 09       | Avg.      |
| ----------- | -------- | --------- | -------- | --------- | -------- | --------- |
| DROID-SLAM  | 92.10    | 344.60    | 118.50   | 161.60    | 72.32    | 100.28    |
| VGGT-Long   | 8.64     | 61.21     | 9.88     | 72.98     | 31.84    | 25.94     |
| LingBot-Map | 27.17    | 70.94     | 26.14    | 23.82     | 17.84    | 28.63     |
| LoGeR       | 30.47    | **47.91** | 26.34    | 24.41     | 10.12    | 18.65     |
| Scal3R      | 4.30     | 45.29     | 3.30     | 36.69     | 12.32    | 14.55     |
| **Ours**    | **2.77** | 53.12     | **2.80** | **32.76** | **5.51** | **13.21** |

Glob3R has the best average RMSE (13.21 m) and best on most listed sequences, but on the highway seq 01 it (53.12) trails LoGeR (47.91) and Scal3R (45.29).

### ETH3D — Relative Pose Accuracy (Average over 13 scenes)

원논문 Table 4 (Average 행). @5는 5° 임계, @1은 1° 임계. 높을수록 좋음.

| Method     | RRA@5↑    | RTA@5↑   |
| ---------- | --------- | -------- |
| COLMAP     | 49.0      | 47.8     |
| GLOMAP     | 58.40     | 47.70    |
| VGGSfM     | 65.4      | 58.9     |
| DF-SfM     | 74.2      | 70.7     |
| MASt3R-SfM | 81.2      | 79.7     |
| AMB3R      | 98.2      | 81.9     |
| **Ours**   | **100.0** | **91.3** |

At the strict 1° threshold, Glob3R also leads AMB3R by a wide margin: RRA@1 91.58 vs. 77.69 and RTA@1 73.27 vs. 35.55 (nearly doubling translation accuracy).

### Ablation on ETH3D

원논문 Table 5.

| Variant       | RRA@1↑    | RTA@1↑    | Speed (FPS)↑ |
| ------------- | --------- | --------- | ------------ |
| Init          | 69.70     | 33.64     | 3.34         |
| + Motion Avg. | 70.20     | 34.75     | 2.77         |
| Ours (full)   | **90.80** | **73.27** | 2.06         |
| Coarse Track. | 67.11     | 48.56     | 2.54         |
| VGGT-Track.   | 59.29     | 29.35     | 1.14         |
| RomaV2-Track. | 57.12     | 44.78     | 0.82         |

## 💡 Insights & Impact

- **Feed-forward alone is not enough**: Pi3X initialization already connects frames (RRA@1 69.70) but bundle adjustment lifts translation accuracy from 33.64 to 73.27 — explicit geometric optimization is essential for precision.
- **Dense-warp tracks beat point tracking**: Replacing the matching head with VGGT's point tracker or RoMaV2 two-view matching drops both accuracy and speed (RTA@1 73.27 → 29.35 / 44.78), since single-reference tracking needs repeated inference and misses shared multi-view context.
- **Bridging two paradigms pays off**: On T&T it improves ~2–3 dB PSNR over feed-forward baselines and ~1 dB over COLMAP; on KITTI it cuts trajectory RMSE 10–50% vs. recent streaming methods; on ETH3D it nearly doubles translation accuracy over AMB3R.
- **Honest limits**: A fixed window size and dependence on the backbone's initial geometry remain; per-sequence it can lose to strong baselines (e.g., KITTI seq 01, TUM 360).

## 🔗 Related Work

- **[Pi3](../reconstruction/pi3.md)**: The frozen permutation-equivariant backbone (Pi3X / π³) Glob3R builds on.
- **[VGGT](../reconstruction/vggt.md)**: Feed-forward foundation model and point-tracking baseline compared in the ablation.
- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: Foundational pointmap and dense-matching models underpinning this line.
- **[AMB3R](../reconstruction/amb3r.md)**: The strongest learning-based SfM baseline compared across all benchmarks.

## 📚 Key Takeaways

1. Glob3R converts frozen Pi3X feed-forward predictions into optimizable global-SfM constraints via a dense-warp matching head that yields reliable multi-view tracks.
2. A keyframe-based sliding-window association plus rotation/translation averaging and bundle adjustment refine every frame, scaling to long driving sequences and unordered collections.
3. It leads on T&T, KITTI, and ETH3D averages and ties AMB3R on TUM RGB-D, while honestly losing some individual sequences (KITTI seq 01, TUM 360) and per-scene comparisons.

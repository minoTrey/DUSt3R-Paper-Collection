# GRS-SLAM3R: Real-Time Dense SLAM with Gated Recurrent State (arXiv preprint 2025-09)

## 📋 Overview

- **Authors**: Guole Shen, Tianchen Deng, Yanbo Wang, Yongtao Chen, Yilin Shen, Jiuming Liu, Jingchuan Wang
- **Institution**: Institute of Medical Robotics, School of Automation and Intelligent Sensing, Shanghai Jiao Tong University
- **Venue**: arXiv preprint (2025-09)
- **Links**: [Paper](https://arxiv.org/abs/2509.23737)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An end-to-end incremental dense SLAM framework that adds a transformer-based gated recurrent latent state (reset + update gates) and hierarchical submap alignment on top of the DUSt3R-style pointmap paradigm, producing metric-scale point clouds in the global frame at ~15 FPS.

## 🎯 Key Contributions

1. **Gated recurrent latent state**: A persistent latent memory updated by two transformer-based gates — a reset gate and an update gate — that selectively integrate the current frame while discarding irrelevant/outdated memory, improving spatial correlation across long sequences.
2. **Multi-submap scene representation**: Keyframe-based submaps with per-submap state reset, plus hierarchical alignment (intra-submap local refinement + inter-submap registration via pose-graph optimization) to bound drift over long sequences.
3. **Global metric-scale output**: Unlike pairwise DUSt3R predictions in local frames, the method directly outputs point maps and 6-DoF poses in the world coordinate system, better suited to online SLAM.
4. **Real-time performance**: Runs at ~15 FPS on a single RTX 4090 while improving reconstruction and tracking over DUSt3R-based online baselines.

## 🔧 Technical Details

### Gated Recurrent Model

- Each input frame `It` is encoded to tokens `Ft` via a ViT encoder; a latent memory state `Mt` (a set of tokens) accumulates scene information across sequential observations (inspired by CUT3R).
- Reset gate `Rt = Gr(Mt−1, Ft)` and update gate `Ut = Gu(Mt−1, Ft)` are computed via self- and cross-attention. The reset gate is applied element-wise to memory (`Mtreset = Rt ⊙ Mt−1`), a transformer decoder fuses reset memory with frame features and a pose token, and the final state is updated via `Mt = Ut ⊙ M̂t + (1 − Ut) ⊙ Mt−1`.
- Two DPT heads decode local-frame and world-frame point clouds; an MLP head decodes 6-DoF pose. All outputs are metric-scale.

### Hierarchical Submap Alignment

- Frontend: a new keyframe is promoted when covisibility with the last keyframe drops below `τkf`; a new submap starts (state reset) when covisibility with the submap anchor drops below `τanchor`.
- Local submap alignment optimizes poses and pointmaps within each submap via a confidence-weighted local alignment loss.
- Inter-submap alignment builds an SE(3) pose graph over submaps; because submaps share a common metric scale, inter-submap constraints are rigid transforms, refined by Levenberg–Marquardt as loop closures are added.

### Training

- Confidence-weighted 3D regression loss + pose loss (following CUT3R).
- Three-stage curriculum (4-frame → decoder unfreeze → 64-frame fine-tuning); longer side resized to 512.
- Trained on 8× NVIDIA A100 (80 GB); inference/SLAM on a single RTX 4090.
- Training data spans 10 datasets including CO3Dv2, ARKitScenes, ScanNet, WildRGBD, BlendedMVS, Matterport3D.

## 📊 Results

### Reconstruction and Runtime on 7-Scenes

원논문 Table III. Accuracy / Completion in centimeters, plus FPS (higher FPS better; Acc./Comp. lower better).

| Method      | Acc. / Comp. (Avg.) | FPS  |
| ----------- | ------------------- | ---- |
| DUSt3R      | 2.19 / 3.24         | <1   |
| MASt3R      | 3.04 / 3.90         | <1   |
| Spann3R     | 3.42 / 2.41         | > 50 |
| CUT3R       | 2.67 / 3.27         | ~20  |
| SLAM3R      | 2.13 / 2.34         | ~25  |
| MASt3R-SLAM | 2.60 / 3.03         | ~15  |
| **Ours**    | **2.12 / 2.27**     | ~15  |

### Camera Tracking (ATE-RMSE) on 7-Scenes

원논문 Table I. Per-scene ATE RMSE in centimeters (lower better).

| Method      | Chess | Fire | Heads | Office | Pump. | RedKit. | Stairs | Avg.     |
| ----------- | ----- | ---- | ----- | ------ | ----- | ------- | ------ | -------- |
| CUT3R       | 5.90  | 5.34 | 6.37  | 13.85  | 14.73 | 9.44    | 6.67   | 8.90     |
| MASt3R-SLAM | 7.24  | 5.78 | 3.68  | 13.31  | 12.87 | 10.07   | 6.68   | 8.52     |
| **Ours**    | 5.30  | 5.31 | 4.09  | 13.43  | 14.41 | 8.95    | 6.81   | **8.27** |

Ours wins on average and on several scenes (e.g. Chess, RedKitchen) but loses to MASt3R-SLAM on Heads (4.09 vs 3.68) and to CUT3R on Fire (5.31 vs 5.34 is a win; Office CUT3R 13.85 vs Ours 13.43 win) — the paper does not lead on every scene.

### Large-Scale Apartment Reconstruction

원논문 Table IV. Apartment dataset (~100 m²). ATE not reported for SLAM3R as it produces no explicit poses.

| Method      | Acc. [cm] ↓ | Comp. [cm] ↓ | ATE [m] ↓ |
| ----------- | ----------- | ------------ | --------- |
| CUT3R       | 48.49       | 39.85        | 2.39      |
| SLAM3R      | 21.67       | 27.66        | –         |
| MASt3R-SLAM | 8.72        | 5.80         | 0.72      |
| **Ours**    | **6.79**    | **5.62**     | **0.16**  |

### Ablation: Gate, Local Align, Submap

원논문 Table V. Apartment dataset. Reconstruction Acc./Comp. (cm) and ATE (m).

| Gate | Local Align | Submap | Acc.  | Comp. | ATE  |
| ---- | ----------- | ------ | ----- | ----- | ---- |
| ✗    | ✗           | ✗      | 48.49 | 39.85 | 2.39 |
| ✗    | ✓           | ✓      | 8.87  | 6.30  | 0.33 |
| ✓    | ✓           | ✗      | 28.95 | 24.93 | 1.38 |
| ✓    | ✗           | ✓      | 7.32  | 6.18  | 0.23 |
| ✓    | ✓           | ✓      | 6.79  | 5.62  | 0.16 |

## 💡 Insights & Impact

- **Gated memory beats naive recurrence**: Directly updating a latent state each frame introduces drift and noise; the reset/update gating selectively suppresses unreliable memory content, which the ablation shows is the largest contributor to both reconstruction accuracy and tracking.
- **Submaps bound long-horizon drift**: Per-submap state reset plus hierarchical alignment prevents error accumulation from propagating through the recurrent state, key for large multi-room scenes where CUT3R fails and SLAM3R / MASt3R-SLAM drift.
- **Speed/accuracy balance**: At ~15 FPS on an RTX 4090 the method matches MASt3R-SLAM's throughput while lowering reconstruction error, making it practical for online dense mapping.

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: Provides the recurrent-state paradigm GRS-SLAM3R builds on; GRS-SLAM3R adds explicit gating and submaps to reduce drift.
- **[SLAM3R](../reconstruction/slam3r.md)** & **[MASt3R-SLAM](../reconstruction/mast3r-slam.md)**: The most directly compared DUSt3R-based SLAM systems.
- **[Spann3R](../reconstruction/spann3r.md)**: External spatial-memory incremental reconstruction baseline.
- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: The pointmap foundation the SLAM line derives from.

## 📚 Key Takeaways

1. Gated recurrent memory (reset + update gates) turns a per-frame latent state into a robust spatial memory for dense monocular SLAM.
2. Keyframe submaps with per-submap reset and hierarchical (intra + inter) alignment bound drift over long, large-scale sequences.
3. Outputs metric-scale point clouds and 6-DoF poses directly in the world frame at ~15 FPS on an RTX 4090, improving reconstruction and tracking over DUSt3R-based online baselines while not dominating every per-scene metric.

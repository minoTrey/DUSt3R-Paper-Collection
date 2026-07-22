# MAGiSt3R: Multi-Agent Feed-forward 3D Reconstruction from Monocular RGB Videos (arXiv preprint (2026-07))

![magist3r — architecture](https://arxiv.org/html/2607.15211v1/x1.png)

_Overview of MAGiSt3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Ziren Gong, Xiaohan Li, Fabio Tosi, Ninghui Xu, Stefano Mattoccia, Jianfei Cai, Matteo Poggi
- **Institution**: University of Bologna, Italy; Faculty of Dentistry, The University of Hong Kong, China; School of Instrument Science and Engineering, Southeast University, China; Monash University, Australia
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.15211) | [Project Page](https://zorangong.github.io/magist3r_page/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first multi-agent, feed-forward dense 3D reconstruction framework for monocular RGB videos. A VGGT backbone regresses local point maps per agent; a novel MAGMA module merges submaps at both intra-agent and inter-agent levels, and pose graph optimization mitigates drift — running at almost 10 FPS.

## 🎯 Key Contributions

1. **First multi-agent feed-forward framework**: Incrementally reconstructs 3D point maps from multiple RGB video streams in a unified coordinate system without known camera parameters — the paper states no multi-agent feed-forward 3D reconstruction system existed before.
2. **MAGMA (Multi-Agent Global Map Aggregation)**: A custom feed-forward merging module that fuses submaps at both intra-agent and inter-agent levels, producing global point maps and camera poses.
3. **Lifting existing 3R models to the multi-agent setting**: Several feed-forward reconstruction models (DUSt3R, MASt3R, SLAM3R, VGGT-SLAM) are adapted to multi-agent operation via RANSAC+ICP (RICP), providing comparable baselines that MAGiSt3R outperforms in both reconstruction and camera tracking.

## 🔧 Technical Details

### Pipeline (three stages)

1. **Intra-agent reconstruction**: Each agent processes its RGB sequence in submaps through a VGGT backbone, then merges submaps incrementally into a geometrically consistent map in its own coordinate system.
2. **Inter-agent alignment**: A loop-closure mechanism detects overlapping regions between agents; once a loop is found, MAGMA combines the agents' point maps into a global map.
3. **Backend pose graph optimization (PGO)**: Poses are optimized after merging (intra- and inter-agent) via the Levenberg–Marquardt algorithm to reduce cumulative drift.

### Intra-agent submap generation

- For every set of `m` consecutive RGB images a submap is created; the middle frame is labeled a keyframe.
- VGGT encodes images into camera tokens and predicts dense depth maps, confidence maps, and camera intrinsics/extrinsics. Point maps are obtained by inverse-projecting depth into the first camera's reference system, then filtered by confidence threshold τ_conf.
- Concurrently, a ViT encoder extracts visual tokens and DINOv2 SALAD produces spatial tokens and global descriptors, used for loop detection and submap merging.

### MAGMA model

- Processes a **reference set** (global map + keyframes) and a **registering set** (new submap). Top-N best-correlated views are retrieved via descriptor similarity.
- A geometric encoder `E_geo` (a 2D conv, kernel 16, stride 16, ViT-patch-like) turns point maps into geometry tokens spatially aligned with visual tokens.
- **Appearance tokens** derived from visual + spatial tokens through an attention module enhance geometry tokens to establish correspondences across coordinate systems and mitigate ambiguity from repetitive/textureless geometry.
- Two decoders (registering `D_reg`, reference `D_ref`), each with self-attention + multi-view cross-attention + MLP, produce registering and reference tokens. DPT heads regress refined/registered point maps and confidence; a pose head (four self-attention layers + linear) predicts refined and registered camera parameters, with an attention mask so `t_reg` attends only to `t_ref`.

### Training loss

End-to-end supervision with a confidence-aware registration loss `L_reg` (following DUSt3R), a camera loss `L_pose` on quaternion + translation + FoV, and a geometry-consistency term `L_geo` (reprojection between two random views). Total: `L = λ_reg·L_reg + λ_pose·L_pose + λ_geo·L_geo`.

### Implementation

- Trained MAGMA for 200 epochs, batch size 5, on 4 A100 GPUs, learning rate 1.5e−5.
- Hyperparameters: VGGT input images `m = 10`, stride `s = 5`, τ_conf = 0.25, τ_loop = 0.6, top-N = 10, β = 1, λ_reg = 1, λ_pose = 1, λ_geo = 0.8.
- Training data: ScanNet, ScanNet++, and Aria Synthetic Environment (multi-agent trajectories simulated by partitioning scenes, since no training set natively supports the setting).
- Evaluation: ReplicaMultiagent (synthetic, 2 agents) and AriaMultiagent (real-world, 3 agents). Reconstruction is scored by accuracy and completeness; tracking by Absolute Trajectory Error (ATE) RMSE.

## 📊 Results

### 3D Reconstruction on ReplicaMultiagent

원논문 Table 3. Accuracy / Completeness (거리 지표, 낮을수록 좋음), scene-averaged (Avg) values. ⨿ = RICP at the inter-agent level; single-agent rows have no inter-agent communication.

| Method       | A1 Acc. ↓ | A1 Comp. ↓ | A2 Acc. ↓ | A2 Comp. ↓ | Multi Acc. ↓ | Multi Comp. ↓ |
| ------------ | --------- | ---------- | --------- | ---------- | ------------ | ------------- |
| DUSt3R       | 11.38     | 9.44       | 8.97      | 6.95       | 12.51        | 9.92          |
| MASt3R       | 7.00      | 4.05       | 9.82      | 8.86       | 10.12        | 8.16          |
| SLAM3R       | 7.38      | 5.75       | 9.28      | 8.89       | 14.29        | 9.06          |
| MASt3R-SLAM  | 9.64      | 4.94       | 13.98     | 12.95      | 13.83        | 9.37          |
| VGGT-SLAM    | 9.04      | 5.38       | 8.29      | 6.81       | 11.36        | 8.44          |
| **MAGiSt3R** | **4.65**  | **2.98**   | **6.21**  | **5.26**   | **5.37**     | **3.36**      |

The paper notes single-agent MAGiSt3R wins "with few exceptions — completeness on Apart 2 and Office 0"; the Avg columns above still favor MAGiSt3R.

### Tracking on ReplicaMultiagent (single-agent)

원논문 Table 4. ATE RMSE ↓, scene-averaged per agent.

| Method       | Agent 1 Avg ↓ | Agent 2 Avg ↓ |
| ------------ | ------------- | ------------- |
| DUSt3R       | 10.99         | 8.35          |
| MASt3R       | 5.04          | 3.05          |
| SLAM3R       | 16.27         | 18.02         |
| MASt3R-SLAM  | 6.15          | 6.90          |
| VGGT-SLAM    | 6.68          | 5.01          |
| **MAGiSt3R** | **4.03**      | **2.91**      |

The paper reports "mixed results on individual scenes" (e.g., not always best per scene) but the best average with both agents.

### Tracking on ReplicaMultiagent (multi-agent)

원논문 Table 5. ATE RMSE ↓. `*` = average excluding Apart 2 (to compare with MA-MASt3R-SLAM [54], which has no Apart 2 result). RGB-D (calibrated) systems are reported as references/upper bounds, not fair baselines.

| Method              | Apart 0 ↓ | Apart 1 ↓ | Apart 2 ↓ | Office 0 ↓ | Avg ↓           |
| ------------------- | --------- | --------- | --------- | ---------- | --------------- |
| Swarm-SLAM (RGB-D)  | 1.80      | 5.56      | 5.61      | 1.42       | 3.60            |
| CP-SLAM (RGB-D)     | 0.95      | 1.42      | 1.91      | 0.65       | 1.23            |
| MAGiC-SLAM (RGB-D)  | 0.16      | 0.26      | 0.32      | 0.27       | 0.25            |
| DUSt3R ⨿            | 8.35      | 12.27     | 11.43     | 14.28      | 11.58           |
| MASt3R ⨿            | 4.02      | 6.58      | 5.66      | 7.69       | 5.99            |
| SLAM3R ⨿            | 11.72     | 31.92     | 11.74     | 20.40      | 18.94           |
| MASt3R-SLAM ⨿       | 6.96      | 8.85      | 7.46      | 9.44       | 8.17            |
| VGGT-SLAM ⨿         | 3.42      | 10.34     | 7.39      | 7.46       | 7.15            |
| MA-MASt3R-SLAM [54] | 5.24      | 5.48      | -         | 3.84       | 4.43\*          |
| **MAGiSt3R**        | **2.75**  | **5.81**  | **3.09**  | **2.57**   | **3.87/3.88\*** |

MAGiSt3R beats all RGB feed-forward baselines and the concurrent MA-MASt3R-SLAM (3.88\* vs 4.43\*), getting close to the RGB-D upper bounds but not surpassing them.

### Tracking on AriaMultiagent (single-agent)

원논문 Table 6. ATE RMSE ↓, per-agent averages (real-world, up to 3 agents).

| Method       | Agent 1 Avg ↓ | Agent 2 Avg ↓ | Agent 3 Avg ↓ |
| ------------ | ------------- | ------------- | ------------- |
| DUSt3R       | 14.06         | 16.08         | 22.12         |
| MASt3R       | 16.04         | 12.30         | 11.76         |
| SLAM3R       | 7.17          | 5.41          | 5.01          |
| MASt3R-SLAM  | 9.62          | 28.47         | 12.55         |
| VGGT-SLAM    | 6.54          | 10.35         | 8.34          |
| **MAGiSt3R** | **2.89**      | **3.99**      | **2.96**      |

### Tracking on AriaMultiagent (multi-agent)

원논문 Table 7. ATE RMSE ↓. RGB-D (calibrated) systems reported as references.

| Method              | Room 0 ↓ | Room 1 ↓ | Avg ↓    |
| ------------------- | -------- | -------- | -------- |
| Swarm-SLAM (RGB-D)  | 6.45     | 4.78     | 5.62     |
| CP-SLAM (RGB-D)     | 3.03     | 2.87     | 2.95     |
| MAGiC-SLAM (RGB-D)  | 1.15     | 0.65     | 0.90     |
| DUSt3R ⨿            | 15.46    | 21.36    | 18.41    |
| MASt3R ⨿            | 7.80     | 20.68    | 14.24    |
| SLAM3R ⨿            | 6.97     | 6.31     | 6.64     |
| MASt3R-SLAM ⨿       | 9.13     | 29.34    | 19.24    |
| VGGT-SLAM ⨿         | 9.59     | 8.47     | 9.03     |
| MA-MASt3R-SLAM [54] | 7.59     | 31.15    | 19.37    |
| **MAGiSt3R**        | **4.68** | **2.36** | **3.52** |

### Runtime

원논문 Table 8. FPS on ReplicaMultiagent (two-agent setup). `*` = taken from original paper.

| Method           | FPS |
| ---------------- | --- |
| CP-SLAM\*        | <1  |
| MAGiC-SLAM\*     | 2   |
| DUSt3R ⨿         | <1  |
| MASt3R ⨿         | <1  |
| SLAM3R ⨿         | 3   |
| MASt3R-SLAM ⨿    | 9   |
| VGGT-SLAM ⨿      | 23  |
| MA-MASt3R-SLAM\* | 11  |
| **MAGiSt3R**     | 9   |

VGGT-SLAM is the fastest at 23 FPS but "falling short on accuracy"; MAGiSt3R and MA-MASt3R-SLAM both run at ~10 FPS (9 and 11 respectively), with MAGiSt3R retrieving significantly more accurate trajectories.

### Ablation — inter-agent merging strategies (ReplicaMultiagent, multi-agent)

원논문 Table 1. Acc. ↓ / Comp. ↓ / RMSE ↓. All variants use VGGT as the single-agent backbone.

| Method              | Train Setting | Acc. ↓   | Comp. ↓  | RMSE ↓   |
| ------------------- | ------------- | -------- | -------- | -------- |
| (A) w/ RICP         | ×             | 8.89     | 6.47     | 7.66     |
| (B) w/ SL(4)        | ×             | 13.66    | 11.67    | 18.94    |
| (C) w/ L2W          | Multi Agent   | 9.71     | 7.16     | 9.19     |
| (D) w/ MAGMA        | Single Agent  | 6.89     | 4.93     | 5.35     |
| **(E) MAGiSt3R**    | Multi Agent   | **5.37** | **3.36** | **3.87** |
| (F) w/o L_geo       | Multi Agent   | 5.88     | 3.60     | 3.97     |
| (G) w/o Spatial Tok | Multi Agent   | 6.04     | 3.71     | 4.19     |

MAGMA outperforms RICP, SL(4), and SLAM3R's L2W even when trained only in a single-agent regime (D); RICP is the best of the alternatives, motivating its use to build the multi-agent baselines. Removing L_geo (F) or spatial tokens (G) both degrade results.

### Ablation — backbone and PGO (ReplicaMultiagent, multi-agent)

원논문 Table 2. Acc. ↓ / Comp. ↓ / RMSE ↓.

| Method            | Acc. ↓   | Comp. ↓  | RMSE ↓   |
| ----------------- | -------- | -------- | -------- |
| **(E) MAGiSt3R**  | **5.37** | **3.36** | **3.87** |
| (H) w/ SAIL-Recon | 5.97     | 3.88     | 4.06     |
| (I) w/o PGO       | 6.18     | 4.11     | 5.65     |

VGGT is a better backbone than SAIL-Recon (H). Removing PGO (I) causes the largest drop, making it more impactful than backbone choice — yet even without PGO, MAGMA still beats the merging strategies (A)/(B)/(C) of Table 1.

## 💡 Insights & Impact

- **Feed-forward multi-agent is new**: Prior multi-agent SLAM (CP-SLAM, MNE-SLAM, MAGiC-SLAM) relies on NeRF/3DGS neural representations that need RGB-D input and per-scene optimization. MAGiSt3R is the first to bring feed-forward 3R models into the multi-agent, RGB-only, uncalibrated setting.
- **Learned merging beats geometric alignment**: RICP and SL(4) alignment depend on submap similarity and break down at low inter-agent overlap; MAGMA learns geometry-feature correspondences and stays effective under low overlap (a custom sequence with ~15% overlap and moving subjects is shown qualitatively).
- **PGO matters most**: The ablation ranks PGO as the single most impactful component for accuracy, above backbone selection.
- **Approaching calibrated RGB-D quality**: On tracking, MAGiSt3R closes much of the gap to calibrated RGB-D systems while using only monocular RGB, though it does not surpass those references.
- **Limitations (author-stated)**: Not designed for agents under very different conditions (day vs night, adverse weather); future work targets new benchmarks and scaling beyond 3 agents.

## 🔗 Related Work

- **[VGGT](vggt.md)**: Backbone of MAGiSt3R — jointly predicts point clouds, poses, and intrinsics per submap.
- **[VGGT-SLAM](vggt-slam.md)**: SL(4)-manifold optimization; used both as a baseline and, via its SL(4) merging, as an ablation alternative (B).
- **[SLAM3R](slam3r.md)**: Its Local-to-World (L2W) module is compared against MAGMA (C); also a baseline.
- **[MASt3R-SLAM](mast3r-slam.md)**: Real-time monocular SLAM baseline; a concurrent multi-agent lift (MA-MASt3R-SLAM) is the closest competitor.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: Foundational 3R pairwise models used as sequential two-view baselines; DUSt3R's confidence-aware loss is reused.
- **[Spann3R](spann3r.md)**: Spatial-memory incremental reconstruction, cited as related single-agent 3R SLAM.

## 📚 Key Takeaways

1. **First of its kind**: MAGiSt3R is the first multi-agent, feed-forward, RGB-only dense 3D reconstruction and tracking framework, running at almost 10 FPS (9 FPS in Table 8).
2. **MAGMA is the key module**: A learned aggregation model that merges submaps at intra- and inter-agent levels, consistently beating RICP, SL(4), and L2W merging strategies.
3. **State-of-the-art among feed-forward methods**: Best reconstruction (Table 3) and tracking (Tables 4–7) versus DUSt3R, MASt3R, SLAM3R, MASt3R-SLAM, VGGT-SLAM, and concurrent MA-MASt3R-SLAM, while approaching — not beating — calibrated RGB-D SLAM references.
4. **PGO and spatial/geometry cues are essential**: Ablations show pose graph optimization, the L_geo loss, and spatial tokens each contribute measurably.

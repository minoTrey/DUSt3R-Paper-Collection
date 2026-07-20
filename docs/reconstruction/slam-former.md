# SLAM-Former: Putting SLAM into One Transformer (ECCV 2026)

## 📋 Overview

- **Authors**: Yijun Yuan, Zhuoguang Chen, Kenan Li, Weibang Wang, Hang Zhao
- **Institution**: IIIS, Tsinghua University
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2509.16909) | [Project Page](https://tsinghua-mars-lab.github.io/SLAM-Former)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A single transformer that houses both the SLAM frontend (causal, incremental keyframe tracking and mapping via KV cache) and the backend (full-attention global refinement of map tokens), with the two alternating and feeding each other through a shared cache.

## 🎯 Key Contributions

1. **One transformer for the whole SLAM stack**: Traditional dense SLAM chains a frontend model, a loop-detection model, and a factor-graph optimizer. SLAM-Former puts frontend and backend into the same backbone with shared weights.
2. **Backend as dense factor graph**: Full attention across all map tokens gives a global receptive field, which the paper argues is equivalent to running loop detection on a dense factor graph — no explicit loop-closure module.
3. **Bidirectional frontend–backend coupling**: After each backend run the refined KV cache replaces the frontend's cache, so subsequent frames are tracked against the refined global structure; the frontend in turn supplies initialization and sequential ordering.
4. **Three-mode joint training**: Causal (frontend), mixed (frontend conditioned on backend-refined cache), and full attention (backend) are all executed within a single training iteration with shared weights.
5. **Local pointmaps instead of global geometry**: Unlike VGGT, heads predict per-frame local pointmaps, avoiding the need to designate a world coordinate frame.

## 🔧 Technical Details

### Architecture

A backbone `f` with L layers of intra-frame attention and inter-frame attention, plus task heads `h` predicting pointmap `P*`, confidence `Σ*`, and camera pose `g*`. Following Pi3-like design, register tokens are **shared across all frames**, removing the need for a designated reference frame. The model has **36 transformer layers** of frame- and global-attention in total.

### Frontend

For each incoming frame, `F_t = f_fn(I_t){C_k}` conditioned on the KV cache of previous keyframes. A pose head estimates `g_t`; a frame becomes a keyframe when its relative translation to the previous keyframe exceeds a threshold τ. Keyframe detection does **not** use the KV cache — it applies `f_fn(I_kprev, I_t)` on the frame pair for efficiency.

Pure causal attention would implicitly make the first frame the reference. The paper therefore applies **full attention to the first two frames** and causal attention thereafter, and at inference jointly processes the first two keyframes to fix the global coordinate.

### Backend

`M̄ = f_bn(M)` refines all accumulated map tokens in a single full-attention pass. Cache sharing then sets `{C_k} ← C_M`. The backend is triggered **after every T keyframes**.

### Training

- Loss: `L = L_depth + L_pmap + λ·L_cam`, with depth and pointmap terms confidence-weighted (`Σ*`) and including spatial-gradient terms, and camera supervision using a scaled Huber loss on relative poses.
- Overall objective across the three modes: `L_all = L_1 + L_2 + β·L_3`.
- Hyperparameters: λ = 100, β = 10.
- Initialized from **Pi3 pre-trained weights**; 10 epochs, batch size 32, AdamW at lr 1e-5 with cosine schedule (image encoder and camera head frozen).
- Training data: ARKitScenes, ScanNet, ScanNet++, HyperSim, BlendedMVS, MegaDepth, MVS-Synth.
- **11 hours on 32 A100 GPUs**; evaluation on a single RTX 4090.

## 📊 Results

### Camera Tracking — TUM RGB-D (ATE RMSE, m)

원논문 Table 1. `*` = baseline evaluated in uncalibrated mode as reported by the VGGT-SLAM paper; `+` = baseline run on the authors' machine. `×` = failure. The first block is calibrated, the second uncalibrated.

| Method        | 360   | desk  | desk2 | floor | plant | room  | rpy   | teddy | xyz   | Avg   |
| ------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| ORB-SLAM3     | ×     | 0.017 | 0.210 | ×     | 0.034 | ×     | ×     | ×     | 0.009 | N/A   |
| DeepV2D       | 0.243 | 0.166 | 0.379 | 1.653 | 0.203 | 0.246 | 0.105 | 0.316 | 0.064 | 0.375 |
| DeepFactors   | 0.159 | 0.170 | 0.253 | 0.169 | 0.305 | 0.364 | 0.043 | 0.601 | 0.035 | 0.233 |
| DPV-SLAM      | 0.112 | 0.018 | 0.029 | 0.057 | 0.021 | 0.330 | 0.030 | 0.084 | 0.010 | 0.076 |
| DPV-SLAM++    | 0.132 | 0.018 | 0.029 | 0.050 | 0.022 | 0.096 | 0.032 | 0.098 | 0.010 | 0.054 |
| GO-SLAM       | 0.089 | 0.016 | 0.028 | 0.025 | 0.026 | 0.052 | 0.019 | 0.048 | 0.010 | 0.035 |
| DROID-SLAM    | 0.111 | 0.018 | 0.042 | 0.021 | 0.016 | 0.049 | 0.026 | 0.048 | 0.012 | 0.038 |
| MASt3R-SLAM   | 0.049 | 0.016 | 0.024 | 0.025 | 0.020 | 0.061 | 0.027 | 0.041 | 0.009 | 0.030 |
| DROID-SLAM\*  | 0.202 | 0.032 | 0.091 | 0.064 | 0.045 | 0.918 | 0.056 | 0.045 | 0.012 | 0.158 |
| MASt3R-SLAM\* | 0.070 | 0.035 | 0.055 | 0.056 | 0.035 | 0.118 | 0.041 | 0.114 | 0.020 | 0.060 |
| VGGT-SLAM     | 0.071 | 0.025 | 0.040 | 0.141 | 0.023 | 0.102 | 0.030 | 0.034 | 0.014 | 0.053 |
| CUT3R+        | 0.102 | 0.054 | 0.118 | 0.211 | 0.083 | 0.264 | 0.044 | 0.120 | 0.020 | 0.113 |
| StreamVGGT+   | 0.088 | 0.063 | 0.105 | 0.604 | 0.070 | 0.633 | 0.025 | 0.081 | 0.015 | 0.187 |
| VGGT-SLAM+    | 0.053 | 0.024 | 0.040 | 0.335 | 0.022 | 0.166 | 0.040 | 0.037 | 0.041 | 0.084 |
| **Ours**      | 0.067 | 0.018 | 0.026 | 0.079 | 0.021 | 0.082 | 0.017 | 0.030 | 0.011 | 0.039 |

Honest reading: SLAM-Former leads every uncalibrated baseline on average, but among **calibrated** methods MASt3R-SLAM (0.030) and GO-SLAM (0.035) are still ahead of its 0.039.

### Camera Tracking — 7-Scenes (ATE RMSE, m)

원논문 Table 2. Same `*` / `+` conventions.

| Method        | chess | fire  | heads | office | pumpkin | kitchen | stairs | Avg   |
| ------------- | ----- | ----- | ----- | ------ | ------- | ------- | ------ | ----- |
| NICER-SLAM    | 0.033 | 0.069 | 0.042 | 0.108  | 0.200   | 0.039   | 0.108  | 0.086 |
| DROID-SLAM    | 0.036 | 0.027 | 0.025 | 0.066  | 0.127   | 0.040   | 0.026  | 0.049 |
| MASt3R-SLAM   | 0.053 | 0.025 | 0.015 | 0.097  | 0.088   | 0.041   | 0.011  | 0.047 |
| DROID-SLAM\*  | 0.047 | 0.038 | 0.034 | 0.136  | 0.166   | 0.080   | 0.044  | 0.078 |
| MASt3R-SLAM\* | 0.063 | 0.046 | 0.029 | 0.103  | 0.114   | 0.074   | 0.032  | 0.066 |
| VGGT-SLAM     | 0.036 | 0.028 | 0.018 | 0.103  | 0.133   | 0.058   | 0.093  | 0.067 |
| CUT3R+        | 0.046 | 0.043 | 0.055 | 0.120  | 0.096   | 0.061   | 0.086  | 0.073 |
| StreamVGGT+   | 0.048 | 0.036 | 0.030 | 0.117  | 0.094   | 0.063   | 0.179  | 0.081 |
| VGGT-SLAM+    | 0.037 | 0.027 | 0.018 | 0.101  | 0.138   | 0.057   | 0.095  | 0.068 |
| **Ours**      | 0.039 | 0.033 | 0.018 | 0.070  | 0.065   | 0.035   | 0.033  | 0.042 |

### Camera Tracking — Replica (ATE RMSE, m)

원논문 Table 3. `+` = run on the authors' machine.

| Method      | Rm0   | Rm1   | Rm2   | Of0   | Of1   | Of2   | Of3   | Of4   | Avg   |
| ----------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| NICER-SLAM  | 0.013 | 0.016 | 0.011 | 0.021 | 0.032 | 0.021 | 0.014 | 0.020 | 0.019 |
| DROID-SLAM  | 0.003 | 0.001 | 0.003 | 0.003 | 0.004 | 0.003 | 0.005 | 0.004 | 0.003 |
| SLAM3R      | 0.046 | 0.059 | 0.057 | 0.112 | 0.063 | 0.062 | 0.050 | 0.081 | 0.066 |
| CUT3R+      | 0.145 | 0.243 | 0.127 | 0.159 | 0.230 | 0.162 | 0.088 | 0.204 | 0.170 |
| StreamVGGT+ | 0.113 | 0.163 | 0.077 | 0.076 | 0.070 | 0.180 | 0.153 | 0.168 | 0.125 |
| VGGT-SLAM+  | 0.030 | 0.167 | 0.086 | 0.042 | 0.064 | 0.095 | 0.039 | 0.043 | 0.071 |
| **Ours**    | 0.030 | 0.026 | 0.027 | 0.028 | 0.029 | 0.038 | 0.028 | 0.031 | 0.030 |

The paper is explicit that this is a partial win: SLAM-Former reports "approximate 50% reduction in ATE compared to SLAM3R" and beats all uncalibrated baselines, but is "on par with NICER-SLAM" and "still lags behind the traditional SLAM method, DROID-SLAM" (0.003). The stated reason is that Replica is synthetic and lacks the noise and blur that hurt matching-based bundle adjustment.

### Reconstruction — Replica (Accuracy / Completeness, average over 8 scenes)

원논문 Table 4, Average column only (the full table is one Acc./Comp. pair per scene, too wide to reproduce faithfully here). `*` = numbers reported in NICER-SLAM, `−` = numbers from SLAM3R, `+` = run by the authors. The caption does not state a unit; the body text discusses the margin over the runner-up in centimetres.

| Method          | Acc. ↓   | Comp. ↓  |
| --------------- | -------- | -------- |
| DUSt3R          | 3.49     | 2.48     |
| MASt3R          | 4.71     | 3.36     |
| NICER-SLAM\*    | 3.65     | 4.16     |
| DROID-SLAM\*    | 5.50     | 12.29    |
| DIM-SLAM\*      | 11.60    | 7.85     |
| GO-SLAM−        | 3.81     | 4.79     |
| Spann3R−        | 10.32    | 13.33    |
| SLAM3R−         | 3.57     | 2.62     |
| CUT3R+          | 7.52     | 3.62     |
| VGGT-SLAM+      | 7.52     | 5.86     |
| **SLAM-Former** | **2.09** | **1.56** |

### Reconstruction — 7-Scenes (m)

원논문 Table 5. `@n` indicates a keyframe every n images.

| Method        | ATE ↓     | Acc. ↓    | Complet. ↓ | Chamfer ↓ |
| ------------- | --------- | --------- | ---------- | --------- |
| DROID-SLAM    | 0.049     | 0.141     | 0.048      | 0.094     |
| MASt3R-SLAM   | 0.047     | 0.089     | 0.085      | 0.087     |
| Spann3R @20   | N/A       | 0.069     | 0.047      | 0.058     |
| Spann3R @2    | N/A       | 0.124     | 0.043      | 0.084     |
| MASt3R-SLAM\* | 0.066     | 0.068     | 0.045      | 0.056     |
| VGGT-SLAM     | 0.067     | 0.052     | 0.058      | 0.055     |
| CUT3R+        | 0.073     | 0.032     | 0.047      | 0.040     |
| StreamVGGT+   | 0.081     | 0.058     | 0.057      | 0.057     |
| VGGT-SLAM+    | 0.068     | 0.054     | 0.060      | 0.057     |
| **Ours**      | **0.042** | **0.017** | **0.037**  | **0.027** |

### Ablation: Frontend / Backend Cooperation (TUM RGB-D, ATE RMSE, m)

원논문 Table 6. F. = Frontend, MB. = Middle Backend, EB. = End Backend.

| Variant        | 360   | desk  | desk2 | floor | plant | room  | rpy   | teddy | xyz   | Avg   |
| -------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| F.-only        | 0.137 | 0.041 | 0.045 | 0.264 | 0.053 | 0.547 | 0.036 | 0.073 | 0.013 | 0.134 |
| F. + EB.       | 0.073 | 0.021 | 0.026 | 0.078 | 0.022 | 0.104 | 0.018 | 0.027 | 0.011 | 0.042 |
| F. + MB.       | 0.067 | 0.018 | 0.025 | 0.081 | 0.023 | 0.082 | 0.017 | 0.031 | 0.011 | 0.039 |
| F. + MB. + EB. | 0.067 | 0.018 | 0.026 | 0.079 | 0.021 | 0.082 | 0.017 | 0.030 | 0.011 | 0.039 |

The frontend alone reaches 0.134; any backend brings it to ~0.04. The paper notes candidly that MB. and EB. are comparable on ATE and that combining them shows no marked improvement on the overall metric — MB.'s value shows up in intermediate reconstructions (Fig. 5), not in the final trajectory number.

### Runtime

원논문 Table 7. TPE = Time per Execution.

| Dataset        | KF-detection TPE (ms) | Frontend TPE (ms) | Backend TPE (ms) | FPS  |
| -------------- | --------------------- | ----------------- | ---------------- | ---- |
| TUM: room      | 89                    | 97                | 187              | 10.8 |
| 7Scene: chess  | 89                    | 77                | 83               | 11.0 |
| Replica: room1 | 87                    | 76                | 113              | 11.3 |

## 💡 Insights & Impact

### The Diagnosis It Starts From

The paper names two distinct failure modes in the current landscape and builds directly against them:

- **Submap-alignment methods** (MASt3R-SLAM, VGGT-SLAM) suffer global inconsistency because they align local submaps. MASt3R-SLAM patches this with TSDF fusion, which the paper says can only fix small mismatches; VGGT-SLAM connects submaps only at front- and end-nodes.
- **Streaming methods** (StreamVGGT, Stream3R, CUT3R) process incremental input without ever remapping the past, so past and incoming data can drift apart.

SLAM-Former's answer is that if a transformer can attend over all map tokens at once, the backend _is_ the global optimizer, and the KV cache is the channel through which that global correction propagates back into the causal frontend.

### Why the Ablation Is the Real Result

Frontend-only ATE of 0.134 versus 0.039 with the backend is a 3.4× gap on the same weights and the same architecture. This isolates the contribution to the alternating execution rather than to the backbone — the model is initialized from Pi3, so raw representational power is largely inherited.

### Where It Does Not Win

Calibrated classical SLAM still wins on synthetic data (DROID-SLAM at 0.003 on Replica). The paper's explanation — clean synthetic data makes correspondence-based bundle adjustment nearly exact — is a useful reminder that benchmark composition, not method quality, drives some of these rankings.

### Limitations

The authors note that replacing loop detection and optimization with full attention in the backend is itself a limitation to examine further.

## 🔗 Related Work

- [VGGT-SLAM](./vggt-slam.md) — the submap + SL(4) manifold approach SLAM-Former argues against; a direct baseline in every table.
- [MASt3R-SLAM](./mast3r-slam.md) — pairwise matching under a traditional SLAM pipeline; the strongest calibrated baseline here.
- [Pi3](./pi3.md) — supplies the pre-trained initialization and the shared-register, reference-frame-free design.
- [VGGT](./vggt.md) — contrasted directly: VGGT predicts global geometry, SLAM-Former predicts per-frame local pointmaps.
- [StreamVGGT](./streamvggt.md), [Stream3R](./stream3r.md), [CUT3R](../dynamic/cut3r.md) — the streaming/causal family whose "never revisit the past" property motivates the backend.
- [Spann3R](./spann3r.md), [SLAM3R](./slam3r.md) — memory-based and SLAM-oriented predecessors appearing as reconstruction baselines.
- [Fast3R](./fast3r.md), [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md) — the feed-forward lineage the paper positions itself within.

## 📚 Key Takeaways

1. **Frontend and backend can be the same weights.** Three training modes (causal, mixed, full attention) over one backbone let a single transformer do both roles, with the KV cache as the coupling mechanism.
2. **Full attention substitutes for loop closure.** The backend's dense connections across all map tokens play the role of loop detection plus graph optimization, without either module.
3. **The backend is what makes it work.** TUM ATE goes from 0.134 (frontend only) to 0.039 with backend refinement.
4. **Reconstruction is the stronger claim.** On 7-Scenes SLAM-Former reaches 0.017 m accuracy where every baseline is above 0.05 m; tracking is competitive but not uniformly best, losing to calibrated MASt3R-SLAM on TUM average and to DROID-SLAM on synthetic Replica.
5. **Real-time-ish, not real-time.** 10.8–11.3 FPS on a single RTX 4090.

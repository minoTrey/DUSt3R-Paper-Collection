# Mem3R: Streaming 3D Reconstruction with Hybrid Memory via Test-Time Training (arXiv preprint (2026-04))

![mem3r — architecture](https://arxiv.org/html/2604.07279v1/x2.png)

_Overview of Mem3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Changkun Liu, Jiezhi Yang, Zeman Li, Yuan Deng, Jiancong Guo, Luca Ballan
- **Institution**: Google; The Hong Kong University of Science and Technology; University of Southern California (Changkun Liu and Zeman Li did the work during a Student Researcher Internship at Google)
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.07279) | [Project Page](https://lck666666.github.io/Mem3R/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An RNN-based streaming 3D reconstruction model built on the CUT3R paradigm that decouples camera tracking from geometric mapping through a hybrid memory: an implicit MLP-based fast-weight memory (updated via Test-Time Training) for pose, and an explicit token-based state for geometry. It shrinks the model from 793M to 644M parameters (~19%) while improving long-sequence accuracy, and stays plug-and-play compatible with CUT3R state-update strategies such as TTT3R and TTSA3R.

## 🎯 Key Contributions

1. **Dual (hybrid) memory design**: Decouples camera tracking from geometric mapping — an implicit fast-weight memory `W` for pose and an explicit token-based state `S` for global geometry — to reduce drift and temporal forgetting over long streams.
2. **Implicit memory via Test-Time Training**: Replaces CUT3R's pose-related state tokens and decoder layers with a lightweight SwiGLU MLP whose fast weights are updated online during inference (per-step decay `α`, per-layer learning rate `η`), preserving O(1) inference complexity.
3. **Channel-wise state update gate**: Treats the decoder's state output as a candidate update and integrates it via a learnable channel-wise gate `ζ ∈ (0,1)`, rather than overwriting the recurrent state.
4. **Parameter efficiency**: Reduces model size from 793M to 644M parameters (~19% reduction) and GPU memory usage by 7% relative to CUT3R, while matching CUT3R throughput.
5. **Plug-and-play compatibility**: Remains compatible with training-free per-token state-update strategies (TTT3R, TTSA3R) and delivers further gains when combined with them.

## 🔧 Technical Details

### Problem setting

In streaming 3D perception a model processes an image sequence `{I_t}` incrementally, estimating camera motion and scene geometry online as new observations arrive. RNN-based recurrent models (e.g. CUT3R) keep a fixed-size state for constant-memory, linear-time inference, but the compact state becomes an information bottleneck once the sequence exceeds the training horizon, causing temporal forgetting and trajectory drift. KV-cache approaches (e.g. StreamVGGT) preserve full history but grow memory linearly and risk out-of-memory (OOM) on long streams.

### Hybrid memory architecture

For each frame `I_t`, a ViT encoder extracts image features `F_t`. Two memories run in parallel:

- **Implicit memory `W` (camera tracking)**: A lightweight SwiGLU MLP fast-weight module, `f_W(x) = W2(SiLU(W1 x) ⊙ (W3 x))`, with weights updated online during inference. An L2-normalized query `q_t` reads a pose prior `p̂_t = f_{W_{t-1}}(q_t)`, which replaces CUT3R's learned pose token `z_t`.
- **Explicit memory `S` (geometric mapping)**: Persistent token-based state `S_t ∈ R^{Ns×C}` preserving global geometry.

The decoder consumes `X_t = [p̂_t, F_t]` and the previous state `S_{t-1}` to produce a refined posterior pose token `p_t`, state-enriched features `F_t'`, and a candidate state update `S̃_t`.

### Test-Time Training update of implicit memory

The fast weights are aligned by the loss `L_ttt(p̂_t, p_t) = ⟨p̂_t, p_t⟩`. A per-step decay `α_t = 1 − γ·σ(W_α F_t)` (with `γ = 0.01`) and per-layer learning rate `η_t = Softplus(W_η F_t + c_base)` (with `c_base = 0.001`) are predicted from current features, giving `W_t = α_t W_{t-1} + η_t ⊙ ∇_W L_ttt`.

### Channel-wise gated update of explicit memory

A channel-wise gate `ζ_t = σ(f_ζ(F_t, S_{t-1}))` controls integration: `S_t = ζ_t ⊙ S̃_t + (1 − ζ_t) ⊙ S_{t-1}`. When applying TTT3R/TTSA3R per-token gates `G`, the update becomes `S_t = G_t ⊙ ζ_t ⊙ S̃_t + G_t ⊙ (1 − ζ_t) ⊙ S_{t-1}`.

### Prediction heads and training

Follows CUT3R: self-frame and world-frame pointmaps with confidence, plus a 6-DoF pose head. Supervision uses CUT3R's confidence-aware 3D regression loss `L_3D`, pose loss `L_pose`, and an RGB reconstruction loss `L_rgb` when raymap inputs are available. Trained on the same 26-dataset mixture and configuration as CUT3R's final stage, with input sequences of 4–64 views. Initialized from pre-trained 512-DPT CUT3R weights and fine-tuned jointly with AdamW (initial learning rate `1×10⁻⁶`, linear warmup, cosine decay). Training takes ~10 hours on 32 NVIDIA H100 GPUs, batch size 8 per GPU.

### Module details (supplementary)

- Explicit geometric memory: 768 state tokens, each of dimension 768. Confidence regularization coefficient `β = 0.2`.
- Fast-weight memory: ~1.56M parameters; projects 1024-dim features into 768-dim latent split over 12 heads (64 dims/head); three `64×64` weight matrices per head; learning-rate head outputs 36 scalars, decay head outputs 12 head-wise `α`.
- Channel-wise update module: ~0.98M parameters; concatenates 768-dim state feature with 1024-dim visual feature (1792-dim), bottleneck 384 with GELU, projects back to 768.
- Total added parameters: ~2.54M across four main projection/bottleneck layers.

## 📊 Results

All quantitative evaluations run on NVIDIA A100 40GB GPUs. The closest baseline is the RNN-based CUT3R; the paper emphasizes long sequences (≥ 200 frames). Full-attention models VGGT (offline) and StreamVGGT are prone to OOM on long streams.

### Model efficiency

원논문 Table 3. 7-Scenes 512×384 images on a single NVIDIA RTX PRO 6000 Blackwell Max-Q GPU.

| Method        | Runtime (fps) ↑ | Memory (MiB) ↓ | Params ↓ |
| ------------- | --------------- | -------------- | -------- |
| CUT3R         | 26              | 7930           | 793M     |
| Ours          | 26              | 7340           | 644M     |
| TTT3R         | 25              | 8364           | 793M     |
| Ours + TTT3R  | 25              | 7774           | 644M     |
| TTSA3R        | 25              | 8786           | 793M     |
| Ours + TTSA3R | 25              | 8208           | 644M     |

### Video depth estimation — KITTI (long sequences)

원논문 Table 1. Subset of frame counts (300 / 400 / 500) shown; the paper also reports 350 and 450.

| Method (Metric Depth) | 300 Abs Rel ↓ | 300 δ1.25 ↑ | 400 Abs Rel ↓ | 400 δ1.25 ↑ | 500 Abs Rel ↓ | 500 δ1.25 ↑ |
| --------------------- | ------------- | ----------- | ------------- | ----------- | ------------- | ----------- |
| CUT3R                 | 0.13          | 83.8        | 0.14          | 82.1        | 0.15          | 80.4        |
| Ours                  | 0.12          | 88.4        | 0.13          | 87.1        | 0.13          | 86.0        |
| TTT3R                 | 0.12          | 88.5        | 0.13          | 87.3        | 0.13          | 86.5        |
| Ours + TTT3R          | 0.11          | 89.5        | 0.12          | 88.6        | 0.13          | 87.5        |
| TTSA3R                | 0.12          | 88.8        | 0.13          | 87.5        | 0.13          | 86.5        |
| Ours + TTSA3R         | 0.12          | 89.0        | 0.12          | 88.2        | 0.13          | 87.0        |

원논문 Table 1 (Scale-Invariant Depth 부분). 같은 프레임 subset.

| Method (Scale-Invariant) | 300 Abs Rel ↓ | 300 δ1.25 ↑ | 400 Abs Rel ↓ | 400 δ1.25 ↑ | 500 Abs Rel ↓ | 500 δ1.25 ↑ |
| ------------------------ | ------------- | ----------- | ------------- | ----------- | ------------- | ----------- |
| CUT3R                    | 0.12          | 87.4        | 0.13          | 87.1        | 0.13          | 86.5        |
| Ours                     | 0.11          | 90.3        | 0.11          | 89.4        | 0.11          | 89.1        |
| TTT3R                    | 0.11          | 90.2        | 0.12          | 89.5        | 0.12          | 89.1        |
| Ours + TTT3R             | 0.10          | 91.3        | 0.11          | 90.5        | 0.11          | 89.9        |
| TTSA3R                   | 0.11          | 90.9        | 0.11          | 90.0        | 0.12          | 89.4        |
| Ours + TTSA3R            | 0.10          | 92.0        | 0.11          | 91.2        | 0.11          | 90.5        |

### Video depth estimation — Bonn (long sequences)

원논문 Table 2 (Scale-Invariant Depth 부분). Subset 300 / 400 / 500 frames.

| Method (Scale-Invariant) | 300 Abs Rel ↓ | 300 δ1.25 ↑ | 400 Abs Rel ↓ | 400 δ1.25 ↑ | 500 Abs Rel ↓ | 500 δ1.25 ↑ |
| ------------------------ | ------------- | ----------- | ------------- | ----------- | ------------- | ----------- |
| CUT3R                    | 0.089         | 93.8        | 0.090         | 93.3        | 0.084         | 93.8        |
| Ours                     | 0.085         | 94.6        | 0.087         | 94.1        | 0.083         | 94.5        |
| TTT3R                    | 0.079         | 94.9        | 0.078         | 95.1        | 0.076         | 95.3        |
| Ours + TTT3R             | 0.077         | 94.9        | 0.076         | 95.1        | 0.075         | 95.3        |
| TTSA3R                   | 0.078         | 95.1        | 0.077         | 95.2        | 0.076         | 95.4        |
| Ours + TTSA3R            | 0.076         | 95.0        | 0.074         | 95.1        | 0.073         | 95.3        |

Note: on Bonn scale-invariant depth, TTT3R and TTSA3R alone slightly edge out Mem3R at some frame counts (e.g. 300 δ1.25: TTT3R 94.9 vs Ours+TTT3R 94.9; TTSA3R 95.1 vs Ours+TTSA3R 95.0); Mem3R's gains here are smaller than on KITTI.

### Camera pose estimation — ATE on long sequences

원논문 Table 5. Subset of frame counts (50 / 200 / 400 / 600 / 800 / 1000); the paper reports 12 frame counts. ATE (m) ↓.

| Method (TUM-D) | 50    | 200   | 400   | 600   | 800   | 1000  |
| -------------- | ----- | ----- | ----- | ----- | ----- | ----- |
| CUT3R          | 0.023 | 0.061 | 0.12  | 0.14  | 0.17  | 0.17  |
| Ours           | 0.012 | 0.042 | 0.078 | 0.096 | 0.14  | 0.15  |
| TTT3R          | 0.014 | 0.041 | 0.051 | 0.067 | 0.091 | 0.11  |
| Ours + TTT3R   | 0.011 | 0.025 | 0.037 | 0.041 | 0.060 | 0.073 |
| TTSA3R         | 0.012 | 0.030 | 0.043 | 0.056 | 0.079 | 0.091 |
| Ours + TTSA3R  | 0.011 | 0.023 | 0.032 | 0.036 | 0.051 | 0.064 |

원논문 Table 5 (ScanNet 부분). ATE (m) ↓, same frame subset.

| Method (ScanNet) | 50    | 200  | 400  | 600  | 800  | 1000 |
| ---------------- | ----- | ---- | ---- | ---- | ---- | ---- |
| CUT3R            | 0.045 | 0.32 | 0.57 | 0.66 | 0.76 | 0.82 |
| Ours             | 0.040 | 0.20 | 0.43 | 0.53 | 0.65 | 0.71 |
| TTT3R            | 0.033 | 0.14 | 0.24 | 0.28 | 0.37 | 0.40 |
| Ours + TTT3R     | 0.034 | 0.13 | 0.20 | 0.22 | 0.27 | 0.29 |
| TTSA3R           | 0.033 | 0.13 | 0.21 | 0.26 | 0.36 | 0.39 |
| Ours + TTSA3R    | 0.035 | 0.12 | 0.18 | 0.21 | 0.26 | 0.30 |

Highlighted result: Mem3R with TTT3R gives a 39% relative reduction in ATE at the 500-frame mark on the TUM Dynamics dataset versus the base TTT3R model. ScanNet/TUM-D per-view curves are also in Figure 3 (그림 3, 수치 미인쇄).

### 3D reconstruction — 7-Scenes and NRGBD

원논문 Table 8. Chamfer Distance (CD) ↓ and Normal Consistency (NC) ↑; OOM = out-of-memory. Subset 200 / 300 / 400 frames (paper also reports 250 / 350).

| Method (7-Scenes) | 200 CD ↓ | 200 NC ↑ | 300 CD ↓ | 300 NC ↑ | 400 CD ↓ | 400 NC ↑ |
| ----------------- | -------- | -------- | -------- | -------- | -------- | -------- |
| VGGT (offline)    | OOM      | OOM      | OOM      | OOM      | OOM      | OOM      |
| Stream-VGGT       | OOM      | OOM      | OOM      | OOM      | OOM      | OOM      |
| CUT3R             | 0.070    | 0.563    | 0.110    | 0.541    | 0.130    | 0.533    |
| Ours              | 0.038    | 0.575    | 0.057    | 0.558    | 0.077    | 0.549    |
| TTT3R             | 0.025    | 0.581    | 0.031    | 0.565    | 0.038    | 0.557    |
| Ours + TTT3R      | 0.023    | 0.580    | 0.025    | 0.566    | 0.027    | 0.560    |
| TTSA3R            | 0.023    | 0.582    | 0.026    | 0.567    | 0.030    | 0.561    |
| Ours + TTSA3R     | 0.021    | 0.581    | 0.022    | 0.566    | 0.023    | 0.560    |

원논문 Table 8 (NRGBD 부분). Same metrics and frame subset.

| Method (NRGBD) | 200 CD ↓ | 200 NC ↑ | 300 CD ↓ | 300 NC ↑ | 400 CD ↓ | 400 NC ↑ |
| -------------- | -------- | -------- | -------- | -------- | -------- | -------- |
| VGGT (offline) | OOM      | OOM      | OOM      | OOM      | OOM      | OOM      |
| Stream-VGGT    | OOM      | OOM      | OOM      | OOM      | OOM      | OOM      |
| CUT3R          | 0.081    | 0.602    | 0.162    | 0.576    | 0.220    | 0.552    |
| Ours           | 0.060    | 0.612    | 0.101    | 0.592    | 0.135    | 0.577    |
| TTT3R          | 0.037    | 0.626    | 0.065    | 0.605    | 0.104    | 0.595    |
| Ours + TTT3R   | 0.037    | 0.625    | 0.062    | 0.612    | 0.064    | 0.608    |
| TTSA3R         | 0.031    | 0.630    | 0.057    | 0.616    | 0.069    | 0.609    |
| Ours + TTSA3R  | 0.032    | 0.625    | 0.052    | 0.616    | 0.061    | 0.612    |

7-Scenes per-view CD and NC curves are in Figure 5 (그림 5, 수치 미인쇄), which also marks OOM points for VGGT (offline) and StreamVGGT.

### Short sequences — Sintel (50 frames)

원논문 Table 6. Online (✓/✗). Camera pose: ATE / RPE trans / RPE rot; per-sequence-scale depth: Abs Rel / δ<1.25. Metric-scale depth columns omitted for width. `–` = metric-scale depth unavailable.

| Method        | Online | ATE ↓ | RPE trans ↓ | RPE rot ↓ | Abs Rel ↓ | δ < 1.25 ↑ |
| ------------- | ------ | ----- | ----------- | --------- | --------- | ---------- |
| DUSt3R-GA     | ✗      | 0.417 | 0.250       | 5.796     | 0.656     | 45.2       |
| MASt3R-GA     | ✗      | 0.185 | 0.060       | 1.496     | 0.641     | 43.9       |
| MonST3R-GA    | ✗      | 0.111 | 0.044       | 0.869     | 0.378     | 55.8       |
| VGGT          | ✗      | 0.172 | 0.062       | 0.471     | 0.299     | 63.8       |
| π³            | ✗      | 0.073 | 0.038       | 0.288     | 0.233     | 66.4       |
| Spann3R       | ✓      | 0.329 | 0.110       | 4.471     | 0.622     | 42.6       |
| Point3R       | ✓      | 0.351 | 0.128       | 1.822     | 0.452     | 48.9       |
| StreamVGGT    | ✓      | 0.251 | 0.149       | 1.894     | 0.323     | 65.7       |
| CUT3R         | ✓      | 0.209 | 0.069       | 0.624     | 0.433     | 46.9       |
| TTT3R         | ✓      | 0.210 | 0.091       | 0.720     | 0.405     | 48.9       |
| TTSA3R        | ✓      | 0.210 | 0.085       | 0.765     | 0.402     | 49.8       |
| Ours          | ✓      | 0.180 | 0.074       | 0.860     | 0.438     | 44.1       |
| Ours + TTT3R  | ✓      | 0.20  | 0.091       | 0.720     | 0.414     | 46.7       |
| Ours + TTSA3R | ✓      | 0.20  | 0.087       | 0.754     | 0.413     | 47.0       |

On Sintel short sequences Mem3R attains the lowest ATE among online 3D reconstruction models (0.180). But note the offline global-alignment models (π³ ATE 0.073, MonST3R-GA 0.111) remain lower, and Mem3R's per-sequence depth δ<1.25 (44.1) trails several online baselines (StreamVGGT 65.7, TTSA3R 49.8). Adding TTT3R/TTSA3R yields only limited additional gains on short sequences.

### Ablation — components (with TTT3R baseline)

원논문 Table 4. Left: TUM-D relative camera pose ATE (m) ↓; Right: KITTI scale-invariant video depth (Abs Rel ↓ / δ1.25 ↑). ATE frame subset 200 / 600 / 1000.

| Method                           | ATE 200 | ATE 600 | ATE 1000 | KITTI 300 Abs Rel ↓ | KITTI 300 δ1.25 ↑ | KITTI 500 Abs Rel ↓ | KITTI 500 δ1.25 ↑ |
| -------------------------------- | ------- | ------- | -------- | ------------------- | ----------------- | ------------------- | ----------------- |
| TTT3R                            | 0.041   | 0.074   | 0.11     | 0.11                | 90.2              | 0.12                | 89.1              |
| Ours + TTT3R (w/o. channel gate) | 0.031   | 0.059   | 0.10     | 0.11                | 91.0              | 0.11                | 89.5              |
| Ours + TTT3R (w/o. fast weight)  | 0.027   | 0.054   | 0.078    | 0.11                | 91.0              | 0.12                | 89.5              |
| Ours + TTT3R                     | 0.025   | 0.046   | 0.073    | 0.10                | 91.4              | 0.11                | 89.9              |

Both the fast-weight memory and the channel-wise state gate help mitigate temporal forgetting; the full model is best or tied-best in every column shown.

## 💡 Insights & Impact

- **Decoupling tracking from mapping.** The core insight is that a single compressed recurrent state overloads two very different jobs — precise per-frame pose tracking and persistent global geometry. Splitting them into an online-adapted implicit MLP (pose) and a gated explicit token state (geometry) improves representational efficiency and long-horizon consistency at once.
- **Fast weights as a compact local map.** Reinterpreting the pose branch as a fast-weight memory updated by Test-Time Training turns pose tracking into an O(1) online adaptation problem, filtering transient noise while accumulating reliable motion cues — the source of the up-to-39% ATE reduction on 500–1000 frame streams.
- **Smaller and cheaper, not just better.** Unusually for an accuracy paper, Mem3R is also lighter: 644M vs 793M parameters (~19% fewer) and 7% less GPU memory than CUT3R, at matched throughput (26 fps; 25 fps with TTT3R/TTSA3R).
- **Orthogonal to state-update research.** Because the explicit-state gate composes with per-token gates, training-free strategies (TTT3R, TTSA3R) drop in and stack, so Mem3R benefits from the ongoing line of CUT3R state-update work rather than competing with it.
- **Honest limits.** On short sequences (Sintel, KITTI/Bonn 110 frames) the advantage over CUT3R is modest and plug-in strategies add little; offline global-alignment models still win several short-sequence metrics. The paper positions Mem3R specifically for long-horizon streaming.

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The closest baseline and backbone paradigm — a fixed-size recurrent latent state for constant-memory streaming. Mem3R inherits its heads, losses, and 26-dataset training recipe, then replaces the pose-related state tokens and decoder with the implicit fast-weight memory.
- **[TTT3R](ttt3r.md)** and **TTSA3R**: Training-free, plug-and-play per-token state-update strategies for CUT3R. Mem3R stays compatible with both and stacks their gates into its channel-wise update.
- **[Point3R](point3r.md)**: A streaming baseline that strengthens memory recall via explicit 3D point pointers, at the cost of memory growth with points/views. Compared throughout the long-sequence and short-sequence tables.
- **[StreamVGGT](streamvggt.md)**: KV-cache causal-transformer streaming — long-range conditioning but linear memory growth and OOM on long streams (shown as OOM in the reconstruction tables).
- **[VGGT](vggt.md)** and **[Fast3R](fast3r.md)** / FastVGGT: Offline / large-window feed-forward transformers with global attention; strong quality but quadratic cost and reprocessing per new view, ill-suited to real-time long-sequence streaming.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: The pairwise feed-forward foundation that motivated this line; require costly global alignment beyond two views.
- **[Spann3R](spann3r.md)**, **[MonST3R](../dynamic/monst3r.md)**, **[π³ (pi3)](pi3.md)**: Additional baselines in the Sintel short-sequence comparison.
- **Fast Weight Programs / deep memory modules**: Mem3R's implicit memory follows the fast-weight-programmer lineage (Schmidhuber; linear transformers as fast weight programmers) and modern test-time-training memory work (Titans, LaCT, "Test-time training done right").

## 📚 Key Takeaways

1. **Hybrid memory beats a single compressed state for long streams.** Separating pose (implicit fast-weight MLP via TTT) from geometry (explicit gated token state) is the key architectural idea.
2. **Compact and accurate.** 644M vs CUT3R's 793M parameters (~19% fewer), 7% less GPU memory, matched fps — while improving long-sequence pose, depth, and reconstruction.
3. **Up to 39% lower ATE** at the 500-frame mark on TUM Dynamics when combined with TTT3R, versus base TTT3R.
4. **Composable, not competing.** Fully compatible with training-free CUT3R state-update strategies (TTT3R, TTSA3R), gaining further on long sequences.
5. **Scope is long-horizon streaming.** Gains are largest on 200–1000 frame sequences; short-sequence advantages are modest and full-attention offline models still lead some short-sequence metrics.

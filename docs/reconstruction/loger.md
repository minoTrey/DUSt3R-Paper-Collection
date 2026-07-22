# LoGeR: Long-Context Geometric Reconstruction with Hybrid Memory (arXiv preprint)

![loger — architecture](https://arxiv.org/html/2603.03269v2/x2.png)

_Overview of a single block of our hybrid memory module (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Junyi Zhang, Charles Herrmann, Junhwa Hur, Chen Sun, Ming-Hsuan Yang, Forrester Cole, Trevor Darrell, Deqing Sun
- **Institution**: Google DeepMind, UC Berkeley
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.03269) | [Project Page](https://LoGeR-project.github.io/)
- **Verification**: PREPRINT (2026-07-20)
- **TL;DR**: Chunk-wise feed-forward reconstruction where a bidirectional backbone handles each chunk and a two-part memory bridges chunks — sliding-window attention for lossless local alignment, Test-Time Training fast weights for compressed global context — trained on 128 frames and generalizing to thousands.

## 🎯 Key Contributions

1. **Hybrid memory module**: SWA (non-parametric, lossless, short-range) plus TTT (parametric, compressed, long-range), both linear in sequence length. The paper's framing is that a single memory strategy is fundamentally insufficient.
2. **Chunk-wise processing as a data strategy, not just a compute strategy**: Decomposing the sequence keeps local inference in-distribution relative to short-context training data, letting the method leverage strong bidirectional backbones (π³, VGGT).
3. **Long-context benchmark from VBR**: 7 sequences of 8,815–18,846 frames covering 1.4–11.5 km, repurposed for feed-forward long-context evaluation.
4. **Curriculum training** for the recurrent TTT layers, progressively shifting the model's reliance from SWA to the global TTT state.
5. **LoGeR\***: an optional purely feed-forward SE(3) alignment step over overlapping frames, applied at both training and inference.

## 🔧 Technical Details

### Architectural Trade-Offs

원논문 Table 1.

| Mechanism            | Compute Cost | Local Context | Global Context |
| -------------------- | ------------ | ------------- | -------------- |
| Full Attention       | O(N²)        | Lossless      | Lossless       |
| Sliding Window Attn. | O(N)         | Lossless      | Limited        |
| TTT / Linear Attn.   | O(N)         | Compressed    | Compressed     |
| **Ours (Hybrid)**    | O(N)         | Lossless      | Compressed     |

### Block Structure

A video is partitioned into M chunks with minimal overlap. Each residual block runs, in order:

1. **Per-frame attention** — self-attention within each frame's tokens.
2. **Sparse sliding-window attention** over `C^{m-1} ∪ C^m` — inserted at **only 4 layers** to stay compute-bound.
3. **Chunk-wise TTT layer** — apply then update:
   - Apply: `H̃ = H + f_{W^m}(LN(H))`
   - Update: `W^{m+1} = U(W^m; H)`
     with pre-norm inside TTT to stabilize long-horizon streaming.
4. **Chunk-wise bidirectional attention** within `C^m`.

Fast weights use a SwiGLU layer with the Muon optimizer for test-time updates; the chunk-level variant follows Large-Chunk Test-Time Training (LaCT). Prediction heads (pointmap decoder, camera-pose decoder) follow π³.

### Why Each Half Is Needed

- **TTT alone** is lossy — problematic for dense reconstruction where adjacent-frame geometric consistency is critical.
- **Deterministic stitching alone** (the Pi3-Chunk baseline) preserves local detail but has no long-range memory to prevent scale drift; the paper notes it relies on local overlapping frames for SIM(3) scale estimation, so scale errors accumulate over distance.

### Learning Objectives

Following π³: a scale-invariant local pointmap loss and an affine-invariant relative pose loss, neither requiring a reference view, plus a global pointmap loss on world-coordinate points.

```text
L = L_local + L_pose + λ_global · L_global
```

`L_local` aligns predicted local pointmaps with a single per-sequence scale s\* (as in MoGe) and normalizes by depth; `L_pose` combines a rotation term with a Huber translation term over supervised frame pairs; `L_global` compares world-coordinate points obtained by transforming local pointmaps with the predicted poses.

### LoGeR\* Alignment

For the overlapping frame k, a rigid SE(3) transform `A^m = T̃_k^{(m-1)} (T̂_k^{(m)})^{-1}` is applied to all frames of chunk m. Used as the final pose prediction for both training and inference.

### Training

- Data mixture: ARKitScenes, DL3DV, HyperSim, MegaDepth, ScanNet, ScanNet++, Spring, TartanAir, TartanAirV2, UnReal4K, Virtual KITTI 2, Waymo, and a subset of OmniWorld-Game — deliberately weighted toward large-scale-scene datasets.
- AdamW, **40k steps, batch size 32**; approximately **two days on 32 NVIDIA H100 GPUs followed by two days on 32 H200 GPUs**.
- Patchifier, frame attention, and chunk-wise bidirectional attention initialized from π³.
- **Curriculum**: (1) 48 frames in 4 chunks; (2) increase to 12 chunks at fixed sequence length; (3) scale context to 128 frames with up to 20 chunks on H200s. LoGeR\* initializes from the first-stage model and fine-tunes through the rest.
- All evaluation on a single NVIDIA A100 40GB.

### Inference-Time Details

Chunk size 64 with 3-frame overlap for the short-sequence experiments. TTT fast weights are **reset after every five windows** to avoid error accumulation within a fixed-size state, with the feed-forward pose alignment also applied at each reset. CUT3R and TTT3R baselines use the reset algorithm proposed in TTT3R.

## 📊 Results

### KITTI — ATE (m), sequences 00–05

원논문 Table 2. Sequence metadata: 00 (4542 frames, 3.7 km, loop), 01 (1101, 2.5 km, no loop), 02 (4661, 5.1 km, loop), 03 (801, 0.6 km, no loop), 04 (271, 0.4 km, no loop), 05 (2761, 2.2 km, loop). The first block is optimization-based, the second feed-forward.

| Method                     | 00     | 01     | 02     | 03     | 04    | 05     |
| -------------------------- | ------ | ------ | ------ | ------ | ----- | ------ |
| DROID-SLAM                 | 92.10  | 344.60 | 107.61 | 2.38   | 1.00  | 118.50 |
| DPV-SLAM                   | 112.80 | 11.50  | 123.53 | 2.50   | 0.81  | 57.80  |
| DPV-SLAM++                 | 8.30   | 11.86  | 39.64  | 2.50   | 0.78  | 5.74   |
| VGGT-Long                  | 8.67   | 121.17 | 32.08  | 6.12   | 4.23  | 8.31   |
| FastVGGT                   | OOM    | 639.39 | OOM    | 21.53  | 9.51  | OOM    |
| InfiniteVGGT               | 186.46 | 623.62 | 289.16 | 166.74 | 68.00 | 143.84 |
| CUT3R                      | 190.38 | 90.59  | 264.39 | 20.40  | 7.31  | 92.25  |
| TTT3R                      | 119.94 | 99.59  | 238.07 | 16.83  | 3.98  | 36.38  |
| Pi3-Chunk (their baseline) | 26.65  | 196.04 | 157.92 | 5.13   | 1.09  | 12.79  |
| LoGeR                      | 62.34  | 41.64  | 39.64  | 4.89   | 1.82  | 41.27  |
| LoGeR\*                    | 30.47  | 47.91  | 36.32  | 5.38   | 1.95  | 26.34  |

### KITTI — ATE (m), sequences 06–10 and average

원논문 Table 2, continued. Sequence metadata: 06 (1101, 1.2 km, loop), 07 (1101, 0.7 km, loop), 08 (4071, 3.2 km, no loop), 09 (1591, 1.7 km, loop), 10 (1201, 0.9 km, no loop).

| Method                     | 06     | 07    | 08     | 09     | 10     | Avg.      |
| -------------------------- | ------ | ----- | ------ | ------ | ------ | --------- |
| DROID-SLAM                 | 62.47  | 21.78 | 161.60 | 72.32  | 118.70 | 100.28    |
| DPV-SLAM                   | 54.86  | 18.77 | 110.49 | 76.66  | 13.65  | 53.03     |
| DPV-SLAM++                 | 11.60  | 1.52  | 110.90 | 76.70  | 13.70  | 25.75     |
| VGGT-Long                  | 5.34   | 4.63  | 53.10  | 41.99  | 18.37  | 27.64     |
| FastVGGT                   | 40.56  | 51.35 | OOM    | 201.54 | 196.22 | –         |
| InfiniteVGGT               | 117.57 | 85.33 | 221.56 | 215.41 | 156.92 | 206.78    |
| CUT3R                      | 67.54  | 22.48 | 145.08 | 67.42  | 40.00  | 91.62     |
| TTT3R                      | 47.20  | 11.62 | 107.33 | 86.96  | 33.58  | 72.86     |
| Pi3-Chunk (their baseline) | 27.66  | 5.94  | 61.26  | 56.31  | 21.96  | 52.07     |
| LoGeR                      | 13.99  | 16.24 | 26.46  | 22.71  | 8.84   | 25.44     |
| LoGeR\*                    | 6.60   | 5.55  | 24.41  | 10.12  | 10.11  | **18.65** |

The paper's own summary of this table: ATE is reduced "from 72.86 to 18.65" against TTT3R (the abstract states "over 74%"), and the average "surpasses even the strongest optimization-based method, VGGT-Long, by 32.5%". Note that on individual sequences LoGeR is **not** uniformly best — DPV-SLAM++ wins 00, 05, and 07, and Pi3-Chunk beats LoGeR on 00, 05, and 07 as well. The advantage concentrates on open-loop trajectories (01, 03, 04, 08, 10), which the paper attributes to mitigating accumulated drift without loop closure.

### VBR — Very Long Sequences (1k–19k frames)

Figure 4 plots ATE against the number of input views for InfiniteVGGT, VGGT-Long (with and without loop closure), VGGT-SLAM, CUT3R, TTT3R, Pi3-Chunk, LoGeR and LoGeR\*. **The figure prints only one number — a 55.2% annotation** — and no per-method values; they are not reproduced here. The paper's stated claim is a **55.2% relative improvement** over prior methods on this benchmark.

The qualitative finding reported alongside it: Pi3-Chunk is slightly better at ~1k frames, but LoGeR's advantage grows with sequence length because Pi3-Chunk's SIM(3) scale estimation from local overlaps accumulates error exponentially over distance, while TTT anchors global scale — with LoGeR reported to maintain scale consistency up to 20k frames.

### 7-Scenes Reconstruction and ScanNet / TUM-Dynamics Pose

Figures 6 and 9 plot Chamfer Distance (7-Scenes, 50–500 views) and ATE (ScanNet and TUM-Dynamics, 50–1k views) against sequence length for VGGT (offline), StreamVGGT, CUT3R, Point3R, TTT3R, Pi3-Chunk, LoGeR and LoGeR\*. **These are plots without printed per-method values.** The only printed figures are the relative-gain annotations the paper reports: **69.2%** on 7-Scenes reconstruction, and **80.0%** and **66.1%** on ScanNet and TUM-Dynamics pose respectively.

Figure 8's caption records an honest qualitative caveat: Pi3-Chunk yields "slightly better pose metrics on small-scale TUM sequences", with LoGeR's advantage being visual reconstruction quality there.

### Ablations — ATE ↓ on ScanNet (subset) and TUM

원논문 Table 3. Ablation models are trained with fewer frames than the final model.

| Method                 | ScanNet 500f | ScanNet 1000f | TUM 500f  | TUM 1000f |
| ---------------------- | ------------ | ------------- | --------- | --------- |
| LoGeR                  | 0.087        | 0.107         | 0.033     | 0.050     |
| w/o TTT                | 0.108        | 0.162         | 0.043     | 0.079     |
| w/o SWA                | 0.115        | 0.143         | 0.039     | 0.053     |
| All datasets           | 0.087        | 0.107         | 0.033     | 0.050     |
| w/o 5 large datasets   | 0.102        | 0.156         | 0.050     | 0.072     |
| LoGeR                  | 0.087        | 0.107         | 0.033     | 0.050     |
| w/o curriculum         | 0.098        | 0.133         | 0.049     | 0.062     |
| LoGeR\*                | **0.070**    | **0.080**     | 0.031     | **0.036** |
| LoGeR\* w/o curriculum | 0.078        | 0.093         | **0.029** | 0.040     |

Three things this table shows cleanly: removing either memory component hurts, and the damage grows with sequence length (TTT removal costs more at 1000f than 500f); excluding the five large-scale datasets (TartanAir, TartanAirV2, Waymo, Virtual KITTI 2, OmniWorld-Game) degrades results substantially; and the curriculum helps everywhere except one cell — LoGeR\* on TUM at 500 frames, where the non-curriculum variant is marginally better (0.029 vs 0.031).

Fig. 10 disables SWA or TTT at inference on a trained model; it is a qualitative figure showing local misalignment artifacts without SWA and severe trajectory drift without TTT, with no printed values.

## 💡 Insights & Impact

### Two Walls, Not One

The paper's diagnosis is unusually explicit. The **context wall** is architectural: bidirectional attention is essential for learning geometric priors but its quadratic cost confines it to short windows. The **data wall** is empirical: models are trained on short-context "bubbles" of dozens to a hundred frames, so even architecture fixes that solve memory (FastVGGT) still fail to generalize to large-scale scenes. Fig. 3 makes the point — FastVGGT processes more frames than VGGT but fails completely on VBR.

Chunk-wise processing is the answer to the data wall specifically: it keeps every local inference inside the distribution the backbone was trained on.

### Why Hybrid Memory Rather Than a Better Single Memory

Table 1 is the argument in one glance. SWA gives lossless local context but limited global reach; TTT/linear attention gives global reach but compresses everything, including the fine geometric detail that adjacent-chunk alignment needs. Language-model hybrids typically add full global attention to recover the lossless global column, but the paper notes the token density of dense vision prediction makes that prohibitive. So LoGeR accepts a compressed global context and insists on a lossless local one.

### The Honest Limitations

The authors state them directly:

1. **TTT fast weights do not generalize beyond the number of chunks they were trained with**, so exceeding the training context on sequences beyond ~1,000 frames causes error accumulation and drift. Periodic state resets are the current mitigation, and they sacrifice long-term context.
2. **Data availability remains the bottleneck** — the data wall is not solved, only worked around.

### Reproducibility Note on the Figures

A large share of this paper's quantitative story (VBR, 7-Scenes, ScanNet, TUM-Dynamics) lives in line plots rather than tables. Only KITTI (Table 2) and the ablations (Table 3) provide printed numbers. The relative-gain percentages quoted above are the paper's own annotations, not values derived from reading the curves.

## 🔗 Related Work

- [Pi3](./pi3.md) — supplies the backbone initialization, the loss formulation, and the prediction heads; also the basis of the Pi3-Chunk baseline the authors construct.
- [TTT3R](./ttt3r.md) — the closest prior use of test-time training here, criticized for being frame-wise and therefore unable to exploit multi-frame bidirectional reasoning; the strongest recurrent baseline on KITTI.
- [FastVGGT](./fastvggt.md) — the inference-time efficiency approach that solves memory but, per Fig. 3, hits the data wall on large-scale scenes.
- [CUT3R](../dynamic/cut3r.md) — the recurrent single-hidden-state design whose lossy compression motivates the SWA half of the hybrid.
- [VGGT](./vggt.md) — the bidirectional backbone family LoGeR builds chunks on.
- [Point3R](./point3r.md), [StreamVGGT](./streamvggt.md) — explicit-state and causal-attention baselines in the short-sequence evaluation.
- [MoGe](./moge.md) — source of the per-sequence scale alignment used in the local pointmap loss.
- [DUSt3R](../foundation/dust3r.md), [MonST3R](../dynamic/monst3r.md) — the geometric foundation model lineage the introduction traces.

## 📚 Key Takeaways

1. **One memory mechanism cannot serve both scales.** Lossless local transfer and compressed global anchoring are different jobs; SWA and TTT each do one, at linear cost.
2. **Chunking is a data-distribution trick as much as a compute trick.** It lets a model trained on 128 frames run 19k-frame sequences by never asking the backbone to reason outside its training regime.
3. **Global scale drift is the failure mode that matters at kilometre scale.** Overlap-based SIM(3) stitching accumulates scale error; a parametric global memory does not.
4. **Curriculum matters for recurrent layers.** Progressively increasing chunk count forces reliance to shift from SWA to TTT, and removing it costs measurable ATE.
5. **The result is real but uneven.** Best average KITTI ATE among feed-forward methods (18.65 for LoGeR\*), yet DPV-SLAM++ still wins several loop-containing sequences, and periodic state resets remain necessary beyond the training context length.

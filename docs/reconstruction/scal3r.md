# Scal3R: Scalable Test-Time Training for Large-Scale 3D Reconstruction (CVPR 2026)

![scal3r — architecture](https://arxiv.org/html/2604.08542v1/x2.png)

_Overview of Scal3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Tao Xie, Peishan Yang, Yudong Jin, Yingfeng Cai, Wei Yin, Weiqiang Ren, Qian Zhang, Wei Hua, Sida Peng, Xiaoyang Guo, Xiaowei Zhou
- **Institution**: Zhejiang University, Horizon Robotics, Zhejiang Lab
- **Venue**: CVPR 2026
- **Award**: Highlight
- **Links**: [Paper](https://arxiv.org/abs/2604.08542) | [Project Page](https://zju3dv.github.io/scal3r)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Adds test-time-adapted lightweight sub-networks inside VGGT's attention stack as a Global Context Memory, plus a cross-GPU synchronization mechanism, so chunk-wise processing of kilometer-scale RGB sequences no longer loses long-range context.

## 🎯 Key Contributions

1. **Scal3R**, a framework for reconstructing high-quality kilometer-scale 3D scenes from RGB-only sequences.
2. **A neural global context representation plus a context aggregation mechanism** that jointly compresses, retains, and shares long-term information across an entire sequence.
3. **State-of-the-art accuracy and global consistency** on large-scale benchmarks, validated on Virtual KITTI, KITTI Odometry, Oxford Spires, and ETH3D.

## 🔧 Technical Details

### The problem with existing scaling strategies

- **FastVGGT** reduces attention redundancy via token merging, but aggressive token compression discards fine-grained spatial cues and weakens long-range dependencies.
- **VGGT-Long** splits the sequence into overlapping chunks and aligns them afterwards. This dodges the quadratic cost, but each chunk is processed _without global context_, so the alignment is highly sensitive to local prediction errors.
- **TTT3R** casts memory update as test-time learning, but still relies on a fixed-size token set.

### Global Context Memory (GCM)

Scal3R attaches **4 GCM modules** after global attention layers. Each contains a query-key-value projection, a compact MLP acting as **Adaptive Memory Units (AMUs)**, and an output projection.

Inspired by LaCT, all tokens `X_k ∈ R^{M×d}` in a chunk are treated as a **single update unit**, which improves parallelism and GPU utilization relative to fine-grained TTT updates:

```text
W ← W − ∇_W Σ_i η_i · L(f_W(k_i), v_i),    L(f_W(K), V) = Σ_i −f_W(k_i)ᵀ v_i
```

with `η_i` a token-wise learning rate predicted from the input tokens. After the update, the AMUs transform the query tokens to produce `f_W(Q)`.

Integration into VGGT's alternating attention is gated:

```text
gate(GCM, X_k^i; α) = α ⊗ GCM(X_k^i) + X_k^i
X̄_k^i = gate(GCM, gattn(fattn(X_k^i)); α) + X_k^i
```

where `α ∈ R^d` is a learnable vector balancing the GCM output against the original tokens.

### Global Context Synchronization (GCS)

GCM alone captures only _intra-chunk_ context. GCS frames the distribution of chunks across GPUs as context parallelism: each GPU computes its local AMU updates, then the gradients are **summed and broadcast** across all GPUs via PyTorch all-reduce primitives:

```text
g = ∇_W Σ_{j=1..K} Σ_{i=1..M} η_i L_i = Σ_{j=1..K} ∇_W Σ_{i=1..M} η_i L_i
```

The aggregated gradient updates the AMUs on every GPU, so each local chunk is enriched with sequence-wide observations.

### Training and Inference

- Jointly trained end-to-end with the VGGT backbone. AdamW, peak LR 1e-4 for GCM and 1e-5 for the backbone, cosine decay with 2k-iteration linear warm-up, gradient clipping at max norm 1.0.
- **60k iterations on 32 A800 GPUs, about 3 days.** For length generalization, the 32 GPUs are randomly partitioned into groups each iteration, with GCS applied only within a group — yielding effective sequence lengths spanning 1 to 32 chunks during training.
- 19 training datasets spanning indoor/outdoor, synthetic/real, and multiple scene scales (Co3Dv2, BlendedMVS, DL3DV, MegaDepth, WildRGB, ScanNet++, HyperSim, Mapillary, Replica, MVS-Synth, Virtual KITTI, Aria Synthetic Environments, Aria Digital Twin, Taskonomy, Tartanair, Mapfree, SceneNet RGB-D, MatrixCity).
- Loss follows VGGT: `L = λ L_cam + L_dpt + L_xyz`.
- At inference, chunks are distributed across GPUs; results are aligned and fused following VGGT-Long, using overlapping regions to compute similarity transformations. For trajectories with revisits, retrieval-based loop candidate discovery followed by pose-graph refinement reduces global drift. The method can also run on a single GPU by processing chunks sequentially, at increased inference time.

## 📊 Results

### Camera Pose Accuracy

원논문 Table 1. RRE in °/100m, RTE in m/100m, ATE in m. Failed scenes are assigned the worst valid score when computing dataset averages. Methods marked † require known camera intrinsics.

| Method      | VKITTI2 RRE ↓ | VKITTI2 RTE ↓ | VKITTI2 ATE ↓ | KITTI RRE ↓ | KITTI RTE ↓ | KITTI ATE ↓ | Oxford RRE ↓ | Oxford RTE ↓ | Oxford ATE ↓ |
| ----------- | ------------- | ------------- | ------------- | ----------- | ----------- | ----------- | ------------ | ------------ | ------------ |
| MASt3R-SLAM | 15.81         | 70.48         | 78.33         | 22.42       | 67.72       | 191.71      | 59.67        | 29.82        | 29.22        |
| VGGT-SLAM   | 12.92         | 21.27         | 17.18         | 33.27       | 78.95       | 214.88      | 55.60        | 32.14        | 26.85        |
| StreamVGGT  | 13.47         | 58.07         | 68.97         | 24.06       | 84.46       | 226.15      | 71.28        | 37.14        | 34.35        |
| STream3R    | 13.46         | 76.06         | 70.87         | 24.06       | 81.63       | 227.77      | 71.29        | 36.65        | 34.65        |
| CUT3R       | 7.93          | 40.42         | 50.75         | 24.24       | 73.65       | 209.78      | 54.69        | 32.15        | 28.01        |
| TTT3R       | 5.88          | 16.34         | 23.49         | 21.90       | 68.55       | 177.73      | 62.68        | 35.51        | 31.57        |
| FastVGGT    | 3.13          | 38.64         | 21.83         | 22.47       | 69.58       | 206.69      | 65.35        | 37.55        | 31.18        |
| VGGT-Long   | 0.71          | 2.01          | 1.03          | 1.71        | 9.67        | 25.94       | 30.91        | 20.79        | 15.46        |
| COLMAP      | 2.53          | 7.63          | 9.09          | 0.62        | 15.88       | 37.79       | 0.32         | 0.24         | 0.15         |
| MASt3R-SfM  | 18.28         | 23.79         | 40.57         | 25.43       | 53.70       | 171.28      | 25.83        | 28.60        | 25.83        |
| DROID-SLAM† | 26.90         | 41.41         | 2.47          | 25.38       | 58.37       | 50.71       | 23.97        | 45.11        | 23.97        |
| DPVO++†     | 0.07          | 0.39          | 0.48          | 0.23        | 15.17       | 52.69       | 29.17        | 30.71        | 29.17        |
| **Ours**    | 0.41          | 0.78          | 0.85          | 0.97        | 4.61        | 14.55       | 7.87         | 6.55         | 4.45         |

**Where Scal3R does not win.** Among the feed-forward and streaming baselines Scal3R leads everywhere. But COLMAP is far more accurate on Oxford Spires (ATE 0.15 vs 4.45), and DPVO++ — which assumes known intrinsics — beats Scal3R on all three VKITTI2 metrics and on KITTI RRE. The paper acknowledges this directly: classical SfM stays competitive when feature matching and global optimization are well conditioned, but degrades on longer, larger-scale video and is extremely slow.

Sequence scales: VKITTI2 223–837 frames / 52–711 m; KITTI 271–4661 frames / 394–5067 m; Oxford Spires 351–787 frames / 280–773 m.

### Resource Comparison

원논문 Table 1, last three columns. Measured on KITTI sequences 03, 04, and 10 (avg. 758 frames). All methods run on a single RTX 4090 except FastVGGT, which requires an A800.

| Method      | Memory ↓ | Time ↓  | FPS ↑ |
| ----------- | -------- | ------- | ----- |
| MASt3R-SLAM | 6.74     | 99.30   | 7.37  |
| VGGT-SLAM   | 10.67    | 39.72   | 19.85 |
| StreamVGGT  | 6.66     | 32.61   | 23.14 |
| STream3R    | 4.70     | 111.23  | 8.19  |
| CUT3R       | 6.50     | 22.96   | 32.87 |
| TTT3R       | 4.59     | 23.65   | 31.95 |
| FastVGGT    | 22.58    | 48.13   | 18.22 |
| VGGT-Long   | 11.77    | 168.83  | 4.80  |
| COLMAP      | 0.00     | 6614.73 | 0.17  |
| MASt3R-SfM  | 8.04     | 2766.76 | 0.27  |
| DROID-SLAM† | 10.29    | 56.14   | 13.58 |
| DPVO++†     | 0.89     | 20.71   | 35.35 |
| **Ours**    | 10.32    | 300.76  | 2.53  |

Scal3R is the slowest learned method in this table at 2.53 FPS. The paper's own framing is that lightweight online systems such as DPVO++ and CUT3R achieve higher throughput, while Scal3R provides substantially stronger accuracy on long sequences — and that **COLMAP is over 20× slower than Scal3R**, the one speedup ratio the paper states explicitly.

### 3D Reconstruction Accuracy

원논문 Table 2. Chamfer Distance and F1 score on point clouds reconstructed from predicted poses and depth maps, after Umeyama alignment to ground truth. 11 / 6 / 50 scenes for ETH3D / Oxford Spires / VKITTI2.

| Method      | ETH3D CD ↓ | ETH3D F1 ↑ | Oxford Spires CD ↓ | Oxford Spires F1 ↑ | VKITTI2 CD ↓ | VKITTI2 F1 ↑ |
| ----------- | ---------- | ---------- | ------------------ | ------------------ | ------------ | ------------ |
| MASt3R-SLAM | 0.89       | 0.31       | 7.78               | 0.53               | 17.08        | 0.33         |
| VGGT-SLAM   | 0.78       | 0.72       | 10.16              | 0.22               | 9.74         | 0.57         |
| StreamVGGT  | 1.86       | 0.14       | 12.23              | 0.25               | 20.45        | 0.35         |
| STream3R    | 1.81       | 0.14       | 12.20              | 0.25               | 18.77        | 0.36         |
| CUT3R       | 0.41       | 0.60       | 6.93               | 0.45               | 5.67         | 0.39         |
| TTT3R       | 0.43       | 0.59       | 9.03               | 0.31               | 3.49         | 0.49         |
| FastVGGT    | 0.50       | 0.70       | 2.76               | 0.76               | 1.73         | 0.67         |
| VGGT-Long   | 0.24       | 0.84       | 3.41               | 0.80               | 1.78         | 0.70         |
| **Ours**    | **0.11**   | **0.91**   | **0.96**           | **0.96**           | **0.40**     | **0.91**     |

This is the cleanest result in the paper: Scal3R is best on all six columns, and by large margins on Oxford Spires (CD 0.96 vs the next-best 2.76) and VKITTI2 (0.40 vs 1.73). ETH3D also shows the method transfers to shorter indoor sequences.

### Ablations

원논문 Table 3. The two blocks are **not directly comparable** — they use different settings. All ablation models are trained and evaluated on a subset of the training datasets.

| State Size | RRE ↓ | RTE ↓ | ATE ↓ |
| ---------- | ----- | ----- | ----- |
| 1M size    | 1.01  | 1.01  | 0.99  |
| 2M size    | 0.95  | 0.91  | 0.93  |
| 4M size    | 0.87  | 0.84  | 0.85  |

| Global Context | RRE ↓ | RTE ↓ | ATE ↓ |
| -------------- | ----- | ----- | ----- |
| w/o GCM        | 1.30  | 7.03  | 19.00 |
| w/o GCS        | 1.28  | 7.01  | 15.80 |
| Full model     | 1.17  | 5.99  | 13.70 |

Both ablations degrade ATE relative to the full model, with the larger drop for `w/o GCM` — showing that GCM carries the primary long-range context while GCS propagates it across chunks. Growing the sub-network state from 1M to 4M improves all three metrics monotonically.

### Qualitative Long-Sequence Results

원논문 Figure 3 reports per-sequence trajectory errors. On KITTI Odometry 00 (4542 frames, 3742 m): Scal3R ATE 4.298 / RTE 1.898 / RRE 0.639; VGGT-Long 8.637 / 4.717 / 1.416; STream3R 191.0 / 62.27 / 27.95; CUT3R 185.9 / 69.45 / 15.20; TTT3R 190.9 / 58.14 / 17.19. FastVGGT runs out of memory on this sequence.

On Oxford kebel 04 (701 frames, 773 m): Scal3R 2.448 / 2.078 / 2.426 versus VGGT-Long 13.20 / 10.19 / 14.14 and FastVGGT 39.93 / 27.03 / 45.20.

## 💡 Insights & Impact

**The core diagnosis.** Chunk-wise processing solves the quadratic-cost problem but creates a new one: each chunk is blind to the rest of the sequence, so local errors have nothing to correct them and the downstream alignment inherits them. Scal3R's answer is not a better aligner but a _shared memory_ that makes every chunk's local prediction better in the first place.

**Why fixed-size state is not enough.** Modern linear-attention RNNs compress all history into a finite hidden state, which degrades on long sequences. TTT extends the recurrent state to an online-adapted nonlinear network, substantially increasing capacity — and the state-size ablation confirms the capacity is the binding constraint, with 4M outperforming 1M on every metric.

**Large chunks are the practical enabler.** Existing TTT approaches struggle to scale to long contexts because frequent fine-grained updates hinder throughput and waste GPU utilization. Treating an entire chunk as one update unit (following LaCT) is what makes this trainable at all.

**Context parallelism as a design pattern.** Summing AMU gradients across GPUs and broadcasting the result turns the multi-GPU chunk distribution into a _sequence-wide_ memory, at all-reduce cost. The same primitive works in training and inference, which is why the model can be trained at variable effective sequence lengths.

**The honest trade-off.** Scal3R buys accuracy with throughput: 2.53 FPS, the lowest of any learned method compared. For kilometer-scale offline mapping this is an acceptable price; for real-time robotics it is not, and the paper positions CUT3R/DPVO++ as the fast-but-less-accurate alternatives.

## 🔗 Related Work

- [VGGT](vggt.md) — the backbone Scal3R extends; its quadratic attention is the scalability constraint being addressed
- [FastVGGT](fastvggt.md) — token-merging acceleration, criticized here for discarding fine-grained spatial cues
- [TTT3R](ttt3r.md) — the closest prior test-time-training approach, limited by a fixed-size token set
- [CUT3R](../dynamic/cut3r.md) — persistent-state online reconstruction, a memory-mechanism baseline
- [STream3R](stream3r.md) / [StreamVGGT](streamvggt.md) — causal-transformer streaming baselines
- [VGGT-SLAM](vggt-slam.md) / [MASt3R-SLAM](mast3r-slam.md) — learning-based SLAM baselines
- [MASt3R-SfM](../foundation/mast3r-sfm.md) — SfM baseline
- [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) — the origins of feed-forward pointmap regression

## 📚 Key Takeaways

1. **Chunking without context is the bottleneck**, not chunking itself. Scal3R keeps VGGT-Long's divide-and-conquer inference but gives every chunk a view of the whole sequence.
2. **Test-time-adapted sub-networks beat fixed-size hidden states** for long-range memory — and bigger states keep helping, from 1M to 4M.
3. **All-reduce the fast-weight gradients.** Global Context Synchronization turns multi-GPU chunk parallelism into a genuine sequence-level memory at negligible communication cost.
4. **Geometry is where the gains are clearest**: best CD and F1 on all three reconstruction benchmarks, with Oxford Spires CD dropping from 2.76 to 0.96.
5. **Accuracy costs throughput.** At 2.53 FPS Scal3R is slower than every learned baseline it beats; the paper's one explicit ratio is that COLMAP is over 20× slower still.

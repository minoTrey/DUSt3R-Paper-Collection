# Anchor3R: Streaming 3D Reconstruction with Transient Anchors for Long-Horizon Visual Mapping (arXiv preprint)

## 📋 Overview

- **Authors**: Peilin Tao, Chong Cheng, Yuansen Du, Caiwei Song, Zhengqing Chen, Xiaoyang Guo, Wei Yin, Weiqiang Ren, Qian Zhang, Hainan Cui, Shuhan Shen
- **Institution**: CASIA, UCAS, Horizon Robotics, HKUST(GZ)
- **Venue**: arXiv preprint (2026-06)
- **Note**: The venue could not be confirmed from any primary source and should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2606.05035)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: Treats streaming reconstruction as current-centric local measurement prediction — each step predicts window-relative poses anchored at the current frame — then accumulates them into a dense relative-pose graph that motion averaging turns into a globally consistent trajectory.

## 🎯 Key Contributions

1. **Current-centric dense relative-pose prediction**: streaming feed-forward reconstruction reformulated as window-relative predictions anchored at the current frame, replacing persistent global-gauge regression.
2. **An image-only cached pose-query Transformer** that separates reusable frame evidence from transient current-gauge pose reasoning, enabling bounded-memory streaming without propagating stale pose states.
3. **A motion graph** accumulating dense relative-pose measurements, supporting online pose updates and loop-aware motion averaging for global drift redistribution.

## 🔧 Technical Details

### The fixed-gauge problem

Existing streaming variants predict poses in a coordinate system tied to the first frame or a persistent scene memory. The paper's argument is that this forces the model to propagate a long-lived coordinate system through hidden states, entangling local geometric reasoning with historical gauge maintenance. Two consequences follow: attention sinks around early anchors, and accumulated uncertainty and scale error. A third, structural one: the accumulated outputs form a _trajectory_ rather than a graph of independent measurements, making global error redistribution difficult.

### Current-Centric Formulation

At time `t` with an active sliding window `W_t = {k, …, t}`, `k = max(1, t − W + 1)`, the network predicts a relative pose `T̂_{i←t} ∈ SE(3)` from the current frame to each frame `i ∈ W_t`. The training target is `T_{i←t} = T_i T_t^{-1}` with `T_{t←t} = I` — depending only on relative geometry within the window, not on an increasingly distant global origin. In parallel a current-frame local pointmap `X̂_t^local` is predicted.

Each step emits graph edges `E_t = {(i, t, T̂_{i←t}) | i ∈ W_t, i < t}`. As the window slides, later anchors add redundant edges for the same frames, turning local window predictions into a dense relative-pose measurement graph.

### Sliding-Window Pose-Query Transformer

A DINOv2 encoder extracts patch tokens `P⁰_t`. For each frame in the window, a pose-query group `Q⁰_{t,i}` of one pose token plus `X` register tokens is instantiated — the current frame uses a learnable reference template `Q_ref`, source frames use `Q_src`. This asymmetric initialization defines the current frame as the local reference.

The block alternates:

1. **Decoupled frame attention** updates only the current image tokens and caches their keys/values; each pose-query group reads from its corresponding frame representation, reusing historical image states from the cache. Frame-level visual evidence is computed **once** and stays independent of future pose-query instantiations.
2. **Current-centric window attention** jointly updates current patch tokens and all pose-query groups, over cached image-side states from `W_t \ {t}`.

The key design decision: **cache only image-side key/value states, discard pose-query states after each local prediction**. Pose-query tokens are tied to one transient gauge, so caching them would mix stale coordinate hypotheses across anchors. Image-conditioned patch states store gauge-agnostic appearance, geometry, and matching cues, and can be safely cached without explicit refresh — which is how Anchor3R achieves bounded-memory streaming.

### Motion Graph and Pose Recovery

For each edge `(i, t)` the network predicts `(R̂_{i←t}, t̂_{i←t})` with `v̂_{i,t} = R̂_{i←t}^T t̂_{i←t} ≈ c_t − c_i`. Rather than composing poses along a spanning tree, global poses are recovered by averaging over the full graph, fixing the first-frame gauge at `R̂_1 = I`, `ĉ_1 = 0`.

- **Online**: the current pose is estimated from the `|W_t| − 1` newly predicted relative poses and previously estimated global poses, taking the **Lie-algebra median** of candidate rotations and the coordinate-wise median of candidate centers.
- **Offline**: joint optimization of all rotations and centers, with the rotation objective solved by IRLS in the Lie algebra and the translation objective by ADMM. Loop-closure keyframes are reinserted into the active window as transient anchors to add long-range edges.

### Training

Multi-task objective `L = λ_cam L_cam + L_pmap` following VGGT. The camera loss supervises relative rotation and translation within each window; the local point-map loss combines confidence-weighted reconstruction with gradient regularization. The scale factor `s*` is estimated following π³ and applied to **both** relative camera translations and local point maps, encouraging scale consistency within and across overlapping windows.

- Initialized from VGGT, retaining its 24-layer alternating-attention backbone, ≈1.2B parameters.
- Fixed active window of **10 frames** for both training and inference; each pose-query group has one pose token and **31 register tokens**.
- AdamW with cosine decay, peak LR 1e-4, 2k warm-up steps. Images resized so the longer side is at most 518 px, with aspect-ratio jittering.
- **80k iterations on 32 NVIDIA A800 GPUs, approximately 12 days.**
- 16 training datasets (WildRGB, ScanNet, HyperSim, Mapillary, Replica, Mapfree, TartanAir, MVS-Synth, Virtual KITTI, Aria Synthetic Environments, Spring, Waymo Open, BlendedMVS, Co3Dv2, MegaDepth, DL3DV). Unordered data gets pose-guided overlapping sequence construction; video data gets random interval sampling and block shuffling.

## 📊 Results

All main evaluation sequences are excluded from training; for Waymo, a held-out subset of the official training split is used. Trajectories are aligned to ground truth with a similarity transformation. Failed cases are marked `*` in the paper and excluded from averages.

**Anchor3R-Online** follows a strict one-pass streaming protocol — temporal order, incremental pose updates, no loop detection or keyframe reinsertion. **Anchor3R-Offline** augments the accumulated graph with loop-closure measurements (keyframes every 5 frames, top-3 retrieval with NetVLAD, temporally separated matches reinserted as transient anchors) and performs motion averaging.

### KITTI Odometry

원논문 Table 1, ATE ↓. Sequence 00 is 4542 frames / 3.7 km; 02 is 4661 frames / 5.1 km; 08 is 4071 frames / 3.2 km.

| Method           | 00     | 01     | 02     | 05     | 08     | 09     | 10     | Avg.   |
| ---------------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| FastVGGT         | \*     | 705.39 | \*     | 157.74 | \*     | 190.10 | 194.75 | 189.29 |
| MASt3R-SLAM      | \*     | 530.37 | \*     | 159.43 | \*     | \*     | \*     | 177.93 |
| VGGT-SLAM        | \*     | 607.16 | \*     | \*     | \*     | \*     | \*     | 263.37 |
| VGGT-Long        | 8.64   | 21.20  | 52.72  | 9.88   | 72.98  | 31.84  | 27.71  | 25.94  |
| CUT3R            | 185.89 | 651.52 | 296.98 | 155.61 | 238.39 | 205.94 | 193.39 | 209.78 |
| TTT3R            | 190.93 | 546.84 | 218.77 | 153.12 | 180.57 | 211.01 | 133.00 | 177.73 |
| STream3R         | 190.98 | 681.95 | 301.40 | 159.85 | 261.15 | 216.31 | 207.49 | 227.77 |
| StreamVGGT       | 191.93 | 653.06 | 303.35 | 160.46 | 263.95 | 216.69 | 209.80 | 226.15 |
| LongStream       | 92.55  | 46.01  | 134.70 | 84.69  | 62.07  | 85.61  | 21.48  | 51.90  |
| Anchor3R-Online  | 44.18  | 48.43  | 149.61 | 62.63  | 52.12  | 55.23  | 8.57   | 40.89  |
| Anchor3R-Offline | 19.68  | 48.62  | 75.75  | 7.56   | 49.34  | 49.02  | 8.00   | 25.03  |

원논문 Table 1, remaining sequences:

| Method           | 03     | 04     | 06     | 07    |
| ---------------- | ------ | ------ | ------ | ----- |
| FastVGGT         | 62.38  | 10.27  | 124.43 | 69.27 |
| MASt3R-SLAM      | 18.87  | 88.98  | 92.00  | \*    |
| VGGT-SLAM        | 169.83 | 13.12  | \*     | \*    |
| VGGT-Long        | 8.78   | 4.20   | 4.67   | 2.66  |
| CUT3R            | 148.06 | 22.17  | 132.54 | 77.03 |
| TTT3R            | 105.28 | 11.62  | 132.94 | 70.95 |
| STream3R         | 158.25 | 102.73 | 135.03 | 90.37 |
| StreamVGGT       | 157.50 | 108.24 | 133.71 | 89.00 |
| LongStream       | 3.81   | 1.95   | 23.12  | 14.93 |
| Anchor3R-Online  | 4.39   | 1.99   | 12.12  | 10.39 |
| Anchor3R-Offline | 4.22   | 1.90   | 6.36   | 7.63  |

**Anchor3R-Offline's average of 25.03 edges out VGGT-Long's 25.94**, but VGGT-Long is clearly better on several individual sequences (00: 8.64 vs 19.68; 02: 52.72 vs 75.75; 06: 4.67 vs 6.36; 07: 2.66 vs 7.63). Among _streaming_ methods the improvement is large and unambiguous: Anchor3R-Online's 40.89 versus LongStream's 51.90 and the 177–228 range of CUT3R, TTT3R, STream3R, and StreamVGGT.

### VBR

원논문 Table 2, ATE ↓. These are the longest sequences in the paper — ciampino_train1 is 18846 frames / 5.20 km, campus_train0 is 12042 frames / 2.73 km.

| Method           | campus_train0 | campus_train1 | ciampino_train1 | colosseo_train0 | diag_train0 | pincio_train0 | spagna_train0 | Avg.  |
| ---------------- | ------------- | ------------- | --------------- | --------------- | ----------- | ------------- | ------------- | ----- |
| VGGT-SLAM        | 93.51         | 71.74         | 124.10          | 101.00          | 33.64       | 66.42         | 57.00         | 78.20 |
| VGGT-Long        | 118.59        | 98.21         | 172.13          | 39.56           | 30.80       | 53.44         | 50.27         | 80.43 |
| Pi3-Chunk        | 78.50         | 65.77         | 111.72          | 77.09           | 23.81       | 41.99         | 44.76         | 63.38 |
| InfiniteVGGT     | 123.65        | 100.00        | \*              | 83.91           | 31.58       | 70.73         | 56.25         | 91.60 |
| LongStream       | 100.57        | 105.55        | 131.78          | 72.52           | 32.35       | 43.47         | 59.31         | 77.93 |
| Anchor3R-Online  | 86.63         | 82.16         | 168.25          | 61.43           | 29.38       | 51.34         | 54.34         | 76.21 |
| Anchor3R-Offline | 5.13          | 3.52          | 78.64           | 17.25           | 5.35        | 15.56         | 11.76         | 19.60 |

Anchor3R-Offline ranks first on all seven sequences with an average ATE of 19.60 against the next-best 63.38 — a 3× reduction. Anchor3R-Online is only marginally ahead of LongStream (76.21 vs 77.93) and worse than Pi3-Chunk (63.38), so on VBR the loop-aware graph refinement is doing most of the work.

### TUM, Oxford Spires, Waymo

원논문 Table 3, ATE ↓.

| Method          | TUM ↓ | Oxford Spires ↓ | Waymo ↓ |
| --------------- | ----- | --------------- | ------- |
| FastVGGT        | 0.418 | 36.577          | 1.281   |
| MASt3R-SLAM     | 0.082 | 37.728          | 7.625   |
| VGGT-SLAM       | 0.123 | 31.003          | 7.431   |
| CUT3R           | 0.542 | 32.440          | 9.396   |
| TTT3R           | 0.308 | 36.214          | 3.486   |
| STream3R        | 0.633 | 37.569          | 42.203  |
| StreamVGGT      | 0.627 | 37.255          | 45.101  |
| LongStream      | 0.076 | 19.815          | 0.737   |
| Anchor3R-Online | 0.091 | 17.661          | 0.425   |

Anchor3R-Online leads on Oxford Spires and Waymo but is behind LongStream (0.076) and MASt3R-SLAM (0.082) on TUM's short indoor trajectories.

### 3D Reconstruction

원논문 Table 4. Chamfer Distance and F1 at threshold 0.25, on point clouds reconstructed from predicted trajectory and depth/point-map outputs, similarity-aligned to ground truth.

| Method          | 7Scenes CD ↓ | 7Scenes F1@0.25 ↑ | TUM CD ↓ | TUM F1@0.25 ↑ |
| --------------- | ------------ | ----------------- | -------- | ------------- |
| FastVGGT        | 6.373        | 0.710             | 0.104    | 0.926         |
| MASt3R-SLAM     | 5.987        | 0.691             | 0.057    | 0.954         |
| VGGT-SLAM       | 6.306        | 0.696             | 1.993    | 0.633         |
| CUT3R           | 6.281        | 0.274             | 0.474    | 0.533         |
| TTT3R           | 6.231        | 0.260             | 0.249    | 0.792         |
| STream3R        | 6.353        | 0.479             | 1.126    | 0.444         |
| StreamVGGT      | 6.630        | 0.483             | 0.680    | 0.402         |
| LongStream      | 2.260        | 0.641             | 0.225    | 0.673         |
| Anchor3R-Online | 1.848        | 0.707             | 0.108    | 0.933         |

Anchor3R-Online has the best 7Scenes CD and second-best F1 (FastVGGT's 0.710 leads). On TUM, MASt3R-SLAM is best on both metrics — the paper attributes this to SLAM-style geometric optimization on short indoor trajectories — with Anchor3R second-best on F1.

### Ablation: Image-Only Key/Value Cache

원논문 Table 5, Virtual KITTI with a ViT-Small backbone.

| Variant        | Sc.01 ATE ↓ | Sc.02 ATE ↓ | Sc.06 ATE ↓ | Sc.18 ATE ↓ | Sc.20 ATE ↓ | Avg. ATE ↓ | Avg. RTE ↓ | Avg. RRE ↓ |
| -------------- | ----------- | ----------- | ----------- | ----------- | ----------- | ---------- | ---------- | ---------- |
| w pose cache   | 3.613       | 2.174       | 0.285       | 3.955       | 7.558       | 3.517      | 0.146      | 0.092      |
| w/o pose cache | 3.113       | 1.054       | 0.424       | 1.410       | 7.208       | 2.642      | 0.097      | 0.090      |

Removing pose-query tokens from the cache improves ATE, RTE, and RRE on most scenes — Scene 06 is the exception (0.285 → 0.424). The paper's reading is that pose-query states encode reasoning under a particular local gauge and interfere when propagated across windows, while image-conditioned states are reusable visual evidence.

### Attention Analysis

원논문 Figure 3 compares attention scores between a STream3R-like fixed-gauge baseline and Anchor3R, showing the baseline increasingly concentrating attention on the first frame while Anchor3R distributes attention over the active local window. The figure carries no printed values, so none are transcribed here.

### Headline Figure

원논문 Figure 1 shows campus-scale VBR reconstructions completing inference on a single 32GB RTX 5090 GPU: campus_train0 (12,042 frames, ≈2.73 km) at 5.13 m ATE and campus_train1 (11,671 frames, ≈2.95 km) at 3.52 m ATE.

## 💡 Insights & Impact

**Decouple local measurement from global gauge alignment.** This is the paper's thesis in one line, and it borrows directly from global SfM's local-to-global decomposition — estimate relative measurements, then average them globally. Anchor3R replaces correspondence-based relative pose estimation with dense relative-pose prediction from a streaming feed-forward model.

**Redundancy is the point.** Because overlapping windows re-observe the same frames from different anchors, each frame ends up constrained by multiple independent measurements. That redundancy is exactly what motion averaging needs to redistribute error — and it is unavailable to methods that emit a single trajectory.

**The cache decision follows from the formulation.** Once poses are current-gauge, pose-query states become gauge-specific and therefore _not_ reusable memory. Caching only image-side states is not an optimization; it is a correctness requirement, and the ablation quantifies it.

**Offline refinement is a consequence, not an add-on.** Because the prediction interface already produces a graph, loop-closure keyframes can be reinserted as transient anchors and generate long-range edges with the same forward pass. This is why the online/offline gap is so large on VBR (76.21 → 19.60).

**Limitations the paper states.** New frames add pose constraints but do not update historical point maps, so early local geometry errors persist. The method relies on scale consistency between relative translations and local point maps across overlapping windows; weak overlap, degenerate motion, or very long sequences can still cause cross-window scale drift. And the evaluation is replay-based — no closed-loop deployment on physical robots or downstream navigation.

## 🔗 Related Work

- [VGGT](vggt.md) — the initialization and backbone; its unified camera/depth/point/track prediction is the starting point
- [Pi3](pi3.md) — permutation-equivariant formulation that removed fixed-reference bias; source of the scale-factor estimation, and the Pi3-Chunk baseline
- [CUT3R](../dynamic/cut3r.md) — persistent latent scene memory, a streaming baseline
- [TTT3R](ttt3r.md) — inference-time state updating, a streaming baseline
- [STream3R](stream3r.md) — causal-transformer streaming, and the fixed-gauge baseline used in the attention ablation
- [StreamVGGT](streamvggt.md) — streaming 4D visual geometry transformer baseline
- [Point3R](point3r.md) — explicit spatial pointer memory anchored to reconstructed 3D structure
- [ZipMap](zipmap.md) — compresses an image collection into a compact hidden state via test-time training
- [Scal3R](scal3r.md) — test-time-adapted global context for large-scale reconstruction
- [FastVGGT](fastvggt.md) — optimization-based baseline in the pose tables
- [Depth Anything 3](depth-anything-3.md) / [MapAnything](mapanything.md) — cited as recent extensions of the offline feed-forward paradigm
- [DUSt3R](../foundation/dust3r.md) — two-view pointmap prediction in a shared pairwise frame

## 📚 Key Takeaways

1. **Anchor at the current frame, not the first one.** Window-relative targets depend only on local geometry, freeing the network from maintaining a long-lived coordinate system through attention and memory.
2. **Emit a graph, not a trajectory.** Overlapping windows generate redundant relative-pose edges, which is what makes global drift redistribution possible at all.
3. **Cache image evidence, discard pose reasoning.** Pose-query states are gauge-specific; the ablation shows caching them hurts ATE, RTE, and RRE.
4. **Loop-aware refinement is where the big wins are.** On VBR, offline motion averaging takes average ATE from 76.21 to 19.60 and wins all seven sequences.
5. **Online mode is competitive but not dominant.** It clearly beats streaming baselines on KITTI (40.89 vs 51.90 for LongStream) and leads on Oxford Spires and Waymo, yet loses to LongStream and MASt3R-SLAM on short indoor TUM trajectories and to VGGT-Long on several KITTI sequences.

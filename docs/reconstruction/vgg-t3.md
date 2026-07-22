# VGG-T3: Offline Feed-Forward 3D Reconstruction at Scale (CVPR 2026)

![vgg-t3 — architecture](https://arxiv.org/html/2602.23361v1/figures/method/vggt_workings.png)

_(a) VGGT (원논문 Fig. 99)_

## 📋 Overview

- **Authors**: Sven Elflein, Ruilong Li, Sérgio Agostinho, Zan Gojcic, Laura Leal-Taixé, Qunjie Zhou, Aljosa Osep
- **Institution**: NVIDIA, Vector Institute, University of Toronto
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2602.23361)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Replaces VGGT's variable-length key–value scene representation with a fixed-size MLP fitted by test-time training, turning an O(n²) offline reconstructor into an O(n) one that handles 1k-image collections in under a minute.

## 🎯 Key Contributions

1. **Linear-time offline reconstruction**: an offline feed-forward model that scales linearly in the number of input views, achieved by distilling the KV space into a fixed-size MLP rather than querying it with softmax attention.
2. **A general linearisation recipe**: models representing scene geometry with a variable-length implicit (KV) representation can be "converted" into linear-time models via a fixed-dimensional implicit state.
3. **Single-GPU and distributed inference**: mini-batching the test-time-training objective allows CPU offloading for large collections on one GPU, and token sharding across GPUs with plain DDP.
4. **Feed-forward visual localization**: querying the frozen, optimised MLP with an unseen image localizes it against the reconstructed scene — mapping and localization in one model.

## 🔧 Technical Details

### The diagnosis

VGGT's global self-attention layer projects all input image tokens into a key–value space that functions as a dense, _variable-length_ scene representation. Decoding 3D attributes means querying that space with softmax attention, which is quadratic in the number of input images. The paper's point is that sparse attention (SparseVGGT) and token merging (FastVGGT) reduce the constant — `O(n²) → O((n/r)²)` for down-sampling ratio `r` — but leave the asymptotic complexity untouched.

### The substitution

Drawing an analogy to DeepSDF, where a fixed-size latent code is test-time-optimised to condition a pre-trained decoder, VGG-T3 maps the KV space through the weights of a fixed-size MLP instead. The MLP is optimised at test time with a reconstruction loss in token space, keeping the pre-trained encoder and decoder intact. Querying the scene then means applying the learned MLP to input tokens — linear in collection size.

### Scaling mechanics

Because the test-time-training objective's gradient can be computed by mini-batching, the method supports (i) processing large image collections on a single GPU by offloading mini-batches to CPU, and (ii) distributed inference by sharding image tokens across GPUs. Cross-GPU communication is needed only during the fast-weight (MLP) update, so plain distributed data parallel suffices — unlike VGGT, which would require engineered context-parallel softmax attention such as ring attention.

### ShortConv2D

An additional architectural component ablated in Table 6; adding it further closes the gap toward softmax attention.

## 📊 Results

### Pointmap estimation

원논문 Table 1. Dense (-D) and sparse (-S) splits. CD is Chamfer distance (lower better), NC normal consistency (higher better). Methods are grouped by asymptotic complexity. FastVGGT's code fails on NRGBD-S because one instance has only two views.

| Complexity | Method     | 7scenes-D CD↓ | 7scenes-S CD↓ | DTU CD↓   | ETH3D CD↓ |
| ---------- | ---------- | ------------- | ------------- | --------- | --------- |
| O(n²)      | VGGT       | 0.024         | **0.054**     | **1.537** | **0.279** |
| O(n²)      | SparseVGGT | 0.023         | 0.094         | 1.541     | 0.327     |
| O(n²)      | FastVGGT   | **0.021**     | 0.065         | 1.683     | 0.594     |
| O(n)       | TTT3R      | 0.035         | 0.129         | 5.708     | 0.885     |
| O(n)       | **VGG-T3** | 0.030         | 0.107         | 1.654     | 0.480     |

원논문 Table 1, NC columns and NRGBD.

| Complexity | Method     | 7scenes-D NC↑ | DTU NC↑   | ETH3D NC↑ | NRGBD-D CD↓ | NRGBD-S CD↓ |
| ---------- | ---------- | ------------- | --------- | --------- | ----------- | ----------- |
| O(n²)      | VGGT       | 0.668         | 0.676     | **0.855** | **0.014**   | **0.055**   |
| O(n²)      | SparseVGGT | 0.665         | 0.675     | 0.836     | 0.018       | 0.079       |
| O(n²)      | FastVGGT   | 0.662         | 0.672     | 0.775     | 0.033       | –           |
| O(n)       | TTT3R      | 0.666         | 0.672     | 0.733     | 0.071       | 0.094       |
| O(n)       | **VGG-T3** | **0.679**     | **0.685** | 0.789     | 0.029       | 0.056       |

Against the other O(n) method, TTT3R, the gap is large — notably DTU CD 1.654 vs 5.708. Against O(n²) baselines, VGG-T3 remains behind on Chamfer distance while leading on normal consistency for three of four splits.

### Video depth estimation

원논문 Table 2. Single per-sequence scale alignment.

| Method     | Bonn δ<1.25↑ | Bonn Abs Rel↓ | KITTI δ<1.25↑ | KITTI Abs Rel↓ | Sintel δ<1.25↑ | Sintel Abs Rel↓ |
| ---------- | ------------ | ------------- | ------------- | -------------- | -------------- | --------------- |
| VGGT       | 0.967        | **0.059**     | 0.964         | **0.071**      | **0.646**      | **0.300**       |
| SparseVGGT | 0.968        | 0.057         | 0.963         | 0.070          | 0.639          | 0.304           |
| FastVGGT   | **0.969**    | 0.058         | 0.964         | 0.073          | 0.630          | 0.307           |
| TTT3R      | **0.969**    | 0.061         | 0.818         | 0.151          | 0.510          | 0.469           |
| **VGG-T3** | 0.963        | 0.063         | **0.967**     | 0.076          | 0.581          | 0.345           |

VGG-T3 beats TTT3R substantially on KITTI and Sintel and is on par with the O(n²) methods on KITTI, but remains behind them on Sintel.

### Camera pose estimation

원논문 Table 3. This is where the method is weakest, and the paper says so directly.

| Method            | ScanNet ATE↓ | Sintel ATE↓ | TUM ATE↓  | TUM RPEr↓ | TUM RPEt↓ |
| ----------------- | ------------ | ----------- | --------- | --------- | --------- |
| VGGT              | **0.035**    | 0.172       | **0.012** | **0.310** | **0.010** |
| SparseVGGT        | 0.036        | 0.177       | 0.013     | 0.316     | **0.010** |
| FastVGGT          | **0.035**    | **0.158**   | 0.013     | 0.317     | 0.011     |
| TTT3R             | 0.063        | 0.196       | 0.025     | 0.337     | 0.012     |
| TTT3R (unordered) | 0.094        | 0.325       | 0.029     | 0.652     | 0.029     |
| **VGG-T3**        | 0.070        | 0.234       | 0.037     | 0.533     | 0.028     |

The paper's hypothesis is that VGGT appends a dedicated camera token to the image tokens immediately before the attention layer, creating two effective input "modalities" whose heterogeneous structure is hard for the TTT-layer MLP to memorise. The one clear advantage: VGG-T3 handles unordered input natively, whereas TTT3R degrades sharply on unordered sequences (ScanNet ATE 0.063 → 0.094).

### Scaling and latency

원논문 Table 4. Reconstruction latency in seconds with distributed inference.

| Method     | 1500 img, 1 GPU | 1500 img, 2 GPUs | 1500 img, 4 GPUs | 2000 img, 1 GPU | 2000 img, 4 GPUs |
| ---------- | --------------- | ---------------- | ---------------- | --------------- | ---------------- |
| TTT3R      | 90.1            | N/A              | N/A              | 126.2           | N/A              |
| VGGT       | OOM             | 1779.3           | 913.6            | OOM             | 1590.2           |
| **VGG-T3** | 173.1           | **56.8**         | **29.7**         | 230.7           | **48.5**         |

VGGT goes out of memory on a single GPU at both collection sizes; TTT3R cannot use multiple GPUs at all because it is autoregressive.

### Stated speed-ups

The paper reports these ratios explicitly, each with its setting:

- **1k images**: VGG-T3 in 58 s vs VGGT over 11 min — **11.6× speed-up** (Fig. 4 caption). FastVGGT takes more than 4 minutes, a **4.3×** gap. The abstract states 54 seconds for the same 11.6× figure.
- **2k images**: **up to 33× faster** than VGGT, which is quoted at 27 min (Sec. 1) for a 48.5 s VGG-T3 run.

### Feed-forward visual localization

원논문 Table 5. Sim(3) alignment on mapping images, then rotation error `e_r` and translation error `e_t` on query poses.

| Dataset  | Method   | e_r (°) ↓ | e_t (m) ↓ | 10cm, 10° (%) ↑ | 20cm, 20° (%) ↑ |
| -------- | -------- | --------- | --------- | --------------- | --------------- |
| 7Scenes  | TTT3R    | 7.18      | 0.17      | 34.59           | 70.21           |
| 7Scenes  | **Ours** | **6.71**  | **0.16**  | **40.69**       | **73.00**       |
| Wayspots | TTT3R    | 74.45     | 4.38      | 0.69            | 2.94            |
| Wayspots | **Ours** | **32.04** | **1.90**  | **13.41**       | **30.64**       |

The paper is explicit that this is a proof of concept, not a competitive localization pipeline: it cites Reloc3r reaching `e_r = 1.02°`, `e_t = 0.04 m` on 7scenes.

### Ablations

원논문 Table 6. Smaller-scale setting: 224×224, ScanNet++ training with 2–24 views, same base architecture throughout.

| Variant                | CD ↓      | NC ↑      | mAA(30) ↑ |
| ---------------------- | --------- | --------- | --------- |
| Softmax Attention      | **0.061** | **0.844** | **76.33** |
| (i) Scratch            | 0.262     | 0.727     | 52.95     |
| (ii) T2R               | 0.137     | 0.804     | 66.27     |
| (iii) LoLCats          | 0.097     | 0.804     | 62.87     |
| (iv) Ours              | 0.074     | 0.833     | 72.16     |
| (v) Ours + ShortConv2D | 0.066     | 0.838     | 74.14     |

Training with TTT from scratch gets stuck in a local optimum; initialising from softmax-pretrained weights is essential. ShortConv2D narrows the remaining gap to softmax attention but does not close it.

### Runtime vs quality

Figure 4 plots runtime against Chamfer distance for collections of 100, 500, and 1k images on 7scenes. The reconstruction-quality gap between VGG-T3 and the O(n²) baselines narrows as the number of images increases, and VGG-T3 does not degrade with more views. Beyond the runtime figures quoted above, the plot has no printed values, so nothing further is transcribed.

## 💡 Insights & Impact

### Attention as an implicit, variable-length scene memory

The paper's reframing is the most valuable part. It reads the KV cache of a global attention layer not as an implementation detail but as _the scene representation_: dense, implicit, and — crucially — variable-length. Once you see it that way, the quadratic cost is not an attention problem but a representation-size problem, and the natural fix is the DeepSDF move: swap a variable-length representation for a fixed-size one optimised at test time. Under this lens FastVGGT and SparseVGGT are structured compressions of the same KV space, which explains why they lower the constant but not the exponent.

### Offline global aggregation without quadratic cost

The prior trade-off was stark: offline methods aggregate globally and are accurate but quadratic; online methods (CUT3R, MUSt3R, Stream3R, StreamVGGT) are linear or streaming but drift, and cannot handle unordered image sets. VGG-T3 sits in a new quadrant — offline and global, hence unordered-input-capable, but linear. The pointmap table bears this out: it beats the other O(n) method by very large margins on DTU and ETH3D.

### An honest limitation

The camera pose results are worse than TTT3R's on ordered sequences and clearly worse than VGGT's. The conclusion states the general limitation plainly: a gap w.r.t. softmax attention remains, especially in the wide-baseline setting, and reconciling the fixed expressivity of an MLP scene representation with the accuracy of quadratic attention is left as future work.

### Localization for free

Because the optimised MLP _is_ a compressed map, querying it with a new image is localization. That two capabilities traditionally requiring separate systems fall out of one representation change is a genuinely novel structural result, even though the accuracy is well short of dedicated pipelines.

## 🔗 Related Work

- [VGGT](./vggt.md) — the base model VGG-T3 linearises; the O(n²) accuracy reference throughout.
- [FastVGGT](./fastvggt.md) and SparseVGGT — token merging and block-sparse attention; reduce the constant, not the asymptotics.
- [TTT3R](./ttt3r.md) — the concurrent O(n) test-time-training baseline; VGG-T3 is offline and global where TTT3R is autoregressive.
- [CUT3R](../dynamic/cut3r.md) and [MUSt3R](./must3r.md) — fixed-size iteratively-updated implicit memory, the online counterpart to this idea.
- [STream3R](./stream3r.md) and [StreamVGGT](./streamvggt.md) — causal conversions of VGGT that still scale quadratically.
- [Point3R](./point3r.md) and [MapAnything](./mapanything.md) — explicit spatial memory alternatives.
- [VGGT-SLAM](./vggt-slam.md) and [Light3R-SfM](./light3r-sfm.md) — chunked and scene-graph approaches to large collections.
- [Fast3R](./fast3r.md), [pi3](./pi3.md) — global softmax-attention fusion baselines discussed in related work.
- [Reloc3r](../pose/reloc3r.md) — the visual localization accuracy reference the paper cites against itself.

## 📚 Key Takeaways

1. **The bottleneck is the representation, not the operator.** Treating the KV space as a variable-length scene memory reframes quadratic attention cost as a representation-size problem with a fixed-size solution.
2. **Test-time training as compression.** Fitting a fixed-size MLP to the KV mapping at test time preserves the pre-trained encoder/decoder while making queries linear in collection size.
3. **Concrete scaling wins.** 1k images 11.6× faster than VGGT, 2k images up to 33× faster; VGGT OOMs on a single GPU at 1500 images where VGG-T3 finishes in 173 s.
4. **Distributed inference comes almost free** — plain DDP works, since cross-GPU communication is confined to the MLP update.
5. **Pose is the weak spot.** VGG-T3 loses to VGGT and to TTT3R on ordered camera pose, likely due to VGGT's separate camera-token modality, and a general accuracy gap to softmax attention persists in wide-baseline settings.

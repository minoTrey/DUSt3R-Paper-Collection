# LiteVGGT: Boosting Vanilla VGGT via Geometry-aware Cached Token Merging (CVPR 2026)

![litevggt — architecture](https://arxiv.org/html/2512.04939/x2.png)

_Architecture Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Zhijian Shu, Cheng Lin, Tao Xie, Wei Yin, Ben Li, Zhiyuan Pu, Weize Li, Yao Yao, Xun Cao, Xiaoyang Guo, Xiao-Xiao Long
- **Institution**: Nanjing University of Posts and Telecommunications, Horizon Robotics, Nanjing University, Zhejiang University, Macau University of Science and Technology, TARS Robotics, China Mobile Zijin Innovation Institute
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2512.04939) | [Project Page](https://garlicba.github.io/LiteVGGT/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Token merging designed for 3D rather than borrowed from LLM/diffusion practice — geometric importance (Sobel gradient + token variance) picks which tokens survive, merge indices are cached across layers, and fine-tuning plus FP8 quantization close the accuracy gap, letting VGGT run 1000-image scenes.

## 🎯 Key Contributions

1. **Geometry-aware token prioritization**: VGGT's tokens are one-to-one with image patches and 3D points, so merging by random or fixed-stride sampling (as in ToMe-style methods) destroys geometry. LiteVGGT scores tokens by a fused gradient + variance map instead.
2. **Cached merge indices**: Token similarity is stable across adjacent layers, so merge indices are computed once every 6 layers (4 computations total over 24 layers) and reused.
3. **Three-way token partition**: GA tokens (top 10%, never merged), dst tokens (merge anchors), src tokens (merged away), with unmerging by replication before the dense prediction heads.
4. **Engineering complements**: Fine-tuning on a dataset mix to recover the merging-induced accuracy loss, and FP8 quantization via NVIDIA Transformer Engine.
5. **Stated headline**: up to **10× speedup** over VGGT with substantial memory savings, enabling single-forward processing of 1000-image scenes.

## 🔧 Technical Details

### Bottleneck Analysis

VGGT (1.2B parameters) tokenizes frames with DINOv2, adds 5 special tokens per frame (1 camera + 4 register), and runs a 24-layer frame-global attention stack. The frame-global attention concatenates tokens across all images, so cost is quadratic in token count. The paper reports that vanilla VGGT **OOMs at 500 images**, and that an optimized VGGT\* (redundant memory-heavy operations removed) still takes **over 20 minutes for 1000 images on an H20 GPU**; at 1100 images at 392×518, VGGT\* OOMs even on a 96 GiB device.

### The Geometric-Cue Experiment

Fig. 5 feeds pure edge maps — stripped of texture and photometric information — into VGGT and DepthAnything-V2. Both still produce coherent, geometrically plausible reconstructions. This is a qualitative figure with no printed metrics, but it is the paper's stated justification for treating edge-rich regions as the backbone of 3D reasoning.

### Geometry-Aware Feature Map

```text
Ψ_GA = α · norm(Ψ_g) + β · norm(Ψ_v)
```

- **Ψ_g (Grad Map)**: Sobel operator on horizontal/vertical intensity changes, downsampled to token granularity.
- **Ψ_v (Var Map)**: tokens rearranged into 2D grids, local average-pooled variance, separating textured surfaces from smooth walls.

The paper notes that because this uses only Sobel operators and average pooling, computing GA maps for 1000 images finishes in **under one second**.

### Token Partition

- **GA Tokens**: top 10% highest-scoring tokens per frame, excluded from merging.
- **Dst Tokens**: all first-frame tokens (VGGT's world-coordinate anchor), plus one token per 2×2 grid in other frames — specifically the _lowest_ GA score in each grid, targeting smooth low-information regions.
- **Src Tokens**: everything else, matched to dst tokens by cosine similarity.

### Merging and Unmerging

```text
x'_d = (x_d + Σ_{x_s ∈ S_d} x_s) / (1 + |S_d|)
```

Only `x'_d` survives into subsequent layers. Before the prediction heads, each merged token is replicated back across `{x_d} ∪ S_d`, with local geometric variability recovered through VGGT's frame attention.

### Fine-tuning and Quantization

Fine-tuning starts from VGGT's checkpoints and updates the aggregator and prediction heads on Co3Dv2, BlendedMVS, DL3DV and others: 4–48 images per batch, 20K iterations on 8 H20 GPUs (about 3 days), with a 5% linear warm-up from 1e-6 to 4e-5 then cosine decay to 7e-7. FP8 inference is applied after weight mapping via NVIDIA's Transformer Engine.

## 📊 Results

### Point Cloud Reconstruction — ScanNet-50

원논문 Table 1. Chamfer Distance and wall-clock time at four sequence lengths. OOM = out of memory. VGGT\* is VGGT with redundant memory-heavy operations removed.

| Method   | CD ↓ (1000) | Time ↓ (1000) | CD ↓ (496) | Time ↓ (496) | CD ↓ (296) | Time ↓ (296) | CD ↓ (96) | Time ↓ (96) |
| -------- | ----------- | ------------- | ---------- | ------------ | ---------- | ------------ | --------- | ----------- |
| Fast3R   | 0.692       | 563.7s        | 0.689      | 143.7s       | 0.711      | 41.3s        | 0.720     | 5.9s        |
| CUT3R    | 0.780       | 112.2s        | 0.774      | 26.7s        | 0.754      | 13.5s        | 0.791     | 5.1s        |
| VGGT     | OOM         | OOM           | OOM        | OOM          | 0.417      | 121.2s       | 0.420     | 16.6s       |
| VGGT\*   | 0.485       | 1275.1s       | 0.424      | 329.7s       | 0.415      | 120.9s       | 0.418     | 16.7s       |
| FastVGGT | 0.436       | 258.3s        | 0.424      | 78.4s        | 0.423      | 32.8s        | 0.409     | 6.4s        |
| LiteVGGT | **0.428**   | 127.2s        | **0.392**  | 37.9s        | **0.365**  | 16.6s        | **0.329** | 3.5s        |

This is the table behind the headline: the paper states LiteVGGT "delivers the lowest Chamfer Distance error and a 10× speed-up over VGGT with 1000 input images."

### Point Cloud Reconstruction — 7 Scenes and NRGBD

원논문 Table 2. Keyframes sampled every 3 frames.

| Method   | 7Sc Acc ↓ | 7Sc Comp ↓ | 7Sc NC ↑  | 7Sc Time ↓ | NR Acc ↓  | NR Comp ↓ | NR NC ↑   | NR Time ↓ |
| -------- | --------- | ---------- | --------- | ---------- | --------- | --------- | --------- | --------- |
| Fast3R   | 0.053     | 0.047      | 0.613     | 58.5s      | 0.083     | 0.023     | 0.655     | 98.9s     |
| CUT3R    | 0.181     | 0.088      | 0.586     | 15.8s      | 0.304     | 0.166     | 0.581     | 27.1s     |
| VGGT     | 0.021     | **0.022**  | **0.614** | 133.1s     | **0.024** | 0.015     | **0.730** | 233.1s    |
| FastVGGT | 0.021     | **0.022**  | 0.604     | 36.5s      | 0.029     | **0.014** | 0.704     | 70.7s     |
| LiteVGGT | **0.020** | 0.024      | 0.606     | 19.2s      | 0.031     | 0.019     | 0.698     | 36.3s     |

On NRGBD, LiteVGGT is the **worst** of the three VGGT variants on all three quality metrics; its advantage is runtime.

### Reconstruction — Tanks & Temples, F1 at ×5 thresholds

원논문 Table 3. Per-scene thresholds Barn 0.050 / Caterpillar 0.025 / Courthouse 0.015 / Ignatius 0.025 / Meetingroom 0.050 / Truck 0.250, i.e. official values expanded ×5.

| Method   | Barn | Caterpillar | Courthouse | Ignatius | Meetingroom | Truck | Avg. ↑   | Time (s) ↓ |
| -------- | ---- | ----------- | ---------- | -------- | ----------- | ----- | -------- | ---------- |
| VGGT     | 0.54 | 0.33        | OOM        | 0.54     | 0.63        | 0.62  | -        | -          |
| VGGT\*   | 0.54 | 0.33        | 0.50       | 0.54     | 0.63        | 0.62  | **0.53** | 221.45s    |
| FastVGGT | 0.37 | 0.27        | 0.44       | 0.34     | 0.43        | 0.45  | 0.38     | 66.20s     |
| LiteVGGT | 0.44 | 0.26        | 0.44       | 0.30     | 0.57        | 0.41  | 0.40     | **29.52s** |

### Reconstruction — Tanks & Temples, F1 at ×10 thresholds

원논문 Table 3, second block. Thresholds Barn 0.100 / Caterpillar 0.050 / Courthouse 0.030 / Ignatius 0.050 / Meetingroom 0.100 / Truck 0.500.

| Method   | Barn | Caterpillar | Courthouse | Ignatius | Meetingroom | Truck | Avg. ↑   | Time (s) ↓ |
| -------- | ---- | ----------- | ---------- | -------- | ----------- | ----- | -------- | ---------- |
| VGGT     | 0.69 | 0.56        | OOM        | 0.70     | 0.79        | 0.74  | -        | -          |
| VGGT\*   | 0.69 | 0.56        | 0.67       | 0.70     | 0.79        | 0.74  | **0.69** | 221.45s    |
| FastVGGT | 0.56 | 0.42        | 0.61       | 0.48     | 0.61        | 0.59  | 0.54     | 66.20s     |
| LiteVGGT | 0.60 | 0.43        | 0.60       | 0.45     | 0.74        | 0.59  | 0.57     | **29.52s** |

This is the clearest quality cost in the paper. LiteVGGT beats FastVGGT at both threshold scales, but sits well below VGGT\* (0.40 vs 0.53 and 0.57 vs 0.69 on average). The paper describes its F1 as "slightly lower than VGGT"; the tabulated gap is larger than that phrasing suggests.

### DTU Reconstruction and CO3Dv2 Pose Estimation

원논문 Table 4. Pose metrics are AUC of relative pose error, where the error is the maximum of rotation and translation angular error.

| Method   | DTU Acc. ↓ | DTU Comp. ↓ | DTU Over. ↓ | CO3Dv2 AUC@30 ↑ | CO3Dv2 AUC@20 ↑ | CO3Dv2 AUC@15 ↑ |
| -------- | ---------- | ----------- | ----------- | --------------- | --------------- | --------------- |
| Fast3R   | 3.712      | 1.412       | 2.562       | 81.3            | 74.2            | 69.7            |
| CUT3R    | 1.428      | 1.396       | 1.412       | 82.5            | 77.3            | 73.8            |
| VGGT     | **0.508**  | **0.561**   | **0.534**   | **86.3**        | **81.4**        | **76.8**        |
| FastVGGT | 0.824      | 0.655       | 0.739       | 83.4            | 77.6            | 71.9            |
| LiteVGGT | 0.652      | 0.780       | 0.716       | 83.2            | 77.3            | 71.9            |

On DTU reconstruction LiteVGGT wins Overall against FastVGGT (0.716 vs 0.739) but loses on Completeness (0.780 vs 0.655). On CO3Dv2 pose it is marginally behind FastVGGT at AUC@30 and AUC@20 and tied at AUC@15.

### Pose Estimation — Tanks & Temples (AUC@30)

원논문 Table 5.

| Method   | Barn | Caterpillar | Courthouse | Ignatius | Meetingroom | Truck | Avg. ↑   | Time (s) ↓ |
| -------- | ---- | ----------- | ---------- | -------- | ----------- | ----- | -------- | ---------- |
| VGGT     | 91.3 | 89.0        | OOM        | 88.9     | 90.0        | 94.1  | -        | -          |
| VGGT\*   | 91.3 | 89.0        | 81.8       | 88.8     | 90.0        | 94.1  | **89.2** | 221.45s    |
| FastVGGT | 90.1 | 86.3        | 81.8       | 88.0     | 87.6        | 93.5  | 87.9     | 66.20s     |
| LiteVGGT | 88.5 | 89.3        | 81.7       | 88.1     | 87.8        | 92.6  | 88.0     | **29.52s** |

### Pose Estimation — DTU

원논문 Table 6.

| Method   | AUC@30 ↑ | AUC@15 ↑ | AUC@5 ↑  |
| -------- | -------- | -------- | -------- |
| VGGT     | **94.3** | **88.6** | **66.3** |
| FastVGGT | 93.4     | 86.8     | 61.4     |
| LiteVGGT | 93.3     | 86.6     | 60.6     |

Pose degradation is concentrated at the tight threshold: AUC@5 drops from 66.3 to 60.6.

### Ablation: Contribution of Each Module

원논문 Table 7. Accuracy on DTU reconstruction; latency and memory for 1000 images at 392×518 on an H20 GPU. Rows are cumulative.

| Method                | Acc. ↓ | Comp. ↓ | Overall ↓ | Time (s) | Mem. (GiB) |
| --------------------- | ------ | ------- | --------- | -------- | ---------- |
| VGGT                  | 0.508  | 0.561   | 0.534     | 1275.6   | OOM        |
| + GA Token Merging    | 0.789  | 0.601   | 0.696     | 264.3    | 60.34      |
| + Fine-tuning         | 0.587  | 0.687   | 0.642     | 264.3    | 60.34      |
| + Cache Merge Indices | 0.621  | 0.755   | 0.688     | 200.6    | 59.28      |
| + FP8 Quantization    | 0.652  | 0.780   | 0.716     | 127.9    | 45.31      |

Read honestly, this table is a ledger of trades: merging costs 0.162 Overall, fine-tuning recovers 0.054 of it, and caching and FP8 each give back some accuracy in exchange for latency and memory. The final model is 0.182 Overall worse than VGGT while running roughly ten times faster and fitting in 45 GiB.

### Stated Efficiency Figures

Only the paper's own numbers, with the setting attached:

- **Up to 10× speedup** over VGGT (abstract; instantiated at 1000 input images and "nearly a 10× speed-up" on Tanks & Temples).
- **Over 4× latency reduction** from geometry-aware token merging alone, on top of VGGT\*.
- **Caching merge indices**: stated as a **20%** latency reduction in the method section (Sec. 3.4, referencing Fig. 4) and as **25%** in the efficiency section (Sec. 4.4 and 4.5). The paper is inconsistent between the two; both figures are reproduced here rather than reconciled.
- **FP8 quantization**: an additional **33% latency reduction** and roughly **25% memory savings**.
- **GA map computation for 1000 images: under one second.**

Note the latency breakdown of VGGT components (Fig. 3) and after token merging (Fig. 4) are plots without printed values.

## 💡 Insights & Impact

### The Argument Against Borrowed Token Merging

The paper's core critique of FastVGGT and ToMe-lineage methods is specific: these strategies were designed for semantic or generic visual tokens in LLMs, VLMs, and diffusion models, where tokens have "no inherent geometric binding." VGGT's tokens do — one-to-one with image patches and 3D points. Random or fixed-stride partitioning therefore risks merging an edge token into a blank-wall token. The Tanks & Temples tables support the claim relative to FastVGGT (0.40 vs 0.38, 0.57 vs 0.54 average F1, at less than half the runtime).

### Two Empirical Observations Doing All the Work

1. **Spatial redundancy**: tokens from local image regions are geometrically correlated, so cross-frame similarity is high.
2. **Temporal (inter-layer) redundancy**: attention patterns are stable across adjacent layers (Fig. 8), so merge decisions can be reused.

The second is what makes caching legitimate — and it is what turns merge-index computation from a new bottleneck (Fig. 4's "CM" term) back into a negligible cost.

### The Honest Position of This Paper

LiteVGGT is not a free lunch. It wins the ScanNet-50 CD table outright, but on NRGBD, DTU, and Tanks & Temples it trades measurable quality for speed. Its own conclusion frames the contribution correctly: large-scale scene reconstruction "does not necessarily require heavy global attention computation," and careful token reduction is sufficient to preserve _high_, not _equal_, geometric fidelity.

### Positioning Against Alternatives

The paper explicitly rejects two other efficiency routes: sequential/streaming input (StreamVGGT) sacrifices the single-pass end-to-end property, and quantization-only approaches (QuantVGGT) need time-consuming cross-scene calibration that harms generality. LiteVGGT keeps the single forward pass and applies FP8 only after token merging has preserved the feature representation.

## 🔗 Related Work

- [VGGT](./vggt.md) — the model being compressed; every table's reference point.
- [FastVGGT](./fastvggt.md) — the closest competitor, and the method LiteVGGT's central argument targets: generic token merging that ignores geometric coupling.
- [StreamVGGT](./streamvggt.md) — the streaming alternative LiteVGGT declines to follow because it gives up single-pass inference.
- [Fast3R](./fast3r.md) — many-view feed-forward baseline appearing in the reconstruction and pose tables.
- [CUT3R](../dynamic/cut3r.md) — recurrent-state baseline; fastest at some settings but with notably worse accuracy here.
- [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md) — the pointmap lineage the related-work section traces.

## 📚 Key Takeaways

1. **Token merging must respect what the tokens mean.** Sobel gradient plus token variance is a cheap proxy for geometric importance, and it measurably beats geometry-agnostic merging.
2. **Merge decisions are reusable across layers.** Computing indices once every 6 layers removes what would otherwise become the new bottleneck at long sequence lengths.
3. **Efficiency compounds only if quality is protected first.** FP8 quantization is applied last, on the premise that merging preserved VGGT's core representation.
4. **The speedup is real and so is the loss.** 10× at 1000 images with the best ScanNet-50 CD, but DTU Overall goes 0.534 → 0.716 and Tanks & Temples average F1 0.69 → 0.57 at the ×10 thresholds.
5. **Scale is the point.** VGGT OOMs at 500 images; LiteVGGT processes 1000 images in 127.2 s within 45.31 GiB.

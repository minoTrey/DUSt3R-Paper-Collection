# TrackCraft3R: Repurposing Video Diffusion Transformers for Dense 3D Tracking (arXiv preprint (2026-05))

![trackcraft3r — architecture](https://arxiv.org/html/2605.12587v1/x1.png)

_Overall architecture (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Jisu Nam, Jahyeok Koo, Soowon Son, Jaewoo Jung, Honggyu An, Junhwa Hur, Seungryong Kim
- **Institution**: KAIST AI, Google DeepMind
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.12587) | [Project Page](https://cvlab-kaist.github.io/TrackCraft3r)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first method to repurpose a pre-trained video diffusion transformer (video DiT) as a feed-forward dense 3D tracker, using a dual-latent representation and temporal RoPE alignment to convert the per-frame generative paradigm into a reference-anchored tracking pointmap predicted in a single forward pass.

## 🎯 Key Contributions

1. **Video DiT repurposed for tracking**: The first method to turn a pre-trained video diffusion transformer into a feed-forward dense 3D tracker, leveraging spatio-temporal priors learned from internet-scale videos rather than static multi-view priors or synthetic-only training.
2. **Dual-latent representation**: Per-frame **geometry latents** (RGB + reconstruction pointmap) and first-frame-anchored **track latents** that act as dense query points; through full 3D attention, each track latent attends to geometry latents across frames to recover its 3D position over time.
3. **Temporal RoPE alignment**: Repurposes the temporal axis of 3D rotary positional embedding so each track latent is assigned a target timestamp, specifying which frame's geometry latent it should attend to.
4. **Efficiency**: Runs **1.3× faster** and uses **4.6× less peak memory** than the strongest prior method DELTAv2, converting frame-anchored generation into reference-anchored tracking with only LoRA fine-tuning.

## 🔧 Technical Details

### Problem framing

Given a monocular video and its **frame-anchored reconstruction pointmap** `P_j(t_j)` (obtained from external 3D foundation models for depth/pose, e.g. ViPE or Depth Anything 3), TrackCraft3R predicts a **reference-anchored tracking pointmap** `P_0(t_j)` — the 3D positions at time `t_j` of the content originally observed in the first frame `I_0` — plus a per-pixel visibility map `o_j`. Frame-anchored generation (each frame's own content) is fundamentally mismatched with reference-anchored tracking (following the same physical points from a reference frame across time); the two designs below bridge this gap.

### Architecture

- **Backbone**: Wan 2.1-T2V video DiT fine-tuned with LoRA; the DiT is used as a one-step regressor (fixed diffusion timestep zero, null text prompt) rather than an iterative denoiser.
- **Separate VAE encoders** for RGB and pointmaps; the geometry latent `g_j = [z_rgb_j ; z_pm_j]` is a channel-wise concatenation, and the track latent `r_j = g_0` replicates the first-frame geometry latent across all timestamps.
- **Bypass temporal compression**: the 3D VAE's temporal dimension is treated as a batch dimension to preserve per-frame spatial precision (ablated in Table 3).
- **Pointmap normalization**: subtract the mean and divide by the maximum distance from the mean, computed over the 2%–98% depth percentile range to exclude outliers, giving values approximately in [−1, 1].
- **Residual prediction**: instead of regressing `P_0(t_j)` directly, the model predicts a residual `Δ_j = P_0(t_j) − P_0(t_0)` (zero for static regions), which stabilizes training and improves accuracy.
- **Two decoder heads** (`D_track`, `D_vis`) decode the track-latent output into the residual track and the visibility map, which is broadcast to three channels to match VAE output dimensionality.

### Training and inference

- Two-stage training at 480×832 on 12-frame clips using 8 H200 GPUs: Stage 1 trains DiT (LoRA + input/output projections) with VAEs frozen (lr 1e-4, batch 80, 3 days); Stage 2 unfreezes all VAE encoders/decoders and trains end-to-end (lr 3e-5 DiT / 1e-5 VAE, batch 64, 2 days).
- **Objective**: MSE loss on the predicted residual in normalized pointmap space plus a BCE visibility loss weighted by 0.1.
- **Datasets**: Kubric, PointOdyssey, Dynamic Replica (dynamic 3D trajectories from mesh vertices), plus TartanAir (static scenes with large camera motion for ego-motion robustness).
- **Long-video inference**: a strided sliding-window strategy with the first frame as a fixed anchor; stride `s = ⌈(L−1)/F⌉`, with consecutive RoPE temporal indices reassigned per pass.

## 📊 Results

Evaluation follows TAPVid-3D metrics after Sim(3) alignment: **AJ↑** (average Jaccard), **APD3D↑** (average percentage of points within a 3D threshold), and **OA↑** (occlusion accuracy). Higher is better for all three. Sparse benchmarks: ADT, PStudio, DR, PO; dense benchmark: Kubric.

### Main 3D tracking comparison — Average across benchmarks

원논문 Table 1. Average over ADT, PStudio, DR, PO, Kubric.

| Method                  | AJ↑        | APD3D↑     | OA↑    |
| ----------------------- | ---------- | ---------- | ------ |
| DELTA + ViPE            | 0.4315     | 0.6123     | 0.8097 |
| DELTAv2 + ViPE          | 0.4395     | 0.6184     | 0.8144 |
| DELTAv2 + DA3           | 0.4975     | 0.6858     | 0.8128 |
| St4RTrack               | 0.4069     | 0.5884     | 0.7564 |
| Any4D                   | 0.4311     | 0.6119     | 0.7893 |
| TraceAnything           | 0.3537     | 0.5002     | 0.7800 |
| MotionCrafter           | 0.4161     | 0.5658     | 0.8276 |
| **TrackCraft3R + ViPE** | 0.5639     | 0.6817     | 0.9258 |
| **TrackCraft3R + DA3**  | **0.6785** | **0.7931** | 0.9250 |

Note the honest trade-off: on **average APD3D**, TrackCraft3R + ViPE (0.6817) slightly trails DELTAv2 + DA3 (0.6858); TrackCraft3R only surpasses it once given the stronger DA3 geometry.

### Per-dataset AJ↑ (top methods)

원논문 Table 1. AJ↑ per benchmark.

| Method              | ADT        | PStudio    | DR         | PO         | Kubric     | Average    |
| ------------------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| DELTAv2 + DA3       | 0.6150     | 0.5571     | 0.4494     | 0.5304     | 0.3354     | 0.4975     |
| TrackCraft3R + ViPE | 0.6683     | 0.6803     | 0.5842     | 0.5836     | 0.3032     | 0.5639     |
| TrackCraft3R + DA3  | **0.8626** | **0.7287** | **0.6518** | **0.7288** | **0.4208** | **0.6785** |

On the dense **Kubric** split, DELTAv2 + DA3 (0.3354 AJ) still beats TrackCraft3R + ViPE (0.3032 AJ); the stronger DA3 geometry is needed to take the lead there.

### Comparison with concurrent V-DPM — Average (sparse benchmarks)

원논문 Table 10. Average over ADT, PStudio, DR, PO; evaluated on the first 24 frames.

| Method               | AJ↑        | APD3D↑     | OA↑        |
| -------------------- | ---------- | ---------- | ---------- |
| V-DPM                | 0.7329     | **0.9155** | 0.8297     |
| TrackCraft3R + DA3   | 0.7410     | 0.8311     | **0.9531** |
| TrackCraft3R + V-DPM | **0.7803** | 0.8832     | 0.9335     |

V-DPM (a concurrent work trained on ~23 3D/4D datasets vs. TrackCraft3R's 4) achieves slightly higher **APD3D**, while TrackCraft3R exceeds it in AJ and OA.

### Ablation — Spatio-temporal prior

원논문 Table 2. Identical architecture trained from scratch vs. pre-trained init.

| Initialization     | AJ↑        | APD3D↑     | OA↑        |
| ------------------ | ---------- | ---------- | ---------- |
| Random             | 0.4698     | 0.6312     | 0.8271     |
| Pre-trained (Ours) | **0.5639** | **0.6817** | **0.9258** |

### Ablation — Model components

원논문 Table 3. Each component removed from the full model (VAE frozen for this study).

| Configuration                 | AJ↑        | APD3D↑     | OA↑        |
| ----------------------------- | ---------- | ---------- | ---------- |
| (a) w/o First-frame anchoring | 0.5135     | 0.6535     | 0.8778     |
| (b) w/o Temporal RoPE align.  | 0.4450     | 0.6317     | 0.8031     |
| (c) w/o Residual displacement | 0.5007     | 0.6172     | 0.9159     |
| (d) w/ VAE temporal compress. | 0.4487     | 0.6325     | 0.8148     |
| **Full model (Ours)**         | **0.5609** | **0.6790** | **0.9225** |

Removing temporal RoPE alignment (b) causes the largest AJ drop; removing residual displacement (c) specifically drops APD3D.

### Ablation — Input geometry quality

원논문 Table 4. Averaged over synthetic datasets (GT available). No retraining when swapping geometry.

| Configuration      | AJ↑        | APD3D↑     | OA↑        |
| ------------------ | ---------- | ---------- | ---------- |
| DELTAv2 + DA3      | 0.4384     | 0.5858     | 0.8476     |
| TrackCraft3R + DA3 | 0.6005     | 0.7144     | 0.9304     |
| DELTAv2 + GT       | 0.5590     | 0.7169     | 0.8380     |
| TrackCraft3R + GT  | **0.7649** | **0.8635** | **0.9353** |

Replacing DA3 with ground-truth geometry consistently improves all metrics (an upper bound), showing that future advances in 3D geometry estimation directly translate to better tracking.

### Ablation — LoRA rank and VAE finetuning

원논문 Table 5.

| LoRA rank | VAE finetuning | AJ↑        | APD3D↑     | OA↑        |
| --------- | -------------- | ---------- | ---------- | ---------- |
| 64        | ✗              | 0.5025     | 0.6430     | 0.8779     |
| 256       | ✗              | 0.5399     | 0.6623     | 0.9112     |
| 1024      | ✗              | 0.5609     | 0.6790     | 0.9225     |
| 1024      | ✓              | **0.5639** | **0.6817** | **0.9258** |

### Inference efficiency

원논문 Table 6. 448×448 resolution on a single NVIDIA A6000 GPU. Lower is better.

| Frames | Method       | Time (s)↓ | Memory (GB)↓ |
| ------ | ------------ | --------- | ------------ |
| 12     | DELTA        | 14.64     | 29.97        |
| 12     | DELTAv2      | 5.00      | 35.46        |
| 12     | TrackCraft3R | **3.91**  | **7.63**     |
| 23     | DELTA        | 28.92     | 30.78        |
| 23     | DELTAv2      | 9.70      | 35.90        |
| 23     | TrackCraft3R | **7.84**  | **7.63**     |

For 12 frames, TrackCraft3R is **1.3× faster** and uses **4.6× less peak memory** than DELTAv2. Against V-DPM (원논문 Table 11), TrackCraft3R runs **3.2× faster / 1.7× less memory** at 12 frames, widening to **6.6× faster / 2.3× less memory** at 23 frames, since it predicts all trajectories in a single feed-forward pass (O(L) runtime, O(1) peak memory) rather than invoking a decoder once per timestamp.

## 💡 Insights & Impact

- **Generic video priors beat 3D-heavy supervision on efficiency and data cost**: TrackCraft3R fine-tunes on only 4 synthetic 3D/4D datasets versus V-DPM's 23, yet remains competitive — the spatio-temporal priors from generic internet video compensate for the absence of dense 3D annotations.
- **Reference-anchoring in one pass avoids error accumulation**: unlike MotionCrafter, which predicts frame-anchored scene flow between adjacent frames and requires temporal chaining (accumulating error under occlusion), TrackCraft3R directly outputs a reference-anchored tracking pointmap.
- **Decoupled geometry input**: because per-frame depth/pose come from external 3D foundation models, the method benefits from future geometry estimators with no retraining — but its accuracy is bounded by input geometry quality (Table 4).
- **Robustness**: performance degrades much more slowly than DELTAv2 as temporal stride `s` (1→12) or frame length `L` (12→120) grows (Figure 5, curves; exact values not printed in text).

## 🔗 Related Work

- **[Any4D](./any4d.md)**: Feed-forward metric 4D reconstruction; a reconstruction-model-based dense 3D tracker baseline compared in Table 1.
- **[V-DPM](./v-dpm.md)**: Concurrent VGGT-based 4D video reconstruction method; compared as an alternative and as an input-geometry source (Tables 10–11).
- **[Stereo4D](./stereo4d.md)**: Learning 3D motion from internet stereo videos; cited among feed-forward approaches that fine-tune 3D reconstruction models.
- **[VGGT](../reconstruction/vggt.md)**: Visual geometry grounded transformer; the 3D reconstruction backbone underlying the concurrent V-DPM comparison.
- **[DUSt3R](../foundation/dust3r.md)**: Geometric pairwise pointmap foundation; representative of the static multi-view reconstruction models that prior feed-forward trackers fine-tune.

## 📚 Key Takeaways

1. **First video-DiT dense 3D tracker**: repurposes a Wan 2.1 video diffusion transformer with LoRA into a single-pass reference-anchored 3D tracker.
2. **Two enabling designs**: dual-latent representation (geometry + first-frame track latents) and temporal RoPE alignment jointly convert frame-anchored generation into reference-anchored tracking.
3. **State-of-the-art with efficiency**: best average AJ/APD3D/OA on standard sparse and dense benchmarks, at 1.3× faster / 4.6× less peak memory than DELTAv2.
4. **Honest trade-offs**: with weaker ViPE geometry it trails DELTAv2 + DA3 on average APD3D and on Kubric AJ; V-DPM still edges it on average APD3D — the strong DA3 geometry is what secures the overall lead.

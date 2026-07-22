# OmniX: Any-view and Any-time 4D Reconstruction via Feed-forward Trajectory Fields (ECCV 2026)

![omnix — architecture](https://arxiv.org/html/2607.10840v1/x1.png)

_Framework of OmniX (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Yanqin Jiang, Tengfei Wang, Zhengwei Wang, Chenjie Cao, Junta Wu, Wenhan Luo, Weiming Hu, Jin Gao, Chunchao Guo
- **Institution**: MAIS, Institute of Automation, Chinese Academy of Sciences; School of Artificial Intelligence, University of Chinese Academy of Sciences; Tencent Hunyuan; HKUST; Beijing Key Laboratory of Super Intelligent Security of Multi-Modal Information; School of Information Science and Technology, ShanghaiTech University
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.10840) | [Project Page](https://omnix4d.github.io/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward 4D reconstruction framework that predicts dense per-pixel 3D point trajectories from videos with large camera motion by disentangling dynamic foreground motion — parameterized by a small set of dynamic tokens through Sparse Spatiotemporal Attention — from static geometry prediction.

## 🎯 Key Contributions

1. **Disentangled 4D reconstruction under large camera motion**: OmniX separates dynamic motion modeling from static geometry prediction, making it robust to large viewpoint changes and temporally discontinuous inputs (single video, multi-video, or image–video combinations).
2. **Sparse Spatiotemporal Attention (SSA)**: Exploiting the sparse, low-rank structure of 3D motion, a small set of selected dynamic tokens parameterizes trajectory fields for all pixels across views and time, keeping global attention efficient.
3. **Deformable Trajectory Sampling Head (DTSH)**: A DPT-based deformable sampling head upsamples the sparse trajectory field into per-pixel trajectory transformations while keeping the dynamic-token selection differentiable.
4. **UE5-based 4D data engine**: An automatic Unreal Engine 5 pipeline synthesizes dynamic scenes and renders them with a customized multi-camera system, producing a dataset of 80K scenes and ~1.28M multi-view videos with depth, camera poses, and dense 3D point trajectory annotations.

## 🔧 Technical Details

### Formulation

Each image is associated with a depth map, a camera ray map, and camera parameters `v = (t, q, f)`; a 3D point is recovered as `P = t + D(u,v)·d`. For 4D geometry, every 3D point's trajectory across timestamps is modeled by a per-frame trajectory transformation `τ = [A | b]` (rotation and translation). Driven by motion sparsity, the per-pixel transformation is a weighted combination of `K` trajectory transformation bases (the trajectory field), with learned combination weights.

### Architecture

Built upon feed-forward 3D reconstruction models — the paper states OmniX is built on **DepthAnything3** — OmniX has three components: a transformer backbone, a DPT head for 3D geometry (depth, ray maps, camera), and a trajectory module for 4D geometry.

- **SSA**: An MLP predicts a per-token dynamic probability and selects the top-ρ% tokens as dynamic tokens. These are expanded along the temporal dimension with sinusoidal temporal embeddings (video index + local frame index), modulated by per-token coefficients (Eq. 4). Expanded tokens act as queries in stacked spatiotemporal cross-attention blocks, attending to all image tokens to predict trajectory transformation bases. Self-attention among query tokens is omitted (found to give negligible benefit).
- **Sparse trajectory field**: Predicted bases (channel `c = 9`: 6D rotation + 3D translation) are scattered back to their 2D spatial token positions, forming a sparse field for grid-based sampling.
- **DTSH**: Aggregates the sparse field via a statistical branch (temporal mean/variance) and a salient branch (per-field projection + temporal max pooling), concatenates with image tokens and dynamic scores, and predicts multi-scale deformable sampling offsets and weights. A dynamic score `θ` gates the final trajectory so background points stay static.

### Training

- **Losses**: Confidence-aware regression losses on depth, ray map, and trajectory (Eq. 13–14); a depth gradient loss; a Huber loss for camera pose; and BCE regularization on token-level and pixel-level dynamic score maps (used only when ground-truth dynamic masks are available).
- **Setup**: 8 SSA blocks, dynamic-mask loss weight 0.01, resolution 280 × 504, sequence length 16 frames (generalizes to 32+ at inference). AdamW, learning rate 2e-4, ~64k steps on 64 GPUs (batch size 1/GPU), ~12 days total. Uses the custom UE dataset plus eight public datasets (DynamicReplica, PointOdyssey, Spring, OmniGame, HOI4D, Waymo, DL3DV, Stereo4D).

## 📊 Results

Evaluation covers dense 3D point trajectory prediction (on the paper's own validation benchmark: 600 videos from 40 scenes), sparse 3D point tracking (TAPVid-3D), video depth (KITTI), camera pose (Sintel, TUM-dynamics), and efficiency. Metrics: APD3D (Average Point Distance, ↑), EPE (End-Point Error, ↓), computed for foreground points (FG) and all points (ALL).

### Dense 3D Point Trajectory Prediction — APD3D↑

원논문 Table 1. Higher APD3D↑ is better. TraceAnything only reports first-frame metrics (no camera parameters). "Ours" is trained on 9 datasets; VDPM on 4 (incl. unreleased Kubric-G); TraceAnything on its custom engine.

| Method        | Eval Type   | Mono FG↑ | Mono ALL↑ | Disjoint FG↑ | Disjoint ALL↑ | Hybrid FG↑ | Hybrid ALL↑ |
| ------------- | ----------- | -------- | --------- | ------------ | ------------- | ---------- | ----------- |
| TraceAnything | first frame | 0.062    | 0.043     | 0.059        | 0.037         | 0.030      | 0.027       |
| VDPM          | first frame | 0.187    | 0.120     | 0.164        | 0.114         | 0.146      | 0.117       |
| **Ours**      | first frame | 0.284    | 0.391     | 0.322        | 0.444         | 0.332      | 0.456       |
| VDPM          | all frames  | 0.199    | 0.118     | 0.143        | 0.093         | 0.135      | 0.104       |
| **Ours**      | all frames  | 0.300    | 0.381     | 0.305        | 0.406         | 0.316      | 0.400       |

### Dense 3D Point Trajectory Prediction — EPE↓

원논문 Table 1. Lower EPE↓ is better.

| Method        | Eval Type   | Mono FG↓ | Mono ALL↓ | Disjoint FG↓ | Disjoint ALL↓ | Hybrid FG↓ | Hybrid ALL↓ |
| ------------- | ----------- | -------- | --------- | ------------ | ------------- | ---------- | ----------- |
| TraceAnything | first frame | 0.354    | 0.316     | 0.380        | 0.343         | 0.521      | 0.447       |
| VDPM          | first frame | 0.338    | 0.287     | 0.341        | 0.306         | 0.458      | 0.405       |
| **Ours**      | first frame | 0.133    | 0.116     | 0.101        | 0.094         | 0.146      | 0.133       |
| VDPM          | all frames  | 0.332    | 0.282     | 0.345        | 0.305         | 0.341      | 0.306       |
| **Ours**      | all frames  | 0.133    | 0.116     | 0.113        | 0.105         | 0.132      | 0.121       |

### Sparse 3D Point Tracking — TAPVid-3D

원논문 Table 2. APD3D↑ / EPE↓ on 16-frame clips. OmniX is best on all three datasets.

| Method           | ADT APD3D↑ | ADT EPE↓ | DriveTrack APD3D↑ | DriveTrack EPE↓ | PStudio APD3D↑ | PStudio EPE↓ |
| ---------------- | ---------- | -------- | ----------------- | --------------- | -------------- | ------------ |
| SpatialTrackerV2 | 0.236      | 0.193    | 0.197             | 1.651           | 0.107          | 0.149        |
| St4RTrack        | 0.202      | 0.259    | 0.124             | 1.906           | 0.099          | 0.191        |
| TraceAnything    | 0.069      | 0.297    | 0.113             | 2.638           | 0.097          | 0.189        |
| VDPM             | 0.266      | 0.162    | 0.228             | 1.576           | 0.118          | 0.141        |
| **Ours**         | 0.367      | 0.134    | 0.256             | 1.490           | 0.141          | 0.156        |

### Video Depth Estimation — KITTI

원논문 Table 3. 16-frame clips. Abs Rel↓ (lower better), δ<1.25↑ (higher better).

| Method           | Abs Rel↓ | δ<1.25↑ |
| ---------------- | -------- | ------- |
| VGGT4D           | 0.041    | 0.972   |
| PAGE4D           | 0.031    | 0.982   |
| π3               | 0.032    | 0.990   |
| SpatialTrackerV2 | 0.049    | 0.981   |
| DepthAnythingV3  | 0.039    | 0.987   |
| **Ours**         | 0.024    | 0.990   |

OmniX achieves the best Abs Rel↓ (0.024) and ties π3 for the best δ<1.25↑ (0.990).

### Camera Pose Estimation

원논문 Table 4. 16-frame clips. All metrics lower-the-better (ATE↓, RPEtrans↓, RPErot↓).

| Method           | Sintel ATE↓ | Sintel RPEtrans↓ | Sintel RPErot↓ | TUM ATE↓ | TUM RPEtrans↓ | TUM RPErot↓ |
| ---------------- | ----------- | ---------------- | -------------- | -------- | ------------- | ----------- |
| VGGT4D           | 0.321       | 0.322            | 1.165          | 0.011    | 0.014         | 0.461       |
| SpatialTrackerV2 | 0.186       | 0.236            | 1.645          | 0.037    | 0.042         | 1.067       |
| PAGE4D           | 0.350       | 0.262            | 1.182          | 0.022    | 0.024         | 0.716       |
| VDPM             | 0.231       | 0.234            | 1.048          | 0.157    | 0.018         | 0.517       |
| π3               | 0.157       | 0.174            | 0.627          | 0.016    | 0.016         | 0.511       |
| DepthAnythingV3  | 0.252       | 0.299            | 0.710          | 0.010    | 0.013         | 0.458       |
| **Ours**         | 0.108       | 0.152            | 0.722          | 0.010    | 0.014         | 0.472       |

OmniX wins Sintel ATE↓ and RPEtrans↓, but π3 has the best Sintel RPErot↓ (0.627 vs 0.722), and DepthAnythingV3 leads on TUM RPEtrans↓ / RPErot↓ (Ours ties it on TUM ATE↓ at 0.010).

### Inference Efficiency

원논문 Table 5. 16-frame clips. TraceAnything is the most efficient (simplest architecture); OmniX is second-best in runtime.

| Method                 | FLOPs (T) | Params (M) | Memory (MB) | Runtime (s) |
| ---------------------- | --------- | ---------- | ----------- | ----------- |
| St4RTrack              | 629.52    | 575.4      | 3273        | 20.59       |
| VDPM                   | 333.72    | 1660.0     | 15749       | 11.70       |
| TraceAnything          | 8.79      | 674.5      | 12613       | 1.05        |
| Ours w/o sparse design | 15.25     | 568.7      | 23727       | 4.10        |
| **Ours**               | 12.07     | 568.7      | 21999       | 2.15        |

The sparse design lowers FLOPs (15.25→12.07 T), memory (23727→21999 MB), and runtime (4.10→2.15 s) versus the dense variant. OmniX uses more memory than TraceAnything because it predicts all trajectories in a single forward pass rather than an inference-time shortcut.

### Ablation — SSA components (foreground APD3D↑)

원논문 Table 6. Foreground APD3D↑ on the custom UE dataset. Removing cross-attention causes a drastic drop; self-attention among query tokens adds little.

| Variant                                 | Mono APD3D↑ | Disjoint APD3D↑ | Hybrid APD3D↑ |
| --------------------------------------- | ----------- | --------------- | ------------- |
| AdaLN-embed (+ SelfAttn + CrossAttn)    | 0.260       | 0.267           | 0.291         |
| Eq.(4)-embed + SelfAttn + CrossAttn     | 0.293       | 0.298           | 0.324         |
| Eq.(4)-embed + SelfAttn (w/o CrossAttn) | 0.171       | 0.197           | 0.205         |
| Eq.(4)-embed + CrossAttn (**Ours**)     | 0.297       | 0.298           | 0.324         |

### Ablation — top-ρ% and data scaling

원논문 Table 7 (top-ρ%, 4-frame monocular videos) and 원논문 Table 8 (data scaling, 16-frame monocular videos). ρ = 20 is used for the final model.

| Top-ρ% | APD3D↑ |
| ------ | ------ |
| 10     | 0.3194 |
| 20     | 0.3356 |
| 30     | 0.3454 |

| Training Size | APD3D↑ |
| ------------- | ------ |
| 2.8k          | 0.182  |
| 6.9k          | 0.210  |
| 13.9k         | 0.243  |

## 💡 Insights & Impact

- **Disentanglement is the key to large camera motion**: Prior dense-trajectory methods (TraceAnything, VDPM) are trained mostly on small-motion monocular video, and their all-point results degrade on disjoint/hybrid inputs because inaccurate camera estimation projects background points out of view. Explicitly separating motion from geometry lets OmniX post large gains on Disjoint Video Pairs and Hybrid Image-video Sets, and on the large-motion ADT dataset.
- **Motion is sparse and low-rank**: A small set of dynamic tokens (top-ρ% = 20) can parameterize per-pixel trajectory fields for all images, making dense trajectory prediction feasible in one forward pass.
- **Self-attention among query tokens is redundant** in this module — removing it improves efficiency with negligible accuracy loss, while cross-attention to image tokens is essential (removing it collapses foreground motion prediction).
- **Data scaling helps**: foreground APD3D rises monotonically with training set size (0.182 → 0.210 → 0.243), motivating the large UE5 data engine.

## 🔗 Related Work

- **[DepthAnything3](../reconstruction/depth-anything-3.md)**: The feed-forward 3D reconstruction backbone OmniX is built upon; also a baseline in the depth and pose tables.
- **[DUSt3R](../foundation/dust3r.md)**: The pioneering feed-forward dense point-map foundation the field builds on.
- **[VGGT](../reconstruction/vggt.md)** / **[Fast3R](../reconstruction/fast3r.md)** / **[MapAnything](../reconstruction/mapanything.md)** / **[WorldMirror](../reconstruction/worldmirror.md)**: All-to-all attention feed-forward reconstruction lineage cited as scalability precursors.
- **[π3](../reconstruction/pi3.md)**: Permutation-equivariant geometry model used as a depth and pose baseline.
- **[MonST3R](./monst3r.md)** / **[CUT3R](./cut3r.md)**: Per-frame dynamic-scene reconstruction that predicts point clouds without explicit cross-time correspondence.
- **[VGGT4D](./vggt4d.md)** / **[PAGE-4D](./page-4d.md)** / **[Any4D](./any4d.md)**: Feed-forward 4D reconstruction baselines (VGGT4D and PAGE-4D appear in the depth/pose tables).
- **[V-DPM](./v-dpm.md)**: Dynamic-point-maps method that predicts both camera parameters and dense trajectories; a primary comparison baseline.
- **[D4RT](./d4rt.md)**: A flexible-querying dense dynamic reconstruction method cited as a strong but non-open-sourced approach.
- **[Stereo4D](./stereo4d.md)**: One of the eight public datasets used to augment training.

## 📚 Key Takeaways

1. **Trajectory fields, not per-frame point clouds**: OmniX outputs dense per-pixel 3D point trajectories across all images in one pass, adding temporal correspondence to feed-forward reconstruction.
2. **Sparse dynamic tokens + cross-attention** (SSA) plus a **deformable sampling head** (DTSH) make dense trajectory prediction efficient and differentiable.
3. **State-of-the-art on trajectory prediction and TAPVid-3D tracking**, with competitive (not always winning) video depth and camera pose — OmniX trails π3 on Sintel RPErot and DepthAnythingV3 on TUM rotation metrics.
4. **UE5 data engine** (80K scenes, ~1.28M multi-view videos) supplies the large-camera-motion 4D supervision that prior methods lacked.

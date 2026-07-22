# ARTDECO: Towards Efficient and High-Fidelity On-the-Fly 3D Reconstruction with Structured Scene Representation (ICLR 2026)

![artdeco — architecture](https://arxiv.org/html/2510.08551/x1.png)

_ARTDECO delivers high-fidelity, interactive 3D reconstruction from monocular images, combining efficiency with robustness across indoor and outdoor… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Guanghao Li, Kerui Ren, Linning Xu, Zhewen Zheng, Changjian Jiang, Xin Gao, Bo Dai, Jian Pu, Mulin Yu, Jiangmiao Pang
- **Institution**: Shanghai Artificial Intelligence Laboratory, Fudan University, Shanghai Innovation Institute, Shanghai Jiao Tong University, The Chinese University of Hong Kong, Carnegie Mellon University, Zhejiang University, The University of Hong Kong
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.08551) | [Project Page](https://city-super.github.io/artdeco/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A streaming SLAM-style system that uses 3D foundation models (MASt3R for tracking, π³ for loop detection) as modular priors and decodes multi-scale features into a hierarchical, LoD-aware 3D Gaussian representation, targeting SLAM-level speed with near per-scene-optimization rendering quality.

## 🎯 Key Contributions

1. **Unified localization + reconstruction + rendering pipeline** designed to run on-the-fly across indoor and outdoor environments rather than optimizing one axis at the expense of the others.
2. **Foundation models as modular SLAM components**: MASt3R instantiates the matching/tracking module; π³ instantiates the loop-detection module. Neither is used as the whole system — they are drop-in priors inside a classical frontend/backend/mapping decomposition.
3. **Hierarchical semi-implicit Gaussian representation with LoD-aware densification**, giving a principled fidelity/efficiency trade-off for large navigable scenes instead of post-hoc anchor pruning or unstructured multi-scale Gaussians.
4. **All frames used, differently**: keyframes and mapper frames insert new Gaussians; common frames only refine existing ones through gradient updates. Prior 3DGS-SLAM systems use keyframes alone.
5. **Reprojection-based pointmap confidence** replacing MASt3R's own predicted confidence, computed by projecting a pointmap onto the `N_c` highest-ASMK-scoring previous keyframes.

## 🔧 Technical Details

### System decomposition

Given monocular RGB frames `{I_i}` with or without known intrinsics, ARTDECO estimates poses `{R_i | t_i}` and Gaussian primitives `{G_j}` in three streaming modules.

**Frontend.** MASt3R produces frame-wise pointmaps, confidences, and pixel correspondences against the latest keyframe. Following MASt3R-SLAM, current-frame 3D points are projected into the keyframe image plane and the relative pose `T_KC ∈ SIM(3)` is solved by Gauss–Newton on reprojection residuals. Because MASt3R is unstable near object boundaries, residuals are weighted by a local covariance `Σ_c` estimated from neighbors within radius δ. Unknown focal length is initialized by GeoCalib and jointly refined.

Frames are then categorized three ways:

- **Keyframe** — valid correspondences with the latest keyframe fall below `τ_k`
- **Mapper frame** — 70th-percentile pixel displacement from the latest keyframe exceeds `τ_m`, i.e. enough parallax for multi-view reconstruction
- **Common frame** — neither; used only to refine existing detail

**Backend.** ASMK gives an initial loop hypothesis (score above `τ_loop`, at least `k_loop` keyframes apart). π³ then processes the current frame plus the top `N_a` ASMK candidates and selects the three most geometrically consistent keyframes by angular error. These are wired into a factor graph and a PnP-based global BA refines poses.

**Mapping.** New Gaussians are inserted only where refinement is needed, using a Laplacian-of-Gaussian insertion probability that compares ground-truth against rendered image:

```text
P_a(u,v) = max( min(‖∇²(G_σ) * I(u,v)‖, 1) − min(‖∇²(G_σ) * Ĩ(u,v)‖, 1), 0 )
```

A Gaussian is added when `P_a(u,v) > τ_a`. Each primitive stores center μ, SH, opacity, base scale `S_b`, local feature `f_l`, `d_max`, and voxel index `v_id`. Opacity is initialized to `0.2 · C(u,v)`, down-weighting low-confidence regions.

### Level-of-detail design

Gaussians are assigned a level `l < L`, level 0 finest. A level-`l` Gaussian covers a `2^{2l}`-pixel patch of the original image; frames are downsampled `L−1` times and Gaussians initialized from both scales. Base scale is weighted by `1.4^{2l}` and each Gaussian carries `d_max = d · 2^{2l}`.

At render time with viewing distance `d_r`:

- `d_r ≤ d_max` → included
- `d_max < d_r ≤ 2·d_max` → faded, `α = (d − d_max)/d_max`
- `d_r > 2·d_max` → excluded

The paper sets **L = 4**.

### Semi-implicit parameterization

Scale and rotation are decoded rather than stored directly:

```text
S = S_b · MLP_s(f_r ⊕ f_l)     R = MLP_r(f_r ⊕ f_l)
```

where `f_l` is a per-Gaussian feature initialized to zero and `f_r` is a voxel-level region feature (space voxelized with cell size ε). This hybrid region–individual design is what "semi-implicit" refers to.

### Training

Streaming: `K` iterations per mapper/keyframe arrival (with insertion), `K/2` per common frame (no insertion). Training frames are sampled 0.2 from the current frame and 0.8 from past frames to avoid local overfitting. After the stream, a global optimization pass runs over all frames with higher sampling weight on under-updated ones, and camera poses are optimized jointly with Gaussian parameters.

### Evaluation setup

Intel Core i9-14900K + NVIDIA RTX 4090. Every 8th frame is held out for evaluation — excluded from mapping, but its pose is still estimated and optimized. Eight benchmarks: TUM (11 scenes), ScanNet++ (14), VR-NeRF (8), ScanNet (6) indoors, 32–5577 frames; KITTI (8), Waymo (9), Fast-LIVO2 (5), MatrixCity (1) outdoors, 200–1363 frames.

## 📊 Results

### Rendering — indoor benchmarks

원논문 Table 1. \*는 대다수 씬에서만 성공, –는 대다수 실패를 뜻하며 완전히 성공한 방법끼리만 비교한다.

| Method       | ScanNet++ PSNR ↑ | SSIM ↑    | LPIPS ↓   | ScanNet PSNR ↑ | SSIM ↑    | LPIPS ↓   | Training Time ↓ |
| ------------ | ---------------- | --------- | --------- | -------------- | --------- | --------- | --------------- |
| MonoGS       | 16.71            | 0.682     | 0.600     | 18.87\*        | 0.780\*   | 0.629\*   | 14.08 min       |
| S3PO-GS      | 22.94            | 0.820     | 0.355     | 20.14          | 0.797     | 0.558     | 41.25 min       |
| SEGS-SLAM    | -                | -         | -         | 19.73\*        | 0.839\*   | 0.365\*   | 10.84 min       |
| OnTheFly-NVS | 18.01            | 0.761     | 0.386     | 15.36          | 0.708     | 0.494     | **2.29 min**    |
| LongSplat    | 24.94\*          | 0.827\*   | 0.260\*   | 19.27\*        | 0.754\*   | 0.404\*   | 442.96 min      |
| **Ours**     | **29.12**        | **0.918** | **0.167** | **24.10**      | **0.865** | **0.271** | 5.33 min        |

원논문 Table 1 (계속) — TUM·VR-NeRF.

| Method       | TUM PSNR ↑ | SSIM ↑    | LPIPS ↓   | VR-NeRF PSNR ↑ | SSIM ↑      | LPIPS ↓     |
| ------------ | ---------- | --------- | --------- | -------------- | ----------- | ----------- |
| MonoGS       | 17.78      | 0.602     | 0.573     | 13.88          | 0.560       | 0.420       |
| S3PO-GS      | 19.62      | 0.656     | 0.466     | 12.43          | 0.642       | 0.497       |
| SEGS-SLAM    | 19.69\*    | 0.743\*   | 0.307\*   | **31.62**\*    | **0.896**\* | **0.232**\* |
| OnTheFly-NVS | 19.72      | 0.719     | 0.380     | 27.30          | 0.872       | 0.310       |
| LongSplat    | 25.09      | 0.804     | 0.272     | 25.74\*        | 0.832\*     | 0.321\*     |
| **Ours**     | **26.18**  | **0.850** | **0.224** | 28.57          | 0.895       | 0.242       |

**ARTDECO loses VR-NeRF to SEGS-SLAM on all three metrics** (28.57 vs 31.62 PSNR), though SEGS-SLAM is marked as succeeding only on a majority of scenes there.

### Rendering — outdoor benchmarks

원논문 Table 1.

| Method       | KITTI PSNR ↑ | SSIM ↑    | LPIPS ↓   | Waymo PSNR ↑ | SSIM ↑    | LPIPS ↓ | Training Time ↓ |
| ------------ | ------------ | --------- | --------- | ------------ | --------- | ------- | --------------- |
| MonoGS       | 14.56        | 0.489     | 0.767     | 19.34        | 0.752     | 0.627   | 16.52 min       |
| S3PO-GS      | 19.97        | 0.645     | 0.410     | 27.28        | 0.865     | 0.352   | 34.89 min       |
| SEGS-SLAM    | 14.03        | 0.463     | 0.488     | 19.01\*      | 0.698\*   | 0.502\* | 8.75 min        |
| OnTheFly-NVS | 16.89        | 0.579     | 0.471     | 25.53        | 0.820     | 0.360   | **0.74 min**    |
| LongSplat    | 16.86        | 0.532     | 0.447     | 25.61        | 0.795     | 0.326   | 313.60 min      |
| **Ours**     | **23.17**    | **0.765** | **0.299** | **28.75**    | **0.880** | 0.276   | 6.58 min        |

ARTDECO leads all three metrics on both KITTI and Waymo here.

원논문 Table 1 (계속) — Fast-LIVO2·MatrixCity.

| Method       | Fast-LIVO2 PSNR ↑ | SSIM ↑    | LPIPS ↓   | MatrixCity PSNR ↑ | SSIM ↑    | LPIPS ↓   |
| ------------ | ----------------- | --------- | --------- | ----------------- | --------- | --------- |
| MonoGS       | 18.87             | 0.598     | 0.699     | 19.36             | 0.593     | 0.736     |
| S3PO-GS      | 21.51             | 0.684     | 0.445     | 21.76             | 0.661     | 0.584     |
| SEGS-SLAM    | 24.58\*           | 0.773\*   | 0.307\*   | 25.57             | 0.784     | 0.366     |
| OnTheFly-NVS | 18.76             | 0.618     | 0.497     | 21.36             | 0.687     | 0.451     |
| LongSplat    | 26.37             | 0.792     | 0.276     | -                 | -         | -         |
| **Ours**     | **29.54**         | **0.894** | **0.158** | 25.62             | **0.790** | **0.327** |

MatrixCity is essentially a tie with SEGS-SLAM (25.62 vs 25.57 PSNR).

On runtime the paper is explicit: ARTDECO "runs faster than all except OnTheFly-NVS, with its extra time cost primarily from pose estimation."

### Tracking (ATE RMSE ↓)

원논문 Table 2. 상단은 3DGS 기반 방법과의 비교, 하단은 TUM에서 non-3DGS SLAM 시스템과의 비교(MASt3R-SLAM을 따라 TUM fr1의 9개 씬).

| Dataset   | MonoGS | S3PO-GS | SEGS-SLAM | MASt3R-SLAM | OnTheFly-NVS | LongSplat | **Ours**  |
| --------- | ------ | ------- | --------- | ----------- | ------------ | --------- | --------- |
| ScanNet++ | 1.217  | 0.632   | 0.245     | 0.025       | 0.891        | 0.602     | **0.018** |
| TUM       | 0.244  | 0.117   | 0.073\*   | 0.031       | -            | -         | **0.025** |
| Waymo     | 7.370  | 1.236   | -         | -           | 3.118        | 4.956     | **1.213** |

원논문 Table 2 하단 — TUM, non-3DGS SLAM 시스템 대비.

| Metric   | ORB-SLAM3 | DPV-SLAM++ | DROID-SLAM | Go-SLAM | MASt3R-SLAM | **Ours**  |
| -------- | --------- | ---------- | ---------- | ------- | ----------- | --------- |
| ATE RMSE | -         | 0.054      | 0.038      | 0.035   | 0.030       | **0.028** |

The margin over MASt3R-SLAM is real but small (0.028 vs 0.030 on TUM; 0.018 vs 0.025 on ScanNet++), and on Waymo ARTDECO barely edges S3PO-GS (1.213 vs 1.236).

### Ablations on ScanNet++

원논문 Table 3. 상단은 localization(ATE RMSE ↓), 하단은 rendering.

| Front & Backend | Full      | w/ SLAM (MASt3R → π³) | w/ Loop (π³ → VGGT) | w/o loop | w/ dense key frame |
| --------------- | --------- | --------------------- | ------------------- | -------- | ------------------ |
| ATE RMSE ↓      | **0.018** | 0.374                 | 0.096               | 0.057    | 0.094              |

Three findings, all against intuition:

- Swapping the tracking backbone from MASt3R to **π³ makes tracking ~20× worse** (0.018 → 0.374). The paper's explanation: π³ trains on more diverse data but lacks metric scale, while MASt3R better preserves consistent object proportions under varying viewpoints.
- Swapping the loop-detection module from π³ to **VGGT** degrades ATE to 0.096.
- **Denser keyframes hurt** (0.094). 3D foundation models struggle with small-parallax input, producing ghosting and blur that corrupt point clouds and correspondences.

| Mapper  | Full      | w/o LoD | w/o implicit structure | w/o global feat | w/o mapper frame | w/o common frame |
| ------- | --------- | ------- | ---------------------- | --------------- | ---------------- | ---------------- |
| PSNR ↑  | **29.12** | 28.13   | 28.54                  | 27.95           | 26.38            | 27.20            |
| SSIM ↑  | **0.918** | 0.912   | 0.914                  | 0.910           | 0.898            | 0.904            |
| LPIPS ↓ | **0.167** | 0.180   | 0.175                  | 0.197           | 0.229            | 0.211            |

The largest single rendering contributor is **mapper frames** (−2.74 PSNR without them), i.e. the frame-categorization idea matters more than any representation trick.

### Not reproduced here

The paper reports per-scene PSNR/SSIM/LPIPS in appendix Tables 4–24 and per-scene tracking in Tables 25–29 across Fast-LIVO2, TUM, ScanNet, Waymo, VR-NeRF, KITTI, and ScanNet++. Those are omitted here for size; consult the original appendix. Figure 1's teaser numbers appear only as figure annotations and are not reproduced.

## 💡 Insights & Impact

### Foundation models as parts, not as the system

The most transferable result in this paper is the ablation table. A great deal of recent work treats "swap in the newest 3D foundation model" as a monotone improvement. ARTDECO shows the choice is task-specific: MASt3R's metric-scale behavior is essential for the _tracking_ role, while π³'s multi-image reasoning is the better _loop-detection_ module — and using either for the other's job costs real accuracy. VGGT as loop detector is also worse than π³ here.

### Small parallax is a foundation-model failure mode

"w/ dense key frame" degrading ATE from 0.018 to 0.094 is a concrete counterexample to "more frames is more information." Feeding an overly dense sequence to a 3D foundation model produces ghosting and blurred pointmaps. Classical SLAM keyframe selection heuristics exist for a reason and remain load-bearing.

### LoD belongs in the representation, not in a post-process

Prior scale handling was either post-hoc anchor pruning (boundary artifacts, memory cost) or unstructured multi-scale Gaussians (no explicit organization). Attaching `d_max` to each primitive at initialization and fading opacity between `d_max` and `2·d_max` gives continuous, flicker-free LoD as a property of the primitive rather than a rendering hack.

### The efficiency position

ARTDECO sits between OnTheFly-NVS (0.74–2.29 min, but 15–18 PSNR on hard scenes) and LongSplat (313–443 min). At 5.33/6.58 min it is roughly 60–80× faster than LongSplat while scoring higher on every benchmark where LongSplat fully succeeds — the paper attributes the residual cost above OnTheFly-NVS to pose estimation, and justifies it with Table 2.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md) — instantiates the matching/tracking module; the ablation shows it cannot be freely substituted
- [MASt3R-SLAM](../reconstruction/mast3r-slam.md) — the tracking formulation ARTDECO follows, and its strongest ATE competitor
- [π³](../reconstruction/pi3.md) — instantiates the loop-detection module
- [VGGT](../reconstruction/vggt.md) — evaluated as an alternative loop-detection backbone and found worse than π³ here
- [DUSt3R](../foundation/dust3r.md) — origin of the pointmap prior this pipeline consumes
- [InstantSplat](instantsplat.md) — related feed-forward-prior + Gaussian optimization hybrid
- [DAS3R](das3r.md) and [PreF3R](pref3r.md) — other DUSt3R-family Gaussian reconstruction entries

## 📚 Key Takeaways

1. **Which foundation model, for which module, matters enormously.** MASt3R → π³ for tracking costs 0.018 → 0.374 ATE; π³ → VGGT for loop detection costs 0.018 → 0.096.
2. **Frame triage is the biggest rendering lever.** Removing mapper frames costs 2.74 PSNR — more than LoD, implicit structure, or global features combined.
3. **Denser input can be worse.** Small-parallax frames corrupt foundation-model pointmaps; keyframe thresholds are load-bearing, not legacy.
4. **LoD as a per-primitive attribute** (`d_max`, with opacity fade over `d_max` → `2·d_max`) delivers scalable rendering without post-hoc pruning artifacts.
5. **State of the art on 7 of 8 benchmarks, honestly not on VR-NeRF**, where SEGS-SLAM leads by 3 PSNR, and effectively tied on MatrixCity.

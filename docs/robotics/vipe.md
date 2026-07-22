# ViPE: Video Pose Engine for 3D Geometric Perception (arXiv preprint)

![vipe — method](https://research.nvidia.com/labs/toronto-ai/vipe/assets/images/method.png)

_메소드 개요 (저자 project page)_

## 📋 Overview

- **Authors**: Jiahui Huang, Qunjie Zhou, Hesam Rabeti, Aleksandr Korovko, Huan Ling, Xuanchi Ren, Tianchang Shen, Jun Gao, Dmitry Slepichev, Chen-Hsuan Lin, Jiawei Ren, Kevin Xie, Joydeep Biswas, Laura Leal-Taixe, Sanja Fidler
- **Institution**: NVIDIA
- **Venue**: arXiv preprint (2025-08)
- **Note**: 자체 페이지가 "NVIDIA Research Whitepaper 2025"로 표기 — 학회 논문이 아니다. <https://research.nvidia.com/labs/toronto-ai/vipe/>
- **Links**: [Paper](https://arxiv.org/abs/2508.10934) | [Project Page](https://research.nvidia.com/labs/toronto-ai/vipe/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A keyframe-based dense bundle adjustment engine that fuses learned flow, sparse keypoint tracks, and depth priors to annotate unconstrained videos with camera intrinsics, poses, and near-metric depth — used to release ~96 M annotated frames.

## 🎯 Key Contributions

1. **Hybrid SLAM/learned pipeline**: ViPE keeps the scalability of a classical keyframe BA back-end while replacing hand-crafted correspondence with learned dense flow and learned depth priors.
2. **Three-term BA energy**: dense flow, sparse keypoint, and depth regularization terms are optimized jointly for poses, intrinsics, and low-resolution depth.
3. **Diverse camera model support**: pinhole, wide-angle, and 360° panoramic video are all handled, with intrinsics jointly optimized rather than assumed.
4. **Dynamic-object robustness**: movable objects are segmented and down-weighted so they do not corrupt camera estimation.
5. **Large-scale dataset release**: Dynpose-100K++ (~100 K real internet videos), Wild-SDG-1M (1 M AI-generated videos), and Web360 (2 K panoramic videos), totaling approximately 96 M annotated frames.

## 🔧 Technical Details

### Pipeline

The system follows a DROID-SLAM-style keyframe architecture:

1. **Intrinsics initialization** — 4 uniformly sampled frames are run through GeoCalib.
2. **Keyframe selection** — motion to the previous keyframe is estimated from weighted optical flow plus sparse keypoint tracks; exceeding a threshold triggers a new keyframe in the BA graph `G = (V, E)`.
3. **Frontend tracking** — a graph over a small sliding window of recent keyframes, connected by temporal proximity or high co-visibility, optimized with Gauss-Newton.
4. **Backend optimization** — full BA over all current keyframes, with intrinsics unlocked. Triggered when the keyframe count reaches 8, 16, and 64, and at the end of frontend tracking.
5. **Pose infilling** — non-keyframes get a small local graph connecting to their two closest keyframes, with uni-directional edges only, so metric depth is not needed for every frame. Applied in parallel.
6. **Dense depth estimation** — a full-resolution depth map consistent with the recovered pose and intrinsics.

### BA formulation

The energy over poses `T_i ∈ SE(3)`, intrinsics `k`, and per-keyframe low-resolution depth `D_i` is:

```text
e_ViPE = Σ_(i,j)∈E e_dense + Σ_(i,j)∈E e_sparse + α · Σ_i∈V e_depth
```

- **Dense flow constraint** (`e_dense`): the DROID-SLAM reprojection residual against a network-regressed flow `F_ij`, summed over an `h × w` grid with `h = H/8`, `w = W/8` to keep the unknown count manageable. A per-pixel weight map `w[u]` encodes both flow confidence and motion probability.
- **Sparse point constraint** (`e_sparse`): features from the CUDA-based cuVSLAM module — Shi-Tomasi corners tracked with Lucas-Kanade — computed at full image resolution, supplying sub-pixel constraints the low-resolution flow misses. To avoid a semi-sparse Hessian, bilinear interpolation of the depth map is replaced with a bilinear _splatting_ operation.
- **Depth regularization** (`e_depth`): a consistency and robustness term on the depth maps.

The system is minimized with Gauss-Newton using a factorized sparse solver with COLAMD reordering.

### Reported speed

The paper states ViPE runs at **3–5 FPS on a single GPU** for standard input resolutions, measured at 640×480 on an NVIDIA RTX 5090.

## 📊 Results

### Pose and intrinsics on TUM RGB-D

원논문 Table 1. Run time is measured on a single RTX 5090, excluding per-frame dense depth estimation where possible; sequences average ~950 frames.

| Method      | Fr1 ATE (cm) ↓ | Fr1 RTE (cm) ↓ | Fr1 RRE (°) ↓ | Fr1 Focal (°) ↓ | Fr3 ATE (cm) ↓ | Fr3 RTE (cm) ↓ | Fr3 RRE (°) ↓ | Fr3 Focal (°) ↓ | Run Time |
| ----------- | -------------- | -------------- | ------------- | --------------- | -------------- | -------------- | ------------- | --------------- | -------- |
| DROID-SLAM  | 4.4            | **0.6**        | 0.39          | 4.1             | 2.7            | 1.0            | 0.27          | 4.3             | ~2min    |
| MASt3R-SLAM | 6.8            | 2.3            | 0.54          | N/A             | 7.6            | 2.7            | 0.41          | N/A             | ~1.5min  |
| VGGT        | 8.4            | 0.8            | 0.44          | 11.1            | 12.9           | **0.5**        | 0.30          | 10.1            | ~4min    |
| MegaSAM     | 7.0            | **0.6**        | **0.37**      | 10.5            | **1.5**        | 0.8            | **0.26**      | 12.6            | ~15min   |
| **ViPE**    | **3.6**        | 0.7            | 0.39          | **1.8**         | **1.5**        | 0.8            | 0.27          | **0.6**         | ~3min    |

Freiburg1 is the static split, Freiburg3 the dynamic split. ViPE's headline advantage is intrinsics: 1.8° and 0.6° focal error versus 10.1–12.6° for the two feed-forward baselines.

### Pose and intrinsics on outdoor driving

원논문 Table 2. KITTI images are cropped to 512×368 and truncated to the first 1024 frames. RDS is a 64-sequence subset of the Real Driving Scene dataset resampled to focal lengths spanning 30–70 degrees.

| Method                   | KITTI ATE (m) ↓ | KITTI Focal (°) ↓ | RDS ATE (m) ↓ | RDS Focal (°) ↓ | Run Time |
| ------------------------ | --------------- | ----------------- | ------------- | --------------- | -------- |
| MASt3R-SLAM              | 122.2           | N/A               | 21.0          | N/A             | ~4min    |
| MASt3R-SLAM<sub>KF</sub> | 21.3            | N/A               | 9.5           | N/A             | -        |
| VGGT                     | 23.8            | **1.9**           | 5.7           | **5.9**         | ~3min    |
| MegaSAM                  | 25.4            | 2.3               | 9.3           | 47.7            | ~17min   |
| **ViPE**                 | **9.2**         | **1.9**           | **5.0**       | 7.9             | ~4.5min  |

VGGT was run with a sliding-window strategy (N = 120/200 frames, K = 5 overlap) with Sim(3) alignment on the top 50% confidence points, since it cannot ingest thousand-frame videos directly. Note ViPE does _not_ lead on RDS focal error — VGGT's 5.9° beats ViPE's 7.9°.

The abstract summarizes these two tables as outperforming existing uncalibrated pose estimation baselines by **18%/50% on TUM/KITTI sequences**.

### Depth estimation

원논문 Table 3. SINTEL uses 6 manually selected sequences; ETH3D excludes dark sequences, leaving 50 scenes.

| Method   | SINTEL RelAbs ↓ | SINTEL LogRMSE ↓ | SINTEL δ<sub>1.25</sub> ↑ | ETH3D RelAbs ↓ | ETH3D LogRMSE ↓ | ETH3D δ<sub>1.25</sub> ↑ |
| -------- | --------------- | ---------------- | ------------------------- | -------------- | --------------- | ------------------------ |
| DepthPro | 0.29            | 0.31             | 62.8                      | 0.31           | 0.37            | 64.4                     |
| UniDepth | 0.23            | 0.28             | 79.8                      | 0.19           | 0.27            | 72.1                     |
| VGGT     | 0.22            | 0.36             | 75.7                      | 0.20           | 0.28            | 69.9                     |
| MegaSAM  | 0.29            | 0.33             | 67.9                      | 0.23           | 0.28            | 64.9                     |
| **ViPE** | **0.21**        | **0.27**         | **80.8**                  | **0.16**       | **0.22**        | **81.7**                 |

The authors note honestly that monocular depth methods can score better on some metrics but exhibit non-negligible frame-to-frame jitter, which ViPE avoids via its video depth model.

### Ablation

원논문 Table 4, on OpenDV and VidBench, which are more representative of real-world casual video.

| e<sub>dense</sub> | e<sub>sparse</sub> | e<sub>depth</sub> | Masking | S-ATE (×10⁻²) ↓ | S-RTE (×10⁻⁴) ↓ | S-RRE (°) ↓ | S-Focal (°) ↓ | Sampson (px) ↓ |
| ----------------- | ------------------ | ----------------- | ------- | --------------- | --------------- | ----------- | ------------- | -------------- |
| ✓                 |                    |                   |         | 1.39            | 4.40            | 0.04        | 5.28          | 1.40           |
| ✓                 |                    | ✓                 |         | 1.40            | 4.45            | 0.04        | 5.20          | 1.36           |
| ✓                 | ✓                  | ✓                 |         | 1.35            | 4.21            | 0.04        | 5.00          | 0.84           |
| ✓                 |                    | ✓                 | ✓       | 1.13            | 4.10            | **0.03**    | 4.45          | 0.96           |
| ✓                 | ✓                  | ✓                 | ✓       | **1.05**        | **3.80**        | **0.03**    | **4.26**      | **0.83**       |

Dynamic masking gives the largest single jump in S-ATE; the sparse term drives the Sampson error down.

## 💡 Insights & Impact

### Annotation engines, not just models

ViPE's framing is different from most work in this collection: the product is not a checkpoint that beats a benchmark but a _pipeline robust enough to run unattended over 96 M frames_. That reframes the design constraints — 3–5 FPS on one GPU and arbitrary video length matter more than shaving the last decimal off ATE.

### Why swapping the front-end is not enough

The introduction argues explicitly against the "put MASt3R inside a SLAM back-end" recipe. Table 2 supports this: MASt3R-SLAM in its uncalibrated all-frames configuration reaches 122.2 m ATE on KITTI, and the paper notes that at kilometer scale the visual-only system's scale estimation degrades badly. Tight integration — jointly optimizing intrinsics, dense flow, sparse tracks, and depth in one energy — is what recovers accuracy.

### Feed-forward models struggle with intrinsics

The most consistent gap in Tables 1 and 2 is focal-length error, where VGGT and MegaSAM sit around 10–12° on TUM while ViPE reaches 0.6–1.8°. Explicitly optimizing intrinsics inside BA remains meaningfully better than regressing them.

### Downstream value

The released datasets target video diffusion / camera-controllable generation, feed-forward reconstruction training, MVS, and embodied-AI policy evaluation — all areas bottlenecked by the scarcity of posed in-the-wild video.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the feed-forward baseline ViPE evaluates against, run under a sliding-window protocol for long video.
- [MASt3R-SLAM](../reconstruction/mast3r-slam.md) — the learned-front-end SLAM system ViPE argues is insufficient at scale.
- [VGGT-SLAM](../reconstruction/vggt-slam.md) — described as concurrent work in the same hybrid direction.
- [MASt3R](../foundation/mast3r.md) — the matching front-end underlying MASt3R-SLAM.
- [DUSt3R](../foundation/dust3r.md) — the pointmap regression paradigm ViPE positions itself against.
- [MonST3R](../dynamic/monst3r.md) — dynamic-scene handling in the feed-forward line.

## 📚 Key Takeaways

1. **Dense BA plus learned components beats either alone** — ViPE reaches 3.6 cm ATE on TUM Freiburg1 and 9.2 m on KITTI while MASt3R-SLAM records 122.2 m on the latter (원논문 Table 1·2).
2. **Intrinsics are the differentiator.** 0.6–1.8° focal error on TUM versus ~10–12° for VGGT and MegaSAM is the largest single margin in the paper.
3. **Speed is stated as 3–5 FPS on one GPU** at 640×480 on an RTX 5090 — the paper does not claim a speedup ratio over baselines, only per-sequence run times.
4. **Dynamic masking and sparse tracks both matter**, and combine: Table 4's full configuration is best on all five metrics.
5. **The dataset is the deliverable** — ~100 K real videos, 1 M generated videos, and 2 K panoramas, approximately 96 M frames total, released alongside the engine.

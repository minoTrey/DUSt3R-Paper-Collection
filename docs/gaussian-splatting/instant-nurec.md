# Instant NuRec: Feed-Forward 3D Gaussian Reconstruction for Driving Scene Simulation (arXiv preprint (2026-07))

![instant-nurec — architecture](https://arxiv.org/html/2607.14203v1/x2.png)

_Pipeline overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: NVIDIA (full list of contributors provided in the paper's Appendix A)
- **Institution**: NVIDIA
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.14203) | [Code](https://github.com/nvidia/instant-nurec) | [Project Page](https://research.nvidia.com/labs/sil/projects/instant-nurec)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward neural reconstruction model that turns a short multi-view driving log into a fully simulatable, layered 3DGS world (static + dynamic Gaussians, sky cubemap, per-camera ISP corrections) in a single forward pass — reconstructing a 10–20 s multi-camera scene in ~1.5 s and reaching a Waymo PSNR 2.01 dB above the strongest evaluated baseline.

## 🎯 Key Contributions

1. **Feed-forward simulatable world**: Emits a complete, closed-loop-simulation-ready layered 3DGS output (not just RGB Gaussians) — static layer, dynamic layer with piecewise-linear trajectories, sky cubemap, and per-camera ISP affine transforms — consumable by NuRec and AlpaSim.
2. **Trajectory recovery without cuboid tracks**: A motion decoder directly predicts piecewise-linear actor trajectories for query points, so the dynamic layer needs no per-actor cuboid tracks at reconstruction time.
3. **Query-point Gaussian decoding**: Gaussians are decoupled from pixels by lifting query points from predicted depth; a Selective strategy sparsifies queries (with a dedicated road branch) to cut the Gaussian budget ~3–4× versus Dense with only marginal quality loss.
4. **Orders-of-magnitude speedup**: Approaches per-scene-optimization quality while requiring 10³–10⁴× less computation per clip (~1.5 s vs ~75 min for NuRec), with native non-pinhole camera support via 3DGUT.

## 🔧 Technical Details

### Input / output

- **Input**: `V × T` RGB images from a calibrated rig of 1–5 cameras, sampled at 2–4 Hz, each with 6-DoF pose and intrinsics. Optional cuboid tracks may be supplied at inference to further calibrate dynamic trajectories.
- **Output**: a static Gaussian layer (position, scale, quaternion, opacity, color, world-space normal, road/non-road semantic label); a dynamic layer with the same attributes but position replaced by a piecewise-linear trajectory over 3 knots, opacity gated by a smooth fade; a sky cubemap `I_sky ∈ ℝ^{6×H×W×3}`; and per-camera ISP affine transforms `{A_v} ∈ ℝ^{V×3×4}`.

### Shared encoder and heads

- **Encoder**: an alternating-attention ViT following Depth-Anything-3 (which repurposes DINOv2 for multi-view input); 14×14 patch tokens plus a per-image class token from 6-DoF pose and FoV via sinusoidal encoding; `L` alternating intra-image / cross-image attention blocks.
- **Context DPT heads**: depth, normals, and semantic logits (four classes: road, movable, sky, ego-car); the depth branch drops the Depth-Anything-3 confidence channel.
- **3DGS decoder**: query points lifted from depth cross-attend to latent features to output per-query Gaussian attributes; rendered via 3DGUT.
- **Motion decoder**: predicts two 3D displacements (6-D target) per query, combining V-DPM and 4RC with AdaLN modulation on target timestamps; a semantic mask assigns only movable queries to the dynamic layer.
- **Sky and ISP decoders**: cubemap query per ray direction borrowing color from the matching input view; a per-camera 3×4 affine RGB transform initialized to identity and applied before the photometric loss.

### Long-clip chunk merging

- Per-chunk opacity pruning (`α < 10⁻²`) and **frustum-ownership pruning**: a Gaussian is kept by the chunk that observed it at the closest range (`D_g^i ≤ min_j D_g^j + δ`), applied to the static layer only.

### Training

- Three-stage curriculum: (1) Depth-Anything-3 pretraining; (2) context training (`L_context + L_motion`) fine-tuning encoder + sky/depth/motion heads with LiDAR/auto-label supervision; (3) GS training with the encoder frozen, enabling the camera-ISP and GS decoders under `L_render` (L1 + LPIPS after ISP transform, plus a sky-opacity loss).
- Trained on ~40K filtered internal NVIDIA AV clips (up to 5 cameras, ~300–600 frames per camera at 30 Hz, LiDAR-derived depth GT), `V ∈ {1,3,5}`, `T ∈ {8,12,18}`; ~6 days on 8 nodes; 3DGUT differentiable renderer.

## 📊 Results

### Waymo Open Dataset (STORM protocol, 240×160)

원논문 Table 1. Full Image·Dynamic Region 각각 PSNR↑, SSIM↑, AbsRel↓, δ1↑. 4개 컨텍스트 프레임(0.5s 간격) 입력.

| Method           | PSNR ↑ (Full) | SSIM ↑ (Full) | AbsRel ↓ (Full) | δ1 ↑ (Full) | PSNR ↑ (Dyn) | SSIM ↑ (Dyn) | AbsRel ↓ (Dyn) | δ1 ↑ (Dyn) |
| ---------------- | ------------- | ------------- | --------------- | ----------- | ------------ | ------------ | -------------- | ---------- |
| DepthSplat       | 22.48         | 0.645         | 0.295           | 0.592       | 18.59        | 0.391        | 0.445          | 0.512      |
| STORM            | 21.88         | 0.752         | 0.123           | 0.870       | 19.89        | 0.556        | 0.178          | 0.789      |
| Depth-Anything-3 | 20.30         | 0.557         | 0.434           | 0.313       | 17.59        | 0.250        | 0.467          | 0.354      |
| DGGT             | 26.25         | 0.805         | 0.135           | 0.841       | 21.76        | 0.652        | 0.249          | 0.689      |
| **Ours**         | **28.26**     | **0.859**     | **0.076**       | **0.937**   | **24.93**    | **0.793**    | **0.085**      | **0.922**  |

Instant NuRec achieves the best RGB reconstruction (PSNR 28.26 vs DGGT 26.25 = +2.01 dB), with even larger margins in dynamic regions, and depth quality on par with or better than the strongest baselines.

### Ablations (internal validation set)

원논문 Table 2. 지표는 PSNR↑, SSIM↑, AbsRel↓, δ1↑.

| Variant                       | PSNR ↑    | SSIM ↑    | AbsRel ↓  | δ1 ↑      |
| ----------------------------- | --------- | --------- | --------- | --------- |
| Instant NuRec (full)          | **29.93** | **0.793** | 0.069     | 0.950     |
| single-stage training         | 27.65     | 0.751     | 0.077     | **0.955** |
| sky MLP instead of cubemap    | 26.73     | 0.692     | **0.068** | 0.950     |
| w/o LPIPS loss                | 26.81     | 0.705     | 0.073     | 0.934     |
| w/o depth loss                | 28.92     | 0.782     | 0.103     | 0.862     |
| w/o frustum-ownership merging | 26.10     | 0.648     | 0.098     | 0.891     |

Removing frustum-ownership merging hurts most on RGB; removing the depth loss most degrades geometry (AbsRel/δ1). The multi-stage schedule is retained despite single-stage having marginally higher δ1.

### LiDAR reconstruction extension (internal data, Pandar128)

원논문 Table 3. CD↓, Prec.↓, Cov.↓, Int. MAE↓, Recon. time↓, Speedup↑ (원문 화살표 그대로).

| Method              | CD ↓  | Prec. ↓ | Cov. ↓ | Int. MAE ↓ | Recon. time ↓ | Speedup ↑ |
| ------------------- | ----- | ------- | ------ | ---------- | ------------- | --------- |
| NuRec               | 0.204 | 0.080   | 0.124  | 0.028      | ~75 min       | 1×        |
| Instant NuRec LiDAR | 0.286 | 0.113   | 0.173  | 0.027      | ~20 s         | ~225×     |
| w/o scale floor     | 0.936 | 0.195   | 0.741  | 0.036      | –             | –         |

The LiDAR branch trails per-scene NuRec on Chamfer distance (0.286 vs 0.204), mainly due to coverage rather than precision, but is ~225× faster; the anisotropic scale floor (inspired by Mip-Splatting) is essential.

### Efficiency and simulator viability

- Reconstructs a scene in ~1.5 s versus ~75 min for per-scene NuRec — a speedup of more than three orders of magnitude — while trailing only modestly in appearance quality (원논문 Fig. 7, PSNR/detection 수치는 그림, 일부 미인쇄).
- Selective query points cut Gaussians ~3× (from ~351K per context view for Dense to ~120K; ~6.3M → ~2.2M per 18-frame scene) with only marginal accuracy loss.
- In closed-loop simulation over 140 scenes (20 s rollouts, 6 trials each, 5 policy configs), the policy ranking under Instant NuRec is identical to NuRec (원논문 Fig. 8, 수치 미인쇄).

## 💡 Insights & Impact

- **Amortizing per-scene optimization**: The central result is that high-quality driving reconstruction can be moved into a single forward pass, making fleet-scale ingestion of millions of clips practical.
- **Simulation-ready, not just photorealistic**: By emitting an explicit layered world with static/dynamic separation, sky, and ISP corrections, the output plugs directly into closed-loop policy evaluation, unlike generative driving world models that emit 2D pixels.
- **Query-decoupled Gaussians**: Anchoring Gaussians on depth-lifted query points (rather than one-per-pixel) both controls the primitive budget and enables the Selective/road-branch trade-off.
- **Limitations**: A tension between Gaussian count and quality (small budgets under-sample thin structures); generalization limited by the training rig distribution (fisheye/low-mounted rigs need fine-tuning); and 3-keyframe piecewise-linear trajectories cannot capture sub-second non-rigid motion like pedestrian articulation.

## 🔗 Related Work

- Preserves the layered output format of per-scene driving reconstruction (NuRec, OmniRe, Neural Scene Graphs) but amortizes it into a feed-forward pass; uses 3DGUT/3DGRT-style rendering for distorted cameras.
- Builds its backbone on Depth-Anything-3 (a DINOv2-based multi-view geometry model), aligning with the alternating-attention design popularized by [VGGT](../reconstruction/vggt.md) and the pointmap paradigm of [DUSt3R](../foundation/dust3r.md); contrasts with pixel-aligned generalizable Gaussian models (DepthSplat) and token/query-based decoders (TokenGS).
- Specializes feed-forward reconstruction to dynamic driving, comparing against STORM, DrivingForward, DGGT, and StreetForward-style depth evaluation; positioned as the reconstruction backbone complementary to generative driving world models.

## 📚 Key Takeaways

1. Instant NuRec produces a fully simulatable layered 3DGS world (static + dynamic + sky + ISP) from a multi-camera driving log in ~1.5 s, 10³–10⁴× faster than per-scene optimization.
2. On the Waymo Open Dataset it leads feed-forward baselines by +2.01 dB PSNR (and larger margins in dynamic regions) while matching or beating their depth accuracy.
3. Closed-loop policy rankings match those of the far more expensive per-scene NuRec, validating feed-forward reconstruction as a reliable substitute for large-scale AD policy evaluation.

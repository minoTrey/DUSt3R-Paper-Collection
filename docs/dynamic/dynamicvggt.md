# DynamicVGGT: Learning Dynamic Point Maps for 4D Scene Reconstruction in Autonomous Driving (arXiv preprint)

## 📋 Overview

- **Authors**: Zhuolin He, Jing Li, Guanghao Li, Xiaolei Chen, Jiacheng Tang, Siyang Zhang, Zhounan Jin, Feipeng Cai, Bin Li, Jian Pu, Jia Cai, Xiangyang Xue
- **Institution**: Fudan University, Huawei, Yinwang Intelligent Technology, Shanghai Innovation Institute, CUHK
- **Venue**: arXiv preprint (2026-03)
- **Note**: The venue could not be confirmed from any primary source (no arXiv comment, OpenReview record, CVF entry, or GitHub badge stating acceptance). It is recorded as a preprint and should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2603.08254)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: Extends VGGT from static perception to a **dynamic point map** for autonomous driving by jointly predicting current and _future_ point maps in a shared reference frame, adding a Motion-aware Temporal Attention module with learnable motion tokens, and a Dynamic 3DGS head that predicts per-Gaussian velocities under scene-flow supervision.

## 🎯 Key Contributions

1. **Motion-aware Temporal Attention (MTA)** — a temporal reasoning module attached to VGGT's alternating-attention features that does _not_ disturb VGGT's spatial attention, so pretrained geometric priors and training stability are preserved.
2. **Future point prediction** — a DPT head that regresses the point map of a _future_ timestep from the current frame's temporally-enhanced feature, forcing the network to learn inter-frame motion implicitly and self-supervised.
3. **Dynamic 3D Gaussian Splatting head** — decodes time-varying Gaussian primitives carrying an explicit velocity attribute `ν_i`, supervised by scene flow. This is explicit motion supervision complementing the implicit point-map-level signal.
4. **Stage-wise training** to mitigate the degradation observed when a pretrained dense-prediction model is fine-tuned directly on large-scale, high-noise, sparse-depth real driving data.
5. **Depth distillation** to work around sparse LiDAR supervision: the stage-1 point-map depth acts as a teacher for the Gaussian depth branch.

## 🔧 Technical Details

### Why not just fine-tune VGGT

The paper identifies two problems specific to driving data. First, it is large-scale, high-noise, and sparse-depth, and training a dense-prediction model directly on it degrades that model's dense prediction capability. Second, existing dynamic-capable 3D foundation models still output _static point maps_, lacking a unified dynamic representation that downstream driving tasks can consume.

### Motion-aware Temporal Attention

From the aggregated tokens `F̃_{v,t} = [F^c_{v,t}; F^p_{v,t}]` produced by VGGT's AA blocks, the camera token `F^c` is removed and the patch tokens are concatenated with **learnable motion tokens** `M^{(l)}_{v,t}`:

```text
F^{(l)}_{m,v,t} = Concat( M^{(l)}_{v,t}, F^{p(l)}_{v,t} )                    if l = 1
                = Concat( M^{(l)}_{v,t}, F^{p(l)}_{v,t} + F^{p(l−1)}_{v,t} ) if l > 1
```

Temporal attention is computed independently per patch position and per view, with a learned temporal bias:

```text
A^{(l)}_{t,t'} = Softmax( Q^{attn,(l)}_t (K^{attn,(l)}_{t'})^T / √d + B^time_{t,t'} )
F^{(l+1)}_{m,v,t} = MLP^{(l)}( LayerNorm( F̃^{(l)}_{m,v,t} ) ) + F^{(l)}_{m,v,t}
```

The final output `TA_{v,t} = F^{(L)}_{m,v,t}` feeds both downstream heads.

### Future Point Head

```text
P̂^fut_{v,t+δ} = DPT_p( TA_{v,t} )
```

with a temporal consistency regularizer that matches _displacements_ rather than absolute positions:

```text
L_temp = (1/|N|) Σ_{i∈N} ‖ (p^{(i)}_{v,t+δ} − p^{(i)}_{v,t}) − (p̂^{(i)}_{v,t+δ} − p̂^{(i)}_{v,t}) ‖_1
```

The displacement field `Δp` acts as a coarse motion representation within the shared DPM coordinate space — crucially, **no explicit camera-extrinsic alignment is needed** because both timesteps live in one reference frame.

### Dynamic 3DGS Head

An observation drives the design: freezing the AA blocks makes the pretrained VGGT backbone over-emphasize geometry and under-weight appearance, which degrades Gaussian rendering. So image features are fused back in:

```text
F^app_{v,t} = Conv(I_{v,t})
F_{g,v,t}, D_{g,v,t} = DPT_g( TA_{v,t} )
G_{v,t} = F^app_{v,t} + F_{g,v,t}
```

Predicted Gaussian depth plus the retained VGGT camera branch reconstruct a point map that initializes Gaussian centers. Each primitive is `{μ_i, σ_i, r_i, c_i, ν_i}` — center, scale, rotation, color, **velocity**. The M motion tokens decode a set of shared velocity bases `ν_b ∈ R³`, and constant velocity is assumed within a short clip:

```text
μ_{i,t+δ} = μ_{i,t} + δ · ν_{i,t}
```

### Training objectives

Stage 1 (synthetic: Virtual KITTI, MVS-Synth):

```text
L_stage1 = L_cam + L_depth + L^{(t)}_point + L^{(t+δ)}_point + λ_temp · L_temp
```

with `L_cam = Σ ‖ĝ_i − g_i‖_ε` (Huber), and depth/point-map losses following VGGT.

Stage 2 (real: Waymo, Virtual KITTI):

```text
L_stage2 = L_stage1 + L_3DGS
L_3DGS   = L_rgb + λ_gs · L_gsdepth + λ_dist · L_distill + λ_flow · L_flow
```

`L_rgb = MSE(I_{v,t}, Î_{v,t})`. The distillation term `L_distill = ‖D_{g,v,t} − sg(D^pm_{v,t})‖_1` exists because direct sparse-LiDAR supervision "leads to severe performance degradation due to their limited density and uneven spatial distribution" — Figure 4 shows the LiDAR-supervised variant producing less smooth depth and rougher point clouds.

Hyperparameters: `λ_temp = 0.01`, `λ_gs = λ_dis = 0.1`, `λ_flow = 0.01`. Stage-1 learning rate 1×10⁻⁶.

## 📊 Results

### Point map reconstruction

원논문 Table 1. KITTI는 카메라별 연속 3프레임 monocular 입력, Waymo는 FRONT·SIDE LEFT·SIDE RIGHT에서 stride 4로 3프레임씩 총 9장을 한 그룹으로 쓴다.

| Method      | KITTI Mean Acc. ↓ | Comp. ↓   | NC ↑      | KITTI Med. Acc. ↓ | Comp. ↓   | NC ↑      |
| ----------- | ----------------- | --------- | --------- | ----------------- | --------- | --------- |
| VGGT        | 1.489             | 0.690     | 0.918     | 1.329             | 0.535     | **0.971** |
| StreamVGGT  | 1.078             | **0.495** | 0.899     | 0.867             | **0.390** | 0.949     |
| DynamicVGGT | **0.901**         | 0.584     | **0.939** | **0.733**         | 0.464     | 0.963     |

원논문 Table 1 (계속) — Waymo 3 cameras.

| Method      | Mean Acc. ↓ | Comp. ↓   | NC ↑      | Med. Acc. ↓ | Comp. ↓   | NC ↑      |
| ----------- | ----------- | --------- | --------- | ----------- | --------- | --------- |
| VGGT        | 4.635       | 2.667     | 0.561     | 2.634       | 1.734     | 0.590     |
| StreamVGGT  | 4.598       | 2.626     | **0.564** | 2.567       | 1.789     | 0.592     |
| DynamicVGGT | **4.021**   | **2.390** | 0.562     | **1.971**   | **1.564** | **0.603** |

**StreamVGGT wins Completeness on KITTI** (0.495 / 0.390 vs 0.584 / 0.464) and Mean NC on Waymo (0.564 vs 0.562); **VGGT retains the best KITTI median NC** (0.971 vs 0.963). DynamicVGGT's consistent advantage is Accuracy.

### Novel view synthesis on Waymo (val)

원논문 Table 2. Full은 조밀한 씬 어노테이션이, Camera는 카메라 intrinsic·extrinsic이 필요함을 뜻한다.

| Method                     | Supervision | Dynamic-only PSNR ↑ | SSIM ↑    | Full image PSNR ↑ | SSIM ↑    |
| -------------------------- | ----------- | ------------------- | --------- | ----------------- | --------- |
| **Per-scene optimization** |             |                     |           |                   |           |
| 3DGS                       | Full        | 17.13               | 0.267     | 25.13             | 0.741     |
| DeformableGS               | Full        | 17.10               | 0.266     | **25.29**         | **0.761** |
| **Feed-forward**           |             |                     |           |                   |           |
| GS-LRM                     | Camera      | 20.02               | 0.520     | 25.18             | 0.753     |
| STORM                      | Camera      | **21.26**           | **0.535** | 25.03             | 0.750     |
| DynamicVGGT                | Image-only  | 18.07               | 0.376     | 24.07             | 0.676     |

**DynamicVGGT loses this table outright on every metric.** It is last on full-image PSNR (24.07) and SSIM (0.676), and its dynamic-only PSNR (18.07) trails STORM by 3.19 dB and GS-LRM by 1.95 dB. The paper's framing is the supervision column: DynamicVGGT is the only method operating **image-only**, without camera parameters or per-scene optimization, while every baseline requires either dense scene annotations or calibrated camera intrinsics and extrinsics.

### Monocular and MVS depth estimation

원논문 Table 3.

| Method      | KITTI(Mono) Abs Rel ↓ | δ<1.25 ↑  | NYU-v2(Mono) Abs Rel ↓ | δ<1.25 ↑  | KITTI(MVS) Abs Rel ↓ | δ<1.25 ↑  |
| ----------- | --------------------- | --------- | ---------------------- | --------- | -------------------- | --------- |
| DUSt3R      | 0.109                 | 0.873     | 0.081                  | 0.909     | 0.143                | 0.814     |
| MASt3R      | 0.077                 | **0.948** | 0.110                  | 0.865     | 0.115                | 0.848     |
| MonST3R     | 0.098                 | 0.895     | 0.094                  | 0.887     | 0.107                | 0.884     |
| VGGT        | 0.082                 | 0.938     | 0.059                  | 0.951     | 0.062                | 0.969     |
| StreamVGGT  | 0.082                 | 0.947     | **0.057**              | **0.959** | 0.173                | 0.721     |
| DynamicVGGT | **0.070**             | 0.940     | 0.064                  | 0.943     | **0.051**            | **0.976** |

Mixed picture, reported as it stands: best Abs Rel on KITTI mono (0.070) and KITTI MVS (0.051, with 97.6% δ<1.25), but **MASt3R still has the best KITTI mono δ<1.25 (0.948) and StreamVGGT the best NYU-v2 on both metrics (0.057 / 0.959)**. NYU-v2 is an out-of-domain indoor test for a model trained on driving data; DynamicVGGT (0.064) sits between DUSt3R and VGGT there. Note StreamVGGT collapses on KITTI MVS (0.173 / 0.721).

### Ablation

원논문 Table 4. TA = temporal attention, FPH = Future Point Head, DGSHead = Dynamic 3DGS Head.

| Method               | KITTI Mean Acc. ↓ | Comp. ↓   | NC ↑      | KITTI Med. Acc. ↓ | Comp. ↓   | NC ↑      |
| -------------------- | ----------------- | --------- | --------- | ----------------- | --------- | --------- |
| Baseline (VGGT)      | 1.489             | 0.690     | 0.918     | 1.329             | 0.535     | **0.971** |
| + TA & FPH (stage 1) | 0.927             | 0.600     | 0.915     | 0.857             | 0.474     | 0.932     |
| + DGSHead (stage 2)  | **0.901**         | **0.584** | **0.939** | **0.733**         | **0.464** | 0.963     |

원논문 Table 4 (계속) — Waymo 3cam.

| Method               | Mean Acc. ↓ | Comp. ↓   | NC ↑      | Med. Acc. ↓ | Comp. ↓   | NC ↑      |
| -------------------- | ----------- | --------- | --------- | ----------- | --------- | --------- |
| Baseline (VGGT)      | 4.635       | **2.667** | 0.561     | 2.634       | 1.734     | 0.590     |
| + TA & FPH (stage 1) | 4.330       | 2.939     | 0.561     | 2.224       | 1.649     | 0.593     |
| + DGSHead (stage 2)  | **4.021**   | 2.390     | **0.562** | **1.971**   | **1.564** | **0.603** |

Temporal attention plus future point prediction does the heavy lifting on Accuracy (1.489 → 0.927 on KITTI); the Gaussian head mainly recovers Normal Consistency (0.915 → 0.939), which stage 1 had _degraded_ below baseline. Note also that stage 1 alone makes Waymo mean Completeness worse than baseline (2.939 vs 2.667) before stage 2 fixes it.

### Qualitative only

Figure 5 compares point maps across single-frame, short-term multi-frame, and long-range temporal configurations, and Figure 4 compares depth/point maps with and without LiDAR supervision. Neither carries printed numeric values, so nothing is reproduced from them here.

## 💡 Insights & Impact

### A shared reference frame removes the alignment step

The design choice with the most leverage is predicting current and future point maps _in one shared coordinate system_. Motion then appears as a displacement field inside a single space, so `L_temp` can supervise it directly without any explicit camera-extrinsic alignment between timesteps. This sidesteps a whole class of drift and alignment machinery that 4D pipelines usually need.

### Two motion signals at different granularities

`L_temp` constrains coarse inter-frame displacement at the point-map level; scene-flow supervision on Gaussian velocities constrains motion at the primitive level. The ablation supports the split being useful rather than redundant — stage 1 improves Accuracy but _hurts_ Normal Consistency, and only the Gaussian stage restores it.

### Frozen backbones lose appearance

The observation that freezing AA blocks makes VGGT over-emphasize geometry and under-serve appearance, requiring a `Conv(I)` bypass, is a concrete and transferable caution for anyone bolting a rendering head onto a frozen geometry foundation model.

### Sparse LiDAR is a bad teacher

Rather than treating LiDAR as ground truth, the paper distills from its own stage-1 point-map depth. This inverts the usual assumption that real sensor supervision beats model prediction — when the sensor is sparse and unevenly distributed, a dense self-prediction is the better training signal.

### Honest positioning

This is a geometry paper, not a rendering paper. It wins point-map Accuracy and KITTI depth, and it loses the Waymo NVS table to every baseline. The defensible claim is what it achieves _without_ camera parameters, dense annotations, or per-scene optimization — a fair comparison of like-for-like supervision is not available in Table 2.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the backbone; also the ablation baseline and a competitor in every table
- [StreamVGGT](../reconstruction/streamvggt.md) — the strongest competitor; wins KITTI Completeness and NYU-v2 depth, collapses on KITTI MVS
- [DUSt3R](../foundation/dust3r.md) — origin of the pointmap regression formulation
- [MASt3R](../foundation/mast3r.md) — depth baseline in Table 3, still best on KITTI mono δ<1.25
- [MonST3R](monst3r.md) — the dynamic-scene predecessor whose output is still a static point map
- [Dynamic Point Maps](dynamic-point-maps.md) — the closest representational relative in this collection
- [VGGT4D](vggt4d.md) — a _training-free_ alternative route to 4D from VGGT; different paper, different mechanism

## 📚 Key Takeaways

1. **Predict the future point map in the same coordinate frame** — motion becomes a displacement field, and no camera-extrinsic alignment is required between timesteps.
2. **Attach temporal attention beside, not inside, spatial attention.** MTA operates on patch tokens plus learnable motion tokens without disrupting VGGT's AA blocks, preserving pretrained priors.
3. **Implicit and explicit motion supervision are complementary.** Stage 1 (`L_temp`) buys Accuracy but costs Normal Consistency; stage 2 (scene-flow on Gaussian velocities) recovers it.
4. **Distill from your own depth when the sensor is sparse.** LiDAR supervision degraded results; the stage-1 point-map branch made a better teacher.
5. **Best point-map Accuracy, last place on NVS.** DynamicVGGT wins Table 1 Accuracy and KITTI depth, but trails STORM by 3.19 dB dynamic-only PSNR on Waymo — the offsetting claim is image-only supervision with no camera parameters.

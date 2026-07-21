# IVGT: Implicit Visual Geometry Transformer for Neural Scene Representation (arXiv preprint (2026-05))

## 📋 Overview

- **Authors**: Yuqi Wu\*, Tianyu Hu\*, Wenzhao Zheng\*†, Yuanhui Huang, Haowen Sun, Jie Zhou, Jiwen Lu (\* Equal contributions, † Project leader)
- **Institution**: Intelligent Vision Group, Tsinghua University
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.16258) | [Code](https://github.com/wzzheng/IVGT/) | [Project Page](https://wzzheng.net/IVGT/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A transformer that learns a continuous implicit SDF-based neural scene representation from pose-free multi-view images in one forward pass, enabling surface extraction, novel-view synthesis, depth and normal rendering without per-scene optimization or post-processing.

## 🎯 Key Contributions

1. **Implicit vs. explicit paradigm**: Instead of regressing pixel-aligned pointmaps (as in VGGT-style explicit models), IVGT learns a global continuous 3D field queryable at any location, avoiding redundancy and cross-view inconsistency of discrete pointmaps.
2. **Pose-free continuous neural scene representation**: A transformer backbone with alternating intra-view / cross-view attention aggregates multi-view tokens into a unified canonical representation without explicit input poses.
3. **Ray-depth positional encoding**: Rather than encoding absolute 3D coordinates (reference-frame dependent, ambiguous), IVGT encodes view-relative ray depths, which stay invariant across reference-frame choices.
4. **Unified geometry + appearance decoding**: Cascaded MLP decoders predict an SDF value (geometry) and view-dependent color (appearance) per query, converted to densities for differentiable volume rendering and Marching Cubes surface extraction.
5. **Multi-dataset joint training with 2D supervision + 3D regularization**: A two-stage strategy (2D render losses, then Eikonal + smoothness + VGGT depth loss) enabling cross-scene generalization in a single forward pass.

## 🔧 Technical Details

### Explicit vs. Implicit Formulation

- **Explicit (prior work)**: Given N images, a per-view decoder produces a pointmap Pᵢ ∈ R^(H×W×3); full geometry is a finite set of N×H×W discrete pixel-anchored points. Limitations: geometry defined only at pixel-aligned locations (no arbitrary queries, no implied continuous surface); the same physical point appears redundantly across views, yielding inconsistent estimates.
- **Implicit (IVGT)**: Learns a global field F queryable at any x ∈ R³, returning signed distance ŝ(x) and view-dependent color ĉ(x, v). The surface is the zero level set S = {x : ŝ(x) = 0}, continuous and view-count-independent. Volume rendering yields RGB / depth / normal; iso-surface via Marching Cubes without post-processing.

### Architecture

- **Image encoder**: DINO tokenizes each view; a multi-layer transformer alternates frame-wise and global self-attention (VGGT-style) for intra-view and cross-view aggregation.
- **Auxiliary outputs**: The backbone also predicts per-view depth maps Dᵢ and camera parameters gᵢ ∈ R⁹; the first image is the reference frame, and the model is permutation-equivariant over the remaining views.
- **Continuous 3D query**: A query point x is projected into all valid views to gather pixel-aligned features z_f = Σ Fᵢ(π(x)) over N_k valid views; a ray-depth feature z_d = Σ f_raydepth(dᵢ(x)) disambiguates points sharing the same projection ray. Concatenation gives the local spatial feature z.
- **Decoders**: An 8-layer MLP decodes (ŝ, ẑ) = f_θ(z); a 2-layer MLP predicts color ĉ = c_θ(ẑ, n̂, γ(v)), where n̂ is the SDF gradient (surface normal) and γ is NeRF positional encoding of the viewing direction.

### Rendering & Surface Extraction

- **Volume rendering**: SDF → density via VolSDF transform with a learnable, scene-shared β; transmittance/alpha compositing (NeRF) gives color Ĉ(r), depth D̂(r), normal N̂(r).
- **Surface extraction**: Input-view depths are projected into the first-frame coordinate system for a coarse point cloud → bounding volume → a 64³ grid inferred for SDF, thresholded to valid regions → upsampled to 512³ → Marching Cubes; mesh-vertex colors use the surface normal as the approximate viewing direction.

### Training

- **Stage 1 (2D)**: L_stage1 = L_rgb + λ₁ L_depth-render + λ₂ L_normal + λ₃ L_camera (Huber loss for camera).
- **Stage 2 (3D regularization)**: adds Eikonal + smoothness + VGGT depth loss: L_stage2 = L_stage1 + λ₄ L_eikonal + λ₅ L_smooth + λ₆ L_depth.
- **Hyperparameters**: λ₁…λ₆ = 0.1, 0.05, 1.0, 0.01, 0.01, 0.1; AdamW, LR warmup to 2e-4 with cosine decay; 8 render viewpoints/iter (4 context + 4 novel), 1024 rays/view, error-bounded sampling. Encoder initialized from VGGT weights.
- **Compute**: 4× A800 NVIDIA GPUs for 4 days.
- **Training data**: ARKitScenes, CO3Dv2, HyperSim, MegaDepth, OmniObject3D, ScanNet, ScanNet++, Unreal4K, WildRGBD (RGB-D + poses; normals predicted via DSine).

## 📊 Results

### Scene-level Mesh Reconstruction (ScanNet)

원논문 Table 1. IVGT is generalizable (single forward pass); baselines are per-scene optimization. IVGT ranks second only to MonoSDF (which needs hours of per-scene optimization).

| Method        | Setting       | Acc↓  | Comp↓ | Chamfer↓ | Prec↑ | Recall↑ | F-score↑ |
| ------------- | ------------- | ----- | ----- | -------- | ----- | ------- | -------- |
| COLMAP        | Per-Scene     | 0.047 | 0.235 | 0.141    | 0.711 | 0.441   | 0.537    |
| UNISURF       | Per-Scene     | 0.554 | 0.164 | 0.359    | 0.212 | 0.362   | 0.267    |
| NeuS          | Per-Scene     | 0.179 | 0.208 | 0.194    | 0.313 | 0.275   | 0.291    |
| VolSDF        | Per-Scene     | 0.414 | 0.120 | 0.267    | 0.321 | 0.394   | 0.346    |
| Manhattan-SDF | Per-Scene     | 0.072 | 0.068 | 0.070    | 0.621 | 0.586   | 0.602    |
| MonoSDF       | Per-Scene     | 0.035 | 0.048 | 0.042    | 0.799 | 0.681   | 0.733    |
| IVGT          | Generalizable | 0.069 | 0.051 | 0.060    | 0.663 | 0.639   | 0.647    |

### Pointmap Reconstruction (7-Scenes / NRGBD / DTU)

원논문 Table 2 (분할 1/3). 7-Scenes (scene-level, kf=50, meters). "IVGT" = pointmaps from per-view features; "IVGT (from render)" = pointmaps from rendered depth maps.

| Method             | Acc↓ Mean | Acc↓ Med | Comp↓ Mean | Comp↓ Med |
| ------------------ | --------- | -------- | ---------- | --------- |
| Fast3R             | 0.053     | 0.023    | 0.084      | 0.033     |
| CUT3R              | 0.024     | 0.011    | 0.028      | 0.009     |
| Point3R            | 0.030     | 0.015    | 0.026      | 0.010     |
| StreamVGGT         | 0.046     | 0.025    | 0.032      | 0.014     |
| VGGT               | 0.020     | 0.008    | 0.028      | 0.012     |
| IVGT               | 0.016     | 0.007    | 0.021      | 0.009     |
| IVGT (from render) | 0.023     | 0.010    | 0.038      | 0.018     |

원논문 Table 2 (분할 2/3). NRGBD (scene-level, kf=100, meters).

| Method             | Acc↓ Mean | Acc↓ Med | Comp↓ Mean | Comp↓ Med |
| ------------------ | --------- | -------- | ---------- | --------- |
| Fast3R             | 0.080     | 0.039    | 0.075      | 0.039     |
| CUT3R              | 0.086     | 0.038    | 0.047      | 0.016     |
| Point3R            | 0.065     | 0.035    | 0.030      | 0.013     |
| StreamVGGT         | 0.080     | 0.056    | 0.044      | 0.021     |
| VGGT               | 0.018     | 0.010    | 0.017      | 0.009     |
| IVGT               | 0.017     | 0.011    | 0.015      | 0.006     |
| IVGT (from render) | 0.043     | 0.023    | 0.031      | 0.014     |

원논문 Table 2 (분할 3/3). DTU (object-level, kf=5, mm). VGGT has lower Acc Mean (1.305) than IVGT (1.686), but IVGT has better Completeness.

| Method             | Acc↓ Mean | Acc↓ Med | Comp↓ Mean | Comp↓ Med |
| ------------------ | --------- | -------- | ---------- | --------- |
| Fast3R             | 3.605     | 1.855    | 3.048      | 1.274     |
| CUT3R              | 4.749     | 2.588    | 2.764      | 1.176     |
| Point3R            | 6.111     | 3.930    | 2.880      | 1.399     |
| StreamVGGT         | 2.520     | 1.395    | 2.048      | 1.075     |
| VGGT               | 1.305     | 0.743    | 2.435      | 1.737     |
| IVGT               | 1.686     | 0.889    | 1.458      | 0.792     |
| IVGT (from render) | 2.476     | 1.167    | 2.979      | 1.576     |

### Camera Pose Estimation (ScanNet / Sintel / TUM-dynamics)

원논문 Table 3. ATE, RPE trans, RPE rot after Sim(3) Umeyama alignment. Lower is better. VGGT and WorldMirror are ahead on several Sintel columns.

| Method      | SN ATE↓ | SN RPEt↓ | SN RPEr↓ | Sin ATE↓ | Sin RPEt↓ | Sin RPEr↓ | TUM ATE↓ | TUM RPEt↓ | TUM RPEr↓ |
| ----------- | ------- | -------- | -------- | -------- | --------- | --------- | -------- | --------- | --------- |
| Fast3R      | 0.084   | 0.059    | 2.844    | 0.274    | 0.224     | 15.69     | 0.048    | 0.052     | 1.197     |
| CUT3R       | 0.096   | 0.022    | 0.733    | 0.210    | 0.071     | 0.627     | 0.045    | 0.014     | 0.441     |
| FLARE       | 0.069   | 0.025    | 0.991    | 0.158    | 0.082     | 2.863     | 0.026    | 0.013     | 0.475     |
| VGGT        | 0.035   | 0.015    | 0.403    | 0.169    | 0.064     | 0.478     | 0.012    | 0.010     | 0.313     |
| WorldMirror | 0.037   | 0.017    | 0.422    | 0.121    | 0.063     | 0.535     | 0.012    | 0.010     | 0.301     |
| IVGT        | 0.032   | 0.014    | 0.422    | 0.140    | 0.060     | 0.530     | 0.012    | 0.010     | 0.319     |

### Novel View Synthesis (sparse-view)

원논문 Table 4 (분할 1/2). Sparse-view: RealEstate10K (2 views) and DL3DV (8 views). IVGT trails WorldMirror.

| Method      | RE10K PSNR↑ | RE10K SSIM↑ | RE10K LPIPS↓ | DL3DV PSNR↑ | DL3DV SSIM↑ | DL3DV LPIPS↓ |
| ----------- | ----------- | ----------- | ------------ | ----------- | ----------- | ------------ |
| FLARE       | 16.33       | 0.574       | 0.410        | 15.35       | 0.516       | 0.591        |
| AnySplat    | 17.62       | 0.616       | 0.242        | 18.31       | 0.569       | 0.258        |
| WorldMirror | 20.62       | 0.706       | 0.187        | 20.92       | 0.667       | 0.203        |
| IVGT        | 18.97       | 0.656       | 0.449        | 19.74       | 0.627       | 0.494        |

### Novel View Synthesis (dense-view)

원논문 Table 4 (분할 2/2). Dense-view: RealEstate10K (32 views) and DL3DV (64 views). FLARE not reported (–). IVGT trails WorldMirror on all metrics.

| Method      | RE10K PSNR↑ | RE10K SSIM↑ | RE10K LPIPS↓ | DL3DV PSNR↑ | DL3DV SSIM↑ | DL3DV LPIPS↓ |
| ----------- | ----------- | ----------- | ------------ | ----------- | ----------- | ------------ |
| FLARE       | –           | –           | –            | –           | –           | –            |
| AnySplat    | 19.96       | 0.718       | 0.234        | 18.40       | 0.602       | 0.286        |
| WorldMirror | 25.14       | 0.859       | 0.109        | 21.25       | 0.703       | 0.223        |
| IVGT        | 21.91       | 0.751       | 0.394        | 19.62       | 0.659       | 0.515        |

### Monocular & Video Depth Estimation (NYUv2 / Sintel)

원논문 Table 5. Abs Rel↓ and δ<1.25↑. On NYUv2 Abs Rel, VGGT (0.056) beats IVGT (0.063), but IVGT leads δ<1.25 and both Sintel settings.

| Method             | NYUv2 AbsRel↓ | NYUv2 δ<1.25↑ | Sin(M) AbsRel↓ | Sin(M) δ<1.25↑ | Sin(V) AbsRel↓ | Sin(V) δ<1.25↑ |
| ------------------ | ------------- | ------------- | -------------- | -------------- | -------------- | -------------- |
| Fast3R             | 0.093         | 0.898         | 0.544          | 0.509          | 0.638          | 0.422          |
| CUT3R              | 0.081         | 0.914         | 0.418          | 0.520          | 0.417          | 0.507          |
| FLARE              | 0.089         | 0.898         | 0.606          | 0.402          | 0.729          | 0.336          |
| VGGT               | 0.056         | 0.951         | 0.606          | 0.599          | 0.299          | 0.638          |
| IVGT               | 0.063         | 0.954         | 0.309          | 0.620          | 0.295          | 0.646          |
| IVGT (from render) | 0.067         | 0.945         | 0.398          | 0.570          | 0.542          | 0.582          |

### Surface Normal Estimation (NYUv2 / iBims-1)

원논문 Table 6. Mean/median angular error (↓) and % pixels within 22.5°/30° (↑). IVGT is comparable to dedicated normal estimators despite being optimized for multi-view reconstruction.

| Method      | NYU mean↓ | NYU med↓ | NYU 22.5↑ | NYU 30↑ | iB mean↓ | iB med↓ | iB 22.5↑ | iB 30↑ |
| ----------- | --------- | -------- | --------- | ------- | -------- | ------- | -------- | ------ |
| OASIS       | 29.2      | 23.4     | 48.4      | 60.7    | 32.6     | 24.6    | 46.6     | 57.4   |
| EESNU       | 16.2      | 8.5      | 77.2      | 83.5    | 20.0     | 8.4     | 73.4     | 78.2   |
| Omnidata v2 | 17.2      | 9.7      | 76.5      | 83.0    | 18.2     | 7.0     | 77.4     | 81.1   |
| DSine       | 16.4      | 8.4      | 77.7      | 83.5    | 17.1     | 6.1     | 79.0     | 82.3   |
| IVGT        | 16.6      | 10.4     | 77.3      | 84.2    | 20.1     | 10.6    | 74.4     | 79.6   |

### Ablation: Positional Encoding for 3D Queries (ScanNet)

원논문 Table 7. Each variant trained 16 hours on the same setup. "No Embed" failed to learn geometry (mostly positive SDF → empty space, no valid mesh), so it is not in the table. IVGT uses Raydepth-Embed.

| Variant        | Acc↓  | Comp↓ | Chamfer↓ | Prec↑ | Recall↑ | F-score↑ |
| -------------- | ----- | ----- | -------- | ----- | ------- | -------- |
| XYZ-PosEnc     | 0.624 | 0.158 | 0.391    | 0.220 | 0.346   | 0.260    |
| XYZ-Embed      | 0.494 | 0.148 | 0.321    | 0.272 | 0.364   | 0.306    |
| Raydepth-Embed | 0.219 | 0.103 | 0.161    | 0.434 | 0.431   | 0.429    |

Two-stage training effect (Figure 8, 수치 미인쇄): stage-1 (2D-only) captures coarse but rough surfaces; adding Eikonal + smoothness in stage-2 yields smoother, more coherent meshes.

## 💡 Insights & Impact

- **Continuous over discrete**: Modeling the scene as a global implicit SDF field removes the redundancy and cross-view inconsistency of pixel-aligned pointmaps, and enables surface extraction and novel-view rendering without post-processing — capabilities that are inherently hard for discrete explicit outputs.
- **Reference-frame invariance matters**: The ablation shows absolute-coordinate encodings (XYZ-PosEnc, XYZ-Embed) degrade sharply and "No Embed" fails entirely; view-relative ray-depth encoding is what makes cross-scene geometry learnable.
- **Generalizable yet competitive**: As a single-forward-pass generalizable method, IVGT approaches per-scene optimization quality on ScanNet mesh reconstruction (2nd only to MonoSDF, which needs hours per scene) and leads representative feed-forward methods on pointmap and depth metrics.
- **Honest trade-offs**: The paper reports IVGT losing to WorldMirror on novel-view synthesis and to VGGT on some depth/pointmap columns, and states limitations: SDF smoothness suppresses high-frequency detail and thin structures; assumes static, bounded scenes; and per-point projection makes inference more costly than direct pixel-aligned decoding, hindering real-time use.

## 🔗 Related Work

- **[VGGT](vggt.md)**: IVGT initializes its encoder/global-feature module from VGGT, reuses its alternating-attention design and depth loss, and positions itself as the implicit-field counterpart to VGGT's explicit pointmap paradigm. VGGT remains a strong baseline across Tables 2, 3, 5.
- **[Fast3R](fast3r.md)**, **[CUT3R](../dynamic/cut3r.md)**: feed-forward explicit-geometry baselines compared on pointmap, pose, and depth benchmarks.
- **[MonST3R](../dynamic/monst3r.md)**: pose-estimation evaluation protocol (ScanNet/Sintel/TUM) follows MonST3R and CUT3R.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: foundational pose-free feed-forward reconstruction lineage that established the explicit pointmap-regression paradigm IVGT contrasts against.

## 📚 Key Takeaways

1. **IVGT reframes visual-geometry foundation models from explicit pointmap regression to an implicit, continuous SDF field** queryable at arbitrary 3D points, learned from pose-free multi-view images in one forward pass.
2. **View-relative ray-depth encoding** is the key design enabling reference-frame-invariant, cross-scene generalization — validated by a decisive ablation.
3. **A single unified representation drives many tasks** (mesh, pointmap, novel view, depth, normal, pose) with competitive-to-leading results, and surface/rendering come for free via VolSDF-style volume rendering + Marching Cubes.
4. **Trade-offs are explicit**: strong geometry and coherence, but appearance detail lags 3DGS-based NVS, and per-point projection raises inference cost — future directions include appearance-oriented heads, dynamic scenes, and more efficient querying.

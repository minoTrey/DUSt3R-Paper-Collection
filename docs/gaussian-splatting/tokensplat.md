# TokenSplat: Token-aligned 3D Gaussian Splatting for Feed-forward Pose-free Reconstruction (CVPR 2026)

## 📋 Overview

- **Authors**: Yihui Li, Chengxin Lv, Zichen Tang, Hongyu Yang, Di Huang
- **Institution**: State Key Laboratory of Complex and Critical Software Environment; School of Computer Science and Engineering, Beihang University; School of Artificial Intelligence, Beihang University
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.00697) | [Project Page](https://kidleyh.github.io/tokensplat/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A feed-forward pose-free 3DGS framework that fuses multi-view information in **feature space** (token-aligned) rather than fusing pixel-aligned Gaussians, combined with an asymmetric decoder that lets camera tokens read image tokens but not contaminate them.

## 🎯 Key Contributions

1. **Token-aligned Gaussian Prediction**: Aligns semantically corresponding information across views directly in feature space, guided by coarse token positions and fusion confidence, aggregating multi-scale contextual features for long-range cross-view reasoning and reduced redundancy from overlapping Gaussians.
2. **Learnable camera tokens**: Per-view camera tokens carry viewpoint cues separately from scene semantics.
3. **Asymmetric Dual-Flow Decoder (ADF-Decoder)**: Enforces **directionally constrained** communication between camera and image tokens, maintaining a clean factorization within a feed-forward architecture — no iterative refinement.
4. **Joint reconstruction and pose in one pass**: Coherent reconstruction and stable pose estimation from unposed multi-view images.

## 🔧 Technical Details

### Problem Formulation

The model learns a mapping from `N` unposed images to Gaussian primitives in the canonical reference frame `I₁`, plus per-view poses:

```text
f_θ : {I_i}ᴺ ↦ {(μ_g, σ_g, r_g, s_g, c_g)}ᴳ ∪ {P_i}ᴺ
```

Gaussian attributes and camera poses are jointly optimized during training.

### Architecture

- **ViT Encoder** (shared across views): patchifies each RGB image into image tokens. Optionally, camera intrinsics are encoded as an additional token via a linear layer and concatenated along the spatial dimension to mitigate scale ambiguity.
- **Canonical Scene Decoder**: processes reference view `I₁` with cross-attention to all other views, establishing a consistent canonical scene representation that anchors subsequent refinement.
- **ADF-Decoder**: processes the remaining views, refining image tokens and learnable camera tokens.
- Two parallel output branches: the **Camera Pose Estimation Head** and the **Token-aligned Gaussian Prediction** module.

### ADF-Decoder: Directional Constraints

The asymmetry is the core idea. Image tokens aggregate scene context; camera tokens absorb geometric cues from image tokens and pass specialized pose signals back — but the flow is restricted so pose information does not contaminate scene features.

**Self-attention (within-view)** — image tokens attend to themselves; camera tokens attend to their own view's image tokens:

```text
t̂ᴵ_i ← Softmax(Qᴵ_i (Kᴵ_i)ᵀ / √d) Vᴵ_i
t̂ᶜ_i ← Softmax(Qᶜ_i (Kᴵ_i)ᵀ / √d) Vᴵ_i
```

**Image token cross-view attention**: each view attends to tokens from _other_ views while **explicitly excluding its own** tokens — the paper argues this prevents information leakage across views and forces complementary cues to be integrated. Keys and values from other views are concatenated along the spatial dimension. A hyperparameter `p_nv` caps each view's attention to its `p_nv − 1` neighbors to control cost with many views.

**Camera token cross-attention**: attending only to other camera tokens, or only to image tokens, is insufficient for global geometry. So each camera token attends to **both**, with other views' camera keys/values replicated to match the image token count and summed:

```text
Kᶜ_cross,i = [Kᴵ_j]_{j≠i} + [repeat(Kᶜ_j)]_{j≠i}
Vᶜ_cross,i = [Vᴵ_j]_{j≠i} + [repeat(Vᶜ_j)]_{j≠i}
```

**Pre- and post-modulation**: because image and camera tokens differ greatly in count and information content, image tokens modulate camera tokens both before and after the attention operation. This stabilizes updates and reinforces the disentanglement.

### Token Fusion for Scene Reconstruction

Where pixel-aligned methods predict dense Gaussians per pixel per view — accumulating redundancy and geometric blurring in overlapping regions — TokenSplat fuses **in feature space**:

1. Predict coarse token positions and fusion confidence.
2. Group tokens by spatial proximity using grouping size `ϵ`.
3. Fuse within groups weighted by confidence, producing a compact token set with consolidated features and coarse positions.

The fusion network uses a **DPT-based architecture** with adjusted prediction-parameter counts.

Multi-scale features `{F_i}` from different decoder layers are projected, channel-unified, and upsampled by layer scale (larger upsampling for lower layers), then progressively fused deep-to-shallow through residual fusion modules:

```text
F_fusion^{n_l} = RF_{n_l}(F̂_{n_l})
F_fusion^{i}   = RF_i(F̂_i, F_fusion^{i+1})
```

The fused high-resolution features pass through a prediction block of upsampling and linear layers, producing continuous tensors of the final Gaussian parameters. Each fused token generates multiple denser Gaussians, including **positional offsets relative to the token**.

### Losses

- **Render loss**: `L_render = L2(I, Î) + λ_lpips · L_lpips(I, Î)`
- **Camera pose loss**: MSE plus a **Unit Dual Quaternion (DQ) alignment** loss, which jointly represents rotation and translation to avoid inconsistencies from predicting them separately: `L_align = ‖p − p̂ p*‖ + ‖p − p̂* p‖`, giving `L_pose = L_MSE(P, P̂) + L_align`
- **Total**: `L = L_render + λ_c · L_pose`

### Implementation

- PyTorch; **ViT-Large** encoder with patch size **16**.
- Encoder-decoder and Gaussian center head initialized from **MASt3R** weights; ADF-Decoder and remaining heads randomly initialized.
- Datasets: RealEstate10K (RE10K) and ScanNet, using splits from prior work for direct comparability.
- All quantitative results at a fixed resolution of **256 × 256**.
- Evaluations: RE10K at 4 and 8 reference views; ScanNet at 3 and 10 views (the 10-view config augments the 3-view setup), plus a **28-view** stress test on ScanNet using models trained with 10 views.
- `AnySplat` denotes zero-shot results trained on other datasets; `AnySplat*` denotes results after fine-tuning on the corresponding dataset.

## 📊 Results

### Novel View Synthesis on RE10K and Cross-Dataset ScanNet

원논문 Table 1. Left half is RE10K; right half is cross-dataset generalization to ScanNet (trained on RE10K).

| Category      | Method     | RE10K-4 PSNR ↑ | RE10K-4 SSIM ↑ | RE10K-4 LPIPS ↓ | RE10K-8 PSNR ↑ | RE10K-8 SSIM ↑ | RE10K-8 LPIPS ↓ |
| ------------- | ---------- | -------------- | -------------- | --------------- | -------------- | -------------- | --------------- |
| Pose-required | MVSplat    | 23.82          | 0.792          | 0.201           | 23.96          | 0.802          | 0.164           |
| Pose-required | FreeSplat  | 24.99          | 0.814          | 0.162           | 25.20          | 0.829          | 0.179           |
| Pose-free     | NoPoSplat  | 24.87          | 0.813          | 0.169           | 25.01          | 0.832          | 0.163           |
| Pose-free     | VicaSplat  | 24.65          | 0.795          | 0.206           | 24.50          | 0.806          | 0.164           |
| Pose-free     | SPFSplat   | 24.98          | 0.819          | 0.166           | 25.18          | 0.828          | 0.169           |
| Pose-free     | AnySplat\* | 20.28          | 0.657          | 0.251           | 20.93          | 0.746          | 0.284           |
| Pose-free     | AnySplat   | 15.55          | 0.475          | 0.424           | 16.23          | 0.520          | 0.401           |
| Pose-free     | **Ours**   | **25.14**      | **0.834**      | **0.156**       | **26.15**      | **0.858**      | **0.135**       |

| Category      | Method     | ScanNet-4 PSNR ↑ | ScanNet-4 SSIM ↑ | ScanNet-4 LPIPS ↓ | ScanNet-8 PSNR ↑ | ScanNet-8 SSIM ↑ | ScanNet-8 LPIPS ↓ |
| ------------- | ---------- | ---------------- | ---------------- | ----------------- | ---------------- | ---------------- | ----------------- |
| Pose-required | MVSplat    | 24.48            | 0.854            | 0.225             | 23.11            | 0.761            | 0.296             |
| Pose-required | FreeSplat  | 27.23            | 0.873            | 0.196             | 24.64            | 0.819            | 0.241             |
| Pose-free     | NoPoSplat  | 27.10            | 0.864            | 0.189             | 24.26            | 0.796            | 0.269             |
| Pose-free     | VicaSplat  | 26.46            | 0.837            | 0.214             | 22.95            | 0.765            | 0.306             |
| Pose-free     | SPFSplat   | 27.17            | 0.873            | 0.185             | 24.15            | 0.793            | 0.263             |
| Pose-free     | AnySplat\* | 22.74            | 0.768            | 0.242             | 21.83            | 0.673            | 0.358             |
| Pose-free     | AnySplat   | 17.07            | 0.580            | 0.436             | 16.72            | 0.577            | 0.457             |
| Pose-free     | **Ours**   | **28.15**        | **0.884**        | **0.178**         | **25.15**        | **0.824**        | **0.233**         |

The paper's stated comparison: in dense-view scenarios TokenSplat surpasses pose-dependent methods like FreeSplat, achieving **0.95 dB higher PSNR on RE10K with 8 views** (26.15 vs 25.20). Cross-dataset, it reports up to **0.92/0.51 dB higher PSNR** than FreeSplat.

### NVS on ScanNet Across View Counts

원논문 Table 2. The 28-view column uses models trained with 10 views.

| Category      | Method     | 3v PSNR ↑ | 3v SSIM ↑ | 3v LPIPS ↓ | 10v PSNR ↑ | 10v SSIM ↑ | 10v LPIPS ↓ | 28v PSNR ↑ | 28v SSIM ↑ | 28v LPIPS ↓ |
| ------------- | ---------- | --------- | --------- | ---------- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| Pose-required | MVSplat    | 24.98     | 0.784     | 0.228      | 23.12      | 0.768      | 0.236       | 22.26      | 0.714      | 0.336       |
| Pose-required | FreeSplat  | 25.63     | 0.804     | 0.218      | 25.38      | 0.815      | 0.189       | 24.30      | 0.798      | 0.249       |
| Pose-free     | NoPoSplat  | 25.55     | 0.803     | 0.213      | 24.21      | 0.811      | 0.198       | 23.21      | 0.764      | 0.268       |
| Pose-free     | VicaSplat  | 24.54     | 0.786     | 0.226      | 23.73      | 0.760      | 0.268       | 22.37      | 0.709      | 0.316       |
| Pose-free     | SPFSplat   | 25.85     | 0.788     | 0.229      | 24.63      | 0.773      | 0.226       | 23.54      | 0.775      | 0.261       |
| Pose-free     | AnySplat\* | 19.84     | 0.658     | 0.314      | 22.06      | 0.687      | 0.353       | 21.17      | 0.680      | 0.357       |
| Pose-free     | AnySplat   | 15.05     | 0.415     | 0.416      | 16.73      | 0.522      | 0.437       | 16.58      | 0.561      | 0.439       |
| Pose-free     | **Ours**   | **26.57** | **0.841** | **0.189**  | **26.83**  | **0.851**  | **0.179**   | **26.87**  | **0.859**  | **0.173**   |

This is the most striking table: every baseline **degrades** from 3 → 28 views (FreeSplat 25.63 → 24.30, NoPoSplat 25.55 → 23.21), while TokenSplat **improves** (26.57 → 26.87). The paper attributes baseline degradation to Gaussian-level fusion accumulating inconsistencies and redundancies as views are added, versus TokenSplat's feature-space fusion. It reports a **higher SSIM of 0.061 over FreeSplat** as view count grows.

### Pose Estimation on RE10K and Cross-Dataset ScanNet

원논문 Table 3. For NoPoSplat, poses are estimated via PnP with RANSAC from predicted Gaussian centers; the other methods output poses directly.

| Method     | RE10K-4 ATE ↓ | RE10K-4 RPE-t ↓ | RE10K-4 RPE-r ↓ | RE10K-8 ATE ↓ | RE10K-8 RPE-t ↓ | RE10K-8 RPE-r ↓ |
| ---------- | ------------- | --------------- | --------------- | ------------- | --------------- | --------------- |
| NoPoSplat  | 0.032         | 0.070           | 1.923           | 0.123         | 0.135           | 1.757           |
| VicaSplat  | 0.027         | 0.057           | 1.392           | 0.021         | 0.031           | 0.793           |
| SPFSplat   | 0.036         | 0.078           | 3.113           | 0.037         | 0.047           | 2.117           |
| AnySplat\* | 0.028         | 0.051           | 1.515           | 0.020         | 0.025           | 0.578           |
| AnySplat   | 0.033         | 0.055           | 1.624           | 0.024         | 0.029           | 0.605           |
| **Ours**   | **0.016**     | **0.034**       | **1.054**       | **0.012**     | **0.019**       | **0.458**       |

| Method     | ScanNet-4 ATE ↓ | ScanNet-4 RPE-t ↓ | ScanNet-4 RPE-r ↓ | ScanNet-8 ATE ↓ | ScanNet-8 RPE-t ↓ | ScanNet-8 RPE-r ↓ |
| ---------- | --------------- | ----------------- | ----------------- | --------------- | ----------------- | ----------------- |
| NoPoSplat  | 0.139           | 0.259             | 2.135             | 0.208           | 0.268             | 4.098             |
| VicaSplat  | 0.095           | 0.234             | 2.735             | 0.163           | 0.197             | 3.162             |
| SPFSplat   | 0.075           | 0.201             | 2.658             | 0.121           | 0.173             | 3.676             |
| AnySplat\* | 0.092           | 0.238             | 1.902             | 0.098           | 0.150             | 2.016             |
| AnySplat   | 0.099           | 0.268             | 1.995             | 0.101           | 0.157             | 2.114             |
| **Ours**   | **0.062**       | **0.159**         | **1.162**         | **0.088**       | **0.130**         | **1.672**         |

The paper's stated deltas on RE10K 8-view: RPE-r reduced by **0.335** vs VicaSplat and **0.147** vs AnySplat. Cross-dataset, ATE reduced by **0.013/0.033** over SPFSplat.

### Pose Estimation on ScanNet Across View Counts

원논문 Table 4.

| Method     | 3v ATE ↓  | 3v RPE-t ↓ | 3v RPE-r ↓ | 10v ATE ↓ | 10v RPE-t ↓ | 10v RPE-r ↓ | 28v ATE ↓ | 28v RPE-t ↓ | 28v RPE-r ↓ |
| ---------- | --------- | ---------- | ---------- | --------- | ----------- | ----------- | --------- | ----------- | ----------- |
| NoPoSplat  | 0.055     | 0.218      | 2.041      | 0.167     | 0.175       | 5.537       | 0.187     | 0.197       | 4.551       |
| VicaSplat  | 0.075     | 0.268      | 1.803      | 0.171     | 0.231       | 3.768       | 0.243     | 0.189       | 3.725       |
| SPFSplat   | 0.104     | 0.336      | 2.351      | 0.155     | 0.167       | 3.249       | 0.207     | 0.216       | 4.428       |
| AnySplat\* | 0.057     | 0.198      | 1.567      | 0.135     | 0.181       | 1.165       | 0.097     | 0.094       | 1.239       |
| AnySplat   | 0.062     | 0.213      | 1.611      | 0.148     | 0.196       | 1.192       | 0.098     | 0.091       | 1.362       |
| **Ours**   | **0.041** | **0.147**  | **1.252**  | **0.093** | **0.135**   | **0.799**   | **0.080** | **0.075**   | **0.709**   |

The paper states the 28-view ATE reduction over AnySplat as **0.018**. TokenSplat leads every column here; the strongest baseline is AnySplat\* (3-view RPE-r 1.567, 28-view ATE 0.097).

### Component Ablations

원논문 Table 5, RE10K 8-view.

| Method                 | PSNR ↑    | SSIM ↑    | LPIPS ↓   | ATE ↓     | RPE-t ↓   | RPE-r ↓   |
| ---------------------- | --------- | --------- | --------- | --------- | --------- | --------- |
| (a) Ours               | **26.15** | **0.858** | **0.135** | **0.012** | **0.019** | **0.458** |
| (b) w Pixel Head       | 25.33     | 0.832     | 0.159     | 0.018     | 0.028     | 0.496     |
| (c) w AnySplat Fusion  | 25.77     | 0.847     | 0.148     | 0.020     | 0.027     | 0.489     |
| (d) w/o ADF-Decoder    | 25.88     | 0.845     | 0.146     | 0.023     | 0.029     | 0.504     |
| (e) w/o intrinsic emb. | 25.54     | 0.835     | 0.157     | 0.016     | 0.022     | 0.471     |

The paper's reading of each row:

- **(b)** Replacing token-aligned prediction with a pixel-aligned Gaussian head degrades both reconstruction and pose — SSIM drops by **0.026**, RPE-r rises by **0.038**.
- **(c)** AnySplat-style Gaussian-level fusion is better than a plain pixel head but still behind feature-space fusion.
- **(d)** Removing the ADF-Decoder costs the most on pose (ATE 0.012 → 0.023, nearly double), confirming directionally constrained communication is what disentangles pose from image features.
- **(e)** Removing the known-intrinsic camera embedding reduces reconstruction quality since the model struggles to capture scale, "though pose estimation remains competitive".

## 💡 Insights & Impact

### Fuse Features, Not Gaussians

The paper's central claim is a diagnosis of why pixel-aligned pose-free 3DGS methods do not scale with view count: every additional view contributes another full set of pixel-aligned Gaussians, and fusing them _after_ prediction accumulates inconsistency and redundancy. Table 2 is the evidence — every baseline peaks early and declines, while TokenSplat's feature-space fusion keeps improving out to 28 views despite being trained on 10. This reframes multi-view scaling as a representation choice rather than a capacity problem.

### Asymmetry as Disentanglement

Symmetric attention between camera and image tokens would let pose information leak into scene features and vice versa. The ADF-Decoder's directional constraint — camera tokens read from image tokens and return only specialized pose signals, with image tokens modulating camera tokens before and after — is a structural rather than loss-based approach to factorization. Ablation (d) shows the effect is concentrated on pose metrics, which is exactly what the design predicts.

### Excluding Self-Attention Across Views

A small but notable detail: in image-token cross-view attention, each view explicitly avoids its own tokens. The stated rationale is preventing information leakage and forcing complementary integration — the opposite of the usual "attend to everything" default.

### Dual Quaternions for Pose Supervision

Predicting rotation and translation separately can yield inconsistent pairs. Supervising with a unit dual quaternion alignment loss represents both jointly, a choice inherited from the pose-estimation literature rather than the 3DGS literature.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md) — supplies the initialization weights for TokenSplat's encoder-decoder and Gaussian center head
- [DUSt3R](../foundation/dust3r.md) — the pointmap paradigm underlying pose-free feed-forward reconstruction
- [Splatt3R](splatt3r.md) — an earlier bridge from MASt3R-style geometry to feed-forward 3DGS
- [PREF3R](pref3r.md), [Styl3R](styl3r.md), [FLowR](flowr.md) — related feed-forward Gaussian prediction from unposed or sparse views
- [InstantSplat](instantsplat.md) — pose-free 3DGS relying on optimization rather than a single feed-forward pass
- [VGGT](../reconstruction/vggt.md) — the unified-transformer approach to joint pose and geometry that TokenSplat's camera-token design echoes
- [DUSt3R-GS](dust-gs.md), [DUSt3R-to-Tower](dust-to-tower.md) — other DUSt3R-based Gaussian pipelines

## 📚 Key Takeaways

1. **Feature-space fusion scales where Gaussian-space fusion does not.** TokenSplat improves from 3 to 28 ScanNet views (26.57 → 26.87 PSNR) while every baseline degrades.
2. **Pose-free can beat pose-required.** On RE10K 8-view, TokenSplat exceeds FreeSplat — which consumes ground-truth poses — by 0.95 dB PSNR.
3. **The ADF-Decoder is the pose component.** Removing it roughly doubles ATE (0.012 → 0.023) while costing only ~0.27 dB PSNR.
4. **Token-aligned prediction is the reconstruction component.** Swapping in a pixel-aligned head costs 0.026 SSIM and 0.82 dB PSNR.
5. **Intrinsics embedding carries scale.** Removing it hurts reconstruction more than pose, consistent with scale ambiguity being a geometry problem.
6. **Generalizes zero-shot.** Trained on RE10K, TokenSplat leads all compared methods on ScanNet for both NVS and pose without fine-tuning.

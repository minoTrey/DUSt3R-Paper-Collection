# Cross-View Splatter: Feed-Forward View Synthesis with Georeferenced Images (CVPR 2026)

![cross-view-splatter — architecture](https://arxiv.org/html/2605.19656v1/x2.png)

_Method overview: Given geolocalized ground images and a single orthorectified satellite perspective, our model synthesizes 3D Gaussian splats in a… (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Matias Turkulainen, Akshay Krishnan, Filippo Aleotti, Mohamed Sayed, Guillermo Garcia-Hernando, Juho Kannala, Arno Solin, Gabriel Brostow, Daniyar Turmukhambetov
- **Institution**: Aalto University; Georgia Tech; Niantic Spatial; University of Oulu; ELLIS Institute Finland; UCL
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2605.19656) | [Project Page](https://nianticspatial.github.io/cross-view-splatter/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward model that predicts pixel-aligned Gaussian splats for outdoor scenes from GPS-tagged ground images _and_ a single orthorectified satellite (BEV) image, fusing them in a unified coordinate frame — using satellite imagery from public mapping services as a global geometric prior to improve coverage and novel-view extrapolation over ground imagery alone.

## 🎯 Key Contributions

1. **Cross-view feed-forward splatting**: The first method to synthesize Gaussian splats for both ground-level perspective imagery and orthorectified satellite views, fused in one 3D coordinate frame; only the GPS location of ground images is required at inference.
2. **Curated georeferenced datasets**: Ground-level imagery paired with BEV satellite images and terrain height maps, mined from open mapping services and public Digital Elevation Models.
3. **New benchmark**: A challenging outdoor novel-view-synthesis benchmark of ground images with aligned satellite views, enabling comparison of state-of-the-art feed-forward 3DGS methods.

## 🔧 Technical Details

### Problem setup

Given ground georeferenced images (tagged with 3DoF pose: GPS latitude, longitude, heading) plus a single top-down orthographic satellite image `I_sat` (known resolution `r_sat` in pixels/meter), the model reconstructs a 3DGS scene in a feed-forward pass. The first ground image `I0_ground` defines the world origin and zero-altitude; the satellite frame is centered and heading-aligned to it.

### Architecture

- **Ground branch**: VGGT feature extractor with DINOv2 patch tokens (patch size 14, embedding dim 1024), camera + register tokens, processed by alternating frame/global attention; heads regress 6DoF pose, intrinsics, depth+confidence, and Gaussian params (DPT heads).
- **Satellite branch**: Because orthoimagery lacks perspective/6DoF, BEV geometry is framed as _height-map regression_ relative to `I0_ground`; a DPT height head outputs `h_sat` + confidence, converted to 3D Gaussian means via `r_sat` under an orthographic projection.
- **Attn_meta**: bidirectional cross-attention between ground and satellite tokens, applied L = 12 times, aligning the two feature spaces.
- Gaussians (means, covariance, opacity, order-1 SH colors) are predicted separately for ground (`G_ground`) and satellite (`G_sat`) and merged into `G_combined`.

### Losses and training

- Ground: confidence-weighted depth loss, camera L1 loss, Gaussian-size depth-consistency loss, RGB + LPIPS rendering loss. Satellite: confidence-weighted height loss, RGB rendering to input and novel views. A combined RGB loss on `G_ground ∪ G_sat`, a BEV rendering loss, and sky regularization (promoting far, opaque sky Gaussians).
- Initialized from AnySplat; trained 4 days on 2× A100, batch size 10, FlashAttention-v2, mixed precision. Satellite/terrain spatial extent 244 m; input resolution 518×518.

## 📊 Results

Metrics: PSNR↑, SSIM↑, LPIPS↓. Benchmark built by aligning COLMAP reconstructions of 10 Tanks and Temples outdoor scenes and 40 DL3DV scenes to satellite imagery. Cross-View Splatter reports ground-only, terrain-only, and combined variants. Overall PSNR is low because input–target pairs have low overlap (IoU ≈ 0.05–0.5). Methods marked * use ground-truth intrinsics / need multi-view input; Sat2Density† uses a single satellite image stylized with one context view.

원논문 Table 2 (Tanks and Temples, averaged over 10 scenes).

| Method          | 1V PSNR↑ | SSIM↑  | LPIPS↓ | 2V PSNR↑ | SSIM↑  | LPIPS↓ | 3V PSNR↑ | SSIM↑  | LPIPS↓ |
| --------------- | -------- | ------ | ------ | -------- | ------ | ------ | -------- | ------ | ------ |
| Splatfacto      | -        | -      | -      | 11.53    | 0.2611 | 0.6436 | 11.72    | 0.2888 | 0.6267 |
| MVSplat         | -        | -      | -      | 6.93     | 0.1252 | 0.6997 | 7.58     | 0.1631 | 0.6941 |
| DepthSplat      | -        | -      | -      | 9.61     | 0.3146 | 0.6077 | 10.72    | 0.3557 | 0.5873 |
| NoPoSplat       | 6.43     | 0.1062 | 0.7040 | 8.97     | 0.2197 | 0.6830 | 8.82     | 0.2359 | 0.6825 |
| Long-LRM        | 8.53     | 0.3392 | 0.7054 | 8.53     | 0.3392 | 0.7054 | 10.54    | 0.3253 | 0.6477 |
| AnySplat        | 7.48     | 0.3572 | 0.6482 | 9.85     | 0.3483 | 0.5773 | 10.93    | 0.3775 | 0.5331 |
| Sat2Density†    | 8.81     | 0.3557 | 0.8172 | 8.90     | 0.3507 | 0.8097 | 8.85     | 0.3508 | 0.8037 |
| Ours (Combined) | 11.13    | 0.3764 | 0.6286 | 11.67    | 0.3725 | 0.5984 | 12.00    | 0.3855 | 0.5699 |
| Ours (Ground)   | 8.92     | 0.3621 | 0.6066 | 9.94     | 0.3615 | 0.5877 | 10.61    | 0.3763 | 0.5631 |
| Ours (Terrain)  | 8.39     | 0.3783 | 0.6257 | 9.82     | 0.4341 | 0.7474 | 9.63     | 0.4301 | 0.7472 |

원논문 Table 3 (DL3DV, averaged over 40 scenes).

| Method          | 1V PSNR↑ | SSIM↑  | LPIPS↓ | 2V PSNR↑ | SSIM↑  | LPIPS↓ | 3V PSNR↑ | SSIM↑  | LPIPS↓ |
| --------------- | -------- | ------ | ------ | -------- | ------ | ------ | -------- | ------ | ------ |
| Splatfacto      | -        | -      | -      | 13.46    | 0.2962 | 0.6158 | 13.61    | 0.3018 | 0.6026 |
| MVSplat         | -        | -      | -      | 6.27     | 0.0413 | 0.7174 | 6.29     | 0.0474 | 0.7158 |
| DepthSplat      | -        | -      | -      | 8.58     | 0.1569 | 0.6774 | 9.04     | 0.1817 | 0.6761 |
| NoPoSplat       | 6.89     | 0.0669 | 0.7019 | 11.01    | 0.2670 | 0.6665 | 11.10    | 0.2731 | 0.6687 |
| Long-LRM        | 4.78     | 0.3153 | 0.7196 | 9.74     | 0.2842 | 0.6813 | 10.93    | 0.2890 | 0.6149 |
| AnySplat        | 8.37     | 0.2639 | 0.6498 | 10.37    | 0.3014 | 0.5702 | 10.88    | 0.3122 | 0.5557 |
| Ours (Combined) | 11.33    | 0.2741 | 0.6307 | 12.10    | 0.2976 | 0.5940 | 12.61    | 0.3204 | 0.5683 |
| Ours (Ground)   | 9.00     | 0.2592 | 0.6191 | 10.05    | 0.2878 | 0.5842 | 10.65    | 0.3103 | 0.5606 |
| Ours (Terrain)  | 8.24     | 0.2790 | 0.6884 | 8.41     | 0.2801 | 0.6932 | 8.30     | 0.2834 | 0.6928 |

The Combined variant leads on PSNR at every context level (notably in the hardest 1-context case), and gains are largest at low overlap (≤0.15 IoU), showing stronger extrapolation. It does not win every metric: AnySplat has a lower (better) LPIPS at 2–3 views on T&T (e.g. 0.5331 vs 0.5699 at 3 views), and per-scene Splatfacto stays competitive on PSNR.

원논문 Table 4 (Metropolis ablation, averaged over 36 test scenes, 2 input + 2 interpolated novel views; PSNR).

| Method                                                     | Ground PSNR | Terrain PSNR | Combined PSNR |
| ---------------------------------------------------------- | ----------- | ------------ | ------------- |
| VGGT w/ 3DGS: Lcam + Ldepth + Lground_RGB                  | 15.26       | -            | -             |
| + Lconst                                                   | 16.99       | -            | -             |
| + Lsky                                                     | 17.10       | -            | -             |
| VGGT w/ 3DGS w/ SAT: Lcam+Ldepth+Lconst+Lsky+Lcombined_RGB | 16.99       | 5.24         | 17.17         |
| + Lground_RGB                                              | 16.61       | 5.36         | 16.87         |
| + Lsat_RGB                                                 | 17.59       | 12.25        | 18.63         |

Consistency (Lconst) and sky (Lsky) regularization each help the ground-only model; the full satellite-aware model with the satellite RGB loss performs best (Combined 18.63 PSNR), attributed to better BEV coverage of occluded/unseen regions.

## 💡 Insights & Impact

- 3D foundation models are trained almost entirely on ground-level calibrated imagery, so they struggle in the cross-view satellite setting; the paper's hybrid strategy reuses pretrained backbones for ground geometry and fine-tunes satellite-specific layers.
- Orthorectified web-map imagery removes perspective and parallax, making classical MVS impossible on it — so satellite geometry is learned as a height map and directly _rendered_ to ground views via splatting rather than warped.
- Unlike generative satellite-to-ground methods, this feed-forward approach synthesizes only visible ground and satellite regions without hallucinating unobserved areas.
- Satellite imagery's coarse resolution and variation in weather/illumination/season remain challenging; only GPS + heading metadata are needed at inference.

## 🔗 Related Work

- Built on the feed-forward geometry line: [DUSt3R](../foundation/dust3r.md), [MASt3R-SfM](../foundation/mast3r-sfm.md), [MapAnything](../reconstruction/mapanything.md), and the [VGGT](../reconstruction/vggt.md) backbone; initialized from AnySplat weights.
- Feed-forward NVS baselines: MVSplat, DepthSplat, NoPoSplat, Long-LRM, AnySplat; satellite-to-ground baseline Sat2Density.
- Related in-collection feed-forward Gaussian splatting: [Splatt3R](splatt3r.md), and the [WorldMirror](../reconstruction/worldmirror.md) universal-prior line.

## 📚 Key Takeaways

1. GPS-tagged ground photos plus a free satellite tile can be jointly splatted in one coordinate frame, turning bird's-eye imagery into a geometric prior for outdoor novel-view synthesis.
2. Framing satellite geometry as height-map regression (not depth) sidesteps the impossibility of MVS on orthorectified tiles, and rendering it directly avoids warping artifacts.
3. On a new low-overlap benchmark (T&T + DL3DV), the combined model leads on PSNR across all context counts with the biggest gains at low overlap — while honestly not dominating LPIPS against AnySplat at higher view counts.

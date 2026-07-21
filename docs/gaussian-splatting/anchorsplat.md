# AnchorSplat: Feed-Forward 3D Gaussian Splatting with 3D Geometric Priors (CVPR 2026)

## 📋 Overview

- **Authors**: Xiaoxue Zhang, Xiaoxu Zheng, Yixuan Yin, Tiao Zhao, Kaihua Tang, Michael Bi Mi, Zhan Xu, Dave Zhenyu Chen
- **Institution**: Huawei Technologies Ltd.
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2604.07053)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward 3DGS framework that predicts Gaussians aligned to sparse 3D _anchors_ (from geometric priors) rather than to 2D pixels, decoupling the representation from image resolution and view count — using ~20× fewer Gaussians and about half the reconstruction time of the pixel/voxel-aligned baseline AnySplat, with a plug-and-play Gaussian Refiner.

## 🎯 Key Contributions

1. **Anchor-aligned feed-forward Gaussian model**: Represents the scene directly in 3D space by back-projecting multi-view features onto a sparse set of 3D anchors, giving a representation independent of input pixel count and viewpoint coverage.
2. **Plug-and-play Gaussian Refiner**: A module that adjusts predicted Gaussian attributes (position, scale, opacity, color) from rendering error in a few forward passes, applicable without retraining the full model.
3. **Efficiency with fidelity**: Superior/competitive reconstruction quality on ScanNet++ v2 while using far fewer Gaussians and less reconstruction time than optimization-based 3DGS/Mip-Splatting and feed-forward AnySplat.

## 🔧 Technical Details

### Pipeline (three stages)

- **Anchor Predictor**: A pretrained multi-view stereo module (e.g., MapAnything) predicts depths and camera poses; predictions are back-projected to 3D and downsampled by farthest-point sampling (FPS), with the count set by voxelizing the 3D space, giving anchors `A_j` with `N ≪ V×H×W`.
- **Gaussian Decoder**: A 2D U-Net encodes each image + depth + camera-ray embedding; features are projected onto the 3D anchors and processed by a transformer, and an MLP predicts, per anchor, four Gaussians (offset δµ, opacity, scale, rotation, SH). Absolute centers are `µ_j = A_j + δµ_j`, constrained to a small range (e.g. 10/128) around each anchor.
- **Gaussian Refiner**: Inspired by G3R, a pretrained ResNet-18 extracts multi-scale features from rendered and GT images; the per-view render error is back-projected to 3D Gaussians, refined by a transformer block and a Point-Transformer, and added as an offset `Ĝ_j = G_j + δG_j`.

### Training

- Two stages: (1) train the Gaussian Decoder (rendering loss `ℓ_I` = L1 + SSIM + LPIPS, depth loss, opacity `ℓ_α` and scale `ℓ_s` regularizers); (2) freeze the decoder and train only the Refiner with rendering loss.
- Loss weights: λ_I = 200, γ_SSIM = 0.2, γ_LPIPS = 0.2, λ_D = 100, λ_α = 1e−1, λ_s = 1e4. SH degree 0.
- Decoder: 84M params, 16 attention blocks (640 channels), 5k steps. Refiner: 31M params, 1 attention block (512 channels) + 4 serialized attention blocks, 5k steps.
- Trained on 64 Ascend 910B3 (64GB) NPUs, bfloat16, AdamW. Input images at 1168×1752; rendering/supervision at 448×672.

## 📊 Results

Benchmark: ScanNet++ v2. Metrics: PSNR↑, SSIM↑, LPIPS↓, depth δ1↑, AbsRel↓, plus NumGS and reconstruction time. AnchorSplat⋆ denotes the model without the Gaussian Refiner.

원논문 Table 1 (novel 4-view, 32 input views).

| Model         | Category     | PSNR↑ | SSIM↑ | LPIPS↓ | δ1↑  | AbsRel↓ | NumGS     | ReconTime(s) |
| ------------- | ------------ | ----- | ----- | ------ | ---- | ------- | --------- | ------------ |
| 3DGS          | Opt.         | 19.98 | 0.72  | 0.30   | 0.31 | 0.42    | 496,087   | 391.44       |
| Mip-Splatting | Opt.         | 19.92 | 0.75  | 0.34   | 0.35 | 0.38    | 398,212   | 289.95       |
| AnySplat      | feed-forward | 20.20 | 0.73  | 0.32   | 0.71 | 0.16    | 5,550,940 | 6.83         |
| AnchorSplat⋆  | feed-forward | 20.96 | 0.78  | 0.47   | 0.94 | 0.068   | 247,153   | 3.11         |
| AnchorSplat   | feed-forward | 21.48 | 0.79  | 0.38   | 0.94 | 0.066   | 247,153   | 5.52         |

AnchorSplat wins on PSNR, SSIM, and both depth metrics with ~22× fewer Gaussians, but note it _loses on LPIPS_: even with the Refiner (0.38) it is worse than AnySplat's 0.32 and optimization-based 3DGS's 0.30.

원논문 Table 2 (varying input/novel views).

| Exp setting  | Model        | PSNR↑ | SSIM↑ | LPIPS↓ | δ1↑  | AbsRel↓ | NumGS      | ReconTime(s) |
| ------------ | ------------ | ----- | ----- | ------ | ---- | ------- | ---------- | ------------ |
| 32 sv / 4 nv | AnySplat     | 20.20 | 0.73  | 0.32   | 0.71 | 0.16    | 5,550,940  | 6.83         |
| 32 sv / 4 nv | AnchorSplat⋆ | 20.96 | 0.78  | 0.47   | 0.94 | 0.068   | 247,153    | 3.11         |
| 32 sv / 4 nv | AnchorSplat  | 21.48 | 0.79  | 0.38   | 0.94 | 0.066   | 247,153    | 5.52         |
| 48 sv / 6 nv | AnySplat     | 20.66 | 0.74  | 0.31   | 0.67 | 0.17    | 8,197,441  | 7.57         |
| 48 sv / 6 nv | AnchorSplat⋆ | 20.80 | 0.78  | 0.48   | 0.94 | 0.064   | 247,153    | 3.23         |
| 48 sv / 6 nv | AnchorSplat  | 21.42 | 0.79  | 0.38   | 0.94 | 0.066   | 247,153    | 5.43         |
| 64 sv / 8 nv | AnySplat     | 20.78 | 0.73  | 0.32   | 0.72 | 0.16    | 10,660,487 | 9.54         |
| 64 sv / 8 nv | AnchorSplat⋆ | 21.10 | 0.78  | 0.47   | 0.94 | 0.064   | 247,153    | 3.71         |
| 64 sv / 8 nv | AnchorSplat  | 21.82 | 0.80  | 0.37   | 0.94 | 0.065   | 247,153    | 6.13         |

The anchor count (247,153) is fixed regardless of input view count, whereas AnySplat's Gaussian count grows linearly (5.5M → 10.7M) with views.

원논문 Table 3 (extremely sparse and dense inputs).

| Exp setting    | Method       | PSNR↑ | SSIM↑ | LPIPS↓ | δ1↑  | AbsRel↓ | NumGS      | ReconTime(s) |
| -------------- | ------------ | ----- | ----- | ------ | ---- | ------- | ---------- | ------------ |
| 3 sv / 1 nv    | AnySplat     | 19.51 | 0.68  | 0.38   | 0.70 | 0.18    | 543,987    | 1.34         |
| 3 sv / 1 nv    | AnchorSplat⋆ | 19.99 | 0.78  | 0.38   | 0.92 | 0.073   | 247,153    | 3.18         |
| 5 sv / 1 nv    | AnySplat     | 20.21 | 0.77  | 0.36   | 0.71 | 0.17    | 909,132    | 2.25         |
| 5 sv / 1 nv    | AnchorSplat⋆ | 20.35 | 0.78  | 0.38   | 0.92 | 0.073   | 247,153    | 3.23         |
| 128 sv / 16 nv | AnySplat     | 20.47 | 0.74  | 0.34   | 0.75 | 0.18    | 19,767,552 | 31.67        |
| 128 sv / 16 nv | AnchorSplat⋆ | 21.58 | 0.79  | 0.37   | 0.94 | 0.058   | 247,153    | 7.36         |
| 256 sv / 32 nv | AnySplat     | OOM   | OOM   | OOM    | OOM  | OOM     | OOM        | OOM          |
| 256 sv / 32 nv | AnchorSplat⋆ | 21.42 | 0.79  | 0.38   | 0.93 | 0.064   | 247,153    | 10.21        |

At 256 views AnySplat runs out of memory while AnchorSplat⋆ stays at 247,153 Gaussians and 10.21 s. Note that in the very sparse 3-view case AnchorSplat⋆'s reconstruction time (3.18 s) exceeds AnySplat's (1.34 s), since the anchor budget is fixed.

## 💡 Insights & Impact

- Pixel-aligned Gaussians grow linearly with pixels/views, yield view-biased density (over-representing frequently observed regions, under-covering complex ones), and produce floaters because 2D features interact weakly with 3D neighbors. Anchoring in 3D removes this dependence on image resolution and view count.
- Depth accuracy (δ1 up to 0.94, AbsRel down to ~0.058) improves markedly over AnySplat (δ1 ≈ 0.71, AbsRel ≈ 0.16), reflecting the geometry-aware anchor representation.
- **Limitation (authors)**: AnchorSplat depends on reasonably accurate geometric priors; when priors are incomplete, the constrained Gaussian growth/budget leaves empty regions hard to cover, degrading quality. Future work: adaptive density control and dynamic Gaussian growth.

## 🔗 Related Work

- Uses feed-forward MVS priors: [MapAnything](../reconstruction/mapanything.md) (anchor predictor), MVSAnywhere, and [Reliev3R](../reconstruction/reliev3r.md).
- Positioned against the pixel/voxel-aligned feed-forward line: AnySplat (baseline), the LRM family including [iLRM](../reconstruction/ilrm.md), [WorldMirror](../reconstruction/worldmirror.md), and [YoNoSplat](yonosplat.md).
- Part of the DUSt3R-lineage of feed-forward reconstruction ([DUSt3R](../foundation/dust3r.md), [VGGT](../reconstruction/vggt.md)) that supplies poses/depth as geometric priors.

## 📚 Key Takeaways

1. Anchoring Gaussians to a fixed, geometry-derived 3D point set (each anchor spawning 4 Gaussians) decouples representation size from image resolution and view count.
2. The fixed 247,153-Gaussian budget stays constant from 3 to 256 input views, where AnySplat's count grows to ~20M and eventually OOMs.
3. AnchorSplat leads on PSNR, SSIM, and depth with ~20× fewer Gaussians and roughly half the reconstruction time, but it does not beat AnySplat on LPIPS — an honest trade-off toward geometric consistency and efficiency.

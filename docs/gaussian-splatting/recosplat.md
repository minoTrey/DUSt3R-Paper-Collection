# ReCoSplat: Autoregressive Feed-Forward Gaussian Splatting Using Render-and-Compare (arXiv preprint (2026-03))

![recosplat — architecture](https://arxiv.org/html/2603.09968v1/x1.png)

_Autoregressive Reconstruction (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Freeman Cheng, Botao Ye, Xueting Li, Junqi You, Fangneng Zhan, Ming-Hsuan Yang
- **Institution**: University of California Merced; ETH Zurich; NVIDIA; Shanghai Jiao Tong University; Hong Kong University of Science and Technology
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.09968) | [Project Page](https://freemancheng.com/ReCoSplat)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An autoregressive feed-forward 3DGS model for online novel view synthesis that handles posed/unposed inputs with or without intrinsics; a Render-and-Compare module renders the current reconstruction at the predicted assembly pose and compares it with the incoming image to bridge the ground-truth→predicted pose distribution mismatch, plus a hybrid KV-cache compression that cuts cache size >90% for 100+ frames.

## 🎯 Key Contributions

1. **Render-and-Compare (ReCo) module**: Renders the accumulated scene at each incoming view's assembly pose and uses the rendered–observed comparison as a cross-attention conditioning signal, bridging the pose distribution mismatch created by training with ground-truth but inferring with predicted assembly poses.
2. **Hybrid KV-cache compression**: Combines early-layer truncation (discarding caches for the first 10 of 18 global-attention layers) with chunk-level selective retention (keeping only one representative view per chunk, marked by a trainable register token), reducing KV-cache memory ~10× (93% for 256 frames) and enabling real-time reconstruction on consumer hardware.
3. **State-of-the-art autoregressive results**: Consistent SOTA across posed/unposed and with/without intrinsics on in- and out-of-distribution datasets and diverse trajectories.

## 🔧 Technical Details

### Problem setting

- Processes a continuous stream in non-overlapping chunks of `n ∈ [4,8]` images. At step `t`, `f_θ` takes a chunk `I_t`, optional intrinsics `K_t` / extrinsics `P_t`, the KV cache `M_{t-1}`, and accumulated scene `S_{t-1}`, and predicts local Gaussians `G_t`, camera params `K̂_t, P̂_t`, and updated cache `M_t`. Local Gaussians are transformed to world coordinates via an **assembly pose** `A_t` (ground-truth or predicted) and merged into `S_t`.

### Backbone

- Built on **YoNoSplat**, augmented with a KV cache. A DINOv2-initialized ViT encoder yields a camera token and patch tokens; intrinsics predicted from the camera token via a 2-layer MLP. A 36-layer alternating-attention (frame/global) transformer decoder (from **π³**) produces multi-view features. Pose head (5-layer transformer + MLP), position/attribute heads (5-layer transformers), and a DPT feature head decode Gaussians from 2×-upsampled features, each cross-attending to ReCo tokens.

### Render-and-Compare

- For each image, render the accumulated scene `S_{t-1}` at its assembly pose to get `R̂ ∈ ℝ^{H×W×12}` (RGB + 9 learned feature channels); concatenate with the input image and patchify (3 strided conv layers) into conditioning tokens `Z` that guide Gaussian prediction. When intrinsics are unavailable, predicted intrinsics are used for rendering to avoid information leakage.

### Efficient long sequences

- **Memory complexity** drops from Θ(L·N) to Θ(N/n): no historical tokens for the first 10 layers; for the remaining 8, keep the initial 8-image chunk plus one set per subsequent chunk. For N=256, n=8 a standard cache stores 4608 token sets vs 312 here — a 93% reduction.

### Training

- Three stages (150k + 50k + 50k steps) from a YoNoSplat DL3DV-10K checkpoint, progressively introducing variable chunk sizes and KV-cache compression; 8 GPUs, batch 1, 224×224. Loss `L = L_MSE + L_LPIPS + L_intrinsic + L_extrinsic + L_opacity` (weights 1.0 / 0.05 / 0.5 / 0.1 / 0.01), Gaussians below opacity 0.005 pruned. First-chunk scale alignment fixes the global scale since future poses are unavailable.

## 📊 Results

Trained/evaluated on DL3DV and ScanNet++, with RealEstate10K, ACID, and ScanNet for generalization. YoNoSplat is an **offline** upper-bound baseline; KV Cache = ReCoSplat without the ReCo module; GIR = ReCoSplat conditioned on LongSplat's Gaussian-Image Representation instead.

### DL3DV, unposed & uncalibrated

원논문 Table 1 (p✗ k✗). 지표 PSNR↑, SSIM↑, LPIPS↓ (32뷰·256뷰). YoNoSplat은 오프라인 상한.

| Method              | 32v PSNR ↑ | 32v SSIM ↑ | 32v LPIPS ↓ | 256v PSNR ↑ | 256v SSIM ↑ | 256v LPIPS ↓ |
| ------------------- | ---------- | ---------- | ----------- | ----------- | ----------- | ------------ |
| YoNoSplat (offline) | 22.368     | 0.736      | 0.180       | 20.749      | 0.677       | 0.226        |
| KV Cache            | 21.705     | 0.703      | 0.202       | 19.819      | 0.606       | 0.292        |
| GIR                 | 21.752     | 0.703      | 0.203       | 19.900      | 0.608       | 0.291        |
| **Ours**            | **22.097** | **0.716**  | **0.194**   | **20.220**  | **0.617**   | **0.281**    |

ReCoSplat beats both autoregressive baselines (KV Cache, GIR) across view counts; it trails the offline YoNoSplat, which sees the whole sequence upfront.

### DL3DV, fully posed & calibrated

원논문 Table 1 (p✓ k✓). 지표 PSNR↑, SSIM↑, LPIPS↓.

| Method              | 32v PSNR ↑ | 32v SSIM ↑ | 32v LPIPS ↓ | 256v PSNR ↑ | 256v SSIM ↑ | 256v LPIPS ↓ |
| ------------------- | ---------- | ---------- | ----------- | ----------- | ----------- | ------------ |
| YoNoSplat (offline) | 22.998     | 0.781      | 0.162       | 21.549      | 0.749       | 0.190        |
| KV Cache            | 22.392     | 0.758      | 0.177       | 20.694      | 0.699       | 0.235        |
| GIR                 | 22.478     | 0.760      | 0.177       | 20.743      | 0.699       | 0.235        |
| **Ours**            | **23.084** | 0.780      | 0.164       | **22.003**  | **0.751**   | 0.202        |

With pose errors removed, ReCoSplat surpasses even the offline YoNoSplat in PSNR (e.g. 256v: 22.003 vs 21.549), evidencing that ReCo corrects local Gaussian mispredictions.

### Out-of-distribution (ScanNet, RealEstate10K, ScanNet++)

원논문 Table 2·3에 따르면, posed&calibrated 설정에서 ReCoSplat이 autoregressive baseline을 일관되게 앞선다: ScanNet 32v에서 24.073 PSNR(KV Cache 23.252, GIR 23.315), RealEstate10K 64v에서 25.830 PSNR(0.884 SSIM), ScanNet++ 512v에서 20.308 PSNR(0.734 SSIM). ScanNet에서 오프라인 어댑트 FreeSplat(32v, 22.691 PSNR)도 상회.

### Pose supervision ablation (DL3DV, 32 views, unposed & calibrated)

원논문 Table 5 (single-view 설정, KV Cache backbone). 지표 PSNR↑, SSIM↑, LPIPS↓.

| Method                             | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ---------------------------------- | ---------- | --------- | --------- |
| KV Cache                           | **21.346** | 0.680     | 0.224     |
| KV Cache + Predicted Assembly Pose | 20.781     | 0.641     | 0.238     |
| KV Cache + Mixed Assembly Pose     | 21.316     | **0.681** | **0.223** |
| KV Cache + Plücker Raymap          | 21.166     | 0.676     | 0.228     |

Training with predicted assembly poses significantly degrades quality; mixed poses are negligible over ground-truth-only; Plücker-raymap conditioning (geometric rays without reconstruction appearance) is worse — motivating the appearance-based ReCo signal instead.

### Camera pose estimation and memory

- On ACID / RealEstate10K / DL3DV pose AUC, ReCoSplat is the best autoregressive method, e.g. RealEstate10K 128v AUC@20° 0.905 vs CUT3R 0.666 and TTT3R 0.748 (원논문 Table 4), despite CUT3R/TTT3R being trained on RealEstate10K; the offline YoNoSplat still scores higher.
- KV-cache compression has minimal quality impact while sharply cutting VRAM at high view counts (원논문 Fig. 5, 수치 미인쇄); curriculum learning enables variable chunk sizes at test time with negligible loss (원논문 Table 6).

## 💡 Insights & Impact

- **Analysis-by-synthesis for pose robustness**: Rendering the current scene and comparing to the observation gives a conditioning signal that directly reacts to assembly-pose errors — a cheaper, more effective alternative to pose-mixing curricula, which fail because autoregressive pose estimates are too noisy to supervise.
- **Decoupling task and memory**: Training with ground-truth poses keeps Gaussian prediction decoupled from pose estimation, while ReCo restores robustness to predicted poses at inference — and the KV-cache compression makes 100+-frame streams feasible on consumer GPUs.
- **Online vs offline gap**: With clean poses ReCoSplat even beats the offline YoNoSplat in PSNR, indicating the remaining gap in unposed settings is bounded mainly by online pose-estimation accuracy.
- **Limitations**: Reconstruction quality in unposed settings cannot be fully independent of pose accuracy; large pose errors still propagate into Gaussian assembly.

## 🔗 Related Work

- Built on the YoNoSplat feed-forward Gaussian backbone and the [Pi3](../reconstruction/pi3.md) (π³) permutation-equivariant decoder, in the feed-forward 3DGS line from PixelSplat, GS-LRM, AnySplat, NoPoSplat, and DepthSplat.
- Positioned against autoregressive/streaming methods StreamGS, SaLon3R, LongSplat (excluded from comparison due to unavailable code) and adapts FreeSplat as a baseline; contrasts with streaming pointmap models [CUT3R](../dynamic/cut3r.md), TTT3R, StreamVGGT, WinT3R, Point3R for pose estimation, building on the [DUSt3R](../foundation/dust3r.md)/[VGGT](../reconstruction/vggt.md) foundation.
- The ReCo module draws on the Analysis-by-Synthesis / vision-as-inverse-problem framework.

## 📚 Key Takeaways

1. ReCoSplat brings feed-forward 3DGS to the autoregressive/online setting, handling posed or unposed streams with or without intrinsics.
2. Its Render-and-Compare module bridges the ground-truth→predicted assembly-pose mismatch, driving the largest gains in unposed settings and even beating offline YoNoSplat in PSNR when poses are clean.
3. A hybrid KV-cache compression cuts cache memory ~10× (93% at 256 frames) with negligible quality loss, making 100+-frame online reconstruction practical on consumer hardware.

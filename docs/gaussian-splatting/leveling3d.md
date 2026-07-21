# Leveling3D: Leveling Up 3D Reconstruction with Feed-Forward 3D Gaussian Splatting and Geometry-Aware Generation (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Yiming Huang, Baixiang Huang, Beilei Cui, CHI KIT NG, Long Bai, Hongliang Ren
- **Institution**: The Chinese University of Hong Kong
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.16211)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A framework that tightly couples feed-forward 3DGS (AnySplat) with geometry-conditioned diffusion (Stable Diffusion 2) via a lightweight "leveling adapter" — refining artifact-ridden extrapolated views with geometry-aware generation and feeding them back to level up the 3D reconstruction, setting SOTA on unseen NVS and depth benchmarks.

## 🎯 Key Contributions

1. **Reconstruction–generation coupling**: The first framework to tightly couple feed-forward 3D reconstruction with geometry-conditioned diffusion generation for simultaneous reconstruction and generation, rather than treating diffusion as a 2D post-process.
2. **Geometry-aware leveling adapter**: A lightweight adapter that injects 3D geometry-prior tokens (aggregated by the VGGT-distilled AnySplat encoder) into the diffusion model via cross-attention, grounding 2D generation in 3D structure.
3. **Palette filtering + test-time mask refinement**: A palette-filtering training strategy that keeps an approximately normal (non-degenerate) appearance distribution to prevent mode collapse, and a morphological test-time mask refinement for seamless boundaries between reconstructed and generated regions.
4. **Feedback refinement**: Enhanced extrapolated views are fed back as inputs to the feed-forward 3DGS, improving both geometry and appearance.

## 🔧 Technical Details

### Pipeline

- Built on **AnySplat** (feed-forward 3DGS distilled from VGGT) and **Stable Diffusion 2** (inpainting-finetuned). Given sparse (typically 2-view) inputs, AnySplat produces a coarse 3DGS; extrapolated poses are rendered to obtain coarse novel views and opacity masks; the leveling adapter refines them; refined views are appended and re-fed to AnySplat to produce the completed reconstruction `Ĝ` (Algorithm 1).

### Geometry-aware leveling adapter

- One projection layer (8×8 conv, stride 8, mapping 512×512 → 64×64), four feature-extraction blocks (each a conv + two ConvNeXt blocks), and three downsample blocks.
- The condition image is patchified into tokens (patch size p=14, VGGT-style); a cross-attention (`W_Q, W_K, W_V ∈ ℝ^{768×768}`) fuses reference-image tokens (Q, K) with geometry tokens (V) to form a condition residual `C_res`; the augmented condition `Ĉ = C + C_res` yields multi-scale features added to the UNet encoder features.

### Palette filtering

- For each rendering, a transmittance-derived opacity mask is thresholded; the palette score `S_p` is the fraction of masked pixels within one standard deviation of the mean intensity. Training samples with `S_p > η_p = 0.68` (the 1σ ≈ 68% rule) are kept, avoiding overly-simple appearances that give weak learning signal.

### Test-time mask refinement

- Morphological closing with a 5×5 kernel followed by dilation with a 20×20 kernel (`M^refine`) expands boundaries to cover artifacts without encroaching on high-fidelity regions (overly aggressive dilation `n > 30` degrades quality).

### Training

- Training data from DL3DV (10,510 scenes) and ScanNet++ (1,006 scenes), ~100K noisy-clean pairs. AnySplat and the diffusion model are frozen; only the leveling adapter is trained (LPIPS loss). 8× NVIDIA A6000, batch 2, AdamW (LR 1e-4), 20 epochs.

## 📊 Results

All tests on unseen datasets with sparse two-view input; metrics averaged over extrapolated novel views after refinement.

### Novel-view synthesis on MipNeRF360 and VRNeRF

원논문 Table 1. Diffusion Type과 PSNR↑/SSIM↑/LPIPS↓ (두 데이터셋), Time(s). Baseline은 AnySplat.

| Method              | Type  | Mip PSNR ↑ | Mip SSIM ↑ | Mip LPIPS ↓ | VR PSNR ↑ | VR SSIM ↑ | VR LPIPS ↓ | Time(s) |
| ------------------- | ----- | ---------- | ---------- | ----------- | --------- | --------- | ---------- | ------- |
| Baseline (AnySplat) | N/A   | 15.60      | 0.318      | 0.314       | 15.89     | 0.532     | 0.347      | N/A     |
| ViewExtrapolator    | Video | 14.85      | 0.324      | 0.606       | 16.716    | 0.591     | 0.518      | 2.59    |
| GSFixer             | Video | 15.69      | 0.332      | 0.348       | 15.86     | 0.554     | 0.356      | 12.07   |
| GSFix3D             | Image | 14.96      | 0.302      | 0.354       | 13.47     | 0.412     | 0.53       | 1.094   |
| Difix3D+            | Image | 15.68      | 0.334      | 0.312       | 16.22     | 0.540     | 0.363      | 0.718   |
| **Ours**            | –     | **16.76**  | **0.352**  | **0.306**   | **18.35** | **0.610** | **0.316**  | 1.167   |

Leveling3D is best on every metric, with inference speed comparable to image-diffusion methods and far faster than video-diffusion ones.

### Novel-view depth estimation on TartanAir and ScanNet

원논문 Table 2. AbsRel↓, RMSE↓, δ<1.25↑, Met3R↓ (다중뷰 일관성) 각 데이터셋.

| Method           | Tartan AbsRel ↓ | Tartan RMSE ↓ | Tartan δ ↑ | Tartan Met3R ↓ | ScanNet AbsRel ↓ | ScanNet RMSE ↓ | ScanNet δ ↑ | ScanNet Met3R ↓ |
| ---------------- | --------------- | ------------- | ---------- | -------------- | ---------------- | -------------- | ----------- | --------------- |
| Baseline         | 0.915           | 20.748        | 0.311      | 0.0683         | 0.372            | 58.826         | 0.708       | 0.0472          |
| ViewExtrapolator | 3.791           | 139.387       | 0.102      | 0.0633         | 3.794            | 120.666        | 0.323       | 0.0646          |
| GSFix3D          | 0.905           | 20.493        | 0.315      | 0.0675         | 0.29             | 33.398         | 0.791       | 0.0453          |
| GSFixer          | 0.892           | 20.366        | 0.315      | 0.0665         | 0.296            | 31.296         | 0.784       | 0.0462          |
| Difix3D+         | 0.893           | 20.298        | 0.321      | 0.0625         | 0.286            | 0.358          | 0.787       | 0.0452          |
| **Ours**         | **0.853**       | **19.54**     | **0.351**  | **0.0614**     | **0.252**        | **24.68**      | **0.826**   | **0.0376**      |

Leveling3D achieves the lowest AbsRel/RMSE/Met3R and highest δ<1.25 on both datasets, and its lowest Met3R scores (0.0614 / 0.0376) indicate the best multi-view geometric consistency across generated views. (Difix3D+'s ScanNet RMSE 0.358 is transcribed as printed in the source table.)

### Component ablation (VRNeRF)

원논문 Table 6. (a) leveling adapter, (b) geometry token fusion, (c) palette filtering, (d) mask refinement. 지표 PSNR↑, SSIM↑, LPIPS↓, FID↓, Met3R↓.

| Method           | PSNR ↑    | SSIM ↑    | LPIPS ↓   | FID ↓      | Met3R ↓    |
| ---------------- | --------- | --------- | --------- | ---------- | ---------- |
| Baseline         | 15.89     | 0.532     | 0.354     | 153.39     | 0.0322     |
| +(a)             | 18.19     | 0.372     | 0.336     | 169.78     | 0.0264     |
| +(a)+(b)         | 18.35     | 0.380     | 0.320     | 146.80     | 0.0248     |
| +(a)+(b)+(c)     | 18.27     | 0.392     | 0.316     | 141.41     | 0.0252     |
| +(a)+(b)+(c)+(d) | **18.36** | **0.610** | **0.314** | **138.31** | **0.0242** |

Test-time mask refinement (d) recovers SSIM sharply (0.392 → 0.610) by preventing the diffusion process from overwriting high-fidelity structure; each component adds incremental gains.

### Robustness to sparsity (ScanNet)

원논문 Table 3에 따르면 입력 뷰 2→10에서 모두 baseline을 상회한다: 2-view에서 12.296 PSNR(baseline 9.506, +22.6%), 10-view에서 14.606 PSNR(baseline 12.951, +12%). Different-control ablation (Table 5)에서 Ours 16.89 PSNR로 ControlNet(15.51)·T2I-Adapter(16.58)를 앞서고 최저 FID를 기록.

## 💡 Insights & Impact

- **Geometry-grounded generation**: Conditioning diffusion on multi-view geometry tokens (rather than a naive reference image, as in Difix3D+) propagates information from confident, well-reconstructed regions into extrapolated artifact areas, keeping generation multi-view consistent.
- **Generation as reconstruction input**: The core loop — refine extrapolated views, then re-feed them to the feed-forward model — improves the underlying 3D representation, unlike prior post-processing methods that only fix 2D renderings.
- **Efficiency**: Because only the adapter is trained and no per-scene loss backpropagation is required at test time, Leveling3D avoids the slow iterative optimization of earlier 3DGS-fixing pipelines while matching image-diffusion speed.
- **Largest gains where hardest**: Improvements are most pronounced under extreme sparsity (2 views) and large extrapolated areas, precisely where feed-forward 3DGS degrades.

## 🔗 Related Work

- Built on the feed-forward 3DGS backbone AnySplat, itself distilled from [VGGT](../reconstruction/vggt.md); situated among pose-free feed-forward methods NoPoSplat, Splatt3R, PF3plat, FLARE, VolSplat and the [MASt3R](../foundation/mast3r.md)/[DUSt3R](../foundation/dust3r.md) geometry lineage.
- Contrasts with diffusion-as-post-processor artifact repair (Difix3D+, GSFixer, GSFix3D, ViewExtrapolator) that operate on 2D renderings without geometric awareness; uses [Pi3](../reconstruction/pi3.md)-style depth protocols and Met3R for multi-view consistency.
- Adapter control relates to T2I-Adapter and ControlNet, which Leveling3D outperforms by adding geometry conditioning.

## 📚 Key Takeaways

1. Leveling3D closes the reconstruction↔generation loop: geometry-conditioned diffusion refines extrapolated views, which are fed back to level up feed-forward 3DGS.
2. Its geometry-aware leveling adapter, palette filtering, and test-time mask refinement together beat both vanilla diffusion controls and prior 3DGS-fixing methods on unseen NVS and depth benchmarks.
3. It sets SOTA on MipNeRF360/VRNeRF (NVS) and TartanAir/ScanNet (depth), with the best multi-view consistency (Met3R) and the largest gains under extreme two-view sparsity.

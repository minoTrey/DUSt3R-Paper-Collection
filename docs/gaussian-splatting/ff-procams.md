# FF-ProCams: Feed-Forward Gaussian Splatting for Projector-Camera System (arXiv preprint 2026-07)

## 📋 Overview

- **Authors**: Ziyao Wang, Yuqi Li, Wenxing Zheng, Jiaying Chen, Chong Wang
- **Institution**: 원논문 1페이지에 소속 표기 없음
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.17803) | [Code](https://github.com/CPREgroup/FF-ProCams)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first feed-forward 3D Gaussian inverse-rendering framework for projector-camera (ProCams) systems — a hybrid Mamba2–Transformer encoder predicts a _relightable_ Gaussian representation (geometry + physical reflectance, not baked appearance) from sparse multi-view observations, and a projector-aware differentiable renderer synthesizes views under arbitrary active illumination and ProCams poses in 0.13 s.

## 🎯 Key Contributions

1. **First feed-forward 3DGS for ProCams**: Predicts a full ProCams scene representation (geometry and reflectance) in a single forward pass, removing test-time per-scene optimization.
2. **Hybrid Mamba2–Transformer Gaussian prediction network**: Aggregates cross-view geometric and photometric cues from black-field / white-field / active-projection observations; two lightweight token-wise linear heads decode geometry (depth, scale, rotation, opacity) and appearance (diffuse albedo, roughness, ambient color).
3. **Large-scale synthetic ProCams dataset**: Diverse geometries, materials, and projection illuminations, providing supervision for feed-forward ProCams reconstruction and projector-aware rendering.

## 🔧 Technical Details

### Inputs and representation

For each of V = 8 views the model receives a black-field image (full-black projection), a white-field image (full-white uniform projection), and active-projection images (spatially varying patterns), with known camera intrinsics/poses. Each Gaussian is `{µ, s, q, α, a, ρ, c}` — geometry plus diffuse albedo `a`, roughness `ρ`, and auxiliary ambient color `c`. Gaussian centers are placed by ray back-projection (`µ_k = r_o + d_k·r_d`) to keep them ray-aligned.

### Projector-aware differentiable rendering

A deferred-shading strategy (inspired by DeferredGS) rasterizes G-buffers (depth, normal, albedo, roughness, ambient color). Camera pixels are back-projected to 3D and re-projected onto the projector plane to sample the projection pattern (with a validity mask). Surface response uses a simplified Cook–Torrance BRDF (Lambertian diffuse + microfacet specular) with fixed dielectric Fresnel `F0 = 0.04`; final color = direct projector reflection + ambient color.

### Training

- Staged photometric supervision: black-field first, then white-field at `Tw = 5,000`, then active projection at `Tp = 10,000`; `Tmax = 100,000` iterations. Losses: staged image (L1 + SSIM + perceptual), foreground mask entropy, depth + depth-distortion + normal-smoothness regularization, albedo-guided roughness smoothness.
- Encoder: L = 12 stacked Mamba2–Transformer hybrid modules (each = one Mamba2 + one Transformer block). Images 128×128; AdamW, lr 4×10⁻⁵; measured on an RTX 3090.
- Synthetic dataset: 43 PBR materials × 150 meshes = 6,450 scenes (Hunyuan3D meshes, MatSynth materials, lollipop projection patterns), split at the mesh level 105 train / 15 val / 30 test; 8 views per object.

## 📊 Results

Benchmark: synthetic ProCams test set. Metrics: PSNR↑, SSIM↑, LPIPS↓, reconstruction time↓. Baselines Nepmap and GS-ProCams are per-scene optimization methods.

원논문 Table 1 (projector-aware rendering quality and test-time reconstruction).

| Method     | Input Views | PSNR↑     | SSIM↑      | LPIPS↓     | Recon. Time↓ |
| ---------- | ----------- | --------- | ---------- | ---------- | ------------ |
| Nepmap     | 297         | 29.63     | 0.9462     | 0.0530     | ~1 h 30 min  |
| Nepmap     | 8           | 17.63     | 0.7062     | 0.2530     | ~1 h 30 min  |
| GS-ProCams | 297         | 33.21     | 0.9734     | 0.0230     | 11.16 min    |
| GS-ProCams | 8           | 16.14     | 0.6675     | 0.2274     | 7.15 min     |
| **Ours**   | 8           | **35.76** | **0.9829** | **0.0174** | **0.13 s**   |

With only 8 views, FF-ProCams beats both baselines even in their 297-view configuration, while cutting reconstruction to 0.13 s (a three-to-five-order-of-magnitude speedup).

원논문 Table 2 (novel projection-pattern relighting) — baselines use 297 views, FF-ProCams uses 8.

| Method     | PSNR↑     | SSIM↑      | LPIPS↓     |
| ---------- | --------- | ---------- | ---------- |
| Nepmap     | 28.58     | 0.9363     | 0.0638     |
| GS-ProCams | 30.21     | 0.9584     | 0.0398     |
| **Ours**   | **32.36** | **0.9611** | **0.0349** |

원논문 Table 3 (novel projector–camera pose simulation) — baselines use 297 views, FF-ProCams uses 8.

| Method     | PSNR↑     | SSIM↑      | LPIPS↓     |
| ---------- | --------- | ---------- | ---------- |
| Nepmap     | 25.85     | 0.9079     | 0.0875     |
| GS-ProCams | 27.84     | 0.9263     | 0.0532     |
| **Ours**   | **32.49** | **0.9575** | **0.0308** |

### Ablations

원논문 Table 4 (Mamba2–Transformer configurations). '−' means training did not converge. The all-Transformer variant edges out the hybrid on PSNR (35.83 vs 35.76) and LPIPS (0.0153 vs 0.0174), but the hybrid `{MTMT}×6` design has the highest SSIM and ~3.3× faster reconstruction (0.13 s vs 0.43 s).

| Method              | Train Mem. | Eval Mem. | Recon. Time | PSNR↑ | SSIM↑      | LPIPS↓ |
| ------------------- | ---------- | --------- | ----------- | ----- | ---------- | ------ |
| all-T               | 19.3G      | 6.4G      | 0.43s       | 35.83 | 0.9735     | 0.0153 |
| {3M1T} × 6          | 18.1G      | 5.1G      | 0.11s       | 29.23 | 0.9361     | 0.0739 |
| {7M1T} × 3          | 17.9G      | —         | —           | —     | —          | —      |
| all-M               | 17.7G      | —         | —           | —     | —          | —      |
| **Ours ({MTMT}×6)** | 18.4G      | 5.3G      | 0.13s       | 35.76 | **0.9829** | 0.0174 |

원논문 Table 5 (perceptual loss and appearance-head design).

| Method         | PSNR↑     | SSIM↑      | LPIPS↓     |
| -------------- | --------- | ---------- | ---------- |
| w/o Perc. Loss | 32.36     | 0.9627     | 0.0645     |
| CNN App. Head  | 27.69     | 0.9160     | 0.0667     |
| **Full Model** | **35.76** | **0.9829** | **0.0174** |

The token-wise linear appearance head beats a CNN-based head, because the hybrid encoder already aggregates multi-view cues and CNN mixing would blur across depths/boundaries.

### Real-world

A real setup (Hikvision camera at 512×512, Epson projector at 1920×1080, turntable) collected 40 objects (25 train / 15 test); the model is pretrained on synthetic data then fine-tuned. Real-world evaluation is qualitative only (no quantitative table) due to sensor noise, calibration, and projector nonlinearity.

## 💡 Insights & Impact

- Mainstream feed-forward Gaussian models bake illumination into color/SH, which is unusable for ProCams where novel projection patterns change the spatially varying incident light — FF-ProCams instead predicts _physically decoupled_ attributes (albedo, roughness, ambient) enabling relighting.
- The hybrid encoder is a deliberate trade: Mamba2 gives efficient long-sequence context, Transformers give global cross-view correlation; the chosen mix maximizes SSIM and speed at a small PSNR/LPIPS cost versus pure Transformer.
- **Limitations (authors)**: resolution is limited to 128×128 by GPU memory; robustness degrades under extremely sparse views (fixed at 8); and training requires _fixed_ ProCams relative poses — arbitrary/unconstrained poses cause unstable convergence.

## 🔗 Related Work

- Built on the feed-forward Gaussian reconstruction / Large Reconstruction Model line (GS-LRM, Long-LRM, AnySplat), which the broader DUSt3R/VGGT feed-forward paradigm ([DUSt3R](../foundation/dust3r.md), [VGGT](../reconstruction/vggt.md)) also belongs to.
- ProCams-specific baselines: Nepmap (neural reflectance field) and GS-ProCams (2D Gaussian Splatting + projector mapping), both per-scene optimization.

## 📚 Key Takeaways

1. FF-ProCams brings the feed-forward paradigm to projector-camera inverse rendering, predicting a relightable Gaussian representation (geometry + BRDF) rather than baked appearance.
2. From 8 views it surpasses 297-view optimization baselines on all quality metrics while reducing reconstruction from minutes/hours to 0.13 s.
3. A projector-aware differentiable renderer with a Cook–Torrance BRDF and an auxiliary ambient-color attribute lets a single forward pass generalize to unseen projection patterns and novel projector–camera poses — within the honest constraints of 128×128 resolution and fixed ProCams poses.

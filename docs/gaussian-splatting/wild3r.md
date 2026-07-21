# Wild3R: Feed-Forward 3D Gaussian Splatting from Unconstrained Sparse Photo Collections (arXiv preprint (2026-06))

## 📋 Overview

- **Authors**: Yuto Furutani, Takashi Otonari, Kaede Shiohara, Toshihiko Yamasaki
- **Institution**: The University of Tokyo
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.11894) | [Project Page](https://furuschool.github.io/wild3r-page)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward 3DGS method for unconstrained sparse photo collections that infers illumination-consistent, transient-free Gaussians conditioned on a reference view in ~1 s, enabled mainly by the newly introduced synthetic WildCity dataset rather than a new architecture.

(Yuto Furutani, Takashi Otonari, and Kaede Shiohara are co-first authors.)

## 🎯 Key Contributions

1. **WildCity dataset**: A large-scale synthetic dataset of 200 scenes, 170 lighting conditions (HDRI maps), and transient objects, totaling 337,500 images — providing the joint multi-view / multi-illumination / transient coverage missing from prior in-the-wild datasets.
2. **Data-centric solution**: Wild3R is realized by fine-tuning an existing camera-free feed-forward model (AnySplat) with no structural modification, demonstrating that the main bottleneck is training data.
3. **Appearance consistency + transient-free geometry losses**: The first frame acts as an appearance reference; rendered views are supervised against the reference illumination, and depth is supervised with transient-free ground-truth depth.
4. **In-the-wild feed-forward reconstruction**: Reconstructs from unposed, appearance-varying sparse views without camera parameters or point-cloud initialization, in ~1 s on a single A100.

## 🔧 Technical Details

### Base Model

Wild3R builds on AnySplat, itself built on VGGT, which adds a Gaussian head predicting per-pixel primitives (µ, α, q, s, c) plus camera parameters and depth. The first frame's camera defines the world coordinate system. Wild3R initializes from pretrained AnySplat weights (~940M learnable parameters), freezes the depth and camera heads, and updates the rest.

### WildCity Dataset Pipeline

- **Assets**: SceneCity Blender add-on (11 building types) augmented with 130+ Sketchfab GLB models, grouped into 9 virtual cities; 20–25 target locations per city yield 200 scenes.
- **Rendering**: 50 views per scene, 30 HDRI illuminations sampled per scene (from 170), Blender Cycles PBR at 512×512 with 512 samples/pixel; FoV sampled between 40° and 100°.
- **Transient objects**: Added via a text-driven image editing model (Gemini) to 12.5% of rendered views, producing 37,500 transient-augmented images.

### Training Objective

L = Lac + λdep·Ldep + λgc·Lgc + λcam·Lcam, where Lac is the appearance-consistency loss (L2 + LPIPS against the reference-illumination target), Ldep supervises transient-free depth, and Lgc, Lcam follow AnySplat. Weights: λlpips = 0.05, λgc = 0.02, λdep = 0.2, λcam = 2.0. Trained for 30K iterations (~1 day on a single A100 80GB), sampling N ∈ [2, 24] views per batch with transient/lighting augmentation.

## 📊 Results

Evaluated on Photo Tourism (Brandenburg Gate, Sacre Coeur, Trevi Fountain) with N ∈ {4, 16, 64} context views, following the NeRF-W half-image protocol. Metrics: PSNR↑, SSIM↑, LPIPS↓.

### Photo Tourism Comparison

원논문 Table 2 (checkmark 컬럼과 재구성 시간은 산문으로 옮김). Reconstruction time (16 views, single A100): NeRF-W 30h, 3DGS 7.7m, GS-W 24m, WildGaussians 1.2h, AsymGS 30m, Long-LRM 0.18s, AnySplat 0.95s, YoNoSplat 0.38s, DA3 1.6s, Wild3R 0.95s.

| Method                  | 4v PSNR↑ | 4v SSIM↑ | 4v LPIPS↓ | 16v PSNR↑ | 16v SSIM↑ | 16v LPIPS↓ | 64v PSNR↑ | 64v SSIM↑ | 64v LPIPS↓ |
| ----------------------- | -------- | -------- | --------- | --------- | --------- | ---------- | --------- | --------- | ---------- |
| NeRF-W (opt.)           | 12.08    | 0.382    | 0.738     | 17.29     | 0.530     | 0.570      | 21.10     | 0.671     | 0.449      |
| 3DGS (opt.)             | 12.42    | 0.378    | 0.612     | 13.56     | 0.437     | 0.560      | 15.20     | 0.564     | 0.462      |
| GS-W (opt.)             | 12.72    | 0.397    | 0.582     | 15.17     | 0.501     | 0.504      | 17.91     | 0.634     | 0.404      |
| WildGaussians (opt.)    | 14.00    | 0.428    | 0.592     | 16.73     | 0.551     | 0.524      | 20.20     | 0.695     | 0.395      |
| AsymGS (opt.)           | 15.93    | 0.506    | 0.574     | 18.37     | 0.607     | 0.463      | 21.24     | 0.718     | 0.340      |
| Long-LRM (cam-known FF) | 11.25    | 0.415    | 0.650     | 15.26     | 0.486     | 0.569      | 15.90     | 0.525     | 0.535      |
| AnySplat (cam-free FF)  | 11.25    | 0.320    | 0.593     | 13.72     | 0.377     | 0.546      | 14.88     | 0.417     | 0.512      |
| YoNoSplat (cam-free FF) | 12.47    | 0.397    | 0.666     | 13.04     | 0.403     | 0.640      | 13.25     | 0.412     | 0.640      |
| DA3 (cam-free FF)       | 13.35    | 0.394    | 0.622     | 14.03     | 0.420     | 0.586      | 14.25     | 0.434     | 0.582      |
| **Wild3R (Ours)**       | 13.04    | 0.370    | **0.556** | **15.87** | **0.435** | **0.506**  | **16.29** | **0.458** | **0.477**  |

Among camera-free feed-forward methods Wild3R leads on most settings, but not all: at 4 views DA3 has higher PSNR (13.35 vs. 13.04) and SSIM (0.394 vs. 0.370). Against the optimization-based methods (which use GT cameras and point clouds), Wild3R remains below AsymGS/NeRF-W on PSNR at 16 and 64 views, while being orders of magnitude faster.

### Ablation on Photo Tourism

원논문 Table 3.

| Method                         | 4v PSNR↑ | 4v LPIPS↓ | 16v PSNR↑ | 16v LPIPS↓ | 64v PSNR↑ | 64v LPIPS↓ |
| ------------------------------ | -------- | --------- | --------- | ---------- | --------- | ---------- |
| (a) AnySplat                   | 11.25    | 0.593     | 13.72     | 0.546      | 14.88     | 0.512      |
| (b) AnySplat w/ Fine-tuning    | 11.47    | 0.588     | 14.18     | 0.543      | 14.98     | 0.516      |
| (c) Ours w/o Transient Objects | 12.66    | 0.556     | 15.57     | 0.514      | 16.08     | 0.487      |
| (d) Ours w/o Sketchfab Assets  | 12.70    | 0.570     | 15.01     | 0.531      | 15.36     | 0.508      |
| (e) Ours (full)                | 13.04    | 0.556     | 15.87     | 0.506      | 16.29     | 0.477      |

### Training-Dataset Comparison on Photo Tourism (16 views)

원논문 Table 6.

| Training Dataset | PSNR↑ | SSIM↑ | LPIPS↓ |
| ---------------- | ----- | ----- | ------ |
| None (AnySplat)  | 13.72 | 0.377 | 0.546  |
| DTU              | 12.79 | 0.352 | 0.599  |
| LightCity        | 11.17 | 0.309 | 0.676  |
| WildCity (Ours)  | 15.87 | 0.435 | 0.506  |

On the NeRF-OSR dataset (원논문 Table 5, 16 views) Wild3R consistently beats the camera-free AnySplat baseline and is competitive on LPIPS with optimization-based methods, though per-scene it does not win every metric (e.g., on lwp its PSNR 10.68 is below AsymGS 12.35).

## 💡 Insights & Impact

- **Data is the bottleneck, not architecture**: Plain fine-tuning of AnySplat (variant b) barely improves over the base model, whereas training on WildCity (full model) lifts 16-view PSNR from 13.72 to 15.87 — the gain comes from the dataset and losses, not new modules.
- **Transient exposure and asset diversity both matter**: Removing Gemini transient objects (c) or Sketchfab assets (d) degrades performance across view counts, confirming both design choices.
- **Frozen heads suffice**: Unfreezing the pretrained depth/camera heads (원논문 Table 7) yields no meaningful improvement, indicating those heads already generalize.
- **Honest limits**: No explicit material modeling (weak on strong speculars/reflections), reference-anchored appearance fails when the reference is heavily occluded, feed-forward detail lags optimization methods, and quality is bounded by the backbone.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: Geometry foundation model underpinning the feed-forward 3DGS line.
- **[VGGT](../reconstruction/vggt.md)**: The transformer backbone that AnySplat (Wild3R's base) is built on.
- **[Depth Anything 3](../reconstruction/depth-anything-3.md)**: A compared camera-free feed-forward baseline (DA3).

## 📚 Key Takeaways

1. Wild3R extends feed-forward 3DGS to unconstrained, appearance-varying sparse photo collections without camera parameters or point clouds, in ~1 s per reference on an A100.
2. Its core contribution is the WildCity dataset (200 scenes, 170 illuminations, 337,500 images) plus appearance-consistency and transient-free depth losses; the architecture is unchanged AnySplat.
3. It outperforms prior camera-free feed-forward methods on most Photo Tourism settings and rivals slow optimization-based methods on perceptual metrics, while still trailing them on PSNR at dense view counts.

# AdaptiveSplat: Texture Aware Controllable 3D Gaussian Allocation for Feed-Forward Reconstruction (ECCV 2026)

![adaptivesplat — architecture](https://arxiv.org/html/2607.04256v1/x1.png)

_Overview: We demonstrate AdaptiveSplat’s ability to maintain scene fidelity while controlling the allocation of primitives (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Badrinath Singhal, Srihari K G, Sreehari Iyer, Ankit Dhiman, Venkatesh Babu Radhakrishnan
- **Institution**: Vision and AI Lab, Indian Institute of Science, Bangalore; Samsung R&D Institute India - Bangalore
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.04256) | [Project Page](https://badrinaths.github.io/projects/adaptive-splat/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward framework that controls how many 3D Gaussians are allocated per region using local texture energy, pruning smooth low-frequency areas aggressively while an adaptive Gaussian head re-predicts attributes of the retained primitives — all without test-time optimization.

## 🎯 Key Contributions

1. **Texture-Based Scene Energy Estimation**: A Discrete Wavelet Transform (DWT) based mechanism that quantifies high-frequency content per image region to find areas needing higher representational capacity.
2. **Texture-Aware Selective Pruning**: A pruning strategy that removes Gaussians from low-texture regions while preserving those in high-detail areas, guided by SuperCluster-level texture energy.
3. **Adaptive Gaussian Head**: A head (built on DPT + ViT features fused with binary masks) that re-predicts attributes of retained Gaussians to mitigate pruning artifacts, staying within the feed-forward pipeline.
4. **Backbone-agnostic integration**: Demonstrated on MASt3R/VGGT (pose-free) and MVSplat (pose-input) backbones, and evaluated on RE10K, ACID, DL3DV, Tanks and Temples, and DTU.

## 🔧 Technical Details

### Problem Formulation

Existing feed-forward models predict a pixel-aligned set of `N = mHW` Gaussians for `m` input views. AdaptiveSplat instead introduces a user-defined pruning budget β ∈ [0, 1), keeping a compact subset of size `B = ⌊(1 − β)N⌋`. Each Gaussian is parameterized as `{µ, s, q, α, ρ}` (3D mean, anisotropic scale, quaternion rotation, opacity, spherical harmonics).

### Pipeline

- **Initial representation**: A 3D point cloud is inferred from context images via a MASt3R/VGGT backbone.
- **SuperCluster formation**: The point cloud is partitioned into `K` SuperClusters via K-means in `(x, y, z, r, g, b)` space; texture is analyzed with a single-level 2D DWT, aggregating horizontal/vertical/diagonal high-frequency responses into a per-pixel texture energy.
- **Binary mask construction**: SuperClusters are ordered by increasing energy; within low-energy clusters a nominal retention of γ = 0.1 per cluster is applied, while high-energy clusters are fully retained. Masks mark the retained set.
- **Adaptive Gaussian Head**: Fuses multi-view ViT features with the binary masks to predict refined attributes for the retained indices only.

### Training and Inference

- Trained with the pruning budget sampled as β ∼ U[0, 1) so the model generalizes across budgets at test time.
- Loss combines an L2 photometric term with an LPIPS perceptual term (weight λ).
- Hyperparameters: K = 300, γ = 10%, λ = 0.001. Trained on 1 NVIDIA A100 40GB GPU for 48 GPU hours per dataset, reusing pretrained baseline checkpoints.
- At inference the user selects a sparsity level β ∈ [0, 0.8]; DWT, masks, and adapted attributes are computed in a single forward pass.

## 📊 Results

Metrics are novel view synthesis quality: PSNR↑, LPIPS↓, SSIM↑. Baselines are built by applying pruning strategies (EAGLES, LightGaussian, EfficientGS, PUP-3DGS) on top of feed-forward backbones. The tables below report the "with fine-tuning" sparse-view setting with NoPoSplat / HiSplat backbones.

원논문 Table 1 (ACID).

| Method      | β=0.4 PSNR↑ | LPIPS↓ | SSIM↑ | β=0.6 PSNR↑ | LPIPS↓ | SSIM↑ | β=0.8 PSNR↑ | LPIPS↓ | SSIM↑ |
| ----------- | ----------- | ------ | ----- | ----------- | ------ | ----- | ----------- | ------ | ----- |
| EAGLES      | 19.433      | 0.620  | 0.555 | 19.769      | 0.605  | 0.565 | 19.464      | 0.618  | 0.556 |
| LightGauss. | 19.785      | 0.604  | 0.566 | 19.594      | 0.612  | 0.560 | 18.660      | 0.628  | 0.541 |
| PUP-3DGS    | 19.382      | 0.617  | 0.558 | 18.529      | 0.643  | 0.538 | 18.003      | 0.659  | 0.527 |
| EfficientGS | 19.762      | 0.607  | 0.565 | 19.677      | 0.608  | 0.564 | 19.310      | 0.619  | 0.556 |
| **Ours**    | **22.549**  | 0.299  | 0.640 | **22.310**  | 0.310  | 0.627 | **21.055**  | 0.342  | 0.593 |

원논문 Table 1 (RE10K).

| Method      | β=0.4 PSNR↑ | LPIPS↓ | SSIM↑ | β=0.6 PSNR↑ | LPIPS↓ | SSIM↑ | β=0.8 PSNR↑ | LPIPS↓ | SSIM↑ |
| ----------- | ----------- | ------ | ----- | ----------- | ------ | ----- | ----------- | ------ | ----- |
| EAGLES      | 16.526      | 0.598  | 0.556 | 16.404      | 0.606  | 0.552 | 16.243      | 0.614  | 0.547 |
| LightGauss. | 16.598      | 0.596  | 0.558 | 16.421      | 0.604  | 0.552 | 16.056      | 0.618  | 0.542 |
| PUP-3DGS    | 16.472      | 0.601  | 0.558 | 16.083      | 0.618  | 0.543 | 15.588      | 0.638  | 0.529 |
| EfficientGS | 16.525      | 0.598  | 0.556 | 16.404      | 0.606  | 0.551 | 16.242      | 0.613  | 0.546 |
| **Ours**    | **22.294**  | 0.235  | 0.735 | **22.110**  | 0.243  | 0.726 | **20.740**  | 0.272  | 0.692 |

On the DL3DV dense-view setting (AnySplat base model), with 6 views at β = 0.4 AdaptiveSplat reaches 20.448 dB PSNR versus 11.361 dB from LightGaussian; the gap is preserved across 9, 16, and 32 views (원논문 Table 2).

### Ablation (β = 0.4)

원논문 Table 3.

| Ablation Variant     | ACID PSNR↑ | LPIPS↓ | SSIM↑ | RE10K PSNR↑ | LPIPS↓ | SSIM↑ |
| -------------------- | ---------- | ------ | ----- | ----------- | ------ | ----- |
| w/o Texture          | 21.31      | 0.326  | 0.623 | 20.73       | 0.260  | 0.713 |
| w/o Adaptive GS Head | 17.44      | 0.445  | 0.490 | 19.81       | 0.399  | 0.617 |
| w/o Binary Mask      | 22.52      | 0.318  | 0.642 | 20.06       | 0.339  | 0.656 |
| **Ours**             | **22.55**  | 0.299  | 0.639 | **22.29**   | 0.235  | 0.735 |

Removing the Adaptive GS Head causes the largest drop (22.55 → 17.44 dB on ACID), confirming that re-predicting attributes post-pruning is critical.

### Hyperparameter sensitivity

원논문 Table 4.

| Clusters k | PSNR↑  | LPIPS↓ | SSIM↑ | Retention γ | PSNR↑  | LPIPS↓ | SSIM↑ |
| ---------- | ------ | ------ | ----- | ----------- | ------ | ------ | ----- |
| k = 50     | 22.416 | 0.303  | 0.636 | γ = 0.05    | 21.796 | 0.347  | 0.608 |
| k = 100    | 22.488 | 0.301  | 0.638 | γ = 0.10    | 22.549 | 0.299  | 0.640 |
| k = 300    | 22.549 | 0.299  | 0.640 | γ = 0.15    | 21.587 | 0.352  | 0.589 |
| k = 400    | 22.559 | 0.298  | 0.641 | γ = 0.20    | 22.262 | 0.304  | 0.629 |

Quality gains become marginal beyond K = 300 while training cost keeps rising; γ = 0.10 gives the best trade-off.

### Inference time

Rendering throughput (FPS) rises with pruning strength as fewer active Gaussians are rasterized (그림 10, 수치 미인쇄). A Pareto plot places AdaptiveSplat in the top-left (highest PSNR at lowest latency) versus fine-tuned baselines for RE10K at β = 0.8 (그림 11, 수치 미인쇄).

## 💡 Insights & Impact

- Natural images follow an approximate power-law power-spectral-density decay (PSD ∝ 1/f^α, α ≈ 2), so most visual energy is low-frequency; smooth regions can be represented with few Gaussians while textured regions need denser allocation.
- Naive pruning of pixel-aligned Gaussians produces "black patch" artifacts (empty regions) in non-finetuned settings and "blobby Gaussian" distortion even after fine-tuning; adaptively re-predicting the survivors avoids both.
- The method is a drop-in addition to existing feed-forward Gaussian pipelines and needs no architectural changes or per-scene optimization.
- **Limitation (authors)**: On smooth surfaces with high-frequency texture (intricate wall patterns) or specular highlights, it shares the same limitation as any pixel-aligned feed-forward model.

## 🔗 Related Work

- Builds on feed-forward Gaussian backbones: [MASt3R](../foundation/mast3r.md) and [VGGT](../reconstruction/vggt.md) supply the initial point cloud; MVSplat is used as a pose-input backbone.
- Contrasts with per-scene 3DGS compression (EAGLES, LightGaussian, EfficientGS, PUP-3DGS), which require dense views and scene-specific optimization.
- Related feed-forward Gaussian splatting entries in this collection: [Splatt3R](splatt3r.md), [PreF3R](pref3r.md).

## 📚 Key Takeaways

1. Texture energy from a DWT lets a feed-forward model decide _where_ to spend its Gaussian budget rather than allocating uniformly per pixel.
2. An adaptive Gaussian head that re-predicts retained-Gaussian attributes is the component that recovers quality after pruning (largest ablation drop).
3. Under a user-selectable budget β ∈ [0, 0.8], AdaptiveSplat holds quality at 80% pruning where prior pruning baselines collapse, giving a favorable quality-efficiency trade-off without test-time optimization.

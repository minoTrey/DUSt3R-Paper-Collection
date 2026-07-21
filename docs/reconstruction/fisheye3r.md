# Fisheye3R: Adapting Unified 3D Feed-Forward Foundation Models to Fisheye Lenses (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Ruxiao Duan, Erin Hong, Dongxu Zhao, Eric Turner, Alex Wong, Yunwen Zhou
- **Institution**: Yale University; Google
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.28896) | [Code](https://github.com/android-xr/fisheye3r)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A lightweight adaptation framework that inserts learnable calibration tokens into frozen multi-view foundation models to recalibrate fisheye features in latent space, extending VGGT, π³, and MapAnything to fisheye inputs without regressing on perspective images and without requiring fisheye training data.

## 🎯 Key Contributions

1. **Calibration tokens for fisheye adaptation**: Trainable tokens inserted into encoder and alternating-attention layers recalibrate fisheye features toward the perspective manifold while the backbone stays frozen.
2. **Masked attention for backward compatibility**: A binary mask nullifies calibration-token effects on perspective frames and activates them on fisheye frames, enabling mixed-camera sequences without degrading perspective accuracy.
3. **Three data-regime learning schemes**: Self-supervised with unlabeled perspective images (SSL), supervised with perspective ground truth (SL), and supervised with fisheye data (SL+), synthesizing distortion via the Kannala-Brandt model.
4. **Generality across models and projections**: Applied to VGGT, π³, and MapAnything, and generalizes to non-Kannala-Brandt projection models and panoramic images.

## 🔧 Technical Details

### Calibration Tokens

- K learnable calibration tokens are injected into all encoder layers after the initial L0 layers, and into every frame-wise and global alternating-attention layer; each layer has its own tokens, dropped immediately after that layer to localize the effect.
- Only calibration tokens (and a linear camera-type classifier) are trained; the original backbone is entirely frozen.

### Masked Attention

- A linear classifier on the L0-layer class token predicts camera type per frame (fisheye vs perspective, threshold 0.5).
- Frame-wise and global attention masks eliminate calibration-token influence on perspective frames while enabling it on fisheye frames, supporting heterogeneous camera sequences (e.g., a forward perspective camera bridging left/right fisheye views in driving).

### Learning and Data

- Fisheye images synthesized from perspective via Kannala-Brandt distortion T; dense predictions undistorted with T⁻¹ for loss computation (extrinsics untransformed). SSL uses the original model's predictions as pseudo-labels (AugUndo-inspired).
- Training data (SSL/SL): ScanNet++ (perspective), MegaDepth, BlendedMVS, TartanAir, MVS-Synth, ParallelDomain-4D. SL+ adds ASE and KITTI360 fisheye. Testing: ScanNet++ (fisheye), ADT, KITTI360.
- Ablations set defaults L0 = 12 (classification accuracy saturates) and K = 8 calibration tokens per layer (reconstruction quality peaks; even K = 1 gives most of the gain).

## 📊 Results

### Fisheye Adaptation on ScanNet++ (selected metrics)

원논문 Table 1에서 발췌. Pose AUC↑, Depth Rel↓, Point Map CD↓, FoV AUC↑.

| Model             | Pose AUC ↑ | Depth Rel ↓ | Point CD ↓ | FoV AUC ↑ |
| ----------------- | ---------- | ----------- | ---------- | --------- |
| VGGT              | 0.381      | 0.287       | 0.112      | 0.305     |
| VGGT w/ SSL       | 0.533      | 0.234       | 0.065      | 0.605     |
| VGGT w/ SL        | 0.656      | 0.230       | 0.060      | 0.722     |
| VGGT w/ SL+       | 0.677      | 0.222       | 0.060      | 0.718     |
| π³                | 0.463      | 0.282       | 0.084      | 0.551     |
| π³ w/ SL+         | 0.719      | 0.212       | 0.054      | 0.873     |
| MapAnything       | 0.519      | 0.274       | 0.083      | 0.647     |
| MapAnything w/SL+ | 0.774      | 0.171       | 0.051      | 0.927     |

### Fisheye Adaptation on KITTI360 (wide-FoV driving, selected metrics)

원논문 Table 1에서 발췌.

| Model             | Pose AUC ↑ | Depth Rel ↓ | Point CD ↓ | FoV AUC ↑ |
| ----------------- | ---------- | ----------- | ---------- | --------- |
| VGGT              | 0.440      | 0.270       | 1.304      | 0.212     |
| VGGT w/ SL+       | 0.904      | 0.111       | 0.726      | 0.757     |
| π³                | 0.548      | 0.153       | 0.927      | 0.444     |
| π³ w/ SL+         | 0.942      | 0.097       | 0.437      | 0.751     |
| MapAnything       | 0.428      | 0.258       | 1.301      | 0.259     |
| MapAnything w/SL+ | 0.917      | 0.091       | 0.575      | 0.805     |

### Generalization to Other Projection Models (π³, Stanford2D3DS)

원논문 Table 2. Reconstruction Chamfer Distance (CD↓); KB 합성만 학습해도 타 projection에 일반화.

| Projection    | π³ CD ↓ | +Ours CD ↓ | Improvement |
| ------------- | ------- | ---------- | ----------- |
| KB (OOD)      | 0.230   | 0.116      | 49.7%       |
| Fisheye624    | 0.228   | 0.117      | 48.5%       |
| MEI           | 0.264   | 0.095      | 64.1%       |
| Equidistant   | 0.219   | 0.107      | 51.1%       |
| Stereographic | 0.211   | 0.088      | 58.1%       |
| Equiangular   | 0.241   | 0.116      | 52.0%       |
| Orthographic  | 0.375   | 0.182      | 51.5%       |

Across all models, datasets, and metrics (135 tests), SSL alone reaches 50%+ improvement in 26/135 tests, SL in 37/135, and SL+ in 77/135.

## 💡 Insights & Impact

- **Recalibrate in latent space, not image space**: Fisheye failures stem from a covariate shift in patch features; learnable tokens realign fisheye embeddings to the perspective distribution (verified via t-SNE), avoiding rectification's peripheral cropping/resampling artifacts.
- **Even unlabeled perspective data helps**: SSL with only unlabeled perspective RGB yields large fisheye gains, suggesting the approach scales with unlabeled corpora.
- **Backward compatibility via masking**: Masked attention preserves native perspective performance and enables a single network to reconstruct panoramic scenes from mixed fisheye + perspective driving rigs.
- **Peripheral focus**: Attention maps show peripheral patches (most radially distorted) attend most strongly to calibration tokens, targeting correction where warping is extreme.

## 🔗 Related Work

- **[VGGT](vggt.md)**, **[π³](pi3.md)**, **[MapAnything](mapanything.md)**: The three unified feed-forward foundation models adapted.
- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: Pointmap-regression predecessors cited as the feed-forward lineage.

## 📚 Key Takeaways

1. Fisheye3R adapts frozen 3D foundation models to fisheye lenses by inserting per-layer calibration tokens that recalibrate distorted features in latent space, trained via SSL, SL, or SL+ schemes.
2. Masked attention gives backward compatibility with perspective imagery and enables mixed-camera reconstruction, addressing the operational overhead of deploying separate models.
3. On VGGT, π³, and MapAnything across ScanNet++, ADT, and KITTI360, calibration tokens consistently improve pose, depth, point map, and FoV estimation and generalize to unseen projection models and panoramas.

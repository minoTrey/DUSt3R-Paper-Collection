# MV-SAM: Multi-view Promptable Segmentation using Pointmap Guidance (arXiv preprint 2026-01)

![mv-sam — architecture](https://arxiv.org/html/2601.17866/x1.png)

_MV-SAM (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Yoonwoo Jeong, Cheng Sun, Yu-Chiang Frank Wang, Minsu Cho, Jaesung Choe
- **Institution**: NVIDIA, POSTECH
- **Venue**: arXiv preprint (2026-01)
- **Links**: [Paper](https://arxiv.org/abs/2601.17866)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: Lifts SAM2-Video image embeddings and user prompts into 3D via π³ pointmaps, so a lightweight transformer predicts view-consistent masks without per-scene optimization, explicit 3D networks, or 3D-annotated data.

## 🎯 Key Contributions

1. **Pointmap-guided multi-view segmentation**: Uses pointmaps — 3D points reconstructed from unposed images — whose strict one-to-one pixel–point correspondence aligns 2D prompts with 3D geometry, eliminating rendering or projection steps.
2. **2D-to-3D knowledge transfer**: Lifts both user prompts and image embeddings from the pretrained SAM2-Video encoder into 3D using the pixel–point correspondence, transferring rich 2D knowledge into 3D understanding.
3. **No specialized 3D networks or 3D labels**: A lightweight transformer with 3D positional embeddings is shown sufficient for robust, view-consistent, 3D-aware segmentation, trained only on single-view object–image pairs from SA-1B.

## 🔧 Technical Details

### Framework (three stages)

1. **Pre-processing**: Reconstruct pointmaps from unposed images with π³ (the default visual geometry model), and extract image embeddings with the frozen SAM2-Video encoder (SAM2.1 large, Hiera-L). π³ also outputs per-point confidence maps.
2. **3D positional embedding**: Embed both image features and user prompts with 3D positional encodings in a common world coordinate system derived from the pointmaps. Coordinates are z-score standardized across all points for robustness to varying frame counts and scene scales, then passed through sinusoidal (Fourier) positional embedding. Learnable positive/negative prompt embeddings and high-/low-confidence embeddings modulate attention; low-confidence points are defined as the bottom 15% ranked by confidence.
3. **Mask decoding**: A two-way transformer (as in SAM2-Video) takes point embeddings as queries and prompt embeddings as keys/values. Uses **single-view attention** (cross-attention restricted to one reference view), avoiding the token-length extrapolation instability of full-view attention.

### Permutation equivariance

Because π³ is permutation-equivariant, MV-SAM inherits equivariance to frame order, yielding consistent performance under random frame permutation.

### Training

- Trained solely on **single-view** object–image pairs from **SA-1B** (no multi-view datasets), which suffices for multi-view consistency because π³ produces nearly identical geometry whether frames are processed jointly or individually.
- Loss: focal loss + dice loss (α = 0.9, γ = 1.5, λ_focal = 1.0, λ_DICE = 0.05). Frozen image encoder; trainable mask decoder, prompt encoder, and confidence embeddings.

## 📊 Results

### Promptable segmentation vs SAM2-Video

원논문 Table 1. mIoU / mAcc (↑), 10 positive + 2 negative prompts.

| Dataset   | SAM2-Video (Video) | MV-SAM (Video)  | SAM2-Video (MV-Images) | MV-SAM (MV-Images) |
| --------- | ------------------ | --------------- | ---------------------- | ------------------ |
| ScanNet++ | 46.1 / 61.4        | **48.9 / 63.5** | 47.5 / 62.8            | **49.1 / 62.9**    |
| uCo3D     | 81.9 / 91.3        | **87.7 / 95.0** | 83.2 / 91.9            | **87.4 / 95.1**    |
| DL3DV     | 67.3 / 82.9        | **75.1 / 91.8** | 64.2 / 78.6            | **75.0 / 92.0**    |
| Average   | 65.1 / 78.5        | **70.6 / 83.4** | 65.0 / 77.8            | **70.5 / 83.3**    |

### NVOS and SPIn-NeRF

원논문 Table 2. mIoU / mAcc (↑). MV-SAM uses no per-scene optimization and no scenes from these benchmarks.

| Category       | Method     | NVOS mIoU / mAcc | SPIn-NeRF mIoU / mAcc |
| -------------- | ---------- | ---------------- | --------------------- |
| per-scene opt. | SPIn-NeRF  | - / -            | 90.7 / 98.8           |
| per-scene opt. | SA3D       | 91.1 / 98.4      | 92.4 / 98.8           |
| per-scene opt. | SAGA       | 92.6 / 98.6      | 93.7 / 99.2           |
| per-scene opt. | SA3D-GS    | 92.7 / 98.5      | 93.4 / 99.1           |
| per-scene opt. | OmniSeg3D  | 92.8 / 98.6      | 94.5 / 99.3           |
| generalization | SAM2-Video | 88.7 / 94.6      | 86.6 / 93.6           |
| generalization | MV-SAM     | 92.1 / 97.5      | 92.9 / 97.1           |

MV-SAM beats SAM2-Video and is competitive with per-scene optimization, but does not surpass the best optimization baselines (e.g., OmniSeg3D 92.8/94.5 mIoU).

### Ablation: positional embeddings and attention scope (ScanNet++)

원논문 Table 3a. mIoU / mAcc (↑). CP = confidence embeddings, PE = positional embedding, Attn = attention scope.

| CP  | PE    | Attn        | mIoU / mAcc     |
| --- | ----- | ----------- | --------------- |
|     | 3D PE | single-view | 44.5 / 61.1     |
| ✓   | No PE | single-view | 10.9 / 52.7     |
| ✓   | No PE | full-view   | 25.6 / 57.8     |
| ✓   | 2D PE | single-view | 18.3 / 53.6     |
| ✓   | 2D PE | full-view   | 26.6 / 59.5     |
| ✓   | 3D PE | full-view   | 45.8 / 62.2     |
| ✓   | 3D PE | single-view | **52.2 / 66.7** |

Confidence embeddings add +7.7%p (44.5 → 52.2 mIoU). 3D PE clearly beats 2D PE and no PE; single-view attention matches full-view at few frames but scales better.

### Cross-dataset generalization

원논문 Table 4. mIoU / mAcc (↑). Large-scale single-view SA-1B nearly matches in-domain training and far exceeds small-scale multi-view cross-domain transfer.

| Train → Eval          | mIoU / mAcc   |
| --------------------- | ------------- |
| ScanNet++ → ScanNet++ | 0.510 / 0.694 |
| uCo3D → ScanNet++     | 0.194 / 0.251 |
| SA-1B → ScanNet++     | 0.489 / 0.635 |
| uCo3D → uCo3D         | 0.910 / 0.965 |
| ScanNet++ → uCo3D     | 0.322 / 0.517 |
| SA-1B → uCo3D         | 0.877 / 0.950 |

### Visual geometry model choice (DL3DV)

원논문 Table 5. mIoU / mAcc (%). Stronger geometry models improve MV-SAM.

| VGM         | mIoU / mAcc |
| ----------- | ----------- |
| VGGT        | 61.1 / 90.4 |
| WorldMirror | 74.3 / 92.6 |
| π³          | 75.1 / 91.8 |

### Runtime and model size

원논문 Table 7·8. Timing on a DL3DV scene with 20 frames; parameters and FLOPs.

| Method     | Pre-processing | Inference | # params | FLOPs (TFLOPs) |
| ---------- | -------------- | --------- | -------- | -------------- |
| SAGA       | 31 min         | 528 ms    | –        | –              |
| OmniSeg3D  | 37 min         | 463 ms    | –        | –              |
| SAM2-Video | 3.2 s          | 4.8 s     | 12.3M    | 16.8           |
| MV-SAM     | 5.1 s          | 1.1 s     | 4.1M     | 44.6           |

MV-SAM has fewer trainable parameters than SAM2-Video (no memory modules) and faster inference (all views processed simultaneously), but more FLOPs due to the visual geometry model, and slower inference than per-scene methods that pre-extract scene features.

## 💡 Insights & Impact

- **Pointmaps as a 2D↔3D bridge**: The one-to-one pixel–point correspondence removes the rendering/projection step that decoupled 3D representations (point clouds, meshes, voxels, Gaussians) require, and is naturally robust to occlusion.
- **Removing explicit 3D operations helps generalization**: Pure 3D encoders (MinkUNet) and voxel-based variants assume metric-depth-aligned inputs and are sensitive to grid resolution; letting a transformer implicitly learn 3D consistency from pointmaps (which lack metric alignment but preserve geometric structure) generalizes better.
- **Scale over multi-view supervision**: A single-view, large-scale dataset (SA-1B) yields far stronger generalization than small, domain-specific multi-view datasets.
- **Limitation**: Performance is tied to π³ pointmap quality; inaccurate depth alignment or structural noise in cluttered indoor scenes propagates downstream, and without explicit cross-view 3D consistency, outliers in textureless regions can cause unreliable predictions.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Feed-forward transformer jointly predicting depth, camera poses, and pointmaps; MV-SAM's ablation shows it as a weaker VGM than π³.
- **[π³ / Pi3](../reconstruction/pi3.md)**: Permutation-equivariant reformulation of VGGT; MV-SAM's default visual geometry model, source of its frame-order equivariance.
- **[DUSt3R](../foundation/dust3r.md)**: Origin of the feed-forward pointmap paradigm MV-SAM builds on.
- **[Fast3R](../reconstruction/fast3r.md)**: Feed-forward multi-view pose + point prediction cited in the same lineage.
- **[SegVGGT](segvggt.md)**: Related VGGT-based segmentation work in this collection.

## 📚 Key Takeaways

1. MV-SAM lifts SAM2-Video embeddings and prompts into 3D via π³ pointmaps, achieving view-consistent promptable segmentation with only a lightweight transformer.
2. It outperforms SAM2-Video across NVOS, SPIn-NeRF, ScanNet++, uCo3D, and DL3DV, and is competitive with per-scene optimization baselines while using none.
3. Training only on single-view SA-1B suffices for multi-view consistency, thanks to π³'s permutation-equivariant, view-stable geometry.
4. Removing explicit 3D network operations — rather than adding them — is the key to strong cross-domain generalization on scale-inconsistent pointmaps.

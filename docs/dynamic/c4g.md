# C4G: Learning Global Motion with Compact Gaussians for Feed-Forward 4D Reconstruction (arXiv preprint (2026-05))

## 📋 Overview

- **Authors**: Mungyeom Kim, Minkyeong Jeon, Honggyu An, Jaewoo Jung, Hyunah Ko, Jisang Han, Hyeonseo Yu, Donghwan Shin, Sunghwan Hong, Takuya Narihira, Kazumi Fukuda, Yuki Mitsufuji, Seungryong Kim
- **Institution**: KAIST AI; ETH Zürich, ETH AI Center; Sony AI; Sony Group Corporation
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.31595) | [Project Page](https://cvlab-kaist.github.io/C4G)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward 4D reconstruction framework (C4G = Compact 4D representation with Gaussians) that replaces per-pixel Gaussian prediction with a compact set of timestamp-conditioned learnable query tokens, aggregating full temporal context to model global motion, using ~0.007× fewer Gaussians without camera poses.

## 🎯 Key Contributions

1. **Compact query-based 4D representation**: A small set of timestamp-conditioned learnable queries aggregate multi-frame features via full self-attention and decode 3D Gaussians whose positions are modulated by the target timestamp — forcing global motion modeling rather than per-frame overfitting.
2. **VDM rendering enhancement**: A Wan2.1-VACE-1.3B video diffusion model, fine-tuned to refine renderings conditioned on context views, recovers fine details lost to the compact bottleneck.
3. **Feed-forward 4D feature lifting**: Reuses the decoder's attention patterns to lift arbitrary 2D VFM features (DINOv3, VGGT) into a 4D feature field supporting point tracking and dynamic scene understanding.

## 🔧 Technical Details

### Architecture

- **Encoder**: VGGT-initialized backbone extracts geometry-grounded per-frame features.
- **Query-based Gaussian decoder**: N learnable query tokens concatenated with features, passed through L transformer layers with full self-attention; refined queries mapped to 3D Gaussians via an MLP head.
- **Time embedding**: sinusoidal timestamp embeddings injected into per-frame features and target-time query conditioning (`F̂_t = F_t + H(ψ(t))`, `Q̂ = Q + H(ψ(t̂))`).
- **Emergent attention**: two self-attention layers specialize — first attends to geometrically corresponding regions across all frames, second to frames temporally close to the target.
- **Feature lifting decoder** `D_F` mirrors `D_G`, reusing queries/keys and training only value projections.

### Training

- N = 2048 queries, L = 2 layers, SH degree 0 (single RGB per Gaussian), 224×224 inputs.
- Datasets: Spring, Kubric, RealEstate10K. Losses: photometric (MSE+LPIPS) + depth/normal from MoGe-2 + tracking from CowTracker (λ_depth = 0.001, λ_normal = 0.001, λ_track = 0.1).
- AdamW, LR 1e-5 (decoder) / 1e-7 (backbone), cosine schedule; batch 1 × 4 NVIDIA H100; initialized from C3G (static).

## 📊 Results

### Novel View Synthesis — DyCheck & ADT (원논문 Table 1)

원논문 Table 1 (일부). #G=Gaussian 수. ADT SSIM/LPIPS에서 4DGT가, DyCheck LPIPS에서 MoVieS가 Ours보다 낫다.

| Method          | Per-scene | Pose | #G ↓   | DyC PSNR ↑ | DyC SSIM ↑ | DyC LPIPS ↓ | ADT PSNR ↑ | ADT SSIM ↑ | ADT LPIPS ↓ |
| --------------- | --------- | ---- | ------ | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| Shape of Motion | ✓         | ✓    | 128K   | 14.13      | 0.313      | 0.690       | -          | -          | -           |
| MoSca           | ✓         | ✓    | 342K   | 11.93      | 0.252      | 0.700       | 2.419      | 0.343      | 0.892       |
| 4DGT            | ✗         | ✓    | 272K   | 12.15      | 0.247      | 0.477       | 19.22      | **0.717**  | **0.260**   |
| MoVieS          | ✗         | ✓    | 802K   | 11.99      | 0.352      | **0.359**   | 20.35      | 0.526      | 0.394       |
| NeoVerse        | ✗         | ✗    | 802K   | 11.90      | 0.251      | 0.450       | 21.94      | 0.629      | 0.270       |
| **Ours**        | ✗         | ✗    | **2K** | **15.64**  | **0.388**  | 0.384       | **22.35**  | 0.631      | 0.313       |

### Novel View Synthesis — TUM-Dynamics & NVIDIA (원논문 Table 1)

원논문 Table 1 (일부).

| Method          | TUM PSNR ↑ | TUM SSIM ↑ | TUM LPIPS ↓ | NVIDIA PSNR ↑ | NVIDIA SSIM ↑ | NVIDIA LPIPS ↓ |
| --------------- | ---------- | ---------- | ----------- | ------------- | ------------- | -------------- |
| Shape of Motion | 14.29      | 0.453      | 0.552       | 10.86         | 0.280         | 0.791          |
| MoSca           | 9.765      | 0.247      | 0.654       | 12.62         | 0.269         | 0.691          |
| 4DGT            | 17.27      | 0.578      | 0.329       | 15.64         | 0.349         | 0.614          |
| MoVieS          | 14.91      | 0.378      | 0.395       | 13.71         | 0.211         | 0.596          |
| NeoVerse        | 15.26      | 0.437      | 0.415       | 15.86         | 0.322         | 0.492          |
| **Ours**        | **19.52**  | **0.603**  | **0.306**   | **20.51**     | **0.489**     | **0.393**      |

### Robustness to Temporal Gap — TUM-Dynamics (원논문 Table 2)

원논문 Table 2. 큰 ∆t에서 Ours의 성능 저하가 가장 적다. ∆t=2의 SSIM(4DGT 0.674)·LPIPS(NeoVerse 0.216)에서는 Ours가 뒤진다.

| Method   | Pose | ∆t2 PSNR ↑ | ∆t2 SSIM ↑ | ∆t2 LPIPS ↓ | ∆t4 PSNR ↑ | ∆t4 SSIM ↑ | ∆t4 LPIPS ↓ |
| -------- | ---- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| 4DGT     | ✓    | 19.27      | **0.674**  | 0.251       | 18.08      | **0.623**  | 0.297       |
| MoVieS   | ✓    | 16.30      | 0.441      | 0.314       | 15.93      | 0.432      | 0.334       |
| NeoVerse | ✗    | 20.14      | 0.671      | **0.216**   | 18.23      | 0.575      | 0.296       |
| **Ours** | ✗    | **20.59**  | 0.647      | 0.267       | **20.00**  | 0.619      | **0.290**   |

원논문 Table 2 (일부, 큰 gap).

| Method   | ∆t6 PSNR ↑ | ∆t6 SSIM ↑ | ∆t6 LPIPS ↓ | ∆t8 PSNR ↑ | ∆t8 SSIM ↑ | ∆t8 LPIPS ↓ |
| -------- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| 4DGT     | 17.27      | 0.578      | 0.329       | 16.27      | 0.547      | 0.351       |
| MoVieS   | 14.91      | 0.378      | 0.395       | 14.23      | 0.322      | 0.428       |
| NeoVerse | 15.26      | 0.437      | 0.415       | 15.94      | 0.475      | 0.387       |
| **Ours** | **19.52**  | **0.603**  | **0.306**   | **19.23**  | **0.599**  | **0.311**   |

### Temporal-Invariant Feature — Point Tracking (원논문 Table 3)

원논문 Table 3. TAP-Vid 프로토콜. RGB-stacking 및 DAVIS, <δ0/<δ2/<δ4/<δavg (↑).

| Method               | RGB δ0 ↑ | RGB δ2 ↑ | RGB δ4 ↑ | RGB δavg ↑ | DAVIS δ0 ↑ | DAVIS δ2 ↑ | DAVIS δ4 ↑ | DAVIS δavg ↑ |
| -------------------- | -------- | -------- | -------- | ---------- | ---------- | ---------- | ---------- | ------------ |
| DINOv3-L             | 1.3      | 11.3     | 65.6     | 23.2       | 0.6        | 6.2        | 40.7       | 13.7         |
| DINOv3-L + Ours      | 6.9      | 38.3     | 74.4     | 39.3       | 2.2        | 19.8       | 63.1       | 27.1         |
| VGGT-Tracking        | 1.1      | 15.9     | 63.6     | 24.8       | 2.7        | 17.9       | 54.0       | 23.1         |
| VGGT-Tracking + Ours | 4.9      | 28.7     | 68.0     | 33.0       | 4.4        | 23.4       | 68.7       | 30.5         |

### Dynamic Scene Understanding — DAVIS (원논문 Table 4)

원논문 Table 4.

| Method | mIOU ↑    | Acc ↑     | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ------ | --------- | --------- | ---------- | --------- | --------- |
| LSeg   | 0.550     | 0.801     | -          | -         | -         |
| LSM    | 0.615     | 0.844     | 14.320     | 0.310     | 0.517     |
| C3G    | 0.345     | 0.528     | 18.623     | 0.376     | 0.460     |
| Ours   | **0.634** | **0.854** | **20.181** | **0.426** | **0.359** |

### Ablation — Time Embedding (원논문 Table 5)

원논문 Table 5. Sinusoidal이 RoPE보다 우수, dim 256에서 포화.

| Positional Emb. | Dim | DyC PSNR ↑ | DyC SSIM ↑ | DyC LPIPS ↓ | TUM PSNR ↑ | TUM SSIM ↑ | TUM LPIPS ↓ |
| --------------- | --- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| RoPE            | -   | 12.73      | 0.302      | 0.520       | 14.90      | 0.349      | 0.571       |
| Sinusoidal      | 64  | 15.31      | 0.382      | 0.397       | 18.65      | 0.559      | 0.363       |
| Sinusoidal      | 128 | 15.39      | 0.377      | 0.388       | 18.67      | 0.560      | 0.355       |
| Sinusoidal      | 256 | 15.54      | 0.383      | 0.385       | 18.94      | 0.575      | 0.341       |
| Sinusoidal      | 512 | 15.54      | 0.386      | 0.391       | 18.90      | 0.572      | 0.345       |

### Ablation — Loss Functions (원논문 Table 6)

원논문 Table 6.

| Method                | DyC PSNR ↑ | DyC SSIM ↑ | DyC LPIPS ↓ | TUM PSNR ↑ | TUM SSIM ↑ | TUM LPIPS ↓ |
| --------------------- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| Ours                  | 15.54      | 0.383      | 0.385       | 18.94      | 0.575      | 0.341       |
| w/o L_track           | 15.46      | 0.381      | 0.390       | 18.97      | 0.574      | 0.342       |
| w/o L_depth           | 15.50      | 0.381      | 0.385       | 18.35      | 0.557      | 0.357       |
| w/o L_normal          | 15.41      | 0.390      | 0.389       | 17.86      | 0.537      | 0.375       |
| w/o L_depth, L_normal | 15.21      | 0.377      | 0.397       | 18.80      | 0.568      | 0.347       |

## 💡 Insights & Impact

- Per-pixel feed-forward 4D methods produce duplicated, view-dependent Gaussians causing ghosting at interpolated times and poor occlusion filling; a compact query bottleneck compels global motion reasoning.
- Compactness (2K Gaussians) trades against high-frequency detail, recovered by a VDM refiner that only enhances details since the base render is geometrically coherent.
- The 4D feature field even surpasses the source 2D VFM features (DINOv3/VGGT) and LSeg itself in temporal/geometric consistency.

## 🔗 Related Work

- Backbone [VGGT](../reconstruction/vggt.md); geometry supervision from [MoGe-2](../reconstruction/moge-2.md); scene-understanding baseline [LSM (Large Spatial Model)](../understanding/largespatialmodel.md); built on C3G (compact static Gaussians); compared against per-pixel 4D methods (4DGT, MoVieS, NeoVerse) and optimization methods (Shape of Motion, MoSca).

## 📚 Key Takeaways

1. Replacing per-pixel with compact query-based Gaussian prediction yields globally coherent motion and eliminates ghosting/occlusion artifacts.
2. State-of-the-art or competitive NVS with ~0.007× the Gaussians and no GT poses, especially robust to large temporal gaps — honestly noting 4DGT/MoVieS/NeoVerse win some ADT/DyCheck LPIPS/SSIM and small-∆t metrics.
3. First feed-forward 4D feature-lifting architecture, enabling point tracking and open-vocabulary dynamic scene understanding.

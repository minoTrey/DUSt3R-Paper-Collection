# GlobalSplat: Efficient Feed-Forward 3D Gaussian Splatting via Global Scene Tokens (arXiv preprint (2026-04))

![globalsplat — architecture](https://arxiv.org/html/2604.15284v2/x5.png)

_GlobalSplat Architecture Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Roni Itkin, Noam Issachar, Yehonatan Keypur, Xingyu Chen, Anpei Chen, Sagie Benaim
- **Institution**: The Hebrew University of Jerusalem; Westlake University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.15284) | [Project Page](https://r-itk.github.io/globalsplat/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An "align first, decode later" feed-forward 3DGS framework that fuses all input views into a fixed set of global latent scene tokens before decoding explicit Gaussians, keeping a view-invariant budget of 2K–32K Gaussians (as low as 16K, ~4 MB) with inference under 78 ms.

## 🎯 Key Contributions

1. **Diagnosis of a scalability bottleneck**: Existing feed-forward 3DGS pipelines form primitives in dense, view-aligned spaces (pixel-/voxel-aligned) and align them globally only afterward, baking in redundancy that scales the Gaussian count with input-view count.
2. **Align First, Decode Later**: GlobalSplat aggregates multi-view input into a fixed number of global latent scene tokens that resolve cross-view correspondence, then decodes an explicit 3DGS asset — without pretrained pixel-prediction backbones or reusing latents from dense baselines.
3. **Compact, view-invariant budget**: A strict 2K–32K Gaussian representation (<4 MB), reducing primitive count by over 99% versus dense baselines while retaining fast rendering and deployment benefits of explicit 3DGS.

## 🔧 Technical Details

### Architecture

- **View Encoder** extracts patchified RGB tokens; each patch is augmented with a camera token built from a patchified Plücker-ray embedding plus a per-view camera code (Fourier-encoded camera center + MLP-encoded intrinsics).
- **Scene normalization**: cameras are mapped to a canonical "average camera" frame; scene scale is set to the diameter of the camera constellation (following YoNoSplat), giving a canonical-frustum geometric prior.
- **Learnable latent tokens**: `M = 2048` tokens of dimension `d = 512`, fixed and independent of input-view count, plus register tokens.
- **Dual-branch encoder** (`B = 4` blocks): parallel geometry and appearance streams; each block cross-attends latent tokens to multi-view patch features, then applies `L = 2` self-attention blocks, and fuses the streams with a 2-layer mixer MLP. The disentanglement prevents the model from masking poor structure with texture.
- **Dual-branch decoder**: separate heads decode geometry (position, scale, quaternion, opacity) and appearance (color).

### Coarse-to-fine capacity curriculum

- Each latent slot predicts `Ks = 16` Gaussian candidates. Training starts coarse (all 16 merged into 1 representative Gaussian, `G = 1`) and increases capacity `G ∈ {2, 4, 8}`; the final model uses `G = 8`. Merging uses temperature-scaled softmax importance weights.

### Training objective

- `L = λ_ren L_ren + λ_con L_con + λ_reg L_reg`: rendering loss (MSE + perceptual), a self-supervised consistency loss between two input-view subsets (stop-gradient on opacity and depth maps), and regularizations (soft feature thresholding + frustum constraint).

## 📊 Results

Evaluated on RealEstate10K and ACID at 256×256, expanding the NoPoSplat/C3G two-view anchors to 12/24/36 context views. Efficiency measured on a single NVIDIA A100 (64 GB).

### RealEstate10K, 24 input views

원논문 Table 1. 지표는 PSNR↑, SSIM↑, LPIPS↓, #G(K)↓ (Gaussian 개수, 천 단위). LVSM은 non-GS 방법.

| Method                 | PSNR ↑    | SSIM ↑    | LPIPS ↓   | #G(K) ↓ |
| ---------------------- | --------- | --------- | --------- | ------- |
| LVSM (non-GS)          | 27.24     | 0.874     | 0.112     | –       |
| NoPoSplat              | 21.24     | 0.664     | 0.200     | 1204    |
| AnySplat               | 24.11     | 0.838     | 0.198     | 2636    |
| EcoSplat               | 24.72     | 0.822     | 0.183     | 78      |
| DepthSplat             | 19.66     | 0.743     | 0.239     | 1572    |
| GGN                    | 18.50     | 0.682     | 0.299     | 385     |
| Zpressor (6 views)     | **28.51** | **0.911** | **0.097** | 393     |
| Zpressor (3 views)     | 23.65     | 0.846     | 0.157     | 197     |
| C3G                    | 23.80     | 0.747     | 0.198     | 2       |
| GlobalSplat-2K (Ours)  | 26.84     | 0.838     | 0.198     | 2       |
| GlobalSplat-16K (Ours) | 28.53     | 0.883     | 0.140     | 16      |
| GlobalSplat-32K (Ours) | 29.48     | 0.901     | 0.122     | 32      |

Zpressor (6 views) remains the strongest per-metric on RealEstate10K, but at 393K Gaussians; GlobalSplat-32K surpasses it on PSNR (29.48 vs 28.51) with a 32K budget, and GlobalSplat-16K matches its quality at ~24× fewer primitives.

### Cross-dataset generalization: ACID, 24 input views (zero-shot)

원논문 Table 2. 지표는 PSNR↑, SSIM↑, LPIPS↓, #G(K)↓.

| Method                 | PSNR ↑    | SSIM ↑    | LPIPS ↓   | #G(K) ↓ |
| ---------------------- | --------- | --------- | --------- | ------- |
| LVSM (non-GS)          | 28.29     | 0.826     | 0.161     | –       |
| DepthSplat             | 20.15     | 0.711     | 0.258     | 1572    |
| GGN                    | 20.90     | 0.657     | 0.314     | 396     |
| Zpressor               | **28.53** | **0.860** | **0.138** | 393     |
| C3G                    | 22.24     | 0.598     | 0.331     | 2       |
| GlobalSplat-16K (Ours) | 28.03     | 0.813     | 0.207     | 16      |

On ACID transfer, Zpressor is slightly ahead on quality (28.53 vs 28.03 PSNR) but again uses ~24× more Gaussians; GlobalSplat clearly beats DepthSplat, GGN, and C3G.

### Efficiency, 24 input views

원논문 Table 3. Peak GPU memory·inference time(단일 forward pass)·디스크 크기. Ours16K = GlobalSplat-16K.

| Metric            | LVSM   | DepthSplat | Zpressor | C3G    | GGN     | Ours16K   |
| ----------------- | ------ | ---------- | -------- | ------ | ------- | --------- |
| Peak Mem (GB)     | 4.60   | 29.84      | 3.70     | 6.04   | 25.08   | **1.79**  |
| Inf. Time (ms)    | 940.00 | 669.50     | 194.20   | 387.14 | 1800.64 | **77.88** |
| Size on Disk (MB) | –      | 534        | 134      | 0.1    | 174     | 3.8       |

GlobalSplat-16K is the most memory-efficient and fastest among the compared methods (C3G has a smaller 0.1 MB disk size but much lower quality).

### Model ablation (RealEstate10K)

원논문 Table 5. 지표는 PSNR↑, SSIM↑, LPIPS↓. Single-stream은 파라미터 수를 맞추려 폭을 키움(90M vs 83.4M).

| Variant                         | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ------------------------------- | --------- | --------- | --------- |
| Ours (full)                     | **28.57** | **0.885** | **0.139** |
| Plücker only                    | 28.30     | 0.880     | 0.140     |
| w/o consistency loss            | 28.15     | 0.876     | 0.143     |
| Single-stream                   | 28.02     | 0.873     | 0.151     |
| Direct full-capacity prediction | 27.69     | 0.867     | 0.150     |

The two-stream factorization helps beyond raw capacity (single-stream is widened to match parameters), and the coarse-to-fine curriculum and re-injected camera metadata each contribute.

### Compactness–quality trade-off

원논문 Table 4. #G = (#Latents) × (Splats/Token). 잠재 토큰 수를 늘리는 편이 토큰당 Gaussian 수를 늘리는 것보다 효과적.

| Total #G | #Latents | Splats/Token | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| -------- | -------- | ------------ | ------ | ------ | ------- |
| 2,048    | 256      | 8            | 25.25  | 0.785  | 0.250   |
| 2,048    | 2,048    | 1            | 26.83  | 0.838  | 0.198   |
| 16,384   | 2,048    | 8            | 28.57  | 0.885  | 0.138   |
| 32,768   | 2,048    | 16           | 28.58  | 0.884  | 0.135   |
| 32,768   | 4,096    | 8            | 29.54  | 0.903  | 0.121   |

## 💡 Insights & Impact

- **Scene-centric primitive allocation**: Driving primitive placement by global scene structure rather than image-grid support yields adaptive allocation — fewer, larger Gaussians in low-frequency regions — enabling complex scenes with far fewer primitives.
- **View-invariant scaling**: Because the token budget is fixed, adding more input views improves coverage without inflating the representation, addressing the central scalability bottleneck of dense pipelines.
- **Latent capacity is the driver**: Ablations show reconstruction quality is governed primarily by the number of latent scene tokens, not the decoded Gaussians per token.
- **Limitations**: Fixed 16K budget may under-serve unbounded/city-scale scenes; the model assumes static scenes; and extreme sparse-view (2–3 image) settings remain hard due to insufficient parallax.

## 🔗 Related Work

- Builds on the feed-forward 3D reconstruction line from [DUSt3R](../foundation/dust3r.md) (pixel-aligned pointmaps) and multi-view extensions with global attention such as [VGGT](../reconstruction/vggt.md) and [Fast3R](../reconstruction/fast3r.md); cites streaming/memory approaches [CUT3R](../dynamic/cut3r.md) and MUSt3R for large-context scalability.
- Contrasts with feed-forward 3DGS baselines: pixelSplat, MVSplat, GS-LRM, DepthSplat, NoPoSplat, AnySplat, GGN, and compression-oriented Zpressor/TinySplat, which rely on view-centric intermediates.
- Closest to LVSM (fixed latent tokens but no explicit 3D asset) and concurrent C3G (learnable queries → compact Gaussians via full self-attention and single-Gaussian decoding); GlobalSplat differs with an iterative disentangled dual-branch encoder and coarse-to-fine curriculum.

## 📚 Key Takeaways

1. Fusing multi-view input into a fixed set of global latent tokens before decoding gives a view-invariant Gaussian budget, breaking the redundancy scaling of pixel/voxel-aligned feed-forward pipelines.
2. A dual-branch geometry/appearance encoder plus a coarse-to-fine capacity curriculum reaches competitive novel-view synthesis (28.5 PSNR at 24 views) with only 16K Gaussians and a ~4 MB footprint.
3. The compact representation translates into the lowest peak memory (1.79 GB) and fastest inference (77.88 ms) among compared methods, though the heavier Zpressor still edges quality on some per-metric comparisons.

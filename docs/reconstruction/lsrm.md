# LSRM: High-Fidelity Object-Centric Reconstruction via Scaled Context Windows (arXiv preprint (2026-04))

## 📋 Overview

- **Authors**: Zhengqin Li, Cheng Zhang, Jakob Engel, Zhao Dong
- **Institution**: Meta Reality Labs Research
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.05182)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: LSRM (Large Sparse Reconstruction Model) scales feed-forward 3D object reconstruction by expanding the transformer context window with Native Sparse Attention (NSA), handling 20× more object tokens and >2× more image tokens than prior SOTA to close the texture-fidelity gap to dense-view optimization (>2.4 dB PSNR, >40% lower LPIPS on GSO).

## 🎯 Key Contributions

1. **Context-window scaling for feed-forward 3D**: Demonstrates that enlarging the number of active object and image tokens—rather than swapping the 3D representation or adding post-hoc refinement—narrows the fine-texture gap to optimization-based pipelines.
2. **Coarse-to-fine sparse pipeline**: A Stage 1 dense reconstruction transformer initializes weights and geometry; a Stage 2 sparse transformer predicts high-resolution sparse volume residuals only over informative (near-surface / foreground) tokens.
3. **3D-aware spatial block routing**: Selects NSA KV-blocks using explicit geometric distances and known camera parameters instead of attention scores, fixing unreliable 2D-3D correspondences in early transformer layers.
4. **Block-aware sequence parallelism with All-gather-KV**: Shards tokens by 2D/3D spatial blocks to keep each block on one GPU, and broadcasts a compressed KV cache (via GQA) to balance dynamic sparse workloads across GPUs.
5. **Inverse-rendering extension**: Fine-tunes the NVS model to predict BRDF material maps (albedo, roughness, metallic), matching or exceeding SOTA dense-view optimization on LPIPS across StanfordORB, DTC, and OWL.

## 🔧 Technical Details

### Two-Stage Coarse-to-Fine Architecture

```text
Stage 1 (Dense):  low-res dense volume  → initializes weights + geometry
Stage 2 (Sparse): high-res sparse residuals over informative tokens (NSA)
```

- **Inputs**: A sparse set of M posed images (M ∈ [12, 18]), cameras encoded as Plücker rays. 256×256 input views split into non-overlapping 8×8 patches → 32-resolution token map per view. A frozen DINOv3 encoder supplies features (images upsampled 2× since DINOv3 uses 16×16 patches).
- **Volume tokens**: Initialized from factorized 1D positional embeddings along the three spatial axes (d = 1024, dense volume resolution Sd = 16), summed element-wise per voxel.
- **Dense transformer**: 24 blocks, hidden dim 1024, grouped-query attention with 32 query heads and 2 key/value heads. Uses a gated mixture of cross-attention updates (self + cross) rather than monolithic self-attention. Decoded dense feature volume upsamples 4× to resolution 64 with feature dim 32. Rendering uses the VolSDF formulation; MLP decoders output SDF + color (NVS) or albedo/roughness/metallic (inverse rendering).

### Stage 2: Sparse Reconstruction with NSA

- **Resolution scaling**: image S^img = 96 (3× dense), volume S^vol = 96 (6× dense); output sparse feature volume resolution 384.
- **Informative token selection**: Keep only foreground image patches; keep volume tokens near the object surface via an SDF distance threshold τ (sampling T = 4³ = 64 points per voxel).
- **Block partitioning**: 8×8 blocks for images, 8×8×8 for the volume; block-level compressed keys/values via ResBlock + AvgPool, following Direct3D-S2.
- **Residual prediction**: The sparse transformer (also 24 blocks, dim 1024) predicts residuals over the upsampled dense prediction rather than regressing high-res volume from scratch. NSACrossAttn combines three gated branches — Compressed (global context), Selected (top KV-blocks), Window (local) — with Triton kernels for the selected branch.
- **Rendering fusion**: High-frequency features from the sparse volume Xs are combined with the full dense volume Xd depending on the near-surface mask, with linear blending at boundaries.

### 3D-Aware Block Routing

Each token is assigned an explicit 3D coordinate (voxel center for volume tokens; highest-opacity foreground surface point for image patches). Blocks are selected by minimal 3D Euclidean distance after projecting query points onto image planes with known cameras, instead of relying on compressed-token attention scores that fail in early layers.

### Custom Sequence Parallelism

Sparse tokenization produces highly variable active-token counts (straggler GPUs stall training). LSRM adapts context parallelism into a block-aware scheme that spreads tokens evenly across GPUs while keeping each spatial block on one device (zero cross-GPU communication for local attention), plus an All-gather-KV protocol that replicates the small compressed KV cache node-wide (hq = 32, hkv = 2 enables high GQA compression). Balanced across 8 GPUs.

### Training & Inference

- **Data**: 600K curated 3D models; 12–16 input views + 4 target views sampled from 32 poses on a sphere. NVS losses: appearance (MSE + LPIPS), foreground-mask, depth, and a numerical normal loss applied only in the final 500–1000 iterations.
- **Three NVS stages** require 5, 7, and 3 days respectively on 128 H100 GPUs; Table 5 lists 16K / 12K / 3K iterations for the three stages.
- **Token scale**: Active image and volume token counts peak at roughly 100K and 300K. Prior SOTA LIRM processes ≤8 images (64×64×8 ≈ 32K image tokens) with a hexaplane representation (48×48×6 ≈ 14K object tokens) → LSRM scales to >2× image tokens and >20× object tokens.
- **Inference**: Single NVIDIA H100, 16 input images at highest resolution → 40 GB peak GPU memory, ~5 s per object on average.

## 📊 Results

### Novel View Synthesis on GSO

Feed-forward baselines and LSRM ablations. Full model = S^img = S^vol = 96 with 3D-aware routing.

원논문 Table 1 (baselines).

| Method          | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| --------------- | --------- | --------- | --------- |
| Mesh-LRM        | 28.13     | 0.923     | 0.093     |
| GS-LRM          | 30.52     | 0.952     | 0.050     |
| LIRM            | 30.65     | 0.949     | 0.054     |
| Dense model     | 28.45     | 0.934     | 0.079     |
| **LSRM (full)** | **33.08** | **0.971** | **0.028** |

원논문 Table 1 (LSRM 컨텍스트 스케일링·라우팅 ablation). "w/o/w routing" = 3D-aware routing 유무.

| Config                         | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ------------------------------ | --------- | --------- | --------- |
| S^img=64, S^vol=48             | 31.68     | 0.958     | 0.044     |
| S^img=48, S^vol=64             | 31.82     | 0.959     | 0.043     |
| S^img=S^vol=64, w/o routing    | 31.34     | 0.956     | 0.045     |
| S^img=S^vol=64, w/ routing     | 31.93     | 0.962     | 0.040     |
| S^img=S^vol=96, w/o routing    | 32.72     | 0.968     | 0.032     |
| **S^img=S^vol=96, w/ routing** | **33.08** | **0.971** | **0.028** |

Full model improves PSNR by >2.4 dB and reduces LPIPS by >40% vs the strongest baseline. Ablation shows volume-token scaling has larger impact than image-token scaling: reducing S^vol from 64 to 48 drops PSNR to 31.68 vs 31.82 when reducing S^img from 64 to 48.

### Inverse Rendering (Full Views)

LSRM consistently achieves the lowest LPIPS on all three datasets but loses some pixel-wise metrics (e.g., NeuralPBIR's PSNR-H/PSNR-L/SSIM on StanfordORB; InvRender's PSNR-L on DTC).

원논문 Table 2 (StanfordORB). PSNR-H·PSNR-L·SSIM↑, LPIPS·CD↓.

| Method          | PSNR-H ↑  | PSNR-L ↑  | SSIM ↑    | LPIPS ↓   | CD ↓     |
| --------------- | --------- | --------- | --------- | --------- | -------- |
| NVDiffrecMc     | 24.43     | 31.60     | 0.972     | 0.036     | 0.51     |
| InvRender       | 23.76     | 30.83     | 0.970     | 0.046     | 0.44     |
| NeuralPBIR      | **26.01** | **33.26** | **0.979** | 0.023     | 0.43     |
| LIRM            | 25.09     | 32.45     | 0.972     | 0.025     | 0.38     |
| **Ours (LSRM)** | 25.47     | 32.85     | 0.977     | **0.022** | **0.29** |

원논문 Table 2 (DTC). PSNR-H·PSNR-L·SSIM↑, LPIPS↓.

| Method          | PSNR-H ↑  | PSNR-L ↑  | SSIM ↑    | LPIPS ↓   |
| --------------- | --------- | --------- | --------- | --------- |
| NVDiffrecMc     | 27.78     | 34.55     | 0.952     | 0.042     |
| InvRender       | 29.52     | **35.98** | 0.961     | 0.037     |
| LIRM            | 27.65     | 34.84     | 0.960     | 0.031     |
| **Ours (LSRM)** | **29.67** | 35.66     | **0.964** | **0.025** |

원논문 Table 2 (OWL). PSNR·SSIM↑, LPIPS↓.

| Method          | PSNR ↑    | SSIM ↑   | LPIPS ↓   |
| --------------- | --------- | -------- | --------- |
| NVDiffrecMc     | 19.82     | 0.73     | 0.389     |
| InvRender       | 23.77     | 0.78     | 0.369     |
| LIRM            | 23.27     | 0.77     | 0.322     |
| **Ours (LSRM)** | **24.88** | **0.79** | **0.269** |

NeuralPBIR reports N/A on DTC and OWL; PSNR-H/PSNR-L on StanfordORB are half/low-exposure PSNR variants.

### NVS with Fewer Input Views on GSO

LSRM is trained on 12–16 views but generalizes to fewer views, outperforming LIRM at both 8 and 16 views.

원논문 Table 3.

| Method   | Views | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------- | ----- | --------- | --------- | --------- |
| LIRM     | 8     | 30.48     | 0.947     | 0.056     |
| LIRM     | 16    | 30.56     | 0.948     | 0.054     |
| **Ours** | 8     | 32.46     | 0.968     | 0.031     |
| **Ours** | 16    | **33.08** | **0.971** | **0.028** |

The 8-view LSRM gains close to 2 dB PSNR over the 16-view LIRM (≈37% MSE drop) with LPIPS dropping >40%.

### Inverse Rendering with Fewer Input Views (StanfordORB)

With only 6 views, LSRM outperforms feed-forward relighting baselines RelitLRM and LIRM.

원논문 Table 4 (StanfordORB 열만 발췌). PSNR-H·PSNR-L·SSIM↑, LPIPS·CD↓.

| Method   | Views | PSNR-H ↑  | PSNR-L ↑  | SSIM ↑    | LPIPS ↓   | CD ↓     |
| -------- | ----- | --------- | --------- | --------- | --------- | -------- |
| RelitLRM | 6     | 24.67     | 31.52     | 0.969     | 0.032     | N/A      |
| LIRM     | 6     | 24.76     | 32.11     | 0.971     | 0.027     | 0.48     |
| **Ours** | 6     | **25.57** | 32.74     | 0.975     | **0.023** | **0.32** |
| **Ours** | 18    | 25.47     | **32.85** | **0.978** | 0.022     | 0.29     |

### Geometry Evaluation on DTC (Appendix)

원논문 Table 6. Normal·Depth 모두 ↓.

| Method          | Normal ↓ | Depth ↓   |
| --------------- | -------- | --------- |
| NVDiffrecMc     | 0.06     | 0.02      |
| InvRender       | **0.03** | 0.22      |
| LIRM            | 0.05     | 0.017     |
| **Ours (LSRM)** | **0.03** | **0.008** |

### Comparison with 3D Gaussian Optimization on GSO (Appendix)

On 10 randomly selected GSO models, LSRM (8–16 views) is competitive with 3DGS at 64 views. 3DGS at 64 views still reports higher SSIM (0.985) and equal/lower LPIPS (0.022), while LSRM leads on PSNR.

원논문 Table 7.

| Method   | Views | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------- | ----- | --------- | --------- | --------- |
| 3DGS     | 16    | 25.10     | 0.944     | 0.160     |
| 3DGS     | 32    | 31.63     | 0.980     | 0.049     |
| 3DGS     | 64    | 33.44     | **0.985** | **0.022** |
| **LSRM** | 8     | 33.68     | 0.970     | 0.027     |
| **LSRM** | 16    | **34.17** | 0.973     | 0.025     |

### Training Hyperparameters (Appendix)

원논문 Table 5 (일부 열 발췌 — 명확히 파싱되는 값만).

| Stage   | Iterations | Learning Rate   | Batch Size | Crop Size |
| ------- | ---------- | --------------- | ---------- | --------- |
| Stage 1 | 16K        | 4×10⁻⁴ → 1×10⁻⁴ | 8          | 192       |
| Stage 2 | 12K        | 1×10⁻⁴ → 4×10⁻⁵ | 4          | 384       |
| Stage 3 | 3K         | 4×10⁻⁵ → 1×10⁻⁵ | 1          | 512       |

## 💡 Insights & Impact

- **Scaling context ≫ representation swaps**: The paper's central finding is that simply increasing the count of active object/image tokens—made tractable by NSA—recovers fine texture (legible text, sharp faces) that prior feed-forward models blur, without changing the underlying 3D representation.
- **Geometry-guided routing matters**: Vanilla NSA's attention-score block selection fails at early layers; explicit 3D-distance routing is what makes previously blurred text legible (Fig. 7, Tab. 1).
- **Systems co-design is load-bearing**: Dynamic sparse workloads create straggler GPUs; block-aware sequence parallelism + All-gather-KV (leveraging GQA compression, hq/hkv = 32/2) is required to train at S^img = S^vol = 96 at all.
- **Honest limitations**: Pixel-wise PSNR gains in inverse rendering are modest due to the ill-posed nature (global albedo/roughness/metallic shifts penalize PSNR); LSRM does not resolve roughness/metallic estimation ambiguity, and extremely fine details (small ingredient lists) can remain illegible. Future work: even longer context via Ulysses/ring attention, and extension to scene-scale reconstruction and video/image generation.
- **Efficiency framing**: ~5 s per object on one H100 (16 views, 40 GB) is orders of magnitude faster than optimization-based methods and comparable to LIRM's iterative refinement.

## 🔗 Related Work

- **[VGGT](vggt.md)**, **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: Cited among the 3D foundation models for joint geometry/camera estimation that motivate the broader feed-forward 3D reconstruction direction LSRM builds on.
- **LIRM** (the primary SOTA baseline) and **MeshLRM**: LSRM inherits their multi-view camera-trajectory sampling and SDF-bias design; LIRM's 8-image / hexaplane token budget is the reference LSRM scales past (>2× image, >20× object tokens).
- **LRM / GS-LRM / Mesh-LRM**: Earlier object-centric reconstruction models compared as baselines; LRM pioneered single-image geometry but struggles with high-fidelity textures.
- **NSA (Native Sparse Attention)** and **Direct3D-S2**: The sparse-attention algorithm LSRM adapts for 3D, and the spatial block-partitioning strategy it borrows for the volume.

## 📚 Key Takeaways

1. **Context-window scaling narrows the feed-forward vs optimization gap**: >2.4 dB PSNR and >40% LPIPS reduction on GSO over the strongest feed-forward baseline, with inverse-rendering LPIPS matching SOTA dense-view optimization.
2. **NSA + 3D-aware routing + block-aware parallelism** together enable 20× object tokens and >2× image tokens without proportional compute growth.
3. **Volume-token scaling dominates image-token scaling** in the ablation, and 3D-aware routing adds consistent gains on top of raw resolution increases.
4. **Generalizes to fewer views** (8-view NVS beats 16-view LIRM; 6-view inverse rendering beats RelitLRM/LIRM) despite training only on 12–16 views.
5. **Feed-forward, single-pass, ~5 s/object on one H100** — practical for industrial-scale 3D digital-twin creation, with material (BRDF) prediction for relighting.

# DarkVGGT: Seeing Through Darkness Using Thermal Geometry without Daylight Tax (arXiv preprint (2026-06))

![darkvggt — architecture](https://arxiv.org/html/2606.11326v2/x2.png)

_Overview of the DarkVGGT framework (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Minseong Kweon, Wenyuan Zhao, Nuo Chen, Lulin Liu, Huiwen Han, Zihao Zhu, Srinivas Shakkottai, Chao Tian, Zhiwen Fan
- **Institution**: University of Minnesota, Texas A&M University, Stanford University
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.11326) | [Code](https://github.com/phai-lab/DarkVGGT) | [Project Page](https://darkvggt.github.io)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An RGB-T feed-forward geometry framework that adapts a frozen VGGT-1B backbone with physics-inspired thermal factorization and geometry-shared thermal routing, improving depth and pose estimation in dark scenes while preserving well-lit RGB performance ("no daylight tax").

## 🎯 Key Contributions

1. **Conservative RGB-T fusion formulation**: Dark-scene geometry is cast as a conservative feed-forward multisensor fusion problem, keeping the RGB geometry pathway as the primary estimator and using thermal observations only for reliability-gated corrections under low light.
2. **Physics-Inspired Thermal Factorization**: A token-level decomposition that separates thermal embeddings into a geometry-consistent emissive-dominant component and a sparsely activated reflective residual before RGB fusion, motivated by Kirchhoff's law for opaque surfaces (ρ̂ = 1 − ε̂).
3. **Geometry-Shared Thermal Routing (GSTR)**: Separates modality-invariant geometry-shared thermal structure from thermal-private patterns via stop-gradient distillation, injecting only reliability-gated geometry-shared cues into the RGB stream.
4. **Daylight-tax reduction**: Thermal-branch dropout plus an anchoring loss (`Ldrop`) toward a frozen base-VGGT reference preserves the pretrained RGB prior, keeping well-lit ETH3D/ScanNet++ performance close to VGGT.
5. **Empirical results**: Consistent depth and pose gains over RGB-only and RGB-T feed-forward baselines across ViViD++, STheReO, and Dark3R.

## 🔧 Technical Details

### Base model and adaptation

DarkVGGT builds on **VGGT** as the base geometry predictor. It initializes from the publicly released **VGGT-1B** weights and keeps the backbone frozen, including a **frozen DINOv2 encoder**. VGGT patchifies each RGB frame into P tokens, augments each frame with a camera token and four register tokens, and processes the sequence with frame-wise and global **Alternating Attention (AA)** blocks.

For RGB-T adaptation, trainable parameters comprise:

- **Shared LoRA adapters** (r = 64, α = 128) on the AA blocks with modality-specific camera tokens
- A thermal camera token and RoPE offset
- The physics-inspired emissive/reflective gates
- The shared–private decomposition with ranks (d_s, d_p, d_mi) = (96, 192, 128), active in the last **k = 8** AA blocks

### Physics-Inspired Thermal Factorization

At each AA block, a joint RGB-T feature `h` is derived via a lightweight FFN from concatenated RGB and thermal patch tokens, predicting patch-wise pseudo-emissivity ε̂ = σ(W_ε h) and pseudo-reflectivity ρ̂ = 1 − ε̂ (complementary constraint from Kirchhoff's law). Emissive and reflective thermal embeddings are formed as z_emit = ε̂ ⊙ W_emit x_thr and z_refl = ρ̂ ⊙ W_refl HP(x_thr), where HP(·) is a high-pass filter implemented as x − AvgPool₃ₓ₃(x). The RGB token is updated by gated addition of both components. Three auxiliary regularizers guide the factorization:

- `Lsparse` = E[ρ̂]: sparsity bias encouraging an emissive-dominant decomposition
- `Ledge` = BCE(ρ̂, ρ_tar): edge-disagreement prior supervising ρ̂ from thermal–depth edge mismatch
- `Lortho` = E[Sim²(z_emit, z_refl)]: orthogonality penalty discouraging redundancy

### Geometry-Shared Thermal Routing

Thermal tokens are decomposed into geometry-shared (u_shr) and thermal-private (u_prv) components, and RGB is projected into the geometry-shared space (v_shr). Supervision uses:

- `Ldistill`: aligns the RGB geometry-shared projection to a stop-gradient geometry-shared thermal teacher
- `Lrecon`: variance-normalized MSE reconstructing thermal tokens from the thermal-private branch
- `Ldecorr` = ‖(u_shr)ᵀ u_prv‖²_F: cross-branch decorrelation to discourage subspace leakage

A per-token reliability gate g_shr routes the gated geometry-shared thermal residual to the RGB tokens; this module is instantiated only in the final k AA blocks.

### Training

Total objective: **L = L_VGGT + L_phys + L_gstr + 1_drop · λ_drop · L_drop**, where `Ldrop` = ‖D̂_rgb − D̂'_rgb‖²₂ + ‖P̂_rgb − P̂'_rgb‖²₂ anchors the RGB-only forward of the adapted model to a frozen base-VGGT reference on thermal-dropout steps, directly counteracting the daylight tax.

Training setup: four NVIDIA A100 GPUs, resolution 518 × 518, bfloat16 AMP, 10 epochs with 200 optimization steps per epoch, thermal dropout probability p = 0.5, AdamW with learning rate 5 × 10⁻⁵, weight decay 10⁻², cosine decay.

### Datasets and metrics

- **Low-visibility RGB-T**: ViViD++ and STheReO (real multi-sensor RGB-T), plus Dark3R as a complementary pseudo-thermal low-light evaluation (pseudo-thermal inputs synthesized with ThermalGen). Dense depth for ViViD++/STheReO is supervised with LiDAR-derived dense depth refined with Lingbot-Depth; Dark3R uses released canonical depth maps.
- **Well-lit (RGB-prior preservation)**: ETH3D and ScanNet++, evaluated RGB-only.
- **Depth metrics**: AbsRel, δ < 1.25, RMSElog. **Pose metrics**: RRA (relative rotation accuracy), RTA (relative translation accuracy), AUC (area under cumulative pose-accuracy curve), at a 30° threshold.

## 📊 Results

### Depth estimation across low-visibility scenes

원논문 Table 1.

| Method         | ViViD++ AbsRel↓ | ViViD++ δ<1.25↑ | ViViD++ RMSElog↓ | STheReO AbsRel↓ | STheReO δ<1.25↑ | STheReO RMSElog↓ | Dark3R AbsRel↓ | Dark3R δ<1.25↑ | Dark3R RMSElog↓ |
| -------------- | --------------- | --------------- | ---------------- | --------------- | --------------- | ---------------- | -------------- | -------------- | --------------- |
| DUSt3R (RGB)   | 0.3765          | 0.4883          | 0.4008           | 0.4759          | 0.3146          | 0.6437           | 0.2118         | 0.6391         | 0.2562          |
| MASt3R (RGB)   | 0.2685          | 0.6121          | 0.3132           | 0.5093          | 0.3418          | 0.6619           | 0.2004         | 0.6933         | 0.2496          |
| Dark3R (RGB)   | 0.3036          | 0.5739          | 0.3392           | 0.4843          | 0.3404          | 0.6437           | 0.1510         | 0.7914         | 0.1960          |
| DepthAnything3 | 0.2552          | 0.6239          | 0.2990           | 0.3145          | 0.4746          | 0.5246           | 0.2054         | 0.6528         | 0.2489          |
| VGGT (RGB)     | 0.2746          | 0.5874          | 0.3234           | 0.2950          | 0.5156          | 0.4567           | 0.2433         | 0.6095         | 0.2861          |
| SEAR (RGB-T)   | 0.1956          | 0.7502          | 0.2421           | 0.2370          | 0.6143          | 0.4147           | 0.1703         | 0.7058         | 0.2151          |
| **DarkVGGT**   | **0.1274**      | **0.8692**      | **0.1970**       | **0.1600**      | **0.7651**      | **0.3077**       | **0.1246**     | **0.8387**     | **0.1651**      |

Averaged over the three benchmarks vs. SEAR: AbsRel 0.2010 → 0.1373, δ < 1.25 0.6901 → 0.8243, RMSElog 0.2906 → 0.2232. Vs. its baseline VGGT: average AbsRel and RMSElog reduced by 0.1337 and 0.1322, and average δ < 1.25 improved by 0.2535.

### Camera pose estimation on low-visibility RGB-T scenes

원논문 Table 2.

| Method         | ViViD++ RRA@30↑ | ViViD++ RTA@30↑ | ViViD++ AUC@30↑ | STheReO RRA@30↑ | STheReO RTA@30↑ | STheReO AUC@30↑ | Dark3R RRA@30↑ | Dark3R RTA@30↑ | Dark3R AUC@30↑ |
| -------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | -------------- | -------------- | -------------- |
| DUSt3R (RGB)   | 0.72            | 0.22            | 6.4             | 0.88            | 0.43            | 27.0            | 0.98           | 0.20           | 10.0           |
| MASt3R (RGB)   | 0.76            | 0.46            | 27.1            | 0.98            | 0.80            | 71.3            | 1.00           | 0.89           | 62.5           |
| Dark3R (RGB)   | 0.74            | 0.41            | 22.7            | 0.99            | 0.79            | 69.8            | 1.00           | 0.94           | 68.0           |
| DepthAnything3 | 0.73            | 0.28            | 12.0            | 0.99            | 0.85            | 76.6            | 0.55           | 0.18           | 5.1            |
| VGGT (RGB)     | 0.81            | 0.48            | 25.9            | 1.00            | 0.99            | 96.3            | 0.64           | 0.47           | 15.3           |
| SEAR (RGB-T)   | 0.91            | 0.59            | 36.1            | 1.00            | 0.97            | 88.5            | 0.66           | 0.52           | 18.6           |
| **DarkVGGT**   | **0.98**        | **0.74**        | **46.0**        | 1.00            | 0.98            | 95.4            | **1.00**       | **0.95**       | 57.4           |

Vs. the average of RGB-only baselines, DarkVGGT improves RRA@30, RTA@30, and AUC@30 by 16.7%, 59.1%, and 66.8%. Vs. SEAR, average RRA@30/RTA@30/AUC@30 rise from 0.857/0.693/47.7 to 0.993/0.890/66.3. Note that on STheReO, VGGT (RGB-only) reaches the highest AUC@30 (96.3 vs. DarkVGGT's 95.4).

### RGB-only performance in well-lit scenes (prior preservation)

원논문 Table 3.

| Method       | ETH3D δ<1.25↑ | ETH3D RMSElog↓ | ETH3D RRA@30↑ | ETH3D RTA@30↑ | ScanNet++ δ<1.25↑ | ScanNet++ RMSElog↓ | ScanNet++ RRA@30↑ | ScanNet++ RTA@30↑ |
| ------------ | ------------- | -------------- | ------------- | ------------- | ----------------- | ------------------ | ----------------- | ----------------- |
| MASt3R       | 0.9413        | 0.1496         | 0.67          | 0.68          | 0.8762            | 0.1890             | 0.89              | 0.90              |
| Dark3R       | 0.8992        | 0.1739         | 0.63          | 0.65          | 0.8889            | 0.1802             | 0.88              | 0.89              |
| VGGT         | 0.9729        | 0.0595         | 1.00          | 0.91          | 0.9479            | 0.1106             | 0.98              | 0.93              |
| **DarkVGGT** | 0.9584        | 0.0803         | 1.00          | 0.88          | **0.9608**        | **0.1016**         | 0.98              | 0.92              |

Averaged over the two datasets, DarkVGGT differs from VGGT by only 0.0008 in δ < 1.25 and 0.0059 in RMSElog, exactly matches average RRA@30, and shows a 0.02 decrease in RTA@30 (0.92 → 0.90). On ETH3D, DarkVGGT is below VGGT (δ < 1.25 0.9584 vs. 0.9729; RMSElog 0.0803 vs. 0.0595); on ScanNet++ it improves both metrics. The reported daylight deviation is smaller than Dark3R's teacher gap vs. MASt3R (0.0147 decrease in average δ < 1.25, 0.0078 increase in RMSElog; pose underperforms MASt3R by 0.025 RRA@30 and 0.02 RTA@30).

### Ablation: proposed modules and cost

원논문 Table 4.

| Method                    | AbsRel↓    | δ<1.25↑    | RMSElog↓   | RRA@30↑ | RTA@30↑  | AUC@30↑ | #Param.(M) | FPS |
| ------------------------- | ---------- | ---------- | ---------- | ------- | -------- | ------- | ---------- | --- |
| AA                        | 0.1672     | 0.7512     | 0.2569     | 0.95    | 0.77     | 61.5    | 604.73     | 9.0 |
| LoRA                      | 0.1658     | 0.7590     | 0.2542     | 0.96    | 0.79     | 62.2    | 50.33      | 8.9 |
| LoRA + Phys               | 0.1422     | 0.8088     | 0.2298     | 1.00    | 0.86     | 68.9    | 107.21     | 7.5 |
| LoRA + GSTR               | 0.1538     | 0.7879     | 0.2386     | 0.97    | 0.79     | 62.4    | 70.81      | 7.5 |
| LoRA + Phys + GSTR (Full) | **0.1373** | **0.8243** | **0.2232** | 0.99    | **0.89** | 66.3    | 124.34     | 7.4 |

Phys provides the largest standalone gain; GSTR complements it in the full model. Vs. AA, the full model gives a 17.9% reduction in AbsRel and a 7.8% increase in AUC@30 while using 79.4% fewer learnable parameters (604.73M → 124.34M), with only marginal FPS differences. Note LoRA + Phys reaches the highest AUC@30 (68.9) in this table.

### Ablation: loss functions

원논문 Table 5. Pose reported at the finer @5 threshold; AUC at @30.

| Configuration | AbsRel↓    | δ<1.25↑    | RMSElog↓   | RRA@5↑ | RTA@5↑ | AUC@30↑ |
| ------------- | ---------- | ---------- | ---------- | ------ | ------ | ------- |
| Full          | **0.1373** | **0.8243** | **0.2232** | 0.68   | 0.45   | 66.3    |
| w/o Lsparse   | 0.1381     | 0.8188     | 0.2249     | 0.68   | 0.45   | 69.2    |
| w/o Lrecon    | 0.1404     | 0.8151     | 0.2274     | 0.68   | 0.44   | 65.9    |
| w/o Ledge     | 0.1418     | 0.8145     | 0.2287     | 0.67   | 0.43   | 65.3    |

Dropping `Ledge` causes the largest AbsRel increase (0.1373 → 0.1418). Removing `Lrecon` degrades AbsRel to 0.1404. `Lsparse` has the smallest AbsRel impact, but its removal lowers δ < 1.25; that variant raises AUC@30 (66.3 → 69.2) at the cost of degraded depth.

Qualitative nighttime comparisons across Dark3R, VGGT, SEAR, and DarkVGGT are shown in 그림 4, 수치 미인쇄.

## 💡 Insights & Impact

- **Thermal as corrective evidence, not a free appearance channel**: The core thesis is that naive RGB-T mixing erodes the pretrained visible-light prior and creates a "daylight tax." DarkVGGT keeps RGB primary and routes only geometry-consistent thermal cues, which the well-lit results support (near-VGGT ETH3D/ScanNet++ performance).
- **Physics factorization drives the main gains**: Ablations attribute most improvement to the emissive/reflective factorization (Phys), with GSTR providing complementary refinement at little runtime overhead.
- **Parameter efficiency**: The full LoRA-based model matches or beats full AA fine-tuning while using 79.4% fewer learnable parameters (124.34M vs. 604.73M).
- **Honest limitations**: The paper does not claim to dominate everywhere — VGGT still wins STheReO pose AUC@30, and DarkVGGT is below VGGT on ETH3D well-lit depth.
- **Stated limitations**: Assumes moderately aligned paired RGB-T inputs (limits weakly aligned/unpaired settings), and introduces several hyperparameters that may need calibration. Authors also flag thermal-sensing privacy concerns for deployment.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The base geometry predictor DarkVGGT adapts — VGGT-1B weights, frozen DINOv2 encoder, and Alternating Attention blocks are all reused; VGGT is the primary RGB-only baseline.
- **[DUSt3R](dust3r.md)**: The feed-forward dense point-map regression paradigm DarkVGGT descends from; RGB-only baseline in Tables 1–2.
- **[MASt3R](mast3r.md)**: Matching-grounded extension of DUSt3R; RGB-only baseline in Tables 1–3.
- **[Fast3R](../reconstruction/fast3r.md)**: Cited among works accelerating multi-view feed-forward geometry by avoiding explicit global correction.
- **[Spann3R](../reconstruction/spann3r.md)**: Cited (3D reconstruction with spatial memory) in the same scalable-aggregation line of DUSt3R descendants.
- **SEAR** (Skorokhodov et al., 2026, arXiv:2603.18774): The most closely related concurrent work — adapts a pretrained VGGT to RGB-T via LoRA fine-tuning, thermal camera tokens, and tailored batching; the primary RGB-T baseline. Not in this collection.
- **Dark3R** (Guo et al., 2026): RGB-only low-light SfM via clean-to-noisy distillation; both a baseline and a pseudo-thermal evaluation source. Not in this collection.

## 📚 Key Takeaways

1. DarkVGGT is a conservative RGB-T adaptation of a **frozen VGGT-1B** backbone, using LoRA plus two thermal modules to improve dark-scene geometry.
2. **Physics-Inspired Thermal Factorization** (emissive vs. reflective, ρ̂ = 1 − ε̂) and **Geometry-Shared Thermal Routing** (shared vs. private, reliability-gated injection) supply only geometry-consistent thermal cues to the RGB stream.
3. Across ViViD++, STheReO, and Dark3R it leads depth (avg AbsRel 0.1373) and pose, beating RGB-T baseline SEAR while keeping ETH3D/ScanNet++ near VGGT — reducing the "daylight tax."
4. Ablations show Phys drives most of the gain; the full model uses 79.4% fewer trainable parameters than full AA fine-tuning (124.34M vs. 604.73M).
5. As a July 2026 preprint, it is unpublished; results are self-reported and not yet peer-reviewed.

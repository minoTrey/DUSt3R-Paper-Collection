# RayMap3R: Inference-Time RayMap for Dynamic 3D Reconstruction (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Feiran Wang, Zezhou Shang, Gaowen Liu, Yan Yan
- **Institution**: University of Illinois Chicago, Cisco Research
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.20588) | [Project Page](https://raymap3r.github.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free streaming framework that exploits the static-scene bias of RayMap-only predictions: a dual-branch inference scheme contrasts image-based and RayMap-only depth to identify dynamic regions and suppress their interference during memory updates, adding reset metric alignment and state-aware smoothing to stabilize long-sequence trajectories — all built on a frozen CUT3R backbone without any fine-tuning.

## 🎯 Key Contributions

1. **RayMap static bias observation**: Models trained with the RayMap (per-pixel camera-ray) paradigm prioritize static structure when queried with RayMap tokens alone, because RayMap tokens encode only camera geometry and force the model to reconstruct scene content from memory — which favors temporally consistent static structure over transient dynamic objects.
2. **Dual-branch dynamic identification**: A main branch (image + RayMap features) and a RayMap-only branch decode from the same frozen state; their per-pixel depth discrepancy becomes a training-free signal for dynamic regions, converted into per-state-token staticness weights that gate memory updates.
3. **Reset metric alignment**: A Sim(3) transformation estimated from a repeated frame before/after each memory reset corrects scale/pose misalignment across segments, reducing accumulated drift over long sequences.
4. **State-aware smoothing**: An online, causal per-frame smoothing coefficient derived from the product of trajectory acceleration and internal state-change magnitude adaptively filters inter-frame displacements without storing history.

## 🔧 Technical Details

### RayMap and memory mechanism

RayMap is an H × W × 6 per-pixel tensor encoding ray origin and unit direction, determined by camera intrinsics K and extrinsics T = [R | τ]. Under the pinhole model, the ray origin c = −Rᵀτ is constant across pixels (the camera center) while the unit direction encodes each pixel's viewing ray. Streaming models such as CUT3R and TTT3R keep an implicit latent state sₜ; during inference (after a short warmup) the model can predict geometry from images or RayMap alone.

### Static bias of RayMap predictions

Given the same memory state sₜ₋₁, the image-based main prediction reconstructs the dynamic foreground, while the RayMap-only prediction focuses on static background. The paper attributes this to (1) training data dominated by static scenes and (2) RayMap tokens carrying only camera geometry. Across 108 sequences from MPI Sintel, DAVIS 2017, and TUM RGB-D, the per-pixel depth discrepancy between branches correlates positively with the ground-truth dynamic ratio (Spearman ρ = 0.77, p < 10⁻²²).

### Dual-branch inference

For predicted pose T̂ₜ, a new RayMap R(T̂ₜ) is encoded into tokens r′ₜ. The two branches decode as ŷₜᵐᵃⁱⁿ = Dec(fₜ + rₜ, sₜ₋₁) and ŷₜʳᵃʸᵐᵃᵖ = Dec(r′ₜ, sₜ₋₁). The absolute relative depth difference δᵢ = |zᵢᵐᵃⁱⁿ − zᵢʳᵃʸᵐᵃᵖ| / |zᵢᵐᵃⁱⁿ| is pooled to image-token scores by confidence-weighted averaging, then projected to per-state-token scores via decoder cross-attention weights. Staticness weights are αₜ = σ(γ · (median(δˢᵗᵃᵗᵉ) − δˢᵗᵃᵗᵉ) / IQR(δˢᵗᵃᵗᵉ)), accumulated over time by EMA, and used to gate the state update sₜ = sₜ₋₁ + αₜ ⊙ Δsₜ.

### Stabilization

- **Reset metric alignment**: memory is reset every 50 frames; a Sim(3) transform is estimated via confidence-weighted SVD from the repeated frame's point clouds before/after reset (weighted by the staticness map) and applied to subsequent poses/points.
- **State-aware smoothing**: with state-change signal scₜ (mean ℓ₂ norm of Δsₜ) and trajectory acceleration aₜ, the coefficient βₜ = 1 / (1 + λ|aₜ × scₜ|) filters displacements as d̂ₜ = βₜdₜ + (1 − βₜ)d̂ₜ₋₁.

### Setup

RayMap3R builds on the frozen pre-trained CUT3R backbone with no fine-tuning. All experiments run on a single NVIDIA RTX A6000 48GB GPU; baselines use official implementations with default hyperparameters.

## 📊 Results

RayMap3R targets the streaming (online, ✓) setting. It does not win everywhere: among streaming methods it trails StreamVGGT on per-sequence Sintel depth, trails CUT3R on Sintel rotational RPE, and is beaten by Spann3R on normal consistency; offline methods (✗) such as VGGT remain more accurate but are not viable for long sequences.

### Video Depth Estimation — Per-sequence scale

원논문 Table 1. Abs Rel↓ (lower better), δ<1.25↑ (higher better). ✗ = offline, ✓ = streaming.

| Method     | Onl. | KITTI AbsRel↓ | KITTI δ↑ | BONN AbsRel↓ | BONN δ↑  | Sintel AbsRel↓ | Sintel δ↑ |
| ---------- | ---- | ------------- | -------- | ------------ | -------- | -------------- | --------- |
| DUSt3R     | ✗    | 0.144         | 81.3     | 0.155        | 83.3     | 0.656          | 45.2      |
| MonST3R    | ✗    | 0.168         | 74.4     | 0.067        | 96.3     | 0.378          | 55.8      |
| VGGT       | ✗    | 0.070         | 96.5     | 0.055        | 97.1     | 0.287          | 66.1      |
| Spann3R    | ✓    | 0.198         | 73.7     | 0.144        | 81.3     | 0.622          | 42.6      |
| Point3R    | ✓    | 0.135         | 84.0     | 0.061        | 96.2     | 0.451          | 48.7      |
| StreamVGGT | ✓    | 0.173         | 72.1     | 0.063        | 97.2     | 0.323          | 65.7      |
| CUT3R      | ✓    | 0.118         | 88.1     | 0.078        | 93.7     | 0.421          | 47.9      |
| TTT3R      | ✓    | 0.114         | 90.4     | 0.068        | 95.4     | 0.409          | 48.8      |
| **Ours**   | ✓    | **0.098**     | **92.8** | **0.057**    | **97.4** | 0.401          | 50.9      |

### Video Depth Estimation — Metric scale

원논문 Table 1. Metric-scale absolute depth (no alignment).

| Method   | Onl. | KITTI AbsRel↓ | KITTI δ↑ | BONN AbsRel↓ | BONN δ↑  | Sintel AbsRel↓ | Sintel δ↑ |
| -------- | ---- | ------------- | -------- | ------------ | -------- | -------------- | --------- |
| Point3R  | ✓    | 0.190         | 73.9     | 0.136        | 94.6     | 0.778          | 17.0      |
| CUT3R    | ✓    | 0.122         | 85.5     | 0.103        | 88.5     | 1.029          | 23.8      |
| TTT3R    | ✓    | 0.111         | 88.8     | 0.089        | 94.2     | 0.977          | 23.2      |
| **Ours** | ✓    | **0.104**     | **89.4** | **0.085**    | **94.8** | 0.954          | **24.0**  |

On per-sequence Sintel, StreamVGGT (0.323) achieves lower depth error than Ours (0.401). Under metric scale on Sintel, Point3R obtains lower absolute error (0.778 vs 0.954) but degrades on threshold accuracy (δ 17.0 vs 24.0).

### Camera Pose Estimation

원논문 Table 2. ATE↓, RPEt↓, RPEr↓ under Sim(3) alignment. ✗ = offline, ✓ = streaming.

| Method     | Onl. | Sintel ATE↓ | Sintel RPEt↓ | Sintel RPEr↓ | TUM-dyn ATE↓ | TUM-dyn RPEt↓ | TUM-dyn RPEr↓ | ScanNet ATE↓ | ScanNet RPEt↓ | ScanNet RPEr↓ |
| ---------- | ---- | ----------- | ------------ | ------------ | ------------ | ------------- | ------------- | ------------ | ------------- | ------------- |
| DUSt3R     | ✗    | 0.417       | 0.250        | 5.796        | 0.083        | 0.017         | 3.567         | 0.081        | 0.028         | 0.784         |
| MASt3R     | ✗    | 0.185       | 0.060        | 1.496        | 0.038        | 0.012         | 0.448         | 0.078        | 0.020         | 0.475         |
| MonST3R    | ✗    | 0.111       | 0.044        | 0.869        | 0.098        | 0.019         | 0.935         | 0.077        | 0.018         | 0.529         |
| VGGT       | ✗    | 0.172       | 0.062        | 0.471        | 0.012        | 0.010         | 0.310         | 0.035        | 0.015         | 0.377         |
| Spann3R    | ✓    | 0.329       | 0.110        | 4.471        | 0.056        | 0.021         | 0.591         | 0.096        | 0.023         | 0.661         |
| Point3R    | ✓    | 0.351       | 0.128        | 1.822        | 0.075        | 0.029         | 0.642         | 0.106        | 0.035         | 1.946         |
| StreamVGGT | ✓    | 0.251       | 0.149        | 1.894        | 0.061        | 0.033         | 3.209         | 0.161        | 0.057         | 3.647         |
| CUT3R      | ✓    | 0.208       | 0.072        | 0.636        | 0.031        | 0.009         | 0.303         | 0.098        | 0.022         | 0.600         |
| TTT3R      | ✓    | 0.210       | 0.091        | 0.722        | 0.019        | 0.008         | 0.292         | 0.065        | 0.021         | 0.637         |
| **Ours**   | ✓    | **0.166**   | **0.056**    | 0.720        | **0.018**    | **0.005**     | **0.287**     | **0.064**    | **0.016**     | 0.635         |

Ours leads ATE and translational RPE (RPEt) across all datasets, but on rotational RPE (RPEr) it does not always win among streaming methods — CUT3R attains lower Sintel RPEr (0.636 vs 0.720).

### 3D Reconstruction on 7-Scenes — Accuracy & Completion

원논문 Table 3. Acc↓ / Comp↓, each with Mean / Med. / Min across scenes (200 frames per scene).

| Method     | Onl. | Acc Mean↓ | Acc Med↓  | Acc Min↓  | Comp Mean↓ | Comp Med↓ | Comp Min↓ |
| ---------- | ---- | --------- | --------- | --------- | ---------- | --------- | --------- |
| DUSt3R-GA  | ✗    | 0.146     | 0.077     | 0.052     | 0.181      | 0.067     | 0.042     |
| MASt3R-GA  | ✗    | 0.185     | 0.081     | 0.056     | 0.180      | 0.069     | 0.047     |
| MonST3R-GA | ✗    | 0.248     | 0.185     | 0.142     | 0.266      | 0.167     | 0.121     |
| Spann3R    | ✓    | 0.298     | 0.226     | 0.170     | 0.205      | 0.112     | 0.078     |
| CUT3R      | ✓    | 0.043     | 0.026     | 0.015     | 0.031      | 0.018     | 0.009     |
| TTT3R      | ✓    | 0.027     | 0.024     | 0.012     | 0.023      | 0.017     | **0.005** |
| **Ours**   | ✓    | **0.023** | **0.023** | **0.009** | **0.022**  | **0.016** | 0.007     |

### 3D Reconstruction on 7-Scenes — Normal Consistency & Chamfer

원논문 Table 3. NC↑ / Chamfer↓, each with Mean / Med. / Min across scenes.

| Method     | Onl. | NC Mean↑ | NC Med↑ | NC Min↑ | Chamfer Mean↓ | Chamfer Med↓ | Chamfer Min↓ |
| ---------- | ---- | -------- | ------- | ------- | ------------- | ------------ | ------------ |
| DUSt3R-GA  | ✗    | 0.736    | 0.839   | 0.865   | 0.327         | 0.144        | 0.094        |
| MASt3R-GA  | ✗    | 0.701    | 0.792   | 0.821   | 0.365         | 0.150        | 0.103        |
| MonST3R-GA | ✗    | 0.672    | 0.759   | 0.783   | 0.514         | 0.352        | 0.263        |
| Spann3R    | ✓    | 0.650    | 0.730   | 0.754   | 0.503         | 0.338        | 0.248        |
| CUT3R      | ✓    | 0.621    | 0.618   | 0.523   | 0.027         | 0.025        | 0.013        |
| TTT3R      | ✓    | 0.582    | 0.583   | 0.545   | 0.025         | **0.020**    | 0.011        |
| **Ours**   | ✓    | 0.629    | 0.626   | 0.605   | **0.024**     | 0.021        | **0.008**    |

Among streaming methods, Spann3R attains higher normal consistency (NC), while RayMap3R leads accuracy across all statistics and Chamfer on Mean/Min (TTT3R has lower Chamfer Med. 0.020 vs 0.021).

### Inference Speed and GPU Memory

원논문 Table 4. Memory in GB↓, throughput in FPS↑, measured on ScanNet (RTX A6000 48GB). OOM = out of memory.

| Method  | 50v Mem↓ | 50v FPS↑ | 1000v Mem↓ | 1000v FPS↑ |
| ------- | -------- | -------- | ---------- | ---------- |
| MonST3R | 32.0     | 0.31     | OOM        | OOM        |
| VGGT    | 20.0     | 21.0     | OOM        | OOM        |
| Point3R | 30.0     | 5.0      | OOM        | OOM        |
| CUT3R   | 6.4      | 19.7     | 6.5        | 19.7       |
| TTT3R   | 7.6      | 19.6     | 7.7        | 19.6       |
| Ours    | 9.2      | 13.8     | 9.4        | 13.8       |

RayMap3R keeps memory stable across sequence lengths (9.2 → 9.4 GB) but its dual-branch design lowers throughput to 13.8 FPS versus CUT3R's 19.7 and TTT3R's 19.6.

### Component Ablation

원논문 Table 5. R: dual-branch identification; M: reset metric alignment; S: state-aware smoothing.

| Metric                     | Base  | R     | R+M   | R+S   | Full      |
| -------------------------- | ----- | ----- | ----- | ----- | --------- |
| Camera Pose ATE↓           | 0.114 | 0.113 | 0.110 | 0.084 | **0.081** |
| Video Depth AbsRel↓        | 0.208 | 0.186 | 0.184 | 0.185 | **0.183** |
| 3D Reconstruction Chamfer↓ | 0.322 | 0.245 | 0.213 | 0.196 | **0.170** |

R drives the largest depth and reconstruction gains; S contributes most to trajectory (ATE); M primarily improves Chamfer via reset-boundary scale correction.

### Dynamic Map Evaluation

원논문 Table 6. Evaluation across 108 sequences from three datasets. disc↑ = discrepancy ratio (dynamic vs static; >1 desired), AUC↑ (0.5 = chance), IoU↑ vs GT masks, ρ↑ = Spearman correlation.

| Dataset    | Seq | Frames | Mean disc↑ | Mean AUC↑ | Mean IoU↑ | ρ↑    |
| ---------- | --- | ------ | ---------- | --------- | --------- | ----- |
| MPI Sintel | 19  | 746    | 1.61       | 0.464     | 0.298     | 0.900 |
| DAVIS 2017 | 81  | 5205   | 1.68       | 0.538     | 0.189     | 0.713 |
| TUM RGB-D  | 8   | 680    | 1.88       | 0.560     | 0.206     | 0.643 |
| All        | 108 | 6631   | 1.69       | 0.532     | 0.203     | 0.771 |

disc exceeds 1 on every dataset; AUC exceeds 0.5 on the real-world datasets, with Sintel below chance (0.464) attributed to more heterogeneous motion, yet Sintel achieves the highest ρ (0.900).

### Cross-Dataset Component Ablation

원논문 Table 9. Each task evaluated on a representative full dataset. R / M / S as above.

| Setting | TUM-dyn ATE↓ | TUM-dyn RPEt↓ | KITTI AbsRel↓ | KITTI δ<1.25↑ | 7-Scenes Acc↓ | 7-Scenes Chamfer↓ |
| ------- | ------------ | ------------- | ------------- | ------------- | ------------- | ----------------- |
| Base    | 0.033        | 0.011         | 0.120         | 88.3          | 0.041         | 0.029             |
| +R      | 0.032        | 0.010         | 0.102         | 92.2          | 0.032         | 0.026             |
| +R+M    | 0.031        | 0.008         | 0.100         | 92.5          | 0.028         | 0.025             |
| +R+S    | 0.020        | 0.006         | 0.101         | 92.3          | 0.026         | 0.025             |
| Full    | **0.019**    | **0.005**     | **0.099**     | **92.7**      | **0.023**     | **0.024**         |

## 💡 Insights & Impact

- **Bias-as-signal**: A pretrained RayMap-based streaming model already encodes an implicit static/dynamic distinction; querying with RayMap tokens alone surfaces it, giving a training-free dynamic cue with no flow estimators, segmentation models, or dynamic mask supervision.
- **Filtering at the state level**: Suppressing dynamic content before memory updates prevents corrupted geometry from accumulating, which the paper argues also preserves metric scale consistency across long sequences.
- **Honest trade-offs**: The dual-branch scheme costs throughput (13.8 vs ~19.7 FPS) and slightly more memory, and RayMap3R still trails StreamVGGT on per-sequence Sintel depth, CUT3R on Sintel rotational RPE, and Spann3R on normal consistency.
- **Dependency on backbone training**: The method relies on the backbone having seen dynamic scenes during training (CUT3R Stage 2); if the training distribution lacks dynamic scenes, the static bias — and thus the dual-branch scheme — may be ineffective.
- **Forward-looking**: As RayMap representations spread to offline feed-forward models, the authors suggest analogous biases may enable training-free dynamic reasoning beyond the streaming setting.

## 🔗 Related Work

- **[CUT3R](./cut3r.md)**: The frozen recurrent implicit-memory backbone RayMap3R builds on; the static bias is derived from its RayMap-only predictions.
- **[MonST3R](./monst3r.md)**: Offline dynamic-scene reconstruction baseline (with global alignment) compared throughout.
- **[TTT3R](../reconstruction/ttt3r.md)**: Extends CUT3R with cross-attention soft gating for long-range reconstruction; the closest streaming competitor in the tables.
- **[Point3R](../reconstruction/point3r.md)**: Streaming baseline with explicit spatial pointer memory that grows with sequence length.
- **[StreamVGGT](../reconstruction/streamvggt.md)**: Distills VGGT for streaming prediction; wins per-sequence Sintel depth but its memory scales with frame count.
- **[Spann3R](../reconstruction/spann3r.md)**: Streaming spatial-memory extension of DUSt3R; higher normal consistency but weaker on other geometric metrics.
- **[VGGT](../reconstruction/vggt.md)**: Offline joint pose/geometry transformer used as an accuracy reference (and StreamVGGT's teacher).
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: Pointmap foundations and offline pose/reconstruction baselines.
- **[Fast3R](../reconstruction/fast3r.md)**: Single-forward multi-view reconstruction cited among offline feed-forward methods.

## 📚 Key Takeaways

1. **Training-free dynamic reconstruction**: robustness to moving objects with zero retraining, by exploiting a RayMap static bias on a frozen CUT3R backbone.
2. **Dual-branch staticness gating**: contrasting image vs RayMap-only depth yields per-state-token weights that suppress dynamic interference during memory updates.
3. **Stabilizers matter**: reset metric alignment (Sim(3) at reset boundaries) and state-aware smoothing (online, causal) address complementary trajectory-drift failure modes.
4. **State-of-the-art among streaming methods** on Bonn/KITTI depth, ATE/RPEt pose across Sintel/TUM-dyn/ScanNet, and 7-Scenes accuracy — at the cost of ~13.8 FPS (below CUT3R/TTT3R) and some losing points (Sintel per-sequence depth, Sintel RPEr, normal consistency).

# ArtSplat: Feed-Forward Articulated 3D Gaussian Splatting from Sparse Multi-State Uncalibrated Views (arXiv preprint 2026-05)

![artsplat — method](https://artsplat.github.io/static/images/method.png)

_메소드 개요 (저자 project page)_

## 📋 Overview

- **Authors**: Inseo Lee, Yoonji Kim, Eugene Sohn, Jiwoong Lee, Jungmin You, Joonseok Lee, Jin-Hwa Kim
- **Institution**: Seoul National University; Sogang University; NAVER AI Lab
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.24304) | [Project Page](https://artsplat.github.io)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first feed-forward framework for articulated 3D Gaussian Splatting — from sparse uncalibrated RGB views captured at two or more articulation states, it predicts geometry _and_ joint parameters (type, axis, pivot, angle/displacement) in one forward pass via a per-pixel joint map and Cross-State Attention, running over 400× faster than per-object-optimization baselines.

## 🎯 Key Contributions

1. **First feed-forward articulated 3DGS**: Jointly predicts 3D Gaussians and joint parameters from uncalibrated RGB views, removing per-object test-time optimization.
2. **Per-pixel joint map representation**: An 11-channel dense map (joint-type logits ×3, axis direction ×3, pivot ×3, revolute angle ×1, prismatic displacement ×1) makes the joint head fully differentiable and end-to-end trainable, avoiding non-differentiable segmentation or unstable fixed-slot assignment.
3. **Cross-State Attention (CSA) with state tokens**: A per-state learnable token plus a single CSA block lets each state attend to the other state's patch tokens, capturing discrete, large-magnitude inter-state motion.

## 🔧 Technical Details

### Problem setup

Input is `N = V·S` pose-free RGB images (V sparse views × S articulation states). The model predicts, per image, camera parameters (R⁹), depth + confidence maps, a Gaussian set (means from unprojected depth; scale, rotation, opacity, SH degree L=4 → 86 params/Gaussian), and the 11-channel joint map. A differentiable articulation transform moves each Gaussian by its per-pixel joint parameters (Rodrigues rotation for revolute, translation for prismatic) into any target state for rendering.

### Joint prediction module

- **State tokens** `z0, z1` (dim 2048) prepended to each state's views, inspired by VGGT's camera token.
- **CSA**: state token as query, the _other_ state's patch tokens as keys/values, producing refined summaries `z̃_s`.
- **Invariant/variant DPT head**: a 9-channel invariant branch (type, axis, pivot — shared across states, conditioned on `(z̃0+z̃1)/2`) and a 2-channel variant branch (θ, d — state-specific, conditioned on `z̃_s`), using FiLM modulation after injecting geometry via a pointwise MLP over the point map.
- **Inference articulation**: HDBSCAN clusters Gaussians into parts (Plücker line coordinates for revolute, axis direction for prismatic); per-part axis/pivot/reference-angle are averaged and applied rigidly to reach a target state.

### Architecture and training

- Backbone: 1B-parameter VGGT aggregator initialized from AnySplat pretrained weights, adapted with rank-16 LoRA (α=16) on every attention projection; all other VGGT params frozen. CSA is one block, 16 heads, dim 2048. Joint DPT aggregates backbone layers {4, 11, 17, 23} → 256-channel maps.
- **Two-stage training**: Stage 1 (80k iters) supervises geometry + joint parameters directly (pose, depth, joint, consistency, smoothness losses) with no rendering; Stage 2 (40k iters) adds an RGB rendering loss (MSE + 0.1·LPIPS). Trained on 4 NVIDIA RTX A6000, bf16, ~4 days. Inputs 448×448 (32×32 patches).

## 📊 Results

Benchmark: PartNet-Mobility, 68 held-out objects (18 single-joint, 50 multi-joint). All methods get the same 8 input views (2 states × 4 views), evaluated on 12 target views/state. Metrics — Geometry: Chamfer Distance for static (CD-s), movable (CD-m), whole (CD-w); Motion: axis angular error (Angm, °), axis position error (Posm); Appearance: PSNR, SSIM.

원논문 Table 1 (single-joint split).

| Method       | Prior           | CD-w↓ | CD-s↓ | CD-m↓     | Angm↓    | Posm↓ | PSNR↑     | SSIM↑     |
| ------------ | --------------- | ----- | ----- | --------- | -------- | ----- | --------- | --------- |
| PARIS        | RGB + #joints   | 0.022 | 0.029 | 0.294     | 55.96    | 0.166 | 20.51     | 0.909     |
| DTA          | RGB-D + #joints | 0.004 | 0.008 | 0.145     | 33.79    | 2.305 | 20.23     | 0.822     |
| ArtGS        | RGB-D + #joints | 0.013 | 0.010 | 0.102     | 64.67    | 1.165 | 28.01     | 0.924     |
| ReArtGS      | RGB + #joints   | 0.045 | 0.129 | 0.443     | 47.87    | 1.993 | 23.44     | 0.865     |
| ScrewSplat   | RGB             | 0.036 | 0.039 | 0.301     | 26.27    | 2.401 | 22.93     | 0.918     |
| **ArtSplat** | RGB             | 0.031 | 0.023 | **0.028** | **6.65** | 0.436 | **28.70** | **0.941** |

원논문 Table 1 (multi-joint split).

| Method       | Prior           | CD-w↓ | CD-s↓ | CD-m↓     | Angm↓    | Posm↓  | PSNR↑     | SSIM↑     |
| ------------ | --------------- | ----- | ----- | --------- | -------- | ------ | --------- | --------- |
| PARIS        | RGB + #joints   | 0.017 | 0.029 | 0.335     | 53.08    | 0.221  | 20.03     | 0.913     |
| DTA          | RGB-D + #joints | 0.025 | 0.053 | 0.527     | 44.48    | 22.790 | 19.56     | 0.813     |
| ArtGS        | RGB-D + #joints | 0.096 | 0.102 | 0.782     | 49.31    | 1.825  | 25.21     | 0.893     |
| ScrewSplat   | RGB             | 0.035 | 0.044 | 0.405     | 46.78    | 3.368  | 23.49     | 0.912     |
| **ArtSplat** | RGB             | 0.034 | 0.024 | **0.030** | **5.79** | 0.864  | **26.30** | **0.921** |

ArtSplat wins CD-m (movable-part reconstruction), motion angular error, PSNR, and SSIM on both splits, though on single-joint CD-w/CD-s the RGB-D method DTA is lower (0.004 / 0.008 vs 0.031 / 0.023). Among RGB-only methods it is best on all three Chamfer metrics. Most baselines report axis angular errors above 30° regardless of prior, while ArtSplat stays at 6.65° / 5.79°.

### Inference speed

원논문 Table 2. ArtSplat reconstructs each object in under 2 seconds — over 400× faster than the baselines and ~700× faster than ScrewSplat (the other RGB-only method).

| Type                    | Method       | Prior           | Time per object↓ |
| ----------------------- | ------------ | --------------- | ---------------- |
| per-object optimization | PARIS        | RGB + #joints   | 12m 57s          |
| per-object optimization | DTA          | RGB-D + #joints | 56m 07s          |
| per-object optimization | ArtGS        | RGB-D + #joints | 15m 50s          |
| per-object optimization | REArtGS      | RGB + #joints   | 1h 37m           |
| per-object optimization | ScrewSplat   | RGB             | 23m 05s          |
| feed-forward            | **ArtSplat** | RGB             | **<2s**          |

### Ablation (multi-joint split)

원논문 Table 3.

| Method                            | CD-w↓ | CD-s↓ | CD-m↓ | Angm↓ | Posm↓ | PSNR↑ | SSIM↑ |
| --------------------------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| ArtSplat (full)                   | 0.034 | 0.024 | 0.030 | 5.79  | 0.864 | 26.30 | 0.921 |
| w/o cross-state attention         | 0.067 | 0.029 | 0.082 | 18.74 | 1.852 | 24.18 | 0.901 |
| w/o state token conditioning      | 0.112 | 0.041 | 0.156 | 31.46 | 2.917 | 22.51 | 0.879 |
| w/o Inv/Var split (single branch) | 0.042 | 0.026 | 0.041 | 7.12  | 1.643 | 25.07 | 0.913 |
| Single-stage joint training       | 0.058 | 0.030 | 0.069 | 12.85 | 1.428 | 23.74 | 0.895 |

Removing the state token (and CSA) is the most damaging (Angm 5.79° → 31.46°), confirming that cross-state comparison drives axis/angle estimation; the two-stage schedule matters because a rendering loss through still-noisy joint predictions destabilizes training.

## 💡 Insights & Impact

- Articulated objects fit neither the static nor the dynamic feed-forward setting: views are unordered yet contain large discrete part motion. Framing articulation as per-pixel regression on top of a VGGT backbone integrates it cleanly into a single forward pass.
- Making the invariant/variant distinction _structural_ (two DPT branches) rather than learned improves variant (angle/displacement) predictions without hurting invariant ones.
- **Limitations (authors)**: handles only single-degree-of-freedom joints attached to a static base (not serial kinematic chains); mesh fidelity suffers from unstructured Gaussians; and when the articulation change between the two observed states is small, joint-axis prediction can deviate significantly. Validation is on synthetic PartNet-Mobility, not real captures.

## 🔗 Related Work

- Extends the static feed-forward geometry line — [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [Fast3R](../reconstruction/fast3r.md), FLARE, and specifically [VGGT](../reconstruction/vggt.md) (backbone) initialized from AnySplat.
- Contrasts with dynamic-scene models such as [MonST3R](../dynamic/monst3r.md) that assume dense temporal correspondence.
- Related feed-forward Gaussian splatting: [Splatt3R](splatt3r.md); closest articulated feed-forward prior work is ART and LARM (pose-conditioned).

## 📚 Key Takeaways

1. A per-pixel 11-channel joint map lets articulation be regressed differentiably alongside depth and Gaussian heads, avoiding fixed part slots and non-differentiable segmentation.
2. Cross-State Attention over state tokens is the component that recovers accurate joint axes (angular error ~6° vs >30° for baselines), and it does not degrade as joint count grows.
3. Producing all Gaussians and joints in one forward pass yields <2s reconstruction (>400× faster) while matching or beating per-object-optimization baselines on movable-part geometry and appearance — with the honest caveat that RGB-D DTA still edges it on whole/static Chamfer distance for single-joint objects.

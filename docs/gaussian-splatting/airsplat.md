# AirSplat: Alignment and Rating for Robust Feed-Forward 3D Gaussian Splatting (arXiv preprint 2026-03)

![airsplat — architecture](https://arxiv.org/html/2603.25129v1/figures/main_architecture.png)

_Overview of our AirSplat training pipeline (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Minh-Quan Viet Bui, Jaeho Moon, Munchurl Kim (Bui and Moon are co-first authors, equal contribution)
- **Institution**: KAIST
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.25129) | [Project Page](https://kaist-viclab.github.io/airsplat-site)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-only framework that adapts 3D Vision Foundation Models with view-synthesis heads (3D-VS-VFMs, e.g. DepthAnything3) into high-fidelity pose-free NVS via Self-Consistent Pose Alignment (SCPA) to fix pose-geometry drift and Rating-based Opacity Matching (ROM) to prune floaters — with zero extra cost at inference.

## 🎯 Key Contributions

1. **Framework for adapting 3D-VS-VFMs**: Fine-tunes only the Gaussian prediction head of a frozen 3DVFM (encoder + depth/pose heads frozen) so high-fidelity NVS is gained while foundational geometry-estimation performance is preserved.
2. **Self-Consistent Pose Alignment (SCPA)**: A training-time feedback loop that re-estimates the target pose from a rendered proxy image, measures the systematic drift as an se(3) vector, and applies an inverse correction so photometric supervision is applied on geometrically consistent renderings.
3. **Rating-based Opacity Matching (ROM)**: Uses a lightweight sparse-view 3DGS "teacher oracle" to rate each primitive's multi-view geometric consistency; the rating is matched to the primitive's opacity via a one-sided margin loss, driving floaters' opacity toward zero.

## 🔧 Technical Details

### Problem: two obstacles in 3D-VS-VFMs

- **Pose-geometry discrepancy**: In the context-target training strategy, target poses are inferred from both context and target images while geometry is conditioned only on context views. This asymmetric information flow induces a latent coordinate misalignment, so a pixel-wise reconstruction loss yields corrupted gradients.
- **Multi-view inconsistency**: Primitives from different context views lack spatial consensus, producing "floaters".

### SCPA

Given the primitives `G` from context views and an initial target pose `P̂_tgt^(1)`, the model renders an initial image, feeds it back to obtain a second pose `P̂_tgt^(2)`, computes the relative transform `ξ_t = log(P̂^(2)(P̂^(1))^-1)` in se(3), then back-extrapolates by negating `ξ_t` and mapping back through the exponential map to get the aligned pose. A minimum-error supervision picks the smaller reconstruction loss between the aligned and initial renderings. `L_rec` is MSE + λ·LPIPS.

### ROM

A scale-normalized geometric error `ε_i` measures how far a primitive's mean drifts when projected to an adjacent context view. Comparing against a two-view teacher's error gives an excess error `E_i^geo`, converted to a continuous rating `ỹ_i = exp(−λ·E_i^geo)` with decay λ = 5.0. A one-sided margin loss `L_opa = mean(max(0, α_i − ỹ_i))²` treats the teacher rating as an upper bound on opacity, plus a spatial regularizer `L_geo` (error clamped at τ = 2.0, weighted by detached opacity). Total loss: `L_total = L_scpa + λ_geo·L_geo + λ_opa·L_opa`.

### Implementation

- Baseline / backbone: DA3-GIANT (DepthAnything3). Only the Gaussian head is trained.
- Trained on 252×252 (RE10K) and 252×448 (DL3DV) images; 24 context views + 8 target views per iteration; 4× NVIDIA A100 40GB, batch 1/GPU, 100,000 iterations (~4.5 days). Testing on a single A100 40GB.
- Hyperparameters (supplementary): AdamW lr 2×10⁻⁶, weight decay 0.01, OneCycleLR with 2,000-step warm-up; λ_geo = 0.1, λ_opa = 1.0, λ_s (LPIPS) = 0.1.

## 📊 Results

Metrics: PSNR↑, SSIM↑, LPIPS↓. OOM = out-of-memory inference.

원논문 Table 1 (RE10K, pose-free vs pose-required).

| Method       | 12V PSNR↑ | SSIM↑     | LPIPS↓    | 24V PSNR↑ | SSIM↑     | LPIPS↓    | 36V PSNR↑ | SSIM↑     | LPIPS↓    |
| ------------ | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| MonoSplat    | 18.16     | 0.663     | 0.336     | 16.66     | 0.593     | 0.391     | 15.79     | 0.551     | 0.424     |
| MVSplat      | 17.98     | 0.638     | 0.357     | 17.27     | 0.609     | 0.379     | OOM       | OOM       | OOM       |
| DepthSplat   | 22.56     | 0.793     | 0.200     | 21.00     | 0.734     | 0.248     | 19.60     | 0.676     | 0.296     |
| NoPoSplat    | 17.15     | 0.571     | 0.437     | 17.10     | 0.570     | 0.443     | 17.09     | 0.570     | 0.446     |
| AnySplat     | 18.69     | 0.591     | 0.273     | 19.15     | 0.610     | 0.257     | 19.31     | 0.615     | 0.251     |
| WorldMirror  | 21.23     | 0.707     | 0.267     | 21.08     | 0.701     | 0.274     | 20.98     | 0.699     | 0.275     |
| SPFSplat     | 21.57     | 0.701     | 0.254     | 21.32     | 0.694     | 0.266     | 21.17     | 0.689     | 0.273     |
| YoNoSplat    | 21.62     | 0.679     | 0.229     | 21.63     | 0.679     | 0.227     | 21.60     | 0.681     | 0.226     |
| DA3          | 20.78     | 0.715     | 0.250     | 21.06     | 0.710     | 0.254     | 21.11     | 0.684     | 0.274     |
| **AirSplat** | **23.08** | **0.799** | **0.190** | **23.77** | **0.814** | **0.178** | **23.94** | **0.815** | **0.179** |

MonoSplat, MVSplat, DepthSplat are pose-required; the rest are pose-free. On DL3DV (12 views) AirSplat beats its DA3 baseline by +1.76 dB PSNR (20.74 → 22.50) and reduces LPIPS by 14.4% (원논문 Table 2). On zero-shot cross-dataset ACID (16/20/24 views) AirSplat reaches 25.96 / 26.21 / 26.42 dB PSNR, above SPFSplat's 24.58 / 24.49 / 24.40 (원논문 Table 3).

### Ablation (RE10K, 12 views)

원논문 Table 4.

| Method                             | PSNR↑     | SSIM↑     | LPIPS↓    |
| ---------------------------------- | --------- | --------- | --------- |
| Baseline (DA3)                     | 20.78     | 0.715     | 0.250     |
| Baseline + Context-only Training   | 21.27     | 0.745     | 0.253     |
| Baseline + Context-Target Training | 21.63     | 0.761     | 0.241     |
| Baseline + Context-Target w/ SCPA  | 22.60     | 0.776     | 0.215     |
| Baseline + ROM                     | 22.41     | 0.769     | 0.211     |
| **Ours (Full)**                    | **23.08** | **0.799** | **0.190** |

SCPA adds +0.97 dB over naive context-target training; ROM independently lifts the baseline to 22.41 dB. The same trends hold on a DL3DV ablation (원논문 Table 5).

### Geometry preservation (7-Scenes point map)

원논문 Table 6. Because only the Gaussian head is trained, DA3 and AirSplat share identical geometry outputs; unlike AnySplat, which degrades its VGGT backbone's zero-shot priors.

| Method       | View   | Acc. Mean↓ | Acc. Med.↓ | Comp. Mean↓ | Comp. Med.↓ | NC. Mean↑ | NC. Med.↑ |
| ------------ | ------ | ---------- | ---------- | ----------- | ----------- | --------- | --------- |
| VGGT         | sparse | 0.044      | 0.025      | 0.056       | 0.033       | 0.733     | 0.845     |
| AnySplat     | sparse | 0.080      | 0.053      | 0.120       | 0.072       | 0.684     | 0.785     |
| π³           | sparse | 0.047      | 0.029      | 0.075       | 0.049       | 0.742     | 0.841     |
| DA3/AirSplat | sparse | 0.049      | 0.034      | 0.065       | 0.046       | 0.757     | 0.866     |
| VGGT         | dense  | 0.022      | 0.008      | 0.026       | 0.012       | 0.666     | 0.760     |
| AnySplat     | dense  | 0.040      | 0.015      | 0.030       | 0.011       | 0.648     | 0.732     |
| π³           | dense  | 0.016      | 0.007      | 0.022       | 0.011       | 0.689     | 0.792     |
| DA3/AirSplat | dense  | 0.018      | 0.007      | 0.023       | 0.009       | 0.688     | 0.795     |

### Training overhead

원논문 Table 7. SCPA + ROM raise time per training iteration by ~65% (2.35 → 3.89 s/iter for the full model), but add zero cost at inference.

| Method                            | Avg. Time (s) / Iter. |
| --------------------------------- | --------------------- |
| Baseline + Context-Target         | 2.35                  |
| Baseline + Context-Target w/ SCPA | 3.67                  |
| Ours (Full Model)                 | 3.89                  |

## 💡 Insights & Impact

- The pose-geometry discrepancy is systematic and predictable: recursively re-rendering and re-posing produces a consistent drift trajectory, which is exactly what lets SCPA recover the aligned pose from just two pose predictions. The paper shows this drift across multiple architectures (DA3, SPFSplat) and datasets.
- Formulating a primitive's "rating" directly as its opacity makes artifact pruning fall out of the feedback-matching objective; one-sided matching (upper bound, not exact target) avoids "solidification" artifacts that would destroy volumetric blending.
- **Limitation (authors)**: As a deterministic feed-forward model, AirSplat cannot hallucinate unseen structures, so severe occlusions or uncaptured regions appear as structural voids; the authors suggest generative video-diffusion inpainting as future work.

## 🔗 Related Work

- Builds on 3DVFMs: [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [VGGT](../reconstruction/vggt.md), and π³ ([Pi3](../reconstruction/pi3.md)); the baseline is a view-synthesis-head variant (DepthAnything3, [Depth-Anything-3](../reconstruction/depth-anything-3.md); [WorldMirror](../reconstruction/worldmirror.md)).
- Compared against pose-free feed-forward NVS: NoPoSplat, AnySplat, SPFSplat, YoNoSplat ([YoNoSplat](yonosplat.md)), and pose-required MVSplat / DepthSplat / MonoSplat.

## 📚 Key Takeaways

1. High-fidelity pose-free NVS from a 3D-VS-VFM is bottlenecked not by the backbone's geometry but by pose-geometry drift and floaters during Gaussian-head training.
2. SCPA converts the drift into a measurable, invertible se(3) correction; ROM converts multi-view inconsistency into an opacity-pruning signal from a cheap teacher.
3. Training only the Gaussian head keeps the foundation model's geometry intact (identical 7-Scenes metrics to DA3) while pushing NVS to state of the art among pose-free methods, at no inference-time cost.

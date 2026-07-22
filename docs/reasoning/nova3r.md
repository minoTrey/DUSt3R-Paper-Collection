# NOVA3R: Non-Pixel-Aligned Visual Transformer for Amodal 3D Reconstruction (ICLR 2026)

![nova3r — architecture](https://arxiv.org/html/2603.04179v2/x3.png)

_Overview of NOVA3R (원논문 Fig. 3)_

## 📋 Overview

- **Authors**: Weirong Chen, Chuanxia Zheng, Ganlin Zhang, Andrea Vedaldi, Daniel Cremers
- **Institution**: Technical University of Munich, Munich Center for Machine Learning, University of Oxford, Nanyang Technological University
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.04179) | [Project Page](https://wrchen530.github.io/nova3r)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Replaces per-ray pixel-aligned prediction with a fixed set of learnable scene tokens decoded by a flow-matching 3D decoder, producing complete (visible + occluded) point clouds without holes or duplicated surfaces from unposed images.

## 🎯 Key Contributions

1. **Non-pixel-aligned formulation**: geometry is decoded from a global, view-agnostic scene representation rather than tied to per-pixel rays, decoupling reconstruction from pixel alignment.
2. **Amodal completeness**: because points are not bound to rays, occluded and unseen regions are recovered alongside visible surfaces.
3. **Physical plausibility**: fusing evidence in 3D rather than along camera rays eliminates the duplicated points and multi-layer artifacts that pixel-aligned methods accumulate in co-visible regions.
4. **Scene-token mechanism**: `M` learnable global tokens aggregate information across unposed images inside a VGGT-style transformer.
5. **Diffusion/flow-matching 3D decoder** that predicts point coordinates directly, avoiding occupancy or SDF supervision that is infeasible for real scene-level data.
6. **Unified across scenes and objects**: the same formulation is trained for scene completion and object completion.

## 🔧 Technical Details

### Stage 1 — diffusion-based 3D autoencoder

The encoder `Φ_enc` maps a point cloud `P ∈ R^{N×3}` to `M` latent tokens `Z ∈ R^{M×C}`. Initial query points are drawn by farthest point sampling with `M ≪ N`, then a **hybrid query representation** concatenates the point query with learnable tokens of the same length along the channel dimension, followed by a linear projection from `2C` back to `C`.

Rather than a deterministic occupancy or SDF decoder, `Φ_dec(x_t, Z, t)` is a flow-matching decoder over `N` noised query points `x_t = (1−t)x_0 + tε`, trained with

```text
L_flow^AE = E_{t, x_0~P, ε~U(−1,1)} [ ‖ Φ_dec(x_t, Z, t) − (ε − x_0) ‖²₂ ]
```

The rationale is stated plainly: ground-truth occupancy or SDF for real scene-level datasets is costly or infeasible, and scenes lack the well-defined boundaries that let objects be enclosed in a canonical space. No KL loss or other latent regularization is used.

**Architecture**: encoder built on TripoSG — one cross-attention layer plus eight self-attention layers. Decoder has three transformer blocks, with the query alternating between the latent tokens `Z` and the noisy point cloud `x_t` in each cross-attention layer. This keeps self-attention maps small while preserving information flow.

### Stage 2 — scene tokens from unposed images

`L` patchified image tokens `t_I` from all `K` views are concatenated with `M` learnable global scene tokens `t_S ∈ R^{M×C}` and fed through a large transformer with frame-level and global-level self-attention. The scene tokens are treated as a global frame under the first view's coordinate system — they undergo the same operations as image tokens in each block, except they use the first view's camera token.

The image encoder is architecturally identical to VGGT, but **its dense prediction heads are discarded**. The output scene tokens `Ẑ` condition the frozen Stage-1 decoder to predict the non-pixel-aligned complete point cloud `P̂ ∈ R^{N×3}`, trained with the same flow-matching loss. Only the transformer and scene tokens are optimized in Stage 2.

### Implementation

`M = 768` scene tokens, `N = 10,000` points for training. 50 epochs in Stage 1, 50 in Stage 2 with the image encoder initialized from VGGT pretrained weights and the decoder from Stage 1. AdamW at learning rate 3e-4, 4 NVIDIA A40 GPUs, total batch size 32. Cosine noise scheduling, timestep sampling in [0,1], fixed 0.04 step size at inference.

Scene training uses 3D-FRONT and ScanNet++V2 (100 k and 230 k unique images via the LaRI and DUSt3R splits), plus ARKitScenes for visible-part training. Training is on 1–2 input views due to compute limits.

## 📊 Results

### Scene completion on SCRREAM (zero-shot)

원논문 Table 1. `K` is the number of input views. Since NOVA3R does not distinguish visible from occluded points, its Visible column uses one-sided Chamfer Distance (GT → Prediction), shown in parentheses.

| Type        | Method      | Complete (K=1) CD ↓ | Complete (K=1) FS@0.1 ↑ | Complete (K=1) FS@0.05 ↑ | Complete (K=2) CD ↓ | Complete (K=2) FS@0.1 ↑ | Complete (K=2) FS@0.05 ↑ |
| ----------- | ----------- | ------------------- | ----------------------- | ------------------------ | ------------------- | ----------------------- | ------------------------ |
| Single-view | Metric3D-v2 | 0.086               | 0.725                   | 0.473                    | -                   | -                       | -                        |
| Single-view | DepthPro    | 0.079               | 0.764                   | 0.535                    | -                   | -                       | -                        |
| Single-view | MoGe        | 0.063               | 0.836                   | 0.668                    | -                   | -                       | -                        |
| Single-view | LaRI        | 0.059               | 0.825                   | 0.590                    | -                   | -                       | -                        |
| Multi-view  | DUSt3R      | 0.086               | 0.757                   | 0.565                    | 0.061               | 0.833                   | 0.641                    |
| Multi-view  | CUT3R       | 0.091               | 0.753                   | 0.543                    | 0.092               | 0.739                   | 0.532                    |
| Multi-view  | VGGT        | 0.070               | 0.810                   | 0.657                    | 0.065               | 0.821                   | 0.606                    |
| Multi-view  | **NOVA3R**  | **0.048**           | **0.882**               | **0.687**                | **0.053**           | **0.862**               | **0.657**                |

원논문 Table 1, visible-region columns (NOVA3R's values are one-sided CD, in parentheses in the original).

| Method     | Visible (K=1) CD ↓ | Visible (K=1) FS@0.1 ↑ | Visible (K=1) FS@0.05 ↑ |
| ---------- | ------------------ | ---------------------- | ----------------------- |
| MoGe       | **0.035**          | **0.945**              | **0.786**               |
| LaRI       | 0.057              | 0.847                  | 0.589                   |
| DUSt3R     | 0.059              | 0.851                  | 0.653                   |
| CUT3R      | 0.069              | 0.835                  | 0.679                   |
| VGGT       | 0.041              | 0.923                  | 0.754                   |
| **NOVA3R** | (0.043)            | (0.904)                | (0.730)                 |

On visible-only reconstruction NOVA3R is competitive but not leading — MoGe and VGGT are ahead. The gains are concentrated in the complete setting, which is what the method targets.

### Hole ratio and density variance

원논문 Table 2. K=4 is an unseen setting — the model was trained on 1–2 views.

| Method     | K=1 Hole Ratio ↓ | K=1 Density Var. ↓ | K=2 Hole Ratio ↓ | K=2 Density Var. ↓ | K=4 Hole Ratio ↓ | K=4 Density Var. ↓ |
| ---------- | ---------------- | ------------------ | ---------------- | ------------------ | ---------------- | ------------------ |
| DUSt3R     | 0.317            | 7.758              | 0.237            | 6.553              | 0.257            | 4.801              |
| CUT3R      | 0.363            | 8.402              | 0.237            | 6.554              | 0.326            | 4.658              |
| VGGT       | 0.307            | 7.105              | 0.238            | 6.546              | 0.261            | 5.217              |
| **NOVA3R** | **0.088**        | **5.127**          | **0.121**        | **2.188**          | **0.134**        | **1.881**          |

Density variance decreases monotonically from one to four input views for NOVA3R, which the authors read as evidence that more views improve spatial uniformity rather than piling up duplicate layers.

### Visible reconstruction on 7-Scenes

원논문 Table 3, K=2. `# Tokens` is the token count used to represent a 3D scene.

| Method   | # Tokens | Acc Mean ↓ | Acc Med. ↓ | Comp Mean ↓ | Comp Med. ↓ | NC Mean ↑ | NC Med. ↑ |
| -------- | -------- | ---------- | ---------- | ----------- | ----------- | --------- | --------- |
| DUSt3R   | 2048     | 0.054      | 0.023      | 0.075       | 0.034       | 0.772     | 0.901     |
| Spann3R  | 784      | 0.044      | 0.022      | 0.046       | 0.025       | 0.792     | 0.922     |
| CUT3R    | 768      | 0.043      | 0.023      | 0.054       | 0.028       | 0.760     | 0.884     |
| VGGT     | 2738     | 0.042      | **0.020**  | 0.045       | 0.025       | **0.813** | **0.923** |
| **Ours** | 768      | **0.041**  | 0.021      | **0.033**   | **0.019**   | 0.794     | 0.917     |

NOVA3R leads on accuracy mean and both completion metrics with 768 tokens against VGGT's 2738, but VGGT retains the lead on normal consistency and accuracy median.

### Object completion on GSO

원논문 Table 4. Single-view uses the 1030-object split from LaRI; two-view fixes image 0 and samples three additional views (3090 pairs).

| Type        | Method   | K=1 CD ↓  | K=1 FS@0.1 ↑ | K=1 FS@0.05 ↑ | K=2 CD ↓  | K=2 FS@0.1 ↑ | K=2 FS@0.05 ↑ |
| ----------- | -------- | --------- | ------------ | ------------- | --------- | ------------ | ------------- |
| Single-view | SF3D     | 0.037     | 0.913        | 0.738         | -         | -            | -             |
| Single-view | SPAR3D   | 0.038     | 0.912        | 0.745         | -         | -            | -             |
| Single-view | LaRI     | 0.025     | 0.966        | 0.894         | -         | -            | -             |
| Single-view | TripoSG  | 0.025     | 0.961        | 0.899         | -         | -            | -             |
| Multi-view  | TRELLIS  | 0.025     | 0.962        | 0.896         | 0.028     | 0.946        | 0.874         |
| Multi-view  | **Ours** | **0.020** | **0.985**    | **0.925**     | **0.023** | **0.978**    | **0.903**     |

### Ablations

원논문 Table 5. All on SCRREAM complete (K=1).

| Metric    | Point (S1) | Learnable (S1) | Hybrid (S1) | 256 tok. | 512 tok. | 768 tok.  | Indep. FM | Joint FM  | Res. 224 | Res. 518  |
| --------- | ---------- | -------------- | ----------- | -------- | -------- | --------- | --------- | --------- | -------- | --------- |
| CD ↓      | 0.011      | 0.013          | **0.011**   | 0.014    | 0.013    | **0.011** | 0.012     | **0.011** | 0.054    | **0.048** |
| FS@0.1 ↑  | 0.999      | 0.998          | **0.999**   | 0.996    | 0.998    | **0.999** | 0.998     | **0.999** | 0.861    | **0.882** |
| FS@0.05 ↑ | 0.991      | 0.981          | **0.993**   | 0.975    | 0.986    | **0.993** | 0.990     | **0.993** | 0.648    | **0.687** |
| FS@0.02 ↑ | 0.894      | 0.841          | **0.904**   | 0.811    | 0.839    | **0.904** | 0.889     | **0.904** | 0.327    | **0.350** |

The hybrid query separates from the pure-point variant only at the tightest threshold (FS@0.02: 0.904 vs 0.894); scene-token count and image resolution have much larger effects.

원논문 Table 6. Flow matching vs Chamfer distance as the Stage-1 training loss.

| Training Loss    | CD ↓      | FS@0.1 ↑  | FS@0.05 ↑ | FS@0.02 ↑ | Inference Time (s) ↓ |
| ---------------- | --------- | --------- | --------- | --------- | -------------------- |
| Chamfer distance | 0.024     | 0.981     | 0.907     | 0.575     | **0.557**            |
| Flow-matching    | **0.011** | **0.999** | **0.993** | **0.904** | 2.985                |

Flow matching wins decisively on quality but costs roughly 5× the decoder inference time. The authors attribute Chamfer's failure to its nearest-neighbour formulation being expensive, density-sensitive, and unable to capture global structure across varying scales.

## 💡 Insights & Impact

### Pixel alignment is a bug, not a feature, for complete reconstruction

Every method in the DUSt3R lineage predicts one 3D point per pixel per view. That constraint has two consequences the paper makes measurable: it can never predict anything a ray does not hit (hole ratio 0.307–0.363 for the pixel-aligned baselines vs 0.088 for NOVA3R at K=1), and it emits `K` points for every surface seen from `K` views (density variance 7.1–8.4 vs 5.1). Decoupling from rays fixes both at once.

### Token efficiency as a side effect

NOVA3R represents a whole scene in 768 tokens and still beats VGGT's 2738 tokens on 7-Scenes accuracy and completion. A global, view-agnostic representation does not have to scale with the number of input pixels.

### Flow matching as the enabler

The critical design choice is refusing occupancy/SDF supervision. Real scene datasets cannot supply it, and scenes have no canonical bounding volume. Predicting coordinates directly via flow matching sidesteps both problems — and Table 6 shows the alternative (Chamfer distance on unordered points) simply does not work at scene level.

### Stated limitations

The authors are candid: compute constraints forced a small token count, a small point count, and at most 2 training views, so quality may degrade on large complex scenes. The model handles static scenes only, with no dynamic objects or temporal consistency. And the flow-matching decoder is ~5× slower than a Chamfer-trained one.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — supplies the image encoder architecture and pretrained weights; its dense prediction heads are the thing NOVA3R removes.
- [DUSt3R](../foundation/dust3r.md) — the pixel-aligned paradigm NOVA3R argues against, and a baseline in Tables 1–3.
- [CUT3R](../dynamic/cut3r.md) — pixel-aligned streaming baseline in Tables 1–3.
- [LaRI](../reasoning/lari.md) — the concurrent amodal/layered-ray reconstruction work NOVA3R follows for evaluation protocol and compares against directly.
- [Spann3R](../reconstruction/spann3r.md) — token-efficient baseline in the 7-Scenes comparison.
- [MoGe](../reconstruction/moge.md) — single-view baseline, still the leader on visible-surface metrics.
- [Amodal3R](../reasoning/amodal3r.md) — related amodal 3D reasoning work in this collection.

## 📚 Key Takeaways

1. **Hole ratio drops from 0.307 (VGGT) to 0.088** at K=1 on SCRREAM — the single clearest quantification of what pixel alignment costs (원논문 Table 2).
2. **768 scene tokens beat VGGT's 2738** on 7-Scenes accuracy mean and both completion metrics (원논문 Table 3).
3. **The gain is in completion, not visible surfaces** — MoGe and VGGT still lead the visible-only columns of Table 1, which the paper reports openly.
4. **Flow matching is load-bearing**: replacing it with Chamfer distance drops FS@0.02 from 0.904 to 0.575, at the cost of ~5× decoder inference time (원논문 Table 6).
5. **Density variance falls as views increase** (5.127 → 2.188 → 1.881 for K = 1, 2, 4), the opposite of the duplication behaviour of ray-conditioned methods — and it generalizes to K=4 despite training on at most 2 views.

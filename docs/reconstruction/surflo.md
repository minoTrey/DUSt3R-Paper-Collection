# Surflo: Consistent 3D Surface Flow Model with Global State (arXiv preprint (2026-06))

![surflo — architecture](https://arxiv.org/html/2606.13644v1/x1.png)

_Surflo turns a handful of unposed RGB views into a detailed 3D surface (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Antoine Guédon, Shu Nakamura, Nicolas Dufour, Jiahui Lei, Ko Nishino, Angjoo Kanazawa
- **Institution**: LIX, École polytechnique; Kyoto University; Kyutai; UC Berkeley
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.13644) | [Project Page](https://anttwo.github.io/surflo)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward reconstruction model that compresses a variable number of unposed RGB views into a single fixed-size latent (global state) and decodes an arbitrary number of oriented surface points by independently transporting them from noise via flow matching, with an inference-time rendering guidance term to correlate nearby points.

## 🎯 Key Contributions

1. **Global-state encoder**: A frozen VGGT backbone plus a Perceiver-style compressor distills a variable number of unposed views into K = 128 latent tokens, a single global state independent of view count.
2. **Arbitrary-resolution flow decoder**: A flow-matching decoder transports oriented query points in R³ × S² independently, so the same latent yields from a few thousand to a million points in one batched pass.
3. **Communication via guidance**: An inference-time guidance term injects the gradient of a differentiable-rendering (photometric + depth) loss into the ODE integration (for t ≥ 0.95), correlating nearby points and aligning the surface with input images.
4. **Meshed DL3DV dataset**: As an auxiliary contribution, ~10.5K DL3DV scenes enriched with watertight meshes and ~10⁷ oriented points via Gaussian Wrapping — the first real scene-level watertight mesh dataset at this scale.

## 🔧 Technical Details

### Encoder

For each view, VGGT produces patch tokens (concatenated from layers ℓ ∈ {4, 11, 17, 23}) plus a camera token, augmented with a 3D Fourier positional encoding read off VGGT pointmaps. A Perceiver compressor with K learned queries cross-attends to all position-encoded patch tokens (Ls = 4 self-attention blocks per cross-attention, iterated Le times) to a latent z ∈ R^{K×D}; camera tokens are similarly compressed to a single token.

### Flow-Matching Decoder

Each query x_t ∈ R³ × S² is transported by a velocity predicted through cross-attention to the latent plus an MLP, conditioned on time and camera token via Ada-LN. Training uses the standard flow-matching loss over independent query points. The source distribution is a mixture of Gaussians centered on perturbed VGGT pointmap samples (not pure Gaussian) to concentrate flow near geometry while covering occluded regions.

### Guidance

Near the end of integration (t ≥ 0.95), predicted target points are rendered as oriented Gaussians through VGGT-recovered cameras, and M gradient steps on a Gaussian-Wrapping-style rendering loss (ℓ1 + DSSIM + depth regularization) couple the points; an optional monocular-depth expert further sharpens geometry.

### Setup

Frozen VGGT-1B backbone, K = 128 tokens of D = 512, F = 512 Fourier frequencies; 12-layer decoder cross-attending for the first 6 layers. Trained with AdamW, batch size 12 scenes, 8K query points/scene/step, on 4× H100 GPUs for 400K iterations. Inference: Euler ODE solver with 150 steps, 100K points by default, guidance from t = 0.95 with M = 32 loss updates/step. Metrics: Chamfer Distance (CD↓) and F1 (F1↑) at 1% of scene diagonal.

## 📊 Results

Evaluated from a fixed set of 16 unposed input views per scene. Per-view pointmap variants (greyed in source) are reported for reference only and excluded from ranking.

### Native Surface Ground Truth

원논문 Table 2. CD lower is better, F1 higher is better.

| Method                 | ML-Hypersim CD↓ | F1↑       | BlendedMVS CD↓ | F1↑       | DTU CD↓    | F1↑       | SCRREAM CD↓ | F1↑       |
| ---------------------- | --------------- | --------- | -------------- | --------- | ---------- | --------- | ----------- | --------- |
| NOVA3R                 | 0.0635          | 27.65     | 0.0413         | 32.13     | 0.0307     | 31.41     | 0.0771      | 27.41     |
| 2DGS                   | 0.0176          | 62.03     | 0.0295         | 48.19     | 0.0394     | 28.78     | 0.0234      | 53.57     |
| RaDe-GS                | 0.0174          | 62.68     | 0.0303         | 48.85     | 0.0393     | 28.30     | 0.0242      | 53.52     |
| Gaussian Wrapping      | 0.0145          | 66.86     | 0.0259         | 55.64     | 0.0460     | 30.17     | 0.0123      | 62.96     |
| Surflo — No guidance   | 0.0097          | 77.98     | **0.0103**     | 76.50     | **0.0242** | 39.23     | 0.0114      | 61.20     |
| Surflo — With guidance | **0.0079**      | **87.97** | 0.0114         | **77.28** | 0.0240     | **42.05** | **0.0070**  | **81.11** |

### Gaussian-Wrapping Pseudo-GT (foreground + background)

원논문 Table 1. CD lower is better, F1 higher is better.

| Method                 | DL3DV CD↓  | F1↑       | T&T CD↓    | F1↑       | Mip-NeRF 360 CD↓ | F1↑       | DeepBlending CD↓ | F1↑       |
| ---------------------- | ---------- | --------- | ---------- | --------- | ---------------- | --------- | ---------------- | --------- |
| NOVA3R                 | 0.0459     | 30.51     | 0.0432     | 32.99     | 0.0429           | 25.60     | 0.0550           | 27.61     |
| 2DGS                   | 0.0163     | 60.10     | 0.0161     | 62.95     | 0.0222           | 51.08     | 0.0204           | 59.54     |
| Gaussian Wrapping      | 0.0168     | 60.67     | 0.0157     | 64.94     | 0.0201           | 57.86     | 0.0164           | 64.54     |
| Surflo — No guidance   | **0.0072** | **81.92** | **0.0053** | **88.57** | **0.0068**       | **82.00** | 0.0116           | 70.96     |
| Surflo — With guidance | 0.0083     | 78.55     | 0.0056     | 86.40     | 0.0103           | 76.57     | **0.0109**       | **75.09** |

Surflo outperforms optimization-based references in absolute Chamfer at a fraction of the cost. Interestingly, the No-guidance variant often gives better CD/F1 metrics, while guidance mainly improves visual quality and outlier suppression (guidance wins DeepBlending in both tables).

### Varying Input Views (Tanks & Temples)

원논문 Table 3. CD lower is better, F1 higher is better.

| Method                 | 2 views CD↓ | F1↑      | 8 views CD↓ | F1↑       | 32 views CD↓ | F1↑       |
| ---------------------- | ----------- | -------- | ----------- | --------- | ------------ | --------- |
| NOVA3R                 | 0.2620      | 5.78     | 0.0557      | 31.78     | 0.0423       | 35.54     |
| Gaussian Wrapping      | 0.1476      | 5.24     | 0.0176      | 60.04     | 0.0133       | 72.10     |
| Surflo — No guidance   | **0.1345**  | **9.28** | **0.0059**  | **86.59** | **0.0049**   | **90.76** |
| Surflo — With guidance | 0.1416      | 7.08     | 0.0061      | 86.25     | 0.0049       | 90.34     |

Surflo is consistently best across all view counts, including the very sparse 2-view regime, while the latent size stays fixed.

### Ablation

원논문 Table 5. DL3DV / Tanks & Temples, 16 views.

| Component    | Variant                | DL3DV CD↓  | F1↑       | T&T CD↓    | F1↑       |
| ------------ | ---------------------- | ---------- | --------- | ---------- | --------- |
| Latent size  | K = 32 tokens          | 0.0089     | 72.76     | 0.0068     | 79.51     |
| Latent size  | K = 128 tokens         | **0.0073** | **81.21** | **0.0055** | **88.02** |
| 3D PE        | None (raw VGGT tokens) | 0.0083     | 76.05     | 0.0068     | 80.78     |
| 3D PE        | Gaussian Fourier 3D PE | **0.0073** | **81.21** | **0.0055** | **88.02** |
| Source dist. | Pure Gaussian          | 0.0088     | 73.57     | 0.0074     | 77.09     |
| Source dist. | Mixture of Gaussians   | **0.0073** | **81.21** | **0.0055** | **88.02** |

## 💡 Insights & Impact

- **One geometry, one state**: Motivated by Klein's Erlangen program — geometry is what stays invariant under viewing — Surflo argues many views encode one geometry, so the right intermediate representation is a single global state, not per-view pointmaps.
- **Decoupling resolution from views**: A single cached latent decodes 8K to 128K+ points on the same GPU, supporting both fast coarse previews and dense surfaces without re-encoding.
- **Guidance as soft consistency**: Injecting rendering-loss gradients couples independently sampled points, acting as a soft consistency prior that suppresses outliers — though it can trade a little metric accuracy for visual quality.
- **Efficiency**: Decoding 10⁵ points from the cached latent takes a few seconds (two orders of magnitude faster than per-scene optimization); guidance adds ~30s to 3min. Limitations: it inherits VGGT's failure modes (poor pointmaps from very few views/extreme baselines), guidance rendering adds cost, and it models geometry but not appearance.

## 🔗 Related Work

- **[VGGT](vggt.md)** & **[DUSt3R](../foundation/dust3r.md)**: Per-view feed-forward foundations; VGGT is Surflo's frozen backbone, and per-view pointmaps are its main contrast.
- **[Depth Anything 3](depth-anything-3.md)**: The DA3 per-view baseline and optional monocular-depth guidance expert.
- **[NOVA3R](../reasoning/nova3r.md)**: The closest latent feed-forward baseline (fixed 10K-point output, 2-view trained).
- **[CUT3R](../dynamic/cut3r.md)**: A global-state model that still decodes per-view pointmaps rather than a global geometric object.
- **[D4RT](../dynamic/d4rt.md)**: A queried scene representation that regresses pixel-anchored positions on dense video, contrasted with Surflo's generative sampling from sparse views.

## 📚 Key Takeaways

1. Surflo compresses arbitrarily many unposed views into a single fixed-size latent and decodes an arbitrary number of oriented surface points via flow matching in R³ × S².
2. Per-point independence enables coarse previews to million-point dense surfaces from the same latent; a rendering-guidance term correlates points and aligns them to the images.
3. It matches or surpasses feed-forward and optimization baselines on 8 benchmarks (best CD, often best F1) and is the only feed-forward model combining a global latent with arbitrary-resolution decoding.
4. The No-guidance variant often wins metrics while guidance improves visual quality; it models geometry but not appearance.

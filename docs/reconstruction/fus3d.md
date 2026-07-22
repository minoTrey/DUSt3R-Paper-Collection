# Fus3D: Decoding Consolidated 3D Geometry from Feed-forward Geometry Transformer Latents (arXiv preprint (2026-03))

![fus3d — architecture](https://arxiv.org/html/2603.25827v1/x3.png)

_Architecture of Fus3D: The geometry transformer 𝒢\mathcal{G} (beige) processes tokenized input images, yielding a list of 2D intermediate features… (원논문 Fig. 3)_

## 📋 Overview

- **Authors**: Laura Fink, Linus Franke, George Kopanas, Marc Stamminger, Peter Hedman
- **Institution**: Friedrich-Alexander-Universität Erlangen-Nürnberg; Inria, Université Côte d'Azur; Google DeepMind
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.25827) | [Project Page](https://lorafib.github.io/fus3d)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward method that regresses a dense Signed Distance Field directly from the intermediate latent features of a multi-view geometry transformer (VGGT backbone) via a learned volumetric extraction module, bypassing per-view prediction and post-hoc fusion in under three seconds without camera calibration.

## 🎯 Key Contributions

1. **Direct 3D extraction from latents**: Identifies the per-view prediction bottleneck as the cause of both sparse-view incompleteness and many-view noise accumulation, and instead extracts 3D geometry directly from the transformer's intermediate feature space.
2. **Learned volumetric extraction**: A set of 3D-position-conditioned canonical embeddings progressively absorbs multi-view features into a structured latent grid via interleaved 2D-to-3D cross-attention and 3D self-attention, enabling projection-free 2D-to-3D lifting.
3. **Validity-aware SDF supervision**: Two binary masks handle non-watertight meshes and unobserved regions, degrading gracefully to an unsigned-distance objective where signs are ill-defined, enabling scalable training on real data.
4. **Pose-free feed-forward SDF**: Regresses SDFs from unstructured image collections without camera parameters at inference.

## 🔧 Technical Details

### Pipeline

- **Backbone G**: VGGT (jointly processes all views in a shared token sequence; retains VGGT's first-view-centered coordinate convention). Pairwise methods like DUSt3R/MASt3R are unsuitable because they fuse post-hoc.
- **Extraction transformer E**: Learned canonical embeddings z3D (extent 16³, dimension d = 2048) conditioned on voxel positions serve as queries; keys/values come from four intermediate feature maps of G. Each stage is one cross-attention + one 3D self-attention block; the four-stage sequence is applied twice → 8 blocks.
- **Decoder H3D**: A convolutional up-sampling network maps the latent grid to a 64³ SDF grid.

### Supervision

- Losses: value loss LSDF, gradient loss L∇, Eikonal regularizer Leik, plus VGGT's camera loss. A validity mask restricts evaluation to reliable GT SDF positions; an Eikonal mask excludes sign-inconsistent regions (LSDF then falls back to unsigned distance).
- Two-stage curriculum: low-res 16³ with a linear decoder (LSDF + Lcam), then full-res under the complete loss. Backbone lightly LoRA-finetuned for object-centric data. Adam + decoupled weight decay, cosine LR with warmup, up to four NVIDIA A100 80 GB GPUs.
- Datasets: ~5% of the Objaverse subset (17K training scenes, 24 views each; 170 held-out) and DTU (splits following VolRecon/UFORecon).

## 📊 Results

### Feed-Forward SDF Baselines on DTU

원논문 Table 1. CD/DGT2P/DP2GT ↓. † = 경쟁 방법에 COLMAP(비 feed-forward) 포즈 제공; 표기 없는 행은 VGGT 예측 포즈(feed-forward).

| Method     | Fav CD ↓  | Fav DGT2P ↓ | Fav DP2GT ↓ | Unfav CD ↓ | Unfav DGT2P ↓ | Unfav DP2GT ↓ |
| ---------- | --------- | ----------- | ----------- | ---------- | ------------- | ------------- |
| VolRecon † | 2.905     | 2.331       | 3.478       | 5.781      | 3.811         | 7.751         |
| UFORecon † | 2.771     | 2.101       | 3.440       | 3.275      | 2.252         | 4.298         |
| UFORecon   | 3.415     | 2.989       | 3.841       | 4.942      | 3.737         | 6.146         |
| VolRecon   | 3.678     | 3.369       | 3.987       | 8.878      | 5.869         | 11.887        |
| **Fus3D**  | **2.432** | **1.804**   | **3.059**   | **3.525**  | **2.814**     | **4.236**     |

Fus3D improves Chamfer distance by 29% over both baselines in the feed-forward (unknown-pose) setting for both favorable and unfavorable view configurations, and remains competitive even against the baselines supplied with COLMAP poses.

### Predict-Then-Fuse Baselines on Objaverse (8 input views, 170 test scenes)

원논문 Table 2. Fϵ/F0.5ϵ ↑, CD/EMD/SDF MAE ↓. 하단 두 행은 non-finetuned baseline.

| Method           | Fϵ ↑     | F0.5ϵ ↑  | CD ↓      | EMD ↓     | SDF MAE ↓ |
| ---------------- | -------- | -------- | --------- | --------- | --------- |
| **Fus3D**        | **0.83** | **0.51** | **0.021** | 0.019     | **0.004** |
| VGGTft + TSDF    | 0.80     | 0.43     | 0.022     | **0.014** | 0.023     |
| VGGTft + Poisson | 0.70     | 0.38     | 0.044     | 0.052     | –         |
| TSDF VGGT        | 0.35     | 0.12     | 0.080     | 0.082     | 0.136     |
| Poisson VGGT     | 0.29     | 0.10     | 0.121     | 0.788     | –         |

Fus3D leads on all metrics except EMD, where VGGTft+TSDF is marginally better (0.014 vs 0.019). Its SDF MAE advantage is pronounced (0.004 vs 0.023 for VGGTft+TSDF).

## 💡 Insights & Impact

- **Joint prior beats per-view fusion**: Extracting geometry from the shared latent lets the full multi-view prior inform every spatial location, giving complete reconstructions in sparse views and noise-free scaling to more views (both Fus3D and VGGTft are trained on ≤8 views, yet Fus3D generalizes well to 24 views).
- **SDF quality, not just surface placement**: At an isovalue offset of 0.5ϵ, Fus3D achieves a higher F-score than a TSDF built from ground-truth synthetic depth, showing the regressed distance field is well-behaved throughout the volume.
- **Emergent structure**: PCA of the volumetric latent shows components varying smoothly in space and aligning with the SDF zero-crossing and category-level parts, hinting at usefulness for downstream shape recognition/completion.
- **Scalable runtime**: Fus3D adds a higher constant cost in sparse views but omits VGGT's depth/point heads, so its runtime is dominated by shared feature extraction and scales more favorably than predict-then-fuse pipelines whose fusion cost grows with view count.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The geometry-transformer backbone; VGGT+TSDF / VGGT+Poisson are the predict-then-fuse baselines.
- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: Pairwise pointmap methods, deemed unsuitable as backbones (post-hoc aggregation).
- **[π³](pi3.md)**, **[MapAnything](mapanything.md)**, **[Depth Anything 3](depth-anything-3.md)**: Cited unified geometry transformers with shared-token processing.
- **[Spann3R](spann3r.md)** and **[CUT3R](../dynamic/cut3r.md)**: Persistent-memory methods, contrasted as still producing 2.5D per-view outputs needing fusion.
- **[Fin3R](fin3r.md)**: Source of the LoRA backbone fine-tuning strategy used for object-centric adaptation.

## 📚 Key Takeaways

1. Fus3D replaces per-view decoder heads with a learned volumetric extraction module that regresses dense SDFs directly from a VGGT backbone's latents, in a fully feed-forward, pose-free manner.
2. Validity-aware supervision makes training on non-watertight, partially observed real data practical by falling back to unsigned distances where signs are undefined.
3. It improves Chamfer distance by 29% over VolRecon/UFORecon on DTU under unknown poses and outperforms VGGT predict-then-fuse baselines on Objaverse across F-score, Chamfer, and SDF MAE (trailing only on EMD).

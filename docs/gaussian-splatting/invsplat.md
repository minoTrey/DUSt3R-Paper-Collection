# InvSplat: Inverse Feed-Forward Scene Splatting (arXiv preprint (2026-07))

## 📋 Overview

- **Authors**: Polina Karpikova, Wenjing Bian, Haofei Xu, Hendrik Lensch, Andreas Geiger
- **Institution**: University of Tübingen, Tübingen AI Center; ETH Zurich
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.02301) | [Project Page](https://poliik.github.io/invsplat/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first feed-forward inverse-rendering framework that predicts, in a single forward pass (~1.5 s), a structured 3D Gaussian scene where each primitive carries geometry plus intrinsic PBR material attributes (albedo, metallic, roughness) and a surface normal — enabling multi-view-consistent material recovery, novel view synthesis, and relighting.

## 🎯 Key Contributions

1. **Feed-forward inverse rendering in 3D**: The first feed-forward framework predicting physically based 3D Gaussian primitives with intrinsic material parameters from posed multi-view images in one pass, avoiding per-scene optimization and iterative diffusion.
2. **Unified prior integration**: Combines a multi-view 3D reconstruction backbone (geometry branch) with an image-based material estimation network (intrinsic branch) into a single network, producing high-quality 3D materials with strong real-world generalization.
3. **Consistent decomposition + relighting**: The explicit 3D Gaussian representation is multi-view consistent by design and supports physically based relighting via a simple point-light BRDF renderer, better modeling view-dependent effects than RGB/SH-based feed-forward methods.

## 🔧 Technical Details

### Scene representation

Each Gaussian `j` carries geometry `(μ_j, q_j, s_j, σ_j, n_j)` — mean, rotation quaternion, scale, opacity, surface normal — and intrinsic materials `(a_j, m_j, r_j)` — albedo, metallic, roughness. Spherical harmonics are replaced by these PBR attributes.

### Dual-branch architecture

- **Geometry branch** (stereo-inspired, following ReSplat): a ResNet feature pyramid → Multi-view Geometry Encoder (cross-view self-attention) → Multi-view Feature Matching that warps features across views to build a depth-candidate cost volume; shallower pyramid scales bypass matching to give high-resolution cues.
- **Intrinsic branch**: DINOv2 ViT-L/14 (with registers) encodes each view; a 36-block Multi-view Intrinsic Translator alternates intra-view / inter-view self-attention; features from uniformly spaced translator layers feed the heads.
- **Decoding (6 heads)**: a DPT depth head over `{C_i, F_m, F_s}`; a Point Transformer refines depth-lifted features into per-Gaussian rotation/scale/opacity; four DPT heads predict albedo, metallic, roughness, and normal from translator features (the albedo head adds ResNet-pyramid skip connections via a 1×1 channel adaptor). Gaussian centers come from unprojecting predicted depth; normals are rotated to world space with input extrinsics.

### Training

- Loss `L = L_a + L_m + L_r + L_d + L_n`: per-material L1 + LPIPS for albedo/metallic/roughness, an affine-invariant (MoGe-style) log-depth loss, and a cosine-similarity normal loss.
- Trained on InteriorVerse at 512×384 with curated triplets (2 input views, 3-view GT supervision). Geometry encoder initialized from ReSplat (ResNet frozen); intrinsic encoder and material heads initialized from MVInverse; jointly fine-tuned. 20k steps, batch 2, single H100, ~12 hours.

## 📊 Results

Evaluated with 2 input views per scene. `*` denotes fine-tuned networks. Albedo is scale-aligned before metric computation for all methods.

### Inverse rendering on InteriorVerse (synthetic)

원논문 Table 2. Albedo(PSNR↑/SSIM↑/LPIPS↓/RMSE↓), Metallic RMSE↓, Roughness RMSE↓, Normal Cosine Similarity↑. Type = 2D 이미지공간 vs 3D 표현.

| Method            | Type | Alb. PSNR ↑ | Alb. SSIM ↑ | Alb. LPIPS ↓ | Alb. RMSE ↓ | Met. RMSE ↓ | Rough. RMSE ↓ | Normal Cos. ↑ |
| ----------------- | ---- | ----------- | ----------- | ------------ | ----------- | ----------- | ------------- | ------------- |
| DiffusionRenderer | 2D   | 17.32       | 0.800       | 0.253        | 0.1506      | 0.2971      | 0.2825        | 0.9468        |
| DNF-Intrinsic     | 2D   | 18.64       | 0.850       | 0.211        | 0.1320      | 0.1884      | 0.2124        | 0.9261        |
| MVInverse         | 2D   | 21.83       | 0.867       | 0.217        | 0.0887      | 0.1039      | 0.1252        | **0.9654**    |
| MVInverse*        | 2D   | **22.92**   | **0.886**   | **0.182**    | **0.0798**  | **0.0985**  | **0.1221**    | 0.9630        |
| Ours              | 3D   | 22.18       | 0.873       | 0.203        | 0.0883      | 0.0993      | 0.1254        | 0.9609        |

InvSplat matches or slightly trails the 2D MVInverse (and the fine-tuned MVInverse* remains best on most per-view metrics), but does so with an explicit 3D representation rather than per-view maps.

### Multi-view consistency on Structured3D

원논문 Table 3. Reprojection RMSE↓ (albedo/metallic/roughness) + Albedo Reconstruction(PSNR↑/SSIM↑/LPIPS↓/RMSE↓). 251개 장면.

| Method            | Type | Repro Alb. ↓ | Repro Met. ↓ | Repro Rough. ↓ | Alb. PSNR ↑ | Alb. SSIM ↑ | Alb. LPIPS ↓ | Alb. RMSE ↓ |
| ----------------- | ---- | ------------ | ------------ | -------------- | ----------- | ----------- | ------------ | ----------- |
| DiffusionRenderer | 2D   | 0.100        | 0.122        | 0.108          | 15.75       | 0.714       | 0.310        | 0.174       |
| DNF-Intrinsic     | 2D   | 0.122        | 0.183        | 0.147          | 14.37       | 0.703       | 0.303        | 0.209       |
| MVInverse         | 2D   | 0.044        | 0.056        | 0.038          | 19.83       | 0.771       | 0.268        | 0.108       |
| MVInverse*        | 2D   | **0.037**    | 0.051        | 0.034          | **20.48**   | **0.798**   | **0.247**    | **0.101**   |
| Ours              | 3D   | 0.039        | **0.041**    | **0.025**      | 19.84       | 0.783       | 0.269        | 0.109       |

InvSplat achieves the best reprojection consistency for metallic (0.041) and roughness (0.025) — the attributes hardest to infer from RGB — with albedo consistency close to MVInverse* and comparable albedo reconstruction.

### Ablation: unified vs stitched 3D baselines (InteriorVerse)

원논문 Table 4. 열은 Table 2와 동일. Naive 3D baseline = MVInverse 재질맵 + ReSplat 기하를 결합.

| Method               | Type | Alb. PSNR ↑ | Alb. SSIM ↑ | Alb. LPIPS ↓ | Alb. RMSE ↓ | Met. RMSE ↓ | Rough. RMSE ↓ | Normal Cos. ↑ |
| -------------------- | ---- | ----------- | ----------- | ------------ | ----------- | ----------- | ------------- | ------------- |
| MVInverse + ReSplat* | 3D   | 20.83       | 0.860       | 0.234        | 0.1011      | 0.1041      | 0.1291        | 0.9582        |
| MVInverse*+ ReSplat* | 3D   | 21.86       | 0.873       | 0.212        | 0.0901      | 0.1011      | 0.1283        | 0.9607        |
| **Ours**             | 3D   | **22.18**   | **0.873**   | **0.203**    | **0.0883**  | **0.0993**  | **0.1254**    | **0.9609**    |

The unified architecture consistently beats both stitched baselines across all material factors while removing redundant backbones.

## 💡 Insights & Impact

- **Materials over baked RGB**: By predicting view-independent PBR parameters instead of SH color, InvSplat avoids baking highlights and illumination into appearance, enabling explicit relighting and material editing (demonstrated on Infinigen and RealEstate10K).
- **3D helps the hardest attributes**: Multi-view aggregation in an explicit 3D representation most improves metallic/roughness consistency, which are ill-posed from single RGB views.
- **Pretraining matters for normals**: Ablations show a dedicated normal head (rather than depth finite-differences or a shared Gaussian head) best separates geometry from appearance and avoids leaking texture into normals.
- **Limitations**: Inherits feed-forward reconstruction fragility to inaccurate input poses; limited on more views / different resolutions; and being non-generative it cannot hallucinate unseen regions.

## 🔗 Related Work

- Builds directly on the feed-forward reconstruction backbone ReSplat (recurrent Gaussian splats) and the material network MVInverse, alongside feed-forward 3DGS lineage pixelSplat, MVSplat, DepthSplat, NoPoSplat, and the multi-representation [VGGT](../reconstruction/vggt.md)/[DUSt3R](../foundation/dust3r.md)/WorldMirror line.
- Contrasts with optimization-based inverse rendering (IRIS, Intrinsic Image Fusion) and image-space diffusion approaches (DiffusionRenderer, DNF-Intrinsic) that lack an explicit, multi-view-consistent 3D representation.
- Uses a [MoGe](../reconstruction/moge.md)-style affine-invariant depth loss for self-supervised depth from pose-free training data.

## 📚 Key Takeaways

1. InvSplat lifts feed-forward inverse rendering into 3D: one forward pass yields a Gaussian scene where each primitive carries albedo/metallic/roughness plus geometry and normals.
2. Fusing a ReSplat geometry branch with an MVInverse-style intrinsic branch, it matches 2D material baselines while adding multi-view consistency and relighting that per-view methods cannot provide.
3. It records the best cross-view reprojection consistency for metallic and roughness on Structured3D, and its unified design beats naive stitched 3D baselines across all material factors.

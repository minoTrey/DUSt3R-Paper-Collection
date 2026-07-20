# E-RayZer: Self-supervised 3D Reconstruction as Spatial Visual Pre-training (CVPR 2026)

## 📋 Overview

- **Authors**: Qitao Zhao, Hao Tan, Qianqian Wang, Sai Bi, Kai Zhang, Kalyan Sunkavalli, Shubham Tulsiani, Hanwen Jiang
- **Institution**: Carnegie Mellon University, Adobe Research, Harvard University
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2512.10950) | [Project Page](https://qitaozhao.github.io/E-RayZer)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Replaces RayZer's latent-space view synthesis with explicit 3D Gaussians and a visual-overlap curriculum, producing a feed-forward reconstruction model trained from scratch with zero 3D annotation whose representations transfer to downstream 3D tasks.

## 🎯 Key Contributions

1. **The first truly self-supervised feed-forward 3D Gaussian splatting reconstruction model**, trained from scratch with zero 3D annotation.
2. **Representations that beat prior visual pre-training** — DINOv3, CroCo v2, VideoMAE V2, Perception Encoder — on downstream 3D tasks.
3. **Stronger 3D understanding than prior self-supervised 3D models**, evidenced by unsupervised camera pose estimation and downstream fine-tuning.
4. **Comparable to supervised VGGT** (reproduced with matched architecture and training setup, denoted VGGT*), with similar scaling behavior, despite being purely self-supervised.

## 🔧 Technical Details

### What was wrong with implicit 3D

RayZer splits inputs into a reference set `I_ref` for latent scene inference and a hidden target set `I_tgt` for photometric self-supervision, rendering through a learned transformer decoder `f_ϕ^rend`. Because pose estimation, scene reconstruction, and rendering are all learned jointly from scratch, they only need to be mutually _compatible_ — not physically meaningful. RayZer's pure-transformer design has almost no 3D inductive bias, giving it enough flexibility to learn shortcut solutions: the paper's diagnosis is that RayZer relies on a mixture of true 3D understanding and video-interpolation priors, which suffices for view synthesis but leaves the pose space uninterpretable.

### Explicit 3D Gaussians

E-RayZer predicts cameras for all views, encodes posed reference views into tokens

```text
s_ref = f_ψ′^scene( Linear(I_ref, R_ref^plk) )
```

then decodes per-pixel 3D Gaussians `G = f_ω^gauss(s_ref)`, each `g_i = (d_i, q_i, C_i, s_i, α_i)` — ray distance, quaternion, spherical harmonic coefficients, scale, and opacity. Target views are rendered with `Î_tgt = π(G, C_tgt)` using self-predicted target cameras and the same photometric loss (MSE + perceptual) as RayZer.

Because 3D Gaussians support closed-form differentiable rendering, RayZer's transformer renderer is removed entirely. The authors modify gsplat to back-propagate gradients into camera intrinsics `K`. Global attention complexity is `O((K_ref·h·w)²)` versus RayZer's `O((K_ref·h·w + n_z)²)`.

### Removing the interpolation shortcut

E-RayZer identifies RayZer's **image index embeddings** — used to associate image tokens with camera tokens — as a main cause of the interpolation shortcut, and removes them entirely. It adopts a VGGT-style multi-view transformer with alternating local-global attention, where the local attention boundary defines the association naturally, and performs **pairwise pose prediction**: a canonical-view camera token concatenated with a target-view camera token regresses their relative pose. As a result no separate camera/register tokens are needed for canonical versus non-canonical views.

### Visual-Overlap Curriculum

Explicit 3D is harder to converge from scratch — the paper notes RayZer reported non-convergence when trained with explicit 3D. E-RayZer's answer is a curriculum keyed to _visual overlap_ rather than frame index.

**Why not frame interval.** Two DL3DV sequences with the same frame interval can have drastically different overlap; interval-based sampling is a coarse proxy, hard-coded per dataset and not scalable to heterogeneous sources.

**Labeling.** For each sequence, sample frame triplets at spacing `Δt` and average the two pairwise overlaps to get `o_tri(i, Δt)`; averaging over triplets gives the per-sequence profile `O_u(Δt)`.

**Sampling.** At curriculum progress `s ∈ [0, 1]`, the overlap lower limit `o(s) = s·o_min + (1−s)·o_max` decreases over training; the sequence-specific spacing `Δt_u(s)` is looked up in the precomputed table and linearly interpolated.

**Two instantiations.** Geometric overlap uses UFM covisibility (trained with 3D annotations); semantic overlap uses DINOv2 cosine similarity (trained self-supervised, keeping the framework annotation-free).

### Training Setup

- 10 input images: 5 reference, 5 target.
- Visual-overlap score decays linearly 1.0 → 0.5 (geometric) or 1.0 → 0.75 (semantic).
- 8 A100 GPUs, global batch size 192 (24/GPU), 152K iterations, ≈198 hours. Curriculum progresses over the first 86K iterations.
- 3K-iteration warm-up to peak LR 4e-4, then cosine decay to zero. AdamW (β₁=0.9, β₂=0.95), gradient clipping at 1.0, skipping steps whose pre-clip gradient norm exceeds 5.0.
- Multi-dataset variant mixes seven sources: DL3DV, CO3Dv2, RealEstate10K, MVImgNet, ARKitScenes, WildRGB-D, ACID.
- For fair comparison, all RayZer models in the paper are retrained with E-RayZer's improved architecture and curriculum.

## 📊 Results

### Comparison with (Partially) Self-supervised Methods

원논문 Table 1. PSNR for novel-view synthesis, RPA↑ @5°/15°/30° for pose. SPFSplat is initialized from MASt3R, itself densely 3D-supervised on 14 datasets, so it is not truly self-supervised.

| Method          | Training Data  | WildRGB-D PSNR ↑ | @5° ↑ | @15° ↑ | @30° ↑ | ScanNet++ PSNR ↑ | @5° ↑ | @15° ↑ | @30° ↑ |
| --------------- | -------------- | ---------------- | ----- | ------ | ------ | ---------------- | ----- | ------ | ------ |
| SPFSplat        | RE10K (+extra) | 16.7             | 31.5  | 58.0   | 69.8   | 14.0             | 2.5   | 11.8   | 30.3   |
| E-RayZer (ours) | RE10K          | 21.0             | 40.3  | 89.4   | 96.5   | 17.5             | 1.1   | 13.3   | 37.3   |
| RayZer          | DL3DV          | 25.9             | 0.0   | 0.2    | 6.5    | 20.5             | 0.0   | 0.7    | 6.2    |
| E-RayZer (ours) | DL3DV          | 24.3             | 84.5  | 98.4   | 99.3   | 20.1             | 7.7   | 33.6   | 63.0   |
| RayZer          | 7 datasets     | 26.7             | 0.2   | 9.3    | 43.6   | 21.5             | 0.0   | 0.9    | 9.0    |
| E-RayZer (ours) | 7 datasets     | 24.9             | 90.8  | 98.6   | 99.3   | 20.7             | 5.7   | 34.8   | 63.7   |

원논문 Table 1, DL3DV columns:

| Method          | Training Data  | DL3DV PSNR ↑ | @5° ↑ | @15° ↑ | @30° ↑ |
| --------------- | -------------- | ------------ | ----- | ------ | ------ |
| SPFSplat        | RE10K (+extra) | 15.1         | 19.5  | 40.6   | 50.5   |
| E-RayZer (ours) | RE10K          | 17.3         | 21.2  | 55.0   | 72.7   |
| RayZer          | DL3DV          | 21.4         | 0.0   | 0.6    | 6.2    |
| E-RayZer (ours) | DL3DV          | 20.3         | 72.0  | 88.4   | 93.5   |
| RayZer          | 7 datasets     | 20.8         | 0.0   | 1.9    | 17.0   |
| E-RayZer (ours) | 7 datasets     | 19.7         | 59.9  | 82.9   | 90.2   |

**The trade is explicit.** RayZer wins on PSNR in every matched setting (25.9 vs 24.3 on WildRGB-D, 26.7 vs 24.9 with 7 datasets) — its implicit formulation over-optimizes for view synthesis. But its pose accuracy is essentially zero: RPA@5° of 0.0–0.2 across the board. E-RayZer gives up ~1–2 dB PSNR to obtain a geometrically meaningful camera space.

### Comparison with Supervised VGGT

원논문 Table 2. Both models trained on DL3DV. VGGT* is the re-implementation with E-RayZer's pairwise camera head.

| Method            | DL3DV @5° ↑ | DL3DV @15° ↑ | RE10K @5° ↑ | RE10K @15° ↑ | CO3Dv2 @5° ↑ | CO3Dv2 @15° ↑ | WildRGB-D @5° ↑ | WildRGB-D @15° ↑ |
| ----------------- | ----------- | ------------ | ----------- | ------------ | ------------ | ------------- | --------------- | ---------------- |
| E-RayZer (ours)   | 72.0        | 88.4         | 83.0        | 96.8         | 19.1         | 61.8          | 51.1            | 82.3             |
| VGGT*             | 79.6        | 94.2         | 80.4        | 97.9         | 16.0         | 64.3          | 32.5            | 76.2             |
| E-RayZer → VGGT\* | 87.3        | 96.6         | 85.3        | 98.4         | 25.3         | 72.2          | 56.2            | 91.4             |

원논문 Table 2, remaining zero-shot datasets:

| Method            | 7-Scenes @5° ↑ | 7-Scenes @15° ↑ | CamLand @5° ↑ | CamLand @15° ↑ | BlendedMVS @5° ↑ | BlendedMVS @15° ↑ | NAVI @5° ↑ | NAVI @15° ↑ | ScanNet++ @5° ↑ | ScanNet++ @15° ↑ |
| ----------------- | -------------- | --------------- | ------------- | -------------- | ---------------- | ----------------- | ---------- | ----------- | --------------- | ---------------- |
| E-RayZer (ours)   | 38.8           | 78.0            | 18.1          | 62.9           | 22.9             | 46.8              | 20.7       | 57.8        | 7.7             | 33.6             |
| VGGT*             | 34.7           | 83.6            | 11.1          | 49.8           | 17.0             | 42.8              | 14.3       | 54.5        | 6.7             | 39.8             |
| E-RayZer → VGGT\* | 43.8           | 82.8            | 30.2          | 75.6           | 29.2             | 52.2              | 26.9       | 64.3        | 14.3            | 53.8             |

Self-supervised E-RayZer beats supervised VGGT*on several out-of-domain sets (WildRGB-D, CamLand, BlendedMVS, NAVI) and almost consistently on the stricter RPA@5°, while VGGT* holds the in-domain DL3DV lead and the looser @15° threshold on 7-Scenes and ScanNet++. Using E-RayZer as initialization for VGGT* improves every column — the paper reads this as the two forms of knowledge being highly complementary, since both are trained on the same data.

### Probing Learned Representations — 3D Downstream Tasks

원논문 Table 3. Evaluated on ScanNet++ and BlendedMVS, neither of which is in any model's pre-training. Only encoders of RayZer and E-RayZer are used; their pre-training camera heads are discarded for fairness.

ScanNet++:

| Method              | Frozen AbsRel ↓ | Frozen δ<1.25 ↑ | Frozen RPA@5° ↑ | Frozen RPA@15° ↑ | Full-ft AbsRel ↓ | Full-ft δ<1.25 ↑ | Full-ft RPA@5° ↑ | Full-ft RPA@15° ↑ |
| ------------------- | --------------- | --------------- | --------------- | ---------------- | ---------------- | ---------------- | ---------------- | ----------------- |
| DINOv2              | 0.193           | 74.9            | 0.8             | 9.5              | 0.178            | 78.2             | 3.3              | 19.6              |
| DINOv3              | 0.201           | 73.2            | 0.4             | 10.0             | 0.176            | 78.7             | 4.0              | 22.3              |
| Percep. Encoder     | 0.203           | 73.2            | 0.5             | 8.5              | 0.181            | 77.8             | 2.9              | 20.0              |
| CroCo v2            | 0.203           | 73.0            | 1.4             | 15.1             | 0.177            | 78.2             | 3.8              | 20.8              |
| VideoMAE V2         | 0.175           | 76.3            | 0.1             | 6.6              | 0.076            | 93.9             | 12.8             | 51.4              |
| RayZer              | 0.161           | 79.3            | 4.7             | 27.4             | 0.077            | 93.9             | 21.5             | 60.6              |
| **E-RayZer (ours)** | **0.116**       | **87.1**        | **13.8**        | **49.5**         | **0.059**        | **95.1**         | **22.7**         | **64.3**          |

BlendedMVS:

| Method              | Frozen AbsRel ↓ | Frozen δ<1.25 ↑ | Frozen RPA@5° ↑ | Frozen RPA@15° ↑ | Full-ft AbsRel ↓ | Full-ft δ<1.25 ↑ | Full-ft RPA@5° ↑ | Full-ft RPA@15° ↑ |
| ------------------- | --------------- | --------------- | --------------- | ---------------- | ---------------- | ---------------- | ---------------- | ----------------- |
| DINOv2              | 0.366           | 50.5            | 1.1             | 8.0              | 0.353            | 52.5             | 1.8              | 12.8              |
| DINOv3              | 0.397           | 49.1            | 1.2             | 6.8              | 0.349            | 52.1             | 1.7              | 15.3              |
| Percep. Encoder     | 0.385           | 49.9            | 1.2             | 6.2              | 0.370            | 50.3             | 2.1              | 11.6              |
| CroCo v2            | 0.412           | 47.7            | 1.6             | 12.6             | 0.369            | 51.2             | 2.8              | 15.9              |
| VideoMAE V2         | 0.371           | 49.4            | 1.0             | 6.2              | 0.197            | 75.9             | 17.3             | 45.5              |
| RayZer              | 0.351           | 52.6            | 16.7            | 34.5             | 0.194            | 77.7             | 26.1             | 50.2              |
| **E-RayZer (ours)** | **0.245**       | **68.3**        | **26.5**        | **45.8**         | **0.148**        | **82.8**         | **36.2**         | **58.8**          |

### Pairwise Flow Estimation (2.5D)

원논문 Table 4. StaticThings3D, an out-of-distribution synthetic dataset; all models fully finetuned under flow supervision.

| Method          | EPE ↓ | @1px ↓ | @2px ↓ | @5px ↓ |
| --------------- | ----- | ------ | ------ | ------ |
| CroCo v2        | 1.273 | 17.7   | 8.7    | 3.8    |
| VideoMAE V2     | 2.028 | 42.7   | 22.1   | 6.9    |
| RayZer          | 1.105 | 13.4   | 6.6    | 2.8    |
| E-RayZer (ours) | 1.254 | 16.9   | 7.8    | 3.1    |

**E-RayZer loses here.** RayZer is better on every flow metric, and CroCo v2 edges out E-RayZer on EPE (1.273 vs 1.254 favors E-RayZer marginally, but RayZer's 1.105 leads clearly). The paper's explanation is that RayZer's implicit formulation is naturally suited to low-level motion estimation, whereas E-RayZer is not trained on a correspondence objective.

### Ablation: Curriculum Learning

원논문 Table 6.

| Training Data | Curriculum Variant | PSNR ↑ | RPA@5° ↑ | RPA@15° ↑ | RPA@30° ↑ |
| ------------- | ------------------ | ------ | -------- | --------- | --------- |
| DL3DV         | No Curriculum      | 16.1   | 4.0      | 27.8      | 47.2      |
| DL3DV         | Frame Interval     | 19.8   | 56.1     | 79.3      | 86.0      |
| DL3DV         | Semantic Overlap   | 20.4   | 73.2     | 88.7      | 93.7      |
| DL3DV         | Geometric Overlap  | 20.3   | 72.0     | 88.4      | 93.5      |
| 7-dataset     | No Curriculum      | 15.9   | 2.1      | 21.6      | 40.7      |
| 7-dataset     | Frame Interval     | 19.1   | 43.8     | 72.1      | 82.9      |
| 7-dataset     | Semantic Overlap   | 19.7   | 58.7     | 81.0      | 89.8      |
| 7-dataset     | Geometric Overlap  | 19.7   | 59.9     | 82.9      | 90.2      |

Notably the semantic (fully unsupervised, DINOv2-based) and geometric (UFM-based, 3D-supervised) variants perform comparably — the annotation-free version costs nothing.

### Ablation: Data Mixing and Scaling

원논문 Table 5. PSNR is not reported for VGGT* (marked `/` in the paper).

| Training Data | Method   | CO3Dv2 @5° ↑ | CO3Dv2 @15° ↑ | ScanNet++ @5° ↑ | ScanNet++ @15° ↑ | DL3DV @5° ↑ | DL3DV @15° ↑ |
| ------------- | -------- | ------------ | ------------- | --------------- | ---------------- | ----------- | ------------ |
| RE10K         | VGGT*    | 0.1          | 3.7           | 0.6             | 10.0             | 17.8        | 50.9         |
| RE10K         | E-RayZer | 0.6          | 8.3           | 1.1             | 13.3             | 21.2        | 55.0         |
| DL3DV         | VGGT*    | 16.0         | 64.3          | 6.7             | 39.8             | 79.6        | 94.2         |
| DL3DV         | E-RayZer | 19.1         | 61.8          | 7.7             | 33.6             | 72.0        | 88.4         |
| 7-dataset Mix | VGGT*    | 43.4         | 83.5          | 13.1            | 54.8             | 66.1        | 88.9         |
| 7-dataset Mix | E-RayZer | 30.3         | 74.2          | 5.7             | 34.8             | 59.9        | 82.9         |

The two models show similar scaling behavior — broader training distributions improve generalization, and reducing a domain's sampling frequency slightly degrades its own test set. But the 7-dataset block is where **VGGT\* pulls clearly ahead**, and the paper says so: VGGT* "holds advantage when trained on large data."

## 💡 Insights & Impact

**A shortcut is not a representation.** The paper's sharpest argument is diagnostic: RayZer's excellent PSNR co-exists with a near-zero pose accuracy, which means its "3D awareness" was largely view interpolation. Explicit geometry is what forces the model to be right for the right reasons.

**Inductive bias, injected carefully.** E-RayZer's thesis is that 3D inductive biases remain essential, but must be introduced without sacrificing scalability. Explicit Gaussians provide geometric regularization through the rendering operator; removing image index embeddings closes the interpolation escape hatch; pairwise pose prediction removes the canonical-view asymmetry.

**Curriculum by overlap, not by index.** Frame interval is a proxy that breaks across heterogeneous sources with different camera motion distributions. Overlap is a natural, unit-free measure of difficulty that also aligns distributions across datasets — and it can be approximated fully unsupervised via DINOv2 similarity.

**Pre-training, not just reconstruction.** The most transferable claim is that E-RayZer initialization improves supervised VGGT* on every dataset in Table 2, even when both are trained on the same data. That points to a self-supervised pre-training / supervised post-training paradigm for 3D vision.

**Limitations the paper states.** E-RayZer operates on static scenes only, and high-quality static-scene data is scarce beyond existing benchmarks. The curriculum assumes continuous video frames with fairly uniform camera motion; sparse images or drastic viewpoint changes may reduce its effectiveness.

## 🔗 Related Work

- [VGGT](vggt.md) — the supervised reference point (reproduced as VGGT*) and the architectural template for the alternating local-global transformer
- [DUSt3R](../foundation/dust3r.md) — pixel-aligned pointmap prediction; also the source of the StaticThings3D image pairs used for flow evaluation
- [MASt3R](../foundation/mast3r.md) — the densely supervised model SPFSplat is initialized from
- [CroCo v2](../foundation/croco-v2.md) — cross-view completion pre-training, a probing baseline
- [Pi3](pi3.md) — permutation-equivariant feed-forward reconstruction in the same lineage
- [MapAnything](mapanything.md) — contemporaneous universal feed-forward metric reconstruction

## 📚 Key Takeaways

1. **Explicit geometry eliminates the shortcut.** Swapping RayZer's latent renderer for 3D Gaussians converts near-zero pose accuracy into 72–90 RPA@5°, at a cost of roughly 1–2 dB PSNR.
2. **The details matter as much as the representation.** Removing image index embeddings and switching to pairwise pose prediction are what actually block view interpolation.
3. **Visual overlap is the right curriculum axis.** It beats frame-interval scheduling on both training regimes, and the fully unsupervised semantic variant matches the 3D-supervised geometric one.
4. **Self-supervision transfers.** Frozen E-RayZer features beat DINOv2/DINOv3/CroCo v2/VideoMAE V2/Perception Encoder on every downstream 3D metric reported, and initializing VGGT* from E-RayZer improves all of its pose columns.
5. **It is not uniformly better.** RayZer wins on PSNR and on pairwise flow; supervised VGGT* wins in-domain and at the largest data scale. The claim is comparability without annotation, not dominance.

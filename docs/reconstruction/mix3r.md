# Mix3R: Mixing Feed-forward Reconstruction and Generative 3D Priors for Joint Multi-view Aligned 3D Reconstruction and Pose Estimation (arXiv preprint (2026-05))

## 📋 Overview

- **Authors**: Siyou Lin, Zhou Xue, Hongwen Zhang, Liang An, Dongping Li, Shaohui Jiao, Yebin Liu
- **Institution**: Tsinghua University; Beijing Normal University; ByteDance
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.03359) | [Project Page](https://jsnln.github.io/mix3r/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: Mix3R fuses a pretrained feed-forward reconstruction model (π³) and a pretrained 3D generative model (TRELLIS) with a Mixture-of-Transformers architecture, jointly generating a coarse sparse-voxel shape, per-view point maps, and camera poses aligned to that shape, then adds a training-free overlap-based attention bias to place input textures onto the generated geometry.

## 🎯 Key Contributions

1. **Aligned unification of generation and feed-forward reconstruction**: A single framework that fuses two pretrained models (one from each domain) so that 3D generation and feed-forward reconstruction become mutually beneficial, rather than the one-way feature injection of ReconViaGen (which injects VGGT features into generation).
2. **Mixture-of-Transformers (MoT) architecture**: Inserts MoT self-attentions and cross-attentions between the π³ feed-forward backbone and the TRELLIS sparse-structure flow transformer, letting the feed-forward branch ground predictions to a generative 3D prior while the 3D branch is conditioned on geometrically informative pixel-aligned features. The design maximally preserves pretrained weights.
3. **Overlap-based attention bias for training-free texture alignment**: Computes an attention bias from the overlaps between generated coarse voxels and aligned image patches, added on top of a pretrained textured-geometry flow model in a training-free manner to correctly place input textures onto the generated shape with minimal extra cost.

## 🔧 Technical Details

### Two-stage coarse-to-fine pipeline

Following TRELLIS, Mix3R generates a 3D shape in two stages:

- **Stage 1 — Joint coarse geometry + pose**: A single network `F_mix` jointly generates a coarse 3D structure (sparse voxels), per-view local point maps `{X_i}`, camera poses `{(R_i, T_i)}`, and a similarity alignment transform `(s, R, T)` mapping π³ output into the TRELLIS voxel space.
- **Stage 2 — Textured geometry generation**: A second flow transformer `F_slat` denoises a structured latent into the final asset (decoded to a mesh and a 3DGS representation), guided by the stage-1 alignment via the overlap-based attention bias.

### MoT block-matching design

- Built on TRELLIS sparse-structure flow transformer (3D branch) and the π³ backbone transformer (2D branch). π³ follows VGGT in alternating local self-attention (views batched) and global self-attention (views concatenated).
- TRELLIS has 24 blocks; π³ has 36 blocks (18 global). A uniform injection matches every global π³ block to a TRELLIS block; the 6 remaining TRELLIS blocks are matched to local π³ blocks in a unique order-preserving way.
- This yields three mixed-block types: **type-A** (local π³ block, no TRELLIS match — no mixing), **type-B** (local π³ block matched to a TRELLIS block — MoT self-attention over 3D tokens + transformation token, plus cross-attention injecting π³ features), and **type-C** (global π³ block matched to a TRELLIS block — the cross-attention is extended to a large global MoT self-attention over all three modalities).
- Only the global blocks of π³ are extended to MoT self-attention; local blocks remain local, preserving π³'s alternating design.

### Training objective

- Flow-matching loss on the velocity: `L_fm = ‖v − (ε − z0)‖²`.
- Aligned point maps `X̂_i = s(R(R_i(X_i) + T_i) + T)` are supervised by an L1 point-coordinate loss `L_pts` and an L1 point-normal loss `L_nml`. Total loss `L = L_fm + λ_pts·L_pts + λ_nml·L_nml`.
- Time-dependent weights: `λ_pts = Sigmoid(−24t + 9)`, `λ_nml = 0.1 × λ_pts`, so `t ≥ 0.5 ⇒ λ_pts ≈ 0` and `t ≤ 0.25 ⇒ λ_pts ≈ 1` (since little geometry is recoverable from noisy `z_t` at large `t`).

### Attention bias (stage 2)

- For each voxel `p_j` an average point count `APC(p_j)` is computed from aligned point maps; the bias `B(f_j, y_k) = α·max((|p_j ∩ x̂_k| − APC(p_j)) / (max_k|p_j ∩ x̂_k| − APC(p_j)), 0)` increases attention where an image patch overlaps a voxel above average. Biases are clipped to a minimum of 0 (decreasing scores was found to degrade performance). Scaling `α = 5`.
- Camera refinement: stage 1 predicts only extrinsics; intrinsics are estimated by least-squares solving the perspective-projection equation, then intrinsics + extrinsics are jointly refined with the DRTK differentiable renderer minimizing RGB + mask loss (Adam, 2000 steps, lr 1e-2, early stopping after 100 non-improving steps).

### Implementation

- Trained on a subset of TRELLIS-500k (Objaverse-XL, ABO, HSSD), containing **404354 objects**; training data generated with TRELLIS itself (8-view renderings), each object paired with GT latents and 32 renderings.
- Core model (excluding the DINOv2 encoder and sparse-structure VAE decoder): **1.71B parameters total, 839.78M trainable**. Only parameters without a pretrained weight plus the new MoT/cross-attention modules are activated during training.
- Learning rate 1e-4 with cosine schedule, 400k steps, batch size 16; 16 NVIDIA-A100 GPUs, about one week. 4 views sampled per step (fully-random / nearest-view / farthest-view sampling with probabilities 0.2 / 0.4 / 0.4).
- Inference: input resolution 518, 50 steps for stage-1 and 25 steps for stage-2.

## 📊 Results

Datasets: **Toys4k** and **Google Scanned Objects (GSO)**. Baselines: TRELLIS, UniLat3D, MV-SAM3D, ReconViaGen, and (for pose) VGGT, π³. Higher is better for PSNR/SSIM and for the pose accuracy metrics; lower is better for LPIPS and CD.

### Input alignment (rendering with predicted poses)

원논문 Table 1.

| Method      | Toys4k PSNR ↑ | Toys4k SSIM ↑ | Toys4k LPIPS ↓ | GSO PSNR ↑ | GSO SSIM ↑ | GSO LPIPS ↓ |
| ----------- | ------------- | ------------- | -------------- | ---------- | ---------- | ----------- |
| MV-SAM3D    | 22.360        | 0.9168        | 0.065          | 22.345     | 0.9016     | 0.084       |
| ReconViaGen | 23.834        | 0.9359        | 0.047          | 24.036     | 0.9260     | 0.058       |
| **Ours**    | **28.144**    | **0.9621**    | **0.030**      | **25.031** | **0.9281** | **0.057**   |

### Novel-view synthesis and geometry accuracy

원논문 Table 2. CD is Chamfer distance (×10⁻³), computed after similarity alignment to GT.

| Method      | Toys4k PSNR ↑ | Toys4k SSIM ↑ | Toys4k LPIPS ↓ | Toys4k CD ↓ | GSO PSNR ↑ | GSO SSIM ↑ | GSO LPIPS ↓ | GSO CD ↓   |
| ----------- | ------------- | ------------- | -------------- | ----------- | ---------- | ---------- | ----------- | ---------- |
| TRELLIS     | 23.930        | 0.9311        | 0.055          | 7.9986      | 22.420     | 0.9034     | 0.079       | 4.5658     |
| UniLat3D    | 25.082        | 0.9415        | 0.049          | 7.0876      | 22.765     | 0.9102     | 0.076       | 7.1384     |
| MV-SAM3D    | 23.550        | 0.9273        | 0.059          | 2.7556      | 22.331     | 0.9032     | 0.085       | 5.2356     |
| ReconViaGen | 24.491        | 0.9335        | 0.046          | 1.9419      | 24.183     | 0.9152     | 0.060       | 1.0015     |
| **Ours**    | **27.177**    | **0.9551**    | **0.033**      | **0.7419**  | **24.826** | **0.9271** | **0.055**   | **0.7945** |

### Camera pose accuracy

원논문 Table 3. RRA = relative rotation accuracy, RTA = relative translation accuracy, AUC = area under curve; all use a 30° threshold (header "Acc@30").

| Method      | Toys4k RRA ↑ | Toys4k RTA ↑ | Toys4k AUC ↑ | GSO RRA ↑ | GSO RTA ↑ | GSO AUC ↑ |
| ----------- | ------------ | ------------ | ------------ | --------- | --------- | --------- |
| VGGT        | 93.05        | 88.58        | 57.13        | **97.78** | 91.36     | 60.20     |
| π³          | 91.71        | 88.72        | 57.72        | 96.42     | 91.93     | 61.41     |
| MV-SAM3D    | 65.73        | 67.22        | 31.88        | 53.45     | 56.18     | 24.35     |
| ReconViaGen | 82.63        | 85.04        | 49.83        | 91.78     | 91.99     | 57.29     |
| **Ours**    | **95.49**    | **95.41**    | **70.63**    | 93.50     | **94.50** | **66.93** |

Mix3R wins all three pose metrics on Toys4k. On GSO it leads on RRA and AUC but **loses to VGGT (97.78) and π³ (96.42) on Acc@30 rotation accuracy (Ours 93.50)**.

### Stage decomposition ablation

원논문 Table S4. Stage-1/stage-2 combinations (TRELLIS stage-1 + Ours stage-2 is not feasible, so not evaluated).

| Stage-1 / Stage-2 | Toys4k PSNR ↑ | Toys4k LPIPS ↓ | Toys4k CD ↓ | GSO PSNR ↑ | GSO LPIPS ↓ | GSO CD ↓ |
| ----------------- | ------------- | -------------- | ----------- | ---------- | ----------- | -------- |
| TRELLIS / TRELLIS | 23.930        | 0.055          | 7.9986      | 22.420     | 0.079       | 4.5658   |
| Ours / TRELLIS    | 26.975        | 0.035          | 0.7259      | 24.399     | 0.062       | 0.8010   |
| Ours / Ours       | 27.177        | 0.033          | 0.7419      | 24.826     | 0.055       | 0.7945   |

The aligned stage-1 alone (with TRELLIS stage-2) already produces large gains over full TRELLIS; the CD is lowest with the Ours/TRELLIS combination while PSNR/LPIPS are best with the full Ours/Ours model.

### Point-map accuracy

원논문 Table S5. Point-map errors (×10⁻³): PE = pixel-wise error, CD = Chamfer distance, both after similarity alignment.

| Method   | Toys4k PE ↓ | Toys4k CD ↓ | GSO PE ↓  | GSO CD ↓  |
| -------- | ----------- | ----------- | --------- | --------- |
| π³       | 9.441       | 3.753       | 6.723     | 2.896     |
| **Ours** | **2.285**   | **0.527**   | **3.729** | **1.258** |

### Attention bias + camera refinement ablation

원논문 Table S6.

| Attn Bias / Refine | Toys4k PSNR ↑ | Toys4k SSIM ↑ | Toys4k LPIPS ↓ | GSO PSNR ↑ | GSO SSIM ↑ | GSO LPIPS ↓ |
| ------------------ | ------------- | ------------- | -------------- | ---------- | ---------- | ----------- |
| No / No            | 25.014        | 0.9397        | 0.042          | 23.020     | 0.9039     | 0.078       |
| Yes / No           | 25.163        | 0.9422        | 0.039          | 23.350     | 0.9107     | 0.070       |
| Yes / Yes          | 28.144        | 0.9621        | 0.030          | 25.031     | 0.9281     | 0.057       |

The metric gain from the attention bias alone (No/No → Yes/No) is small; the paper notes it is most effective on rotationally symmetric objects with asymmetric texture, of which Toys4k/GSO contain few. On GSO's manually annotated SGAT subset (279 objects), Table S7 reports PSNR rising 20.849 → 21.654 → 23.207 across No/No → Yes/No → Yes/Yes.

### Runtime

Reported for 4 input views on a single NVIDIA-A100 (원논문 §S2.2): stage-1 generation ~30s, stage-2 generation ~3–10s (voxel-count dependent), attention-bias computation <10s, camera refinement ≤10s per view (only needed if accurate poses are required).

## 💡 Insights & Impact

- **Chicken-and-egg alignment resolved by mutual conditioning**: A feed-forward model with knowledge of the underlying 3D shape can ground predictions to that shape instead of relying on image overlaps, while a generative model conditioned on known poses can exploit pixel alignment. Mix3R breaks this cycle by making both branches co-generate the shape, poses, and their alignment in one stage.
- **Preserving pretrained priors is the design driver**: The whole MoT block-matching scheme and the freezing strategy are motivated by retaining TRELLIS and π³ pretrained abilities while adding only the modules needed for cross-modal exchange (839.78M of 1.71B parameters trainable).
- **Training-free refinement**: The overlap-based attention bias improves texture placement on the pretrained stage-2 flow model without any additional training, which is especially valuable for rotationally symmetric shapes with asymmetric textures where pure generative methods produce plausible-but-misaligned textures.
- **Stated limitations**: (1) When test-view configurations deviate from the training distribution, the π³ branch can actually disrupt the 3D branch and degrade performance; (2) training uses TRELLIS-generated data lacking lighting and view-dependent effects, hurting in-the-wild and specular cases (e.g., OmniObject3D); (3) the frozen TRELLIS VAE decoders upper-bound generation quality (e.g., text/logos on products).

## 🔗 Related Work

- **Feed-forward branch — [π³](pi3.md)**: The pixel-aligned, permutation-equivariant backbone reused as Mix3R's 2D branch; its affine-invariant point-map/pose outputs are grounded to the generative prior.
- **[VGGT](vggt.md)**: Cited as the prototypical feed-forward reconstruction method and used as the pose baseline; π³ follows VGGT's alternating local/global attention, which Mix3R preserves.
- **[DUSt3R](../foundation/dust3r.md)**: The pioneering point-map regression paradigm from which the feed-forward reconstruction line (and π³/VGGT) descends.
- **[MonST3R](../dynamic/monst3r.md)** and **[CUT3R](../dynamic/cut3r.md)**: Cited extensions of the point-map paradigm to dynamic scenes and to latent-state streaming reconstruction.
- **Generative branch — TRELLIS**: The two-stage sparse-structure flow model reused for both the coarse-voxel generation and the training-free textured stage-2. Related unification attempts include ReconViaGen (one-way VGGT-feature injection into generation) and CUPID (UV voxel volume + PnP); Mix3R differs by making the two branches mutually beneficial.

## 📚 Key Takeaways

1. **Mix3R = π³ ⊕ TRELLIS via MoT**: A Mixture-of-Transformers fusion of a pretrained feed-forward reconstructor and a pretrained 3D generator, trained to jointly emit aligned voxels, point maps, and poses.
2. **Best input alignment and geometry/texture accuracy**: Leads all baselines on PSNR/SSIM/LPIPS/CD across Toys4k and GSO (원논문 Table 1·2), with the lowest Chamfer distances by a wide margin.
3. **Strong but not universally best pose accuracy**: Wins all pose metrics on Toys4k and leads RRA/AUC on GSO, but trails VGGT and π³ on GSO Acc@30 rotation accuracy (원논문 Table 3).
4. **Training-free attention bias**: A small-but-targeted stage-2 improvement, most effective on rotationally symmetric objects with asymmetric texture, added without retraining the pretrained flow model.

# L2D2-GS: Learning to Densify for Feedforward Dynamic Gaussian Scene Reconstruction (arXiv preprint (2026-06))

![l2d2-gs — architecture](https://arxiv.org/html/2606.29374v1/x1.png)

_Our proposed learning-to-densitfy framework enables generalizable reconstruction of dynamic urban scenes through a combination of feedforward… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Zetian Song, Chenming Wu, Junnan Liu, Chitian Sun, Liangliang He, Hangjun Ye, Jiaqi Zhang, Siwei Ma, Wen Gao
- **Institution**: State Key Laboratory of Multimedia Information Processing, School of Computer Science, Peking University; Xiaomi EV
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.29374)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A generalizable dynamic-urban reconstruction framework that reformulates feed-forward 3DGS as an iterative optimize-and-densify process, using a self-supervised policy (RL-style reward from reconstruction gains) to decide where to spawn new Gaussians and a geometric reparameterization to prevent early-stage needle-like degeneracy.

## 🎯 Key Contributions

1. **Learning-to-densify framework**: Treats generalizable reconstruction not as one-shot regression but as an iterative feed-forward optimization with adaptive densification, combining a Sparse 3D U-Net reconstructor with a policy-based densifier.
2. **Self-supervised densification policy**: Resolves the ambiguity of where to densify by deriving explicit reward signals from global reconstruction gains — back-projecting per-pixel rendering-error reduction onto individual added Gaussians via the differentiable rasterizer, at zero extra compute (reusing the CUDA backward kernels).
3. **Geometric regularization by reparameterization**: Decouples scale into a single global log-scale plus two expansive ratio coefficients, anchoring Gaussians at an isotropic limit (`ψ(0)=1`) to prevent early collapse into needle-like shapes.

## 🔧 Technical Details

### Dynamic scene representation

- A composite scene graph of voxel-wise neural Gaussians `G = {Θ, f}` (explicit attributes plus a latent feature decoded by a shallow MLP), with three node types: static background nodes, dynamic rigid nodes (canonical space transformed by ground-truth SE(3) trajectories), and a learnable sky cubemap (512×512 per face).

### Iterative feed-forward optimization

- A Sparse 3D U-Net `Ψ` performs recurrent updates: at each step the scene is rendered, photometric-MSE gradients w.r.t. Gaussian parameters are computed and channel-wise concatenated with current attributes, and `Ψ` predicts a residual `G_{t+1} = G_t + Ψ(G_t, ∇G_t)`. Step-specific independent weights (not shared) handle distribution shift across iterations.

### Policy-based densification

- A grow-on-demand paradigm: from a sparse init, a k-NN cross-attention policy network (k=16, 4 heads, d_head=32) embeds candidate points `P_query` and current Gaussians, predicting a densification probability `w_i ∈ [0,1]` per candidate; deterministic top-N selection instantiates the highest-scoring candidates.
- **Self-supervised reward**: a tentative densified reconstruction gives a gain map `ΔE = E_c − E_f`; an auxiliary mask channel is rasterized and the attribution loss `L_attr = ⟨ΔE, M_dens⟩` back-propagated to yield per-point contribution scores `S_i = ∇_{m_i} L_attr`. The policy loss maximizes expected utility (contribution minus a depth-consistency penalty) plus an entropy term to avoid over-confident selection.

### Training

- Three phases: (1) reconstructor pre-training with `L_recon` (L2 + LPIPS + scale regularization); (2) policy learning from cached `{G_coarse, P_dens, S}` tuples; (3) joint training of all modules.
- Reconstructor is a SparseResUNet (torchsparse); candidates sampled from raw LiDAR plus MapAnything-derived priors. Inference: `|P_sparse| = 800K`, coarse/fine steps `T1=12`, `T2=24`, top-N from `|P_query|=4M` to `|P_dens|=400K`. Trained on 8× NVIDIA H20, AdamW, LR 1e-4.

## 📊 Results

Primary evaluation on PandaSet (Flux4D data partition); cross-dataset zero-shot on Waymo (NOTR Dynamic32). Per-scene optimization methods serve as an upper-bound reference.

### Full-sequence interpolation (80 frames)

원논문 Table II. 홀수 프레임 입력, 짝수 프레임 평가. 지표 PSNR↑, SSIM↑, LPIPS↓, Time, Ngs(가우시안 수). Bold/underline은 generalizable 방법 중 최고/차선.

| Method         | PSNR ↑    | SSIM ↑    | LPIPS ↓   | Time   | Ngs  |
| -------------- | --------- | --------- | --------- | ------ | ---- |
| StreetGS (opt) | 24.54     | 0.739     | 0.224     | ~70min | 3M   |
| OmniRe (opt)   | 24.57     | 0.739     | 0.222     | ~80min | 3M   |
| G3R            | 23.15     | 0.636     | –         | 60s    | 3M   |
| G3R*           | 23.18     | 0.653     | 0.406     | 75s    | 3M   |
| **Ours**       | **24.19** | **0.705** | **0.329** | 98s    | 1.2M |
| Ours-f         | 23.93     | 0.703     | 0.356     | 39s    | 1.2M |

Among generalizable methods L2D2-GS is best (24.19 dB, +1.01 over reproduced G3R*) with a more compact 1.2M primitives; the fast variant Ours-f runs in 39 s with marginal degradation. Per-scene StreetGS/OmniRe still yield slightly higher PSNR but need ~70–80 min per scene.

### Short-sequence interpolation (1s snippets)

원논문 Table III. 지표 PSNR↑, SSIM↑, LPIPS↓. Best는 bold.

| Method   | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------- | --------- | --------- | --------- |
| AnySplat | 22.97     | 0.673     | 0.412     |
| STORM    | 19.69     | 0.628     | 0.683     |
| G3R      | 24.35     | 0.686     | –         |
| G3R*     | 24.36     | 0.698     | 0.347     |
| Flux4D   | 23.84     | 0.675     | –         |
| **Ours** | **25.22** | **0.735** | **0.287** |

The gain over G3R is smaller here, as inaccurate geometry in short snippets is easier to compensate by overfitting.

### Cross-dataset generalization (PandaSet → Waymo, zero-shot)

원논문 Table IV. 지표 PSNR↑, SSIM↑, LPIPS↓.

| Method   | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------- | --------- | --------- | --------- |
| STORM    | 20.14     | 0.734     | 0.630     |
| **Ours** | **25.24** | **0.794** | **0.436** |

L2D2-GS gains ~5 dB PSNR and 0.19 LPIPS over STORM under domain shift with no fine-tuning.

### Component ablation (PandaSet, mean over 10 runs)

원논문 Table V. 지표 PSNR↑, SSIM↑, LPIPS↓ (평균값).

| Method                | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| --------------------- | --------- | --------- | --------- |
| L2D2-GS (full)        | **24.19** | **0.705** | **0.329** |
| − consistency penalty | 24.17     | 0.704     | 0.330     |
| − densification       | 23.78     | 0.682     | 0.368     |
| − reparameterization  | 23.41     | 0.667     | 0.396     |
| − independent weights | 23.18     | 0.653     | 0.406     |

Even with the same 1.2M budget via denser init, removing learned densification drops PSNR (24.19 → 23.78), and removing reparameterization drops it further (23.41), confirming both modules are essential. Geometric-prior ablation (Table VI) shows LiDAR + 3D-VFM combined (24.19 PSNR) beats LiDAR-only (24.14) or 3D-VFM-only (24.04).

## 💡 Insights & Impact

- **Reward from reconstruction gain**: The key trick is turning the delayed, implicit benefit of densification into an explicit per-primitive reward by attributing 2D rendering-error reduction back to added Gaussians through the differentiable rasterizer.
- **Stability via manifold constraint**: Reparameterizing scale onto an isotropic-anchored manifold prevents the irreversible needle-like collapse that otherwise poisons early iterations of gradient-fed feed-forward optimization.
- **Efficiency–fidelity bridge**: L2D2-GS closes much of the gap to per-scene optimization (24.19 vs ~24.57 PSNR) while running in ~40–100 s instead of ~70–80 min and using fewer primitives (1.2M vs 3M).
- **Application**: Serves as an engine for closed-loop AD simulation with disentangled dynamic representation enabling vehicle removal and trajectory editing.

## 🔗 Related Work

- Builds on generalizable-optimization methods G3R (gradient-guided refinement) and Flux4D (flow-based unsupervised 4D), and feed-forward reconstruction including AnySplat and STORM; initializes geometry from LiDAR and [VGGT](../reconstruction/vggt.md)/MapAnything-style vision foundation priors.
- Contrasts with per-scene driving reconstruction (Street Gaussians, OmniRe, Desire-GS, AD-GS) that inherit slow per-scene optimization, and with single-pass densification methods (QuickSplat, Generative Densification, GaussianLens) limited to object-centric scenes.
- Related to the recurrent feed-forward refinement line exemplified by ReSplat.

## 📚 Key Takeaways

1. L2D2-GS reframes generalizable dynamic reconstruction as iterative optimize-and-densify, learning where to add Gaussians via a self-supervised, reward-driven policy.
2. A geometric reparameterization anchors Gaussians at an isotropic limit, eliminating the early needle-like degeneracy that plagues gradient-fed feed-forward pipelines.
3. It sets state-of-the-art among generalizable methods on PandaSet full/short sequences and gains ~5 dB zero-shot on Waymo, approaching per-scene quality at a fraction of the time and primitive count.

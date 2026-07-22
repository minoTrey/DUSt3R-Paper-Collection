# DGGT: Feedforward 4D Reconstruction of Dynamic Driving Scenes using Unposed Images (CVPR 2026)

![dggt — architecture](https://arxiv.org/html/2512.03004/x3.png)

_Overall Architecture (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Xiaoxue Chen, Ziyi Xiong, Yuantao Chen, Gen Li, Nan Wang, Hongcheng Luo, Long Chen, Haiyang Sun, Bing Wang, Guang Chen, Hangjun Ye, Hongyang Li, Ya-Qin Zhang, Hao Zhao
- **Institution**: AIR Tsinghua University, Xiaomi EV, The University of Hong Kong, Beijing Academy of Artificial Intelligence
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2512.03004) | [Code](https://github.com/xiaomi-research/dggt)
- **Verification**: CONFIRMED (2026-07-21)
- **TL;DR**: A pose-free feedforward transformer for dynamic driving scenes that predicts per-frame 3D Gaussian maps, camera parameters, dynamic masks, per-pixel 3D motion, and a per-Gaussian lifespan in a single pass, then refines renderings with a single-step diffusion model.

## 🎯 Key Contributions

1. **Pose as output, not input**: Reformulating camera pose as a model output rather than a required input, enabling reconstruction from sparse unposed images and an arbitrary number of views.
2. **Dynamic decomposition with full 3D motion**: A dynamic head splits each Gaussian map into static and dynamic components; a motion head predicts full per-pixel 3D displacement trajectories rather than just velocities (the paper's stated distinction from STORM).
3. **Lifespan parameter**: A per-Gaussian σ that modulates opacity over time, letting the representation express appearance changes on nominally static objects (e.g. lighting variation).
4. **Diffusion-based rendering refinement**: A single-step diffusion post-render module conditioned on a random reference frame that repairs ghosting, disocclusion gaps, and compositing holes.
5. **Instance-level scene editing**: Because dynamic and static Gaussians are separated, vehicles and cyclists can be removed, shifted, or inserted from other scenes.

## 🔧 Technical Details

### Backbone

A ViT encoder patchifies inputs and passes them through a DINO-pretrained feature extractor yielding `F_dino`, which is refined by alternating attention into `F_attn`. Multiple heads consume these features: camera head `H_cam`, Gaussian head `H_gs`, lifespan head `H_life`, dynamic head `H_dy`, motion head `H_motion`, and a lightweight sky head `H_sky`.

An important implementation detail: `F_attn` primarily encodes high-level semantics and lacks detail for appearance reconstruction, so the Gaussian head consumes the _fused_ features — `G^t = H_gs(F_dino, F_attn)`. During training the feature extractor and camera head are frozen to leverage pretrained priors; the remaining heads are trained from scratch.

### Scene Representation

Each frame is a pixel-aligned Gaussian map `G^t ∈ R^{H×W×15}`: RGB color c ∈ R³, mean position μ ∈ R³, rotation quaternion r ∈ R⁴, scale s ∈ R³, opacity o ∈ R, and lifespan σ ∈ R₊ which modulates opacity across timestamps.

### Dynamic Decomposition

The dynamic head predicts `M_d^t = H_dy(F_attn)`, splitting each map by element-wise multiplication:

`G_s^t = G^t ⊙ (1 − M_d^t)`, `G_d^t = G^t ⊙ M_d^t`

The full representation at time t unions the sky Gaussian, _all_ static Gaussians across every frame, and only the current frame's dynamic Gaussians: `Ĝ^t = (∪_{t'} G_s^{t'}) ∪ G_d^t ∪ G_sky`.

### 3D Motion Estimation

A transformer motion head jointly processes 2D images and 3D points from the Gaussian maps, encoding images into multi-scale features associated with 3D points to form a spatio-temporal feature cloud. For timestamp t_a the one-valued pixels of `M_d^{t_a}` become query pixels Q, back-projected to initialize 3D positions and iteratively refined via neighborhood-to-neighborhood attention:

`F(t_a, t_b) = H_motion(Q | G^{t_a}, G^{t_b}, I^{t_a}, I^{t_b}) ∈ R^{q×3}`

The head is initialized from pretrained weights and fine-tuned with a photometric loss on interpolated frames.

### Interpolation

Dynamic Gaussian means at an intermediate time t_i are linearly advected along the predicted motion: `μ_d^{t_i} = μ_d^{t_a} + ω^{t_i} F(t_a, t_b)` with `ω^{t_i} = (t_i − t_a)/(t_b − t_a)`. Camera pose is interpolated with linear translation and SLERP on quaternions.

### Diffusion Refinement

Built on a single-step diffusion framework with a frozen VAE encoder, a UNet denoiser, and a LoRA fine-tuned decoder. A rendered frame `Î^{t_i}` and a randomly sampled reference frame `I_ref` from the input sequence are concatenated frame-wise, encoded, denoised, and decoded: `Ĩ^{t_i} = f_diffusion(Î^{t_i}, I_ref)`. Trained on roughly 2,000 clips curated from the 798 Waymo training scenes.

### Losses

- **Feedforward**: `L_feedforward = L_rgb + λ_opacity L_opacity + λ_dynamic L_dynamic + λ_lifespan L_lifespan`, where `L_rgb = L_ℓ2 + λ_LPIPS L_LPIPS`, the opacity and dynamic terms are binary cross-entropy against sky and dynamic ground-truth masks, and `L_lifespan = ‖σ‖₁` regularizes under the assumption that most of the scene is static.
- **Diffusion**: `L_diffusion = L_Recon + L_LPIPS + λ_Gram L_Gram`, with the Gram-matrix style loss over VGG-16 features added for sharpness.

Each training iteration samples N ∈ [4, 8] input images with 2N ground-truth targets; the model predicts 2N interpolated frames.

### Compute and Evaluation Protocol

Training used an eight-card H200 configuration, completing in approximately 24 hours with convergence around 5,000 iterations. All evaluations were run on NVIDIA A100 GPUs to match STORM's setup. For Table 1, inputs are frames 0, 5, 10, 15 predicting frames 0–19 from the forward-facing, front-left, and front-right cameras. Depth is compared as **D-RMSE** after a linear alignment, since pose-free methods (NoPoSplat and DGGT) predict only relative depth.

## 📊 Results

### Novel View Synthesis on Waymo

원논문 Table 1. 세 개의 입력 뷰로 인접 프레임 사이의 중간 프레임을 보간하는 과제다. `*`는 저자들이 직접 재현한 결과다.

| Method       | PSNR ↑    | SSIM ↑    | D-RMSE ↓ | Inference time | Dynamic | Pose-free |
| ------------ | --------- | --------- | -------- | -------------- | ------- | --------- |
| EmerNeRF     | 24.51     | 0.738     | 33.99    | 14min          | ✓       | ✗         |
| 3DGS         | 25.13     | 0.741     | 19.68    | 23min          | ✗       | ✗         |
| PVG          | 22.38     | 0.661     | 13.01    | 27min          | ✓       | ✗         |
| DeformableGS | 25.29     | 0.761     | 14.79    | 29min          | ✓       | ✗         |
| LGM          | 18.53     | 0.447     | 9.07     | 0.06s          | ✗       | ✗         |
| GS-LRM       | 25.18     | 0.753     | 7.94     | **0.02s**      | ✗       | ✗         |
| MVSplat      | 20.56     | 0.697     | 10.13    | 0.08s          | ✗       | ✗         |
| NoPoSplat    | 24.31     | 0.751     | 9.08     | 23.22s         | ✗       | ✓         |
| DepthSplat   | 23.26     | 0.696     | 10.05    | 0.11s          | ✗       | ✗         |
| STORM\*      | 26.05     | 0.819     | 5.91     | 0.50s          | ✓       | ✗         |
| STORM        | 26.38     | 0.794     | 5.48     | 0.18s          | ✓       | ✗         |
| VGGT++       | 22.50     | 0.749     | 3.80     | 0.24s          | ✗       | ✓         |
| **DGGT**     | **27.41** | **0.846** | **3.47** | 0.39s          | ✓       | ✓         |

DGGT is the only entry marked both Dynamic and Pose-free, and it leads all three quality metrics — though GS-LRM, LGM, MVSplat, DepthSplat, and STORM are all faster. The paper attributes VGGT++'s weak PSNR/SSIM to the limited RGB detail preserved in attention features, consistent with its own decision to fuse `F_dino` back into the Gaussian head.

### Cross-Dataset Generalization

원논문 Table 2. Zero-shot는 Waymo로 학습한 모델을 그대로 평가한 것이고, Trained는 대상 데이터셋에서 따로 학습한 것이다.

| Setting   | Method     | nuScenes PSNR ↑ | SSIM ↑    | LPIPS ↓   | Argoverse2 PSNR ↑ | SSIM ↑    | LPIPS ↓   |
| --------- | ---------- | --------------- | --------- | --------- | ----------------- | --------- | --------- |
| Zero-shot | MVSplat    | 17.84           | 0.563     | 0.451     | 18.67             | 0.647     | 0.304     |
| Zero-shot | NoPoSplat  | 19.75           | 0.545     | 0.394     | 22.00             | 0.646     | 0.237     |
| Zero-shot | DepthSplat | 19.52           | 0.601     | 0.376     | 22.05             | 0.636     | 0.280     |
| Zero-shot | STORM      | 17.77           | 0.669     | 0.394     | 20.83             | 0.542     | 0.326     |
| Zero-shot | **DGGT**   | **25.31**       | **0.794** | **0.152** | **26.34**         | **0.812** | **0.155** |
| Trained   | STORM      | 24.54           | 0.784     | 0.267     | 24.97             | 0.791     | 0.240     |
| Trained   | **DGGT**   | **26.63**       | **0.813** | **0.122** | **26.96**         | **0.831** | **0.118** |

Notably, zero-shot DGGT beats _trained_ STORM on both datasets. The paper credits this to the pose-free design: without explicit camera poses the model cannot overfit to dataset-specific trajectory patterns or camera configurations.

### Scaling with Number of Input Views

원논문 Table 3. Reconstruction은 입력 프레임에 대한 것이고, NVS는 보간된 프레임에 대한 것이다.

| Method   | #Views | Recon PSNR ↑ | SSIM ↑    | D-RMSE ↓  | NVS PSNR ↑ | SSIM ↑    | D-RMSE ↓  |
| -------- | ------ | ------------ | --------- | --------- | ---------- | --------- | --------- |
| STORM    | 4      | 26.55        | 0.851     | 6.139     | 26.05      | 0.819     | 5.914     |
| **DGGT** | 4      | **30.54**    | **0.884** | **3.352** | **27.41**  | **0.846** | **3.471** |
| STORM    | 8      | 25.11        | 0.807     | 6.054     | 25.44      | 0.807     | 5.470     |
| **DGGT** | 8      | **31.41**    | **0.895** | **3.315** | **27.74**  | **0.858** | **3.455** |
| STORM    | 16     | 23.69        | 0.765     | 5.700     | 22.98      | 0.723     | 5.836     |
| **DGGT** | 16     | **30.66**    | **0.887** | **3.337** | **28.14**  | **0.885** | **3.480** |

This is the strongest evidence for the scalability claim: STORM's reconstruction PSNR falls monotonically from 26.55 to 23.69 as views grow from 4 to 16, while DGGT stays in the 30.5–31.4 band and its NVS PSNR actually improves.

### 3D Motion Estimation on Waymo Scene Flow

원논문 Table 5. 지표는 STORM을 따른다.

| Method   | EPE3D (m) ↓ | Acc5 (%) ↑ | Acc10 (%) ↑ | θ (rad) ↓ |
| -------- | ----------- | ---------- | ----------- | --------- |
| NSFP     | 0.698       | 42.17      | 54.26       | 0.919     |
| NSFP++   | 0.711       | 53.10      | 63.02       | 0.989     |
| STORM    | 0.276       | 81.12      | 85.61       | 0.658     |
| **DGGT** | **0.183**   | **85.42**  | **90.42**   | **0.328** |

### Ablation

원논문 Table 4.

| Method        | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ------------- | --------- | --------- | --------- |
| w/o lifespan  | 24.21     | 0.774     | 0.169     |
| w/o diffusion | 27.32     | 0.844     | **0.108** |
| **Full**      | **27.41** | **0.846** | 0.109     |

Reported honestly: the lifespan parameter carries almost all the ablation signal (PSNR 27.41 → 24.21 without it). Diffusion refinement is nearly a wash numerically — +0.09 PSNR, +0.002 SSIM, and _slightly worse_ LPIPS (0.109 vs 0.108). The authors acknowledge this directly, arguing PSNR/SSIM emphasize per-pixel fidelity while the diffusion module corrects structural defects and reconstructs missing content, and retain it for downstream usability. The supporting evidence for that argument is qualitative (Fig. 5, Fig. 6) and no metric is reported for it.

## 💡 Insights & Impact

### Pose-Free as a Generalization Mechanism

The most interesting result in the paper is not the Waymo headline but Table 2, where zero-shot DGGT outperforms STORM trained on the target dataset. The proposed explanation is causal rather than incidental: methods that consume poses learn dataset-specific trajectory priors and camera rigs, and those priors are exactly what breaks under domain transfer. Treating pose as an output removes the channel through which that overfitting happens.

### The Lifespan Parameter Is Doing More Than Expected

A per-Gaussian temporal opacity envelope sounds like a minor regularizer, but removing it costs 3.2 PSNR — more than any other component. The paper's explanation is that "static" in a driving log is not really static: lighting changes over a 20-frame window, and without a temporal opacity modulation the model has no way to express appearance variation on geometry it has correctly labeled static. The ℓ1 prior on σ encodes the complementary assumption that most of the scene _is_ static.

### Full Trajectories vs Velocities

The stated advance over STORM's velocity model is predicting full 3D displacement `F(t_a, t_b)` between arbitrary timestamp pairs, which captures non-linear dynamics and permits synthesis at any intermediate time. Table 5 supports this — EPE3D 0.276 → 0.183 and angular error roughly halved (0.658 → 0.328).

### An Honest Weak Component

Sections rarely admit this cleanly: the diffusion refinement's numeric contribution is within noise and it makes LPIPS marginally worse. Keeping it is a judgment call about editing artifacts, and the paper says so rather than dressing up the numbers. It also carries real cost — DGGT's 0.39s inference is slower than STORM's 0.18s.

### Scope

Everything here is driving-specific: Waymo, nuScenes, Argoverse2, a sky head, vehicle/cyclist editing, and ground-truth masks derived from 3D bounding boxes plus off-the-shelf segmentation. The generality of the pose-free-as-generalization argument beyond driving logs is untested in this paper.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the alternating-attention aggregator design DGGT's backbone follows; VGGT++ (VGGT plus a Gaussian head) is a baseline in Table 1.
- [DUSt3R](../foundation/dust3r.md) — the feed-forward pointmap paradigm this line of work descends from.
- [MonST3R](monst3r.md) — dynamic-scene extension of the pointmap paradigm via video fine-tuning.
- [CUT3R](cut3r.md) — streaming dynamic reconstruction with a persistent state.
- [Any4D](any4d.md) — feed-forward 4D reconstruction in a general (non-driving) setting.
- [Dynamic Point Maps](dynamic-point-maps.md) — an alternative 4D representation for moving scenes.
- [InstantSplat](../gaussian-splatting/instantsplat.md) — pose-free Gaussian splatting from sparse views.

## 📚 Key Takeaways

1. **Making pose an output improves cross-dataset transfer.** Zero-shot DGGT beats target-trained STORM on both nuScenes and Argoverse2.
2. **Lifespan is the load-bearing component.** Removing it costs 3.2 PSNR — far more than the diffusion module contributes.
3. **Scalability is the differentiator.** STORM degrades from 26.55 to 23.69 reconstruction PSNR going from 4 to 16 views; DGGT stays flat.
4. **Full 3D trajectories beat velocity models.** EPE3D 0.276 → 0.183 against STORM on Waymo Scene Flow.
5. **Diffusion refinement is qualitative, not quantitative.** It buys +0.09 PSNR and slightly worse LPIPS; its justification is artifact repair for editing, shown only in figures.

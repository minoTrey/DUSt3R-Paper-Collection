# NoPo4D: No Pose, No Problem in 4D — Feed-Forward Dynamic Gaussians from Unposed Multi-View Videos (arXiv preprint)

## 📋 Overview

- **Authors**: Matteo Balice, Yanik Künzi, Chenyangguang Zhang, Matteo Matteucci, Marc Pollefeys, Sungwhan Hong
- **Institution**: Politecnico di Milano, ETH Zürich, ETH AI Center
- **Venue**: arXiv preprint (2026-05)
- **Note**: 자체 프로젝트 페이지 BibTeX가 arXiv preprint. 떠도는 CVPR 2026 주장은 1차 출처가 없다. <https://bralani.github.io/nopo4d_html/>
- **Links**: [Paper](https://arxiv.org/abs/2605.22190) | [Project Page](https://bralani.github.io/nopo4d_html/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first feed-forward system to jointly handle dynamic content, multi-view input, and unknown camera poses, achieved by decomposing Gaussian motion into per-pixel image-plane shifts plus a depth change so that optical flow can supervise motion directly without any differentiable rendering step.

## 🎯 Key Contributions

1. **Filling an empty quadrant**: Prior feed-forward work handles dynamics _or_ multi-view _or_ pose-free, never all three in general environments (Table 1). NoPo4D claims that intersection.
2. **Decomposed motion parameterization**: Splitting Gaussian motion into 2D pixel shifts (Δx, Δy) and a depth displacement Δd, which permits direct supervision from pseudo ground-truth optical flow — sidestepping both the differentiable rendering that couples posed methods to pose accuracy and the 3D motion ground truth that pose-free methods otherwise require.
3. **Bidirectional motion encoder**: Joint self-attention over 2CN tokens (all cameras at frame t plus all cameras at frame t+1) for cross-view and cross-frame aggregation.
4. **View-dependent opacity**: Spherical-harmonic opacity coefficients acting as a learned confidence metric that lets unreliable Gaussians go transparent from viewpoints where geometry disagrees across cameras.
5. **Optional post-optimization**: A 100-step test-time refinement following AnySplat that pushes the system past per-scene optimization SOTA.

## 🔧 Technical Details

### Setup

C uncalibrated, time-synchronized video streams `I = {(I_t^c)_{t=1}^T}_{c=1}^C`, with the cameras assumed to form a **static rig** (as in Ego-Exo4D captures). NoPo4D predicts per-camera intrinsics K̂_c and extrinsics (R̂_c, t̂_c), obtained by averaging the backbone's per-frame predictions across t, plus G 4D Gaussians carrying static attributes (mean μ, covariance Σ, opacity α, color c) and dynamic ones (temporal center τ, lifespan l, and forward/backward linear and angular velocities v^±, ω^± permitting asymmetric motion around the temporal center).

### Backbone

The pretrained transformer of **Depth Anything 3**. Frames pass through frozen within-view self-attention layers; sinusoidal temporal tokens encoding each frame's timestamp are injected before the _trainable_ alternating within-view and cross-view attention layers. Frozen pretrained heads predict per-frame depth, intrinsics, and extrinsics; keeping these frozen prevents overfitting and yields more stable training.

### Gaussian Means

Each depth map is unprojected to a world-space point map `P̂_t^c = Π⁻¹(D̂_t^c, R̂_c, t̂_c, K̂_c)`. One Gaussian is instantiated per pixel per frame, indexed g = (c, t, x, y), with μ_g set to the corresponding point-map entry.

### View-Dependent Opacity

Opacity is parameterized by spherical harmonic coefficients `α_g ∈ R^{(k+1)²}` of order k rather than the scalar of standard 3DGS. The stated rationale: in a pose-free multi-view dynamic setting, geometry prediction is imperfect, so Gaussians misalign across views and timesteps; SH opacity lets the model learn to hide them from problematic viewpoints.

### Decomposed Motion

A DPT head decodes per-pixel 2D shifts (Δx, Δy) — bounded via tanh and scaled to (W, H) — plus a depth displacement Δd:

`x' = x + Δx`, `y' = y + Δy`, `D̂_{t+1}^c(x,y) = D̂_t^c(x,y) + Δd`

Source and displaced pixels are unprojected into camera space using K̂_c and differenced to give ΔX_cam, then rotated into world coordinates and scaled by the temporal interval: `v_g^+ = R̂_c ΔX_cam / Δt`. The backward velocity is computed symmetrically from the preceding frame's features.

This contrasts explicitly with prior feed-forward dynamic methods that predict 3D Gaussian velocities directly.

### Motion Encoder

For each consecutive pair (t, t+1), tokens from all C cameras at frame t are concatenated with those at frame t+1, with two learnable embeddings tagging source vs neighbour. Joint self-attention over the 2CN tokens aggregates across views and time. Outputs are split into forward and backward halves and decoded by a shared DPT head producing (Δx, Δy), Δd, angular velocities ω^±, a per-pixel **motion gate** ρ_g ∈ (0,1) suppressing motion in static regions, a temporal covariance σ_g, and a temporal center τ_g anchored to the source frame's timestamp.

### Losses

`L = L_recon + λ_motion L_motion + λ_consis L_consis + L_distill`

- **Reconstruction**: `L_recon = λ_MSE L_MSE + λ_SSIM L_SSIM + λ_LPIPS L_LPIPS`, evaluated only on rendered target frames.
- **Motion**: aligns predicted pixel shifts with pseudo ground-truth optical flow from SEA-RAFT, as an ℓ1 loss over only those pixels with ground-truth shift magnitude exceeding 2 pixels (`Ω' = {p : ‖f*(p)‖₂ > 2}`). The paper explains the alternative it rejects — rendering 2D flow from predicted velocities and comparing to f\* — because rendering introduces dependence on Gaussian alignment and amplifies pose-induced errors. Since each Gaussian corresponds one-to-one with an input pixel, the predicted pixel shift already encodes its 2D motion.
- **Consistency**: `λ_consis (1/|Ω|) Σ ‖D̂(p) − D(p)‖₂²`, matching rendered depth to backbone priors.
- **Distillation**: from the frozen DA3 Giant model using pseudo-labels {T\*, D\*, ∇D\*} — Huber pose loss plus depth and normal-gradient ℓ2 terms.

### Pose Alignment for Target-View Rendering

Because the model is pose-free, rendering target views during training needs alignment. A two-pass strategy is used: pass 1 processes only context frames, producing Gaussians and context poses defining the scene frame; pass 2 processes all frames under `no_grad`, giving fresh context and target poses; Umeyama alignment between the two context-pose sets yields a closed-form Sim(3) mapping. Because pass 2 is detached, the rendering loss supervises only the Gaussians, not the encoder's pose predictions. The same strategy is used at inference.

### Training

Two stages of 20,000 steps each on ~2,900 Ego-Exo4D scenes: first single-camera viewpoints (static representations + motion head initialization), then 16-frame batches across 1–4 cameras with temporal stride sampled from 4–8, warmed up over the first 2,000 steps. Frames undistorted and downsampled to 796 × 448 (max 448 on the longer side), with randomized aspect ratios in [0.5, 1.0], random center-cropping (77–100%), and horizontal flipping.

Backbone: Depth Anything 3 Large. AdamW with learning rates 5×10⁻⁶ (backbone alternating attention), 5×10⁻⁵ (motion encoder), 1×10⁻⁴ (velocity DPT and Gaussian head); 1,000-step linear warmup and cosine annealing to 1/10 of the initial rate. Loss weights: λ_MSE = 1, λ_LPIPS = 0.5, λ_SSIM = 0.05, λ_consis = 0.1, λ_flow = 0.02, λ_pose = 1.0, λ_depth = 0.1, λ_normal = 0.1. Batch size 1 per GPU at 448 × 448 on 4 NVIDIA GH200s.

Post-optimization: prune Gaussians with opacity below 0.01, then 100 steps, under 5 seconds per scene.

### Evaluation Protocol

Chunk-based across all four benchmarks: each scene is partitioned into chunks of 5 consecutive timestamps, with 4 surrounding frames as input context and the middle frame held out as target. Each method synthesizes the target frame at each input camera viewpoint; PSNR/SSIM/LPIPS are averaged across cameras, chunks, and test scenes. Capped at 60 chunks per scene for ExoRecon and 100 for the others.

## 📊 Results

### Capability Comparison

원논문 Table 1. FF는 feed-forward 추론, Unposed는 GT 포즈 불필요, MV는 다중뷰 입력, Dyn.은 동적 장면 모델링, General은 특정 도메인에 한정되지 않음을 뜻한다.

| Method          | Type   | FF  | Unposed | MV  | Dyn. | General |
| --------------- | ------ | --- | ------- | --- | ---- | ------- |
| NoPoSplat       | Static | ✓   | ✓       | ✓   | ✗    | ✓       |
| FLARE           | Static | ✓   | ✓       | ✓   | ✗    | ✓       |
| AnySplat        | Static | ✓   | ✓       | ✓   | ✗    | ✓       |
| 4DGT            | Dyn.   | ✓   | ✗       | ✗   | ✓    | ✓       |
| NeoVerse        | Dyn.   | ✓   | ✓       | ✗   | ✓    | ✓       |
| DGGT            | Dyn.   | ✓   | ✓       | ✓   | ✓    | ✗       |
| Shape of Motion | Opt.   | ✗   | ✗       | ✗   | ✓    | ✓       |
| MonoFusion      | Opt.   | ✗   | ✗       | ✓   | ✓    | ✓       |
| **NoPo4D**      | Dyn.   | ✓   | ✓       | ✓   | ✓    | ✓       |

### In-Distribution: ExoRecon

원논문 Table 2. FF는 feed-forward 추론을 뜻한다. 공정한 비교를 위해 DGGT를 NoPo4D와 같은 Ego-Exo4D 파생 학습 데이터로 재학습했다 (DGGT (EgoExo4D)).

| Method                 | FF  | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ---------------------- | --- | --------- | --------- | --------- |
| Dyn3D-GS               | ✗   | 24.28     | 0.692     | 0.539     |
| MV-SOM                 | ✗   | 26.91     | 0.890     | 0.138     |
| MonoFusion             | ✗   | 30.43     | **0.930** | **0.060** |
| **NoPo4D (post-opt.)** | ✗   | **31.95** | 0.928     | 0.075     |
| MoVies                 | ✓   | 18.78     | 0.725     | 0.288     |
| DGGT                   | ✓   | 19.67     | 0.645     | 0.417     |
| DGGT (EgoExo4D)        | ✓   | 20.44     | 0.704     | 0.418     |
| NeoVerse               | ✓   | 20.03     | 0.714     | 0.354     |
| **NoPo4D**             | ✓   | **29.15** | **0.886** | **0.125** |

Reported honestly: the post-optimized variant leads PSNR but MonoFusion — a per-scene optimization method with known calibration — still holds the best SSIM and LPIPS. Among feed-forward methods the gap is large (29.15 vs 20.44 for the strongest baseline).

### Out-of-Distribution Generalization

원논문 Table 3. NoPo4D는 두 벤치마크 어느 쪽으로도 학습되지 않았다. NeoVerse는 Kubric으로 학습되어 그 벤치마크에서는 in-distribution이다.

| Method                 | Immersive LF PSNR ↑ | SSIM ↑    | LPIPS ↓   | Kubric PSNR ↑ | SSIM ↑    | LPIPS ↓   |
| ---------------------- | ------------------- | --------- | --------- | ------------- | --------- | --------- |
| MoVies                 | 16.12               | 0.650     | 0.410     | 14.49         | 0.720     | 0.260     |
| NeoVerse               | 19.83               | 0.680     | 0.360     | 16.86         | 0.500     | 0.520     |
| DGGT                   | 20.65               | 0.700     | 0.360     | 20.14         | 0.530     | 0.430     |
| DGGT (EgoExo4D)        | 20.23               | 0.685     | 0.453     | 18.22         | 0.551     | 0.522     |
| **NoPo4D**             | 21.63               | 0.740     | 0.280     | 23.61         | 0.739     | 0.256     |
| **NoPo4D (post-opt.)** | **24.04**           | **0.817** | **0.245** | **28.17**     | **0.838** | **0.159** |

### View Synthesis on N3DV

원논문 Table 4. 세 가지 시점 구성 — 원래 입력 카메라, 중간 정도의 신규 시점 (5.7°–27.7° 회전), 극단적 신규 시점 (34.6°–71.9° 회전).

| Method                 | Input PSNR ↑ | SSIM ↑    | LPIPS ↓   | Moderate PSNR ↑ | SSIM ↑    | LPIPS ↓   | Extreme PSNR ↑ | SSIM ↑    | LPIPS ↓   |
| ---------------------- | ------------ | --------- | --------- | --------------- | --------- | --------- | -------------- | --------- | --------- |
| MoVies                 | 14.10        | 0.556     | 0.505     | 14.54           | 0.435     | 0.582     | 9.63           | 0.162     | 0.716     |
| NeoVerse               | 24.50        | 0.789     | 0.313     | 18.63           | 0.530     | 0.449     | 13.32          | 0.423     | 0.601     |
| DGGT                   | 23.08        | 0.749     | 0.268     | 17.93           | 0.532     | 0.435     | **15.87**      | 0.449     | 0.557     |
| DGGT (EgoExo4D)        | 22.49        | 0.713     | 0.356     | 6.84            | 0.223     | 0.626     | 10.43          | 0.419     | 0.631     |
| **NoPo4D**             | 28.43        | 0.905     | 0.144     | **19.84**       | **0.578** | **0.315** | 15.69          | **0.467** | **0.520** |
| **NoPo4D (post-opt.)** | **31.79**    | **0.956** | **0.089** | 19.93           | 0.570     | 0.320     | 15.91          | 0.449     | 0.531     |

At extreme viewpoints DGGT edges out feed-forward NoPo4D on PSNR (15.87 vs 15.69). The paper argues from Fig. 3 that pixel-aligned metrics under-credit confident-but-shifted predictions relative to blurry-but-aligned ones, and that NoPo4D is visually cleaner there — but it does not claim the numeric win, and the supporting evidence is qualitative.

### Ablation: Architectural Components

원논문 Table 5a. ExoRecon 기준, 각 행은 전체 파이프라인에서 한 구성 요소를 제거하거나 교체한 것이다.

| Method               | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------------------- | --------- | --------- | --------- |
| No opacity SH        | 21.61     | 0.758     | 0.247     |
| No motion branch     | 22.97     | 0.856     | 0.161     |
| No decomposition     | 27.67     | 0.865     | 0.129     |
| No temporal encoding | 27.69     | 0.861     | **0.125** |
| **NoPo4D**           | **29.15** | **0.886** | **0.125** |

View-dependent opacity is the single most important component (−7.5 PSNR without it), followed by the bidirectional motion encoder (−6.2). The motion decomposition itself costs only 1.5 PSNR when replaced by direct 3D velocity prediction with flow supervision routed through differentiable rendering. However, the paper reports that removing **both** the decomposition and the flow loss causes training to fail outright — velocity magnitudes grow without bound and the loss diverges within the first few thousand steps. That configuration has no table row, only this text description.

### Ablation: Auxiliary Losses

원논문 Table 5b. 재구성 손실 L_recon은 항상 활성이다.

| Recon. | Distill. | Consis. | Flow | PSNR ↑    | SSIM ↑    | LPIPS ↓ |
| ------ | -------- | ------- | ---- | --------- | --------- | ------- |
| ✓      | ✗        | ✗       | ✗    | 25.09     | 0.829     | 0.162   |
| ✓      | ✗        | ✓       | ✗    | 3.51      | 0.238     | 0.803   |
| ✓      | ✗        | ✓       | ✓    | 25.91     | 0.815     | 0.159   |
| ✓      | ✓        | ✗       | ✓    | 28.02     | 0.867     | 0.122   |
| ✓      | ✓        | ✓       | ✗    | 28.19     | 0.869     | 0.125   |
| ✓      | ✓        | ✓       | ✓    | **29.15** | **0.886** | 0.125   |

The catastrophic row is recon + consistency alone at 3.51 PSNR: without geometric grounding from distillation or flow, consistency merely constrains rendered depth to match backbone-predicted depth with nothing anchoring geometry to the target, and Gaussians collapse together to satisfy it trivially. Consistency is a regularizer, not a supervisory signal. Leave-one-out drops are −3.24 (distillation), −1.13 (consistency), −0.96 (flow).

### Ablation: Backbone Fine-Tuning Strategy

원논문 Table 6. ExoRecon 기준.

| Method                           | Trainable params | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------------------------------- | ---------------- | --------- | --------- | --------- |
| Unfreeze camera and depth heads  | 525 M            | 16.94     | 0.654     | 0.354     |
| Full fine-tuning                 | 621 M            | 25.09     | 0.829     | 0.162     |
| Freeze backbone                  | 266 M            | 25.68     | 0.804     | 0.151     |
| Fine-tune last 4 layers          | 318 M            | 26.32     | 0.841     | 0.152     |
| Fine-tune last 8 layers          | 369 M            | 27.28     | 0.853     | 0.140     |
| **Ours (16 alternating layers)** | 470 M            | **29.15** | **0.886** | **0.125** |

Unfreezing the DA3 depth and camera heads is the most damaging option at −12.4 PSNR — noisy gradients from the dynamic Gaussian losses corrupt the geometric priors, which makes the unprojected point map and therefore all Gaussian means unreliable. Full fine-tuning also underperforms (−4.3), and freezing everything under-fits (−3.7). Note that full fine-tuning uses _more_ parameters (621 M) than the best configuration (470 M) and does worse.

### Scalability to More Cameras

Figure 4 plots quality and cost against C ∈ {2, …, 12} on N3DV, where NoPo4D was never trained beyond C = 4. Text-reported values: NoPo4D loses ~4.7 PSNR from C = 2 to C = 12, compared to ~6.9 for NeoVerse and ~3.6 for DGGT. Cost scales near-linearly for NoPo4D, NeoVerse, and MoVieS, while DGGT's memory and inference time grow super-linearly, reaching ~50 GB and ~15 seconds at 12 cameras; NoPo4D remains under 27 GB and 5 seconds at the same scale. The curves themselves are plots without printed per-point values and are not transcribed here.

The abstract's "orders of magnitude faster" claim against per-scene optimization is stated without an accompanying ratio for any specific setting, so no speedup factor is reported here.

## 💡 Insights & Impact

### The Decomposition Is About Supervision, Not Representation

The clever part of NoPo4D is not that 2D shift + depth change is a better motion representation — Table 5a shows it is worth only 1.5 PSNR on its own. It is that this parameterization makes optical flow a _direct_ supervision target. Because each Gaussian is instantiated one-to-one with an input pixel, the predicted pixel shift already is the Gaussian's 2D motion; there is no need to render flow and no dependence on pose accuracy or Gaussian alignment in the gradient path. In a pose-free setting, every gradient that passes through rendering also passes through pose error, and that is the coupling the whole design is built to avoid.

### And It Is Load-Bearing for Trainability

The 1.5 PSNR reading understates the case. The text-only result — that removing decomposition _and_ flow loss diverges within a few thousand steps — indicates the two together are what bound the motion prediction at all. The ablation table can only measure configurations that converge.

### Opacity as Confidence

Making opacity view-dependent is the largest single contributor (7.5 PSNR). The mechanism is worth generalizing: when geometry is predicted rather than measured, per-primitive misalignment is inevitable, and a scalar opacity forces the model to either keep a bad Gaussian everywhere or delete it everywhere. SH opacity gives it a third option — be visible only from viewpoints where you happen to be right. That is a confidence estimate learned without any explicit uncertainty supervision.

### Freeze the Geometry Heads

Table 6's most transferable lesson is that the pretrained depth and camera heads must stay frozen. Everything downstream — Gaussian means, unprojection, alignment — depends on them, so gradients from a noisy dynamic objective flowing back into them is not fine-tuning but corruption. The 12.4 PSNR collapse is severe enough to be a general warning for anyone attaching new heads to a geometry foundation model.

### Honest Limits

MonoFusion still holds SSIM and LPIPS on ExoRecon; DGGT edges PSNR at extreme N3DV viewpoints; the static-rig assumption is baked into the per-camera pose averaging; and absolute quality at extreme novel views remains low for every method (best PSNR 15.91). The paper documents failure cases in an appendix figure.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md) — the pretrained backbone, and the frozen Giant model used as distillation teacher.
- [DGGT](dggt.md) — the closest existing method (unposed multi-view dynamic), retrained here on matched data; marked domain-restricted in Table 1.
- [Any4D](any4d.md) — feed-forward 4D reconstruction in an adjacent formulation.
- [MonST3R](monst3r.md) — dynamic-scene pointmap reconstruction requiring optimization.
- [CUT3R](cut3r.md) — streaming dynamic reconstruction with a persistent state.
- [InstantSplat](../gaussian-splatting/instantsplat.md) — pose-free Gaussian splatting for static sparse views.
- [PAGE-4D](page-4d.md) — another 4D perception model built on a static geometry foundation model.
- [VGGT](../reconstruction/vggt.md) — the alternating within-view / cross-view attention pattern DA3 and this work inherit.

## 📚 Key Takeaways

1. **Parameterize motion so supervision can bypass rendering.** In a pose-free system, any loss routed through differentiable rendering inherits pose error; 2D pixel shifts let optical flow supervise motion directly.
2. **Decomposition and flow loss are jointly necessary.** Removing both makes training diverge outright, a result the ablation table cannot show.
3. **View-dependent opacity is the biggest single win** (+7.5 PSNR), functioning as learned per-viewpoint confidence under imperfect predicted geometry.
4. **Freeze the pretrained geometry heads.** Unfreezing them costs 12.4 PSNR — more than any other configuration choice, and more parameters trained is not better (621 M full fine-tuning loses to 470 M targeted).
5. **Consistency losses regularize, they do not supervise.** Recon + consistency alone collapses to 3.51 PSNR via degenerate Gaussian collapse.

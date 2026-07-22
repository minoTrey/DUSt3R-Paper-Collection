# SHOW: Scene and Human in One World — Reconstruction in a Feedforward Pass (arXiv preprint (2026-06))

![show — architecture](https://arxiv.org/html/2606.27720v1/x1.png)

_Our method can produce better human and scene alignment under monocular human-centric video input (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Boao Shi, Qiao Feng, Yiming Huang, Lingjie Liu
- **Institution**: University of Pennsylvania
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.27720) | [Project Page](https://bowieshi.github.io/SHOW-project-page/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A mask-promptable feed-forward framework that couples VGGT-based scene point-map prediction with SMPL-X human mesh recovery in a shared metric space, so human semantic/scale priors and scene geometry mutually constrain each other from monocular human-centric video.

## 🎯 Key Contributions

1. **Unified human–scene feed-forward framework**: Jointly estimates dense scene geometry and SMPL-X human meshes in a shared metric coordinate system, reducing scale ambiguity and the cascading errors of multi-stage alignment pipelines.
2. **Bidirectional human–scene coupling**: Injects human semantic and metric-scale priors into scene reconstruction, while using scene geometry to constrain human mesh recovery and global localization — enabling joint learning of human-aware geometric features and geometry-constrained human features.
3. **Mask-as-prompt mechanism**: Uses human masks as dense 2D prompts for the visual geometry foundation model, giving target-aware feature extraction, improved human surface localization, and robustness to clutter and multi-person interference.
4. **Human–scene alignment evaluation protocol**: Proposes two new metrics — Human–Scene Chamfer (HS-CF) and Human–Scene Variance (HS-V) — plus benchmarking of existing feed-forward methods.

## 🔧 Technical Details

### Problem Setup

Given a monocular video I = {I_t}, for each frame the model predicts a normalized partial 3D point map P̄_t and reconstructs all visible humans in the same coordinate frame. Each human instance H_{t,i} = {θ, β, τ, s} carries pose, shape, global translation, and a scalar scale factor s_{t,i} that maps the normalized point map to the metric scale of the reconstructed body (P_{t,i} = s_{t,i} · P̄_t).

### Stage 1 — Human-Aware Geometry Encoding

- **Backbone**: Adapts VGGT for human-centric reconstruction.
- **Mask encoder**: A human foreground mask M_t (from an off-the-shelf segmentation model, e.g. SAM 2 / SAM 3) is encoded and fused into VGGT latent geometry features via an adaptation module.
- **Auxiliary DensePose head**: Supervises the shared latent feature with a foreground-weighted DensePose regression loss (weight 1/r_t for human pixels, 1/(1−r_t) otherwise, with r_t the foreground pixel ratio) so features encode human body information rather than merely separating foreground from background. DensePose is used at training time only.
- **Loss**: L_geo = L_camera + L_depth + L_pmap + λ_dp · L_dp (geometry losses follow VGGT; DensePose loss injects human-specific supervision).

### Stage 2 — Geometry-Aware SMPL-X Decoding

- Human feature tokens come from PromptHMR; paired with the adapted geometry feature and ray-based positional encodings (RayEnc) computed from predicted camera intrinsics.
- A lightweight Transformer decoder regresses SMPL-X parameters from three query tokens (SMPL token, scale token, register token) via K rounds of self-attention among tokens followed by cross-attention to human and geometry features.
- **Asymmetric cross-attention**: SMPL and register tokens attend to both human and geometry features; the scale token attends only to geometry features (grounding scale in the reconstructed scene).
- In this stage the human-aware geometry encoder is frozen; the decoder is trained with standard human reconstruction losses L_hmr.

### Stage 3 — Joint Training for Human–Scene Alignment

- **Scale consistency**: L_scale supervises the predicted scale factor in log space; L_temp regularizes per-instance scale toward its sequence-level average for temporal stability.
- **SMPL-guided point-map alignment**: L_align is a Chamfer loss pulling the rescaled human-region point map toward detached (stop-gradient) visible SMPL-X surface points.
- **Total objective**: L_total = L_geo + L_hmr + λ_scale·L_scale + λ_temp·L_temp + λ_align·L_align.

### Implementation

- Stage 1: geometry backbone trained on 4 NVIDIA B200 GPUs for 100 epochs.
- Stage 2: SMPL-X decoder trained on 2 NVIDIA B200 GPUs for 100 epochs.
- Stage 3: end-to-end training on 4 NVIDIA B200 GPUs for 200 epochs.
- **Training data**: BEDLAM2.0 synthetic dataset; sequences with inaccurate HDRI-based depth rendering discarded, leaving 4,250 valid sequences. Videos downsampled to 6 FPS, 5-frame clips.

## 📊 Results

Metric spaces: camera-space local accuracy on 3DPW and EMDB (subset 1) via PA-MPJPE / MPJPE / PVE (mm); world-space global motion on EMDB (subset 2) and RICH via World-aligned MPJPE (WA), World MPJPE (W), and Root Translation Error (RTE, %). Human–scene consistency via HS-CF and HS-V (5%–95% and 10%–90% percentile filtering give the ₅/₁₀ variants).

### Local Human Mesh Reconstruction

원논문 Table 1. Local mesh reconstruction. PA: PA-MPJPE (mm). Lower is better for all metrics. "w/o sc." = no scene branch; "w/ sc." = joint human–scene methods.

| Cat.    | Method    | 3DPW PA ↓ | 3DPW MPJ ↓ | 3DPW PVE ↓ | EMDB-1 PA ↓ | EMDB-1 MPJ ↓ | EMDB-1 PVE ↓ |
| ------- | --------- | --------- | ---------- | ---------- | ----------- | ------------ | ------------ |
| w/o sc. | CLIFF     | 43.0      | 69.0       | 81.2       | 68.3        | 103.3        | 123.7        |
| w/o sc. | HMR2.0a   | 44.4      | 69.8       | 82.2       | 61.5        | 97.8         | 120.0        |
| w/o sc. | TokenHMR  | 44.3      | 71.0       | 84.6       | 55.6        | 91.7         | 109.4        |
| w/o sc. | CameraHMR | 38.5      | 62.1       | 72.9       | 43.7        | 73.0         | 85.4         |
| w/o sc. | NLF       | 37.3      | 60.3       | 71.4       | 41.2        | 69.6         | 82.4         |
| w/o sc. | PromptHMR | 36.6      | 58.7       | 69.4       | 41.0        | 71.7         | 84.5         |
| w/ sc.  | Human3R   | 44.1      | 71.2       | 84.9       | 48.5        | 73.9         | 86.0         |
| w/ sc.  | UniSH     | 48.8      | 75.6       | 88.8       | 86.6        | 112.9        | 140.0        |
| w/ sc.  | **Ours**  | **41.0**  | **67.7**   | **78.7**   | **45.8**    | 75.7         | 88.8         |

SHOW is best among joint human–scene (w/ sc.) methods on 3DPW and best in EMDB-1 PA-MPJPE, but **Human3R has lower EMDB-1 MPJ (73.9 vs 75.7) and PVE (86.0 vs 88.8)**. Camera-space-only methods (PromptHMR, NLF) still lead overall on 3DPW.

### Global Human Motion Estimation

원논문 Table 2. Global human motion estimation on EMDB-2 and RICH. Opt. = feed-forward (optimization-free); Scene = joint 3D scene reconstruction. WA: World-aligned MPJPE, W: MPJPE, RTE: Root translation error (%). "–" = not reported.

| Method   | Opt. | Scene | EMDB-2 WA ↓ | EMDB-2 W ↓ | EMDB-2 RTE ↓ | RICH WA ↓ | RICH W ↓ | RICH RTE ↓ |
| -------- | ---- | ----- | ----------- | ---------- | ------------ | --------- | -------- | ---------- |
| SLAHMR   | ✗    | ✗     | 326.9       | 776.1      | 10.2         | 132.2     | 237.1    | 6.4        |
| TRAM     | ✗    | ✗     | 76.4        | 222.4      | 1.4          | 127.8     | 238.0    | 6.0        |
| JOSH     | ✗    | ✓     | 68.9        | 174.7      | 1.3          | 89.0      | 132.5    | 3.0        |
| TRACE    | ✓    | ✗     | 429.0       | 1702.3     | 17.7         | 238.1     | 925.4    | 101.4      |
| WHAM     | ✓    | ✗     | 135.6       | 334.8      | 6.0          | 108.4     | 190.1    | 4.5        |
| GVHMR    | ✓    | ✗     | 111.0       | 276.5      | 2.0          | 78.8      | 126.3    | 2.4        |
| JOSH3R   | ✓    | ✓     | 220.0       | 661.7      | 13.1         | –         | –        | –          |
| Human3R  | ✓    | ✓     | 112.2       | 267.9      | 2.2          | 110.0     | 184.9    | 3.3        |
| UniSH    | ✓    | ✓     | 118.5       | 270.1      | 5.8          | 118.1     | 183.2    | 4.8        |
| **Ours** | ✓    | ✓     | **109.1**   | **262.3**  | **2.1**      | 107.3     | 172.7    | 2.2        |

On EMDB-2 (moving camera) SHOW leads the joint feed-forward group and even surpasses GVHMR, which relies on an off-the-shelf scale estimator. **On RICH, SHOW is slightly lower** — the authors attribute this to RICH's static-camera setup, where visual geometry models benefit from multi-view observation that is not available. Among the RICH columns, GVHMR reports lower WA (78.8) and W (126.3) than SHOW (107.3 / 172.7).

### Human–Scene Consistency

원논문 Table 3. Comparison of human–scene consistency metrics on 3DPW and EMDB-1. Lower is better for all metrics. Footnotes: Human3R's scene point branch trained with additional metric-scale point-map data; UniSH's scale branch trained with additional self-collected real-world video data.

| Method   | 3DPW HS-V5 ↓ | 3DPW HS-V10 ↓ | 3DPW HS-CF5 ↓ | 3DPW HS-CF10 ↓ | EMDB-1 HS-V5 ↓ | EMDB-1 HS-V10 ↓ | EMDB-1 HS-CF5 ↓ | EMDB-1 HS-CF10 ↓ |
| -------- | ------------ | ------------- | ------------- | -------------- | -------------- | --------------- | --------------- | ---------------- |
| Human3R  | 0.652        | 0.640         | **1.30**      | **1.32**       | 3.66           | 2.91            | **1.13**        | **1.31**         |
| UniSH    | **0.028**    | 0.028         | 7.65          | 7.52           | 0.033          | 0.037           | 7.10            | 6.99             |
| **Ours** | 0.030        | **0.026**     | 5.69          | 5.44           | **0.013**      | **0.017**       | 5.88            | 5.79             |

SHOW is best on most metrics among approaches that do **not** explicitly predict metric point maps, and best on HS-V. **Human3R wins HS-CF** (1.13–1.32) because it uses a metric geometry backbone trained on large-scale metric data — but it shows inferior HS-V (0.640–3.66), reflecting poor scale alignment.

### Ablation Study

원논문 Table 4. Comparison of human–scene consistency metrics on 3DPW (lower is better). Ablation models are trained for 150 epochs on subsampled 6 FPS data; end-to-end fine-tuning adds 100 epochs.

| Setting                | HS-V5 ↓ | HS-V10 ↓ | HS-CF5 ↓ | HS-CF10 ↓ |
| ---------------------- | ------- | -------- | -------- | --------- |
| w/o pretrain alignment | 0.708   | 0.660    | 38.51    | 38.39     |
| w/o joint modeling     | 0.312   | 0.295    | 17.32    | 17.08     |
| w/o mask prompting     | 0.033   | 0.035    | 14.12    | 14.10     |
| w/o ray encoder        | 0.734   | 0.667    | 11.23    | 11.06     |
| full                   | 0.028   | 0.030    | 9.44     | 9.38      |
| full + e2e tuning      | 0.029   | 0.027    | **6.21** | **5.99**  |

- **Pretraining alignment** is critical: removing it degrades all metrics (HS-V5 0.708 vs 0.028; HS-CF5 38.51 vs 9.44).
- **Mask prompting** matters for alignment (HS-CF5 14.12 vs 9.44 without it).
- **Ray encoder** removal substantially hurts HS-V (0.734).
- **Joint modeling** removal (scale from scene semantics only) degrades HS-CF badly (17.32).
- **End-to-end tuning** gives the best overall result, improving HS-CF5 from 9.44 to 6.21 and HS-CF10 from 9.38 to 5.99.

Qualitative comparisons and the ablation visualizations (Fig. 4–8) are figure-only — 수치 미인쇄.

## 💡 Insights & Impact

- **Coupling over co-prediction**: The paper argues human–scene alignment needs the two tasks to actively inform each other during learning, not merely be predicted in the same output space. Human priors are injected into the geometry backbone (human-aware scene features) and scene geometry is fused back to constrain body pose, scale, and placement.
- **Masks beat sparse cues**: Full-body masks as dense prompts give more precise, instance-specific human localization than head detection (Human3R) or bounding boxes (UniSH), improving robustness under occlusion, truncation, and multi-person overlap.
- **Fine-tuning the backbone matters**: Unlike UniSH, which freezes geometry and HMR branches and uses a lightweight alignment network, SHOW fine-tunes the VGGT backbone to align its depth/scale distribution with training data — enabling stronger scene–human coupling without extra real-world video data.
- **Honest limitations**: A sim-to-real gap persists (trained on synthetic BEDLAM2.0); out-of-distribution cases such as extreme scale variation or humans occupying a very small image region remain hard. Static-camera setups (RICH) also reduce the benefit of the multi-view geometry prior.

## 🔗 Related Work

- **[VGGT](vggt.md)**: Provides the feed-forward geometry backbone (camera/depth/point-map prediction) that SHOW adapts with mask prompting and a DensePose head.
- **[CUT3R](../dynamic/cut3r.md)**: Online 4D reconstruction model with persistent state; the foundation extended by Human3R.
- **[Human3R](../dynamic/human3r.md)**: Extends CUT3R with visual prompt tuning to decode SMPL-X from reconstruction latents; a primary baseline (strong HS-CF via metric backbone, but weaker HS-V).
- **[DUSt3R](../foundation/dust3r.md)**: Progenitor of the feed-forward 3D reconstruction paradigm this line of work builds on.
- **UniSH** (Li et al. 2026) and **JOSH3R** (Liu et al. 2026): Concurrent feed-forward joint human–scene methods used as baselines (not in this collection).

## 📚 Key Takeaways

1. **One world, one pass**: SHOW reconstructs humans (SMPL-X) and scene (point maps) jointly in a shared metric space from monocular human-centric video, in a single feed-forward pipeline.
2. **Bidirectional priors**: Human semantics/scale prior → scene reconstruction; scene geometry → human recovery. Realized via a human-aware geometry encoder (mask + DensePose) and a geometry-aware SMPL-X decoder with asymmetric cross-attention.
3. **New alignment metrics**: HS-CF (Chamfer between body and scene point map) and HS-V (variance mismatch) let the community measure human–scene consistency, not just per-task accuracy.
4. **Where it wins and loses**: Best joint-method local accuracy on 3DPW and best EMDB-2 global motion among feed-forward joint methods; leads HS-V. But it trails camera-space-only HMR on 3DPW, loses HS-CF to Human3R's metric backbone, and is slightly weaker on static-camera RICH.

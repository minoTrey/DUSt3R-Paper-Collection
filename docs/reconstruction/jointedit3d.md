# JointEdit3D: Feed-Forward 3D Scene Editing in a Unified Latent Space (arXiv preprint (2026-06))

![jointedit3d — architecture](https://arxiv.org/html/2606.13345v1/x1.png)

_JointEdit3D pipeline (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Xinnan Zhu, Ruijie Xu, Jiayu Ying, Daoguo Dong, Jiachen Xu, Yuan Xie, Xin Tan (Xinnan Zhu and Ruijie Xu contributed equally; Xin Tan is corresponding author)
- **Institution**: East China Normal University; Shanghai Artificial Intelligence Laboratory; Fudan University; Tencent
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.13345) | [Project Page](https://xinnan-zhu.github.io/JointEdit3D-Page/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward 3D scene editor that treats editing as RGB-geometry latent inpainting in a unified reconstruction-generation latent space. From one edited RGB reference frame it generates all remaining RGB views and the edited geometry latent, using a SceneAnchor Branch and edit-aware losses to preserve unedited content without inference-time masks.

## 🎯 Key Contributions

1. **Editing as unified-latent generation**: Formulates 3D scene editing as feed-forward generation in a joint RGB-geometry latent space, coupling edit decisions, appearance synthesis, and geometry updates instead of separating 2D view editing from reconstruction.
2. **JointEdit3D framework**: Combines asymmetric single-frame-guided RGB-geometry latent inpainting, an edit-aware **SceneAnchor Branch**, and edit-aware latent losses to propagate reference edits while preserving source-scene structure — without requiring edit masks at inference.
3. **SceneEdit3D-15K + SceneEdit3D-Bench**: A 15K-sample paired scene-level 3D editing dataset with renderer-provided 3D annotations (depth, camera, masks, instructions), plus a curated 100-sample held-out benchmark evaluating edit fidelity, background preservation, and 3D structure. Claimed as the first paired scene-level 3D editing dataset with comprehensive 3D annotations.

## 🔧 Technical Details

### Problem Framing

Prior 3D scene editing is decoupled: optimization-based methods edit NeRF/3D-Gaussian representations per scene (costly, mask-reliant), and recent feed-forward methods still perform the edit at the 2D/multi-view level before reconstruction, so view inconsistencies propagate to the 3D output. JointEdit3D instead edits directly inside a latent that already represents 3D structure.

### Unified RGB-Geometry Latent (built on Gen3R)

- Adapts the Gen3R unified RGB-geometry reconstruction-generation latent space. Given a multi-view video, appearance is encoded by a pretrained Wan video VAE (`z_rgb`) and geometry via frozen VGGT features passed through a learned Geometry Adapter encoder (`z_geo`).
- The two halves are concatenated along spatial width into one lattice `z = [z_rgb ; z_geo]`, so generation is joint rather than RGB-only.
- `G_θ` denotes the Gen3R-tuned Wan backbone; `G_{θ,ϕ}` adds the SceneAnchor Branch parameters `ϕ`.

### Edit Conditioning via Single-Frame Inpainting (asymmetric)

- The editing condition exposes only the edited RGB reference frame; all other RGB positions and the entire geometry half are unknown → asymmetric inpainting.
- The reference is VAE-encoded and placed at latent temporal index `k` in a zero-filled tensor; a binary mask (replicated over four temporal sub-channels to match the Wan VAE's 4× temporal compression) marks observed entries and is concatenated with the conditioning tensor.
- Cross-attention context `ctx = (CLIP(I_e), T5(p))` from the reference image and optional instruction is added, but the edited reference remains the primary control (explicit appearance + placement).

### SceneAnchor Branch (source-scene preservation)

- A dedicated trainable branch `A_ϕ` injects source-scene RGB features back into the frozen main branch as interleaved residual corrections, treating the source as an edit-aware preservation prior rather than a target to copy (avoids the "copy shortcut").
- Consumes only the RGB half of the source (`[z_rgb_s ; 0]`, geometry half zeroed since no source geometry is assumed at inference).
- Mirrors the block structure of `G_θ` but with hidden width `d_a = 512`; residual output projections are zero-initialized, so the editor degenerates to `G_θ` at the start of training.

### Edit-Aware Training Objectives

- Base objective: flow matching over the edited target latent (velocity supervised toward `ϵ − z⋆`).
- Standard MSE is dominated by unchanged background in sparse 3D edits, so the loss is decomposed into **edit** and **background** regions per modality (RGB and geometry), with edit masks estimated from source-target latent differences (threshold `τ`).
- **Within-region weighting** upweights positions with larger latent change (`w = 1 + α d`); **temporal weighting** upweights frames farther from the reference. Final objective `L_train = L_rgb + γ_geo L_geo`.

### Implementation

- Backbone: frozen Gen3R-tuned image-camera-conditioned Wan2.1 1.3B DiT, `L = 32` blocks. SceneAnchor Branch: `d_a = 512`, `K = 8` anchor blocks injected at layers {0, 4, 8, 12, 16, 20, 24, 28}, **70M trainable parameters** (only the branch is trained).
- Optimizer: AdamW, initial LR `1×10⁻⁴`, bf16 mixed precision, gradient checkpointing. Objective hyperparameters: `τ = 0.15`, `α = 5.0`, `η = 0.5`, `λ = 0.5`, `γ_geo = 1.5`.
- Training: 10K steps, batch size 10, on **8 NVIDIA H200 GPUs**.
- Data representation: 49 RGB frames at 560×560; Wan VAE → 16-channel latents, 13 temporal steps, 70×70 spatial; concatenated target latent shape 16×13×70×140.
- Inference: FlowMatch Euler sampling with **5 denoising steps**, classifier-free guidance scale 1.0, control scale 1.0, seed 42; pose-free via zero camera embeddings when camera is unavailable.

## 📊 Results

Evaluated on SceneEdit3D-Bench (100 held-out samples) and 360-USID (deletion-only real scenes). Region-aware PSNR↑ / LPIPS↓ on edited and background pixels, plus 3D reconstruction metrics against renderer-provided geometry. JointEdit3D is trained only on synthetic SceneEdit3D-15K.

### Deletion Edit-Region Quality

원논문 Table 2. 각 셀은 `PSNR↑ / LPIPS↓`. 360-USID는 편집 영역(edit-region)만 평가.

| Method            | Bench PSNR↑ / LPIPS↓ | 360-USID PSNR↑ / LPIPS↓ |
| ----------------- | -------------------- | ----------------------- |
| SPIn-NeRF         | 19.20 / 0.528        | 15.89 / 0.4826          |
| Gaussian Grouping | 20.41 / 0.377        | 16.67 / 0.4241          |
| GScream           | 20.38 / 0.449        | 14.37 / 0.5725          |
| GaussianEditor    | 20.26 / 0.451        | 16.23 / 0.3975          |
| MVInpainter       | 21.37 / 0.406        | 15.60 / 0.5677          |
| Omni-3DEdit       | 24.86 / 0.307        | 17.78 / 0.3655          |
| **JointEdit3D**   | **31.92 / 0.151**    | **18.57 / 0.3426**      |

### Operation-Wise Edit Region

원논문 Table 3 (Edit region). 각 셀은 `PSNR↑ / LPIPS↓`. Average는 연산 그룹에 대한 macro-average.

| Method          | Delete            | Add               | Move              | Appearance        | Multi-op          | Average           |
| --------------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- |
| SEVA            | 23.39 / 0.399     | 15.92 / 0.523     | 17.87 / 0.450     | 17.50 / 0.464     | 16.93 / 0.496     | 18.72 / 0.465     |
| MVInpainter     | 21.37 / 0.406     | 20.04 / 0.362     | 16.99 / 0.437     | 18.94 / 0.349     | 17.92 / 0.423     | 19.05 / 0.392     |
| Omni-3DEdit     | 24.86 / 0.307     | 20.63 / 0.293     | 18.55 / 0.377     | 20.92 / 0.230     | 17.03 / 0.461     | 21.10 / 0.323     |
| **JointEdit3D** | **31.92 / 0.151** | **23.88 / 0.195** | **23.19 / 0.244** | **27.67 / 0.115** | **23.77 / 0.263** | **26.63 / 0.187** |

SEVA is a protocol-mismatched novel-view-synthesis diagnostic, not a native 3D editor.

### Operation-Wise Background Region

원논문 Table 3 (Bg. region). 각 셀은 `PSNR↑ / LPIPS↓`. JointEdit3D는 배경 PSNR에서 MVInpainter에 근소하게 뒤진다(32.33 vs 32.40 avg)는 점을 그대로 기록한다.

| Method          | Delete        | Add           | Move          | Appearance    | Multi-op      | Average       |
| --------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| SEVA            | 17.89 / 0.421 | 17.74 / 0.426 | 17.69 / 0.411 | 19.00 / 0.378 | 17.54 / 0.445 | 17.93 / 0.418 |
| MVInpainter     | 33.57 / 0.080 | 33.64 / 0.076 | 30.97 / 0.081 | 33.76 / 0.073 | 30.06 / 0.091 | 32.40 / 0.080 |
| Omni-3DEdit     | 25.00 / 0.215 | 24.24 / 0.217 | 24.40 / 0.210 | 25.88 / 0.190 | 23.81 / 0.235 | 24.65 / 0.214 |
| **JointEdit3D** | 32.62 / 0.079 | 32.59 / 0.081 | 31.22 / 0.069 | 33.80 / 0.059 | 30.84 / 0.095 | 32.33 / 0.077 |

Mask-guided baselines (e.g. MVInpainter) can obtain higher background PSNR because their inputs/constraints keep out-of-mask regions nearly unchanged; JointEdit3D is mask-free yet keeps background LPIPS lowest.

### 3D Geometry Quality

원논문 Table 4. Target RGB + VGGT는 oracle RGB 입력 참조로 순위에서 제외. Method | 3D Source | Accuracy↓ | Completeness↓ | CD↓ | F-score↑.

| Method                     | 3D Source    | Accuracy↓  | Completeness↓ | CD↓        | F-score↑   |
| -------------------------- | ------------ | ---------- | ------------- | ---------- | ---------- |
| Target RGB + VGGT (oracle) | VGGT recon.  | 0.0724     | 0.0950        | 0.0837     | 0.9619     |
| SEVA + VGGT                | VGGT recon.  | 0.1433     | 0.2244        | 0.1839     | 0.8722     |
| Omni-3DEdit + VGGT         | VGGT recon.  | 0.1165     | 0.1313        | 0.1239     | 0.9143     |
| JointEdit3D RGB + VGGT     | VGGT recon.  | **0.0891** | 0.1211        | 0.1051     | 0.9357     |
| **JointEdit3D**            | Joint output | 0.1153     | **0.0886**    | **0.1020** | **0.9702** |

Versus its own cascaded RGB→VGGT variant, JointEdit3D trades a small accuracy gap (0.1153 vs 0.0891) for better completeness, CD, and F-score from the jointly generated RGB-geometry latent.

### Supplementary Operation-Specific Metrics

원논문 Table 7. JointEdit3D 단일 결과. Edit/Bg SSIM↑, Abs Rel↓, δ<1.25↑.

| Operation  | Edit SSIM↑ | Bg. SSIM↑ | Abs Rel↓ | δ<1.25 ↑ |
| ---------- | ---------- | --------- | -------- | -------- |
| Delete     | 0.836      | 0.914     | 0.0540   | 0.9819   |
| Add        | 0.698      | 0.921     | 0.0592   | 0.9741   |
| Move       | 0.698      | 0.913     | 0.0858   | 0.9305   |
| Appearance | 0.840      | 0.926     | 0.0606   | 0.9719   |
| Multi-op   | 0.672      | 0.892     | 0.0683   | 0.9628   |

Move and Multi-op are hardest (larger disocclusion/spatial rearrangement), consistent with the main tables.

### Runtime and Memory (49-frame full-3D)

원논문 Table 8. Figure 3 효율-품질 그래프의 근거 수치. `–`는 원논문이 비교 가능한 메모리를 기록하지 않은 항목.

| Method            | Time (s)  | Gen./Opt. (s) | Post. (s) | Peak alloc. (GB) | Peak reserved (GB) |
| ----------------- | --------- | ------------- | --------- | ---------------- | ------------------ |
| **JointEdit3D**   | **11.94** | 11.94         | 0.00      | 29.07            | 50.33              |
| MVInpainter       | 43.25     | 19.45         | 23.81     | 43.80            | 66.88              |
| Omni-3DEdit       | 237.15    | 213.34        | 23.81     | 56.40            | 73.08              |
| SPIn-NeRF         | 1619.00   | 1619.00       | 0.00      | –                | –                  |
| Gaussian Grouping | 486.00    | 486.00        | 0.00      | –                | –                  |
| GaussianEditor    | 285.07    | 285.07        | 0.00      | –                | –                  |

JointEdit3D avoids the extra VGGT reconstruction pass that RGB/video baselines need (Post. = 0.00) and the per-scene optimization of NeRF/3DGS methods.

### Ablation Study

원논문 Table 5. 각 변형은 자원 제약상 full-model 행 포함 2K steps로 학습(메인 표의 10K와 다름). Edit/Background PSNR↑·LPIPS↓, 3D Structure CD↓.

| Variant                                 | Edit PSNR↑ | Edit LPIPS↓ | Bg PSNR↑  | Bg LPIPS↓ | CD↓        |
| --------------------------------------- | ---------- | ----------- | --------- | --------- | ---------- |
| JointEdit3D (full)                      | **26.82**  | **0.209**   | 30.69     | 0.103     | **0.1053** |
| Source video in main branch (no anchor) | 23.53      | 0.292       | **30.88** | **0.086** | 0.1194     |
| w/o source video (traj. only)           | 19.4       | 0.510       | 18.91     | 0.562     | 0.1829     |
| w/o GEO in Wan Flow (+VGGT)             | 24.75      | 0.381       | 27.85     | 0.337     | 0.1506     |
| w/o Text Condition                      | 26.37      | 0.214       | 30.66     | 0.109     | 0.1064     |
| w/o Region Decomposition                | 23.69      | 0.324       | 30.16     | 0.159     | 0.1257     |
| w/o Within-region Weighting             | 25.35      | 0.234       | 29.94     | 0.119     | 0.1126     |
| w/o Temporal Weighting                  | 26.12      | 0.238       | 29.91     | 0.124     | 0.1148     |

Replacing the anchor branch with main-branch source conditioning preserves background slightly better (Bg PSNR 30.88 vs 30.69, Bg LPIPS 0.086 vs 0.103) but reduces edit PSNR by 3.29 dB and worsens CD. Removing the source video causes the largest background collapse; removing the geometry latent degrades both RGB and 3D. Text conditioning has only a minor effect (edited reference is the dominant edit signal).

### Dataset Statistics

원논문 Table 9. SceneEdit3D-15K 분할·연산별 샘플 수.

| Split    | Total  | Scenes | Add   | Delete | Move  | Appearance | Multi-op |
| -------- | ------ | ------ | ----- | ------ | ----- | ---------- | -------- |
| Train    | 13,799 | 135    | 4,990 | 4,987  | 1,884 | 1,017      | 921      |
| Test/val | 1,520  | 16     | 600   | 600    | 186   | 24         | 110      |
| Bench    | 100    | 15     | 29    | 29     | 14    | 14         | 14       |

### Efficiency-Quality Trade-off

Figure 3 plots inference time per scene vs LPIPS Edit with VRAM annotations; individual annotated values (그림 3, 수치 미인쇄) — the underlying runtime/memory numbers are in Table 8 above.

## 💡 Insights & Impact

- **Edit where geometry lives**: The central thesis is that edit decisions, appearance synthesis, and geometry updates should happen in the same latent state, rather than as separate 2D view-editing then reconstruction stages. Table 4 supports this — the joint output beats the cascaded RGB→VGGT variant on completeness/CD/F-score.
- **Anchoring without copying**: The SceneAnchor Branch works as an implicit, mask-free edit-region localizer via edit-conditioned residual corrections, letting compatible tokens receive strong source anchoring while the edited region departs from the source. This is why a mask-free method still keeps background LPIPS competitive with mask-guided baselines.
- **Losses matter for sparse edits**: Region-decomposed + within-region + temporal weighting are each ablated as contributing; removing region decomposition causes the largest edit-region drop because sparse edits are diluted by unchanged background.
- **Data as a bottleneck**: The paper argues progress is gated by the lack of paired before/after 3D-annotated scene edits, and contributes SceneEdit3D-15K/Bench (Blender-rendered, identical camera trajectories for paired source/target) to address it.
- **Limitations (stated)**: JointEdit3D is reference-guided, not end-to-end text-to-3D editing; quality depends on the edited reference image, and reference errors can propagate across views and into the generated point cloud. Direct text-driven editing is left to future work requiring stronger foundation models and larger paired 3D editing data.

## 🔗 Related Work

- **[VGGT](vggt.md)**: JointEdit3D reuses frozen VGGT features (via a Geometry Adapter) as the geometry stream of the unified latent, and also uses a VGGT reconstruction backend for the RGB→3D baselines and the cascaded "JointEdit3D RGB + VGGT" comparison in Table 4.
- **Gen3R** [11]: The feed-forward 3D scene reconstruction model whose unified RGB-geometry reconstruction-generation latent space JointEdit3D adapts to editing; also the source of the point-cloud evaluation protocol (Table 4).
- **Wan** [29]: The pretrained video VAE and diffusion backbone (Wan2.1 1.3B DiT) that JointEdit3D freezes as its main branch.
- **Feed-forward 3D editors**: MVInpainter [2], Omni-3DEdit [4], EditCast3D [24], Edit3R [19] — prior feed-forward methods that still edit at the 2D/multi-view level; MVInpainter and Omni-3DEdit are the main feed-forward baselines.
- **Optimization-based editors**: SPIn-NeRF [21], Gaussian Grouping [38], GScream [31], GaussianEditor [6] — per-scene NeRF/3DGS editing baselines.
- **3D latent editing**: TRELLIS [35], VoxHammer [15], Fuse3D [12] — object-level controllable generation/editing in voxel-structured 3D latents; JointEdit3D extends latent editing to full scenes.

## 📚 Key Takeaways

1. JointEdit3D reframes 3D scene editing as **feed-forward RGB-geometry latent inpainting** in a unified reconstruction-generation latent space, coupling appearance and geometry in one shared generation target.
2. A mask-free **SceneAnchor Branch** (70M trainable params over a frozen Wan2.1 1.3B backbone) injects source-scene structure as edit-conditioned residuals, preserving unedited content without copying.
3. **Edit-aware region-decomposed losses** are essential for sparse 3D edits, giving the largest edit-region gains among ablated components.
4. On the new SceneEdit3D-Bench, JointEdit3D achieves the strongest edited-region quality across all five operations (avg edit PSNR 26.63) and best joint-output 3D structure (F-score 0.9702, CD 0.1020), while background PSNR is competitive but slightly below mask-guided MVInpainter — and it is markedly faster (11.94s vs 43.25s / 237.15s for the feed-forward baselines).
5. Contributions include **SceneEdit3D-15K** (15K paired samples) and **SceneEdit3D-Bench** (100 samples), addressing the lack of paired, 3D-annotated scene-editing resources. As a PREPRINT, venue/metadata remain unverified pending indexing.

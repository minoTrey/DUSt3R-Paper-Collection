# One4D: Unified 4D Generation and Reconstruction via Decoupled LoRA Control (arXiv preprint (2025-11))

## 📋 Overview

- **Authors**: Zhenxing Mi, Yuxin Wang, Dan Xu
- **Institution**: The Hong Kong University of Science and Technology (HKUST)
- **Venue**: arXiv preprint (2025-11)
- **Links**: [Paper](https://arxiv.org/abs/2511.18922) | [Project Page](https://mizhenxing.github.io/One4D)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A single video-diffusion model that produces dynamic 4D content as synchronized RGB frames and pointmaps, using Decoupled LoRA Control (two modality-specific LoRA branches joined by zero-initialized control links) plus Unified Masked Conditioning to seamlessly cover single-image-to-4D generation, sparse-frame generation-and-reconstruction, and full-video reconstruction.

## 🎯 Key Contributions

1. **Unified 4D framework**: One4D bridges 4D generation and 4D reconstruction within a single video diffusion model, handling single-image, sparse-frame, and full-video inputs without architectural changes.
2. **Decoupled LoRA Control (DLC)**: Two modality-specific LoRA branches (one for RGB, one for XYZ pointmaps) share the frozen base parameters but keep forward computation disjoint, connected by lightweight zero-initialized control links that gradually learn pixel-level cross-modal consistency. This preserves the base model's video priors while enabling accurate geometry.
3. **Unified Masked Conditioning (UMC)**: A single conditioning interface that packs different condition types into one masked conditioning video — single-image (pure generation), sparse frames (mixed generation and reconstruction), and full video (pure reconstruction) — without changing the architecture.
4. **Efficient adaptation under modest compute**: Trained on a curated mixture of synthetic and real 4D datasets, avoiding the extreme compute of channel-wise coupling approaches such as WVD.

## 🔧 Technical Details

### Representation

Each 4D scene is represented as RGB frames and pointmaps, where pointmaps are 3-channel 2D (XYZ) videos analogous to RGB videos. At each training step, RGB and pointmaps are encoded by a video VAE into latents, noised under a Rectified Flow formulation, and fed to DiTs to predict per-modality velocities supervised by a mean-squared error loss.

### Decoupled LoRA Control (DLC)

- Prior diffusion reconstruction methods (e.g., Marigold, Geo4D) concatenate clean RGB latents with noisy geometry latents channel-wise, which works only when RGB is fixed. In the joint generation setting both RGB and geometry latents are noisy, and channel-wise (WVD) or spatial-wise (4DNeX) concatenation induces premature, excessive cross-modal interaction that degrades RGB quality or prevents high-quality geometry.
- DLC instead attaches two separate LoRA adapters on each DiT submodule, evaluating each submodule once per modality — reusing frozen base weights but keeping computation decoupled. This drastically reduces memory versus duplicating parameters, making finetuning feasible for the 14B base model.
- **Control links**: at a small subset of linked DiT layers, features of one modality are updated by the other via zero-initialized linear control links (`ZCLrgb←xyz`, `ZCLxyz←rgb`). Zero initialization keeps branches independent at the start of training, preserving video priors while the links gradually learn pixel-wise alignment.

### Unified Masked Conditioning (UMC)

- Available image conditions are assembled into a conditioning video with unobserved frames filled with zeros, encoded by the video VAE, and concatenated channel-wise **only** with the noisy RGB latents (plus a binary observed/unobserved mask). Conditioning signals reach the geometry branch through the DLC control links from the RGB branch, avoiding conditioning artifacts in geometry.
- After generation, camera poses and depth maps are recovered from the generated pointmaps via a lightweight global optimization (following MonST3R and Geo4D), combining a point-map alignment loss and a temporal camera-trajectory smoothness loss.

### Training / Inference setup

- Base model: **Wan2.1-Fun-V1.1-14B-InP** (a community finetune of Wan2.1-I2V-14B for video inpainting).
- LoRA rank 64 on all DiT linear layers for both branches (**685M** parameters); DLC control links added to **five** DiT layers (**250.7M** parameters); overall **935.7M** trainable parameters.
- Trained on 8 NVIDIA H800 GPUs, batch size 1 per GPU with gradient accumulation 4, for **5500** steps at learning rate 1 × 10⁻⁴. Task sampling ratios: 0.35 single-image, 0.30 sparse-frame, 0.35 full-video. Max 81 training frames at resolution 352 × 624.
- Datasets: dynamic synthetic 4D (OmniWorld-Game, BEDLAM, PointOdyssey, TartanAir) plus real-world SpatialVID videos annotated with pseudo-geometry from Geo4D — about 17k synthetic and 17k real-world clips, roughly 2M frames.
- Inference: 50 flow-matching steps with classifier-free guidance scale 6.0.

## 📊 Results

One4D is trained once as a **unified** generation-and-reconstruction (G&R) model and compared against reconstruction-only (R) baselines. It does not win every metric — on full-video depth (Table 3) it trails the reconstruction-only Geo4D-ref, and on Bonn it trails MonST3R/CUT3R; on camera accuracy (Table 4) MonST3R/CasualSAM report lower errors on several columns.

### 4D generation — user study (vs 4DNeX)

원논문 Table 1. Percentages indicate user preference (higher is better).

| Method       | Consistency↑ | Dynamic↑ | Aesthetic↑ | Depthmap↑ | 4D↑   |
| ------------ | ------------ | -------- | ---------- | --------- | ----- |
| 4DNeX        | 21.0%        | 16.7%    | 17.7%      | 11.7%     | 10.0% |
| One4D (Ours) | 78.9%        | 83.3%    | 82.3%      | 88.3%     | 90.0% |

### 4D generation — VBench video quality (vs 4DNeX)

원논문 Table 2.

| Method       | Dynamic↑ | I2V consistency↑ | Aesthetic↑ |
| ------------ | -------- | ---------------- | ---------- |
| 4DNeX        | 25.6%    | 98.7%            | 61.9%      |
| One4D (Ours) | 55.7%    | 97.8%            | 63.8%      |

One4D substantially improves motion dynamics and aesthetic quality while keeping comparable I2V consistency (it slightly trails 4DNeX on I2V consistency: 97.8% vs 98.7%).

### Full-video-to-4D — depth accuracy on Sintel and Bonn

원논문 Table 3. Abs Rel↓ (lower better), δ<1.25↑ (higher better). Task: R = reconstruction-only, G&R = unified generation-and-reconstruction. Robust-CVD has no Bonn result reported (-).

| Method         | Task | Sintel Abs Rel↓ | Sintel δ<1.25↑ | Bonn Abs Rel↓ | Bonn δ<1.25↑ |
| -------------- | ---- | --------------- | -------------- | ------------- | ------------ |
| Marigold       | R    | 0.532           | 51.5           | 0.091         | 93.1         |
| Depth-Anything | R    | 0.367           | 55.4           | 0.106         | 92.1         |
| NVDS           | R    | 0.408           | 48.3           | 0.167         | 76.6         |
| ChronoDepth    | R    | 0.687           | 48.6           | 0.100         | 91.1         |
| DepthCrafter   | R    | 0.270           | 69.7           | 0.071         | 97.2         |
| Robust-CVD     | R    | 0.703           | 47.8           | -             | -            |
| CasualSAM      | R    | 0.387           | 54.7           | 0.169         | 73.7         |
| MonST3R        | R    | 0.335           | 58.5           | 0.063         | 96.4         |
| CUT3R          | R    | 0.311           | 62.0           | 0.070         | 96.7         |
| Geo4D-ref      | R    | 0.205           | 73.5           | 0.059         | 97.2         |
| One4D (Ours)   | G&R  | 0.273           | 70.4           | 0.092         | 93.7         |

Among pointmap-based methods One4D clearly outperforms MonST3R and CUT3R on Sintel δ<1.25 (70.4 vs 58.5 / 62.0) and remains close to the reconstruction-only Geo4D-ref, despite being trained once for both tasks.

### Camera trajectory accuracy on Sintel and TUM-dynamics

원논문 Table 4. All metrics lower-the-better: ATE↓, RPE-T↓, RPE-R↓.

| Method       | Task | Sintel ATE↓ | Sintel RPE-T↓ | Sintel RPE-R↓ | TUM ATE↓ | TUM RPE-T↓ | TUM RPE-R↓ |
| ------------ | ---- | ----------- | ------------- | ------------- | -------- | ---------- | ---------- |
| Robust-CVD   | R    | 0.360       | 0.154         | 3.443         | 0.153    | 0.026      | 3.528      |
| CasualSAM    | R    | 0.141       | 0.035         | 0.615         | 0.071    | 0.010      | 1.712      |
| MonST3R      | R    | 0.108       | 0.042         | 0.732         | 0.063    | 0.009      | 1.217      |
| CUT3R        | R    | 0.208       | 0.062         | 0.610         | 0.046    | 0.014      | 0.446      |
| Geo4D-ref    | R    | 0.185       | 0.063         | 0.547         | 0.073    | 0.020      | 0.635      |
| One4D (Ours) | G&R  | 0.213       | 0.057         | 0.818         | 0.129    | 0.022      | 1.447      |

One4D achieves ATE and RPE within the same range as Geo4D-ref and other reconstruction baselines, indicating its pointmaps support robust camera estimation, though MonST3R and CasualSAM report lower errors on most columns.

### Sparse-frame-to-4D — depth accuracy vs sparsity

원논문 Table 5. Sparsity is the fraction of observed frames kept. Extreme sparsity rows on Sintel are not reported (-).

| Sparsity   | Sintel Abs Rel↓ | Sintel δ<1.25↑ | Bonn Abs Rel↓ | Bonn δ<1.25↑ |
| ---------- | --------------- | -------------- | ------------- | ------------ |
| 0.50       | 0.314           | 70.3           | 0.094         | 93.5         |
| 0.25       | 0.443           | 67.7           | 0.094         | 93.3         |
| 0.10       | 0.453           | 64.0           | 0.099         | 92.9         |
| 0.05       | 0.641           | 57.6           | 0.151         | 87.2         |
| 0.04       | -               | -              | 0.191         | 82.5         |
| 0.03       | -               | -              | 0.277         | 71.1         |
| Full Model | 0.273           | 70.4           | 0.092         | 93.7         |

At 50% or 25% of frames One4D is almost as accurate as the full-video setting; degradation is graceful, and even at sparsity 0.05 / 0.03 it produces reasonable geometry from only 2 or 3 frames.

### Ablation — CFG scale and training steps

원논문 Table 6. Depth reconstruction on Sintel and Bonn.

| Setting      | Sintel Abs Rel↓ | Sintel δ<1.25↑ | Bonn Abs Rel↓ | Bonn δ<1.25↑ |
| ------------ | --------------- | -------------- | ------------- | ------------ |
| CFG=4        | 0.257           | 71.5           | 0.092         | 94.0         |
| CFG=5        | 0.259           | 70.9           | 0.090         | 94.1         |
| Step=1000    | 0.331           | 65.4           | 0.114         | 88.9         |
| Step=3000    | 0.284           | 68.1           | 0.097         | 91.8         |
| One4D (Ours) | 0.273           | 70.4           | 0.092         | 93.7         |

One4D is robust to the CFG choice (CFG=4/5 give very similar accuracy) and already reaches reasonable accuracy at 1K steps, approaching the full model by 3K steps and improving with longer training.

## 💡 Insights & Impact

- **Decoupling beats concatenation for joint RGB-geometry generation.** Channel-wise (WVD) and spatial-wise (4DNeX) concatenation cause severe cross-modal interference under modest compute; DLC's disjoint per-modality computation with sparse zero-initialized links preserves the base video priors while learning accurate geometry.
- **Compute efficiency.** Where WVD requires around 1M steps over two weeks on 64 A100 GPUs with channel-wise concatenation, One4D adapts the base video model in 5500 steps on 8 H800 GPUs, supporting the claim that its architecture preserves and leverages pretrained video priors.
- **One interface, many tasks.** UMC lets the same model switch between single-image generation, sparse-frame mixed generation-reconstruction, and full-video reconstruction with no architectural changes.
- **Honest trade-offs.** As a unified G&R model, One4D trails reconstruction-only Geo4D-ref on depth and trails MonST3R/CasualSAM on several camera-accuracy columns, while clearly beating MonST3R/CUT3R on Sintel δ<1.25.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: Introduced the paired pointmap representation that One4D adopts as its geometry representation for joint RGB–geometry generation.
- **[MonST3R](./monst3r.md)**: Dynamic-scene pointmap baseline; One4D follows its evaluation setting and its global optimization for recovering cameras/depth, and compares against it.
- **[CUT3R](./cut3r.md)**: Reconstruction-only pointmap baseline compared on full-video depth and camera accuracy.
- **[Geo4D](./geo4d.md)**: Video-generator-based 4D reconstruction method used both to annotate One4D's real-world training data and as a strong reconstruction-only reference (Geo4D-ref).
- **[VGGT](../reconstruction/vggt.md)**: Cited as evidence that pointmaps are effective for static 3D and dynamic 4D reconstruction.

## 📚 Key Takeaways

1. **Unified 4D model**: one video-diffusion model handles single-image-to-4D generation, sparse-frame generation-reconstruction, and full-video reconstruction, outputting synchronized RGB frames and pointmaps.
2. **Decoupled LoRA Control**: two modality-specific LoRA branches over shared frozen weights, joined by zero-initialized control links, decouple computation while learning pixel-wise RGB–geometry consistency.
3. **Unified Masked Conditioning**: a single masked conditioning interface spans pure generation to pure reconstruction without architectural changes.
4. **Efficient and competitive**: adapts a 14B video model in 5500 steps on 8 H800 GPUs, strongly preferred over 4DNeX in the user study, and competitive with reconstruction-only baselines on Sintel/Bonn depth and Sintel/TUM-dynamics camera accuracy — while honestly trailing Geo4D-ref and, on some columns, MonST3R.

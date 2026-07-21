# FFAvatar: Feed-Forward 4D Head Avatar Reconstruction from Sparse Portrait Images (ECCV 2026)

## 📋 Overview

- **Authors**: Jianjiang Yao, Ke Xian, Renxiang Dai, Robert Caiming Qiu
- **Institution**: School of Electronic Information and Communications, Huazhong University of Science and Technology, Wuhan, China
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2606.30347) | [Project Page](https://jj-yao.github.io/ffavatar/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A Transformer-based 3D Gaussian framework that reconstructs animatable 4D head avatars from one or more reference portraits, supporting _incremental_ reconstruction (refining as more images arrive) via an alternating-attention mechanism that disentangles identity appearance from expression/viewpoint, a sparse-to-dense (FLAME vertex → UV) learning paradigm, and a plug-and-play motion refinement module.

## 🎯 Key Contributions

1. **Incremental feed-forward 4D avatar**: A unified global canonical Gaussian field (built on the FLAME prior) whose Gaussian count and animation speed are independent of the number of input images, allowing progressive refinement as reference images are added — unlike multi-canonical designs whose cost grows with views.
2. **Sparse-to-dense hierarchical learning**: Coarse, semantically stable features are learned at the sparse FLAME vertex level (5,023 vertices) and densified in the UV domain to capture high-frequency geometry/texture, trading fidelity against efficiency.
3. **Motion-Aware Refinement Module (MARM)**: A plug-and-play module predicting residual Gaussian updates beyond FLAME's parametric deformation, for subject-specific dynamic personalization.

## 🔧 Technical Details

### Static appearance canonical field

- DINOv3 (frozen) extracts per-image features, augmented with camera and expression embeddings, then an alternating (intra-/inter-image) attention aggregates an identity-consistent global appearance representation while suppressing viewpoint/expression variation.
- Sparse-to-dense cross-modal alignment: sparse Gaussian centers initialized from 5,023 FLAME vertices are aligned to the global appearance via cross-attention, then densified in UV space by barycentric interpolation, giving `M + 5023` Gaussians. A second cross-attention stage refines the fused sparse+dense features.
- A feed-forward decoder outputs, per Gaussian, a positional offset relative to the FLAME template, opacity, color, anisotropic scale, and quaternion rotation — an expression- and viewpoint-invariant canonical field.

### Animation

FLAME provides coarse deformation via linear blend skinning + corrective blendshapes; densified surface points (barycentric on the deformed mesh) plus the original 5,023 deformed vertices give a `M + 5023` coarse surface. MARM predicts residual offsets `Δg` conditioned on canonical vertex PE, pose/expression θ, and camera parameters, applied to the FLAME-driven field.

### Implementation

- PyTorch, Adam, lr 4×10⁻⁵, 300,000 iterations; DINOv3 backbone frozen. Each batch samples 1∼8 frames from a monocular video. GAGAvatar tracker for camera/expression conditions.
- Trained on VFHQ (15,204 monocular clips, ~3M frames), images resized to 512×512 with background removal; evaluated zero-shot on NeRSemble and Ava-256.

## 📊 Results

Metrics: PSNR↑, SSIM↑, LPIPS↓ (rendering); CSIM↑ (identity), AED↓/APD↓ (motion); plus creation time and FPS.

원논문 Table 1 (VFHQ, novel expression).

| Method         | Setting  | PSNR↑ | SSIM↑ | LPIPS↓ | CSIM↑ | AED↓  | APD↓  | Creation↓ | FPS↑ |
| -------------- | -------- | ----- | ----- | ------ | ----- | ----- | ----- | --------- | ---- |
| Real3DPortrait | One-shot | 20.88 | 0.780 | 0.154  | 0.750 | 0.150 | 0.268 | 3.5s      | 15   |
| Portrait4D-v2  | One-shot | 21.34 | 0.794 | 0.144  | 0.717 | 0.117 | 0.187 | 2.9s      | 11   |
| GAGAvatar      | One-shot | 21.83 | 0.818 | 0.128  | 0.816 | 0.111 | 0.135 | 1.6s      | 63   |
| LAM            | One-shot | 22.65 | 0.829 | 0.109  | 0.822 | 0.102 | 0.134 | 1.1s      | 219  |
| FastAvatar     | One-shot | 17.85 | 0.813 | 0.167  | 0.679 | 0.136 | 0.328 | 2.6s      | 339  |
| Ours           | One-shot | 21.82 | 0.843 | 0.108  | 0.817 | 0.109 | 0.149 | 1.3s      | 31   |
| GPAvatar       | Few-shot | 22.91 | 0.795 | 0.154  | 0.765 | 0.138 | 0.189 | 0.7s      | 5    |
| FastAvatar     | Few-shot | 18.12 | 0.819 | 0.153  | 0.781 | 0.116 | 0.321 | 12.2s     | 97   |
| Ours(fast)     | Few-shot | 23.20 | 0.862 | 0.088  | 0.852 | 0.084 | 0.117 | 2.1s      | 468  |
| Ours           | Few-shot | 23.35 | 0.864 | 0.081  | 0.861 | 0.079 | 0.114 | 2.1s      | 31   |

In the few-shot setting FFAvatar is best on all image-quality and motion metrics. In one-shot it does not top every metric (LAM has higher PSNR 22.65 vs 21.82), but it leads SSIM/LPIPS. The fast variant (no MARM) reaches 468 FPS.

원논문 Table 2 (NeRSemble, zero-shot; NV = novel views, NE = novel expressions).

| Method          | Setting            | NV LPIPS↓ | NV SSIM↑ | NV PSNR↑ | NE LPIPS↓ | NE SSIM↑ | NE PSNR↑ |
| --------------- | ------------------ | --------- | -------- | -------- | --------- | -------- | -------- |
| Real3DPortrait  | One-shot           | 0.197     | 0.785    | 16.22    | 0.165     | 0.821    | 17.48    |
| Portrait4D-v2   | One-shot           | 0.172     | 0.797    | 16.81    | 0.152     | 0.814    | 18.24    |
| GAGAvatar       | One-shot           | 0.129     | 0.833    | 22.52    | 0.095     | 0.857    | 25.87    |
| LAM-20K         | One-shot           | 0.175     | 0.819    | 16.43    | 0.122     | 0.834    | 20.55    |
| FastAvatar      | One-shot           | 0.232     | 0.800    | 14.78    | 0.185     | 0.821    | 19.41    |
| Ours            | One-shot           | 0.121     | 0.839    | 19.18    | 0.106     | 0.851    | 20.23    |
| FlashAvatar     | Train From Scratch | 0.209     | 0.785    | 17.84    | 0.221     | 0.764    | 16.94    |
| GHA             | Train From Scratch | 0.269     | 0.722    | 13.93    | -         | -        | -        |
| GaussianAvatars | Train From Scratch | 0.164     | 0.813    | 17.99    | 0.178     | 0.822    | 17.56    |
| GPAvatar        | Few-shot           | 0.163     | 0.822    | 22.26    | 0.154     | 0.829    | 22.58    |
| FastAvatar      | Few-shot           | 0.158     | 0.824    | 20.11    | 0.135     | 0.845    | 22.49    |
| Ours            | Few-shot           | 0.098     | 0.858    | 21.95    | 0.075     | 0.881    | 24.08    |

FFAvatar leads LPIPS and SSIM in both few-shot settings, but the authors note honestly that **GAGAvatar reports higher PSNR in the one-shot setting** (22.52 / 25.87 vs FFAvatar's 19.18 / 20.23), and GPAvatar has slightly higher few-shot novel-view PSNR (22.26 vs 21.95).

### Ablations

원논문 Table 3 (number of input images, VFHQ novel expression).

| Inputs | PSNR↑ | SSIM↑ | LPIPS↓ | CSIM↑ | AED↓  | APD↓  | Creation↓ |
| ------ | ----- | ----- | ------ | ----- | ----- | ----- | --------- |
| 1      | 21.82 | 0.843 | 0.108  | 0.817 | 0.109 | 0.149 | 1.3s      |
| 4      | 22.75 | 0.858 | 0.091  | 0.852 | 0.094 | 0.119 | 1.7s      |
| 8      | 23.35 | 0.864 | 0.081  | 0.861 | 0.079 | 0.114 | 2.1s      |
| 16     | 23.36 | 0.866 | 0.080  | 0.872 | 0.078 | 0.110 | 4.3s      |
| 32     | 23.38 | 0.867 | 0.077  | 0.874 | 0.078 | 0.111 | 11.6s     |

The largest gain is from 1→8 frames; 16/32 frames give smaller but consistent improvements.

원논문 Table 4 (sparse-to-dense strategy; S = FLAME vertices only, D = dense point clouds, S2D = proposed). OOM under a 40 GB constraint; Time is per 1,000 iterations.

| Method  | UV Res | PSNR↑ | SSIM↑ | LPIPS↓ | CSIM↑ | AED↓  | APD↓  | Time↓  | Memory↓ |
| ------- | ------ | ----- | ----- | ------ | ----- | ----- | ----- | ------ | ------- |
| S-5K    | -      | 19.69 | 0.837 | 0.174  | 0.689 | 0.131 | 0.141 | 40min  | 22.5GB  |
| S2D-20K | 128    | 23.35 | 0.864 | 0.081  | 0.861 | 0.079 | 0.114 | 47min  | 25.8GB  |
| D-20K   | 128    | 23.41 | 0.869 | 0.097  | 0.858 | 0.087 | 0.115 | 120min | 38.2GB  |
| S2D-64K | 256    | 23.42 | 0.871 | 0.077  | 0.866 | 0.078 | 0.111 | 72min  | 37.1GB  |
| D-64K   | 256    | -     | -     | -      | -     | -     | -     | -      | OOM     |

Dense-only (D-20K) has marginally higher PSNR (23.41) but worse LPIPS (0.097 vs 0.081) and 2.5× the training time; dense-only at 256 UV resolution runs out of memory, whereas the sparse-to-dense variant fits and gives the best perceptual scores.

## 💡 Insights & Impact

- Anchoring a single unified canonical Gaussian field to FLAME (rather than fusing multiple view-dependent canonical subspaces) keeps Gaussian count and animation cost constant regardless of input-view count, which is what enables incremental reconstruction from 1 to hundreds of images.
- Sparse-to-dense modeling captures fine detail (hair, subtle texture) without the memory blowup of uniformly dense optimization; MARM adds identity-specific dynamics beyond the FLAME template.
- Combined with diffusion-based multi-view/expression synthesis (MMDM), the method can produce 4D avatars even from a single image, including AI-generated portraits.

## 🔗 Related Work

- The alternating-attention core is inspired by [VGGT](../reconstruction/vggt.md); the paper also cites FastVGGT ([FastVGGT](../reconstruction/fastvggt.md)) and the broader feed-forward reconstruction / LRM line ([DUSt3R](../foundation/dust3r.md)).
- Closely related feed-forward Gaussian head avatars include Avat3r ([Avat3r](avat3r.md)), GAGAvatar, LAM, GPAvatar, FastAvatar, and FastGHA; optimization baselines include GaussianAvatars, FlashAvatar, GHA.

## 📚 Key Takeaways

1. A FLAME-anchored unified canonical Gaussian field makes avatar cost independent of view count, enabling genuine incremental refinement as more portraits arrive.
2. Sparse-to-dense (vertex → UV) learning and a residual motion-refinement module together give a favorable fidelity/efficiency trade-off, with a 468-FPS fast variant.
3. FFAvatar leads perceptual metrics (SSIM/LPIPS) and few-shot quality, while the paper transparently reports that GAGAvatar keeps a PSNR edge in the one-shot NeRSemble setting.

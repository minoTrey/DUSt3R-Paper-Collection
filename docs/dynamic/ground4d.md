# Ground4D: Spatially-Grounded Feedforward 4D Reconstruction for Unstructured Off-Road Scenes (arXiv preprint (2026-05))

![ground4d — architecture](https://arxiv.org/html/2605.04435v1/x2.png)

_Overview of our Ground4D framework (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Shuo Wang, Jilin Mei, Fuyang Liu, Wenfei Guan, Fanjie Kong, Zhihua Zhao, Shuai Wang, Chen Min, Yu Hu
- **Institution**: Institute of Computing Technology, Chinese Academy of Sciences; Xi'an Jiaotong University; Beijing Institute of Technology
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.04435) | [Code](https://github.com/wsnbws/Ground4D)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A pose-free feedforward 4D Gaussian Splatting framework built on a frozen VGGT backbone that resolves spatial-temporal attribute conflicts in unstructured off-road scenes via voxel-grounded temporal Gaussian aggregation (intra-voxel query-conditioned attention + softmax normalization) plus surface-normal regularization.

## 🎯 Key Contributions

1. **Spatially-grounded 4D feedforward framework** for pose-free off-road reconstruction, addressing high-frequency geometry, ego-motion jitter, and diffuse non-rigid dynamics.
2. **Voxel-grounded temporal Gaussian aggregation**: Partitions canonical Gaussian space into voxels and applies query-conditioned temporal attention with intra-voxel softmax normalization, making temporal selectivity and spatial occupancy mutually reinforcing (avoiding both blurry fusion and structural holes).
3. **Surface normal regularization**: A normal head supervises geometry and injects features into the Gaussian head to regularize orientation in photometrically ambiguous regions.
4. **State-of-the-art off-road results** on ORAD-3D with zero-shot generalization to RELLIS-3D.

## 🔧 Technical Details

### Canonical Gaussian Space (frozen VGGT)

- A frozen VGGT backbone processes all `T` frames, producing cross-view, image-level, and DINOv2 semantic tokens. Only prediction heads and the temporal-fusion module are trained.
- Heads: camera, DPT depth, Gaussian attributes (11 channels: color, opacity, scale, rotation), surface normal, dynamic confidence, and a parametric sky model.
- Explicitly dynamic objects: a dynamic confidence head weights opacity by `(1 − Π_dyn)`; sparse 3D points tracked by a pretrained TAPIP3D and linearly interpolated to query times.

### Voxel-Grounded Temporal Aggregation

- **Spatial voxelization** (cell side `ρ`): quantizes Gaussian centers into voxels (non-differentiable grouping).
- **Query-conditioned temporal attention**: encodes each Gaussian's feature + sinusoidal time embedding, produces a relevance logit vs. query time `τ*`.
- **Intra-voxel normalization**: temperature-scaled softmax within each voxel; attribute-specific fusion (Euclidean mean for position/color, geometric mean in log-space for scale, quaternion mean + renormalization for rotation, weighted-mean/max blend for opacity).
- **Temporal augmentation**: random frame dropout (`p_drop = 0.7`) withholds the query-time frame to prevent nearest-neighbor degeneration.

### Training

- Loss: `L = L_rgb + L_lpips + L_dyn + L_sky + L_norm^pred + L_norm^gs`.
- Images 518×518; voxel `ρ = 0.002`, 10 frequency bands, opacity mix `λ = 0.3`, temperature `β` init 1.0, softmin `η = 10.0`; AdamW + cosine (1K warmup) for 2K epochs; two A6000 GPUs, batch 1, 4-frame sequences.

## 📊 Results

### Off-Road FFGS Comparison (원논문 Table 1)

원논문 Table 1. Time·Memory는 단일 A6000, 256×448, 4 context frames. RELLIS-3D는 zero-shot. RELLIS PSNR에서는 pose-supervised DepthSplat(22.29)이 Ground4D(22.12)보다 높다.

| Method       | ORAD PSNR ↑ | ORAD SSIM ↑ | ORAD LPIPS ↓ | RELLIS PSNR ↑ | RELLIS SSIM ↑ | RELLIS LPIPS ↓ | Dynamic | Pose-free | Time (s) | Mem (MB) |
| ------------ | ----------- | ----------- | ------------ | ------------- | ------------- | -------------- | ------- | --------- | -------- | -------- |
| MvSplat      | 15.01       | 0.30        | 0.53         | 9.95          | 0.16          | 0.68           | ✘       | ✘         | 0.03     | 2370     |
| DepthSplat   | 21.98       | 0.60        | 0.37         | **22.29**     | 0.52          | 0.34           | ✘       | ✘         | 0.01     | 7708     |
| STORM        | 20.56       | 0.54        | 0.44         | 18.40         | 0.46          | 0.56           | ✔       | ✔         | 0.08     | 16932    |
| NopoSplat    | 22.41       | 0.62        | 0.33         | 21.40         | 0.50          | 0.38           | ✘       | ✔         | 1.47     | 9744     |
| DGGT         | 21.76       | 0.61        | 0.32         | 21.27         | 0.53          | 0.36           | ✔       | ✔         | 0.08     | 15576    |
| **Ground4D** | **23.89**   | **0.64**    | **0.23**     | 22.12         | **0.55**      | **0.28**       | ✔       | ✔         | 0.17     | 15566    |

On ORAD-3D, Ground4D's 23.89 dB is a 1.48 dB PSNR gain over the strongest baseline (NopoSplat, 22.41).

### Urban Generalization — nuScenes (원논문 Table 2)

원논문 Table 2. Ground4D는 nuScenes에서 fine-tune. DGGT는 LPIPS(0.122)에서 Ground4D(0.135)보다 낮다.

| Method         | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| -------------- | --------- | --------- | --------- |
| MVSplat        | 22.83     | 0.629     | 0.317     |
| DepthSplat     | 19.52     | 0.601     | 0.376     |
| Drivingforward | 26.06     | 0.781     | 0.215     |
| STORM          | 24.54     | 0.784     | 0.267     |
| DGGT           | 26.63     | 0.813     | **0.122** |
| **Ours**       | **27.23** | **0.814** | 0.135     |

### Ablation: Voxel-Grounded Aggregation (원논문 Table 3)

원논문 Table 3. TA=Temporal Attention, IN=Intra-Voxel Normalization. Voxelize+TA만으로는 오히려 하락; IN이 있어야 개선.

| Voxelize | TA  | IN  | PSNR ↑    | SSIM ↑   | LPIPS ↓  |
| -------- | --- | --- | --------- | -------- | -------- |
| –        | –   | –   | 22.45     | 0.62     | 0.34     |
| –        | ✔   | –   | 21.70     | 0.61     | 0.33     |
| ✔        | –   | –   | 22.88     | 0.62     | 0.30     |
| ✔        | ✔   | –   | 22.47     | 0.62     | 0.35     |
| ✔        | ✔   | ✔   | **23.89** | **0.64** | **0.23** |

### Ablation: Voxel Size (원논문 Table 5)

원논문 Table 5. ρ=0.002에서 canonical Gaussian이 약 600K→370K(1.6×)로 압축; ρ=0.005는 2.85 dB PSNR 하락.

| ρ     | PSNR ↑    | SSIM ↑   | LPIPS ↓  |
| ----- | --------- | -------- | -------- |
| 0.001 | 23.50     | 0.63     | 0.24     |
| 0.002 | **23.89** | **0.64** | **0.23** |
| 0.003 | 23.71     | 0.63     | 0.25     |
| 0.005 | 21.04     | 0.57     | 0.35     |

### Ablation: Context Frames (원논문 Table 6)

원논문 Table 6. 10프레임에서 정점 후 saturate.

| Context Frames | PSNR ↑    | SSIM ↑   | LPIPS ↓  |
| -------------- | --------- | -------- | -------- |
| 4              | 23.89     | 0.64     | 0.23     |
| 7              | 23.99     | 0.65     | 0.23     |
| 10             | **24.05** | **0.65** | **0.22** |
| 13             | 23.76     | 0.64     | 0.24     |
| 16             | 23.65     | 0.63     | 0.25     |

Surface-normal regularization (원논문 Table 4) improves PSNR 23.45 → 23.89 and LPIPS 0.27 → 0.23.

## 💡 Insights & Impact

- Naive fusion (NopoSplat) blurs co-located Gaussians; per-Gaussian temporal modeling (DGGT) collapses occupancy into structural holes; confining temporal competition to spatial voxels resolves both.
- Temporal attention without intra-voxel normalization can hurt (22.88 → 22.47 PSNR); normalization is the key that makes selectivity and occupancy mutually reinforcing.
- The voxel-grounded prior transfers zero-shot across off-road domains and even extends to structured urban driving scenes.

## 🔗 Related Work

- Backbone [VGGT](../reconstruction/vggt.md); foundation [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md).
- Closest driving-scene feedforward baseline [DGGT](dggt.md); also compared against STORM, NopoSplat, MvSplat, DepthSplat.

## 📚 Key Takeaways

1. Intra-voxel spatial grounding of temporal competition is the core idea enabling high-fidelity pose-free 4D reconstruction in chaotic off-road scenes.
2. State-of-the-art on ORAD-3D (1.48 dB PSNR over the best baseline) with zero-shot RELLIS-3D transfer — honestly noting pose-supervised DepthSplat edges out RELLIS PSNR and DGGT wins nuScenes LPIPS.
3. Surface-normal regularization and careful voxel sizing (ρ=0.002) are essential to the geometric quality.

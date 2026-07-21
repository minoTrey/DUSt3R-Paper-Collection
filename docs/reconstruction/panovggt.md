# PanoVGGT: Feed-Forward 3D Reconstruction from Panoramic Imagery (CVPR 2026)

## 📋 Overview

- **Authors**: Yijing Guo, Mengjun Chao, Luo Wang, Tianyang Zhao, Haizhao Dai, Yingliang Zhang, Jingyi Yu, Yujiao Shi
- **Institution**: ShanghaiTech University; Sudo
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.17571)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A permutation-equivariant transformer that jointly predicts camera poses, depth, and consistent 3D point clouds from one or more unordered panoramas in a single forward pass, using spherical-aware positional embeddings and three-axis SO(3) rotation augmentation, plus a new 120K-panorama outdoor dataset PanoCity.

## 🎯 Key Contributions

1. **Panoramic feed-forward reconstruction**: PanoVGGT extends the permutation-equivariant transformer paradigm (VGGT / π³) to full-spherical panoramas, jointly regressing poses, dense depth, and globally consistent point clouds in one pass.
2. **Spherical-aware design**: A circularly symmetric 4D spherical positional embedding preserves wrap-around continuity at the panorama seam, and a panorama-specific three-axis SO(3) rotation augmentation decouples fixed positions from rotated content, avoiding specialized spherical convolutions.
3. **Stochastic anchoring**: A randomly selected reference panorama defines the world frame each iteration, resolving global-frame ambiguity while preserving permutation equivariance.
4. **PanoCity dataset**: Over 120,000 outdoor panoramas (4096×2048 equirectangular RGB, 16-bit depth, 6DoF pose) rendered in UE5 + AirSim under five weather/illumination conditions.

## 🔧 Technical Details

### Framework

Each panorama is tokenized by a DINOv2 encoder, augmented with SO(3) rotation, and encoded with shared and branch-adapted spherical positional embeddings. A Geometric Aggregator of L Alternating-Attention blocks (frame-wise self-attention then global self-attention, following π³/VGGT) reasons jointly over local and cross-view geometry, feeding three prediction heads: camera pose (SE(3)), local point clouds, and world-frame global point clouds. Over-complete supervision (explicitly regressing 3D points in addition to pose+depth) improves accuracy and robustness.

### Losses

Scale-consistent local and global geometry losses (ℓ1) share a single optimal scale s* per sample (following π³), plus a normal-consistency SmoothL1 regularization and relative pose supervision (angular rotation loss + scale-consistent translation loss). Final loss weights: λ_T = 100, λ_g = 0.1.

### Training

8 NVIDIA A100 GPUs for roughly ten days at 336×672 input; sequences of length N ∈ [2, 24] dynamically sampled, up to 384 images/GPU with eight-step gradient accumulation. Panoramas resized to 512×1024 for training and evaluation.

## 📊 Results

Evaluated on Matterport3D, Stanford2D3D, Structured3D, Pano3D, and PanoCity. Multi-view experiments use a three-view protocol. Baselines: Bifusev2, VGGT, π³, and π³* (π³ retrained on panoramas).

### Camera Pose — AUC@30↑

원논문 Table 2. Higher is better.

| Method       | Matterport3D | Stanford2D3D | PanoCity  |
| ------------ | ------------ | ------------ | --------- |
| Bifusev2     | 0.007        | 0.030        | 0.833     |
| VGGT         | 0.034        | 0.047        | 0.205     |
| π³           | 0.047        | 0.076        | 0.571     |
| π³\*         | 0.305        | 0.274        | 0.682     |
| **PanoVGGT** | **0.459**    | **0.556**    | **0.949** |

### Monocular Depth — Indoor

원논문 Table 3. Abs Rel lower is better, δ<1.25 higher is better.

| Model        | Input      | MP3D AbsRel↓ | MP3D δ↑    | S2D3D AbsRel↓ | S2D3D δ↑   |
| ------------ | ---------- | ------------ | ---------- | ------------- | ---------- |
| BiFuse++     | Monocular  | 0.1076       | 0.8846     | 0.1120        | 0.8805     |
| EGFormer     | Monocular  | 0.0987       | 0.9082     | 0.0929        | 0.8890     |
| PanoVGGT     | Monocular  | 0.0884       | 0.9157     | **0.0711**    | **0.9392** |
| **PanoVGGT** | Multi-view | **0.0840**   | **0.9266** | 0.0778        | 0.9323     |

BiFuse++ and EGFormer show slight advantages on Structured3D and PanoCity (per-dataset depth-only models); PanoVGGT is a single unified pose-depth-point model and reaches state of the art on Matterport3D and Stanford2D3D.

### Point Cloud Reconstruction — PanoCity

원논문 Table 5. Mean distances, lower is better. "†" = perspective-based model via dodecahedral projection.

| Method                   | Acc↓ (Mean) | Comp↓ (Mean) | Overall↓ (Mean) |
| ------------------------ | ----------- | ------------ | --------------- |
| π³                       | 1.404       | 11.737       | 6.570           |
| π³†                      | 1.261       | 15.182       | 8.222           |
| π³\*                     | 1.111       | 1.037        | 1.074           |
| PanoVGGT (global points) | 0.768       | 0.705        | **0.737**       |
| PanoVGGT (local points)  | 0.744       | 0.756        | 0.750           |

### Ablation (Matterport3D, three-view)

원논문 Table 6. Progressive component addition; epoch-100 checkpoint.

| Components              | Pose AUC@30↑ | Depth AbsRel↓ | Depth δ<1.25↑ |
| ----------------------- | ------------ | ------------- | ------------- |
| Baseline (π³\*)         | 0.228        | 0.194         | 0.709         |
| + PanoCity              | 0.256        | 0.105         | 0.896         |
| + Tri-axis aug          | 0.285        | 0.116         | 0.871         |
| + Global pt. fusion     | 0.380        | 0.103         | 0.894         |
| + Pos. embedding (Full) | **0.427**    | **0.098**     | **0.908**     |

The paper notes translation error slightly increases after adding tri-axis spherical augmentation, attributed to greater orientation diversity delaying translation convergence under the short 100-epoch ablation schedule.

## 💡 Insights & Impact

- **Perspective priors transfer partially**: VGGT/π³ pretrained on perspective data still work near the panorama equator (where local geometry approximates pinhole), but degrade with spherical distortion — motivating panorama-specific training.
- **Augmentation compels rotational robustness**: Full SO(3) augmentation is only possible because panoramas support valid spherical rotations, forcing the model to learn genuine rotational robustness rather than equirectangular projection biases.
- **Zero-shot generalization**: On Pano3D (GibsonV2), PanoVGGT outperforms prior methods across most metrics under both scale-only and scale+shift alignment.
- **Limitations**: Pose estimation remains sensitive to extreme domain shifts, and the design is tailored to equirectangular projections.

## 🔗 Related Work

- **[VGGT](vggt.md)** & **[π³ (pi3)](pi3.md)**: The perspective-domain permutation-equivariant foundations PanoVGGT adapts to the spherical domain.
- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: The feed-forward pointmap lineage.
- **[MoGe](moge.md)** & **[MoGe-2](moge-2.md)**: Monocular geometry baselines used in the zero-shot dodecahedral-projection depth comparison.
- **[MonST3R](../dynamic/monst3r.md)**: Referenced dynamic-scene pointmap variant.

## 📚 Key Takeaways

1. PanoVGGT is the first unified feed-forward model to jointly predict pose, depth, and consistent 3D point clouds from unordered panoramas in a single pass.
2. Spherical-aware positional embeddings plus three-axis SO(3) augmentation deliver rotation-aware geometry without spherical convolutions; stochastic anchoring resolves global-frame ambiguity.
3. It achieves the best pose AUC on all three benchmarks and state-of-the-art indoor depth on Matterport3D/Stanford2D3D, though per-dataset depth-only models can still edge it on some datasets.
4. PanoCity contributes a large-scale (120K) annotated outdoor panoramic dataset for this underexplored setting.

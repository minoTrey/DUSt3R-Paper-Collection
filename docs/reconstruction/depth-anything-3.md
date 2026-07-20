# DA3: Recovering the Visual Space from Any Views (ICLR 2026)

## 📋 Overview

- **Authors**: Haotong Lin, Sili Chen, Jun Hao Liew, Donny Y. Chen, Zhenyu Li, Guang Shi, Jiashi Feng, Bingyi Kang
- **Institution**: ByteDance Seed
- **Venue**: ICLR 2026
- **Award**: Oral
- **Links**: [Paper](https://arxiv.org/abs/2511.10647) | [Project Page](https://depth-anything-3.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A single plain transformer (vanilla DINOv2) trained on a minimal depth-ray prediction target reconstructs geometry from any number of views, with or without known poses, setting a new state of the art across pose, geometry, and rendering benchmarks.

## 🎯 Key Contributions

1. **Minimal prediction target**: A depth map plus a per-pixel ray map replaces the redundant multi-task cocktail (point maps + depth + camera + tracks) used by prior unified models.
2. **Single plain transformer**: No bespoke two-stream architecture. Cross-view reasoning comes from an input-adaptive self-attention that rearranges tokens, not from new modules.
3. **Dual-DPT head**: Depth and ray branches share reassembly modules and diverge only at the fusion stage, encouraging aligned outputs.
4. **Teacher-student training**: A monocular teacher trained purely on synthetic data produces dense pseudo-depth, RANSAC-aligned to the original sparse/noisy ground truth.
5. **New visual geometry benchmark**: 5 datasets (HiRoom, ETH3D, DTU, 7Scenes, ScanNet++), 89+ scenes, jointly measuring pose and reconstruction accuracy — plus a 160+ scene feed-forward NVS benchmark.
6. **Optional pose conditioning**: Known camera parameters enter as camera tokens through a lightweight MLP encoder; otherwise a shared learnable placeholder token is used.

## 🔧 Technical Details

### Depth-Ray Representation

Instead of predicting a rotation matrix under an orthogonality constraint, DA3 represents the camera implicitly as a dense per-pixel ray map `M ∈ R^{H×W×6}` storing ray origin `t ∈ R³` and direction `d = RK⁻¹p`. Directions are deliberately left unnormalized so their magnitude preserves projection scale, making a world point simply:

```text
P = t + D(u, v) · d
```

Camera parameters are recovered from the ray map by averaging per-pixel origins for the center `t_c`, then solving a homography `H = KR` via DLT and decomposing it with RQ decomposition. Because this is costly at inference, a lightweight camera head predicts FOV `f ∈ R²`, quaternion `q ∈ R⁴`, and translation `t ∈ R³` directly from one token per view.

### Architecture

- **Backbone**: Pretrained ViT (DINOv2), `L = Ls + Lg` blocks
- **Attention split**: first `Ls` layers do within-image self-attention; the last `Lg` layers alternate cross-view and within-view attention via tensor reordering. Ratio `Ls : Lg = 2 : 1`
- **Camera token**: prepended per view, participates in all attention operations
- **Dual-DPT head**: shared reassembly modules → two fusion stacks (depth / ray) → two output layers

The design is input-adaptive: with a single image the model degenerates to monocular depth estimation at no extra cost.

### Training

- DA3-Giant: 128×H100 GPUs for roughly 10 days
- Ablations: ViT-L backbone, max 10 views, ~4 days on 32×H100 GPUs
- Teacher-generated pseudo-depth aligned to sparse ground truth via RANSAC least squares
- Trained exclusively on public academic datasets

## 📊 Results

### Camera Pose Accuracy — Static Object & Indoor Scenes

원논문 Table 2. 두 지표 모두 높을수록 좋다.

| Methods     | Params | HiRoom Auc3 ↑ | HiRoom Auc30 ↑ | ETH3D Auc3 ↑ | ETH3D Auc30 ↑ | DTU Auc3 ↑ | DTU Auc30 ↑ |
| ----------- | ------ | ------------- | -------------- | ------------ | ------------- | ---------- | ----------- |
| DUSt3R      | 0.57B  | 17.6          | 54.3           | 4.30         | 27.3          | 4.00       | 74.3        |
| Fast3R      | 0.65B  | 25.9          | 77.0           | 8.10         | 44.4          | 9.50       | 79.1        |
| MapAnything | 0.56B  | 17.9          | 82.8           | 19.2         | 77.4          | 6.50       | 72.7        |
| Pi3         | 0.96B  | 67.0          | 94.8           | 35.2         | 87.3          | 62.5       | 94.9        |
| VGGT        | 1.19B  | 49.1          | 88.0           | 26.3         | 80.8          | **79.2**   | **99.8**    |
| DA3-Giant   | 1.10B  | **80.3**      | **95.9**       | **48.4**     | **91.2**      | 94.1       | 99.4        |
| DA3-Large   | 0.36B  | 58.7          | 94.2           | 32.2         | 86.9          | 70.2       | 96.7        |
| DA3-Base    | 0.11B  | 19.0          | 83.2           | 15.1         | 74.6          | 60.1       | 95.9        |
| DA3-Small   | 0.03B  | 9.49          | 75.2           | 8.59         | 62.1          | 30.6       | 91.2        |

DTU Auc30 is the single setting where DA3-Giant does not lead — VGGT reaches 99.8 against DA3-Giant's 99.4.

원논문 Table 2 (계속).

| Methods     | 7Scenes Auc3 ↑ | 7Scenes Auc30 ↑ | ScanNet++ Auc3 ↑ | ScanNet++ Auc30 ↑ |
| ----------- | -------------- | --------------- | ---------------- | ----------------- |
| DUSt3R      | 6.90           | 61.6            | 8.10             | 33.9              |
| Fast3R      | 19.0           | 78.6            | 17.9             | 72.5              |
| MapAnything | 12.6           | 79.7            | 20.2             | 84.1              |
| Pi3         | 25.5           | 86.3            | 50.7             | 92.1              |
| VGGT        | 23.9           | 85.0            | 62.6             | 95.1              |
| DA3-Giant   | 28.5           | **86.8**        | **85.0**         | **98.1**          |
| DA3-Large   | **29.2**       | 86.6            | 60.2             | 94.7              |
| DA3-Base    | 20.1           | 82.9            | 25.1             | 83.4              |
| DA3-Small   | 14.0           | 78.7            | 10.9             | 71.9              |

### Reconstruction Accuracy

원논문 Table 3. DTU를 제외한 모든 데이터셋은 F-Score (F1 ↑), DTU는 chamfer distance (CD ↓, 단위 mm).
`w/o p.`와 `w/ p.`는 ground-truth 카메라 포즈 제공 여부.

| Methods     | HiRoom w/o p. F1 ↑ | HiRoom w/ p. F1 ↑ | ETH3D w/o p. F1 ↑ | ETH3D w/ p. F1 ↑ | DTU w/o p. CD ↓ | DTU w/ p. CD ↓ |
| ----------- | ------------------ | ----------------- | ----------------- | ---------------- | --------------- | -------------- |
| DUSt3R      | 30.1               | 39.5              | 19.7              | 18.8             | 7.60            | 7.97           |
| Fast3R      | 40.7               | 48.2              | 38.5              | 50.3             | 6.88            | 8.20           |
| MapAnything | 32.4               | 69.2              | 54.8              | 71.9             | 7.91            | 3.97           |
| Pi3         | 75.8               | 85.0              | 72.7              | 80.6             | 3.28            | 1.72           |
| VGGT        | 56.7               | 70.2              | 57.2              | 66.7             | 2.05            | 1.44           |
| DA3-Giant   | **85.1**           | **95.6**          | **79.0**          | **87.1**         | **1.85**        | 1.85           |
| DA3-Large   | 69.5               | 87.1              | 65.8              | 75.2             | 2.08            | **1.23**       |

On DTU with ground-truth poses, DA3-Giant's CD of 1.85 is worse than VGGT's 1.44, Pi3's 1.72, and its own smaller DA3-Large at 1.23 — pose conditioning does not help the Giant model on this object-centric set.

원논문 Table 3 (계속). 두 지표 모두 F-Score (F1 ↑).

| Methods     | 7Scenes w/o p. | 7Scenes w/ p. | ScanNet++ w/o p. | ScanNet++ w/ p. |
| ----------- | -------------- | ------------- | ---------------- | --------------- |
| DUSt3R      | 26.6           | 39.8          | 18.9             | 27.3            |
| Fast3R      | 41.0           | 49.8          | 37.1             | 53.7            |
| MapAnything | 44.8           | 55.2          | 39.4             | 71.3            |
| Pi3         | 44.2           | **57.5**      | 63.1             | 73.3            |
| VGGT        | 47.9           | 51.4          | 66.4             | 70.7            |
| DA3-Giant   | 53.5           | 56.5          | **77.0**         | **79.3**        |
| DA3-Large   | **56.3**       | 49.2          | 67.9             | 75.7            |

The paper notes 7Scenes is the exception where pose conditioning brings little benefit — the limited video setting already saturates performance.

### Monocular Depth

원논문 Table 4. δ1 ↑. Rank는 낮을수록 좋다.

| Method  | KITTI    | NYU      | SINTEL   | ETH3D    | DIODE    | Rank     |
| ------- | -------- | -------- | -------- | -------- | -------- | -------- |
| DA2     | 94.6     | **97.9** | **77.2** | 86.5     | 95.2     | 2.60     |
| VGGT    | 91.7     | **97.9** | 67.9     | 97.5     | 95.3     | 3.75     |
| DA3     | **95.3** | 97.4     | 75.5     | **98.6** | **95.4** | **2.20** |
| Teacher | 97.2     | 97.9     | 81.4     | 99.8     | 96.6     | 1.00     |

DA3 overtakes DA2 on average rank but still trails it on NYU and SINTEL.

### Feed-Forward Novel View Synthesis

원논문 Table 5. 12개 context view, 270 × 480 해상도.

| Methods    | DL3DV PSNR ↑ | DL3DV SSIM ↑ | DL3DV LPIPS ↓ | T&T PSNR ↑ | T&T SSIM ↑ | T&T LPIPS ↓ |
| ---------- | ------------ | ------------ | ------------- | ---------- | ---------- | ----------- |
| pixelSplat | 16.55        | 0.456        | 0.480         | 13.81      | 0.347      | 0.558       |
| MVSplat    | 18.13        | 0.559        | 0.393         | 14.81      | 0.391      | 0.508       |
| DepthSplat | 19.24        | 0.620        | 0.322         | 15.80      | 0.474      | 0.418       |
| Fast3R     | 19.30        | 0.604        | 0.320         | 16.24      | 0.478      | 0.409       |
| MV-DUSt3R  | 20.01        | 0.645        | 0.294         | 17.04      | 0.529      | 0.370       |
| VGGT       | 20.96        | 0.697        | 0.253         | 17.18      | 0.550      | 0.347       |
| DAv3       | **21.33**    | **0.711**    | **0.241**     | **18.10**  | **0.578**  | **0.311**   |

원논문 Table 5 (계속). MegaDepth (19 scenes), out-of-domain.

| Methods    | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| ---------- | --------- | --------- | --------- |
| pixelSplat | 13.87     | 0.367     | 0.561     |
| MVSplat    | 14.67     | 0.398     | 0.533     |
| DepthSplat | 15.90     | 0.471     | 0.450     |
| Fast3R     | 16.43     | 0.493     | 0.421     |
| MV-DUSt3R  | 16.20     | 0.484     | 0.437     |
| VGGT       | 16.45     | 0.500     | 0.417     |
| DAv3       | **17.89** | **0.561** | **0.351** |

### Ablation: Prediction Targets

원논문 Table 6. 모든 실험은 camera condition token 없이 ViT-L 백본으로 수행.

| Methods           | HiRoom Auc3 ↑ | HiRoom F1 ↑ | ETH3D Auc3 ↑ | ETH3D F1 ↑ | DTU Auc3 ↑ | DTU CD ↓  |
| ----------------- | ------------- | ----------- | ------------ | ---------- | ---------- | --------- |
| depth + pcd + cam | 9.1           | 12.8        | 19.0         | 60.4       | 42.3       | 4.918     |
| depth + cam       | 10.8          | 16.5        | 9.9          | 48.0       | 23.3       | 5.316     |
| **depth + ray**   | **48.7**      | **60.3**    | **25.5**     | **65.4**   | 46.5       | 3.919     |
| depth + ray + cam | 37.2          | 45.4        | 22.3         | 59.4       | **56.3**   | **3.066** |

Adding an auxiliary camera head brings no consistent benefit, confirming that depth + ray is sufficient. DA3 nonetheless adopts depth + ray + cam because the camera head costs roughly 0.1% of the backbone's compute.

### Ablation: Architecture

원논문 Table 7. (b) VGGT Style은 두 개의 별도 transformer를 쌓은 구성, (c) Full Alt.는 모든 레이어에서 교대 어텐션.

| Methods           | HiRoom Auc3 ↑ | HiRoom F1 ↑ | ETH3D Auc3 ↑ | ETH3D F1 ↑ | DTU CD ↓ | 7Scenes F1 ↑ |
| ----------------- | ------------- | ----------- | ------------ | ---------- | -------- | ------------ |
| a. Proposed Arch. | **39.2**      | **47.0**    | **21.0**     | **55.4**   | **3.82** | 47.6         |
| b. VGGT Style     | 3.72          | 14.5        | 2.31         | 27.4       | 6.93     | 21.4         |
| c. Full Alt.      | 24.7          | 29.3        | 13.1         | 51.9       | 4.23     | **48.6**     |
| d. w/o Dual DPT   | 5.59          | 11.5        | 13.6         | 33.4       | 5.14     | 49.4         |
| e. w/o Teacher    | 11.2          | 16.0        | 16.2         | 57.6       | 3.29     | 40.3         |

Removing the teacher improves DTU (3.29 vs 3.82) but degrades HiRoom sharply — the paper attributes this to HiRoom's fine synthetic structures.

### Model Scale and Throughput

원논문 Table 8. A100 GPU, 32장 장면, 504 × 336, 이미지당 평균 속도.

| Model            | Max # of Images | Backbone | DualDPT | CameraHead | Running Speed |
| ---------------- | --------------- | -------- | ------- | ---------- | ------------- |
| VGGT (Reference) | 400-500         | 0.91B    | 0.064B  | 0.22B      | 34.1 FPS      |
| DA3-Giant        | 900-1000        | 1.130B   | 0.050B  | 0.018B     | 37.6 FPS      |
| DA3-Large        | 1500-1600       | 0.300B   | 0.047B  | 0.008B     | 78.37 FPS     |
| DA3-Base         | 2100-2200       | 0.086B   | 0.015B  | 0.004B     | 126.5 FPS     |
| DA3-Small        | 4000-4100       | 0.022B   | 0.003B  | 0.001B     | 160.5 FPS     |

## 💡 Insights & Impact

### Redundancy Was Never the Point

VGGT's design bet was that predicting overlapping targets (point maps, depth, cameras, tracks) regularizes the shared representation. DA3's Table 6 argues the opposite: redundant targets entangle rather than reinforce, and `depth + ray` alone beats `depth + pcd + cam` on every dataset and metric in the ablation.

### Pretraining Beats Architecture

The VGGT-style ablation (item b) collapses to a small fraction of the proposed architecture's scores. The paper attributes this to full pretraining of a single backbone versus roughly two-thirds untrained blocks in a stacked two-transformer design. The implication is uncomfortable but clear — much of the architectural specialization in this literature is paying for lost pretraining.

### Pose Estimation Scales Harder Than Depth

With pose conditioning supplied, gains from scaling model size shrink markedly. The paper reads this as evidence that pose estimation, not depth, is what demands larger models.

### Geometry Quality Transfers to Rendering

In the FF-NVS benchmark, ranking by NVS quality reproduces the ranking by geometry quality (Fast3R < MV-DUSt3R < VGGT < DA3). A plain geometry backbone plus a DPT Gaussian head beats specialist 3DGS models built on epipolar transformers and cost volumes.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The direct predecessor and primary baseline. DA3 keeps the alternating-attention idea but discards the two-transformer stack and the redundant multi-task heads, and reports large gains on HiRoom, ETH3D, and ScanNet++ pose accuracy.
- **[Pi3](pi3.md)**: The permutation-equivariant contemporary. The paper explicitly calls its own contribution orthogonal to Pi3's, and Pi3 remains the strongest baseline on 7Scenes `w/ p.` F1 (57.5).
- **[MapAnything](mapanything.md)**: The other pose-conditionable model in the comparison. Both exploit known poses, but MapAnything trails DA3 on nearly every pose-free setting.
- **[Fast3R](fast3r.md)**: Included as the many-view point-map baseline in both the geometry and NVS tables.
- **[DUSt3R](../foundation/dust3r.md)**: The pairwise origin the related-work section credits as the turning point; here the weakest baseline across the board.
- **[MoGe](moge.md)**: Shares the monocular-depth lineage that DA3's teacher model draws on.

## 📚 Key Takeaways

1. **A minimal target set is sufficient**: depth + ray captures both scene structure and camera motion; extra heads add cost, not accuracy.
2. **A plain pretrained transformer suffices**: cross-view reasoning can come from token rearrangement instead of new architecture, and preserves the backbone's scaling properties.
3. **Teacher-student pseudo-labeling unifies messy data**: dense synthetic-trained pseudo-depth, RANSAC-aligned to sparse real ground truth, buys detail without sacrificing geometric accuracy.
4. **DA3 is not uniformly ahead**: VGGT still wins DTU Auc30, and DA2 still wins NYU and SINTEL monocular depth.
5. **Geometry backbones are the right substrate for NVS**: the FF-NVS benchmark shows reconstruction quality and rendering quality move together.

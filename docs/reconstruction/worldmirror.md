# WorldMirror: Universal 3D World Reconstruction with Any-Prior Prompting (ICML 2026)

![worldmirror — architecture](https://arxiv.org/html/2510.10726/Figs/teaser.png)

_WorldMirror is a large feed-forward 3D reconstruction model that takes raw images along with optional priors (depth, calibrated intrinsics, camera… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Yifan Liu, Zhiyuan Min, Zhenwei Wang, Junta Wu, Tengfei Wang, Yixuan Yuan, Yawei Luo, Chunchao Guo
- **Institution**: Zhejiang University, Chinese University of Hong Kong, Tencent Hunyuan
- **Venue**: ICML 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.10726)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: An all-in-one feed-forward model that accepts any subset of camera pose, intrinsics, and depth priors as prompt tokens and jointly outputs point maps, depth, camera parameters, surface normals, and 3D Gaussians in a single pass.

## 🎯 Key Contributions

1. **Multi-Modal Prior Prompting**: calibrated intrinsics, camera poses, and depth maps are encoded into tokens and injected into a VGGT-style backbone; a dynamic prior injection scheme randomly samples prior combinations during training so the model handles arbitrary subsets (including none) at inference.
2. **Universal Geometric Prediction**: one framework covering point maps, multi-view depth, camera parameters, surface normals, and 3D Gaussians — extending VGGT's task set with normal estimation and novel view synthesis.
3. **Systematic curriculum learning** across three axes: task sequencing, data scheduling, and progressive resolution.

## 🔧 Technical Details

### Encoding each prior modality differently

The paper argues prior modalities should not be treated uniformly, and encodes each according to its information density:

- **Camera pose**: the scene is first normalised to a unit cube (`t_norm = (t − c)/α`, with `c` the camera center and `α` the maximum camera-to-center distance). The rotation is converted to a quaternion and concatenated with `t_norm` into a 7-vector, projected by a two-layer MLP into a **single token** `T^cam ∈ R^{1×D}`.
- **Calibrated intrinsics**: `(f_x, f_y, c_x, c_y)` normalised by image width and height, then a two-layer MLP into a **single token** `T^intr ∈ R^{1×D}`.
- **Depth map**: normalised to `[0,1]` and patchified by a convolutional layer whose kernel matches the visual patch size, producing **dense tokens** that are spatially aligned with the image tokens and **added** to them.

The prompted token set is `T^prompt = [T^cam, T^intr, T^img + T^depth]`.

### Prediction heads

Following VGGT, DPT heads regress the dense outputs (point map `P̂`, multi-view depth `D̂`) and transformer layers decode camera parameters `Ê` from the camera tokens. Surface normals use the same DPT architecture followed by L2 normalisation to enforce unit vectors. Because ground-truth normal annotations are scarce, the paper uses hybrid supervision: annotated datasets plus pseudo-normals derived from ground-truth depth by plane fitting.

### 3D Gaussians

A DPT head regresses pixel-wise Gaussian depth maps and Gaussian feature maps. Gaussian centers are obtained by back-projecting the depth predictions with ground-truth camera poses and intrinsics; remaining attributes (opacity, orientation, scale, residual SH colour coefficients, fusion weight) come from combining the feature map with convolutional appearance features. Per-pixel Gaussians are clustered and pruned by voxelisation to reduce redundancy from overlapping views, following AnySplat. During training, inputs are split into context and target sets — Gaussians are built only from context views but supervised on both target and context viewpoints.

### Loss

`L = L_points + L_depth + L_cam + L_normal + L_3dgs`.

## 📊 Results

### Point map reconstruction

원논문 Table 1. Accuracy and Completion, mean values only (the paper also reports medians). Multi-view images use the fixed sequence-id mappings from π³.

| Method                     | 7-Scenes Acc.↓ | 7-Scenes Comp.↓ | NRGBD Acc.↓ | NRGBD Comp.↓ | DTU Acc.↓ | DTU Comp.↓ |
| -------------------------- | -------------- | --------------- | ----------- | ------------ | --------- | ---------- |
| Fast3R                     | 0.096          | 0.145           | 0.135       | 0.163        | 3.340     | 2.929      |
| CUT3R                      | 0.094          | 0.101           | 0.104       | 0.079        | 4.742     | 3.400      |
| FLARE                      | 0.085          | 0.142           | 0.053       | 0.051        | 2.541     | 3.174      |
| VGGT                       | 0.046          | 0.057           | 0.051       | 0.066        | 1.338     | 1.896      |
| π³                         | 0.048          | 0.072           | 0.026       | 0.028        | 1.198     | 1.849      |
| WorldMirror                | 0.043          | 0.049           | 0.041       | 0.045        | 1.017     | 1.780      |
| WorldMirror (w/ all three) | **0.018**      | **0.023**       | **0.016**   | **0.014**    | **0.735** | **0.935**  |

"w/ all three" is the intrinsics + depth + camera pose configuration. Without any prior, WorldMirror is behind π³ on NRGBD (0.041 vs 0.026 Acc.). The paper reports mean-accuracy gains of 10.4% and 17.8% over prior SOTA on 7-Scenes and DTU, and 58.1% / 53.1% gains from all priors over its own no-prior baseline on 7-Scenes and NRGBD.

원논문 Table 1, single-prior rows on 7-Scenes and DTU (mean).

| Configuration               | 7-Scenes Acc.↓ | 7-Scenes Comp.↓ | DTU Acc.↓ | DTU Comp.↓ |
| --------------------------- | -------------- | --------------- | --------- | ---------- |
| WorldMirror (no prior)      | 0.043          | 0.049           | 1.017     | 1.780      |
| WorldMirror (w/ intrinsics) | 0.042          | 0.048           | 0.977     | 1.762      |
| WorldMirror (w/ depth)      | 0.038          | 0.039           | 0.831     | 1.022      |
| WorldMirror (w/ pose)       | 0.023          | 0.036           | 0.990     | 1.847      |

Depth is the most useful prior for DTU; camera pose is the most useful for 7-Scenes.

### Camera pose estimation

원논문 Table 2. All datasets are excluded from training, except that RealEstate10K was in CUT3R's training set.

| Method      | Re10K RRA@30↑ | Re10K RTA@30↑ | Re10K AUC@30↑ | Sintel ATE↓ | Sintel RPE trans↓ | Sintel RPE rot↓ |
| ----------- | ------------- | ------------- | ------------- | ----------- | ----------------- | --------------- |
| Fast3R      | 99.05         | 81.86         | 61.68         | 0.371       | 0.298             | 13.75           |
| CUT3R       | 99.82         | 95.10         | 81.47         | 0.217       | 0.070             | 0.636           |
| FLARE       | 99.69         | 95.23         | 80.01         | 0.207       | 0.090             | 3.015           |
| VGGT        | 99.97         | 93.13         | 77.62         | 0.167       | 0.062             | 0.491           |
| π³          | **99.99**     | 95.62         | 85.90         | **0.074**   | **0.040**         | **0.282**       |
| WorldMirror | **99.99**     | **95.81**     | **86.28**     | 0.096       | 0.058             | 0.490           |

WorldMirror trails π³ on all three Sintel metrics; the paper attributes this to limited outdoor dynamic scenes in its training data.

원논문 Table 2, TUM-dynamics.

| Method      | TUM ATE↓  | TUM RPE trans↓ | TUM RPE rot↓ |
| ----------- | --------- | -------------- | ------------ |
| Fast3R      | 0.090     | 0.101          | 1.425        |
| CUT3R       | 0.047     | 0.015          | 0.451        |
| FLARE       | 0.026     | 0.013          | 0.475        |
| VGGT        | 0.012     | 0.010          | 0.312        |
| π³          | 0.014     | **0.009**      | 0.312        |
| WorldMirror | **0.010** | **0.009**      | **0.297**    |

### Surface normal estimation

원논문 Table 3. Angular error (mean / median, lower better) and percentage of pixels below 22.5° and 30.0° thresholds. EESNU is trained on ScanNet, so its in-domain row is omitted by the authors.

| Method       | ScanNet mean↓ | ScanNet 30°↑ | NYUv2 mean↓ | NYUv2 30°↑ | iBims-1 mean↓ | iBims-1 30°↑ |
| ------------ | ------------- | ------------ | ----------- | ---------- | ------------- | ------------ |
| OASIS        | 32.8          | 52.6         | 29.2        | 60.7       | 32.6          | 57.4         |
| Omnidata v2  | 16.2          | 84.7         | 17.2        | 83.0       | 18.2          | 81.1         |
| DSine        | 16.2          | 84.4         | 16.4        | 83.5       | 17.1          | 82.3         |
| GeoWizard    | 16.7          | 84.2         | 19.5        | 81.6       | 20.4          | 80.6         |
| StableNormal | 16.0          | 86.5         | 18.5        | 83.6       | 17.9          | **83.9**     |
| WorldMirror  | **13.8**      | **87.3**     | **15.1**    | **85.7**   | **16.6**      | 83.7         |

On iBims-1, StableNormal keeps a marginally better 30° threshold score.

### Novel view synthesis

원논문 Table 4. FLARE targets sparse-view NVS, so its dense-view results are omitted by the authors.

| Method                        | Re10K (2 v) PSNR↑ | Re10K (2 v) LPIPS↓ | DL3DV (8 v) PSNR↑ | DL3DV (8 v) LPIPS↓ |
| ----------------------------- | ----------------- | ------------------ | ----------------- | ------------------ |
| FLARE                         | 16.33             | 0.410              | 15.35             | 0.591              |
| AnySplat                      | 17.62             | 0.242              | 18.31             | 0.258              |
| WorldMirror                   | 20.62             | 0.187              | 20.92             | 0.203              |
| WorldMirror (w/ intr. + pose) | **22.30**         | **0.155**          | **22.15**         | **0.174**          |

원논문 Table 4, dense-view settings.

| Method                        | Re10K (32 v) PSNR↑ | Re10K (32 v) LPIPS↓ | DL3DV (64 v) PSNR↑ | DL3DV (64 v) LPIPS↓ |
| ----------------------------- | ------------------ | ------------------- | ------------------ | ------------------- |
| AnySplat                      | 19.96              | 0.234               | 18.40              | 0.286               |
| WorldMirror                   | 25.14              | 0.109               | 21.25              | 0.223               |
| WorldMirror (w/ intr. + pose) | **25.77**          | **0.101**           | **21.66**          | **0.204**           |

### Prior embedding ablation

원논문 Table 5. Averaged over ETH3D and DTU with 10 input views. The single-token design wins on the aggregate average and uses far fewer extra parameters.

| Prior embedding                | Extra Params | Focal acc@1.03↑ | Pose AUC@5↑ | Point τ@1.03↑ | Avg. ↑    |
| ------------------------------ | ------------ | --------------- | ----------- | ------------- | --------- |
| **Input: images & poses**      |              |                 |             |               |           |
| Dense Plücker                  | 9.02M        | 33.07           | 72.74       | 33.74         | 60.44     |
| Single Token                   | **1.06M**    | **33.82**       | **74.55**   | **38.51**     | **61.06** |
| **Input: images & intrinsics** |              |                 |             |               |           |
| Dense Raymap                   | 6.65M        | **86.48**       | 60.57       | **37.40**     | 66.58     |
| Single Token                   | **1.06M**    | 84.43           | **66.52**   | 36.29         | **68.96** |

### Prior-guidance benchmark

Section 4.2 measures inlier ratio at a 1.03 relative threshold for points and depths, AUC@5, and average focal error in pixels over ETH3D and DTU. These results appear only as Fig. 6 with no printed values, so no numbers are transcribed here. The stated finding is that adding a single modality prior improves both its corresponding task and the model's other geometric predictions.

### Novel view synthesis ablation

원논문 Table 6.

| Method          | Re10K (2 v) PSNR↑ | DL3DV (8 v) PSNR↑ | VR-NeRF (32 v) PSNR↑ |
| --------------- | ----------------- | ----------------- | -------------------- |
| w/o GT Cameras  | **20.30**         | 20.69             | 24.76                |
| w/o Novel Views | 18.51             | 20.21             | 24.35                |
| w/o GS DPT      | 20.28             | 20.55             | 25.08                |
| Ours            | 20.29             | **20.91**         | **25.75**            |

Novel-view supervision is the component that matters most; the GT-camera and GS-DPT ablations are near-ties on RealEstate10K.

## 💡 Insights & Impact

### Priors as prompts, not as architecture

The paper's framing is that geometric priors — intrinsics, poses, depth — are routinely available in real deployments (calibration files, LiDAR, RGB-D sensors) yet discarded by image-only feed-forward models. Rather than building a separate model per input configuration, WorldMirror trains one model with randomly sampled prior subsets so that any combination, including the empty set, is a valid inference-time input. This is the same "any-prior" motivation as Pow3R, extended from the DUSt3R pairwise setting to a dense multi-view VGGT-style backbone.

### Compact beats dense for compact quantities

The ablation is the most transferable finding: a camera pose or an intrinsics matrix is a handful of numbers, and compressing it into a single token outperforms spreading it over dense per-pixel Plücker or raymap embeddings — while costing roughly one-sixth to one-ninth the extra parameters. Only depth, which genuinely is a dense spatial signal, is embedded densely.

### Multi-task transfer

Adding surface normals and 3D Gaussians to the task set does not appear to cost accuracy on the classical tasks; the paper argues shared representations across a broader task set let the multi-task model outperform specialised single-task normal estimators like DSine and StableNormal.

### Limits

Sintel camera pose remains behind π³, and the no-prior configuration does not uniformly beat π³ on point maps. The strongest results all require priors that image-only baselines do not receive, which is the intended use case but is not an apples-to-apples comparison.

## 🔗 Related Work

- [VGGT](./vggt.md) — the architecture and multi-task template WorldMirror extends.
- [pi3](./pi3.md) — the strongest image-only baseline; source of the evaluation protocol and sequence-id mappings.
- [Pow3R](./pow3r.md) — the closest prior-conditioning precedent, limited to sparse-view DUSt3R-style inputs.
- [CUT3R](../dynamic/cut3r.md) — recurrent baseline in the point map and pose tables.
- [Fast3R](./fast3r.md) — multi-view feed-forward baseline.
- [MapAnything](./mapanything.md) — related any-input/any-output universal reconstruction direction.
- [DUSt3R](../foundation/dust3r.md) — the paradigm origin.

## 📚 Key Takeaways

1. **One model, any prior subset.** Dynamic prior injection during training removes the need for separate models per input configuration and lets priors be optional at inference.
2. **Match the embedding to the modality.** Single-token embeddings win for poses and intrinsics; dense token addition is reserved for depth.
3. **Priors compound.** All three priors together cut mean accuracy roughly in half versus WorldMirror's own no-prior baseline on 7-Scenes and NRGBD.
4. **The task set is genuinely broader** than VGGT's — surface normals and feed-forward 3D Gaussians are added, and the normal results beat dedicated normal estimators on ScanNet and NYUv2.
5. **Not uniformly ahead.** π³ retains the edge on Sintel pose, and StableNormal on one iBims-1 metric.

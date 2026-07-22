# AMB3R: Accurate Feed-forward Metric-scale 3D Reconstruction with Backend (CVPR 2026)

![amb3r — architecture](https://arxiv.org/html/2511.20343/x2.png)

_Overview of AMB3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Hengyi Wang, Lourdes Agapito
- **Institution**: Department of Computer Science, University College London
- **Venue**: CVPR 2026
- **Award**: Highlight
- **Links**: [Paper](https://arxiv.org/abs/2511.20343) | [Code](https://github.com/HengyiWang/amb3r) | [Project Page](https://hengyiwang.github.io/projects/amber)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A sparse volumetric backend bolted onto a frozen VGGT front-end recovers metric scale and performs explicit 3D geometric reasoning, extending without fine-tuning to visual odometry, SLAM, and structure from motion.

## 🎯 Key Contributions

1. **Sparse volumetric backend**: pointmaps and geometric features are fused into a sparse voxel grid, serialized by space-filling curves, processed by Point Transformer v3, and read back via KNN interpolation.
2. **Frozen front-end + zero convolution**: VGGT stays frozen; backend features re-enter each decoder layer through zero convolution, reusing the learned attention and confidence functions and cutting training cost drastically.
3. **Per-frame metric scale regression**: instead of regressing a global scale that depends on all frames, AMB3R regresses the metric log depth of the median-depth pixel per frame and takes the median at inference.
4. **Training-free task extension**: uncalibrated VO, SLAM, and large-scale SfM all fall out of the same model with no task-specific fine-tuning or test-time optimization.
5. **Extremely cheap training**: 40 epochs × 2000 samples = 80K samples, roughly 50 H100 GPU hours for the backend — less than a single epoch of VGGT's training data.

## 🔧 Technical Details

### Backend

Given front-end pointmaps `{P_t^(1)}` and geometric features `{G_t}`, voxel features are averaged within each occupied voxel:

```text
H_i = (1/|P_i|) · Σ_{(t,u) ∈ P_i} G_t[u]
```

Voxel size is 0.01 in normalized space, which yields adaptive resolution as scene scale varies. The sparse grid is serialized to 1D, processed, and unserialized:

```text
{Ĥ_i} = (S⁻¹ ∘ f_θ ∘ S)({H_i})
```

with `f_θ` implemented as Point Transformer v3, a U-Net-like architecture. Per-point features come back by KNN interpolation `G̃_t[u] = KNN(P_t^(1)[u], {Ĥ})` and are fused into every decoder layer through zero convolution.

### Why Zero Convolution Matters

Confidence in these models is learned self-supervised and depends on both data distribution and training recipe. Fine-tuning a pretrained model on a different distribution risks catastrophic forgetting of the learned confidence. The ablation confirms this bluntly: without zero convolution the model fails to converge at all under the paper's compute budget.

### Metric Scale

A global scale regressed via a ROE solver depends on all frames and proved hard to train and prone to overfitting — the scale difference varies with frame combination and even frame order. Regressing per-frame metric log depth of the median-depth pixel captures an intrinsic per-frame property recoverable from individual encoder features, avoiding dependence on the model's global prediction.

### Training

The front-end (VGGT) is frozen. Loss matches VGGT minus tracking:

```text
L = L_depth + L_pointmap + L_camera
```

Because loss, data, and preprocessing differ from VGGT, the canonical scale learned by minimizing L may not match VGGT's. Predictions are therefore ROE-aligned to normalized ground truth before supervision — one scale per sequence for pointmaps, an independent scale per image for depth. Backend trained for 40 epochs on a mixture of 12 datasets, 5–16 frames per sample.

### Visual Odometry

Rewriting VGGT's token-based temporal encoding as a memory formulation lets carefully selected keyframes serve as memory. Pose distance is `D_{i,j} = arccos((Tr(R_j R_iᵀ) − 1)/2) + λ‖τ'_i − τ'_j‖₂`, with minimum keyframe distance `η_d = 0.15` and mapping window `N_w = 8`. New windows are ROE-scaled against keyframes and fused into the global map by confidence-weighted running average, with SLERP for rotations. Active keyframes cap at `N_max = 10`, resampling to `N_min = 7`. The backend runs only when front-end confidence falls below a threshold.

### Structure from Motion

Divide-and-conquer: whitened feature descriptors build a distance matrix, Furthest Point Sampling with iterative splitting and merging forms clusters, then incremental registration proceeds without optimization. Coarse registration keeps a global keyframe list with `η_d = 0.2`, partitioning into sub-clusters when keyframes exceed `N_k^max = 8`. Global mapping refines via confidence-prioritized breadth-first search over the keyframe graph.

## 📊 Results

### Monocular Depth

원논문 Table 1. Rel은 낮을수록, δ1.25는 높을수록 좋다. 괄호는 학습 데이터셋을 뜻한다.

| Method        | NYUv2 Rel ↓ | NYUv2 δ1.25 ↑ | KITTI Rel ↓ | KITTI δ1.25 ↑ | ETH3D Rel ↓ | ETH3D δ1.25 ↑ |
| ------------- | ----------- | ------------- | ----------- | ------------- | ----------- | ------------- |
| Omnidata      | 7.4         | 94.5          | 14.9        | 83.5          | 16.6        | 77.8          |
| DepthAny v2   | 4.3         | 97.9          | 8.0         | 94.4          | 5.7         | 98.3          |
| Marigold      | 5.5         | 96.4          | 9.9         | 91.6          | 6.5         | 96.0          |
| Diffusion-E2E | 5.2         | 96.6          | 9.6         | 91.9          | 6.2         | 95.9          |
| MoGe          | 3.6         | 98.0          | **5.5**     | **97.6**      | 3.3         | 98.8          |
| VGGT          | 3.6         | 98.0          | 8.8         | 92.7          | 3.8         | 97.9          |
| AMB3R         | **3.0**     | **98.9**      | 7.3         | 95.4          | **3.2**     | **98.8**      |

원논문 Table 1 (계속).

| Method      | ScanNet Rel ↓ | ScanNet δ1.25 ↑ | DIODE Rel ↓ | DIODE δ1.25 ↑ |
| ----------- | ------------- | --------------- | ----------- | ------------- |
| Omnidata    | 7.5           | 93.6            | 33.9        | 74.2          |
| DepthAny v2 | (4.2)         | (97.9)          | 21.6        | 75.2          |
| MoGe        | 3.5           | 98.3            | **22.4**    | **82.3**      |
| VGGT        | (2.7)         | (98.8)          | 26.9        | 79.1          |
| AMB3R       | (2.7)         | (98.9)          | 24.7        | 80.7          |

MoGe still leads on KITTI and DIODE — AMB3R's claim is consistent improvement over VGGT, not universal SOTA.

### Camera Pose Estimation

원논문 Table 2. RealEstate10K에서 전체 시퀀스로부터 10프레임 무작위 추출, AUC@30 ↑.
VGGT는 두 개 열로, 공식 보고치와 저자 재현치를 함께 싣는다.

| Method              | Re10K AUC@30 ↑ |
| ------------------- | -------------- |
| DUSt3R              | 67.7           |
| MASt3R              | 76.4           |
| Fast3R              | 72.7           |
| VGGT (official)     | 85.3           |
| VGGT (authors' run) | 81.8           |
| AMB3R               | **86.3**       |

### Multi-View Depth on Robust-MVD

원논문 Table 3, (e) 그룹 (포즈 없이 프레임만 사용). ‡는 동시기 연구, 괄호는 학습 데이터셋.

| Method  | KITTI rel ↓ | KITTI δ1.03 ↑ | ScanNet rel ↓ | ScanNet δ1.03 ↑ | ETH3D rel ↓ | ETH3D δ1.03 ↑ |
| ------- | ----------- | ------------- | ------------- | --------------- | ----------- | ------------- |
| DeMoN   | 15.5        | 15.2          | 12.0          | 21.0            | 17.4        | 15.4          |
| DUSt3R  | 5.4         | 49.5          | (3.1)         | (71.8)          | 3.0         | 76.0          |
| Spann3R | 7.9         | 36.2          | (3.3)         | (67.1)          | 5.7         | 58.6          |
| Pow3R   | 5.7         | 45.7          | (3.2)         | (68.8)          | 3.0         | 74.7          |
| MUSt3R  | 4.5         | 55.0          | (4.0)         | (59.8)          | 2.5         | 80.3          |
| VGGT    | 4.5         | 59.6          | (2.3)         | (80.8)          | 1.8         | 86.3          |
| π³‡     | **2.8**     | 72.9          | (2.0)         | (83.6)          | **1.3**     | **92.4**      |
| MapAny‡ | 4.0         | 59.4          | 4.0           | 60.5            | 2.8         | 73.2          |
| AMB3R   | **2.8**     | **74.4**      | **(1.9)**     | **(85.8)**      | 1.4         | 90.9          |

원논문 Table 3 (계속).

| Method  | DTU rel ↓ | DTU δ1.03 ↑ | T&T rel ↓ | T&T δ1.03 ↑ | Avg rel ↓ | Avg δ1.03 ↑ |
| ------- | --------- | ----------- | --------- | ----------- | --------- | ----------- |
| DUSt3R  | 3.9       | 68.6        | 3.3       | 75.1        | 3.7       | 68.2        |
| MUSt3R  | 4.6       | 55.4        | (2.6)     | (80.4)      | 3.7       | 66.2        |
| VGGT    | **0.9**   | **95.6**    | 2.4       | 84.1        | 2.4       | 81.3        |
| π³‡     | 1.3       | 91.8        | 1.8       | 87.3        | 1.8       | 85.6        |
| MapAny‡ | 3.9       | 63.7        | 3.3       | 73.0        | 3.6       | 66.0        |
| AMB3R   | **0.9**   | 95.1        | **1.7**   | **90.2**    | **1.7**   | **87.3**    |

ETH3D δ1.03 and DTU δ1.03 both go to competitors — π³ at 92.4 and VGGT at 95.6 respectively.

### Multi-View 3D Reconstruction

원논문 Table 5. 단위 [cm]. Acc는 정확도, Cp는 완전성. ETH3D·DTU는 RMVDB 이미지 튜플, 7-Scenes는 Spann3R 프레임.

| Method  | ETH3D rel ↓ | ETH3D Acc ↓ | ETH3D Cp ↓ | DTU rel ↓ | DTU Acc ↓ | DTU Cp ↓ |
| ------- | ----------- | ----------- | ---------- | --------- | --------- | -------- |
| Spann3R | 24.96       | 47.63       | 31.87      | 4.96      | 1.89      | 0.64     |
| MUSt3R  | 19.91       | 45.19       | 82.72      | 5.26      | 1.68      | 1.09     |
| CUT3R   | 18.83       | 38.90       | 22.93      | 9.11      | 3.75      | 0.96     |
| VGGT    | 6.02        | 12.81       | 11.89      | 0.83      | **0.22**  | **0.08** |
| π³‡     | 5.82        | 10.54       | 10.42      | 1.57      | 0.50      | 0.29     |
| MapAny‡ | 11.20       | 21.87       | 19.76      | 10.37     | 4.35      | 1.54     |
| AMB3R   | **4.64**    | **9.98**    | **9.69**   | **0.81**  | **0.22**  | **0.08** |

원논문 Table 5 (계속). 7-Scenes.

| Method  | rel ↓    | Acc ↓    | Cp ↓     |
| ------- | -------- | -------- | -------- |
| Spann3R | 8.58     | 4.81     | 5.48     |
| MUSt3R  | 11.57    | 8.94     | 14.97    |
| CUT3R   | 6.32     | 2.88     | 3.26     |
| VGGT    | 5.51     | 2.32     | 3.51     |
| π³‡     | 5.92     | 2.60     | 3.42     |
| MapAny‡ | 7.61     | 3.48     | 3.33     |
| AMB3R   | **4.74** | **1.74** | **2.84** |

### Video Depth

원논문 Table 6. Sintel과 Bonn은 전체 장면으로 평가 (선행 연구의 14개·4개 선별과 다름).
AMB3R는 동적 데이터셋 전용 파인튜닝을 하지 않았다.

| Method  | Sintel rel ↓ | Sintel δ1.03 ↑ | Sintel δ1.25 ↑ | Bonn rel ↓ | Bonn δ1.03 ↑ | Bonn δ1.25 ↑ |
| ------- | ------------ | -------------- | -------------- | ---------- | ------------ | ------------ |
| Spann3R | 55.2         | 7.3            | 46.3           | 5.5        | 40.9         | 97.8         |
| CUT3R   | 58.4         | 9.6            | 46.6           | 5.1        | 47.4         | 98.0         |
| VGGT    | 28.0         | 13.6           | 61.8           | 3.6        | 63.2         | 98.4         |
| π³      | 31.9         | 13.3           | **66.8**       | **3.0**    | **72.0**     | **98.8**     |
| AMB3R   | **23.6**     | **14.0**       | 62.7           | 3.3        | 66.0         | 98.5         |

π³ leads Bonn outright and Sintel δ1.25 — but it fine-tunes on dynamic datasets, which AMB3R does not.

원논문 Table 6 (계속). KITTI.

| Method  | rel ↓   | δ1.03 ↑  | δ1.25 ↑  |
| ------- | ------- | -------- | -------- |
| Spann3R | 24.7    | 10.4     | 64.4     |
| CUT3R   | 13.6    | 18.0     | 81.0     |
| VGGT    | 8.2     | 40.4     | 90.9     |
| π³      | **3.6** | **59.5** | **98.8** |
| AMB3R   | 4.1     | 53.8     | 98.3     |

### Uncalibrated Visual Odometry — TUM RGB

원논문 Table 8. ATE RMSE [cm]. 베이스라인은 loop closure와 global bundle adjustment 없이 재실행.
S는 sparse, D는 dense, U는 dense unconstrained 방식. 먼저 fr1 시퀀스.

| Method      | fr1 360 | fr1 desk | fr1 desk2 | fr1 plant | fr1 room | fr1 rpy | fr1 teddy | fr1 xyz |
| ----------- | ------- | -------- | --------- | --------- | -------- | ------- | --------- | ------- |
| DPVO        | 13.1    | 9.4      | 6.5       | 3.0       | 39.8     | 3.5     | 6.2       | 1.3     |
| DeepFactors | 17.9    | 15.9     | 20.2      | 31.9      | 38.3     | 3.8     | 56.0      | 5.9     |
| DepthCov    | 12.8    | 5.6      | 4.8       | 26.1      | 25.7     | 5.2     | 47.5      | 5.6     |
| DROID-VO    | 15.7    | 5.2      | 11.1      | 6.0       | 33.4     | 3.2     | 19.1      | 5.6     |
| COMO        | 12.9    | 4.9      | 9.5       | 13.8      | 27.0     | 4.8     | 24.5      | 4.0     |
| GlORIE-VO   | 13.1    | 4.0      | 8.6       | 4.1       | 32.7     | 2.9     | 14.5      | 1.2     |
| Spann3R     | 20.7    | 16.1     | 28.3      | 57.4      | 84.8     | 6.1     | 92.4      | 2.1     |
| MUSt3R      | 8.9     | 5.1      | 7.1       | 5.4       | 13.4     | 5.2     | 6.9       | 2.7     |
| AMB3R (ALL) | 4.6     | 1.9      | 2.8       | 2.9       | 5.8      | 2.3     | 3.7       | 1.1     |
| AMB3R (KF)  | **3.9** | **1.7**  | **2.3**   | **2.7**   | **5.5**  | **2.2** | **2.8**   | **0.8** |

원논문 Table 8 (계속). fr2·fr3 시퀀스와 전체 평균.

| Method      | fr2 xyz | fr2 desk | fr3 long | AVG     |
| ----------- | ------- | -------- | -------- | ------- |
| DPVO        | 0.5     | 3.5      | 5.5      | 8.4     |
| DeepFactors | 8.4     | 26.3     | 49.0     | 24.9    |
| DepthCov    | 1.2     | 15.9     | 68.8     | 19.9    |
| DROID-VO    | 10.7    | 7.9      | 7.3      | 11.4    |
| COMO        | 0.7     | 6.3      | 10.5     | 10.8    |
| GlORIE-VO   | **0.2** | 16.1     | 4.8      | 9.3     |
| Spann3R     | 4.4     | 20.7     | 193.9    | 47.9    |
| MUSt3R      | 1.7     | 15.6     | 4.3      | 7.1     |
| AMB3R (ALL) | 2.1     | 3.4      | 5.0      | 3.2     |
| AMB3R (KF)  | 0.6     | **3.0**  | **4.0**  | **2.7** |

### Uncalibrated Visual Odometry — ETH3D SLAM

원논문 Table 10. ATE RMSE [cm]. MUSt3R와 동일한 장면 집합, image stride 2.

| Method      | cables1 | camshake1 | einstein1 | plant1  | plant2  | sofa1   | table3  | table7  | avg     |
| ----------- | ------- | --------- | --------- | ------- | ------- | ------- | ------- | ------- | ------- |
| Spann3R     | 33.2    | 5.1       | 30.9      | 4.1     | 5.7     | 17.1    | 19.3    | 18.9    | 16.8    |
| MUSt3R      | 20.7    | 5.6       | 15.4      | 2.3     | 2.7     | 15.8    | 17.6    | 9.5     | 11.2    |
| MUSt3R⋆     | 20.7    | 5.3       | 11.2      | 1.8     | 2.7     | 15.5    | 17.3    | 5.5     | 10.0    |
| AMB3R (ALL) | 2.8     | 2.4       | 2.3       | 1.5     | 1.6     | 3.6     | 3.7     | 2.8     | 2.6     |
| AMB3R (KF)  | **2.3** | **2.1**   | **1.9**   | **0.5** | **0.9** | **3.1** | **2.6** | **2.4** | **2.0** |

### SLAM on TUM RGB

원논문 Table 9. ATE RMSE [cm], image stride 2, MASt3R-SLAM과 동일한 keyframe pose 평가.
베이스라인은 loop closure와 global bundle adjustment를 후처리로 사용할 수 있다.

| Method           | 360     | desk    | desk2   | floor   | plant   | room    | rpy     | teddy   | xyz     | avg     |
| ---------------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| **Calibrated**   |         |         |         |         |         |         |         |         |         |         |
| DPV-SLAM++       | 13.2    | 1.8     | 2.9     | 5.0     | 2.2     | 9.6     | 3.2     | 9.8     | 1.0     | 5.4     |
| GO-SLAM          | 8.9     | **1.6** | 2.8     | 2.5     | 2.6     | 5.2     | **1.9** | 4.8     | 1.0     | 3.5     |
| DROID-SLAM       | 11.1    | 1.8     | 4.2     | 2.1     | **1.6** | 4.9     | 2.6     | 4.8     | 1.2     | 3.8     |
| MASt3R-SLAM      | 4.9     | **1.6** | 2.4     | 2.5     | 2.0     | 6.1     | 2.7     | 4.1     | 0.9     | 3.0     |
| **Uncalibrated** |         |         |         |         |         |         |         |         |         |         |
| DROID-SLAM       | 20.2    | 3.2     | 9.1     | 6.4     | 4.5     | 91.8    | 5.6     | 4.5     | 1.2     | 15.8    |
| MASt3R-SLAM      | 7.0     | 3.5     | 5.5     | 5.6     | 3.5     | 11.8    | 4.1     | 11.4    | 2.0     | 6.0     |
| VGGT-SLAM        | 7.1     | 2.5     | 4.0     | 14.1    | 2.3     | 10.2    | 3.0     | 3.4     | 1.4     | 5.3     |
| AMB3R (ALL)      | 4.6     | 1.9     | 2.8     | 3.2     | 2.9     | 5.8     | 2.3     | 3.7     | 1.1     | 3.1     |
| AMB3R (KF)       | **3.9** | 1.7     | **2.3** | **2.7** | 2.7     | **5.5** | 2.2     | **2.8** | **0.8** | **2.7** |

AMB3R runs uncalibrated with no trajectory post-processing yet beats the calibrated MASt3R-SLAM average of 3.0 with 2.7.

### Dynamic Scenes — TUM Dynamic

원논문 Table 11. ATE RMSE. MUSt3R⋆는 re-rendering과 궤적 평활화를 사용하고,
MegaSaM은 keyframe을 사용하며 동적 환경 전용으로 설계된 방법이다.

| Method  | sit xyz | desk p  | walk rpy | walk s  | walk h  | sit s   | sit h   | walk x  | sit r   | avg     |
| ------- | ------- | ------- | -------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| MUSt3R  | 3.5     | 3.3     | 6.7      | 2.2     | 5.5     | 1.5     | 5.3     | 7.8     | 4.9     | 4.5     |
| MUSt3R⋆ | 2.4     | 2.2     | 5.0      | 1.9     | 3.9     | 1.3     | 4.6     | 5.4     | 4.0     | 3.4     |
| MegaSaM | **1.1** | OOM     | **3.3**  | **0.6** | **1.8** | **0.6** | **2.5** | **1.4** | 2.5     | —       |
| AMB3R   | 1.3     | **2.1** | 4.2      | 0.9     | 1.9     | 0.8     | 2.2     | 2.0     | **2.0** | **1.9** |

MegaSaM — explicitly designed for dynamic scenes with global bundle adjustment and trajectory smoothing — is better on most individual scenes but runs out of memory on `desk p`.

### Structure from Motion on ETH3D

원논문 Table 12. RRA@5 / RTA@5, 높을수록 좋다. AMB3R는 최적화 기반 BA를 사용하지 않는다.

| Method      | RRA@5 ↑  | RTA@5 ↑  |
| ----------- | -------- | -------- |
| COLMAP      | 49.0     | 47.8     |
| ACE-Zero    | 16.4     | 9.7      |
| VGGSfM      | 65.4     | 58.9     |
| DF-SfM      | 74.2     | 70.7     |
| MASt3R-SfM  | 81.2     | 79.7     |
| AMB3R (SfM) | **98.2** | **81.9** |

### Structure from Motion on Tanks & Temples

원논문 Table 13. 장면당 151–1106장. 모든 장면에서 성공한 방법만 남겼다.

| Method      | Training RRA@5 ↑ | Training RTA@5 ↑ | Intermediate RRA@5 ↑ | Intermediate RTA@5 ↑ | Advanced RRA@5 ↑ | Advanced RTA@5 ↑ |
| ----------- | ---------------- | ---------------- | -------------------- | -------------------- | ---------------- | ---------------- |
| ACE-Zero    | 73.9             | 72.9             | 67.6                 | 74.0                 | 22.9             | 19.1             |
| MASt3R-SfM  | 56.2             | 64.9             | 50.8                 | 57.5                 | 38.8             | 36.5             |
| AMB3R (SfM) | **95.0**         | **94.5**         | **98.7**             | **96.9**             | **68.0**         | **72.4**         |

### VO Trajectory vs Pseudo Ground Truth on 7-Scenes

원논문 Table 7. ATE RMSE [cm]와 novel view synthesis PSNR.
COLMAP GT는 각 장면의 전체 시퀀스로 산출.

| Metric | Method      | chess   | fire    | head    | office  | pump    | redkit  | stair | avg     |
| ------ | ----------- | ------- | ------- | ------- | ------- | ------- | ------- | ----- | ------- |
| ATE ↓  | Pseudo GT   | 3.5     | 2.5     | **1.4** | 9.4     | 15.1    | 4.9     | 2.9   | 5.7     |
| ATE ↓  | AMB3R (ALL) | **1.8** | **1.8** | 2.1     | **4.7** | **2.4** | **1.6** | 3.7   | **2.1** |
| PSNR ↑ | COLMAP (GT) | 25.3    | 25.7    | 22.6    | 25.8    | 25.0    | 21.9    | 24.7  | 24.4    |
| PSNR ↑ | Pseudo GT   | 21.2    | 22.1    | 21.2    | 22.6    | 22.6    | 19.9    | 23.1  | 21.8    |
| PSNR ↑ | AMB3R       | 20.6    | 22.3    | 20.2    | 22.0    | 23.6    | 21.8    | 22.2  | 21.8    |

### Ablations

원논문 Table 14. 3D backend와 alternating attention 기반 2D backend 비교.

| Method       | ETH3D rel ↓ | ETH3D Acc ↓ | ETH3D Cp ↓ | 7-Scenes rel ↓ | 7-Scenes Acc ↓ | 7-Scenes Cp ↓ |
| ------------ | ----------- | ----------- | ---------- | -------------- | -------------- | ------------- |
| w/o backend  | 6.02        | 12.81       | 11.89      | 5.51           | 2.32           | 3.51          |
| w 2D backend | 5.32        | 11.78       | 12.78      | 5.15           | 1.92           | 3.10          |
| Full         | **4.64**    | **9.98**    | **9.69**   | **4.74**       | **1.74**       | **2.84**      |

원논문 Table 15. RMVDB 평균 기준 설계 선택 ablation.

| Method          | Avg rel ↓ | Avg δ ↑  |
| --------------- | --------- | -------- |
| w/o backend     | 2.3       | 80.6     |
| w/ 2d backend   | 1.8       | 86.2     |
| w/o scale align | 1.9       | 86.2     |
| w/o zero conv   | 17.5      | 19.9     |
| Full            | **1.7**   | **87.3** |

Without zero convolution the model does not converge at all under the paper's compute budget — 17.5 average rel against 1.7.

## 💡 Insights & Impact

### Reasoning in 3D, Not in Token Space

Every model in this lineage reasons about geometry through 2D attention over image tokens. AMB3R's argument is that correspondence — the many-to-one mapping from pixels to 3D points — is naturally expressed in a compact 3D representation, as classical TSDF and cost-volume methods knew. The 3D-vs-2D backend ablation supports this: matched-capacity alternating attention improves less than the sparse voxel backend on every metric.

### Freezing Is Cheaper Than Fine-Tuning, and Safer

Reusing VGGT frozen with zero-convolution injection is presented as a cost measure, but the ablation reveals it is also a correctness measure. The confidence function learned by the front-end is fragile under distribution shift; zero convolution preserves it. The result is a state-of-the-art system for roughly 50 H100 GPU hours of added training.

### Coordinate Alignment Is Unnecessary

The paper points out a prior that VO systems built on pointmap models have been ignoring: predictions always live in the reference frame's coordinate system, up to an unknown median scale. So no rigid transformation needs estimating — only a scale. AMB3R maps the global map into the local frame, estimates scale, and averages relative poses, avoiding explicit Kabsch–Umeyama alignment entirely.

### Feed-Forward SfM Without Bundle Adjustment

On ETH3D unordered image collections and Tanks & Temples video, AMB3R beats optimization-based SfM including MASt3R-SfM and ACE-Zero without any bundle adjustment. Divide-and-conquer clustering plus confidence-prioritized BFS mapping substitutes for global optimization.

### Its Own Stated Limits

The supplement notes the system can fail under long-term kidnapping scenarios, where an optimization-based loop closure module would help. And on DTU, larger absolute errors appear in scenes with toy buildings on white tables with dark backgrounds, which some models mistake for real structures.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The frozen front-end. AMB3R's gains are explicitly attributed to improved geometric features from the backend, since VGGT's weights never change. Its type-(c) token-based temporal encoding is what AMB3R reinterprets as a memory formulation for VO.
- **[DUSt3R](../foundation/dust3r.md)**: Categorized as type-(a) network-based temporal encoding — two intertwined decoders, inherently limited to two images.
- **[Spann3R](spann3r.md)**: Type-(b) causal temporal encoding, where each frame queries accumulated memory. Baseline across depth, reconstruction, and VO.
- **[MUSt3R](must3r.md)**: The previous uncalibrated VO state of the art, which AMB3R surpasses on TUM, ETH3D SLAM, and TUM Dynamic.
- **[CUT3R](../dynamic/cut3r.md)**: Streaming baseline in the reconstruction and video depth tables.
- **[Pi3](pi3.md)**: The strongest concurrent competitor; it wins ETH3D δ1.03, Bonn video depth, and KITTI video depth, though it fine-tunes on dynamic data while AMB3R does not.
- **[MapAnything](mapanything.md)**: Concurrent work, compared on Robust-MVD and multi-view reconstruction.
- **[MASt3R](../foundation/mast3r.md)**: The basis of MASt3R-SLAM and MASt3R-SfM, both of which AMB3R outperforms in the uncalibrated setting.
- **[MoGe](moge.md)**: Retains the lead on KITTI and DIODE monocular depth.

## 📚 Key Takeaways

1. **A sparse 3D backend beats more 2D attention**: explicit geometric reasoning in a compact volumetric representation outperforms a matched-capacity alternating-attention variant.
2. **Zero convolution is load-bearing, not incidental**: without it training does not converge, because the front-end's learned confidence is destroyed.
3. **Per-frame scale regression beats global scale regression**: an intrinsic per-frame quantity is far easier to learn than one depending on all frames and their order.
4. **One model, seven tasks, no fine-tuning**: monocular and multi-view depth, metric scale, reconstruction, VO, SLAM, and SfM.
5. **Uncalibrated feed-forward can beat calibrated optimization**: 2.7 cm average on TUM SLAM keyframe poses without loop closure or bundle adjustment.
6. **Cost is the quiet headline**: roughly 50 H100 GPU hours of backend training on 80K samples, less than a single epoch of VGGT's data.

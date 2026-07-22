# FUSER: Feed-Forward Multiview 3D Registration Transformer and SE(3)N Diffusion Refinement (CVPR 2026)

![fuser — architecture](https://arxiv.org/html/2512.09373v3/x2.png)

_Architecture of FUSER (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Haobo Jiang, Jin Xie, Jian Yang, Liang Yu, Jianmin Zheng
- **Institution**: Nanyang Technological University; Alibaba Group; Nanjing University
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2512.09373) | [Code](https://github.com/Jiang-HB/FUSER)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: The first feed-forward multiview point-cloud registration transformer that jointly processes all scans in a compact latent space to directly regress global poses without any pairwise matching, plus FUSER-DF, an SE(3)N diffusion refinement that denoises the predicted poses in the joint SE(3)N space.

## 🎯 Key Contributions

1. **Feed-forward multiview paradigm**: Directly predicts per-scan global poses without redundant pairwise matching or pose-graph synchronization, cutting inference from minutes to the second scale.
2. **Absolute geometric encoding**: A MinkowskiEngine sparse 3D CNN encodes each scan into low-resolution superpoints that preserve absolute translation cues (departing from translation-invariant relative encodings).
3. **Geometric Alternating Attention + 2D-to-3D prior transfer**: L = 32 alternating intra/cross-scan layers, initialized with pretrained weights from π³ (a VGGT variant), transferring 2D attention priors to 3D despite the modality gap.
4. **FUSER-DF (SE(3)N diffusion refinement)**: Reformulates multiview pose correction as denoising on the joint SE(3)N manifold, using FUSER itself as the multiview surrogate registration model with a prior-conditioned variational lower bound.

## 🔧 Technical Details

### FUSER

- **Encoding**: Each scan undergoes hierarchical voxelization and a five-layer sparse convolutional hierarchy (kernel 3, stride 2), yielding compact superpoints with absolute coordinate cues.
- **Attention**: 16 intra-scan + 16 cross-scan alternating blocks, made permutation-equivariant by removing VGGT's learnable reference tokens and replacing 2D RoPE with sinusoidal positional encodings on superpoint coordinates.
- **Pose head**: Self-attention refines superpoint tokens, global average pooling gives a scan descriptor, and two MLP heads regress translation t̂ᵢ and a 9D rotation proxy projected to SO(3) via SVD.
- **Supervision**: Reference-free — geodesic rotation loss + Huber translation loss on relative poses T̂ᵢ←ⱼ, plus a point-wise consistency loss.

### FUSER-DF

Unlike SE(3) diffusion that denoises from the identity, FUSER-DF diffuses from optimal poses toward FUSER's prior predictions T̂₁:N and learns an SE(3)N denoiser that refines from the prior toward the optimum. FUSER serves as the surrogate model estimating residual poses at each step; training uses T = 200 diffusion steps and 10 denoising steps at inference (perturbation weight γ = 0.1). The model has ~0.6B parameters, trained on 3DMatch, ScanNet, ScanNet++, and ArkitScenes.

## 📊 Results

Metrics: rotation/translation recall at thresholds (↑) and Mean/Median rotation (°) and translation (m) error (↓); Registration Recall RR (%↑), RE (°↓), TE (m↓). #Pair = number of pairwise registrations required (FUSER/FUSER-DF use 0).

### Multiview Registration on ScanNet (30 scans)

원논문 Table 1 (임계값 일부와 대표 baseline만 발췌). Recall@threshold는 높을수록, Mean/Med 오차는 낮을수록 좋음.

| Method              | Rot@3°↑  | Rot@5°↑  | Rot@10°↑ | RotMean°↓ | RotMed°↓ | TE@0.05↑ | TE@0.1↑  | TE@0.25↑ | TEMean↓  | TEMed↓   |
| ------------------- | -------- | -------- | -------- | --------- | -------- | -------- | -------- | -------- | -------- | -------- |
| LMVR (Full)         | 48.3     | 53.6     | 58.9     | 48.1      | 33.7     | 34.5     | 49.1     | 58.5     | 0.83     | 0.55     |
| MDGD (Full)         | 54.7     | 71.4     | 83.4     | 17.6      | 19.1     | 38.7     | 62.8     | 77.8     | 0.42     | 0.35     |
| SGHR (Full)         | 57.2     | 68.5     | 75.1     | 26.4      | 19.5     | 39.4     | 61.5     | 72.0     | 0.70     | 0.59     |
| IncreMVR (Sparse)   | 58.6     | 73.4     | 79.7     | 19.8      | 15.6     | 39.6     | 63.9     | 76.3     | 0.55     | 0.37     |
| MDGD (Sparse)       | 56.1     | 71.8     | 83.5     | 17.4      | 19.0     | 38.2     | 61.2     | 77.5     | 0.37     | 0.31     |
| **FUSER (Ours)**    | 69.4     | 86.9     | **94.7** | 6.7       | 2.1      | 36.2     | 71.8     | 92.5     | 0.15     | 0.07     |
| **FUSER-DF (Ours)** | **72.0** | **89.7** | 94.5     | 7.1       | **2.0**  | **43.2** | **75.5** | **92.8** | **0.15** | **0.06** |

FUSER dominates on looser thresholds and mean/median error, but at the strictest translation threshold TE@0.05 plain FUSER (36.2) trails SGHR (39.4), IncreMVR (39.6), and MDGD-Full (38.7); the diffusion refinement FUSER-DF recovers the lead there (43.2).

### 3DMatch (60 scans) and ArkitScenes (200 scans)

원논문 Table 2 (3DMatch) · Table 3 (ArkitScenes).

| Method              | 3DMatch RR↑ | 3DMatch RE°↓ | 3DMatch TE↓ | ArkitScenes RR↑ | ArkitScenes RE°↓ | ArkitScenes TE↓ |
| ------------------- | ----------- | ------------ | ----------- | --------------- | ---------------- | --------------- |
| Full+GeoTrans       | 61.5        | 38.0         | 0.61        | 24.7            | 92.5             | 1.36            |
| Full+PARENet        | 61.9        | 31.2         | 0.68        | 14.3            | 109.2            | 1.44            |
| SGHR+GeoTrans       | 55.2        | 29.8         | 0.69        | 26.7            | 91.2             | 1.48            |
| SGHR+PARENet        | 55.3        | 37.0         | 0.60        | 23.7            | 95.3             | 1.24            |
| **FUSER (Ours)**    | 90.3        | 3.2          | 0.14        | 92.1            | 5.4              | 0.13            |
| **FUSER-DF (Ours)** | **92.0**    | **3.1**      | **0.14**    | **95.0**        | 5.6              | **0.12**        |

### Ablation on ScanNet — 2D Prior & Data Scaling (FUSER)

원논문 Table 4 (FUSER 행 발췌).

| Config                       | Rot@3°↑ | RotMean°↓ | TE@0.05↑ | TEMean↓ |
| ---------------------------- | ------- | --------- | -------- | ------- |
| ScaN, w/o 2D Attention Prior | 12.9    | 34.8      | 5.4      | 0.74    |
| ScaN                         | 36.6    | 22.6      | 15.4     | 0.45    |
| ScaN + ArkitS                | 35.8    | 11.4      | 16.3     | 0.26    |
| ScaN + ArkitS + ScaNP        | 56.9    | 9.4       | 27.5     | 0.20    |
| ScaN + ArkitS + ScaNP + 3DM  | 69.4    | 6.7       | 36.2     | 0.15    |

### Runtime (seconds per sequence)

원논문 Table 5 (대표값) 및 본문. 프리프린트 본문 기준 FUSER-DF 메모리는 200-scan ArkitScenes에서 5.09G, FUSER는 2.83G.

| Setting            | GeoTrans | PARENet | FUSER | FUSER-DF |
| ------------------ | -------- | ------- | ----- | -------- |
| 3DMatch (Full)     | 495.4    | 384.0   | 0.31  | 2.91     |
| 3DMatch (SGHR)     | 180.5    | 155.4   | 0.31  | 2.91     |
| ArkitScenes (Full) | 2454.6   | 1831.3  | 0.61  | 6.50     |
| ArkitScenes (SGHR) | 714.8    | 583     | 0.61  | 6.50     |

## 💡 Insights & Impact

- **Global reasoning beats pairwise-then-sync**: By jointly reasoning over all scans, FUSER avoids error propagation and redundant computation, e.g., reducing 3DMatch mean errors from MDGD's 0.37 m / 17.4° to 0.15 m / 6.7°.
- **2D attention priors transfer to 3D**: Initializing the alternating layers from π³ lifts ScanNet Rot@3° from 12.9 to 36.6 and drops mean rotation error from 34.8° to 22.6° — evidence that view-grouping/alignment priors generalize across the 2D→3D modality gap.
- **Second-scale, memory-light**: FUSER runs in 0.31–0.61 s vs. hundreds-to-thousands of seconds for two-stage pipelines, using only 2.83 GB (FUSER) / 5.09 GB (FUSER-DF) even on 200-scan sequences.
- **Diffusion refinement helps at strict thresholds**: FUSER-DF's main gains are under tight thresholds (e.g., ScanNet Rot@3° 69.4 → 72.0, TE@0.05 36.2 → 43.2), where plain FUSER is relatively weakest.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Source of the alternating-attention architecture that FUSER adapts to 3D scans.
- **[Pi3](../reconstruction/pi3.md)**: The π³ VGGT variant whose pretrained 2D weights are transferred to initialize FUSER's attention layers.
- **[DUSt3R](../foundation/dust3r.md)**: Foundational feed-forward geometry model motivating the shift away from pairwise pipelines.

## 📚 Key Takeaways

1. FUSER is the first feed-forward multiview point-cloud registration transformer, regressing all global poses jointly with no pairwise matching or synchronization.
2. Absolute geometric (superpoint) encoding plus a π³-initialized Geometric Alternating Attention delivers large accuracy gains over two-stage baselines on ScanNet, 3DMatch, and ArkitScenes while running in seconds.
3. FUSER-DF refines the estimates via SE(3)N diffusion, further improving precision at strict thresholds where the feed-forward estimate is weakest (notably tight translation).

# HD-VGGT: High-Resolution Visual Geometry Transformer (arXiv preprint (2026-03))

![hd-vggt — architecture](https://arxiv.org/html/2603.27222v2/x1.png)

_Overview of the HD-VGGT architecture (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Tianrun Chen, Yuanqi Hu, Yidong Han, Hanjie Xu, Deyi Ji, Qi Zhu, Chunan Yu, Xin Zhang, Cheng Chen, Chaotao Ding, Ying Zang, Xuanfu Li, Jin Ma, Lanyun Zhu
- **Institution**: KOKONI 3D, Moxin Technology; Zhejiang University; Huzhou University; University of Science and Technology of China; Nanjing University of Science and Technology; Huawei; Tongji University
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.27222)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A dual-branch extension of VGGT that decouples coarse global geometry (low-resolution branch) from detail refinement (high-resolution branch with a learned feature upsampler), plus a Feature Modulation mechanism that suppresses unstable tokens, achieving high-resolution reconstruction without the quadratic cost of full-resolution transformer attention.

## 🎯 Key Contributions

1. **Dual-branch hierarchical architecture**: A low-resolution branch (standard VGGT backbone) builds a globally consistent coarse geometry, and a high-resolution branch refines detail — avoiding the quadratic complexity explosion of running global self-attention over high-resolution tokens.
2. **Learned feature upsampling module**: A guidance-based upsampler `U` that fuses coarse 3D features with high-resolution image cues (inspired by AnyUp [37]), reversing the low-pass information loss of naive bilinear/nearest interpolation.
3. **Feature Modulation**: A training-free mechanism that detects statistically unstable feature tokens in early transformer layers (repetitive patterns, weak textures, specular surfaces) and attenuates their influence by nullifying the Key vectors of anomalous tokens in shallow layers.
4. **State-of-the-art results** across camera pose estimation, point map reconstruction, and monocular depth estimation on multiple standard benchmarks.

## 🔧 Technical Details

### The VGGT high-resolution bottleneck

Standard VGGT applies global self-attention over `N · K0` tokens from `N` views, with complexity `O((N · K0)² · C)` — quadratic in the total token count. Doubling the input resolution to `2H0 × 2W0` quadruples the per-image token count (`K ≈ 4K0`), so the global-attention complexity explodes by a factor of `4² = 16` (원논문 Section 3.1). This makes full-resolution processing computationally infeasible and motivates the hierarchical design.

### Dual-branch architecture

- **Low-resolution branch** (`T_coarse`): Takes images downsampled to a standard resolution (e.g., 518 × 518 pixels), processed by a standard VGGT backbone (DINOv2 feature extractor + deep transformer) to produce coarse 3D-aware feature maps and initial camera parameters.
- **High-resolution branch**: Operates in two stages —
  1. **Learned Feature Upsampling** (`U`): Extracts high-frequency cues from the guidance image via a shallow conv net `ϕ_guidance`, interpolates + refines coarse features via `ϕ_feat`, then fuses both streams via `ϕ_fuse` to produce the high-resolution feature map `F^hr` (원논문 Eqs. 3–5).
  2. **High-Resolution Refiner** (`T_refine`): A lightweight refiner transformer, significantly shallower than the backbone (e.g., 6 layers vs. 24 layers) using more localized attention, which enforces fine-scale multi-view consistency and regresses the final high-fidelity outputs.

### Feature Modulation for robust inference

The paper frames visually ambiguous regions as "geometric singularities" that behave, statistically, like dynamic events (inspired by VGGT4D [38]). The mechanism has three training-free stages:

1. **Manifold Anomaly Detection via Kernelized Gramian Statistics**: Computes cross-view Gramians of Q and K features in an RKHS, models their sequence over a temporal window as a matrix-valued stochastic process, and fuses multi-scale shallow/middle/deep priors into a posterior anomaly saliency map `S_anomaly` (원논문 Eqs. 7–13).
2. **Manifold Regularization via Projection Gradient Flow**: Refines the initial anomaly map using an aggregated gradient of geometric residual `r_d,i` and photometric residual `r_c,i`, yielding a refined mask `M_refined` (원논문 Eq. 14).
3. **Information-Gated Attentional Suppression**: Applies `M_refined` only to shallow layers by nullifying the Key vectors of anomalous tokens: `K'_p,l = (1 − M_refined,p) · K_p,l` for `l ∈ L_shallow` (원논문 Eq. 15).

### Training

Trained for 2 weeks on a cluster of 16 Ascend 910C within a CloudMatrix384 supernode, adopting a training strategy similar to VGGT (data scheduling, optimizer settings, and loss formulations). No specific loss values are reported in the source.

## 📊 Results

### Camera Pose Estimation — RealEstate10K (static)

원논문 Table 1. 세 지표 모두 높을수록 좋다 (RRA@30↑, RTA@30↑, AUC@30↑).

| Method      | RRA@30 ↑  | RTA@30 ↑  | AUC@30 ↑  |
| ----------- | --------- | --------- | --------- |
| Fast3R      | 99.05     | 81.86     | 61.68     |
| CUT3R       | 99.82     | 95.10     | 81.47     |
| FLARE       | 99.69     | 95.23     | 80.01     |
| VGGT        | 99.97     | 93.13     | 77.62     |
| π³          | 99.99     | 95.62     | 85.90     |
| WorldMirror | 99.99     | 95.81     | 86.28     |
| **HD-VGGT** | **99.99** | **96.15** | **87.01** |

### Camera Pose Estimation — Sintel & TUM-dynamics (dynamic)

원논문 Table 1. 궤적 지표는 모두 낮을수록 좋다 (ATE↓, RPEt↓, RPEr↓).

| Method      | Sintel ATE ↓ | Sintel RPEt ↓ | Sintel RPEr ↓ | TUM ATE ↓ | TUM RPEt ↓ | TUM RPEr ↓ |
| ----------- | ------------ | ------------- | ------------- | --------- | ---------- | ---------- |
| Fast3R      | 0.371        | 0.298         | 13.75         | 0.090     | 0.101      | 1.425      |
| CUT3R       | 0.217        | 0.070         | 0.636         | 0.047     | 0.015      | 0.451      |
| FLARE       | 0.207        | 0.090         | 3.015         | 0.026     | 0.013      | 0.475      |
| VGGT        | 0.167        | 0.062         | 0.491         | 0.012     | 0.010      | 0.312      |
| π³          | 0.074        | 0.040         | 0.282         | 0.014     | 0.009      | 0.312      |
| WorldMirror | 0.096        | 0.058         | 0.490         | 0.010     | 0.009      | 0.297      |
| **HD-VGGT** | **0.071**    | **0.038**     | **0.275**     | **0.009** | **0.008**  | **0.281**  |

### Camera Pose Estimation — CO3Dv2 (object-centric)

원논문 Table 2. Pose AUC는 두 임계값 모두 높을수록 좋다 (↑ @10°, @30°).

| Method      | Pose AUC ↑ (@10) | Pose AUC ↑ (@30) |
| ----------- | ---------------- | ---------------- |
| DUSt3R      | 70.1             | 76.7             |
| MASt3R      | 78.2             | 81.8             |
| VGGT        | 83.3             | 88.2             |
| **HD-VGGT** | **86.5**         | **90.4**         |

### Point Map Reconstruction — 7-Scenes

원논문 Table 3. 모든 값은 cm 단위, 낮을수록 좋다 (Acc.↓, Comp.↓).

| Method      | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ |
| ----------- | ----------- | ----------- | ------------ | ------------ |
| Fast3R      | 9.6         | 6.5         | 14.5         | 9.3          |
| CUT3R       | 9.4         | 5.1         | 10.1         | 5.0          |
| FLARE       | 8.5         | 5.8         | 14.2         | 10.4         |
| VGGT        | 4.6         | 2.6         | 5.7          | 3.4          |
| π³          | 4.8         | 2.8         | 7.2          | 4.7          |
| WorldMirror | 4.3         | 2.6         | 4.9          | 2.8          |
| **HD-VGGT** | **3.9**     | **2.1**     | **4.5**      | **2.5**      |

### Point Map Reconstruction — NRGBD

원논문 Table 3. 모든 값은 cm 단위, 낮을수록 좋다 (Acc.↓, Comp.↓).

| Method      | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ |
| ----------- | ----------- | ----------- | ------------ | ------------ |
| Fast3R      | 13.5        | 9.1         | 16.3         | 10.4         |
| CUT3R       | 10.4        | 4.1         | 7.9          | 3.1          |
| FLARE       | 5.3         | 2.4         | 5.1          | 2.5          |
| VGGT        | 5.1         | 2.9         | 6.6          | 3.8          |
| π³          | 2.6         | 1.5         | 2.8          | 1.4          |
| WorldMirror | 4.1         | 2.0         | 4.5          | 1.9          |
| **HD-VGGT** | **2.4**     | **1.3**     | **2.6**      | **1.2**      |

### Point Map Reconstruction — DTU

원논문 Table 3. 모든 값은 cm 단위, 낮을수록 좋다 (Acc.↓, Comp.↓).

| Method      | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ |
| ----------- | ----------- | ----------- | ------------ | ------------ |
| Fast3R      | 334.0       | 191.9       | 292.9        | 112.5        |
| CUT3R       | 474.2       | 260.0       | 340.0        | 131.6        |
| FLARE       | 254.1       | 146.8       | 317.4        | 142.0        |
| VGGT        | 133.8       | 77.9        | 189.6        | 99.2         |
| π³          | 119.8       | 64.6        | 184.9        | 60.7         |
| WorldMirror | 101.7       | 56.4        | 178.0        | 69.0         |
| **HD-VGGT** | **95.3**    | **51.2**    | **165.4**    | **61.1**     |

### Monocular Depth Estimation — ScanNet & NYUv2

원논문 Table 4. AbsRel은 낮을수록 좋고 (↓), δ1은 높을수록 좋다 (↑).

| Method      | ScanNet AbsRel ↓ | ScanNet δ1 ↑ | NYUv2 AbsRel ↓ | NYUv2 δ1 ↑ |
| ----------- | ---------------- | ------------ | -------------- | ---------- |
| DUSt3R      | 0.081            | 0.909        | 0.143          | 0.814      |
| MASt3R      | 0.110            | 0.865        | 0.115          | 0.848      |
| VGGT        | 0.056            | 0.951        | 0.062          | 0.969      |
| π³          | 0.054            | 0.956        | 0.038          | 0.986      |
| WorldMirror | 0.052            | 0.957        | 0.063          | 0.968      |
| **HD-VGGT** | **0.049**        | **0.961**    | **0.035**      | **0.988**  |

### Monocular Depth Estimation — ScanNet under pose conditions

원논문 Table 5. Abs Rel은 낮을수록 좋다 (↓), GT pose 유무별.

| Method      | Abs Rel ↓ (w/ GT Pose) | Abs Rel ↓ (w/o GT Pose) |
| ----------- | ---------------------- | ----------------------- |
| DUSt3R      | 0.145                  | 0.182                   |
| MASt3R      | 0.131                  | 0.165                   |
| VGGT        | 0.119                  | 0.140                   |
| **HD-VGGT** | **0.102**              | **0.121**               |

### Qualitative results

Figure 2 (monocular depth) and Figure 3 (point maps) show sharper boundaries and better recovery of thin structures (e.g., lamp poles, chair legs) versus VGGT and DA3 — 그림 2·3, 수치 미인쇄.

## 💡 Insights & Impact

- **Decoupling global vs. local reasoning**: The central insight is that a globally consistent coarse geometry can be established cheaply at low resolution, while fine detail can be recovered by a lightweight refiner guided by high-resolution image cues — sidestepping the `4² = 16` complexity blowup that a naive resolution doubling incurs in VGGT's global attention.
- **Feature stability matters at high resolution**: The paper argues that unstable tokens in ambiguous regions become more prominent as resolution increases, and that suppressing them early (Feature Modulation) is necessary — not just architectural efficiency — to scale reconstruction quality. An ablation model HD-VGGT (w/o FM) is defined to isolate this component (원논문 Section 4.1); per-metric ablation values are not printed as a standalone table in the extracted text.
- **Consistent SOTA across tasks**: HD-VGGT improves over the base VGGT and recent methods (π³, WorldMirror) on camera pose, point map reconstruction, and monocular depth simultaneously, including the harder w/o-GT-Pose setting where it reaches AbsRel 0.121 vs. VGGT's 0.140.

## 🔗 Related Work

HD-VGGT positions itself as a high-resolution extension of the VGGT line of feed-forward reconstruction:

- **[VGGT](../reconstruction/vggt.md)**: The core backbone and primary baseline; HD-VGGT reuses its DINOv2 + global-attention transformer as the low-resolution branch and targets its quadratic token-scaling bottleneck.
- **[DUSt3R](dust3r.md)**: The seminal direct point-map regression work cited as the paradigm origin; a baseline in the CO3Dv2 and depth tables.
- **[MASt3R](mast3r.md)**: DUSt3R-paradigm matching model; baseline in the CO3Dv2 and depth tables.
- **[Fast3R](../reconstruction/fast3r.md)**: Cited as an architectural refinement for scalability (1000+ images); baseline across pose and point-map tables.
- **[π³](../reconstruction/pi3.md)**: Permutation-equivariant VGGT variant addressing reference-view bias; a strong baseline across all task tables.
- **[FastVGGT](../reconstruction/fastvggt.md)**: Training-free acceleration of the visual geometry transformer, cited among the surrounding VGGT-acceleration literature.

The paper also compares against CUT3R, FLARE, WorldMirror, DA3, and MonST3R, which do not have dedicated pages in this collection.

## 📚 Key Takeaways

1. **Hierarchical dual-branch design** lets feed-forward reconstruction exploit high-resolution imagery and supervision without scaling the full transformer, avoiding the `4² = 16` global-attention cost of doubling resolution.
2. **A learned, guidance-based feature upsampler** recovers high-frequency detail that naive interpolation (a low-pass filter) discards.
3. **Training-free Feature Modulation** improves robustness by gating out unstable tokens in ambiguous regions at shallow layers.
4. **New SOTA** on RealEstate10K (AUC@30 87.01), CO3Dv2 (Pose AUC@10 86.5), 7-Scenes/NRGBD/DTU point maps, and ScanNet/NYUv2 depth — consistently ahead of the base VGGT.
5. As an arXiv preprint (2026-03), venue and acceptance are unverified — treat as PREPRINT.

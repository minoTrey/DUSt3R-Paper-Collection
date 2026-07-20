# OmniVGGT: Omni-Modality Driven Visual Geometry Grounded Transformer (CVPR 2026)

## 📋 Overview

- **Authors**: Haosong Peng, Hao Li, Yalun Dai, Yushi Lan, Yihang Luo, Tianyu Qi, Zhengshen Zhang, Yufeng Zhan, Junfei Zhang, Wenchao Xu, Ziwei Liu
- **Institution**: HKUST, NTU, SYSU, NUS, Alibaba Group
- **Venue**: CVPR 2026
- **Award**: Highlight
- **Links**: [Paper](https://arxiv.org/abs/2511.10560) | [Project Page](https://livioni.github.io/OmniVGGT-official/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Extends VGGT with a lightweight GeoAdapter and a stochastic multimodal fusion regimen so that an arbitrary number of auxiliary depth maps and camera intrinsics/poses can be injected at train and test time, while keeping RGB-only accuracy at state of the art.

## 🎯 Key Contributions

1. **Arbitrary Auxiliary Modalities**: Unlike Pow3R, which handles at most a pair of auxiliary inputs, OmniVGGT accepts any subset of the input frames carrying depth and/or camera parameters.
2. **GeoAdapter**: A camera adapter using zero-initialized convolutions plus a depth adapter that adds tokens directly to spatial tokens, injecting geometry without destabilizing the foundation model's feature space.
3. **Stochastic Multimodal Fusion**: Modality subsets are randomly sampled per training instance, which enables arbitrary test-time combinations and discourages overfitting to auxiliary cues.
4. **Negligible Overhead**: The GeoAdapter adds only 26.8M parameters; inference stays at ~0.2s, matching vanilla VGGT (원논문 Table 4).
5. **VLA Downstream Transfer**: Spatial tokens injected into a Kosmos-VLA 1.6B model improve robotic manipulation on CALVIN.

## 🔧 Technical Details

### Core Innovation: Injecting Geometry Without Disturbing the Backbone

```text
VGGT:      RGB images → Alternating-Attention → depth / camera / pointmap
Pow3R:     RGB pair + (at most) one auxiliary pair → pointmaps
OmniVGGT:  RGB images + arbitrary subsets of {depth, K, RT} → depth / camera / pointmap
```

Camera parameters are a global attribute while depth is dense and per-pixel, so the two are injected by different mechanisms. Directly injecting encoded camera information destabilizes the large-scale backbone, which motivates the zero-convolution path.

### Camera Adapter

- Coordinate origin aligned with the first camera; poses normalized by the mean distance of remaining cameras to the origin.
- Intrinsics and normalized poses parameterized as `g = {q, t, f}` (rotation quaternion, translation, field of view).
- A dedicated camera encoder before each of the L Alternating-Attention blocks produces auxiliary camera tokens.
- Missing entries are replaced by a learned camera placeholder token.
- Tokens pass through a zero-conv layer before being added to the camera tokens, so training starts exactly at the pretrained VGGT behaviour.

### Depth Adapter

- Depth maps normalized per batch over valid pixels; depth and validity mask concatenated as a 2-channel input.
- A single convolutional encoder with kernel size 14 patchifies the input to the spatial token dimension.
- Auxiliary depth tokens (or a depth placeholder token) are added **directly** to the spatial tokens — an extra zero-conv on the depth branch was found to be redundant and actively harmful (ablation variant (c)).

### Training

- Backbone follows VGGT with L = 24 AA blocks.
- Camera GeoAdapter uses (L + 1) independent single-linear-layer encoders; depth GeoAdapter uses one convolutional encoder.
- Loss: `L = L_camera + L_depth + L_pmap`, with ℓ1 camera regression and confidence-aware regression plus gradient terms for depth and pointmaps.
- Stochastic assignment: sample Q ∈ [0, S] frames to receive GT cameras (assigned to the first Q frames) and independently O ∈ [0, S] frames to receive GT depth (random indices). A fraction of batches is RGB-only.
- 19 public datasets (ARKitScenes, BlendedMVS, DL3DV, Dynamic Replica, HyperSim, Kubric, MapFree, MegaDepth, Matterport3D, MVS-Synth, ScanNet, ScanNet++, Spring, TartanAir, UASOL, Unreal 4K, Virtual KITTI, Waymo, WildRGBD).
- 32 NVIDIA A100 GPUs for ten days, with gradient checkpointing.

## 📊 Results

### Single-frame Depth Evaluation

원논문 Table 2. `w/ D` means 100% of depth maps are provided. Sintel, Bonn, NYU-v2 are all zero-shot.

| Method            | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | NYU-v2 Abs Rel ↓ | NYU-v2 δ<1.25 ↑ |
| ----------------- | ---------------- | --------------- | -------------- | ------------- | ---------------- | --------------- |
| VGGT              | 0.271            | 67.7            | 0.053          | 97.3          | 0.060            | 94.8            |
| Fast3R            | 0.502            | 52.8            | 0.192          | 77.3          | 0.099            | 88.9            |
| DUSt3R            | 0.424            | 58.7            | 0.141          | 82.5          | 0.080            | 90.7            |
| MASt3R            | 0.340            | 60.4            | 0.142          | 82.0          | 0.129            | 84.9            |
| MonST3R           | 0.358            | 54.8            | 0.076          | 93.9          | 0.102            | 88.0            |
| Spann3R           | 0.470            | 53.9            | 0.118          | 85.9          | 0.122            | 84.9            |
| CUT3R             | 0.428            | 55.4            | 0.063          | 96.2          | 0.086            | 90.9            |
| Pow3R             | 0.464            | 54.8            | 0.132          | 84.2          | 0.094            | 89.6            |
| Pow3R w/ D        | 0.150            | 87.4            | 0.009          | 99.7          | 0.009            | 99.8            |
| OmniVGGT          | 0.250            | 68.2            | 0.064          | 95.5          | 0.058            | 95.8            |
| **OmniVGGT w/ D** | **0.107**        | **90.2**        | **0.008**      | **99.9**      | **0.008**        | **99.9**        |

RGB-only OmniVGGT wins on Sintel and NYU-v2 but **loses to VGGT on Bonn** (0.064 vs 0.053 Abs Rel, 95.5 vs 97.3 δ<1.25).

### Multi-view Depth Evaluation

원논문 Table 3. Metrics are Absolute Relative error (rel ↓) and inlier ratio τ ↑. Parentheses denote
in-domain training data. "K", "RT", "D" denote intrinsics, relative pose, depth.

| Method                   | ScanNet rel ↓ | ScanNet τ ↑ | ETH3D rel ↓ | ETH3D τ ↑ | DTU rel ↓ | DTU τ ↑ | T&T rel ↓ | T&T τ ↑  |
| ------------------------ | ------------- | ----------- | ----------- | --------- | --------- | ------- | --------- | -------- |
| DUSt3R                   | (3.1)         | (71.8)      | 3.0         | 76.0      | 3.9       | 68.6    | 3.3       | 75.1     |
| Pow3R                    | (3.2)         | (68.8)      | 3.0         | 74.7      | 3.0       | 74.3    | 3.3       | 76.6     |
| VGGT                     | (3.7)         | (70.0)      | 1.7         | 87.2      | 0.9       | 95.4    | 1.7       | 90.6     |
| OmniVGGT                 | (3.6)         | (72.3)      | 1.8         | 87.5      | 1.1       | 93.9    | 1.8       | 90.0     |
| Pow3R w/ (K+RT)          | (3.1)         | (71.4)      | 2.8         | 77.1      | 1.5       | 91.1    | 3.2       | 78.2     |
| OmniVGGT w/ (K+RT)       | (3.7)         | (72.2)      | 1.8         | 87.8      | 1.2       | 93.6    | 1.8       | 89.9     |
| OmniVGGT w/ D            | (2.3)         | (85.6)      | 0.5         | 98.7      | 0.3       | 99.5    | 0.9       | 95.5     |
| **OmniVGGT w/ (K+RT+D)** | **(2.2)**     | **(86.7)**  | **0.5**     | **98.7**  | **0.3**   | 99.4    | **0.9**   | **95.6** |

Honest reading: in the RGB-only setting OmniVGGT is **behind VGGT** on ETH3D rel (1.8 vs 1.7),
DTU (1.1 vs 0.9), T&T (1.8 vs 1.7) and T&T τ (90.0 vs 90.6). Its RGB-only edge is on ScanNet τ and
ETH3D τ. The large gains come only once depth is supplied.

Average across the four datasets (원논문 Table 3):

| Method                   | Average rel ↓ | Average τ ↑ |
| ------------------------ | ------------- | ----------- |
| DUSt3R                   | 3.3           | 72.9        |
| Pow3R                    | 3.1           | 73.6        |
| VGGT                     | 2.0           | 85.8        |
| OmniVGGT                 | 2.1           | 85.9        |
| Pow3R w/ (K+RT)          | 2.7           | 79.5        |
| OmniVGGT w/ (K+RT)       | 2.1           | 85.9        |
| OmniVGGT w/ D            | 1.0           | 94.8        |
| **OmniVGGT w/ (K+RT+D)** | **1.0**       | **95.1**    |

### Camera Pose Estimation

원논문 Table 4. AUC@30° (%) ↑ on 10 randomly sampled images per scene. `()` means not trained on CO3D.

| Method               | Re10K unseen ↑ | CO3Dv2 ↑ | Time  |
| -------------------- | -------------- | -------- | ----- |
| COLMAP+SPSG          | 45.2           | 25.3     | ~15s  |
| PixSfM               | 49.4           | 30.1     | >20s  |
| PoseDiff             | 48.0           | 66.5     | ~7s   |
| DUSt3R               | 67.7           | 76.7     | ~7s   |
| MASt3R               | 76.4           | 81.8     | ~9s   |
| VGGSfM v2            | 78.9           | 83.4     | ~10s  |
| MV-DUSt3R            | 71.3           | (69.5)   | ~0.6s |
| CUT3R                | 75.3           | 82.8     | ~0.6s |
| FLARE                | 78.8           | 83.3     | ~0.5s |
| Fast3R               | 72.7           | 82.5     | ~0.2s |
| VGGT                 | 85.3           | 88.2     | ~0.2s |
| Pow3R (Pro)          | 62.5           | 78.5     | >7s   |
| OmniVGGT             | 85.9           | 88.4     | ~0.2s |
| **OmniVGGT w/ K+RT** | **88.5**       | **93.4** | ~0.2s |

The paper states OmniVGGT "operates approximately 30× faster than Pow3R" and that it outperforms
Pow3R "by up to 16% on Re10K" when auxiliary inputs are available.

### 3D Reconstruction on 7-Scenes

원논문 Table 5. Each scene has 3–5 sparsely captured frames with minimal or no overlap.

| Method                   | Acc↓ Mean | Acc↓ Med. | Comp↓ Mean | Comp↓ Med. | NC↑ Mean  | NC↑ Med.  |
| ------------------------ | --------- | --------- | ---------- | ---------- | --------- | --------- |
| VGGT                     | 0.087     | 0.039     | 0.091      | 0.039      | 0.787     | 0.890     |
| Fast3R                   | 0.164     | 0.108     | 0.163      | 0.080      | 0.686     | 0.775     |
| DUSt3R-GA                | 0.146     | 0.077     | 0.181      | 0.067      | 0.736     | 0.839     |
| MASt3R-GA                | 0.185     | 0.081     | 0.180      | 0.069      | 0.701     | 0.792     |
| MonST3R-GA               | 0.248     | 0.185     | 0.266      | 0.167      | 0.672     | 0.759     |
| Spann3R                  | 0.298     | 0.226     | 0.205      | 0.112      | 0.650     | 0.730     |
| SLAM3R                   | 0.287     | 0.155     | 0.226      | 0.066      | 0.644     | 0.720     |
| CUT3R                    | 0.126     | 0.047     | 0.154      | 0.031      | 0.727     | 0.834     |
| OmniVGGT                 | 0.104     | 0.037     | 0.112      | 0.031      | 0.763     | 0.875     |
| OmniVGGT w/ D            | 0.085     | 0.034     | 0.085      | 0.027      | 0.789     | 0.894     |
| OmniVGGT w/ (K+RT)       | 0.037     | 0.017     | 0.049      | 0.019      | 0.778     | 0.893     |
| **OmniVGGT w/ (K+RT+D)** | **0.036** | **0.017** | **0.036**  | **0.017**  | **0.810** | **0.912** |

RGB-only OmniVGGT is **worse than VGGT on Acc mean (0.104 vs 0.087)**, Comp mean and NC. The paper
attributes the 65.4% gain from adding camera parameters (0.104 → 0.036) to the extreme sparsity of
7-Scenes, which makes from-scratch pose estimation the bottleneck.

### Auxiliary Information Ratio (zero-shot Sintel)

원논문 Table 1. Injecting a growing fraction of GT depth or camera information.

| Setting                  | Abs Rel ↓ | δ<1.25 ↑  | RRA@5° ↑  | RTA@5° ↑  | AUC@30° ↑ |
| ------------------------ | --------- | --------- | --------- | --------- | --------- |
| VGGT (no aux.)           | 0.722     | 70.81     | 95.69     | 53.92     | 70.55     |
| OmniVGGT (no aux.)       | 0.558     | 71.46     | 96.15     | 54.01     | 70.83     |
| OmniVGGT + 30% depth     | 0.169     | 78.92     | 96.65     | 54.15     | 71.43     |
| OmniVGGT + 100% depth    | 0.106     | 85.95     | 96.93     | 59.73     | 77.16     |
| OmniVGGT + 30% camera    | 0.555     | 72.45     | 98.56     | 61.44     | 75.87     |
| OmniVGGT + 100% camera   | 0.553     | 72.36     | 99.97     | 75.83     | 85.35     |
| **OmniVGGT + 100% both** | **0.106** | **85.95** | **99.97** | **76.33** | **85.99** |

The paper notes that 30% depth alone reduces Abs Rel error by 69.71%, and that 100% depth improves
pose AUC@30° by 6.33 — evidence that auxiliary cues improve the spatial representation rather than
being copied to the output.

### GeoAdapter Ablation

원논문 Table 7, on Sintel. (d) is the adopted design.

| Architecture          | Aux.   | Abs Rel ↓ | δ<1.25 ↑  | RRA@5° ↑  | RTA@5° ↑  | AUC@30° ↑ |
| --------------------- | ------ | --------- | --------- | --------- | --------- | --------- |
| (a) Replace           | none   | 0.845     | 64.74     | 93.40     | 30.88     | 64.74     |
| (b) One-Layer Adapter | none   | 0.604     | 68.74     | 96.78     | 44.92     | 68.74     |
| (c) Depth ZeroConv    | none   | 0.569     | 70.71     | 96.44     | 51.86     | 69.70     |
| **(d) OmniVGGT**      | none   | **0.558** | **71.46** | 96.15     | **54.01** | **70.83** |
| (a) Replace           | K+RT+D | 0.655     | 82.96     | 97.08     | 57.61     | 77.83     |
| (b) One-Layer Adapter | K+RT+D | 0.133     | 85.65     | 99.97     | 60.89     | 81.66     |
| (c) Depth ZeroConv    | K+RT+D | 0.505     | 71.11     | 99.72     | 71.66     | 84.12     |
| **(d) OmniVGGT**      | K+RT+D | **0.106** | **85.95** | **99.97** | **76.33** | **85.99** |

Note that variant (b) reaches a slightly higher RRA@5° than (d) in the RGB-only block (96.78 vs 96.15).

### VLA Application on CALVIN

원논문 Table 6. Kosmos-VLA (w/ rgb-d) is a point-cloud version with a lightweight point encoder.

| Method                | Task   | 1    | 2    | 3    | 4    | 5    | Avg. Len. ↑ |
| --------------------- | ------ | ---- | ---- | ---- | ---- | ---- | ----------- |
| Kosmos-VLA (w/ rgb)   | ABCD→D | 92.9 | 85.4 | 79.4 | 74.4 | 68.1 | 4.00        |
| Kosmos-VLA (w/ rgb-d) | ABCD→D | 93.4 | 85.8 | 80.5 | 75.3 | 69.2 | 4.04        |
| Ours (w/ rgb)         | ABCD→D | 93.8 | 86.6 | 81.0 | 75.5 | 69.5 | 4.07        |
| **Ours (w/ rgb-d)**   | ABCD→D | 93.7 | 86.8 | 81.4 | 76.7 | 70.2 | **4.08**    |
| Kosmos-VLA (w/ rgb)   | ABC→D  | 90.1 | 79.1 | 69.2 | 59.6 | 50.9 | 3.49        |
| Kosmos-VLA (w/ rgb-d) | ABC→D  | 93.6 | 86.0 | 78.6 | 72.9 | 64.8 | **3.97**    |
| Ours (w/ rgb)         | ABC→D  | 93.8 | 86.9 | 77.9 | 70.3 | 62.2 | 3.92        |
| Ours (w/ rgb-d)       | ABC→D  | 95.1 | 87.7 | 79.2 | 70.8 | 63.0 | 3.96        |

Honest reading: on the zero-shot ABC→D split, **Kosmos-VLA (w/ rgb-d) still has the best Avg. Len.
(3.97)**; the OmniVGGT variants reach 3.92 and 3.96. The paper's claimed 0.43 gain is against the
RGB-only Kosmos baseline (3.49).

## 💡 Insights & Impact

### Why zero-conv on cameras but not on depth

The paper's central empirical finding is asymmetry. Camera parameters are a _global_ attribute whose
encoded tokens have statistics unrelated to the pretrained camera tokens — injecting them directly
destabilizes early training, so a zero-initialized convolution is needed to fade them in. Depth, in
contrast, is _dense and pixel-aligned_, structurally compatible with the spatial tokens; the ablation
shows that a zero-conv there makes the model treat depth as noise (variant (c) improves camera
metrics but barely improves depth: 0.505 Abs Rel vs 0.106 for the full design).

### Stochastic training is what buys flexibility

Sampling modality subsets per instance is what allows arbitrary test-time combinations. Importantly,
the paper argues this also prevents the network from learning a shortcut mapping from auxiliary input
to output: pose accuracy improves when only _depth_ is supplied, which is only possible if depth is
being fused into the shared representation.

### Where the gains actually are

The RGB-only results are essentially at VGGT parity — sometimes slightly better, sometimes slightly
worse. The distinctive value of OmniVGGT is that it degrades gracefully to VGGT when nothing extra is
available and improves substantially when something is. The most dramatic case is sparse,
low-overlap capture (7-Scenes) where cameras remove the dominant failure mode.

## 🔗 Related Work

- [VGGT](vggt.md) — the backbone this work adapts; OmniVGGT keeps its Alternating-Attention design, L = 24 blocks, DPT heads, and camera head.
- [Pow3R](pow3r.md) — the prior work on conditioning reconstruction on camera and scene priors, and the main baseline; limited to pairs and much slower.
- [π³](pi3.md) — a contemporaneous RGB-only spatial foundation model in the same lineage.
- [Fast3R](fast3r.md), [CUT3R](../dynamic/cut3r.md), [Spann3R](spann3r.md), [SLAM3R](slam3r.md) — multi-view / streaming baselines compared on 7-Scenes and depth.
- [MonST3R](../dynamic/monst3r.md) — dynamic-scene baseline included in the 7-Scenes and single-frame depth tables.

## 📚 Key Takeaways

1. **Auxiliary geometry is free performance when it exists.** Depth injection cuts multi-view depth error roughly in half on average (2.1 → 1.0 rel) and pushes ETH3D/DTU τ above 98.
2. **The injection mechanism must match the modality's structure.** Zero-conv helps global camera tokens and hurts dense depth tokens — the paper's ablation isolates this cleanly.
3. **RGB-only parity, not RGB-only supremacy.** OmniVGGT trades small losses against VGGT on ETH3D/DTU/T&T rel and 7-Scenes Acc for small wins elsewhere; the headline claim rests on the auxiliary-input settings.
4. **Sparse, low-overlap capture is the killer application.** On 7-Scenes, supplying intrinsics and poses improves Acc mean from 0.104 to 0.036.
5. **Cheap to add.** 26.8M extra parameters and ~0.2s inference, unchanged from VGGT.

# WinT3R: Window-based Streaming Reconstruction with Camera Token Pool (arXiv preprint)

## 📋 Overview

- **Authors**: Zizun Li, Jianjun Zhou, Yifan Wang, Haoyu Guo, Wenzheng Chang, Yang Zhou, Haoyi Zhu, Junyi Chen, Chunhua Shen, Tong He
- **Institution**: University of Science and Technology of China, Shanghai AI Lab, SII, Zhejiang University
- **Venue**: arXiv preprint (2025-09)
- **Note**: The venue could not be confirmed from any primary source (no acceptance statement appears in the PDF, and no external record was available). This should be re-checked before the entry is relied upon.
- **Links**: [Paper](https://arxiv.org/abs/2509.05296) | [Code](https://github.com/LiZizun/WinT3R)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: An online feed-forward reconstruction model that processes an image stream in half-overlapping sliding windows and keeps a growing pool of compact per-frame camera tokens as lightweight global memory, running at 17.2 FPS.

## 🎯 Key Contributions

1. **Online sliding-window mechanism**: image tokens interact directly with other image tokens in the same window and, through a stride of `w/2`, across adjacent windows — not only indirectly through state tokens as in CUT3R.
2. **Camera token pool**: one 1536-dimensional camera token per frame is stored in an expandable pool and attended over when predicting the pose of each new frame, acting as a "global memory" that is far cheaper than caching per-layer keys and values.
3. **Speed**: the paper reports the fastest reconstruction speed among the online methods it evaluates, at 17.2 FPS on KITTI on a single NVIDIA A800.

## 🔧 Technical Details

### Pipeline

Each incoming image is encoded frame-wise by a ViT encoder into image tokens. A learnable camera token is prepended to each frame's tokens, and all tokens in the current window are fed jointly to a dual-branch decoder:

- One branch performs Alternating-Attention (as in VGGT) over image and camera tokens, producing both global and local enriched tokens.
- The other branch carries the scene state tokens `S`, which are read from and updated by the window's tokens. State tokens are initialised as a set of learnable tokens.

### Window configuration

Window size 4, stride 2, so neighbouring windows share half their frames. Predictions in the overlapping region are resolved by taking the camera pose from the updated prediction and the point map with the higher confidence. At inference the window waits until full; the last image is duplicated to fill remaining slots.

### Heads

- **Point map head**: a lightweight convolutional head applied to the _local_ image tokens, predicting a per-frame point map in its own camera coordinate system plus a confidence map. The authors deliberately avoid the expensive DPT head and the linear head, which they report introduces grid-like artifacts.
- **Camera head**: the local and global camera tokens are concatenated along the channel dimension into a single token per frame, appended to the pool, and decoded with sliding-window masked attention so that a frame conditions on all previous windows but not on future ones. Output is a 7-dimensional vector (rotation quaternion + translation).

### Training objective

`L_total = L_camera + L_pmap`. Predictions and ground truth are normalised by a confidence-weighted average point-map scale. The point map loss is a confidence-aware ℓ2 regression term with a `−α log C` penalty. Following π³, the camera loss supervises _relative_ pairwise poses with an ℓ1 loss instead of absolute poses, so no coordinate frame has to be fixed by hand. The authors note both terms were found equally critical and are simply summed.

### Training setup

750M parameters, initialised from DUSt3R weights, AdamW. Stage 1: 12-frame data, 100 epochs, max LR 1e-4, batch size 4 per GPU, 64 NVIDIA A800 GPUs, 7 days. Stage 2: 60-frame fine-tuning, 12 epochs, max LR 2e-6, 32 A800 GPUs, 4 days. Longest image edge fixed at 512 px.

## 📊 Results

### 3D reconstruction (DTU, ETH3D)

원논문 Table 1. Metrics are Accuracy / Completeness / Overall (Chamfer distance), all lower-is-better.

| Method     | DTU Acc↓  | DTU Comp↓ | DTU Overall↓ | ETH3D Acc↓ | ETH3D Comp↓ | ETH3D Overall↓ |
| ---------- | --------- | --------- | ------------ | ---------- | ----------- | -------------- |
| Spann3R    | 6.021     | 3.554     | 4.788        | 0.733      | 1.546       | 1.139          |
| SLAM3R     | 6.672     | 5.256     | 5.964        | 0.626      | 0.888       | 0.757          |
| CUT3R      | 4.454     | 1.944     | 3.199        | 0.533      | 0.503       | 0.518          |
| Point3R    | 4.887     | 1.688     | 3.288        | 0.662      | 0.579       | 0.621          |
| StreamVGGT | 3.997     | **1.651** | 2.823        | 0.581      | 0.359       | 0.470          |
| **WinT3R** | **3.638** | 1.838     | **2.738**    | **0.411**  | **0.272**   | **0.341**      |

Note that on DTU, StreamVGGT retains the better Completeness; WinT3R wins on Accuracy and Overall.

### 3D reconstruction (7-Scenes, NRGBD)

원논문 Table 2.

| Method     | 7-Sc Acc↓ | 7-Sc Comp↓ | 7-Sc Overall↓ | NRGBD Acc↓ | NRGBD Comp↓ | NRGBD Overall↓ |
| ---------- | --------- | ---------- | ------------- | ---------- | ----------- | -------------- |
| Spann3R    | 0.054     | 0.044      | 0.049         | 0.134      | 0.078       | 0.106          |
| SLAM3R     | 0.069     | 0.060      | 0.064         | 0.130      | 0.082       | 0.106          |
| CUT3R      | **0.023** | 0.027      | 0.025         | 0.086      | 0.048       | 0.067          |
| Point3R    | 0.034     | 0.026      | 0.030         | 0.066      | 0.032       | 0.049          |
| StreamVGGT | 0.047     | 0.030      | 0.038         | 0.096      | 0.049       | 0.074          |
| **WinT3R** | **0.023** | **0.022**  | **0.022**     | **0.032**  | **0.020**   | **0.026**      |

### Camera pose estimation

원논문 Table 3. Higher is better for all three metrics. Tanks and Temples uses 30 frames per scene at stride 10; CO3Dv2 uses 10 randomly sampled frames; 7-Scenes uses stride 40.

| Method     | T&T RRA@30↑ | T&T RTA@30↑ | T&T AUC@30↑ | CO3Dv2 RRA@30↑ | CO3Dv2 RTA@30↑ | CO3Dv2 AUC@30↑ |
| ---------- | ----------- | ----------- | ----------- | -------------- | -------------- | -------------- |
| Spann3R    | 65.52       | 68.54       | 40.78       | 93.81          | 89.95          | 70.41          |
| CUT3R      | 92.35       | 91.86       | 76.22       | 96.33          | 92.67          | 75.94          |
| Point3R    | 74.64       | 79.27       | 42.63       | 95.51          | 91.21          | 67.99          |
| StreamVGGT | 93.23       | 92.81       | 74.98       | 98.61          | **95.60**      | **84.68**      |
| **WinT3R** | **94.53**   | **94.35**   | **81.34**   | **98.66**      | **95.60**      | 84.61          |

On CO3Dv2 the AUC@30 is essentially tied with StreamVGGT and marginally lower (84.61 vs 84.68).

원논문 Table 3, 7-Scenes column.

| Method     | 7-Scenes RRA@30↑ | 7-Scenes RTA@30↑ | 7-Scenes AUC@30↑ |
| ---------- | ---------------- | ---------------- | ---------------- |
| Spann3R    | 99.98            | 95.10            | 72.60            |
| CUT3R      | **100.0**        | 95.36            | 74.49            |
| Point3R    | **100.0**        | 94.13            | 66.81            |
| StreamVGGT | 99.98            | 95.78            | 75.50            |
| **WinT3R** | **100.0**        | **97.40**        | **78.59**        |

### Video depth estimation and speed

원논문 Table 4. Per-sequence scale alignment. FPS measured on KITTI on a single NVIDIA A800.

| Method     | Sintel Abs Rel↓ | Sintel δ<1.25↑ | BONN Abs Rel↓ | BONN δ<1.25↑ | KITTI Abs Rel↓ | KITTI δ<1.25↑ | FPS↑     |
| ---------- | --------------- | -------------- | ------------- | ------------ | -------------- | ------------- | -------- |
| Spann3R    | 0.597           | 0.384          | 0.072         | 0.953        | 0.251          | 0.566         | 10.4     |
| CUT3R      | 0.417           | 0.507          | 0.078         | 0.937        | 0.122          | 0.876         | 12.9     |
| Point3R    | 0.461           | 0.455          | 0.060         | 0.962        | 0.137          | 0.839         | 3.6      |
| StreamVGGT | **0.343**       | **0.604**      | **0.057**     | **0.974**    | 0.185          | 0.700         | 13.7     |
| **WinT3R** | 0.374           | 0.506          | 0.070         | 0.912        | **0.081**      | **0.949**     | **17.2** |

Depth is where WinT3R is weakest: it loses to StreamVGGT on Sintel and to several baselines on BONN, while winning decisively on KITTI. The paper describes the result as "comparable or better" rather than uniformly better.

### Ablations

원논문 Table 5. All ablation models are trained from scratch at 224×224 with no pretrained weights, so the numbers are not comparable to the main tables.

| Method      | 7-Sc Acc↓ | 7-Sc Comp↓ | 7-Sc Overall↓ | NRGBD Acc↓ | NRGBD Comp↓ | NRGBD Overall↓ |
| ----------- | --------- | ---------- | ------------- | ---------- | ----------- | -------------- |
| w/o pool    | 0.126     | 0.200      | 0.163         | 0.220      | 0.480       | 0.350          |
| w/o window  | 0.123     | 0.300      | 0.212         | 0.253      | 0.556       | 0.404          |
| w/o overlap | 0.126     | 0.265      | 0.195         | 0.220      | 0.349       | 0.285          |
| Full model  | **0.118** | **0.205**  | **0.161**     | **0.217**  | **0.298**   | **0.258**      |

원논문 Table 6. The camera token pool matters far more for pose than for geometry.

| Method      | T&T AUC@30↑ | CO3Dv2 AUC@30↑ | 7-Scenes AUC@30↑ |
| ----------- | ----------- | -------------- | ---------------- |
| w/o pool    | 8.87        | 38.10          | 11.54            |
| w/o window  | 12.05       | 37.83          | 7.39             |
| w/o overlap | 11.83       | 44.31          | 11.54            |
| Full model  | **15.73**   | **47.17**      | **15.01**        |

## 💡 Insights & Impact

### Splitting local geometry from global pose

The central design decision is an asymmetry in what each output needs. A per-frame local point map is argued to depend mainly on local cues, so it is decoded from window-local tokens with a cheap convolutional head. A camera pose, by contrast, positions the frame within the whole scene, so it is decoded conditioned on every historical frame. Because a camera token is a single 1536-d vector while an image contributes hundreds of tokens, attending over all history is affordable for pose but would not be for geometry. The ablation supports this split: removing the pool costs 6.86 AUC@30 on Tanks and Temples but only 0.002 Overall on 7-Scenes.

### Windows as a middle ground

Fully offline methods (VGGT, π³, FLARE) attend across all frames and cannot incrementally absorb new ones; purely recurrent online methods (CUT3R, Spann3R) let adjacent frames communicate only through a bottlenecked state. The half-overlapping window is a compromise: direct token-to-token attention within a small neighbourhood, plus state tokens for longer-range context. The `w/o window` ablation — feeding images one at a time — is the worst configuration for reconstruction Overall on both datasets.

### Where it does not win

The paper is honest that video depth is mixed. On Sintel and BONN, StreamVGGT remains ahead. The DTU Completeness column also goes to StreamVGGT. The claim the results actually support is state-of-the-art _online_ reconstruction and pose, with the fastest throughput, rather than dominance on every metric.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md) — the recurrent state-token design WinT3R builds on and repeatedly ablates against.
- [Spann3R](./spann3r.md) — earlier memory-based online reconstruction baseline.
- [StreamVGGT](./streamvggt.md) — the strongest online baseline here; wins Sintel/BONN depth and DTU Completeness.
- [Point3R](./point3r.md) — explicit spatial-pointer memory, compared throughout.
- [VGGT](./vggt.md) — source of the Alternating-Attention block used in the decoder's image-token branch.
- [pi3](./pi3.md) — source of the relative-pose supervision strategy.
- [DUSt3R](../foundation/dust3r.md) — WinT3R is initialised from DUSt3R weights.
- [SLAM3R](./slam3r.md) — online SLAM-style baseline in the reconstruction tables.

## 📚 Key Takeaways

1. **Compact tokens buy global context cheaply.** Pooling one 1536-d camera token per frame gives every new frame a global view for pose estimation at a fraction of the cost of caching per-layer KV.
2. **Half-overlapping windows beat frame-by-frame streaming.** Direct cross-frame token attention within a window, plus stride-`w/2` overlap for continuity, is the single largest contributor to reconstruction quality in the ablation.
3. **17.2 FPS is the headline efficiency number**, measured on KITTI on one A800 — the highest among the online methods compared.
4. **The wins are task-dependent.** Reconstruction and pose are consistently strong; video depth is only competitive, losing to StreamVGGT on two of three datasets.
5. **The venue is unconfirmed** — treat the publication status of this entry as open.

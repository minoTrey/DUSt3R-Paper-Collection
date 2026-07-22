# Human3R: Everyone Everywhere All at Once (ICLR 2026)

![human3r — pipeline](https://fanegg.github.io/Human3R/static/images/fig_pipe.png)

_전체 파이프라인 (저자 project page)_

## 📋 Overview

- **Authors**: Yue Chen, Xingyu Chen, Yuxuan Xue, Anpei Chen, Yuliang Xiu, Gerard Pons-Moll
- **Institution**: Zhejiang University, Westlake University, University of Tübingen (Tübingen AI Center), Max Planck Institute for Informatics
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.06219) | [Code](https://github.com/fanegg/Human3R) | [Project Page](https://fanegg.github.io/Human3R)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Fine-tunes CUT3R with visual prompt tuning so that a single online feed-forward pass jointly recovers global multi-person SMPL-X bodies, dense scene geometry, and camera trajectories — trained in one day on one GPU.

## 🎯 Key Contributions

1. **One Model**: A unified network reasons jointly about humans, scene, and camera instead of chaining separate off-the-shelf detectors, depth estimators, and SLAM systems.
2. **One Stage**: Streaming online inference at 15 FPS on an RTX 4090 with an 8 GB memory footprint, replacing multi-stage pipelines with iterative contact-aware refinement that take hours.
3. **One Shot**: A bottom-up multi-person SMPL-X regressor reconstructs all people in a single forward pass, so cost does not scale with crowd size.
4. **One GPU, One Day**: Parameter-efficient visual prompt tuning on the relatively small synthetic BEDLAM dataset (6k sequences), on a single 48 GB GPU.
5. **Human Prompts from Head Tokens**: Instead of random learnable prompt tokens, head tokens detected from CUT3R's image features are complemented with human prior tokens and projected through a learnable MLP.

## 🔧 Technical Details

### Core Innovation: Prompting a Frozen 4D Backbone

```text
Prior work: detect → track → crop → per-person HMR → depth → SLAM → contact refinement (hours)
Human3R:    RGB stream → CUT3R (frozen) + human prompts → {SMPL-X bodies, scene points, camera}
```

CUT3R is a recurrent 4D reconstruction foundation model that maintains a persistent internal state
encoding "everywhere and everyone", incrementally updated with each new observation. Human3R keeps
the entire CUT3R backbone **frozen** and fine-tunes via visual prompt tuning (VPT), prepending a
minimal set of learnable parameters into the input space. This is what preserves CUT3R's
spatiotemporal priors while enabling direct readout of multiple SMPL-X bodies.

### Human Prompts

- The head is the most discriminative keypoint on the human body, so head tokens are detected from CUT3R's image features.
- These are complemented with human prior tokens from a Multi-HMR ViT DINO encoder fine-tuned on human-specific datasets.
- A learnable MLP projects them into human prompts, which act as SMPL-X queries anchoring full-body reconstruction.
- Prompts **self-attend to image tokens** for whole-body spatial aggregation and **cross-attend to the persistent internal state**, which makes the 3D human estimates scene-aware.

### Architecture and Training

- Streamlined architecture: Encoder, Multi-HMR encoder, Decoder, and Heads only.
- Training data: BEDLAM — 6k sequences with 3D scene depth, camera poses, and world-coordinate SMPL-X meshes for multiple persons.
- TTT3R, a training-free closed-form state transition rule, is integrated to mitigate CUT3R's catastrophic forgetting on long sequences.
- Backbone variants: ViT-S/672, ViT-B/672, ViT-L/672, ViT-L/896 for the Multi-HMR encoder, trading speed against accuracy.

## 📊 Results

### Local Human Mesh Reconstruction

원논문 Table 1. Camera-coordinate metrics in millimeters. "Crop-free / Detection-free /
Intrinsic-free" indicate what the method does **not** require.

| Category    | Method      | Crop-free | Detect-free | Intr-free | 3DPW PA-MPJPE ↓ | 3DPW MPJPE ↓ | 3DPW PVE ↓ | EMDB-1 PA-MPJPE ↓ | EMDB-1 MPJPE ↓ | EMDB-1 PVE ↓ |
| ----------- | ----------- | --------- | ----------- | --------- | --------------- | ------------ | ---------- | ----------------- | -------------- | ------------ |
| Multi-stage | CLIFF       | ✗         | ✗           | ✗         | 43.0            | 69.0         | 81.2       | 68.3              | 103.3          | 123.7        |
| Multi-stage | HMR2.0a     | ✗         | ✗           | ✓         | 44.4            | 69.8         | 82.2       | 61.5              | 97.8           | 120.0        |
| Multi-stage | TokenHMR    | ✗         | ✗           | ✓         | 44.3            | 71.0         | 84.6       | 55.6              | 91.7           | 109.4        |
| Multi-stage | CameraHMR   | ✗         | ✗           | ✓         | 38.5            | 62.1         | 72.9       | 43.7              | 73.0           | 85.4         |
| Multi-stage | NLF         | ✗         | ✗           | ✗         | 37.3            | 60.3         | 71.4       | **41.2**          | **69.6**       | **82.4**     |
| Multi-stage | PromptHMR   | ✓         | ✗           | ✗         | **36.6**        | **58.7**     | **69.4**   | 41.0              | 71.7           | 84.5         |
| One-stage   | BEV         | ✓         | ✓           | ✓         | 46.9            | 78.5         | 92.3       | 70.9              | 112.2          | 133.4        |
| One-stage   | Multi-HMR   | ✓         | ✓           | ✗         | 45.9            | 73.1         | 87.1       | 50.1              | 81.6           | 95.7         |
| One-stage   | **Human3R** | ✓         | ✓           | ✓         | 44.1            | 71.2         | 84.9       | 48.5              | 73.9           | 86.0         |

Honest reading: Human3R is best only within the **one-stage, intrinsic-free** setting it targets.
Multi-stage methods that use cropping, detection, and/or ground-truth intrinsics (CameraHMR, NLF,
PromptHMR) beat it on every column. The paper's claimed "10% improvement on MPJPE and PVE on
EMDB-1" is relative to Multi-HMR, the comparable one-stage baseline.

### Global Human Motion Estimation

원논문 Table 2. World-coordinate metrics; W-MPJPE aligns the first two frames, WA-MPJPE aligns the
whole 100-frame segment (both mm), RTE is root translation error in % after rigid alignment
without scaling.

| Category | Method      | EMDB-2 WA-MPJPE ↓ | EMDB-2 W-MPJPE ↓ | EMDB-2 RTE ↓ | RICH WA-MPJPE ↓ | RICH W-MPJPE ↓ | RICH RTE ↓ |
| -------- | ----------- | ----------------- | ---------------- | ------------ | --------------- | -------------- | ---------- |
| Offline  | GLAMR       | 280.8             | 726.6            | 11.4         | 129.4           | 236.2          | 3.8        |
| Offline  | SLAHMR      | 326.9             | 776.1            | 10.2         | 132.2           | 237.1          | 6.4        |
| Offline  | COIN        | 152.8             | 407.3            | 3.5          | 169.5           | 254.5          | —          |
| Offline  | GVHMR       | 111.0             | 276.5            | 2.0          | **78.8**        | **126.3**      | **2.4**    |
| Offline  | TRAM        | 76.4              | 222.4            | 1.4          | 127.8           | 238.0          | 6.0        |
| Offline  | JOSH        | **68.9**          | **174.7**        | **1.3**      | 89.0            | 132.5          | 3.0        |
| Online   | TRACE       | 529.0             | 1702.3           | 17.7         | 238.1           | 925.4          | 610.4      |
| Online   | WHAM        | 135.6             | 354.8            | 6.0          | 108.4           | 196.1          | 4.5        |
| Online   | JOSH3R      | 220.0             | 661.7            | 13.1         | —               | —              | —          |
| Online   | **Human3R** | 112.2             | 267.9            | 2.2          | 110.0           | 184.9          | 3.3        |

Honest reading: Human3R is the strongest **online** method and beats WHAM by roughly 20% on
EMDB-2 W-MPJPE and 60% on RTE, as the paper claims. But offline JOSH and TRAM are clearly ahead on
EMDB-2, and GVHMR is ahead on all three RICH metrics; Human3R also loses to WHAM on RICH WA-MPJPE
(110.0 vs 108.4). What Human3R adds over all of these is that it simultaneously outputs scene
geometry and camera poses.

### Human Prior and TTT3R Ablation

원논문 Table 3, on EMDB-2. "Naive" is a simple combination of Multi-HMR and CUT3R.

| Ablations            | WA-MPJPE ↓ | W-MPJPE ↓ | RTE ↓   |
| -------------------- | ---------- | --------- | ------- |
| Human3R w/o Prior    | 221.2      | 808.4     | 2.2     |
| Human3R w/ ViT-S/672 | 129.9      | 314.2     | 2.2     |
| Human3R w/ ViT-B/672 | 122.1      | 292.9     | 2.2     |
| Human3R w/ ViT-L/672 | 113.6      | 291.7     | 2.2     |
| Human3R w/ ViT-L/896 | **112.2**  | **267.9** | 2.2     |
| Naive w/o TTT3R      | 455.4      | 1263      | 14.3    |
| Naive w/ TTT3R       | 401.3      | 1173.9    | 12.2    |
| Human3R w/o TTT3R    | 124.3      | 292.3     | 2.5     |
| Human3R w/ TTT3R     | **112.2**  | **267.9** | **2.2** |

The naive Multi-HMR + CUT3R combination is roughly 4× worse than Human3R on WA-MPJPE, which is the
paper's evidence that prompt tuning — not merely stacking two models — is what works.

### Full Backbone Sweep

원논문 Table 8. Same ablation extended to all four benchmarks plus FPS.

| Ablations            | 3DPW PA-MPJPE ↓ | 3DPW MPJPE ↓ | EMDB-1 PA-MPJPE ↓ | EMDB-1 MPJPE ↓ | EMDB-2 WA-MPJPE ↓ | RICH WA-MPJPE ↓ | RICH W-MPJPE ↓ | RICH RTE ↓ | FPS ↑  |
| -------------------- | --------------- | ------------ | ----------------- | -------------- | ----------------- | --------------- | -------------- | ---------- | ------ |
| Human3R w/o Prior    | 102.1           | 173.5        | 145.8             | 214.0          | 221.2             | 226.0           | 399.5          | 3.4        | **18** |
| Human3R w/ ViT-S/672 | 56.1            | 87.8         | 66.9              | 93.6           | 129.9             | 131.8           | 208.3          | 3.3        | 15     |
| Human3R w/ ViT-B/672 | 49.3            | 79.6         | 56.6              | 84.1           | 122.1             | 119.2           | 188.3          | 3.3        | 11     |
| Human3R w/ ViT-L/672 | 48.5            | 83.1         | 54.1              | 82.9           | 113.6             | 110.3           | 185.0          | 3.3        | 7      |
| Human3R w/ ViT-L/896 | **44.1**        | **71.2**     | **48.5**          | **73.9**       | **112.2**         | **110.0**       | **184.9**      | 3.3        | 5      |

### Inference Speed

원논문 Table 4. FPS on an NVIDIA RTX 4090 with dual Intel Xeon Gold 6530 CPUs.

| Model                | 3DPW (288×512) | BEDLAM (512×288) | RICH (512×368) | EMDB (384×512) | Bonn (512×384) | TUM-D (512×384) |
| -------------------- | -------------- | ---------------- | -------------- | -------------- | -------------- | --------------- |
| Human3R w/ ViT-S/672 | **15.87**      | **15.64**        | **14.28**      | **13.75**      | **13.65**      | **13.59**       |
| Human3R w/ ViT-B/672 | 13.33          | 12.69            | 11.89          | 11.68          | 11.67          | 12.41           |
| Human3R w/ ViT-L/672 | 9.17           | 8.73             | 8.38           | 8.27           | 8.27           | 8.61            |
| Human3R w/ ViT-L/896 | 5.38           | 5.3              | 5.15           | 5.09           | 5.06           | 5.15            |

### Pipeline Latency Comparison

원논문 Tables 5, 6, 7. Average runtime per frame in seconds, measured on 3DPW sequences.

| Pipeline stage / model                   | Seconds ↓  |
| ---------------------------------------- | ---------- |
| GVHMR: YOLOv8 (detection)                | 0.041      |
| GVHMR: ViTPose (2D keypoints)            | 0.067      |
| GVHMR: ViT feature extraction            | 0.059      |
| GVHMR: DPVO (SLAM)                       | 0.037      |
| GVHMR: HMR                               | 0.001      |
| **GVHMR total (4.88 FPS, single-human)** | **0.205**  |
| TRAM: DEVA (detection & tracking)        | 0.3617     |
| TRAM: SAM (segmentation)                 | 0.1757     |
| TRAM: DROID-SLAM                         | 0.0463     |
| TRAM: ZoeDepth (metric depth)            | 0.0120     |
| TRAM: global alignment                   | 0.0049     |
| TRAM: VIMO (HMR)                         | 0.5581     |
| **TRAM total (0.86 FPS, multi-human)**   | **1.1587** |

Human3R component breakdown (원논문 Table 7):

| Module            | ViT-S/672 | ViT-B/672 | ViT-L/672 | ViT-L/896 |
| ----------------- | --------- | --------- | --------- | --------- |
| Encoder           | 0.012     | 0.012     | 0.012     | 0.012     |
| Multi-HMR Encoder | 0.011     | 0.023     | 0.057     | 0.134     |
| Decoder           | 0.019     | 0.019     | 0.019     | 0.019     |
| Heads             | 0.021     | 0.021     | 0.021     | 0.021     |
| **Total (s)**     | **0.063** | 0.075     | 0.109     | 0.186     |
| **FPS**           | **15.87** | 13.33     | 9.17      | 5.38      |

The paper also notes that JOSH, which likewise reconstructs humans and scenes jointly, reports
approximately 0.8 FPS on an RTX 4090.

### Generic 3D Reconstruction

Camera pose estimation on TUM-dynamics (ATE after Sim(3) alignment) and metric-scale video depth on
Bonn (Abs Rel, δ<1.25) are reported **only as plots** in 원논문 Figure 9, not as numeric tables, so no
values are transcribed here. The qualitative findings: VGGT and StreamVGGT use full attention and run
out of memory on long sequences; CUT3R keeps low GPU usage but forgets long sequences; integrating
TTT3R with Human3R improves camera pose and depth over plain TTT3R. VGGT and StreamVGGT are excluded
from the metric-depth plot because they predict only relative depth.

## 💡 Insights & Impact

### Prompt tuning preserves what fine-tuning would destroy

The whole design rests on keeping CUT3R frozen. Its persistent internal state already encodes the
scene and, implicitly, the people in it; the risk of full fine-tuning on a small synthetic dataset
like BEDLAM is losing the general spatiotemporal prior. VPT sidesteps this, which is why one GPU-day
suffices and why the scene reconstruction actually **improves** after human-only fine-tuning — the
paper presents this mutual benefit as evidence that joint human–scene reasoning helps both.

### The head is the right anchor

Choosing head tokens as prompts is a strong inductive bias: heads are the most discriminative body
keypoint, so the prompts localize people cheaply and then aggregate whole-body information by
self-attention. The cost is the paper's first stated limitation — reconstruction fails when the head
is not visible.

### Intrinsic-free robustness

Multi-HMR needs ground-truth intrinsics and is sensitive to image aspect ratio; Human3R inherits
CUT3R's spatial understanding and performs consistently without intrinsics, which is what makes it
usable on intrinsic-agnostic internet video.

### Online, not most accurate

The results consistently show Human3R winning the online category and trailing offline
optimization-based pipelines. Its argument is throughput and completeness rather than peak accuracy:
0.063s/frame for humans **and** scene **and** camera, versus 1.16s/frame for TRAM's humans alone.

## 🔗 Related Work

- [CUT3R](cut3r.md) — the frozen 4D backbone. Human3R's entire method is a parameter-efficient prompt-tuning layer on top of it.
- [ODHSR](odhsr.md) — the closest neighbour in the collection on joint human + scene reconstruction from monocular video; ODHSR optimizes per scene while Human3R is feed-forward and online.
- [MonST3R](monst3r.md) — the dynamic DUSt3R line that handles moving scenes without an explicit human model.
- [VGGT](../reconstruction/vggt.md) — used as an offline upper bound for camera pose in Figure 9; its full attention makes it accurate but memory-bound on long sequences.
- [Dynamic Point Maps](dynamic-point-maps.md) and [V-DPM](v-dpm.md) — the complementary approach of representing dynamics in the point-map representation itself rather than with a parametric body model.

## 📚 Key Takeaways

1. **A 4D reconstruction foundation model already contains most of what human mesh recovery needs** — one day of prompt tuning on one GPU converts CUT3R into a multi-person 4D human-scene reconstructor.
2. **Head tokens make excellent visual prompts**, far better than randomly initialized ones; without the human prior, EMDB-2 WA-MPJPE degrades from 112.2 to 221.2.
3. **Stacking models is not enough**: the naive Multi-HMR + CUT3R baseline is ~4× worse than prompt-tuned Human3R.
4. **Real-time and complete, not maximally accurate**: 15 FPS and 8 GB for humans, scene, and camera, but offline JOSH/TRAM/GVHMR still lead several global-motion metrics.
5. **Joint reasoning is mutually beneficial** — fine-tuning for humans also improved the scene reconstruction and camera poses over the CUT3R baseline.

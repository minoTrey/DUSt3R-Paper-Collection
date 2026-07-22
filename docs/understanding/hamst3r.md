# HAMSt3R: Human-Aware Multi-view Stereo 3D Reconstruction (ICCV 2025)

![hamst3r — architecture](https://arxiv.org/html/2508.16433/imgs/GA_scene/input_0.jpg)

_Results on HumGen3D data (on a scene not seen during training), using global alignment: Given a set of images of a scene (three out of eight of them… (원논문 Fig. 3)_

## 📋 Overview

- **Authors**: Sara Rojas, Matthieu Armando, Bernard Ghanem, Philippe Weinzaepfel, Vincent Leroy, Grégory Rogez
- **Institution**: KAUST, NAVER LABS Europe
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2508.16433)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: MASt3R extended with instance-segmentation and DensePose heads plus a DUNE distilled encoder, producing dense pointmaps enriched with human semantics in a single feed-forward pass — no optimization pipeline.

## 🎯 Key Contributions

1. **Human-aware pointmaps**: Every predicted 3D point is classified human / non-human, with human points mapped to specific body locations of a specific person instance.
2. **DUNE encoder**: Replaces the MASt3R encoder with a distilled ViT-B/14 that fuses three teachers — DINOv2, Multi-HMR, and the MASt3R encoder itself — via the UNIC projection mechanism.
3. **Two new heads**: A Mask2Former-inspired instance segmentation head and a continuous DensePose head (RGB SMPL-template map + validity mask), trained jointly with the MASt3R pointmap and matching heads.
4. **Synthetic human dataset**: 524k images rendered from 10k scenes and 1000 unique 3D environments (Infinigen Indoors + HumGen3D), ~5 persons per scene.
5. **Feed-forward SMPL fitting**: The semantic pointmap lets SMPL be fit as a cheap post-process rather than through a multi-stage optimization pipeline.

## 🔧 Technical Details

### Architecture

Two images pass through a shared ViT encoder, then separate ViT decoders with cross-attention (the DUSt3R/MASt3R layout). Each decoder feeds three linear heads: PointMap, Segmentation, DensePose. The paper uses linear heads exclusively (no DPT).

### Losses

The total objective is a weighted sum:

```text
L = L_MASt3R + λ1·L_seg + λ2·L_dp + λ3·L_mask
```

- `L_seg`: classification (human vs. background) + mask loss (BCE + dice), following Mask2Former.
- `L_dp`: L2 on the continuous RGB DensePose map — the problem is cast as 3D regression, not discrete body-part classification.
- `L_mask`: cross-entropy on the SMPL-projection binary mask (excludes hair and clothing, unlike the instance mask which covers the full silhouette).

Supplementary material reports the final weights as λ1 = 0.01, λ2 = 1, λ3 = 1.

### Training

- DUNE encoder is **frozen**; decoders and new heads are fine-tuned.
- Each epoch mixes 50% original MASt3R data (supervising only pointmaps + matching) with 50% human-centric data (supervising all heads).
- Images downscaled to a max dimension of 518 px.

### Human-centric training data

원논문 Table 1.

| Dataset  | Domain    | Type             | Scenes |
| -------- | --------- | ---------------- | ------ |
| HumGen3D | Synthetic | Indoor           | 10k    |
| BEDLAM   | Synthetic | Indoor & Outdoor | 9.2k   |
| HuMMan   | Real      | Studio           | 339    |
| EgoBody  | Real      | Indoor           | 125    |

### Beyond two views

The network runs independently on every image pair; pointmaps are aligned with the MASt3R global alignment procedure. Instance IDs are reconciled across pairs by 2D overlap, and DensePose predictions for the same image are fused by confidence-weighted averaging.

## 📊 Results

### Human pose on EgoHumans and EgoExo4D

원논문 Table 2. MPJPE in meters.

| Method         | EgoHumans W-MPJPE ↓ | EgoHumans GA-MPJPE ↓ | EgoHumans PA-MPJPE ↓ | EgoExo4D W-MPJPE ↓ | EgoExo4D PA-MPJPE ↓ |
| -------------- | ------------------- | -------------------- | -------------------- | ------------------ | ------------------- |
| Multi-HMR      | 7.66                | 0.99                 | 0.12                 | 2.88               | **0.07**            |
| UnCaliPose     | 3.51                | 0.67                 | 0.13                 | 2.90               | 0.13                |
| HSfM (init)    | 4.28                | 0.51                 | 0.06                 | 5.29               | **0.07**            |
| HSfM           | **1.04**            | **0.21**             | **0.05**             | 0.56               | 0.06                |
| HAMSt3R (Ours) | 3.80                | 0.42                 | 0.14                 | **0.51**           | 0.09                |

HAMSt3R wins W-MPJPE on EgoExo4D but **loses PA-MPJPE to HSfM on both datasets** and loses every EgoHumans metric to HSfM. The paper attributes the EgoHumans gap to large open outdoor scenes where downscaling shrinks subjects, and to the MASt3R log-scaling of the 3D regression loss which under-penalizes distant points.

### Camera pose on EgoExo4D

원논문 Table 3.

| Method         | TE ↓     | s-TE ↓   | AE ↓     | RRA@10 ↑ | CCA@10 ↑ | s-CCA@10 ↑ |
| -------------- | -------- | -------- | -------- | -------- | -------- | ---------- |
| UnCaliPose     | 2.43     | 1.16     | 65.61    | 0.19     | -        | 0.24       |
| DUSt3R         | -        | 0.33     | 9.92     | 0.81     | -        | 0.64       |
| MASt3R         | 0.96     | 0.35     | 11.70    | 0.79     | 0.06     | 0.68       |
| HSfM           | 0.95     | 0.36     | 11.57    | 0.78     | 0.07     | 0.67       |
| DUNE           | 1.03     | 0.26     | 6.45     | 0.94     | 0.25     | 0.85       |
| HAMSt3R (Ours) | **0.60** | **0.15** | **2.85** | **0.99** | **0.42** | **0.87**   |

### Camera pose on EgoHumans

원논문 Table 3. Here DUNE — the frozen encoder HAMSt3R builds on — is better on every metric.

| Method         | TE ↓     | s-TE ↓   | AE ↓     | RRA@10 ↑ | CCA@10 ↑ | s-CCA@10 ↑ |
| -------------- | -------- | -------- | -------- | -------- | -------- | ---------- |
| UnCaliPose     | 2.63     | 2.63     | 60.90    | 0.28     | -        | 0.33       |
| DUSt3R         | -        | 1.15     | 11.00    | 0.61     | -        | 0.49       |
| MASt3R         | 4.97     | 0.92     | 10.42    | 0.61     | 0.06     | 0.65       |
| HSfM           | 2.09     | 0.75     | 9.35     | 0.72     | 0.32     | 0.75       |
| DUNE           | **1.43** | **0.17** | **3.51** | **0.96** | 0.27     | **0.97**   |
| HAMSt3R (Ours) | 2.33     | 0.40     | 10.24    | 0.77     | 0.06     | 0.75       |

원논문 Table 4 splits this by scale: on small environments (Basketball, Fencing, Lego, Tagging) HAMSt3R reaches TE 1.31 / s-TE 0.12 / AE 2.32 / RRA@10 1.00, edging out DUNE (2.04 / 0.11 / 2.36 / 1.00); on large open scenes (Badminton, Tennis, Volleyball) it degrades to TE 3.30 / AE 16.303 / RRA@10 0.58 against DUNE's 0.98 / 4.78 / 0.90.

### Multi-view depth (traditional 3D task)

원논문 Table 6. The paper is explicit that performance drops relative to DUSt3R and MASt3R.

| Method         | KITTI rel ↓ | KITTI τ ↑ | ScanNet rel ↓ | ScanNet τ ↑ | ETH3D rel ↓ | ETH3D τ ↑ | Avg rel ↓ | Avg τ ↑   |
| -------------- | ----------- | --------- | ------------- | ----------- | ----------- | --------- | --------- | --------- |
| DeepV2D        | 10.00       | 36.20     | 4.40          | 54.80       | 11.80       | 29.30     | 8.60      | 39.90     |
| DUSt3R         | 5.88        | 47.67     | **3.01**      | **72.54**   | 3.04        | 75.17     | 3.56      | 69.56     |
| MASt3R         | **3.54**    | **65.68** | 4.17          | 65.22       | **2.44**    | **82.77** | **3.13**  | **73.69** |
| DUNE           | 4.88        | 50.76     | 4.24          | 59.68       | 2.48        | 77.97     | 3.38      | 68.65     |
| HAMSt3R (Ours) | 5.60        | 45.66     | 4.43          | 56.50       | 2.96        | 71.68     | 4.26      | 61.00     |

원논문 Table 6 also reports DTU and T&T, where HAMSt3R is likewise last (DTU 5.31 rel / 57.62 τ; T&T 3.01 / 73.53).

### Multi-view pose regression

원논문 Table 5, 10 random frames.

| Method         | CO3Dv2 RRA@15 ↑ | CO3Dv2 RTA@15 ↑ | CO3Dv2 mAA(30) ↑ | RealEstate10K mAA(30) ↑ |
| -------------- | --------------- | --------------- | ---------------- | ----------------------- |
| DUSt3R         | 93.3            | 88.4            | 77.2             | 61.2                    |
| MASt3R         | **94.6**        | **91.9**        | **81.8**         | 76.4                    |
| DUNE           | 92.2            | 90.7            | 78.7             | **80.1**                |
| HAMSt3R (Ours) | 90.7            | 90.2            | 76.3             | 77.4                    |

CO3Dv2 drops relative to DUSt3R/MASt3R; RealEstate10K improves over both, which the paper attributes to the DUNE distillation.

### Runtime

원논문 Table 7, 4-view / 3-person scene on a single NVIDIA V100.

| Method  | Stage                                     | Time      |
| ------- | ----------------------------------------- | --------- |
| HAMSt3R | Reconstruction + Segmentation + DensePose | ~14s      |
| HAMSt3R | SMPL fitting (post-process)               | ~6s       |
| HAMSt3R | **Total**                                 | **~32s**  |
| HSfM    | 2D pose initialization                    | ~1s       |
| HSfM    | Segmentation (SAM)                        | ~2s       |
| HSfM    | 3D reconstruction (DUSt3R)                | ~18s      |
| HSfM    | Stage 1 (translation & scale only)        | ~25s      |
| HSfM    | Stage 2 (global orientation + align)      | ~48s      |
| HSfM    | Stage 3 (local body pose)                 | ~24s      |
| HSfM    | **Total**                                 | **~118s** |

The paper does not state a speedup ratio, so none is reported here.

## 💡 Insights & Impact

### The distillation trade-off is measured, not hidden

The paper reports both directions honestly: the DUNE encoder buys human understanding and much better egocentric camera pose, but costs structure-level depth accuracy. Table 6 shows the drop occurs already between MASt3R and DUNE (3.13 → 3.38 average rel), before HAMSt3R's human heads add a further loss (→ 4.26). Attributing the regression to two separable causes — encoder change and 50% human data mixing — is unusually clean reporting.

### Scale sensitivity as a diagnostic

Table 4's large/small split turns a puzzling aggregate loss into a specific hypothesis: MASt3R's log-scaled 3D regression loss does not penalize distant points enough, so large outdoor scenes suffer. This is a concrete, testable claim about a loss design choice inherited from an ancestor model.

### Semantics attached to geometry, not fused afterwards

Prior joint human-scene methods (JOSH, HSfM, SynCHMR) chain off-the-shelf modules and reconcile them with global optimization. HAMSt3R predicts geometry and human semantics from shared decoder features in one pass, and only uses optimization for the optional SMPL fit at evaluation time.

### Limitations acknowledged

SMPL fitting fails when subjects are far from the camera (sparse, noisy points) and under extreme body poses where DensePose breaks down.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md) — the direct base; HAMSt3R adds heads and swaps the encoder
- [DUSt3R](../foundation/dust3r.md) — pointmap paradigm and the multi-view depth protocol used here
- [Human3R](../dynamic/human3r.md) — the other human-centric entry in this collection, targeting 4D
- [MUSt3R](../reconstruction/must3r.md) and [CUT3R](../dynamic/cut3r.md) — cited as the efficiency-focused extensions of the same lineage
- [Splatt3R](../gaussian-splatting/splatt3r.md) — cited as a DUSt3R extension producing Gaussian parameters
- [MonST3R](../dynamic/monst3r.md) — cited as the dynamic-scene extension

## 📚 Key Takeaways

1. **A pointmap can carry semantics.** Classifying each 3D point as human / non-human and mapping it to an SMPL surface location makes the reconstruction directly usable for tracking and interaction, not just geometry.
2. **Encoder distillation is a real trade.** DUNE improves human and egocentric-pose performance while measurably degrading building/structure depth — the paper shows both halves.
3. **Feed-forward beats staged optimization on cost.** ~32s vs ~118s on a 4-view, 3-person scene (Table 7), with the SMPL fit needed only for evaluation.
4. **HAMSt3R does not win everywhere.** It loses PA-MPJPE to HSfM, loses multi-view depth to DUSt3R/MASt3R, and loses EgoHumans camera pose to the DUNE encoder it is built on.

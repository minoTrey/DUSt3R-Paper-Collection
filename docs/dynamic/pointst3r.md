# PointSt3R: Point Tracking through 3D Grounded Correspondence (WACV 2026)

## 📋 Overview

- **Authors**: Rhodri Guerrier, Adam W. Harley, Dima Damen
- **Institution**: University of Bristol, Meta Reality Labs Research
- **Venue**: WACV 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.26443) | [Project Page](http://rhodriguerrier.github.io/PointSt3R)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Reformulates point tracking as pairwise 3D-grounded correspondence, fine-tuning MASt3R on dynamic correspondences with a visibility head so that a model with **no temporal context** competes with dedicated point trackers.

## 🎯 Key Contributions

1. **Diagnosis**: MASt3R is already a strong point tracker on _static_ points — it beats CoTracker3 on the EgoPoints static split by +13.7% — but collapses on dynamic points, trailing CoTracker3 by −25.6% on PointOdyssey and −23.5% on EgoPoints.
2. **Fine-tuning strategy**: image pairs at large temporal strides from existing 3D point-tracking datasets, combining the reconstruction loss with a dynamic correspondence loss and a new visibility head.
3. **No temporal context**: training and evaluation use only _pairs_ of frames where one contains the query point. The paper's stated goal is not to build the best tracker but to measure what 3D grounding foundation models can do for tracking.
4. **Static/dynamic mixing ratio matters**: the ratio `r` of dynamic correspondences per batch is ablated; both 0% and 100% degrade, and `r = 95%` is chosen.
5. **2D and 3D tracking** from the same model, with 3D results reported both with pointmaps and with ZoeDepth lifting.

## 🔧 Technical Details

### Formulating tracking as correspondence

Given a query point `i` and frames `I⁰ … I^T`, PointSt3R feeds the pair `(I^q, I^t)` — query timestep and target timestep — extracts feature maps `D^q, D^t`, computes cosine similarity of `D^q(i)` against all features in `D^t`, and takes the argmax pixel position as the tracked location. Bilinear interpolation is used when indexing the query correspondence feature.

### Losses

The matching loss is the InfoNCE-style symmetric objective from MASt3R over ground-truth correspondences `M̂`, with

```text
s_τ(i, j) = exp[−τ · D_i^{1T} D_j^2]
```

used in a confidence-weighted form that shares confidence maps with the regression loss. The total objective weights the regression, matching, and visibility terms by `α, β, γ`, set to 0.075, 0.075, and 1.0 respectively.

### Visibility head

Added to both branches, using the same MLP architecture as the feature heads but with output dimension 1, randomly initialized. Each head predicts whether each pixel is visible in the _other_ branch's image.

### Training setup

- MASt3R's encoder is frozen; decoders and heads are fine-tuned from pretrained MASt3R weights.
- 10,000 samples evenly split across PointOdyssey, Kubric, and DynamicReplica.
- Dynamic points are identified as 2D track correspondences whose 3D world coordinates differ across the image pair.
- Following MonST3R's temporal striding, sampling probability increases linearly with stride length; strides are `[10, 30, 50, …, 170]` for PointOdyssey and DynamicReplica, `[10, 20, …, 90]` for the shorter Kubric videos.
- 4096 positive and 4096 negative correspondences are targeted per sample, padded with extra negatives when large strides leave fewer matches.
- Learning rate 5×10⁻⁵, batch size 16, on 4 H100 GPUs. Roughly 12 hours for 50 epochs. Inference at (512, 384).

## 📊 Results

### The static/dynamic split that motivates the work

원논문 Table 1. δ<sub>avg</sub> on labelled static and dynamic subsets.

| Model      | Static PointOdyssey | Static EgoPoints | Dynamic PointOdyssey | Dynamic EgoPoints |
| ---------- | ------------------- | ---------------- | -------------------- | ----------------- |
| PIPs++     | 34.5                | 47.6             | 22.7                 | 20.0              |
| CoTracker2 | 42.1                | 45.2             | 26.2                 | 20.2              |
| CoTracker3 | **82.6**            | 65.0             | **50.1**             | **35.8**          |
| MASt3R     | 67.0                | **78.7**         | 24.5                 | 12.3              |

MASt3R's +33.5 point lead over CoTracker2 on EgoPoints static (78.7 vs 45.2) is the abstract's headline; its 12.3 on EgoPoints dynamic is the problem.

### 2D point tracking

원논문 Table 2. Tracking accuracy δ<sub>avg</sub> ↑ using the "first" query mode. Temporally-informed trackers appear above the correspondence models in the original table.

| Model         | TAP-Vid-DAVIS | RoboTAP  | RGB-S    | EgoPoints | Dyn. RoboTAP | Dyn. RGB-S | Dyn. EgoPoints |
| ------------- | ------------- | -------- | -------- | --------- | ------------ | ---------- | -------------- |
| PIPs++        | 69.1          | 63.0     | 77.8     | 36.9      | 62.7         | 51.3       | 20.0           |
| CoTracker2    | 75.7          | 70.6     | 83.3     | 35.5      | 66.9         | 53.7       | 20.2           |
| CoTracker3    | **76.7**      | **78.8** | 82.8     | 54.2      | **74.6**     | **65.2**   | **35.8**       |
| LoFTR         | 22.8          | 24.8     | 28.8     | 9.2       | 11.4         | 18.6       | 4.8            |
| DINOv2        | 13.4          | 15.1     | 15.9     | 5.8       | 10.7         | 11.0       | 4.8            |
| MASt3R        | 38.5          | 71.6     | 73.2     | 53.5      | 42.5         | 39.4       | 12.3           |
| **PointSt3R** | 73.8          | 78.6     | **87.0** | **61.3**  | 69.4         | 61.6       | 31.4           |

Reported honestly by the authors: PointSt3R falls short of CoTracker2 and CoTracker3 on TAP-Vid-DAVIS by −1.9% and −2.9%, falls short of CoTracker3 on RoboTAP by −0.2%, and is 4.4% below CoTracker3 on dynamic EgoPoints. It _outperforms_ CoTracker2 on RGB-S by 3.7% and beats all listed models on EgoPoints all-points and RGB-S.

원논문 Table 3. Occlusion accuracy on TAP-Vid-DAVIS.

| Model      | OA       |
| ---------- | -------- |
| CoTracker2 | 88.3     |
| CoTracker3 | **90.2** |
| PointSt3R  | 85.8     |

PointSt3R sits 2.5% and 4.4% below CoTracker2 and CoTracker3 respectively — achieved without any temporal context.

### 3D point tracking

원논문 Table 4. APD with fixed thresholds `[0.1, 0.3, 0.5, 1.0]` and median global scaling on the PStudio minival set. "w G.T." uses the ground-truth intrinsics matrix for lifting to 3D.

| Model                 | w G.T.   | w/o G.T. |
| --------------------- | -------- | -------- |
| CoTracker3 + ZoeDepth | 80.3     | 66.2     |
| SpaTracker + ZoeDepth | **81.6** | **67.1** |
| DELTA + ZoeDepth      | 79.2     | 66.3     |
| MASt3R                | –        | 40.5     |
| MASt3R + ZoeDepth     | 36.1     | 33.8     |
| PointSt3R             | –        | 61.2     |
| PointSt3R + ZoeDepth  | 75.3     | 62.9     |

PointSt3R improves over MASt3R by +39.2% and +29.1% with ZoeDepth and by 20.7% with pointmaps, but underperforms CoTracker3 by 5.0% with ground-truth intrinsics and 3.3% with estimated intrinsics. St4RTrack is not compared because its model is not public.

### Ablations

원논문 Table 5. Training stride schedule, evaluated on TAP-Vid-DAVIS.

| Strides                                  | δ<sub>avg</sub> ↑ |
| ---------------------------------------- | ----------------- |
| [1, 2, 3, 4, 5, 6, 7, 8, 9]              | 68.5              |
| [1, 5, 10, 15, 20, 25, 30, 35, 40]       | 72.2              |
| [10, 20, 30, 40, 50, 60, 70, 80, 90]     | 73.4              |
| [10, 30, 50, 70, 90, 110, 130, 150, 170] | **73.8**          |

원논문 Table 6. Fine-tuning dataset mixture, TAP-Vid-DAVIS.

| Datasets                               | δ<sub>avg</sub> ↑ |
| -------------------------------------- | ----------------- |
| PointOdyssey                           | 72.7              |
| PointOdyssey + Kubric                  | 73.2              |
| PointOdyssey + Kubric + DynamicReplica | **73.8**          |

원논문 Table 8, the full dynamic-ratio sweep. Selected rows; `PO` is the PointOdyssey split.

| Model            | All DAVIS | All RoboTAP | All RGB-S | All EgoPoints | All PO   | Dyn. RoboTAP | Dyn. RGB-S | Dyn. EgoPoints | Dyn. PO  |
| ---------------- | --------- | ----------- | --------- | ------------- | -------- | ------------ | ---------- | -------------- | -------- |
| MASt3R           | 38.5      | 71.6        | 73.2      | 53.5          | 45.6     | 42.5         | 39.4       | 12.3           | 25.2     |
| PointSt3R - 0%   | 20.2      | 56.0        | 64.4      | 48.2          | 38.8     | 13.5         | 22.2       | 8.5            | 7.4      |
| PointSt3R - 50%  | 71.2      | 77.9        | 84.2      | 59.9          | **57.3** | 65.0         | 55.1       | 27.8           | 38.6     |
| PointSt3R - 95%  | 73.8      | **78.6**    | **87.0**  | **61.3**      | 56.2     | 69.4         | 61.6       | 31.4           | 43.4     |
| PointSt3R - 99%  | **73.9**  | **78.6**    | 86.3      | **61.3**      | 53.9     | 69.2         | 62.2       | 31.7           | 43.7     |
| PointSt3R - 100% | 73.8      | 76.2        | 75.0      | 57.7          | 31.4     | **69.8**     | **62.3**   | **32.3**       | **43.8** |

At 100% dynamic the model shows catastrophic forgetting of the 3D grounding — PointOdyssey all-points falls to 31.4 and RGB-S to 75.0 — even as dynamic-only metrics keep creeping up. At 0% dynamic the model drops _below_ the MASt3R baseline almost everywhere. `r = 95%` is chosen for consistency across datasets and splits.

원논문 Table 7. Inference resolution and feature sampling, TAP-Vid-DAVIS.

| Resolution | Sampling | δ<sub>avg</sub> ↑ |
| ---------- | -------- | ----------------- |
| (512, 160) | Nearest  | 63.5              |
| (512, 256) | Nearest  | 70.0              |
| (512, 288) | Nearest  | 70.7              |
| (512, 336) | Nearest  | 71.9              |
| (512, 384) | Nearest  | 72.7              |
| (512, 384) | Bilinear | **73.8**          |

Bilinear interpolation over nearest-neighbour sampling is worth +1.1%.

### Cost

원논문 Table 9. Runtime for a 16-frame window with 5 query points.

| Model      | Time (s) |
| ---------- | -------- |
| CoTracker3 | 0.3      |
| PointSt3R  | 1.7      |

The paper states PointSt3R is **5× slower** than CoTracker3, expected given the pairwise formulation, and notes the implementation is not particularly optimised.

## 💡 Insights & Impact

### Temporal context is less essential than assumed

The central empirical result is that a purely pairwise model with no temporal window reaches within ~2–3 points of CoTracker3 on TAP-Vid-DAVIS and _exceeds_ every listed tracker on EgoPoints and RGB-S. The authors state this directly: "temporal context can be removed from point trackers without impacting the performance much."

### MASt3R's features are globally 3D-sensitive but locally blind

The PCA visualisation (Figure 2) is the qualitative counterpart to Table 1: MASt3R's feature maps represent the static 3D background well but produce no distinctive features for dynamic objects, whereas CoTracker3's features are locally sensitive without global structure. PointSt3R's contribution is recovering local discriminability while retaining the 3D global features.

### Dynamic training data is a dial, not a switch

The dynamic-ratio sweep is the paper's most instructive ablation. Training on only static correspondences pushes performance _below_ the untouched MASt3R baseline, and training on only dynamic correspondences destroys the 3D grounding that made MASt3R strong in the first place. The useful regime is a heavy but not exclusive dynamic mix.

### Stride length is what makes long-term tracking work

Table 5 shows a 5.3-point spread from short to long strides, and the supplementary track-length analysis shows the advantage concentrating on tracks longer than 20 frames. Large temporal gaps during training are what teach the model long-term correspondence.

### Scope, stated plainly

The paper is explicit that it does not aim to produce a competitive point tracker but to evaluate what 3D-grounding foundation models offer for the task. The 5× runtime gap and the OA shortfall should be read in that light.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md) — the starting point; PointSt3R fine-tunes its decoders and heads.
- [DUSt3R](../foundation/dust3r.md) — the pointmap regression foundation MASt3R extends.
- [MonST3R](../dynamic/monst3r.md) — the precedent that dynamic reconstruction failure is a training-regime problem, not an architectural one, and the source of the temporal striding scheme.
- [Dynamic Point Maps](../dynamic/dynamic-point-maps.md) — DPM, cited among 3D-tracking approaches.
- [D4RT](../dynamic/d4rt.md) — a unified 4D query-based model addressing the same dynamic-correspondence gap.
- [Easi3R](../dynamic/easi3r.md) — related work on static/dynamic separation in DUSt3R-family models.

## 📚 Key Takeaways

1. **MASt3R is already a strong static point tracker** — +33.5% over CoTracker2 on EgoPoints static (원논문 Table 1) — its weakness is confined to dynamic correspondence.
2. **A pairwise, temporally-blind model reaches 73.8 δ<sub>avg</sub> on TAP-Vid-DAVIS** and 87.0 on RGB-S, exceeding CoTracker2 on the latter (원논문 Table 2).
3. **The wins and losses are both real**: PointSt3R leads on EgoPoints and RGB-S but trails CoTracker3 on TAP-Vid-DAVIS, RoboTAP, occlusion accuracy, and 3D APD.
4. **95% dynamic correspondences is the sweet spot** — 0% falls below the baseline, 100% causes catastrophic forgetting of 3D grounding (원논문 Table 8).
5. **Long training strides are essential** for long-term tracking, worth +5.3 δ<sub>avg</sub> from the shortest to longest schedule (원논문 Table 5).

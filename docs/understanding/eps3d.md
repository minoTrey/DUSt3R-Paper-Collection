# EPS3D: End-to-End Feed-Forward 3D Panoptic Segmentation (ICML 2026)

## 📋 Overview

- **Authors**: Runsong Zhu, Jiaxin Guo, Xiaoyang Guo, Zhengzhe Liu, Ka-Hei Hui, Wei Yin, Kai Chen, Wei Chen, Weiqiang Ren, Yunhui Liu, Pheng-Ann Heng, Chi-Wing Fu
- **Institution**: The Chinese University of Hong Kong, Hong Kong Centre for Logistics Robotics, Horizon Robotics, Lingnan University, Autodesk AI Lab
- **Venue**: ICML 2026
- **Links**: [Paper](https://arxiv.org/abs/2606.08980) | [Code](https://github.com/Runsong123/EPS3D)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: The first end-to-end feed-forward framework for open-vocabulary 3D panoptic segmentation — it predicts semantic and instance features directly from the geometry transformer rather than fusing precomputed per-view 2D features, and adds a semantic-instance mutual enhancement module.

## 🎯 Key Contributions

1. **End-to-end instead of two-stage**: LSM and Uni3R first extract per-view features with a 2D model and then fuse them with a 3D network — inheriting the 2D model's view inconsistency. EPS3D takes raw multi-view RGB and predicts a unified 3D panoptic Gaussian representation directly, using 2D foundation models only as training teachers.
2. **Panoptic, not just semantic**: Prior feed-forward work covers semantics only. EPS3D predicts both a 512-d CLIP-aligned semantic feature and a 32-d instance feature per Gaussian.
3. **Sem2Ins**: Semantic features are projected and fused with initial instance features to produce semantically refined instance attributes.
4. **Ins2Sem**: Random anchor Gaussians select top-K neighbors by instance-feature similarity, and semantic features within those neighborhoods are aligned by cosine loss.
5. **Feature splatting as the consistency mechanism**: Supervision is applied to rendered feature maps rather than to head outputs directly, so single-view supervision becomes an implicit multi-view consistency objective.

## 🔧 Technical Details

### Representation

```text
G = { (I_g, S_g), (μ_g, σ_g, r_g, s_g, c_g) }_{g=1}^G
```

with `D_S = 512` (CLIP feature dimension) and `D_I = 32` by default.

### Architecture

A VGGT-based geometry transformer patchifies images and produces 3D-aware aggregated tokens. Four DPT heads consume them: one for depth (back-projected to Gaussian centers), one for the remaining Gaussian attributes (opacity, rotation, scale, SH color), and two more — `F_S` and `F_I` — for the semantic and instance features.

### Training losses

- **Text-aligned semantic loss**: cosine dissimilarity between rendered semantic feature `S_i` and the 2D teacher's feature `Ŝ_i` (LSeg).
- **Instance contrastive loss**: InfoNCE over rendered instance features, with positives/negatives defined by SAM's per-view instance IDs and centroids — making supervision invariant to ID permutation across views.
- **Ins2Sem loss**: cosine alignment of semantic features among top-K instance-similar neighbors of M random anchors.

```text
L_total = w1 L_rgb + w2 L_ins + w3 L_sem + w4 L_Ins2Sem
```

with w1 = 1e-1, w2 = 1e-3, w3 = 1e-1, w4 = 1e-4. Trained on ScanNet and ScanNet++ on eight NVIDIA A800 GPUs.

### Inference

Semantic labels come from argmax cosine similarity between rendered pixel features and CLIP text-encoder prototypes. Instance labels come from HDBSCAN clustering on the 3D instance features, then argmax similarity to the resulting prototypes.

## 📊 Results

### Two-view setting on ScanNet

원논문 Table 1. Reconstruction time measured on a single NVIDIA A800.

| Method       | Type          | Time  | Ctx Sem mIoU ↑ | Ctx Sem Acc. ↑ | Ctx Inst mIoU ↑ | Ctx Inst F-sc. ↑ |
| ------------ | ------------- | ----- | -------------- | -------------- | --------------- | ---------------- |
| LSeg         | 2D            | 0.2s  | 0.4701         | 0.7891         | –               | –                |
| SAM          | 2D            | 1.6s  | –              | –              | 0.3659          | 0.1150           |
| NeRF-DFF     | Two-stage 3D  | 1min  | 0.4540         | 0.7173         | –               | –                |
| Feature-3DGS | Two-stage 3D  | 18min | 0.4453         | 0.7276         | –               | –                |
| Unified-Lift | Two-stage 3D  | 5min  | –              | –              | 0.1441          | 0.2009           |
| LSM          | Two-stage 3D  | 0.43s | 0.5034         | 0.7740         | –               | –                |
| Uni3R        | Two-stage 3D  | 0.85s | 0.5233         | 0.8188         | –               | –                |
| EPS3D (ours) | End-to-end 3D | 0.73s | **0.6323**     | **0.8465**     | **0.4147**      | **0.4552**       |

원논문 Table 1, novel views: EPS3D reaches 0.6432 Sem mIoU / 0.8555 Acc. / 0.4227 Inst mIoU / 0.4387 F-sc., against Uni3R's 0.5336 / 0.8173 for semantics and SAM's 0.3363 / 0.1049 for instances.

### Multi-view (8-view) setting

원논문 Table 2, novel-view columns.

| Method       | ScanNet Sem mIoU ↑ | ScanNet Sem Acc. ↑ | ScanNet Inst mIoU ↑ | Replica Sem mIoU ↑ | Replica Sem Acc. ↑ | Replica Inst mIoU ↑ |
| ------------ | ------------------ | ------------------ | ------------------- | ------------------ | ------------------ | ------------------- |
| LSeg         | 0.4513             | 0.7727             | –                   | 0.4038             | 0.8224             | –                   |
| SAM          | –                  | –                  | 0.2792              | –                  | –                  | 0.2781              |
| Feature-3DGS | 0.2239             | 0.6702             | –                   | 0.3260             | 0.7932             | –                   |
| Unified-Lift | –                  | –                  | 0.1876              | –                  | –                  | 0.2264              |
| LSM          | 0.3351             | 0.7350             | –                   | 0.2874             | 0.6787             | –                   |
| Uni3R        | 0.5215             | 0.8069             | –                   | 0.3216             | 0.7420             | –                   |
| EPS3D (ours) | **0.6169**         | **0.8469**         | **0.3912**          | **0.4833**         | **0.8512**         | **0.3468**          |

The abstract's headline is **+13% mIoU for semantics on Replica**; the context-view Replica comparison in Table 2 is 0.4999 (EPS3D) vs 0.3066 (Uni3R).

### Complete panoptic quality

원논문 Table 3, novel views. Two ensemble baselines are constructed because no prior method does both tasks.

| Method               | ScanNet PQ ↑ | ScanNet SQ ↑ | ScanNet RQ ↑ | Replica PQ ↑ | Replica SQ ↑ | Replica RQ ↑ |
| -------------------- | ------------ | ------------ | ------------ | ------------ | ------------ | ------------ |
| LSeg + SAM           | 0.3803       | 0.4810       | 0.5127       | 0.2617       | 0.3682       | 0.2631       |
| Uni3R + Unified-Lift | 0.4013       | 0.5022       | 0.5189       | 0.2716       | 0.3751       | 0.2834       |
| EPS3D (ours)         | **0.5304**   | **0.6643**   | **0.6759**   | **0.3539**   | **0.4925**   | **0.4166**   |

### Ablation on Replica

원논문 Table 4, novel views.

| Method                       | Sem mIoU ↑ | Sem Acc. ↑ | Inst mIoU ↑ | Inst F-sc. ↑ |
| ---------------------------- | ---------- | ---------- | ----------- | ------------ |
| EPS3D full pipeline          | **0.4833** | **0.8512** | **0.3468**  | **0.3106**   |
| Without feature splatting    | 0.4533     | 0.8112     | 0.2519      | 0.1510       |
| Without Ins2Sem module       | 0.4531     | 0.8201     | 0.3388      | 0.3103       |
| Without Sem2Ins module       | 0.4821     | 0.8500     | 0.3210      | 0.3017       |
| Replace with cross-attention | 0.4677     | 0.8321     | 0.3230      | 0.3065       |

Feature splatting is the single most important component, and the mutual-enhancement design beats a generic cross-attention substitute.

### Where feature splatting matters

원논문 Table 5, Replica, context views. ✓ = feature splatting, ✗ = direct DPT prediction.

| Model          | Training | Inference | Sem mIoU ↑ | Sem Acc. ↑ | Inst mIoU ↑ | Inst F-sc. ↑ |
| -------------- | -------- | --------- | ---------- | ---------- | ----------- | ------------ |
| Model 1 (Full) | ✓        | ✓         | **0.4999** | **0.8629** | **0.3382**  | **0.3232**   |
| Model 2        | ✓        | ✗         | 0.4965     | 0.8617     | 0.3365      | 0.3201       |
| Model 3        | ✗        | ✓         | 0.4615     | 0.8167     | 0.2638      | 0.1598       |
| Model 4        | ✗        | ✗         | 0.4606     | 0.8149     | 0.2609      | 0.1576       |

Model 2 vs Model 1 barely differs, but Model 3 vs Model 1 drops sharply — splatting matters at **training** time, not inference. The explanation: with splatting, each rendered pixel's gradient propagates to every Gaussian with non-zero splatting weight, turning per-view supervision into an implicit multi-view consistency objective.

### Teacher-model sensitivity

원논문 Table 6, Replica, novel views.

| Model             | Instance teacher | Semantic teacher | Sem mIoU ↑ | Sem Acc. ↑ | Inst mIoU ↑ | Inst F-sc. ↑ |
| ----------------- | ---------------- | ---------------- | ---------- | ---------- | ----------- | ------------ |
| Model 1 (default) | SAM              | LSeg             | 0.4833     | 0.8512     | 0.3468      | 0.3106       |
| Model 2           | Semantic-SAM     | LSeg             | 0.4841     | 0.8520     | 0.3485      | 0.3198       |
| Model 3           | SAM              | MaskCLIP         | 0.4788     | 0.8489     | 0.3460      | 0.3100       |

Swapping either teacher changes results marginally, which the paper reads as evidence the framework is not tied to a particular 2D model.

## 💡 Insights & Impact

### Error accumulation is architectural, not incidental

The two-stage feed-forward baselines are fast, but their inputs are per-view 2D features computed independently — inconsistencies are baked in before the 3D network ever sees them. Predicting features from 3D-aware transformer tokens removes that failure mode at the source, and the ~10-point mIoU gap over Uni3R is the measured consequence.

### Semantics and instances are complementary supervision signals

Instance features carry boundary and object-level structure; semantic features carry category context. Coupling them in both directions (Sem2Ins, Ins2Sem) outperforms leaving them independent, and outperforms a naive cross-attention coupling (Table 4).

### Splatting is a training trick, not an inference requirement

Table 5 is the sharpest result in the paper: the model can be trained with feature splatting and then queried without it at almost no cost. This means the multi-view consistency is genuinely internalized into the prediction heads rather than being an artifact of the rendering step.

### Downstream reach

The paper demonstrates robotic manipulation (segmentation guiding grasping) and 3D scene editing (recoloring, cross-scene object insertion) built on the instance-level Gaussians, at roughly 1s per scene.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the geometry transformer backbone
- [Large Spatial Model (LSM)](largespatialmodel.md) — the two-stage feed-forward baseline EPS3D contrasts against throughout
- [DUSt3R](../foundation/dust3r.md) — cited as the origin of feed-forward 3D reconstruction models used for scene understanding
- [FF3R](ff3r.md) — contemporaneous annotation-free joint geometry-semantics feed-forward framework
- [PE3R](pe3r.md) — related perception-efficient 3D reconstruction entry

## 📚 Key Takeaways

1. **End-to-end beats two-stage for 3D understanding.** Predicting semantic and instance features from geometry-transformer tokens avoids the view inconsistency that per-view 2D extraction bakes in.
2. **Panoptic, in one pass, in ~1s.** EPS3D is the first feed-forward method to deliver semantics and instances together, and reports PQ/SQ/RQ against ensemble baselines because no single prior method covers both.
3. **Feature splatting during training is what buys view consistency** — removing it at inference costs almost nothing, removing it during training costs a lot.
4. **Mutual enhancement > generic attention.** Replacing Sem2Ins/Ins2Sem with plain cross-attention degrades all four metrics.
5. **Teacher-agnostic.** Results hold across SAM / Semantic-SAM and LSeg / MaskCLIP.

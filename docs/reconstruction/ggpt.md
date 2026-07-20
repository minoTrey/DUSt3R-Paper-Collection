# GGPT: Geometry-Grounded Point Transformer (CVPR 2026)

## 📋 Overview

- **Authors**: Yutong Chen, Yiming Wang, Xucong Zhang, Sergey Prokudin, Siyu Tang
- **Institution**: ETH Zurich, Delft University of Technology
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.11174) | [Project Page](https://chenyutongthu.github.io/research/ggpt)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A refinement module that corrects feed-forward dense point maps by attending, directly in 3D, between the dense prediction and a sparse but geometrically reliable point cloud from an improved SfM pipeline.

## 🎯 Key Contributions

1. **An improved SfM pipeline** based on dense feature matching plus lightweight geometric optimisation (sparse bundle adjustment and direct linear triangulation), producing accurate camera poses and partial 3D point clouds from sparse views — and, notably, running faster than the SfM alternatives compared.
2. **A geometry-guided 3D point transformer** that jointly processes the dense feed-forward point map and the sparse SfM point cloud and predicts a residual correction per point, reasoning by 3D spatial proximity rather than 2D pixel coordinates.
3. **Architecture- and dataset-agnostic refinement**: trained solely on ScanNet++ with VGGT predictions, GGPT improves VGGT, Pi3, MapAnything, MAtCha, and MASt3R-SfM across in-domain, cross-domain, and out-of-domain settings.

## 🔧 Technical Details

### The problem

Feed-forward reconstructors produce visually coherent dense point maps that nonetheless exhibit multi-layer artifacts and deviate from ground truth, especially outside the training distribution — the paper's out-of-domain examples are clothed human bodies and robotic abdominal surgery. SfM, in contrast, is grounded in explicit geometry and stays consistent, but is fragile under wide baselines and low overlap and recovers only sparse structure. GGPT combines the completeness of the former with the geometric accuracy of the latter.

### Input encoding

Each point carries a positional encoding `PE(·)` (frequency 4) and a learnable type token. Guidance points get `e_type(s)`. Dense points that originate from the same image pixel as a guidance point are given the correspondence explicitly:

```text
z_d^(0) = [PE(x_d), e_type(d), PE(x_d→s), Δ_d→s]
```

where `Δ_d→s = x_d→s − x_s` encodes the positional offset. Dense points without a correspondence use only the first two terms; all embeddings are zero-padded to a uniform dimension.

### Backbone

An 8-layer Point Transformer V3 with patch-wise self-attention over spatial neighbourhoods. At 53M parameters it is deliberately far lighter than the ~300M 2D vision transformers used by prior geometry-conditioned methods. Because attention is over 3D proximity, the receptive field is defined by spatial neighbourhood rather than the 2D grid, which is what enforces multi-view consistency directly. A shared MLP head decodes a residual displacement `δ ∈ R³` and a raw confidence per point.

### Losses

`L = L_conf + λ_id L_id`.

- **Confidence-weighted regression** (heteroscedastic): `L_conf = Σ c‖x̂ − x_GT‖ − α log c`. Ground-truth points are pre-aligned to the guidance `X_s` via Umeyama alignment so that supervision targets local corrections rather than a global shift.
- **Identity consistency**: `L_id = Σ ‖x̂ − x_d→s‖` over points that have a valid guidance correspondence, anchoring predictions to the reliable geometry.

### Configuration

SfM filtering thresholds `ε = 4`, `ε_BA = 0.6`, `ε_DLT = 0.1`, `n_BA = 2048`; after DLT, points with reprojection error above 4 pixels or maximal triangulation angle below 3 degrees are removed. Training uses 20k multi-view sequences from 856 ScanNet++ training scenes, with VGGT supplying `X_d` and the SfM initialisation. Each input patch has a half-width of 0.4× the scene radius; each forward pass processes up to 400k points. `λ_id = 1`, `α = 0.2`. 8 NVIDIA GH200 GPUs for one day.

## 📊 Results

### Within-domain and cross-domain reconstruction

원논문 Table 1. AUC@5/10 cm (% ↑). GGPT is trained only on ScanNet++ with VGGT predictions, so the VGGT/ScanNet++ cell is the only within-domain entry.

| Method             | SNt++ 4 | SNt++ 8 | SNt++ 16 | ETH3D 4 | ETH3D 8 | ETH3D 16 |
| ------------------ | ------- | ------- | -------- | ------- | ------- | -------- |
| VGGT               | 23/37   | 19/32   | 16/29    | 27/41   | 23/36   | 19/32    |
| VGGT + Ours        | 38/53   | 45/60   | 50/66    | 41/55   | 47/61   | 49/63    |
| Pi3                | 54/69   | 56/71   | 58/74    | 31/47   | 25/41   | 23/38    |
| Pi3 + Ours         | 54/68   | 56/72   | 59/74    | 36/53   | 36/53   | 37/54    |
| MapAnything        | 40/57   | 38/57   | 38/58    | 10/20   | 7/15    | 5/12     |
| MapAnything + Ours | 44/61   | 48/64   | 52/68    | 32/43   | 33/45   | 34/47    |
| MAtCha             | 12/19   | 15/26   | 18/32    | 40/52   | 41/53   | 42/56    |
| MAtCha + Ours      | 27/37   | 40/52   | 48/63    | 42/55   | 47/60   | 50/65    |
| MASt3R-SfM         | 12/22   | 14/35   | 16/31    | 37/50   | 39/51   | 40/54    |
| MASt3R-SfM + Ours  | 30/41   | 39/52   | 48/64    | 41/55   | 46/59   | 48/63    |

원논문 Table 1, Tanks and Temples.

| Method             | T&T 4 imgs | T&T 8 imgs | T&T 16 imgs |
| ------------------ | ---------- | ---------- | ----------- |
| VGGT               | 26/40      | 25/39      | 24/38       |
| VGGT + Ours        | 34/47      | 42/57      | 43/57       |
| Pi3                | 25/39      | 26/42      | 25/40       |
| Pi3 + Ours         | 27/43      | 32/50      | 33/50       |
| MapAnything        | 10/21      | 9/20       | 8/17        |
| MapAnything + Ours | 29/43      | 40/55      | 42/56       |
| MAtCha             | 34/47      | 36/50      | 33/47       |
| MAtCha + Ours      | 35/48      | 43/57      | 43/57       |
| MASt3R-SfM         | 34/46      | 37/50      | 36/49       |
| MASt3R-SfM + Ours  | 33/47      | 41/56      | 42/56       |

Two honest near-ties/regressions: Pi3 on ScanNet++ with 4 images drops from 54/69 to 54/68, and MASt3R-SfM on T&T with 4 images drops from 34/46 to 33/47. Pi3 is trained on ScanNet++ alongside many similar indoor scenes, so its within-domain performance is already highly optimised — the gains for Pi3 appear on the cross-domain datasets instead.

An additional trend worth noting: for the un-refined baselines, adding more views often makes AUC _worse_ (VGGT on ScanNet++: 23 → 19 → 16), whereas after refinement it improves monotonically (38 → 45 → 50).

### Out-of-domain reconstruction

원논문 Table 2. AUC@1/5 cm for human body reconstruction (4D-DRESS) and AUC@1/5 mm for surgical scene reconstruction (MV-dVRK). 24 sequences each, 4–12 input views per sequence.

| Method             | 4D-DRESS | MV-dVRK |
| ------------------ | -------- | ------- |
| VGGT               | 10/45    | 8/33    |
| VGGT + Ours        | 66/77    | 45/61   |
| Pi3                | 8/50     | 18/51   |
| Pi3 + Ours         | 63/80    | 40/67   |
| MapAnything        | 2/12     | 3/13    |
| MapAnything + Ours | 42/52    | 35/47   |
| MAtCha             | 48/68    | 37/62   |
| MAtCha + Ours      | 62/75    | 50/67   |
| MASt3R-SfM         | 54/71    | 39/62   |
| MASt3R-SfM + Ours  | 64/75    | 49/66   |

The largest gains are at the tight AUC@1 threshold, which the paper reads as evidence of improved fine-grained geometric accuracy.

### Geometry conditions vs geometry-grounded models

원논문 Table 3. Points AUC@5/10 cm on the ETH3D 8-view test set. Column-wise the comparison isolates the SfM guidance quality; row-wise it isolates the refinement architecture.

| Method      | X_s from MASt3R-SfM | X_s from our SfM    |
| ----------- | ------------------- | ------------------- |
| Murre       | 9/23                | 26/40 (+17/+17)     |
| OMNI-DC     | 25/44               | 31/44 (+6/+0)       |
| POW3R       | 13/29               | 32/45 (+19/+16)     |
| MapAnything | 13/32               | 27/40 (+14/+8)      |
| VGGT + GGPT | **36/50**           | **47/61 (+11/+11)** |

Both conclusions hold: the improved SfM is a stronger geometric signal for every model, and given identical guidance the 3D point transformer beats all the 2D depth-completion alternatives.

### Ablations

원논문 Table 7. AUC@5/10 cm on ScanNet++ and ETH3D 8-view splits, AUC@1/5 cm on 4D-DRESS.

| Variant                         | SNt++     | ETH3D     | 4DDS.     |
| ------------------------------- | --------- | --------- | --------- |
| VGGT (unrefined)                | 19/32     | 23/36     | 10/45     |
| **(a) Refinement architecture** |           |           |           |
| 2D: X_s → VGGT                  | **55/70** | 25/40     | 12/52     |
| 2D: X_s → MapAnything           | 39/57     | 11/21     | 5/34      |
| 3D: Minkowski                   | 39/53     | 47/60     | 63/73     |
| 3D: PTv3 (Ours)                 | 45/60     | **47/61** | **66/77** |
| **(b) Input encodings**         |           |           |           |
| w/o X_s                         | 21/35     | 20/34     | 13/42     |
| w/o X_d→s                       | 24/41     | 24/41     | 14/47     |
| w/o z_s                         | 42/57     | 44/58     | 56/72     |
| Full model                      | **45/60** | **47/61** | **66/77** |

The 2D X_s → VGGT variant actually wins the within-domain ScanNet++ column (55/70 vs 45/60) but collapses on cross-domain ETH3D (25/40) and out-of-domain 4D-DRESS (12/52) — a clean illustration that the 3D formulation buys generalisation, not in-domain fit. Removing the guidance point cloud `X_s` entirely is catastrophic and drops the model roughly to the unrefined baseline.

원논문 Table 7(c). Patch size sweep; `r = 0.2` (the default half-width setting) is best on all three.

| Patch size | SNt++     | ETH3D     | 4DDS.     |
| ---------- | --------- | --------- | --------- |
| r=0.05     | 30/44     | 37/50     | 30/56     |
| r=0.1      | 39/53     | 43/57     | 60/72     |
| r=0.2      | **45/60** | **47/61** | **66/77** |
| r=0.6      | 40/55     | 38/53     | 64/74     |
| r=1.0      | 41/56     | 40/56     | 63/75     |

### SfM pipeline evaluation

The direct SfM comparison (camera AUC@5°, partial point map Accuracy/Completeness by Chamfer distance, and runtime, across 4/8/16-view setups on ETH3D) appears only as Figure 4 with no printed values, so no numbers are transcribed. The stated findings are that the pipeline beats state-of-the-art global SfM methods on camera pose and points accuracy, attains competitive completeness against MASt3R-SfM's dense-grid optimisation without sacrificing accuracy, and has the lowest runtime at every input view count.

### DLT vs COLMAP triangulation

The supplementary ablation reports that direct linear triangulation is orders of magnitude faster than the LO-RANSAC + non-linear refinement pipeline in pycolmap — because DLT runs as CUDA tensor operations — while attaining comparable and in many cases superior accuracy and completeness. The paper attributes this robustness to prefiltering correspondences by cycle consistency and matching confidence. The ablation also finds `n_BA = 512` suffices on ETH3D despite the default 2048.

## 💡 Insights & Impact

### Refine in 3D, not in 2D

The central architectural claim is that prior geometry-conditioned methods operate on 2D image tokens and fuse sparse geometry channel-wise, so their receptive fields are defined by pixel coordinates. GGPT runs attention on both point clouds directly in the global 3D coordinate space, where spatial proximity defines the neighbourhood. Points that are adjacent in 3D but distant in any single image — precisely the configuration where multi-view inconsistency shows up as multi-layer artifacts — can then interact. The ablation makes the trade-off legible: the 2D variant fits the training domain better but does not transfer.

### A modular decomposition

GGPT is not a reconstruction model but a refinement module, and the results treat it as such: five different upstream predictors, two different SfM guidance sources, all with one set of frozen weights trained on a single dataset with a single upstream model. That the same weights improve MAtCha and MASt3R-SfM — hybrid forward-optimisation methods, not feed-forward ones — suggests the correction it learns is about _geometric inconsistency in general_ rather than the idiosyncrasies of VGGT.

### Fixing the more-views-is-worse pathology

The unrefined baselines frequently degrade as views are added, which is the opposite of what more observations should do and points at accumulating multi-view inconsistency. After refinement the trend reverses. This is arguably the strongest evidence that explicit sparse geometry is supplying something the dense predictors genuinely lack, rather than merely smoothing their output.

### Efficiency framing

At 53M parameters against the ~300M of comparable 2D transformers, and with the runtime dominated by dense matching rather than by the proposed BA, DLT, and GGPT stages, the module is cheap relative to what it is bolted onto.

## 🔗 Related Work

- [VGGT](./vggt.md) — the dense predictor GGPT is trained on and improves most dramatically.
- [pi3](./pi3.md) — concurrent predictor; already strong in-domain on ScanNet++, refined mainly cross-domain.
- [MapAnything](./mapanything.md) — refined as an upstream predictor and also compared as a 2D geometry-conditioned baseline.
- [MASt3R-SfM](../foundation/mast3r-sfm.md) — the prior SfM whose guidance `X_s` is the comparison point in Table 3.
- [Pow3R](./pow3r.md) — 2D geometry-conditioned baseline (POW3R) in Table 3.
- [DUSt3R](../foundation/dust3r.md) and [MASt3R](../foundation/mast3r.md) — the lineage that established dense feed-forward point map prediction.

## 📚 Key Takeaways

1. **Sparse-but-correct beats dense-but-drifting, when you can fuse them.** Triangulated SfM points propagate their geometric accuracy into dense feed-forward predictions through residual corrections.
2. **The fusion must happen in 3D.** Attention over 3D spatial neighbourhoods generalises across domains where 2D-token fusion overfits — the 2D variant wins ScanNet++ (55/70) and collapses on 4D-DRESS (12/52).
3. **One set of weights, five upstream models.** Trained only on ScanNet++ with VGGT, GGPT improves Pi3, MapAnything, MAtCha, and MASt3R-SfM, including on surgical and human-body data far from any training distribution.
4. **Both halves contribute independently.** Better SfM guidance helps every geometry-conditioned model; given identical guidance, the 3D point transformer beats every 2D alternative.
5. **DLT is enough.** Direct linear triangulation with well-prefiltered correspondences matches or beats RANSAC + non-linear refinement, orders of magnitude faster, because it runs as CUDA tensor ops.

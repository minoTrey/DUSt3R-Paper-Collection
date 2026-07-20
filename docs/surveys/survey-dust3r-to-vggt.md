# Survey-DUSt3R-to-VGGT: Review of Feed-forward 3D Reconstruction (JAICS 2025)

## 📋 Overview

- **Authors**: Wei Zhang, Yihang Wu, Songhua Li, Wenjie Ma, Xin Ma, Qiang Li, Qi Wang
- **Institution**: School of Artificial Intelligence, Optics and Electronics (iOPEN), Northwestern Polytechnical University; School of Computer Science, Northwestern Polytechnical University
- **Venue**: JAICS 2025
- **Note**: JAICS is a low-profile journal, so the venue carries little signal about peer-review rigour. Several factual characterisations in this review are imprecise (see Insights below), and the metric arrow directions in its own results table are internally inconsistent. Treat it as a readable roadmap rather than an authoritative reference.
- **Links**: [Paper](https://arxiv.org/abs/2507.08448)
- **Verification**: LIKELY (2026-07-20)
- **TL;DR**: A literature review of the feed-forward 3D reconstruction paradigm from DUSt3R onward, organised around three technical pillars, a contrast with the classical SfM+MVS pipeline, and an inventory of datasets and metrics.

## 🎯 Key Contributions

1. **A three-pillar decomposition** of the feed-forward architecture: learning robust dense correspondences, joint inference of geometry and pose, and scaling from two-view to multi-view.
2. **An explicit contrast with classical and modular pipelines** (COLMAP, MVSNet) across workflow, core engine, robustness, ease of use, computation mode, and bottleneck.
3. **Inventories of training datasets and evaluation protocols**, with a consolidated DTU results table spanning both traditional and feed-forward models.
4. **A challenges-and-futures agenda** covering scalability, dynamic scenes, uncertainty quantification, out-of-distribution robustness, and integration with neural rendering and language models.

## 🔧 Technical Details

This is a review, not a method paper; the methodology is a structured survey of the literature organised as follows.

### Pillar 1 — Learning robust dense correspondences

Traditional methods rely on sparse hand-crafted features (SIFT) that fail in texture-poor regions and under large viewpoint change. Feed-forward models instead follow LoFTR's lead: a CNN or ViT backbone extracts multi-scale features, which are flattened into token sequences and processed by stacked self-attention (intra-image context) and cross-attention (inter-image exchange) layers, computing pixel-wise matching within a global receptive field. The review's framing is that the output of the matching stage has shifted from discrete inlier/outlier pairs to a dense probabilistic confidence map.

### Pillar 2 — Joint inference of geometry and pose

Where a classical pipeline needs RANSAC to solve for the essential or fundamental matrix, feed-forward models decode geometry directly from the dense correspondence map. The review reads DUSt3R's design as "pose-from-alignment": rather than regressing R and t, it predicts per-pixel 3D coordinates in a normalised camera frame, and a differentiable Kabsch/Umeyama layer recovers the rigid transformation aligning the predicted point cloud with its counterpart. Pose and geometry thereby mutually supervise each other.

### Pillar 3 — Scaling to multi-view

The review describes the dominant strategy as two-stage — run the two-view model over image pairs, then globally aggregate — and surveys pose-graph optimisation, sequential/SLAM-style processing with keyframing and loop closure, and true N-view transformer architectures that bypass pairwise aggregation at higher GPU memory cost.

### Comparison with classical MVS

원논문 Table 2. The review's summary of three paradigms:

| Aspect           | Traditional (COLMAP)                       | Modular Deep Learning (MVSNet)      | Feed-forward (DUSt3R)               |
| ---------------- | ------------------------------------------ | ----------------------------------- | ----------------------------------- |
| Workflow         | Multi-stage, sequential, iterative         | Modular, still iterative            | End-to-end, feed-forward            |
| Core Engine      | Geometric optimization (BA)                | Learned matcher + geometric opt.    | End-to-end network (Transformer)    |
| Robustness       | Sensitive to texture, baseline, init       | Improved matching, fragile SfM core | High robustness via learned priors  |
| Ease of Use      | Requires expertise, complex tuning         | Requires toolchain integration      | "Black-box" model, direct inference |
| Computation Mode | Mixed CPU (BA) & GPU (MVS)                 | Mixed CPU (SfM) & GPU (MVS)         | Fully GPU-intensive                 |
| Bottleneck       | Geometric failures, optimization fragility | Iterative and fragile SfM core      | GPU memory, data scale & diversity  |

## 📊 Results

This section reports what the review compiles, not results it produces.

### DTU evaluation

원논문 Table 4. Metric names and arrow directions are transcribed exactly as printed. Note that `τ↓` is inconsistent with the review's own text, which defines τ as an inlier ratio — an inconsistency in the source. Parenthesised MVSNet values are as printed; `/` denotes an unreported cell.

| Type         | Model            | Known GT camera | rel↓  | τ↓     | time (s)↓ |
| ------------ | ---------------- | --------------- | ----- | ------ | --------- |
| Traditional  | COLMAP           | ✓               | 0.7   | 96.5   | ~3 min    |
| Traditional  | MVSNet           | ✓               | (1.8) | (86.0) | 0.07      |
| Traditional  | MVSNet Inv.Depth | ✓               | (1.8) | (86.7) | 0.32      |
| Feed-forward | DUSt3R           | ✗               | 3.3   | 69.9   | 0.05      |
| Feed-forward | Test3R           | ✗               | 2.0   | 84.1   | /         |
| Feed-forward | PE3R             | ✗               | 3.2   | 69.1   | /         |
| Feed-forward | Spann3R          | ✗               | 3.5   | 65.2   | 0.32      |
| Feed-forward | MUSt3R           | ✗               | 4.6   | 63.1   | 0.19      |
| Feed-forward | Pow3R            | ✗               | 3.0   | 74.3   | /         |

원논문 Table 4, 3D reconstruction columns. Acc. / Comp. / Overall in mm; Overall is their average, equivalent to Chamfer distance.

| Type         | Model         | Known GT camera | Acc.↓ | Comp.↓ | Overall↓ |
| ------------ | ------------- | --------------- | ----- | ------ | -------- |
| Traditional  | Gipuma        | ✓               | 0.283 | 0.873  | 0.578    |
| Traditional  | MVSNet        | ✓               | 0.396 | 0.527  | 0.462    |
| Traditional  | CIDER         | ✓               | 0.417 | 0.437  | 0.427    |
| Traditional  | PatchmatchNet | ✓               | 0.427 | 0.377  | 0.417    |
| Traditional  | GeoMVSNet     | ✓               | 0.331 | 0.259  | 0.295    |
| Feed-forward | DUSt3R        | ✗               | 2.667 | 0.805  | 1.741    |
| Feed-forward | VGGT          | ✗               | 0.389 | 0.374  | 0.382    |
| Feed-forward | MASt3R        | ✗               | 0.403 | 0.344  | 0.374    |
| Feed-forward | Pow3R         | ✗               | 2.116 | 1.370  | 1.743    |

The most informative reading of this table is the "Known GT camera" column. Traditional models are handed ground-truth cameras; feed-forward models are not, and MASt3R and VGGT nonetheless land in the same Overall range as GeoMVSNet and PatchmatchNet.

### Training dataset inventory

원논문 Table 3, selected rows. The review catalogues 16 datasets with year, size, and category.

| Dataset        | Year | Size / Content                                  | Category          |
| -------------- | ---- | ----------------------------------------------- | ----------------- |
| MegaDepth      | 2018 | 130K+ images, 200+ scenes                       | Outdoor           |
| ARKitScenes    | 2021 | 5,048 RGB-D sequences from 1,661 scenes         | Indoor            |
| ScanNet++      | 2023 | 460 scenes, 280K DSLR images, 3.7M+ iPhone RGBD | Indoor            |
| CO3D-v2        | 2021 | 1.5 million frames from ~19,000 videos          | Object-centric    |
| Waymo          | 2020 | 1,150 scenes                                    | Outdoor, Driving  |
| DL3DV          | 2022 | 10,510 scenes                                   | Outdoor           |
| HyperSim       | 2021 | 774 scenes (~100K images) from 461 layouts      | Indoor, Synthetic |
| Habitat (MP3D) | 2019 | 1,000 scenes                                    | Indoor            |

### Model summary table

원논문 Table 1 summarises eleven models by contribution, input, output, and primary application: DUSt3R, MASt3R, Align3R, Pow3R, SLAM3R, Fast3R, Driv3R, MonST3R, MV-DUSt3R+, and Reloc3r. Several of these characterisations do not match the primary papers — see Insights.

## 💡 Insights & Impact

### What the review gets right

The three-pillar decomposition is a genuinely useful mental model, and the paradigm framing — from "iterative optimization" to "end-to-end inference," with the SfM+MVS workflow effectively distilled into a single network — is the correct high-level story. The Table 2 comparison is a clean articulation of _where the bottleneck moved_: from geometric failures and optimisation fragility to GPU memory and data scale and diversity. The DTU table's "Known GT camera" column quietly makes the strongest point in the paper.

### Where it should not be trusted

Several Table 1 characterisations conflict with the primary sources:

- **Fast3R** is listed as taking an _image pair_ and achieving speed through "lightweight architectural design and knowledge distillation." Fast3R's actual contribution is parallel multi-view processing of many images at once; it is not a pairwise method and does not rely on distillation.
- **Pow3R** is described as extending pose-graph optimisation with point cloud registration. Pow3R's contribution is conditioning DUSt3R on optional camera and depth priors.
- **Spann3R** is described as investigating sparse attention to cut Transformer cost. Spann3R's contribution is an external spatial memory for incremental reconstruction.
- **Align3R** is credited with confidence-weighted pose graph optimisation for multi-view aggregation; Align3R is a dynamic-scene method aligning monocular depth estimates.

The results table also prints `τ↓` for a metric the body text defines as an inlier ratio, which would be higher-better. These are the kinds of errors that a rigorous review process would normally catch, and they are consistent with the venue caveat noted in the Overview.

### Coverage and timing

The review's title promises coverage "from DUSt3R to VGGT," and VGGT appears in the DTU table, but the technical sections give it little independent treatment relative to its significance — it is mentioned mostly alongside MASt3R as improving multi-scale matching. Fast-moving subareas that had already emerged by the review's date — pointmap-free formulations, streaming and memory-based online models, and Gaussian-splatting outputs — are largely absent. Readers wanting current coverage of those directions will need the primary papers.

### Useful takeaways that survive

The future-work agenda is reasonable and holds up: quadratic attention complexity as the fundamental scalability bottleneck, uncertainty quantification as underexplored and safety-critical, hybrid feed-forward-plus-differentiable-optimisation architectures, direct output of NeRF or 3DGS representations, and the eventual convergence with language models into "geometrically-aware LLMs." Each of these has since attracted substantial work.

## 🔗 Related Work

Primary papers for the models this review surveys, where the collection has entries:

- [DUSt3R](../foundation/dust3r.md) and [MASt3R](../foundation/mast3r.md) — the origin of the paradigm.
- [VGGT](../reconstruction/vggt.md) — the review's titular endpoint.
- [Spann3R](../reconstruction/spann3r.md) — spatial memory, not sparse attention.
- [Fast3R](../reconstruction/fast3r.md) — parallel multi-view, not pairwise.
- [Pow3R](../reconstruction/pow3r.md) — prior conditioning, not pose-graph optimisation.
- [MonST3R](../dynamic/monst3r.md) — dynamic scenes with monocular depth priors.
- [MUSt3R](../reconstruction/must3r.md), [CUT3R](../dynamic/cut3r.md) — memory-based and recurrent extensions.
- [SLAM3R](../reconstruction/slam3r.md), [Reloc3r](../pose/reloc3r.md), [PE3R](../understanding/pe3r.md), [Test3R](../reconstruction/test3r.md), [Regist3R](../reconstruction/regist3r.md), [MV-DUSt3R+](../reconstruction/mv-dust3r-plus.md).

## 📚 Key Takeaways

1. **A serviceable roadmap, not a reference.** The three-pillar structure and the classical-vs-feed-forward comparison are worth reading; the per-model claims in Table 1 need verification against primary sources.
2. **The bottleneck moved, it did not vanish.** Classical pipelines fail on geometry and optimisation fragility; feed-forward models fail on GPU memory, data scale, and data diversity.
3. **Feed-forward models compete without ground-truth cameras.** In the compiled DTU table, MASt3R (0.374 Overall↓) and VGGT (0.382 Overall↓) sit alongside traditional methods that are given GT cameras.
4. **The identified open problems held up**: quadratic scalability, dynamic scenes, uncertainty quantification, and OOD robustness have all since driven substantial follow-up work.
5. **Venue caveat applies.** JAICS is low-profile, and the paper contains factual and metric-direction errors that peer review would ordinarily have removed.

# IGGT: Instance-Grounded Geometry Transformer for Semantic 3D Reconstruction (ICLR 2026)

![iggt — architecture](https://arxiv.org/html/2510.22706/x2.png)

_Data Curation Pipeline (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Hao Li, Zhengyu Zou, Fangfu Liu, Xuanyang Zhang, Fangzhou Hong, Yukang Cao, Yushi Lan, Manyuan Zhang, Gang Yu, Dingwen Zhang, Ziwei Liu
- **Institution**: NWPU, S-Lab NTU, StepFun Inc., THU, MMLab CUHK
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.22706) | [Code](https://github.com/lifuguan/IGGT_official)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A VGGT-scale unified transformer with a geometry head and an instance head, trained with 3D-consistent contrastive supervision so that instance clustering and pointmap regression reinforce each other — and using the resulting instance masks, rather than a baked-in language embedding, as the plug-and-play interface to any VLM.

## 🎯 Key Contributions

1. **Instance grounding instead of language alignment**: Rather than aligning 3D features to a fixed VLM embedding (LSeg-style), IGGT learns instance-discriminative features and uses masks as the bridge to _any_ VLM or LMM.
2. **3D-Consistent Contrastive Learning**: A multi-view contrastive loss pulls features of the same 3D instance together across views and pushes different instances apart, using only 2D visual input at inference.
3. **Cross-Modal Fusion Block**: Sliding-window cross-attention lets the instance head query fine-grained geometric features (Q from instance latent, K/V from geometry latent), sharpening object boundaries while avoiding the quadratic cost of global attention.
4. **InsScene-15K dataset**: 15K scenes / 200M images with RGB, poses, depth, and 3D-consistent instance masks, built by a SAM2-driven curation pipeline covering synthetic, video-captured, and RGBD-scan sources.
5. **Instance-Grounded Scene Understanding**: HDBSCAN clustering of the instance features yields 3D-consistent masks that drive spatial tracking, open-vocabulary segmentation (via CLIP / OpenSeg / LSeg) and QA scene grounding (via Qwen2.5-VL).

## 🔧 Technical Details

### Formulation

```text
F : {I_i}_{i=1..N}  ↦  (t_i, D_i, P_i, S_i)_{i=1..N}
```

camera parameters, depth map, point map, and a 3D-consistent instance-level feature map per view.

### Large Unified Transformer

Following VGGT, a **1B parameter** backbone. Pretrained DINOv2 extracts patch tokens; a learnable camera token is concatenated per view to support arbitrary multi-view input while maintaining permutation equivariance; **24 blocks** of intra-view self-attention and global-view cross-attention produce the unified tokens.

### Two Heads

- **Geometry Head** — inherited from VGGT: camera predictor, depth predictor, point predictor, the latter two DPT-like with progressive upsampling and multi-scale fusion, producing 4 feature levels.
- **Instance Head** — also DPT-like, producing 4 levels of dense instance features.

### Cross-Modal Fusion

```text
F̂ins_(l) = Fins_(l) + F_win(Q = Fins_(l), K = Fpt_(l), V = Fpt_(l))
```

Refined instance features across all levels are concatenated and mapped by a 3×3 convolution to an **8-dimensional** instance feature map `O_ins ∈ R^{N×8×H×W}`.

### Multi-View Contrastive Loss

```text
L_mvc = λ_pull · Σ_{m(p_i)=m(p_j)} d(f_pi, f_pj)
      + λ_push · Σ_{m(p_i)≠m(p_j)} max(0, M − d(f_pi, f_pj))
```

with `d` the L2 distance between normalized features and `M` a margin. Total objective:

```text
L_overall = L_pose + L_depth + L_pmap + L_mvc
```

where the three geometry terms follow VGGT's training paradigm.

### Data Curation

- **Synthetic** (Aria, Infinigen): RGB, depth, pose, and object masks rendered directly; masks used without post-processing.
- **Video-captured** (RE10K): SAM proposals on the first frame, propagated by SAM2; a new keyframe is designated whenever unsegmented area grows, and a final bi-directional propagation pass enforces temporal consistency.
- **RGBD-scan** (ScanNet++): coarse 3D annotations projected to 2D for consistent IDs, then SAM2 proposals matched to those IDs and merged, iterating until all regions are covered.

### Downstream Strategy

HDBSCAN clusters the multi-view instance features into K clusters; re-projecting cluster labels gives 3D-consistent 2D masks. For open-vocabulary segmentation, VLM features are aggregated within each mask by average mask pooling. For QA grounding, the instance region is highlighted in red across views and an LMM is asked yes/no consistency questions, with positive responses concatenated into the final mask.

## 📊 Results

### ScanNet

원논문 Table 1. `SAM2*` is a modified SAM2 supporting dense multi-view segmentation; `SpaTracker+SAM` uses tracked points as SAM prompts. Empty cells mean the method does not support that capability. The open-vocabulary columns for "Ours" here correspond to the LSeg pairing (see the VLM ablation below).

| Model             | T-mIoU ↑ | T-SR ↑ | Abs. Rel ↓ | τ ↑   | 2D mIoU ↑ | 2D mAcc ↑ | 3D mIoU ↑ |
| ----------------- | -------- | ------ | ---------- | ----- | --------- | --------- | --------- |
| LSeg              | -        | -      | -          | -     | 58.11     | 65.76     | -         |
| OpenSeg           | -        | -      | -          | -     | 42.33     | 68.06     | -         |
| NeRF-DFF          | -        | -      | 7.99       | 36.53 | 45.40     | 65.29     | 12.29     |
| Feature-3DGS      | -        | -      | 6.48       | 41.63 | 57.69     | 63.26     | 23.42     |
| LSM (2 Views)     | -        | -      | 4.22       | 58.65 | 53.07     | 53.86     | -         |
| LSM (Multi-Views) | -        | -      | 3.17       | 64.81 | 53.40     | 59.50     | 35.37     |
| SpaTracker+SAM    | 26.43    | 38.57  | -          | -     | -         | -         | -         |
| SAM2\*            | 53.74    | 71.25  | -          | -     | -         | -         | -         |
| VGGT              | -        | -      | **1.84**   | 83.60 | -         | -         | -         |
| **Ours**          | 69.41    | 98.66  | 1.90       | 83.71 | 60.46     | 81.84     | 39.68     |

Note the honest comparison on geometry: on ScanNet, VGGT has the better Abs. Rel (1.84 vs 1.90) and IGGT the better τ (83.71 vs 83.60). The paper's own wording is that IGGT is "on par with VGGT on ScanNet".

### ScanNet++

원논문 Table 2. Here the "Ours" open-vocabulary numbers correspond to the OpenSeg pairing.

| Model             | T-mIoU ↑ | T-SR ↑ | Abs. Rel ↓ | τ ↑   | 2D mIoU ↑ | 2D mAcc ↑ | 3D mIoU ↑ |
| ----------------- | -------- | ------ | ---------- | ----- | --------- | --------- | --------- |
| LSeg              | -        | -      | -          | -     | 22.61     | 34.42     | -         |
| OpenSeg           | -        | -      | -          | -     | 13.92     | 48.13     | -         |
| Feature-3DGS      | -        | -      | 5.92       | 41.64 | 22.47     | 33.14     | 10.59     |
| LSM (2 Views)     | -        | -      | 4.22       | 74.02 | 17.76     | 26.95     | -         |
| LSM (Multi-Views) | -        | -      | 2.96       | 83.28 | 17.88     | 27.84     | 15.17     |
| SpaTracker+SAM    | 16.15    | 23.68  | -          | -     | -         | -         | -         |
| SAM2\*            | 44.16    | 57.89  | -          | -     | -         | -         | -         |
| VGGT              | -        | -      | 2.75       | 85.41 | -         | -         | -         |
| **Ours**          | 73.02    | 98.90  | **2.61**   | 85.66 | 31.31     | 70.78     | 20.14     |

The paper states that on ScanNet++ IGGT outperforms VGGT "by 0.14 in Abs. Rel and 0.25 in τ", and improves 3D mIoU over previous approaches by **4.31%** (ScanNet) and **4.97%** (ScanNet++) — consistent with the LSM (Multi-Views) rows in both tables.

### VLM Integration Ablation

원논문 Table 3.

| Method          | ScanNet mIoU ↑ | ScanNet mAcc ↑ | ScanNet++ mIoU ↑ | ScanNet++ mAcc ↑ |
| --------------- | -------------- | -------------- | ---------------- | ---------------- |
| Ours w/ LSeg    | **60.46**      | **81.84**      | 22.72            | 63.56            |
| Ours w/ CLIP    | 49.36          | 62.68          | 21.52            | 61.36            |
| Ours w/ OpenSeg | 58.12          | 78.75          | **31.31**        | **70.78**        |

No single VLM wins everywhere. The paper's reading: LSeg and OpenSeg, with better global context representation, handle background classes (e.g. cabinet) better; CLIP, with stronger text alignment, does better on unusual categories such as "DALL-E" and "Ottolenghi" (Fig. 10). This is precisely the argument for decoupling the geometry model from any one VLM.

### Cross-Modal Fusion Ablation

Fig. 11 shows the training curves with and without the cross-modal fusion module, plus PCA visualizations of the chair's edges. **These are plots and images with no printed numbers** — the reported observation is that without fusion the instance head struggles to capture high-resolution geometric information and converges more slowly, with visibly blunter object boundaries. No quantitative delta is given.

### Evaluation Protocol

10 scenes are randomly selected from each dataset, with 8–10 images sampled per scene to maximize coverage while retaining overlap. Tracking uses Temporal mIoU (segmentation accuracy of the same object across views) and Temporal Success Rate (whether the object is tracked in every view). Reconstruction follows LSM and VGGT using Absolute Relative Error and Inlier Ratio τ at threshold 1.03. Ground-truth tracking labels for a subset of objects were manually annotated by the authors.

## 💡 Insights & Impact

### Why Instance Masks Are a Better Interface Than Language Features

The paper lists three concrete failures of geometry↔VLM feature alignment:

1. Forcing low-level geometric signal into alignment with high-level textual concepts **over-smooths** the representation, degrading high-frequency detail and multi-view consistency.
2. Tight coupling caps performance at the base model (e.g. LSeg) and blocks adoption of stronger models (CLIP, SigLIP).
3. VLMs trained on 2D image–text pairs cannot distinguish **two objects of the same category** — fatal for instance tracking under large viewpoint change.

Table 3 is the empirical payoff of avoiding this: the same geometry backbone can be re-paired with a different VLM and gain 8+ mIoU on ScanNet++ without retraining.

### Tracking Is Where the Gap Is Largest

T-SR of 98.66 / 98.90 against SAM2\*'s 71.25 / 57.89 is the widest margin in the paper. The stated reason is that 3D-grounded instance features survive large camera motion where 2D video propagation loses the target. T-mIoU above 60 versus baselines below 30 supports the same story.

### Mutual Enhancement Is Modest on Geometry

The claim that semantics improve geometry is supported only weakly by the numbers: IGGT is slightly behind VGGT on ScanNet Abs. Rel and ahead by 0.14 on ScanNet++. The understanding side, not the geometry side, is where the joint training clearly pays.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — supplies the backbone design, the geometry head, and the geometry loss recipe; also the geometry baseline in both tables.
- [Large Spatial Model](./largespatialmodel.md) — the LSM baseline; the language-aligned feed-forward approach IGGT argues against.
- [DUSt3R](../foundation/dust3r.md) — cited as the origin of direct pointmap regression and, alongside Panst3R, as a feed-forward attempt that keeps geometry and semantics decoupled.
- [PE3R](./pe3r.md), [MEt3R](./met3r.md) — neighbouring work on perception and consistency in the understanding category.
- [Depth Anything 3](../reconstruction/depth-anything-3.md), [MapAnything](../reconstruction/mapanything.md) — contemporaneous large geometry models without the instance-grounding component.

## 📚 Key Takeaways

1. **Masks, not embeddings, are the right handoff point.** Grounding on instances keeps the geometry model VLM-agnostic and lets it inherit future VLM improvements for free — Table 3 shows the swap is worth double-digit mIoU on ScanNet++.
2. **Instance-level 3D consistency solves tracking under large motion.** Near-99% T-SR versus 57–71% for SAM2\* is the paper's clearest result.
3. **Cross-modal fusion is what makes the instance head spatially sharp**, but the supporting evidence is qualitative (training curves and PCA visualizations), not tabulated.
4. **Joint training does not obviously improve geometry.** IGGT matches VGGT rather than beating it on ScanNet; the gain is on the understanding side.
5. **The dataset may outlast the model.** InsScene-15K (15K scenes, 200M images, 3D-consistent instance masks from a SAM2-driven pipeline) addresses a genuine scarcity of instance-level geometry-semantics annotation.

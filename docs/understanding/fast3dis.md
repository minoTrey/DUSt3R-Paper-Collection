# FAST3DIS: Feed-forward Anchored Scene Transformer for 3D Instance Segmentation (arXiv preprint 2026-03)

![fast3dis — architecture](https://arxiv.org/html/2603.25993v1/figs/overview.jpg)

_Overview of the FAST3DIS framework (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Changyang Li, Xueqing Huang, Shin-Fang Chng, Huangying Zhan, Qingan Yan, Yi Xu
- **Institution**: Goertek Alpha Labs
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.25993)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An end-to-end multi-view 3D instance segmentation framework that eliminates post-hoc clustering — using a LoRA-adapted frozen Depth Anything V3 backbone, a learned 3D anchor generator, and anchor-sampling cross-attention that projects 3D queries into multi-view feature maps, delivering competitive accuracy with orders-of-magnitude faster inference than clustering-based methods.

## 🎯 Key Contributions

1. **3D-anchored cross-attention for dense segmentation**: Formulates object queries as dynamic 3D anchors that probe continuous geometric space; projecting anchors into multi-view feature maps to sample local context reduces cross-attention complexity to scale linearly with queries and views (spatial complexity O(HW) → O(1)) while enforcing multi-view geometric consistency.
2. **Explicit feature and spatial regularization**: A dual-level strategy — a multi-view contrastive loss pulling same-instance representations together across views, and a dynamically scheduled overlap penalty preventing distinct queries from claiming the same region.
3. **Optimized inference and scalability**: By bypassing test-time heuristics and clustering, it delivers large inference speedups and marginal added VRAM over the frozen backbone, scaling to large multi-view inputs.

## 🔧 Technical Details

### Dual-Pass LoRA-Adapted Backbone

- The frozen Depth Anything V3 (DA3) backbone is run in two passes per batch: a **geometry pass** (LoRA disabled) extracting dense metric depth + intrinsics/extrinsics, and a **feature pass** (LoRA enabled) extracting multi-scale view features while preserving DA3's 3D structural knowledge.

### Geometry-Injected Pixel Decoder & Anchor Decoder

- A DPT-style pixel decoder injects the unprojected 3D point map into the deepest feature to produce 3D-aware feature pyramids and high-resolution mask features (regularized by a geometric consistency loss).
- A learned 3D anchor generator produces Nq learnable 3D anchors (shifted by an MLP conditioned on global scene context) and Nq content queries.
- The transformer decoder alternates query self-attention (with Fourier 3D positional encoding), anchor-sampling cross-attention (projecting each 3D anchor into each view to bilinearly sample local features), and iterative anchor refinement.

### Training Objectives

- Hungarian bipartite matching (class-agnostic), Sigmoid Focal (Lcls), BCE (Lbce), Dice (Ldice), a point-level supervised contrastive loss (Lgeo), and a confidence-weighted dynamically scheduled overlap penalty (Loverlap) that warms up then decays over training.
- Trained only on the Aria Synthetic Environments dataset (40% of scenes sampled), Nq = 80 anchors/queries, input long-edge 504 px, on a single NVIDIA H200 (144 GB). Evaluated zero-shot on ScanNet V2, ScanNet++, Replica.

## 📊 Results

### 3D Instance Segmentation (class-agnostic AP)

원논문 Table 1. Average Precision at IoU 25%/50% and overall AP (averaged 50–95%). Higher is better.

| Method       | SN V2 AP25 | SN V2 AP50 | SN V2 AP | SN++ AP25 | SN++ AP50 | SN++ AP | Replica AP25 | Replica AP50 | Replica AP |
| ------------ | ---------- | ---------- | -------- | --------- | --------- | ------- | ------------ | ------------ | ---------- |
| HDBSCAN      | 5.6        | 0.6        | 0.2      | 2.4       | 0.6       | 0.2     | 2.3          | 0.1          | 0.0        |
| SAM3D        | 23.3       | 8.0        | 2.4      | 19.2      | 7.0       | 2.2     | 28.3         | 16.1         | 7.1        |
| Segment3D    | 17.2       | 7.2        | 2.5      | 17.3      | 8.1       | 3.1     | 15.8         | 9.3          | 4.0        |
| PanSt3R      | 22.5       | 3.5        | 0.8      | 21.7      | 6.2       | 1.7     | 20.7         | 6.2          | 1.7        |
| IGGT         | 28.7       | 11.2       | 2.8      | 10.0      | 2.2       | 0.6     | 15.2         | 3.9          | 1.1        |
| **FAST3DIS** | 31.6       | 9.6        | 3.8      | 14.7      | 3.5       | 1.0     | 30.3         | 13.8         | 5.1        |

FAST3DIS outperforms its primary baseline IGGT on ScanNet V2, ScanNet++ and Replica overall AP, but does not win every column — e.g. IGGT scores higher AP50 on ScanNet V2 (11.2 vs 9.6), and SAM3D leads on Replica AP50 (16.1 vs 13.8). Both FAST3DIS and IGGT degrade on the exhaustively annotated ScanNet++ (Nq = 80 queries miss objects in scenes with 100–200 instances; IGGT under-segments to ~20–30 instances/scene).

### Efficiency vs. IGGT

원논문 §4.2 and Figure 2 (log-scale timing). Inference time to process a scene:

- At 30 input views: FAST3DIS **7.9 s** vs IGGT **910.8 s** (GPU HDBSCAN) / **1141.5 s** (CPU) — over a **115× speedup**.
- At 50 input views: FAST3DIS **18.4 s** vs IGGT **~4663.3 s** (CPU; GPU fails with OOM) — a **250× acceleration**.
- FAST3DIS processes up to 350 images (**682.7 s**) in a single forward pass without hitting hardware limits.

## 💡 Insights & Impact

- **Clustering is the bottleneck, not the backbone**: IGGT uses efficient geometric backbones but its post-hoc HDBSCAN clustering scales quadratically (O(N²)) with points, triggering OOM on GPU and extreme latency on CPU; FAST3DIS's set-prediction formulation removes this.
- **Spatial regularization is essential for class-agnostic segmentation**: Without the contrastive loss and overlap penalty, the model degenerates to a multi-view Mask2Former with "query hijacking" and blurry boundaries; a static overlap penalty instead creates artificial background gaps, motivating the dynamic schedule.
- **Sharper small-object and adjacent-object separation**: 3D anchors competing for exclusive spatial occupancy better isolate small objects on large supports and separate touching objects than density-based clustering.

## 🔗 Related Work

- **[Depth Anything 3](../reconstruction/depth-anything-3.md)**: The frozen geometric backbone (DA3) that FAST3DIS LoRA-adapts.
- **[IGGT](iggt.md)**: The post-hoc clustering class-agnostic 3D instance segmentation baseline FAST3DIS is primarily positioned against.
- **[PanSt3R](panst3r.md)**: Feed-forward multi-view panoptic segmentation on MUSt3R, a related baseline.
- **[VGGT](../reconstruction/vggt.md)**, **[Fast3R](../reconstruction/fast3r.md)** & **[DUSt3R](../foundation/dust3r.md)**: Feed-forward reconstruction models providing the geometric foundation.

## 📚 Key Takeaways

1. FAST3DIS performs multi-view 3D instance segmentation end-to-end via 3D anchors and anchor-sampling cross-attention, fully eliminating post-hoc clustering.
2. A dual-level regularization (multi-view contrastive + dynamically scheduled overlap penalty) is required for robust class-agnostic separation, preventing query hijacking and artificial background gaps.
3. It matches or beats clustering-based methods in accuracy while achieving 115×–250× inference speedups and scaling to 350 views in a single pass on a frozen DA3 backbone.

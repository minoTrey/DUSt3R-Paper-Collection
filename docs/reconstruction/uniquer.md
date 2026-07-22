# UniQueR: Unified Query-based Feedforward 3D Reconstruction (arXiv preprint)

![uniquer — architecture](https://arxiv.org/html/2603.22851v1/x2.png)

_UniQueR pipeline overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Chensheng Peng, Quentin Herau, Jiezhi Yang, Yichen Xie, Yihan Hu, Wenzhao Zheng, Matthew Strong, Masayoshi Tomizuka, Wei Zhan
- **Institution**: Applied Intuition, UC Berkeley, Stanford University
- **Venue**: arXiv preprint (2026-03)
- **Note**: The venue could not be confirmed from any primary source. It should be re-checked before being treated as final.
- **Links**: [Paper](https://arxiv.org/abs/2603.22851)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: Replaces pixel-aligned prediction with a sparse set of learnable 3D queries living in global space; each query spawns K Gaussians, and supervising renderings at held-out novel views forces queries to allocate geometry to regions no input pixel ever saw.

## 🎯 Key Contributions

1. **Queries instead of pixels as the scene representation**: DUSt3R, VGGT, and AnySplat predict per-pixel pointmaps or pixel-aligned Gaussians, which the paper characterizes as "fundamentally 2.5D and limited to visible surfaces." UniQueR's queries are anchored in global 3D, not per-frame camera space.
2. **Decoupled cross-attention**: Cross-attention from queries to image tokens followed by self-attention among queries, reducing complexity from `O((Q + N·HW/p²)²)` for full self-attention to `O(Q·N·HW/p² + Q²)`.
3. **Hybrid query initialization**: Half the queries sampled from the first-stage predicted point maps (grounding), half as learnable anchors uniformly sampled in 3D space (exploration of unobserved regions).
4. **Novel-view supervision as the mechanism for occlusion filling**: Supervision views are a strict superset of input views, so the model is penalized for holes visible only from held-out cameras.
5. **Order-of-magnitude fewer primitives**: 4096 queries × 64 Gaussians = 262K Gaussians, against per-pixel methods producing 448×448×N.

## 🔧 Technical Details

### Pipeline

1. **Image tokenization**: DINOv2 ViT per frame, then an alternating-attention transformer (intra-frame / inter-frame) following VGGT and π³.
2. **Per-frame geometry decoding**: `{P_i, X_i, C_i} = Decoder({T_i})` — camera pose, point map, confidence map. These serve as geometric priors that guide the query update.
3. **Query transformer**: queries updated against image tokens.
4. **GS spawning**: each query `q_i` at position `p_i` predicts a deformation `δq_i` and K Gaussian offsets `δg_ik` via MLP, plus opacity, scale, rotation, and color:

```text
G = ⋃_i ⋃_k ( p_i + δq_i + δg_ik , Σ_ik , c_ik , α_ik )
```

1. **Differentiable rendering** to RGB and depth.

### Positional Encoding

Predicted camera poses are converted to Plücker ray embeddings as positional encodings for image tokens; each query carries its own 3D coordinate as its positional embedding. The paper's rationale is that this 3D-aware parameterization makes the query↔token interaction geometrically meaningful.

### Why Random Query Initialization Fails

Unlike DETR3D, where 3D bounding boxes supply supervision, UniQueR has no 3D annotations. The paper reports that with all queries starting at random positions, training is "prone to divergence due to the lack of meaningful geometric grounding" — hence the hybrid scheme.

### Losses

```text
L = L_rgb + λ_d · L_depth + λ_c · L_cam
```

`L_rgb` combines ℓ1 and LPIPS; `L_depth` is scale-invariant on rendered depth; `L_cam` is retained from the backbone. No ground-truth 3D supervision is used — Gaussian splatting is the differentiable bridge to abundant 2D signal.

### Training

- DINOv2 encoder and point-map head initialized from **π³ and kept frozen**; only the camera head and query transformer are trained.
- AdamW, lr 1e-4 with cosine decay, **100 epochs at 224×224 on 32× A100 GPUs**, then fine-tuned at 448×448 for 20 epochs.
- 2–64 input views randomly sampled per training sample; dynamic resolution following MapAnything with aspect ratios 1.0, 1.33, 1.52, 1.77, 2.0.
- Training data: DL3DV-10K, ScanNet++, BlendedMVS, Co3D, using the data processing of MapAnything and CUT3R.
- Defaults: **Q = 4096 queries, K = 64 Gaussians per query (262K total)**.

### Post-Optimization

Following AnySplat, predicted Gaussians and poses initialize a test-time optimization that renders back into the input views and backpropagates reconstruction losses. Evaluated only under the dense-view setting.

### Representation Landscape

Table 1 of the paper positions representations along three axes — Volumetric (geometry beyond visible surfaces), Fast Inference (single forward pass), Low Memory — placing per-scene GS/NeRF, pixel-aligned pointmaps (VGGT, π³), voxel-aligned GS (AnySplat), voxel-aligned NeRF (DistillNeRF), and queries (UniQueR). The check/cross grid did not extract cleanly from the PDF and is not reproduced here; the paper's claim is that UniQueR is the only row favorable on all three.

## 📊 Results

### Sparse-View Novel View Synthesis

원논문 Table 2. Metrics on held-out views only; 5 different input subsets sampled and averaged. Inference time is end-to-end latency from images to Gaussians on a single A100 80GB.

| Dataset  | Method    | 3V PSNR ↑ | 3V SSIM ↑ | 3V LPIPS ↓ | 3V Time ↓ | 6V PSNR ↑ | 6V SSIM ↑ | 6V LPIPS ↓ | 6V Time ↓ |
| -------- | --------- | --------- | --------- | ---------- | --------- | --------- | --------- | ---------- | --------- |
| Mip-NeRF | NoPoSplat | 18.21     | 0.482     | 0.426      | 0.416     | 16.06     | 0.423     | 0.540      | 2.121     |
| Mip-NeRF | AnySplat  | 20.08     | 0.606     | 0.274      | 0.279     | 18.29     | 0.518     | 0.336      | 0.646     |
| Mip-NeRF | UniQueR   | **22.70** | **0.660** | **0.261**  | **0.213** | **21.80** | **0.622** | **0.300**  | **0.447** |
| VR-NeRF  | NoPoSplat | 21.28     | **0.744** | **0.381**  | 0.406     | 20.69     | **0.728** | **0.426**  | 2.176     |
| VR-NeRF  | AnySplat  | 19.67     | 0.745     | 0.313      | 0.290     | 17.25     | 0.683     | 0.411      | 0.656     |
| VR-NeRF  | UniQueR   | **21.99** | 0.708     | 0.446      | **0.198** | **20.87** | 0.689     | 0.431      | **0.412** |

On Mip-NeRF 360 UniQueR wins every metric. On VR-NeRF it wins PSNR and inference time but **loses SSIM and LPIPS to both baselines** — LPIPS 0.446 against NoPoSplat's 0.381 at 3 views. The paper's claim is "state-of-the-art PSNR across both", which is accurate but narrower than the table might suggest at a glance.

### Camera Pose Estimation

원논문 Table 3. RRA / RTA / AUC at a 30-degree error threshold, higher is better.

| Method  | RE10K RRA@30 ↑ | RE10K RTA@30 ↑ | RE10K AUC@30 ↑ | Co3Dv2 RRA@30 ↑ | Co3Dv2 RTA@30 ↑ | Co3Dv2 AUC@30 ↑ |
| ------- | -------------- | -------------- | -------------- | --------------- | --------------- | --------------- |
| Fast3R  | 99.05          | 81.86          | 61.68          | 97.49           | 91.11           | 73.43           |
| CUT3R   | 99.82          | 95.10          | 81.47          | 96.19           | 92.69           | 75.82           |
| FLARE   | 99.69          | 95.23          | 80.01          | 96.38           | 93.76           | 73.99           |
| VGGT    | 99.97          | 93.13          | 77.62          | 98.96           | 97.13           | **88.59**       |
| Pi3     | **99.99**      | **95.62**      | **85.90**      | **99.05**       | 97.33           | 88.41           |
| UniQueR | **99.99**      | 95.44          | 83.69          | **99.05**       | **97.44**       | 88.52           |

Pose accuracy is comparable to π³ but not better on RE10K (AUC@30 83.69 vs 85.90). The paper attributes the gap to more limited training data, noting π³ uses a private dataset.

### Dense-View Novel View Synthesis

원논문 Table 4. Top rows per dataset are feed-forward only; the rest are feed-forward initialization followed by per-scene optimization.

| Dataset    | Method                | 32V PSNR ↑ | 32V SSIM ↑ | 32V LPIPS ↓ | 64V PSNR ↑ | 64V SSIM ↑ | 64V LPIPS ↓ |
| ---------- | --------------------- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- |
| MipNeRF360 | AnySplat              | **22.32**  | **0.660**  | **0.258**   | 21.26      | 0.607      | **0.303**   |
| MipNeRF360 | Ours                  | 21.51      | 0.619      | 0.325       | **21.58**  | **0.641**  | 0.335       |
| MipNeRF360 | 3DGS+VGGT             | 22.61      | 0.701      | 0.233       | 23.78      | 0.729      | 0.221       |
| MipNeRF360 | 3DGS+AnySplat         | 24.99      | 0.705      | 0.227       | 23.71      | 0.664      | 0.266       |
| MipNeRF360 | 3DGS+Ours             | 25.14      | **0.774**  | **0.183**   | **26.00**  | **0.784**  | **0.176**   |
| MipNeRF360 | MipSplatting+VGGT     | 22.27      | 0.686      | 0.247       | 23.72      | 0.721      | 0.230       |
| MipNeRF360 | MipSplatting+AnySplat | 24.98      | 0.710      | 0.223       | 23.84      | 0.675      | 0.257       |
| MipNeRF360 | MipSplatting+Ours     | **25.26**  | 0.772      | 0.184       | 25.99      | 0.782      | 0.178       |
| VR-NeRF    | AnySplat              | **23.21**  | **0.773**  | **0.308**   | 23.62      | 0.802      | **0.285**   |
| VR-NeRF    | Ours                  | 23.18      | 0.770      | 0.395       | **24.74**  | **0.808**  | 0.334       |
| VR-NeRF    | 3DGS+VGGT             | 21.74      | 0.720      | 0.352       | 23.18      | 0.748      | 0.315       |
| VR-NeRF    | 3DGS+AnySplat         | 21.90      | 0.708      | 0.377       | 24.27      | 0.768      | 0.306       |
| VR-NeRF    | 3DGS+Ours             | **27.03**  | **0.846**  | **0.223**   | **28.56**  | **0.879**  | **0.174**   |
| VR-NeRF    | MipSplatting+VGGT     | 21.79      | 0.715      | 0.362       | 23.50      | 0.759      | 0.308       |
| VR-NeRF    | MipSplatting+AnySplat | 21.93      | 0.711      | 0.373       | 24.08      | 0.764      | 0.311       |
| VR-NeRF    | MipSplatting+Ours     | 26.62      | 0.838      | 0.237       | 28.39      | 0.873      | 0.185       |

The paper is candid about the feed-forward-only rows: at 32 views AnySplat edges it out on both datasets, and the authors attribute this to "the inherent sparsity of our representation" — 262K Gaussians against 448×448×N for per-pixel methods. The compelling result is the post-optimization block, where UniQueR-initialized 3DGS reaches 27.03 / 28.56 PSNR on VR-NeRF versus 21.90 / 24.27 for AnySplat-initialized.

The paper also flags an anomaly honestly: 3DGS+AnySplat occasionally underperforms standalone AnySplat on VR-NeRF, which it attributes to inaccurate AnySplat pose estimates degrading the per-scene optimization.

### Efficiency and Geometry

원논문 Table 5. 32 input views, 448×448, A100 80GB, batch size 1.

| Method   | # Gaussians | GPU Mem.     | Time (s) | Depth Abs Rel ↓ |
| -------- | ----------- | ------------ | -------- | --------------- |
| AnySplat | 3.85M       | 18.42 GB     | 4.63     | 0.062           |
| UniQueR  | **260K**    | **11.19 GB** | **1.97** | **0.038**       |

The paper's own summary of this table: **15× fewer Gaussians, 40% less GPU memory, 2.4× faster inference**, with abs-rel depth 0.038 vs 0.062.

### Ablations — Mip-NeRF 360, 3-View Sparse Setting

원논문 Table 6. Note these absolute values differ from Table 2's main results (20.23 vs 22.70 PSNR for the full model), so the ablation configuration is not the final model.

| Configuration                     | PSNR ↑    | SSIM ↑    | LPIPS ↓   |
| --------------------------------- | --------- | --------- | --------- |
| (a) w/o depth rendering           | 19.96     | **0.718** | 0.234     |
| (b) w/o hybrid init (random only) | 12.11     | 0.259     | 0.574     |
| Full model (hybrid init)          | **20.23** | 0.713     | **0.182** |

Random-only initialization is catastrophic (12.11 PSNR), confirming the paper's claim that point-map grounding is what makes query training stable. Removing depth rendering costs 0.27 PSNR and 0.052 LPIPS, but marginally _improves_ SSIM (0.718 vs 0.713) — a small inversion worth noting rather than glossing.

### Scaling Ablations

Figures 5a–5c ablate the number of queries, Gaussians per query (16 / 32 / 64 with 4096 queries), and model size (transformer depth and hidden size). **These are plots with no printed values.** The reported trend is monotone PSNR improvement along all three axes.

## 💡 Insights & Impact

### The 2.5D Critique, Stated Precisely

The paper's central argument is that pixel-aligned representations are _view-anchored_: because learned features are tied to specific camera projections, the model cannot allocate geometry to occluded or unseen regions, producing holes and artifacts in novel views that deviate from the input cameras. It also notes a second symptom — density imbalance that "reflects viewpoint distribution rather than true underlying geometry."

### Novel-View Supervision Is the Real Trick

The query architecture alone would not fill occlusions; nothing would ask it to. The training protocol does: with 3 input images the model renders and is supervised on 6 views. If the model only reconstructs what the input views saw, holes appear in the novel supervision views and are penalized. Architecture and supervision are inseparable here.

### The Sparsity Trade Cuts Both Ways

262K Gaussians buy 40% less memory and 2.4× faster inference, and they clearly win in the sparse-view regime where per-pixel methods have too few pixels to work with. But under dense views the same sparsity caps feed-forward rendering quality — AnySplat's 3.85M primitives win at 32 views. What survives is that a compact, geometrically well-placed set is a _better initialization_ than a large, view-anchored one, which is a different and arguably more useful claim.

### Lineage

The query formulation is borrowed explicitly from DETR / DETR3D / PETR in detection, and from Scaffold-GS's anchor-spawning idea. The paper's distinction is that Scaffold-GS still requires per-scene optimization, and LRM-style query architectures are object-centric with near-complete view coverage, whereas UniQueR targets scene-level settings where occlusion and partial coverage are the norm.

## 🔗 Related Work

- [Pi3](./pi3.md) — supplies the frozen DINOv2 encoder and point-map head, the alternating-attention design, and the pose evaluation protocol; also the strongest pose baseline.
- [VGGT](./vggt.md) — the pixel-aligned pointmap approach UniQueR argues against, and a pose and initialization baseline.
- [MapAnything](./mapanything.md) — source of the data processing and the dynamic-resolution training recipe.
- [CUT3R](../dynamic/cut3r.md) — the other data-processing source, and a pose baseline.
- [Fast3R](./fast3r.md) — many-view feed-forward pose baseline.
- [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md) — the pointmap lineage; named in the abstract as representative of the 2.5D paradigm.
- [Spann3R](./spann3r.md), [MUSt3R](./must3r.md) — memory/recurrent extensions surveyed in the related work.
- [InstantSplat](../gaussian-splatting/instantsplat.md), [Splatt3R](../gaussian-splatting/splatt3r.md) — feed-forward Gaussian neighbours in this collection.

## 📚 Key Takeaways

1. **Decoupling the representation from camera space is what enables occlusion reasoning.** Queries live in global 3D and are not bound to any pixel grid.
2. **Supervising beyond the input views is what makes that capability materialize.** The architecture provides the freedom; the loss provides the pressure.
3. **Hybrid initialization is not a detail.** Pure random query placement drops PSNR from 20.23 to 12.11.
4. **Decoupled attention is what makes many views affordable**, reducing complexity from quadratic in total tokens to linear in image tokens per query.
5. **The honest scorecard**: clear wins in the sparse-view regime and on efficiency and depth accuracy; roughly tied on pose with π³; behind AnySplat on dense feed-forward rendering; decisively ahead as an initialization for per-scene optimization.

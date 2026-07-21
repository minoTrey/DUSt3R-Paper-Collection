# DVGT: Driving Visual Geometry Transformer (arXiv preprint (2025-12))

## 📋 Overview

- **Authors**: Sicheng Zuo, Zixun Xie, Wenzhao Zheng, Shaoqing Xu, Fang Li, Shengyin Jiang, Long Chen, Zhi-Xin Yang, Jiwen Lu
- **Institution**: Tsinghua University; University of Macau; Xiaomi EV; Peking University
- **Venue**: arXiv preprint (2025-12)
- **Links**: [Paper](https://arxiv.org/abs/2512.16919) | [Code](https://github.com/wzzheng/DVGT) | [Project Page](https://wzzheng.net/DVGT)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A driving-targeted visual geometry transformer that reconstructs a metric-scaled global 3D point map in the ego-vehicle coordinate system plus per-frame ego poses from a sequence of unposed multi-view images, using factorized intra-view / cross-view / cross-frame attention and predicting metric scale directly without post-alignment to external sensors.

## 🎯 Key Contributions

1. **Ego-centric metric point map reconstruction**: Formulates driving geometry perception as predicting continuous, metric-scaled 3D point maps in the ego-vehicle frame of the first frame, decoupling the output from camera intrinsics/extrinsics and view count.
2. **Factorized spatial-temporal transformer**: Replaces VGGT's global attention with cascaded intra-view local, cross-view spatial, and cross-frame temporal attention for efficiency on many-view driving inputs, plus temporal positional embeddings.
3. **3D prior-free design**: The model is structurally independent of camera parameters and 2D-to-3D projection, learning geometry directly from image features so it adapts across camera configurations.
4. **Large mixed-domain driving dataset with dense pseudo-GT**: A robust pseudo-labeling pipeline (MoGe-2 depth + ROE alignment with LiDAR, plus failure-pattern threshold filtering) generates dense 3D point-map ground truth across five benchmarks.

## 🔧 Technical Details

### Architecture

- **Encoder**: a DINOv3-pretrained ViT-L converts each image into tokens; a learnable ego token is concatenated per image and temporal positional embeddings are added per frame.
- **Geometry transformer**: L = 24 blocks (feature dim 1024, 16 heads, QKNorm, LayerScale init 0.01), each block running intra-view local → cross-view spatial → cross-frame temporal attention. Total ~1.7 billion parameters. DPT decoder fed from blocks 4/11/17/23.
- **Heads**: a point-map head decodes per-image metric point maps; a pose head takes ego tokens averaged over views per frame to regress the ego pose (7-D: 3-D translation + 4-D quaternion).

### Training

- Loss L = λ·L_epose + L_pmap with λ = 5.0; point-map loss follows VGGT (uncertainty-weighted L2 + gradient term, regularizer α = 2.0).
- AdamW, 160K iterations, cosine LR peak 1e-4 with 8K warmup, grad-norm clip 1.0, bf16 + gradient checkpointing, ~6 days on 64 H20 GPUs; 48 images/batch. Dataset sampling ratio nuScenes : KITTI : OpenScene : Waymo : DDAD = 6 : 5 : 77 : 6 : 6.

## 📊 Results

Baselines: general models (VGGT, MapAnything, CUT3R, StreamVGGT) and driving-specific Driv3R. `*` means the predicted point map is Umeyama-aligned to sparse LiDAR to recover metric scale; DVGT and MapAnything predict metric scale directly.

### 3D reconstruction (Accuracy↓ / Completeness↓)

원논문 Table 1. Inference time on 128 images (16 frames × 8 views). DVGT leads on Accuracy across most datasets but not every Completeness column, and on Waymo its Accuracy trails Driv3R (see Insights).

| Method      | KITTI Acc/Comp | NuScenes Acc/Comp | Waymo Acc/Comp | OpenScene Acc/Comp | DDAD Acc/Comp | Time   |
| ----------- | -------------- | ----------------- | -------------- | ------------------ | ------------- | ------ |
| CUT3R*      | 0.965 / 2.050  | 2.054 / 2.603     | 3.391 / 4.216  | 1.864 / 2.258      | 2.774 / 4.677 | ~5.6s  |
| VGGT*       | 1.154 / 1.294  | 1.300 / 1.498     | 1.641 / 2.053  | 1.422 / 1.496      | 1.741 / 2.473 | ~13.7s |
| MapAnything | 1.880 / 1.014  | 4.499 / 4.886     | 10.205 / 8.494 | 3.353 / 4.303      | 8.015 / 8.493 | ~5.8s  |
| StreamVGGT* | 3.421 / 2.196  | 2.588 / 2.414     | 3.630 / 3.275  | 2.304 / 2.098      | 2.717 / 2.788 | ~31.0s |
| Driv3R*     | 0.864 / 1.083  | 0.742 / 1.345     | 0.800 / 1.311  | 0.884 / 1.693      | 0.950 / 1.259 | ~9.0s  |
| **DVGT**    | 0.846 / 1.468  | 0.457 / 0.494     | 1.714 / 2.216  | 0.402 / 0.481      | 0.751 / 1.009 | ~4.0s  |

### Ray depth (Abs Rel↓ / δ<1.25↑)

원논문 Table 2. DVGT is best on every dataset.

| Method      | KITTI       | NuScenes    | Waymo       | OpenScene   | DDAD        |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| CUT3R       | 0.217/0.659 | 0.332/0.547 | 0.291/0.562 | 0.278/0.593 | 0.870/0.315 |
| VGGT        | 0.158/0.801 | 0.243/0.729 | 0.176/0.811 | 0.241/0.719 | 0.613/0.476 |
| MapAnything | 0.188/0.725 | 0.568/0.269 | 0.507/0.211 | 0.486/0.240 | 1.971/0.195 |
| StreamVGGT  | 0.362/0.469 | 0.412/0.540 | 0.339/0.584 | 0.319/0.607 | 0.838/0.415 |
| Driv3R      | 0.164/0.784 | 0.189/0.721 | 0.168/0.770 | 0.188/0.740 | 0.185/0.740 |
| **DVGT**    | 0.136/0.849 | 0.069/0.953 | 0.106/0.921 | 0.049/0.971 | 0.152/0.837 |

### Ego pose (AUC@30↑)

원논문 Table 3. DVGT is best on OpenScene and DDAD; VGGT is higher on KITTI, NuScenes, and Waymo.

| Method      | KITTI | NuScenes | Waymo | OpenScene | DDAD |
| ----------- | ----- | -------- | ----- | --------- | ---- |
| CUT3R       | 51.8  | 43.5     | 50.1  | 34.7      | 48.6 |
| VGGT        | 96.9  | 87.8     | 87.7  | 66.3      | 92.8 |
| MapAnything | 90.6  | 85.0     | 82.8  | 65.6      | 87.0 |
| StreamVGGT  | 95.8  | 86.2     | 85.6  | 74.1      | 91.9 |
| **DVGT**    | 87.6  | 86.5     | 86.4  | 74.7      | 95.1 |

### Depth vs driving models (nuScenes, LiDAR GT)

원논문 Table 4. DVGT needs no scale post-processing yet leads on both metrics.

| Method        | Scale Method   | Abs Rel↓ | δ<1.25↑ |
| ------------- | -------------- | -------- | ------- |
| MonoDepth2    | Median Scaling | 0.29     | 0.64    |
| SurroundDepth | SfM Pretrain   | 0.28     | 0.66    |
| R3D3          | Extrinsic      | 0.25     | 0.73    |
| SelfOcc       | Pose GT        | 0.23     | 0.75    |
| OmniNWM       | Pose GT        | 0.23     | 0.81    |
| **DVGT**      | None           | 0.13     | 0.86    |

### Ablations (nuScenes)

- **Coordinate normalization** (원논문 Table 5): linearly dividing target coordinates by 10 is best (Acc 1.349, AbsRel 0.195, AUC@30 79.8) vs base ÷1 (Acc 1.584, AUC 68.4), ÷100 (Acc 1.646, AUC 80.7), and arcsinh (Acc 1.411, AUC 80.8).
- **Attention design** (원논문 Table 6): global L+G gives the best Acc (1.131) and AbsRel (0.178) but is slow (~8.2s); the factorized L+S+T is fast (~4.0s) but weaker (Acc 1.584); adding temporal positional embeddings (L+S+T+TE) recovers most quality (Acc 1.458, AbsRel 0.227, AUC 77.6) at ~4.0s.

## 💡 Insights & Impact

- Directly predicting metric scale in an ego-centric frame removes the LiDAR/pose post-alignment that VGGT and CUT3R require, so the point maps are usable downstream without external sensors — a practical advantage over general geometry models.
- Honest weaknesses the authors flag: Waymo results are less competitive (its Accuracy trails Driv3R) because Waymo (5× larger) was given the same sampling weight as smaller datasets; ego-pose on KITTI is lower because its high-overlap dual-camera setup limits full 3D/ego-motion understanding, and VGGT's global attention still beats DVGT's factorized attention on KITTI/NuScenes/Waymo pose AUC.
- The factorized attention trades a small accuracy drop for a large speedup (~4.0s vs global's ~8.2s), with temporal positional embeddings narrowing most of the gap.

## 🔗 Related Work

- **[VGGT](./vggt.md)**: the global-attention backbone DVGT re-architects with factorized spatial-temporal attention and metric-scale prediction; a primary baseline.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: pioneering feed-forward pointmap regression cited as the paradigm's origin.
- **[MapAnything](./mapanything.md)** / **[Point3R](./point3r.md)** / **[StreamVGGT](./streamvggt.md)** / **[CUT3R](../dynamic/cut3r.md)**: general feed-forward reconstruction baselines compared on driving data.
- **[MoGe-2](./moge-2.md)**: monocular geometry model used to produce dense depth pseudo-labels in the GT-construction pipeline.

## 📚 Key Takeaways

1. DVGT reformulates driving 3D perception as ego-centric metric point-map reconstruction, decoupling outputs from camera parameters and predicting metric scale directly (no LiDAR/pose post-alignment).
2. A factorized intra-view / cross-view / cross-frame transformer (1.7B params, DINOv3 ViT-L) plus temporal positional embeddings balances accuracy and ~4.0s inference on 128 images.
3. It leads ray-depth accuracy on all five driving datasets and reconstruction Accuracy on most, though VGGT retains higher pose AUC on KITTI/NuScenes/Waymo and Driv3R edges Accuracy on Waymo.

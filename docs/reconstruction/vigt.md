# ViGT: Visual Implicit Geometry Transformer for Autonomous Driving (arXiv preprint 2026-02)

## 📋 Overview

- **Authors**: Arsenii Shirokov, Mikhail Kuznetsov, Danila Stepochkin, Egor Evdokimov, Daniil Glazkov, Nikolay Patakin, Anton Konushin, Dmitry Senushkin
- **Institution**: Lomonosov Moscow State University
- **Venue**: arXiv preprint (2026-02)
- **Links**: [Paper](https://arxiv.org/abs/2602.05573) | [Code](https://github.com/whesense/ViGT)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A calibration-free, self-supervised geometric model that estimates a continuous 3D occupancy field in BEV directly from surround-view camera rigs, trained on synchronized image-LiDAR pairs and generalizing across diverse sensor configurations.

## 🎯 Key Contributions

1. **Continuous occupancy field for driving**: Unlike pixel-aligned geometric foundation models, ViGT estimates a continuous 3D occupancy field in a bird's-eye-view (BEV) frame, addressing domain-specific autonomous-driving requirements and providing a common representation for multiple geometric tasks.
2. **Calibration-free architecture**: A single model adapts to different camera rigs (e.g. 6 cameras on NuScenes, 7 on Argoverse 2) without explicit camera parameters, via an implicit BEV projection that learns the image-to-BEV transformation.
3. **Self-supervised training from image-LiDAR pairs**: The occupancy classification objective is supervised only by raw LiDAR point clouds along rays, eliminating voxel annotation and calibration requirements.
4. **Cross-dataset generalization**: Trained jointly on five large-scale datasets, ViGT achieves state-of-the-art pointmap estimation across NuScenes, Argoverse 2, Waymo, ONCE, and NuPlan and remains competitive on the Occ3D-nuScenes occupancy benchmark without task-specific retraining.

## 🔧 Technical Details

### Architecture

Each image is encoded independently by a ViT-Large backbone into token embeddings. An implicit BEV projector (two sequential cross-attention blocks) maps these tokens to BEV features without explicit calibration; features are aggregated to 256×256 resolution via DPT. A query-based implicit decoder (à la Convolutional Occupancy Networks) predicts point-wise occupancy probabilities.

### Self-supervised occupancy

Query points are sampled along LiDAR rays: points before the reflection point are labeled free (negative), points near the reflection point occupied. Training is a binary occupancy classification. Depth and point clouds are derived by integrating occupancy along rays (Eq. 3), so one model serves multiple downstream representations.

### Training

AdamW for 200K iterations, learning rate 5×10⁻⁵ with 10K warmup, batch size 6 per GPU, images resized to a 192-pixel short side, 1024 BEV queries; trained on 128 A100 GPUs over five days.

## 📊 Results

### Occupancy estimation on Occ3D-NuScenes

원논문 Table 1. F1/IoU higher is better. "Calib. −" = no camera calibration used.

| Method     | Supervision | Calib. | F1-score↑ | IoU↑   |
| ---------- | ----------- | ------ | --------- | ------ |
| FB-Occ     | 3D GT       | +      | 0.8181    | 0.7022 |
| Sparse-Occ | 3D GT       | +      | 0.6271    | 0.4680 |
| PanoOcc    | 3D GT       | +      | 0.8347    | 0.7271 |
| Offset-Occ | 3D GT       | +      | 0.6240    | 0.4637 |
| RenderOcc  | 2D GT       | +      | 0.6442    | 0.4824 |
| Self-Occ   | Self-sup    | +      | 0.6552    | 0.4960 |
| **Ours**   | Self-sup    | −      | 0.7115    | 0.5658 |

ViGT is third-best overall (behind the 3D-GT-supervised PanoOcc and FB-Occ) but best among self-supervised / 2D-label methods, improving the previous best self-supervised Self-Occ by 0.056 F1 and 0.07 IoU while also removing the calibration requirement.

### Pointmap estimation across five datasets

원논문 Table 2 (depth-map "D" variant for baselines; "PR" = points rendered from occupancy for RenderOcc and Ours). AbsRel/CD lower is better; Avg Rank across all metrics/datasets lower is better.

| Method    | NuScenes AbsRel↓ | NuScenes CD↓ | AV2 AbsRel↓ | AV2 CD↓ | Avg Rank↓ |
| --------- | ---------------- | ------------ | ----------- | ------- | --------- |
| VGGT      | 0.195            | 4.019        | 0.164       | 3.724   | 3.9       |
| DUSt3R    | 0.250            | 4.466        | 0.230       | 3.906   | 6.9       |
| Mast3R    | 0.191            | 4.583        | 0.190       | 4.752   | 6.4       |
| Monst3R   | 0.217            | 3.945        | 0.201       | 4.013   | 4.8       |
| Stream3R  | 0.173            | 3.931        | 0.162       | 3.992   | 4         |
| Cut3R     | 0.189            | 4.062        | 0.194       | 3.681   | 3.5       |
| DA3       | 0.289            | 5.606        | 0.174       | 4.488   | 6.4       |
| RenderOcc | 0.245            | 3.637        | 0.316       | 10.864  | 7.3       |
| **Ours**  | 0.068            | 1.807        | 0.131       | 2.965   | 1.8       |

ViGT has the best Average Rank (1.8). On NuScenes it improves AbsRel by 0.105 and CD by 1.83 over the second-best (Stream3R depth-maps). On Waymo it is second-best CD (2.431), trailing the best by only 0.05; on ONCE and NuPlan it is best AbsRel but third-/second-best CD respectively.

### Ablation of design choices

원논문 Table 3. Trained on NuScenes only. CD lower is better; F1/IoU higher is better.

| Setting                        | CD↓   | F1-score↑ | IoU↑  |
| ------------------------------ | ----- | --------- | ----- |
| **BEV Projector Architecture** |       |           |       |
| CA                             | 3.051 | 0.697     | 0.547 |
| CA + CA                        | 2.699 | 0.713     | 0.566 |
| CA + SA + CA                   | 2.814 | 0.697     | 0.548 |
| **Encoder Output Layers**      |       |           |       |
| Last 4 layers                  | 2.699 | 0.713     | 0.566 |
| Layers 5, 11, 16, 23           | 3.093 | 0.70      | 0.55  |
| **Query Sampling Strategy**    |       |           |       |
| Random                         | 2.895 | 0.701     | 0.552 |
| Stratified                     | 3.039 | 0.697     | 0.547 |
| Stratified + Sym. Interval     | 2.699 | 0.713     | 0.566 |

Two sequential cross-attention blocks (CA + CA) beat a single block or a self-attention variant; the last four ViT-L layers and stratified + symmetric-interval sampling near object boundaries perform best.

## 💡 Insights & Impact

- **Occupancy over pointmaps for driving**: A continuous BEV occupancy field is a more natural, sensor-agnostic geometric representation for autonomous driving than pixel-aligned pointmaps, and can be decoded into depth or point clouds on demand.
- **Calibration-free generalization**: Learning the image-to-BEV mapping implicitly lets one model serve heterogeneous camera rigs, which the paper visualizes via camera-to-BEV attention that partitions BEV space by field of view.
- **Label efficiency**: Using only raw LiDAR for supervision, ViGT closes much of the gap to 3D-GT-supervised occupancy methods while being the only fully self-supervised and calibration-free approach.

## 🔗 Related Work

- **[VGGT](vggt.md)**, **[CUT3R](../dynamic/cut3r.md)**, **[MonST3R](../dynamic/monst3r.md)**: General-domain feed-forward geometric models evaluated as pointmap baselines.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: Foundational pixel-aligned reconstruction baselines.

## 📚 Key Takeaways

1. ViGT reframes autonomous-driving geometry as continuous, calibration-free 3D occupancy prediction in BEV, trained self-supervised from image-LiDAR pairs.
2. It achieves the best Average Rank (1.8) for pointmap estimation across five driving datasets, notably improving NuScenes AbsRel (0.068) and CD (1.807).
3. On Occ3D-NuScenes it is the strongest self-supervised, calibration-free method, trailing only 3D-GT-supervised occupancy models.

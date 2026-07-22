# UniScene3D: RGB-Pointmap Pretraining for Unified 3D Scene Understanding (ECCV 2026)

![uniscene3d — architecture](https://arxiv.org/html/2604.02546v3/x2.png)

_Overview of UniScene3D pretraining (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Ye Mao, Weixun Luo, Ranran Huang, Junpeng Jing, Krystian Mikolajczyk
- **Institution**: Imperial College London
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2604.02546) | [Project Page](https://yebulabula.github.io/UniScene3D/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A transformer encoder that learns unified 3D scene representations by jointly modeling appearance (RGB) and geometry (pointmaps) from multi-view RGB-Pointmap pairs, initialized from a 2D foundation model and pretrained with cross-view geometric and grounded view alignment.

## 🎯 Key Contributions

1. **UniScene3D encoder**: Learns unified 3D scene representations by jointly modeling geometry and appearance from multi-view RGB-Pointmap (image + pixel-aligned pointmap) pairs via early token fusion at the patch embedding stage, reusing pretrained 2D backbone weights.
2. **Novel alignment objectives**: Cross-view geometric alignment (rank-aware, Chamfer-distance-ordered contrastive learning across views within a scene) and grounded view alignment (aligning object referring text with all views that observe the object) to capture geometric and semantic consistency across viewpoints.
3. **Systematic low-shot evaluation**: Evaluates 3D scene representation quality under zero-shot, few-shot, and task-specific fine-tuning across viewpoint grounding, scene retrieval, scene type classification, and 3D VQA — reaching state-of-the-art on all.

## 🔧 Technical Details

### RGB-Pointmap representation

- Input: V aligned multi-view image–pointmap pairs; each pointmap is a pixel-aligned back-projection of the depth map (via camera intrinsics/extrinsics) expressed in the world frame.
- Built on and initialized from the pretrained 2D image encoder of **FG-CLIP** (ViT-B/16). Image and pointmap patch embedding layers share architecture and initialization; their patch tokens are fused by **element-wise summation** (early fusion). A per-view class token is processed by N transformer blocks to give per-view representations.

### Four multimodal alignment objectives

- **L_geo (cross-view geometric)**: Within a scene, sorts other views by symmetric Chamfer distance to build a rank-aware soft target, interpolated with a hard nearest-neighbor target (coefficient α); soft-label cross-entropy over cross-view similarity logits.
- **L_ground (grounded view)**: Positive view–object pairs determined by intersection between a view's 3D pointmap and the object's 3D mask (from SceneVerse); bidirectional contrastive loss.
- **L_view / L_scene (view-/scene-level)**: Batch-level RGBP–text alignment following POMA-3D, using per-view captions and mean-pooled scene captions with the FG-CLIP text encoder.
- Total loss: L_total = λ·L_geo + L_ground + L_view + L_scene, with λ = 0.1.

### Training setup

- Pretrained on **6,562 indoor scenes** from ScanNet, 3RScan, and ARKitScenes; referring expressions from SceneVerse; view/scene captions from POMA-3D.
- 80 epochs, batch size 64, ViT-B/16 FG-CLIP backbone, AdamW (β₁=0.9, β₂=0.98), lr 1e-4 → 1e-5 cosine, 32 image–pointmap pairs per scene (maximum coverage sampling) at 224×224, α = 0.7, τ_r = 0.35.

## 📊 Results

All baselines use ViT-B/16 checkpoints at 224×224. R@N = Recall@N. Best in bold.

### Viewpoint grounding (zero-shot, R@1)

원논문 Table 2. Recall@1 (↑) across three benchmarks; Input = image (I), point cloud (PC), pointmap (PM), RGB-Pointmap (RGBP).

| Method     | Input | ScanRefer | Nr3D     | Sr3D     |
| ---------- | ----- | --------- | -------- | -------- |
| DFN        | I     | 20.9      | 17.3     | 12.6     |
| SigLIP2    | I     | 22.2      | 18.8     | 13.0     |
| FG-CLIP    | I     | 20.2      | 17.3     | 13.4     |
| Uni3D-g    | PC    | 4.2       | 3.6      | 3.4      |
| POMA-3D    | PM    | 16.4      | 13.6     | 10.2     |
| UniScene3D | RGBP  | **38.6**  | **25.2** | **23.6** |

On ScanRefer, UniScene3D also leads at R@5/R@10 (72.5 / 85.7 vs POMA-3D 50.6 / 71.2).

### Scene retrieval (zero-shot, R@1)

원논문 Table 3. Recall@1 (↑); each scene caption contains n = 5 or n = 10 utterances.

| Method     | Input | ScanRefer n=5 | ScanRefer n=10 | Nr3D n=10 | Sr3D n=10 |
| ---------- | ----- | ------------- | -------------- | --------- | --------- |
| FG-CLIP    | I     | 9.2           | 16.3           | 12.4      | 0.7       |
| Uni3D-g    | PC    | 0.3           | 0.3            | 0.4       | 0.2       |
| 3D-VisTA   | PC    | 0.6           | 0.7            | 0.2       | 0.2       |
| SceneVerse | PC    | 0.5           | 0.6            | 0.5       | 0.1       |
| POMA-3D    | PM    | 13.8          | 20.4           | 19.3      | 2.4       |
| UniScene3D | RGBP  | **22.4**      | **33.4**       | **30.7**  | **4.6**   |

### Scene type classification (accuracy %)

원논문 Table 4. 21 ScanNet room types; linear probing for few-shot. Higher is better.

| Method     | Input | 0-shot   | 1-shot   | 5-shot   | 10-shot  |
| ---------- | ----- | -------- | -------- | -------- | -------- |
| DFN        | I     | 41.6     | 40.5     | 60.1     | 77.5     |
| SigLIP2    | I     | 36.0     | 36.6     | 57.8     | 77.9     |
| FG-CLIP    | I     | 49.5     | 40.0     | 62.0     | 77.5     |
| Uni3D-g    | PC    | 8.6      | 21.4     | 37.1     | 45.4     |
| 3D-VisTA   | PC    | 1.9      | 28.9     | 49.4     | 55.0     |
| SceneVerse | PC    | 0.8      | 24.0     | 51.1     | 64.2     |
| POMA-3D    | PM    | 63.9     | 32.2     | 64.9     | 74.1     |
| UniScene3D | RGBP  | **70.7** | **43.2** | **72.4** | **83.7** |

### 3D VQA — Exact Match (EM@1 / EM@10 ↑)

원논문 Table 5. Task-specific fine-tuning; frozen visual encoder, tuned QA head + BERT.

| Method     | Input | ScanQA          | SQA3D           | Hypo3D          |
| ---------- | ----- | --------------- | --------------- | --------------- |
| FG-CLIP    | I     | 20.9 / 49.9     | 49.5 / 89.7     | 31.1 / 82.1     |
| 3D-VisTA   | PC    | 22.4 / 52.1     | 48.5 / 85.6     | 31.0 / 81.2     |
| SceneVerse | PC    | 22.7 / 51.5     | 49.9 / 85.0     | 31.6 / 80.3     |
| POMA-3D    | PM    | 22.3 / 52.3     | 51.1 / 91.2     | 33.4 / 84.8     |
| UniScene3D | RGBP  | **23.2 / 53.5** | **52.5 / 92.3** | **35.2 / 85.9** |

### Ablations (viewpoint grounding / scene retrieval, ScanRefer)

원논문 Table 8. R@1 (↑) with individual components removed.

| Case         | ScanRefer VG R@1 | Nr3D VG R@1 | Sr3D VG R@1 | Retrieval n=5 R@1 |
| ------------ | ---------------- | ----------- | ----------- | ----------------- |
| UniScene3D   | **38.6**         | **25.2**    | **23.6**    | **22.4**          |
| w/o image    | 37.6             | 23.7        | 23.1        | 21.2              |
| w/o pointmap | 28.8             | 21.3        | 18.5        | 21.8              |
| w/o L_geo    | 38.2             | 23.2        | 23.0        | 21.6              |
| w/o L_ground | 18.5             | 15.6        | 11.5        | 21.8              |

Removing pointmap input hurts grounding most among modalities, while removing grounded view alignment (L_ground) causes the largest overall grounding drop.

원논문 Table 7. Fusion-design ablation on viewpoint grounding (ScanRefer). R@1 / R@5 (↑).

| Case                        | R@1  | R@5  |
| --------------------------- | ---- | ---- |
| UniScene3D                  | 38.6 | 72.5 |
| Random Init. PM Patch Embed | 38.0 | 71.8 |
| w/o Positional Encoding     | 37.2 | 71.4 |
| Concat + Projection         | 36.5 | 70.0 |

Early summation fusion with pretrained patch-embedding weights beats concat+projection, which even underperforms the w/o-image setting.

## 💡 Insights & Impact

- **Pointmaps unify grid structure with global geometry**: Unlike point clouds (irregular, incompatible with grid backbones) or multi-view images/depth (lack globally consistent scene geometry), pointmaps share a world frame while preserving an image-like grid — enabling reuse of pretrained 2D priors.
- **2D priors help pointmap learning** (원논문 Table 6): Initializing the pointmap-only ViT from FG-CLIP rather than random weights improves ScanRefer viewpoint grounding even before 3D training (R@1 7.53 vs 4.32 without further training), and the gap widens after full UniScene3D training (37.62 vs 7.53).
- **Appearance + geometry are complementary**: Pointmap-only misses color cues (fails on "green seats"); image-only misses spatial extent (fails on "longest seating area"). Joint RGB-Pointmap resolves both.
- **View robustness**: UniScene3D with 16 views already surpasses POMA-3D with 32 views, indicating no bias toward a fixed view count.
- **Limitations**: Fixed input resolution and a single ViT-B/16 backbone; trained on a limited number of scenes and remains data-hungry despite 2D priors.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: Feed-forward pointmap prediction that made scene-level pointmaps a practical modality for representation learning.
- **[VGGT](../reconstruction/vggt.md)**: Geometry foundation model producing dense pointmaps of the kind UniScene3D consumes.
- **[Large Spatial Model](largespatialmodel.md)**: Related unposed-image-to-semantic-3D work in this collection.
- POMA-3D (not in this collection): the closest prior pointmap-only representation method, which UniScene3D consistently outperforms by adding appearance and cross-view alignment.

## 📚 Key Takeaways

1. UniScene3D jointly models RGB and pointmap geometry via early token fusion on a 2D-foundation backbone, learning unified 3D scene representations.
2. Cross-view geometric alignment and grounded view alignment inject geometric and semantic consistency across viewpoints.
3. It reaches state-of-the-art across viewpoint grounding, scene retrieval, scene type classification, and 3D VQA under zero-shot, few-shot, and fine-tuning.
4. Pointmaps' grid structure lets standard 2D backbones and their pretrained priors transfer directly into 3D scene understanding, outperforming point-cloud and pointmap-only encoders.

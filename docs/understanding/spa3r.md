# Spa3R: Predictive Spatial Field Modeling for 3D Visual Reasoning (arXiv preprint 2026-02)

![spa3r — architecture](https://arxiv.org/html/2602.21186/x1.png)

_Overview of the Spa3R framework and Spa3-VLM integration (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Haoyi Jiang, Liu Liu, Xinjie Wang, Yonghao He, Wei Sui, Zhizhong Su, Wenyu Liu, Xinggang Wang
- **Institution**: Huazhong University of Science & Technology, Horizon Robotics, D-Robotics
- **Venue**: arXiv preprint (2026-02)
- **Links**: [Paper](https://arxiv.org/abs/2602.21186) | [Code](https://github.com/hustvl/Spa3R)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A self-supervised framework (Predictive Spatial Field Modeling) that learns a unified, view-invariant spatial representation from unposed multi-view images by synthesizing feature fields for arbitrary unseen views, then plugs its frozen encoder into a VLM (Spa3-VLM) to ground language reasoning in 3D space.

## 🎯 Key Contributions

1. **Diagnosis of a VLM bottleneck**: Existing spatial-reasoning VLMs offload holistic 3D reconstruction to the language model from partial, view-conditioned features under sparse supervision — an inefficient, ill-posed objective.
2. **Predictive Spatial Field Modeling (PSFM)**: A self-supervised paradigm that learns a unified, view-invariant spatial representation by synthesizing feature fields for arbitrary novel views, internalizing intrinsic geometry and spatial layout via a predictive information bottleneck.
3. **Spa3-VLM**: Integrates the frozen pretrained Spa3R encoder into Qwen2.5-VL through a lightweight Residual Cross-Attention Adapter, grounding reasoning in a holistic spatial context.

## 🔧 Technical Details

### Predictive Spatial Field Modeling (PSFM)

- Treats a 3D scene as a continuous spatial feature field f: V → F mapping camera pose to a view-centric feature map.
- Framed as a Neural Process: an amortized encoder E_ϕ maps N_C context views into a single latent z; a decoder D_θ acts as a conditional neural field reconstructing target-view features F̂_t for arbitrary poses conditioned on z.
- Objective L_PSFM minimizes the distance between predicted and ground-truth target features. Views sampled per scene are randomly split into context and target sets; the single-latent bottleneck compels the encoder to internalize complete 3D geometry.

### Spa3R architecture

- **Asymmetric View Aggregator**: Adapts the pretrained VGGT with an asymmetric attention mask so target views attend to all views while context views attend only to other context views — preventing target→context information leakage and keeping context features independent of targets.
- **Spa3R Encoder**: A transformer that aggregates N_q learnable query embeddings with context features to produce the compact latent z.
- **Spa3R Decoder**: Synthesizes target features via ray-based querying (camera-space ray directions from estimated intrinsics) and **PRoPE** relative positional encoding, which injects the relative camera transformation directly into attention.
- **Losses**: Reconstruction of target features composed of geometric features (from the Asymmetric View Aggregator) and semantic features (from a frozen DINOv3 backbone, an auxiliary objective), with separate geometric and semantic heads; each head uses L1 + cosine-similarity loss.

### Spa3-VLM integration

- Frozen Spa3R encoder produces spatial latent z; a Residual Cross-Attention Adapter fuses z with the VLM's native visual features F_V (query = F_V, key/value = z), followed by a zero-initialized MLP projector and residual connection to preserve pretrained knowledge.
- Only the adapter and language model are fine-tuned (one epoch); the Spa3R encoder and the VLM vision encoder stay frozen.

### Setup

- Pre-training data: ScanNet + ScanNet++. Encoder/decoder are 6-layer transformers (D = 768), N_q = 256 queries, 80K steps, AdamW lr 1e-3, 4–12 views sampled per scene (half context / half target), 8 NVIDIA 5090 GPUs. Base VLM: Qwen2.5-VL-3B (Spa3-VLM is a 4B model). Instruction-tuning: VSI-590K (video), and SPAR-234K + LLaVA-Hound + VLM3R data (image).

## 📊 Results

### VSI-Bench (average accuracy)

원논문 Table 1. Avg accuracy (↑) on VSI-Bench spatial reasoning. Per-category sub-columns exist in the source table but their headers are rendered as rotated text and are not transcribed here.

| Model              | Avg.     |
| ------------------ | -------- |
| GPT-4o             | 34.0     |
| Gemini-1.5-Flash   | 42.1     |
| Gemini-1.5-Pro     | 45.4     |
| InternVL2-8B       | 37.5     |
| LLaVA-Video-7B     | 35.6     |
| Qwen2.5VL-7B       | 33.0     |
| Spatial-MLLM-4B    | 48.4     |
| VG-LLM-8B          | 50.7     |
| Cambrian-S-3B      | 57.3     |
| Spa3-VLM-4B (Ours) | **58.6** |

Spa3-VLM leads on average, though Cambrian-S-3B is higher on several individual VSI-Bench sub-categories (원논문 Table 1).

### Cross-benchmark generalization

원논문 Table 2. Accuracy (↑). Dashes are values not reported in the source.

| Model             | CV-Bench 2D | CV-Bench 3D | CV-Bench Avg. | SPAR-Bench | ViewSpatial |
| ----------------- | ----------- | ----------- | ------------- | ---------- | ----------- |
| Qwen2.5-VL-3B     | 69.1        | 72.2        | 70.6          | 24.6       | 35.6        |
| SpatialLadder-3B  | 72.4        | 74.9        | 73.7          | 34.4       | **44.2**    |
| Spatial-MLLM-4B   | -           | -           | 73.8          | 35.1       | 43.6        |
| SpatialThinker-3B | 71.0        | 76.3        | 73.6          | -          | -           |
| SpaceR-7B         | -           | -           | -             | 37.6       | 37.3        |
| Spa3-VLM (Ours)   | **72.9**    | **78.3**    | **75.6**      | **58.4**   | 43.9        |

Spa3-VLM leads on CV-Bench and SPAR-Bench, but on ViewSpatial-Bench it trails SpatialLadder-3B (43.9 vs 44.2).

### Ablations (VSI-Bench: Numerical / Multiple-Choice / Avg.)

원논문 Table 3. Spatial representation paradigm.

| Spa. Repr. | Numerical | Multi-Choice | Avg.     |
| ---------- | --------- | ------------ | -------- |
| None       | 58.4      | 43.5         | 50.9     |
| VGGT       | 60.5      | 49.5         | 55.1     |
| Spa3R      | 60.4      | 56.8         | **58.6** |

Spa3R's unified representation gains +3.5% over feeding partial view-conditioned VGGT features.

원논문 Table 5. VLM integration architecture.

| Integration  | Numerical | Multi-Choice | Avg.     |
| ------------ | --------- | ------------ | -------- |
| None         | 58.4      | 43.5         | 50.9     |
| Seq. Append. | 58.5      | 43.7         | 51.1     |
| Cross-Attn.  | 60.4      | 56.8         | **58.6** |

Cross-attention fusion beats sequential appending by +7.5% (appending gives only marginal gains over the baseline — attributed to "modality collapse").

원논문 Table 4·6·7. Reconstruction targets, PSFM mask ratio, and camera embedding.

| Ablation setting      | Avg.     |
| --------------------- | -------- |
| Targets: VGGT only    | 57.5     |
| Targets: DINO only    | 56.7     |
| Targets: CLIP only    | 51.9     |
| Targets: VGGT + DINO  | **58.6** |
| Mask ratio 25%        | 57.5     |
| Mask ratio 50%        | **58.6** |
| Mask ratio 75%        | 58.1     |
| Camera embed: Plücker | 57.6     |
| Camera embed: PRoPE   | **58.6** |

Combining geometric (VGGT) and semantic (DINO) reconstruction targets is best; a 50% target-view mask ratio is optimal; PRoPE beats Plücker coordinates by +1.0%.

## 💡 Insights & Impact

- **Spatial intelligence from 2D alone**: PSFM argues that a unified, view-invariant spatial field can emerge from predictive modeling of unposed 2D images, without explicit 3D modalities (e.g., LiDAR) or explicit spatial instruction tuning.
- **Predictive information bottleneck**: Forcing synthesis of arbitrary novel-view features through a single latent z compels the encoder to internalize holistic 3D geometry rather than memorize input views — qualitatively, Spa3R plausibly extrapolates features for occluded/unobserved regions and a detached depth probe recovers accurate geometry.
- **Decoupling representation from reasoning**: The frozen encoder is a versatile plug-in; cross-attention fusion lets the VLM actively query spatial context while preserving its general capabilities.
- **Relative over absolute pose encoding**: PRoPE's relative camera transformation is more robust to scene-scale and coordinate-origin shifts than absolute Plücker encodings.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Geometry foundation model whose global attention Spa3R adapts (with asymmetric masking) as its View Aggregator, and a baseline whose partial view-conditioned features Spa3R outperforms.
- **[DUSt3R](../foundation/dust3r.md)**: Part of the geometry-foundation-model lineage that inspired augmenting VLMs with geometric priors.
- **[Large Spatial Model](largespatialmodel.md)**: Related unposed-images-to-semantic-3D approach cited in this space.
- VLM-3R, Spatial-MLLM, VG-LLM (not in this collection): contemporary methods that inject partial view-conditioned geometry into VLMs — the very bottleneck Spa3R targets.

## 📚 Key Takeaways

1. Spa3R learns a unified, view-invariant spatial representation by predicting feature fields for arbitrary novel views (PSFM), a self-supervised objective over unposed multi-view images.
2. Its Asymmetric View Aggregator (adapted VGGT) plus a PRoPE-conditioned decoder synthesize spatially aligned geometric and semantic target features.
3. Spa3-VLM injects the frozen encoder into Qwen2.5-VL via a Residual Cross-Attention Adapter, reaching 58.6% average on VSI-Bench — state of the art on average, while trailing on a few individual sub-tasks and on ViewSpatial-Bench.
4. Ablations show the unified representation (+3.5% over view-conditioned VGGT), cross-attention fusion (+7.5% over appending), combined geometric+semantic targets, a 50% mask ratio, and PRoPE (+1.0%) each matter.

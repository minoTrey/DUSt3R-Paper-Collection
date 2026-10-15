# GroupForward: Building Referable 3D Scenes via Instance-Grouped Feed-Forward Gaussian Splatting (arXiv 2026)

## 📋 Overview

- **Authors**: Qijian Tian, Zimeng Wu, Xuhong Wang, Lizhuang Ma, Xin Tan
- **Institution**: Shanghai Jiao Tong University, Beihang University, Shanghai Artificial Intelligence Laboratory, East China Normal University
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.17535)
- **Verification**: UNKNOWN (2026-10-15; source 2608.17535v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Group Gaussians into 3D instances through compact embeddings instead of storing large semantic features per Gaussian, then use group semantics/relations for language grounding.

## 🎯 Key Contributions

1. Predict geometry, appearance and instance embeddings feed-forward.
2. Aggregate semantics through instance prototypes.
3. Connect 3D scene graphs and VLMs for referential reasoning.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Sparse unposed/uncalibrated RGB views, plus referring expressions for grounding tasks.
- **Output**: Instance-grouped Gaussian scenes, semantic renderings and referred-object 3D groups/masks.
- **Problem**: Category features struggle to distinguish same-category objects, while per-Gaussian high-dimensional semantics are costly.

### Method

1. Predict cameras, depth and primitives through shared encoders and geometry/Gaussian decoders.
2. Cluster cross-view Gaussians using compact instance embeddings.
3. Aggregate input-view open-vocabulary features into group prototypes.
4. Retrieve scene-graph candidates and let VLMs combine structure, appearance and relations to choose targets.

Train gauge-aligned self-rendering and rendering-consistent instance learning progressively. VLM reasoning differs from a single reconstruction-network head.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.17535v1), Table II, PDF p.7.

ScanNet novel-view semantic segmentation/NVS, 4 input views. Higher mIoU/PSNR is better.

| Method       | mIoU ↑ | PSNR ↑ |
| ------------ | ------ | ------ |
| Uni3R        | 0.5443 | 25.32  |
| GroupForward | 0.5868 | 27.14  |

This table covers category segmentation/rendering; referring-expression success uses separate Table IV. Semantic-model choices also affect performance.

## 💡 Insights & Impact

Use persistent 3D instances, rather than pixels/categories, as the basic referable scene units.

- Clustering errors propagate to semantics and grounding.
- VLM/semantic-model errors and extra costs remain.

## 🔗 Related Work

- [IGGT](iggt.md): instance-grounded geometry background.
- [Splatt3R](../gaussian-splatting/splatt3r.md): feed-forward Gaussian background.

## 📚 Key Takeaways

1. Group Gaussians into objects with compact embeddings.
2. Transfer semantics at instance level.
3. Evaluate segmentation and referring-expression understanding separately.

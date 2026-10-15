# PanoSeg3R: Feed-Forward 3D Semantic Segmentation for Panoramic Images with an Automatic Data Curation Pipeline (arXiv 2026)

## 📋 Overview

- **Authors**: Heechan Yoon, Dongki Jung, Phuc Nguyen, Ming Lin, Dinesh Manocha
- **Institution**: University of Maryland, College Park
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.22687)
- **Verification**: UNKNOWN (2026-10-15; source 2609.22687v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Add semantic-query decoders and low-level ERP features to Wid3R panoramic-ray geometry, training with automatically generated panorama labels.

## 🎯 Key Contributions

1. Jointly process panoramas without perspective-cubemap conversion.
2. Predict masks/classes with shared semantic queries and text embeddings.
3. Scale pseudo-semantic annotation through foundation-model pipelines.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Overlapping multi-view equirectangular RGB panoramas.
- **Output**: Geometry, view-consistent semantic masks and 3D semantic point clouds.
- **Problem**: Applying perspective models to panorama fragments can disrupt boundary and wide-FoV semantic/geometric consistency.

### Method

1. Extract rays, radial distances and multi-view features with Wid3R.
2. Refine semantic instances through shared query decoders.
3. Add circular-padding image stems to DPT features for ERP detail.
4. Classify masks with SigLIP embeddings and project semantics onto geometry.

Use official semantic GT and automatic pseudo-labels. VLM validation does not make pseudo-labels equivalent to manual GT.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.22687v1), Table 2, PDF p.5.

ScanNet++ scene-level 3D semantic segmentation. Perspective baselines evaluate six cubemap faces per panorama.

| Method           | 3D mIoU ↑ | 3D mAcc ↑ |
| ---------------- | --------- | --------- |
| PanSt3R, cubemap | 9.26      | 12.12     |
| PanoSeg3R        | 17.28     | 22.56     |

Not all panorama-specific models are beaten in 2D segmentation. The 3D evaluation includes cloud alignment, unlike absolute placement.

## 💡 Insights & Impact

Preserve panoramic-geometry features and supervision through semantic prediction.

- Pseudo-label class confusion and ERP distortion remain.
- Mainly indoor-panorama benchmarks; outdoor/other-camera transfer is separate.

## 🔗 Related Work

- [IGGT](iggt.md): perspective instance-geometry comparisons.
- [MEOW](../reconstruction/meow.md): mixed-camera geometry is a different semantic task.

## 📚 Key Takeaways

1. The actual backbone is Wid3R.
2. Combine ERP detail with query masks.
3. Distinguish pseudo-label training from GT evaluation.

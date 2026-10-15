# PhysVGGT: Feed-Forward Dense Physical Property Estimation from A Single Image (arXiv 2026)

## 📋 Overview

- **Authors**: Sneha Paul, Guile Wu, Bingbing Liu, Dongfeng Bai
- **Institution**: Huawei Noah’s Ark Lab, Concordia University, Huawei Foundation Model Department
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.18920)
- **Verification**: UNKNOWN (2026-10-15; source 2609.18920v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Predict dense friction, hardness, elasticity and density maps plus object mass from geometry tokens, using material pseudo-labels and catalog weights during training.

## 🎯 Key Contributions

1. Formulate physical properties as per-pixel predictions.
2. Learn inter-property relationships through latent attention.
3. Regress object mass with a separate global head.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Single RGB image.
- **Output**: Friction, Shore hardness, Young's modulus and density maps, plus object mass.
- **Problem**: Monocular appearance cannot determine physical properties exactly; scene optimization and inference-time VLM queries are costly.

### Method

1. Convert frozen geometry-encoder tokens into DPT dense features.
2. Exchange property features through shared encoder–decoders and cross-property coupling.
3. Predict dense maps with property-specific heads.
4. Predict catalog-supervised mass through token pooling and MLPs.

Build dense supervision from SAM2 parts, VLM material/hardness labels, engineering lookups and empirical relations. These are not fully measured physical-property GT; mass comes separately from ABO catalogs.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.18920v1), Table 1, PDF p.7.

ABO-500, held-out 100 test objects. ADE is in kg; ALDE is logarithmic error; MnRE is min-of-ratio score, with higher better.

| Method   | ADE (kg) ↓ | ALDE ↓ | MnRE ↑ |
| -------- | ---------- | ------ | ------ |
| AURA     | 8.33       | 0.582  | 0.634  |
| PhysVGGT | 4.73       | 0.574  | 0.655  |

Mass tables and NeRF2Physics sparse friction/hardness measurements are different benchmarks. Grasp forces computed from predicted friction do not guarantee safety in actual contact experiments.

## 💡 Insights & Impact

Monocular property outputs are estimates based on geometry/material priors, not direct measurements.

- Pseudo-label and material-table assumptions enter predictions.
- Hidden materials, hollow structures and actual contact conditions are difficult to identify from appearance alone.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): geometry-aware representations.
- [IGGT](iggt.md): extending geometry features to dense tasks.

## 📚 Key Takeaways

1. Dense properties and global mass use separate branches.
2. Distinguish measurements from pseudo-labels.
3. Do not describe benchmark estimates as actual property measurements.

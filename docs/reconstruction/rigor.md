# RIGOR: Rig-Informed Geometry for Omnidirectional Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Tingjun Huang, Dmitry Rudshin, Mathieu Meyer, Pietro Bonazzi, Marc Pollefeys, Emilia Szymańska
- **Institution**: ETH Zürich, Hilti AG
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.13504)
- **Verification**: UNKNOWN (2026-10-15; source 2609.13504v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Split gravity-aligned panoramas into a known perspective-view virtual rig, then repair frozen DA3 predictions with rig constraints and loop graphs.

## 🎯 Key Contributions

1. Use DA3 without panorama-specific retraining.
2. Repair local predictions using known co-centered view rotations.
3. Verify loops through cyclic retrieval and joint geometric checks.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Gravity-aligned panoramas, known virtual-view rotations, and dynamic/device masks.
- **Output**: Long camera trajectories and fused dense point clouds.
- **Problem**: Repeated structures and weak texture in long construction-site videos produce local inconsistency and global drift.

### Method

1. Render several perspective views sharing a panorama's optical center.
2. Apply frozen DA3 to overlapping blocks.
3. Check virtual-rig consistency and apply accepted pose/pointmap corrections.
4. Optimize capture-level retrieval and verified loops in a Sim(3) graph, then perform owner-point fusion.

No panorama-specific training is needed, but gravity alignment, known virtual rigs and graph optimization are required. Co-centered rigs directly provide neither stereo parallax nor metric scale.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.13504v2), Table 2, PDF p.7.

Hilti–Trimble–Oxford: medians over 30 trajectories and 29 LiDAR geometry sequences. ATE uses SE(3) alignment; ROI geometry uses GT-assisted Sim(3) plus scale-adjusting ICP.

| Method     | ATE (m) ↓ | ROI CD (m) ↓ | F@25cm ↑ |
| ---------- | --------- | ------------ | -------- |
| DA3-Legacy | 2.704     | 0.155        | 0.833    |
| RIGOR      | 2.312     | 0.132        | 0.873    |

Cloud alignment evaluates reconstructed shape, not metric scale or absolute map placement. ATE does not improve in every run.

## 💡 Insights & Impact

Use known capture structure for prediction repair and loop verification instead of model retraining.

- Incorrect gravity leveling or virtual-rig assumptions destabilize corrections.
- Some difficult baselines are qualitative-only, limiting quantitative comparison coverage.

## 🔗 Related Work

- [Depth Anything 3](depth-anything-3.md): frozen predictor.
- [MEOW](meow.md): a different approach learning camera adaptation.

## 📚 Key Takeaways

1. Virtual rigs supply relative rotations but no baseline.
2. Combine local repair with global loop optimization.
3. Trajectories and clouds use different alignment protocols.

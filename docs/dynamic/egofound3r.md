# EgoFound3R: End-to-End Egocentric Hand Reconstruction in World Space with Point-Wise Interaction Attributes (arXiv 2026)

## 📋 Overview

- **Authors**: Hongming Fu, Jingcheng Shi, Wenjia Wang, Binhua Zuo, Bo Zhao
- **Institution**: Shanghai Jiao Tong University, QuicRobot, Rutgers University, University of Hong Kong
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.01210)
- **Verification**: UNKNOWN (2026-10-15; source 2610.01210v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Hand root, joint and surface queries prompt frozen VGGT-Ω to predict hand geometry, visibility, contact and distance in the scene's metric frame.

## 🎯 Key Contributions

1. Reuse scene geometry priors through structured hand prompts.
2. Decode explicit hand points together with interaction attributes.
3. Control computation with separate hand and scene update rates.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Egocentric RGB video.
- **Output**: World-space hand geometry, per-point visibility, contact and surface distance, plus cameras and scene scale.
- **Problem**: Hand crops alone cannot resolve occlusion and camera motion; chaining models can destabilize scale and throughput.

### Method

1. Build hand prompts from VGGT-Ω's shared DINOv3 features.
2. Exchange information between hands with a bidirectional temporal transformer.
3. Pool fast hand observations into slower scene anchors.
4. Produce shared-world-frame outputs through hand decoders, scene heads and metric heads.

Freeze the backbone and train prompts, adapters and prediction heads. Rows marked † or ‡ use camera GT and must be distinguished from the default.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2610.01210v2), Table 2, PDF p.7.

TACO joint-level contact prediction. Geometry-based baselines receive GT geometry and use different contact conventions, as the paper states.

| Method     | Precision ↑ | Recall ↑ | F1 ↑  |
| ---------- | ----------- | -------- | ----- |
| ContactOpt | 0.557       | 0.197    | 0.259 |
| EgoFound3R | 0.654       | 0.777    | 0.697 |

Contact performance does not establish world-placement accuracy. Large HOI4D world-space MPJPE errors remain; do not mix these with camera-frame or aligned results.

## 💡 Insights & Impact

Read local hand geometry in scene context and attach interaction labels to the same points.

- Metric-scale and camera errors propagate to world-space hands.
- Multi-rate interpolation and contact definitions affect results.

## 🔗 Related Work

- [VGGT-Ω](../reconstruction/vggt-omega.md): frozen backbone.
- [WildHSR](wildhsr.md): metric reconstruction of people and scenes.

## 📚 Key Takeaways

1. Output geometry and interaction attributes together.
2. Update hands and scenes at different rates.
3. Evaluate contact and world placement separately.

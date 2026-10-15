# WildHSR: Metric Feed-Forward 4D People-Scene Reconstruction from a 3D Foundation Model (arXiv 2026)

## 📋 Overview

- **Authors**: Jerrin Bright, John Zelek
- **Institution**: University of Waterloo
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.29106)
- **Verification**: UNKNOWN (2026-10-15; source 2609.29106v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Add metric-scale and person-identity readouts to VGGT-Ω's up-to-scale geometry, linking people, scenes and cameras in a shared metric frame.

## 🎯 Key Contributions

1. Generate web-video scale pseudo-labels using bodies as rulers.
2. Read person correspondences from intermediate query–key features.
3. Associate identities through metric pelvis motion and dustbin-aware matching.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Dynamic monocular RGB video.
- **Output**: Metric cameras and scenes, persistent person tracks and SMPL-X bodies.
- **Problem**: Up-to-scale geometry lacks absolute scale and person identity across windows.

### Method

1. Add small LoRA modules and Scale Readout to VGGT-Ω window features.
2. Pretrain scale with offline body/keypoint pseudo-labels, then refine with actual metric annotations.
3. Combine pelvis readouts and human tokens through cross-attention.
4. Compute Sinkhorn associations from intermediate correspondences, pelvis motion and confidence to merge windows.

After web-video pseudo-supervision, fine-tune on exact metric training splits of RICH and 3DPW. This differs from supplying body rulers or teachers again at inference.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.29106v1), Table 4, PDF p.8.

Held-out 3DPW: camera-frame errors over 14 joints and mesh PVE, in mm. PA-MPJPE is measured after per-person similarity alignment.

| Method  | PA-MPJPE ↓ | MPJPE ↓ | PVE ↓ |
| ------- | ---------- | ------- | ----- |
| SHOW    | 41.0       | 67.7    | 78.7  |
| WildHSR | 38.7       | 65.2    | 74.4  |

This table does not evaluate world placement. Global-motion tables on EMDB/RICH show higher W error than some optimization methods, and RICH RTE is not always best.

## 💡 Insights & Impact

Read geometry scale and person correspondence from one foundation representation through separate readouts.

- Omitting exact metric training supervision can misleadingly imply zero-shot metric estimation.
- Occlusion, multi-person association and window-merging errors remain.

## 🔗 Related Work

- [VGGT-Ω](../reconstruction/vggt-omega.md): the base representation.
- [Human3R](human3r.md): human–scene reconstruction comparisons.

## 📚 Key Takeaways

1. Scale and identity are separate missing outputs.
2. Exact metric training follows pseudo-label training.
3. Separate local-body scores from global-placement scores.

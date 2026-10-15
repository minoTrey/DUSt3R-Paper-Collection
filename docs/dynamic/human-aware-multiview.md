# Feed-Forward Multi-view Multi-person Reconstruction with Contrastive Human-Aware 3D Representation (arXiv 2026)

## 📋 Overview

- **Authors**: Yuanwang Yang, Buzhen Huang, Zongxuan Ren, Jing Huang, Kun Li
- **Institution**: Tianjin University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.00745)
- **Verification**: UNKNOWN (2026-10-15; source 2609.00745v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Aggregate observations of multiple people in a VGGT-initialized shared 3D feature space, then jointly predict cameras, associations and SMPL with instance contrastive learning.

## 🎯 Key Contributions

1. Maintain a human-aware, view-agnostic 3D representation.
2. Contrastively align cross-view and cross-modal features of the same person.
3. Jointly estimate cameras and articulated shapes of multiple people.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Multiple uncalibrated RGB views.
- **Output**: Camera parameters, per-person SMPL bodies and poses, and shared scene placement.
- **Problem**: Occlusion makes cross-view matching and person identification difficult in 2D.

### Method

1. Lift pixels into 3D using VGGT depth, cameras, features and confidence.
2. Fuse spatial neighbors through confidence-weighted soft aggregation.
3. Bring the same person's geometry, appearance and semantic features together while separating different people.
4. Regress cameras and body parameters from human-aware 3D features in a feed-forward pass.

Training uses human-instance, body and camera supervision. Distinguish the pretrained prior for initializing the 3D representation from additional contrastive training.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.00745v1), Table 1, PDF p.16.

OcMotion human reconstruction; MPJPE-family metrics are in m. CA means camera-aligned and PA means per-person Procrustes-aligned error; these measure different properties.

| Method   | CA-MPJPE (m) ↓ | PA-MPJPE (m) ↓ |
| -------- | -------------- | -------------- |
| HSfM     | 0.35           | 0.05           |
| Proposed | 0.19           | 0.04           |

The OcMotion table uses a single-person setting with severe object occlusion. For multi-person spatial relationships, see the separate EgoHumans table and group alignment. Some alignment names in the paper are ambiguous, so the alignment target is stated explicitly.

## 💡 Insights & Impact

Jointly estimate cameras and people through instance features in a shared 3D space rather than solving matching sequentially.

- Initial depth, camera and body-prior errors can propagate.
- Aligned joint error alone does not establish absolute person-placement accuracy.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): initialization of 3D features.
- [Human3R](human3r.md): context for human-centered reconstruction.

## 📚 Key Takeaways

1. Aggregate observations in a shared, person-specific 3D space.
2. Contrastive learning supports cross-view identity association.
3. Distinguish person, group and camera alignment.

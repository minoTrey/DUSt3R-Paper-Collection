# Zero-Shot Novel Depth Synthesis Using 3D Foundation Models Scene Representations (arXiv 2026)

## 📋 Overview

- **Authors**: Denis M. Akola, David F. Fouhey
- **Institution**: New York University, Tandon School of Engineering, Courant Institute of Mathematical Sciences
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.04174)
- **Verification**: UNKNOWN (2026-10-15; source 2609.04174v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Conditionally generate target-camera latents from 3D-foundation scene tokens, then decode unseen-view geometry through existing depth heads.

## 🎯 Key Contributions

1. Probe hidden-surface information through layered depth.
2. Diffuse in geometry-token space rather than pointmap space.
3. Generate novel depth conditioned on source tokens and relative target pose.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Source RGB views and target camera poses relative to the source.
- **Output**: Depth and pointmaps for unobserved target views.
- **Problem**: Visible-surface reconstruction alone cannot readily answer queries about occluded structure from new viewpoints.

### Method

1. Extract source tokens with frozen VGGT or WorldMirror.
2. Use multiple source layers as context and generate selected target-layer tokens from noise.
3. Condition target geometry with pose encoders and DiT cross-attention.
4. Decode sampled representations into depth through a DPT head.

Train diffusion and pose conditioning on large multi-view datasets. Zero-shot in the title means transfer to new datasets, not absence of training.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.04174v1), Table 3, PDF p.13.

One source → one target novel-view depth. These are out-of-domain AbsRel results for the VGGT direct-depth baseline and Z3D-VGGT.

| Dataset  | VGGT-DD ↓ | Z3D-VGGT ↓ |
| -------- | --------- | ---------- |
| DTU      | 0.022     | 0.012      |
| 7-Scenes | 0.274     | 0.260      |
| NRGBD    | 0.192     | 0.260      |

Results are worse on NRGBD. Point-cloud accuracy/completeness and depth use separate tables; no single metric establishes generation's factual accuracy.

## 💡 Insights & Impact

Reuse geometry-backbone representations as a latent generation space for new views.

- Limited overlap harms fine geometry.
- Hidden surfaces are plausible completions, not observed GT.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md), [WorldMirror](../reconstruction/worldmirror.md): backbone.
- [JUSt3R](../reconstruction/just3r.md): generates pointmaps through flow rather than these latents.

## 📚 Key Takeaways

1. Generate new depth from source tokens and target poses.
2. Distinguish zero-shot from training-free.
3. Preserve domain-specific failures and completeness trade-offs.

# Colon3R: Cross-Domain 3D Reconstruction from Monocular Colonoscopic Video (arXiv 2026)

## 📋 Overview

- **Authors**: Zhihao Xing, Yingyu Wang, Liang Zhao, Shoudong Huang
- **Institution**: Not stated in the source; author affiliations require separate confirmation.
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.23961)
- **Verification**: UNKNOWN (2026-10-15; source 2609.23961v3 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Adapt phantom/simulation-trained VGGT to unlabeled in-vivo colonoscopy through teacher–student learning while limiting loss of source geometry.

## 🎯 Key Contributions

1. Retain source-geometry supervision during adaptation.
2. Gate EMA-teacher updates by scale stability and support.
3. Weight cross-view supervision with sequence-, pair- and pixel-level reliability.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Monocular colonoscopy RGB sequences; training uses labeled phantom/simulation and unlabeled in-vivo video.
- **Output**: Cameras, depth, pointmaps and multi-view reconstructions.
- **Problem**: Tissue deformation, specularity and limited overlap can defeat both source-only models and unrestricted pseudo-label adaptation.

### Method

1. Learn source-supervised camera/depth/pointmap priors from VGGT.
2. Update late-attention LoRA and heads on a frozen backbone with different source/target scopes.
3. Apply hierarchical reliability to teacher cross-view pseudo-supervision.
4. Update the EMA teacher only with reliable support and stable scale.

This is semi-supervised domain adaptation without geometric GT from the in-vivo target; it is not entirely unsupervised.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.23961v3), Table II, PDF p.7.

Adaptation ablation. In-vivo CV is an unweighted cross-view consistency residual, not actual GT error. C3VD depth Rel measures source-domain retention.

| Variant         | In-vivo CV ↓ | C3VD depth Rel ↓ |
| --------------- | ------------ | ---------------- |
| Fine-tuned VGGT | 0.0764       | 0.0608           |
| Uniform EMA     | 0.0435       | 0.0862           |
| Colon3R         | 0.0479       | 0.0675           |

Uniform EMA has lower CV alone; source fine-tuning has lower C3VD depth error alone. The proposed method balances these objectives, without proving in-vivo absolute geometry accuracy.

## 💡 Insights & Impact

Minimizing target consistency alone can damage geometry priors; evaluate adaptation and retention together.

- Without in-vivo dense GT, actual geometry accuracy cannot be directly quantified.
- Quasi-rigid reliability does not fully model large tissue deformations.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md): source backbone.
- [Endo3R](endo3r.md): endoscopic geometry comparisons.

## 📚 Key Takeaways

1. Combine source labels with unlabeled targets.
2. Gate teacher updates themselves.
3. Do not confuse consistency residuals with GT errors.

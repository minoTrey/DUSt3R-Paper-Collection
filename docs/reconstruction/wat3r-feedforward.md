# WAT3R: Feedforward Underwater 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Jiayi Xu, Jiahao Lu, Ziqiang Zheng, Yihao Tan, Yaolong Zhu, Yuan Liu, Sai-Kit Yeung
- **Institution**: Hong Kong University of Science and Technology, Chinese University of Hong Kong, Peking University
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.21023)
- **Verification**: UNKNOWN (2026-10-15; source 2607.21023v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Jointly model underwater attenuation/scattering and geometry, adapting feed-forward reconstruction poses through restored clean-view consistency.

## 🎯 Key Contributions

1. Add degradation adaptation to a π3-family geometry branch.
2. Generate supervised adaptation data through physical underwater-image formation.
3. Refine poses through clean-view warping on real imagery.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Multiple underwater RGB images or video.
- **Output**: Pixel-aligned pointmaps, camera poses, depth, clean images and water optical parameters.
- **Problem**: Color attenuation and backscatter disrupt cross-view feature consistency, defeating terrestrial geometry models.

### Method

1. Share features between geometry, clean-image and water-parameter heads.
2. Synthesize water effects on imagery with GT geometry for point/camera/radiometric supervision.
3. Warp clean images using predicted depth/poses on real underwater sequences.
4. Mask occlusions/dynamic regions and adapt camera predictions with clean-view photometric consistency.

Synthetic supervised adaptation precedes real-data self-supervised adaptation. Underwater optics provide soft regularization, not perfect hard constraints. This is a different-author paper from Wat3R (2607.08772).

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2607.21023v1), Table 1, PDF p.7.

FLSea-Canyons multi-view depth with scale-only alignment. δ is the fraction of pixels whose GT-relative ratio error meets the threshold.

| Method | AbsRel ↓ | δ < 1.25 ↑ |
| ------ | -------- | ---------- |
| π3     | 0.0891   | 0.9613     |
| DA3    | 0.0943   | 0.9345     |
| WAT3R  | 0.0725   | 0.9726     |

Not every SQUID scale-and-shift metric is best. USOD10K depth references are DPT pseudo-depth, not sensor GT.

## 💡 Insights & Impact

Use color restoration as geometry-adaptation supervision rather than only preprocessing.

- Simplified water models do not explain all real scattering.
- Pseudo-depth results do not establish physical depth accuracy.

## 🔗 Related Work

- [π3](pi3.md): the geometry-branch base.
- [Swimm3R](../gaussian-splatting/swimm3r.md): another underwater approach including SfM/splatting.

## 📚 Key Takeaways

1. Distinguish same-name Wat3R papers by arXiv ID.
2. Clean-view consistency supports pose adaptation.
3. Preserve alignment and depth-reference provenance.

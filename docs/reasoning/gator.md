# GATOR: Generative and Agentic 3D Object Reconstruction From Casual Images (arXiv 2026)

## 📋 Overview

- **Authors**: Qirui Wu, Stan Birchfield, Hesam Rabeti, Angel X. Chang, Bowen Wen
- **Institution**: NVIDIA, Simon Fraser University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.11215)
- **Verification**: UNKNOWN (2026-10-15; source 2610.11215v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Follow an object generator conditioned on RGB, masks and Pi3X pointmaps with observation-driven edit–render–review agents to refine scene-aligned textured assets.

## 🎯 Key Contributions

1. Separate targets and scenes with patch-aligned modality mixing.
2. Condition structure, geometry and appearance generation separately on text.
3. Initialize agents with generated assets, then edit structure and texture.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Casual RGB images, target masks/categories/captions, and estimated cameras/pointmaps.
- **Output**: Completed textured object assets and scene-relative poses.
- **Problem**: Object completion invents hidden surfaces, but target placement, structure and text textures can disagree with observations in clutter.

### Method

1. Estimate cameras/depth with Pi3X and mix RGB/mask/pointmap features patchwise.
2. Generate structure, geometry and appearance through a TRELLIS.2-family cascade.
3. Condition categories/captions through stage-specific semantic adapters.
4. Supply generated assets to agents for repeated targeted edits comparing renders with observations.

Generative adaptation differs from inference-time agent refinement. This directly conditions an application on geometry rather than training a new geometry backbone.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2610.11215v1), Table 1, PDF p.7.

Toys4K four-view object reconstruction. Normalize CD by reference diameter; use geometry alignment and shared lighting protocols.

| Method     | Normalized CD ↓ | Normal consistency ↑ | F1 ↑  | PSNR ↑ |
| ---------- | --------------- | -------------------- | ----- | ------ |
| Pixal3D-MV | 0.011           | 0.783                | 0.701 | 17.18  |
| GATOR      | 0.009           | 0.801                | 0.757 | 17.60  |

Both methods share Pi3X geometry estimates. Compare generator-only, agent-only and full-framework time budgets separately.

## 💡 Insights & Impact

Geometry-conditioned generation supplies instance-specific initializations, letting agents focus on concrete observation-based edits.

- Hidden surfaces reflect generative priors, not measured object interiors.
- Agents, proprietary models and tool budgets affect reproducibility and runtime.

## 🔗 Related Work

- [π3](../reconstruction/pi3.md): the Pi3X geometry-conditioning family.
- [SPOON](spoon.md): another framework connecting generated objects to scene layouts.

## 📚 Key Takeaways

1. Geometry models condition object generation.
2. Agents edit after generative initialization.
3. Preserve normalized distances and time budgets.

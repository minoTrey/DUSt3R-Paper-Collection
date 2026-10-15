# Pose-Free Feed-Forward 3D Inpainting via Learnable Mask Attention and Support Token Refinement (arXiv 2026)

## 📋 Overview

- **Authors**: Jingyi Pan, Dan Xu, Qiong Luo
- **Institution**: Hong Kong University of Science and Technology Guangzhou, Hong Kong University of Science and Technology
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.11857)
- **Verification**: UNKNOWN (2026-10-15; source 2610.11857v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Adapt DA3 attention to masked multi-view inputs, then selectively reinject generated support tokens into evidence-poor regions for 3D inpainting.

## 🎯 Key Contributions

1. Update layerwise mask suppression according to features.
2. Identify blind spots through rendered opacity.
3. Inject diffusion-support-view tokens with confidence weighting.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Unposed RGB source images, masked regions and reference views.
- **Output**: Cameras, completed geometry and an inpainted Gaussian scene.
- **Problem**: Masked tokens contaminate pose/geometry correspondence; severe occlusion leaves insufficient evidence for one network pass.

### Method

1. Initialize key-side biases in DA3 attention with masks.
2. Adjust suppression progressively through learned layers.
3. Render initial Gaussians and find low-opacity masked regions.
4. Generate support views with SDEdit/IP-Adapter and reinject tokens according to blind-spot confidence.

Adapt using depth pseudo-GT from an unmasked DA3 teacher and rendering losses. Enabling support generation changes time and information relative to a basic forward pass.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2610.11857v1), Table 1, PDF p.6.

SPIn-NeRF novel-view image metrics. These are published per-scene-optimization baseline and FreeInpaint results; camera preparation and pipeline stages differ.

| Method      | PSNR ↑ | LPIPS ↓ |
| ----------- | ------ | ------- |
| GScream     | 16.85  | 0.3644  |
| FreeInpaint | 17.79  | 0.2819  |

Distinguish the approximately 0.4-second basic forward pass from approximately 1.8-second support refinement. Generated support is not a real new observation.

## 💡 Insights & Impact

Preserve coordinate anchors from reliable observations while controlling masked-region participation and generated evidence.

- Diffusion priors can invent content inconsistent with actual hidden geometry.
- Opacity confidence is not a probability of factual or physical accuracy.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): backbone·teacher.
- [DensiTok](densitok.md): another approach connecting generated evidence through tokens.

## 📚 Key Takeaways

1. Learn to prevent masks from corrupting pose and geometry.
2. Add support tokens only to blind spots.
3. Separate generation/re-inference costs from single-pass runtime.

# FLAT: Feedforward Latent Triangle Splatting for Geometrically Accurate Scene Generation (arXiv preprint 2026-06)

![flat — architecture](https://arxiv.org/html/2606.24876v1/x1.png)

_Pipeline: Starting from a single image, we construct a point-cloud-based control video by rendering along the target camera trajectory (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Orest Kupyn, Goutam Bhat, Philipp Henzler, Fabian Manhardt, Christian Rupprecht, Federico Tombari
- **Institution**: Google Research; University of Oxford, Visual Geometry Group; TU Munich
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.24876) | [Project Page](https://flat-splat.github.io)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first method to decode explicit _triangle splats_ (surface-aligned, non-volumetric primitives) directly from a frozen video diffusion model's latents in a single forward pass, giving geometrically accurate, game-engine-convertible scenes from a single image — enabled by a ray-centered rotation parameterization and a product window function that fixes the poor gradient flow of flat primitives.

## 🎯 Key Contributions

1. **Triangle splats from video-diffusion latents**: First demonstration that explicit, non-volumetric surface primitives can be decoded directly from compressed video-diffusion latents in one forward pass, formulating how to parameterize and train feedforward flat-primitive decoding.
2. **Stable parameterization + window function**: A ray-centered local triangle parameterization (constrained Cholesky-style 2D shape + residual orientation around a ray-aligned frame) and a novel product window function that routes gradients to all three vertices and extends support beyond the boundary.
3. **Systematic representation comparison**: The first apples-to-apples comparison of 3DGS, 2DGS, and triangle splatting under identical latent-decoding conditions, characterizing the rendering-quality vs geometric-accuracy vs mesh-compatibility trade-offs.

## 🔧 Technical Details

### Pipeline

A frozen camera-conditioned latent video diffusion model (Uni3C, built on Wan-2.1) takes a single image + target camera trajectory and produces denoised video latents. A feedforward scene decoder — the reused Wan-2.1 RGB VAE decoder backbone, with camera conditioning via zero-convolution blocks and the last upsampling stage removed so each token predicts a triangle for a 2×2 pixel area — maps latents to triangle-splat parameters. Camera is encoded as dense per-pixel RPPC ray embeddings (Plücker moment replaced by the closest point on the ray to the world origin), encoded through the pretrained VAE.

### Triangle parameterization

Each token predicts a ray-centered triangle: center at `r_o + D·r_d`; 2D shape from a canonical equilateral triangle transformed by a lower-triangular (Cholesky-style) matrix with positive diagonal (guaranteeing positive area, avoiding degenerate triangles); orientation from two residual tilt angles + an in-plane spin around a ray-tangent frame (more stable than predicting a full quaternion, which caused divergence). The window function normalizes each edge's signed distance by the inradius, applies a shifted clamp (ε extends support past the boundary), and multiplies the three edge responses raised to a sharpness σ — avoiding the max-reduction of the original triangle-splatting formulation.

### Training

- Uni3C generates 49–81 frames at 432×768; VAE downsamples temporally by 4 and spatially by 8. Decoder trained in four progressive stages (320→768p), AdamW lr 1e-4, 8× H100, 200,000 iterations.
- Loss `L = λ_rgb L2 + λ_perc LPIPS + λ_D L_D + λ_N L_N + λ_O L_O` with λ_rgb=1.0, λ_perc=0.5, λ_D=0.01, λ_N=0.01, λ_O=0.001 (scale-invariant disparity depth loss; normals supervised via NormalCrafter pseudo-GT; triangles with opacity <40% removed).
- Data: RealEstate10K, DL3DV, and 25,000 S3OD images with synthesized Uni3C videos; metric poses/depth from MapAnything.
- Optional opaque-mesh conversion (σ=0.5 start): refine geometry/color/opacity, then 50 iterations pushing opacity toward binary, densify near boundaries, stitch nearest boundary vertices, and repair.

## 📊 Results

Benchmarks: RealEstate10K and DL3DV. Metrics: PSNR↑, SSIM↑, LPIPS↓; geometry via rendered-vs-GT normals (L1↓, Cosine↑, evaluated with Metric3D-v2 to reduce bias). The 3DGS/2DGS variants use identical training.

원논문 Table 1 (novel view synthesis and geometry quality; geometry averaged over both datasets).

| Method      | Representation | RE10K PSNR↑ | SSIM↑ | LPIPS↓ | DL3DV PSNR↑ | SSIM↑ | LPIPS↓ | Geo L1↓ | Geo Cosine↑ |
| ----------- | -------------- | ----------- | ----- | ------ | ----------- | ----- | ------ | ------- | ----------- |
| ZeroNVS     | 3DGS           | 13.01       | 0.378 | 0.448  | 13.35       | 0.339 | 0.465  | –       | –           |
| ViewCrafter | 3DGS           | 16.84       | 0.514 | 0.341  | 15.53       | 0.525 | 0.352  | –       | –           |
| Wonderland  | 3DGS           | 17.15       | 0.550 | 0.292  | 16.64       | 0.574 | 0.325  | –       | –           |
| Bolt3D      | 3DGS           | 21.54       | 0.747 | 0.234  | -           | -     | -      | –       | –           |
| Lyra        | 3DGS           | 21.79       | 0.752 | 0.219  | 20.09       | 0.583 | 0.313  | –       | –           |
| FLAT        | 3DGS           | 22.39       | 0.762 | 0.203  | 20.71       | 0.663 | 0.275  | 0.686   | 0.116       |
| FLAT        | 2DGS           | 22.03       | 0.734 | 0.219  | 20.44       | 0.647 | 0.284  | 0.388   | 0.587       |
| FLAT        | Triangles      | 21.45       | 0.710 | 0.245  | 20.04       | 0.627 | 0.314  | 0.211   | 0.853       |

The core trade-off is explicit: FLAT's own 3DGS variant is the best on visual metrics (and beats all prior methods), but produces near-random normals (cosine 0.116); the Triangles variant gives the best geometry (cosine 0.853, L1 0.211) at a modest visual cost. 3DGS is described as an approximate upper bound for rendering quality.

원논문 Table 2 (opaque mesh conversion).

| Representation | Conversion | Vertices | RE10K PSNR↑ | SSIM↑ | LPIPS↓ | DL3DV PSNR↑ | SSIM↑ | LPIPS↓ |
| -------------- | ---------- | -------- | ----------- | ----- | ------ | ----------- | ----- | ------ |
| 2DGS           | TSDF       | 5M       | 15.89       | 0.633 | 0.468  | 12.00       | 0.433 | 0.563  |
| 3DGS           | GS2Mesh    | 4M       | 14.18       | 0.619 | 0.452  | 12.31       | 0.465 | 0.541  |
| Triangles      | Ours       | 0.5M     | 21.23       | 0.749 | 0.388  | 19.71       | 0.609 | 0.466  |

The triangle mesh gives a >7 dB PSNR gain over 3DGS meshes on RealEstate10K (21.23 vs 14.18) with ~10× fewer vertices (0.5M vs 4–5M), and TSDF/marching-cubes extraction fails on most sparse-view scenes.

원논문 Table 3 (ablation). The Global-rotation row diverges (values shown as inequalities in the paper).

| Architecture | Window Function    | Representation | Rotation | RE10K PSNR↑ | SSIM↑ | LPIPS↓ | DL3DV PSNR↑ | SSIM↑ | LPIPS↓ |
| ------------ | ------------------ | -------------- | -------- | ----------- | ----- | ------ | ----------- | ----- | ------ |
| Ours         | Ours               | Ours           | Global   | <10         | <0.4  | >0.4   | <10         | <0.4  | >0.4   |
| Ours         | Ours               | 3 Offsets      | Residual | 20.09       | 0.674 | 0.289  | 19.18       | 0.588 | 0.372  |
| Ours         | Triangle Splatting | Ours           | Residual | 20.65       | 0.693 | 0.282  | 19.75       | 0.610 | 0.341  |
| LongLRM      | Ours               | Ours           | Residual | 21.24       | 0.701 | 0.275  | 19.74       | 0.608 | 0.355  |
| Ours         | Ours               | Ours           | Residual | 21.45       | 0.710 | 0.245  | 20.04       | 0.627 | 0.314  |

Predicting rotation directly in world space diverges to noise/empty renders; the LongLRM Mamba decoder (used by Lyra) underperforms; reverting the window function or the 3-offset parameterization weakens results — all components are needed.

## 💡 Insights & Impact

- Flat primitives are far harder to decode than volumetric Gaussians: an incorrectly oriented triangle contributes negligibly to the render, so gradients are compact and early-training supervision is poor. The ray-centered residual-rotation parameterization + product window function are what make feedforward triangle decoding stable.
- Volumetric 3DGS optimizes pixel metrics well but yields no clean surface (near-random normals); 2DGS improves geometry but cannot be effectively supervised with high-quality normals; triangles recover sharp, mesh-ready surfaces.
- Reusing a pretrained video VAE decoder (rather than training a small transformer/Mamba from scratch) provides local appearance/spatial priors that simplify the decoding problem.

## 🔗 Related Work

- Uses feed-forward metric reconstruction [MapAnything](../reconstruction/mapanything.md) for metric poses/depth; geometry-free NVS methods leverage [VGGT](../reconstruction/vggt.md) features, and the paper cites [Depth Anything 3](../reconstruction/depth-anything-3.md) and [YoNoSplat](yonosplat.md) among feed-forward NVS baselines.
- Positioned against latent 3DGS scene generators (Wonderland, Lyra, Generative Gaussian Splatting, Bolt3D) and the generate-then-optimize line (ViewCrafter, WorldStereo).

## 📚 Key Takeaways

1. Triangle splats can be decoded directly from frozen video-diffusion latents in a single pass — the first non-volumetric feedforward latent scene decoder.
2. A ray-centered Cholesky-shape + residual-rotation parameterization and a product window function are the ingredients that make flat-primitive gradient flow stable.
3. Under identical training, 3DGS wins rendering but has no usable geometry, while triangles win geometry (cosine 0.853 vs 0.116) and convert to a game-engine mesh with a >7 dB PSNR advantage over 3DGS meshes at ~8× fewer vertices (0.5M vs 3DGS's 4M) — a clear accuracy-vs-fidelity trade-off, reported honestly.

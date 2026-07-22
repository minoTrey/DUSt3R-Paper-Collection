# StructSplat: Generalizable 3D Gaussian Splatting from Uncalibrated Sparse Views (arXiv preprint (2026-06))

![structsplat — overview](https://raw.githubusercontent.com/J-C-Zhao/StructSplat/main/asserts/demo.jpeg)

_전체 개요 (저자 project page)_

## 📋 Overview

- **Authors**: Jia-Chen Zhao, Beiqi Chen, Xinyang Chen, Guangcong Wang, Liqiang Nie
- **Institution**: Harbin Institute of Technology (Shenzhen); Great Bay University; Guangzhou CloudButterfly Technology Co., Ltd.
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.28321) | [Code](https://github.com/J-C-Zhao/StructSplat) | [Project Page](https://structsplat.github.io)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward, generalizable 3D Gaussian reconstruction framework that operates directly on uncalibrated images without camera intrinsics or extrinsics, using a structured representation that assigns explicit roles to geometry, semantic, and texture cues.

## 🎯 Key Contributions

1. **Camera-parameter-free feed-forward 3DGS**: Reconstructs 3D Gaussians directly from uncalibrated source images in a single forward pass, requiring neither intrinsics nor extrinsics.
2. **Structured representation**: Separates geometry (VGGT-based encoder), semantics (DINOv3-based encoder), and texture (lightweight convolutional encoder) into explicit functional roles rather than entangling them in a unified backbone.
3. **Pixel-aligned feature injection**: A late-stage injection of high-resolution texture features into the Gaussian decoder to recover high-frequency textures and consistent colors.
4. **Camera alignment for leakage-free training**: A parallel-stream strategy that estimates cameras with and without target views and aligns them, preventing target-view information leakage through cross-attention.

## 🔧 Technical Details

### Motivation

Directly attaching a Gaussian head to a strong geometry backbone (e.g., MASt3R or VGGT) is shown to be insufficient for appearance modeling: when a color head is attached to VGGT for 2D reconstruction, color fidelity and texture detail are poor even on training views (Fig. 3), because compact 3D features are biased toward spatial smoothness and geometric consistency.

### Architecture

- **Geometry Encoder**: VGGT-based, produces tokenized view-consistent 3D features; decoded into a pixel-aligned depth map for Gaussian centers.
- **Semantic Encoder**: extracts features via a pretrained vision foundation model (DINOv3) to encode view-invariant correspondences and improve global consistency.
- **Texture Encoder**: lightweight convolutional layers producing high-resolution image-space features, injected into the 3D feature stream via pixel-aligned feature injection.
- **Gaussian Decoder**: modified DPT heads with a redesigned Reassembling block that aligns and concatenates geometric and semantic features; texture features are injected just before the final prediction layer.
- **Camera Decoder + Alignment**: predicts camera parameters and aligns target cameras (from a mixed source+target set) into the source-only coordinate system via rotation-quaternion alignment (Lagrange multiplier) and translation least-squares (scale λ + offset ∆τ).

### Camera Alignment for Leakage-Free Training

Two image sets are processed in parallel through the geometry extractor: a mixed source+target set and a source-only set. Because cross-attention in the geometry extractor leaks target information into source features, the Gaussian decoder is fed only the source-only features, while target cameras are aligned to the source-only coordinate system for fair supervision and evaluation.

## 📊 Results

Metrics: PSNR↑, SSIM↑, LPIPS↓. All images resized/center-cropped to 256×256. Models trained on DL3DV; ACID and RealEstate10K are cross-dataset. "Camera" column: "Weak" = intrinsics only, "No" = no camera parameters.

원논문 Table 1.

| Method                 | Camera | DL3DV PSNR↑ | DL3DV SSIM↑ | DL3DV LPIPS↓ | ACID PSNR↑ | ACID SSIM↑ | ACID LPIPS↓ | RE10K PSNR↑ | RE10K SSIM↑ | RE10K LPIPS↓ |
| ---------------------- | ------ | ----------- | ----------- | ------------ | ---------- | ---------- | ----------- | ----------- | ----------- | ------------ |
| NoPoSplat              | Weak   | 25.592      | 0.838       | 0.104        | 25.521     | 0.750      | 0.185       | 24.724      | 0.818       | 0.145        |
| FLARE\*                | Weak   | 23.441      | 0.757       | 0.126        | 24.365     | 0.702      | 0.200       | 23.611      | 0.777       | 0.155        |
| Splatt3R               | No     | 15.936      | 0.391       | 0.408        | 11.000     | 0.307      | 0.582       | 12.092      | 0.364       | 0.540        |
| AnySplat               | No     | 22.377      | 0.716       | 0.150        | 22.433     | 0.651      | 0.237       | 20.521      | 0.686       | 0.212        |
| Depth Anything 3       | No     | 20.715      | 0.615       | 0.226        | 20.482     | 0.588      | 0.346       | 18.769      | 0.613       | 0.312        |
| **StructSplat (Ours)** | No     | **28.045**  | **0.888**   | **0.091**    | **24.372** | **0.712**  | **0.219**   | **22.240**  | **0.729**   | **0.201**    |

\*FLARE natively uses camera intrinsics as conditional input for the novel-view-synthesis subtasks. Among camera-free methods, StructSplat is best on all three datasets; against the intrinsics-using "Weak" methods it surpasses NoPoSplat on DL3DV (28.045 vs. 25.592) but on ACID/RealEstate10K it trails NoPoSplat's PSNR (24.372 vs. 25.521; 22.240 vs. 24.724).

### Multi-View Reconstruction on DL3DV

원논문 Table 2.

| Method                 | 2-view PSNR↑ | 2-view SSIM↑ | 2-view LPIPS↓ | 4-view PSNR↑ | 4-view SSIM↑ | 4-view LPIPS↓ | 6-view PSNR↑ | 6-view SSIM↑ | 6-view LPIPS↓ |
| ---------------------- | ------------ | ------------ | ------------- | ------------ | ------------ | ------------- | ------------ | ------------ | ------------- |
| RayZer                 | 19.802       | 0.527        | 0.286         | 27.888       | 0.868        | 0.140         | 28.851       | 0.889        | 0.128         |
| AnySplat               | 22.377       | 0.716        | 0.150         | 24.499       | 0.769        | 0.112         | 26.529       | 0.841        | 0.085         |
| Depth Anything 3       | 20.715       | 0.615        | 0.226         | 20.486       | 0.601        | 0.232         | 20.566       | 0.602        | 0.232         |
| **StructSplat (Ours)** | **28.045**   | **0.888**    | **0.091**     | **30.415**   | **0.931**    | **0.061**     | **31.137**   | **0.942**    | **0.057**     |

### Ablations on DL3DV

원논문 Table 3 (구조 요소) · Table 5 (Camera Alignment, ATE) · Table 6 (rendering w/o CA).

| Setting                   | PSNR↑  | SSIM↑ | LPIPS↓ | ATErot↓    | ATEpos↓    |
| ------------------------- | ------ | ----- | ------ | ---------- | ---------- |
| Geometric Features only   | 20.610 | 0.622 | 0.343  | —          | —          |
| + Semantic Features       | 26.236 | 0.848 | 0.151  | —          | —          |
| + Texture Features (full) | 28.045 | 0.888 | 0.091  | —          | —          |
| w/o Camera Alignment      | 27.338 | 0.879 | 0.097  | —          | —          |
| AnySplat (alignment)      | —      | —     | —      | 0.0866     | 0.1003     |
| **StructSplat (Ours)**    | —      | —     | —      | **0.0016** | **0.0093** |

With pose post-optimization on DL3DV (원논문 Table 4), StructSplat reaches 29.287 PSNR / 0.911 SSIM / 0.085 LPIPS, above NoPoSplat (27.243) and FLARE (26.916).

## 💡 Insights & Impact

- **Disentangling appearance from geometry matters**: Adding semantic features raises PSNR from 20.610 to 26.236, and texture features push it to 28.045 — the two appearance-oriented pathways together contribute the majority of the gain on DL3DV.
- **Leakage control is measurable**: The camera-alignment strategy reduces target-pose ATE by roughly two orders of magnitude vs. AnySplat's scale-only alignment (ATErot 0.0016 vs. 0.0866; ATEpos 0.0093 vs. 0.1003) and removing it drops DL3DV PSNR from 28.045 to 27.338.
- **Honest limits**: The camera-free design still trails the intrinsics-using NoPoSplat in PSNR on the two cross-dataset benchmarks (ACID, RealEstate10K), and the paper notes remaining challenges under extremely sparse views, severe occlusions, and complex view-dependent lighting.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Used as the geometry backbone; StructSplat argues geometry features alone underfit appearance.
- **[MASt3R](../foundation/mast3r.md)**: Alternative geometry backbone (used by Splatt3R baseline).
- **[DUSt3R](../foundation/dust3r.md)**: Foundational feed-forward pointmap reconstruction that this line of pose-free NVS builds upon.
- **[Depth Anything 3](../reconstruction/depth-anything-3.md)**: A compared camera-free baseline with a Gaussian decoding head.

## 📚 Key Takeaways

1. StructSplat performs feed-forward generalizable 3DGS from fully uncalibrated images (no intrinsics, no extrinsics).
2. Its structured representation (geometry + semantics + texture) with pixel-aligned texture injection recovers appearance detail that a geometry-only backbone misses.
3. A parallel-stream camera alignment strategy prevents target-view leakage, yielding far lower target-pose ATE than scale-only alignment.
4. On DL3DV it sets the best camera-free results (28.045 PSNR), though it still trails intrinsics-using NoPoSplat in PSNR on the ACID and RealEstate10K cross-dataset transfers.

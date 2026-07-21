# GUSH3R: Everyone Everywhere All at Once as Gaussians (arXiv preprint (2026-07))

## 📋 Overview

- **Authors**: Keito Abe, Kaede Shiohara, Takashi Otonari, Toshihiko Yamasaki
- **Institution**: The University of Tokyo
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.05243) | [Project Page](https://abkeito.github.io/gush3r-page/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward framework for online dynamic human-scene reconstruction that, building on the frozen Human3R foundation model, lifts static scenes and dynamic humans into a unified 3D Gaussian Splatting representation (Scene Gaussian Decoder + Human Gaussian Decoder) enabling photorealistic novel view synthesis in a single forward pass.

## 🎯 Key Contributions

1. **New problem setting**: Feed-forward, photorealistic, renderable dynamic human-scene reconstruction from monocular video, establishing a strong baseline.
2. **Unified 3DGS representation**: Bridges human-scene foundation models and photorealistic rendering via geometric priors and SMPL-X representations, disentangling humans and scene into a common Gaussian space.
3. **Efficiency**: Competitive novel view synthesis vs. decomposition-based feed-forward and optimization-based baselines at substantially higher FPS.

## 🔧 Technical Details

### Foundation and Decoders

- **Backbone**: Frozen Human3R, which jointly estimates camera pose, scene point maps, and SMPL-X human meshes (10,475 vertices) with a recurrent state and per-person tokens.
- **Scene Gaussian Decoder**: Initializes Gaussian centers from scene point maps; decodes Human3R image tokens (DPT) fused with CNN image features via an MLP to predict opacity/rotation/scale/color. Newly predicted Gaussians are filtered by confidence and human-detection scores, then merged across frames by metric-space **voxelization** (highest-confidence center + confidence-weighted attributes).
- **Human Gaussian Decoder**: Uses SMPL-X vertices as anchors; a Human Gaussian Transformer (HGT) cross-attends human/vertex/memory tokens (queries) to image tokens (keys/values), predicting per-vertex Gaussians in canonical A-pose transformed to posed space via linear blend skinning.
- **Appearance memory**: Per-person memory tokens preserve appearance across frames/occlusions, associated by SMPL-X matching.

### Training

- Decoders trained separately with Human3R frozen. Images resized to longer-side 512; AdamW, LR 1×10⁻⁴.
- Scene Decoder: 100k iters on one A100 80GB (~1 day); loss `L_scene = λ_mse L_mse + λ_lpips L_lpips + λ_dep L_dep + λ_reg L_reg` on BEDLAM + DL3DV.
- Human Decoder: 150k iters on one A100 40GB (~2 days); loss with partial LPIPS + silhouette on BEDLAM + Motion-X++.

## 📊 Results

### Concept-Level Comparison (원논문 Table 1)

원논문 Table 1. Streaming(인과적 프레임별 처리), Dynamic human(비강체 모델링), Photo-reality(렌더 가능 표현).

| Method   | Streaming | Dynamic human | Photo-reality |
| -------- | --------- | ------------- | ------------- |
| VGGT     | ✗         | ✗             | ✗             |
| AnySplat | ✗         | ✗             | ✓             |
| CUT3R    | ✓         | ✗             | ✗             |
| Human3R  | ✓         | ✓             | ✗             |
| Ours     | ✓         | ✓             | ✓             |

### Single-Human NVS — NeuMan (원논문 Table 2)

원논문 Table 2 (일부). 최적화 기반 HSR은 per-scene 최적화 덕에 PSNR/SSIM이 높지만, Ours가 LPIPS와 FPS에서 앞선다.

| Method               | NeuMan-4 PSNR ↑ | NeuMan-4 SSIM ↑ | NeuMan-4 LPIPS ↓ | NeuMan-16 PSNR ↑ | NeuMan-16 SSIM ↑ | NeuMan-16 LPIPS ↓ | FPS ↑    |
| -------------------- | --------------- | --------------- | ---------------- | ---------------- | ---------------- | ----------------- | -------- |
| HSR (opt.)           | 20.6            | 0.58            | 0.58             | 18.3             | 0.57             | 0.59              | –        |
| AnySplat             | 15.2            | 0.33            | 0.42             | 15.4             | 0.35             | 0.48              | (6.77)   |
| AnySplat+LHM+Human3R | 13.9            | 0.32            | 0.46             | 15.0             | 0.35             | 0.46              | 0.16     |
| AnySplat+LHM+GT      | 14.6            | 0.32            | 0.43             | 15.9             | 0.37             | 0.43              | 0.42     |
| **Ours**             | 18.6            | 0.55            | **0.28**         | 16.6             | 0.39             | **0.44**          | **1.70** |

### Single-Human NVS — EMDB (원논문 Table 2)

원논문 Table 2 (일부).

| Method               | EMDB-4 PSNR ↑ | EMDB-4 SSIM ↑ | EMDB-4 LPIPS ↓ | EMDB-16 PSNR ↑ | EMDB-16 SSIM ↑ | EMDB-16 LPIPS ↓ |
| -------------------- | ------------- | ------------- | -------------- | -------------- | -------------- | --------------- |
| HSR (opt.)           | 20.2          | 0.67          | 0.50           | 16.2           | 0.68           | 0.51            |
| AnySplat             | 14.4          | 0.45          | 0.45           | 13.2           | 0.46           | 0.51            |
| AnySplat+LHM+Human3R | 15.5          | 0.46          | 0.44           | 14.7           | 0.47           | 0.49            |
| AnySplat+LHM+GT      | 13.9          | 0.44          | 0.48           | 13.4           | 0.45           | 0.52            |
| **Ours**             | 18.1          | 0.60          | **0.30**       | 18.0           | 0.57           | **0.41**        |

### Multi-Human NVS — BEDLAM (원논문 Table 3)

원논문 Table 3. Full(Human-Scene), Scene, Human 영역. Human 영역 PSNR에서는 LHM 기반 baseline(특히 +GT의 16.9)이 Ours(13.5)보다 높다.

| Method               | HS PSNR ↑ | HS SSIM ↑ | HS LPIPS ↓ | Sc PSNR ↑ | Sc SSIM ↑ | Sc LPIPS ↓ | Hu PSNR ↑ | Hu SSIM ↑ | Hu LPIPS ↓ | FPS ↑    |
| -------------------- | --------- | --------- | ---------- | --------- | --------- | ---------- | --------- | --------- | ---------- | -------- |
| AnySplat             | 15.9      | 0.43      | 0.42       | 16.2      | 0.50      | 0.37       | 14.3      | 0.87      | 0.14       | (6.77)   |
| AnySplat+LHM+Human3R | 14.5      | 0.31      | 0.47       | 14.5      | 0.38      | 0.46       | 14.7      | 0.88      | 0.11       | 0.16     |
| AnySplat+LHM+GT      | 15.1      | 0.35      | 0.43       | 15.0      | 0.40      | 0.42       | **16.9**  | **0.90**  | **0.08**   | 0.20     |
| **Ours**             | **17.0**  | **0.53**  | **0.34**   | **17.5**  | **0.59**  | **0.30**   | 13.5      | 0.87      | 0.13       | **1.45** |

### Scene Gaussian Decoder Ablation — NeuMan (원논문 Table 4)

원논문 Table 4 (일부).

| Variant        | 4v PSNR ↑ | 4v SSIM ↑ | 4v LPIPS ↓ | 8v PSNR ↑ | 8v SSIM ↑ | 8v LPIPS ↓ | 16v PSNR ↑ | 16v SSIM ↑ | 16v LPIPS ↓ |
| -------------- | --------- | --------- | ---------- | --------- | --------- | ---------- | ---------- | ---------- | ----------- |
| Full model     | 19.7      | 0.60      | 0.26       | 17.8      | 0.49      | 0.37       | 17.4       | 0.47       | 0.39        |
| w/o depth loss | 19.3      | 0.58      | 0.29       | 17.6      | 0.48      | 0.40       | 17.1       | 0.46       | 0.43        |
| w/o DL3DV      | 19.5      | 0.59      | 0.28       | 17.7      | 0.48      | 0.37       | 17.3       | 0.47       | 0.39        |

### Human Gaussian Decoder Ablation — NeuMan (원논문 Table 4)

원논문 Table 4 (일부). Cross-attention 제거가 가장 큰 성능 저하.

| Variant             | 4v PSNR ↑ | 4v SSIM ↑ | 4v LPIPS ↓ | 8v PSNR ↑ | 8v SSIM ↑ | 8v LPIPS ↓ | 16v PSNR ↑ | 16v SSIM ↑ | 16v LPIPS ↓ |
| ------------------- | --------- | --------- | ---------- | --------- | --------- | ---------- | ---------- | ---------- | ----------- |
| Full model          | 11.6      | 0.74      | 0.20       | 13.0      | 0.81      | 0.17       | 12.6       | 0.78       | 0.19        |
| w/o Motion-X++      | 11.4      | 0.74      | 0.22       | 13.0      | 0.80      | 0.18       | 12.4       | 0.77       | 0.20        |
| w/o Partial LPIPS   | 11.6      | 0.74      | 0.21       | 12.9      | 0.79      | 0.18       | 12.5       | 0.77       | 0.20        |
| w/o memory tokens   | 11.5      | 0.74      | 0.21       | 13.0      | 0.80      | 0.18       | 12.5       | 0.77       | 0.19        |
| w/o cross-attention | 10.2      | 0.72      | 0.24       | 11.7      | 0.78      | 0.20       | 11.3       | 0.76       | 0.21        |

### Video Depth Estimation — NeuMan (원논문 Table 5)

원논문 Table 5. 시퀀스당 단일 글로벌 스케일. AbsRel↓, δ<1.25↑.

| Method              | AbsRel ↓ | δ < 1.25 ↑ |
| ------------------- | -------- | ---------- |
| DepthAnything3      | 0.47     | 0.70       |
| Human3R             | 0.54     | 0.71       |
| Ours w/o depth loss | 0.44     | 0.74       |
| **Ours**            | **0.43** | **0.75**   |

A background-only static-scene analysis (원논문 Table 6) shows batch feed-forward methods better exploit multi-view consistency — e.g., AnySplat reaches 24.0 PSNR on NeuMan 4-view vs. Ours 19.7 — reflecting a batch–streaming trade-off, while Ours remains competitive on LPIPS.

## 💡 Insights & Impact

- Existing feed-forward methods either ignore dynamic humans or lack a renderable representation; GUSH3R unifies both in a single 3DGS space.
- Joint reconstruction beats post-hoc composition of separately reconstructed humans and scenes, improving both quality and FPS.
- Cross-attention in the Human Gaussian Transformer is the most critical component for transferring appearance to canonical human Gaussians.

## 🔗 Related Work

- Foundation [Human3R](human3r.md); backbone lineage cites [VGGT](../reconstruction/vggt.md), [CUT3R](cut3r.md), [MonST3R](monst3r.md), [DUSt3R](../foundation/dust3r.md), [MASt3R-SfM](../foundation/mast3r-sfm.md), [Depth Anything 3](../reconstruction/depth-anything-3.md), [HAMSt3R](../understanding/hamst3r.md), [YoNoSplat](../gaussian-splatting/yonosplat.md); related human-scene method [ODHSR](odhsr.md).

## 📚 Key Takeaways

1. First feed-forward, streaming, photorealistic dynamic human-scene reconstruction unifying humans and scene as 3D Gaussians.
2. Competitive NVS at ~10× the FPS of decomposition baselines, winning full-image and scene-region quality while honestly trailing LHM-based baselines on isolated human regions and optimization/batch methods on some PSNR/SSIM.
3. Best video-depth consistency on NeuMan, outperforming both DepthAnything3 and the underlying Human3R.

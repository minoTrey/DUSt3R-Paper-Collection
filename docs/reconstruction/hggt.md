# HGGT: Robust and Flexible 3D Hand Mesh Reconstruction from Uncalibrated Images (arXiv preprint (2026-03))

![hggt — architecture](https://arxiv.org/html/2603.23997v2/images/pipeline_new.png)

_The pipeline of HGGT (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Yumeng Liu, Xiao-Xiao Long, Marc Habermann, Xuanze Yang, Cheng Lin, Yuan Liu, Yuexin Ma, Wenping Wang, Ligang Liu
- **Institution**: University of Science and Technology of China; Nanjing University; Max-Planck-Institut für Informatik; Macau University of Science and Technology; Hong Kong University of Science and Technology; ShanghaiTech University; Texas A&M University
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.23997) | [Project Page](https://lym29.github.io/HGGT/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward framework that adapts the VGGT backbone to jointly infer 3D hand meshes (MANO parameters) and camera poses from uncalibrated multi-view images, using learnable hand and camera tokens in a cross-attention refinement module and a mixed real+synthetic training strategy.

## 🎯 Key Contributions

1. **First calibration-free multi-view hand recovery**: A feed-forward framework that jointly estimates camera poses and hand meshes from uncalibrated views, eliminating pre-calibration and iterative optimization.
2. **Unified cross-attention refinement**: Learnable hand and camera tokens act as queries that aggregate geometric and view-dependent cues from multi-view image features, disentangling hand geometry from camera viewpoints.
3. **Mixed-data training strategy**: Combines real monocular, real multi-view, and a new large-scale synthetic multi-view dataset with randomized viewpoints, using gradient accumulation over alternating single/multi-view steps.
4. **New synthetic dataset**: 85,683 multi-view image sets for training and 21,242 for validation, each with 10 rendered views (856,830 synthetic images), from GraspXL grasps with DART/Objaverse textures.

## 🔧 Technical Details

### Architecture

- **Backbone**: VGGT aggregator (DINOv2 ViT-L/14 encoder, 24 transformer blocks, embedding dim 1024, 16 heads, MLP ratio 4.0, alternating frame/global attention with RoPE); pretrained weights resumed and all aggregator layers unfrozen.
- **Refinement**: 4 stacked cross-attention blocks where hand tokens + camera tokens are queries and multi-view image features are keys/values.
- **Heads**: A Hand Head (MLP) regresses MANO (θ ∈ ℝ⁴⁸, β ∈ ℝ¹⁰, t ∈ ℝ³) → 778 vertices / 21 joints; a Camera Head predicts per-view 9-D encoding [T, q, FoV] (shares VGGT's camera-head architecture).

### Losses and Training

- Hand loss (MANO + root-relative 3D joints, applied when GT available), camera loss (translation + geodesic rotation + FoV, S > 1 only), projection consistency loss (reprojection alignment + negative-depth penalty, final block only). Intermediate supervision across the 4 blocks with exponential stage weights (γ = 0.6).
- ~1.4 billion parameters, 8 NVIDIA A100 GPUs, AdamW (weight decay 0.05), micro-batch 32 images/GPU, gradient accumulation over 4 steps, warmup 1e-8→1e-6 over first 5% of 80,000 iterations then cosine decay; ~5 days. Patch size 14, max dimension 518 px. Constant image budget with B = ⌊Nimg/S⌋.
- Data: HaMeR single-view collection (~2.7M examples), POEM multi-view real (~438K frames across DexYCB, HO3D, OakInk, ARCTIC, InterHand2.6M), plus the synthetic set.

## 📊 Results

### Main Comparison (mesh/joint error, mm)

원논문 Table 1. Cali-Free ✗ 행은 GT 카메라 사용(상한 참조), ✓ 행은 calibration-free. RR = Root Relative, PA = Procrustes Alignment. 모두 낮을수록 좋음.

| Dataset       | Method       | Cali-Free | RR-MPVPE ↓ | RR-MPJPE ↓ | PA-MPVPE ↓ | PA-MPJPE ↓ |
| ------------- | ------------ | --------- | ---------- | ---------- | ---------- | ---------- |
| DexYCB (8v)   | POEMv2-large | ✗         | 7.50       | 7.54       | 3.84       | 3.68       |
| DexYCB (8v)   | VGGT+POEM    | ✓         | 39.08      | 39.99      | 11.06      | 10.20      |
| DexYCB (8v)   | Ours+POEM    | ✓         | 19.69      | 20.18      | 4.38       | 4.19       |
| DexYCB (8v)   | Ours         | ✓         | 13.29      | 13.79      | 4.47       | 4.57       |
| OakInk (4v)   | POEMv2-large | ✗         | 8.47       | 8.47       | 4.49       | 4.24       |
| OakInk (4v)   | VGGT+POEM    | ✓         | 47.29      | 48.66      | 13.18      | 12.08      |
| OakInk (4v)   | Ours+POEM    | ✓         | 26.58      | 27.34      | 5.49       | 5.14       |
| OakInk (4v)   | Ours         | ✓         | 20.13      | 20.59      | 6.14       | 6.12       |
| InterHand(8v) | POEMv2-large | ✗         | 9.04       | 8.82       | 5.23       | 4.72       |
| InterHand(8v) | VGGT+POEM    | ✓         | 49.92      | 50.57      | 20.16      | 18.49      |
| InterHand(8v) | Ours+POEM    | ✓         | 19.18      | 19.47      | 5.98       | 5.37       |
| InterHand(8v) | Ours         | ✓         | 23.22      | 27.46      | 6.05       | 13.81      |
| ARCTIC (8v)   | POEMv2-large | ✗         | 7.13       | 6.80       | 4.43       | 3.91       |
| ARCTIC (8v)   | VGGT+POEM    | ✓         | 20.19      | 20.67      | 8.21       | 7.29       |
| ARCTIC (8v)   | Ours+POEM    | ✓         | 19.67      | 19.93      | 5.35       | 4.75       |
| ARCTIC (8v)   | Ours         | ✓         | 19.48      | 20.04      | 6.57       | 6.61       |
| HO3D (5v)     | POEMv2-large | ✗         | 10.58      | 10.58      | 4.59       | 4.13       |
| HO3D (5v)     | VGGT+POEM    | ✓         | 56.07      | 57.53      | 21.05      | 20.29      |
| HO3D (5v)     | Ours+POEM    | ✓         | 28.48      | 29.37      | 6.05       | 5.57       |
| HO3D (5v)     | Ours         | ✓         | 9.98       | 10.03      | 3.30       | 3.33       |

On HO3D, HGGT (Ours) even surpasses the GT-camera POEMv2-large (PA-MPJPE 3.33 vs 4.13). On InterHand, Ours+POEM is stronger than the standalone Ours under Procrustes (PA-MPJPE 5.37 vs 13.81); on OakInk, POEM with GT cameras remains ahead.

### Ablation on HO3D (PA error, mm)

원논문 Table 2. (a) VGGT freezing strategy, (b) training data composition. Freezing none이 최적.

| Setting          | Trainable | RR-MPJPE ↓ | PA-MPVPE ↓ | PA-MPJPE ↓ |
| ---------------- | --------- | ---------- | ---------- | ---------- |
| Freeze 24 layers | 0.46B     | 26.41      | 17.82      | 18.19      |
| Freeze 20 layers | 0.56B     | 17.60      | 13.72      | 14.06      |
| Freeze 10 layers | 0.81B     | 12.88      | 4.32       | 4.39       |
| Freeze None      | 1.37B     | **10.03**  | **3.30**   | **3.33**   |
| Real Only        | -         | 15.33      | 5.97       | 6.04       |
| Real + Synthetic | -         | **10.03**  | **3.30**   | **3.33**   |

## 💡 Insights & Impact

- **Off-the-shelf VGGT fails on hands**: With cropped hand images, minimal cross-view overlap collapses VGGT's geometry; with full frames, camera estimation is dominated by static high-texture background, so the small, weakly textured hand remains misaligned — motivating the integrated hand+camera reasoning.
- **Full backbone training matters**: Freezing all VGGT layers is far worse (PA-MPJPE 18.19) than unfreezing everything (3.33), indicating a non-negligible domain gap between scene pretraining and hand reconstruction.
- **Synthetic data as regularizer**: Adding the randomized-viewpoint synthetic set improves all metrics (PA-MPJPE 6.04 → 3.33), providing perfect annotations and diverse viewpoints that curb overfitting to fixed real rigs.
- **Robust in the wild**: Recovers global hand pose under severe motion blur and heavy occlusion (right hand visible in only 2 of 8 views); efficient at 0.23 s/frame (plus ~1.2 s for an external hand detector).

## 🔗 Related Work

- **[VGGT](vggt.md)**: The alternating-attention backbone adopted and fully fine-tuned; also the source of the camera-head design.
- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: Cited feed-forward reconstruction predecessors.
- **[Fast3R](fast3r.md)** and **[CUT3R](../dynamic/cut3r.md)**: Cited follow-up feed-forward geometry methods; **[Human3R](../dynamic/human3r.md)** cited as a concurrent human-reconstruction effort building on such priors.

## 📚 Key Takeaways

1. HGGT is the first feed-forward, calibration-free multi-view 3D hand reconstruction framework, jointly regressing MANO parameters and camera poses from uncalibrated images via a VGGT backbone plus hand/camera token cross-attention.
2. A mixed real-monocular / real-multi-view / synthetic-multi-view training strategy with a new randomized-viewpoint synthetic dataset drives generalization to uncalibrated, in-the-wild settings.
3. It matches or surpasses GT-camera POEM on several benchmarks (notably HO3D) and clearly beats POEM equipped with off-the-shelf VGGT cameras, with ablations showing full backbone training and synthetic data are both essential.

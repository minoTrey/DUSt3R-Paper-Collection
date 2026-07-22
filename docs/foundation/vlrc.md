# VLRC: Vision-Language Reprojection Consistency as a Scalable Signal for Better Feed-Forward 3D Pretraining (arXiv preprint 2026-07)

![vlrc — architecture](https://arxiv.org/html/2607.02707v3/images/vlrc_figure_2.png)

_Reprojection of a point p∈ℝ3p\in\mathbb{R}^{3}: the head of a cyclist - The 3d point centered on the head of the cyclist is reprojected on the… (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Marwane Hariat, David Filliat, Antoine Manzanera
- **Institution**: U2IS, ENSTA – Institut Polytechnique de Paris; Agence Ministérielle pour l'IA de Défense
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.02707)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An auxiliary training objective that reprojects dense frozen vision-language (VLM) features across views using the predicted 3D geometry and enforces feature-space consistency — providing semantic multi-view supervision that complements both self-supervised photometric and supervised feed-forward 3D pretraining, with no extra 3D annotations.

## 🎯 Key Contributions

1. **Vision-Language Reprojection Consistency (VLRC)**: Uses predicted depth/pose/intrinsics to warp dense VLM feature maps between frames and penalizes cosine dissimilarity between reprojected and target features — a signal less tied to raw RGB than photometric loss, useful in textureless / illumination-varying regions.
2. **Complements both training regimes**: Integrates with self-supervised SS3D video pretraining (added to the photometric SfM loss) and with SelfEvo-style unlabeled adaptation of supervised VGGT (added to the self-distillation objective).
3. **Geometry–semantics alignment**: By making language-grounded features multi-view consistent, VLRC-trained geometry supports more coherent 2D-to-3D feature lifting, improving zero-shot open-vocabulary 3D semantic segmentation.

## 🔧 Technical Details

- **Objective**: `L_final = L3D + λ_VLRC·L_VLRC`, where `L_VLRC = Σ m_{t,s}(p)·[1 − cos(F̂_t(p), F_t(p))]`; gradients flow through the differentiable reprojection into the 3D model while the VLM encoder stays frozen.
- **Validity masking** (self-supervised): pixels with large discrepancy between depth-pose reprojection and optical-flow correspondences (dynamic objects, occlusions) are excluded via CoopNet; no masking in the SelfEvo setting.
- **Dense VLM features**: CLIP-derived features (from CLIP-Seg), upsampled with FeatUp; the encoder is frozen throughout.
- **Optimization**: images resized to shortest side 518 then 518×518 crop; λ_VLRC = 0.01 (SS3D) / 0.1 (VGGT/SelfEvo); 20 epochs, Adam (β₁=0.99, β₂=0.999), cosine lr 10⁻⁵ → 10⁻⁸.

## 📊 Results

### Depth estimation on KITTI (fine-tune + eval on KITTI)

원논문 Table 1. Abs Rel·Sq Rel·RMSE·RMSE log 낮을수록, δ 높을수록 좋음.

| Method        | Abs Rel ↓ | Sq Rel ↓  | RMSE ↓    | RMSE log ↓ | δ1 ↑      | δ2 ↑      | δ3 ↑  |
| ------------- | --------- | --------- | --------- | ---------- | --------- | --------- | ----- |
| Monodepth2    | 0.110     | 0.831     | 4.642     | 0.187      | 0.883     | 0.962     | 0.982 |
| MonoViT       | 0.099     | 0.708     | 4.372     | 0.175      | 0.900     | 0.967     | 0.984 |
| RA-Depth      | 0.096     | 0.613     | 4.216     | 0.171      | 0.903     | 0.968     | 0.985 |
| Hariat et al. | 0.082     | 0.604     | 4.108     | 0.162      | 0.928     | 0.968     | 0.985 |
| SS3D          | 0.064     | 0.530     | 3.212     | 0.138      | 0.946     | 0.977     | 0.986 |
| SS3D + VLRC   | **0.060** | **0.496** | **2.908** | **0.133**  | **0.950** | **0.978** | 0.986 |

### Depth estimation on NYUv2 (fine-tune + eval on NYUv2)

원논문 Table 2. MonoIndoor++의 RMSE log는 N/A.

| Method        | Abs Rel ↓ | RMSE ↓    | RMSE log ↓ | δ1 ↑      | δ2 ↑      | δ3 ↑  |
| ------------- | --------- | --------- | ---------- | --------- | --------- | ----- |
| MovingIndoor  | 0.208     | 0.712     | 0.086      | 0.674     | 0.900     | 0.968 |
| StructDepth   | 0.140     | 0.540     | 0.060      | 0.817     | 0.955     | 0.988 |
| IndoorDepth   | 0.126     | 0.494     | 0.054      | 0.845     | 0.965     | 0.991 |
| Hariat et al. | 0.115     | 0.458     | 0.054      | 0.859     | 0.970     | 0.992 |
| SS3D          | 0.090     | 0.418     | 0.049      | 0.866     | 0.970     | 0.992 |
| SS3D + VLRC   | **0.082** | **0.407** | **0.044**  | **0.867** | **0.971** | 0.992 |

### VLRC on SelfEvo-style adaptation of VGGT

원논문 Table 4. Sintel·KITTI depth.

| Method         | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ | KITTI AbsRel ↓ | KITTI δ<1.25 ↑ |
| -------------- | --------------- | --------------- | -------------- | -------------- |
| VGGT           | 0.227           | 0.684           | 0.059          | 0.961          |
| SelfEvo (VGGT) | 0.212           | 0.692           | 0.042          | 0.979          |
| SelfEvo + VLRC | **0.209**       | **0.700**       | **0.038**      | **0.980**      |

### VLM feature backbone ablation (VLRC on SS3D, KITTI)

원논문 Table 3. Δ는 SS3D 대비. CLIP-Seg가 DINOv2·TIPSv2를 앞선다.

| Method      | AbsRel ↓  | Δ AbsRel | δ1 (%) ↑ | Δ δ1 |
| ----------- | --------- | -------- | -------- | ---- |
| SS3D (base) | 0.064     | –        | 94.6     | –    |
| w/ DINOv2   | 0.065     | +0.001   | 94.3     | -0.3 |
| w/ TIPSv2   | 0.061     | -0.003   | 95.0     | +0.3 |
| w/ CLIP-Seg | **0.060** | -0.004   | **95.0** | +0.4 |

### Open-vocabulary 3D semantic segmentation

원논문 Table 5. ScanNet200(Casper3D protocol)·KITTI(zero-shot). 높을수록 좋음.

| Method                            | ScanNet200 mIoU ↑ | ScanNet200 mAcc ↑ | KITTI mIoU ↑ | KITTI mAcc ↑ |
| --------------------------------- | ----------------- | ----------------- | ------------ | ------------ |
| Casper3D                          | 11.0              | 18.1              | –            | –            |
| Casper3D w/ SelfEvo geometry      | 11.1              | 18.3              | –            | –            |
| Casper3D w/ SelfEvo+VLRC geometry | **12.1**          | **19.0**          | –            | –            |
| SS3D                              | –                 | –                 | 17.5         | 28.3         |
| SS3D + VLRC                       | –                 | –                 | **24.0**     | **39.3**     |

### KITTI zero-shot 3D segmentation vs. supervised methods

원논문 Table A.1. 감독학습 DUSt3R(무거운 test-time 최적화 포함)가 VLRC보다 높다.

| Method      | mIoU (%) ↑ | mAcc (%) ↑ |
| ----------- | ---------- | ---------- |
| DUSt3R      | **26.2**   | **43.4**   |
| AnyCam      | 15.2       | 24.0       |
| VGGT        | 18.2       | 32.2       |
| SS3D        | 17.5       | 28.3       |
| SS3D + VLRC | 24.0       | 39.3       |

### Zero-shot pose and intrinsics (SS3D+VLRC retrained on YouTube8M)

원논문 Table B.1·B.2. Pose는 Sintel·TUM-RGBD (모두 낮을수록 좋음); Intrinsics는 Sintel AFE(px)·RFE(%).

| Method      | Sintel ATE ↓ | Sintel RPEt ↓ | Sintel RPEr ↓ | TUM ATE ↓ | TUM RPEt ↓ | TUM RPEr ↓ |
| ----------- | ------------ | ------------- | ------------- | --------- | ---------- | ---------- |
| AnyCam      | 0.099        | 0.045         | **0.567**     | 0.095     | 0.025      | 1.050      |
| SS3D        | 0.090        | 0.043         | 0.601         | 0.092     | 0.026      | 1.064      |
| SS3D + VLRC | **0.088**    | **0.041**     | 0.587         | **0.090** | **0.021**  | **1.038**  |

| Method      | AFE (px) ↓ | RFE (%) ↓ |
| ----------- | ---------- | --------- |
| UniDepth    | 447.4      | 35.7      |
| DUSt3R      | 434.0      | 36.4      |
| AnyCam      | **252.2**  | 18.1      |
| SS3D        | 256.6      | 16.7      |
| SS3D + VLRC | 255.5      | **16.5**  |

## 💡 Insights & Impact

- **Inconsistency as supervision**: If predicted geometry induces inconsistent multi-view VLM features, the geometry is likely misaligned — enforcing consistency turns semantic features into a scalable, annotation-free geometric signal.
- **Feature-space over RGB-space**: Because VLM features encode higher-level semantics, VLRC gives useful gradients in textureless / illumination-varying regions where photometric loss is ambiguous.
- **CLIP beats DINO here**: Language-aligned CLIP-Seg features supervise geometry better than purely visual DINOv2 features (Table 3), and CLIP-over-SAM-masks helps further (appendix).
- **Honest limits**: On KITTI segmentation, supervised DUSt3R (with heavy test-time optimization) still leads (26.2 vs 24.0 mIoU); AnyCam edges VLRC on Sintel RPErot and intrinsics AFE. VLRC's gains are as an auxiliary term, not a new architecture.
- **Scales to web video**: SS3D+VLRC trained on YouTube8M reconstructs and text-localizes casual videos (e.g., Sagrada Familia interior/exterior).

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Supervised backbone adapted with VLRC under a SelfEvo-style protocol; also the architecture reused by SS3D.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Supervised pointmap references (DUSt3R is a strong supervised baseline in the segmentation protocol).
- **[CroCo](croco.md)**: Cross-view completion pretraining that DUSt3R initializes from.
- **[π³](../reconstruction/pi3.md)** / **[CUT3R](../dynamic/cut3r.md)**: Feed-forward 3D models cited as the supervised/continuous line VLRC complements.

## 📚 Key Takeaways

1. **Semantic multi-view consistency is a scalable 3D training signal** requiring no 3D labels, usable on raw web video.
2. **Auxiliary and general**: VLRC drops into both self-supervised (SS3D) and supervised-pretrained (VGGT/SelfEvo) pipelines and improves depth, pose, and intrinsics.
3. **Better geometry → better 3D semantics**: aligning geometry with VLM features during training yields more coherent open-vocabulary 3D segmentation on both indoor (ScanNet200) and outdoor (KITTI) protocols.

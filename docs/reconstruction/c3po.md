# C3Po: Cross-View Cross-Modality Correspondence by Pointmap Prediction (NeurIPS 2025)

![c3po — teaser](https://c3po-correspondence.github.io/static/images/teaser.png)

_핵심 개념 (저자 project page)_

## 📋 Overview

- **Authors**: Kuan Wei Huang, Brandon Li, Bharath Hariharan, Noah Snavely
- **Institution**: Cornell University
- **Venue**: NeurIPS 2025
- **Links**: [Paper](https://arxiv.org/abs/2511.18559) | [Project Page](https://c3po-correspondence.github.io/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: Introduces C3, the first cross-view cross-modality correspondence dataset pairing ground-level photos with floor plans (90K pairs, 153M correspondences), and C3Po, a method that reframes photo-to-floor-plan matching as DUSt3R pointmap prediction — fine-tuning DUSt3R on C3 to cut correspondence RMSE by 34% over the best baseline.

> The PDF footer confirms "39th Conference on Neural Information Processing Systems (NeurIPS 2025) Track on Datasets and Benchmarks"; the Verification grade follows the batch's LIKELY assignment.

## 🎯 Key Contributions

1. **C3 dataset**: A first-of-its-kind dataset of paired floor plans and photos with pixel correspondences and per-photo camera poses, built by SfM-reconstructing Internet photo collections then manually registering the point clouds to floor plans.
2. **Failure of SOTA correspondence models**: Demonstrates that state-of-the-art matchers (SuperGlue, LoFTR, DINOv2, DIFT, RoMa, DUSt3R, MASt3R) all fail to draw accurate photo↔floor-plan correspondences, most with errors above 10% of image size.
3. **C3Po method**: Adapts DUSt3R's pointmap prediction to cross-view cross-modality matching, outperforming the best baseline by 34% in RMSE.
4. **Downstream pose + open challenges**: Uses predicted correspondences for 2D "you-are-here" camera pose estimation on the floor plan, and identifies structured failure modes (minimal-context photos, structural symmetry) for future work.

## 🔧 Technical Details

### Dataset construction

- Floor plans sourced from Wikimedia Commons by recursively traversing the "Floor plans" category, filtering to scenes of interest (churches, castles, temples, etc.), yielding 10,842 floor plans across 6,194 scenes.
- Photos taken from MegaScenes (intersecting with the collected floor-plan scenes), augmented with geotagged YFCC100M photos within a 50 m radius when reconstructions were sparse — 1,474 scenes, 766K photos, 2,942 floor plans at this stage.
- Correspondences derived via a two-step pipeline: (1) COLMAP SfM reconstruction of each scene's photos (exhaustive matching for small sets, vocabulary-tree with 40 nearest neighbors for large ones, plus model-merger post-processing); (2) a custom UI to manually align the two largest reconstructed point clouds to the floor plan, saving T_{pc→fp}. Projecting each visible 3D point X into the photo (x_i = T_i·X) and floor plan (x_fp = T_{pc→fp}·X) yields correspondences.

### C3Po method

- Fine-tunes pre-trained DUSt3R on C3. The floor plan is the reference image defining the 3D frame; DUSt3R's pointmap maps each photo pixel to a 3D point in floor-plan coordinates, then an orthographic projection (x, y, z) → (x, z) drops the up (y) axis to recover a 2D floor-plan correspondence (discarding z instead converged slower).
- **Splits DUSt3R's Siamese encoders** so each domain (photos vs floor plans) is learned separately, and applies photometric (color jitter) + geometric (crop, rotation) augmentation to the floor plan only, to counter overfitting.
- Training: 10 epochs (~3 days) on 8×A6000 40GB, DUSt3R hyperparameters — DPT head, AdamW, base LR 1e-4 / min 1e-6, weight decay 0.05, batch size 48, 3 warmup epochs, cosine decay, input 512×512, initialized from DUSt3R.

### Camera pose estimation

- Estimates 2D camera pose in floor-plan coordinates from predicted correspondences: essential matrix via OpenCV findEssentialMat (large focal length 107 px to simulate orthographic projection), decomposed to rotation/translation, with a −90° x-axis rotation to move from XY to the floor plan's XZ plane. Near-planar ambiguities (upside-down cameras) are detected and corrected by reflecting across the best-fit plane; the camera center is the epipole in the floor-plan image.

## 📊 Results

### C3 dataset statistics

원논문 Section 3.4. Overall: 90K plan-photo pairs, 597 scenes, 648 unique floor plans, 85K photos, 153M pixel-level correspondences (1 to 13,262 per pair, average 1,711).

| Split | Scenes | Floor plans | Photos | Correspondences |
| ----- | ------ | ----------- | ------ | --------------- |
| Train | 479    | 519         | 66K    | 120M            |
| Test  | 118    | 129         | 19K    | 33M             |

### Correspondence accuracy (C3 test set)

원논문 Figure 2 (RMSE table, outputs normalized so image dimensions map to a unit square; lower is better). C3Po (0.1919) beats the best baseline LoFTR (0.2901) by 34%. Notably MASt3R (built on DUSt3R for matching) does worse than DUSt3R, likely because DUSt3R predicts scene structure projected onto the plan, closer to the solution.

| Method          | RMSE↓  |
| --------------- | ------ |
| SuperGlue       | 0.4050 |
| LoFTR           | 0.2901 |
| DINOv2          | 0.5338 |
| DIFT            | 0.3036 |
| RoMa            | 0.3308 |
| DUSt3R          | 0.2925 |
| MASt3R          | 0.4616 |
| **Ours (C3Po)** | 0.1919 |

Wilcoxon signed-rank tests between C3Po and each baseline give P-values all below 0.05. C3Po also shows stronger PCK and precision-recall curves (그림 2 middle·right, curves; 수치 미인쇄).

### Camera pose estimation (recall)

원논문 Table 1. Recall under angular, positional, and combined thresholds; positional thresholds are a percentage of the floor plan's diagonal length.

| Metric                        | Value |
| ----------------------------- | ----- |
| Angular R@5°                  | 21.86 |
| Angular R@10°                 | 32.53 |
| Angular R@20°                 | 44.12 |
| Angular R@30°                 | 51.35 |
| Positional R@5%               | 15.94 |
| Positional R@10%              | 27.73 |
| Positional R@20%              | 41.21 |
| Angular+Positional (30°, 20%) | 29.48 |

### Validation vs test generalization

원논문 Figure 8 (RMSE table). C3Po reaches RMSE 0.0369 on the held-out validation set (plan seen during training, photo unseen) versus 0.1877 on the test set (scenes unseen) — the model does markedly better when the floor plan itself was seen in training.

## 💡 Insights & Impact

- Isolates a genuinely unaddressed problem: prior datasets have either varied modality without correspondences (WAFFLE) or cross-view imagery without abstract layouts (VIGOR); C3 supplies both floor-plan↔photo pairs and dense correspondences plus poses.
- Key methodological insight: DUSt3R's geometric pointmap prior transfers to this cross-modal task better than dedicated matchers, because it predicts and projects scene structure rather than matching raw features — even MASt3R, DUSt3R's matching-specialized descendant, underperforms DUSt3R here.
- Remaining errors are far higher than classical correspondence; the authors attribute this to (1) photos with minimal global context and (2) structural symmetry, suggesting distributional (e.g. diffusion-based) prediction over unimodal regression as future work.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: the pointmap-prediction backbone C3Po fine-tunes; its ability to correspond across near-opposite viewpoints motivates the approach.
- **[MASt3R](../foundation/mast3r.md)**: DUSt3R-based matching model evaluated as a baseline; underperforms DUSt3R on this cross-modal task.
- **[MASt3R-SfM](../foundation/mast3r-sfm.md)**: related fully-integrated SfM extension of the DUSt3R/MASt3R family (cited).
- **[VGGT](./vggt.md)**: broader multi-view feed-forward geometry line into which pointmap-based correspondence fits.

## 📚 Key Takeaways

1. C3 is the first dataset with ground-truth photo↔floor-plan correspondences and camera poses — 90K pairs, 153M correspondences, 597 scenes — built from SfM point clouds manually aligned to Internet floor plans.
2. Off-the-shelf correspondence models (including DUSt3R and MASt3R) fail at combined cross-view + cross-modality matching.
3. C3Po reframes the task as DUSt3R pointmap prediction with split domain encoders and floor-plan-only augmentation, cutting RMSE 34% over the best baseline (0.1919 vs 0.2901) and enabling downstream "you-are-here" pose estimation, while symmetry and low-context photos remain open challenges.

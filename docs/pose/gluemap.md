# GLUEMAP: Global Structure-from-Motion Meets Feedforward Reconstruction (CVPR 2026)

![gluemap — architecture](https://arxiv.org/html/2605.26103v2/x2.png)

_Illustration of our proposed GLUEMAP pipeline consisting of four major steps: view graph initialization, feedforward local inference, global motion… (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Linfei Pan, Johannes Schönberger, Marc Pollefeys
- **Institution**: ETH Zurich; Meta Reality Labs; Microsoft
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2605.26103) | [Code](https://github.com/colmap/gluemap)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: GLUEMAP is a hybrid Structure-from-Motion pipeline that combines classical global-SfM optimization with feedforward local inference (π³): a sparse view graph drives batched local star-graph reconstructions, which are merged via global motion averaging and refined by an augmented bundle adjustment with virtual feedforward tracks, scaling robustly to tens of thousands of images.

## 🎯 Key Contributions

1. **Analysis of feedforward limitations**: Shows feedforward accuracy degrades with view-graph radius and that adding more images can _hurt_ transformer/diffusion methods, unlike optimization-based pipelines.
2. **Hybrid global-SfM pipeline (GLUEMAP)**: Four stages — view graph initialization (retrieval + Doppelganger filtering), feedforward local inference on star graphs, global motion averaging (intrinsics/rotation/similarity averaging), and augmented bundle adjustment.
3. **Local attention via star graphs**: Instead of globally attending over all images, feedforward inference runs on local star graphs, avoiding OOM and improving robustness to symmetry.
4. **Augmented bundle adjustment with virtual tracks**: Injects feedforward-conditioned virtual tracks (with known 3D positions) alongside SIFT and network tracks, so BA stays well-conditioned even under low overlap/texture.

## 🔧 Technical Details

### Pipeline

- **View Graph Initialization**: For each image, retrieve c candidate neighbors via SALAD; score pairs with Doppelgangers++ (DG). Edges are added by dynamic thresholding (initial δ₀ = 0.8, lowered by 0.1 until connected or δ < 0.2) between different connected components.
- **Feedforward Local Inference**: Each star graph Sₗ is reconstructed independently with π³ (keeping the 25 highest-DG neighbors), yielding local poses, depth, focal lengths, and tracks; overlapping tracks merge by snapping to SIFT keypoints within β = 1 px. A forward-backward depth-consistency check defines overlap ratios.
- **Global Motion Averaging**: Median focal per camera (intrinsics averaging), robust rotation averaging (Huber), then similarity averaging (single scale sₗ per star) for camera centers, initialized from a maximum spanning tree.
- **Augmented Bundle Adjustment**: Combines SIFT tracks, network tracks T, and ≈100 virtual tracks (10% conditioned on global poses); Huber robustifier for SIFT/network tracks and Arctan for virtual tracks.

### Efficiency

Experiments run on a GH200 (96 GB), but the method fits on an RTX 4090 (24 GB). It scales to tens of thousands of images where feedforward baselines run out of memory (e.g., LaMAR scenes with several thousand views).

## 📊 Results

Metric: AUC@X (Area Under the recall Curve) over pose errors — higher is better; tight thresholds reflect accuracy, loose thresholds reflect completeness. `†` = GLUEMAP after motion averaging (before augmented BA); `*` = with ground-truth calibration.

### ETH3D

원논문 Table 1 (AUC@1/3/5, 두 하위표 통합).

| Method            | AUC@1↑   | AUC@3↑   | AUC@5↑   |
| ----------------- | -------- | -------- | -------- |
| SIFT (classical)  | 45.6     | 62.2     | 66.7     |
| AL+LG (classical) | 42.9     | 62.1     | 67.4     |
| CUT3R             | 5.0      | 11.4     | 18.8     |
| VGGT              | 8.6      | 24.0     | 35.0     |
| MapAnything       | 5.1      | 11.1     | 18.3     |
| π³                | 13.2     | 36.1     | 48.9     |
| MASt3R-SfM        | 39.2     | 55.6     | 60.5     |
| π³ + BA           | 30.6     | 55.1     | 65.1     |
| MP-SFM\* (sparse) | 74.3     | —        | 88.3     |
| MP-SFM\* (dense)  | 70.3     | —        | 88.2     |
| GLUEMAP†          | 20.3     | 49.0     | 61.9     |
| GLUEMAP           | 53.0     | 76.9     | 83.6     |
| GLUEMAP\*         | **74.0** | **85.9** | **89.0** |

π³ is the strongest pure-feedforward method (clearly above CUT3R/VGGT/MapAnything). GLUEMAP\* leads at AUC@3/@5, while at the tightest AUC@1 the calibrated MP-SFM\* (sparse) is marginally ahead (74.3 vs. 74.0).

### IMC2021 (bag5 and Full)

원논문 Table 2 (bag5·Full 발췌).

| Method   | bag5 @3↑ | bag5 @5↑ | bag5 @10↑ | Full @3↑ | Full @5↑ | Full @10↑ |
| -------- | -------- | -------- | --------- | -------- | -------- | --------- |
| SIFT     | 39.6     | 47.3     | 57.0      | **76.9** | **83.8** | **90.1**  |
| AL+LG    | 48.4     | 58.5     | 70.6      | 62.8     | 72.4     | 82.5      |
| π³       | 46.2     | 58.4     | 73.0      | 35.2     | 49.2     | 66.2      |
| π³ + BA  | 54.0     | 64.9     | 77.6      | 45.8     | 54.8     | 65.9      |
| GLUEMAP† | 46.2     | 58.4     | 72.9      | 36.7     | 51.7     | 69.1      |
| GLUEMAP  | **54.3** | **65.3** | **77.8**  | 73.0     | 81.3     | 89.1      |

GLUEMAP is best on sparse bag5, but on the dense Full setting classical GLOMAP+SIFT (76.9/83.8/90.1) beats GLUEMAP (73.0/81.3/89.1) — high image density favors the classical baseline.

### CO3Dv2 (Average over 10/20/40 images)

원논문 Table 3 (Average).

| Method   | AUC@3↑   | AUC@10↑  | AUC@30↑  |
| -------- | -------- | -------- | -------- |
| SIFT     | 37.0     | 49.9     | 56.4     |
| AL+LG    | 38.1     | 52.2     | 59.9     |
| π³       | 47.3     | 76.6     | 89.5     |
| π³ + BA  | **58.4** | 80.3     | **90.7** |
| GLUEMAP† | 47.4     | 76.8     | 89.5     |
| GLUEMAP  | 56.7     | **79.9** | 90.4     |

On object-centric CO3Dv2 GLUEMAP is on par with feedforward methods (classical ones fall far behind), but π³ + BA edges it at AUC@3 (58.4 vs. 56.7) and AUC@30 (90.7 vs. 90.4).

### SMERF (low-overlap setting)

원논문 Table 4 ("low" overlap 컬럼).

| Method            | AUC@1↑   | AUC@5↑   | AUC@20↑  |
| ----------------- | -------- | -------- | -------- |
| SIFT              | 1.4      | 1.6      | 1.8      |
| AL+LG             | 2.4      | 6.1      | 9.8      |
| π³                | 1.5      | 14.3     | 49.8     |
| π³ + BA           | 1.5      | 14.3     | 53.4     |
| MASt3R-SfM        | 4.3      | 11.7     | 23.0     |
| MP-SFM\* (sparse) | 5.4      | 29.1     | 53.0     |
| MP-SFM\* (dense)  | **26.6** | 63.2     | 84.1     |
| GLUEMAP†          | 12.9     | 70.2     | 92.1     |
| GLUEMAP           | 14.6     | 71.4     | 92.4     |
| GLUEMAP\*         | 14.7     | **71.8** | **92.5** |

Classical methods largely fail at low overlap; GLUEMAP leads at AUC@5/@20, but the dense MP-SFM\* wins the tightest AUC@1 (26.6 vs. 14.7).

### LaMAR (Average over CAB/HGE/LIN)

원논문 Table 5 (Average). CAB/HGE/LIN의 view-graph radius는 각각 49/61/59로, feedforward는 OOM으로 실패.

| Method     | AUC@3↑   | AUC@10↑  | AUC@30↑  |
| ---------- | -------- | -------- | -------- |
| SIFT       | 2.6      | 12.4     | 28.3     |
| AL+LG      | 10.9     | 30.1     | 46.0     |
| MASt3R-SfM | OOM      | OOM      | OOM      |
| π³         | OOM      | OOM      | OOM      |
| π³ + BA    | OOM      | OOM      | OOM      |
| GLUEMAP†   | 18.3     | 53.7     | 78.1     |
| GLUEMAP    | **26.4** | **59.1** | **80.6** |

## 💡 Insights & Impact

- **More views can hurt feedforward, help classical**: Figure 3 and the IMC2021/SMERF tables show transformer methods (VGGT, MapAnything) degrade with larger view-graph radius and higher density, while GLUEMAP behaves like an optimization pipeline — accuracy grows with density.
- **Best of both worlds, with caveats**: GLUEMAP tops the average rank across all five datasets, but honestly loses in specific regimes — to classical SIFT on dense IMC2021 Full, to π³+BA at CO3Dv2 AUC@3, and to dense MP-SFM\* at the tightest thresholds on ETH3D/SMERF.
- **Scalability where feedforward can't reach**: On LaMAR's several-thousand-view scenes, all feedforward baselines OOM while GLUEMAP reconstructs and, uniquely, fits within a 24 GB RTX 4090.
- **Honest limits**: It cannot yet handle fisheye images (feedforward backbones are pinhole-trained) or purely rotational motion, and it currently combines several separate feedforward models rather than one shared architecture.

## 🔗 Related Work

- **[Pi3](../reconstruction/pi3.md)**: The permutation-equivariant π³ model used as GLUEMAP's feedforward local-inference backbone and strongest pure-feedforward baseline.
- **[VGGT](../reconstruction/vggt.md)** and **[MapAnything](../reconstruction/mapanything.md)**: Multi-view feedforward baselines analyzed for their view-graph-radius sensitivity.
- **[MASt3R-SfM](../foundation/mast3r-sfm.md)**: Feedforward SfM baseline compared across ETH3D, SMERF, and LaMAR.
- **[DUSt3R](../foundation/dust3r.md)**: Two-view transformer foundation underpinning the feedforward line.

## 📚 Key Takeaways

1. GLUEMAP fuses classical global SfM with feedforward local inference: sparse view graph → π³ star-graph reconstructions → global motion averaging → augmented bundle adjustment with virtual tracks.
2. It achieves the best average rank across ETH3D, IMC2021, CO3Dv2, SMERF, and LaMAR, and scales to tens of thousands of images on a single 24 GB GPU where feedforward methods OOM.
3. The paper is candid about where it does not win — classical SIFT on dense collections, π³+BA on some object-centric thresholds, and dense MP-SFM at the tightest accuracy thresholds.

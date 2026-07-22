# Sat3R: Satellite DSM Reconstruction via RPC-Aware Depth Fine-tuning (arXiv preprint (2026-05))

![sat3r — architecture](https://arxiv.org/html/2605.07264v1/figs/method_new.png)

_Overview of Sat3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Qiaoyi Yang, Chaoyi Zhou, Xi Liu, Run Wang, Minghui Xu, Mert D. Pesé, Feng Luo, Yuhao Xu, Zhi-Qi Cheng, Qiushi Chen, Hairong Qi, Siyu Huang
- **Institution**: Clemson University; University of Washington; University of Tennessee
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.07264)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first feed-forward framework for satellite Digital Surface Model (DSM) reconstruction, bridging the RPC-camera domain gap by fine-tuning Depth Anything V2 on physically consistent pseudo depth built from RPC geometry with the SiLog loss, matching optimization-based accuracy at over 300× speedup.

## 🎯 Key Contributions

1. **First feed-forward satellite DSM framework**: Sat3R enables efficient inference without per-scene optimization for satellite DSM reconstruction.
2. **RPC-aware pseudo depth pipeline**: A physically consistent pseudo depth (slant-range distance from a near-plane reference to the true surface intersection along the imaging ray) provides metric depth supervision for fine-tuning a monocular depth foundation model.
3. **Domain-gap bridging**: On DFC2019, Sat3R reduces MAE by 38% over zero-shot feed-forward baselines and approaches optimization-based SatDN while delivering over 300× speedup.

## 🔧 Technical Details

### Problem

Satellite cameras follow the Rational Polynomial Camera (RPC) model, which has no explicit camera center, making perspective depth undefined; the satellite depth-scale distribution also differs substantially from natural-image training data, so geometry foundation models (VGGT, AnySplat) fail zero-shot.

### Pseudo Depth Construction

For each image a near-plane is defined at altitude z_ref = z_max + δ (margin δ = 50 m). For each pixel, the RPC imaging ray's intersection with the near-plane (p_near) and the true surface (p_surface, via fixed-point iteration on the ground-truth DSM) gives pseudo depth d = ‖p_surface − p_near‖₂. Training pairs are curated from DFC2019 with complete RGB–CLS alignment, sufficient multi-view coverage, and winter scenes excluded.

### Fine-tuning and Inference

Depth Anything V2 (DA2) is fine-tuned with the Scale-Invariant Logarithmic (SiLog) loss following DA2's metric fine-tuning protocol; maximum inference depth range set to 150 m to align with the satellite scene distribution, giving direct metric-scale output. At inference, per-view depths are fused (SatDN fusion module) and back-projected through the RPC model to 3D points, then rasterized to a DSM grid via p90 pooling.

### Setup

Fine-tuned for 40 epochs at lr 5×10⁻⁶ with AdamW on 2× NVIDIA A100 40GB; inference on a single A100 40GB. Evaluated on 6 held-out DFC2019 scenes (JAX 207/214/260, OMA 212/287/315) using MAE and Median Error (MED).

## 📊 Results

### DSM Reconstruction — Mean over Six Scenes

원논문 Table 1. MAE / MED lower is better; time lower is better.

| Method           | Mean MAE↓ | Mean MED↓ | Time↓    |
| ---------------- | --------- | --------- | -------- |
| SatDN (optim.)   | **1.44**  | **0.74**  | 5h 36min |
| AnySplat         | 4.21      | 3.49      | 1min 37s |
| VGGT             | 4.11      | 2.95      | 1min 31s |
| DA3              | 4.37      | 3.50      | 1min 40s |
| DA2 (zero-shot)  | 4.59      | 3.44      | 1min 26s |
| **Sat3R (Ours)** | 2.82      | 1.78      | 1min 05s |

Sat3R is the best feed-forward method, cutting mean MAE from zero-shot DA2's 4.59 to 2.82 (a 38% reduction) and mean MED from 3.44 to 1.78, approaching the optimization-based upper bound SatDN while running over 300× faster (5h 36min → ~1min 05s).

### Max Depth Threshold Ablation

원논문 Table 2. Mean MAE / MED lower is better.

| Max Depth | Mean MAE↓ | Mean MED↓ |
| --------- | --------- | --------- |
| 100       | 3.312     | 2.254     |
| 300       | 3.412     | 2.354     |
| 150       | **3.131** | **1.963** |

A 150 m threshold is best: 100 m causes saturation near the depth boundary, while 300 m reduces effective depth resolution relative to the actual scene range (~55–94 m).

## 💡 Insights & Impact

- **Adaptation, not architecture**: Sat3R shows a feed-forward monocular depth model can match optimization-based satellite accuracy purely through domain-appropriate supervision, at a fraction of the cost.
- **RPC as supervision, not just projection**: Rather than fighting the RPC model, Sat3R exploits its geometry to synthesize physically consistent metric pseudo depth, sidestepping the perspective-camera assumption.
- **Metric-scale output**: Fine-tuning to a satellite-aligned 150 m depth range yields directly metric depth, giving a better initial estimate that accelerates the fusion stage — no post-hoc scale recovery.
- **Practicality**: The ~300× speedup over hours-long optimization makes large-scale, time-sensitive DSM reconstruction (disaster response, mapping) practical.

## 🔗 Related Work

- **[VGGT](vggt.md)**: A geometry foundation model baseline that fails zero-shot on satellite imagery.
- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: Feed-forward geometry foundations in the cited lineage.
- **[MonST3R](../dynamic/monst3r.md)**: Referenced geometry-estimation model.
- **[FF3R](../understanding/ff3r.md)**: Feedforward feature 3D reconstruction cited from the same group.

## 📚 Key Takeaways

1. Sat3R is the first feed-forward satellite DSM reconstruction framework, replacing hours of per-scene optimization with near-instant inference.
2. It bridges the RPC domain gap by fine-tuning Depth Anything V2 on RPC-geometry pseudo depth with the SiLog loss, aligned to a 150 m satellite depth range.
3. On DFC2019 it cuts feed-forward MAE by 38% and approaches optimization-based SatDN at over 300× speedup.
4. Aligning the inference depth range with the satellite data distribution is critical to effective fine-tuning.

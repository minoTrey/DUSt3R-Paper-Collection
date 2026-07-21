# G-MASt3R-SfM: Graph-based View Pruning and Multi-Stage Optimization for Robust SfM (arXiv preprint (2026-06))

## 📋 Overview

- **Authors**: Toshiki Watanabe, Shintaro Ito, Natsuki Takama, Koichi Ito, Takafumi Aoki
- **Institution**: Graduate School of Information Sciences, Tohoku University, Japan
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.22856)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An SfM pipeline that hardens MASt3R-SfM against outlier correspondences via a Graph-based View Pruning module (scene-graph community analysis to remove inconsistent views) and a Multi-Stage Optimization module (bundle adjustment expanding from local to global consistency).

## 🎯 Key Contributions

1. **Graph-based View Pruning (GVP)**: Builds a scene graph from MASt3R confidence and geometric verification, partitions it into communities via the Louvain method, and removes outlier communities using a separation score computed on a Spring-Layout embedding.
2. **Multi-Stage Optimization (MSO)**: Iterative bundle adjustment over three progressively widening scopes (Local → Neighbor → Global) exploiting graph community structure to stabilize convergence.
3. **State-of-the-art on ETH3D**: Improves both camera pose estimation and 3D reconstruction over COLMAP, DFSfM, VGGSfM, VGGT, and MASt3R-SfM by suppressing outlier-induced noise.

## 🔧 Technical Details

### Baseline: MASt3R-SfM

MASt3R-SfM performs global alignment (aligning per-view point maps to a common frame by minimizing 3D position error e_pos) followed by bundle adjustment minimizing reprojection error e_rep. Its weakness is that MASt3R emits correspondences even for non-overlapping pairs, which are fed unfiltered into optimization and degrade global consistency.

### GVP Module

For each pair (n, m) it estimates relative pose from MASt3R-derived focal length and a RANSAC fundamental matrix, reprojects points, and keeps inliers. An edge is added only where the summed inlier confidence exceeds a threshold (set to 1,000). Louvain partitions the graph into communities {C₁, C₂, …}; the separation score sᵢ = (min inter-community distance / Scale) · 1/log(1+|Cᵢ|) flags small, distant communities. Communities with sᵢ > 1.5 are removed (e.g., sky-dominated, low-overlap views).

### MSO Module

Starting from GA initialization on the selected views, three stages minimize e_rep: **Local** (each community independently), **Neighbor** (each community plus adjacent communities, subsampling to round(N/2) if targets exceed half of N), and **Global** (all views). Convergence per stage uses the ratio of recent-to-preceding average errors (k=5, l=10) until eⱼ < δ=0.01; the loop repeats from Local until total iterations reach imax = 500.

## 📊 Results

Evaluated on 13 ETH3D scenes (14–76 images each; scenes with >50 images subsampled by half). Metrics: RRE↓ / RTE↓ (deg), AUC@5↑ (%), SfM rate↑ (% images registered); MVS Acc.↑ / Cpl.↑ / F1↑.

### Ablation: View Selection & Pruning

원논문 Table 1.

| Config          | RRE↓ [deg] | RTE↓ [deg] | SfM rate [%] |
| --------------- | ---------- | ---------- | ------------ |
| Random, w/o GVP | 2.173      | 2.307      | 100          |
| Random, w/ GVP  | 0.479      | 0.992      | 97           |
| Ours, w/o GVP   | 2.231      | 2.247      | 100          |
| Ours, w/ GVP    | **0.474**  | **0.978**  | 97           |

Without GVP, "Random" and "Ours" view selection are indistinguishable; the drastic gains come from GVP, and GVP + Ours selection is best.

### Camera Pose Estimation on ETH3D

원논문 Table 2. 13개 씬 평균.

| Method                  | RRE↓ [deg] | RTE↓ [deg] | AUC@5↑ [%] | SfM rate [%] |
| ----------------------- | ---------- | ---------- | ---------- | ------------ |
| COLMAP                  | 0.655      | 2.645      | 90.7       | 87           |
| DFSfM                   | 2.298      | 3.711      | 68.0       | 85           |
| VGGSfM                  | 22.439     | 17.220     | 52.7       | 98           |
| VGGT                    | 2.485      | 8.806      | 35.4       | 100          |
| MASt3R-SfM              | 2.572      | 3.343      | 75.7       | 100          |
| **G-MASt3R-SfM (Ours)** | **0.474**  | **0.978**  | **93.9**   | 97           |

G-MASt3R-SfM has the best RRE, RTE, and AUC@5, but its SfM rate drops to 97% (vs. 100% for MASt3R-SfM/VGGT) precisely because GVP excludes unreliable views — an explicit accuracy-vs-coverage trade-off.

### Multi-View Stereo on ETH3D

원논문 Table 3. Acc./Cpl./F1는 높을수록 좋음.

| Method                  | Acc.↑     | Cpl.↑     | F1↑       |
| ----------------------- | --------- | --------- | --------- |
| COLMAP                  | **0.997** | 0.631     | 0.729     |
| MASt3R-SfM              | 0.944     | 0.645     | 0.741     |
| **G-MASt3R-SfM (Ours)** | 0.973     | **0.666** | **0.762** |

COLMAP retains the highest accuracy (0.997) but its lower SfM rate limits completeness; G-MASt3R-SfM wins completeness and the overall F1 score, and beats MASt3R-SfM on all three.

## 💡 Insights & Impact

- **Filtering matters more than selection**: The ablation shows GVP is the dominant factor — it slashes RRE from ~2.2° to ~0.48° and RTE from ~2.3° to ~0.98° regardless of the view-selection heuristic.
- **Coarse-to-fine BA avoids local minima**: The MSO error trajectory temporarily rises during Local/Neighbor stages (as views are added) but drops sharply in the Global stage, converging lower than MASt3R-SfM's single-shot optimization.
- **Accuracy over coverage**: Pruning unreliable views costs a small drop in SfM rate (100% → 97%) but yields substantially more accurate poses and better reconstruction — a deliberate and honest trade-off.
- **Complementary to feature-based SfM**: MASt3R-based dense matching still reconstructs texture-less scenes (e.g., "pipes") where COLMAP fails, and GVP removes the noise MASt3R-SfM otherwise introduces.

## 🔗 Related Work

- **[MASt3R-SfM](../foundation/mast3r-sfm.md)**: The baseline pipeline this work augments with GVP and MSO.
- **[MASt3R](../foundation/mast3r.md)**: The matching model whose confidence/point maps feed the scene graph.
- **[DUSt3R](../foundation/dust3r.md)**: The pointmap-regression foundation MASt3R extends.
- **[VGGT](../reconstruction/vggt.md)**: A transformer-based multi-view baseline compared on ETH3D.

## 📚 Key Takeaways

1. G-MASt3R-SfM makes MASt3R-based SfM robust by pruning geometrically inconsistent views through scene-graph community analysis (GVP).
2. Its Multi-Stage Optimization expands bundle-adjustment scope from local to global, converging to lower reprojection error than MASt3R-SfM.
3. On ETH3D it achieves the best pose accuracy (RRE 0.474°, RTE 0.978°, AUC@5 93.9%) and the best MVS F1 (0.762), at the cost of a slightly reduced SfM rate (97%) from excluding unreliable views.

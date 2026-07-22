# MERG3R: A Divide-and-Conquer Approach to Large-Scale Neural Visual Geometry (CVPR 2026)

![merg3r — architecture](https://arxiv.org/html/2603.02351v1/x2.png)

_Overview of our large-scale 3D reconstruction pipeline (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Leo Kaixuan Cheng, Abdus Shaikh, Ruofan Liang, Zhijie Wu, Yushi Guan, Nandita Vijaykumar
- **Institution**: University of Toronto, Vector Institute
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.02351) | [Project Page](https://leochengkx.github.io/MERG3R/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A training-free, model-agnostic wrapper that orders unordered image collections into a pseudo-video, partitions them into interleaved overlapping subsets each sized to fit GPU memory, reconstructs each with any geometric foundation model, and merges them via Sim(3) alignment plus confidence-weighted global bundle adjustment.

## 🎯 Key Contributions

1. **Pseudo-video ordering of unordered collections**: A dense DINO visual-similarity matrix is treated as a weighted complete graph, and an approximate Hamiltonian path maximizing consecutive-frame similarity imposes a pseudo-temporal ordering.
2. **Interleaved partitioning**: Rather than contiguous chunks, frames are drawn cyclically across K target subsequences so every subset spans the whole trajectory, guaranteeing viewpoint diversity within each local reconstruction.
3. **Scalable global tracking**: A sparse k-NN graph over frames with SuperPoint + LightGlue matching, geometrically filtered by bidirectional reprojection error and merged into multi-view tracks via disjoint-set union — O(kN) matchings rather than O(N²).
4. **Confidence-weighted global bundle adjustment**: Joint gradient-based optimization of intrinsics, extrinsics, and 3D points over the merged tracks.
5. **Model-agnostic**: Demonstrated with VGGT\*, FastVGGT, and π³ as interchangeable backbones.

## 🔧 Technical Details

### Complexity Argument

A monolithic transformer over N images costs O(N²) in self-attention. Splitting into K subsets of size T reduces this to O(KT²), or O(N²/K) when subsets run sequentially. Peak GPU memory drops accordingly, and subsets can additionally be parallelized across multiple GPUs.

### Image Set Ordering and Partitioning

**Step 1 — Pseudo-video.** Compute `M ∈ R^{N×N}` where `M_{i,j}` is DINO-based visual similarity. Approximate the Hamiltonian path maximizing `Σ_k M_{p_k, p_{k+1}}`.

**Step 2 — Interleaving.** Permute the ordering P\* into P̃ with `P̃_i = P*{(i mod K)·K + ⌊i/K⌋}`, drawing frames cyclically across the full ordering. The paper is explicit about why: without interleaving, subsets contain nearly identical viewpoints and produce unreliable local reconstructions. For particularly long sequences an additional DINO similarity constraint governs next-frame selection.

**Step 3 — Windowing.** Slide a fixed-length window of T elements across P̃ with stride T − O, where O is the overlap; keep only windows containing at least O frames beyond their start.

### Local Reconstruction

Each subset S_k is passed independently through a pretrained foundation model: `F_g(S_k) = (G_k, D_k, C_k)` — camera parameters, depth/point maps, and per-pixel confidence.

### Cluster Alignment

Adapting the weighted iterative similarity-transform estimator from VGGT-Long, corresponding 3D points between overlapping subsets are filtered by a confidence percentile threshold τ_conf, then aligned by solving for `T ∈ Sim(3)` minimizing a Huber objective `Σ_i ρ(‖p_i^k − T p_i^{k+1}‖₂)` via Iteratively Reweighted Least Squares, with weights `w_i^{(t)} = c_i · ρ'(r_i^{(t)})/r_i^{(t)}`.

### Tracking

For each subset, a sparse k-NN graph is built from the similarity matrix M. On each retained edge, SuperPoint features are matched with LightGlue; if (i,j) is already matched, (j,i) is skipped in favor of the next nearest neighbor. Raw matches are unprojected to 3D via the per-pixel depth, reprojected into the paired view using known intrinsics and poses, and discarded if bidirectional reprojection error exceeds τ_reproj. Survivors are merged by disjoint-set union into tracks, with each track's 3D location and confidence being the confidence-weighted mean over its observations.

### Global Bundle Adjustment

Minimizes the confidence-weighted reprojection error over ν gradient-descent iterations:

`L_BA = Σ_{(T_l, x_l, C_l)} Σ_{y^{l,i}} C_l ‖y^{l,i} − π_i(x_l)‖₂^λ`, with λ = 0.5.

The paper contrasts this with MASt3R-SfM, which also uses gradient-based refinement but optimizes over image _pairs_, limiting global consistency and scalability at large view counts.

### Experimental Setup

All experiments run on a single AMD Instinct MI210 GPU (64 GB). Unless otherwise specified, all images in each scene are used without subsampling. VGGT\* denotes the VRAM-efficient VGGT variant introduced in the FastVGGT paper. For fairness, the pseudo-video images are also fed to VGGT as input. Default hyperparameters: split size 100, overlap 5.

## 📊 Results

### Camera Pose Estimation on 7-Scenes

원논문 Table 2. 500장은 stride 2, 1000장은 서브샘플링 없음. OOM은 out-of-memory다.

| Method          | 500 img RRA@30↑ | RTA@30↑   | AUC@30↑   | 1000 img RRA@30↑ | RTA@30↑   | AUC@30↑   |
| --------------- | --------------- | --------- | --------- | ---------------- | --------- | --------- |
| MASt3R-SfM      | 100             | 97.30     | 79.47     | OOM              | OOM       | OOM       |
| CUT3R           | 75.89           | 40.16     | 38.82     | 60.47            | 30.50     | 14.11     |
| TTT3R           | 100             | 86.55     | 57.44     | 97.19            | 53.69     | 30.95     |
| VGGT\*          | 100             | 96.87     | 81.13     | OOM              | OOM       | OOM       |
| FastVGGT        | 100             | 96.75     | 80.59     | OOM              | OOM       | OOM       |
| VGGT-Long       | 100             | 97.24     | 79.51     | 100              | 95.54     | 75.11     |
| π³              | 100             | **97.74** | **83.89** | OOM              | OOM       | OOM       |
| Ours + VGGT\*   | 100             | 97.65     | 82.41     | 100              | 97.42     | 82.20     |
| Ours + FastVGGT | 100             | 97.71     | 81.76     | 100              | 97.56     | 81.45     |
| **Ours + π³**   | 100             | **97.74** | 82.97     | 100              | **97.69** | **83.63** |

At 500 images the wrapper is roughly neutral — π³ alone already achieves the best AUC@30 (83.89 vs 82.97 with MERG3R). The value appears at 1000 images, where every monolithic baseline is OOM and MERG3R + π³ retains 83.63 AUC@30.

### Camera Pose on Tanks & Temples and Cambridge Landmarks

원논문 Table 3. Umeyama 정렬 후 계산한다.

| Method          | T&T ATE↓  | RRE↓      | RTE↓      | Cambridge ATE↓ | RRE↓      | RTE↓      |
| --------------- | --------- | --------- | --------- | -------------- | --------- | --------- |
| MASt3R-SfM      | 0.202     | 0.521     | 0.024     | 7.695          | 4.426     | 0.987     |
| CUT3R           | 1.575     | 1.217     | 0.087     | 16.645         | 4.436     | 1.212     |
| TTT3R           | 0.951     | 2.025     | 0.090     | 7.162          | 4.856     | 1.419     |
| VGGT\*          | 0.535     | 1.498     | 0.071     | 0.793          | 5.728     | 1.085     |
| FastVGGT        | 0.549     | 1.400     | 0.072     | 0.812          | **4.198** | 1.095     |
| VGGT-Long       | 0.585     | 0.768     | 0.057     | 0.970          | 4.176     | **0.971** |
| π³              | 0.090     | 0.229     | 0.025     | 1.630          | 4.416     | 1.109     |
| Ours + VGGT\*   | 0.522     | 1.563     | 0.026     | **0.661**      | 4.482     | 1.215     |
| Ours + FastVGGT | 0.527     | 1.598     | 0.061     | 0.780          | 4.433     | 1.261     |
| **Ours + π³**   | **0.077** | **0.178** | **0.013** | 1.022          | 4.795     | 1.552     |

Reported honestly: on Cambridge Landmarks the picture is mixed. MERG3R + VGGT\* gives the best ATE (0.661), but VGGT-Long holds the best RRE and RTE, and adding MERG3R to π³ _worsens_ both rotation and translation relative pose error there (RRE 4.416 → 4.795, RTE 1.109 → 1.552) while improving ATE. The clean sweep is on Tanks & Temples.

### Comparison with Classical SfM

원논문 Table 4. 7-Scenes 500장 기준.

| Method        | RRA@30↑ | RTA@30↑   | AUC@30↑   | Time           |
| ------------- | ------- | --------- | --------- | -------------- |
| GLOMAP        | 100     | 96.67     | 81.38     | 10 min 34 s    |
| InstantSfM    | 100     | 95.55     | 76.32     | 8 min 56 s     |
| **Ours + π³** | 100     | **97.61** | **83.31** | **4 min 48 s** |

### Point Cloud Estimation

원논문 Table 5. 7-Scenes는 stride 2와 3, NRGBD는 3과 5로 키프레임을 샘플링한다. 원표가 13열이라 데이터셋별로 나눈다. VGGT-Long은 두 stride 설정 모두 3/5 행으로 보고된다.

**7-Scenes**

| Method          | Stride | Acc↓ Mean | Med.      | Comp↓ Mean | Med.      | NC↑ Mean  | Med.      |
| --------------- | ------ | --------- | --------- | ---------- | --------- | --------- | --------- |
| CUT3R           | 3/5    | 0.086     | 0.054     | 0.055      | 0.017     | 0.564     | 0.596     |
| TTT3R           | 3/5    | 0.137     | 0.090     | 0.072      | 0.027     | 0.554     | 0.581     |
| VGGT\*          | 3/5    | 0.019     | 0.008     | 0.028      | 0.011     | 0.607     | 0.660     |
| FastVGGT        | 3/5    | **0.014** | 0.006     | 0.028      | 0.010     | **0.631** | **0.705** |
| π³              | 3/5    | 0.019     | **0.004** | 0.036      | 0.018     | 0.539     | 0.556     |
| VGGT-Long       | 3/5    | 0.016     | 0.007     | 0.028      | 0.011     | 0.617     | 0.676     |
| Ours + VGGT\*   | 3/5    | 0.018     | 0.007     | 0.021      | 0.009     | 0.592     | 0.640     |
| Ours + FastVGGT | 3/5    | 0.018     | 0.008     | 0.023      | 0.007     | 0.576     | 0.613     |
| Ours + π³       | 3/5    | 0.017     | 0.007     | **0.019**  | 0.009     | 0.592     | 0.640     |
| CUT3R           | 2/3    | 0.165     | 0.111     | 0.086      | 0.025     | 0.537     | 0.553     |
| TTT3R           | 2/3    | 0.159     | 0.117     | 0.099      | 0.037     | 0.533     | 0.548     |
| VGGT\*          | 2/3    | 0.021     | 0.008     | 0.027      | 0.011     | 0.604     | 0.656     |
| FastVGGT        | 2/3    | **0.014** | 0.007     | 0.028      | 0.010     | **0.630** | **0.702** |
| π³              | 2/3    | 0.030     | 0.010     | 0.055      | 0.055     | 0.525     | 0.535     |
| Ours + VGGT\*   | 2/3    | 0.020     | 0.008     | 0.024      | 0.008     | 0.580     | 0.621     |
| Ours + FastVGGT | 2/3    | 0.018     | 0.008     | 0.022      | 0.007     | 0.573     | 0.61      |
| Ours + π³       | 2/3    | 0.016     | 0.007     | **0.017**  | **0.008** | 0.599     | 0.649     |

**NRGBD**

| Method          | Stride | Acc↓ Mean | Med.      | Comp↓ Mean | Med.      | NC↑ Mean  | Med.      |
| --------------- | ------ | --------- | --------- | ---------- | --------- | --------- | --------- |
| CUT3R           | 3/5    | 0.266     | 0.178     | 0.117      | 0.047     | 0.600     | 0.659     |
| TTT3R           | 3/5    | 0.769     | 0.504     | 0.089      | 0.046     | 0.702     | 0.796     |
| VGGT\*          | 3/5    | 0.028     | 0.018     | 0.018      | 0.007     | 0.710     | 0.816     |
| FastVGGT        | 3/5    | 0.024     | 0.013     | 0.018      | 0.010     | 0.665     | 0.791     |
| π³              | 3/5    | **0.018** | **0.008** | **0.013**  | **0.004** | 0.652     | 0.743     |
| VGGT-Long       | 3/5    | 0.021     | 0.012     | 0.016      | 0.007     | **0.780** | **0.887** |
| Ours + VGGT\*   | 3/5    | 0.025     | 0.015     | 0.015      | 0.006     | 0.703     | 0.814     |
| Ours + FastVGGT | 3/5    | 0.032     | 0.02      | 0.016      | 0.007     | 0.676     | 0.776     |
| Ours + π³       | 3/5    | 0.021     | 0.011     | 0.016      | 0.006     | 0.736     | 0.845     |
| CUT3R           | 2/3    | 0.329     | 0.250     | 0.144      | 0.044     | 0.568     | 0.603     |
| TTT3R           | 2/3    | 0.258     | 0.170     | 0.111      | 0.032     | 0.592     | 0.648     |
| VGGT\*          | 2/3    | 0.027     | 0.019     | 0.024      | 0.008     | 0.726     | 0.830     |
| FastVGGT        | 2/3    | 0.032     | 0.020     | 0.020      | 0.010     | 0.662     | 0.788     |
| π³              | 2/3    | 0.064     | 0.042     | 0.038      | 0.018     | 0.600     | 0.656     |
| VGGT-Long       | 3/5    | **0.018** | **0.01**  | 0.015      | 0.006     | **0.780** | **0.887** |
| Ours + VGGT\*   | 2/3    | 0.020     | 0.013     | **0.013**  | **0.006** | 0.700     | 0.805     |
| Ours + FastVGGT | 2/3    | 0.026     | 0.017     | 0.014      | 0.007     | 0.67      | 0.764     |
| Ours + π³       | 2/3    | 0.020     | 0.011     | 0.015      | 0.006     | 0.735     | 0.843     |

The pattern the paper emphasizes: CUT3R and TTT3R degrade rapidly as the number of input images increases (compare their 2/3 vs 3/5 rows), while the MERG3R variants stay flat. At the denser stride, MERG3R + π³ improves π³'s NRGBD Acc from 0.064 to 0.020 — but at the sparser stride, plain π³ is already better than MERG3R + π³ on NRGBD Acc and Comp. Bare FastVGGT also holds the best 7-Scenes Acc and NC in both settings.

### Ablation: Ordered vs Unordered Input

원논문 Table 6. Tanks & Temples 전 장면 기준.

| Method   | Real video ATE↓ | RRE↓  | RTE↓  | Pseudo seq. ATE↓ | RRE↓      | RTE↓      |
| -------- | --------------- | ----- | ----- | ---------------- | --------- | --------- |
| VGGT     | 0.521           | 1.317 | 0.544 | 0.522            | 1.563     | 0.061     |
| FastVGGT | 0.525           | 1.364 | 0.056 | 0.526            | 1.598     | 0.079     |
| π³       | 0.077           | 0.196 | 0.014 | 0.077            | **0.178** | **0.013** |

ATE is essentially unchanged (differences ≤ 0.001), showing the Hamiltonian-path ordering recovers a sequence as informative as the original video. For π³ the pseudo ordering is even marginally better on RRE and RTE.

### Ablation: Splitting Strategy

원논문 Table 7.

| Splitting Method | ATE↓      | RRE↓      | RTE↓      |
| ---------------- | --------- | --------- | --------- |
| Graph clustering | 0.319     | 1.280     | 0.060     |
| Sliding window   | 0.106     | 0.492     | 0.024     |
| **Interleaved**  | **0.077** | **0.178** | **0.013** |

The interpretation given: DINO-feature graph clustering performs _worst_, because geometric reconstruction needs more than feature-level similarity — it needs diverse multi-view observations. Sliding windows restrict each subset to a narrow trajectory segment, so a subset may see only one façade of a building, which shows up as poor RRE.

### Ablation: Subset Size

원논문 Table 8 (왼쪽). Tanks & Temples 전 장면.

| Split Size | ATE↓      | RRE↓      | RTE↓      | Time (s) | Mem. (GB) |
| ---------- | --------- | --------- | --------- | -------- | --------- |
| 25         | 0.084     | 0.674     | 0.026     | 127.41   | 10.95     |
| 50         | 0.078     | 0.415     | 0.016     | 127.20   | **10.63** |
| 75         | **0.076** | 0.180     | 0.014     | 132.43   | 10.98     |
| 100        | **0.076** | **0.177** | **0.013** | 136.51   | 11.63     |

Accuracy saturates by split size 100, which the paper adopts as the practical balance. For overlap size, the paper reports little sensitivity — overlap 3 gives ATE 0.075 / RRE 0.198 / RTE 0.017 and overlap 5 gives 0.076 / 0.175 / 0.013, with overlaps 7 and 10 also at ATE 0.076; the remaining entries of that sub-table did not extract cleanly from the PDF and are not transcribed here. Overlap 5 is the chosen default.

### Ablation: Bundle Adjustment Method

원논문 Table 9. VGGT를 백본으로, OOM을 피하기 위해 서브셋 크기 50을 쓴다.

| Variant                        | ATE↓      | RRE↓      | RTE↓      | Time      | Mem.      |
| ------------------------------ | --------- | --------- | --------- | --------- | --------- |
| w/o BA                         | 0.551     | 2.284     | 0.119     | **62.86** | 12.58     |
| BA w/ VGGT Tracking            | 0.602     | 2.659     | 0.155     | 137.68    | 33.22     |
| BA w/ LightGlue (pseudo video) | 0.526     | 1.572     | 0.061     | 140.53    | **12.58** |
| **BA w/ LightGlue (graph)**    | **0.522** | **1.563** | **0.060** | 141.08    | 12.68     |

Notable negative result: BA using VGGT's own tracking module is _worse than no BA at all_ on every accuracy metric, while costing 33.22 GB of memory. The paper's conclusion is that VGGT's iterative transformer-based tracking is not suited to large-scale BA. The gap between the graph-based and pseudo-video LightGlue variants is small (0.526 → 0.522 ATE).

### Runtime and Memory

Figure 7 plots runtime and peak GPU memory against input count from ~100 to ~1200 images, showing VGGT\*, FastVGGT, and π³ hitting OOM while the MERG3R-wrapped variants stay bounded. The curves are plots without printed values and are not transcribed here. The teaser figure states that for 1,000 input images MERG3R uses ~20 GB and ~8.5 min, against a baseline at >64 GB and >20 min.

## 💡 Insights & Impact

### Interleaving Is the Whole Trick

Table 7 is the paper's most instructive result, and it inverts an intuitive prior. If you must split N images into subsets, grouping _similar_ images together sounds right — that is what classical SfM's visual-similarity partitioning does, and what graph clustering here implements. It is the worst option (ATE 0.319 vs 0.077). Geometric foundation models need wide baselines inside each subset to triangulate at all; feeding them a cluster of near-duplicate views starves them of parallax. Interleaving deliberately does the opposite of clustering, and wins by a factor of four on ATE.

### Ordering Is Nearly Free Information

Table 6 shows the Hamiltonian-path pseudo-video is functionally equivalent to ground-truth video ordering. This matters because the ordering is not used for temporal reasoning — it is used only as a substrate for interleaved sampling. Once you accept that, "unordered image collection" stops being a distinct problem class from "video."

### The Wrapper Is Not Free at Small Scale

Honest reading of Table 2 and Table 5: at 500 images MERG3R usually leaves accuracy roughly where the backbone had it, and sometimes slightly below (π³ AUC@30 83.89 → 82.97). Bare FastVGGT holds the best 7-Scenes Acc/NC. The framework's value proposition is not "makes your model better" but "makes your model _runnable_" — the 1000-image column, where the baselines are all OOM, is the argument.

### Feature Matching Beats Learned Tracking for BA

Table 9's result that VGGT-tracking BA underperforms no BA is a useful warning. Learned dense trackers designed for short windows do not extend to cross-subset track merging at scale; classical SuperPoint + LightGlue with geometric filtering does, at a quarter of the memory.

### Model-Agnostic by Construction

Because MERG3R only requires `F_g(I) = (G, D, C)` — poses, depth, confidence — it composes with any current or future foundation model. The three backbones tested span quite different architectures (VGGT's alternating attention, FastVGGT's token merging, π³'s permutation-equivariant design) and all scale.

## 🔗 Related Work

- [VGGT](vggt.md) — the primary backbone; MERG3R uses the VRAM-efficient VGGT\* variant.
- [Pi3](pi3.md) — permutation-equivariant successor to VGGT; MERG3R's strongest pairing.
- [FastVGGT](fastvggt.md) — token-merging efficiency variant, both a baseline and a supported backbone.
- [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) — the pointmap lineage; DUSt3R's RRA/RTA protocol is followed here.
- [MASt3R-SfM](../foundation/mast3r-sfm.md) — pairwise gradient-based global refinement, the method MERG3R's BA is positioned against.
- [CUT3R](../dynamic/cut3r.md) / [TTT3R](ttt3r.md) — streaming/test-time-optimization baselines with good raw scalability but rapid accuracy degradation.
- [Fast3R](fast3r.md) — restructured attention for high token counts, discussed as still memory-bounded.
- [MapAnything](mapanything.md) — another recent feed-forward geometry foundation model cited in the same lineage.
- [Light3R-SfM](light3r-sfm.md) — scalable feed-forward SfM in an adjacent direction.

## 📚 Key Takeaways

1. **Cluster for diversity, not similarity.** Interleaved sampling beats graph clustering by 4× on ATE and sliding windows by ~1.4×; grouping visually similar frames starves local reconstructions of parallax.
2. **A Hamiltonian path over DINO similarity is as good as real video order.** ATE differs by ≤ 0.001 between the two.
3. **The gain is feasibility, not accuracy.** At 500 images MERG3R roughly matches its backbone; at 1000 images the backbones OOM and MERG3R does not.
4. **Classical matching beats learned tracking for cross-subset BA.** VGGT-tracking BA is worse than skipping BA entirely, at 33.22 GB vs 12.68 GB.
5. **Split size saturates early.** Accuracy peaks at 100 images per subset with ~11.6 GB peak memory, so the method is practical on modest GPUs.

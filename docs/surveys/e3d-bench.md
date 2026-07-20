# E3D-Bench: A Benchmark for End-to-End 3D Geometric Foundation Models (arXiv preprint)

## 📋 Overview

- **Authors**: Wenyan Cong, Yiqing Liang, Yancheng Zhang, Ziyi Yang, Yan Wang, Boris Ivanovic, Marco Pavone, Chen Chen, Zhangyang Wang, Zhiwen Fan
- **Institution**: University of Texas at Austin, Brown University, University of Central Florida, NVIDIA Research, Stanford University
- **Venue**: arXiv preprint (2025-06)
- **Links**: [Paper](https://arxiv.org/abs/2506.01933) | [Code](https://github.com/VITA-Group/E3D-Bench) | [Project Page](https://e3dbench.github.io/)
- **Verification**: PREPRINT (2026-07-20)
- **TL;DR**: The first systematic benchmark for end-to-end 3D geometric foundation models, evaluating 16 GFMs across five core tasks plus efficiency, on standard and out-of-distribution datasets with a shared toolkit.

## 🎯 Key Contributions

1. **First comprehensive GFM benchmark**: 16 models spanning feed-forward ViT and diffusion families, grouped by input type (image pairs, image sequences, multi-view, sparse-view).
2. **Five tasks plus efficiency**: Sparse-view depth, video depth, multi-view relative pose, multi-view 3D reconstruction (sparse and dense regimes), novel view synthesis, and latency/memory profiling.
3. **Out-of-distribution stress tests**: Drone footage, egocentric motion with blur, street driving, and air-ground paired trajectories — domains that no GFM was designed for.
4. **Standardized toolkit**: Automates dataset handling, evaluation protocols, and metric computation for reproducible comparison.
5. **Four takeaway findings** on task difficulty, data domains, architecture choice, and real-time readiness.

## 🔧 Technical Details

### Benchmark design

**Evaluated models** (원논문 Table 1) are grouped by input type: pairs (DUSt3R, MASt3R, LSM, MonST3R, NoPoSplat, Align3R, Splatt3R, Easi3R), sequences (Spann3R, CUT3R, Aether, Geo4D, GeometryCrafter), multi-view (Fast3R, VGGT), and sparse-view (FLARE). Table 1 also tags each model's output modality, metric-scale support, multi-view handling strategy (Global Alignment / Online Registration / Feed-Forward), backbone type, and training dataset count. Since LSM builds on DUSt3R without modifying its weights, they are reported jointly as DUSt3R/LSM.

### Per-task protocols

- **Sparse-view depth**: Depth extracted from the z-coordinate of predicted point maps, or confidence-weighted averaging as in DUSt3R for multiply-predicted views. Normalized models evaluated with median depth scaling; metric-scale models under both raw and median-aligned settings. Predictions upsampled to full resolution. Quasi-optimal source views selected to reduce selection bias. Five datasets spanning scene scales from 0.2m to 85m.
- **Video depth**: Same metrics with a looser δ threshold of 1.25. No access to intrinsics or ground-truth poses. Geo4D input sequences shorter than 16 frames are padded by repeating the last frame; Aether uses its default 41-frame one-shot output.
- **Pose**: ATE, RPE-translation, and RPE-rotation after Sim(3) Umeyama alignment. ULTRRA is handled separately because aerial and ground trajectories are reconstructed in separate coordinate systems, making a single Sim(3) alignment infeasible.
- **Reconstruction**: Extremely sparse (2–5 images, minimal/no overlap, wide baselines) and dense (10–50 images, high coverage). For models producing both local and global coordinates (Fast3R, CUT3R), only the global pointmap is evaluated to test direct inference. No ground-truth camera parameters at inference; Umeyama alignment to GT; official masks applied where available.
- **NVS**: 2-view input for all methods, because NoPoSplat does not support multi-view.
- **Efficiency**: Single 80GB NVIDIA A100, 2 to 128 input views, inference time and peak GPU memory averaged over 10 runs.

## 📊 Results

### Sparse-view depth estimation

원논문 Table 2. AbsRel ↓ and δ<1.03 ↑.

| Scale      | Method     | DTU AbsRel ↓ | DTU δ ↑    | ScanNet AbsRel ↓ | ScanNet δ ↑ | ETH3D AbsRel ↓ | ETH3D δ ↑  |
| ---------- | ---------- | ------------ | ---------- | ---------------- | ----------- | -------------- | ---------- |
| Normalized | Robust MVD | 2.490        | 80.056     | 7.468            | 35.651      | 9.302          | 42.909     |
| Normalized | DUSt3R/LSM | 2.741        | 75.685     | 4.732            | 61.337      | 3.132          | 74.851     |
| Normalized | MASt3R     | 3.343        | 68.301     | 5.949            | 54.516      | 2.471          | 81.291     |
| Normalized | Spann3R    | 6.431        | 38.339     | 7.779            | 33.713      | 5.121          | 54.708     |
| Normalized | CUT3R      | 6.200        | 47.421     | 8.231            | 39.464      | 5.224          | 59.864     |
| Normalized | VGGT       | **1.085**    | **94.305** | **4.386**        | **64.968**  | **1.782**      | **86.337** |
| Normalized | Fast3R     | 3.940        | 62.120     | 6.271            | 50.283      | 4.692          | 62.663     |
| Normalized | MonST3R    | 5.346        | 67.977     | 5.557            | 53.309      | 3.368          | 72.624     |
| Metric     | MASt3R     | 84.904       | 0.000      | 93.584           | 0.000       | 97.021         | 0.000      |
| Metric     | CUT3R      | 84.904       | 0.000      | 93.584           | 0.000       | 97.022         | 0.000      |

The metric-scale rows are the headline failure: both MASt3R and CUT3R score δ<1.03 of exactly 0.000 on every dataset. 원논문 Table 2 also covers KITTI and T&T, where VGGT is not always best — MASt3R leads KITTI δ<1.03 at 46.805 versus VGGT's 41.309.

### Video depth estimation

원논문 Table 3. AbsRel ↓ and δ<1.25 ↑, normalized scale.

| Method          | Bonn AbsRel ↓ | Bonn δ ↑ | KITTI AbsRel ↓ | KITTI δ ↑ | PointOdyssey AbsRel ↓ | PointOdyssey δ ↑ | Sintel AbsRel ↓ | Sintel δ ↑ |
| --------------- | ------------- | -------- | -------------- | --------- | --------------------- | ---------------- | --------------- | ---------- |
| DepthCrafter    | 0.107         | 88.3     | 0.120          | 86.2      | 0.144                 | 81.3             | 0.354           | 58.2       |
| DUSt3R/LSM      | 0.174         | 83.5     | 0.124          | 84.9      | 0.168                 | 77.8             | 0.475           | 59.1       |
| MASt3R          | 0.160         | 81.5     | 0.082          | 93.2      | 0.150                 | 79.3             | 0.374           | 63.9       |
| Spann3R         | 0.205         | 77.4     | 0.449          | 49.1      | 0.303                 | 58.4             | 0.587           | 43.3       |
| CUT3R           | 0.068         | 95.0     | 0.104          | 89.9      | 0.095                 | 88.4             | 0.466           | 56.0       |
| VGGT            | **0.056**     | **96.3** | **0.051**      | **96.6**  | **0.026**             | **99.0**         | **0.242**       | 65.9       |
| Fast3R          | 0.232         | 69.4     | 0.308          | 46.8      | 0.271                 | 66.2             | 0.565           | 48.7       |
| MonST3R         | 0.061         | 95.4     | 0.083          | 93.4      | 0.066                 | 92.3             | 0.343           | 59.4       |
| Align3R         | 0.062         | 96.8     | 0.105          | 89.2      | 0.077                 | 93.3             | 0.237           | 69.0       |
| Geo4D           | 0.060         | 97.8     | 0.086          | 93.8      | 0.082                 | 93.0             | 0.205           | **73.2**   |
| Aether          | 0.582         | 61.2     | 0.065          | 96.2      | 0.123                 | 87.9             | 0.343           | 69.4       |
| GeometryCrafter | 0.061         | 96.8     | 0.410          | 53.8      | 0.124                 | 83.6             | 0.280           | 72.4       |

VGGT leads AbsRel across these domains, but **Geo4D beats it on Sintel δ<1.25 (73.2 vs 65.9)** and Geo4D/Align3R beat it on Bonn δ<1.25. The benchmark also reports metric-scale rows where MASt3R collapses (0.967 AbsRel / 0 δ on Syndrone) and CUT3R improves but still fails on drone data.

### Multi-view relative pose estimation

원논문 Table 4, selected column groups. ✗ marks methods incompatible with pairwise inputs.

| Method     | CO3Dv2 ATE ↓ | CO3Dv2 RPE_rot ↓ | KITTI Odom. ATE ↓ | KITTI RPE_rot ↓ | ACID & Syndrone ATE ↓ | ULTRRA RPE_rot ↓ |
| ---------- | ------------ | ---------------- | ----------------- | --------------- | --------------------- | ---------------- |
| DUSt3R/LSM | 0.903        | 4.312            | 2.935             | 2.832           | 0.126                 | 70.390           |
| MASt3R     | 0.987        | 3.999            | 1.492             | 0.407           | 0.130                 | 78.036           |
| Spann3R    | 0.915        | 6.352            | 15.848            | 4.645           | 0.117                 | **38.366**       |
| CUT3R      | 0.847        | 6.361            | 2.421             | 0.669           | **0.071**             | 54.395           |
| VGGT       | **0.478**    | **2.264**        | **0.955**         | **0.335**       | 0.280                 | 77.281           |
| Fast3R     | 0.698        | 4.352            | 22.109            | 7.366           | 0.436                 | 54.150           |
| MonST3R    | 2.456        | 23.458           | 2.426             | 0.949           | 0.335                 | 77.325           |
| Geo4D      | 0.798        | 5.692            | 1.662             | 0.696           | 0.384                 | ✗                |
| Aether     | 3.168        | 21.643           | 1.553             | 0.744           | 0.152                 | ✗                |

VGGT dominates in-distribution and street-driving, but **CUT3R wins the drone datasets and Spann3R wins the air-ground ULTRRA challenge** — where every GFM performs poorly in absolute terms.

### Multi-view 3D reconstruction

원논문 Table 5, ACC ↓ / Comp ↓ / NC ↑.

| Setting          | Method     | DTU ACC ↓ | DTU Comp ↓ | 7-Scenes ACC ↓ | ScanNet ACC ↓ | TUM-RGBD ACC ↓ |
| ---------------- | ---------- | --------- | ---------- | -------------- | ------------- | -------------- |
| Extremely Sparse | DUSt3R/LSM | **1.731** | 1.936      | 0.146          | 0.474         | 1.108          |
| Extremely Sparse | MASt3R     | 1.895     | 2.003      | 0.262          | 0.467         | 0.738          |
| Extremely Sparse | FLARE      | 3.406     | 3.950      | 0.152          | 0.357         | 0.515          |
| Extremely Sparse | CUT3R      | 6.885     | 5.022      | 0.118          | 0.260         | 0.587          |
| Extremely Sparse | VGGT       | 2.716     | 2.301      | **0.077**      | **0.063**     | **0.385**      |
| Extremely Sparse | MonST3R    | 20.145    | 10.322     | 0.276          | 0.623         | 1.688          |
| Dense            | DUSt3R/LSM | **1.284** | **1.349**  | 0.022          | 0.026         | 0.620          |
| Dense            | MASt3R     | 1.374     | 1.409      | 0.025          | 0.035         | 0.209          |
| Dense            | CUT3R      | 4.710     | 2.413      | 0.025          | 0.042         | 0.740          |
| Dense            | VGGT       | 2.103     | 1.925      | **0.019**      | **0.016**     | **0.065**      |
| Dense            | MonST3R    | 14.455    | 7.508      | 0.100          | 0.346         | 1.138          |

**DUSt3R still wins DTU in both regimes** — the object-centric case where a two-view method with global alignment is strongest. VGGT wins every indoor scene dataset. MonST3R, third-best in video depth, is far worst here — the benchmark's evidence that per-attribute skill does not transfer to full scene reconstruction.

### Novel view synthesis

Full quantitative results are deferred to the appendix; the main paper reports only the qualitative finding of a noticeable gap between in-domain and out-of-domain performance, since these models train on small dataset subsets.

### Inference efficiency

Reported only as Figure 2 (inference time and peak GPU memory vs. number of input views, on a single A100) with no printed values. The findings stated in text: global-alignment methods incur significantly longer inference and are more prone to OOM; window-based GA (MonST3R) and sparse scene graphs (MASt3R) mitigate but do not resolve this; online registration methods (Spann3R, CUT3R) achieve faster inference and lower memory. Even the most efficient models still require tens of seconds for 256 input views.

## 💡 Insights & Impact

### Takeaway ①: task difficulty compounds

Three consistent gradients: pair-view geometry outperforms true multi-view; single-attribute prediction (depth, pose) is more reliable than full scene reconstruction; relative metrics beat absolute metric-scale outputs. The MonST3R contrast — top-3 in video depth, poor in reconstruction — is the clearest single data point. The benchmark's recommendation is to decompose hard joint objectives into simpler sub-problems under limited 3D data.

### Takeaway ②: generalization tracks data coverage

GFMs handle aerial views, street driving, and egocentric perspectives surprisingly well, but collapse on ULTRRA's air-ground pairs and on large altitude variation. The benchmark notes that a specialized method combining DUSt3R with a diffusion backbone and domain-specific training substantially improves this, confirming the cause is missing training data rather than an architectural limit. The same explanation covers metric-scale failure: metrically accurate training data is scarce.

### Takeaway ③: backbone family is not the deciding factor

Neither feed-forward ViT nor diffusion dominates. Feed-forward designs offer more input flexibility and scale better with data and modalities; diffusion models remain competitive on pose and video depth. What does matter is the strength of the 2D feature extractor — VGGT and Fast3R share a feed-forward transformer architecture, yet VGGT's DINO-based backbone consistently wins.

### Takeaway ④: not yet real-time

Even online-registration models need tens of seconds for 256 views, which rules out robotics and AR deployment as-is. The benchmark frames efficiency as co-equal with accuracy for the field's next phase.

### Stated limitation

All evaluations use GPU setups, following prior GFM studies. The authors call for extending to edge and mobile devices and exploring quantization and sparsity.

## 🔗 Related Work

This benchmark evaluates many papers already in this collection:

- [DUSt3R](../foundation/dust3r.md) and [MASt3R](../foundation/mast3r.md) — the pairwise baselines
- [VGGT](../reconstruction/vggt.md) — the consistent top performer across tasks
- [Fast3R](../reconstruction/fast3r.md) — architecturally similar to VGGT, consistently weaker
- [Spann3R](../reconstruction/spann3r.md) and [CUT3R](../dynamic/cut3r.md) — the online-registration models that win on efficiency
- [MonST3R](../dynamic/monst3r.md), [Align3R](../dynamic/align3r.md), [Easi3R](../dynamic/easi3r.md), [Geo4D](../dynamic/geo4d.md) — the dynamic/video branch
- [Large Spatial Model (LSM)](../understanding/largespatialmodel.md) — reported jointly with DUSt3R since it does not modify DUSt3R's weights
- [Splatt3R](../gaussian-splatting/splatt3r.md) — evaluated in the NVS task

## 📚 Key Takeaways

1. **VGGT is the strongest all-round GFM in this evaluation**, but not universally — DUSt3R wins DTU reconstruction in both sparse and dense regimes, Geo4D wins Sintel video depth δ, CUT3R wins drone pose, and Spann3R wins air-ground pose.
2. **Metric scale is broken.** MASt3R and CUT3R score δ<1.03 = 0.000 on every sparse-view depth dataset.
3. **Depth and pose are solved-ish; full reconstruction is not.** Most GFMs beat task-specific depth baselines while still struggling on dense 3D scene prediction.
4. **2D backbone quality transfers to 3D.** The VGGT vs Fast3R comparison isolates DINO pretraining as a major factor at matched architecture family.
5. **No GFM is real-time.** Tens of seconds for 256 views on an A100, with global-alignment methods hitting OOM.

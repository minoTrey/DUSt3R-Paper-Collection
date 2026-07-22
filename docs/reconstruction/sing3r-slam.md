# SING3R-SLAM: Submap-based Indoor Monocular Gaussian SLAM with 3D Reconstruction Priors (arXiv preprint)

![sing3r-slam — architecture](https://arxiv.org/html/2511.17207v2/x2.png)

_Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Kunyi Li, Michael Niemeyer, Sen Wang, Stefano Gasperini, Nassir Navab, Federico Tombari
- **Institution**: Technical University of Munich, Google, Munich Center for Machine Learning, VisualAIs
- **Venue**: arXiv preprint (2025-11)
- **Note**: The publication venue could not be confirmed from any primary source (GitHub badge, OpenReview, CVF openaccess, or arXiv comment). This entry should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2511.17207)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: A purely monocular indoor SLAM system that aligns CUT3R-predicted submaps into a persistent, differentiable Global Gaussian Map, then jointly refines poses and geometry by rendering-based bundle adjustment — correcting the geometric errors that prior 3D-prior SLAM systems leave untouched.

## 🎯 Key Contributions

1. **Gaussian map as global memory**: Local submaps reconstructed with 3D priors are aligned into a Gaussian map that acts as a persistent differentiable memory and a robust initialization for later optimization.
2. **Per-frame geometry refinement**: Differentiable bundle adjustment corrects errors inherited from the 3D prior itself — the paper's central complaint about VGGT-SLAM, MASt3R-SLAM, and ViSTA-SLAM is that they optimize poses but leave the prior's geometry unrefined.
3. **SE(3) submap registration + frame-level refinement**: Unlike VGGT-SLAM's SL(4) manifold optimization at the submap level, SING3R-SLAM resolves submap alignment and scale with SE(3) and delegates frame-level correction to the Gaussian stage.
4. **Feature-based loop closure**: Loop detection uses the geometry estimator's patch-level features plus reprojection overlap against the globally consistent Gaussian map, avoiding both extra feature correspondence and bag-of-words.
5. **Compact representation**: 7 MB global map versus 110 MB for MASt3R-SLAM's per-frame per-pixel point maps.

## 🔧 Technical Details

### Keyframe selection

Rather than optical flow or 2D feature matching, the motion filter flattens the geometry estimator's patch features (`H/16 × W/16 × 1024`) and computes an overlap ratio against the latest keyframe with similarity threshold β = 0.7. A low ratio signals a new keyframe.

### Submap construction

Each submap `G_i` holds K frames, with the last frame of `G_{i−1}` shared as the first frame of `G_i` for temporal continuity. The monocular geometry estimator D predicts self-coordinate point maps and local camera poses; depth is inferred from the local point maps.

### Global registration

Submap poses are transferred to world coordinates via the overlapping frame. New submap poses are then optimized against the fixed existing Gaussian map by minimizing a silhouette-masked L1 color loss plus a scale-invariant depth loss `L_scaleD`, after which depth is corrected by the exponentiated log-difference between rendered and predicted depth.

### Differentiable bundle adjustment

Over a sliding window of W frames, the Gaussians and poses are jointly updated:

```text
min  Σ  L_pho + λ_D L_D + λ_N L_N + λ_DN L_DN + λ_S L_S
```

where `L_pho` is L1 + SSIM, `L_D` is inverted depth L1, `L_N` is rendered normal loss, `L_DN` is depth-normal loss, and `L_S` prevents excessively slender Gaussians.

### Loop closure

The loop score is `S_{q,m} = 0.7·r^overlap + 0.3·r^feat`, combining reprojection overlap with feature similarity to avoid false positives from ambiguous geometry. A two-frame submap is formed from the query and its match, and submap-level pose graph optimization on SE(3) enforces adjacency consistency and loop closure. Optimized transforms are then applied directly to the Gaussians of each submap.

### Implementation

CUT3R is the monocular geometry estimator; RaDe-GS is the rasterizer. Single NVIDIA RTX 4090. K = 6 frames per submap, keyframe threshold 0.7, loop threshold 0.5, λ_scaleD = 10. Local BA: 20 online iterations, sliding window W = 10, λ_D = 10, λ_N = 0, λ_DN = 0.01, λ_S = 10. Global BA: offline, 20000 iterations, λ_D = 0, λ_N = 0.005, λ_DN = 0.005, λ_S = 0.

## 📊 Results

### Pose estimation on 7-Scenes

원논문 Table I. ATE in cm.

| Method             | Avg.    | chess   | fire    | heads   | office  | pumpkin | redkitchen | stairs  |
| ------------------ | ------- | ------- | ------- | ------- | ------- | ------- | ---------- | ------- |
| CUT3R              | 47.7    | 74.3    | 22.6    | 36.3    | 66.4    | 54.6    | 38.1       | 41.3    |
| MASt3R-SLAM        | 6.6     | 6.3     | 4.6     | 2.9     | 10.3    | 11.2    | 7.4        | 3.2     |
| VGGT-SLAM          | 6.7     | 3.6     | **2.7** | **1.8** | 10.3    | 13.3    | 5.8        | 9.3     |
| ViSTA-SLAM         | 5.5     | 7.3     | 3.5     | 2.8     | **5.5** | 12.9    | **3.5**    | 2.9     |
| HI-SLAM2           | 5.5     | 3.8     | 3.1     | 2.6     | 8.5     | 14.2    | 4.0        | **2.4** |
| SING3R-SLAM (Ours) | **4.9** | **3.3** | **2.7** | 4.5     | 7.2     | **8.7** | 3.6        | 4.5     |

SING3R-SLAM has the best average — the paper states this is a reduction of **over 10%** (Table I caption says 12%) — but is beaten per-scene on heads, office, redkitchen, and stairs.

### 3D reconstruction on 7-Scenes

원논문 Table II. Unit: m.

| Method             | Acc. ↓    | Complet. ↓ | Chamfer ↓ |
| ------------------ | --------- | ---------- | --------- |
| DROID-SLAM         | 0.141     | **0.048**  | 0.094     |
| MASt3R-SLAM        | 0.068     | **0.045**  | 0.056     |
| VGGT-SLAM          | 0.052     | 0.058      | 0.055     |
| SING3R-SLAM (Ours) | **0.045** | 0.047      | **0.046** |

SING3R-SLAM wins accuracy and Chamfer distance but **loses completeness to MASt3R-SLAM** (0.047 vs 0.045). The paper attributes this to over-smoothing at boundaries of large planar regions, where normal regularization without direct depth supervision oversmooths.

### Pose estimation on ScanNet-v2

원논문 Table III. ATE in cm.

| Method             | Avg.     | 00       | 59       | 106      | 169      | 181      | 207      |
| ------------------ | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| MASt3R-SLAM        | 7.95     | 6.96     | 8.48     | 9.53     | 8.34     | **7.16** | 7.20     |
| VGGT-SLAM          | 19.3     | 12.79    | 10.21    | 39.89    | 22.38    | 12.63    | 17.97    |
| MonoGS             | 122.7    | 149.2    | 96.8     | 155.5    | 140.3    | 92.6     | 101.9    |
| Splat-SLAM         | 7.66     | **5.57** | 9.11     | 7.09     | 8.26     | 8.39     | 7.53     |
| HI-SLAM2           | **7.16** | 5.82     | 7.30     | 6.80     | 8.25     | 7.41     | **7.40** |
| SING3R-SLAM (Ours) | 7.41     | 5.70     | **7.20** | **6.75** | **8.02** | 8.47     | 8.31     |

**SING3R-SLAM loses the ScanNet-v2 average to HI-SLAM2** (7.41 vs 7.16), though it wins four of six individual scenes. The paper describes the result as "competitive" rather than state-of-the-art on this dataset.

### Rendering on ScanNet-v2

원논문 Table IV, average.

| Method             | Input | PSNR ↑    | SSIM ↑   | LPIPS ↓  |
| ------------------ | ----- | --------- | -------- | -------- |
| SplaTAM            | RGB-D | 20.42     | 0.78     | 0.38     |
| Gaussian-SLAM      | RGB-D | 27.67     | **0.92** | 0.25     |
| Splat-SLAM         | RGB   | 29.48     | 0.85     | **0.18** |
| HI-SLAM2           | RGB   | 29.27     | 0.88     | 0.24     |
| SING3R-SLAM (Ours) | RGB   | **30.47** | 0.89     | 0.21     |

Best PSNR among both RGB-D and RGB-only Gaussian SLAM, but Gaussian-SLAM (RGB-D) still wins SSIM and Splat-SLAM wins LPIPS.

### Ablation

원논문 Table V, scene 0059 of ScanNet-v2. LBA = local bundle adjustment, GBA = global bundle adjustment.

| #   | frame refine | LBA | GBA | Loop | ATE ↓    | PSNR ↑    |
| --- | ------------ | --- | --- | ---- | -------- | --------- |
| (a) |              |     |     |      | 104.15   | –         |
| (b) |              |     |     | ✓    | 34.25    | –         |
| (c) |              | ✓   | ✓   | ✓    | 12.25    | 25.66     |
| (d) | ✓            | ✓   |     | ✓    | 9.39     | 26.43     |
| (e) | ✓            | ✓   | ✓   |      | 24.54    | 20.17     |
| (f) | ✓            | ✓   | ✓   | ✓    | **7.20** | **29.44** |

Row (a) is CUT3R with submap reconstruction alone and fails on long sequences. Frame-level refinement (c → f) is the largest single contributor.

### Runtime and map size

원논문 Table VI, scene 0059 of ScanNet-v2. Submap local reconstruction is counted as the equivalent of tracking.

| Method             | Tracking | LBA   | GBA   | Map Size |
| ------------------ | -------- | ----- | ----- | -------- |
| MASt3R-SLAM        | 5min     | –     | –     | 110 MB   |
| HI-SLAM2           | 8min     | 12min | 10min | 9 MB     |
| SING3R-SLAM (Ours) | 5min     | 10min | 8min  | **7 MB** |

Global bundle adjustment runs offline in parallel, so the paper argues the overhead is minimal.

## 💡 Insights & Impact

### 3D priors are good initializations, not good answers

The paper's framing is that SLAM3R, MASt3R-SLAM, VGGT-SLAM, and ViSTA-SLAM all consume the reconstruction network's raw point maps and optimize only camera poses on top. The prior's geometric error therefore survives into the final map. Ablation row (a) makes this concrete: CUT3R submaps alone yield 104.15 cm ATE on scene 0059, which the full system reduces to 7.20 cm.

### SE(3) plus rendering vs SL(4)

VGGT-SLAM absorbs alignment, scale, and projective error into an SL(4) submap-level optimization. SING3R-SLAM argues that scale and alignment are adequately handled by SE(3) plus a scale-invariant depth loss, and that the residual per-frame error is better fixed by differentiable rendering. The 7-Scenes reconstruction numbers (0.046 vs 0.055 Chamfer) support the choice, and Figure 1's wall-consistency comparison is the qualitative version.

### Compactness is a byproduct of the representation

7 MB vs 110 MB is not an engineering optimization but a consequence of replacing per-pixel point maps with Gaussians while retaining dense reconstruction through per-pixel depth rendering.

### Where it does not win

ScanNet-v2 average ATE goes to HI-SLAM2. Completeness on 7-Scenes goes to MASt3R-SLAM. The paper names its own failure mode — over-smoothing at large planar boundaries without direct depth supervision.

## 🔗 Related Work

- [VGGT-SLAM](vggt-slam.md) — the SL(4)-manifold submap baseline that SING3R-SLAM contrasts its SE(3) + rendering design against
- [MASt3R-SLAM](mast3r-slam.md) — the two-view feature-matching SLAM baseline; wins completeness, loses map compactness
- [SLAM3R](slam3r.md) — cited as the first system integrating DUSt3R into a sequential framework
- [CUT3R](../dynamic/cut3r.md) — used as the monocular geometry estimator inside SING3R-SLAM
- [VGGT](vggt.md) and [Spann3R](spann3r.md) — cited as the multi-view priors that improve geometric consistency but drift on long sequences
- [DUSt3R](../foundation/dust3r.md) and [MASt3R](../foundation/mast3r.md) — the underlying pointmap priors

## 📚 Key Takeaways

1. **Refine the prior's geometry, not just the poses.** The differentiating design choice versus VGGT-SLAM and MASt3R-SLAM, and ablation row (a) shows how badly the raw prior fails alone.
2. **A Gaussian map can serve as global memory.** Differentiable rendering makes it both the consistency enforcer and the compact deliverable (7 MB).
3. **Best 7-Scenes ATE and Chamfer; not best on ScanNet-v2.** HI-SLAM2 still holds the ScanNet-v2 average ATE, and MASt3R-SLAM holds 7-Scenes completeness.
4. **Loop closure and global BA are both necessary** — removing either (rows d, e) costs substantially more than removing local components.
5. **Features from the geometry estimator do double duty** — keyframe selection and loop detection both reuse patch features, avoiding a separate matcher or bag-of-words module.

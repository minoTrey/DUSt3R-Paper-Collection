# Cross3R: Feedforward 3D Reconstruction from Satellite, Drone, and Ground Images (arXiv preprint (2026-05))

![cross3r — architecture](https://arxiv.org/html/2605.07978v1/framework.png)

_Overview of Cross3R (원논문 Fig. 3)_

## 📋 Overview

- **Authors**: Qiwei Wang, Zhongyao Tuo, Xianghui Ze, Yujiao Shi
- **Institution**: ShanghaiTech University, Shanghai, China; Nanjing University of Science and Technology, Nanjing, China
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.07978)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward model (built on π³) that ingests a satellite tile plus a UAV image, a ground image, or both, and in a single forward pass recovers a cross-view 3D point cloud, 6-DoF camera poses, and on-tile (x, y)+yaw localization — using a single UAV image as an intermediate viewpoint to break the 3-DoF ceiling of prior satellite-only cross-view localization. Introduces CrossGeo, a 277,812-image tri-view dataset.

> The paper titles the method **Cross3R** (the TSV descriptor slug `crossview-sat` is renamed accordingly).

## 🎯 Key Contributions

1. **UAV as a geometric bridge**: A single UAV image at intermediate altitude supplies the roll/pitch/altitude cues a nadir satellite tile cannot, requiring only spatial overlap with the ground camera (no known relative pose), lifting cross-view localization from 3-DoF to full 6-DoF.
2. **Cross3R model**: A flexible feed-forward architecture extending π³ that jointly outputs a tri-view point cloud, 6-DoF poses for every view, and on-tile ground/UAV localization in one pass, with no satellite intrinsics required.
3. **Per-tile learned scale ρ**: Replaces satellite intrinsics with a single learned relative scale ρ, so any 3D point (including camera centers) can be placed on the satellite tile by transforming to the satellite frame and dividing by ρ.
4. **CrossGeo dataset**: An automatically curated tri-view corpus — 46,302 samples (× 6 images = 277,812) across 85 globally distributed scenes (every continent except Antarctica), each with two satellite, two UAV, and two ground views with 6-DoF poses and dense metric depth.

## 🔧 Technical Details

### CrossGeo dataset

- Built from Google Maps (300 m×300 m satellite tiles), Google Earth (UAV renders at altitudes H_drone ∈ [30, 120] m, pitch ∈ [0°, 90°], high-pitch oversampled), and Google Street View (ground). Satellite pose modeled as a virtual straight-down camera with a narrow [2°, 5°] FoV; sweeping altitude in Google Earth finds 5,726 m as the canonical height.
- Ground depth: Street View coarse absolute depth fused with Depth Anything V3 relative depth via Prior Depth Anything; UAV depth from COLMAP MVS; satellite depth by projecting that point cloud into the top-down virtual camera. Tri-view samples require all 15 pairwise overlaps non-empty.
- Scene-level split: train 75 scenes (38,962 samples), validation 5 scenes (3,614), cross-continent test 5 scenes (3,726). Real-world OOD test repurposes AnyVisLoc UAV photos augmented with Baidu Maps ground + Google Maps tiles → 5,068 tri-view samples.

### Model (extends π³)

- **Encoder**: injects a Fourier positional embedding of the satellite's normalized pixel grid into satellite tokens, and doubles π³'s register-token bank.
- **Alternating attention**: heads fuse hidden states across layers with softmax-weighted gates (early = local geometry, late = global layout).
- **Decoding**: satellite branch enforces an orthographic prior — (x_i, y_i) = (u_i, v_i)·ρ with a tiny MLP regressing ρ per satellite image, keeping only per-pixel depth; UAV/ground branches receive satellite features broadcast-added before the shared point/camera heads.
- **Per-sample altitude redefinition**: re-anchors the lower ground camera at y = 0 and places satellites at a constant H_sat = 150 m (instead of 5,726 m) so gradients through satellite translation stay bounded.
- Loss (from π³): L = L_geo + λ_n·L_norm + λ_c·L_conf + λ_p·L_cam, with λ_n = 1, λ_c = 0.05, λ_p = 0.1; L_norm enabled after a 5-epoch warm-up.
- Initialized from π³; adds only ~2.5M params (961.20M vs 958.70M, +0.26%), per-triplet inference 137.8 ms vs π³'s 138.5 ms. Fine-tuned on 8× NVIDIA L40: stage 1 at 224×224 (6h, batch 64/GPU), stage 2 at variable resolution (8h, batch 16/GPU); inference resizes to 504×504.

## 📊 Results

Baselines: VGGT and π³ (feed-forward), AerialMD (DUSt3R fine-tuned for aerial-ground), and π³* (π³ fine-tuned on CrossGeo under the same schedule, isolating data vs architecture contributions). All numbers are single forward pass, no per-scene optimization.

### Point cloud reconstruction + camera pose (CrossGeo test, n=3,726)

원논문 Table 2. Cross3R leads every column. Acc-mean↓; δ↑ (fraction within τ m); RRA/RTA↑ (recall at θ); AUC@30↑.

| Method      | Acc-mean↓ | δ@1m  | RRA@5° | RTA@5° | AUC@30 |
| ----------- | --------- | ----- | ------ | ------ | ------ |
| AerialMD    | 2.1334    | 48.56 | 3.00   | 7.50   | 35.41  |
| VGGT        | 2.3029    | 33.97 | 8.40   | 0.00   | 2.69   |
| π³          | 1.9818    | 42.31 | 26.45  | 1.34   | 15.98  |
| π³*         | 1.1771    | 61.40 | 86.99  | 29.93  | 71.87  |
| **Cross3R** | 1.0671    | 66.56 | 95.10  | 41.19  | 76.84  |

### Cross-view localization (CrossGeo, n=3,726)

원논문 Table 3. Meter = on-tile translation error; Yaw = rotation error about the up axis. Cross3R leads all twelve columns.

| Method      | Grd Meter-Mean↓ | Grd Yaw-Med↓ | Grd PCK@2m↑ | UAV Meter-Mean↓ | UAV PCK@2m↑ |
| ----------- | --------------- | ------------ | ----------- | --------------- | ----------- |
| AerialMD    | 22.22           | 11.38        | 4.92        | 12.77           | 25.88       |
| VGGT        | 121.42          | 20.89        | 0.02        | 12.12           | 29.19       |
| π³          | 62.84           | 8.12         | 0.96        | 14.82           | 11.26       |
| π³*         | 7.16            | 2.05         | 11.04       | 12.06           | 8.66        |
| **Cross3R** | 3.68            | 1.30         | 42.60       | 2.38            | 67.75       |

### Zero-shot KITTI Test 2 (n=7,542, ground+satellite only, unknown orientation)

원논문 Table 4. Cross3R is trained only on CrossGeo, never on KITTI. It attains the lowest median translation error and the strongest lateral recall at every threshold, beating the KITTI-supervised cross-view methods on most metrics — but not all: SliceMatch has higher orientation recall @1° (31.69 vs 16.14) and CCVPE has higher longitudinal recall @5m (42.12 vs 19.07).

| Method      | Loc Mean↓ | Loc Med↓ | Lat@1m | Lat@5m | Lon@5m | Ori@1° |
| ----------- | --------- | -------- | ------ | ------ | ------ | ------ |
| LM          | 15.50     | 16.02    | 5.60   | 25.60  | 25.76  | 0.60   |
| SliceMatch  | 14.85     | 11.85    | 24.00  | 72.89  | 33.12  | 31.69  |
| CCVPE       | 13.94     | 10.98    | 23.42  | 60.46  | 42.12  | 4.39   |
| π³*         | 16.28     | 14.85    | 9.44   | 44.18  | 21.36  | 15.27  |
| **Cross3R** | 11.69     | 10.52    | 39.11  | 85.95  | 19.07  | 16.14  |

### Out-of-distribution AnyVisLoc (n=5,068, real UAV photos)

원논문 Table 5. Cross3R has the best ground and UAV translation and best ground yaw; only UAV yaw trails π³* by a small margin (Mean 39.39 vs 38.11, Med 12.27 vs 11.24).

| Method      | Grd Meter-Mean↓ | Grd Yaw-Mean↓ | UAV Meter-Mean↓ | UAV Yaw-Mean↓ |
| ----------- | --------------- | ------------- | --------------- | ------------- |
| AerialMD    | 48.90           | 59.81         | 40.17           | 71.62         |
| VGGT        | 100.51          | 30.61         | 71.77           | 44.25         |
| π³          | 57.36           | 15.76         | 58.31           | 59.20         |
| π³*         | 10.53           | 13.13         | 16.49           | 38.11         |
| **Cross3R** | 10.49           | 8.00          | 14.51           | 39.39         |

### Ablation (CrossGeo full test, n=3,736)

원논문 Table 6. Removing the orthographic head (ρ) leaves Acc-mean nearly unchanged but collapses cross-view localization (ground Met.Med 2.14→4.04, UAV 1.64→7.33). Undoing the altitude redefinition is catastrophic on every metric (Acc 1.07→3.89, ground Met.Med →7.37, UAV →12.00). Dropping the UAV view substantially degrades ground localization, while dropping the ground view only marginally affects UAV localization.

| Variant              | Acc-mean↓ | Grd Met.Med↓ | UAV Met.Med↓ |
| -------------------- | --------- | ------------ | ------------ |
| Cross3R              | 1.07      | 2.14         | 1.64         |
| w/o ortho (ρ)        | 1.09      | 4.04         | 7.33         |
| w/o ms-fusion        | 1.16      | 2.24         | 1.79         |
| w/o sat-pos-embed    | 1.16      | 2.20         | 1.76         |
| w/o sat-inject       | 1.12      | 2.36         | 1.83         |
| w/o double register  | 1.12      | 2.43         | 1.80         |
| w/o altitude-redef   | 3.89      | 7.37         | 12.00        |
| w/o UAV (sat+grd)    | 1.28      | 2.48         | –            |
| w/o ground (sat+UAV) | 1.34      | –            | 1.84         |

Data-scaling (Fig. 8, low-res 224×224): nearly every metric improves monotonically from 20% → 100% of training data with no sign of saturation (그림 8, 곡선; 개별 수치 미인쇄).

## 💡 Insights & Impact

- Directly attacks the core limitation of ground-to-satellite localization: a single nadir tile gives no roll/pitch/altitude cues, forcing planar-motion 3-DoF assumptions that break on slopes and tilted mounts. The UAV bridge and per-tile scale ρ recover full 6-DoF without satellite intrinsics.
- The π³ → π³*→ Cross3R decomposition cleanly attributes gains: most of the improvement over π³ comes from the CrossGeo data (π³*), with the satellite-aware architecture adding the remainder (notably RRA@5° and RTA@5°).
- The ρ head is the essential glue tying the three branches into one scale-consistent frame — removing it collapses localization while barely changing point-cloud accuracy.
- Stated limitations: at most three images per forward pass (limited compute), pinhole-only inputs (no panoramic/fisheye), and a data-hungry model with headroom as CrossGeo scales; CrossGeo UAV imagery is synthetic (Google Earth), mitigated by the real AnyVisLoc OOD test.

## 🔗 Related Work

- **[π³](./pi3.md)**: the permutation-equivariant feed-forward backbone Cross3R extends with satellite-aware modifications; π³* is the key ablation baseline.
- **[VGGT](./vggt.md)**: feed-forward multi-view geometry baseline compared on CrossGeo.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: foundational feed-forward reconstruction; AerialMD (a baseline) fine-tunes DUSt3R for aerial-ground.
- **[Fast3R](./fast3r.md)** / **[MapAnything](./mapanything.md)** / **[SLAM3R](./slam3r.md)**: cited feed-forward reconstruction methods that assume common-altitude image collections.
- **[Depth Anything 3](./depth-anything-3.md)**: monocular depth foundation model whose predecessor (V3) supplies ground-depth priors in the CrossGeo pipeline.

## 📚 Key Takeaways

1. Cross3R adds a single UAV image as an intermediate viewpoint to bridge satellite and ground, lifting cross-view localization from 3-DoF to full 6-DoF in one feed-forward pass with no satellite intrinsics.
2. A learned per-tile scale ρ replaces satellite intrinsics and ties satellite/UAV/ground branches into a single scale-consistent frame; ablations show it is indispensable, as is the per-sample altitude redefinition.
3. On CrossGeo it leads all reconstruction, pose, and localization metrics; zero-shot on KITTI it beats KITTI-trained cross-view methods on most (not all) metrics; and it adds only ~2.5M params / ~1 ms over π³.

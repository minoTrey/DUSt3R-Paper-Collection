# DePT3R: Joint Dense Point Tracking and 3D Reconstruction of Dynamic Scenes in a Single Forward Pass (arXiv preprint (2025-12))

## 📋 Overview

- **Authors**: Vivek Alumootil, Tuan-Anh Vu
- **Institution**: University of California, Los Angeles
- **Venue**: arXiv preprint (2025-12)
- **Links**: [Paper](https://arxiv.org/abs/2512.13122) | [Code](https://github.com/StructuresComp/DePT3R)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward framework built on VGGT that jointly performs dense 3D point tracking and 3D reconstruction of dynamic scenes from unposed monocular sequences in a single forward pass, using a frame-to-query motion formulation and an intrinsic embedding.

## 🎯 Key Contributions

1. **Joint dense tracking + reconstruction**: Simultaneously reconstructs dynamic scenes and tracks all visible points from unposed monocular sequences, without auxiliary depth or external pose inputs.
2. **Frame-to-query motion formulation**: Predicts a motion field mapping points from each observation time `t` to a query time `q`, avoiding explicit frame-to-frame chaining and its drift accumulation.
3. **Extended VGGT backbone**: Adds a dedicated motion head, query conditioning, and an intrinsic embedding (focal lengths `fx`, `fy` and principal-point `py`) to a globally aggregated transformer.
4. **Memory efficiency for dense tracking**: Handles far more query points than query-based trackers at the same resolution.

## 🔧 Technical Details

### Representation and Backbone

- **Pointmap representation**: Adopts St4RTrack's time-dependent pointmaps; predicts per-frame point positions at observation time plus a motion map `M̂ = X̂(t→q) − X̂(t→t)`.
- **Backbone**: VGGT with DINOv2 tokenization, a learnable camera token and four register tokens per image, and alternating frame-wise/global attention. DPT heads regress pointmaps, depth, and (added) motion maps; the camera head outputs intrinsics and extrinsics.
- **Motion head**: An added DPT head initialized from VGGT's pointmap head, preserving pretrained capabilities.

### Training

- **Datasets**: Trained on five synthetic datasets — PointOdyssey, DynamicReplica, Kubric Movi-F (with trajectory supervision), plus Virtual KITTI 2 and TartanAir (pose/depth/pointmap only).
- **Two-phase training**: Phase 1 trains camera/depth/pointmap losses with intrinsic embedding (no query embedding); Phase 2 adds query embedding, motion head, and tracking loss (no confidence loss for stability), on PointOdyssey/DynamicReplica/Kubric.
- **Hardware**: Single NVIDIA RTX 6000 (~3 days); images scaled to width 514; multi-task loss follows VGGT.
- **Metrics**: APD (↑) and EPE (↓) after global median scaling.

## 📊 Results

### Capability + Benchmark Overview (원논문 Table 1)

원논문 Table 1. Panoptic Studio (Point Tracking) 및 TUM RGB-D (3D Reconstruction). ∗VGGT는 2D point tracking만 제공.

| Method         | Dynamic | Unposed | Dense PT | Temporal Attn. | PT APD ↑ | PT EPE ↓ | Recon APD ↑ | Recon EPE ↓ |
| -------------- | ------- | ------- | -------- | -------------- | -------- | -------- | ----------- | ----------- |
| DUSt3R         | -       | ✓       | -        | -              | -        | -        | 72.27       | 0.29        |
| MonST3R        | ✓       | ✓       | ✓        | -              | 51.32    | 0.46     | 61.38       | 0.36        |
| MASt3R         | -       | ✓       | ✓        | -              | -        | -        | 66.22       | 0.55        |
| St4RTrack      | ✓       | ✓       | ✓        | -              | 69.67    | 0.26     | 83.42       | 0.19        |
| SpatialTracker | ✓       | -       | -        | ✓              | 62.59    | 0.31     | -           | -           |
| VGGT ∗         | ✓       | ✓       | -        | ✓              | -        | -        | 89.87       | 0.09        |
| **DePT3R**     | ✓       | ✓       | ✓        | ✓              | 89.36    | 0.10     | 92.22       | 0.10        |

### World-Coordinate 3D Point Tracking (원논문 Table 2)

원논문 Table 2. Global median scaling 후 APD(↑)/EPE(↓).

| Method         | PO APD ↑  | DR APD ↑  | PS APD ↑  | PO EPE ↓   | DR EPE ↓   | PS EPE ↓   |
| -------------- | --------- | --------- | --------- | ---------- | ---------- | ---------- |
| SpatialTracker | 38.54     | 54.85     | 62.59     | 0.7499     | 0.9274     | 0.3094     |
| MonST3R        | 33.47     | 58.06     | 51.32     | 0.9021     | 0.4387     | 0.4568     |
| St4RTrack      | 67.95     | 73.74     | 69.67     | 0.3140     | 0.2682     | 0.2637     |
| **DePT3R**     | **91.33** | **91.12** | **89.36** | **0.0949** | **0.0925** | **0.1046** |

### World-Coordinate 3D Reconstruction (원논문 Table 3)

원논문 Table 3. PointOdyssey(PO) 및 TUM RGB-D. Global median scaling 후 APD(↑)/EPE(↓). VGGT는 TUM EPE에서 DePT3R보다 낮다(더 좋음).

| Method     | PO APD ↑  | PO EPE ↓   | TUM APD ↑ | TUM EPE ↓  |
| ---------- | --------- | ---------- | --------- | ---------- |
| DUSt3R     | 45.79     | 0.6386     | 72.27     | 0.2891     |
| MASt3R     | 56.90     | 0.4644     | 66.22     | 0.5510     |
| MonST3R    | 68.25     | 0.3044     | 61.38     | 0.3646     |
| St4RTrack  | 78.73     | 0.2406     | 83.42     | 0.1854     |
| VGGT       | 97.69     | 0.0514     | 89.87     | **0.0930** |
| **DePT3R** | **98.01** | **0.0406** | **92.22** | 0.0968     |

### Ablation (원논문 Table 4)

원논문 Table 4. Panoptic Studio.

| Variant                     | APD ↑ | EPE ↓  |
| --------------------------- | ----- | ------ |
| No intrinsic embedding      | 78.09 | 0.1735 |
| No center-crop augmentation | 82.94 | 0.1398 |
| **DePT3R (Ours)**           | 89.36 | 0.1046 |

### Memory (본문)

On a 10-frame video at 518×518 (RTX A6000, 48 GB): SpatialTrackerV2 exceeds 48 GB and OOMs at 40k query points; VGGT's 2D tracker exhausts memory at 22.5k query points; DePT3R generates over 268k point tracks (518×518 dense) using only 12 GB. (수치 미인쇄인 Figure 5 곡선은 옮기지 않음.)

## 💡 Insights & Impact

- Frame-to-query correspondences avoid drift from pairwise chaining, enabling long-range deformation reasoning; models trained on ≤10-frame clips generalize to 64-frame test sequences.
- The intrinsic embedding is crucial for resolving scale ambiguity in unposed dynamic reconstruction.
- Global temporal attention gives dense-tracking scalability well beyond query-based trackers in the same resolution regime.

## 🔗 Related Work

- Backbone and closest baseline: [VGGT](../reconstruction/vggt.md); foundation lineage [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), scalability from [Fast3R](../reconstruction/fast3r.md).
- Dynamic reconstruction/tracking peers: [MonST3R](monst3r.md), [CUT3R](cut3r.md), [Stereo4D](stereo4d.md), [POMATO](pomato.md); builds on St4RTrack's pointmap representation.

## 📚 Key Takeaways

1. A single-forward-pass model unifying dense 3D point tracking and reconstruction of dynamic scenes from unposed video.
2. State-of-the-art 3D point tracking on PointOdyssey/DynamicReplica/Panoptic Studio and strong reconstruction, though VGGT retains a slight edge on TUM RGB-D EPE.
3. Dramatically better memory scaling for dense tracking (268k tracks at 12 GB where VGGT/SpatialTrackerV2 OOM).

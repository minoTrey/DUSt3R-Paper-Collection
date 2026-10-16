# MUSt3R: Multi-view Network for Stereo 3D Reconstruction (CVPR 2025)

![MUSt3R Architecture](https://raw.githubusercontent.com/naver/must3r/main/assets/overview.jpg)
_Official implementation overview: current RGB frames read layerwise latent memory to predict global and local pointmaps._

## 📋 Overview

- **Authors**: Yohann Cabon, Lucas Stoffl, Leonid Antsfeld, Gabriela Csurka, Boris Chidlovskii, Jérôme Revaud, Vincent Leroy
- **Institution**: NAVER LABS Europe, ENS Paris-Saclay
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.01661) | [Code](https://github.com/naver/must3r) | [Project Page](https://europe.naverlabs.com/research/publications/must3r-multi-view-network-for-stereo-3d-reconstruction/)
- **Verification**: CONFIRMED (venue: cached DBLP verdict 2026-07-20; methods/results PDF re-reviewed 2026-10-15)
- **TL;DR**: Symmetrize DUSt3R decoders for shared-frame multi-image pointmaps. Cache historical layerwise features and selectively add frames to handle more views.

## 🎯 Key Contributions

1. **Shared Decoder**: All views share one decoder's weights.
2. **Multi-Layer Memory**: New images reuse previously computed layerwise features.
3. **3D Feedback**: Send final-layer 3D information into earlier-layer memory.
4. **Online and Offline Modes**: Support sequential prediction and a rendering path that re-predicts after constructing memory.
5. **Memory Selection**: Select memory frames according to newly observed space.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Time-ordered video or unordered RGB images, without camera calibration supplied to the network.
- **Output**: Per-image shared-frame pointmaps and confidence; focal lengths/camera poses can be recovered afterward.
- **Problem**: Predicting every image pair with DUSt3R increases pair counts and alignment costs.

### Memory and Rendering

```text
Initial images → shared encoder/decoder → layerwise memory
New image → memory cross-attention → shared-frame pointmap
          → add to memory if enough new space is observed
Optional rendering → read full memory and re-predict previous images
```

Here, rendering means re-estimating input-image pointmaps from memory.
It does not mean synthesizing new RGB images (§3.3).
MUSt3R-C is the causal path; default MUSt3R results include rendering and minimal Laplacian smoothing (§5.1).

Initialize with symmetric DUSt3R trained from CroCo v2, then freeze the encoder during multi-view training (§4).
Paper-evaluated checkpoints differ in configuration from subsequent official-repository updates.
Results below correspond to the arXiv v1 paper.

### Complexity and Limits

Memory grows with stored-image count (§3.4).
If every new frame reads all accumulated tokens, per-frame attention cost also grows.
Linear memory-size growth therefore does not unconditionally guarantee O(N) total sequence computation.
Frame selection reduces costs but guarantees neither unlimited views nor constant memory.

## 📊 Results

**Source**: [arXiv 2503.01661v1 PDF](https://arxiv.org/pdf/2503.01661v1).
Remove duplicate tables and incorrectly merged multi-level headers from the older note; organize results by protocol below.
Consult the source tables for all baselines, detailed sequences and supplementary results.

### Uncalibrated Visual Odometry: TUM RGB

Table 1, PDF p.6. All three methods below use dense unconstrained (U) settings.
ATE RMSE is in cm; lower is better. Mean error must not be read as FPS.
This table evaluates VO over 11 sequences.

| TUM Sequence | Spann3R ATE ↓ | MUSt3R-C ATE ↓ | MUSt3R ATE ↓ |
| ------------ | ------------- | -------------- | ------------ |
| fr1/360      | 20.7          | 8.9            | 7.8          |
| fr1/desk     | 16.1          | 5.1            | 4.0          |
| fr1/desk2    | 28.3          | 7.1            | 4.6          |
| fr1/plant    | 57.4          | 5.4            | 4.0          |
| fr1/room     | 84.8          | 13.4           | 9.9          |
| fr1/rpy      | 6.1           | 5.2            | 4.3          |
| fr1/teddy    | 92.4          | 6.9            | 4.2          |
| fr1/xyz      | 2.1           | 2.7            | 1.3          |
| fr2/xyz      | 4.4           | 1.7            | 1.2          |
| fr3/desk     | 20.7          | 15.6           | 15.3         |
| fr3/long     | 193.9         | 5.9            | 4.3          |
| Average      | 47.9          | 7.1            | 5.5          |

§5.1 measures speed on NVIDIA V100.
Spann3R: 4.8 FPS; MUSt3R-C: 11.1 FPS; MUSt3R: 8.4 FPS.
Spann3R's 47.9 is mean ATE (cm), not 47.9 FPS.

### TUM RGB-D: All Evaluation Categories

Table 2, PDF p.7. Evaluate all 46 test scenes in six categories.
Each cell is ATE RMSE (cm), **mean (median)**; this population differs from the 11-sequence mean above.

| Category   | Spann3R      | MUSt3R-C   | MUSt3R     |
| ---------- | ------------ | ---------- | ---------- |
| Test       | 4.1(4.0)     | 3.9(3.8)   | 3.8(3.8)   |
| Handheld   | 60.1(28.3)   | 7.2(7.1)   | 6.2(5.8)   |
| Robot      | 122.8(115.6) | 37.4(32.6) | 20.6(14.6) |
| Structure  | 32.7(6.8)    | 5.2(5.0)   | 3.9(3.6)   |
| Dynamic    | 88.3(76.6)   | 39.1(12.7) | 29.1(10.8) |
| 3D Objects | 80.9(61.2)   | 32.0(7.1)  | 22.7(5.6)  |
| Avg        | 64.8(48.7)   | 20.8(11.4) | 14.4(7.4)  |

### ETH3D SLAM

Table 5, PDF p.8. Separate ATE RMSE (cm) and FPS across the selected 8 trajectories.

| Method   | Mean ATE (cm) ↓ | FPS ↑ |
| -------- | --------------- | ----- |
| Spann3R  | 16.8            | 6.1   |
| MUSt3R-C | 11.2            | 11.8  |
| MUSt3R   | 10.0            | 8.7   |

### Point-Cloud Reconstruction

Table 6, PDF p.9. Only **mean** results under Spann3R's evaluation protocol are excerpted below.
Acc/Comp are distance errors; NC is normal consistency.
This note does not assume identical distance units across datasets.
Evaluate point clouds after all images have entered memory and rendering is performed (§5.3).

| Dataset    | Method     | Mean Acc ↓ | Mean Comp ↓ | Mean NC ↑ |
| ---------- | ---------- | ---------- | ----------- | --------- |
| 7Scenes    | DUSt3R-224 | 0.029      | 0.028       | 0.668     |
| 7Scenes    | Spann3R    | 0.034      | 0.024       | 0.664     |
| 7Scenes    | MUSt3R-224 | 0.028      | 0.027       | 0.665     |
| 7Scenes    | MUSt3R-512 | 0.026      | 0.027       | 0.617     |
| NeuralRGBD | DUSt3R-224 | 0.054      | 0.032       | 0.802     |
| NeuralRGBD | Spann3R    | 0.069      | 0.029       | 0.778     |
| NeuralRGBD | MUSt3R-224 | 0.062      | 0.031       | 0.788     |
| NeuralRGBD | MUSt3R-512 | 0.048      | 0.020       | 0.768     |
| DTU        | DUSt3R-224 | 2.296      | 2.158       | 0.747     |
| DTU        | Spann3R    | 4.785      | 2.743       | 0.721     |
| DTU        | MUSt3R-224 | 3.256      | 2.193       | 0.715     |
| DTU        | MUSt3R-512 | 3.261      | 1.965       | 0.661     |

Table 6 speed/memory use A100, unlike the preceding V100 VO measurements.
Maximum rendering batches are 10 for MUSt3R-224 and 5 for MUSt3R-512.
DUSt3R uses complete pair graphs. Implementation and attention kernels also affect memory differences (§5.3).

| Method     | FPS ↑ | GPU Memory (source G notation) ↓ |
| ---------- | ----- | -------------------------------- |
| DUSt3R-224 | 0.74  | 38.1                             |
| Spann3R    | 27.38 | 5.0                              |
| MUSt3R-224 | 40.41 | 4.1                              |
| MUSt3R-512 | 12.10 | 8.1                              |

§5.3 also reports 5.2G for naive attention in MUSt3R-224.
The difference between 4.1G and 5.0G cannot be attributed solely to memory algorithms.

### Additional Evaluations

Source Table 3 measures vertical FoV error (degrees), Table 4 scale error, Table 7 relative pose over 10 views,
and Table 8 multi-view depth with median normalization and no GT poses/intrinsics.
Appendix Tables 11–12 provide full TUM/ETH3D results.
Refer to these source tables instead of the older note's merged 33–37-column headers.
Do not combine these conditions with point-cloud/VO results into one performance ranking.

## 💡 Insights & Impact

The method caches previous images' decoder features to reduce pairwise recomputation.
Quality can decline far from an old reference view (§5.5).
Memory-selection criteria, input order and rendering settings affect costs and quality.

Results do not establish simultaneous gains on every metric.
For example, Table 6 gives MUSt3R-512 lower 7Scenes NC than MUSt3R-224.
VO and point-cloud paths use different hardware/protocols; one FPS figure is not general throughput.

Official code specifies the [MUSt3R Non-Commercial License](https://github.com/naver/must3r/blob/main/LICENSE).
Official [NOTICE](https://github.com/naver/must3r/blob/main/NOTICE) records checkpoint-data conditions.
This note records only those documents' existence and names; it does not assign collection licensing terms.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: the pairwise-pointmap regression foundation.
- **[MASt3R](../foundation/mast3r.md)**: adds correspondence features, a different objective from MUSt3R memory scaling.
- **[Spann3R](spann3r.md)**: a direct spatial-memory comparison; read ATE and FPS separately.
- **[VGGT](../foundation/vggt.md)**: another approach using joint attention across views.
- **[Slot3R](slot3r.md)**: subsequent work on spatially addressed state retention and bounded memory reads.

## 📚 Key Takeaways

1. Inputs are RGB images; primary outputs are shared-frame pointmaps.
2. Process new views through cached layerwise features and 3D feedback.
3. Linear memory growth does not guarantee linear total computation.
4. Read rendering settings, resolution, hardware and evaluation protocols alongside accuracy/speed.

# Slot3R: Set-Associative Spatial Memory for Streaming 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Xiyuan Zhang, Yanming Yang, Kaiyuan Xu, Ruibo Li, Chi Zhang
- **Institution**: Westlake University, University of Illinois Urbana-Champaign, Nanyang Technological University
- **Venue**: arXiv preprint (2026-10)
- **Links**: [Paper](https://arxiv.org/abs/2610.12282) | [Project Page](https://ashleyxyz.github.io/Slot-3R/)
- **Verification**: UNKNOWN (2026-10-15; arXiv v1 source reviewed; conference publication unconfirmed)
- **TL;DR**: Keep Point3R weights fixed and change spatial memory: preserve different observations at one location in separate slots, while reading bounded memory per frame.

## 🎯 Key Contributions

1. **Separate Address and Identity**: Averaging nearby features can mix surfaces/view directions. Position selects storage addresses; feature similarity determines merging.
2. **Set-Associative Memory**: Store multiple position/feature states per address. Use confidence/similarity for insertion, merging and replacement.
3. **Bounded Decoder Readout**: Separate total storage from decoder-read token counts; total memory is not constant.
4. **Training-Free Retrofit**: Change inference-time memory management without retraining Point3R.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Time-ordered RGB video; no future frames are used for the current frame.
- **Output**: Per-frame camera poses, depth and shared-frame pointmaps storing a 3D coordinate per pixel.
- **Problem**: Point3R patch locations summarize broad regions; nearby features may describe different surfaces.

### Memory Update and Readout

```text
Current RGB → frozen Point3R encoder
         → local memory + global-anchor retrieval → decoder → pose, depth and pointmaps
         → new position/feature candidates → confidence checks → slot merging/insertion/replacement
```

Source §3.2–3.4 proceeds as follows.

1. Assign spatial addresses through spherical-coordinate bin hashing.
2. Reject low-confidence candidates using within-frame quantiles.
3. Merge sufficiently similar high-confidence candidates at the same address; preserve different features separately or replace low-confidence slots.
4. Approximate current patch locations with previous-frame pointmaps for local retrieval; these are not exact pixel correspondences.
5. Add global anchors to local candidates and pass only the read-budget tokens to the decoder.

Defaults: 8 slots per address, 128 global anchors and a 640-token read budget (§4.1).
Optional VPC augments pose queries with separate view-direction memory. Tables below report Core without VPC.

## 📊 Results

### Point-Cloud Reconstruction

[arXiv v1 PDF](https://arxiv.org/pdf/2610.12282v1), Table 1, PDF p.7.
Sample every other frame (`k=2`); the table excerpts the 500-sampled-frame setting.
Acc measures predicted-point surface accuracy error; Comp measures completeness error; NC is normal consistency.
Distance units are unspecified in this table and are not inferred here.

| Dataset    | Method      | Acc ↓  | Comp ↓ | NC ↑   |
| ---------- | ----------- | ------ | ------ | ------ |
| 7Scenes    | Point3R     | 0.0745 | 0.0265 | 0.5510 |
| 7Scenes    | Slot3R Core | 0.0275 | 0.0158 | 0.5790 |
| NeuralRGBD | Point3R     | 0.2106 | 0.0706 | 0.6025 |
| NeuralRGBD | Slot3R Core | 0.0589 | 0.0236 | 0.6728 |

### Runtime and Evaluation Limits

Table 1 Avg. FPS averages completed runs under 300–500-frame conditions.
Measured on one RTX 4090 24 GB, excluding data loading and metric computation (§4.1).

| Dataset    | Point3R Avg. FPS ↑ | Slot3R Core Avg. FPS ↑ |
| ---------- | ------------------ | ---------------------- |
| 7Scenes    | 16.77              | 19.17                  |
| NeuralRGBD | 18.01              | 19.02                  |

Evaluation first encodes the whole sequence, then decodes causally.
This speed is therefore not actual online sensor-to-output latency.
Table 2 improves aligned relative depth but worsens metric-scale AbsRel on Bonn/KITTI.
Table 3 Core ATE gains do not imply gains in every relative-pose error.

## 💡 Insights & Impact

The practical question is what to merge when revisiting a location.
Keep different evidence at the same place instead of merging every nearby observation.
Read only selected evidence rather than the entire retained store.

Total memory grows as new space is observed (§5).
Fixed slot counts, spatial bins and read budgets can constrain different scenes/motions.
The paper validates Point3R; evidence does not yet establish identical effects on other backbones.

## 🔗 Related Work

- **[Point3R](point3r.md)**: supplies the modified spatial-pointer memory and frozen backbone.
- **[Spann3R](spann3r.md)**: earlier preservation of historical features in memory.
- **[CUT3R](../dynamic/cut3r.md)**: summarizes past observations in a fixed recurrent state.
- **[InfiniteVGGT](infinitevggt.md)**: a chronological-cache comparison; Slot3R manages spatially addressed states.
- **[MUSt3R](must3r.md)**: connects memory-feature selection with computation and reconstruction quality.

## 📚 Key Takeaways

1. Same location does not mean identical observation state; check feature content before merging.
2. Manage total storage separately from per-frame read costs.
3. Bounded reads do not bound total memory.
4. Judge point clouds, depth, poses and speed under their own protocols.

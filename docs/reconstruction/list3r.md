# LIST3R: Long-sequence Instance-aware 3D Reconstruction (arXiv preprint (2026-07))

![list3r — architecture](https://arxiv.org/html/2607.00375v1/x2.png)

_Method overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Jing Gao, Wei Wang, Feiran Wang, Yan Yan
- **Institution**: Beijing Jiaotong University; University of Illinois Chicago (Wei Wang: corresponding author)
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.00375) | [Project Page](https://yixn965.github.io/LIST3R/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An instance-aware framework for long-sequence 3D reconstruction that anchors reconstruction around persistent, trackable object instances, using them to recover long-range revisits and guide cross-subsequence alignment for globally consistent trajectories and point clouds.

## 🎯 Key Contributions

1. **Instance anchors for long-horizon reconstruction**: Uses recognizable object instances as persistent scene anchors to reconnect fragmented subsequences and consolidate local observations into a coherent global 3D scene, inspired by how humans organize spatial memory around stable objects.
2. **Local instance library per subsequence**: Builds a structured library of trackable instance anchors carrying semantic and geometric evidence for each partial reconstruction.
3. **Instance-guided cross-subsequence association**: Three-stage association — instance-enhanced long-range revisit discovery (ILRD), instance-aware subsequence merging (IASM), and confidence-weighted cross-subsequence graph optimization (CWGO).
4. **Global 3D instance library**: Consolidates local instances of the same physical object into persistent global records with object-level geometry, global location, and spatial relations — a structured scene-level representation that can serve as a 3D memory basis for downstream VLMs.

## 🔧 Technical Details

### Pipeline (three stages)

LIST3R partitions a long video into overlapping subsequences, reconstructs each with a feed-forward 3D foundation model (π³ is used as the base model per the paper), then organizes reconstruction around instance anchors.

**1. Local Instance Library Initialization (Sec. 3.1)**

- Uniformly select anchor frames per subsequence; run lightweight query-based instance discovery (following EntitySAM [28]) to initialize each instance with a mask prompt and object feature.
- Propagate discovered objects over the subsequence with SAM3 [4] to obtain temporally consistent mask tracks.
- Each local instance record stores: local identifier, multi-frame mask track, visible frames, per-frame 2D locations, and aggregated instance feature (Eq. 1).

**2. Instance-guided Cross-subsequence Association (Sec. 3.2)**

- **Long-range revisit discovery (ILRD)**: A frame-level loop detector yields coarse candidates (appearance score `s_det`); each candidate is strengthened by instance semantic consistency (`s_sem`, cosine similarity of matched instance features under mutual nearest matching) and spatial relation consistency (`s_rel`). Final revisit score: `s_loop = λ·s_det + (1−λ)·(s_sem + s_rel)` (Eq. 2).
- **Instance-aware subsequence merging (IASM)**: Rather than keeping only high-confidence points (which biases support toward large planar walls/floors), LIST3R evaluates per-instance motion inconsistency `δ(o)` (Eq. 3), removes dynamic/unstable instance regions, and retains structurally informative static objects as alignment support.
- **Cross-subsequence graph optimization (CWGO)**: Subsequences form a global association graph with adjacent + loop edges. Relative Sim(3) transforms are estimated via confidence-weighted alignment; edge weights derive from alignment confidence. Global transforms are optimized by minimizing a weighted Sim(3) pose-graph objective (Eq. 4).

**3. Global Instance Library (Sec. 3.3)**

- After alignment, local instances are lifted to 3D support from globally aligned point maps; nodes with overlapping global 3D support and compatible features are merged into unified global instance records (Eq. 5), each holding geometry, global 3D location, and spatial relations.

### Implementation notes (from Appendix A)

- One anchor frame sampled every 50 frames; each subsequence set to 100 frames (two anchor frames per subsequence); adjacent subsequences use a 30-frame overlap (following VGGT-Long).
- Candidate masks filtered by confidence, area, and redundancy before SAM3 propagation.
- Relaxed frame-level loop threshold of 0.5 for long-range candidate preselection (neighboring subsequences excluded from long-range loop candidates).
- Edge-weight sharpening: log-compression strength α = 0.30, contrast γ = 6.0.
- All experiments run on a single NVIDIA RTX 4090 GPU.

## 📊 Results

### Camera Pose Estimation on Long Sequences

All metrics are lower-better. VGGT and π³ run out-of-memory (OOM) when directly processing the full sequence. LIST3R ("Ours") attains the best ATE on all three datasets; on RTE/RRE some baselines remain favored by local trajectory characteristics (paper explicitly notes Scal3R obtains lower RRE on TUM and ETH3D, while CUT3R and TTT3R achieve lower RTE on BONN).

원논문 Table 1. (TUM)

| Method    | ATE (m) ↓ | RTE (m) ↓ | RRE (deg) ↓ |
| --------- | --------- | --------- | ----------- |
| VGGT      | OOM       | OOM       | OOM         |
| π³        | OOM       | OOM       | OOM         |
| CUT3R     | 0.866     | 0.963     | 40.189      |
| TTT3R     | 0.317     | 0.385     | 9.923       |
| VGGT-Long | 0.325     | 0.489     | 25.209      |
| π-Long    | 0.208     | 0.279     | 7.805       |
| Scal3R    | 0.267     | 0.329     | **5.724**   |
| **Ours**  | **0.150** | **0.211** | 6.974       |

원논문 Table 1. (ETH3D)

| Method    | ATE (m) ↓ | RTE (m) ↓ | RRE (deg) ↓ |
| --------- | --------- | --------- | ----------- |
| CUT3R     | 2.895     | 2.537     | 43.040      |
| TTT3R     | 1.317     | 0.939     | 10.326      |
| VGGT-Long | 1.292     | 1.701     | 32.922      |
| π-Long    | 0.562     | 0.455     | 13.654      |
| Scal3R    | 0.807     | 0.590     | **7.002**   |
| **Ours**  | **0.516** | **0.444** | 9.322       |

원논문 Table 1. (BONN)

| Method    | ATE (m) ↓ | RTE (m) ↓ | RRE (deg) ↓ |
| --------- | --------- | --------- | ----------- |
| CUT3R     | 0.319     | **0.561** | 58.127      |
| TTT3R     | 0.149     | 0.759     | 47.509      |
| VGGT-Long | 0.123     | 0.787     | 47.426      |
| π-Long    | 0.094     | 0.770     | 48.008      |
| Scal3R    | 0.117     | 0.779     | 49.093      |
| **Ours**  | **0.085** | 0.779     | **45.890**  |

### Point Cloud Reconstruction Quality

Chamfer / Acc. / Comp. are lower-better; NC and F@5cm are higher-better. LIST3R achieves the best across all five metrics on ETH3D, and the best Chamfer/Acc./Comp./F@5cm on NRGBD (NC comparable to the strongest baseline). Against π-Long, Chamfer improves 4.973 → 4.680 and F@5cm 68.917 → 73.363 on NRGBD.

원논문 Table 2. (ETH3D)

| Method    | Chamfer ↓  | Acc. ↓     | Comp. ↓    | NC ↑      | F@5cm ↑    |
| --------- | ---------- | ---------- | ---------- | --------- | ---------- |
| VGGT      | OOM        | OOM        | OOM        | OOM       | OOM        |
| π³        | OOM        | OOM        | OOM        | OOM       | OOM        |
| CUT3R     | 140.049    | 62.803     | 217.294    | 0.536     | 3.995      |
| TTT3R     | 102.590    | 36.604     | 168.575    | 0.610     | 7.274      |
| VGGT-Long | 50.551     | 56.748     | 44.354     | 0.618     | 19.834     |
| π-Long    | 41.536     | 37.775     | 45.296     | 0.686     | 32.655     |
| Scal3R    | 33.790     | 36.451     | 31.129     | 0.658     | 26.203     |
| **Ours**  | **27.362** | **31.094** | **23.629** | **0.709** | **36.450** |

원논문 Table 2. (NRGBD)

| Method    | Chamfer ↓ | Acc. ↓    | Comp. ↓   | NC ↑      | F@5cm ↑    |
| --------- | --------- | --------- | --------- | --------- | ---------- |
| CUT3R     | 73.239    | 50.051    | 96.427    | 0.575     | 9.009      |
| TTT3R     | 41.287    | 26.162    | 56.413    | 0.647     | 22.236     |
| VGGT-Long | 6.097     | 5.334     | 6.860     | **0.857** | 68.878     |
| π-Long    | 4.973     | 4.412     | 5.535     | 0.876     | 68.917     |
| Scal3R    | 7.669     | 4.231     | 11.106    | 0.829     | 71.203     |
| **Ours**  | **4.680** | **4.104** | **5.256** | 0.875     | **73.363** |

### Ablation Study

Starting from the π-Long split-and-fuse baseline, the three association components are progressively enabled. CWGO (Full) achieves the best results on all metrics.

원논문 Table 3. (Camera pose ablation)

| Variant       | ATE (m) ↓ | RTE (m) ↓ | RRE (deg) ↓ |
| ------------- | --------- | --------- | ----------- |
| Baseline      | 0.964     | 1.231     | 17.908      |
| + ILRD        | 0.708     | 0.724     | 13.351      |
| + IASM        | 0.706     | 0.720     | 13.340      |
| + CWGO (Full) | **0.277** | **0.402** | **6.920**   |

원논문 Table 4. (Reconstruction quality ablation)

| Variant       | Comp. ↓    | Chamfer ↓  | F@5cm ↑  |
| ------------- | ---------- | ---------- | -------- |
| Baseline      | 168.246    | 149.726    | 2.29     |
| + ILRD        | 86.192     | 125.382    | 4.80     |
| + IASM        | 82.961     | 121.684    | 4.91     |
| + CWGO (Full) | **32.719** | **35.325** | **9.91** |

Per-scene representative results (원논문 Tables 5–7, Appendix B) are not transcribed here; see the paper.

## 💡 Insights & Impact

- **Global consistency over local smoothness**: LIST3R's optimization prioritizes globally reliable subsequence relations, down-weighting weak cross-subsequence connections. This yields the best ATE on all datasets (the global-consistency metric) while some relative-pose metrics (RTE/RRE) stay competitive rather than best — an explicit, honestly reported trade-off.
- **Instances beat pure geometric confidence for alignment**: Selecting alignment support by geometric confidence alone concentrates support on planar walls/floors and discards structurally useful static objects (tables, chairs, cabinets) under viewpoint change/occlusion. Instance-aware merging keeps those informative anchors and removes dynamic instance regions.
- **Semantics + spatial layout disambiguate revisits**: Frame-level appearance similarity misses long-range revisits under viewpoint change; combining instance semantic consistency with spatial relation consistency recovers valid loops that frame-level detection misses (Fig. 8, qualitative).
- **Scalability**: Direct multi-view foundation models (VGGT, π³) OOM on full long sequences; the subsequence + instance-anchor design makes long-horizon reconstruction tractable on a single RTX 4090.
- **Downstream potential**: The global 3D instance library provides a persistent object-level scene memory usable by downstream VLMs for object querying, spatial-relation understanding, and scene-level reasoning.

## 🔗 Related Work

### Foundation models for feed-forward 3D reconstruction

- **[DUSt3R](../foundation/dust3r.md)** pioneered aligned pointmap prediction from image pairs without known poses or explicit optimization.
- **[MASt3R](../foundation/mast3r.md)** strengthens the formulation with improved local matching.
- **[Fast3R](fast3r.md)** processes many views jointly in a single forward pass.
- **[VGGT](vggt.md)** and **[π³ (pi3)](pi3.md)** regress camera parameters and dense geometry from flexible multi-view inputs; used here as direct feed-forward baselines (both OOM on full long sequences).

### Long-sequence reconstruction

- Streaming/stateful line: **[CUT3R](../dynamic/cut3r.md)** (persistent-state continuous 3D perception) and TTT3R (test-time adaptation for length generalization) — earlier scene information may be gradually weakened as sequences grow.
- Partition-and-align line: VGGT-Long (chunk-based processing + overlap alignment + loop closure over VGGT) and Scal3R (scalable test-time training) — but they lack stable anchors persisting across subsequences. LIST3R adds instance anchors as the missing organizing cue and introduces a strong π-Long split-and-fuse baseline (π³ as base model).

## 📚 Key Takeaways

1. **Object instances as persistent anchors** are an effective, scalable organizing cue for long-horizon 3D reconstruction — recovering long-range revisits and guiding fragment alignment where geometry/appearance alone fail.
2. **Best global trajectory accuracy (ATE) on TUM, ETH3D, BONN** and **best point-cloud quality on ETH3D (all five metrics)** and NRGBD (four of five), while feed-forward baselines OOM on full sequences.
3. **Ablation confirms complementarity**: ILRD expands long-range associations, IASM improves their reliability, and CWGO consolidates them into globally consistent poses and geometry.
4. **Honest trade-off**: prioritizing high-confidence long-range constraints can raise some local relative-pose errors (Scal3R lower RRE on TUM/ETH3D; CUT3R/TTT3R lower RTE on BONN), but improves overall global consistency.

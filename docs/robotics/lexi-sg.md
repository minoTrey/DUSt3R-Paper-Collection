# LEXI-SG: Monocular 3D Scene Graph Mapping with Room-Guided Feed-Forward Reconstruction (arXiv preprint 2026-05)

## 📋 Overview

- **Authors**: Christina Kassab, Hyeonjae Gil, Matı́as Mattamala, Ayoung Kim, Maurice Fallon
- **Institution**: Department of Engineering Science, University of Oxford; Department of Mechanical Engineering, Seoul National University; School of Informatics, University of Edinburgh
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.13741)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first dense monocular visual mapping system for open-vocabulary 3D scene graphs from RGB alone — it partitions the scene into rooms using foundation-model semantic priors, defers feed-forward reconstruction until each room is fully observed (avoiding sliding-window scale inconsistencies), and globally aligns rooms via a Sim(3) room-level factor graph.

## 🎯 Key Contributions

1. **First monocular open-vocabulary 3D scene graph SLAM**: Builds a full 3D scene graph from RGB alone, without depth or ground-truth pose input.
2. **Vision-only room identification**: Detects room transitions (doorways/corridors) using DINO features compared against text encodings, governed by a hysteresis mechanism.
3. **Room-based reconstruction**: Defers feed-forward inference until a room is fully observed, then reconstructs it once from a curated batch — reducing double-walling and scale drift.
4. **Sim(3) room-level factor graph**: Globally aligns per-room reconstructions while preserving local consistency and correcting monocular scale ambiguity.
5. **Open-vocabulary object segmentation module**: Lifts 2D mask tracklets into the scene graph as 3D object nodes.

## 🔧 Technical Details

### System Overview

- Input is a stream of RGB images only. The system maintains a room pose graph and incrementally populates a hierarchical 3D scene graph with room and object nodes.
- Scene graph G = (V, E) has room nodes (VR) and object nodes (VO); room-to-room edges encode relative Sim(3) transforms, room-to-object edges encode containment (not optimized).

### Room-Based Reconstruction

- Per-frame DINO features are matched against transition-cue text encodings; a running confidence score with hysteresis triggers a room transition. On transition, the accumulated batch is finalized, subsampled, and passed through the feed-forward model (MapAnything) to produce per-frame depths and poses in a local room frame.
- A few frames overlap between consecutive batches for continuity. Each room is reconstructed exactly once from its full observation set.

### Transition Edges, Loop Closure & Optimization

- Transition edges between adjacent rooms are estimated by feeding boundary frame pairs through the model: `Tri rj = Tri p · Tpq · Trj q⁻¹`.
- Loop closure compares new room image features against a database via cosine similarity; matches trigger a merge and edge re-verification.
- Object segmentation uses Recognize Anything + Grounding DINO for seed masks and a SAM2-based tracker to propagate masks into multi-view tracklets, lifted into object point clouds.
- Global optimization is over the room pose graph on Sim(3), solved with Levenberg–Marquardt; object poses in room-local frames update implicitly.

### Configuration

- MapAnything is the feed-forward model, batch size 60. MapAnything was chosen over VGGT and DepthAnything3 for robustness in long corridors. Experiments run on an NVIDIA RTX 4090.

## 📊 Results

### Camera Pose Estimation (ATE) on HM3D

원논문 Table II. ATE (m) on Habitat-Matterport 3D. X = failed or >2 m error. Lower is better.

| Method           | 824   | 829   | 843   | 847   | 873   | 877   | 890   |
| ---------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| ViSTA-SLAM       | 0.351 | 0.309 | 1.154 | 1.884 | X     | 0.576 | X     |
| VGGT-SLAM Sim(3) | 1.153 | 0.849 | 1.777 | 1.431 | X     | 0.872 | 0.613 |
| VGGT-SLAM 2      | 0.703 | 0.611 | 0.620 | X     | 0.477 | 0.955 | 0.553 |
| MASt3R-SLAM      | 0.693 | X     | 1.521 | 0.717 | X     | X     | 1.695 |
| **LEXI-SG**      | 0.343 | 0.143 | 0.628 | 0.461 | X     | 0.554 | 0.712 |

LEXI-SG achieves the lowest average trajectory error, though it fails (X) on scene 873 as do all monocular methods, and VGGT-SLAM 2 is second best on HM3D.

### Camera Pose Estimation (ATE) on Aria Office Dataset

원논문 Table III. ATE (m) on the self-collected AOD. X = failed or >2 m error.

| Method      | F1 Seq1 | F1 Seq2 | F1 Seq3 | GF Seq1 | GF Seq2 | GF Seq3 | avg   |
| ----------- | ------- | ------- | ------- | ------- | ------- | ------- | ----- |
| ViSTA-SLAM  | 0.840   | 1.038   | 1.405   | 0.668   | 0.291   | 1.651   | 0.982 |
| MASt3R-SLAM | 0.302   | X       | 0.294   | 0.241   | 0.139   | 0.296   | –     |
| **LEXI-SG** | 0.166   | 0.277   | 0.277   | 0.647   | 0.201   | 0.262   | 0.305 |

On AOD ground-floor sequences 1–2, LEXI-SG performance is reduced by room-segmentation errors (a large meeting room partly misclassified as corridor); MASt3R-SLAM is the second best but fails a sequence.

### Ablations (average ATE, m)

원논문 Table VI (room-based reconstruction + loop closure, excluding seq 877) and Table VII (batch size). Lower better.

| Study      | Setting               | AOD   | HM3D  |
| ---------- | --------------------- | ----- | ----- |
| Components | ✗ Room-Based / ✗ Loop | 0.812 | 0.626 |
| Components | ✓ Room-Based / ✗ Loop | 0.427 | 0.518 |
| Components | ✓ Room-Based / ✓ Loop | 0.305 | 0.474 |
| Batch size | 30                    | 0.467 | 1.074 |
| Batch size | 60                    | 0.305 | 0.474 |
| Batch size | 90                    | 0.401 | 0.594 |

Room-based reconstruction nearly halves ATE on AOD over a sliding-window baseline; loop closures add further gains (smaller on HM3D due to fewer revisits). Batch size 60 is best on both datasets.

### Runtime

원논문 Table VIII. AOD seq 3 (4248 frames). The full pipeline runs at 12.92 FPS without object segmentation and 1.56 FPS with; object segmentation dominates at 87.9% of cost, followed by MapAnything inference at 4.65%.

## 💡 Insights & Impact

- **Room-level semantics guide geometry**: Deferring feed-forward inference until a room is fully traversed gives each batch maximal co-visibility, improving per-room reconstruction and reducing the drift that accumulates when chaining many sliding-window batches.
- **Trade-off in open-plan spaces**: Because transitions are detected via doorways/corridors, room-segmentation precision drops in open-plan layouts — a stated limitation.
- **Feed-forward SLAM scaled semantically**: The work shows monocular feed-forward SLAM can be scaled to large multi-room environments and coupled to open-vocabulary scene graphs, with competitive OpenLex3D segmentation using only RGB.

## 🔗 Related Work

- **[MapAnything](../reconstruction/mapanything.md)**: The feed-forward reconstruction model used throughout LEXI-SG.
- **[VGGT](../reconstruction/vggt.md)** & **[MASt3R](../foundation/mast3r.md)**: Foundation models behind compared SLAM baselines.
- **[MASt3R-SLAM](../reconstruction/mast3r-slam.md)** & **[VGGT-SLAM](../reconstruction/vggt-slam.md)**: The feed-forward SLAM baselines LEXI-SG is evaluated against.

## 📚 Key Takeaways

1. LEXI-SG is the first system to build an open-vocabulary 3D scene graph from monocular RGB alone, without depth or ground-truth poses.
2. Room-guided, deferred feed-forward reconstruction plus a Sim(3) room factor graph reduces double-walling and scale drift, nearly halving ATE over sliding-window baselines.
3. It achieves the lowest average trajectory error among monocular feed-forward SLAM methods and competitive open-vocabulary segmentation, at 12.92 FPS without object segmentation (1.56 FPS with).

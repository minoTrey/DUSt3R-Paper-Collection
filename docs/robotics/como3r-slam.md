# CoMo3R-SLAM: Collaborative Monocular Dense SLAM with Learned 3D Reconstruction Priors for Outdoor Multi-Agent Systems (arXiv preprint 2026-05)

## 📋 Overview

- **Authors**: Zhihao Cao, Qi Shao, Shuhao Zhai, Feng Tian, Anh Nguyen, Hesheng Wang, Baoru Huang
- **Institution**: ETH Zurich; University of Liverpool; Harbin Engineering University; University of Ottawa; Shanghai Jiao Tong University; Imperial College London
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.30488) | [Project Page](https://como3r-slam.github.io)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: The first collaborative monocular dense RGB SLAM system that puts learned feed-forward 3D reconstruction priors (MASt3R pointmaps) at the center of outdoor multi-agent mapping, using dense cross-agent verification, closed-form Sim(3) gauge synchronization, and GPU-accelerated global Sim(3) bundle adjustment — no depth sensors or known intrinsics, online at 8 FPS.

## 🎯 Key Contributions

1. **First prior-centered collaborative monocular dense SLAM**: Systematically incorporates learned feed-forward 3D reconstruction priors at the core of outdoor multi-agent mapping, requiring neither depth sensors nor parametric intrinsics.
2. **Prior-guided cross-agent association**: A pipeline that generates candidate inter-agent links from the prior's encoder features and verifies them with dense pointmap matching and closed-form Sim(3) alignment, yielding reliable constraints even under low overlap and large viewpoint change.
3. **Global Sim(3) bundle adjustment with segment-level depth refinement**: A GPU-accelerated global Sim(3) BA over a unified multi-agent factor graph, complemented by segment-level depth refinement that alternates pose and depth optimization.

## 🔧 Technical Details

### Two-level architecture

Each agent runs a prior-guided front-end for real-time tracking and local dense fusion, maintaining a local Sim(3) keyframe graph. A central coordinator retrieves candidate cross-agent links over the prior's encoder features, verifies them via dense pointmap matching, performs closed-form Sim(3) gauge synchronization (Umeyama), and jointly refines all keyframe poses with a global Sim(3) bundle adjustment propagated back to every agent.

### Sim(3) tracking

All tracking and optimization operate in Sim(3) (assuming only a unique camera center), so the system is deployable on heterogeneous, uncalibrated cameras. Poses use left-perturbation updates on the sim(3) Lie algebra with analytic Jacobians. Tracking minimizes a robust ray-and-range residual (Huber kernel) against the MASt3R prior's pointmaps, whose metric pointmaps provide an approximate learned scale prior.

### Segment-level depth refinement

Per-pixel depth optimization would be under-constrained and huge, so pixels are grouped into a few hundred compact segments sharing a single depth degree of freedom (boundaries follow surface normals and log-range from the canonical pointmap). Stacked log-scales are solved by Gauss-Newton; the terminal refinement alternates a pose LM-IRLS step (geometry frozen) with a depth LM-IRLS step (poses frozen) until convergence.

## 📊 Results

Each sequence is split into two narrow-overlap sub-trajectories to simulate two agents. Tracking accuracy is ATE RMSE [m] after global alignment. Baselines assume known intrinsics; CoMo3R-SLAM (‡) runs without known calibration. ✗ = divergent/invalid.

### Tanks and Temples (ATE RMSE, m)

원논문 Table 1. Lower is better.

| Method                  | Type  | Barn  | Caterpillar | Ignatius | Truck |
| ----------------------- | ----- | ----- | ----------- | -------- | ----- |
| MAGiC-SLAM              | RGB-D | 0.519 | 0.349       | 0.356    | 0.316 |
| MAC-Ego3D               | RGB-D | ✗     | 0.361       | ✗        | 0.374 |
| CP-SLAM                 | RGB-D | 4.972 | 5.873       | 6.178    | 6.250 |
| MNE-SLAM                | RGB-D | 0.152 | 0.155       | 0.162    | 0.190 |
| MultiSlam-DiffPose      | RGB   | 0.221 | 0.148       | 0.167    | 0.035 |
| **CoMo3R-SLAM (Ours)‡** | RGB   | 0.051 | 0.102       | 0.144    | 0.053 |

CoMo3R-SLAM has the best ATE on Barn (0.051), Caterpillar (0.102), and Ignatius (0.144), and is second-best on Truck (0.053, behind MultiSlam-DiffPose's 0.035) — all from monocular RGB without intrinsics.

### Waymo (ATE RMSE, m)

원논문 Table 2. Lower is better. Driving scenes are harder (forward motion, low parallax, repetitive structure).

| Method                  | Type  | 158686 | 134763 | 153495 | 106762 |
| ----------------------- | ----- | ------ | ------ | ------ | ------ |
| MAGiC-SLAM              | RGB-D | 2.269  | 1.276  | 7.846  | 14.441 |
| MAC-Ego3D               | RGB-D | 6.063  | 3.506  | 8.827  | 26.867 |
| CP-SLAM                 | RGB-D | 12.277 | 10.287 | ✗      | 32.641 |
| MNE-SLAM                | RGB-D | 1.849  | 1.173  | 2.811  | 5.013  |
| MultiSlam-DiffPose      | RGB   | 1.808  | 2.607  | ✗      | ✗      |
| **CoMo3R-SLAM (Ours)‡** | RGB   | 1.773  | 1.965  | 3.491  | 5.004  |

CoMo3R-SLAM is best overall on 158686 (1.773) and 106762 (5.004) and remains competitive with the RGB-D MNE-SLAM on 134763 and 153495, where MNE-SLAM is stronger. It runs online at ~8 FPS.

## 💡 Insights & Impact

- **Priors stabilize scale under low parallax**: The soft metric prior from MASt3R pointmaps prevents per-agent gauges from drifting in scale during long forward-dominant driving, while Sim(3) BA redistributes residual scale through inter-agent edges instead of locking to a brittle initial guess.
- **Dense verification enables robust cross-agent links**: Accepting inter-agent edges only when both directions of the prior agree, then synchronizing gauges by closed-form Umeyama, yields well-conditioned constraints even under low overlap.
- **Limitations**: The system assumes a single common camera center (non-central/fisheye optics fall outside its regime) and its coordinator-based design ties communication load and fault tolerance to a single process as the team scales.

## 🔗 Related Work

- **[MASt3R](../foundation/mast3r.md)**: The feed-forward reconstruction prior whose pointmaps and encoder features drive tracking, cross-agent verification, and the metric scale prior.
- **[DUSt3R](../foundation/dust3r.md)**: Foundational feed-forward reconstruction formulation underlying the prior.
- **[MASt3R-Fusion](mast3r-fusion.md)**: Related MASt3R-prior-based SLAM/fusion system in the robotics collection.

## 📚 Key Takeaways

1. CoMo3R-SLAM is the first collaborative monocular dense SLAM to place feed-forward 3D reconstruction priors at the core of outdoor multi-agent mapping, needing no depth sensors or intrinsics.
2. It achieves the best ATE on three of four Tanks and Temples scenes and best-overall on two of four Waymo scenes, matching or exceeding RGB-D collaborative systems while running at ~8 FPS.
3. Closed-form Sim(3) gauge synchronization plus global Sim(3) bundle adjustment with segment-level depth refinement are the mechanisms that keep monocular multi-agent maps metrically consistent.

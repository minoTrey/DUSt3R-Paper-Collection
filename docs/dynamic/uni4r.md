# Marrying Optimal Transport and ODEs for Unified Continuous-Time 4D Reconstruction and Tracking (arXiv 2026)

## 📋 Overview

- **Authors**: Liying Yang, Hao Mo, Jialun Liu, Chen Liu, Xinxing Yu, Chenhao Guan, Hui Ma, Xiao Cao, Ajian Liu, Yanyan Liang
- **Institution**: Macau University of Science and Technology, University of Queensland, Great Bay University, Tsinghua University, National University of Singapore, Institute of Automation Chinese Academy of Sciences
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.09613)
- **Verification**: UNKNOWN (2026-10-15; source 2608.09613v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Learn a continuous-time velocity field and integrate it with an ODE to predict pointmaps and trajectories between integer frames.

## 🎯 Key Contributions

1. Connect 4D reconstruction and tracking through a shared continuous velocity.
2. Build a flow-matching decoder from OT-based anchor features.
3. Use integral consistency to learn fractional times from integer-time GT.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Timestamped RGB video and tracking queries.
- **Output**: World-coordinate pointmaps and 3D trajectories at arbitrary timestamps.
- **Problem**: Independent frame predictions or arbitrary interpolation struggle to preserve intermediate motion and surface structure.

### Method

1. Extract sequence anchor features with a global velocity branch.
2. Learn velocity features through optimal-transport paths and flow matching.
3. Combine reconstruction features and time embeddings in a local velocity predictor.
4. Integrate velocities with an ODE solver and supervise against integer-time GT pointmaps.

Use integer-timestamp supervision from Point Odyssey, Dynamic Replica and Kubric. Intermediate-time outputs do not receive additional GT velocity supervision directly.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.09613v2), Table 2, PDF p.6.

World-coordinate 4D reconstruction with APD/EPE after global median scaling. PO means Point Odyssey. These rows come from the feed-forward block.

| Dataset      | Method    | APD ↑ | EPE ↓ |
| ------------ | --------- | ----- | ----- |
| PO           | St4RTrack | 78.73 | 0.241 |
| PO           | Uni4R     | 80.71 | 0.222 |
| TUM-Dynamics | St4RTrack | 83.42 | 0.185 |
| TUM-Dynamics | Uni4R     | 84.36 | 0.181 |

Continuous-time kinematic metrics use a separate benchmark; do not mix them with integer-time reconstruction results. Solver steps affect accuracy and runtime.

## 💡 Insights & Impact

A shared velocity field explains reconstruction and tracking instead of regressing positions independently at every time.

- ODE integration errors and incorrect velocities can accumulate.
- Arbitrary-timestamp outputs do not imply sufficient observation of fractional-time GT.

## 🔗 Related Work

- [MonST3R](monst3r.md): a dynamic-geometry comparison family.
- [V-DPM](v-dpm.md): a reconstruction/tracking comparison model.

## 📚 Key Takeaways

1. Integrate continuous velocity to predict intermediate frames.
2. Combine integer supervision with integral consistency.
3. State alignment and solver conditions beside results.

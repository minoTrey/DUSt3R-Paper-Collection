# Topometric Autonomous Vehicle Localization by Combining Visual Embeddings and Feed-Forward 3D Models (arXiv 2026)

## 📋 Overview

- **Authors**: Eulogio Quemada-Torres, Alberto Jaenal, Francisco-Angel Moreno, Javier Gonzalez-Jimenez
- **Institution**: University of Malaga, University of Zaragoza
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.06021)
- **Verification**: UNKNOWN (2026-10-15; source 2608.06021v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Select references from place-retrieval beliefs and fuse DA3 local poses in a particle filter for planar localization under appearance changes.

## 🎯 Key Contributions

1. Build topometric maps from descriptor clusters and metric poses.
2. Select FF3D references using sequential beliefs.
3. Fuse appearance/geometric likelihoods in log space.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Georeferenced map images/poses, query RGB sequences and odometry.
- **Output**: Map-coordinate SE(2) positions, yaw and place beliefs.
- **Problem**: Compact VPR provides coarse metric positions; single-retrieval aliasing can cause large pose errors.

### Method

1. Cluster offline descriptors and retain diverse reference images.
2. Propagate particles with odometry and compute appearance likelihoods.
3. Run DA3 on queries and belief-selected references for metric poses.
4. Combine normalized log-likelihoods to update particle weights and poses.

Default descriptors are MixVPR and geometry uses DA3-Large. The system assumes an existing georeferenced map and odometry, rather than creating maps from RGB alone.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.06021v1), Table 2, PDF p.9.

4Seasons, identical map/query/post-initialization frames. Particle methods average seeded runs. AUC integrates jointly tightened position/yaw tolerances.

| Method              | Mean position (m) ↓ | Median position (m) ↓ | AUC ↑ |
| ------------------- | ------------------- | --------------------- | ----- |
| VPR + FF3D          | 1.404               | 0.144                 | 0.897 |
| Topometric proposal | 0.268               | 0.173                 | 0.864 |

Reducing large errors lowers the mean, but median/AUC are worse than the direct baseline. Map size counts online files, excluding model checkpoints.

## 💡 Insights & Impact

Sequential uncertainty reduces large reference-selection failures at a cost to instantaneous precision.

- Require georeferenced maps, odometry and a planar-pose assumption.
- Not every metric is superior; tolerances differ across datasets.

## 🔗 Related Work

- [Depth Anything 3](../reconstruction/depth-anything-3.md): the local metric-pose estimator.
- [Reloc3r](reloc3r.md): another feed-forward localization approach.

## 📚 Key Takeaways

1. Connect retrieval and metric geometry through probabilistic filtering.
2. Inspect means, medians and tails together.
3. Disclose map and odometry inputs.

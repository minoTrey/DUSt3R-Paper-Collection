# AMB3R-SLAM: Kilometer-scale SLAM with Hierarchical Backend (arXiv 2026)

## 📋 Overview

- **Authors**: Hengyi Wang, Lourdes Agapito
- **Institution**: University College London
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.19518)
- **Verification**: UNKNOWN (2026-10-15; source 2609.19518v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Combine a lightweight geometry frontend with a large long-context backend to correct relative-pose errors over several distance scales in long videos.

## 🎯 Key Contributions

1. Separate high-frequency frontend updates from low-frequency long-context mapping.
2. Combine short-range constraints from overlapping submaps with long-range constraints.
3. Evaluate monocular, stereo and LiDAR inputs separately.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Time-ordered imagery, with monocular, stereo or LiDAR inputs depending on configuration.
- **Output**: Globally connected trajectories and scene geometry.
- **Problem**: Short-context odometry errors accumulate over long drives; running large models on every frame is costly.

### Method

1. The default frontend estimates local geometry with DA3-Small. The paper's name does not mean it uses the AMB3R backbone.
2. Correct local errors with span-2 edges between overlapping submaps.
3. Add medium-range constraints from sparse long-context predictions of a larger DA3 backend.
4. Connect distant states through loop closure and global alignment.

The system uses large-model geometry priors during inference. Frontend model FPS differs from full-SLAM latency.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.19518v1), Table 2, PDF p.5.

Mean KITTI ATE (m). All rows below are monocular; offline and online processing are distinguished.

| Method     | Processing        | Mean ATE (m) ↓ |
| ---------- | ----------------- | -------------- |
| Scal3R     | Offline           | 14.55          |
| Glob3R     | Offline           | 13.21          |
| LoGeR      | Online            | 18.65          |
| AMB3R-SLAM | Online, monocular | 13.11          |

Stereo 12.15m and LiDAR 0.95m in the same table use additional inputs and are not monocular gains. Monocular sequence 01 reaches 55.91m, worse than Scal3R's 45.29m.

## 💡 Insights & Impact

Add large-model constraints only when long context is needed rather than executing the model on every frame.

- Static-scene geometry assumptions and reliable loop connections matter.
- Modality and online/offline differences prevent judging every configuration from one mean.

## 🔗 Related Work

- [VGGT](vggt.md): the feed-forward geometry family.
- [Depth Anything 3](depth-anything-3.md): the default geometry-model family.

## 📚 Key Takeaways

1. Separate small-frontend and large-backend roles.
2. Do not infer AMB3R-backbone usage from the name.
3. Separate monocular, stereo and LiDAR numbers.

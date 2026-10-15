# GAUGE: Group-Wise View-Inconsistency Rectification for Feed-Forward 4D Tracking (arXiv 2026)

## 📋 Overview

- **Authors**: Zhuoqian Feng, Weixing Chen, Ziliang Chen, Yang Liu, Liang Lin
- **Institution**: Sun Yat-sen University, Pengcheng Laboratory, X-Era AI Lab
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.32596)
- **Verification**: UNKNOWN (2026-10-15; source 2609.32596v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Correct residual 3D tracking errors with motion-group-specific radial scale and translation. No training is required, but sparse metric anchors and camera centers are additional inputs.

## 🎯 Key Contributions

1. Analyze group-specific view inconsistency remaining after global alignment.
2. Form motion groups from displacement directions and spatial connectivity.
3. Estimate group corrections from a small set of metric anchors.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Predicted, globally aligned 3D trajectories and visibility, camera centers, and sparse GT 3D anchors.
- **Output**: Corrected 3D point trajectories.
- **Problem**: Different dynamic objects have different radial biases that a single global scale cannot correct.

### Method

1. Separate groups by point displacement directions and spatial neighborhoods.
2. Estimate radial scale from robust ratios of anchor and predicted distances.
3. Scale each frame around its camera center and correct group translation.
4. Use separate centers or fallbacks for degenerate groups and leave unstable corrections unapplied.

Tracker weights remain unchanged. Training-free does not mean self-supervised metric correction from RGB alone: evaluation camera centers come from GT extrinsics.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.32596v1), Table 2, PDF p.7.

PointOdyssey, default anchor budget 5%. DQS means dynamic query screening; Full uses all queries visible in the first frame. D4RT is evaluated through a public reimplementation.

| D4RT configuration | DQS EPE ↓ | Full EPE ↓ |
| ------------------ | --------- | ---------- |
| Base               | 0.1812    | 0.1930     |
| + GAUGE            | 0.1269    | 0.1597     |

Errors or AJ can worsen for other trackers under Full. Improvements on dynamic groups do not establish improvements across the static background.

## 💡 Insights & Impact

Constrain correction to the radial direction, which 2D observations weakly constrain, to use sparse anchors efficiently.

- Assume metric anchors and cameras are available, including their acquisition cost.
- Motion grouping, low parallax and static-group assumptions can fail.

## 🔗 Related Work

- [D4RT](d4rt.md), [V-DPM](v-dpm.md): tracker families to which correction is applied.
- [Uni4R](uni4r.md): an approach that learns continuous motion itself.

## 📚 Key Takeaways

1. This is post-hoc correction, not tracker training.
2. Disclose GT anchor and camera inputs.
3. Distinguish dynamic-query and full-query protocols.

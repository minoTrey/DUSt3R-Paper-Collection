# LG-VLN: A Zero-Shot Vision-and-Language Navigation Framework with LangGraph State Orchestration (arXiv 2026)

## 📋 Overview

- **Authors**: Jianhe Zhao, Yanhua Qiu, Zhiyu Zhang, Zibo Zhao, Jinhua Xie
- **Institution**: Wuhan University; Huazhong University of Science and Technology
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.15098)
- **Verification**: UNKNOWN (2026-10-15; source 2609.15098v1 methods, tables and affiliations reviewed; independent publication evidence unavailable; a different-title/author Crossref candidate rejected)
- **TL;DR**: Combine VGGT geometry and CleanDIFT correspondences from monocular RGB/language instructions to update maps/poses, with LangGraph transitions controlling movement, stopping and recovery.

## 🎯 Key Contributions

1. Filter cross-frame correspondences with VGGT confidence and CleanDIFT similarity, then update maps/poses through Sim(3) registration.
2. Reuse CleanDIFT features in language-conditioned semantic value maps.
3. Connect instruction parsing, perception, mapping, planning, actions and recovery through persistent-state LangGraph execution.

This applies existing backbones to registration, mapping and navigation rather than training a new geometry backbone.
Geometry-input ablations and pose-error evaluation make this more than an external tool invocation.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Time-ordered monocular RGB, natural-language navigation instructions and known camera mounting height for metric initialization.
- **Output**: Forward, left-turn, right-turn and stop actions; internal poses, accumulated point clouds, occupancy/traversability and semantic-value maps.
- **Problem**: Separate geometric/semantic representations lose cross-frame correspondence and target-location consistency. Long instructions require tracking and recovery from false detections, stagnation and planning failures.

### Geometry and Shared Features

1. VGGT predicts relative depth, pointmaps and confidence. Fit ground planes during initial rotations and compare with known camera height to establish shared scale (§3.4.1, Appendix A.3).
2. Reject adjacent-frame candidates with low CleanDIFT cosine similarity or VGGT confidence (§3.4.2).
3. Refine RANSAC initialization with confidence/semantic-weighted robust Sim(3), bound scale changes and exclude failed registrations from map fusion (§3.4.3).
4. Fuse CleanDIFT target-reference similarity with BLIP-2 image–text relevance; reproject history using estimated poses into world-aligned bird's-eye-view maps (§3.6–3.7).

This is not one forward model mapping pointmaps directly to actions: combine pretrained inference, correspondence filtering, robust registration, mapping and planning.

### Navigation and Training Scope

LangGraph retains active sub-instructions, poses, maps, action history and recovery states, routing execution conditionally.
Grounding DINO and SAM2 locate target regions; semantic-waypoint selection precedes FMM local planning.
Zero-shot means no navigation-policy training or task-specific fine-tuning on the R2R-CE training split.
Visual/language backbones are already pretrained (§4.1).

## 📊 Results

**Source**: [arXiv 2609.15098v1 PDF](https://arxiv.org/pdf/2609.15098v1), Tables 3–4 (PDF p.15), Table 6 (p.17), Table 7 (p.19).

### Geometry Inputs and Navigation

A fixed 550-episode, per-scene-selected subset of R2R-CE val-unseen in Habitat-Sim/Matterport3D.
Initial scale-calibration rotations are excluded from action budgets and evaluation trajectories. Then allow 150 low-level actions with a 3.0m success threshold (§4.1).
Table 3 changes geometry inputs while retaining semantic/planning modules. SR/SPL are percentages; NE is in m.

| Geometry setting | Depth          | Pose      | SR ↑ | SPL ↑ | NE (m) ↓ |
| ---------------- | -------------- | --------- | ---- | ----- | -------- |
| Oracle           | GT             | GT        | 24.9 | 17.7  | 6.80     |
| Hybrid           | VGGT predicted | GT        | 24.2 | 15.2  | 7.04     |
| LG-VLN           | Predicted      | Predicted | 21.3 | 12.1  | 7.85     |

GT depth/poses appear only in Oracle/Hybrid diagnostics. Default navigation receives neither, but assumes known camera height and initialization observations.

### Pose Registration

Same-subset Table 7: ATE is positional RMSE after Sim(3) alignment to GT; RTE is consecutive-frame relative-translation RMSE.
Average per-episode RMSEs. Geometric RANSAC registration is matched apart from CleanDIFT filtering (§4.7).

| Correspondence filtering | ATE RMSE (m) ↓ | RTE RMSE (m) ↓ |
| ------------------------ | -------------- | -------------- |
| Without CleanDIFT        | 0.322          | 0.150          |
| With CleanDIFT           | 0.318          | 0.092          |

Local relative-translation error decreases, while ATE changes little. Do not generalize to solved global drift or every geometric task.

### Scale and Runtime Limits

Table 6 computes framewise AbsRel on valid GT pixels, then aggregates frame means/medians.
Fixed initial scale matches navigation deployment; per-frame median alignment is GT-assisted post-hoc diagnosis.

| AbsRel aggregation | Fixed initial scale ↓ | Per-frame GT median alignment ↓ |
| ------------------ | --------------------- | ------------------------------- |
| Mean               | 0.5874                | 0.0493                          |
| Median             | 0.2643                | 0.0319                          |

Do not present post-hoc aligned columns as deployed metric-depth accuracy; fixed-scale errors remain substantial.

Table 4 per-module call times: NVIDIA RTX 5090, Intel Xeon Platinum 8470Q, Ubuntu 22.04 (§4.1, §4.4).
These values are not end-to-end FPS; event-driven semantic-call frequencies and candidate counts differ.

| Module                | Time per call (ms) | Invocation                              |
| --------------------- | ------------------ | --------------------------------------- |
| VGGT                  | 178                | Every frame                             |
| CleanDIFT             | 179                | Every frame                             |
| Grounding DINO + SAM2 | 602                | Semantic update triggered               |
| BLIP-2 ITM            | 52–72              | Per short-text candidate when triggered |
| GTM + FMM             | 86                 | Map fusion and local planning           |

## 💡 Insights & Impact

Language navigation here both consumes geometry and directly applies semantic correspondence filtering with pose-error evaluation.
As with topometric localization and physical-property heads, separate backbone improvements from application-layer contributions.

- Results cover a fixed simulation subset, not full R2R-CE or real robots. Initial rotation/scale-calibration costs are excluded from navigation evaluation.
- Assume known camera height, visible ground and stable plane fitting. Monocular RGB alone does not automatically determine absolute scale.
- Table 2 removes CleanDIFT value-map signals, not all geometric filtering. Table 7 separately evaluates pose filtering.
- The paper cautions against strong statistical conclusions from single-run SR differences (PDF p.20). Sim(3)-aligned ATE does not guarantee absolute metric-scale accuracy.
- These geometric ablations alone do not establish LangGraph's independent effect. No experiments were reproduced.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): the geometry backbone used.
- [VGGT-SLAM](../reconstruction/vggt-slam.md): cited dense RGB SLAM/Sim(3)-backend context.
- [Topometric FF3D localization](../pose/topometric-ff3d.md): another direct learned-geometry localization application.
- [PhysVGGT](../understanding/physvggt.md): learns downstream prediction heads from geometry features.

## 📚 Key Takeaways

1. Inputs are RGB, language and camera height; outputs are actions and persistent map states.
2. Add CleanDIFT filtering and robust Sim(3) registration to VGGT predictions.
3. Read local-pose gains with fixed-scale limitations and initialization exclusions.

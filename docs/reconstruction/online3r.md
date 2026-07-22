# Online3R: Online Learning for Consistent Sequential Reconstruction Based on Geometry Foundation Model (arXiv preprint (2026-04))

![online3r — architecture](https://arxiv.org/html/2604.09480v1/x1.png)

_Overview of our proposed Online3R (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Shunkai Zhou, Zike Yan, Fei Xue, Dong Wu, Yuchen Deng, Hongbin Zha
- **Institution**: Peking University; State Key Laboratory of General Artificial Intelligence; T-Stone Robotics Institute, The Chinese University of Hong Kong; NVIDIA; Southwest University; Anqing Normal University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.09480) | [Project Page](https://shunkaizhou.github.io/online3r-1.0/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: Injects lightweight learnable visual prompts into a frozen MASt3R-SLAM pipeline and tunes them online at test time via a local-global self-supervised loss, letting a frozen geometry foundation model adapt to new scenes for consistent sequential reconstruction.

## 🎯 Key Contributions

1. **Online learning framework**: Online3R empowers a frozen pre-trained geometry foundation model (MASt3R) to adapt to novel scenes at test time via prompt tuning, addressing consistency in sequential reconstruction.
2. **Local-global self-supervised mechanism**: A local consistency constraint derived from temporally fused geometry improves subsequent predictions; a global consistency constraint enforces geometric invariance across distant keyframes to mitigate long-term drift.
3. **Parameter-efficient adaptation**: A prompt-based approach (prompt length Np = 32, dimension D = 1024) updates only lightweight prompts, keeping the backbone frozen while running at approximately 10 FPS.

## 🔧 Technical Details

### Base System

Online3R builds on MASt3R-SLAM, a real-time keyframe-based dense SLAM system that pairs each incoming frame with the latest keyframe and feeds the pair through a frozen MASt3R network to produce per-pixel pointmaps and confidence maps, plus a relative pose in Sim(3).

### Visual Prompt Tuning

A set of learnable prompts is inserted within MASt3R's ViT encoder (following VPT/Test3R). Output pointmaps become conditioned on the current prompt state, which is continuously optimized as the online video stream is processed.

### Self-Supervised Constraints

- **Local consistency (L_local)**: Uses the confidence-weighted fused keyframe pointmap as a high-quality pseudo ground truth, and takes the ℓ1 distance to a fresh single-shot prediction of the previous keyframe.
- **Global consistency (L_global)**: Samples two historical keyframes and penalizes the ℓ1 discrepancy between two predictions of the same keyframe geometry conditioned on different reference frames.
- **Total loss**: L_total = λ·L_local + (1 − λ)·L_global with λ = 0.5.

### Implementation

Built on the official MASt3R-SLAM release, AdamW with learning rate 1×10⁻⁴, prompts zero-initialized, all experiments on a single NVIDIA A100 GPU; input longest dimension resized to 512 pixels. Monocular RGB only (no depth input).

## 📊 Results

Camera pose is evaluated on TUM RGB-D and NRGBD; dense geometry on 7-Scenes and NRGBD, all in the monocular setting. "*" denotes the uncalibrated mode.

### Camera Pose — Average ATE (m)↓

원논문 Table 1 (TUM RGB-D avg) · Table 2 (NRGBD avg).

| Method        | TUM RGB-D avg ↓ | NRGBD avg ↓ |
| ------------- | --------------- | ----------- |
| MASt3R-SLAM   | 0.030           | —           |
| **Ours**      | **0.027**       | —           |
| Spann3R       | 0.238           | 1.444       |
| CUT3R         | 0.058           | 0.861       |
| Point3R       | 0.101           | 0.615       |
| MASt3R-SLAM\* | 0.060           | 0.090       |
| **Ours\***    | **0.056**       | **0.076**   |

TUM RGB-D calibrated rows use the non-starred variants; NRGBD is reported only in the uncalibrated mode.

### Dense Geometry (uncalibrated)

원논문 Table 3. Acc / Comp / Chamfer distance, all lower is better.

| Types   | Methods       | 7-scenes Acc↓ | Comp↓ | Chamf↓    | NRGBD Acc↓ | Comp↓ | Chamf↓    |
| ------- | ------------- | ------------- | ----- | --------- | ---------- | ----- | --------- |
| Offline | DUSt3R-GA     | 0.146         | 0.181 | 0.164     | 0.144      | 0.154 | 0.149     |
| Offline | MASt3R-GA     | 0.185         | 0.180 | 0.183     | 0.085      | 0.063 | 0.074     |
| Offline | Test3R        | 0.105         | 0.136 | 0.121     | 0.083      | 0.079 | 0.081     |
| Online  | CUT3R         | 0.126         | 0.154 | 0.140     | 0.099      | 0.076 | 0.088     |
| Online  | Point3R       | 0.124         | 0.139 | 0.132     | 0.079      | 0.073 | 0.076     |
| Online  | MASt3R-SLAM\* | 0.068         | 0.045 | 0.056     | 0.065      | 0.094 | 0.080     |
| Online  | **Ours\***    | **0.039**     | 0.067 | **0.053** | **0.053**  | 0.093 | **0.073** |

Online3R surpasses offline methods like DUSt3R-GA and MASt3R-GA in Acc and Chamfer. Note it trades slightly higher Completion than MASt3R-SLAM\* on 7-scenes (0.067 vs 0.045).

### Efficiency & Ablation

원논문 Table 4 (efficiency) · Table 5 (7-scenes component analysis, avg Acc).

| Method | ATE↓  | #iter. | FPS  |     | Variant  | Acc↓      |
| ------ | ----- | ------ | ---- | --- | -------- | --------- |
| M-S\*  | 0.090 | –      | 13.2 |     | M-S\*    | 0.068     |
| Ours\* | 0.076 | 32     | 10.0 |     | Local\*  | 0.042     |
|        |       |        |      |     | Global\* | 0.044     |
|        |       |        |      |     | Full\*   | **0.039** |

Online learning adds a marginal FPS cost (13.2 → 10.0) while significantly improving ATE; each constraint helps independently but their joint application (Full) is best.

## 💡 Insights & Impact

- **Adaptation over generalization**: Rather than training a perfect model for all scenes, Online3R argues the ability to adapt to new environments at test time is necessary, and realizes it with parameter-efficient prompts.
- **Fusion as pseudo ground truth**: The paper repurposes MASt3R-SLAM's confidence-weighted multi-view fusion as a supervisory signal, distilling multi-view fused geometry back into the feed-forward network.
- **Non-overlapping views**: The learned prompt lets the model reconstruct non-reference geometry where the frozen MASt3R baseline fails, hinting at prompts as implicit scene representation.
- **Limitations**: Adds computational overhead, and is currently limited to static-scene sequential reconstruction; extending to dynamic 4D scenes is left as future work.

## 🔗 Related Work

- **[MASt3R](../foundation/mast3r.md)** & **[MASt3R-SLAM](mast3r-slam.md)**: The frozen backbone and base SLAM system Online3R adapts.
- **[DUSt3R](../foundation/dust3r.md)**: The feed-forward pointmap foundation the lineage builds on.
- **[Test3R](test3r.md)**: Introduced prompt tuning to geometry foundation models for offline consistency; Online3R adapts the idea to efficient online tuning.
- **[Spann3R](spann3r.md)**, **[CUT3R](../dynamic/cut3r.md)**, **[Point3R](point3r.md)**: Online sequential reconstruction baselines compared against.
- **[VGGT](vggt.md)**: Multi-view alternating-attention foundation model referenced for its memory limits in sequential settings.

## 📚 Key Takeaways

1. Online3R adapts a frozen geometry foundation model to new scenes at test time by tuning lightweight visual prompts, no ground truth required.
2. A local-global self-supervised strategy supplies pseudo supervision from temporal fusion and enforces cross-view consistency to fight drift.
3. It reaches state-of-the-art average ATE on TUM RGB-D and NRGBD and best geometry on 7-Scenes/NRGBD among online methods, at ~10 FPS on a single A100.
4. The approach is static-scene only for now; dynamic 4D adaptation is the stated next direction.

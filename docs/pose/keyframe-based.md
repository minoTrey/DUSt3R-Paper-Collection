# Keyframe-Based Feed-Forward VO: RL-Driven Keyframe Selection for VGGT (arXiv preprint (2026-01))

## 📋 Overview

- **Authors**: Weichen Dai, Wenhan Su, Da Kong, Yuhang Ming, Wanzeng Kong
- **Institution**: Key Laboratory of Brain Machine Collaborative Intelligence of Zhejiang Province, School of Computer Science, Hangzhou Dianzi University, Hangzhou, China; Technion Autonomous Systems Program, Technion – Israel Institute of Technology, Haifa, Israel
- **Venue**: arXiv preprint (2026-01)
- **Links**: [Paper](https://arxiv.org/abs/2601.16020)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A keyframe-based feed-forward visual odometry method that uses VGGT as backbone and learns an RL policy (PPO) to decide, from mean-pooled DINOv2 CLS tokens plus relative poses, whether each new frame should be kept as a keyframe — replacing hand-crafted geometric heuristics with a data-driven keyframe policy aligned to VGGT's internal characteristics.

> Note: the paper does not define an acronym for its method (it is referred to descriptively as "keyframe-based feed-forward VO"), so the descriptive slug is retained.

## 🎯 Key Contributions

1. **RL-based keyframe policy for feed-forward VO**: Introduces a data-driven, reinforcement-learning keyframe selection method that aligns input-frame selection with VGGT's intrinsic representation characteristics rather than explicit geometric metrics.
2. **Keyframe management for 3D-vision foundation models**: Adapts the classic keyframe idea to "black-box" foundation models like VGGT, where explicit geometric metrics are unavailable.
3. **Cross-dataset generalization**: Trained only on the synthetic TartanAir dataset yet evaluated on EuRoC, TUM-RGBD, and KITTI, demonstrating strong sim-to-real generalization.

## 🔧 Technical Details

### Backbone and sliding window

- Uses VGGT as backbone: DINOv2 tokenization → alternating frame-wise self-attention and global cross-attention → task heads for camera poses, depth maps, and point clouds.
- A fixed-size sliding window is maintained; the first frame in the window is the anchor whose global pose is known. All window frames are fed to VGGT to obtain relative poses to the anchor, then converted to global poses. Window size is 8; the first 7 frames are treated directly as keyframes for fast initialization, with the first sequence frame set to identity pose.

### RL formulation

- Modeled as an MDP M = {S, A, P, R, γ}. The agent (a three-layer ReLU MLP; separate actor and critic sharing the architecture) decides whether to retain the new frame as a keyframe or replace an existing one.
- **Observation**: mean-pooled DINOv2 CLS tokens over all frames in the keyframe window, concatenated with each frame's relative pose to the new input frame (relative pose normalized via running mean/std).
- **Reward**: r = λ₁·max(−1, λ_threshold − e_tran) + λ₂·α_keyframe, where e_tran is the translational error after Umeyama alignment. Parameters: λ₁ = 0.01, λ₂ = 5×10⁻³, λ_threshold = 0.2, α_keyframe = 0.000025. The α_keyframe compensation term prevents action collapse (always adding/removing keyframes).
- **Training**: PPO (Stable Baselines3) on TartanAir, 20 concurrent VGGT environment instances, learning rate linearly decayed 3×10⁻⁴ → 3×10⁻⁵ with Adam, a single RTX 4090, plus a privileged critic and DPVO-style photometric/frame-drop augmentation.

### Evaluation

- Metric: RMSE of ATE [m] after Umeyama alignment, over the poses of all input frames.
- For fairness, VGGT-SLAM and VGGT-Long use the same window size with loop closure disabled; StreamVGGT / FastVGGT adopt the VGGT-Long "chunk and align" strategy with no further post-processing.

## 📊 Results

### EuRoC — ATE [m] ↓

원논문 Table I. Ours (no post-processing) attains the best average, narrowly ahead of VGGT-Long which requires post-processing.

| Method       | Keyframe | Post-Proc. | MH01 | MH04 | V101 | V201 | V203 | Avg  |
| ------------ | -------- | ---------- | ---- | ---- | ---- | ---- | ---- | ---- |
| VGGT-Long    | ✗        | Required   | 2.11 | 4.65 | 1.46 | 1.68 | 1.91 | 2.45 |
| VGGT-SLAM    | ✓        | Required   | 4.78 | 6.79 | 1.81 | 2.36 | 1.96 | 3.31 |
| FastVGGT     | ✗        | No         | 4.58 | 6.71 | 2.28 | 2.32 | 2.52 | 3.58 |
| StreamVGGT   | ✗        | No         | 4.29 | 6.80 | 1.84 | 2.28 | 1.92 | 3.42 |
| InfiniteVGGT | ✗        | No         | 3.48 | 5.45 | 1.63 | 1.98 | 1.78 | 2.97 |
| **Ours**     | ✓        | No         | 2.74 | 4.82 | 1.30 | 0.99 | 1.86 | 2.44 |

### TUM-RGBD — ATE [m] ↓

원논문 Table II. Here VGGT-Long (with required post-processing) has the lowest average (0.169); Ours (0.186) is best among the no-post-processing methods and beats VGGT-SLAM.

| Method       | Post-Proc. | fr1-desk | fr1-room | fr1-rpy | fr1-xyz | Avg   |
| ------------ | ---------- | -------- | -------- | ------- | ------- | ----- |
| VGGT-Long    | Required   | 0.138    | 0.283    | 0.057   | 0.087   | 0.169 |
| VGGT-SLAM    | Required   | 0.216    | 0.770    | 0.048   | 0.042   | 0.314 |
| FastVGGT     | No         | 0.433    | 1.109    | 0.047   | 0.171   | 0.527 |
| StreamVGGT   | No         | 0.869    | 1.014    | 0.063   | 0.185   | 0.648 |
| InfiniteVGGT | No         | 0.496    | 0.920    | 0.053   | 0.177   | 0.446 |
| **Ours**     | No         | 0.176    | 0.409    | 0.037   | 0.015   | 0.186 |

### KITTI — ATE [m] ↓

원논문 Table III. Ours has the best average (87.0), just ahead of FastVGGT (87.9) and far ahead of the post-processing baselines.

| Method       | Post-Proc. | 00    | 01    | 05    | 08     | 10    | Avg   |
| ------------ | ---------- | ----- | ----- | ----- | ------ | ----- | ----- |
| VGGT-Long    | Required   | 181.9 | 232.2 | 147.2 | 247.7  | 71.2  | 135.2 |
| VGGT-SLAM    | Required   | 190.8 | 793.3 | 167.7 | 271.51 | 221.2 | 234.5 |
| FastVGGT     | No         | 102.5 | 176.8 | 76.1  | 99.3   | 36.7  | 87.9  |
| StreamVGGT   | No         | 193.6 | 716.8 | 160.0 | 264.8  | 210.9 | 233.3 |
| InfiniteVGGT | No         | 181.0 | 607.9 | 157.0 | 261.6  | 157.3 | 207.9 |
| **Ours**     | No         | 138.1 | 179.1 | 131.6 | 86.5   | 26.8  | 87.0  |

### Keyframe strategy comparison — Avg ATE [m] ↓

원논문 Table IV. VGGT-SW treats every frame as a keyframe; VGGT-LK uses Lucas–Kanade flow with a fixed threshold of 50. The learned policy is best on all three datasets.

| Method   | KITTI | TUM-RGBD | EuRoC |
| -------- | ----- | -------- | ----- |
| VGGT-SW  | 88.3  | 0.233    | 2.64  |
| VGGT-LK  | 109.9 | 0.194    | 2.54  |
| **Ours** | 87.0  | 0.186    | 2.44  |

### Runtime and ablation

- 원논문 Table V (EuRoC, ms): Ours total 380.2 (Aggregator 370.0, DPT 1.1, Keyframe Decision 0.74) — the RL keyframe decision adds negligible overhead.
- 원논문 Table VI (EuRoC avg ATE): Full Method 2.443 vs VGGT-SW 2.648; removing any observation component degrades results — w/o o_pose 2.661, w/o o_cls token 2.647, w/o α_keyframe 2.648.

## 💡 Insights & Impact

- Central finding: directly transferring conventional geometry-driven keyframe heuristics (VGGT-LK) does not align with a foundation model's intrinsic properties; a data-driven policy conditioned on CLS tokens is more consistent across scenes.
- Suggests that for feed-forward VO, performance is not limited solely by lack of long-term memory — effective preservation of short-term temporal context via keyframes is equally critical.
- Post-processing baselines (VGGT-SLAM, VGGT-Long) do well indoors with strong geometry but degrade in large-scale outdoor scenes (KITTI), where this end-to-end approach stays stable; the authors flag loop closure / long-term memory as future work toward a fully feed-forward SLAM.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: backbone visual foundation model the keyframe policy wraps without modifying its architecture.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: pioneering feed-forward pose + dense geometry from uncalibrated pairs, cited as the lineage.
- **[CUT3R](../dynamic/cut3r.md)** / **[Fast3R](../reconstruction/fast3r.md)**: successors that refined the feed-forward paradigm, cited in related work.
- **[π³](../reconstruction/pi3.md)** / **[MapAnything](../reconstruction/mapanything.md)** / **[FlashVGGT](../foundation/flashvggt.md)**: recent foundation models and long-sequence variants cited; VGGT-Long, StreamVGGT, FastVGGT, InfiniteVGGT are the compared baselines.

## 📚 Key Takeaways

1. A PPO agent conditioned on mean-pooled DINOv2 CLS tokens plus relative poses selects keyframes for a VGGT-backbone sliding-window VO, adding only ~0.74 ms of decision overhead.
2. Trained solely on synthetic TartanAir, it generalizes across EuRoC, TUM-RGBD and KITTI, achieving the best average ATE among no-post-processing feed-forward methods on all three (2.44 / 0.186 / 87.0).
3. It beats hand-crafted keyframe strategies (VGGT-SW, VGGT-LK) everywhere and beats VGGT-SLAM broadly, but VGGT-Long — which uses required post-processing — still has a lower TUM-RGBD average (0.169 vs 0.186).

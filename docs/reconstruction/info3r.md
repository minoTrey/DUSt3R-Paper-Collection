# Info3R: Information-Adaptive Test-Time Training for 3D Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Sunghyun Baek, Hanna Bae, Minchan Kwon, Junmo Kim
- **Institution**: Korea Advanced Institute of Science and Technology (KAIST)
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.21938)
- **Verification**: UNKNOWN (2026-10-15; source 2609.21938v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Modulate recurrent 3D-state updates by new information, reset saturated states and reconnect their coordinate frames rather than updating every frame equally.

## 🎯 Key Contributions

1. **Information-Aware Update**: Give repeated frames and new observations different update strengths.
2. **Dynamic State Reset**: Recover capacity for new information using accumulated updates and confidence.
3. **Anchor-to-World Alignment**: Connect reset reference frames to the existing world.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Time-ordered RGB video and a trained streaming reconstruction model.
- **Output**: Per-frame cameras, depth, pointmaps and a connected scene. Update sequentially without future frames.
- **Problem**: Repeated observations can exhaust or saturate long-video state capacity. Unconditional resets disconnect new coordinates from the existing map.

### Method

1. Modulate test-time state updates using frame redundancy and information content.
2. Choose reset times from accumulated state changes and predicted confidence.
3. Align anchors across resets to connect old and new pointmaps in world coordinates.
4. Evaluate poses, depth and point clouds through the same recurrent path. State updates differ from network pretraining.

Source §III–IV uses CUT3R and follows TTT3R's long-sequence protocol, evaluated on one RTX 4090. Do not assume identical effects on other backbones.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.21938v1), Tables II–III, PDF p.5.

The pose table uses 1,000-frame TUM/ScanNet sequences. ATE measures trajectory error; RPE trans/rot measure relative translation/rotation. Values follow the source; unspecified distance units are not inferred.

| Dataset | Method | ATE ↓ | RPE trans ↓ | RPE rot ↓ |
| ------- | ------ | ----- | ----------- | --------- |
| TUM     | TTT3R  | 0.117 | 0.010       | 0.480     |
| TUM     | Info3R | 0.061 | 0.011       | 0.508     |
| ScanNet | TTT3R  | 0.394 | 0.039       | 1.162     |
| ScanNet | Info3R | 0.176 | 0.023       | 0.595     |

Better TUM ATE does not mean both RPE metrics improve. Table III's KITTI 50-frame AbsRel also worsens: TTT3R 0.105 versus Info3R 0.115. Long-sequence gains do not establish superiority at every length/metric.

## 💡 Insights & Impact

Storing more information differs from retaining capacity to learn new observations. State selection, resets and geometric alignment jointly address long-sequence collapse.

- Unstable reset triggers or anchor alignment affect global consistency.
- Relative poses, depth and global trajectories are distinct; better ATE alone does not guarantee reconstruction quality.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md): the recurrent geometric base model.
- [TTT3R](ttt3r.md): the direct test-time state-learning comparison.
- [Slot3R](slot3r.md): another streaming approach changing storage/readout structure.

## 📚 Key Takeaways

1. Give repeated and new frames different updates.
2. Reconnect coordinate frames after state resets.
3. Report length/metric-specific results and failure conditions.

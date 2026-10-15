# IGGT4D: Streaming 4D Instance-Grounded Geometry Transformer (arXiv 2026)

## 📋 Overview

- **Authors**: Zhengyu Zou, Hao Li, Kuixuan Jiao, Liu Liu, Tingyang Xiao, Xiaolin Zhou, Fangzhou Hong, Zhizhong Su, Dingwen Zhang, Ziwei Liu
- **Institution**: Horizon Robotics, Nanyang Technological University, Institute of Artificial Intelligence Hefei Comprehensive National Science Center
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.19228)
- **Verification**: UNKNOWN (2026-10-15; source 2607.19228v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Extend DA3 to causal streaming with joint depth/ray/instance features, preserving geometry and object identities in dynamic scenes.

## 🎯 Key Contributions

1. Build causal Transformers jointly predicting geometry and instances.
2. Connect framewise object IDs through streaming instance codebooks.
3. Construct InsScene4D training data with geometry, poses and temporally consistent masks.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Time-ordered RGB frames and optional camera poses.
- **Output**: Camera motion, depth/ray geometry and temporally linked instance masks/embeddings.
- **Problem**: Geometry-only streaming loses identities during motion, occlusion and reappearance.

### Method

1. Add causal masks to DA3 view attention.
2. Reuse past context through camera/cross-view KV caches.
3. Jointly decode depth, rays and instances with geometry-aware Tri-DPT attention.
4. Cluster within-frame masks, associate with global codebooks and update feature centers with area weights.

Train with geometry and temporally consistent instance supervision. Separate GT-pose-input experiments from predicted-pose-only settings.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2607.19228v1), Table 1, PDF p.7.

DA3 protocols, means over HiRoom/ETH3D/7Scenes/ScanNet++. F1 below uses predicted poses (w/o p.); higher is better.

| Method      | Processing | Pose AUC@30 ↑ | Reconstruction F1 ↑ |
| ----------- | ---------- | ------------- | ------------------- |
| LingBot-Map | Streaming  | 0.8647        | 0.5228              |
| IGGT4D      | Streaming  | 0.8924        | 0.6678              |
| DA3         | Offline    | 0.9352        | 0.7430              |

Streaming comparisons improve, but not every mean exceeds offline DA3. GT-pose conditions also supply poses to some models at inference.

## 💡 Insights & Impact

Jointly updating time-consistent instances and geometry goes beyond independent framewise segmentation.

- Codebook associations can fail on repeated objects or reappearance.
- Causal and offline full-attention methods use different future-information assumptions.

## 🔗 Related Work

- [IGGT](iggt.md): instance-grounded geometry background.
- [Depth Anything 3](../reconstruction/depth-anything-3.md): the base model.

## 📚 Key Takeaways

1. Output video geometry and object identity jointly.
2. Historical caches and codebooks serve different roles.
3. Separate predicted/GT poses and online/offline settings.

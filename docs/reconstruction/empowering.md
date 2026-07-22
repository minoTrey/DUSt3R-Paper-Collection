# Empowering: Metric-Scale Feed-Forward Reconstruction via Satellite Images (arXiv preprint (2026-06))

![empowering — architecture](https://arxiv.org/html/2606.08205v1/x1.png)

_By incorporating satellite patches retrieved from coarse GPS signals, our method resolves the scale ambiguity of foundation-model-based 3D estimation… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Xianghui Ze, Yongjian Luo, Mengjun Chao, Zhenbo Song, Jianfeng Lu, Yujiao Shi
- **Institution**: Nanjing University of Science and Technology; ShanghaiTech University
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.08205)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: Resolves the scale ambiguity of feed-forward 3D reconstruction by retrieving a satellite patch from a coarse GPS pose and fusing it with a π³ backbone through bidirectional cross-view attention, jointly predicting a global scale factor, a coordinate offset, and a geometric correction for metric geometry and absolute pose.

## 🎯 Key Contributions

1. **Satellite imagery as a metric reference**: Uses readily available satellite patches as an external metric cue, enabling metric geometry estimation from only a coarse camera pose.
2. **Unified metric geometry + absolute pose**: A single framework jointly estimates metric scene geometry and absolute camera pose in the satellite coordinate frame.
3. **Scene-to-satellite alignment objective**: A BEV triplet-style alignment loss enforces consistency between the reconstructed scene and the corresponding satellite image.
4. **Cross-dataset generalization**: Trains on one driving dataset and tests on another (KITTI, nuScenes, Oxford RobotCar) while preserving the generalization of scale-agnostic foundation models.

## 🔧 Technical Details

### Architecture

- **Backbone**: π³ [8] adopted as the representative feed-forward backbone; the pretrained model ϕ is frozen and cloned into a trainable satellite branch.
- **Bidirectional cross-view interaction**: Satellite features and ground-view features exchange information through two-direction cross-attention (satellite-as-query and ground-as-query).
- **Three prediction heads**: A scale head Dβ (global average pooling + linear) outputs scalar β; a coordinate head DC (MLP) regresses rotation/translation offset C = [Cʳ, Cᵗ]; a geometry-correction head predicts ΔXₙ.
- **Output relation**: T′ₙ = [Cʳ Tʳₙ, β Tᵗₙ + Cᵗ], X′ₙ = β(Xₙ + ΔXₙ).

### Training

- **Losses**: Scale supervision L_scale (normalized squared error to optimal scale β̂), absolute pose losses (rotation via arccos, translation via Huber), and a BEV triplet alignment loss L_triplet built on DINO features projected to bird's-eye view.
- **Staged schedule**: 100 epochs; first 80 epochs optimize scale and coordinate offset, remaining 20 epochs refine geometry correction. Number of ground-view images N sampled between 1 and 3.
- **Coarse GPS simulation**: ground-truth latitude/longitude perturbed within ±20 m and yaw within ±10°.
- **Hardware**: four NVIDIA L40 GPUs. Satellite images from Google Maps covering 250 m × 250 m each.

## 📊 Results

### Monocular Metric Depth on KITTI (trained on nuScenes, no KITTI training)

원논문 Table 1. 모든 비교 방법은 KITTI 미학습.

| Method   | AbsRel ↓   | SqRel ↓    | RMSE ↓     | RMSElog ↓  | δ1 ↑       | δ2 ↑       | δ3 ↑       |
| -------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| DepthPro | 0.1833     | 0.7400     | 3.6684     | 0.1872     | 0.7361     | 0.9813     | 0.9972     |
| MoGeV2   | 0.1822     | 0.6595     | 3.8175     | 0.2191     | 0.6142     | 0.9786     | 0.9970     |
| DA3      | 0.2263     | 1.0362     | 4.4589     | 0.2198     | 0.5512     | **0.9860** | 0.9964     |
| **Ours** | **0.1371** | **0.5361** | **3.4067** | **0.1558** | **0.8542** | **0.9881** | **0.9976** |

### Multi-view Metric Depth on KITTI (trained on nuScenes)

원논문 Table 2. Upper part: 모든 방법을 GT 스케일에 정렬. Lower part: metric-scale 예측을 GT와 직접 비교.

| Scale | Method   | AbsRel ↓   | SqRel ↓    | RMSE ↓     | RMSElog ↓  | δ1 ↑       |
| ----- | -------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| GT    | Fast3R   | 0.1024     | 0.5489     | 3.9426     | 0.1501     | 0.9053     |
| GT    | MASt3R   | 0.0834     | 0.6435     | 4.6779     | 0.3605     | 0.9445     |
| GT    | π³       | 0.0464     | 0.1488     | 2.1142     | 0.0748     | 0.9828     |
| GT    | VGGT     | 0.0703     | 0.2904     | 3.2424     | 0.1064     | 0.9618     |
| GT    | DA3      | 0.0473     | 0.2601     | 2.5869     | 0.0875     | 0.9754     |
| GT    | **Ours** | **0.0353** | **0.1219** | **2.0039** | **0.0634** | **0.9896** |
| Pred  | DA3      | 0.2448     | 1.1920     | 5.0979     | 0.3014     | 0.3588     |
| Pred  | **Ours** | **0.1226** | **0.3605** | **2.9460** | **0.1475** | **0.8590** |

### Cross-view Localization on KITTI

원논문 Table 4. Loc.는 미터, Orien.은 도.

| Method    | Same Loc. Mean ↓ | Same Orien. Mean ↓ | Cross Loc. Mean ↓ | Cross Orien. Mean ↓ |
| --------- | ---------------- | ------------------ | ----------------- | ------------------- |
| CCVPE     | 1.22             | 0.67               | 9.16              | 1.55                |
| DenseFlow | 1.48             | 0.49               | 7.97              | 2.17                |
| FG2       | 0.75             | 1.28               | 7.45              | 3.33                |
| **Ours**  | **0.73**         | **0.43**           | **5.75**          | **0.52**            |

### Ablation on nuScenes (point-cloud, cross-dataset)

원논문 Table 6. 모두 KITTI 학습 → nuScenes 평가.

| Variant        | Acc. Mean ↓ | Comp. Mean ↓ | N.C. Mean ↑ |
| -------------- | ----------- | ------------ | ----------- |
| w/o Sat.       | 1.8701      | 4.699        | 0.7162      |
| w/o Correction | 1.9894      | 1.9730       | 0.7639      |
| **Ours**       | **1.3632**  | **1.4166**   | **0.7846**  |

Multi-view point-cloud estimation on nuScenes (Table 3): with GT-scale alignment, Ours reaches Acc. mean 0.9922 vs π³ 1.0041 and VGGT 1.0736; under direct metric prediction, Ours reaches Comp. mean 1.4166 vs DA3 2.0295.

## 💡 Insights & Impact

- **Scale from external geometry, not priors**: Rather than baking metric scale into a model via large annotated datasets (which generalizes poorly), the method injects scale from an always-available geographic reference, improving cross-dataset transfer.
- **Coarse GPS is enough**: Only a ±20 m / ±10° GPS estimate is required to retrieve the satellite patch, from which the network infers absolute pose and metric geometry.
- **Ablation confirms both components**: Removing the satellite reference or the geometric correction both degrade cross-dataset accuracy substantially (Table 6).
- **Applications**: Autonomous driving, embodied AI, and AR that require metric understanding of outdoor scenes.

## 🔗 Related Work

- **[π³](pi3.md)**: Adopted as the frozen feed-forward backbone.
- **[VGGT](vggt.md)**: Compared as a scale-agnostic multi-view baseline.
- **[Fast3R](fast3r.md)** and **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: Feed-forward reconstruction lineage compared against.
- **[MoGe](moge.md)**: MoGeV2 compared as a monocular metric geometry baseline.

## 📚 Key Takeaways

1. Satellite imagery provides a practical, widely available metric anchor that resolves feed-forward scale ambiguity without dense metric annotations or precise calibration.
2. A frozen π³ branch plus a trainable satellite branch with bidirectional cross-attention predicts scale β, coordinate offset C, and geometry correction ΔXₙ for metric-scale reconstruction and absolute pose.
3. Trained on one driving dataset and tested on another, the method leads on most metric-depth, point-cloud, and localization metrics, with the strongest cross-area localization gains highlighting geographic generalization.

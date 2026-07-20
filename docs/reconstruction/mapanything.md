# MapAnything: Universal Feed-Forward Metric 3D Reconstruction (3DV 2026)

## 📋 Overview

- **Authors**: Nikhil Keetha, Norman Müller, Johannes Schönberger, Lorenzo Porzi, Yuchen Zhang, Tobias Fischer, Arno Knapitsch, Duncan Zauss, Ethan Weber, Nelson Antunes, Jonathon Luiten, Manuel Lopez-Antequera, Samuel Rota Bulò, Christian Richardt, Deva Ramanan, Sebastian Scherer, Peter Kontschieder
- **Institution**: Meta Reality Labs; Carnegie Mellon University
- **Venue**: 3DV 2026
- **Links**: [Paper](https://arxiv.org/abs/2509.13414) | [Code](https://github.com/facebookresearch/map-anything) | [Project Page](https://map-anything.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A single transformer that regresses metric 3D geometry and camera poses from any mix of images, intrinsics, poses, and depth maps, covering 12+ reconstruction tasks through a factored ray-depth-pose-plus-scale scene representation.

## 🎯 Key Contributions

1. **Universal input flexibility**: N images plus any subset of ray directions, quaternions, translations, or ray depths — 64 exhaustive input combinations supported by one model.
2. **Factored scene representation**: rays, depth-along-ray, pose, and a single global metric scale factor (RDP & Scale), instead of a monolithic pointmap.
3. **Decoupled scale prediction**: a dedicated learnable scale token decoded through an MLP, shown to be critical for metric feed-forward inference.
4. **Probability-based universal training**: geometric inputs supplied with per-factor selection probabilities so one model covers all configurations without task-specific tuning.
5. **Generic central camera model**: ray directions rather than a pinhole focal length, enabling calibration for non-centered principal points and generalization toward wide-angle models.
6. **Scaling to 100 views**: benchmarked from 2 to 100 input views under four input configurations.

## 🔧 Technical Details

### Factored Representation

MapAnything maps inputs to an N-view factored metric output:

```text
f(Î, [R̂, Q̂, T̂, D̂]) = { m, (R_i, D̃_i, P̃_i)_{i=1..N} }
```

where `m` is the global metric scaling factor, `R_i` are unit-length local ray directions, `D̃_i` are up-to-scale ray depths, and `P̃_i` is the pose of view `i` in the frame of view 1. Local pointmaps follow as `L̃_i = R_i · D̃_i`, world-frame pointmaps as `X̃_i = O_i · L̃_i + T̃_i`, and the final metric reconstruction as `X_i^metric = m · X̃_i`.

Because ray directions amount to calibration and depth-along-ray is per-view, both can be produced by a single dense head.

### Encoding

- **Images**: DINOv2 ViT-G, 24th-layer normalized patch features, `F_I ∈ R^{1536×H/14×W/14}`. Chosen over CroCov2, DUSt3R's encoder, RADIO, and random-init patchification for downstream performance, convergence speed, and generalization.
- **Dense geometry** (ray directions, normalized ray depths): shallow convolutional encoder with a single pixel-unshuffle of size 14, projected into the same latent dimension as DINOv2 features.
- **Global quantities** (rotations as unit quaternions, translation directions, depth and pose scales): 4-layer MLP with GeLU, projected to `R^1536`. Scales are log-transformed before encoding since they vary drastically with scene size.

Rotation and translation are encoded separately so IMU or GPS priors can be supplied individually, and depth and pose normalization are decoupled since they are not assumed to arrive together.

### Transformer and Heads

- 16-layer alternating-attention transformer, 24 heads, latent dimension 1536, MLP ratio 4, initialized from the last 16 layers of DINOv2 ViT-G
- Constant reference-view embedding added to view 1's patch tokens
- No RoPE — the authors find DINOv2's patch-level positional encoding suffices and RoPE introduces unnecessary bias
- A single learnable scale token appended to the N-view patch tokens
- One DPT head decodes ray directions, up-to-scale ray depths, ambiguity masks, and confidence maps
- An average-pooling convolutional pose head predicts quaternions and up-to-scale translations
- The scale token passes through a 2-layer ReLU MLP, exponentially scaled to yield `m`

### Training

Geometric inputs are provided with an overall probability of 0.9; ray directions, ray depth, and pose each have an input probability of 0.5. When depth is selected, dense and 90%-sparsified depth are equally likely. Per-view input probability is 0.95, so views can be heterogeneous.

AdamW, two-stage curriculum totaling 420K steps: 6 days on 64 H200-140GB GPUs (effective batch 768→1536, views 4→2), then 4 days on 64 H200-140GB GPUs at 10× lower peak LR (batch 128→1536, views 24→2).

## 📊 Results

### Two-View Dense Reconstruction

원논문 Table 2. ETH3D, ScanNet++ v2, TartanAirV2-WB 평균. rel은 절대 상대 오차, τ는 1.03% 임계 inlier 비율,
ATE는 정렬된 궤적 오차, AUC는 5° 임계, err°는 평균 각도 오차.

| Methods                | Scale rel ↓ | Points rel ↓ | Points τ ↑ | Pose ATE ↓ | Pose AUC ↑ | Depth rel ↓ | Depth τ ↑ | Rays err° ↓ |
| ---------------------- | ----------- | ------------ | ---------- | ---------- | ---------- | ----------- | --------- | ----------- |
| **a) Images**          |             |              |            |            |            |             |           |             |
| DUSt3R                 | —           | 0.21         | 43.9       | 0.08       | 35.5       | 0.17        | 32.6      | 2.55        |
| MASt3R                 | 0.38        | 0.25         | 30.2       | 0.07       | 37.3       | 0.19        | 24.8      | 7.03        |
| Pow3R                  | —           | 0.22         | 43.1       | 0.09       | 36.9       | 0.19        | 35.0      | 2.06        |
| VGGT                   | —           | 0.20         | 43.2       | 0.07       | 34.2       | 0.13        | 29.3      | 2.34        |
| MapAnything            | **0.13**    | **0.08**     | **57.5**   | **0.02**   | **56.0**   | **0.07**    | **49.3**  | **0.85**    |
| **b) + Intrinsics**    |             |              |            |            |            |             |           |             |
| Pow3R                  | —           | 0.20         | 46.0       | 0.08       | 51.3       | 0.15        | 43.2      | 0.40        |
| MapAnything            | **0.13**    | **0.07**     | **59.3**   | **0.01**   | **64.7**   | **0.06**    | **55.1**  | **0.19**    |
| **c) + Poses**         |             |              |            |            |            |             |           |             |
| Pow3R                  | —           | 0.13         | 50.9       | 0.05       | 67.5       | 0.11        | 47.2      | 0.38        |
| MapAnything            | **0.05**    | **0.06**     | **60.4**   | **0.01**   | **93.6**   | **0.06**    | **57.5**  | **0.18**    |
| **d) + Depth**         |             |              |            |            |            |             |           |             |
| Pow3R                  | —           | 0.13         | **77.9**   | 0.04       | 66.5       | 0.07        | **77.3**  | 0.29        |
| MapAnything            | **0.02**    | **0.04**     | 77.8       | **0.01**   | **73.1**   | **0.03**    | 76.6      | **0.18**    |
| **e) + Poses & Depth** |             |              |            |            |            |             |           |             |
| Pow3R                  | —           | 0.03         | **90.1**   | 0.01       | 81.3       | 0.02        | **89.0**  | 0.29        |
| MapAnything            | **0.01**    | **0.02**     | 82.0       | **0.00**   | **94.8**   | 0.02        | 81.5      | **0.16**    |

Pow3R holds the inlier-ratio columns in configurations (d) and (e) — MapAnything wins on error magnitude but not on τ once dense depth is supplied.

### Single-Image Calibration

원논문 Table 3. 평균 각도 오차 (err°, 낮을수록 좋다). MapAnything은 단일 이미지 입력으로 학습되지 않았다.

| Methods     | Avg.     | ETH3D    | SN++v2   | TAV2     |
| ----------- | -------- | -------- | -------- | -------- |
| VGGT        | 4.00     | 2.83     | 5.21     | 3.95     |
| MoGe-2      | 1.95     | 1.89     | 1.56     | 2.40     |
| AnyCalib    | 2.01     | **1.52** | 2.41     | 2.10     |
| MapAnything | **1.06** | 1.33     | **0.39** | **1.47** |

### Metric Depth on Robust-MVD

원논문 Table 4. rel은 절대 상대 오차, τ는 1.03% 임계 inlier 비율. K는 intrinsics 제공 여부.
괄호 안 회색 표기는 평가 데이터셋이 학습 분포에 포함된 경우다.

| Approach           | K   | Poses | KITTI rel ↓ | KITTI τ ↑ | ScanNet rel ↓ | ScanNet τ ↑ |
| ------------------ | --- | ----- | ----------- | --------- | ------------- | ----------- |
| **a) Single-View** |     |       |             |           |               |             |
| MoGe-2             | ✗   | ✗     | 14.21       | 6.8       | **10.57**     | **19.8**    |
| MapAnything        | ✗   | ✗     | **9.69**    | **17.9**  | 27.77         | 2.9         |
| Depth Pro          | ✓   | ✗     | 13.60       | 14.3      | 9.20          | 19.7        |
| UniDepthV2         | ✓   | ✗     | 13.70       | 4.8       | 3.20          | **61.3**    |
| Metric3DV2         | ✓   | ✗     | 8.70        | 13.2      | 6.20          | 19.3        |
| MapAnything        | ✓   | ✗     | **8.48**    | **27.7**  | 31.12         | 3.0         |
| **b) Multi-View**  |     |       |             |           |               |             |
| MASt3R             | ✗   | ✗     | 61.40       | 0.4       | 12.80         | 19.4        |
| MUSt3R             | ✗   | ✗     | 19.76       | 7.3       | **7.66**      | **35.7**    |
| MapAnything        | ✗   | ✗     | **5.45**    | **45.7**  | 22.23         | 10.6        |
| MVSA               | ✓   | ✓     | **3.20**    | **68.8**  | **3.70**      | **62.9**    |
| MapAnything        | ✓   | ✓     | 4.63        | 51.6      | 5.58          | 48.1        |

MapAnything loses clearly on ScanNet metric depth. The paper attributes this to lower benchmark dataset quality rather than model error, but the numbers are reported as-is. It also trails MVSA when both are given intrinsics and poses.

### Depth with Alignment

원논문 Table 4 (c)·(d). Median scale alignment 적용.

| Approach           | K   | KITTI rel ↓ | KITTI τ ↑ | ScanNet rel ↓ | ScanNet τ ↑ |
| ------------------ | --- | ----------- | --------- | ------------- | ----------- |
| **c) Single-View** |     |             |           |               |             |
| MoGe-2             | ✗   | **4.82**    | **47.9**  | 3.77          | 63.1        |
| VGGT               | ✗   | 7.50        | 33.0      | 3.33          | 70.8        |
| π³                 | ✗   | 6.00        | 40.1      | **2.90**      | **73.9**    |
| MapAnything        | ✗   | 6.12        | 42.2      | 4.95          | 55.6        |
| UniDepthV2         | ✓   | **4.00**    | **55.3**  | **2.10**      | **82.6**    |
| MapAnything        | ✓   | 6.15        | 41.6      | 4.77          | 57.1        |
| **d) Multi-View**  |     |             |           |               |             |
| MASt3R             | ✗   | 3.30        | 67.7      | 4.30          | 64.0        |
| MUSt3R             | ✗   | 4.47        | 56.7      | 3.22          | 69.2        |
| VGGT               | ✗   | 4.60        | 53.0      | 2.34          | 80.6        |
| π³                 | ✗   | **3.09**    | **69.5**  | **1.98**      | **83.6**    |
| MapAnything        | ✗   | 4.04        | 60.3      | 3.47          | 67.0        |

Under scale alignment MapAnything is mid-pack, behind π³ on both datasets in the multi-view setting — its advantage is metric-scale prediction, not aligned depth accuracy.

### Ablation: Scene Representation

원논문 Table 5a. 50뷰, ETH3D·ScanNet++ v2·TAv2 평균.

| Methods                              | Metric Scale rel ↓ | Pointmaps rel ↓ | Pointmaps τ ↑ |
| ------------------------------------ | ------------------ | --------------- | ------------- |
| **Input: Images Only**               |                    |                 |               |
| Local PM + Pose                      | **0.14**           | 0.32            | 33.2          |
| RDP                                  | 0.17               | 0.33            | 32.6          |
| LPMP & Scale                         | 0.16               | 0.30            | 38.7          |
| RDP & Scale (ours)                   | 0.16               | **0.28**        | **40.7**      |
| **Input: Images, Intrinsics, Poses** |                    |                 |               |
| Local PM + Pose                      | **0.04**           | 0.08            | 53.5          |
| RDP                                  | 0.06               | 0.09            | 46.7          |
| LPMP & Scale                         | 0.06               | **0.07**        | 55.9          |
| RDP & Scale (ours)                   | 0.05               | **0.07**        | **57.8**      |

Note the chosen representation is not best on metric scale rel — Local PM + Pose wins that column in both configurations. The decision favors pointmap accuracy and inlier ratio.

### Ablation: Expert vs Universal Training

원논문 Table 5b. 12개 이상 태스크를 한 번에 학습한 universal 모델과, 특정 입력 구성 전용으로 학습한 expert 모델 비교.

| Methods                              | Metric Scale rel ↓ | Pointmaps rel ↓ | Pointmaps τ ↑ |
| ------------------------------------ | ------------------ | --------------- | ------------- |
| **Input: Images Only**               |                    |                 |               |
| Expert Training                      | **0.16**           | 0.29            | 31.8          |
| Universal Training                   | **0.16**           | **0.28**        | **40.7**      |
| **Input: Images, Intrinsics, Poses** |                    |                 |               |
| Expert Training                      | **0.03**           | **0.07**        | 56.2          |
| Universal Training                   | 0.05               | **0.07**        | **57.8**      |
| **Input: Images & Metric Depth**     |                    |                 |               |
| Expert Training                      | **0.06**           | **0.24**        | 53.0          |
| Universal Training                   | **0.06**           | 0.25            | **54.0**      |

Universal training wins the inlier ratio everywhere but is slightly worse on metric scale with intrinsics and poses supplied.

## 💡 Insights & Impact

### Factoring Is What Makes Conditioning Possible

Prior work either takes only images or, like Pow3R, conditions on a narrow pinhole prior for two views. Factoring the scene into rays, depth, pose, and one global scale means each conditioning signal has a natural slot to enter and a natural slot to exit. That symmetry is why the same weights serve SfM, MVS, depth completion, and localization.

### Metric Scale Wants Its Own Token

Predicting scale jointly with geometry entangles it with everything else. The dedicated scale token, exponentially rescaled, is called out as critical to universal metric feed-forward inference — and the ablation shows the scale-free variants losing pointmap inlier ratio.

### Multi-Task Training Is Not a Tax

The expert-versus-universal ablation is the paper's most useful negative result for the field: training one model for 12+ tasks with compute equivalent to two bespoke models matches or beats three bespoke models. Task interference, the usual objection to universal models, does not materialize here.

### The Honest Limitations

The paper lists them itself: no explicit handling of noise or uncertainty in geometric inputs; no support for views without images (which novel view synthesis would need); untested test-time compute scaling; and multi-modal features fused before input rather than fed directly to the transformer. Scalability is also bounded by the one-to-one pixel-to-output mapping, and the scene parameterization captures no dynamic motion or scene flow.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: MapAnything follows DUSt3R's ground-truth validity convention but replaces the two-view pointmap with a factored N-view metric representation.
- **[MASt3R](../foundation/mast3r.md)**: A two-view baseline in the reconstruction and depth tables; MapAnything outperforms its bundle-adjusted variant on multi-view metric depth.
- **[VGGT](vggt.md)**: The alternating-attention transformer MapAnything borrows for its 16-layer trunk, and its main image-only baseline. The qualitative comparison targets VGGT specifically on large disparity changes, seasonal shifts, and water bodies.
- **[MUSt3R](must3r.md)**: The scalable multi-view baseline MapAnything beats on multi-view metric depth from images alone.
- **[Pi3](pi3.md)**: The strongest baseline under scale alignment — π³ leads MapAnything on both KITTI and ScanNet aligned depth.
- **[MoGe](moge.md)**: The monocular geometry line MoGe-2 extends; the single-view calibration and single-view depth comparisons run against it.

## 📚 Key Takeaways

1. **One model, 12+ tasks, 64 input combinations**: uncalibrated SfM, calibrated MVS, monocular depth, localization, and depth completion without task-specific tuning.
2. **A factored representation is the enabler**: rays + depth-along-ray + pose + one global scale gives every conditioning signal a place to live.
3. **Universal training beats bespoke training**: equivalent compute, better inlier ratios, no measurable task interference.
4. **Auxiliary inputs help monotonically**: performance improves as more modalities are supplied, from images only through poses and depth.
5. **It is not uniformly best**: Pow3R holds inlier ratios with dense depth, π³ leads on aligned depth, MVSA leads with known poses and intrinsics, and ScanNet metric depth is weak.

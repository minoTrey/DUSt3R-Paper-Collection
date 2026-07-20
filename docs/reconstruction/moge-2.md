# MoGe-2: Accurate Monocular Geometry with Metric Scale and Sharp Details (arXiv preprint)

## 📋 Overview

- **Authors**: Ruicheng Wang, Sicheng Xu, Yue Dong, Yu Deng, Jianfeng Xiang, Zelong Lv, Guangzhong Sun, Xin Tong, Jiaolong Yang
- **Institution**: USTC, Microsoft Research, Tsinghua University
- **Venue**: arXiv preprint (2025-07)
- **Links**: [Paper](https://arxiv.org/abs/2507.02546) | [Project Page](https://wangrc.site/MoGe2Page/)
- **Verification**: PREPRINT (2026-07-20)
- **TL;DR**: Extends MoGe to metric-scale monocular geometry by decoupling an affine-invariant point map from a separately predicted global scale, and sharpens fine detail via a real-data filtering-and-completion pipeline that uses synthetic labels.

## 🎯 Key Contributions

1. **Decoupled metric representation**: A metric monocular geometry estimation (MGE) framework that keeps MoGe's affine-invariant point map branch and adds a separate global-scale branch, avoiding the focal-distance ambiguity of direct absolute point map regression.
2. **CLS-token scale head**: Metric scale is predicted by an MLP conditioned on the DINOv2 encoder's classification token, so scale learning draws on global image context and does not perturb relative geometry.
3. **Real data refinement**: A unified filter-and-complete pipeline that removes RGB-depth mismatch artifacts in real data using locally aligned synthetic-model predictions, then inpaints the removed regions with logarithmic-space Poisson completion.
4. **Simultaneous strengths**: Accurate relative geometry, precise metric scale, and sharp boundaries at once — the paper's stated point of departure from prior MGE models, which trade one for another.

## 🔧 Technical Details

### Core Innovation: Scale and Relative Geometry Decomposition

```text
Naive metric MGE: image → absolute metric point map (focal-distance ambiguity)
MoGe-2:           image → affine-invariant point map P̂  ×  global scale ŝ
```

The geometry branch is supervised exactly as in MoGe, with a robust L1 loss aligned by the ROE
(robust and optimal) solver. Scale receives its own loss in log space with the target detached:

```text
L_s = || log(ŝ) − stopgrad(log(s*)) ||²₂
```

where `s*` is the optimal scale computed online between the predicted affine-invariant point map and
the ground truth by the ROE solver. The final metric geometry is `ŝ · P̂`.

### Architecture

- **Backbone**: DINOv2 ViT-Large (ViT-Base for all ablation models)
- **Convolutional neck + heads**: mask head and affine-invariant point map head, following MoGe's design but with all normalization layers removed to reduce inference latency
- **Scale head**: MLP on the ViT CLS token, producing a single global scale factor
- **Outputs**: validity mask, affine-invariant point map, metric scale → metric-scale points and metric depth

### Design Choices Explored

The paper compares four ways of injecting metric scale (see the ablation table below):

- **Entangled (SI-log)**: direct metric point map with entangled scale and shift, SI-log loss
- **Entangled (shift-invariant)**: scale absorbed into the point map, shift resolved by ROE alignment — bypasses focal-distance ambiguity but scale learning is unstable because open-domain scene scales span a wide range
- **Decoupled (conv. head)**: scale from a convolution head sharing the conv neck — fails to decouple, since the neck still carries most of the information and a small head aggregates local rather than global features
- **Decoupled (CLS-MLP)**: the adopted configuration

### Real Data Refinement Pipeline

1. **Failure analysis**: LiDAR data suffers depth-color mismatch from sensor asynchrony; SfM data misses reflective surfaces, thin structures, and sharp boundaries.
2. **Mismatch filtering**: A MoGe model `G_syn` trained only on synthetic data predicts geometry for real images. For each sampled point, a local spherical region is aligned to the prediction by the ROE solver, and real points deviating beyond the region radius are marked as outliers and removed from the valid mask. Local alignment is essential — global alignment inherits `G_syn`'s absolute depth bias and produces incorrect filtering.
3. **Geometry completion**: Filtered-out regions are reconstructed by logarithmic-space Poisson completion, matching the gradient of `G_syn`'s predicted depth while keeping the surviving real depth as a boundary condition.

### Training Setup

- **Data**: 24 datasets — 16 synthetic, 3 LiDAR-scanned, 5 SfM-reconstructed. Dataset weighting, loss balancing, cropping, and augmentation follow MoGe.
- **Learning rates**: 1 × 10⁻⁵ for the ViT backbone, 1 × 10⁻⁴ for the neck and heads; halved every 25K steps
- **Schedule**: 120K iterations on 32 NVIDIA A100 GPUs for 120 hours (ablation models: 100K iterations)

## 📊 Results

Evaluation covers 10 datasets: NYUv2, KITTI, ETH3D, iBims-1, GSO, Sintel, DDAD, DIODE, Spring, HAMMER.

### Relative Geometry — Point Metrics

원논문 Table 1. 10개 평가 데이터셋 평균. `Rk.`는 8개 방법 간 평균 순위이며 표 전체 평균이다.
ZoeDepth, DA V1/V2, Metric3D V2는 카메라 초점거리를 예측하지 않아 point 설정에서 평가되지 않았다.
MoGe 행은 원논문에서 회색 셀로 표시되어 일부 테스트 데이터셋이 학습에 쓰였음을 뜻한다.

| Method            | Scale-inv. Rel_p ↓ | Scale-inv. δ1p ↑ | Affine-inv. Rel_p ↓ | Affine-inv. δ1p ↑ | Local Rel_p ↓ | Local δ1p ↑ | Avg. Rk. ↓ |
| ----------------- | ------------------ | ---------------- | ------------------- | ----------------- | ------------- | ----------- | ---------- |
| MASt3R            | 14.5               | 82.1             | 11.6                | 86.0              | 8.09          | 92.2        | 6.75       |
| UniDepth V1       | 13.6               | 85.0             | 10.9                | 88.1              | 9.21          | 91.0        | 5.01       |
| UniDepth V2       | 11.6               | 87.7             | 8.56                | 91.9              | 6.34          | 94.9        | 2.88       |
| Depth Pro         | 12.4               | 87.7             | 9.93                | 89.4              | 6.91          | 94.1        | 4.52       |
| MoGe              | **7.46**           | **94.1**         | **5.69**            | **95.2**          | 5.50          | 95.6        | 2.53       |
| **MoGe-2 (Ours)** | 10.8               | 88.5             | 7.98                | 91.7              | **5.33**      | **95.9**    | **2.05**   |

### Relative Geometry — Depth Metrics

원논문 Table 1의 depth 부분. 동일한 10개 데이터셋 평균.

| Method            | Scale-inv. Rel_d ↓ | Scale-inv. δ1d ↑ | Affine-inv. Rel_d ↓ | Affine-inv. δ1d ↑ | Disp. Rel_d ↓ | Disp. δ1d ↑ | Avg. Rk. ↓ |
| ----------------- | ------------------ | ---------------- | ------------------- | ----------------- | ------------- | ----------- | ---------- |
| ZoeDepth          | 12.7               | 83.9             | 10.1                | 88.5              | 11.1          | 88.3        | 8.87       |
| DA V1             | 11.7               | 85.8             | 8.76                | 90.4              | 8.63          | 92.2        | 6.92       |
| DA V2             | 10.7               | 87.6             | 8.48                | 90.8              | 8.82          | 91.6        | 6.12       |
| Metric3D V2       | 7.92               | 91.8             | 7.66                | 92.9              | 9.51          | 89.4        | 4.70       |
| MASt3R            | 11.2               | 86.5             | 9.38                | 89.1              | 11.6          | 87.8        | 6.75       |
| UniDepth V1       | 10.1               | 89.1             | 8.61                | 91.0              | 9.75          | 89.9        | 5.01       |
| UniDepth V2       | 8.61               | 90.8             | 6.42                | 93.9              | 7.35          | 93.0        | 2.88       |
| Depth Pro         | 9.81               | 89.1             | 7.65                | 92.0              | 8.42          | 91.7        | 4.52       |
| MoGe              | **5.77**           | **94.5**         | **4.51**            | **96.1**          | **5.58**      | **95.4**    | 2.53       |
| **MoGe-2 (Ours)** | 7.35               | 92.2             | 5.62                | 94.8              | 6.66          | 93.8        | **2.05**   |

MoGe-2 does not beat MoGe on relative geometry; the paper's claim is that it stays comparable to the
state-of-the-art relative method while adding metric scale, and it takes the best average rank overall.

### Metric Geometry

원논문 Table 2. metric scale 주석이 있는 7개 데이터셋 평균. 세 번째 블록은 GT 카메라 내부
파라미터를 입력으로 받는 방법들만 해당하며, 원논문 헤더 표기를 그대로 옮겼다.

| Method            | Point Rel_p ↓ | Point δ1p ↑ | Depth Rel_d ↓ | Depth δ1d ↑ | w/ GT Cam Rel_p ↓ | w/ GT Cam δ1p ↑ | Avg. Rk. ↓ |
| ----------------- | ------------- | ----------- | ------------- | ----------- | ----------------- | --------------- | ---------- |
| ZoeDepth          | -             | -           | 39.3          | 49.9        | -                 | -               | 5.90       |
| DA V1             | -             | -           | 31.8          | 54.8        | -                 | -               | 5.50       |
| DA V2             | -             | -           | 29.9          | 56.6        | -                 | -               | 4.43       |
| Metric3D V2       | -             | -           | -             | -           | 18.3              | 73.9            | 2.75       |
| MASt3R            | 26.2          | 55.3        | 49.7          | 30.3        | -                 | -               | 5.82       |
| UniDepth V1       | 12.1          | 87.2        | 23.2          | 67.5        | 21.4              | 68.6            | 2.84       |
| UniDepth V2       | 10.1          | 91.9        | 21.3          | 75.3        | 18.5              | 82.6            | 2.51       |
| Depth Pro         | 13.7          | 81.9        | 27.6          | 54.4        | -                 | -               | 3.83       |
| **MoGe-2 (Ours)** | **8.19**      | **93.6**    | **15.7**      | **76.8**    | **13.6**          | **87.4**        | **1.95**   |

### Boundary Sharpness

원논문 Table 3. Depth Pro가 제안한 boundary F1 점수(%), 높을수록 좋다.

| Method            | iBims-1  | HAMMER   | Sintel   | Spring   | Avg. Rk. ↓ |
| ----------------- | -------- | -------- | -------- | -------- | ---------- |
| ZoeDepth          | 2.47     | 0.17     | 2.30     | 0.43     | 7.75       |
| DA V1             | 3.68     | 0.76     | 5.64     | 1.09     | 6.75       |
| DA V2             | 13.9     | 4.74     | 32.5     | 6.10     | 3.75       |
| Metric3D V2       | 7.36     | 1.40     | 25.3     | 7.23     | 5.25       |
| MASt3R            | 1.24     | 0.05     | 1.72     | 0.15     | 9.50       |
| UniDepth V1       | 2.35     | 0.06     | 0.73     | 0.17     | 9.00       |
| UniDepth V2       | 11.2     | 4.40     | 39.7     | 7.08     | 3.75       |
| Depth Pro         | 14.3     | 5.36     | **41.6** | **11.0** | **1.50**   |
| MoGe              | 11.4     | 3.89     | 26.3     | 8.36     | 4.67       |
| **MoGe-2 (Ours)** | **17.9** | **5.42** | 35.2     | 8.63     | 1.75       |

### Ablation

원논문 Table 4. ViT-Base 인코더, 10개 데이터셋 평균. 위 블록은 metric scale 예측 설계,
아래 블록은 학습 데이터 구성이다. `Decoupled (CLS-MLP)`와 `w/ Improved real data`는 동일한
최종 설정이다.

| Configuration             | Metric Point Rel_p ↓ | Metric Point δ1p ↑ | Metric Depth Rel_d ↓ | Metric Depth δ1d ↑ | Local Rel_p ↓ | Local δ1p ↑ | F1 ↑     |
| ------------------------- | -------------------- | ------------------ | -------------------- | ------------------ | ------------- | ----------- | -------- |
| Entangled (SI-Log)        | 10.0                 | 90.7               | 17.9                 | 68.6               | 8.21          | 93.0        | 10.7     |
| Entangled (Shift inv.)    | 8.99                 | 92.1               | 16.9                 | 68.8               | 6.69          | 94.6        | 11.8     |
| Decoupled (Conv. head)    | 9.62                 | 91.4               | 17.7                 | 68.4               | 6.34          | 94.9        | 12.7     |
| **Decoupled (CLS-MLP)**   | 9.20                 | 91.9               | 16.5                 | 72.8               | 6.26          | 95.1        | 12.5     |
| Synthetic data only       | 12.4                 | 87.3               | 21.7                 | 65.0               | 6.42          | 94.9        | **13.3** |
| w/ Raw real data          | 9.01                 | 92.2               | **15.8**             | **75.7**           | 6.37          | 94.9        | 10.3     |
| **w/ Improved real data** | 9.20                 | 91.9               | 16.5                 | 72.8               | **6.26**      | **95.1**    | 12.5     |

The data ablation is the clearest statement of the paper's thesis: synthetic-only training gives the
highest sharpness (F1 13.3) but the worst metric accuracy (Rel_p 12.4), raw real data gives the best
metric depth but the worst sharpness (F1 10.3), and refined real data recovers most of the sharpness
while keeping metric accuracy close to the raw-real configuration.

## 💡 Insights & Impact

### Why Decoupling Works

Predicting an absolute metric point map directly is confounded by focal-distance ambiguity — a
distant object seen with a long focal length and a near object seen with a short one project
identically. Absorbing scale into the point map (the shift-invariant variant) removes the ambiguity
but leaves the network regressing values that span orders of magnitude across indoor scenes and
landscapes. Unstable scale learning then produces large gradients that leak into the shared
representation and degrade relative geometry. Isolating scale into a stop-gradient-supervised scalar
branch removes that coupling entirely, and conditioning it on the CLS token gives it the global
context that a local convolutional head cannot supply.

### Why Local Alignment Matters for Filtering

The refinement pipeline depends on trusting the synthetic-trained model's _local_ structure while
distrusting its _absolute_ depth. Aligning globally propagates the model's absolute bias into the
error map, over-filtering some regions and under-filtering others; aligning within small spherical
neighborhoods isolates genuine artifacts. This is what allows real data to be kept in training
rather than discarded, which is the choice that separates MoGe-2 from the synthetic-only strategy of
Depth Anything V2 and the synthetic second stage of Depth Pro.

### Applications

- **SLAM and autonomous driving**: metric scale directly from a single image
- **Embodied AI**: absolute distances for manipulation and navigation
- **Image editing and generation**: sharp boundary geometry for compositing
- **3D world modeling and content creation**: point maps with recovered intrinsics

### Limitations (stated by the authors)

- Extremely fine structures such as thin lines and hair remain difficult
- Straight and aligned structures degrade under large foreground/background scale differences
- Real-world metric scale ambiguity can cause deviations out of distribution

## 🔗 Related Work

### Building On

- **MoGe**: supplies the affine-invariant point map representation, the ROE alignment solver, the multi-scale local supervision, and the dataset weighting recipe. MoGe-2 keeps all of it and adds a scale branch.
- **DINOv2**: ViT backbone; its CLS token is what makes the decoupled scale head viable.
- **Depth Pro**: source of the boundary F1 sharpness metric used for evaluation, and the closest competitor on sharpness.

### Contrast with Detail-Oriented Depth Methods

- **Depth Anything V2**: trains on synthetic labels only for sharpness, accepting a synthetic-to-real gap. MoGe-2 keeps real data and repairs it instead.
- **Depth Pro**: multi-patch ViTs plus a synthetic training stage; sharp but weaker in geometric accuracy, which the metric geometry table reflects.
- **UniDepth V1/V2**: predicts camera embeddings to condition depth. MoGe-2 instead bypasses explicit camera conditioning and recovers intrinsics from the point map.

### Enables

- Metric-scale monocular priors for multi-view feed-forward reconstruction pipelines
- Downstream use as a foundation geometry model where both absolute scale and boundary fidelity are required

## 📚 Key Takeaways

MoGe-2 demonstrates that:

1. **Metric scale is best learned as a separate scalar**: decoupling it from the point map, with a stop-gradient target and global CLS-token conditioning, keeps relative geometry intact while adding absolute scale.
2. **Where the head sits matters more than that it exists**: the convolutional scale head and the MLP scale head differ only in feature source, yet only the CLS-conditioned MLP improves metric geometry.
3. **Real data should be repaired, not replaced**: filtering with locally aligned synthetic predictions plus Poisson completion recovers most of the sharpness of synthetic-only training without its accuracy cost.
4. **Sharpness and accuracy are a measurable trade-off**: the data ablation quantifies it in a single table, and the refined-real configuration sits close to the best of both.

By separating what is ambiguous (scale) from what is well-conditioned (relative shape), and by
treating noisy real supervision as something to be cleaned rather than abandoned, MoGe-2 reaches
accurate relative geometry, precise metric scale, and sharp detail in one model — a combination the
paper argues no prior monocular geometry method had achieved simultaneously.

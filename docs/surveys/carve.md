# CARVE: Unlocking the Power of Critical Factors for 3D Visual Geometry Estimation (CVPR 2026)

![carve — architecture](https://arxiv.org/html/2604.21713v1/x1.png)

_Network architecture of our proposed CARVE model (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Guangkai Xu, Hua Geng, Huanyi Zheng, Songyi Yin, Yanlong Sun, Hao Chen, Chunhua Shen
- **Institution**: State Key Lab of CAD & CG, Zhejiang University; Tsinghua University; Ant Group
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2604.21713) | [Code](https://github.com/aim-uofa/CARVE)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: An empirical study of which training factors actually drive feed-forward visual geometry performance — finding that two widely-copied loss terms hurt — plus CARVE, a resolution-enhanced model built from the surviving choices.

## 🎯 Key Contributions

1. **A rigorous ablation study** on a representative multi-frame method (VGGT), isolating the effect of training data, each loss term, alignment strategy, and input resolution, reported as four numbered Insights.
2. **A consistency loss** enforcing agreement between the estimated point cloud and the one unprojected from the estimated depth and camera parameters, integrating the 2D-to-3D projection constraint into training rather than applying it as post-processing.
3. **An efficient high-resolution architecture** that fuses high-resolution ViT features into a low-resolution main branch via frame-wise cross-attention with zero-initialised gates, avoiding the 4× TFLOPs and 16× attention cost of naïvely upsampling the input.
4. **CARVE**, the model that results from combining these, evaluated on point cloud reconstruction, video depth, monocular depth, and camera pose/intrinsics.

## 🔧 Technical Details

The methodology is an ablation study, not a novel architecture proposal in the usual sense; the model follows from the study.

### The motivating gap

Multi-frame feed-forward models produce better cross-frame consistency than per-frame monocular models, yet frequently _underperform_ them on single-frame accuracy. The study sets out to determine why, by ablating training objectives and data on VGGT while holding architecture fixed.

### Experimental protocol

The model is initialised from VGGT pretrained weights, the ViT feature extractor is frozen, and the remaining components are trained. Predicted point cloud, depth map, and camera translation are aligned to ground truth by a per-sequence scale factor before loss computation. Training uses a dynamic batch size up to 24 frames for 30K iterations; evaluation uses uniformly sampled keyframes, up to 200 frames per video. For data ablation only the training data varies; for loss ablation "Data3" is fixed; for resolution ablation "Data3" with "Our Loss" is fixed.

### The baseline losses under test

`L = L_cam + L_depth + L_point`, where each dense loss is `L_reg + L_sg + L_conf`:

- `L_reg(ξ̂, ξ, W) = E_{p∈M} W_p · (ξ̂_p − ξ_p)` — masked regression with a weight map.
- `L_sg(ξ̂, ξ, W) = E_{p∈M} W_p · (∇_p ξ̂_p − ∇_p ξ_p)` — spatial gradient loss.
- `L_conf(W) = E_{p∈M} |−α log W_p|` — supervising the learnable confidence map.

Additional terms tested: temporal gradient loss `L_tg`; per-frame scale-shift alignment `L_F`; per-region alignment `L_S` over sampled local 3D spherical regions `S_j = {p | ‖P_p − P_j‖ ≤ r_j}`. Alignment parameters are computed with ROE alignment.

### The proposed consistency loss

```text
L_consis(P̂, D̂, r̂, t̂, θ̂) = E_{p∈M} ‖P̂_unproj(p) − P̂(p)‖
P̂_unproj(p) = R̂(D̂(p) K̂⁻¹ p) + t̂,   R̂ = H(r̂)
f̂_x = W / (2 tan(θ̂_x/2)),   f̂_y = H / (2 tan(θ̂_y/2)),   ĉ_x = W/2, ĉ_y = H/2
```

The point cloud head and the depth + camera heads are made to agree with each other under perspective projection.

### Efficient high-resolution adaptation

Low- and high-resolution images are encoded separately by the (frozen) ViT. The low-resolution feature is the query, the high-resolution feature the key and value, in a frame-wise cross-attention block:

```text
f̂_img = f̂_img_low + β · CrossAttn(f̂_img_low, f̂_img_high)
```

`β` is a learnable gate initialised to zero — a ResNet-style residual so pretrained parameters are not degraded at the start of training. The fused feature has the same dimensionality as the low-resolution feature and drops in as a replacement. For the depth and point heads, features are simply upsampled before the last few convolution layers.

## 📊 Results

### The four insights

The study's headline findings, as stated in the paper:

- **Insight 1**: scaling up data diversity and quality unlocks further performance gains in SOTA visual geometry estimation.
- **Insight 2**: gradient-based loss functions and learnable confidence weight maps unexpectedly _degrade_ performance; a simple inverse-depth weight map is superior.
- **Insight 3**: per-sequence plus per-frame alignment supervision helps, while local region alignment unexpectedly hurts; enforcing point cloud / unprojection consistency helps.
- **Insight 4**: the efficient high-resolution architecture gives a better performance-efficiency balance than upsampling the input.

### Ablation study

원논문 Table 1. Rank is the average rank across all metrics; each block is ranked separately. Gray rows in the original (the last two here) train with up to 12 frames and evaluate with up to 100 due to GPU memory limits, so they are not comparable to the rows above.

| Method                        | 7-Sc C-L1↓ | 7-Sc ATE↓ | 7-Sc Rel↓ | Bonn C-L1↓ | Bonn ATE↓ | Bonn Rel↓ | Rank↓    |
| ----------------------------- | ---------- | --------- | --------- | ---------- | --------- | --------- | -------- |
| VGGT baseline                 | 0.049      | 0.073     | 0.069     | 0.057      | 0.075     | 0.054     | –        |
| Data1                         | 0.056      | 0.079     | 0.070     | 0.051      | 0.064     | 0.049     | 2.50     |
| Data2                         | 0.052      | 0.078     | 0.069     | 0.051      | 0.071     | 0.052     | 2.25     |
| (Our Data) Data3              | 0.049      | 0.065     | 0.065     | 0.048      | 0.055     | 0.046     | **1.00** |
| (VGGT Loss) L_reg+L_conf+L_sg | 0.049      | 0.065     | 0.065     | 0.048      | 0.055     | 0.046     | 2.08     |
| L_reg + L_conf                | 0.050      | 0.064     | 0.065     | 0.043      | 0.046     | 0.046     | 2.00     |
| L_reg (W_inv)                 | 0.043      | 0.066     | 0.062     | 0.044      | 0.050     | 0.046     | **1.33** |

원논문 Table 1, KITTI and TUM columns for the same rows.

| Method                        | KITTI C-L1↓ | KITTI ATE↓ | KITTI Rel↓ | TUM C-L1↓ | TUM ATE↓ | TUM Rel↓ |
| ----------------------------- | ----------- | ---------- | ---------- | --------- | -------- | -------- |
| VGGT baseline                 | 0.296       | 1.113      | 0.094      | 0.051     | 0.047    | 0.062    |
| Data1                         | 0.281       | 1.411      | 0.085      | 0.040     | 0.090    | 0.049    |
| Data2                         | 0.277       | 1.267      | 0.083      | 0.040     | 0.090    | 0.052    |
| (Our Data) Data3              | 0.263       | 0.937      | 0.082      | 0.038     | 0.050    | 0.042    |
| (VGGT Loss) L_reg+L_conf+L_sg | 0.263       | 0.937      | 0.082      | 0.038     | 0.050    | 0.042    |
| L_reg + L_conf                | 0.270       | 1.059      | 0.082      | 0.038     | 0.050    | 0.043    |
| L_reg (W_inv)                 | 0.254       | 0.866      | 0.079      | 0.036     | 0.039    | 0.039    |

원논문 Table 1, alignment and consistency block (ranked within its own block against a repeated `L_reg (W_inv)` reference row at Rank 2.42).

| Method                                    | 7-Sc C-L1↓ | Bonn C-L1↓ | KITTI C-L1↓ | KITTI ATE↓ | TUM C-L1↓ | Rank↓    |
| ----------------------------------------- | ---------- | ---------- | ----------- | ---------- | --------- | -------- |
| L_reg (W_inv)                             | 0.043      | 0.044      | 0.254       | 0.866      | 0.036     | 2.42     |
| L_reg (W_inv) + L_sg                      | 0.045      | 0.045      | 0.270       | 0.949      | 0.038     | 4.17     |
| L_reg (W_inv) + L_tg                      | 0.045      | 0.046      | 0.263       | 1.270      | 0.039     | 5.17     |
| L_reg (W_inv) + L_F                       | 0.042      | 0.044      | 0.245       | 1.042      | 0.037     | 2.33     |
| L_reg (W_inv) + L_F + L_S                 | 0.043      | 0.047      | 0.255       | 0.901      | 0.037     | 3.08     |
| (Our Loss) L_reg (W_inv) + L_F + L_consis | 0.043      | 0.042      | 0.249       | 0.919      | 0.037     | **1.92** |

Both gradient losses rank worst in this block: adding `L_sg` back to the inverse-depth-weighted baseline degrades it from Rank 2.42 to 4.17, and `L_tg` to 5.17.

### Point cloud estimation

원논문 Table 5. Chamfer L1 and F-score at 5/25/50 cm. Aligned by similarity transformation; both clouds voxel-downsampled at 2 cm.

| Method          | KITTI C-L1↓ | KITTI F@25↑ | 7-Sc C-L1↓ | 7-Sc F@5↑ | TUM C-L1↓ | TUM F@5↑  | Rank↓    |
| --------------- | ----------- | ----------- | ---------- | --------- | --------- | --------- | -------- |
| MoGe v2 + LoFTR | 0.726       | 0.562       | 0.161      | 0.242     | 0.221     | 0.199     | 4.67     |
| Spann3R         | 2.359       | 0.296       | 0.101      | 0.375     | 0.122     | 0.498     | 4.58     |
| Fast3R          | 4.974       | 0.357       | 0.655      | 0.045     | 0.936     | 0.028     | 5.75     |
| VGGT            | 0.296       | 0.688       | 0.049      | 0.660     | 0.051     | 0.712     | 2.75     |
| Pi3             | 0.273       | 0.749       | 0.049      | 0.662     | 0.032     | 0.834     | 1.67     |
| CARVE (Ours)    | **0.238**   | **0.767**   | **0.043**  | **0.720** | **0.029** | **0.861** | **1.42** |

원논문 Table 6. Here the picture is more mixed.

| Method          | HAMMER C-L1↓ | HAMMER F@5↑ | Bonn C-L1↓ | Bonn F@5↑ | ETH3D C-L1↓ | ETH3D F@5↑ | Rank↓    |
| --------------- | ------------ | ----------- | ---------- | --------- | ----------- | ---------- | -------- |
| MoGe v2 + LoFTR | 0.030        | 0.872       | 0.174      | 0.226     | 1.889       | 0.002      | 3.92     |
| Spann3R         | 0.041        | 0.727       | 0.114      | 0.354     | 2.479       | 0.067      | 3.75     |
| Fast3R          | 0.062        | 0.488       | 0.983      | 0.019     | 3.901       | 0.000      | 5.17     |
| VGGT            | 0.035        | 0.828       | 0.057      | 0.645     | **0.202**   | 0.410      | 3.00     |
| Pi3             | 0.013        | 0.997       | **0.031**  | **0.796** | **0.106**   | **0.433**  | **1.17** |
| CARVE (Ours)    | **0.012**    | **0.999**   | 0.043      | 0.720     | 0.236       | 0.423      | 1.92     |

Pi3 wins Bonn and ETH3D outright, and CARVE's ETH3D C-L1 (0.236) is worse than even VGGT's (0.202). CARVE takes the better average rank on Table 5 and Pi3 on Table 6.

### Video depth estimation

원논문 Table 7. Rel↓ and δ↑ across seven datasets; the paper's own summary is "on par with the strongest baseline overall, while outperforming prior methods on several datasets and metrics."

| Method          | KITTI Rel↓ | 7-Sc Rel↓ | TUM Rel↓  | HO3D Rel↓ | HAMMER Rel↓ | Bonn Rel↓ | ETH3D Rel↓ | Rank↓    |
| --------------- | ---------- | --------- | --------- | --------- | ----------- | --------- | ---------- | -------- |
| MoGe v2 + LoFTR | 0.453      | 0.217     | 0.225     | 0.278     | 0.036       | 0.171     | 0.242      | 3.79     |
| Fast3R          | 0.254      | 0.312     | 0.377     | 0.524     | 0.135       | 0.339     | 0.568      | 4.86     |
| VGGT            | 0.094      | 0.069     | 0.062     | 0.270     | 0.046       | 0.054     | 0.043      | 3.21     |
| Pi3             | **0.078**  | 0.064     | 0.043     | 0.248     | 0.033       | **0.026** | **0.023**  | 1.57     |
| CARVE (Ours)    | 0.082      | **0.062** | **0.040** | **0.220** | **0.020**   | 0.041     | **0.023**  | **1.50** |

### Camera pose and intrinsics

원논문 Table 8. FoV Rel is the absolute relative field-of-view error, resolution-independent. MoGe v2 is evaluated on FoV Rel only.

| Method       | KITTI FoV Rel↓ | KITTI ATE↓ | 7-Sc FoV Rel↓ | 7-Sc ATE↓ | TUM ATE↓  | HO3D FoV Rel↓ | Rank↓    |
| ------------ | -------------- | ---------- | ------------- | --------- | --------- | ------------- | -------- |
| MoGe v2      | 0.162          | –          | 0.192         | –         | –         | 0.067         | 4.50     |
| Fast3R       | 0.079          | 106.082    | 0.075         | 1.696     | 1.257     | 0.012         | 3.38     |
| VGGT         | 0.084          | 1.113      | 0.076         | 0.073     | 0.038     | 0.109         | 2.69     |
| Pi3          | 0.094          | **0.572**  | 0.036         | 0.058     | 0.034     | 0.082         | 2.31     |
| CARVE (Ours) | **0.078**      | 0.664      | **0.024**     | **0.052** | **0.032** | **0.039**     | **1.69** |

원논문 Table 9. CARVE and Pi3 tie on average rank here (1.92 each).

| Method       | HAMMER FoV Rel↓ | HAMMER ATE↓ | Bonn FoV Rel↓ | Bonn ATE↓ | ETH3D FoV Rel↓ | ETH3D ATE↓ | Rank↓    |
| ------------ | --------------- | ----------- | ------------- | --------- | -------------- | ---------- | -------- |
| MoGe v2      | 0.084           | –           | 0.136         | –         | 0.058          | –          | 4.67     |
| Fast3R       | 0.062           | 0.119       | 0.025         | 0.669     | 0.075          | 13.074     | 3.83     |
| VGGT         | 0.040           | **0.001**   | 0.040         | 0.075     | 0.020          | 1.804      | 2.25     |
| Pi3          | 0.082           | 0.003       | **0.022**     | **0.039** | 0.031          | **0.140**  | **1.92** |
| CARVE (Ours) | **0.035**       | **0.001**   | 0.028         | 0.044     | **0.018**      | 0.184      | **1.92** |

### Monocular depth estimation

원논문 Table 10. Notably, CARVE — a multi-frame model — takes the best average rank against the dedicated per-frame MoGe and MoGe v2, which is the gap the study set out to close.

| Method       | KITTI Rel↓ | 7-Sc Rel↓ | TUM Rel↓  | HO3D Rel↓ | HAMMER Rel↓ | ETH3D Rel↓ | Rank↓    |
| ------------ | ---------- | --------- | --------- | --------- | ----------- | ---------- | -------- |
| MoGe         | **0.094**  | 0.070     | 0.055     | 0.282     | 0.028       | 0.035      | 2.43     |
| MoGe v2      | 0.098      | 0.077     | 0.057     | 0.256     | **0.023**   | 0.036      | 2.79     |
| Fast3R       | 0.274      | 0.247     | 0.285     | 0.550     | 0.143       | 0.404      | 6.00     |
| VGGT         | 0.125      | 0.070     | 0.062     | 0.269     | 0.054       | 0.043      | 4.64     |
| Pi3          | 0.112      | 0.068     | 0.055     | 0.271     | 0.040       | 0.034      | 2.93     |
| CARVE (Ours) | 0.106      | **0.066** | **0.049** | **0.236** | 0.028       | **0.033**  | **1.86** |

### Efficiency

원논문 Table 3. Single NVIDIA H200, sequence length 32, averaged over 100 runs after warm-up.

| Method       | Params. (M) | Image Resolution | FPS       |
| ------------ | ----------- | ---------------- | --------- |
| VGGT         | 1189.01     | 518 × 518        | 24.85     |
| VGGT         | 1189.01     | 1036 × 1036      | 2.54      |
| CARVE (Ours) | 1214.21     | 1036 × 1036      | **15.26** |

원논문 Table 4. TFLOPs and peak GPU memory (GiB) on a single H200.

| # Frames | VGGT 518² TFLOPs | VGGT 1036² TFLOPs | CARVE 1036² TFLOPs | VGGT 1036² Mem | CARVE 1036² Mem |
| -------- | ---------------- | ----------------- | ------------------ | -------------- | --------------- |
| 8        | 25.57            | 101.99            | 52.97              | 21.80          | 9.08            |
| 16       | 51.14            | 203.98            | 105.93             | 30.49          | 11.40           |
| 32       | 102.28           | 407.97            | 211.87             | 47.89          | 16.05           |
| 64       | 204.56           | 815.93            | 423.73             | 88.81          | 25.71           |
| 128      | 409.13           | OOM               | 847.47             | OOM            | 46.86           |
| 256      | 818.25           | OOM               | 1694.94            | OOM            | 89.14           |

The paper states its architecture requires **0.3× to 0.4× GPU memory, 0.5× TFLOPs, and delivers up to 6× higher FPS** than VGGT at the same 1036×1036 resolution. It also reports that naïve high-resolution input costs VGGT 4× TFLOPs, 3–4× GPU memory, and 0.1× FPS.

## 💡 Insights & Impact

### Two widely-copied loss terms are counterproductive

The most consequential finding is Insight 2, because both terms it indicts are standard. The spatial gradient loss `L_sg` is argued to focus excessively on local region variance at the cost of overall accuracy. The learnable confidence weighting `L_conf` admits a shortcut: rather than learning hard regions, the model can lower the total loss by shrinking the learnable weight on those regions — self-defeating for exactly the pixels that need supervision. Replacing both with a fixed weight map inversely proportional to ground-truth depth, which naturally emphasises nearby regions, is better on nearly every metric. The temporal gradient loss `L_tg` fares even worse, ranking last in its block.

### Alignment granularity has an optimum

Per-sequence supervision alone is worse than adding per-frame alignment `L_F`; but going one level finer to local 3D spherical regions `L_S` reverses the gain. The interpretation implied is that per-frame alignment corrects genuine per-frame scale ambiguity, while region-level alignment removes so much global structure from the supervision signal that the model stops learning coherent scene geometry.

### Resolution without quadratic cost

Doubling input resolution quadruples tokens and, in theory, multiplies attention cost sixteenfold. Fusing high-resolution features as a zero-gated residual into a low-resolution main branch sidesteps this and — notably — _outperforms_ simply feeding high-resolution input. The paper's two hypotheses: multi-resolution features are themselves beneficial, and high-resolution inputs conflict with pretrained weights learned at low resolution. The zero-initialised gate is the mechanism protecting those pretrained weights at the start of fine-tuning.

### The stated goal is achieved, but the model does not dominate

The gap the study targets — multi-frame models losing to per-frame models on single-frame accuracy — is closed: CARVE takes the best average rank on monocular depth against MoGe and MoGe v2. But Pi3 still wins Table 6 outright and ties on Table 9, and CARVE's ETH3D point cloud C-L1 is worse than VGGT's. The paper's own language is measured — "on par with the strongest baseline overall," "ties for the best average rank" — and the value here is more the ablation than the leaderboard position.

### Why this belongs with surveys rather than methods

CARVE the model exists mainly to demonstrate that the study's conclusions compose. The transferable content is the four Insights, which apply to anyone training a VGGT-family model regardless of whether they adopt CARVE's architecture.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the representative method ablated, the initialisation, and the efficiency comparison point.
- [pi3](../reconstruction/pi3.md) — the strongest baseline throughout; permutation-equivariant, reference-view-free.
- [MoGe](../reconstruction/moge.md) and [MoGe-2](../reconstruction/moge-2.md) — the per-frame models whose single-frame accuracy motivates the study, and the source of the inverse-depth weighting and ROE alignment ideas.
- [Fast3R](../reconstruction/fast3r.md) and [Spann3R](../reconstruction/spann3r.md) — multi-view baselines in the point cloud tables.
- [CUT3R](../dynamic/cut3r.md) — implicit multi-frame scene representation discussed in related work.
- [Depth Anything 3](../reconstruction/depth-anything-3.md) — cited as generalising visual geometry estimation with a unified depth-ray target.
- [DUSt3R](../foundation/dust3r.md) — the origin of the point-cloud-regression paradigm under study.

## 📚 Key Takeaways

1. **Question your loss terms.** Spatial gradient loss and learnable confidence weighting both _degrade_ performance; a fixed inverse-depth weight map beats them. Learnable confidence in particular gives the model a shortcut to down-weight exactly the regions it should be learning.
2. **Data scaling is not exhausted.** Even starting from VGGT pretrained weights, progressively adding diversity and then noisy data (Data1 → Data3) improves every rank.
3. **Alignment granularity has a sweet spot** at per-frame; going finer to local 3D regions hurts.
4. **Enforce projection consistency in training, not post-processing.** Making the point head agree with the unprojected depth + camera prediction improves robustness and accuracy.
5. **Fuse high-resolution features rather than feeding high-resolution input** — 0.3–0.4× memory, 0.5× TFLOPs, up to 6× FPS versus VGGT at the same resolution, and better accuracy than upsampling.
6. **The result is competitive, not dominant.** Pi3 still wins several benchmarks; the enduring contribution is the ablation.

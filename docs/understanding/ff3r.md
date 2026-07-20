# FF3R: Feedforward Feature 3D Reconstruction from Unconstrained views (CVPR 2026)

## 📋 Overview

- **Authors**: Chaoyi Zhou, Run Wang, Feng Luo, Mert D. Pesé, Zhiwen Fan, Yiqi Zhong, Siyu Huang
- **Institution**: Microsoft, Clemson University, Texas A&M University
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2604.09862) | [Project Page](https://chaoyizh.github.io/ff3r_project)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: An annotation-free feed-forward framework that predicts Feature-3DGS jointly with geometry from unposed images, scaling to 64 views via semantic-aware voxelization where prior feed-forward semantic methods run out of memory past 6.

## 🎯 Key Contributions

1. **Fully annotation-free**: Trained with rendering supervision on RGB and feature maps only — no camera poses, depth maps, or semantic labels.
2. **Token-wise Fusion Module**: Cross-attention with geometry tokens as queries over LSeg semantic tokens as keys/values, applied only at the last layer of the Alternating-Attention stack to preserve 3D awareness.
3. **Geometry-Guided Feature Warping (G→S)**: A bidirectional cosine-distance loss between a view's feature map and the feature map warped from a paired view via predicted depth and pose, injecting multi-view consistency into features that 2D foundation models lack.
4. **Semantic-aware Voxelization (S→G)**: Extends AnySplat's differentiable voxelization by weighting fusion with both geometric confidence and semantic distance to the voxel prototype, so a single high-confidence outlier cannot contaminate a voxel.
5. **Scale to unconstrained inputs**: Handles 2–64 views in one framework where LSM OOMs at 16.

## 🔧 Technical Details

### Pipeline

DINOv2 encodes each image into patch tokens; LSeg (CLIP-based) provides semantic tokens in parallel. Image, camera, and register tokens pass through an L-layer Alternating-Attention module following VGGT. The final-layer geometry tokens then cross-attend to semantic tokens:

```text
x'_v = Softmax( (x_v^(-1) W_Q)(s_v W_K)^T / sqrt(d_k) ) (s_v W_V)
```

A DPT-based decoder outputs depth, camera parameters, and Gaussian attributes. Each Gaussian carries an extra semantic embedding: `G_i = (μ_i, Σ_i, c_i, α_i, f_i)`. Depth is unprojected to give the Gaussian centers; skip connections from early encoder stages carry high-frequency appearance and semantic detail.

### Semantic-aware voxelization weights

Gaussian centers are quantized into voxels of size ε. For each voxel, a semantic prototype `f̄_s^sem` is the mean semantic feature, and each Gaussian's semantic distance is `d_g^sem = 1 − cos(f_g^sem, f̄_s^sem)`. The fusion weight combines confidence and semantic agreement:

```text
w_{g→s} = exp(C_g − λ d_g^sem) / Σ_h exp(C_h − λ d_h^sem)
```

### Learning objective

```text
L_total = L_rgb + λ1 L_feat + λ2 L_warp + λ3 L_d + λ4 L_p
```

with λ1 = 0.1, λ2 = 0.1, λ3 = 1.0, λ4 = 10.0 and λ_lpips = 0.05 inside `L_rgb`. Camera and depth pseudo-labels come from a pretrained VGGT via the AnySplat distillation strategy (Huber loss on pose encoding, squared error on depth over a top-N% confidence mask). Training uses DL3DV-10K with multi-view RGB supervision only.

## 📊 Results

### Sparse-view NVS + segmentation on ScanNet

원논문 Table 1.

| Method         | 2V PSNR ↑ | 2V mIoU ↑ | 2V Time(s) ↓ | 6V PSNR ↑ | 6V mIoU ↑ | 6V Time(s) ↓ | 16V PSNR ↑ | 16V mIoU ↑ | 16V Time(s) ↓ |
| -------------- | --------- | --------- | ------------ | --------- | --------- | ------------ | ---------- | ---------- | ------------- |
| LSeg (2D only) | –         | **0.543** | –            | –         | **0.551** | –            | –          | **0.540**  | –             |
| Feature-3DGS   | 17.54     | 0.332     | 18min        | 18.34     | 0.330     | 18min        | 19.12      | 0.349      | 18min         |
| LSM            | 14.95     | 0.424     | 0.408s       | 14.50     | 0.392     | 16.3s        | OOM        | OOM        | OOM           |
| Ours           | **22.70** | 0.486     | 0.884s       | **22.19** | 0.500     | 1.2s         | **22.58**  | 0.492      | 2.2s          |

FF3R dominates on rendering quality, but the purely 2D LSeg baseline still has the highest mIoU at every sparse setting — FF3R trades some raw 2D segmentation accuracy for 3D consistency. Accuracy follows a similar pattern (LSeg 0.810 / 0.804 / 0.800 vs FF3R 0.754 / 0.751 / 0.739 at 2/6/16 views).

### Dense-view NVS + segmentation on DL3DV-10K

원논문 Table 1.

| Method       | 32V PSNR ↑ | 32V mIoU ↑ | 32V Time(s) ↓ | 48V PSNR ↑ | 48V mIoU ↑ | 48V Time(s) ↓ | 64V PSNR ↑ | 64V mIoU ↑ | 64V Time(s) ↓ |
| ------------ | ---------- | ---------- | ------------- | ---------- | ---------- | ------------- | ---------- | ---------- | ------------- |
| Feature-3DGS | 17.42      | 0.196      | 30min         | 18.52      | 0.225      | 30min         | 18.48      | 0.230      | 30min         |
| AnySplat     | 18.02      | –          | 1.4s          | 19.18      | –          | 2.7s          | **19.58**  | –          | 4.1s          |
| Ours         | **18.56**  | **0.484**  | 3.1s          | **19.31**  | **0.514**  | 6.1s          | 19.31      | **0.521**  | 9.3s          |

At 64 views AnySplat edges out FF3R on PSNR (19.58 vs 19.31), but AnySplat produces no semantics. The paper's headline claim is that FF3R runs **180× faster than existing optimization-based methods** — the comparison is against Feature-3DGS's 30min per-scene optimization on dense-view DL3DV-10K.

### Depth consistency

원논문 Table 2. Inlier ratio τ at threshold 1.03.

| Method      | 2V Rel ↓ | 2V τ ↑    | 6V Rel ↓ | 6V τ ↑    |
| ----------- | -------- | --------- | -------- | --------- |
| LSM         | 7.36     | 46.24     | 8.38     | 38.65     |
| FF3R (Ours) | **3.99** | **67.99** | **3.36** | **71.10** |

LSM degrades from 2 to 6 views because its pairwise post-optimization accumulates error; FF3R improves, which the paper credits to semantic-aware voxelization.

### Ablation

원논문 Table 3.

| Method      | TW Fusion | G→S | S→G | PSNR ↑    | SSIM ↑    | LPIPS ↓   | mIoU ↑    | Acc. ↑    |
| ----------- | --------- | --- | --- | --------- | --------- | --------- | --------- | --------- |
| Base        |           |     |     | 17.85     | 0.699     | 0.380     | 0.411     | 0.684     |
| + TW Fusion | ✓         |     |     | 18.70     | **0.721** | 0.359     | 0.440     | 0.721     |
| + G→S       | ✓         | ✓   |     | 18.61     | 0.705     | 0.373     | **0.450** | 0.722     |
| + S→G       | ✓         | ✓   | ✓   | **19.12** | 0.718     | **0.357** | 0.449     | **0.725** |

Note that G→S alone slightly reduces PSNR/SSIM while lifting mIoU — the geometry gain only materializes once S→G's semantic-aware voxelization is added.

## 💡 Insights & Impact

### 2D semantic features are not multi-view consistent, and that is the bottleneck

The paper's PCA visualization of CLIP-LSeg features shows color shifts and boundary misalignment across views. Supervising a 3D field with such features causes overfitting to context views. Geometry-Guided Feature Warping is the direct fix: use the geometry the model already predicts to enforce cross-view feature agreement.

### Voxelization needs semantics, not just confidence

AnySplat's confidence-weighted voxel averaging can be dominated by a single high-confidence outlier that is semantically wrong for its neighborhood. Adding a semantic-distance term to the softmax weight is a small change with measurable effect on both appearance and mIoU.

### The mutual-boosting loop closes

Geometry improves semantics (warping loss uses predicted depth/pose); semantics improve geometry (voxel merging respects object boundaries). Table 2's depth result is the evidence for the second direction — depth consistency improves with more views rather than degrading.

### Honest ceiling

FF3R does not beat 2D LSeg on raw segmentation mIoU in the ScanNet sparse setting, and does not beat AnySplat on 64-view PSNR. Its argument is that it delivers both jointly, annotation-free, in seconds.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the geometry backbone architecture and the source of pseudo-label distillation
- [Large Spatial Model (LSM)](largespatialmodel.md) — the closest prior feed-forward semantic-geometry method; FF3R's main baseline
- [DUSt3R](../foundation/dust3r.md) — the pairwise post-optimization strategy used to extend LSM to multi-view
- [Depth Anything 3](../reconstruction/depth-anything-3.md) — contemporary geometry foundation model in the same family
- [Splatt3R](../gaussian-splatting/splatt3r.md) — pixel-aligned Gaussian prediction from unposed pairs

## 📚 Key Takeaways

1. **Annotation-free is achievable for joint geometry + semantics.** Rendering supervision on RGB and feature maps, plus VGGT pseudo-labels, removes the need for poses, depth, and semantic masks.
2. **Scale is the differentiator.** LSM OOMs at 16 views; FF3R runs 64 views in 9.3s (Table 1).
3. **The 180× figure applies to optimization-based baselines** (Feature-3DGS at 30min per scene on dense-view DL3DV-10K), not to feed-forward peers — AnySplat is comparable in speed.
4. **Bidirectional coupling matters.** Ablation shows G→S alone helps semantics but not appearance; only with S→G do both improve.
5. **Not uniformly best.** 2D LSeg still wins ScanNet sparse-view mIoU; AnySplat wins 64-view PSNR.

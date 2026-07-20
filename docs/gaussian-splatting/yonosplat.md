# YoNoSplat: You Only Need One Model for Feedforward 3D Gaussian Splatting (ICLR 2026)

## 📋 Overview

- **Authors**: Botao Ye, Boqi Chen, Haofei Xu, Daniel Barath, Marc Pollefeys
- **Institution**: ETH Zurich, ETH AI Center, Microsoft
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2511.07321) | [Code](https://github.com/cvg/yonosplat) | [Project Page](https://botaoye.github.io/yonosplat/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A single feed-forward 3DGS model that works with posed or unposed, calibrated or uncalibrated inputs and an arbitrary number of views, using a mix-forcing training curriculum to untangle joint pose and Gaussian learning.

## 🎯 Key Contributions

1. **One Model for All Settings**: The first feed-forward model to reach state-of-the-art performance in both pose-free and pose-dependent settings for an arbitrary number of views.
2. **Mix-Forcing Training**: A curriculum that starts with teacher-forcing (ground-truth poses for aggregation) and gradually mixes in the model's own predicted poses, avoiding both the instability of self-forcing and the exposure bias of pure teacher-forcing.
3. **Intrinsic Condition Embedding (ICE)**: Predicts focal length from an intrinsic token during the encoder stage, converts it to camera rays, and re-encodes it as conditioning — enabling uncalibrated inputs.
4. **Pairwise Camera-Distance Normalization**: Normalizing by the maximum pairwise camera distance resolves the data-level scale ambiguity of SfM poses and aligns with the relative pose supervision used in training.
5. **Efficiency**: Reconstructs a scene from 100 views at 280×518 in 2.69 seconds on an NVIDIA GH200 GPU.

## 🔧 Technical Details

### Core Innovation: Local Prediction plus a Training Curriculum

```text
Pose-dependent (pixelSplat, MVSplat): local Gaussians + GT poses → global
Pose-free (NoPoSplat, Flare):         Gaussians directly in a canonical space
YoNoSplat:                            local Gaussians + poses (predicted or given) → global
```

Canonical-space prediction aligns views naturally but degrades as view count increases. YoNoSplat
instead predicts per-view local Gaussians alongside per-view camera poses, then aggregates. This
scales, and retains full compatibility with pose-dependent workflows where accurate pre-existing
poses must be honoured (e.g. map reconstruction).

The cost of this choice is entanglement: pose errors corrupt the Gaussian learning signal and vice
versa. **Self-forcing** (aggregate with predicted poses from the start) is unstable. **Teacher-forcing**
(always ground truth) is stable but the model never sees its own imperfect predictions, so it
degrades at inference. **Mix-forcing** begins with pure teacher-forcing, then after step `t_start`
linearly increases the probability of using predicted poses, reaching a final mixing ratio `r` at
step `t_end`.

### Architecture

- **Encoder**: DINOv2 Large ViT, 24 attention layers. Image tokens are concatenated with a learnable camera intrinsic token.
- **Decoder**: 18 alternating-attention layers (per-frame self-attention for local refinement, global concatenated self-attention across views), following VGGT and π³. This scales better with many frames than the cross-attention used by NoPoSplat.
- **Gaussian heads**: two separate heads (centers; all other parameters), each M self-attention layers plus a linear layer. Backbone features are upsampled 2× before the heads, with a skip connection from the input image to counter ViT downsampling.
- **Pose head**: MLP → average pooling → MLP, predicting a 12D camera vector (translation plus a 9D rotation representation converted to R via SVD orthogonalization).
- **Intrinsic head**: performed at the _encoder_ stage, since intrinsics can be inferred per image while poses need cross-frame information. The intrinsic token aggregates image information and is passed through an MLP.

### Resolving Scale Ambiguity

Two sources: SfM training poses defined only up to scale, and the ill-posedness of jointly estimating
intrinsics and extrinsics. Three normalization strategies were evaluated — max pairwise distance,
mean pairwise distance, and max translation from origin — with max pairwise distance chosen.

ICE closes the second gap: predicted focal length → camera rays → linear layer → embedding features
added to the image features. When ground-truth intrinsics are available they are used directly.
**During training the network is conditioned on ground-truth intrinsics, not predicted ones**;
conditioning the decoder on encoder-predicted intrinsics led to training instability and failure.

### Training

- `L = L_image + λ_intrin L_intrin + λ_pose L_pose + λ_opacity L_opacity`.
- Rendering loss: MSE + LPIPS against 4 randomly sampled target views rendered with their ground-truth poses.
- Intrinsic loss: L2 on focal length.
- Pose loss: relative pose loss following π³ — `L_R(i,j) = arccos((tr(Rᵢ←ⱼᵀ R̂ᵢ←ⱼ) − 1)/2)` and Huber loss on relative translation, averaged over all ordered pairs, which makes the model invariant to input image order.
- Opacity regularization promotes sparsity; Gaussians with opacity < 0.005 are pruned, removing roughly 20%–70% depending on view count and overlap.
- Datasets: RealEstate10K (67,477 train / 7,289 test) and DL3DV (10,000 videos, 140 test).
- Input view count randomly sampled between 2 and 32; 4 target views. 224×224 model on 16 GH200 GPUs for 150k steps (batch 2 each); 280×518 model initialized from it and trained on 32 GH200 GPUs for another 150k steps (batch 1).

### Evaluation Protocol

In the pose-free setting the predicted camera space differs from SfM ground truth, so target camera
poses are first predicted by optimizing a photometric loss against the predicted Gaussians, then used
for rendering — following prior pose-free work. An optional fast post-optimization refines predicted
poses plus Gaussian centers and colors while freezing everything else.

## 📊 Results

### Novel View Synthesis on DL3DV

원논문 Table 1. `p`, `k`, `Opt` denote using ground-truth poses, ground-truth intrinsics, and
post-optimization respectively.

| Method     | p   | k   | Opt | 6v PSNR ↑  | 6v SSIM ↑ | 6v LPIPS ↓ | 12v PSNR ↑ | 12v SSIM ↑ | 12v LPIPS ↓ |
| ---------- | --- | --- | --- | ---------- | --------- | ---------- | ---------- | ---------- | ----------- |
| MVSplat    | ✓   | ✓   |     | 22.659     | 0.760     | 0.173      | 21.289     | 0.709      | 0.224       |
| DepthSplat | ✓   | ✓   |     | 23.418     | 0.797     | **0.136**  | 21.911     | 0.753      | 0.179       |
| Ours       | ✓   | ✓   |     | 24.717     | 0.817     | 0.139      | **23.285** | **0.773**  | **0.177**   |
| NoPoSplat  |     | ✓   |     | 22.766     | 0.743     | 0.179      | 19.380     | 0.563      | 0.318       |
| Ours       |     | ✓   |     | **24.887** | **0.819** | 0.138      | 23.149     | 0.758      | 0.183       |
| AnySplat   |     |     |     | 19.027     | 0.554     | 0.235      | 18.940     | 0.549      | 0.262       |
| Ours       |     |     |     | 24.531     | 0.804     | 0.142      | 22.933     | 0.746      | 0.187       |

Note DepthSplat retains the best 6-view LPIPS (0.136 vs 0.139).

24-view results and the post-optimization rows (원논문 Table 1):

| Method       | p   | k   | Opt | 24v PSNR ↑ | 24v SSIM ↑ | 24v LPIPS ↓ |
| ------------ | --- | --- | --- | ---------- | ---------- | ----------- |
| MVSplat      | ✓   | ✓   |     | 19.975     | 0.662      | 0.269       |
| DepthSplat   | ✓   | ✓   |     | 20.088     | 0.690      | 0.240       |
| Ours         | ✓   | ✓   |     | 22.664     | 0.758      | 0.192       |
| NoPoSplat    |     | ✓   |     | 17.860     | 0.495      | 0.397       |
| Ours         |     | ✓   |     | 22.354     | 0.731      | 0.205       |
| AnySplat     |     |     |     | 19.703     | 0.596      | 0.249       |
| Ours         |     |     |     | 22.174     | 0.720      | 0.209       |
| InstantSplat |     |     | ✓   | 18.493     | 0.510      | 0.381       |
| **Ours**     |     |     | ✓   | **25.855** | **0.814**  | **0.136**   |

Post-optimization rows across all view counts (원논문 Table 1): Ours reaches 27.533 / 0.866 / 0.106 at
6v and 26.126 / 0.820 / 0.133 at 12v, against InstantSplat's 21.677 / 0.627 / 0.273 and 20.792 /
0.580 / 0.316.

Two things the paper is explicit about: even in the hardest **pose-free, intrinsic-free** setting the
model outperforms the pose-dependent DepthSplat at every view count; and as view count and scene
scale grow (12v, 24v) supplying ground-truth extrinsics starts to help again, since pose estimation
gets harder at larger scale.

### Novel View Synthesis on RealEstate10K

원논문 Table 2, 6 input views.

| Method     | p   | k   | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ---------- | --- | --- | ---------- | --------- | --------- |
| DepthSplat | ✓   | ✓   | 24.156     | 0.846     | 0.145     |
| NoPoSplat  |     | ✓   | 22.175     | 0.750     | 0.207     |
| Ours       | ✓   | ✓   | 25.037     | 0.848     | 0.134     |
| **Ours**   |     | ✓   | **25.395** | **0.857** | **0.131** |
| Ours       |     |     | 24.571     | 0.823     | 0.144     |

Interesting inversion: on this sparse indoor benchmark the pose-**free** variant beats the
pose-dependent one. The paper attributes this to slightly imperfect SfM ground-truth poses — the
model's own coordinate system yields better renderings than being forced to align with noisy GT — and
to slight target-pose misalignment.

### Cross-Dataset Generalization to ScanNet++

원논문 Table 3. Trained on DL3DV, tested on ScanNet++ without fine-tuning. AnySplat _is_ trained on
ScanNet++.

| Method           | 32v PSNR ↑ | 32v SSIM ↑ | 32v LPIPS ↓ | 64v PSNR ↑ | 64v SSIM ↑ | 64v LPIPS ↓ | 128v PSNR ↑ | 128v SSIM ↑ | 128v LPIPS ↓ |
| ---------------- | ---------- | ---------- | ----------- | ---------- | ---------- | ----------- | ----------- | ----------- | ------------ |
| AnySplat         | 14.054     | 0.494      | 0.468       | 15.982     | 0.551      | 0.412       | 16.988      | 0.583       | 0.386        |
| Ours w/o GT k    | 16.886     | 0.600      | 0.432       | 17.368     | 0.608      | 0.413       | 17.641      | 0.617       | 0.405        |
| **Ours w/ GT k** | **17.935** | **0.659**  | **0.380**   | **18.833** | **0.688**  | **0.342**   | **19.284**  | **0.701**   | **0.325**    |

Performance improves monotonically with more input views, which is the paper's evidence that the
model genuinely fuses additional information rather than saturating.

### Camera Pose Estimation

원논문 Table 4. AUC of the cumulative angular pose error curve at 5°, 10°, 20°. DL3DV→RE10K rows use
a model trained exclusively on DL3DV, so no method in the RE10K column is trained on RE10K.

| Method                     | DL3DV 5° ↑ | DL3DV 10° ↑ | DL3DV 20° ↑ | RE10K 5° ↑ | RE10K 10° ↑ | RE10K 20° ↑ |
| -------------------------- | ---------- | ----------- | ----------- | ---------- | ----------- | ----------- |
| MASt3R 518×288             | 0.778      | 0.883       | 0.941       | 0.609      | 0.776       | 0.878       |
| NoPoSplat 256×256          | 0.538      | 0.735       | 0.853       | 0.443      | 0.627       | 0.755       |
| VGGT 518×280               | 0.700      | 0.848       | 0.924       | 0.566      | 0.753       | 0.867       |
| π³ 518×280                 | 0.795      | 0.897       | 0.949       | 0.705      | 0.841       | 0.916       |
| Ours 224×224               | 0.833      | 0.917       | 0.958       | 0.722      | 0.852       | 0.923       |
| Ours 224×224 (DL3DV→RE10K) | —          | —           | —           | 0.74       | 0.859       | 0.924       |
| **Ours 518×280**           | **0.844**  | **0.922**   | **0.961**   | **0.813**  | **0.904**   | **0.951**   |
| Ours 518×280 (DL3DV→RE10K) | —          | —           | —           | 0.78       | 0.884       | 0.939       |

Notably YoNoSplat at only 224×224 already beats π³ and VGGT at 518×280 — the paper's reading is that
training with a rendering loss also benefits pose estimation.

### Ablation: Forcing Strategy

원논문 Table 5. Trained with 6 input views for faster iteration, so numbers run slightly better than
the main tables.

| Method          | Pose-dep. PSNR ↑ | Pose-dep. SSIM ↑ | Pose-dep. LPIPS ↓ | Pose-free PSNR ↑ | Pose-free SSIM ↑ | Pose-free LPIPS ↓ |
| --------------- | ---------------- | ---------------- | ----------------- | ---------------- | ---------------- | ----------------- |
| Mix-forcing     | 25.212           | 0.848            | 0.133             | **25.587**       | **0.854**        | **0.130**         |
| Self-forcing    | 24.150           | 0.815            | 0.150             | 24.652           | 0.831            | 0.145             |
| Teacher-forcing | **25.228**       | **0.850**        | **0.131**         | 25.300           | 0.851            | 0.131             |

Honest reading: teacher-forcing is marginally better in the _pose-dependent_ column (25.228 vs
25.212 PSNR). Mix-forcing's value is that it wins the pose-free column while remaining competitive
there — a balance, not a strict dominance.

### Ablation: Scene Normalization

원논문 Table 6.

| Normalization       | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ------------------- | ---------- | --------- | --------- |
| max\_{i,j} d\_{ij}  | **25.212** | **0.848** | **0.133** |
| mean\_{i,j} d\_{ij} | 24.950     | 0.845     | 0.135     |
| max\_i d\_i         | 22.739     | 0.756     | 0.184     |
| No normalization    | 22.662     | 0.757     | 0.185     |

### Ablation: Output Space, ICE, and Plücker Rays

원논문 Tables 7, 8, 9. All on the 6-view setting.

| Ablation                     | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ---------------------------- | ---------- | --------- | --------- |
| Local Gaussian (Table 7)     | **25.587** | **0.854** | **0.130** |
| Canonical Gaussian (Table 7) | 24.104     | 0.819     | 0.172     |
| GT Intrinsic (Table 8)       | 25.587     | 0.854     | 0.130     |
| Pred Intrinsic (Table 8)     | 24.711     | 0.825     | 0.141     |
| No Intrinsic (Table 8)       | 24.481     | 0.813     | 0.149     |
| w/o Plücker (Table 9)        | 25.212     | 0.848     | 0.133     |
| w/ Plücker (Table 9)         | 25.202     | 0.851     | 0.129     |

Plücker ray embedding gives no significant benefit — the model establishes cross-view correspondence
from image features alone, which suits pose-free operation where such geometry is unavailable.

## 💡 Insights & Impact

### Exposure bias is the real obstacle to pose-free 3DGS

The paper's most transferable idea is borrowing an autoregressive-sequence-modelling framing.
Aggregating local Gaussians with predicted poses is structurally the same train/test mismatch as
teacher forcing in sequence models, and the same curriculum fix applies. Table 5 isolates it cleanly:
self-forcing is worst in both settings; teacher-forcing collapses only when evaluated pose-free.

### Local beats canonical once views are plentiful

Canonical-space prediction forces one network to align features from many views into an arbitrary
shared frame. The 1.5 dB PSNR gap in Table 7 at just 6 views, plus NoPoSplat's collapse from 22.766
to 17.860 PSNR going 6v → 24v in Table 1, shows how badly that scales.

### Intrinsics are a scale anchor, and can be predicted

ICE recovers most of the ground-truth-intrinsic benefit (24.711 vs 25.587 PSNR, against 24.481
without any intrinsic conditioning). The asymmetry — condition on GT intrinsics during training but
predicted ones at inference — is a concrete recipe; the alternative failed to train.

### Rendering supervision helps geometry

YoNoSplat's pose AUC beats π³, the point-cloud model it is initialized from, at both resolutions.
Photometric supervision through the Gaussian rasterizer appears to be a useful additional signal for
camera estimation, not just appearance.

## 🔗 Related Work

- [Splatt3R](splatt3r.md) — the DUSt3R/MASt3R-derived zero-shot feed-forward 3DGS model; YoNoSplat generalizes the same "no per-scene optimization" goal to arbitrary view counts and uncalibrated input.
- [PreF3R](pref3r.md) — feed-forward pose-free 3DGS from image sequences, the same problem setting with a different scaling strategy.
- [InstantSplat](instantsplat.md) — the optimization-based sparse-view pose-free baseline in Table 1, which YoNoSplat's optional post-optimization variant outperforms substantially.
- [π³](../reconstruction/pi3.md) — supplies the initialization for YoNoSplat's backbone, Gaussian center head, and pose head, and the pairwise relative pose loss formulation.
- [VGGT](../reconstruction/vggt.md) — the source of the local-global alternating attention used in the decoder, and a pose-estimation baseline.

## 📚 Key Takeaways

1. **One model really does cover four settings** — posed/unposed × calibrated/uncalibrated — at state of the art, including beating pose-dependent DepthSplat while using no poses or intrinsics at all.
2. **Mix-forcing is the enabling trick**: pure self-forcing destabilizes training and pure teacher-forcing creates exposure bias; the curriculum captures most of both.
3. **Scale ambiguity has two independent fixes** — max-pairwise-distance normalization for the data, ICE for the model. Removing normalization costs ~2.5 dB PSNR.
4. **Local per-view Gaussians scale, canonical-space Gaussians do not.**
5. **Fast**: 100 views at 280×518 in 2.69 seconds on a GH200, with 20%–70% of Gaussians pruned by opacity regularization.

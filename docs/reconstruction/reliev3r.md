# Reliev3R: Relieving Feed-forward 3D Reconstruction from Multi-View Geometric Annotations (CVPR 2026)

![reliev3r — architecture](https://arxiv.org/html/2604.00548v1/figures/Figure1-v7-ds4.jpg)

_In this paper, we propose Reliev3R, the first learning paradigm to train a Feed-forward Reconstruction Model (FFRM) from scratch without reliance on… (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Youyu Chen, Junjun Jiang, Yueru Luo, Kui Jiang, Xianming Liu, Xu Yan, Dave Zhenyu Chen
- **Institution**: Harbin Institute of Technology, Huawei, The Chinese University of Hong Kong, Shenzhen
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2604.00548)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: The first weakly-supervised paradigm for training feed-forward reconstruction models from scratch with no multi-view geometric annotations — supervision comes only from pseudo monocular relative depth and sparse image correspondences, combined through an ambiguity-aware depth loss and a trigonometry-based reprojection loss.

## 🎯 Key Contributions

1. **No SfM/MVS annotations**: eliminates both the geometric sensory data and the compute-exhaustive structure-from-motion preprocessing that fully-supervised FFRMs depend on.
2. **Ambiguity-aware scale-invariant depth loss** `L_d` that automatically down-weights unreliable regions such as sky or reflective surfaces where monocular predictions are multi-view inconsistent.
3. **Trigonometry-based reprojection loss** `L_rgst` that optimizes an angular residual in 3D space, producing meaningful gradients even when a corresponding point falls _behind_ the image plane of another view — the failure mode that breaks naive pixel-space reprojection when camera poses are learned from scratch.
4. **Empirical parity with early fully-supervised FFRMs**: matches or surpasses MVDUSt3R and FLARE while training on ~5% of the data used by SOTA models.
5. **Semi-supervised extension**: warm-up on synthetic fully-supervised data, then finetune on real data with Reliev3R's weak supervision.

## 🔧 Technical Details

### The reframing

Standard FFRM training is written as `A : I → (P, C)`, where the annotation pipeline `A` decomposes into matching and reconstruction:

```text
A = R ∘ M,     M : I → M,     R : M → (P, C)
```

The expensive part is `R` — going from correspondences to dense point maps and camera poses. Reliev3R asks whether correspondences alone can supervise the model, and answers by regularizing the dense prediction with monocular relative depth:

```text
F_R : I → (D, C),   F_R = S ∘ (M × D),   D : I → D
```

`D` is a pretrained monocular depth model; `S` is the multi-view-consistency supervision applied on top. Camera intrinsics are assumed known, which makes depth equivalent to point maps.

### Ambiguity-aware depth loss

```text
L_d = W_i · | Γ(D̂_i, sg(W_i)) − Γ(D_i, sg(W_i)) | − α log(W_i)
```

where `W_i` is a confidence map predicted by Reliev3R itself, `Γ` is the weighted median absolute deviation (WMAD) normalization, and `sg` is gradient detach. `W_i` is restricted to `(0, 2)`: values approaching 2 push the model to explore complicated regions, values approaching 0 mark multi-view-inconsistent depth to be ignored. WMAD shields the relative-depth normalization from low-confidence pixels.

Only the _scale-invariant shape_ of the monocular depth is used — global scale registration is left to the reprojection loss — because monocular metric predictions are inconsistent across views in both global scale and local detail.

### Trigonometry-based reprojection loss

Given correspondences `M_{i,j} = {(u_{i,k}, u_{j,k})}` and back-projected world points `p_{i,k} = C_i × π(u_{i,k}, d_{i,k})`, the naive objective `Σ ‖p_{i,k} − p_{j,k}‖²` collapses: far points have large coordinate magnitudes, dominate the error, and pull `p` toward the camera centre, distorting the point cloud. A pixel-space reprojection error also fails, giving wrong gradients when `p_{j,k}` falls behind view `i`'s image plane. The fix optimizes angles instead:

```text
L_rgst = Σ_{i,j,k} ⟨ p_{i,k} − t_i , p_{j,k} − t_i ⟩
```

with `t_i` the camera centre of view `i`. The direction of `p_{i,k} − t_i` depends only on view `i`'s rotation (intrinsics being fixed and known); the direction of `p_{j,k} − t_i` depends on the relative position, which supplies the gradient that rescales `D_j` for registration.

Total objective: `L = L_d + λ · L_rgst`, with `λ = 0.5`.

### Setup

- Architecture based on π³ with the point map head replaced by a depth head; 450 M parameters total.
- Pseudo-labels: Depth Pro for monocular relative depth (its metric output is used only for relative regularization), CoTracker for image correspondences. Neither is trained on DL3DV-10K, which the authors note strictly simulates scaling to data unseen by the pseudo-labelers.
- Training on DL3DV-10K only. 60 k steps on 64 Ascend 910B3 NPUs for 3 days, total batch size 64, 8 views per batch, learning rate 10⁻⁴ with cosine decay.

## 📊 Results

### DL3DV-benchmark, 8-view reconstruction

원논문 Table 1. `rel` is absolute relative error, `τ` is inlier ratio at a 10% relative threshold, `ATE` is average aligned trajectory error, `AUC` is at a 30° error threshold. π³† denotes π³ trained from scratch on DL3DV-10K alone. MVG = multi-view geometric annotations. The original marks the SOTA rows in gray because they train on ~20× the data.

| Method       | DL3DV-10K | MVG Ann. | Point Map rel ↓ | Point Map τ ↑ | Pose ATE ↓ | Pose AUC ↑ | Depth rel ↓ | Depth τ ↑ |
| ------------ | --------- | -------- | --------------- | ------------- | ---------- | ---------- | ----------- | --------- |
| Map-Anything | Yes       | w        | 0.051           | 0.911         | 0.004      | 87.088     | 0.045       | 0.896     |
| π³           | No        | w        | 0.056           | **0.927**     | **0.003**  | 92.746     | 0.054       | **0.916** |
| VGGT         | Yes       | w        | 0.061           | 0.905         | **0.003**  | **94.795** | 0.059       | 0.899     |
| CUT3R        | Yes       | w        | 0.073           | 0.815         | 0.005      | 89.432     | 0.072       | 0.801     |
| π³†          | Alone     | w        | 0.057           | 0.897         | 0.013      | 63.314     | 0.047       | 0.890     |
| MVDUSt3R     | No        | w        | 0.593           | 0.233         | 0.458      | 2.529      | 0.690       | 0.134     |
| FLARE        | Yes       | w        | 0.134           | 0.771         | 0.338      | 80.905     | 0.376       | 0.302     |
| AnyCam       | No        | w/o      | 0.262           | 0.490         | 0.023      | 29.527     | 0.181       | 0.400     |
| **Reliev3R** | Alone     | **w/o**  | 0.122           | 0.663         | 0.018      | 49.426     | 0.115       | 0.657     |

Reliev3R beats FLARE on point map rel (0.122 vs 0.134), pose ATE (0.018 vs 0.338), and both depth metrics, and beats MVDUSt3R on everything — while using no geometric annotations. It does _not_ close the gap to π³†, its directly-matched fully-supervised counterpart, on point map or pose. Against AnyCam, the only other annotation-free baseline, Reliev3R leads on every metric.

### Zero-shot on ScanNet++

원논문 Table 2. ScanNet++ has a different focal length and aspect ratio from DL3DV-10K and was unseen during training of both Reliev3R and π³†.

| Method       | Point Map rel ↓ | Point Map τ ↑ | Pose ATE ↓ | Pose AUC ↑ | Depth rel ↓ | Depth τ ↑ |
| ------------ | --------------- | ------------- | ---------- | ---------- | ----------- | --------- |
| π³           | **0.027**       | **0.972**     | **0.002**  | **86.941** | **0.027**   | **0.970** |
| π³†          | 0.232           | 0.678         | **0.028**  | 17.789     | 0.220       | 0.171     |
| AnyCam       | 0.438           | 0.448         | 0.084      | 15.376     | 0.286       | 0.095     |
| **Reliev3R** | 0.172           | 0.594         | 0.030      | 15.711     | 0.124       | 0.583     |

This is the paper's most interesting table. Both Reliev3R and π³† overfit to DL3DV-10K's focal length and drop sharply. But Reliev3R now _leads_ π³† on point map rel (0.172 vs 0.232) and dominates it on depth (rel 0.124 vs 0.220, τ 0.583 vs 0.171) — the authors read this as weak supervision being more robust under domain shift than full supervision on the same data. π³† retains a marginal edge on pose ATE (0.028 vs 0.030) and AUC (17.789 vs 15.711). Official π³, trained on ScanNet++ among other data, is far ahead of both.

### Semi-supervised warm-up and finetune

원논문 Table 3, evaluated on DL3DV-benchmark. "Synth Fully-Sup." is π³ trained from scratch fully-supervised for 20 k iterations on a down-sampled synthetic mixture (ASE, TartanAir, MVS-Synth, Blended-MVS, etc.) with batch size 128; "+Reliev3R" finetunes that checkpoint on DL3DV for 20 k steps with Reliev3R's weak supervision. Both use a FoV head — the former supervised with ground-truth intrinsics, the latter with pseudo FoV from MoGe2.

| Method           | Point Map rel ↓ | Point Map τ ↑ | Pose ATE ↓ | Pose AUC ↑ | Depth rel ↓ | Depth τ ↑ |
| ---------------- | --------------- | ------------- | ---------- | ---------- | ----------- | --------- |
| RayZer           | ×               | ×             | 0.786      | 0.362      | ×           | ×         |
| Synth Fully-Sup. | 0.277           | 0.475         | 0.042      | 17.075     | 0.208       | 0.357     |
| **+Reliev3R**    | **0.137**       | **0.667**     | **0.033**  | **34.240** | **0.106**   | **0.679** |

Weak supervision roughly halves the relative errors and doubles pose AUC, demonstrating a practical synthetic→real adaptation route where ground truth is unavailable.

### Confidence weight ablation

원논문 Table 4, DL3DV-benchmark.

| α           | Point Map rel ↓ | Point Map τ ↑ | ATE ↓     | AUC ↑      | Depth rel ↓ | Depth τ ↑ |
| ----------- | --------------- | ------------- | --------- | ---------- | ----------- | --------- |
| α = 0.2     | 0.143           | 0.607         | 0.022     | 42.116     | 0.137       | 0.606     |
| α = 0.5     | 0.137           | 0.626         | 0.023     | 46.703     | 0.129       | 0.628     |
| **α = 1.0** | **0.122**       | **0.663**     | **0.018** | **49.426** | **0.115**   | **0.657** |
| α = 2.0     | 0.127           | 0.651         | 0.020     | 48.566     | 0.121       | 0.647     |

## 💡 Insights & Impact

### Supervision, not architecture, is the scaling bottleneck

The paper's framing is that supervising an FFRM with SfM/MVS output amounts to "embedding the traditional reconstruction pipeline inside a transformer through ground-truth labels." If that pipeline is what caps training-set size, the way to scale is to remove it — not to build a better transformer. Reliev3R is the existence proof that this is possible at all.

### The reprojection loss is the non-obvious part

Two natural objectives both fail when poses are learned from scratch: 3D L2 distance is dominated by far points and distorts the cloud toward the camera centre, and pixel-space reprojection gives wrong gradients for points behind the image plane. The angular formulation is what makes optimization from random initial poses tractable, and it is also cited as the fix for the scale inconsistency that forced FLARE to introduce a learnable reprojector.

### Weak supervision may generalize better

The ScanNet++ result is the strongest argument in the paper: given identical training data, the weakly-supervised model transfers better than the fully-supervised one on point maps and depth. Pseudo-labels from a monocular prior carry less dataset-specific geometry bias than annotations produced by an SfM pipeline on that same dataset.

### Limitations stated by the authors

- **No large-scale data scaling analysis.** The entire motivation is scalability, and the paper does not empirically verify behaviour on substantially larger datasets.
- **Static scenes only.** Multi-view inconsistency caused by dynamics is not handled, which limits applicability to in-the-wild video — precisely the setting that would enable unlimited data.
- **Inherited pseudo-label weaknesses** from Depth Pro and CoTracker.
- Known camera intrinsics are assumed in the main formulation.

## 🔗 Related Work

- [π³](../reconstruction/pi3.md) — the architecture Reliev3R is built on (with the point map head swapped for a depth head) and the primary fully-supervised reference point, including the matched-data π³† baseline.
- [MapAnything](../reconstruction/mapanything.md) — fully-supervised SOTA baseline; its open-sourced annotation pipeline also produced the DL3DV-benchmark ground truth.
- [VGGT](../reconstruction/vggt.md) — fully-supervised baseline in Table 1.
- [CUT3R](../dynamic/cut3r.md) — fully-supervised baseline in Table 1.
- [DUSt3R](../foundation/dust3r.md) — the two-view foundation that MVDUSt3R and FLARE extend to multiple views.
- [MV-DUSt3R+](../reconstruction/mv-dust3r-plus.md) — related multi-view extension of DUSt3R.
- [MoGe-2](../reconstruction/moge-2.md) — used to generate pseudo depth and pseudo FoV labels in the semi-supervised experiment.

## 📚 Key Takeaways

1. **Feed-forward reconstruction can be trained from scratch without any multi-view geometric annotation** — the first demonstration of this, using only pseudo monocular relative depth and sparse correspondences.
2. **It beats FLARE and MVDUSt3R**, both fully supervised, on DL3DV-benchmark while training on 5% of SOTA data — but does not reach π³ trained on the same data (원논문 Table 1).
3. **Weak supervision transfers better under domain shift**: on zero-shot ScanNet++, Reliev3R's depth rel of 0.124 versus π³†'s 0.220 with identical training data (원논문 Table 2).
4. **Angular reprojection beats both 3D L2 and pixel-space reprojection** when poses start from random initialization — the key technical enabler.
5. **Practical as a finetuning recipe**: applying Reliev3R's weak supervision to a synthetic-only checkpoint doubles pose AUC on real data (원논문 Table 3).

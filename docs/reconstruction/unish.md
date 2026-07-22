# UniSH: Unifying Scene and Human Reconstruction in a Feed-Forward Pass (arXiv preprint 2026-01)

![unish — architecture](https://arxiv.org/html/2601.01222/x1.png)

_The network architecture of UniSH (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Mengfei Li, Peng Li, Zheng Zhang, Jiahao Lu, Chengfeng Zhao, Wei Xue, Qifeng Liu, Sida Peng, Wenxiao Zhang, Wenhan Luo, Yuan Liu, Yike Guo
- **Institution**: The Hong Kong University of Science and Technology; Beijing University of Posts and Telecommunications; Zhejiang University
- **Venue**: arXiv preprint (2026-01)
- **Links**: [Paper](https://arxiv.org/abs/2601.01222) | [Project Page](https://murphylmf.github.io/UniSH/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A unified feed-forward framework that jointly reconstructs metric-scale 3D scene geometry, human point clouds, camera parameters, and coherent SMPL bodies from a monocular video in a single pass, trained with a paradigm that leverages unlabeled in-the-wild data.

## 🎯 Key Contributions

1. **Unified feed-forward scene + human reconstruction**: A single forward pass recovers scene geometry, human point clouds, camera parameters, and metric-scale SMPL bodies, unlike prior work that treats scene reconstruction and Human Mesh Recovery (HMR) separately.
2. **Human surface refinement via distillation**: An expert depth model (MoGe-2) generates pseudo-labels for unlabeled data to refine high-frequency human surface detail where GT-only supervision fails.
3. **Coarse-to-fine (two-stage) supervision**: First learns coarse localization on synthetic data, then fine-tunes AlignNet on real data by directly optimizing the geometric correspondence between the SMPL mesh and the reconstructed human point cloud.
4. **Leveraging unlabeled real data**: The training paradigm bridges the sim-to-real domain gap that arises from reliance on synthetic datasets, improving generalization on in-the-wild videos.

## 🔧 Technical Details

### Architecture

UniSH has three parts: a scene reconstruction branch, a human body regression branch, and an AlignNet for human-scene alignment. The scene branch predicts a metric-scale point map and confidence maps and leverages the strong structural priors of π³ for robust camera pose. Human crops from the video are fed to the human body branch (built on CameraHMR-style regression) with intrinsics `K` to estimate a shared SMPL shape and per-frame SMPL translations.

### Human-scene alignment losses

- **One-way Chamfer alignment** (Eq. 4): from visible SMPL vertices to the target human point cloud (masked by SAM2), `Lalign,i`.
- **Depth-ordering regularization** (Eq. 5): `Ldreg,i = ReLU(d̄tgt,i − d̄src,i)`, enforcing that the reconstructed human point cloud (closer to camera) is not occluded by the SMPL mesh.
- **Stage-3 loss** (Eq. 6): combines the fine-grained alignment, depth-ordering, and a 2D keypoint reprojection loss (supervised with CameraHMR pseudo-annotations), fine-tuning AlignNet only on unlabeled real-world data.

## 📊 Results

### Human-centric video depth on Bonn

원논문 Table 1. Abs Rel lower is better; δ<1.25 higher is better.

| Method    | Abs Rel↓ | δ<1.25↑ |
| --------- | -------- | ------- |
| DUSt3R    | 0.151    | 0.839   |
| MASt3R    | 0.188    | 0.765   |
| MonST3R   | 0.072    | 0.957   |
| Fast3R    | 0.194    | 0.772   |
| MVDUSt3R  | 0.426    | 0.357   |
| CUT3R     | 0.078    | 0.937   |
| Aether    | 0.273    | 0.594   |
| FLARE     | 0.152    | 0.790   |
| VGGT      | 0.057    | 0.966   |
| π³        | 0.049    | 0.975   |
| **UniSH** | 0.035    | 0.980   |

### Global human motion on EMDB-2 and RICH

원논문 Table 2. 3D joint errors (mm) and RTE(%), all lower is better. Opt. Free(✓) = feed-forward; Scene(✓) = jointly reconstructs the 3D scene.

| Method    | Opt.Free | Scene | EMDB WA-MPJPE↓ | EMDB W-MPJPE↓ | EMDB RTE%↓ | RICH WA-MPJPE↓ | RICH W-MPJPE↓ | RICH RTE%↓ |
| --------- | -------- | ----- | -------------- | ------------- | ---------- | -------------- | ------------- | ---------- |
| SLAHMR    | ✗        | ✗     | 326.9          | 776.1         | 10.2       | 132.2          | 237.1         | 6.4        |
| TRAM      | ✗        | ✗     | 76.4           | 222.4         | 1.4        | 127.8          | 238.0         | 6.0        |
| JOSH      | ✗        | ✓     | 68.9           | 174.7         | 1.3        | 89.0           | 132.5         | 3.0        |
| WHAM      | ✓        | ✗     | 135.6          | 334.8         | 6.0        | 108.4          | 190.1         | 4.5        |
| GVHMR     | ✓        | ✗     | 111.0          | 276.5         | 2.0        | 78.8           | 126.3         | 2.4        |
| JOSH3R    | ✓        | ✓     | 220.0          | 661.7         | 13.1       | -              | -             | -          |
| **UniSH** | ✓        | ✓     | 118.5          | 270.1         | 5.8        | 118.1          | 183.2         | 4.8        |

UniSH is the only method that is simultaneously feed-forward and jointly reconstructs the scene; it substantially beats the other feed-forward joint-reconstruction baseline (JOSH3R) but trails HMR-specialized methods (e.g. GVHMR, and the optimization-based JOSH) on several motion metrics.

### Ablation: human surface refinement on Bonn

원논문 Table 3. "BEDLAM" = GT-only synthetic supervision; "Real" = real-world data with the proposed surface refinement loss.

| Training Data   | Abs Rel↓ | δ<1.25↑ |
| --------------- | -------- | ------- |
| No Refinement   | 0.049    | 0.975   |
| BEDLAM          | 0.062    | 0.960   |
| BEDLAM + Real   | 0.051    | 0.968   |
| **Real (Ours)** | 0.035    | 0.980   |

Naively fine-tuning on synthetic BEDLAM degrades performance (sim-to-real gap); even BEDLAM+Real underperforms the baseline, whereas real-data refinement is best.

## 💡 Insights & Impact

- **Priors over labels**: By reusing π³'s camera/geometry priors and distilling MoGe-2's depth detail, UniSH avoids the scarcity of joint scene+human+camera ground truth.
- **Honest trade-off**: The authors explicitly note that HMR-specialized methods achieve better numerical motion accuracy; UniSH's value is being feed-forward and jointly reconstructing the scene, which specialized HMR methods do not.
- **Limitations**: The non-parametric human geometry can still show artifacts such as floaters (원논문 Conclusion).

## 🔗 Related Work

- **[π³ (pi3)](pi3.md)**: Provides the scene-branch structural priors for robust camera pose that UniSH builds on.
- **[MoGe-2](moge-2.md)**: Expert depth model distilled for human surface refinement.
- **[VGGT](vggt.md)**, **[CUT3R](../dynamic/cut3r.md)**, **[Fast3R](fast3r.md)**: Reconstruction baselines on human-centric depth.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**, **[MonST3R](../dynamic/monst3r.md)**: Foundational and dynamic reconstruction baselines.

## 📚 Key Takeaways

1. UniSH unifies scene and human reconstruction into one feed-forward pass, jointly recovering scene geometry, human point clouds, cameras, and metric-scale SMPL bodies.
2. On human-centric depth (Bonn) it sets a new best (Abs Rel 0.035, δ 0.980), surpassing π³ and VGGT.
3. A coarse-to-fine training paradigm that exploits unlabeled real data is the key to bridging the sim-to-real gap and refining human surface fidelity.

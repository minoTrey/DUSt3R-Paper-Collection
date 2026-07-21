# VGGT-Edit: Feed-forward Native 3D Scene Editing with Residual Field Prediction (arXiv preprint 2026-05)

## 📋 Overview

- **Authors**: Kaixin Zhu, Yiwen Tang, Yifan Yang, Renrui Zhang, Bohan Zeng, Ziyu Guo, Ruichuan An, Zhou Liu, Qizhi Chen, Delin Qu, Jaehong Yoon, Wentao Zhang
- **Institution**: Peking University; Tencent; The Chinese University of Hong Kong; Shanghai AI Lab; NTU Singapore; Zhongguancun Academy; Beijing Key Lab of Data Intelligence & Security (PKU)
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.15186) | [Project Page](https://chriszkxxx.github.io/VGGT-Edit/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward framework for text-conditioned native 3D scene editing that injects depth-synchronized semantic guidance and predicts residual 3D geometric displacements, avoiding the blur and inconsistency of 2D-lifting editors.

## 🎯 Key Contributions

1. **VGGT-Edit framework**: A native feed-forward 3D scene editing method that operates directly in the geometric field, eliminating the multi-view inconsistency and high latency of traditional 2D-lifting approaches.
2. **Synchronized and weighted fusion**: A depth-synchronized feature injection strategy plus a view-aware weighting mechanism for stable, controllable, instruction-driven editing.
3. **DeltaScene dataset and pipeline**: A scalable data-generation pipeline with 3D agreement filtering that produces the DeltaScene dataset of approximately 100,000 high-quality training pairs.
4. **State-of-the-art quality + near-instant inference**: Best geometric accuracy and multi-view consistency with near-instantaneous editing.

## 🔧 Technical Details

### Depth-synchronized text injection

Given an instruction `I`, a text embedding `etext` is obtained from a pre-trained OpenCLIP. VGGT-Edit aligns this semantic guidance with the backbone's spatial poses via depth-synchronized injection, ensuring stable instruction grounding across the multi-view geometry rather than injecting text at a single layer.

### Residual transformation head

Instead of a standard reconstruction head, a residual transformation head directly predicts 3D geometric displacements that deform the scene while preserving background stability (the geometric prior backbone is frozen).

### View-aware weighting

Views with more complete observations contribute more strongly during fusion, so unreliable observations from occluded or boundary views introduce less geometric noise.

### Training

The model is supervised with a multi-term objective (geometric accuracy + cross-view consistency; loss weights λnormal = 0.1, λcam = 0.1, λ∆ = 0.01) using 95,000 pairs from the DeltaScene dataset.

## 📊 Results

### Editing quality on DeltaScene

원논문 Table 1. CLIP Score = semantic alignment (higher better); C-FID, C-KID = geometric consistency (lower better); Time(s) = end-to-end latency (lower better).

| Method        | CLIP Score↑ | C-FID↓ | C-KID↓ | Time(s)↓ |
| ------------- | ----------- | ------ | ------ | -------- |
| GaussCtrl     | 26.4        | 145.2  | 0.192  | ~300     |
| EditSplat     | 27.1        | 138.5  | 0.154  | ~600     |
| Omni-3DEdit   | 28.5        | 128.1  | 0.85   | ~115     |
| NoPoSplat     | 25.8        | 135.4  | 0.112  | ~20      |
| Edit3r        | 28.9        | 130.8  | 0.92   | ~10      |
| **VGGT-Edit** | 30.2        | 122.4  | 0.048  | ~5       |

VGGT-Edit reaches the best CLIP Score (30.2, a 1.3-point gain over the best competitor Edit3r at 28.9) and the lowest C-FID (122.4). The paper reports it is "nearly two orders of magnitude faster" than optimization-based methods such as EditSplat (~600 s vs ~5 s in the table; the text separately cites ~2 s per scene).

### Ablation of components

원논문 Table 2. Sync-Attn = depth-synchronized attention; View-W = view-aware weighting; Res-Head = residual transformation head.

| Configuration               | CLIP Score↑ | C-FID↓ | C-KID↓ |
| --------------------------- | ----------- | ------ | ------ |
| View-W + Res-Head (no Sync) | 28.1        | 126.5  | 0.062  |
| Sync + Res-Head (no View-W) | 27.8        | 127.2  | 0.068  |
| Sync + View-W (no Res-Head) | 29.5        | 131.4  | 0.085  |
| **Full (all three)**        | 30.2        | 122.4  | 0.048  |

Removing depth-synchronized injection drops CLIP Score from 30.2 to 28.1; removing view-aware weighting raises C-FID; replacing the residual head with a standard reconstruction head gives the weakest geometric consistency.

## 💡 Insights & Impact

- **Edit in 3D, not in 2D**: Predicting residual displacements in the geometric field preserves cross-view structure far better than independently editing 2D views and lifting them back.
- **Frozen prior + residuals**: Keeping the geometric backbone frozen and predicting only localized residuals preserves background stability while executing instruction-guided changes.
- **Practical latency**: Near-instant editing makes native 3D scene manipulation feasible for interactive spatial-computing and robotics applications.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The feed-forward geometry backbone whose geometric field VGGT-Edit edits.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**: Foundational feed-forward reconstruction models underlying the native-3D editing paradigm.

## 📚 Key Takeaways

1. VGGT-Edit performs text-conditioned 3D scene editing natively in the geometric field via depth-synchronized text injection and a residual displacement head.
2. On the new DeltaScene benchmark it leads all baselines in CLIP Score (30.2) and C-FID (122.4) while editing a scene in a few seconds.
3. Ablations confirm all three components (synchronized injection, view-aware weighting, residual head) are needed for accurate, stable, view-consistent edits.

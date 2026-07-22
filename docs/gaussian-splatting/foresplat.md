# ForeSplat: Optimization-Aware Foresight for Feed-Forward 3D Gaussian Splatting (arXiv preprint 2026-05)

![foresplat — architecture](https://arxiv.org/html/2605.22020v2/x1.png)

_Overview of ForeSplat (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Yuke Li, Weihang Liu, Cheng Zhang, Yuefeng Zhang, Jiadi Cui, Zixuan Wang, Junran Ding, Haoyu Wu, Yujiao Shi, Jingyi Yu, Xin Lou
- **Institution**: ShanghaiTech University; GGU Technology Co., Ltd; Stereye
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.22020)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: An optimization-aware _training_ framework that retrains a feed-forward 3DGS model's Gaussian head so its predictions are good _initializations_ for downstream per-scene refinement (not just low zero-step error). Its core, MetaGrad, is a lightweight multi-anchor first-order meta-gradient rule that avoids second-order differentiation through the 3DGS optimizer, adds no inference cost, and plugs into diverse backbones (AnySplat, Pi3X, a distilled Pi3X).

## 🎯 Key Contributions

1. **Optimization-aware training**: Identifies a training–deployment mismatch — feed-forward 3DGS is trained for zero-step rendering error, but predict-then-refine pipelines care about post-refinement quality — and reframes training as learning an initialization that a downstream optimizer can improve rapidly, without needing larger 3D datasets.
2. **MetaGrad (multi-anchor FOMAML)**: Bypasses the intractable second-order MAML gradient (the Gaussian state has 10⁷–10⁸ parameters) by unrolling a short refinement trajectory, sampling sparse anchor states (stride Δ=40), computing first-order photometric gradients on detached anchors, and averaging them as a surrogate signal to the prediction head — reducing inner-loop memory from O(K) to O(1).
3. **Plug-in across backbones**: Applied to AnySplat, Pi3X, and a distilled compact Pi3X with no architectural change or inference overhead, consistently improving post-refinement quality under a fixed budget.

## 🔧 Technical Details

### Problem formulation

Standard training minimizes `E[L_A(f_Θ(I))]` (zero-step error). ForeSplat instead minimizes the post-optimization loss `E[L_A(R_K(f_Θ(I)))]` where `R_K` applies K refinement steps — the MAML objective instantiated for feed-forward 3DGS. Post-optimization keeps the Gaussian count fixed (densification/cloning/splitting/pruning disabled), updating only attributes.

### MetaGrad

The full second-order meta-gradient requires Hessians `∇²_{G} L_A ∈ R^{|G|×|G|}` (intractable) and O(K) unroll memory. FOMAML approximates `∂G_{k+1}/∂G_k ≈ I`, so the surrogate gradient on the initialization is the photometric gradient at the anchor state. MetaGrad supervises _multiple_ horizons: each iteration samples `K_rand ∼ U{K_min,…,K_max}`, rolls out `K_rand` Adam refinement steps, and caches anchors at `k mod 40 = 0`. The MetaLoss is the equal-weight average of photometric losses at anchors; the outer objective is `L(Θ) = λ·L_A(G_0) + (1−λ)·L_meta`, where the L_meta term is applied via a detached surrogate estimator rather than end-to-end differentiation. Sparse Δ=40 anchoring avoids the noise/instability of dense (Reptile-style) supervision.

### Setup

- Trained on 9 datasets (DL3DV-10K, CO3Dv2, ARKitScenes, WildRGB-D, TartanAir, GTA-SfM, ScanNet++, MatrixCity, BlendedMVS). Only the Gaussian head is fine-tuned for 2,000 iterations, backbone frozen; inner trajectory length sampled from [50, 500].
- Backbones: AnySplat (native GS head, 448×448), Pi3X (with an appended DPT-style Gaussian head, 224×224), and Distill Pi3X (~45% of Pi3X's parameters).
- Evaluated on 50 scenes from CO3Dv2, DL3DV-10K, GTA-SfM, ScanNet++, TartanAir (strictly scene-disjoint from training), 16 images each (12 train / 4 test), AnySplat-style pose-aligned protocol.

## 📊 Results

원논문 Table 1 (training cost).

| Method            | Backbone     | Trainable part    | GPUs            | Wall-clock | GPU hours |
| ----------------- | ------------ | ----------------- | --------------- | ---------- | --------- |
| w/o MetaGrad      | AnySplat     | Backbone, GS head | 16× NVIDIA A800 | 48.00      | 768.00    |
| w/o MetaGrad      | Pi3X         | GS head           | 2× RTX 5090     | 23.11      | 46.22     |
| w/o MetaGrad      | Distill Pi3X | Backbone, GS head | 6× NVIDIA H20   | 124.31     | 745.86    |
| MetaGrad Finetune | AnySplat     | GS head           | 1× RTX 5090     | 6.86       | 6.86      |
| MetaGrad Finetune | Pi3X         | GS head           | 1× RTX 5090     | 6.11       | 6.11      |
| MetaGrad Finetune | Distill Pi3X | GS head           | 1× RTX 5090     | 4.41       | 4.41      |

원논문 Table 2 (post-optimization PSNR↑ over refinement steps).

| Method                  | 0     | 200   | 500   | 1k    | 2k    |
| ----------------------- | ----- | ----- | ----- | ----- | ----- |
| InstantSplat            | 18.77 | 23.55 | 25.20 | 25.63 | 25.91 |
| AnySplat Vanilla        | 21.66 | 26.17 | 26.88 | 27.02 | 27.03 |
| AnySplat + MetaGrad     | 20.70 | 26.36 | 27.32 | 27.60 | 27.68 |
| Pi3X Vanilla            | 21.29 | 23.88 | 24.48 | 24.86 | 24.97 |
| Pi3X + MetaGrad         | 18.84 | 23.92 | 24.92 | 25.44 | 25.81 |
| Distill Pi3X Vanilla    | 20.30 | 22.89 | 23.28 | 23.50 | 23.61 |
| Distill Pi3X + MetaGrad | 19.44 | 23.02 | 23.61 | 23.86 | 24.05 |

원논문 Table 2 (SSIM↑).

| Method                  | 0     | 200   | 500   | 1k    | 2k    |
| ----------------------- | ----- | ----- | ----- | ----- | ----- |
| InstantSplat            | 0.640 | 0.732 | 0.771 | 0.779 | 0.771 |
| AnySplat Vanilla        | 0.736 | 0.838 | 0.844 | 0.839 | 0.833 |
| AnySplat + MetaGrad     | 0.698 | 0.839 | 0.852 | 0.850 | 0.846 |
| Pi3X Vanilla            | 0.675 | 0.775 | 0.782 | 0.784 | 0.777 |
| Pi3X + MetaGrad         | 0.562 | 0.762 | 0.783 | 0.788 | 0.792 |
| Distill Pi3X Vanilla    | 0.597 | 0.717 | 0.725 | 0.729 | 0.727 |
| Distill Pi3X + MetaGrad | 0.580 | 0.721 | 0.737 | 0.741 | 0.743 |

원논문 Table 2 (LPIPS↓).

| Method                  | 0     | 200   | 500   | 1k    | 2k    |
| ----------------------- | ----- | ----- | ----- | ----- | ----- |
| InstantSplat            | 0.389 | 0.236 | 0.202 | 0.193 | 0.194 |
| AnySplat Vanilla        | 0.254 | 0.166 | 0.153 | 0.156 | 0.163 |
| AnySplat + MetaGrad     | 0.299 | 0.172 | 0.148 | 0.144 | 0.146 |
| Pi3X Vanilla            | 0.231 | 0.168 | 0.164 | 0.165 | 0.171 |
| Pi3X + MetaGrad         | 0.365 | 0.193 | 0.167 | 0.158 | 0.153 |
| Distill Pi3X Vanilla    | 0.287 | 0.175 | 0.173 | 0.175 | 0.180 |
| Distill Pi3X + MetaGrad | 0.326 | 0.181 | 0.170 | 0.168 | 0.168 |

The consistent pattern: MetaGrad _starts lower at step 0_ (e.g. AnySplat 20.70 vs 21.66 PSNR; Pi3X 18.84 vs 21.29) but converges faster and reaches a higher final quality (AnySplat 27.68 vs 27.03; Pi3X 25.81 vs 24.97, ~0.9 dB gain). This is by design — the head is trained for post-refinement quality, not step-zero rendering.

원논문 Table 3 (PSNR under wall-clock post-optimization budgets; inference times are shared by both variants).

| Method                  | inference | +1s   | +2s   | +5s   | +10s  | +20s  |
| ----------------------- | --------- | ----- | ----- | ----- | ----- | ----- |
| AnySplat Vanilla        | 21.66     | 24.85 | 25.56 | 26.56 | 26.97 | 27.02 |
| AnySplat + MetaGrad     | 20.70     | 24.98 | 25.81 | 26.92 | 27.43 | 27.61 |
| Pi3X Vanilla            | 21.29     | 23.48 | 23.88 | 24.47 | 24.87 | 24.97 |
| Pi3X + MetaGrad         | 18.84     | 23.28 | 23.92 | 24.92 | 25.55 | 25.81 |
| Distill Pi3X Vanilla    | 20.30     | 22.36 | 22.89 | 23.29 | 23.50 | 23.61 |
| Distill Pi3X + MetaGrad | 19.44     | 22.38 | 23.02 | 23.60 | 23.87 | 24.05 |

Inference times: AnySplat 0.72 s, Pi3X 0.30 s, Distill Pi3X 0.23 s. At a +1 s budget the two variants are comparable; MetaGrad overtakes from +2 s onward and the gap widens.

### Ablations

원논문 Table 4 (loss weight λ on Pi3X; λ=1.0 is vanilla supervised fine-tuning, λ=0.0 is pure-meta).

| Method   | 0     | 200   | 500   | 1k    | 2k    |
| -------- | ----- | ----- | ----- | ----- | ----- |
| baseline | 21.30 | 23.71 | 24.27 | 24.62 | 24.82 |
| λ = 1.00 | 21.29 | 23.88 | 24.48 | 24.86 | 24.97 |
| λ = 0.75 | 21.31 | 23.94 | 24.62 | 24.96 | 25.07 |
| λ = 0.50 | 21.23 | 24.02 | 24.71 | 25.07 | 25.28 |
| λ = 0.25 | 20.99 | 24.03 | 24.79 | 25.19 | 25.41 |
| λ = 0.00 | 18.84 | 23.92 | 24.92 | 25.44 | 25.81 |

Increasing the meta-gradient weight (lowering λ) deepens the early deficit but lifts the late plateau — a controllable trade-off, not binary.

원논문 Table 5 (anchor stride Δ on AnySplat; Reptile is the dense first-order baseline).

| Method   | 0     | 200   | 500   | 1k    | 2k    | GPU Hours |
| -------- | ----- | ----- | ----- | ----- | ----- | --------- |
| Baseline | 21.90 | 26.16 | 26.91 | 27.03 | 27.05 | -         |
| Vanilla  | 21.66 | 26.17 | 26.88 | 27.02 | 27.03 | 0.98      |
| Reptile  | 22.53 | 26.16 | 26.88 | 26.97 | 27.00 | 8.05      |
| Δ1       | 21.32 | 26.11 | 26.86 | 27.13 | 27.20 | 22.37     |
| Δ20      | 21.09 | 26.15 | 26.92 | 27.19 | 27.28 | 6.54      |
| Δ40      | 20.70 | 26.36 | 27.32 | 27.60 | 27.68 | 6.86      |
| Δ80      | 21.20 | 26.11 | 26.91 | 27.17 | 27.19 | 6.75      |

Δ=40 gives the best final PSNR (27.68) at moderate cost. Reptile achieves the strongest step-0 initialization (22.53) but the _worst_ final quality (27.00) — confirming that optimizing the post-refinement trajectory, not the immediate prediction, is what matters. Δ=1 (dense) is far costlier (22.37 GPU-hours) yet worse than Δ=40.

## 💡 Insights & Impact

- A prediction with low zero-step error is not necessarily a good optimizer starting point — it may sit where convergence is slow or gradients uninformative. Training for post-refinement loss produces "optimization-friendly" initializations.
- Multi-anchor sparse sampling stabilizes the meta-objective: consecutive Adam steps are highly correlated, so dense anchoring adds noise and cost without benefit; a single fixed horizon leaves intermediate states unconstrained and sensitive to the deployment K.
- By offloading part of the scene-modeling burden to the optimizer, ForeSplat makes a _distilled compact_ backbone viable, pointing toward on-device "capture-and-refine" 3D-reconstruction cameras.
- **Limitation (authors)**: limited to fixed-topology post-optimization (densification/cloning/splitting/pruning disabled); extending to structural 3DGS operations is future work.

## 🔗 Related Work

- Backbones and the feed-forward geometry line: [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [Fast3R](../reconstruction/fast3r.md), [VGGT](../reconstruction/vggt.md), and Pi3X (a variant of [Pi3](../reconstruction/pi3.md)); AnySplat is the primary host.
- Predict-then-refine peers: InstantSplat, [Splatt3R](splatt3r.md), MVSGaussian; other feed-forward Gaussian works [YoNoSplat](yonosplat.md), DepthSplat, EcoSplat.
- Meta-learning foundations: MAML, Reptile, and learned NeRF initializations (Tancik et al.).

## 📚 Key Takeaways

1. ForeSplat retrains only the Gaussian head with an optimization-aware objective, so the model outputs initializations tuned for rapid refinement rather than low step-0 error — with zero inference-time overhead.
2. MetaGrad makes MAML tractable for 10⁷–10⁸-parameter Gaussian states via sparse multi-anchor FOMAML (Δ=40), completing fine-tuning in a few single-GPU hours.
3. Across AnySplat, Pi3X, and a distilled Pi3X, MetaGrad trades a slightly lower step-0 quality for faster convergence and a higher final plateau (e.g. AnySplat 27.68 vs 27.03 PSNR at 2k steps), an honestly reported tradeoff that also enables compact edge-side reconstruction.

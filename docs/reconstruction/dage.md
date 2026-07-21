# DAGE: Dual-Stream Architecture for Efficient and Fine-Grained Geometry Estimation (CVPR 2026)

## 📋 Overview

- **Authors**: Tuan Duc Ngo, Jiahui Huang, Seoung Wug Oh, Kevin Blackburn-Matzen, Evangelos Kalogerakis, Chuang Gan, Joon-Young Lee
- **Institution**: UMass Amherst; Adobe Research; TU Crete
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.03744) | [Project Page](https://github.com/dage-site)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A dual-stream visual geometry transformer that disentangles global coherence from fine detail — a low-resolution stream runs global attention to build view-consistent features and camera poses efficiently, a high-resolution per-frame stream preserves sharp detail (up to 2K), and a lightweight cross-attention adapter fuses them — decoupling spatial resolution from clip length so it scales to ~1000 frames with practical runtime.

## 🎯 Key Contributions

1. **Dual-stream transformer**: Couples a per-frame high-resolution detail path with a multi-view low-resolution global-attention path, decoupling image resolution from sequence length (independent control of spatial detail and multi-view coherence).
2. **Lightweight fusion adapter**: A cross-attention (inject global context) + self-attention (re-calibrate per-frame coherence) adapter after the HR ViT encoder produces sharp yet globally consistent geometry.
3. **Efficiency + fidelity**: Confining heavy global attention to the LR stream avoids the quadratic bottleneck (2× faster at 540p, 28× faster at 2K vs global-attention baselines) while the HR stream keeps high-frequency detail.

## 🔧 Technical Details

### Architecture

- **LR stream**: processes the whole sequence at long side ≤ 252px through a DINOv2 tokenizer + alternating frame/global attention (no camera tokens, preserving permutation equivariance), regressing camera poses and a scene-wide metric scale. Trained with knowledge distillation from a Pi3 teacher (input capped at 518px) via a cosine-similarity feature-distillation loss.
- **HR stream**: a frozen 24-layer MoGe2 ViT processes each frame independently at native resolution for fine detail and zero-shot generalization.
- **Adapter**: five stacked [CrossAttn → SelfAttn] blocks; HR tokens (queries) cross-attend to LR tokens (keys/values). Uses interpolated RoPE for self-attention and a "snap-to-nearest-LR-grid-cell" RoPE for cross-attention to bridge the LR↔HR resolution mismatch (e.g. 252px vs 2K).
- **Heads**: a convolutional feature-pyramid dense head regresses pointmaps (smoother than grid-artifact heads); camera poses from LR features via average pooling + MLP (9D rotation representation); a metric-scale token + MLP for a single per-scene scale.

### Training

- Losses: ROE-aligned ℓ1 pointmap loss (no uncertainty weighting, to keep hard structures sharp), relative camera loss (geodesic rotation + ℓ1 translation), scale loss, normal loss, multi-scale image-gradient loss on canonical inverse depth, and feature distillation. Normal/gradient losses applied on synthetic data only (a single global alignment is kept rather than per-region alignment, to avoid seams/drift).
- LR stream initialized from Pi3, HR stream frozen from MoGe2; trained on 18 public indoor/outdoor, static/dynamic datasets.

## 📊 Results

### Video pointmap (Relp↓ / δp↑, per-video shared scale+shift)

원논문 Table 1. DAGE has the best average Rank (1.6) with pronounced high-resolution gains; it is not best in every column (e.g. GeoCrafter has lower KITTI Relp, VGGT lower Unreal4K Relp). MV/HR/PO = multi-view / high-res / pose support.

| Method     | GMU Relp/δp | Monkaa Relp/δp | Sintel Relp/δp | ScanNet Relp/δp | KITTI Relp/δp | Rank↓ |
| ---------- | ----------- | -------------- | -------------- | --------------- | ------------- | ----- |
| DepthPro   | 9.5 / 93.9  | 25.1 / 58.4    | 40.8 / 44.7    | 9.3 / 94.9      | 10.0 / 94.9   | 7.9   |
| MoGe2      | 19.6 / 72.4 | 25.0 / 57.0    | 29.8 / 58.4    | 12.4 / 89.4     | 9.0 / 97.2    | 6.8   |
| CUT3R      | 8.0 / 93.7  | 31.8 / 47.5    | 35.8 / 47.5    | 5.9 / 97.9      | 14.5 / 87.5   | 6.8   |
| VGGT       | 5.4 / 93.8  | 13.6 / 84.4    | 23.7 / 73.1    | 2.9 / 99.0      | 7.5 / 97.4    | 3.4   |
| Pi3        | 5.2 / 94.2  | 11.6 / 90.0    | 22.0 / 72.9    | 2.2 / 99.4      | 6.3 / 97.3    | 3.3   |
| GeoCrafter | 8.3 / 94.8  | 15.7 / 83.4    | 25.0 / 69.3    | 8.3 / 96.9      | 5.6 / 98.8    | 3.9   |
| **DAGE**   | 4.9 / 94.2  | 10.1 / 91.0    | 21.5 / 75.6    | 2.1 / 99.5      | 5.9 / 99.0    | 1.6   |

### Sharpness depth (F1↑ / CPDBE↓)

원논문 Table 2. Among temporally consistent video methods DAGE has the highest F1 and lowest CPDBE. DepthPro reaches higher F1 on some datasets (e.g. Sintel 0.41) but higher CPDBE (less temporally consistent boundaries).

| Method   | Monkaa F1/CPDBE | Sintel F1/CPDBE | UrbanSyn F1/CPDBE | Unreal4K F1/CPDBE |
| -------- | --------------- | --------------- | ----------------- | ----------------- |
| DepthPro | 0.19 / 21.3     | 0.41 / 17.0     | 0.14 / 12.5       | 0.07 / 116.4      |
| MoGe2    | 0.27 / 11.6     | 0.27 / 10.1     | 0.09 / 19.1       | 0.10 / 35.2       |
| CUT3R    | 0.08 / 20.3     | 0.11 / 16.5     | 0.01 / 44.0       | 0.01 / 63.1       |
| VGGT     | 0.14 / 11.1     | 0.20 / 9.6      | 0.02 / 42.0       | 0.03 / 38.1       |
| Pi3      | 0.14 / 12.7     | 0.20 / 8.1      | 0.01 / 27.9       | 0.03 / 46.9       |
| **DAGE** | 0.29 / 10.1     | 0.34 / 7.8      | 0.09 / 17.8       | 0.14 / 33.1       |

### Multi-view reconstruction (Acc↓ / Comp↓ / NC↑)

원논문 Table 3 (median). DAGE matches VGGT/Pi3 on sparse/dense and dominates the metric-scale setting.

| Setting | Method   | 7-Scenes Acc/Comp/NC  | NRGBD Acc/Comp/NC     |
| ------- | -------- | --------------------- | --------------------- |
| sparse  | VGGT     | 0.025 / 0.033 / 0.845 | 0.029 / 0.038 / 0.981 |
| sparse  | Pi3      | 0.029 / 0.049 / 0.841 | 0.015 / 0.014 / 0.992 |
| sparse  | **DAGE** | 0.027 / 0.042 / 0.846 | 0.018 / 0.016 / 0.992 |
| dense   | Pi3      | 0.007 / 0.011 / 0.792 | 0.008 / 0.005 / 0.987 |
| dense   | **DAGE** | 0.007 / 0.009 / 0.793 | 0.009 / 0.006 / 0.985 |
| metric  | CUT3R    | 0.189 / 0.186 / 0.582 | 0.307 / 0.253 / 0.606 |
| metric  | MapAny   | 0.339 / 0.109 / 0.639 | 0.156 / 0.108 / 0.910 |
| metric  | **DAGE** | 0.034 / 0.041 / 0.847 | 0.085 / 0.101 / 0.923 |

### Camera pose (ATE↓ / RPET↓ / RPER↓)

원논문 Table 4. DAGE runs its LR stream at 252px; at that resolution it beats VGGT/Pi3, but Pi3 at its full 518px still has lower Sintel pose error (ATE 0.074 vs DAGE 0.132).

| Method       | Sintel ATE/RPET/RPER  | TUM-dyn ATE/RPET/RPER | ScanNet ATE/RPET/RPER |
| ------------ | --------------------- | --------------------- | --------------------- |
| VGGT         | 0.167 / 0.062 / 0.491 | 0.012 / 0.010 / 0.311 | 0.035 / 0.015 / 0.382 |
| Pi3          | 0.074 / 0.040 / 0.282 | 0.014 / 0.009 / 0.312 | 0.031 / 0.013 / 0.347 |
| VGGT (252px) | 0.228 / 0.095 / 1.03  | 0.053 / 0.028 / 0.652 | 0.109 / 0.039 / 1.357 |
| Pi3 (252px)  | 0.153 / 0.088 / 0.684 | 0.025 / 0.019 / 0.370 | 0.045 / 0.017 / 0.438 |
| **DAGE**     | 0.132 / 0.051 / 0.406 | 0.014 / 0.010 / 0.323 | 0.031 / 0.014 / 0.389 |

### Throughput (FPS↑ / GPU memory↓ GB, 100-frame clips, A100)

원논문 Table 5. DAGE sustains 65.4 FPS at 540p (~2× Pi3) and 5.6 FPS at 2K where VGGT and GeoCrafter run OOM. MoGe2 is faster but does not produce temporally consistent geometry.

| Resolution | MoGe2†      | GeoCrafter | CUT3R       | VGGT        | Pi3         | **DAGE**    |
| ---------- | ----------- | ---------- | ----------- | ----------- | ----------- | ----------- |
| 540×360    | 79.4 / 8.1  | 3.1 / 17.3 | 27.2 / 16.5 | 30.1 / 17.3 | 36.3 / 17.2 | 65.4 / 10.1 |
| 960×512    | 30.0 / 15.3 | 1.7 / 24.1 | 20.3 / 19.0 | 2.1 / 26.9  | 3.1 / 23.1  | 28.9 / 18.3 |
| 2048×1024  | 6.1 / 22.1  | OOM        | 4.5 / 33.2  | OOM         | 0.2 / 66.7  | 5.6 / 27.9  |

### Ablations

- **Adapter design** (원논문 Table 6a, NRGBD): the proposed CrossAttn→SelfAttn adapter after the HR ViT (Acc 0.018 / Comp 0.016) beats aligned-MoGe2, interp+SA, all-CA, and per-ViT-block variants.
- **Sharpness components** (원논문 Table 6b, Sintel): full model F1 0.34; removing the monocular prior drops to 0.27, removing the gradient loss to 0.31; Pi3+AnyUp only 0.09.
- **LR-stream resolution** (원논문 Table 7): raising LR resolution slightly helps (252px ATE 0.132, F1 0.34, 65.4 FPS → 518px ATE 0.117, F1 0.36, 22.5 FPS) but sharply cuts FPS; distillation helps pose (252px no-distill RPER 0.584 vs 0.406).

## 💡 Insights & Impact

- The core idea — that global multi-view coherence needs only low resolution while sharp detail needs only per-frame high resolution — lets DAGE break the resolution/sequence-length coupling that forces VGGT/Pi3 to ≤518px and short clips, enabling 2K inputs and ~1000-frame videos.
- It dominates the metric-scale reconstruction setting where CUT3R/MapAnything are far weaker, and gives the best sharpness among temporally consistent methods.
- Honest trade-offs the authors state: Pi3 at its native 518px still edges DAGE on some pose metrics; performance can drop under extremely low overlap or rapid non-rigid motion; the HR path is memory-intensive at very high resolution; and the method does not recover dynamic motion.

## 🔗 Related Work

- **[Pi3](./pi3.md)**: alternating-attention teacher used for LR-stream distillation/initialization and the main comparison.
- **[VGGT](./vggt.md)**: global-attention feed-forward baseline whose quadratic cost DAGE sidesteps.
- **[MoGe-2](./moge-2.md)** / **[MoGe](./moge.md)**: single-view geometry model providing DAGE's frozen HR backbone and gradient-loss design.
- **[CUT3R](../dynamic/cut3r.md)** / **[Fast3R](./fast3r.md)** / **[MapAnything](./mapanything.md)** / **[DUSt3R](../foundation/dust3r.md)**: feed-forward reconstruction baselines compared on reconstruction/pose.

## 📚 Key Takeaways

1. DAGE splits geometry estimation into a low-res global stream (poses + view consistency, distilled from Pi3) and a high-res per-frame stream (sharp detail, frozen MoGe2), fused by a lightweight cross/self-attention adapter.
2. This decoupling scales to 2K resolution and ~1000 frames at 2× (540p) to 28× (2K) speedups over global-attention baselines, sustaining 65.4 FPS at 540p and 5.6 FPS at 2K where VGGT runs OOM.
3. It achieves the best video-pointmap average rank (1.6), the best sharpness among temporally consistent methods, and dominates metric reconstruction — while Pi3 at full 518px retains an edge on some pose metrics.

# NoDrift3R: Raymap-Guided Coupling for Drift-Robust Unposed Feed-Forward 3D Reconstruction (arXiv preprint)

## 📋 Overview

- **Authors**: Xiangyu Sun, Liu Liu, Seungkwon Yang, Jingbing Han, Seungtae Nam, Zhizhong Su, Eunbyung Park
- **Institution**: Sungkyunkwan University, Horizon Robotics, Yonsei University
- **Venue**: arXiv preprint (2026-07)
- **Note**: The venue could not be confirmed from any primary source (no arXiv comment, OpenReview record, CVF entry, or GitHub badge stating acceptance). It is recorded as a preprint and should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2607.07168) | [Project Page](https://xiangyu1sun.github.io/NoDrift3R-project-page/)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: Identifies cumulative pose drift as the bottleneck in pose-free feed-forward 3DGS, and fixes it by deriving Gaussian centers from a predicted **raymap** (`p = o + D·r`) so that RGB rendering loss backpropagates into geometry and raymap loss regularizes appearance — a bidirectional loop the paper calls "Rendering-to-Geometry Gain."

## 🎯 Key Contributions

1. **Diagnosis of the long-sequence bottleneck**: cumulative pose estimation drift, not rendering capacity, limits quality in long sequences. SfM-based pseudo-GT poses inject sensor noise; purely rendering-based supervision produces optimization instability and local minima because geometry and pose are optimized simultaneously.
2. **Raymap-Guided Coupling (RGC) module**: Gaussian positions are lifted from a per-pixel raymap rather than conditioned on low-dimensional pose parameters, removing the information bottleneck that limits pose→Gaussian interaction in prior pose-conditioned designs.
3. **Dual-Frequency Viewpoint Scheduling**: an easy-to-hard overlap curriculum _plus_ a replay mechanism that keeps re-injecting small-interval pairs, addressing a specific failure the paper attributes to E-RayZer's linear visual-overlap extension — it degrades on small-interval samples that local geometric consistency depends on.

## 🔧 Technical Details

### Why raymaps rather than poses

The paper contrasts three paradigms:

- **(a)** Predict pixel-aligned Gaussians directly from images with no use of estimated poses (AnySplat, Uni3R). Reasonable renderings, but no mechanism tying pose estimation to the 3D representation.
- **(b)** Condition Gaussian prediction on estimated poses (YoNoSplat). Some interaction, but poses are low-dimensional rotation/translation parameters — an information bottleneck that cannot carry the dense geometric cues Gaussian placement needs.
- **(c)** NoDrift3R: predict dense raymaps that _directly determine_ the spatial distribution of Gaussians. Because raymaps encode per-pixel ray directions, appearance supervision and geometric constraints both influence every per-pixel Gaussian.

### The lifting equation

Per-view tokens from a patch embedding are processed by a single multi-view transformer (e.g. Depth Anything v3). A **Dual-DPT head** predicts two signals per view: a raymap `R ∈ R^{HW×6}` and a depth map `D ∈ R^{HW}`. The first three channels of R are the ray direction `r`, the last three the ray origin `o`. Gaussian centers are then:

```text
p_j = o_j + D_j · r_j
```

and `μ_j = p_j` — the lifted position _is_ the Gaussian center, with no separate offset head. The Gaussian head predicts `{α_j, c_j, s_j, q_j}` from the same latent tokens, constrained by `α = σ(f^α)`, `s = exp(f^s)`, `q = normalize(f^q)`.

### Loss

```text
L     = L_rgb + λ_cam · L_cam + λ_ray · L_ray
L_rgb = (1/N) Σ ( λ_mse ‖I_i − Î_i‖²₂ + λ_lpips · LPIPS(I_i, Î_i) )
L_cam = (1/N) Σ Huber(θ̂_i − θ_i)
L_ray = L_origin + L_direction     (MSE on ray origins and directions separately)
```

with `λ_ray = 1.0`, `λ_cam = 0.5`.

The paper is explicit that the simplicity here is intentional: because Gaussian positions are _derived_ from depth and raymap, `L_rgb` backpropagates through rendering into the raymaps (appearance refines geometry), while `L_ray` constrains ray directions which define Gaussian positions (geometry improves rendering). "The synergy is baked into the representation and the training flow itself."

### Dual-Frequency Viewpoint Scheduling

Two mechanisms on top of a standard overlap curriculum:

1. **Bounded overlap-aware curriculum** — parameterized by `g_max`, the maximum interval expansion.
2. **Replay** — repeatedly re-injects small-interval samples, providing stochastic local geometric regularization.

## 📊 Results

### Novel view synthesis on DL3DV

원논문 Table 1. p, k 열은 각각 ground-truth 포즈·intrinsic 사용 여부다.

| Method          | Venue       | p   | k   | 6v PSNR ↑  | SSIM ↑    | LPIPS ↓   |
| --------------- | ----------- | --- | --- | ---------- | --------- | --------- |
| MVSplat         | ECCV'24     | ✓   | ✓   | 22.659     | 0.760     | 0.173     |
| DepthSplat      | CVPR'25     | ✓   | ✓   | 23.418     | 0.797     | 0.136     |
| NoPoSplat       | ICLR'25     |     | ✓   | 22.766     | 0.743     | 0.179     |
| AnySplat        | SA'25 (TOG) |     |     | 19.027     | 0.554     | 0.235     |
| YoNoSplat       | ICLR'26     |     |     | 24.531     | 0.804     | 0.142     |
| ERayZer 256×256 | CVPR'26     |     |     | 24.814     | 0.791     | 0.184     |
| **Ours**        | -           |     |     | **24.922** | **0.826** | **0.127** |

원논문 Table 1 (계속) — 12·24 view.

| Method          | 12v PSNR ↑ | SSIM ↑    | LPIPS ↓   | 24v PSNR ↑ | SSIM ↑    | LPIPS ↓   |
| --------------- | ---------- | --------- | --------- | ---------- | --------- | --------- |
| MVSplat         | 21.289     | 0.709     | 0.224     | 19.975     | 0.662     | 0.269     |
| DepthSplat      | 21.911     | 0.753     | 0.179     | 20.088     | 0.690     | 0.240     |
| NoPoSplat       | 19.380     | 0.563     | 0.318     | 17.860     | 0.495     | 0.397     |
| AnySplat        | 18.940     | 0.549     | 0.262     | 19.703     | 0.596     | 0.249     |
| YoNoSplat       | 22.933     | 0.746     | 0.187     | 22.174     | 0.720     | 0.209     |
| ERayZer 256×256 | 20.454     | 0.639     | 0.317     | 18.750     | 0.571     | 0.406     |
| **Ours**        | **24.250** | **0.797** | **0.141** | **24.242** | **0.794** | **0.142** |

The revealing pattern is the _slope_. Every baseline degrades as views increase (ERayZer 24.814 → 18.750; NoPoSplat 22.766 → 17.860; YoNoSplat 24.531 → 22.174), while NoDrift3R holds at 24.922 → 24.250 → 24.242. The paper's stated headline is **+1.6 dB PSNR over YoNoSplat in the 24-view setting** — that arithmetic (24.242 − 22.174 = 2.07) is closer to +2.1 dB in this table; the +1.6 dB figure is what the paper states.

### Camera pose estimation on DL3DV (224×224 input)

원논문 Table 2. '-'는 해당 설정 결과가 보고되지 않은 경우다.

| Model             | 6v AUC@5° ↑ | AUC@10° ↑ | AUC@20° ↑ | 12v AUC@5° ↑ | AUC@10° ↑ | AUC@20° ↑ | 24v AUC@5° ↑ | AUC@10° ↑ | AUC@20° ↑ |
| ----------------- | ----------- | --------- | --------- | ------------ | --------- | --------- | ------------ | --------- | --------- |
| VGGT 518×280      | 0.700       | 0.848     | 0.924     | -            | -         | -         | -            | -         | -         |
| π³ 518×280        | 0.795       | 0.897     | 0.949     | -            | -         | -         | -            | -         | -         |
| NoPoSplat 256×256 | 0.538       | 0.735     | 0.853     | -            | -         | -         | -            | -         | -         |
| AnySplat 448×448  | 0.596       | 0.776     | 0.884     | 0.517        | 0.732     | 0.864     | 0.476        | 0.708     | 0.851     |
| YoNoSplat 224×224 | 0.833       | 0.917     | 0.958     | 0.804        | 0.902     | 0.951     | 0.778        | 0.885     | 0.942     |
| ERayZer 256×256   | 0.846       | 0.972     | 0.983     | 0.421        | 0.699     | 0.767     | 0.389        | 0.654     | 0.707     |
| **Ours 224×224**  | **0.967**   | **0.983** | **0.992** | **0.961**    | **0.979** | **0.990** | **0.949**    | **0.972** | **0.985** |

ERayZer's collapse (0.846 → 0.389 AUC@5° from 6v to 24v) is the drift phenomenon the paper set out to attack. NoDrift3R loses only 0.018.

### Comparison against 3D foundation models

원논문 Table 10. DAv3 = Depth Anything v3.

| Method   | 6v 5° ↑   | 10° ↑     | 20° ↑     | 12v 5° ↑  | 10° ↑     | 20° ↑     | 24v 5° ↑  | 10° ↑     | 20° ↑     |
| -------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| VGGT     | 0.700     | 0.848     | 0.924     | -         | -         | -         | -         | -         | -         |
| π³       | 0.795     | 0.897     | 0.949     | -         | -         | -         | -         | -         | -         |
| DAv3     | 0.659     | 0.823     | 0.911     | 0.576     | 0.769     | 0.879     | 0.529     | 0.736     | 0.860     |
| **Ours** | **0.970** | **0.985** | **0.992** | **0.942** | **0.969** | **0.984** | **0.936** | **0.966** | **0.982** |

### Against a fine-tuned Depth Anything v3

원논문 Table 8. \*는 DL3DV로 파인튜닝한 DepthAnything v3를 뜻한다 — 즉 백본이 동일한 데이터를 본 공정한 대조군이다.

| Model              | 6v AUC@5° ↑ | 12v AUC@5° ↑ | 24v AUC@5° ↑ |
| ------------------ | ----------- | ------------ | ------------ |
| NoPoSplat 256×256  | 0.538       | -            | -            |
| AnySplat 448×448   | 0.596       | 0.517        | 0.476        |
| YoNoSplat 224×224  | 0.833       | 0.804        | 0.778        |
| DepthAnything v3   | 0.659       | 0.576        | 0.529        |
| DepthAnything v3\* | 0.955       | 0.928        | 0.920        |
| **Ours 224×224**   | **0.970**   | **0.942**    | **0.936**    |

This is the honest control. Fine-tuning the DAv3 backbone on DL3DV closes most of the gap (0.659 → 0.955 at 6v). NoDrift3R's remaining margin over the fine-tuned backbone is 0.015 / 0.014 / 0.016 AUC@5° — real but modest. Much of the headline improvement over off-the-shelf DAv3 comes from in-domain training, and the paper reports this rather than hiding it.

### Zero-shot pose on RE10K (trained on DL3DV, 6 views)

원논문 Table 3.

| Method            | AUC@5° ↑  | AUC@10° ↑ | AUC@20° ↑ |
| ----------------- | --------- | --------- | --------- |
| MASt3R 518×288    | 0.609     | 0.776     | 0.878     |
| VGGT 518×280      | 0.566     | 0.753     | 0.867     |
| π³ 518×280        | 0.705     | 0.841     | 0.916     |
| NoPoSplat 256×256 | 0.443     | 0.627     | 0.755     |
| YoNoSplat 224×224 | 0.740     | 0.895     | **0.924** |
| **Ours 224×224**  | **0.755** | **0.911** | 0.923     |

**YoNoSplat retains the best AUC@20°** (0.924 vs 0.923). The paper states its own claim precisely: best on 5° and 10°.

### NVS on RE10K (trained and tested on RE10K, 6 views)

원논문 Table 4.

| Method     | p   | k   | PSNR ↑     | SSIM ↑    | LPIPS ↓   |
| ---------- | --- | --- | ---------- | --------- | --------- |
| DepthSplat | ✓   | ✓   | 24.156     | 0.846     | 0.145     |
| NoPoSplat  |     | ✓   | 22.175     | 0.750     | 0.207     |
| YoNoSplat  | ✓   | ✓   | 25.037     | 0.848     | 0.134     |
| YoNoSplat  |     | ✓   | 25.395     | 0.857     | 0.131     |
| YoNoSplat  |     |     | 24.571     | 0.823     | 0.144     |
| **Ours**   |     |     | **25.736** | **0.876** | **0.128** |

NoDrift3R without poses or intrinsics beats YoNoSplat even when YoNoSplat is given both.

### Cross-dataset generalization to ScanNet++

원논문 Table 5. DL3DV로 학습 후 ScanNet++에서 파인튜닝 없이 평가. 전체 시퀀스에서 샘플링하며 타깃 뷰는 고정이다.

| Method    | 32v PSNR ↑ | SSIM ↑    | LPIPS ↓   | 64v PSNR ↑ | SSIM ↑    | LPIPS ↓   | 128v PSNR ↑ | SSIM ↑    | LPIPS ↓   |
| --------- | ---------- | --------- | --------- | ---------- | --------- | --------- | ----------- | --------- | --------- |
| AnySplat  | 14.054     | 0.494     | 0.468     | 15.982     | 0.551     | 0.412     | 16.988      | 0.583     | 0.386     |
| YoNoSplat | 16.886     | 0.600     | 0.432     | 17.368     | 0.608     | 0.413     | 17.641      | 0.617     | 0.405     |
| **Ours**  | **17.569** | **0.620** | **0.419** | **18.935** | **0.668** | **0.348** | **19.714**  | **0.695** | **0.317** |

The margin _widens_ with view count (0.68 → 1.57 → 2.07 dB), which the paper attributes to accurate pose estimation on long sequences.

### Loss ablation

원논문 Table 6. large 모델 기준.

| Model             | 6v PSNR ↑  | SSIM ↑    | AUC@5° ↑  | AUC@10° ↑ |
| ----------------- | ---------- | --------- | --------- | --------- |
| w/o raymap-guided | 23.062     | 0.752     | 0.821     | 0.907     |
| w/o raymap loss   | 21.869     | 0.708     | 0.869     | 0.927     |
| w/o rgb loss      | 12.608     | 0.321     | 0.851     | 0.922     |
| **Ours**          | **23.302** | **0.766** | **0.874** | **0.935** |

원논문 Table 6 (계속) — 12·24 view.

| Model             | 12v PSNR ↑ | SSIM ↑    | AUC@5° ↑  | AUC@10° ↑ | 24v PSNR ↑ | SSIM ↑    | AUC@5° ↑  | AUC@10° ↑ |
| ----------------- | ---------- | --------- | --------- | --------- | ---------- | --------- | --------- | --------- |
| w/o raymap-guided | **22.375** | **0.717** | 0.753     | 0.867     | 21.379     | 0.599     | 0.690     | 0.821     |
| w/o raymap loss   | 20.933     | 0.655     | 0.814     | 0.902     | 20.609     | 0.635     | 0.782     | 0.875     |
| w/o rgb loss      | 12.375     | 0.325     | 0.801     | 0.891     | 12.378     | 0.328     | 0.754     | 0.851     |
| **Ours**          | 21.909     | 0.696     | **0.829** | **0.907** | **21.626** | **0.675** | **0.787** | **0.883** |

The paper reads this as evidence of bidirectional coupling: removing raymap loss hurts _rendering_ (geometry helps appearance), and removing RGB loss hurts _pose_ (appearance helps geometry). Note the reported loss: **at 12 views the "w/o raymap-guided" variant beats the full model on PSNR (22.375 vs 21.909) and SSIM (0.717 vs 0.696)** while losing badly on pose — the paper acknowledges this variant "can still produce competitive rendering in some settings."

### RGC module ablation

원논문 Table 11. DL3DV, 6 views.

| Variant                       | PSNR ↑            | SSIM ↑    | LPIPS ↓   | 5° ↑      | 10° ↑     | 20° ↑     |
| ----------------------------- | ----------------- | --------- | --------- | --------- | --------- | --------- |
| DAv3 Gaussian Head            | 22.407            | 0.731     | 0.212     | 0.841     | 0.919     | 0.959     |
| Ours, detach raymap and depth | does not converge | -         | -         | -         | -         | -         |
| Ours, detach raymap           | 20.178            | 0.610     | 0.320     | 0.833     | 0.914     | 0.957     |
| **Ours**                      | **23.302**        | **0.766** | **0.168** | **0.874** | **0.935** | **0.967** |

**Detaching both raymap and depth prevents convergence entirely.** The gradient path from rendering back through the lifted positions is not an optimization nicety here — it is load-bearing.

### Dual-Frequency Viewpoint Scheduling ablation

원논문 Table 7.

| Model                   | 0–50 PSNR ↑ | SSIM ↑    | AUC@5° ↑  | AUC@10° ↑ | 0–150 PSNR ↑ | SSIM ↑    | AUC@5° ↑  | AUC@10° ↑ |
| ----------------------- | ----------- | --------- | --------- | --------- | ------------ | --------- | --------- | --------- |
| original sampler        | 22.696      | 0.747     | 0.782     | 0.884     | 18.815       | 0.571     | 0.591     | 0.744     |
| g_max = 10, w/o replay  | **23.302**  | **0.766** | **0.874** | **0.935** | 19.542       | 0.579     | 0.687     | 0.803     |
| g_max = 20, w/o replay  | 22.892      | 0.752     | 0.872     | 0.935     | 19.690       | 0.592     | 0.709     | 0.826     |
| g_max = ∞, w/o replay   | 22.744      | 0.742     | 0.862     | 0.930     | 19.712       | 0.588     | **0.722** | **0.832** |
| g_max = ∞, replay = 50% | 23.006      | 0.745     | 0.864     | 0.929     | **19.745**   | **0.592** | 0.721     | 0.832     |

Three findings the paper draws: (1) any variant beats the original YoNoSplat-style sampler, so sampling strategy is a primary limiting factor; (2) without replay, larger `g_max` trades short-range (0–50) performance for long-range (0–150); (3) replay at `g_max = ∞` recovers short-range performance while keeping long-range strength. Note this is a genuine trade-off, not a free win — `g_max = 10` is still the best short-range configuration.

### Speed and model size

원논문 Table 9. A100 한 장에서 end-to-end로 측정.

| Method            | Params | 6v speed   | 6v PSNR ↑  | 6v AUC@5° ↑ | 24v speed  | 24v PSNR ↑ | 24v AUC@5° ↑ |
| ----------------- | ------ | ---------- | ---------- | ----------- | ---------- | ---------- | ------------ |
| AnySplat 448×448  | 1.19B  | 0.955s     | 19.027     | 0.596       | 3.940s     | 19.703     | 0.476        |
| YoNoSplat 224×224 | 1.02B  | 0.236s     | 24.531     | 0.833       | 0.395s     | 22.174     | 0.778        |
| **Ours-Large**    | 0.44B  | **0.108s** | 24.341     | 0.906       | **0.319s** | 22.095     | 0.788        |
| **Ours-Giant**    | 1.40B  | 0.155s     | **24.550** | **0.970**   | 0.667s     | **23.753** | **0.936**    |

Ours-Large is the fastest at 0.44B parameters; Ours-Giant is the most accurate at 1.40B. Note Ours-Large loses 6v and 24v PSNR to YoNoSplat (24.341 vs 24.531; 22.095 vs 22.174) while winning pose.

### Zero-shot on Mip-NeRF 360

원논문 Table 13.

| Method         | Params | Indoor PSNR ↑ | SSIM ↑    | AUC@10° ↑ | AUC@20° ↑ | Outdoor PSNR ↑ | SSIM ↑    | AUC@10° ↑ | AUC@20° ↑ |
| -------------- | ------ | ------------- | --------- | --------- | --------- | -------------- | --------- | --------- | --------- |
| AnySplat       | 1.19B  | 19.76         | 0.518     | 0.667     | 0.815     | 13.50          | 0.231     | 0.669     | 0.782     |
| E-RayZer       | 0.25B  | 20.05         | 0.574     | 0.464     | 0.653     | 16.19          | 0.248     | 0.106     | 0.525     |
| **Ours-Large** | 0.44B  | **20.54**     | **0.590** | **0.842** | **0.921** | **17.52**      | **0.288** | **0.767** | **0.883** |

### Figures without printed values

Figures 5, 6, and 7 (qualitative NVS comparisons and the view-count degradation plot) carry PSNR annotations per-image but no tabulated values; nothing is read off them here.

## 💡 Insights & Impact

### The representation determines what gradients can reach

The single most transferable idea is architectural, not algorithmic. By making `μ_j = o_j + D_j·r_j` rather than predicting Gaussian centers from a separate head, the paper guarantees that photometric gradients flow into the geometry. Table 11 confirms this is not decoration: detach the raymap and depth and the model does not converge at all. Pose-conditioned designs route geometry through a 6-DoF bottleneck; raymap-conditioned designs route it through HW×6 values.

### Drift shows up as a slope, not a level

Every table in this paper should be read across view counts rather than at a single setting. At 6 views NoDrift3R beats ERayZer by 0.108 dB — nearly a tie. At 24 views the gap is 5.5 dB, because ERayZer's pose AUC@5° has fallen from 0.846 to 0.389. Benchmarking pose-free 3DGS at small view counts systematically hides the failure mode that matters.

### Curricula need a low-frequency component

The critique of E-RayZer's linear overlap extension is specific and testable: monotonically increasing difficulty starves the model of the small-interval pairs that local geometric consistency depends on. Table 7 shows the trade-off explicitly — `g_max = ∞` without replay is best long-range and worst short-range — and shows replay resolving it. This is a general lesson for any easy-to-hard schedule.

### Fine-tuning the backbone is a large part of the story

Table 8 deserves emphasis: fine-tuning Depth Anything v3 on DL3DV takes it from 0.659 to 0.955 AUC@5° at 6 views, against NoDrift3R's 0.970. The RGC module's contribution over a domain-matched backbone is ~0.015 AUC — meaningful, but the paper's honest inclusion of this control is more informative than the headline comparison against off-the-shelf DAv3.

## 🔗 Related Work

- [VGGT](vggt.md) — pose-estimation reference in Tables 2, 3, and 10
- [π³](pi3.md) — the strongest 3D foundation model baseline on 6-view pose; NoDrift3R exceeds it at 224×224 against π³'s 518×280
- [Depth Anything 3](depth-anything-3.md) — the multi-view transformer backbone, and the fine-tuned control in Table 8
- [MASt3R](../foundation/mast3r.md) — zero-shot RE10K pose baseline
- [YoNoSplat](../gaussian-splatting/yonosplat.md) — the closest prior pose-free feed-forward 3DGS method and the main competitor throughout
- [InstantSplat](../gaussian-splatting/instantsplat.md) — related pose-free Gaussian reconstruction
- [DUSt3R](../foundation/dust3r.md) — origin of the unposed feed-forward reconstruction line

## 📚 Key Takeaways

1. **Derive Gaussian centers from a raymap, not from a pose.** `p = o + D·r` gives photometric gradients a path into geometry; detaching that path stops convergence entirely.
2. **Pose drift, not rendering capacity, is what breaks long sequences.** ERayZer falls 24.814 → 18.750 PSNR from 6 to 24 views as its pose AUC@5° falls 0.846 → 0.389; NoDrift3R holds 24.922 → 24.242.
3. **Bidirectional coupling is measurable.** Removing raymap loss costs PSNR; removing RGB loss costs pose AUC. Neither loss is purely for its own task.
4. **Curricula need replay.** Monotone easy-to-hard scheduling trades short-range consistency for long-range coverage; re-injecting small-interval pairs recovers both.
5. **Report the fine-tuned control.** Against a DL3DV-fine-tuned Depth Anything v3, the margin is ~0.015 AUC@5°, not the ~0.31 implied by comparing to the off-the-shelf model.
6. **Not uniformly best.** YoNoSplat retains RE10K zero-shot AUC@20°; the "w/o raymap-guided" ablation beats the full model on 12-view PSNR and SSIM; Ours-Large trails YoNoSplat on PSNR while beating it on pose.

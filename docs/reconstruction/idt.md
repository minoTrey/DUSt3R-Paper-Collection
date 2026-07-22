# IDT: A Physically Grounded Transformer for Feed-Forward Multi-View Intrinsic Decomposition (arXiv preprint (2025-12))

![idt — architecture](https://arxiv.org/html/2512.23667/assets/pipeline.png)

_Overview of the IDT pipeline (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Kang Du, Yirui Guan, Zeyu Wang
- **Institution**: The Hong Kong University of Science and Technology (Guangzhou); The Hong Kong University of Science and Technology; Tencent
- **Venue**: arXiv preprint (2025-12)
- **Links**: [Paper](https://arxiv.org/abs/2512.23667) | [Code](https://github.com/dukang/IDT)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward multi-view transformer that decomposes a set of images of a static scene into diffuse reflectance (albedo), diffuse shading, and specular shading in a single forward pass, using a VGGT-style encoder plus factor-specific appearance adapters and a physically grounded image formation model.

## 🎯 Key Contributions

1. **Feed-forward multi-view intrinsic decomposition**: Extends multi-view geometric reasoning (VGGT-style attention) to intrinsic factorization, producing view-consistent intrinsic factors in a single forward pass without iterative generative sampling.
2. **Physically grounded intrinsic formulation**: An explicit image formation model `I_v(x) = A(x) ⊙ S_v^diff(x) + S_v^spec(x)` that separates view-invariant albedo, view-dependent diffuse (Lambertian) shading, and additive view-dependent specular shading.
3. **Appearance adapters + shared illumination**: Factor-specific cross-attention adapters route information from a shared multi-view token set to each intrinsic head, and a Spherical Gaussian Mixture (SGM) scene-level illumination representation conditions the shading heads.
4. **Improved single-view accuracy and multi-view consistency**: Reported on both synthetic (Hypersim) and real-world/photorealistic (InteriorVerse) indoor datasets versus prior intrinsic decomposition methods.

## 🔧 Technical Details

### Image Formation Model

For each view `v`, the observed image is modeled (원논문 Eq. 2) as:

```text
I_v(x) = A(x) ⊙ S_v^diff(x) + S_v^spec(x)
```

- `A` — view-invariant diffuse reflectance (albedo), shared across all views.
- `S_v^diff` — diffuse shading capturing illumination-dependent Lambertian effects (view-dependent).
- `S_v^spec` — additive, view-dependent non-Lambertian effects such as specular highlights.

The multiplicative albedo–diffuse form follows a Lambertian assumption; specular reflection is modeled as an additive view-dependent term because it cannot be reliably factorized without explicit BRDF parameters (e.g., roughness). Isolating the specular term prevents view-dependent appearance from leaking into albedo.

### Pipeline

1. **Multi-view transformer encoder** (VGGT-style): produces a single shared latent token set `Z = E(I)` for all `V` input views. IDT does not hard-split `Z`; geometry vs. appearance token specialization (`Z_geo`, `Z_app`) emerges implicitly from task-specific supervision and routing.
2. **Appearance adapters**: for each factor `k ∈ {alb, diff, spec}`, a lightweight cross-attention adapter produces a compact task-specific representation `Z̃_k = A_k(Z)`. Adapter parameters are factor-specific (not shared across intrinsic heads).
3. **Scene-conditioned cross-attention**: adapter queries are derived from pooled scene-level tokens (camera tokens, register tokens) across views rather than learnable slots; keys/values come from patch-level tokens across all views. This keeps the module fully feed-forward and aligns attended features across views.
4. **Illumination representation (SGM)**: a compact Spherical Gaussian Mixture `L` shared across views conditions the shading heads for illumination-aware prediction without explicit physically based rendering.
5. **Intrinsic prediction heads** (원논문 Eq. 6–8): `A = h_alb(Z̃_alb)`, `S_v^diff = h_diff(Z̃_diff,v, L)`, `S_v^spec = h_spec(Z̃_spec,v, L)`. Albedo `A` and illumination `L` are shared across views; shading components remain view-dependent.

### Training Objectives

The final objective (원논문 Eq. 14) is a weighted sum: `L = λ_alb L_alb + λ_diff L_diff + λ_spec L_spec + λ_recon L_recon + λ_illum L_illum`.

- **Albedo loss** `L_alb = ‖A − A*‖_1` — ℓ1 to preserve sharp material boundaries and reduce color bleeding.
- **Diffuse shading loss** — squared ℓ2 in the log domain (`‖log(S^diff+ε) − log(S^diff*+ε)‖_2^2`) to emphasize relative intensity errors and be robust to global illumination scale.
- **Specular shading loss** — squared ℓ2 in the log domain, preventing sparse high-intensity highlights from dominating training.
- **Reconstruction loss** `L_recon = (1/V) Σ_v ‖A ⊙ S_v^diff + S_v^spec − I_v‖_1` — enforces consistency with the image formation model.
- **Illumination loss** `L_illum = ‖L − L*‖_2^2` — applied only on datasets with explicit illumination supervision.

## 📊 Results

Metrics (원논문 Sec. 4.2): depth/normals use AbsRel, RMSE, mean angular error; intrinsic factors use MAE, PSNR, SSIM (shading additionally in the log domain). Multi-view consistency is measured by warping predicted factors to a reference view with known camera geometry and computing the average ℓ1 difference (lower is better).

> **Note on losses vs. baselines**: In the printed quantitative tables below (Tables 1–3), IDT reports the best value on every listed metric. The paper's specular-shading, multi-view-consistency, reconstruction (PSNR/SSIM), and ablation results are described in prose/figures without printed numbers, so no numeric comparison is transcribed for them here.

### Single-View Intrinsic Decomposition on HyperSim

원논문 Table 1. 화살표 방향은 원문 표기 그대로 (Shading PSNR은 원문에 ↓로 인쇄됨). `-`는 원문에서 미평가.

| Method     | Albedo PSNR ↑ | Albedo MAE ↓ | Albedo SSIM ↑ | Shading PSNR ↓ | Shading SSIM ↑ |
| ---------- | ------------- | ------------ | ------------- | -------------- | -------------- |
| IID        | 15.42         | 0.061        | 0.781         | -              | -              |
| RGBX       | 21.10         | 0.024        | 0.742         | 15.42          | 0.734          |
| IDT (Ours) | **22.85**     | **0.021**    | **0.842**     | 18.32          | **0.801**      |

### Single-View Depth Estimation

원논문 Table 2. 단일 뷰 세팅에서 평가.

| Method         | AbsRel ↓  | RMSE ↓    | δ1 ↑      |
| -------------- | --------- | --------- | --------- |
| Depth Anything | 0.406     | 0.391     | 0.372     |
| VGGT           | 0.383     | 0.354     | 0.412     |
| IDT (Ours)     | **0.358** | **0.341** | **0.433** |

### Single-View Surface Normal Estimation

원논문 Table 3. `11.25°`는 각오차 임계 내 픽셀 비율(%).

| Method     | Mean Angular Error ↓ | 11.25° ↑ |
| ---------- | -------------------- | -------- |
| RGB-X      | 19.8                 | 58.8     |
| IDT (Ours) | **14.1**             | **60.8** |

### Multi-View Consistency, Reconstruction, and Ablations

- **Multi-view consistency**: reported as substantially improved over prior intrinsic decomposition methods, but no numeric table is printed in the extracted text (그림/서술만, 수치 미인쇄).
- **Reconstruction quality**: PSNR and SSIM are stated to be reported on both Hypersim and InteriorVerse (원논문 Sec. 4.2), but the numeric values are not printed in the extracted text (수치 미인쇄).
- **Ablations** (원논문 Sec. 4.6, Hypersim, qualitative/서술): removing joint multi-view attention significantly degrades cross-view consistency while single-view accuracy stays comparable; disabling intrinsic-specific adapters increases material/illumination entanglement; removing SGM illumination conditioning causes unstable shading and illumination leakage into albedo. No numbers are printed for these ablations.

## 💡 Insights & Impact

- **Intrinsic ≠ geometry**: The authors argue intrinsic decomposition differs from geometric reconstruction — geometry benefits from aggregating all cross-view correspondences, whereas intrinsic factors need selective reasoning over appearance, illumination, and view-dependent effects. This motivates factor-specific adapters on top of a shared multi-view encoder rather than feeding one shared token set to all heads.
- **Emergent token specialization**: Rather than hard-splitting tokens into geometry vs. appearance, IDT lets specialization emerge from supervision and routing, consistent with emergent specialization in multi-task transformers.
- **Feed-forward vs. diffusion**: Prior single-view diffusion methods require iterative sampling and operate per-image, limiting efficiency and cross-view consistency; IDT enforces consistency at the representation level in a single pass.
- **Limitations** (원논문 Sec. 5): relies on a simplified image formation model and may struggle with extreme lighting or strongly non-Lambertian materials; does not explicitly enforce global geometric constraints; primarily evaluated on indoor scenes.

## 🔗 Related Work

- **[VGGT](vggt.md)**: IDT adopts a VGGT-style multi-view transformer encoder and uses per-view VGGT as a backbone-matched baseline (same backbone and training setup, but without joint multi-view attention) to isolate the effect of joint inference. VGGT is also a depth baseline (원논문 Table 2).
- **[Pi3](pi3.md)**: Cited among feed-forward multi-view transformer architectures that aggregate multi-view information in a single forward pass (원논문 Related Work, ref [28]).
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: Foundational feed-forward multi-view geometry line that IDT's multi-view reasoning motivation builds on (not directly benchmarked here).

IDT positions itself against three lines: inverse rendering / physically grounded decomposition (iterative, optimization-heavy), single-view intrinsic image decomposition (per-image, view-inconsistent), and diffusion-based intrinsic decomposition (iterative sampling, per-image). Its contribution is bringing feed-forward multi-view transformer reasoning into the intrinsic decomposition problem.

## 📚 Key Takeaways

1. **Feed-forward multi-view intrinsic decomposition**: albedo, diffuse shading, and specular shading inferred jointly across views in one pass, without iterative generative inference.
2. **Physically grounded**: an explicit additive diffuse+specular image formation model with a shared SGM illumination representation keeps factors interpretable and prevents specular leakage into albedo.
3. **Adapters over shared tokens**: factor-specific scene-conditioned cross-attention adapters decouple material vs. illumination cues from a shared multi-view encoder.
4. **Evidence**: on HyperSim, IDT reports the best albedo PSNR/MAE/SSIM and shading SSIM (원논문 Table 1), best depth AbsRel/RMSE/δ1 (원논문 Table 2), and best normal metrics (원논문 Table 3); multi-view consistency, reconstruction, and ablation gains are reported qualitatively without printed numbers.

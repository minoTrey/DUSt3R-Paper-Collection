# Trust3R: Evidential Uncertainty for Feed-Forward 3D Reconstruction (ICML 2026)

![trust3r — architecture](https://arxiv.org/html/2605.19539v1/x2.png)

_Overview of the proposed Trust3R framework (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Zihao Zhu, Wenyuan Zhao, Nuo Chen, Chao Tian, Zhiwen Fan
- **Institution**: Department of Electrical and Computer Engineering, Texas A&M University
- **Venue**: ICML 2026
- **Links**: [Paper](https://arxiv.org/abs/2605.19539) | [Project Page](https://trust3r-z.github.io/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A lightweight evidential uncertainty framework that augments a frozen feed-forward pointmap backbone (MASt3R) with a gated residual mean-refinement and a Normal-Inverse-Wishart evidential head, yielding a closed-form multivariate Student-t distribution for per-point geometric uncertainty in a single pass.

## 🎯 Key Contributions

1. **Probabilistically grounded pointmap uncertainty**: Replaces MASt3R's heuristic confidence score with an evidential UQ head that predicts NIW distributional parameters, giving each 3D point a closed-form Student-t predictive distribution — no Monte-Carlo sampling at inference.
2. **Pointmap-tailored evidential learning**: An evidence-regularized NLL loss (`L_UQ = L_NLL + λ_evi·L_evi`) prevents degenerate over-confidence by penalizing high evidence (κ + ν) under large errors.
3. **Gated residual head**: A residual correction `m = X₀ + σ(G)⊙Δm` refines the frozen backbone's mean only where needed, preserving pretrained geometric accuracy while stabilizing evidential training; an identity-initialized post-upsampling smoother suppresses patch-grid artifacts.
4. **Uncertainty decomposition and cross-architecture use**: Separates aleatoric (Ψ/(ν−4)) from epistemic (Ψ/(κ(ν−4))) uncertainty, and the same head transfers to a frozen VGGT backbone.

## 🔧 Technical Details

- **Backbone**: frozen MASt3R; only lightweight add-on heads are trained.
- **Predictive distribution**: multivariate Gaussian likelihood with a NIW conjugate prior (parameters θ = {m, κ, Ψ, ν}, d = 3, ν > d+1), integrated to a multivariate Student-t over the pointmap. Ψ is produced via a Cholesky factor L.
- **Mean-field factorization** over 3D points captures cross-coordinate covariance within a point but not cross-pixel covariance (left to future work).
- **Training**: AdamW (weight decay 0.05), base learning rate 3 × 10⁻⁴, cosine schedule over 10 epochs, no warmup; evidence regularization λ_evi = 10⁻³.
- **Evaluation**: per-image Sim(3) alignment before computing 3D errors, so metrics reflect local reliability rather than global pose/scale drift.

## 📊 Results

### Uncertainty ranking (average over three datasets)

원논문 Table 1. AURC·AUSE 낮을수록, ρ 높을수록 좋음. Time은 학습 시간(h). Sampling 계열(MCD, DeepEns)은 다중 패스.

| Inference   | Method         | Time  | AURC ↓     | AUSE ↓     | ρ ↑        |
| ----------- | -------------- | ----- | ---------- | ---------- | ---------- |
| Sampling    | MCD (T=16)     | –     | 0.4902     | 0.2726     | 0.2644     |
| Sampling    | DeepEns (K=5)  | 100.2 | 0.2992     | 0.0916     | 0.4556     |
| Single-pass | MASt3R         | –     | 0.4155     | 0.2053     | 0.4057     |
| Single-pass | Hetero         | 9.4   | 0.3973     | 0.1872     | 0.4183     |
| Single-pass | Trust3R (ours) | 10.5  | **0.3861** | **0.1684** | **0.4898** |

### Uncertainty ranking per dataset

원논문 Table 1. Single-pass 블록에서 Trust3R가 ScanNet++·TUM에서 최고이나 KITTI AURC는 Hetero(0.9749)가 Trust3R(0.9868)보다 낮다.

| Method         | SN++ AURC ↓ | SN++ AUSE ↓ | SN++ ρ ↑   | TUM AURC ↓ | TUM AUSE ↓ | TUM ρ ↑    | KITTI AURC ↓ | KITTI AUSE ↓ | KITTI ρ ↑  |
| -------------- | ----------- | ----------- | ---------- | ---------- | ---------- | ---------- | ------------ | ------------ | ---------- |
| MCD (T=16)     | 0.1777      | 0.0989      | 0.1937     | 0.0672     | 0.0368     | 0.2747     | 1.2257       | 0.6821       | 0.3249     |
| DeepEns (K=5)  | 0.0722      | 0.0381      | 0.3921     | 0.0453     | 0.0208     | 0.3127     | 0.7802       | 0.2159       | 0.6620     |
| MASt3R         | 0.1649      | 0.0747      | 0.2837     | 0.0538     | 0.0233     | 0.4812     | 1.0277       | 0.5178       | 0.4523     |
| Hetero         | 0.1616      | 0.0715      | 0.3545     | 0.0555     | 0.0251     | 0.4669     | **0.9749**   | **0.4650**   | 0.4335     |
| Trust3R (ours) | **0.1233**  | **0.0444**  | **0.4930** | **0.0481** | **0.0178** | **0.5169** | 0.9868       | 0.4431       | **0.4596** |

On ScanNet++, Trust3R reduces AURC from 0.1649 to 0.1233 (≈25%) and AUSE from 0.0747 to 0.0444 (≈41%) over the MASt3R confidence baseline.

### Reconstruction accuracy (Sim(3)-aligned pointmap error)

원논문 Table 2. 낮을수록 좋음. KITTI에서는 Trust3R가 MASt3R보다 높은(나쁜) 오차.

| Method  | SN++ MAE ↓ | SN++ RMSE ↓ | TUM MAE ↓  | TUM RMSE ↓ | KITTI MAE ↓ | KITTI RMSE ↓ |
| ------- | ---------- | ----------- | ---------- | ---------- | ----------- | ------------ |
| MASt3R  | 0.2164     | 0.3026      | 0.0938     | 0.1600     | **1.6108**  | **3.0427**   |
| Trust3R | **0.1959** | **0.2849**  | **0.0873** | **0.1496** | 1.6648      | 3.0772       |

### Computational overhead

원논문 Table 3. MASt3R는 사전학습 체크포인트라 학습 시간 비교 불가(–).

| Method        | Training (h) | PeakMem (GB) | Inference (ms/pair) |
| ------------- | ------------ | ------------ | ------------------- |
| MCD (T=16)    | –            | 3.15         | 1225.77             |
| DeepEns (K=5) | 100.2        | 13.60        | 316.88              |
| MASt3R        | –            | 2.71         | 49.35               |
| Hetero        | 9.4          | 2.88         | 70.14               |
| Trust3R       | 10.5         | 3.16         | 80.92               |

### Cross-architecture generalization to VGGT

원논문 Table 4. ρ 높을수록, AURC·AUSE·NLL 낮을수록 좋음.

| Variant         | ρ ↑        | AURC ↓     | AUSE ↓     | NLL ↓       |
| --------------- | ---------- | ---------- | ---------- | ----------- |
| VGGT confidence | 0.3162     | 0.1084     | 0.0452     | -2.4770     |
| VGGT + Trust3R  | **0.6419** | **0.0841** | **0.0209** | **-3.5999** |

## 💡 Insights & Impact

- **Heuristic confidence ≠ uncertainty**: DUSt3R/MASt3R confidence is a learned regression weight without probabilistic meaning; Trust3R's evidential distribution aligns better with empirical 3D error and reduces overconfident failures (Fig. 1 shows top-error/lowest-uncertainty pixels dropping, e.g., 6.22% → 0.00% and 23.34% → 11.67% in the shown cases, 수치는 그림 캡션 기준).
- **Single-pass efficiency**: Trust3R adds only moderate overhead (49.35 → 80.92 ms/pair vs MASt3R) versus sampling methods (MCD 1225.77 ms/pair; DeepEns 100.2 h training) while approaching or exceeding their ranking quality on indoor data.
- **Honest limits**: Deep Ensembles (multi-pass) still lead on KITTI ranking, and on KITTI Trust3R slightly worsens both AURC and reconstruction MAE/RMSE versus MASt3R — the gains concentrate on cluttered indoor scenes.
- **Plug-and-play across backbones**: Attaching the head to frozen VGGT roughly doubles rank correlation (0.3162 → 0.6419) and halves AUSE, indicating the approach is not MASt3R-specific.

## 🔗 Related Work

- **[MASt3R](mast3r.md)**: The frozen backbone whose deterministic pointmap + heuristic confidence Trust3R replaces with an evidential distribution.
- **[DUSt3R](dust3r.md)**: Established the pairwise pointmap regression paradigm and the confidence-as-weight design Trust3R critiques.
- **[VGGT](../reconstruction/vggt.md)**: Second backbone used for cross-architecture validation of the evidential head.

## 📚 Key Takeaways

1. **Evidential learning brings probabilistic uncertainty to dense pointmaps** in one forward pass, avoiding the sampling cost of MC dropout / deep ensembles.
2. **Gated residual refinement preserves pretrained geometry** while stabilizing NIW/Student-t training, so accuracy improves on indoor data rather than degrading.
3. **Reliable per-point uncertainty** yields lower AURC/AUSE and higher rank correlation, providing a usable reliability signal for downstream weighting, filtering, and fusion — with the largest gains on cluttered indoor scenes.

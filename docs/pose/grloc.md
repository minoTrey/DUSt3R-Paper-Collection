# GRLoc: Geometric Representation Regression for Visual Localization (arXiv preprint (2025-11))

## 📋 Overview

- **Authors**: Changyang Li, Xuejian Ma, Lixiang Liu, Zhan Li, Qingan Yan, Yi Xu
- **Institution**: Goertek Alpha Labs
- **Venue**: arXiv preprint (2025-11)
- **Links**: [Paper](https://arxiv.org/abs/2511.13864)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: GRLoc reformulates Absolute Pose Regression as an inverse-rendering task — Geometric Representation Regression (GRR) — predicting a per-patch raymap (for rotation) and pointmap (for translation) in world coordinates, then recovering the 6-DoF pose with a differentiable Kabsch solver; decoupling rotation and translation into separate branches is the key to its accuracy.

## 🎯 Key Contributions

1. **Pose estimation as inverse rendering**: Instead of the black-box image→pose mapping of APR, GRR does image→geometry→pose, decomposing into a learned perception step and an analytical solving step.
2. **Disentangled geometric representations**: A raymap of view directions estimates camera rotation, and a pointmap (constrained to unit distance from the camera, removing scale ambiguity) estimates translation.
3. **Decoupled dual-branch design**: Separate ray and point branches prevent the competing objectives of rotation (translation-invariant global cues) and translation (parallax-sensitive local cues) from degrading shared features — shown to be critical.
4. **State-of-the-art APR results**: On 7-Scenes and Cambridge Landmarks, with an optional refinement variant (GRLoc_ref) competitive with top PPR methods.

## 🔧 Technical Details

### Representations & Solver

The image is split into an N×N grid (empirically 16×16). Each patch predicts a unit ray direction d̂ᵢ ∈ S² (world coordinates) and a 3D point p̂ᵢ constrained to lie on d̂ᵢ at unit distance from the camera. The pose T = (R, t) minimizes a joint rotation-alignment (rays) + rigid-registration (points) error, both solved in closed form via the Kabsch algorithm (SVD-based, fully differentiable). Rotation is taken from the ray-alignment; translation from the point-alignment.

### Architecture

A decoupled dual-branch network: each branch has a Swin Transformer V2-large backbone (ImageNet-pretrained) plus a fusion neck (1×1 convs, resize, concat to N×N) producing a spatial feature for the prediction head and a global feature for a domain classifier. Lightweight MLP heads regress the ray field and pointmap.

### Training

3DGS (gsplat, 3DGS-MCMC) renders synthetic novel views offline to expand scene coverage; domain-adversarial adaptation with a Gradient Reversal Layer aligns synthetic and real domains. The composite loss combines pose supervision (geodesic rotation + translation), geometry supervision (cosine ray + point distance), geometric regularization (angular + rigidity), and domain BCE loss. A warmup phase uses p=1 norm, switching to p=2.

## 📊 Results

Metrics: median translation error (cm) / rotation error (°), lower is better. GRLoc is categorized with APR; GRLoc_ref adds the optional RAP-style refinement.

### 7-Scenes

원논문 Table 1 (대표 행 발췌; cell = 이동오차 cm / 회전오차 °).

| Method                | Chess     | Fire      | Heads     | Office    | Pumpkin   | Kitchen   | Stairs    | Average       |
| --------------------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | ------------- |
| PoseNet (APR)         | 10/4.02   | 27/10.00  | 18/13.00  | 17/5.97   | 19/4.67   | 22/5.91   | 35/10.50  | 21/7.74       |
| MS-Transformer (APR)  | 11/6.38   | 23/11.5   | 13/13.0   | 18/8.14   | 17/8.42   | 16/8.92   | 29/10.30  | 18/9.51       |
| DFNet (APR)           | 3/1.12    | 6/2.30    | 4/2.29    | 6/1.54    | 7/1.92    | 7/1.74    | 12/2.63   | 6/1.93        |
| RAP (APR)             | 2/0.85    | 6/2.84    | 4/4.52    | 4/1.57    | 3/1.10    | 5/1.10    | 10/1.30   | 5/1.90        |
| Marepo (APR)          | 1.9/0.83  | 2.3/0.92  | 2.1/1.24  | 2.9/0.93  | 2.5/0.88  | 2.9/0.98  | 5.9/1.48  | 2.9/1.04      |
| **GRLoc (ours, GRR)** | 0.97/0.31 | 2.93/0.95 | 1.40/0.90 | 5.08/1.05 | 2.28/0.53 | 3.13/0.69 | 3.42/0.82 | **2.75/0.75** |
| ACE (SCR)             | 0.5/0.18  | 0.8/0.33  | 0.6/0.34  | 1.0/0.29  | 1.0/0.22  | 0.8/0.20  | 2.9/0.81  | 1.1/0.34      |
| STDLoc (PPR)          | 0.46/0.15 | 0.57/0.24 | 0.45/0.26 | 0.86/0.24 | 0.93/0.21 | 0.63/0.19 | 1.42/0.41 | 0.76/0.24     |
| RAP_ref (PPR)         | 0.33/0.11 | 0.51/0.21 | 0.39/0.27 | 0.57/0.16 | 0.81/0.20 | 0.45/0.12 | 1.11/0.32 | 0.60/0.20     |
| **GRLoc_ref (ours)**  | 0.28/0.10 | 0.32/0.13 | 0.22/0.14 | 0.65/0.15 | 0.70/0.15 | 0.35/0.10 | 0.61/0.19 | **0.45/0.14** |

Among APR/GRR methods GRLoc has the best average (2.75/0.75), beating Marepo on average and in 5 of 7 scenes — but Marepo is better on Fire (2.3 vs. 2.93 cm) and Office (2.9 vs. 5.08 cm). Refined, GRLoc_ref (0.45/0.14) surpasses RAP_ref and STDLoc on 7-Scenes.

### Cambridge Landmarks

원논문 Table 2 (대표 행 발췌; cell = cm / °).

| Method                | College   | Hospital  | Shop     | Church   | Average     | Court     |
| --------------------- | --------- | --------- | -------- | -------- | ----------- | --------- |
| RAP (APR)             | 52/0.90   | 87/1.21   | 33/1.48  | 53/1.52  | 56/1.28     | 115/1.68  |
| **GRLoc (ours, GRR)** | 34/0.42   | 54/0.88   | 15/0.48  | 46/0.93  | **37/0.68** | 88/0.53   |
| STDLoc (PPR)          | 15.0/0.17 | 11.9/0.21 | 3.0/0.13 | 4.7/0.14 | 10.1/0.14   | 15.7/0.06 |
| RAP_ref (PPR)         | 15/0.23   | 18/0.38   | 5/0.23   | 9/0.23   | 12/0.27     | 22/0.15   |
| **GRLoc_ref (ours)**  | 16/0.21   | 16/0.35   | 5/0.20   | 8/0.23   | 11/0.25     | 21/0.11   |

Against APR baselines GRLoc cuts average translation error ~33% and rotation error ~46% (vs. RAP) and handles the large-scale Court scene often omitted by prior APR work. Refined, GRLoc_ref (11/0.25) beats RAP_ref but is slightly worse than STDLoc (10.1/0.14) on Cambridge — attributed to the difficulty of training high-fidelity NVS in large outdoor scenes.

### Ablation on the Shop Scene

원논문 Table 3. cell = 이동오차 cm / 회전오차 °.

| Variant                          | Trans (cm)↓ | Rot (°)↓ |
| -------------------------------- | ----------- | -------- |
| ViT backbone                     | 29          | 0.98     |
| W/o Domain Adaptation            | 33          | 1.25     |
| APR (pose-only)                  | 39          | 1.67     |
| GR-only (no pose loss)           | 20          | 3.96     |
| W/o point (ray-only + MLP trans) | 41          | 0.66     |
| W/o ray (point-only)             | 15          | 0.86     |
| Share (shared backbone)          | 17          | 0.77     |
| GRLoc (full)                     | 15          | 0.48     |

### Inference Latency

원논문 4.3절. Batch size 1, single H200.

| Method       | Latency  |
| ------------ | -------- |
| RAP          | 12.84 ms |
| GRLoc (ours) | 36.78 ms |
| Marepo       | 68.50 ms |

## 💡 Insights & Impact

- **Decoupling resolves competing objectives**: The ray-only variant has good rotation but no translation basis; the point-only variant has good translation but worse rotation (0.86° vs. 0.48°); sharing a backbone is a poor compromise. Fully decoupled branches give the best result (15 cm / 0.48°).
- **Pairing geometry with pose loss is best**: Pure pose supervision (APR, 39/1.67) and pure geometric supervision (GR-only, 20/3.96) both underperform the full model, which combines both.
- **Domain adaptation is necessary**: Removing it degrades the Shop scene from 15/0.48 to 33/1.25, confirming synthetic-to-real alignment matters.
- **Honest limits**: GRLoc still trails SCR/PPR methods (ACE, STDLoc) in absolute accuracy without refinement; refined, it loses to STDLoc on Cambridge; and its Swin backbone makes it slower (36.78 ms) than lightweight RAP (12.84 ms).

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: The pointmap-regression paradigm GRLoc's geometric representations echo, applied here to single-image localization.
- **[Reloc3r](reloc3r.md)**: A relative-pose-regression baseline compared on both 7-Scenes and Cambridge.

## 📚 Key Takeaways

1. GRLoc reframes absolute pose regression as inverse rendering: predict a raymap (rotation) and pointmap (translation), then recover pose with a differentiable Kabsch solver.
2. Decoupling rotation and translation at both the representation and architecture levels is the paper's central, ablation-validated finding.
3. It sets state-of-the-art among APR/GRR methods on 7-Scenes and Cambridge Landmarks and, with optional refinement, rivals top PPR methods — while candidly trailing SCR/PPR pipelines in some settings and running heavier than lightweight APR baselines.

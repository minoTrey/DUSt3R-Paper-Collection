# Free Geometry: Refining 3D Reconstruction from Longer Versions of Itself (arXiv preprint (2026-04))

## 📋 Overview

- **Authors**: Yuhang Dai, Xingyi Yang
- **Institution**: The Hong Kong Polytechnic University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.14048) | [Code](https://github.com/hiteacherIamhumble/Free-Geometry)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A test-time adaptation framework that exploits a "more-views-better" regime: full-view predictions supervise masked-view predictions at the encoder feature level, recalibrating feed-forward reconstruction models (Depth Anything 3, VGGT) via lightweight LoRA updates in under two minutes per dataset without any 3D ground truth.

## 🎯 Key Contributions

1. **"Longer is better" as free supervision**: Identifies that feed-forward multi-view models produce more reliable geometry with more views, providing a label-free self-supervision signal (full view teaches masked view).
2. **Feature-level distillation**: Applies supervision to backbone encoder features (where cross-view reasoning happens) rather than per-view decoder outputs, making adaptation stable and efficient.
3. **Fast LoRA recalibration**: Optimizes only LoRA adapters and camera tokens in the multi-view transformer (< 0.2% of parameters), under two minutes per dataset on a single GPU.
4. **Cross-view-count generalization**: Adapting with an 8→4 consistency signal improves reconstruction and pose across 4, 8, 16, and 32 input views.

## 🔧 Technical Details

### Teacher–Student Distillation

- Teacher: all N frames through a frozen backbone → features Ffull. Student: M unmasked frames through the same backbone + LoRA → Fpartial. Default N = 8 views, M = 4 even-indexed unmasked views.
- Two losses: (1) **Intra-frame consistency** — Huber + (1 − cosine) alignment of matched teacher/student tokens on unmasked frames; (2) **Cross-frame relational** — KL over pairwise similarity distributions plus L1 on triangle cosine angles Φ(p,k,q), using K = 4 masked-frame anchors (two most similar, two least similar) per reference patch.

### Training

- LoRA rank r = 32, scaling α = 32; AdamW, weight decay 1e-5, cosine schedule with 15% warmup, 5 epochs (dataset-specific per-scene sample counts and learning rates), FP16. ~2 minutes per dataset on a single RTX Pro 6000 GPU.
- Evaluated on ETH3D, ScanNet++, 7Scenes, HiRoom over 3 seeds (43/44/45); pose via AUC@3/AUC@30, reconstruction via F1/Chamfer distance using evo alignment.

## 📊 Results

### Longer Sequence → Better Reconstruction

원논문 Table 1. AUC@3↑, F1↑. 8→4는 8뷰로 인코더 특징을 계산하고 4뷰만 디코더로 전달.

| # Views | ETH3D AUC@3 | ETH3D F1 | 7-Scenes AUC@3 | 7-Scenes F1 | ScanNet++ AUC@3 | ScanNet++ F1 | HiRoom AUC@3 | HiRoom F1 |
| ------- | ----------- | -------- | -------------- | ----------- | --------------- | ------------ | ------------ | --------- |
| 8       | 0.445       | 0.536    | 0.315          | 0.439       | 0.733           | 0.436        | 0.827        | 0.787     |
| 8→4     | 0.424       | 0.188    | 0.302          | 0.285       | 0.747           | 0.306        | 0.857        | 0.682     |
| 4       | 0.318       | 0.142    | 0.254          | 0.239       | 0.586           | 0.231        | 0.700        | 0.561     |

### 3D Reconstruction Comparison (mean over 3 seeds)

원논문 Table 2. AUC3↑, F1↑. 각 method 쌍 내 더 나은 값을 bold.

| #View | Method        | ETH3D AUC3 | ETH3D F1 | ScanNet++ AUC3 | ScanNet++ F1 | 7Sc AUC3 | 7Sc F1 | HiRoom AUC3 | HiRoom F1 |
| ----- | ------------- | ---------- | -------- | -------------- | ------------ | -------- | ------ | ----------- | --------- |
| 4     | VGGT          | 0.157      | 0.102    | 0.408          | 0.171        | 0.238    | 0.196  | 0.421       | 0.276     |
| 4     | VGGT+Free Geo | 0.178      | 0.110    | 0.419          | 0.174        | 0.241    | 0.197  | 0.441       | 0.307     |
| 4     | DA3           | 0.286      | 0.207    | 0.620          | 0.236        | 0.280    | 0.244  | 0.708       | 0.557     |
| 4     | DA3+Free Geo  | 0.305      | 0.209    | 0.624          | 0.239        | 0.302    | 0.248  | 0.719       | 0.578     |
| 8     | VGGT          | 0.207      | 0.301    | 0.496          | 0.326        | 0.252    | 0.329  | 0.516       | 0.502     |
| 8     | VGGT+Free Geo | 0.209      | 0.327    | 0.501          | 0.330        | 0.250    | 0.331  | 0.537       | 0.528     |
| 8     | DA3           | 0.408      | 0.495    | 0.722          | 0.411        | 0.316    | 0.392  | 0.792       | 0.777     |
| 8     | DA3+Free Geo  | 0.439      | 0.500    | 0.723          | 0.411        | 0.317    | 0.385  | 0.800       | 0.781     |

Note: on ScanNet++ (where frozen baselines already perform strongly) and on some 8-view cells (e.g., VGGT 7-Scenes AUC3 0.252→0.250, DA3 7-Scenes/HiRoom F1), Free Geometry gives negligible or slightly negative changes.

### Cross-View-Count Relative Improvement (%)

원논문 Table 3. Free Geo의 baseline 대비 상대 변화, seeds 43/44/45 및 4개 데이터셋 평균.

| #View | VGGT AUC3 | VGGT AUC30 | VGGT F1 | VGGT CD | DA3 AUC3 | DA3 AUC30 | DA3 F1 | DA3 CD |
| ----- | --------- | ---------- | ------- | ------- | -------- | --------- | ------ | ------ |
| 4     | +5.33%    | +4.73%     | +4.51%  | -8.15%  | +2.74%   | +1.03%    | +2.85% | -4.03% |
| 8     | +2.19%    | +1.35%     | +4.32%  | -3.53%  | +1.82%   | +0.57%    | +0.21% | -0.35% |
| 16    | +3.93%    | +1.33%     | +3.03%  | -5.35%  | +2.61%   | +0.89%    | +0.70% | -7.67% |
| 32    | +3.73%    | +1.03%     | +2.88%  | -4.34%  | +2.89%   | +0.94%    | +0.78% | -8.73% |

The headline "3.73% pose / 2.88% point map" figures are the VGGT 32-view AUC3 and F1 relative gains.

### Loss Ablation on ETH3D (N=4)

원논문 Table 4. 이 표의 AUC는 백분율 스케일로 표기됨.

| Configuration        | AUC3 ↑    | AUC30 ↑   | F1 ↑       | CD ↓       |
| -------------------- | --------- | --------- | ---------- | ---------- |
| w/o Consistency Loss | 35.87     | 72.12     | 0.2324     | 3.6976     |
| w/o Relational Loss  | 36.37     | 72.22     | 0.2190     | 3.9567     |
| Full Loss (Free Geo) | **37.88** | **72.32** | **0.2475** | **3.5473** |

## 💡 Insights & Impact

- **Architecture-guaranteed supervision**: Because cross-view reasoning lives in the backbone (decoders are per-view), full-observation features are a strictly stronger teacher than symmetric consistency (contrasted with Test3R), directly addressing the representation bottleneck.
- **Biggest gains where views are scarce**: Improvements peak at 4 views and saturate as N grows, matching the intuition that more views already supply strong geometric constraints.
- **Both losses needed**: Dropping the relational term lowers F1 (0.2475 → 0.2190); dropping consistency lowers pose AUC — they act synergistically.
- **Feature-distance verification**: Adaptation lowers MSE and raises cosine similarity of student features toward full-observation features (Table 5), confirming feature-level recalibration.

## 🔗 Related Work

- **[Depth Anything 3](depth-anything-3.md)** and **[VGGT](vggt.md)**: The two frozen feed-forward backbones adapted.
- **[DUSt3R](../foundation/dust3r.md)**: Cited pointmap-regression predecessor.
- **[Test3R](test3r.md)**: Prior 3D test-time adaptation via symmetric pairwise consistency, contrasted with the asymmetric full-vs-partial signal.

## 📚 Key Takeaways

1. Free Geometry turns the "more-views-better" property into a label-free test-time supervision signal, distilling full-view encoder features into masked-view predictions.
2. Lightweight LoRA adaptation (plus trainable camera tokens) recalibrates the backbone in under two minutes per dataset with no 3D ground truth.
3. It consistently improves pose and reconstruction for VGGT and DA3, most in sparse-view regimes, and the calibration transfers across 4–32 input views, though gains are small where frozen baselines are already strong.

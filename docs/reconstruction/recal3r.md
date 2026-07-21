# ReCal3R: Reliability-Calibrated Learning Rates for Streaming 3D Reconstruction (arXiv preprint (2026-07))

## 📋 Overview

- **Authors**: Xinze Li, Yiyuan Wang, Pengxu Chen, Weifeng Su, Weisi Lin, Wentao Cheng
- **Institution**: Beijing Normal-Hong Kong Baptist University; Hong Kong Baptist University; Jilin University; Guangdong Provincial Key Laboratory of Interdisciplinary Research and Application for Data Science; Nanyang Technological University
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.05356) | [Code](https://github.com/Powertony102/ReCal3R)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free calibration rule for recurrent streaming reconstruction that estimates state-token reliability and interpolates a candidate learning rate toward a conservative base rate, protecting unreliable tokens from aggressive updates; applied to CUT3R it cuts ATE by 3.7× on 1000-frame ScanNet.

## 🎯 Key Contributions

1. **Reliability gap diagnosis**: Existing adaptive updates (e.g., TTT3R) are driven by the incoming observation but never assess whether the state token being updated is still a reliable carrier of historical geometry.
2. **Reliability-calibrated learning rate**: ReCal3R interpolates between a conservative base rate and a candidate rate according to per-token reliability, so reliable tokens adapt while unreliable ones are protected.
3. **Training-free, closed-form**: The mechanism requires no training and applies directly on top of CUT3R without modifying the recurrent architecture, preserving linear-time and bounded-memory streaming.

## 🔧 Technical Details

### Reliability-Calibrated Update

The final per-token learning rate is β_t = (1 − R_t)·β_base + R_t ⊙ β̃_t, where β_base is a small conservative rate, β̃_t the uncalibrated candidate rate, and R_t the state-token reliability. Substituting into the TTT-style update S_t = S_{t−1} − β_t ⊙ ∇(S_{t−1}, X_t) yields the ReCal3R update.

### State Token Reliability

Reliability combines two normalized cues: accumulated state deviation d (departure of a token from its learned initialization) and attention entropy e (ambiguity of the token-frame relation). An agreement-based pooling ρ = (1−d)(1−e) / [(1−d)(1−e) + de] is high only when the token is both stable and clearly associated with the current frame, then confidence-calibrated as R = ρ(2ρ−1)². An appendix derives ρ and R from a single Bernoulli latent-variable model.

### Uncalibrated Learning Rate

β̃_t = r_t · g_t ⊙ ϕ(h_t), where g_t is TTT3R's alignment gate, r_t a state-reconstruction residual score (grows when the frame carries content the state cannot predict), and h_t a recent-update-pressure EMA (decay λ = 0.95, effective window ~20 frames) attenuated by ϕ(x) = exp(−x).

### Evaluation

Official pretrained weights, CUT3R input resolution/preprocessing; runtime and peak memory on a single NVIDIA RTX PRO 6000 (96 GB). Baselines: CUT3R, TTT3R, MeMix (TTT3R-based variant), TTSA3R.

## 📊 Results

Pose on TUM-Dynamics and ScanNet; 3D reconstruction on 7-Scenes and NRGBD; video depth on Bonn and TUM-Dynamics. Pose/depth curves (Figs. 2, 4) are not printed as tables.

### 3D Reconstruction — 700 Frames

원논문 Table 1. Acc/Comp lower is better, NC higher is better (700-frame column).

| Method  | 7-Scenes Acc↓ | Comp↓     | NC↑       | NRGBD Acc↓ | Comp↓     | NC↑       |
| ------- | ------------- | --------- | --------- | ---------- | --------- | --------- |
| CUT3R   | 0.210         | 0.130     | 0.539     | 0.388      | 0.233     | 0.550     |
| TTT3R   | 0.099         | 0.051     | 0.570     | 0.197      | 0.073     | 0.608     |
| MeMix   | 0.090         | 0.044     | 0.574     | 0.160      | 0.055     | 0.614     |
| TTSA3R  | 0.069         | 0.035     | 0.588     | 0.123      | 0.043     | 0.644     |
| ReCal3R | **0.034**     | **0.028** | **0.608** | **0.093**  | **0.031** | **0.658** |

ReCal3R's advantage grows with sequence length. On NRGBD, MeMix attains the best accuracy at the shortest length (300 frames, 0.063), but ReCal3R becomes strongest from 400 to 700 frames.

### Pose Ablation — 1000 Frames

원논문 Table 2. ATE↓ on ScanNet and TUM-Dynamics.

| Method                  | ScanNet    | TUM-D      |
| ----------------------- | ---------- | ---------- |
| CUT3R                   | 0.7865     | 0.3330     |
| TTT3R                   | 0.4230     | 0.1599     |
| ReCal3R w/ TTT3R rate   | 0.2431     | 0.1152     |
| ReCal3R w/o reliability | 0.2502     | 0.1169     |
| ReCal3R                 | **0.2106** | **0.0769** |

Reliability calibration helps even when the candidate rate is inherited from TTT3R, and the uncalibrated rate alone already beats TTT3R; combined they are best. ReCal3R reduces ATE from CUT3R's 0.7865 to 0.2106 on 1000-frame ScanNet — a 3.7× reduction.

## 💡 Insights & Impact

- **Who receives the update matters**: The core idea is that a candidate learning rate should not be applied by default; it should be discounted according to the reliability of the state token receiving it.
- **Two failure modes**: A token becomes unreliable either by accumulating large deviation from its initialization or by having diffuse (ambiguous) attention to the current frame — the two cues ReCal3R fuses.
- **Balanced trade-off**: ReCal3R does not dominate every entry; on short streams it is comparable to its variants, and its default trades slightly lower long-stream ATE for stable cross-length behavior.
- **Limitations**: Conservative updates can occasionally reduce fine frame-level details even while improving overall long-stream consistency; extending reliability calibration beyond compact recurrent states is future work.

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The recurrent-state base model ReCal3R calibrates without modifying its architecture.
- **[TTT3R](ttt3r.md)**: The alignment-based learning-rate rule whose gate ReCal3R reuses and extends.
- **[Spann3R](spann3r.md)** & **[Point3R](point3r.md)**: Persistent/pointer-memory streaming methods.
- **[StreamVGGT](streamvggt.md)**, **[Stream3R](stream3r.md)**, **[InfiniteVGGT](infinitevggt.md)**, **[HorizonStream](horizonstream.md)**: Causal VGGT-style streaming systems with cache management.
- **[VGG-T3](vgg-t3.md)** & **[ZipMap](zipmap.md)**: TTT-based approaches that scale feed-forward reconstruction rather than modifying recurrent updates.
- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)**, **[VGGT](vggt.md)**, **[Fast3R](fast3r.md)**, **[MonST3R](../dynamic/monst3r.md)**: Feed-forward foundations referenced.

## 📚 Key Takeaways

1. ReCal3R adds a training-free, closed-form reliability calibration on top of CUT3R's recurrent state update, protecting degraded tokens from aggressive writes.
2. Reliability fuses accumulated state deviation and attention entropy; the candidate rate fuses alignment, state-reconstruction residual, and recent update pressure.
3. It cuts ATE by 3.7× over CUT3R on 1000-frame ScanNet and leads reconstruction/depth on long streams while preserving runtime and memory.
4. Gains are strongest on long sequences; on short streams it is comparable to its ablated variants.

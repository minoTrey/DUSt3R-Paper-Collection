# VGGT4D: Mining Motion Cues in Visual Geometry Transformers for 4D Scene Reconstruction (CVPR 2026)

![vggt4d — architecture](https://arxiv.org/html/2511.19971/x2.png)

_Overview of VGGT4D (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Yu Hu, Chong Cheng, Sicheng Yu, Xiaoyang Guo, Hao Wang
- **Institution**: The Hong Kong University of Science and Technology (Guangzhou), Horizon Robotics
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2511.19971) | [Project Page](https://3dagentworld.github.io/vggt4d/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A **training-free** extension of VGGT to dynamic scenes: dynamic masks are mined from Gram similarities (QQ^T, KK^T) of VGGT's own global attention, sharpened by projection-gradient refinement, and injected into layers 1–5 of inference to keep motion from corrupting geometry.

## 🎯 Key Contributions

1. **Training-free 4D perception for VGGT**: motion cues latent in VGGT's global attention are mined to give a static-trained 3D foundation model 4D capability, with no additional training and no external segmentation module.
2. **Gram-similarity dynamic cue extraction**: instead of the standard `QK^T` attention map, the method computes the self-similarity matrices `QQ^T` and `KK^T`, which the paper argues amplify the distributional discrepancy caused by motion that `QK^T` mixes with texture and semantics.
3. **Layer-band decomposition**: shallow, middle, and deep layer statistics are shown to carry _different_ signals — semantic saliency, motion instability, and a spatial outlier-suppression prior respectively — and are combined multiplicatively.
4. **Projection-gradient mask refinement**: 3D points from dynamic objects incur large geometric and photometric residuals when projected into other views' static regions; the gradient of that residual sharpens mask boundaries.
5. **Early-stage selective masking**: masks are applied only to layers 1–5 by suppressing the K vectors of dynamic tokens. The paper shows masking _all_ layers is worse than masking none.
6. **500+ frame single-pass inference**, achieved by building on FastVGGT's observation that prediction heads consume tokens only from layers (5, 12, 18, 24).

## 🔧 Technical Details

### Empirical starting point

Visualizing camera-token → image-token attention `A^{QK}` shows shallow layers respond strongly to semantically dynamic objects (people) while deeper layers gradually suppress geometrically inconsistent pixels. But the paper reports this is **highly scene-dependent and unreliable** — appendix Figure 9 shows that at layer 18 the camera token can fail to suppress a moving actor entirely. This motivates looking past camera-token attention.

### Gram similarities

Standard attention is `A^{QK}_{l,t,s} = Q_{l,t} K_{l,s}^T / √c`. VGGT4D adds:

```text
A^{QQ}_{l,t,s} = Q_{l,t} Q_{l,s}^T / √c
A^{KK}_{l,t,s} = K_{l,t} K_{l,s}^T / √c
```

These are aggregated over an inter-frame sliding window `W(t) = {t−n, …, t−1, t+1, …, t+n}` and over three layer bands, taking mean `S` and variance `V`:

```text
S^X_{i–j} = Mean_s( (1/|W(t)|) Σ_{s∈W(t)} (1/L) Σ_{l=i}^{j} A^X_{l,t,s} )
V^X_{i–j} = Var_s ( … same … ),    X ∈ {QQ, QK, KK}
```

### The saliency map

```text
Dyn = w_shallow ⊙ w_middle ⊙ w_deep

w_shallow = (1 − S^{KK}_shallow) ⊙ V^{QK}_shallow      # semantic saliency
w_middle  = 1 − S^{QQ}_middle                          # motion instability
w_deep    = (1 − V^{QQ}_deep) ⊙ S^{QQ}_deep            # spatial outlier prior
```

The per-frame mask is `M_t = [Dyn > α]`, refined with feature clustering. The threshold α is not hand-set: VGGT's ViT features are k-means clustered across frames, each cluster's dynamic score is checked, and **Otsu's algorithm** picks the separation threshold.

### Projection-gradient refinement

For a 3D point projected into view `i`:

```text
L_proj = ½ ‖ I_i (1 − M_i) r_{d,i} ‖²
```

with `r_{d,i} = d_i − D_i(u_i, v_i)` the depth residual, `M_i` the initial dynamic mask, `I_i` the visibility mask. The gradient `∇r_{d,i}` (which depends on projection Jacobians and the target depth map's spatial gradient) is aggregated over all N views:

```text
agg_proj  = (1/N) Σ_i w_i r_{d,i} ∇r_{d,i},   w_i = I_i(1 − M_i)
agg_photo = (1/N) Σ_i w_i ( c − C_i(u_i, v_i) )
```

The photometric term exists because depth gradients are uninformative in textureless regions (flat walls, floors). Before this stage, Statistical Outlier Removal filters floaters and gradients are averaged within point clusters so isolated outliers cannot trigger false dynamic classifications.

### Memory

Materializing the full `QK^T` Gram matrix is O(N²) in token count and would OOM on multi-view input with thousands of tokens. VGGT4D computes per-frame Gram similarities **in-place within the attention layer**, keeping memory linear in the number of frames.

### Inference intervention

Masks are applied only to **layers 1–5**, suppressing the K vectors of dynamic tokens so queries cannot attend to dynamic regions early. Deeper layers then operate within their trained distribution. All experiments run on a single NVIDIA A6000.

## 📊 Results

### Dynamic object segmentation on DAVIS

원논문 Table 1. JM/FM은 IoU와 Boundary F-measure의 시퀀스 평균, JR/FR은 각 지표가 0.5를 넘으면 성공으로 보는 mean recall이다. Easi3R의 아래첨자는 백본을 뜻한다.

| Method         | DAVIS-2016 JM ↑ | JR ↑      | FM ↑      | FR ↑      |
| -------------- | --------------- | --------- | --------- | --------- |
| Easi3R_dust3r  | 50.10           | 55.77     | 43.40     | 37.25     |
| Easi3R_monst3r | 54.93           | 68.00     | 45.29     | 47.30     |
| MonST3R        | 40.42           | 40.39     | 49.54     | 52.12     |
| DAS3R          | 41.13           | 38.67     | 44.50     | 36.94     |
| **Ours**       | **62.12**       | **76.80** | **56.04** | **67.49** |

원논문 Table 1 (계속) — DAVIS-2017·DAVIS-all.

| Method         | 2017 JM ↑ | JR ↑      | FM ↑      | FR ↑      | all JM ↑  | JR ↑      | FM ↑      | FR ↑      |
| -------------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| Easi3R_dust3r  | 46.86     | 50.54     | 39.06     | 30.05     | 44.10     | 50.85     | 35.16     | 27.24     |
| Easi3R_monst3r | 54.75     | **66.16** | 44.09     | 42.36     | 51.64     | **63.06** | 40.98     | 38.49     |
| MonST3R        | 38.07     | 36.05     | 48.24     | 49.01     | 36.98     | 34.52     | 47.03     | **46.72** |
| DAS3R          | 44.51     | 43.95     | 46.71     | 44.96     | 43.33     | 38.93     | 45.24     | 38.78     |
| **Ours**       | **56.45** | 65.62     | **51.09** | **56.85** | **50.75** | 55.59     | **47.04** | 46.43     |

**Losses shown honestly**: on DAVIS-2017 Easi3R_monst3r has higher JR (66.16 vs 65.62); on DAVIS-all Easi3R_monst3r leads JM (51.64 vs 50.75) and JR (63.06 vs 55.59), and MonST3R leads FR (46.72 vs 46.43). The paper attributes Easi3R_monst3r's DAVIS-all recall to MonST3R's post-training on optical flow, whereas VGGT4D is training-free.

### Camera pose estimation

원논문 Table 2.

| Method           | Sintel ATE ↓ | RTE ↓     | RRE ↓     | TUM-Dyn ATE ↓ | RTE ↓     | RRE ↓     | VKITTI ATE ↓ | RTE ↓     | RRE ↓     |
| ---------------- | ------------ | --------- | --------- | ------------- | --------- | --------- | ------------ | --------- | --------- |
| Easi3R_dust3r    | 0.372        | 0.227     | 10.356    | 0.063         | 0.046     | 2.523     | 2.789        | 0.506     | 0.108     |
| Easi3R_monst3r   | 0.109        | 0.051     | 0.277     | 0.133         | 0.120     | 4.366     | 2.036        | 0.173     | 0.124     |
| MonST3R          | 0.151        | **0.034** | 0.258     | 0.156         | 0.103     | 12.041    | 2.272        | 0.180     | 0.091     |
| POMATO           | 0.557        | 0.158     | 0.878     | 0.153         | 0.097     | 11.102    | 1.377        | 0.232     | 0.119     |
| SpatialTrackerV2 | **0.073**    | 0.035     | 0.340     | 0.054         | 0.041     | 2.530     | 0.720        | 0.160     | 0.127     |
| DAS3R            | 0.125        | **0.030** | **0.185** | 0.155         | 0.102     | 12.038    | 2.043        | 0.169     | 0.114     |
| CUT3R            | 0.152        | 0.077     | 0.454     | 0.054         | 0.041     | 5.346     | 5.583        | 0.381     | 0.174     |
| VGGT             | 0.081        | 0.045     | 0.287     | 0.017         | 0.020     | 0.617     | 0.170        | 0.065     | 0.062     |
| **Ours**         | 0.076        | 0.043     | 0.273     | **0.016**     | **0.020** | **0.612** | **0.164**    | **0.064** | **0.062** |

**On Sintel, VGGT4D does not win**: SpatialTrackerV2 has the best ATE (0.073 vs 0.076), and DAS3R the best RTE/RRE (0.030 / 0.185). The paper's claim is scoped correctly — SOTA on TUM-Dynamics and VKITTI, and a consistent improvement over the VGGT baseline everywhere.

### Long-sequence pose estimation on Point Odyssey (500 frames)

원논문 Table 3. '–'는 OOM으로 실패한 경우다.

| Method           | ATE ↓     | RTE ↓     | RRE ↓     |
| ---------------- | --------- | --------- | --------- |
| Easi3R_dust3r    | -         | -         | -         |
| Easi3R_monst3r   | -         | -         | -         |
| MonST3R          | -         | -         | -         |
| POMATO           | -         | -         | -         |
| DAS3R            | -         | -         | -         |
| SpatialTrackerV2 | -         | -         | -         |
| CUT3R            | 0.417     | 0.028     | 0.605     |
| FastVGGT         | 0.026     | 0.017     | 0.380     |
| VGGT             | 0.022     | 0.015     | 0.344     |
| **Ours**         | **0.019** | **0.009** | **0.290** |

Six of the nine specialized 4D baselines run out of memory at 500 frames. This is the clearest argument for the approach: the 4D capability is added _on top of_ a backbone that already scales.

### 4D reconstruction on DyCheck

원논문 Table 4. Accuracy/Completeness/Distance는 모두 거리 기반 지표다.

| Method           | ATE ↓     | RTE ↓     | RRE ↓     | Acc. Mean ↓ | Acc. Median ↓ | Comp. Mean ↓ | Comp. Median ↓ | Dist. Mean ↓ | Dist. Median ↓ |
| ---------------- | --------- | --------- | --------- | ----------- | ------------- | ------------ | -------------- | ------------ | -------------- |
| Easi3R_dust3r    | 0.022     | 0.009     | 0.806     | 0.070       | 0.044         | 0.060        | 0.033          | 0.194        | 0.132          |
| Easi3R_monst3r   | 0.032     | 0.008     | 1.075     | 0.100       | 0.050         | 0.121        | 0.082          | 0.289        | 0.270          |
| MonST3R          | 0.038     | 0.010     | 1.172     | 0.090       | 0.033         | 0.113        | 0.064          | 0.279        | 0.234          |
| POMATO           | 0.128     | 0.027     | 3.648     | 0.960       | 0.950         | 0.814        | 0.776          | 1.484        | 1.434          |
| SpatialTrackerV2 | 0.011     | **0.006** | 0.347     | 0.115       | 0.064         | 0.052        | 0.026          | 0.421        | 0.304          |
| DAS3R            | 0.052     | 0.012     | 1.560     | 0.192       | 0.142         | 0.250        | 0.108          | 0.428        | 0.336          |
| CUT3R            | 0.036     | 0.013     | 0.860     | 0.073       | 0.054         | 0.133        | 0.049          | 0.328        | 0.224          |
| VGGT             | 0.013     | 0.008     | 0.418     | 0.028       | 0.009         | 0.063        | 0.019          | 0.150        | 0.055          |
| **Ours**         | **0.010** | 0.007     | **0.374** | **0.022**   | **0.004**     | **0.051**    | **0.012**      | **0.123**    | **0.050**      |

SpatialTrackerV2 keeps the best RTE (0.006) but its reconstruction quality is poor (Acc. Mean 0.115 vs 0.022) — the paper's stated point is doing both well simultaneously. Over the VGGT baseline, median Accuracy drops 0.009 → 0.004 and mean Distance 0.150 → 0.123.

### Ablation: mask estimation

원논문 Table 5. DAVIS-2016 기준 일부만 옮긴다.

| Method      | JM ↑      | JR ↑      | FM ↑      | FR ↑      |
| ----------- | --------- | --------- | --------- | --------- |
| Easi3R_vggt | 7.51      | 0.12      | 12.78     | 0.00      |
| w/o refine  | 59.74     | 73.10     | 50.64     | 58.30     |
| **Ours**    | **62.12** | **76.80** | **56.04** | **67.49** |

**Easi3R's epipolar logic transplanted onto VGGT collapses to 7.51 JM / 0.12 JR** — near-total failure. This is the paper's evidence that training-free 4D methods are tightly coupled to their backbone, and that a new cue was actually necessary rather than a convenience. Gram-similarity mining alone already reaches 59.74 JM; refinement adds 2.4.

### Ablation: saliency components

원논문 Table 8. "w/o" 변형은 cue extraction의 영향을 분리하기 위해 refinement 이전 단계에서 평가한다. DAVIS-2016.

| Method         | JM ↑      | JR ↑      | FM ↑      | FR ↑      |
| -------------- | --------- | --------- | --------- | --------- |
| w/o w_shallow  | 54.15     | 62.44     | 46.43     | 44.27     |
| w/o w_middle   | 56.13     | 57.12     | 44.07     | 41.90     |
| w/o w_deep     | 46.85     | 48.89     | 41.52     | 45.30     |
| w/o refinement | 59.74     | 73.10     | 50.64     | 58.30     |
| **Ours**       | **62.12** | **76.80** | **56.04** | **67.49** |

Dropping `w_deep` hurts most (46.85 JM), confirming its role as an outlier suppressor even though `w_shallow` and `w_middle` carry the primary motion signal.

### Ablation: where to apply the mask

원논문 Table 6. DyCheck. Full Mask는 VGGT의 모든 attention layer에 마스크를 적용한 경우다.

| Method    | ATE ↓      | RTE ↓      | RRE ↓      |
| --------- | ---------- | ---------- | ---------- |
| Full Mask | 0.0302     | 0.0213     | 1.0660     |
| VGGT      | 0.0131     | 0.0082     | 0.4185     |
| **Ours**  | **0.0106** | **0.0072** | **0.3746** |

The key negative result: **full masking (0.0302) is worse than no masking at all (0.0131)**. Aggressive intervention pushes VGGT out of distribution and discards too much information.

### Zero-shot vs trained 2D segmentation

원논문 Table 9. DAVIS-2016. FlowSAM은 공정한 비교를 위해 zero-shot 설정으로 조정했다.

| Method              | JM ↑      | JR ↑      | FM ↑      | FR ↑      |
| ------------------- | --------- | --------- | --------- | --------- |
| FlowSAM (zero-shot) | 54.53     | 56.86     | 52.48     | 52.97     |
| DAS3R               | 41.13     | 38.67     | 44.50     | 36.94     |
| Easi3R_dust3r       | 50.10     | 55.77     | 43.40     | 37.25     |
| Easi3R_monst3r      | 54.93     | 68.00     | 45.29     | 47.30     |
| **Ours**            | **62.12** | **76.80** | **56.04** | **67.49** |

### Limitations stated by the paper

Computing Gram similarities adds overhead over single-pass inference. Refinement depends on VGGT's initial depth quality — if the backbone blends foreground and background, projection gradients become unreliable. The refinement assumes rigid motion for its projection checks and may struggle with highly non-rigid or fluid deformations.

## 💡 Insights & Impact

### `QK^T` is the wrong place to look

The reusable finding is architectural: attention logits entangle motion with texture and semantics, but the _self_-similarity structure of Q and K separately is a cleaner motion signal. Easi3R's whole method rests on `QK^T` epipolar inconsistency, and Table 5 shows it produces essentially noise on VGGT (7.51 JM). If a training-free probe works on one backbone, do not assume it transfers.

### Layers specialize, and you should read them separately

The three-band decomposition is not a tuning artifact — the ablation shows each band contributes something the others do not, with the deep band acting purely as an outlier suppressor. Treating a transformer's depth as a spectrum of different signals, rather than averaging across it, is what makes the cue robust enough to threshold automatically via Otsu.

### Intervene early, gently

The Full Mask result is the most instructive number in the paper. A model trained on static scenes has a learned distribution; masking dynamic tokens throughout violates it and costs more than the dynamics did. Restricting the intervention to layers 1–5 (K-vector suppression only) prevents motion from contaminating early geometric features while leaving the deeper stack in-distribution.

### Training-free composes with efficiency work

Because the method touches only attention computation and masking, it stacks directly on FastVGGT's token-discarding trick. The result — 500+ frames in a single pass where six specialized 4D methods OOM — comes from inheriting the backbone's scalability rather than rebuilding it.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the frozen backbone; VGGT4D is a pure inference-time modification of it
- [Easi3R](easi3r.md) — the direct conceptual predecessor (training-free attention-based 4D on DUSt3R); Table 5 shows its mechanism does not transfer to VGGT
- [MonST3R](monst3r.md) — fine-tunes on dynamic data with optical flow; the main recall competitor on DAVIS-all
- [DAS3R](../gaussian-splatting/das3r.md) — feed-forward motion masks via an augmented DPT head
- [CUT3R](cut3r.md) — fine-tunes on mixed static/dynamic data; one of the few baselines that survives 500-frame Point Odyssey
- [POMATO](pomato.md) — dynamic-scene baseline in Tables 2 and 4
- [FastVGGT](../reconstruction/fastvggt.md) — supplies the long-sequence token-discarding backbone VGGT4D builds on
- [DUSt3R](../foundation/dust3r.md) — origin of the pairwise attention formulation Easi3R exploits

## 📚 Key Takeaways

1. **Gram similarities (`QQ^T`, `KK^T`) beat attention logits (`QK^T`) as a motion cue** in VGGT — 62.12 vs 7.51 JM on DAVIS-2016 for the transplanted Easi3R logic.
2. **Masking all layers is worse than masking none** (ATE 0.0302 vs 0.0131 on DyCheck). Selective layer-1–5 K-vector suppression reaches 0.0106.
3. **Training-free probes are backbone-specific.** Easi3R's epipolar reasoning does not survive the move from DUSt3R to VGGT.
4. **Scalability is inherited, not rebuilt.** Stacking on FastVGGT gives 500+ frame single-pass inference where six specialized 4D methods OOM.
5. **The wins are honest and scoped.** SOTA on TUM-Dynamics, VKITTI, Point Odyssey, and DyCheck reconstruction; but SpatialTrackerV2 and DAS3R still lead parts of Sintel, and Easi3R_monst3r still leads DAVIS-all JM/JR.

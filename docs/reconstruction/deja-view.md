# DejaView: Looping Transformers for Multi-View 3D Reconstruction (arXiv preprint)

## 📋 Overview

- **Authors**: Alessandro Burzio, Tobias Fischer, Sven Elflein, Qunjie Zhou, Riccardo de Lutio, Jiawei Ren, Jiahui Huang, Shengyu Huang, Marc Pollefeys, Laura Leal-Taixé, Zan Gojcic, Haithem Turki
- **Institution**: NVIDIA, University of Modena and Reggio Emilia (AImageLab), University of Toronto / Vector Institute, ETH Zürich
- **Venue**: arXiv preprint (2026-05)
- **Note**: The venue could not be confirmed from any primary source and should be re-checked.
- **Links**: [Project Page](https://research.nvidia.com/labs/dvl/projects/dvlt/)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: Applies a _single_ transformer block recurrently for K steps instead of stacking unique layers, matching or beating billion-parameter feed-forward reconstruction models at 117 M parameters, with K exposed as an inference-time compute knob.

## 🎯 Key Contributions

1. **Explicit iteration over depth**: the hypothesis is that "model depth partially buys iteration, paid for inefficiently in unique parameters." DejaView makes that iteration architectural — one shared block applied K times to an evolving per-view state.
2. **Continuous-time conditioning**: the block is conditioned on the interval `(t_k, t_{k+1})` of a unit-interval partition rather than on a discrete step index, decoupling the weights from any specific K.
3. **K as an inference-time knob**: trained once with `K ∼ Beta(2,1)` scaled into `[8, 16]`, a single checkpoint serves any step count in that range.
4. **Looping beats decoupling under matched budget**: an otherwise identical variant with independent per-step parameters is _worse_ on every metric, suggesting explicit iteration is a stronger inductive bias, not merely a compute-efficient substitute for capacity.
5. **Directional refinement**: the recurrence is characterized empirically as converging in _direction_ rather than to a fixed point, distinguishing it from deep equilibrium networks and from RAFT-style task-space refinement.

## 🔧 Technical Details

### Recurrence

```text
z_{k+1} = f_θ(z_k, t_k, t_{k+1})
```

over the partition `0 = t_0 < t_1 < ⋯ < t_K = 1`. Unlike RAFT-style refinement, which decodes after every step and applies a sequence loss, DejaView refines an _internal_ state and supervises only at the final step — sparing `(K−1)` decoder forward and backward passes per training iteration.

### Block design

Two attention sub-blocks in sequence, following VGGT's alternating frame/global pattern: frame attention with 2D rotary position embeddings, then global attention over all tokens across all views. Each sub-block is pre-norm Attn + MLP with LayerScale. Three channel-wise scale vectors gate the update:

```text
z'    = z_k + s_attn ⊙ LS₁(Attn(LN₁(z_k)))
z''   = z'  + s_mlp  ⊙ LS₂(MLP(LN₂(z')))
z_{k+1} = s_out ⊙ z''
```

The scales come from a zero-initialized MLP, `s = 1 + MLP(γ(t_k, t_{k+1}))`, where `γ` concatenates sinusoidal embeddings of both endpoints.

### State and heads

`z_0` is initialized from a pretrained DINOv2 ViT-B encoder. Each view's token sequence is prepended with `R = 4` learnable register tokens and a learnable camera token, with parameters tied across views; the camera token uses two parameter sets, one for the reference (first) view and one tied across all others.

Two parallel decoder branches, each a shallow transformer plus an output head:

- **Ray decoder**: linear pixel-shuffle head producing `R_θ ∈ R^{H×W×6}`.
- **Depth decoder**: convolutional depth head to avoid block artifacts at patch boundaries, producing `D_θ` and a confidence map `c_D`.
- **Camera MLP head** decoding `c_θ = (t_θ, q_θ, f_θ)` — translation, unit quaternion, field of view — from camera tokens. This is a faster alternative to ray-derived recovery, which remains the default at inference.

World points follow analytically: `X_θ = R_o^θ + D_θ · R_d^θ`.

### Training

Five loss terms — ℓ2 on depth, a multi-scale ℓ1 depth-gradient term, ℓ1 on rays, ℓ2 on the analytically derived point cloud, and a camera loss decomposing into weighted ℓ1 on translation, rotation, and field of view. Predictions and ground truth are independently normalized following DUSt3R.

Two stages: 200 K iterations end-to-end with a linear pixel-shuffle depth head and plain ℓ2, then 40 K iterations finetuning only the convolutional depth decoder with DUSt3R-style confidence weighting (`λ_c = 0.2`), with ray and camera losses disabled.

128 H100 GPUs, `V ∈ [2, 18]` views per scene at 504-pixel longest edge, up to 4,608 images per step at a fixed ≈2.5 M token budget. AdamW at base LR 3×10⁻⁴, weight decay 0.05, cosine decay without warmup, 0.1× multiplier on the DINOv2 backbone. `K_inf = 16` at inference. Trained on a mixture of 29 public datasets. The depth-gradient term is applied only on synthetic data where ground-truth depth is dense enough.

## 📊 Results

### Pointmap accuracy

원논문 Table 1. Rel. L2 and inlier ratio (IR, fraction of points with relative error < 3%) on the global pointmap after Sim(3) alignment. VGGT-Ω is concurrent work, reported for completeness. ScanNet++ uses a clean scene-level train/eval split because it trains multiple baselines and DejaView itself.

| Method       | DTU Rel. L2 ↓ | DTU IR ↑ | ETH3D Rel. L2 ↓ | ETH3D IR ↑ | 7-Scenes Rel. L2 ↓ | 7-Scenes IR ↑ |
| ------------ | ------------- | -------- | --------------- | ---------- | ------------------ | ------------- |
| MASt3R       | 0.011         | 94.9     | 0.340           | 29.1       | 0.076              | 41.7          |
| MASt3R-SfM   | **0.009**     | 96.9     | 0.095           | 54.1       | 0.051              | 64.7          |
| MapAnything  | 0.014         | 95.2     | 0.227           | 40.6       | 0.044              | 67.9          |
| Pi3          | **0.009**     | **97.3** | 0.034           | 66.8       | **0.032**          | **77.8**      |
| VGGT         | 0.010         | 95.8     | 0.053           | 52.6       | 0.042              | 70.8          |
| VGGT-Ω-1B    | **0.009**     | 97.2     | **0.024**       | **78.6**   | 0.039              | 65.3          |
| DA3-L        | 0.010         | 97.1     | 0.211           | 49.9       | 0.039              | 69.6          |
| DA3-G        | 0.010         | 97.1     | 0.129           | 64.7       | 0.037              | 71.1          |
| **DejaView** | **0.009**     | 97.1     | 0.026           | 78.3       | 0.035              | 74.2          |

| Method       | ScanNet++ Rel. L2 ↓ | ScanNet++ IR ↑ | nuScenes Rel. L2 ↓ | nuScenes IR ↑ |
| ------------ | ------------------- | -------------- | ------------------ | ------------- |
| MASt3R       | 0.251               | 14.5           | 0.360              | 11.4          |
| MASt3R-SfM   | 0.042               | 69.7           | 0.311              | 18.4          |
| MapAnything  | 0.019               | 89.2           | 0.089              | 51.9          |
| Pi3          | **0.014**           | **94.3**       | 0.078              | 51.0          |
| VGGT         | 0.034               | 68.4           | 0.081              | 42.3          |
| VGGT-Ω-1B    | 0.032               | 70.6           | **0.055**          | **62.3**      |
| DA3-L        | 0.051               | 48.1           | 0.141              | 27.0          |
| DA3-G        | 0.041               | 57.8           | 0.080              | 42.0          |
| **DejaView** | 0.015               | 93.3           | 0.067              | 58.5          |

Pi3 leads indoor pointmap accuracy at 8× DejaView's parameters and 2× its compute; VGGT-Ω edges DejaView on outdoor Rel. L2 (ETH3D, nuScenes) at 10× the parameters.

### Camera pose accuracy

원논문 Table 2. AUC of the cumulative pose-error curve at 3° and 30°, where per-pair error is the max of rotation and translation angle error. The paper states DejaView ranks first or second on nine of ten cells and top-three on every cell.

| Method       | DTU @3   | DTU @30  | ETH3D @3 | ETH3D @30 | 7-Scenes @3 | 7-Scenes @30 |
| ------------ | -------- | -------- | -------- | --------- | ----------- | ------------ |
| MASt3R       | 21.6     | 81.7     | 35.2     | 57.6      | 9.3         | 70.6         |
| MASt3R-SfM   | 40.2     | 91.4     | 52.8     | 85.0      | 16.4        | 80.3         |
| MapAnything  | 18.1     | 88.8     | 37.1     | 73.8      | 8.2         | 74.6         |
| Pi3          | 70.2     | 97.3     | 43.2     | 84.9      | 11.3        | 81.3         |
| VGGT         | **96.5** | **99.8** | 35.4     | 82.8      | 11.1        | 79.1         |
| VGGT-Ω-1B    | 77.4     | 98.1     | 64.1     | **95.4**  | **21.3**    | **87.0**     |
| DA3-L        | 69.2     | 97.3     | 38.8     | 75.3      | 11.8        | 79.7         |
| DA3-G        | 74.9     | 97.9     | 55.4     | 82.4      | 12.0        | 80.9         |
| **DejaView** | 83.2     | 98.8     | **66.0** | **95.4**  | 13.9        | 81.7         |

| Method       | ScanNet++ @3 | ScanNet++ @30 | nuScenes @3 | nuScenes @30 |
| ------------ | ------------ | ------------- | ----------- | ------------ |
| MASt3R       | 15.5         | 43.9          | 9.4         | 62.7         |
| MASt3R-SfM   | 38.7         | 85.0          | 9.1         | 70.9         |
| MapAnything  | 70.6         | 96.7          | 37.8        | 82.8         |
| Pi3          | 76.5         | 97.3          | 24.8        | 82.4         |
| VGGT         | 15.1         | 74.7          | 39.2        | 83.8         |
| VGGT-Ω-1B    | 29.9         | 87.3          | 42.4        | **85.5**     |
| DA3-L        | 7.6          | 71.8          | 11.0        | 74.7         |
| DA3-G        | 26.4         | 80.2          | 37.7        | 82.0         |
| **DejaView** | **79.4**     | **98.0**      | **43.4**    | 85.3         |

The two clear losses: VGGT retains the DTU pose lead at 10× the parameters, concentrated at the tight AUC@3 threshold (96.5 vs 83.2) and shrinking to within 1.0 point at AUC@30; and VGGT-Ω leads 7-Scenes pose. Conversely, on ScanNet++ DejaView leads VGGT-Ω by nearly 50 points at AUC@3 and over 10 points at AUC@30.

### Efficiency

원논문 Table 3. Measured on a single A100 with 24 input views. IR and AUC@30° are averaged across the five benchmarks of Tables 1 and 2. For MASt3R (swin-5, 120 pairs) and MASt3R-SfM (retrieval-20-10, 273 pairs), FLOPs cover only the pair-network forward passes, excluding the iterative global alignment that follows; their lower peak memory comes from processing pairs sequentially.

| Method       | Params (M) ↓ | Compute (TFLOPs) ↓ | Compute/Img (TFLOPs) ↓ | Peak Mem (GiB) ↓ | IR (%) ↑ | AUC@30 (%) ↑ |
| ------------ | ------------ | ------------------ | ---------------------- | ---------------- | -------- | ------------ |
| MASt3R       | 689          | 500.0              | 20.8                   | 4.4              | 38.3     | 63.3         |
| MASt3R-SfM   | 690          | 1150.1             | 47.9                   | **3.4**          | 60.8     | 82.5         |
| MapAnything  | 1228         | 148.4              | 6.2                    | 20.1             | 69.0     | 83.3         |
| Pi3          | 959          | 153.8              | 6.4                    | 6.6              | 77.4     | 88.6         |
| VGGT         | 1257         | 190.0              | 7.9                    | 14.7             | 66.0     | 84.0         |
| VGGT-Ω-1B    | 1144         | **99.8**           | **4.2**                | 7.9              | 74.8     | 90.7         |
| DA3-L        | 356          | **71.4**           | **3.0**                | 7.3              | 58.3     | 79.7         |
| DA3-G        | 1201         | 178.7              | 7.4                    | 13.0             | 66.5     | 84.7         |
| **DejaView** | **117**      | 75.9               | 3.2                    | 4.9              | **80.3** | **91.8**     |

DejaView leads both averages at the smallest parameter count, running in under 5 GiB at 24 views. It does not lead on raw FLOPs — DA3-L is lower — nor on peak memory, where MASt3R-SfM's sequential pair processing is lower.

### Block design ablation

원논문 Table 4. All variants use a ViT-B encoder, 100 K iterations, same data. Metrics averaged across the five benchmarks.

| Variant                 | Weight sharing | Residual gates | State gate | Rel. L2 ↓ | IR ↑     | AUC@3 ↑  | AUC@30 ↑ |
| ----------------------- | -------------- | -------------- | ---------- | --------- | -------- | -------- | -------- |
| Decoupled               | ✗              | ✗              | ✗          | 0.056     | 61.1     | 23.0     | 82.0     |
| Shared                  | ✓              | ✗              | ✗          | 0.045     | 66.4     | 30.2     | 84.8     |
| Shared + residual gates | ✓              | ✓              | ✗          | 0.042     | 67.0     | 31.5     | 85.9     |
| Shared + state gate     | ✓              | ✓              | ✓          | **0.040** | **69.2** | **33.3** | **86.9** |

Every component improves every metric monotonically. The headline finding is the first row versus the second: weight sharing alone outperforms the decoupled architecture despite having **16× fewer parameters**.

### Step-count analysis

원논문 Table 5. Metrics averaged across the five benchmarks.

| Variant                     | Training K-sampler | K_inf | Rel. L2 ↓ | IR ↑     | AUC@3 ↑  | AUC@30 ↑ |
| --------------------------- | ------------------ | ----- | --------- | -------- | -------- | -------- |
| Fixed K=12                  | fixed              | 12    | 0.044     | 67.6     | 30.4     | 85.5     |
| Ours (Variable, K_max = 16) | Beta on [8, 16]    | 12    | 0.043     | 66.7     | 29.6     | 85.4     |
| Fixed K=16                  | fixed              | 16    | 0.041     | **69.6** | **33.8** | 86.8     |
| Ours (Variable, K_max = 16) | Beta on [8, 16]    | 16    | **0.040** | 69.2     | 33.3     | **86.9** |

Variable-K training stays within ~2% of Fixed K=16 at `K_inf = 16` and ~3% of Fixed K=12 at `K_inf = 12`, so one checkpoint covers both budgets at near-zero quality cost.

### Recurrence dynamics

Figure 3 reports per-iteration diagnostics: task quality improves monotonically with iteration count, cosine similarity `cos(z_k, z_16)` rises toward 1, the feature norm `‖z_k‖` grows rather than contracting, and the relative update norm `‖Δz_k‖/‖z_k‖` decays from ~0.5 at the first step to ~0.1 at the last — described in the text as decaying by **roughly 5×**. These are plots; no per-iteration table of values is printed, so no individual figures are transcribed here.

## 💡 Insights & Impact

### A different axis than everything else in this collection

Every other recent entry here scales up — more parameters, more data, bigger backbones. DejaView goes the other way and asks whether the depth of these stacks is doing work that a loop could do. At 117 M parameters against VGGT's 1257 M and MapAnything's 1228 M, it leads the averaged IR and AUC@30 of Table 3. That is a genuinely different claim about where the gains in this line of work come from.

### Looping is an inductive bias, not just compression

The strongest evidence is Table 4's first two rows. A decoupled 16-block variant has 16× the parameters of the shared variant and is worse on all four metrics under matched data and compute. If looping were merely a cheap approximation of depth, the decoupled model should win. It does not.

### Directional, not fixed-point, convergence

The recurrence does not contract in feature space — the state norm grows monotonically. What converges is the _direction_: cosine similarity to the endpoint approaches 1 while the relative update magnitude decays. Because each decoder branch is pre-norm, the input LayerNorm absorbs the norm growth, so the decoded representation effectively converges. This distinguishes DejaView from deep equilibrium networks (which contract to a fixed point) and from RAFT (which contracts in task space, decoding at every step).

### Supervising only the last step is what makes it affordable

Refining an internal state instead of the output means no decoder pass and no loss computation at intermediate steps — `(K−1)` forward and backward passes saved per training iteration. This is arguably as important as the parameter savings for making a 16-step recurrence trainable at all.

### Limitations stated by the authors

- **The recurrence does not extrapolate** beyond its trained step range — a few channels diverge once `K_inf` exceeds `K_max`. Preliminary attempts with looped-transformer stabilization recipes plateau past the trained budget rather than continuing to improve, at significant extra training cost.
- Variable-K training carries a small quality cost relative to fixed-K training at the matched step count.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — supplies the alternating frame/global attention design of the looped block, and remains the DTU pose leader at 10× the parameters.
- [VGGT-Ω](../reconstruction/vggt-omega.md) — concurrent work included in Tables 1–3, ahead on outdoor pointmap Rel. L2 and 7-Scenes pose.
- [π³](../reconstruction/pi3.md) — the closest competitor overall, leading indoor pointmap accuracy at 8× the parameters.
- [Depth Anything 3](../reconstruction/depth-anything-3.md) — DA3-L/DA3-G baselines; DejaView also follows its camera-parameter recovery from ray maps and its camera MLP head.
- [MapAnything](../reconstruction/mapanything.md) — baseline in all three main tables.
- [MASt3R](../foundation/mast3r.md) — pairwise baseline, with MASt3R-SfM adding sparse global alignment.
- [DUSt3R](../foundation/dust3r.md) — source of the normalization scheme and the confidence-weighted depth loss used in stage 2.

## 📚 Key Takeaways

1. **117 M parameters, top average IR (80.3%) and AUC@30 (91.8%)** across five benchmarks — the best parameter efficiency in Table 3 by roughly 3× over the next-smallest model.
2. **Weight sharing beats decoupled blocks under matched budget** (Rel. L2 0.045 vs 0.056, IR 66.4 vs 61.1) despite 16× fewer parameters — the paper's central argument that iteration is a real inductive bias (원논문 Table 4).
3. **One checkpoint, a range of compute budgets**: continuous-time conditioning plus Beta-sampled K keeps variable-K training within ~2–3% of fixed-K at both K_inf = 12 and 16 (원논문 Table 5).
4. **It does not win everywhere**: VGGT keeps the DTU pose lead (96.5 vs 83.2 at AUC@3), VGGT-Ω leads 7-Scenes pose and outdoor pointmap Rel. L2, and π³ leads indoor pointmap accuracy.
5. **The recurrence refines directionally rather than converging to a fixed point**, and it does not extrapolate past its trained step range — an explicit limitation the authors flag.

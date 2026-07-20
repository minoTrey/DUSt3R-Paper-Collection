# PAGE-4D: VGGT-4D Perception via Disentangled Pose and Geometry Estimation (ICLR 2026)

## 📋 Overview

- **Authors**: Kaichen Zhou, Yuhan Wang, Grace Chen, Xinhai Chang, Gaspard Beaudouin, Fangneng Zhan, Paul Pu Liang, Mengyu Wang
- **Institution**: Harvard University (Harvard AI and Robotics Lab, Kempner Institute), MIT (Media Lab and EECS), Imperial College London, École Nationale des Ponts et Chaussées / Institut Polytechnique de Paris
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.17568)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Extends VGGT to dynamic scenes by predicting a self-supervised dynamics-aware mask and applying it asymmetrically — suppressing dynamic regions for the camera and register tokens while leaving geometry heads free to exploit motion — with only the middle 10 attention layers fine-tuned.

> **Naming note**: this paper lists "VGGT-4D, Dynamic VGGT" among its own keywords. It is a distinct work from VGGT4D (arXiv 2511.19971) and DynamicVGGT (arXiv 2603.08254); nothing in this document is drawn from those papers.

## 🎯 Key Contributions

1. **Diagnosis of a task conflict**: Camera pose estimation reduces to fitting an essential matrix that holds only on the _static_ pixel subset, while geometry estimation remains valid on all non-occluded pixels. Suppressing dynamics therefore helps pose and hurts geometry — the two tasks want opposite things from the same tokens.
2. **Dynamics-aware aggregator**: A three-stage aggregator where the middle stage uses Dynamics-Aware Global Attention driven by a learned mask, applied only to camera/register token queries.
3. **Self-supervised dynamic mask prediction**: A linear projection plus depthwise convolutional head over patch tokens produces mask logits with no explicit motion supervision.
4. **Memory-efficient additive mask**: An O(N) two-vector reformulation of the O(N²) attention mask that stays compatible with fused Scaled Dot-Product Attention.
5. **Targeted fine-tuning**: Only the middle 10 attention layers are updated — 30% of the model — motivated by a layer-perturbation analysis.

## 🔧 Technical Details

### The Motivating Analysis

On the Odyssey test set the paper measures VGGT's Absolute Depth Error in dynamic regions as **94% higher** than in static regions. Attention-map visualization at global attention layers 5, 12, 18, and 24 shows dynamic regions with weaker activations — VGGT already tends to ignore dynamic content.

The formal argument: under static conditions, correspondence is fully determined by intrinsics, depth, and relative pose,

`x_t = K [ R_{t←r} D_r(x_r) K⁻¹ x_r + t_{t←r} ]`

while pose estimation reduces to fitting an essential matrix `E = [t_{t←r}]_× R_{t←r}` satisfying `x̃_tᵀ E x̃_r = 0`. Dynamic displacement adds a residual proportional to the component of motion perpendicular to the epipolar line. The larger that residual, the greater the pose error — so the epipolar constraint holds only for the static subset `(x_r^sta, x_t^sta)`, whereas the geometry equation remains valid for all non-occluded pairs.

### Architecture

PAGE-4D inherits VGGT's DINO-style encoder, the lightweight depth/point decoders, and the larger camera decoder. Only the aggregator is changed, into three stages:

- **Stage 1** (N₁ layers): Global Attention + Frame Attention, as in VGGT. Its output feeds the dynamic mask prediction module.
- **Stage 2** (N₂ layers): Dynamics-Aware Global Attention + Frame Attention, with the predicted mask applied.
- **Stage 3** (N₃ layers): same structure as stage 1.

### Mask Prediction and Asymmetric Application

Patch tokens `z_p ∈ R^{B×S×(H_P·W_P)×d}` are projected to a lower dimension and passed through a depthwise convolutional head producing logits `m = Conv(z_p)`. The mask enters attention additively:

`Attn(Q,K,V) = softmax(QKᵀ/√d + M̃) V`

The asymmetry is the core idea:

- **Pose estimation** — for queries corresponding to the camera token and registration token, M̃ actively suppresses attention to dynamic regions, keeping pose consistent with epipolar geometry.
- **Depth and point cloud** — for patch queries the mask is _not_ applied, so motion cues remain available for reconstruction and 2D–3D tracking.

### Memory-Efficient Mask

Rather than materializing an (S·P)² matrix, the mask head predicts two vectors r, c ∈ R^N and augments the feature dimension: `q'ᵢ = [qᵢ√(d'/d), rᵢ√d']`, `k'ⱼ = [kⱼ, cⱼ]`, `v'ⱼ = [vⱼ, 0]` with d' = d+1, giving `q'ᵢk'ⱼᵀ/√d' = qᵢᵀkⱼ/√d + rᵢcⱼ` at O(N) memory.

### Training

- **Loss**: `L = λ_c L_camera + L_depth + L_pmap`, with λ_c = 5.
- **Fine-tuning**: middle 10 layers only, ≈30% of the model; the rest of the aggregator and all decoders frozen.
- **Data**: Odyssey, DynamicReplica, Kubric-MV, Spring, CO3D, Waymo, Sintel, and an internal dataset — approximately 2.39M sampled sequences, with per-dataset sampling multipliers.

The authors release both a training-and-inference masking variant and a training-only masking variant (the latter is architecturally identical to VGGT at inference).

### Parameter Distribution of the VGGT Backbone

원논문 Table 6. 파라미터가 aggregator에 몰려 있다는 것이 중간 레이어만 미세조정하는 설계의 근거다.

| Module     | Parameters |
| ---------- | ---------- |
| Depth      | 32.7M      |
| Point      | 32.7M      |
| Track      | 65.9M      |
| Camera     | 216.2M     |
| Aggregator | 909.1M     |

## 📊 Results

### Video and Monocular Depth Estimation

원논문 Table 1. FPS는 KITTI에서 A800 GPU 1장으로 측정했다. `-`는 원논문들이 보고하지 않은 항목이다. 정렬 방식별로 표를 나눈다.

**Video Depth, scale alignment**

| Method      | Params | Sintel Abs Rel ↓ | δ < 1.25 ↑ | Bonn Abs Rel ↓ | δ < 1.25 ↑ | DyCheck Abs Rel ↓ | δ < 1.25 ↑ | FPS  |
| ----------- | ------ | ---------------- | ---------- | -------------- | ---------- | ----------------- | ---------- | ---- |
| DUSt3R      | 571M   | 0.662            | 0.434      | 0.151          | 0.839      | -                 | -          | 1.25 |
| MASt3R      | 689M   | 0.558            | 0.487      | 0.188          | 0.765      | -                 | -          | 1.01 |
| CUT3R       | 793M   | 0.430            | 0.465      | **0.077**      | **0.937**  | 0.176             | 0.740      | 6.98 |
| Fast3R      | 648M   | 0.638            | 0.422      | 0.194          | 0.772      | -                 | -          | 65.8 |
| FLARE       | 1.40B  | 0.729            | 0.336      | 0.152          | 0.790      | -                 | -          | 1.75 |
| VGGT        | 1.26B  | 0.484            | 0.553      | 0.107          | 0.883      | 0.182             | 0.743      | 43.2 |
| **PAGE-4D** | 1.26B  | **0.357**        | **0.699**  | 0.092          | 0.904      | **0.170**         | **0.785**  | 43.2 |

**Video Depth, scale & shift alignment**

| Method      | Params | Sintel Abs Rel ↓ | δ < 1.25 ↑ | Bonn Abs Rel ↓ | δ < 1.25 ↑ | DyCheck Abs Rel ↓ | δ < 1.25 ↑ | FPS  |
| ----------- | ------ | ---------------- | ---------- | -------------- | ---------- | ----------------- | ---------- | ---- |
| DUSt3R      | 571M   | 0.570            | 0.493      | 0.152          | 0.835      | -                 | -          | 1.25 |
| MASt3R      | 689M   | 0.480            | 0.517      | 0.189          | 0.771      | -                 | -          | 1.01 |
| CUT3R       | 793M   | 0.534            | 0.558      | 0.075          | **0.943**  | 0.228             | 0.635      | 6.98 |
| Fast3R      | 648M   | 0.518            | 0.486      | 0.196          | 0.768      | -                 | -          | 65.8 |
| FLARE       | 1.40B  | 0.791            | 0.358      | 0.142          | 0.797      | -                 | -          | 1.75 |
| VGGT        | 1.26B  | 0.261            | 0.639      | 0.102          | 0.890      | 0.155             | 0.792      | 43.2 |
| **PAGE-4D** | 1.26B  | **0.212**        | **0.763**  | **0.090**      | 0.903      | **0.145**         | **0.854**  | 43.2 |

**Monocular Depth**

| Method      | Params | Sintel Abs Rel ↓ | δ < 1.25 ↑ | Bonn Abs Rel ↓ | δ < 1.25 ↑ | DyCheck Abs Rel ↓ | δ < 1.25 ↑ | FPS  |
| ----------- | ------ | ---------------- | ---------- | -------------- | ---------- | ----------------- | ---------- | ---- |
| DUSt3R      | 571M   | 0.488            | 0.532      | 0.139          | 0.832      | -                 | -          | 1.25 |
| MASt3R      | 689M   | 0.413            | 0.569      | 0.123          | 0.833      | -                 | -          | 1.01 |
| MonST3R     | 571M   | 0.402            | 0.525      | 0.069          | 0.954      | -                 | -          | 1.27 |
| CUT3R       | 793M   | 0.418            | 0.520      | 0.058          | 0.967      | 0.149             | 0.790      | 6.98 |
| Fast3R      | 648M   | 0.544            | 0.509      | 0.169          | 0.796      | -                 | -          | 65.8 |
| FLARE       | 1.40B  | 0.606            | 0.402      | 0.130          | 0.836      | -                 | -          | 1.75 |
| VGGT        | 1.26B  | 0.292            | 0.629      | 0.071          | 0.947      | 0.160             | 0.799      | 43.2 |
| **PAGE-4D** | 1.26B  | **0.242**        | **0.742**  | **0.053**      | **0.970**  | **0.141**         | **0.840**  | 43.2 |

The paper's headline comparison: on Sintel with scale-shift alignment, δ < 1.25 rises from VGGT's 0.639 to 0.763 (+19.4%) and Abs Rel falls from 0.261 to 0.212 (−18.8%), with no noticeable change in speed or memory — FPS is identical at 43.2 since the parameter count is unchanged. Note that CUT3R still holds Bonn under both video-depth alignment settings.

### Camera Pose Estimation

원논문 Table 2. Sim(3) Umeyama 정렬 후, 시퀀스당 10프레임을 균일 샘플링해 평가한다. `Optim.` 열의 `•`는 최적화를 수반하는 방법이다.

| Method      | Optim. | Sintel ATE ↓ | RPE trans ↓ | RPE rot ↓ | Tum ATE ↓ | RPE trans ↓ | RPE rot ↓ |
| ----------- | ------ | ------------ | ----------- | --------- | --------- | ----------- | --------- |
| MonST3R     | •      | **0.108**    | **0.042**   | 0.732     | 0.098     | 0.019       | 0.935     |
| DUSt3R      |        | 0.417        | 0.250       | 5.796     | 0.140     | 0.106       | 3.286     |
| Spann3R     |        | 0.329        | 0.110       | 4.471     | 0.056     | 0.021       | 0.591     |
| CUT3R       |        | 0.213        | 0.066       | 0.621     | 0.046     | 0.015       | 0.473     |
| VGGT        |        | 0.214        | 0.079       | 0.643     | 0.028     | 0.014       | 0.371     |
| **PAGE-4D** |        | 0.178        | 0.069       | **0.547** | **0.016** | **0.011**   | **0.323** |

Reported honestly: the optimization-based MonST3R still leads Sintel ATE and RPE trans. PAGE-4D's claims are narrower — reducing Tum RPE trans by 21% and RPE rot by 13% relative to prior feed-forward approaches while remaining competitive on ATE, and reducing Sintel RPE rot by 17%. Its RPE trans on Sintel (0.069) is also behind CUT3R's 0.066.

### Point Map Reconstruction on DyCheck

원논문 Table 3. Acc / Comp / Overall 모두 낮을수록 좋다.

| Method      | Optim. | Acc ↓ Mean | Median    | Comp ↓ Mean | Median    | Overall ↓ Mean | Median    |
| ----------- | ------ | ---------- | --------- | ----------- | --------- | -------------- | --------- |
| MonST3R     | •      | 0.851      | 0.689     | 1.734       | 0.958     | 1.292          | 0.823     |
| DUSt3R      |        | 0.802      | 0.595     | 1.950       | 0.815     | 1.376          | 0.705     |
| CUT3R       |        | 0.458      | 0.342     | 1.633       | 0.792     | 1.042          | 0.567     |
| DAS3R       |        | 1.772      | 1.438     | 2.503       | 1.548     | **0.475**      | **0.352** |
| VGGT        |        | 1.051      | 1.016     | 1.594       | 1.393     | 1.322          | 1.204     |
| **PAGE-4D** |        | **0.403**  | **0.284** | **1.222**   | **0.728** | 1.115          | 0.559     |

PAGE-4D leads on Acc and Comp but **not** on Overall — DAS3R reports far lower Overall (0.475 / 0.352) despite much worse Acc and Comp. The paper's own claims are confined to the Acc and Comp columns: >60% mean Accuracy reduction vs VGGT (1.051 → 0.403), >70% median (1.016 → 0.284), and >20% reduction in both Completion statistics.

### Novel View Synthesis on Nerfie

원논문 Table 4. PAGE-4D의 점군을 4D-Gaussian splatting 초기화로 사용한 결과의 평균값만 옮긴다 (원표는 5개 장면별 값을 포함해 18열이다).

| Method      | Avg PSNR ↑ | Avg SSIM ↑ | Avg LPIPS ↓ |
| ----------- | ---------- | ---------- | ----------- |
| dust3r      | 12.632     | 0.314      | 0.601       |
| monst3r     | 12.982     | 0.325      | 0.595       |
| cut3r       | 16.319     | 0.448      | 0.472       |
| vggt        | 16.861     | 0.483      | 0.454       |
| **PAGE-4D** | **17.593** | **0.485**  | **0.449**   |

Per-scene results are mixed — on `laptop8` VGGT (15.954 PSNR) and CUT3R (16.505) both beat PAGE-4D (15.718), and CUT3R holds the best LPIPS on that scene (0.365).

### Ablation: Fine-Tuning Scope and Mask Attention

원논문 Table 5.

| Method                                        | Sintel Abs Rel ↓ | δ < 1.25 ↑ | Bonn Abs Rel ↓ | δ < 1.25 ↑ | DyCheck Abs Rel ↓ | δ < 1.25 ↑ |
| --------------------------------------------- | ---------------- | ---------- | -------------- | ---------- | ----------------- | ---------- |
| VGGT\* (Whole Model)                          | 0.405            | 0.593      | 0.101          | 0.891      | 0.175             | 0.775      |
| VGGT\* (Middle Layers)                        | 0.409            | 0.590      | 0.099          | 0.879      | 0.177             | 0.766      |
| **Ours — VGGT\* (Middle Layers + Mask Attn)** | **0.357**        | **0.699**  | **0.092**      | **0.904**  | **0.170**         | **0.785**  |

Two conclusions follow: fine-tuning only the middle layers matches full fine-tuning (0.409 vs 0.405 on Sintel Abs Rel), and essentially all the gain comes from the dynamics-aware mask, not from the fine-tuning itself.

### Ablation: Masking Strategies and Layer Importance

원논문 Table 7. Odyssey 데이터셋에서 unscaled pose를 평가한다. Static-D는 정적 영역의 Absolute Depth Error, Static-T는 2D 포인트 트래킹의 Average Endpoint Error (EPE)다. 마지막 레이어만 camera head로 들어가므로 레이어 제거 실험에서는 pose 항목이 `-`다.

| Method    | RPE trans ↓ | RPE rot ↓ | Static-D ↓ | Static-T ↓ |
| --------- | ----------- | --------- | ---------- | ---------- |
| Normal    | 0.244       | 0.942     | **0.085**  | **17.071** |
| Input-MSK | 0.246       | 1.006     | 0.099      | 17.866     |
| DD-MSK    | **0.243**   | **0.869** | 0.566      | 24.797     |
| w/o 4th   | -           | -         | 0.114      | 18.821     |
| w/o 11th  | -           | -         | 0.095      | 18.403     |
| w/o 17th  | -           | -         | 1.663      | 39.841     |
| w/o 23rd  | -           | -         | 0.103      | 17.645     |

This is the paper's central empirical evidence, and it cuts both ways honestly: DD-MSK (blocking self-attention among dynamic patches) improves pose (RPE rot 0.942 → 0.869) but wrecks geometry (Static-D 0.085 → 0.566, Static-T 17.071 → 24.797). Rigid masking is confirmed suboptimal — hence the asymmetric, task-specific design. Replacing layer 17's output with random noise is by far the most damaging perturbation, motivating the middle-layer fine-tuning target.

The paper also notes that keeping the mask throughout training and applying it only in the first stage yield similar performance, and that both beat the unmasked baseline — which is why both variants are released.

## 💡 Insights & Impact

### The Conflict Is Structural, Not a Training Artifact

The paper's most valuable contribution is not the mask but the framing. Pose estimation and geometry estimation in a shared transformer are not merely competing for capacity; they place _contradictory_ requirements on the same tokens. Equation 2 (epipolar) holds only on static pixels; equation 3 (geometry) holds on all non-occluded pixels. Any architecture that treats dynamic tokens uniformly must pick a side. Table 7 is the empirical proof: every global masking strategy that helps pose hurts geometry.

### Asymmetry as the Resolution

The fix is elegantly cheap — apply the mask to _which queries_, not to _which tokens_. Camera and register token queries see a masked attention field; patch queries see the unmasked one. The dynamic tokens are never removed from the network, only from the pose pathway. This costs nothing at inference (FPS and parameter count are unchanged at 43.2 and 1.26B) and requires no architectural surgery.

### Adapting Rather Than Retraining

30% of the model is tuned, and Table 5 shows the layer selection itself contributes almost nothing — 0.409 vs 0.405 on Sintel. That is a useful negative result: the received wisdom that dynamic scenes need dynamic-specific fine-tuning is not what is doing the work here. The backbone already had the capacity; it was being spent suppressing motion.

### Where It Doesn't Win

Optimization-based MonST3R still leads Sintel ATE and RPE trans, CUT3R holds Bonn video depth, and DAS3R holds DyCheck Overall. PAGE-4D's argument is that it is the best _feed-forward, post-processing-free_ option across the board at VGGT's speed, not that it dominates every column.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md) — the backbone PAGE-4D extends; all four components except the aggregator are inherited unchanged.
- [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) — pairwise pointmap foundations that the paper argues are constrained by their pairwise framework.
- [MonST3R](monst3r.md) — DUSt3R fine-tuned on video; the optimization-based dynamic baseline that still wins Sintel ATE.
- [CUT3R](cut3r.md) — recurrent state-token streaming model, the strongest non-VGGT feed-forward competitor here.
- [Easi3R](easi3r.md) — training-free dynamic adaptation; the paper's Input-MSK and DD-MSK baselines are inspired by this line of work.
- [D²USt3R](d2ust3r.md) — 4D pointmaps with cross-frame attention for moving-object correspondence.
- [Dynamic Point Maps](dynamic-point-maps.md) / [V-DPM](v-dpm.md) — alternative 4D pointmap formulations.
- [Fast3R](../reconstruction/fast3r.md) — the high-FPS feed-forward baseline in Table 1.
- [StreamVGGT](../reconstruction/streamvggt.md) — a VGGT extension the paper positions as application-specific rather than general.
- [Any4D](any4d.md) / [Human3R](human3r.md) — adjacent 4D perception directions.

## 📚 Key Takeaways

1. **Pose and geometry want opposite things from dynamic pixels.** The epipolar constraint holds only on static pixels; the geometry equation holds everywhere. This is a formal, not empirical, conflict.
2. **Mask the queries, not the tokens.** Suppressing dynamics for camera/register queries while leaving patch queries unmasked resolves the conflict at zero inference cost.
3. **Global masking is a trap.** DD-MSK improves RPE rot but raises Static-D from 0.085 to 0.566 — the classic symptom of solving one task by breaking another.
4. **Layer 17 carries the geometry.** Noising layer 17 raises Static-D to 1.663 and Static-T to 39.841, far beyond any other layer.
5. **The gains come from the mask, not the fine-tuning.** Middle-layer fine-tuning alone matches full fine-tuning; adding mask attention is what moves Sintel δ < 1.25 from 0.590 to 0.699.

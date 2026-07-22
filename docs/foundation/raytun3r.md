# RayTun3R: Online Camera Adaptation in 3D Foundation Models (arXiv preprint 2026-07)

![raytun3r — architecture](https://arxiv.org/html/2607.02711v1/x1.png)

_RayTun3R overview (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Daniil Sinitsyn, Nikita Araslanov, Daniel Cremers
- **Institution**: TU Munich; Munich Center for Machine Learning; University of Oxford
- **Venue**: arXiv preprint (2026-07)
- **Links**: [Paper](https://arxiv.org/abs/2607.02711)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A lightweight online adapter that corrects the pinhole bias in the positional encodings of frozen 3D foundation models (DA3, VGGT, π³), letting them handle fisheye input. It learns only 10,752 parameters from a short self-supervised temporal segment with no inference-time overhead.

## 🎯 Key Contributions

1. **Diagnosing pinhole bias**: The local Jacobian of pretrained positional embeddings is nearly radius-independent, matching a pinhole camera's constant back-projection Jacobian — evidence that the positional representation carries a pinhole spatial prior that fails on fisheye geometry.
2. **Positional-encoding adapter**: Parameter-efficient residual corrections to absolute positional embeddings and rotary positional encoding (RoPE), parameterized as small radial/angular lookup tables around the principal point, all initialized to zero.
3. **Parameter-free geometry corrections**: Camera-aware prediction-grid coordinates (undistorting the DPT sinusoidal grid) and per-patch local undistortion + border-token handling remove residual pinhole assumptions without adding weights.
4. **Self-supervised online fitting**: The adapter is fit on a short temporal segment using reprojection, a MAGSAC++ pose target from UFM correspondences, edge-aware depth smoothness, and PE regularization — no ground truth.

## 🔧 Technical Details

### Adapter formulation

For each patch, given normalized radius ρ and angle θ w.r.t. the calibrated principal point, the corrected absolute embedding is `P'(u,v) = P_A(u,v) + t_r(ρ) + ρ·δ_θ(θ)`, where the ρ factor suppresses the (ill-defined) angular term at the center. For RoPE backbones, a shared radial lookup table corrects the rotary angle: `ω'(u,v) = ω(u,v) + Δ_r(ρ)`.

### Training objective

`L = L_reproj + w_smooth·L_smooth + w_L2·L_L2 + w_TV·L_TV + w_pose·L_pose` with `w_pose = 1, w_smooth = 10, w_L2 = 2, w_TV = 20`. A fixed relative-pose target `T̃_ij` is estimated once via MAGSAC++ from UFM matches (so the adapter cannot influence its own pseudo-label). No photometric warping loss is used.

### Configuration

- Images resized to max patch-aligned resolution 504 × 504; Adam, lr 1 × 10⁻³, gradient clipping at norm 1.0.
- PE adapter uses 20 radial + 8 angular bins; RoPE backbones add 20 radial RoPE bins.
- Adaptation set: 30 three-frame windows per sequence (filtering near-static windows with average optical-flow displacement below 2 px); evaluate on the full sequence.
- Datasets span FOV 110° to 200°: KITTI-360 (185°), TUM-VI (195°), ScanNet++ (115°), ETH3D (110°), FIORD (200°).

## 📊 Results

### Rotation error R° across five datasets (DA3-Small)

원논문 Table 1 (R° 성분). 낮을수록 좋음. KITTI-360 회전에서는 Center-PH(0.79)가 RayTun3R(0.84)보다 근소 우위.

| Method    | ETH3D    | KITTI-360 | TUM-VI   | ScanNet++ | FIORD    |
| --------- | -------- | --------- | -------- | --------- | -------- |
| Vanilla   | 8.59     | 1.69      | 10.41    | 10.21     | 18.20    |
| Center-PH | 3.46     | **0.79**  | 3.33     | 3.27      | 6.92     |
| Multi-PH  | 3.31     | 1.71      | 2.99     | 1.66      | 6.30     |
| LoRA      | 2.18     | 1.37      | 3.38     | 3.68      | 7.75     |
| CalTok    | 2.48     | 1.66      | 3.84     | 4.51      | 20.40    |
| RayTun3R  | **0.70** | 0.84      | **2.41** | **1.11**  | **4.10** |

### Translation-direction error t° across five datasets (DA3-Small)

원논문 Table 1 (t° 성분). RayTun3R가 모든 데이터셋에서 최저.

| Method    | ETH3D    | KITTI-360 | TUM-VI    | ScanNet++ | FIORD    |
| --------- | -------- | --------- | --------- | --------- | -------- |
| Vanilla   | 15.16    | 12.81     | 23.23     | 30.26     | 29.50    |
| Center-PH | 13.70    | 4.17      | 29.24     | 22.77     | 23.40    |
| Multi-PH  | 13.68    | 9.75      | 25.60     | 10.43     | 18.90    |
| LoRA      | 10.74    | 8.49      | 13.63     | 17.66     | 12.20    |
| CalTok    | 13.21    | 10.05     | 16.17     | 23.20     | 22.20    |
| RayTun3R  | **4.48** | **2.92**  | **13.23** | **5.78**  | **5.40** |

### Reprojection depth error d_reproj across five datasets (DA3-Small)

원논문 Table 1 (d_reproj 성분). ScanNet++에서는 Multi-PH(1.63)가 최저.

| Method    | ETH3D    | KITTI-360 | TUM-VI   | ScanNet++ | FIORD    |
| --------- | -------- | --------- | -------- | --------- | -------- |
| Vanilla   | 15.98    | 11.64     | 57.01    | 23.82     | 75.30    |
| Center-PH | 10.92    | **3.10**  | 3.22     | 2.21      | 7.20     |
| Multi-PH  | 13.48    | 4.72      | 4.92     | **1.63**  | 15.60    |
| LoRA      | 9.02     | 5.56      | 3.83     | 4.98      | 12.10    |
| CalTok    | 11.94    | 5.83      | 9.61     | 7.02      | 25.20    |
| RayTun3R  | **5.82** | 3.88      | **3.81** | 4.16      | **9.00** |

### Dense depth on ETH3D and ScanNet++ (DA3-Small)

원논문 Table 3 (left). AbsRel 낮을수록, δ1.25 높을수록 좋음. ScanNet++ AbsRel에서는 Center-PH(0.066)가 RayTun3R를 앞선다 (perspective 입력이 백본 사전학습 분포에 가깝기 때문).

| Method    | ETH3D AbsRel ↓ | ETH3D δ1.25 ↑ | ScanNet++ AbsRel ↓ | ScanNet++ δ1.25 ↑ |
| --------- | -------------- | ------------- | ------------------ | ----------------- |
| Center-PH | 0.111          | 0.867         | **0.066**          | **0.961**         |
| LoRA      | 0.166          | 0.814         | 0.175              | 0.760             |
| CalTok4   | 0.175          | 0.793         | 0.168              | 0.769             |
| Vanilla   | 0.178          | 0.751         | 0.282              | 0.601             |
| RayTun3R  | **0.107**      | **0.884**     | 0.108              | 0.886             |

### Inference cost and parameter count (DA3-Small, 504×504)

원논문 Table 4b. 프레임당 ms, 오버헤드, 학습 파라미터 수.

| Method             | ms/frame | Overhead | Params |
| ------------------ | -------- | -------- | ------ |
| Vanilla DA3        | ~100     | baseline | 0      |
| Center-PH (110°)   | ~105     | +5%      | 0      |
| Multi-PH (5 views) | ~400     | +300%    | 0      |
| LoRA (r=8)         | ~110     | +10%     | 147.5K |
| CalTok (t=4)       | ~105     | +5%      | 18.4K  |
| RayTun3R (ours)    | ~100     | ≈ 0%     | 10.8K  |

### Component ablation (KITTI-360, 185° fisheye)

원논문 Table 4a. 학습된 PE residual이 가장 큰 이득; parameter-free 보정은 작은 변화.

| Configuration                        | R° ↓  | t° ↓  | d_reproj ↓ |
| ------------------------------------ | ----- | ----- | ---------- |
| Patch undistortion (no learnable PE) | 1.397 | 6.66  | 8.96       |
| Naive remap of PE                    | 0.810 | 12.93 | 11.53      |
| Radial PE only                       | 1.154 | 5.48  | 3.70       |
| Radial + angular PE                  | 1.038 | 4.21  | 3.39       |
| RayTun3R (full)                      | 1.183 | 4.81  | **3.03**   |

## 💡 Insights & Impact

- **Camera geometry lives in positional encodings, not features**: Correcting position-to-ray mappings beats generic PEFT (LoRA) and calibration-token adaptation, supporting the view that camera mismatch is best isolated in the positional representation.
- **Model-agnostic**: Gains hold across DA3-Small, π³, and VGGT (원논문 Table 2), where RayTun3R gives the lowest translation error on every tested sequence.
- **Trade-off vs. projection baselines**: Center-PH stays strong for depth on moderate-FOV data (it feeds perspective-like crops to the backbone) but discards peripheral content, hurting pose; RayTun3R keeps the full fisheye FOV at single-view inference cost. The abstract reports a 2–12× rotation-error reduction over the unadapted model and ~14× fewer trainable parameters than LoRA.
- **Limitations**: The correction is camera-specific (a new lens requires re-adaptation), assumes a principal point and mostly radial distortion, requires camera parameters, and needs sufficient inter-frame motion for the self-supervised losses.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)** / **[π³](../reconstruction/pi3.md)**: Frozen backbones (alongside Depth Anything 3) that RayTun3R adapts to fisheye.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: 3D foundation models cited as inheriting pinhole spatial priors from perspective training.

## 📚 Key Takeaways

1. **Pinhole bias is measurable** in the positional-embedding Jacobian and is the main reason foundation models fail on fisheye input.
2. **A tiny positional adapter fixes it**: 10,752 trainable parameters, zero inference overhead, learned self-supervised from ~30 short windows.
3. **Targeting geometry beats generic tuning**: correcting camera-dependent positional components outperforms LoRA and calibration tokens while using far fewer parameters and preserving the full fisheye field of view.

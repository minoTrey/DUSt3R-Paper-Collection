# FGQ: Fisher-Guided Quantization for Visual Geometry Transformer (arXiv preprint (2026-05))

_FGQ preserves point-map reconstruction fidelity under 4-bit quantization, surpassing the prior VGGT-specific PTQ method QuantVGGT (원논문 Figure 1, 수치 미인쇄)._

## 📋 Overview

- **Authors**: Yipu Zhang, Jintao Cheng, Weilun Feng, Jiehao Luo, Chuanguang Yang, Zhulin An, Yongjun Xu, Wei Zhang
- **Institution**: Department of Electronic and Computer Engineering, HKUST; State Key Laboratory of AI Safety, Institute of Computing Technology, Chinese Academy of Sciences; University of Chinese Academy of Sciences; School of Data Science and Engineering, South China Normal University; Xiamen Institute of Data Intelligence
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.15828) | [Code](https://github.com/ypzhng/FGQ)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A task-aware post-training quantization (PTQ) framework for feed-forward 3D reconstruction models that uses the diagonal Fisher information matrix to measure per-task, per-block, and per-channel quantization sensitivity and folds it into a learnable affine transformation, achieving up to 39% relative improvement over SOTA PTQ baselines on VGGT under 4-bit quantization.

## 🎯 Key Contributions

1. **Multi-task sensitivity problem**: Identifies that feed-forward 3D reconstruction models (VGGT) predict depth, pose, and point maps through a shared backbone, where different transformer blocks and hidden channels contribute distinctly to each task, causing substantially different sensitivities to quantization error across tasks, blocks, and channels.
2. **Fisher-Guided Quantization (FGQ)**: Uses the diagonal Fisher information matrix to quantify per-task, per-block, and per-channel sensitivity, and integrates these sensitivities into the Learnable Affine Transformation calibration objective to steer calibration toward the most quantization-sensitive components.
3. **Consistent gains under 4-bit**: Extensive experiments on camera pose estimation, point map reconstruction, and depth estimation show FGQ improves task performance by up to 39% over SOTA PTQ baselines under 4-bit quantization, with the largest gains on point map reconstruction, where prior PTQ methods incur the most severe degradation.

## 🔧 Technical Details

### Setting: PTQ on VGGT

- Base model: open-source **VGGT-1.2B** [Wang et al., 2025a]; a feed-forward transformer mapping N input images to camera parameters, depth maps, point maps, and tracking features in a single pass.
- Backbone: DINOv2 patch encoder + L Alternating-Attention (AA) blocks, each interleaving FrameAttention (per-view) and GlobalAttention (across all views).
- FGQ is implemented on top of **FlatQuant** [Sun et al., 2025b], a learnable affine transformation PTQ backbone; FGQ only changes the calibration objective.

### Why task-aware quantization

- **Normalized Performance Degradation (NPD)** for task k at bit-width b: `NPD_k(b) = (Metric_k(b) − Metric_k(FP16)) / Metric_k(FP16) × 100%`.
- Under W4A4, camera pose estimation stays relatively robust, while point map reconstruction collapses with an NPD of **200% ∼ 500%** (원논문 Fig. 2, per-task NPD 값은 그림 내 표기, 수치 미인쇄).
- Per-block and per-channel quantization-loss profiles differ markedly between the camera and depth tasks (원논문 Fig. 3(a)(b), 수치 미인쇄), motivating a task-aware design.

### Fisher information as a Hessian surrogate

- A second-order Taylor expansion assigns a task-specific cost to each perturbation direction; the Hessian is replaced by an empirical Fisher via the conditional Hessian–Fisher (Bartlett) identity (proved in Appendix A).
- Only the **diagonal** empirical Fisher `F_k[l,c]` is kept, reducing storage from O(C²) to O(C).
- The Fisher-predicted loss correlates strongly with the empirically measured loss across blocks under W4A4, with Pearson correlation **r = 0.88** (원논문 Fig. 3(c)).

### Fisher-guided calibration loss

- Per-task Fisher scores are normalized by their global mean, summed with equal task weights, and normalized per block to mean weight 1, with a small floor `w_l[c] ← max(w_l[c], 0.01)` so low-Fisher channels are never fully ignored.
- The uniform block-output reconstruction loss is replaced by a Fisher-weighted reconstruction loss `L_FGQ`.

### Implementation notes (Appendix B)

- Diagonal **activation** Fisher (not parameter Fisher); estimated once before calibration and kept fixed. Fisher tensor shape **3 × 48 × 1024** (tasks × blocks × channels).
- VGGT has **48 calibrated aggregator blocks** (frame_0, global_0, …, frame_23, global_23); hidden channel dimension **1024**.
- Default W4A4: weights and activations both quantized to 4 bits (symmetric); weights per output channel, activations per token; DINOv2/patch embedding, task heads, normalization, and special tokens are not quantized.
- Calibration: Co3Dv2 source, 64 clips × 4 frames, batch size 2 clips, seed 42, AdamW, 15 epochs/block ⇒ 480 optimizer steps/block ⇒ **48 × 480 = 23040** total optimizer steps; also reported under W4A8.
- Generalization: FGQ is additionally extended to the **π³** model [Wang et al., 2025b] (Appendix D).

## 📊 Results

All results are on VGGT-1.2B unless noted. FP16 is the full-precision reference; FGQ is built on FlatQuant. "Best in bold" follows the paper.

### Camera pose estimation (Co3Dv2 + Re10K)

원논문 Table 1. AUC@N은 누적 오차 곡선 아래 면적, 높을수록 좋다(↑).

| Method    | W/A   | Co3D @30↑ | Co3D @15↑ | Co3D @5↑ | Co3D @3↑ | Re10K @30↑ | Re10K @15↑ | Re10K @5↑ | Re10K @3↑ |
| --------- | ----- | --------- | --------- | -------- | -------- | ---------- | ---------- | --------- | --------- |
| FP16      | 16/16 | 0.9731    | 0.9462    | 0.8462   | 0.7630   | 0.8667     | 0.7818     | 0.5803    | 0.4688    |
| RTN       | 4/8   | 0.9619    | 0.9238    | 0.7822   | 0.6691   | 0.8483     | 0.7514     | 0.5318    | 0.4158    |
| QuaRot    | 4/8   | 0.9672    | 0.9343    | 0.8098   | 0.7032   | 0.8480     | 0.7537     | 0.5307    | 0.4038    |
| FlatQuant | 4/8   | 0.9674    | 0.9351    | 0.8051   | 0.7191   | 0.8481     | 0.7543     | 0.5262    | 0.3958    |
| QuantVGGT | 4/8   | 0.9684    | 0.9363    | 0.8127   | 0.7117   | 0.8516     | 0.7587     | 0.5379    | 0.4125    |
| FGQ       | 4/8   | 0.9686    | 0.9371    | 0.8185   | 0.7230   | 0.8566     | 0.7651     | 0.5485    | 0.4318    |
| RTN       | 4/4   | 0.6547    | 0.3950    | 0.0474   | 0.0123   | 0.4334     | 0.2520     | 0.0590    | 0.0224    |
| QuaRot    | 4/4   | 0.8169    | 0.6471    | 0.2252   | 0.0904   | 0.5722     | 0.3952     | 0.1381    | 0.0663    |
| FlatQuant | 4/4   | 0.9295    | 0.8648    | 0.6405   | 0.4691   | 0.7240     | 0.5849     | 0.3233    | 0.2169    |
| QuantVGGT | 4/4   | 0.9387    | 0.8840    | 0.6973   | 0.5419   | 0.7703     | 0.6437     | 0.3845    | 0.2710    |
| FGQ       | 4/4   | 0.9425    | 0.8887    | 0.7025   | 0.5575   | 0.7704     | 0.6443     | 0.3898    | 0.2756    |

Under W4A8 this task is relatively robust; FGQ gives the best overall Re10K and competitive Co3Dv2. Under W4A4 FGQ is on par with or better than baselines; the paper notes the pose gain is modest compared with the dense tasks below.

### Point map reconstruction — 7-Scenes

원논문 Table 2. Acc는 정확도(↓), Comp는 완전성(↓), N.C.는 normal consistency(↑). mean/med 병기.

| Method    | W/A   | Acc mean↓ | Acc med↓ | Comp mean↓ | Comp med↓ | N.C. mean↑ | N.C. med↑ |
| --------- | ----- | --------- | -------- | ---------- | --------- | ---------- | --------- |
| FP16      | 16/16 | 0.044     | 0.024    | 0.056      | 0.033     | 0.733      | 0.846     |
| RTN       | 4/8   | 0.046     | 0.027    | 0.060      | 0.037     | 0.729      | 0.839     |
| QuaRot    | 4/8   | 0.047     | 0.027    | 0.056      | 0.033     | 0.736      | 0.848     |
| FlatQuant | 4/8   | 0.045     | 0.025    | 0.055      | 0.031     | 0.732      | 0.845     |
| QuantVGGT | 4/8   | 0.044     | 0.025    | 0.056      | 0.033     | 0.729      | 0.840     |
| FGQ       | 4/8   | 0.043     | 0.024    | 0.055      | 0.031     | 0.736      | 0.848     |
| RTN       | 4/4   | 0.146     | 0.103    | 0.134      | 0.086     | 0.600      | 0.655     |
| QuaRot    | 4/4   | 0.107     | 0.079    | 0.165      | 0.128     | 0.663      | 0.749     |
| FlatQuant | 4/4   | 0.056     | 0.036    | 0.070      | 0.047     | 0.717      | 0.824     |
| QuantVGGT | 4/4   | 0.053     | 0.032    | 0.085      | 0.059     | 0.719      | 0.828     |
| FGQ       | 4/4   | 0.048     | 0.031    | 0.059      | 0.036     | 0.723      | 0.832     |

Under W4A4, FGQ reduces mean completeness error from 0.085 (QuantVGGT) to 0.059 and mean accuracy from 0.053 to 0.048.

### Point map reconstruction — ETH3D

원논문 Table 2. Acc(↓), Comp(↓), N.C.(↑). mean/med 병기.

| Method    | W/A   | Acc mean↓ | Acc med↓ | Comp mean↓ | Comp med↓ | N.C. mean↑ | N.C. med↑ |
| --------- | ----- | --------- | -------- | ---------- | --------- | ---------- | --------- |
| FP16      | 16/16 | 0.263     | 0.167    | 0.288      | 0.167     | 0.846      | 0.947     |
| RTN       | 4/8   | 0.271     | 0.183    | 0.299      | 0.174     | 0.840      | 0.938     |
| QuaRot    | 4/8   | 0.262     | 0.174    | 0.272      | 0.161     | 0.846      | 0.951     |
| FlatQuant | 4/8   | 0.262     | 0.169    | 0.287      | 0.168     | 0.845      | 0.943     |
| QuantVGGT | 4/8   | 0.269     | 0.185    | 0.292      | 0.170     | 0.842      | 0.942     |
| FGQ       | 4/8   | 0.260     | 0.165    | 0.270      | 0.158     | 0.848      | 0.949     |
| RTN       | 4/4   | 0.944     | 0.843    | 1.339      | 0.920     | 0.603      | 0.656     |
| QuaRot    | 4/4   | 0.917     | 0.781    | 1.151      | 0.757     | 0.667      | 0.753     |
| FlatQuant | 4/4   | 0.291     | 0.193    | 0.297      | 0.173     | 0.833      | 0.935     |
| QuantVGGT | 4/4   | 0.312     | 0.206    | 0.305      | 0.180     | 0.832      | 0.937     |
| FGQ       | 4/4   | 0.275     | 0.177    | 0.279      | 0.164     | 0.834      | 0.940     |

Under W4A4, FGQ improves mean accuracy from 0.312 (QuantVGGT) to 0.275 and mean completeness from 0.305 to 0.279.

### Point map reconstruction — DTU

원논문 Table 3. Acc(↓), Comp(↓), N.C.(↑). mean/med 병기.

| Method    | W/A   | Acc mean↓ | Acc med↓ | Comp mean↓ | Comp med↓ | N.C. mean↑ | N.C. med↑ |
| --------- | ----- | --------- | -------- | ---------- | --------- | ---------- | --------- |
| FP16      | 16/16 | 1.308     | 0.761    | 1.929      | 1.015     | 0.665      | 0.750     |
| RTN       | 4/8   | 1.363     | 0.786    | 1.904      | 0.976     | 0.669      | 0.753     |
| QuaRot    | 4/8   | 1.401     | 0.815    | 1.899      | 0.978     | 0.668      | 0.754     |
| FlatQuant | 4/8   | 1.429     | 0.840    | 1.910      | 0.977     | 0.665      | 0.752     |
| QuantVGGT | 4/8   | 1.292     | 0.752    | 1.944      | 1.007     | 0.667      | 0.753     |
| FGQ       | 4/8   | 1.287     | 0.742    | 1.881      | 0.965     | 0.675      | 0.762     |
| RTN       | 4/4   | 7.987     | 5.648    | 4.355      | 2.593     | 0.657      | 0.731     |
| QuaRot    | 4/4   | 3.470     | 2.107    | 2.145      | 1.077     | 0.665      | 0.750     |
| FlatQuant | 4/4   | 1.478     | 0.829    | 1.895      | 0.982     | 0.667      | 0.754     |
| QuantVGGT | 4/4   | 1.488     | 0.837    | 1.933      | 1.001     | 0.669      | 0.756     |
| FGQ       | 4/4   | 1.420     | 0.801    | 1.879      | 0.965     | 0.669      | 0.757     |

Under W4A4, FGQ gives the best accuracy, completeness, and normal consistency among the quantized methods (N.C. mean ties QuantVGGT at 0.669).

### Depth estimation — KITTI (monocular + video)

원논문 Table 4. AbsRel/SqRel/RMSE는 낮을수록 좋고(↓), δ<1.25는 높을수록 좋다(↑).

| Method    | W/A   | Mono AbsRel↓ | Mono SqRel↓ | Mono RMSE↓ | Mono δ↑ | Vid AbsRel↓ | Vid SqRel↓ | Vid RMSE↓ | Vid δ↑ |
| --------- | ----- | ------------ | ----------- | ---------- | ------- | ----------- | ---------- | --------- | ------ |
| FP16      | 16/16 | 0.092        | 0.459       | 3.902      | 0.936   | 0.058       | 0.373      | 3.618     | 0.961  |
| RTN       | 4/8   | 0.093        | 0.453       | 3.903      | 0.936   | 0.058       | 0.348      | 3.500     | 0.964  |
| QuaRot    | 4/8   | 0.087        | 0.443       | 3.897      | 0.943   | 0.059       | 0.364      | 3.642     | 0.963  |
| FlatQuant | 4/8   | 0.087        | 0.410       | 3.623      | 0.946   | 0.052       | 0.314      | 3.350     | 0.968  |
| QuantVGGT | 4/8   | 0.091        | 0.462       | 3.931      | 0.936   | 0.054       | 0.339      | 3.450     | 0.967  |
| FGQ       | 4/8   | 0.086        | 0.396       | 3.566      | 0.947   | 0.051       | 0.292      | 3.240     | 0.970  |
| RTN       | 4/4   | 0.148        | 0.728       | 5.159      | 0.823   | 0.164       | 0.985      | 5.615     | 0.748  |
| QuaRot    | 4/4   | 0.117        | 0.487       | 4.083      | 0.903   | 0.126       | 0.713      | 4.896     | 0.838  |
| FlatQuant | 4/4   | 0.084        | 0.399       | 3.650      | 0.948   | 0.062       | 0.339      | 3.488     | 0.960  |
| QuantVGGT | 4/4   | 0.088        | 0.446       | 3.842      | 0.938   | 0.058       | 0.336      | 3.486     | 0.963  |
| FGQ       | 4/4   | 0.079        | 0.389       | 3.642      | 0.951   | 0.056       | 0.313      | 3.384     | 0.965  |

FGQ is best across all metrics under W4A8. Under W4A4 it obtains the best AbsRel, SqRel, and δ on KITTI Mono and the best error metrics on KITTI Video (on Mono RMSE, FlatQuant 3.650 vs FGQ 3.642).

### Ablation — Fisher task composition (Table 5)

원논문 Table 5. Co3Dv2는 카메라 포즈(AUC@15↑), DTU는 point map(Acc. mean↓) 평가.

| Fisher Info. (Co3Dv2)  | AUC@15↑ | Fisher Info. (DTU)     | Acc. mean↓ |
| ---------------------- | ------- | ---------------------- | ---------- |
| plain (w/o Fisher)     | 0.8825  | plain (w/o Fisher)     | 1.537      |
| point                  | 0.8868  | camera                 | 1.465      |
| point + depth          | 0.8875  | camera + depth         | 1.458      |
| point + depth + camera | 0.8952  | camera + depth + point | 1.446      |

Fisher weighting helps most when it includes the task aligned with the evaluation metric; multi-task Fisher gives the largest gains.

### Calibration overhead (Table 6 / Appendix C)

원논문 Table 6. base 값만 표기(빨간 증감값은 산문에 서술).

| Method                   | GPU mem (GB) | GPU time (h) | AUC@15 (Co3Dv2)↑ | DTU Acc. mean↓ |
| ------------------------ | ------------ | ------------ | ---------------- | -------------- |
| FP16                     | –            | –            | 0.9462           | 1.308          |
| Baseline PTQ (FlatQuant) | 3.54         | 0.87         | 0.8825           | 1.537          |
| FGQ (Ours)               | 3.62         | 0.92         | 0.8952           | 1.446          |

Appendix C: on a single A100 40GB, a representative W4A4 run takes 52.53 min for FlatQuant vs 55.54 min for FGQ (+3.01 min ≈ 5.73%), and peak memory 3.54 GB vs 3.62 GB (+0.08 GB ≈ 2.26%).

### Efficiency — real vs fake W4A4 (Figure 4)

원논문 Figure 4의 값이 본문에도 인쇄돼 있어 옮긴다. 배속은 fake quantization 대비 정규화 speedup.

- Parameter (data) loading: RTN 3.41×, FGQ 3.42× (both benefit from 4-bit weight/activation storage).
- Compute kernel: RTN 6.01×, FGQ 4.67× (gap from FGQ's extra affine transformation).
- Full block level (Overall): RTN 2.01×, FGQ 1.81×.

### Generalization to π³ (Appendix D)

원논문 Table 7 (상단: camera pose). AUC 모두 높을수록 좋다(↑). 4/4 설정.

| Method    | W/A   | Co3D @30↑ | Co3D @15↑ | Co3D @5↑ | Co3D @3↑ | Re10K @30↑ | Re10K @15↑ | Re10K @5↑ | Re10K @3↑ |
| --------- | ----- | --------- | --------- | -------- | -------- | ---------- | ---------- | --------- | --------- |
| FP16      | 16/16 | 0.9441    | 0.8882    | 0.6811   | 0.5140   | 0.8907     | 0.8212     | 0.6511    | 0.5523    |
| RTN       | 4/4   | 0.7684    | 0.5491    | 0.0954   | 0.0246   | 0.5662     | 0.4040     | 0.1538    | 0.0740    |
| FlatQuant | 4/4   | 0.9119    | 0.8240    | 0.5022   | 0.2686   | 0.8298     | 0.7317     | 0.5204    | 0.4142    |
| FGQ       | 4/4   | 0.9394    | 0.8795    | 0.6711   | 0.5032   | 0.8436     | 0.7502     | 0.5517    | 0.4461    |

원논문 Table 7 (하단: point map, mean 값만). Acc/Comp는 낮을수록(↓), N.C.는 높을수록 좋다(↑). med 값은 원논문 참조.

| Method    | W/A   | DTU Acc mean↓ | DTU Comp mean↓ | DTU N.C. mean↑ | ETH3D Acc mean↓ | ETH3D Comp mean↓ | ETH3D N.C. mean↑ |
| --------- | ----- | ------------- | -------------- | -------------- | --------------- | ---------------- | ---------------- |
| FP16      | 16/16 | 1.138         | 1.926          | 0.662          | 0.188           | 0.211            | 0.884            |
| RTN       | 4/4   | 7.744         | 19.290         | 0.585          | 1.353           | 2.030            | 0.589            |
| FlatQuant | 4/4   | 1.396         | 1.917          | 0.662          | 0.197           | 0.217            | 0.870            |
| FGQ       | 4/4   | 1.358         | 1.878          | 0.663          | 0.193           | 0.215            | 0.874            |

On π³ under 4/4, FGQ raises Co3Dv2 AUC@3 from 0.2686 (FlatQuant) to 0.5032, approaching FP16's 0.5140, and tracks FP16 closely on point maps (DTU Acc. mean 1.358 vs FP16 1.138; ETH3D N.C. mean 0.874 vs FP16 0.884).

## 💡 Insights & Impact

- **Shared backbone, unequal sensitivity**: The core observation is that a shared multi-task backbone routes depth, pose, and point-map predictions through the same parameters, yet each task tolerates quantization noise very differently — point map reconstruction is by far the most fragile (NPD 200%∼500% at W4A4).
- **Fisher is a cheap, accurate sensitivity proxy**: A diagonal empirical Fisher, computed once with a single backward pass per task, predicts measured quantization loss with r = 0.88 while reducing storage from O(C²) to O(C).
- **Objective-only change**: FGQ modifies only the calibration loss of an existing affine-transform PTQ backbone (FlatQuant), adding ≈5.73% calibration time and ≈2.26% peak memory — practically free.
- **Largest gains where it hurts most**: Improvements concentrate on dense geometric tasks (point map, depth) rather than the globally-pooled pose task, which is consistent with the sensitivity analysis.
- **Deployment framing**: Motivated by on-device 3D perception for AR/VR, robotics, and autonomous driving where billion-parameter feed-forward models are otherwise too costly.

## 🔗 Related Work

- **Quantized model** — [VGGT](../reconstruction/vggt.md): the feed-forward 3D transformer that FGQ quantizes (VGGT-1.2B, 48 aggregator blocks).
- **Direct PTQ baseline** — [QuantVGGT](../reconstruction/quantvggt.md) [Feng et al., 2025]: the prior VGGT-specific PTQ method addressing special-token activation outliers; FGQ's main comparison point.
- **Generalization target** — [π³](../reconstruction/pi3.md) [Wang et al., 2025b]: FGQ is additionally validated on this more recent feed-forward 3D model (Appendix D).
- **Efficient VGGT (token merging), cited** — [FastVGGT](../reconstruction/fastvggt.md) [Shen et al., 2025] and [LiteVGGT](../reconstruction/litevggt.md) [Shu et al., 2025]: orthogonal efficiency methods that fuse redundant tokens rather than quantize.
- **Lineage** — [DUSt3R](dust3r.md) and [MASt3R](mast3r.md): the feed-forward 3D reconstruction family that VGGT and this quantization line build upon.

FGQ's quantization backbone derives from LLM PTQ: QuaRot (fixed Hadamard rotation), SpinQuant (learned rotations), and FlatQuant (learnable per-layer affine transformations) — the last serving as FGQ's base method.

## 📚 Key Takeaways

1. **Not all tasks quantize equally**: In a shared-backbone feed-forward 3D model, point map reconstruction degrades far more under 4-bit quantization than camera pose, so treating all tasks uniformly over-protects insensitive tasks and sacrifices sensitive ones.
2. **Fisher-guided calibration**: A diagonal empirical Fisher (tensor 3 × 48 × 1024 for VGGT) yields per-task/block/channel weights folded into a learnable affine transformation, preserving the channels most critical to each task.
3. **Consistent 4-bit wins**: FGQ matches or beats RTN, QuaRot, FlatQuant, and QuantVGGT across camera pose (Co3Dv2/Re10K), point map (7-Scenes/ETH3D/DTU), and depth (KITTI), with up to 39% relative improvement and the largest gains on dense point-map reconstruction.
4. **Nearly free and transferable**: Only the calibration objective changes; overhead is ≈5.73% time / ≈2.26% memory, and the method transfers to π³ under aggressive W4A4 quantization.

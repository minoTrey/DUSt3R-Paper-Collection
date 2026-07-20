# STream3R: Scalable Sequential 3D Reconstruction with Causal Transformer (ICLR 2026)

## 📋 Overview

- **Authors**: Yushi Lan, Yihang Luo, Fangzhou Hong, Shangchen Zhou, Honghua Chen, Zhaoyang Lyu, Shuai Yang, Bo Dai, Chen Change Loy, Xingang Pan
- **Institution**: S-Lab, Nanyang Technological University; Shanghai Artificial Intelligence Laboratory; WICT, Peking University; The University of Hong Kong
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2508.10893) | [Project Page](https://nirvanalan.github.io/projects/stream3r)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Reformulates pointmap prediction as a decoder-only causal transformer problem, caching past-frame features as context so streaming reconstruction inherits KV-cache efficiency and LLM-style training infrastructure.

## 🎯 Key Contributions

1. **Causal attention for 3D reconstruction**: each incoming frame cross-attends to cached features of all previous frames, replacing both bidirectional global attention and fixed-size RNN state.
2. **Decoder-only design**: DUSt3R's symmetric two-decoder structure collapses to a single decoder handling arbitrary view counts.
3. **KV-cache compatibility**: the causal formulation is directly optimized by standard LLM inference machinery.
4. **Two initializations**: STream3Rα fine-tuned from DUSt3R weights, STream3Rβ from VGGT with SelfAttn in Global Attention replaced by CausalAttn.
5. **Sliding-window variant**: STream3Rβ-W[5] uses sliding-window attention for constant cache size.
6. **Demonstrated convergence advantage**: at matched compute and initialization, the decoder-only design converges faster than the RNN-based CUT3R architecture.

## 🔧 Technical Details

### Causal Decoding

After frame-wise self-attention in each decoder block, the current feature cross-attends to same-layer features of all previously observed frames:

```text
G_t^i = DecoderBlock^i( G_t^{i-1}, G_0^{i-1} ⊕ G_1^{i-1} ⊕ ⋯ ⊕ G_{t-1}^{i-1} )
```

The first two frames follow the DUSt3R convention because there is no historical context yet; every frame afterwards uses the causal operation. A learnable register token `[reg]` is added element-wise to the first frame's tokens to designate the canonical world space — this is what lets a single decoder emit global points without N separate decoders. No positional embedding is imposed on other frames.

### Prediction Heads

Three heads consume the full stack of decoder features `(G_t^0, …, G_t^B)`:

- `Head_local` → local pointmap `X̂_t^local` in the viewing camera's frame, plus confidence
- `Head_global` → global pointmap `X̂_t^global` in the first image's frame, plus confidence
- `Head_pose` → `P̂_t ∈ R⁹` (intrinsics and extrinsics)

This redundancy is retained because prior work showed it simplifies training and enables use of partially annotated 3D datasets such as single-view depth data.

### Losses

Confidence-aware pointmap regression following DUSt3R:

```text
L_conf = Σ ĉ · ‖x̂/ŝ − x/s‖₂ − α log ĉ
```

with `ŝ := s` on metric-scale datasets to enable metric pointmaps, plus an L2 pose loss over quaternion, scale-normalized translation, and focal length.

### Implementation

- **STream3Rα**: 24-layer CroCo ViT encoder; DUSt3R's 12-layer decoder retrofitted to retain only `Decoder¹`; DPT-L heads
- **STream3Rβ**: VGGT with CausalAttn substituted, all parameters fine-tuned
- QK-Norm injected per transformer layer; FlashAttention with BFloat16 mixed precision
- AdamW, batch size 64, LR 1e-4, 400K iterations, 4–10 frames sampled per batch
- Resolutions from 224 × 224 to 512 × 384; 8 × A100 over seven days with gradient checkpointing

The paper notes it trains end-to-end for only 7 epochs on a subset of CUT3R's datasets, against CUT3R's four-stage curriculum of 100 + 35 + 40 + 10 = 185 epochs.

## 📊 Results

### Single-Frame Depth

원논문 Table 1. Abs Rel은 낮을수록, δ<1.25는 높을수록 좋다.

| Method    | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ |
| --------- | ---------------- | --------------- | -------------- | ------------- |
| VGG-T     | 0.271            | 67.7            | **0.053**      | **97.3**      |
| Fast3R    | 0.502            | 52.8            | 0.192          | 77.3          |
| DUSt3R    | 0.424            | 58.7            | 0.141          | 82.5          |
| MASt3R    | 0.340            | 60.4            | 0.142          | 82.0          |
| MonST3R   | 0.358            | 54.8            | 0.076          | 93.9          |
| Spann3R   | 0.470            | 53.9            | 0.118          | 85.9          |
| CUT3R     | 0.428            | 55.4            | 0.063          | 96.2          |
| STream3Rα | 0.350            | 59.0            | 0.075          | 93.4          |
| STream3Rβ | **0.228**        | **70.7**        | 0.061          | 96.7          |

원논문 Table 1 (계속).

| Method    | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ | NYU-v2 Abs Rel ↓ | NYU-v2 δ<1.25 ↑ |
| --------- | --------------- | -------------- | ---------------- | --------------- |
| VGG-T     | 0.076           | 93.3           | 0.060            | 94.8            |
| Fast3R    | 0.129           | 81.2           | 0.099            | 88.9            |
| DUSt3R    | 0.112           | 86.3           | 0.080            | 90.7            |
| MASt3R    | 0.079           | 94.7           | 0.129            | 84.9            |
| MonST3R   | 0.100           | 89.3           | 0.102            | 88.0            |
| Spann3R   | 0.128           | 84.6           | 0.122            | 84.9            |
| CUT3R     | 0.092           | 91.3           | 0.086            | 90.9            |
| STream3Rα | 0.088           | 91.3           | 0.091            | 89.9            |
| STream3Rβ | **0.063**       | **95.5**       | **0.057**        | **95.7**        |

Bonn is the one dataset where VGG-T holds the lead. STream3Rβ takes Sintel, KITTI, and NYU-v2.

### Video Depth — Per-Sequence Scale Alignment

원논문 Table 2. Type은 Optim(최적화 기반), Stream(스트리밍), FA(full attention).
FPS는 KITTI에서 512×144 해상도, A100 기준. Spann3R만 224×224 스트림 입력을 사용한다.

| Method         | Type   | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ | FPS       |
| -------------- | ------ | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- | --------- |
| VGG-T          | FA     | 0.297            | 68.8            | **0.055**      | **97.1**      | 0.073           | **96.5**       | 7.32      |
| Fast3R         | FA     | 0.653            | 44.9            | 0.193          | 77.5          | 0.140           | 83.4           | 47.23     |
| DUSt3R-GA      | Optim  | 0.656            | 45.2            | 0.155          | 83.3          | 0.144           | 81.3           | 0.76      |
| MASt3R-GA      | Optim  | 0.641            | 43.9            | 0.252          | 70.1          | 0.183           | 74.5           | 0.31      |
| MonST3R-GA     | Optim  | 0.378            | 55.8            | 0.067          | 96.3          | 0.168           | 74.4           | 0.35      |
| Spann3R        | Stream | 0.622            | 42.6            | 0.144          | 81.3          | 0.198           | 73.7           | 13.55     |
| CUT3R          | Stream | 0.421            | 47.9            | 0.078          | 93.7          | 0.118           | 88.1           | 16.58     |
| STream3Rα      | Stream | 0.478            | 51.1            | 0.075          | 94.1          | 0.116           | 89.6           | 23.48     |
| STream3Rβ      | Stream | **0.264**        | **70.5**        | 0.069          | 95.2          | 0.080           | 94.7           | 12.95     |
| STream3Rβ-W[5] | Stream | 0.279            | 68.6            | 0.064          | 96.7          | **0.083**       | 95.2           | **32.93** |

The sliding-window variant, seeing only five past frames, actually beats full STream3Rβ on Bonn and KITTI while running at the highest FPS among streaming methods. VGG-T remains best on Bonn.

### Video Depth — Metric Scale

원논문 Table 2 (계속). 정렬 없이 metric scale로 평가.

| Method    | Type   | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| --------- | ------ | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| MASt3R-GA | Optim  | 1.022            | 14.3            | 0.272          | 70.6          | 0.467           | 15.2           |
| CUT3R     | Stream | **1.029**        | **23.8**        | 0.103          | 88.5          | **0.122**       | **85.5**       |
| STream3Rα | Stream | 1.041            | 21.0            | **0.084**      | **94.4**      | 0.234           | 57.6           |

In the metric-scale setting STream3Rα loses to CUT3R on Sintel and badly on KITTI (0.234 vs 0.122). Only STream3Rα is reported here.

### 3D Reconstruction on 7-Scenes

원논문 Table 3. Acc·Comp는 낮을수록, NC는 높을수록 좋다. 장면당 3–5 프레임의 희소 샘플링.
STream3Rβ-FA는 학습된 모델의 causal attention을 full attention으로 바꾼 것.

| Method       | Type   | Acc Mean ↓ | Acc Med. ↓ | Comp Mean ↓ | Comp Med. ↓ | NC Mean ↑ | NC Med. ↑ | FPS   |
| ------------ | ------ | ---------- | ---------- | ----------- | ----------- | --------- | --------- | ----- |
| VGG-T        | FA     | **0.087**  | **0.039**  | 0.091       | **0.039**   | **0.787** | **0.890** | 12.0  |
| Fast3R       | FA     | 0.164      | 0.108      | 0.163       | 0.080       | 0.686     | 0.775     | 30.92 |
| DUSt3R-GA    | Optim  | 0.146      | 0.077      | 0.181       | 0.067       | 0.736     | 0.839     | 0.68  |
| MASt3R-GA    | Optim  | 0.185      | 0.081      | 0.180       | 0.069       | 0.701     | 0.792     | 0.34  |
| MonST3R-GA   | Optim  | 0.248      | 0.185      | 0.266       | 0.167       | 0.672     | 0.759     | 0.39  |
| STream3Rβ-FA | Stream | 0.091      | 0.043      | **0.075**   | 0.042       | 0.769     | 0.879     | 12.0  |
| Spann3R      | Stream | 0.298      | 0.226      | 0.205       | 0.112       | 0.650     | 0.730     | 12.97 |
| SLAM3R       | Stream | 0.287      | 0.155      | 0.226       | 0.066       | 0.644     | 0.720     | 38.40 |
| CUT3R        | Stream | 0.126      | 0.047      | 0.154       | 0.031       | 0.727     | 0.834     | 17.00 |
| STream3Rα    | Stream | 0.148      | 0.077      | 0.177       | 0.058       | 0.700     | 0.801     | 26.4  |
| STream3Rβ    | Stream | 0.122      | 0.044      | 0.110       | 0.038       | 0.746     | 0.856     | 20.12 |

CUT3R retains the best completion median at 0.031. VGG-T leads accuracy and normal consistency; the STream3Rβ-FA variant matches it and exceeds it on completion mean.

### Camera Pose Estimation

원논문 Table 4. Sim(3) 정렬 후 ATE, RPE_trans, RPE_rot. 모두 낮을수록 좋다.

| Method       | Type  | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | TUM-dyn ATE ↓ | TUM-dyn RPE trans ↓ | TUM-dyn RPE rot ↓ |
| ------------ | ----- | ------------ | ------------------ | ---------------- | ------------- | ------------------- | ----------------- |
| Particle-SfM | Optim | 0.129        | **0.031**          | **0.535**        | —             | —                   | —                 |
| Robust-CVD   | Optim | 0.360        | 0.154              | 3.443            | 0.153         | 0.026               | 3.528             |
| CasualSAM    | Optim | 0.141        | 0.035              | 0.615            | 0.071         | 0.010               | 1.712             |
| DUSt3R-GA    | Optim | 0.417        | 0.250              | 5.796            | 0.083         | 0.017               | 3.567             |
| MASt3R-GA    | Optim | 0.185        | 0.060              | 1.496            | 0.038         | **0.012**           | 0.448             |
| MonST3R-GA   | Optim | **0.111**    | 0.044              | 0.869            | 0.098         | 0.019               | 0.935             |
| DUSt3R       | Onl   | 0.290        | 0.132              | 7.869            | 0.140         | 0.106               | 3.286             |
| Spann3R      | Onl   | 0.329        | 0.110              | 4.471            | 0.056         | 0.021               | 0.591             |
| CUT3R        | Onl   | 0.213        | **0.066**          | **0.621**        | 0.046         | 0.015               | 0.473             |
| STream3Rβ    | Onl   | 0.213        | 0.076              | 0.868            | **0.026**     | 0.013               | **0.330**         |

원논문 Table 4 (계속). ScanNet.

| Method       | Type  | ATE ↓     | RPE trans ↓ | RPE rot ↓ |
| ------------ | ----- | --------- | ----------- | --------- |
| Particle-SfM | Optim | 0.136     | 0.023       | 0.836     |
| Robust-CVD   | Optim | 0.227     | 0.064       | 7.374     |
| CasualSAM    | Optim | 0.158     | 0.034       | 1.618     |
| DUSt3R-GA    | Optim | 0.081     | 0.028       | 0.784     |
| MASt3R-GA    | Optim | 0.078     | 0.020       | **0.475** |
| MonST3R-GA   | Optim | 0.077     | **0.018**   | 0.529     |
| DUSt3R       | Onl   | 0.246     | 0.108       | 8.210     |
| Spann3R      | Onl   | 0.096     | 0.023       | 0.661     |
| CUT3R        | Onl   | 0.099     | 0.022       | 0.600     |
| STream3Rβ    | Onl   | **0.052** | 0.021       | 0.850     |

The paper is candid that optimization-based systems still achieve the lowest errors overall on Sintel; STream3R's claim is being strongest among streaming approaches, and it surpasses CUT3R on TUM-dynamics and ScanNet ATE while losing on ScanNet RPE rot.

### Ablation: Causal Transformer vs RNN

원논문 Table 5. 동일한 데이터셋, MASt3R 사전학습 가중치 초기화, 동일 하이퍼파라미터·컴퓨트,
224×224 해상도, 동일 iteration 수에서 학습한 체크포인트로 평가.

| Method    | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | BONN Abs Rel ↓ | BONN δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| --------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| CUT3R     | 0.598            | 40.7            | 0.102          | 90.7          | 0.157           | 77.4           |
| STream3Rα | **0.535**        | **47.0**        | **0.083**      | **94.2**      | **0.141**       | **81.8**       |

원논문 Table 6. 동일 조건, 7-Scenes 3D 재구성.

| Method    | Acc Mean ↓ | Acc Med. ↓ | Comp Mean ↓ | Comp Med. ↓ | NC Mean ↑ | NC Med. ↑ |
| --------- | ---------- | ---------- | ----------- | ----------- | --------- | --------- |
| CUT3R     | 0.480      | 0.365      | 0.330       | 0.148       | 0.555     | 0.583     |
| STream3Rα | **0.328**  | **0.261**  | **0.255**   | **0.095**   | **0.605** | **0.659** |

The training curves show `Head_local` converging similarly for both architectures while `Head_global` converges noticeably faster for the causal design — the paper's explanation is that CUT3R's single state makes registering incoming frames harder.

## 💡 Insights & Impact

### Attending to a Longer Context Can Be Faster

The counterintuitive result the paper draws attention to: STream3R attends to all cached past frames, CUT3R attends to one constant-size state, and yet STream3R completes 60% more training steps in the same wall clock. The reason is that CUT3R's RNN requires a state-update operation after every state-readout interaction, whereas causal attention just reads cached features.

### Borrowing the LLM Stack

Framing pointmap prediction as decoder-only next-token prediction is not merely an analogy — it makes KV caching, FlashAttention, QK-Norm, and sliding-window attention all directly applicable. This is the paper's argument for why the design will keep improving without further 3D-specific research.

### Causal Attention Costs Surprisingly Little

Swapping the trained model's causal attention for full attention at inference (STream3Rβ-FA) produces results comparable to VGG-T and better completion mean. The gap between streaming and offline reconstruction is therefore mostly an architectural choice, not an inherent limit of causal processing.

### Five Frames of Context Can Be Enough

STream3Rβ-W[5] beats the unbounded-context STream3Rβ on Bonn and KITTI depth despite accessing only five past frames, while running at the highest streaming FPS. For many sequences, long-range context is apparently not where the accuracy comes from.

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The primary comparison and the RNN design STream3R argues against. Both the retrained ablation and the main tables target it; CUT3R still holds the best completion median on 7-Scenes and better metric-scale KITTI depth.
- **[DUSt3R](../foundation/dust3r.md)**: STream3Rα's initialization and the source of the confidence-aware pointmap loss. Its symmetric two-decoder design is the specific structure STream3R removes.
- **[VGGT](vggt.md)**: STream3Rβ's initialization — the SelfAttn layers in Global Attention are replaced by CausalAttn and everything is fine-tuned. Also the reference bidirectional baseline it must justify itself against.
- **[MASt3R](../foundation/mast3r.md)**: Used for the metric-scale supervision convention and as the initialization for all ablation runs.
- **[Fast3R](fast3r.md)**: The full-attention many-view baseline; STream3R outperforms it while remaining streaming.
- **[Spann3R](spann3r.md)**: The fixed-size memory approach STream3R characterizes as scaling poorly with sequence length.
- **[MonST3R](../dynamic/monst3r.md)**: The optical-flow-dependent dynamic-scene optimization baseline that STream3R surpasses under per-sequence scale alignment.

## 📚 Key Takeaways

1. **Causal attention is a viable third option**: neither bidirectional global attention nor a fixed-size recurrent state, but cached context with KV-cache efficiency.
2. **A learnable register token defines world space**: one decoder can emit global pointmaps for arbitrary view counts without per-view decoders.
3. **Decoder-only converges faster than RNN**: at matched data, initialization, and compute, the causal design wins every ablation metric and completes more steps.
4. **Sliding windows are surprisingly competitive**: five frames of context, the fastest streaming FPS, and better Bonn/KITTI depth than unbounded context.
5. **Honest gaps remain**: optimization-based methods still lead Sintel pose overall, VGG-T leads Bonn depth and 7-Scenes accuracy, and the metric-scale setting is where STream3Rα is weakest.

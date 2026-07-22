# LONG3R: Long Sequence Streaming 3D Reconstruction (ICCV 2025)

![long3r — architecture](https://arxiv.org/html/2507.18255/x2.png)

_(a) Main Architecture. (원논문 Fig. 99)_

## 📋 Overview

- **Authors**: Zhuoguang Chen, Minghui Qin, Tianyuan Yuan, Zhe Liu, Hang Zhao
- **Institution**: Shanghai Artificial Intelligence Laboratory, IIIS Tsinghua University, Shanghai Qi Zhi Institute
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2507.18255) | [Project Page](https://zgchen33.github.io/LONG3R/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A recurrent streaming reconstruction model that keeps a pruned 3D spatio-temporal memory, gates it per frame, and refines predictions with an interleaved dual-source decoder, so quality degrades gracefully over hundreds of frames at real-time speed.

## 🎯 Key Contributions

1. **Memory Gating & Dual-Source Refined Decoder**: A gating mechanism selectively retains memory tokens relevant to the current observation, and an interleaved dual-source decoder performs coarse-to-fine interaction between the new observation and retrieved memory.
2. **3D Spatio-Temporal Memory**: A dynamic memory that combines short-term temporal memory with a long-term 3D spatial memory, pruning redundant tokens by voxelizing 3D positions and adapting voxel resolution to scene scale.
3. **Two-Stage Curriculum Training**: Progressive sequence-length curriculum (5 frames → 10 frames → 32 frames) that adapts the model to long sequences while keeping training tractable.
4. **Long-sequence robustness**: The paper defines long-sequence reconstruction as real-time processing of tens to hundreds of frames with near-constant memory, and demonstrates it on 100- and 200-frame Replica sequences.

## 🔧 Technical Details

### Recurrent Streaming Formulation

LONG3R follows the Spann3R-style recurrent design: given a new image, the model retrieves relevant memories, interacts with the current view to predict its pointmap, and writes updated tokens back to memory. Predictions are expressed relative to the first frame.

### Memory Gating

An indicator function δ(s) keeps a memory token s only if its maximum attention weight against the current frame exceeds a threshold τ; the surviving subset forms the relevant memory `F_r_mem`. The paper reports a 27% reduction in retained memory tokens on 7Scenes.

### 3D Spatial Memory Pruning

Memory tokens are grouped into voxels by their 3D position. The image voxel size is the minimum inter-point distance in a frame, and the scene voxel size is the running average of image voxel sizes over past frames, so it updates online during streaming. Within each voxel only the token with the highest accumulated attention weight is retained.

### Dual-Source Refined Decoder

Two designs are compared (Fig. 7): a _concatenated_ variant that concatenates relevant memory with frame features, and an _interleaved_ variant that alternates cross-attention over memory and over frame features. LONG3R adopts the interleaved design, which the paper attributes to progressively aligning the two feature spaces and avoiding information loss from feature-space misalignment.

### Training

- **Loss**: `L = L_conf + L_scale` — a confidence-aware 3D regression loss plus a scale loss encouraging the predicted point cloud to have a smaller average distance than the ground truth.
- **Encoder**: ViT-Large initialized from DUSt3R's encoder weights; frozen during stage 2.
- **Stage 1**: 5 randomly sampled frames per sequence, AdamW, learning rate 1.12×10⁻⁴, batch size 10 per GPU, 120 epochs, 16 A100 GPUs for 28 hours.
- **Stage 2**: AdamW, learning rate 1×10⁻⁵, 10-view then 32-view sequences, 12 epochs each, ~20 hours on the same hardware.
- **Training data**: mixture of 6 datasets — Habitat, ARKitScenes, BlendedMVS, ScanNet++, Co3Dv2, ScanNet.
- **Inference memory**: 10-frame short-term memory plus 3000-token long-term memory.

All experiments use 224 × 224 inputs on a single NVIDIA RTX 3090 (24 GB).

## 📊 Results

### 3D Reconstruction on 7Scenes and NRGBD

원논문 Table 1. Accuracy와 Completeness는 cm 단위, 각 지표는 Mean/Med. 두 값으로 보고된다. 표가 12열을 넘어 데이터셋별로 나눈다.

| Method     | 7Scenes Acc↓ Mean | Med. | Comp↓ Mean | Med. | NC↑ Mean  | Med.      | FPS |
| ---------- | ----------------- | ---- | ---------- | ---- | --------- | --------- | --- |
| F-Recon    | 12.43             | 7.62 | 5.54       | 2.31 | 61.89     | 68.85     | ≪1  |
| DUSt3R     | 3.01              | 1.47 | 5.11       | 2.79 | 58.83     | 63.73     | ≤3  |
| MASt3R     | 2.82              | 1.56 | 5.26       | 3.24 | 58.22     | 62.46     | ≤3  |
| MV-DUSt3R  | 2.92              | 1.24 | 2.49       | 0.78 | 66.42     | 76.07     | ∼15 |
| MV-DUSt3R+ | 2.93              | 1.07 | 8.63       | 0.95 | 66.38     | 76.18     | ∼3  |
| CUT3R      | 7.73              | 3.57 | 7.75       | 1.83 | 65.74     | 73.98     | ∼23 |
| Spann3R    | 3.42              | 1.48 | 2.41       | 0.85 | 66.35     | 76.25     | ∼22 |
| **LONG3R** | **2.57**          | 1.14 | **2.08**   | 0.73 | **66.55** | **76.43** | ∼22 |

| Method     | NRGBD Acc↓ Mean | Med.  | Comp↓ Mean | Med. | NC↑ Mean | Med.  | FPS |
| ---------- | --------------- | ----- | ---------- | ---- | -------- | ----- | --- |
| F-Recon    | 28.55           | 20.59 | 15.05      | 6.31 | 65.47    | 75.77 | ≪1  |
| DUSt3R     | 3.94            | 2.48  | 5.31       | 3.58 | 62.62    | 72.29 | ≤3  |
| MASt3R     | 3.85            | 2.54  | 5.50       | 3.62 | 60.92    | 68.67 | ≤3  |
| MV-DUSt3R  | 3.76            | 1.99  | 2.55       | 0.92 | 81.16    | 95.39 | ∼15 |
| MV-DUSt3R+ | 3.47            | 1.60  | 3.69       | 0.85 | 84.33    | 97.27 | ∼3  |
| CUT3R      | 12.48           | 5.57  | 6.34       | 2.35 | 75.84    | 90.05 | ∼23 |
| Spann3R    | 6.91            | 3.15  | 2.91       | 1.10 | 77.75    | 93.71 | ∼22 |
| **LONG3R** | 6.66            | 2.54  | 3.11       | 1.21 | 77.56    | 93.08 | ∼22 |

LONG3R leads the online streaming group on 7Scenes across all three metrics. On NRGBD it improves Acc over Spann3R but is slightly behind it on Comp and NC — the paper does not claim a clean sweep there, and the offline MV-DUSt3R+ remains ahead on NC by a wide margin at ∼3 FPS.

### Long-Sequence Reconstruction on Replica

원논문 Table 2. Replica100 / Replica200은 각각 100·200 프레임을 균일 샘플링한 설정이다.

| Method     | Replica100 Acc↓ Mean | Med.  | Comp↓ Mean | Med. | NC↑ Mean  | Med.      | FPS |
| ---------- | -------------------- | ----- | ---------- | ---- | --------- | --------- | --- |
| DUSt3R     | 6.34                 | 3.99  | 6.44       | 3.68 | 61.67     | 69.27     | ≤3  |
| MASt3R     | 5.10                 | 2.96  | 6.00       | 3.43 | 61.81     | 69.52     | ≤3  |
| MV-DUSt3R  | 10.41                | 6.48  | 4.34       | 1.22 | 73.76     | 88.36     | ∼7  |
| MV-DUSt3R+ | 5.28                 | 3.26  | 2.56       | 0.89 | **79.07** | **93.63** | ∼1  |
| CUT3R      | 20.44                | 14.64 | 5.67       | 2.32 | 69.63     | 84.31     | ∼23 |
| Spann3R    | 14.08                | 8.88  | 4.67       | 1.61 | 72.46     | 88.98     | ∼21 |
| **LONG3R** | 11.46                | 7.55  | 3.68       | 1.24 | 73.29     | 89.86     | ∼21 |

| Method     | Replica200 Acc↓ Mean | Med.  | Comp↓ Mean | Med. | NC↑ Mean  | Med.      | FPS |
| ---------- | -------------------- | ----- | ---------- | ---- | --------- | --------- | --- |
| DUSt3R     | 4.99                 | 2.76  | 4.63       | 2.59 | 62.26     | 70.76     | ≤3  |
| MASt3R     | 5.26                 | 3.23  | 7.31       | 3.75 | 58.03     | 62.81     | ≤3  |
| MV-DUSt3R  | 17.02                | 11.70 | 5.10       | 1.36 | 66.74     | 78.24     | ∼7  |
| MV-DUSt3R+ | 11.79                | 8.37  | 5.64       | 1.53 | **70.66** | **83.86** | ∼1  |
| CUT3R      | 28.3                 | 20.68 | 6.61       | 1.88 | 63.95     | 73.85     | ∼23 |
| Spann3R    | 16.29                | 10.17 | 4.02       | 1.16 | 68.56     | 82.80     | ∼21 |
| **LONG3R** | 11.93                | 7.42  | **2.73**   | 0.87 | 68.67     | 82.92     | ∼21 |

The paper is explicit that post-optimization methods (DUSt3R, MASt3R) achieve higher accuracy on Replica thanks to global alignment, at the cost of much lower FPS. LONG3R's claim is that it avoids the catastrophic degradation the other online methods show as sequences lengthen — CUT3R's Replica200 Acc mean is 28.3 vs LONG3R's 11.93.

### Camera Pose Estimation

원논문 Table 3. 단위는 cm/°이며, ATE / RPEt / RPEr 모두 낮을수록 좋다.

| Method     | 7Scenes ATE | RPEt     | RPEr     | TUM ATE  | RPEt | RPEr | ScanNet ATE | RPEt     | RPEr     |
| ---------- | ----------- | -------- | -------- | -------- | ---- | ---- | ----------- | -------- | -------- |
| Spann3R    | 12.64       | 6.15     | 1.88     | 5.66     | 2.13 | 0.59 | 9.83        | 2.30     | 0.66     |
| CUT3R      | 12.40       | 7.65     | 2.34     | 6.25     | 2.55 | 0.69 | 14.27       | 3.58     | 0.92     |
| **LONG3R** | **8.72**    | **5.03** | **1.67** | **5.40** | 2.36 | 0.60 | **6.44**    | **2.14** | **0.61** |

On TUM Dynamics LONG3R is best on ATE but Spann3R is better on both RPE terms — the paper only claims to remain "competitive" there, since LONG3R is trained exclusively on static scenes.

### Ablation: Memory Gating

원논문 Table 4.

| Method     | 7Scenes Acc↓ Mean | Med. | Comp↓ Mean | Med. | NRGBD Acc↓ Mean | Med. | Comp↓ Mean | Med. | FPS      |
| ---------- | ----------------- | ---- | ---------- | ---- | --------------- | ---- | ---------- | ---- | -------- |
| w/o Gating | **2.53**          | 1.12 | 2.12       | 0.74 | 6.72            | 3.14 | 2.91       | 1.20 | 18.0     |
| w/ Gating  | 2.57              | 1.14 | **2.08**   | 0.73 | **6.66**        | 3.11 | 2.92       | 1.21 | **21.4** |

Reported honestly: gating is essentially accuracy-neutral (marginally worse Acc, marginally better Comp) and is justified by the throughput gain — the paper states 21.4 FPS with gating vs 18.0 FPS without, a 20% boost.

### Ablation: Dual-Source Decoder

원논문 Table 5. 메모리 제약 때문에 이 실험만 2단계 학습에서 32프레임 대신 24프레임을 쓴다.

| Method          | Replica100 Acc↓ Mean | Med.     | Comp↓ Mean | Med.     | Replica200 Acc↓ Mean | Med.     | Comp↓ Mean | Med.     |
| --------------- | -------------------- | -------- | ---------- | -------- | -------------------- | -------- | ---------- | -------- |
| Concat.         | 14.83                | 10.26    | 4.59       | 1.81     | 29.52                | 21.04    | 8.88       | 4.05     |
| **Interleaved** | **12.06**            | **7.67** | **3.68**   | **1.23** | **13.34**            | **8.41** | **3.15**   | **0.94** |

### Ablation: Memory Framework

원논문 Table 6. `w/o 3D Spa. Mem.`는 장기 3D 공간 메모리 없이 시간 메모리만 쓰는 변형이다.

| Method           | 7Scenes Acc↓ Mean | Med.     | Comp↓ Mean | Med.     | Replica200 Acc↓ Mean | Med.     | Comp↓ Mean | Med.     |
| ---------------- | ----------------- | -------- | ---------- | -------- | -------------------- | -------- | ---------- | -------- |
| w/o 3D Spa. Mem. | 5.76              | 2.96     | 3.30       | 1.22     | 65.75                | 47.63    | 13.24      | 3.49     |
| w/ Spann3R Mem.  | 2.64              | 1.16     | 2.10       | 0.74     | 12.41                | 7.87     | 3.07       | 0.88     |
| **LONG3R**       | **2.57**          | **1.14** | **2.08**   | **0.73** | **11.93**            | **7.42** | **2.74**   | **0.87** |

Removing the long-term 3D spatial memory is catastrophic on Replica200 (Acc mean 11.93 → 65.75), which is the paper's strongest ablation evidence.

### Memory Token Counts

Figure 6 compares all-memory vs relevant-memory token counts across the four evaluation settings, but the paper prints only the 27% 7Scenes reduction in text; the remaining per-dataset values exist only in the plot and are not transcribed here.

## 💡 Insights & Impact

### What Actually Limits Streaming Reconstruction

The paper's diagnosis of Spann3R is unusually concrete: (1) memory is attended only once per iteration so it cannot be reused, (2) memory becomes spatially redundant as frames accumulate, and (3) training never exposes the model to long sequences. LONG3R's three contributions map one-to-one onto those three failure modes — a rare case of a paper whose method section is a direct rebuttal of its own related-work analysis.

### Redundancy Is Spatial, Not Temporal

The central design bet is that in a streaming scan, the thing that saturates memory is _revisiting the same 3D space_, not the passage of time. Voxelizing memory tokens by 3D position and keeping only the highest-attention token per voxel turns an unbounded token stream into a near-constant-size bank without an explicit eviction schedule. The adaptive voxel size — averaged online from per-frame point spacing — is what lets one model handle both room-scale and object-scale scenes.

### Honest Positioning Against Offline Methods

LONG3R does not claim to beat global-alignment methods on raw accuracy, and Table 2 shows DUSt3R/MASt3R ahead on Replica Acc. The claim is narrower and better supported: among methods that run at ~21 FPS, LONG3R is the one whose error does not explode as the sequence grows.

### Limitations

The authors state two: predictions are relative to the first frame, so large viewpoint deviation produces blurry results; and the lack of dynamic training data means highly dynamic scenes with large object motion remain hard.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md) — pairwise pointmap regression; LONG3R initializes its ViT-L encoder from DUSt3R weights and uses DUSt3R's confidence-aware loss.
- [MASt3R](../foundation/mast3r.md) — coarse-to-fine matching baseline compared with post-processing.
- [Spann3R](spann3r.md) — the direct predecessor: recurrent memory streaming reconstruction, and the memory framework LONG3R ablates against.
- [CUT3R](../dynamic/cut3r.md) — persistent state-token streaming reconstruction; the other primary online baseline.
- [MV-DUSt3R+](mv-dust3r-plus.md) — offline multi-view baseline that is stronger on NC but runs at ∼1–3 FPS.
- [Point3R](point3r.md) — another explicit-3D-memory streaming approach.
- [Stream3R](stream3r.md) — streaming causal reconstruction in the same family.

## 📚 Key Takeaways

1. **Prune memory in 3D, not in time.** Voxel-based pruning with adaptive scene voxel size keeps the memory bank near-constant over hundreds of frames.
2. **Gating buys speed, not accuracy.** Table 4 shows gating is accuracy-neutral; its measured payoff is 18.0 → 21.4 FPS.
3. **Interleaved beats concatenated fusion.** Alternating cross-attention over memory and frame features avoids feature-space misalignment; the gap widens sharply at 200 frames (Acc mean 29.52 → 13.34).
4. **Curriculum length matters.** Progressive 5 → 10 → 32 frame training is what makes long-sequence behavior learnable within a feasible compute budget.
5. **Static training shows.** LONG3R is trained only on static scenes and the authors flag highly dynamic scenes as an open limitation.

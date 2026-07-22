# StreamVGGT: Streaming Visual Geometry Transformer (ICLR 2026)

![streamvggt — architecture](https://arxiv.org/html/2507.11539v2/x3.png)

_Framework of StreamVGGT (원논문 Fig. 3)_

## 📋 Overview

- **Authors**: Dong Zhuo, Wenzhao Zheng, Jiahe Guo, Yuqi Wu, Jie Zhou, Jiwen Lu
- **Institution**: Tsinghua University
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2507.11539) | [Code](https://github.com/wzzheng/StreamVGGT) | [Project Page](https://wzzheng.net/StreamVGGT/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Converts VGGT's global self-attention into temporal causal attention with a cached key/value memory, distilled from VGGT as teacher, so that streaming inputs can be reconstructed incrementally instead of reprocessing the whole sequence per frame.

## 🎯 Key Contributions

1. **Causal transformer for streaming geometry**: Replaces every global self-attention layer in VGGT with a temporal attention layer where each frame attends only to itself and its predecessors, reducing per-step latency from O(N²) to O(N).
2. **Cached memory tokens**: At inference, historical keys and values are cached as implicit memory so each new frame cross-attends to stored representations rather than recomputing them — reproducing the training-time causal behaviour without full-sequence input.
3. **Distillation-based training**: Uses the bidirectional VGGT as a teacher supplying dense pseudo-labels for camera parameters, depth, point maps, and tracks. This avoids per-dataset ground-truth engineering and makes training feasible under a limited budget.
4. **Long-sequence pruning strategies**: Windowed streaming (fixed-length chunks aligned by predicted extrinsics) and K-nearest-frames caching, both of which bound peak memory and latency.
5. **FlashAttention compatibility**: The causal formulation lets optimized attention operators from LLM infrastructure carry over directly.

## 🔧 Technical Details

### Attention formulations compared

```text
Memory-based:   G_t, M_t = Decoder(CrossAttn(F_t, M_{t-1}))
Global (VGGT):  {G_t} = Decoder(GlobalSelfAttn({F_t}))      # O(N^2) memory
StreamVGGT:     {G_t} = Decoder(TemporalSelfAttn({F_t}))    # causal, O(N) latency
```

At inference the causal path becomes an explicit cache:

```text
G_T = Decoder(CrossAttn(F_T, {M_t}_{t=1}^{T-1}))
M_T = TokenCachedMemory(G_T)
```

### Architecture

- **Image encoder**: DINO patchification into N tokens per frame.
- **Spatio-temporal decoder**: L = 24 alternating spatial and temporal attention layers.
- **Multi-task heads**: camera head (translation, rotation quaternion, FoV), geometry head (point map, depth map, confidence maps, dense tracking features via a DPT layer), track head.
- A learnable camera token marks the first frame as the global reference so subsequent frames are incrementally aligned in a shared coordinate system with no post-processing.

### Training

Initialized from pre-trained VGGT weights; approximately 950 M parameters fine-tuned (image backbone frozen) for 10 epochs, AdamW with 0.5-epoch linear warm-up then cosine decay to a peak learning rate of 1e-6, batches of 10 randomly sampled frames, maximum edge resized to 518 px. Trained on 4 NVIDIA A800 GPUs for 7 days over a curated collection of 13 datasets. The loss follows VGGT's design (camera Huber loss + confidence-weighted depth and point-map losses) but supervises against teacher outputs as pseudo ground truth.

## 📊 Results

### 3D reconstruction on 7-Scenes and NRGBD

원논문 Table 1. 희소 입력(7-Scenes 장면당 3–5프레임, NRGBD 2–4프레임).

| Method     | Type       | 7S Acc ↓ (Mean) | 7S Comp ↓ (Mean) | 7S NC ↑ (Mean) | NRGBD Acc ↓ (Mean) | NRGBD Comp ↓ (Mean) | NRGBD NC ↑ (Mean) |
| ---------- | ---------- | --------------- | ---------------- | -------------- | ------------------ | ------------------- | ----------------- |
| DUSt3R-GA  | Pair-wise  | 0.146           | 0.181            | 0.736          | 0.144              | 0.154               | 0.870             |
| MASt3R-GA  | Pair-wise  | 0.185           | 0.180            | 0.701          | 0.085              | 0.063               | 0.794             |
| MonST3R-GA | Pair-wise  | 0.248           | 0.266            | 0.672          | 0.272              | 0.287               | 0.758             |
| VGGT       | Dense-view | 0.088           | 0.091            | 0.787          | 0.073              | 0.077               | 0.910             |
| Spann3R    | Streaming  | 0.298           | 0.205            | 0.650          | 0.416              | 0.417               | 0.684             |
| CUT3R      | Streaming  | 0.126           | 0.154            | 0.727          | 0.099              | 0.076               | 0.837             |
| StreamVGGT | Streaming  | 0.129           | 0.115            | 0.751          | 0.084              | 0.074               | 0.861             |

Note the honest reading: StreamVGGT is _not_ uniformly better than CUT3R here — CUT3R has the better 7-Scenes mean accuracy (0.126 vs 0.129). StreamVGGT leads on completeness and normal consistency, and on NRGBD accuracy.

### Point cloud accuracy on ETH3D

원논문 Table 2. 장면당 10프레임 무작위 샘플. Overall은 Chamfer distance.

| Method     | Type       | Acc. ↓    | Comp. ↓ | Overall ↓ |
| ---------- | ---------- | --------- | ------- | --------- |
| DUSt3R     | Pair-wise  | 1.167     | 0.842   | 1.005     |
| MASt3R     | Pair-wise  | 0.968     | 0.684   | 0.826     |
| VGGT       | Dense-view | 0.928     | 0.443   | 0.686     |
| CUT3R      | Streaming  | 1.426     | 1.395   | 1.411     |
| StreamVGGT | Streaming  | **0.609** | 0.545   | **0.577** |

### Camera pose estimation

원논문 Table 6. Sim(3) 정렬 후 측정.

| Method     | Type       | ScanNet ATE ↓ | ScanNet RPE rot ↓ | Sintel ATE ↓ | Sintel RPE rot ↓ | TUM-D ATE ↓ | TUM-D RPE rot ↓ |
| ---------- | ---------- | ------------- | ----------------- | ------------ | ---------------- | ----------- | --------------- |
| DUSt3R-GA  | Pair-wise  | 0.081         | 0.784             | 0.417        | 5.796            | 0.083       | 3.567           |
| MASt3R-GA  | Pair-wise  | 0.078         | 0.475             | 0.185        | 1.496            | 0.038       | 0.448           |
| MonST3R-GA | Pair-wise  | 0.077         | 0.529             | 0.111        | 0.869            | 0.098       | 0.935           |
| VGGT       | Dense-view | 0.035         | 0.377             | 0.169        | 0.474            | 0.012       | 0.307           |
| Spann3R    | Streaming  | 0.096         | 0.661             | 0.329        | 4.471            | 0.056       | 0.591           |
| CUT3R      | Streaming  | 0.099         | 0.600             | 0.213        | 0.621            | 0.046       | 0.473           |
| Point3R    | Streaming  | 0.106         | 1.946             | 0.351        | 1.822            | 0.075       | 0.642           |
| StreamVGGT | Streaming  | 0.048         | 0.557             | 0.219        | 1.041            | 0.026       | 0.316           |

StreamVGGT is the strongest streaming method on ScanNet and TUM-dynamics, but on Sintel its ATE (0.219) is worse than CUT3R's (0.213) and its RPE rot (1.041) is clearly worse (0.621).

### Single-frame depth estimation

원논문 Table 4.

| Method     | Type       | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | KITTI Abs Rel ↓ | NYU-v2 Abs Rel ↓ | NYU-v2 δ<1.25 ↑ |
| ---------- | ---------- | ---------------- | --------------- | -------------- | --------------- | ---------------- | --------------- |
| DUSt3R     | Pair-wise  | 0.424            | 58.7            | 0.141          | 0.112           | 0.080            | 90.7            |
| MASt3R     | Pair-wise  | 0.340            | 60.4            | 0.142          | 0.079           | 0.129            | 84.9            |
| MonST3R    | Pair-wise  | 0.358            | 54.8            | 0.076          | 0.100           | 0.102            | 88.0            |
| VGGT       | Dense-view | 0.276            | 67.5            | 0.055          | 0.072           | 0.060            | 95.1            |
| Spann3R    | Streaming  | 0.470            | 53.9            | 0.118          | 0.128           | 0.122            | 84.9            |
| CUT3R      | Streaming  | 0.428            | 55.4            | 0.063          | 0.092           | 0.086            | 90.9            |
| Point3R    | Streaming  | 0.395            | 56.8            | 0.061          | 0.087           | 0.079            | 92.0            |
| StreamVGGT | Streaming  | **0.254**        | **68.5**        | **0.052**      | 0.072           | **0.055**        | **95.9**        |

### Video depth estimation

원논문 Table 5. Per-sequence scale 정렬.

| Method     | Type       | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | BONN Abs Rel ↓ | BONN δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ---------- | ---------- | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| VGGT       | Dense-view | 0.298            | 68.1            | 0.057          | 96.8          | 0.061           | 97.0           |
| Spann3R    | Streaming  | 0.622            | 42.6            | 0.144          | 81.3          | 0.198           | 73.7           |
| CUT3R      | Streaming  | 0.421            | 47.9            | 0.078          | 93.7          | 0.118           | 88.1           |
| Point3R    | Streaming  | 0.452            | 48.9            | 0.060          | 96.0          | 0.136           | 84.2           |
| StreamVGGT | Streaming  | 0.323            | 65.7            | 0.059          | 97.2          | 0.173           | 72.1           |

KITTI video depth is a clear loss: StreamVGGT's 0.173 Abs Rel / 72.1 δ<1.25 is the worst among the streaming methods listed other than Spann3R, and far behind CUT3R.

### Online inference cost

원논문 Table 7. 각 셀은 Acc↓ / ms↓ / GB↓. VGGT/StreamVGGT는 518×392, CUT3R/Spann3R는 512×384.

| Method     | 1 frame           | 10 frames         | 20 frames         | 30 frames         | 40 frames         |
| ---------- | ----------------- | ----------------- | ----------------- | ----------------- | ----------------- |
| Spann3R    | 0.039 / 500 / 5.3 | 0.046 / 82 / 5.5  | 0.036 / 120 / 5.5 | 0.043 / 192 / 5.6 | 0.068 / 125 / 5.7 |
| CUT3R      | 0.035 / 101 / 3.4 | 0.039 / 99 / 3.6  | 0.031 / 101 / 3.8 | 0.027 / 102 / 4.0 | 0.023 / 102 / 4.2 |
| StreamVGGT | 0.028 / 63 / 2.1  | 0.024 / 120 / 3.2 | 0.021 / 152 / 4.3 | 0.021 / 184 / 5.5 | 0.021 / 216 / 6.6 |

The paper is explicit that this is a trade-off: latency and memory grow with sequence length because the cached memory grows, and StreamVGGT "shows a good one for not very long sequences."

### Pruning strategies on a 200-frame sequence

원논문 Table 8.

| Method                        | Acc ↓ (Mean) | Comp ↓ (Mean) | NC ↑ (Mean) | Inference Time (Frame 200) | Peak Memory |
| ----------------------------- | ------------ | ------------- | ----------- | -------------------------- | ----------- |
| Spann3R                       | 0.225        | 0.070         | 0.538       | 221.054 ms                 | 6.7 GB      |
| CUT3R                         | 0.165        | 0.030         | 0.551       | 102.533 ms                 | 7.6 GB      |
| Ours No Pruning               | 0.058        | 0.026         | 0.632       | 733.083 ms                 | 25.3 GB     |
| Ours Window-based (50)        | 0.054        | 0.023         | 0.636       | 219.454 ms                 | 8.2 GB      |
| Ours Window-based (100)       | 0.062        | 0.032         | 0.633       | 392.634 ms                 | 14.0 GB     |
| Ours K-nearest-frames (K=50)  | 0.157        | 0.104         | 0.605       | 220.109 ms                 | 8.4 GB      |
| Ours K-nearest-frames (K=100) | 0.054        | 0.034         | 0.626       | 392.634 ms                 | 14.0 GB     |

### Ablations

원논문 Table 9. 동일 학습 예산에서 distillation의 효과.

| Method              | Attention | 7S Acc ↓ (Mean) | 7S NC ↑ (Mean) | NRGBD Acc ↓ (Mean) | NRGBD NC ↑ (Mean) |
| ------------------- | --------- | --------------- | -------------- | ------------------ | ----------------- |
| VGGT (teacher)      | Global    | 0.088           | 0.787          | 0.073              | 0.910             |
| StreamVGGT (w/o KD) | Causal    | 0.202           | 0.718          | 0.189              | 0.816             |
| StreamVGGT (w/ KD)  | Causal    | 0.129           | 0.751          | 0.084              | 0.861             |

원논문 Table 10. 캐시와 FlashAttention의 효과 (프레임 5 기준).

| Method                | Inference Time (at Frame 5) | Peak Memory |
| --------------------- | --------------------------- | ----------- |
| w/o FlashAttn & Cache | 1135.860 ms                 | 5.4 GB      |
| w/ FlashAttn          | 850.699 ms                  | 2.3 GB      |
| w/ FlashAttn & Cache  | 88.193 ms                   | 2.7 GB      |

## 💡 Insights & Impact

### Causality as an architectural commitment

The paper's premise is that VGGT's offline paradigm "diverges from the causal nature of human perception". Turning global attention into causal attention is a small code change with a large systems consequence: only the newest geometry token needs updating per frame, so the model becomes usable in an interactive loop.

### Distillation as a budget substitute

The KD ablation (Table 9) is the most instructive result. Under the _same_ training budget, the non-distilled causal student degrades badly (7-Scenes Acc 0.202 vs 0.129). The teacher's soft targets and confidence estimates act as regularizers and unify supervision across 13 heterogeneous datasets without per-dataset label engineering.

### The unresolved scaling problem

The cached KV memory grows linearly with sequence length, so StreamVGGT trades VGGT's quadratic recompute for linear memory accumulation rather than eliminating growth. This is precisely the criticism [TTT3R](ttt3r.md) levels, and it is why [FastVGGT](fastvggt.md) reports StreamVGGT as OOM on its 100+-image benchmarks. Window-based pruning is the paper's own mitigation, and it works well (Table 8), but it is a post-hoc bound rather than a constant-memory design.

## 🔗 Related Work

- [VGGT](vggt.md) — the direct parent: same encoder, same heads, same loss structure, and the teacher model for distillation. StreamVGGT is best read as "VGGT made causal".
- [CUT3R](../dynamic/cut3r.md) — the fixed-length-state alternative, and the main streaming baseline throughout.
- [Point3R](point3r.md) — sibling work from the same lab; StreamVGGT adopts its variable-aspect-ratio image processing.
- [Spann3R](spann3r.md) / [MUSt3R](must3r.md) — the earlier explicit-memory streaming lineage.
- [TTT3R](ttt3r.md) — classifies StreamVGGT as O(t) state growth and shows it exhausting memory on long sequences.
- [FastVGGT](fastvggt.md) — the other efficiency answer to VGGT: token merging inside global attention rather than causal restriction.
- [Fast3R](fast3r.md) — the all-frames-at-once feed-forward design StreamVGGT contrasts against.

## 📚 Key Takeaways

1. **Causal attention buys streaming, not unbounded scale.** Latency per frame drops, but the KV cache still grows — good for interactive short-to-medium sequences, not for thousand-frame reconstruction.
2. **Distillation from a strong bidirectional teacher is what makes the causal student viable** under a 4×A800 / 7-day budget; without KD the same architecture is substantially worse.
3. **Results are mixed, not uniform.** StreamVGGT wins decisively on ETH3D, single-frame depth, and ScanNet/TUM pose, but loses to CUT3R on Sintel pose and KITTI video depth.
4. **Windowed streaming is the practical deployment mode**, cutting 200-frame peak memory from 25.3 GB to 8.2 GB while slightly _improving_ accuracy.

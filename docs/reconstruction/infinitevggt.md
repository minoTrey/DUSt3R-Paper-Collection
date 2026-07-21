# InfiniteVGGT: Visual Geometry Grounded Transformer for Endless Streams (arXiv preprint (2026-01))

## 📋 Overview

- **Authors**: Shuai Yuan, Yantai Yang, Xiaotian Yang, Xupeng Zhang, Zhonghao Zhao, Lingming Zhang, Zhipeng Zhang
- **Institution**: AutoLab, School of Artificial Intelligence, Shanghai Jiao Tong University; Anyverse Dynamics
- **Venue**: arXiv preprint (2026-01)
- **Links**: [Paper](https://arxiv.org/abs/2601.02281) | [Code](https://github.com/AutoLab-SAI-SJTU/InfiniteVGGT)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free "rolling memory" for streaming VGGT-family models that keeps a strictly bounded KV cache by pruning redundant tokens via key cosine similarity (FlashAttention-compatible), enabling infinite-horizon online 3D reconstruction; introduces the Long3D benchmark (~10,000-frame sequences).

## 🎯 Key Contributions

The paper states three contributions:

1. **Unbounded-horizon memory architecture**: InfiniteVGGT, a rolling-memory design for continuous 3D geometry understanding, built on a dynamic and interpretable explicit memory system rather than an implicit RNN state.
2. **State-of-the-art long-sequence performance**: robust infinite-horizon reconstruction without memory overflow, applied as a training-free modification on top of StreamVGGT.
3. **Long3D benchmark**: a new dataset for rigorous evaluation of long-term performance on continuous streams of about 2,000 to 10,000 frames.

## 🔧 Technical Details

### Problem Setup

- Offline models like [VGGT](vggt.md) process a batch of N images in a single pass over 24 self-attention layers (alternating frame `Fθ` and global `Gθ` interaction), jointly estimating camera parameters `gi ∈ R⁹`, depth `Di`, point map `Pi`, and tracking features `Ti`.
- Streaming variants like [StreamVGGT](streamvggt.md) replace the global interaction `Gθ` with a causal temporal module `Tθ` and a KV cache `Ct-1` that stores context from all previous frames. The cache grows linearly (`O(t)`), which is unsustainable for long streams.

### Key Insight: redundancy in key space

- Each new frame adds roughly **1,000 tokens**; the cache reaches `O(10⁵)` tokens within 100 frames, forcing use of FlashAttention-style kernels to stay functional.
- Adjacent-frame patch-embedded tokens from the StreamVGGT backbone have cosine similarity consistently **exceeding 0.95** — the DINO backbone encodes "what" is seen more than "from where", producing heavy token-level redundancy.
- Attention-score-based eviction is rejected: it requires materializing the full `O(N²)` attention matrix, defeating the very FlashAttention kernels needed at this scale.
- Instead, redundancy is measured in **key space** using cosine similarity, an attention-independent proxy that runs _before_ attention computation and stays FlashAttention-compatible.

### Diversity-aware Rolling Memory

- **Immutable Anchor Token**: the complete KV cache of the first input frame is designated as an anchor set `Canc` and excluded from all pruning, because VGGT rigidly aligns all subsequent 3D predictions to the first frame's coordinate system. The rest of the cache (from `t = 2`) forms the mutable candidate set.
- **Diversity score**: per layer `l` and head `h`, compute the mean of L2-normalized candidate keys `µ(l,h)`, then score each key by negative cosine similarity to that mean: `sdiv(k̂i) = − CosSim(µ(l,h), k̂i)`. Keys most dissimilar from the mean (most geometrically distinct) score highest and are retained via TopK.
- **Layer-wise Adaptive Budget Allocation**: each layer's budget proportion `plbud` is a softmax (temperature `τ`) over its average diversity score, giving `Bl = plbud · Btotal`. Motivation: shallow layers amplifying inter-frame differences show high diversity, while the initial layer (low-level color/brightness) and deep layers (holistic semantics) show less.
- The method is **training-free, attention-agnostic**, and implemented on top of StreamVGGT; all experiments run on a single NVIDIA A100 GPU.

### Long3D Benchmark

- 5 challenging indoor/outdoor sequences, each about 2,000 to 10,000 frames.
- Captured with a handheld 3D spatial scanner: IMU, 3D LiDAR (360° horizontal × 59° vertical FOV), and an RGB camera (800 × 600 at 10 Hz, 90° FOV).
- Each scene provides a global ground-truth point cloud plus the uninterrupted RGB sequence; predicted and GT clouds are aligned with ICP. Metrics: Accuracy (Acc.), Completion (Comp.), Chamfer Distance (CD), Normal Consistency (NC).

## 📊 Results

### 3D Reconstruction on 7-Scenes and NRGBD (input = 500)

원논문 Table 1. Images sampled with stride 2, first 500 used as input. VGGT (Offline) and StreamVGGT both report OOM at this length (memory constraint).

| Method       | 7S Acc. Mean ↓ | 7S Acc. Med. ↓ | 7S Comp. Mean ↓ | 7S Comp. Med. ↓ | 7S NC Mean ↑ | 7S NC Med. ↑ |
| ------------ | -------------- | -------------- | --------------- | --------------- | ------------ | ------------ |
| CUT3R        | 0.183          | 0.130          | 0.091           | 0.033           | 0.530        | 0.543        |
| Point3R      | 0.063          | 0.026          | 0.031           | 0.015           | 0.555        | 0.583        |
| TTT3R        | 0.062          | 0.036          | 0.029           | 0.005           | 0.552        | 0.577        |
| InfiniteVGGT | 0.043          | 0.018          | 0.025           | 0.005           | 0.561        | 0.593        |

원논문 Table 1 (NRGBD, 동일 input=500).

| Method       | NRGBD Acc. Mean ↓ | NRGBD Acc. Med. ↓ | NRGBD Comp. Mean ↓ | NRGBD Comp. Med. ↓ | NRGBD NC Mean ↑ | NRGBD NC Med. ↑ |
| ------------ | ----------------- | ----------------- | ------------------ | ------------------ | --------------- | --------------- |
| CUT3R        | 0.326             | 0.243             | 0.132              | 0.042              | 0.556           | 0.582           |
| Point3R      | 0.113             | 0.048             | 0.037              | 0.005              | 0.613           | 0.684           |
| TTT3R        | 0.165             | 0.084             | 0.095              | 0.015              | 0.594           | 0.648           |
| InfiniteVGGT | 0.080             | 0.054             | 0.037              | 0.008              | 0.643           | 0.746           |

At the shorter 300- and 400-frame inputs the same trend holds (원논문 Table 1); e.g. at input 300 InfiniteVGGT reaches 7-Scenes Acc. Mean 0.040 and NRGBD NC Mean 0.649.

### 3D Reconstruction on Long3D

원논문 Table 2. Sequence length in parentheses. Lower Acc./Comp./CD better, higher NC better.

| Method       | Scene (frames)           | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ | NC Mean ↑ | NC Med. ↑ | CD ↓  |
| ------------ | ------------------------ | ----------- | ----------- | ------------ | ------------ | --------- | --------- | ----- |
| CUT3R        | Classroom (2128)         | 0.496       | 0.374       | 0.085        | 0.036        | 0.520     | 0.525     | 0.291 |
| TTT3R        | Classroom (2128)         | 0.396       | 0.319       | 0.081        | 0.035        | 0.530     | 0.540     | 0.239 |
| InfiniteVGGT | Classroom (2128)         | 0.357       | 0.298       | 0.057        | 0.033        | 0.576     | 0.612     | 0.207 |
| CUT3R        | Dormitory (4208)         | 1.800       | 1.372       | 0.404        | 0.090        | 0.501     | 0.495     | 1.102 |
| TTT3R        | Dormitory (4208)         | 1.965       | 1.749       | 0.329        | 0.100        | 0.515     | 0.509     | 1.147 |
| InfiniteVGGT | Dormitory (4208)         | 1.438       | 1.159       | 0.575        | 0.089        | 0.526     | 0.538     | 1.007 |
| CUT3R        | Library (4726)           | 1.907       | 1.437       | 0.193        | 0.079        | 0.504     | 0.507     | 1.050 |
| TTT3R        | Library (4726)           | 2.175       | 1.484       | 0.430        | 0.095        | 0.494     | 0.481     | 1.303 |
| InfiniteVGGT | Library (4726)           | 1.121       | 0.821       | 0.571        | 0.077        | 0.508     | 0.514     | 0.846 |
| CUT3R        | Badminton Court (6067)   | 2.489       | 2.432       | 5.802        | 5.071        | 0.495     | 0.483     | 4.146 |
| TTT3R        | Badminton Court (6067)   | 2.791       | 2.392       | 3.160        | 2.673        | 0.509     | 0.502     | 2.975 |
| InfiniteVGGT | Badminton Court (6067)   | 1.843       | 1.555       | 1.854        | 0.816        | 0.510     | 0.509     | 1.848 |
| CUT3R        | Academic Building (9545) | 8.062       | 5.650       | 0.673        | 0.251        | 0.496     | 0.491     | 4.638 |
| TTT3R        | Academic Building (9545) | 7.710       | 5.793       | 6.192        | 5.159        | 0.513     | 0.519     | 6.951 |
| InfiniteVGGT | Academic Building (9545) | 5.733       | 4.603       | 1.206        | 0.251        | 0.495     | 0.490     | 3.470 |

InfiniteVGGT leads on Acc. and CD across all five scenes. Two honest losses: on **Comp. Mean** it is beaten by both baselines on Dormitory (0.575 vs CUT3R 0.404 / TTT3R 0.329) and Library (0.571 vs CUT3R 0.193 / TTT3R 0.430) — the paper explicitly notes it "underperforms on the mean of Comp. metric" and flags this for future work. On **NC Mean** it also trails TTT3R on Academic Building (0.495 vs 0.513).

### Video Depth Estimation on Bonn (input = 500)

원논문 Table 3. VGGT (Offline) and StreamVGGT report OOM.

| Method       | Abs Rel ↓ | δ < 1.25 ↑ |
| ------------ | --------- | ---------- |
| CUT3R        | 0.084     | 0.939      |
| Point3R      | 0.081     | 0.946      |
| TTT3R        | 0.076     | 0.953      |
| InfiniteVGGT | 0.069     | 0.960      |

InfiniteVGGT is best on both metrics at input 500; the same ordering holds at inputs 200/300/400 (원논문 Table 3), e.g. at input 200 InfiniteVGGT reaches Abs Rel 0.063 and δ<1.25 0.964.

### Ablation: token-selection policy (7-Scenes)

원논문 Table 4. CD = average of accuracy and completeness. Attention-weight selection also adds ~120 ms latency per frame (본문 서술).

| Method            | CD ↓  | NC ↑  | Time (s) ↓ | Peak Memory (GB) ↓ |
| ----------------- | ----- | ----- | ---------- | ------------------ |
| Attention weight  | 0.036 | 0.567 | 0.288      | 17.30              |
| Cosine similarity | 0.032 | 0.570 | 0.168      | 14.49              |

### Ablation: initial per-head budget (7-Scenes)

원논문 Table 5. `B(l,h)` = initial max token capacity per head per layer.

| Initial Budget | 300 CD ↓ | 300 NC ↑ | 500 CD ↓ | 500 NC ↑ |
| -------------- | -------- | -------- | -------- | -------- |
| B10000         | 0.062    | 0.565    | 0.075    | 0.555    |
| B25000         | 0.032    | 0.570    | 0.033    | 0.560    |
| B50000         | 0.032    | 0.570    | 0.031    | 0.562    |

### Ablation: layer-wise allocation and anchor frame (7-Scenes)

원논문 Table 6 (layer-wise allocation, input 500) · Table 7 (anchor frame, input 300).

| Setting                   | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ | NC Mean ↑ | NC Med. ↑ |
| ------------------------- | ----------- | ----------- | ------------ | ------------ | --------- | --------- |
| w/o layer-wise allocation | 0.098       | 0.058       | 0.057        | 0.008        | 0.554     | 0.582     |
| w/ layer-wise allocation  | 0.093       | 0.053       | 0.056        | 0.008        | 0.555     | 0.583     |
| w/o anchor frame          | 0.047       | 0.020       | 0.027        | 0.006        | 0.570     | 0.606     |
| w/ anchor frame           | 0.040       | 0.015       | 0.025        | 0.006        | 0.570     | 0.607     |

On short 50–100 frame sequences (where the StreamVGGT baseline fits in memory), the paper reports negligible CD/NC differences and a slight NC advantage for InfiniteVGGT (그림 6, 수치 미인쇄).

## 💡 Insights & Impact

- **Reframes the streaming dilemma**: prior online methods are either explicit-history accumulators ([StreamVGGT](streamvggt.md), Stream3R) that OOM, or implicit RNN-state compressors ([CUT3R](../dynamic/cut3r.md), TTT3R) that drift via catastrophic forgetting. InfiniteVGGT keeps an _explicit but bounded_ cache, aiming to get both stability and unbounded horizon.
- **Kernel-aware pruning**: the central engineering point is that token importance must be estimated without materializing attention weights, so the method uses key-space cosine similarity — cheaper and FlashAttention-compatible.
- **Interpretable memory**: anchor-frame preservation is tied to VGGT's first-frame coordinate system, and layer-wise budgets follow measured per-layer diversity, giving a rationale for where capacity is spent.
- **Training-free deployment**: because it is a drop-in modification of StreamVGGT, no retraining is needed; the reported gains are attributed purely to memory management.
- **Honest limitation**: mean Completion on the longest Long3D scenes is worse than baselines, acknowledged as future work.

## 🔗 Related Work

- **[VGGT](vggt.md)**: the offline backbone architecture (24 alternating frame/global attention layers) whose first-frame coordinate alignment motivates the immutable anchor token.
- **[StreamVGGT](streamvggt.md)**: the causal streaming base that InfiniteVGGT modifies; suffers from unbounded KV growth (Fig. 1(c)).
- **[CUT3R](../dynamic/cut3r.md)** and **TTT3R**: implicit RNN-state streaming baselines that bound memory but drift; the main long-sequence competitors.
- **[Point3R](point3r.md)**: explicit spatial-pointer streaming memory, an additional baseline whose memory still grows.
- **[Fast3R](fast3r.md)** / **[FastVGGT](fastvggt.md)**: efficiency-oriented VGGT-family work (FastVGGT reports a 4× speedup on 1000-frame sequences via training-free token merging).
- **[VGGT-Long](vggt-long.md)**, **[WinT3R](wint3r.md)**, **[Stream3R](stream3r.md)**: other long-sequence / windowed streaming extensions discussed as related scalability efforts.
- **[π³ (pi3)](pi3.md)**: refines VGGT to be reference-frame independent.
- **[DUSt3R](../foundation/dust3r.md)** / **[MASt3R](../foundation/mast3r.md)**: pairwise pointmap-regression predecessors with expensive global alignment.

## 📚 Key Takeaways

1. **Bounded explicit memory beats implicit compression for long streams**: a fixed-size, diversity-pruned KV cache keeps InfiniteVGGT running where VGGT and StreamVGGT OOM, while leading TTT3R/CUT3R on Acc./CD across ~2K–10K-frame Long3D scenes.
2. **Cosine similarity in key space is the enabling trick**: it estimates token redundancy before attention, preserving FlashAttention efficiency (0.168 s/frame, 14.49 GB peak vs 0.288 s, 17.30 GB for attention-weight pruning).
3. **Anchor + layer-wise budget both help**: keeping the first frame intact and allocating budget by measured per-layer diversity each improve reconstruction accuracy in ablations.
4. **Long3D fills a benchmark gap**: continuous sequences up to ~10,000 frames enable rigorous infinite-horizon evaluation previously impossible with ≤1000-frame or discontinuous clip datasets.
5. **Not uniformly ahead**: InfiniteVGGT trails baselines on mean Completion for the longest scenes, a stated open problem.

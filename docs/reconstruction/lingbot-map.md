# LingBot-Map: Geometric Context Transformer for Streaming 3D Reconstruction (arXiv preprint)

## 📋 Overview

- **Authors**: Lin-Zhuo Chen, Jian Gao, Yihang Chen, Ka Leong Cheng, Yipengjing Sun, Liangxiao Hu, Nan Xue, Xing Zhu, Yujun Shen, Yao Yao, Yinghao Xu
- **Institution**: 원논문 1페이지에 소속 표기 없음
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.14141) | [Code](https://github.com/robbyant/lingbot-map) | [Project Page](https://technology.robbyant.com/lingbot-map)
- **Verification**: PREPRINT (2026-07-20)
- **TL;DR**: A streaming 3D foundation model whose attention mask is factored the way a SLAM system factors its state — an anchor context for scale grounding, a bounded local window for dense registration, and a 6-token-per-frame trajectory memory for drift correction — giving ~20 FPS at 518×378 over sequences beyond 10,000 frames with near-constant per-frame cost.

## 🎯 Key Contributions

1. **Geometric Context Attention (GCA)**: replaces hand-crafted SLAM optimization with a structured, end-to-end differentiable attention mask that decomposes streaming context into three complementary roles.
2. **Anchor context for scale grounding**: the first _n_ frames are designated anchors with full mutual attention and a learnable anchor token; all later frames attend to them as fixed references. This substitutes for the global point-cloud normalization that DUSt3R and VGGT use but which is incompatible with causal streaming.
3. **Trajectory memory at 6 tokens per frame**: evicted frames keep only camera, anchor, and register tokens — the M image tokens are discarded — plus video temporal positional encodings so the memory is temporally ordered.
4. **Camera-to-world pose supervision** rather than VGGT's world-to-camera, because in the world-to-camera parameterization rotation and translation are coupled, making translation highly sensitive to rotation error over long sequences.
5. **Relative pose loss over the local window**, following π³, complementing the absolute pose loss.

## 🔧 Technical Details

### The three contexts

**Anchor Context.** Monocular reconstruction is scale-ambiguous, so a coordinate system and absolute scale must be fixed before streaming. The first n images get full attention among themselves and a learnable anchor token. Ground-truth normalization during training uses a canonical scale derived from anchors:

```text
s = (1/|X̄_anchor|) Σ_{x∈X̄_anchor} ‖x‖₂
```

All ground-truth depths and camera translations are divided by `s`.

**Local Pose-Reference Window.** The k most recent frames retain their full image tokens, supplying the dense visual overlap needed to register each new frame — something distant anchor frames cannot provide.

**Trajectory Memory.** Frames outside both sets keep only 6 context tokens (camera + anchor + 4 register), discarding the M image tokens, with video temporal positional encodings applied.

### Complexity

For a T-frame sequence, GCA's per-frame context is `(n + k)·M + 6T` — a constant term plus growth of just 6 tokens per frame. Causal attention retains `T·(M+6) = MT + 6T`. Since each new frame adds M+6 tokens under causal attention but only 6 under GCA, **the per-frame growth rate is reduced by roughly 80× for typical M ≈ 500**.

Concretely, with n=3, k=16, T=10,000: causal attention accumulates ~5×10⁶ tokens; GCA retains only ~7×10⁴.

### Architecture

A DINOv2-initialized ViT produces M image tokens per frame, augmented with a camera token `c`, four register tokens `r_j`, and a learnable anchor token `a`. These pass through alternating **Frame Attention** (within-frame refinement) and **GCA** (cross-frame reasoning under the structured mask). A camera head reads the camera token for absolute pose `P̂_t`; a depth head reads the image tokens for `D̂_t`.

### Loss

```text
L = λ_depth · L_depth + λ_abs-pose · L_abs-pose + λ_rel-pose · L_rel-pose
```

`L_depth` and `L_abs-pose` follow VGGT:

```text
L_depth    = Σ_i Σ^D_i ⊙ (D̂_i − D_i) + Σ^D_i ⊙ (∇D̂_i − ∇D_i) − α log Σ^D_i
L_abs-pose = Σ_i ‖P̂_i − P_i‖_ε
```

The relative pose term, over all frame pairs in the sliding window:

```text
L_rel-pose = 1/(k(k−1)) · Σ_{i≠j, i,j∈{1..k}} ( L_rot(i,j) + λ_trans · L_trans(i,j) )
```

## 📊 Results

### Oxford Spires, sparse setting (320 frames, sampled every 12)

원논문 Table 2. 이 설정에서는 offline·optimization·online 세 범주가 모두 실행 가능해 공정한 비교가 된다.

| Method          | Type    | AUC@15 ↑  | AUC@30 ↑  | ATE ↓    | RPE-trans ↓ | RPE-Rot ↓ |
| --------------- | ------- | --------- | --------- | -------- | ----------- | --------- |
| Fast3R          | offline | 1.20      | 2.99      | 34.80    | 8.21        | 59.51     |
| VGGT            | offline | 23.84     | 35.09     | 24.78    | 8.87        | 22.79     |
| DA3             | offline | 49.84     | 56.68     | 12.87    | 3.22        | 16.17     |
| FastVGGT        | offline | 21.68     | 34.64     | 22.43    | 7.25        | 16.12     |
| Pi3             | offline | 38.64     | 48.65     | 14.03    | 2.58        | 10.33     |
| DroidSLAM       | optim   | 8.58      | 21.41     | 21.84    | 1.02        | 6.90      |
| MegaSAM         | optim   | 15.91     | 28.03     | 13.80    | **0.76**    | 7.24      |
| VIPE            | optim   | 45.35     | 51.88     | 10.52    | **0.43**    | 5.98      |
| StreamVGGT      | online  | 10.91     | 17.04     | 28.41    | 6.35        | 16.28     |
| SLAM3R          | online  | 1.67      | 5.10      | 29.69    | 7.57        | 27.50     |
| InfiniteVGGT    | online  | 10.25     | 16.33     | 30.49    | 5.72        | 15.01     |
| Spann3R         | online  | 2.06      | 5.09      | 32.12    | 3.54        | 14.37     |
| Stream3R-w      | online  | 6.56      | 11.03     | 33.03    | 4.73        | 16.79     |
| Stream3R        | online  | 9.67      | 15.21     | 29.58    | 6.67        | 16.90     |
| CUT3R           | online  | 5.98      | 14.95     | 18.16    | 1.17        | 7.18      |
| TTT3R           | online  | 13.92     | 25.90     | 19.35    | 2.28        | 13.30     |
| Wint3R          | online  | 11.61     | 23.42     | 21.10    | 1.62        | 6.27      |
| **LingBot-Map** | online  | **61.64** | **75.16** | **6.42** | 1.01        | **3.70**  |

The paper's own framing: AUC@15 of 61.64 against DA3's 49.84 and VGGT's 23.84; ATE reduced from 12.87 (DA3) and 24.78 (VGGT) to 6.42; against the best online competitor CUT3R (5.98 AUC@15, 18.16 ATE) it reports **"a 10× improvement in pose accuracy and 2.8× reduction in trajectory error."**

**Honest exception**: VIPE (0.43) and MegaSAM (0.76) both beat LingBot-Map on RPE-trans (1.01). Optimization-based methods that explicitly minimize reprojection error retain an edge on frame-to-frame translation precision.

### Sparse vs dense (320 → 3,840 frames)

원논문 Table 3. ΔATE는 sparse에서 dense로 갈 때의 열화폭이다.

| Metric       | CUT3R          | TTT3R         | Wint3R         | Inf.-VGGT     | Stream3R-w    | **LingBot-Map**  |
| ------------ | -------------- | ------------- | -------------- | ------------- | ------------- | ---------------- |
| ATE_sparse ↓ | 18.16          | 19.35         | 21.10          | 30.49         | 33.03         | **6.42**         |
| ATE_dense ↓  | 32.47 (+14.31) | 25.05 (+5.70) | 32.90 (+11.80) | 31.75 (+1.26) | 33.73 (+0.70) | **7.11 (+0.69)** |
| FPS ↑        | **29.21**      | 28.97         | 3.88           | 7.78          | 13.66         | 20.29            |

This is the paper's central claim, and it is well-supported: over a 12× longer sequence, LingBot-Map's ATE rises by 0.69 while CUT3R's rises by 14.31. **CUT3R and TTT3R are faster** (29.21 / 28.97 FPS vs 20.29); LingBot-Map is the fastest among methods that do not degrade.

### Generalization: ETH3D, 7-Scenes, Tanks & Temples

원논문 Table 4. 모두 online streaming 방법이다.

| Method          | ETH3D Auc3 ↑ | Auc30 ↑   | ATE ↓    | 7-Scenes Auc3 ↑ | Auc30 ↑   | ATE ↓    |
| --------------- | ------------ | --------- | -------- | --------------- | --------- | -------- |
| SLAM3R          | 1.46         | 22.95     | 1.98     | 4.79            | 66.92     | 0.11     |
| Spann3R         | 1.13         | 23.02     | 2.10     | 2.79            | 57.87     | 0.20     |
| InfiniteVGGT    | 12.00        | 62.20     | 1.46     | 8.45            | 73.40     | 0.12     |
| CUT3R           | 10.63        | 57.77     | 1.43     | 1.50            | 42.44     | 0.29     |
| TTT3R           | 9.98         | 56.12     | 1.22     | 5.52            | 71.23     | 0.10     |
| Wint3R          | 11.31        | 58.71     | 0.86     | 2.74            | 63.02     | 0.12     |
| Stream3R        | 13.73        | 64.76     | 1.67     | 9.31            | 73.70     | 0.10     |
| Stream3R-w      | 9.00         | 58.69     | 1.71     | 7.47            | 61.70     | 0.25     |
| **LingBot-Map** | **27.79**    | **86.20** | **0.22** | **12.63**       | **78.59** | **0.08** |

원논문 Table 4 (계속) — Tanks & Temples.

| Method          | Auc3 ↑    | Auc30 ↑   | ATE ↓    |
| --------------- | --------- | --------- | -------- |
| SLAM3R          | 2.87      | 47.92     | 1.42     |
| Spann3R         | 2.22      | 32.22     | 2.11     |
| InfiniteVGGT    | 21.69     | 77.76     | 1.00     |
| CUT3R           | 1.71      | 25.19     | 1.79     |
| TTT3R           | 9.01      | 71.30     | 0.66     |
| Wint3R          | 3.84      | 57.85     | 0.88     |
| Stream3R        | 39.27     | 81.33     | 0.76     |
| Stream3R-w      | 24.69     | 72.30     | 1.22     |
| **LingBot-Map** | **45.80** | **92.80** | **0.20** |

Best on every metric of all three datasets. The paper quantifies Tanks & Temples as +11.47 AUC points and 3.8× lower ATE over Stream3R, and ETH3D ATE as nearly 4× lower than Wint3R.

### Point cloud reconstruction

원논문 Table 5.

| Method          | ETH3D Acc ↓ | Comp ↓   | F1 ↑      | 7-Scenes Acc ↓ | Comp ↓   | F1 ↑      | NRGBD Acc ↓ | Comp ↓   | F1 ↑      |
| --------------- | ----------- | -------- | --------- | -------------- | -------- | --------- | ----------- | -------- | --------- |
| StreamVGGT      | 0.64        | 0.34     | 58.11     | 0.04           | 0.11     | 69.44     | 0.13        | 0.05     | 45.08     |
| InfiniteVGGT    | 0.65        | 0.35     | 57.69     | 0.04           | 0.11     | 68.53     | 0.13        | 0.05     | 42.27     |
| CUT3R           | 0.57        | 0.50     | 67.63     | 0.07           | 0.10     | 58.98     | 0.25        | 0.15     | 32.22     |
| TTT3R           | 0.41        | 0.22     | 68.48     | 0.03           | 0.08     | 77.25     | 0.16        | 0.06     | 53.55     |
| Wint3R          | 0.28        | 0.21     | 77.28     | 0.03           | 0.07     | 78.81     | 0.09        | 0.04     | 56.96     |
| Stream3R        | 0.44        | 0.28     | 72.87     | **0.02**       | 0.09     | 78.79     | 0.21        | 0.07     | 54.07     |
| Stream3R-w      | 0.58        | 0.37     | 67.09     | 0.04           | 0.15     | 71.94     | 0.20        | 0.06     | 53.74     |
| **LingBot-Map** | **0.09**    | **0.03** | **98.98** | **0.02**       | **0.07** | **80.39** | **0.07**    | **0.03** | **64.26** |

Best F1 on all three. The paper notes the 7-Scenes margin is modest ("most methods already perform reasonably well") because room-scale trajectories are short, and that the largest relative gains appear where drift matters: NRGBD +7.30 F1 over Wint3R, ETH3D +21.70.

### Ablation on TartanGround

원논문 Table 6. TartanAir·TartanGround로 파인튜닝 후 320프레임(stride 8, 실제 시간 범위 ~2,400프레임) 검증셋에서 평가. 실험 하나당 약 3,840 GPU 시간.

| Rel. Loss | A. Init. | Co. Tok. | V. RoPE | AUC@3 ↑   | AUC@30 ↑  | ATE ↓    | RPE-trans ↓ | RPE-rot ↓ |
| --------- | -------- | -------- | ------- | --------- | --------- | -------- | ----------- | --------- |
| ✓         |          |          |         | 9.80      | 65.84     | 8.59     | 1.62        | 2.57      |
| ✓         | ✓        |          |         | 13.63     | 68.71     | 7.88     | 1.60        | 2.90      |
|           | ✓        | ✓        |         | 13.91     | 68.25     | 8.25     | 1.67        | 5.35      |
| ✓         | ✓        | ✓        |         | 15.75     | 69.92     | 7.46     | 1.48        | 2.26      |
| ✓         | ✓        | ✓        | ✓       | **16.39** | **71.87** | **5.98** | **1.33**    | **1.93**  |

Component-by-component, as the paper reads it:

- **Anchor init** (row 1→2): AUC@3 +3.83, ATE −0.71. Resolves scale ambiguity without needing all frames.
- **Context tokens** (row 2→4): AUC@3 +2.12, AUC@30 +1.21, ATE −0.42. A 6-token summary is enough to check drift between anchor and window.
- **Relative pose loss** (row 3 vs 4): removing it degrades RPE-rot from 2.26 to 5.35 (2.4× worse) and ATE 7.46 → 8.25. Rotation is far more sensitive than translation to the loss of local pairwise supervision.
- **Video RoPE** (row 4→5): the single largest ATE gain, 7.46 → 5.98 (−1.48). Without temporal encoding the memory tokens carry geometry but no notion of _when_.

### Bounded window vs full causal attention

원논문 Table 7.

| Window Size | ATE ↓    | RPE-trans ↓ | RPE-rot ↓ | FPS ↑     | Mem (GB) ↓ |
| ----------- | -------- | ----------- | --------- | --------- | ---------- |
| 64          | **5.98** | **1.33**    | 1.93      | **20.29** | **13.28**  |
| Full        | 6.60     | 1.50        | **1.71**  | 11.87     | 36.06      |

The paper describes the bounded window as achieving **1.7× higher speed and 2.7× lower memory** while also improving ATE. Note that full attention retains a better RPE-rot (1.71 vs 1.93) — the bounded window trades a little rotation precision for a large efficiency and global-consistency gain.

### Figures without printed values

Figure 5 (trajectory comparisons on Oxford Spires, Tanks & Temples), Figure 6 (qualitative point-cloud reconstruction vs TTT3R and Wint3R), and the teaser radar plots on page 1 carry no printed numeric values usable here.

## 💡 Insights & Impact

### SLAM's state decomposition, ported to attention

The design argument is unusually clean. Classical SLAM factors its state into a reference frame (coordinate and scale), a local window (dense geometry), and a global map (drift correction). LingBot-Map keeps that factorization but makes each part a learned attention mechanism instead of a hand-crafted optimizer. The ablation validates the decomposition piecewise — each of the three contributes, and none subsumes another.

### Compact memory is enough, if it is ordered

The trajectory memory's 6 tokens per frame contribute +2.12 AUC@3, but adding Video RoPE on top contributes a _larger_ ATE gain (−1.48) than the tokens themselves did (−0.42). The lesson is that a geometric summary without temporal ordering is only half a memory: the model needs to know how far apart frames are in time and which direction the camera has been moving.

### Rotation needs pairwise supervision

Removing the relative pose loss degrades rotation 2.4× while translation barely moves. Combined with the camera-to-world parameterization choice (made precisely because world-to-camera couples rotation into translation), the paper reads as a sustained argument that rotation is the fragile quantity in long-sequence streaming pose estimation.

### Bounded context can beat unbounded context

Table 7 is the counterintuitive result: full causal attention has strictly more information available and still produces worse ATE (6.60 vs 5.98) at 1.7× the time and 2.7× the memory. Unbounded history is not free — it dilutes attention across mostly-redundant tokens. Structuring the context beats hoarding it.

### Streaming no longer implies a quality penalty

Table 2 shows an online method beating the strongest offline (DA3, 49.84 AUC@15) and optimization-based (VIPE, 45.35) baselines on the same sparse setting. The paper's explanation for the offline methods' failure is instructive: they are trained on datasets where consecutive frames are close and observe the same local region, so their learned priors do not transfer to the large viewpoint changes in Oxford Spires.

## 🔗 Related Work

- [VGGT](vggt.md) — the loss definitions and token layout LingBot-Map builds from; also an offline baseline it beats by 2.6× on Oxford Spires AUC@15
- [π³](pi3.md) — source of the relative pose loss over window pairs; an offline baseline in Table 2
- [CUT3R](../dynamic/cut3r.md) — the strongest online competitor on Oxford Spires; degrades 14.31 ATE from sparse to dense
- [TTT3R](ttt3r.md) and [Stream3R](stream3r.md) — online streaming baselines across every table
- [StreamVGGT](streamvggt.md) — causal-attention streaming baseline
- [Spann3R](spann3r.md) — early memory-based streaming reconstruction
- [FastVGGT](fastvggt.md) — efficiency-focused offline baseline in Table 2
- [Fast3R](fast3r.md) and [SLAM3R](slam3r.md) — additional baselines
- [Depth Anything 3](depth-anything-3.md) — the DA3 offline baseline, strongest non-LingBot method on Oxford Spires
- [DUSt3R](../foundation/dust3r.md) — the global point-cloud normalization the anchor context replaces

## 📚 Key Takeaways

1. **Three contexts, three jobs.** Anchor for scale, window for registration, memory for drift — each ablates to a measurable loss, mirroring SLAM's own state decomposition.
2. **6 tokens per frame keeps cost near-constant.** Per-frame growth is ~80× lower than causal attention at M≈500; at T=10,000 that is ~7×10⁴ retained tokens versus ~5×10⁶.
3. **Ordering matters more than capacity.** Video RoPE gives a larger ATE gain (−1.48) than the trajectory memory tokens it orders (−0.42).
4. **Bounded beats unbounded.** A 64-frame window outperforms full causal attention on ATE while running 1.7× faster in 2.7× less memory.
5. **Near-constant degradation over 12× sequence length**: ATE 6.42 → 7.11, where CUT3R goes 18.16 → 32.47.
6. **Not uniformly best.** VIPE and MegaSAM retain better RPE-trans; CUT3R and TTT3R run faster; full attention keeps better RPE-rot.

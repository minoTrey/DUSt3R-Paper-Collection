# FastVGGT: Training-Free Acceleration of Visual Geometry Transformer (ICLR 2026)

## 📋 Overview

- **Authors**: You Shen, Zhipeng Zhang, Yansong Qu, Xiawu Zheng, Jiayi Ji, Shengchuan Zhang, Liujuan Cao
- **Institution**: Key Laboratory of Multimedia Trusted Perception and Efficient Computing (Ministry of Education of China), Xiamen University; AutoLab, School of Artificial Intelligence, Shanghai Jiao Tong University
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2509.02560) | [Code](https://github.com/mystorm16/FastVGGT) | [Project Page](https://mystorm16.github.io/fastvggt/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Profiles VGGT to identify global attention as the long-sequence bottleneck, observes token collapse in its attention maps, and applies a 3D-tailored token merging scheme that is entirely training-free — reported as a 4× speedup on 1000-image inputs while also reducing error accumulation.

## 🎯 Key Contributions

1. **Bottleneck identification**: Component-wise profiling shows that frame attention and global attention are comparable at short sequences, but global attention dominates runtime as frame count grows (Figure 2). Flash-Attention reduces memory from O(n²) to O(nd) but leaves time complexity at O(n²d).
2. **Token collapse observation**: Attention maps across tokens and blocks are highly similar (Figure 3). The paper reframes this not as a defect in VGGT's two-stage design — global attention deliberately distills global semantics, frame attention reintroduces local variability — but as exploitable redundancy.
3. **First token merging in feed-forward 3D geometry models**, with a partitioning strategy designed for the 3D setting rather than transplanted from 2D vision.
4. **Three-category token partition**: salient / destination (dst) / source (src), instead of the conventional two.
5. **VRAM-efficient VGGT\***: Discarding unused intermediate block outputs raises the OOM ceiling from ~300 frames to over 1000 without affecting reconstruction quality. All experiments use VGGT\* as the baseline.

## 🔧 Technical Details

### Why 2D token merging fails here

The paper tests conventional partitioning directly in VGGT's global attention layer before proposing anything.

원논문 Table 1. r은 merging ratio, s는 dst 토큰 선택 stride. Baseline은 병합 없음.

| Setting | Random r = 0.5 | Random r = 0.8 | Fixed s = 5 | Fixed s = 8 | Baseline |
| ------- | -------------- | -------------- | ----------- | ----------- | -------- |
| CD ↓    | 0.32           | 0.44           | 0.33        | 0.77        | **0.21** |
| Time ↓  | 22.6           | 16.9           | 17.2        | **11.6**    | 30.4     |

Both reduce time and both significantly increase Chamfer Distance — the motivation for a tailored design.

### The five-step merging pipeline

```text
1. Fix first-frame tokens as Dst  → global reference, exempt from merging
2. Retain top salient tokens      → cross-frame correspondence anchors
3. Region-based random sampling   → spatially balanced Src/Dst within each frame
4. Fuse Src into nearest Dst      → reduces sequence length in Global Attention
5. Unmerge Src from Dst           → restores per-token resolution for dense heads
```

Three governing principles: preserve cross-frame correspondence, merge uniformly within each frame to avoid over-compression, and merge the most redundant tokens into the most representative ones.

- **Reference token selection**: VGGT defines the first frame as the world coordinate system and tokens consistently show stronger activation toward it, so all first-frame tokens become dst.
- **Salient token selection**: A top-k strategy on token norms measures distinctiveness, but its cost grows with sequence length; the default is fixed-stride sampling retaining about 10% of tokens per frame, which the paper reports achieves accuracy comparable to top-k at much lower cost.
- **Merging and unmerging**: cosine similarity assigns each src to its nearest dst; the pair is averaged (`x'_d = (x_d + x_s)/2`) and later replicated back (`x'_1 = x'_2 = x*_{1,2}`). An explicit src–dst mapping makes unmerging deterministic.

### Setup

Architecture follows VGGT with L = 24 frame and global attention layers, FlashAttention-2 integrated. All experiments on a single NVIDIA A800 (80 GiB). ScanNet-50 is a reproducible benchmark of 50 scenes uniformly sampled from ScanNet's 1,500.

## 📊 Results

### Point cloud reconstruction on ScanNet-50

원논문 Table 2. OOM은 out-of-memory.

| Method     | CD ↓ (1000) | Time ↓ (1000) | CD ↓ (500) | Time ↓ (500) | CD ↓ (300) | Time ↓ (300) | CD ↓ (100) | Time ↓ (100) |
| ---------- | ----------- | ------------- | ---------- | ------------ | ---------- | ------------ | ---------- | ------------ |
| π³         | OOM         | OOM           | OOM        | OOM          | OOM        | OOM          | OOM        | OOM          |
| StreamVGGT | OOM         | OOM           | OOM        | OOM          | OOM        | OOM          | OOM        | OOM          |
| Fast3R     | 0.684       | 397.8s        | 0.701      | 97.3s        | 0.711      | 34.9s        | 0.723      | 4.8s         |
| CUT3R      | 0.786       | 34.8s         | 0.774      | 18.8s        | 0.775      | 11.1s        | 0.767      | 3.6s         |
| VGGT\*     | 0.471       | 724.6s        | 0.420      | 177.5s       | 0.416      | 131.4s       | 0.423      | 9.1s         |
| FastVGGT   | **0.425**   | **180.7s**    | **0.411**  | **55.2s**    | 0.416      | **23.8s**    | 0.426      | **5.4s**     |

The paper's stated speedup claim is **4× at 1000 input images** (abstract and conclusion). At 100 frames FastVGGT is marginally _worse_ in CD than the baseline (0.426 vs 0.423) — the accuracy benefit only appears once error accumulation matters.

### Point cloud reconstruction on 7 Scenes

원논문 Table 3. Stride는 키프레임 샘플링 간격. Mean 값만 옮긴다.

| Method     | Acc ↓ (S3) | Comp ↓ (S3) | NC ↑ (S3) | Time ↓ (S3) | Acc ↓ (S10) | Comp ↓ (S10) | NC ↑ (S10) | Time ↓ (S10) |
| ---------- | ---------- | ----------- | --------- | ----------- | ----------- | ------------ | ---------- | ------------ |
| π³         | OOM        | OOM         | OOM       | OOM         | OOM         | OOM          | OOM        | OOM          |
| StreamVGGT | OOM        | OOM         | OOM       | OOM         | OOM         | OOM          | OOM        | OOM          |
| Fast3R     | 0.045      | 0.047       | 0.616     | 43.7s       | 0.040       | 0.056        | 0.639      | 5.5s         |
| CUT3R      | 0.179      | 0.097       | 0.588     | 14.5s       | 0.041       | 0.029        | 0.651      | 4.2s         |
| VGGT\*     | 0.019      | 0.027       | 0.611     | 76.7s       | 0.020       | 0.027        | 0.623      | 8.7s         |
| FastVGGT   | **0.018**  | **0.026**   | **0.617** | **28.0s**   | **0.018**   | 0.027        | **0.628**  | **5.1s**     |

### Point cloud reconstruction on NRGBD

원논문 Table 4. Mean 값만 옮긴다.

| Method   | Acc ↓ (S3) | Comp ↓ (S3) | NC ↑ (S3) | Time ↓ (S3) | Acc ↓ (S10) | Comp ↓ (S10) | NC ↑ (S10) | Time ↓ (S10) |
| -------- | ---------- | ----------- | --------- | ----------- | ----------- | ------------ | ---------- | ------------ |
| Fast3R   | 0.074      | 0.024       | 0.658     | 68.9s       | 0.061       | 0.031        | 0.669      | 7.4s         |
| CUT3R    | 0.346      | 0.184       | 0.579     | 18.3s       | 0.132       | 0.056        | 0.669      | 5.7s         |
| VGGT\*   | 0.029      | **0.018**   | 0.727     | 136.1s      | **0.016**   | **0.017**    | 0.735      | 13.9s        |
| FastVGGT | 0.029      | 0.019       | **0.730** | **53.1s**   | 0.018       | 0.018        | **0.736**  | **7.3s**     |

On NRGBD, FastVGGT matches or slightly trails VGGT\* on accuracy and completeness while leading on normal consistency — the honest summary is parity, bought at roughly half the runtime.

### Camera pose estimation on ScanNet-50

원논문 Table 5. Baseline은 VGGT\*.

| Input Frames | ATE ↓ Baseline | ATE ↓ Ours | ARE ↓ Baseline | ARE ↓ Ours | RPE-rot ↓ Baseline | RPE-rot ↓ Ours | RPE-trans ↓ Baseline | RPE-trans ↓ Ours |
| ------------ | -------------- | ---------- | -------------- | ---------- | ------------------ | -------------- | -------------------- | ---------------- |
| 1000         | 0.196          | **0.164**  | 4.636          | **3.860**  | 0.997              | **0.667**      | 0.039                | **0.029**        |
| 500          | 0.174          | **0.145**  | 4.190          | **3.591**  | 0.963              | **0.627**      | 0.042                | **0.031**        |
| 300          | 0.145          | **0.142**  | 3.689          | **3.554**  | **0.786**          | 0.801          | 0.040                | **0.036**        |
| 100          | **0.140**      | 0.141      | 3.625          | **3.512**  | **1.224**          | 1.262          | **0.058**            | 0.061            |

The pattern is consistent with the reconstruction results: FastVGGT matches the baseline on short sequences (and is fractionally worse on three of four 100-frame metrics) and substantially reduces error on long ones.

### Ablation: token partitioning

원논문 Table 6. ScanNet-50의 500프레임 입력.

| Variant | Uniform | Reference | Salient | CD ↓      | ATE ↓     |
| ------- | ------- | --------- | ------- | --------- | --------- |
| (a)     | -       | -         | -       | 0.947     | 0.842     |
| (b)     | ✓       | -         | -       | 0.637     | 0.722     |
| (c)     | ✓       | ✓         | -       | 0.431     | 0.149     |
| (d)     | ✓       | ✓         | ✓       | **0.411** | **0.141** |

Fixing the first frame as the global reference is the dominant factor: CD drops 0.637 → 0.431 and ATE collapses 0.722 → 0.149 from that step alone.

### Ablation: merging location and intensity

원논문 Table 7. 열은 merging ratio, 행은 병합을 시작하는 block.

| Blocks | CD ↓ (0.3) | Time ↓ (0.3) | CD ↓ (0.6) | Time ↓ (0.6) | CD ↓ (0.9) | Time ↓ (0.9) |
| ------ | ---------- | ------------ | ---------- | ------------ | ---------- | ------------ |
| 0      | 0.408      | 119.8s       | 0.415      | 64.3s        | 0.411      | **55.2s**    |
| 10     | 0.418      | 146.2s       | 0.424      | 118.4s       | 0.431      | 106.3s       |
| 20     | 0.423      | 172.9s       | 0.427      | 169.1s       | 0.411      | 157.3s       |

Increasing the merging ratio consistently reduces time with only minor CD fluctuation, so the adopted default is aggressive: a 90% merging ratio applied from block 0 across all subsequent layers.

## 💡 Insights & Impact

### Redundancy as a design opportunity

The most interesting move in the paper is interpretive. Attention-map similarity is normally called feature degradation and treated as a problem to correct (as DINO's Gram Anchoring does). FastVGGT argues that in VGGT's two-stage design the collapse in global attention is _deliberate distillation of global semantics_, with frame attention restoring local variability — so it is safe to exploit rather than necessary to fix.

### Acceleration that improves accuracy

Reducing the number of tokens in global attention also reduces the token space over which minor inaccuracies get amplified. That is why FastVGGT both speeds up inference and lowers pose error on 500- and 1000-frame sequences, rather than paying the usual efficiency-accuracy tax. The paper is careful to note this benefit does not appear at 100 frames.

### The engineering contribution is not incidental

VGGT\* — discarding intermediate outputs from the 20 of 24 encoder blocks that inference never reads — is what makes the whole comparison possible. Without it the baseline OOMs at ~300 frames and there is no 1000-image experiment to run.

## 🔗 Related Work

- [VGGT](vggt.md) — the sole acceleration target. FastVGGT changes no weights, only which tokens enter global attention.
- [StreamVGGT](streamvggt.md) — the causal-attention route to efficiency; FastVGGT reports it as OOM across all tested sequence lengths on ScanNet-50, 7 Scenes, and NRGBD.
- [CUT3R](../dynamic/cut3r.md) — the constant-memory recurrent baseline; fast on long sequences but with substantially worse reconstruction quality here.
- [Fast3R](fast3r.md) — the other 1000+-image feed-forward design, used as a long-sequence baseline.
- [Pi3](pi3.md) — π³, evaluated as a recent SOTA that OOMs on these benchmarks.
- [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) — the lineage the paper traces VGGT back to.
- [TTT3R](ttt3r.md) — solves the same long-sequence problem from the recurrent side rather than by pruning global attention.

## 📚 Key Takeaways

1. **Global attention is the whole bottleneck.** Component-wise profiling, not intuition, drives the design — frame attention and decoding stay cheap while global attention runs away with the runtime budget.
2. **2D token merging does not transfer.** Random and fixed-stride partitioning both degrade Chamfer Distance badly; the 3D setting needs a reference frame, salient-token protection, and spatially balanced sampling.
3. **The reference frame matters most.** Ablation (b) → (c) accounts for most of the accuracy recovery, because VGGT's first frame defines the world coordinate system.
4. **4× at 1000 images is the paper's own figure**, and it comes with reduced pose drift rather than degraded quality — but the advantage is specific to long sequences, not short ones.
5. **Training-free means immediately usable**: no retraining, no new parameters, full compatibility with the released VGGT architecture.

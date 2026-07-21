# Spark3R: Asymmetric Token Reduction Makes Fast Feed-Forward 3D Reconstruction (arXiv preprint 2026-05)

## 📋 Overview

- **Authors**: Zecheng Tang, Jiaye Fu, Qiankun Gao, Haijie Li, Yanmin Wu, Jiaqi Zhang, Siwei Ma, Jian Zhang
- **Institution**: Peking University
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.06270)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free, plug-and-play acceleration framework that decouples token compression in feed-forward 3D reconstruction: query tokens (sensitive) get gentle intra-group merging while key-value tokens (compressible) get aggressive pruning, plus a layer-adaptive KV schedule — reaching up to 28× speedup on 1,000-frame inputs.

## 🎯 Key Contributions

1. **Asymmetric token reduction**: The insight that query tokens encode view-specific geometric requests (compression-sensitive) while key-value tokens form a shared scene context (compression-tolerant). Separate factors rQ and rKV (rKV > rQ) with distinct operators are assigned to each.
2. **Intra-group query merging**: Because standard merge pairs are overwhelmingly local (peaking at 1-frame distance, virtually none beyond 20 frames), merging is restricted to groups of G = 20 consecutive frames, cutting matching cost from O(S²) to O(S·G).
3. **Lightweight KV pruning**: Since matched key/value source–destination pairs almost all exceed cosine similarity 0.9, the destination-averaging update is dropped and KV compression reduces to pure temporal-stride pruning with negligible overhead.
4. **Layer-adaptive KV schedule**: A one-time offline probe splits layers into high-/low-sensitivity tiers (degradation-ratio threshold 1.05×); low-sensitivity layers get an elevated reduction factor (multiplier l = 3).

## 🔧 Technical Details

### Length-adaptive reduction factors

- Query merging: rQ = 1 (S ≤ 100), 2 (100 < S ≤ 300), 3 (300 < S ≤ 500), 4 (S > 500).
- KV pruning: rKV = 1 (S ≤ 100), ⌈S/40⌉ otherwise.
- On short sequences (e.g., Sintel ≤ 50 frames) both base factors collapse to 1, but the layer-adaptive schedule still applies an elevated rKV = 3 to low-sensitivity layers.

### Integration and setup

- Plug-and-play into VGGT, π³, Depth-Anything-3 (Giant), and VGGT-Ω — no retraining.
- Sensitivity probe: raise a single layer's factor from 32 to 256 with others fixed at 32; sensitive layers cluster mid-to-late (layers 11–16 in VGGT and π³, 3–12 in DA3, 10–13/15–17/21 in VGGT-Ω).
- Evaluation retains up to 1,000 frames per sequence (extending the TTT3R protocol). Single NVIDIA H20 GPU in bfloat16 (float32 for SVD heads).

## 📊 Results

### Point map estimation on 7-Scenes

원논문 Table I. Time·Acc·Comp 낮을수록, NC 높을수록 좋음. VGGT-Ω는 제출 후 공개돼 별도 비교.

| Method      | Time(s) ↓ | Acc Mean ↓ | Acc Med ↓ | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑ | NC Med ↑ |
| ----------- | --------- | ---------- | --------- | ----------- | ---------- | --------- | -------- |
| CUT3R       | 69.5      | 0.197      | 0.126     | 0.074       | 0.021      | 0.536     | 0.552    |
| TTT3R       | 69.2      | 0.103      | 0.061     | 0.056       | 0.024      | 0.566     | 0.599    |
| VGGT        | 1102.7    | 0.047      | 0.018     | 0.035       | 0.013      | 0.601     | 0.656    |
| DA3         | 976.4     | 0.015      | 0.006     | 0.018       | 0.009      | 0.620     | 0.687    |
| π³          | 830.2     | 0.012      | 0.006     | 0.016       | 0.010      | 0.646     | 0.729    |
| FastVGGT    | 247.2     | 0.043      | 0.010     | 0.025       | 0.009      | 0.595     | 0.646    |
| ZipMap      | 46.2      | 0.019      | 0.007     | 0.025       | 0.009      | 0.605     | 0.661    |
| Ours+VGGT   | 40.7      | 0.017      | 0.007     | 0.020       | 0.010      | 0.617     | 0.681    |
| Ours+DA3    | 58.0      | 0.015      | 0.006     | 0.018       | 0.009      | 0.620     | 0.687    |
| Ours+π³     | 34.1      | 0.012      | 0.006     | 0.016       | 0.010      | 0.644     | 0.726    |
| VGGT-Ω      | 505.3     | 0.015      | 0.007     | 0.014       | 0.007      | 0.608     | 0.667    |
| Ours+VGGT-Ω | 27.7      | 0.014      | 0.007     | 0.014       | 0.007      | 0.606     | 0.664    |

### Point map estimation on NRGBD

원논문 Table I.

| Method      | Time(s) ↓ | Acc Mean ↓ | Acc Med ↓ | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑ | NC Med ↑ |
| ----------- | --------- | ---------- | --------- | ----------- | ---------- | --------- | -------- |
| CUT3R       | 70.1      | 0.415      | 0.310     | 0.197       | 0.080      | 0.551     | 0.576    |
| TTT3R       | 70.3      | 0.262      | 0.181     | 0.117       | 0.040      | 0.571     | 0.604    |
| VGGT        | 1110.4    | 0.042      | 0.030     | 0.025       | 0.008      | 0.798     | 0.907    |
| DA3         | 983.3     | 0.012      | 0.006     | 0.015       | 0.004      | 0.898     | 0.979    |
| π³          | 835.7     | 0.014      | 0.007     | 0.016       | 0.005      | 0.884     | 0.974    |
| FastVGGT    | 245.7     | 0.024      | 0.017     | 0.018       | 0.007      | 0.768     | 0.891    |
| ZipMap      | 46.6      | 0.022      | 0.012     | 0.016       | 0.006      | 0.766     | 0.891    |
| Ours+VGGT   | 40.9      | 0.014      | 0.009     | 0.016       | 0.005      | 0.863     | 0.964    |
| Ours+DA3    | 56.9      | 0.012      | 0.006     | 0.015       | 0.004      | 0.899     | 0.979    |
| Ours+π³     | 34.3      | 0.014      | 0.008     | 0.016       | 0.005      | 0.880     | 0.971    |
| VGGT-Ω      | 508.4     | 0.015      | 0.009     | 0.008       | 0.005      | 0.829     | 0.948    |
| Ours+VGGT-Ω | 27.8      | 0.014      | 0.008     | 0.007       | 0.005      | 0.835     | 0.948    |

### Camera pose estimation (ATE / RPEt / RPEr, Sim(3)-aligned)

원논문 Table II. 모든 지표 낮을수록 좋음. Time(s)은 시퀀스 처리 시간.

| Method      | TUM Time ↓ | TUM ATE ↓ | TUM RPEt ↓ | TUM RPEr ↓ | SN Time ↓ | SN ATE ↓ | SN RPEt ↓ | SN RPEr ↓ |
| ----------- | ---------- | --------- | ---------- | ---------- | --------- | -------- | --------- | --------- |
| CUT3R       | 81.6       | 0.165     | 0.007      | 0.534      | 86.5      | 0.783    | 0.021     | 0.841     |
| TTT3R       | 81.4       | 0.110     | 0.009      | 0.451      | 87.1      | 0.424    | 0.021     | 0.595     |
| VGGT        | 993.7      | 0.018     | 0.009      | 0.294      | 1162.7    | 0.156    | 0.055     | 1.532     |
| DA3         | 870.8      | 0.018     | 0.009      | 0.295      | 1018.1    | 0.057    | 0.013     | 0.350     |
| π³          | 739.4      | 0.022     | 0.008      | 0.295      | 865.1     | 0.056    | 0.011     | 0.264     |
| FastVGGT    | 253.8      | 0.020     | 0.010      | 0.297      | 256.8     | 0.078    | 0.025     | 0.565     |
| ZipMap      | 44.6       | 0.021     | 0.010      | 0.314      | 43.6      | 0.066    | 0.017     | 0.361     |
| Ours+VGGT   | 38.4       | 0.016     | 0.010      | 0.297      | 41.3      | 0.065    | 0.019     | 0.403     |
| Ours+DA3    | 54.0       | 0.016     | 0.008      | 0.291      | 57.8      | 0.057    | 0.012     | 0.320     |
| Ours+π³     | 32.2       | 0.022     | 0.008      | 0.298      | 34.6      | 0.058    | 0.012     | 0.280     |
| VGGT-Ω      | 448.7      | 0.008     | 0.005      | 0.263      | 525.1     | 0.067    | 0.018     | 0.463     |
| Ours+VGGT-Ω | 28.7       | 0.009     | 0.006      | 0.278      | 28.0      | 0.063    | 0.019     | 0.426     |

### Camera pose on Sintel (short sequences, ~46 frames)

원논문 Table II. Sintel은 최대 50프레임으로 global attention 병목 구간이 아님.

| Method      | Time(s) ↓ | ATE ↓ | RPEt ↓ | RPEr ↓ |
| ----------- | --------- | ----- | ------ | ------ |
| VGGT        | 2.0       | 0.172 | 0.062  | 0.469  |
| DA3         | 2.6       | 0.102 | 0.053  | 0.441  |
| π³          | 1.6       | 0.073 | 0.038  | 0.294  |
| ZipMap      | 3.9       | 0.134 | 0.067  | 0.429  |
| Ours+VGGT   | 1.6       | 0.172 | 0.058  | 0.478  |
| Ours+DA3    | 2.6       | 0.100 | 0.050  | 0.431  |
| Ours+π³     | 1.4       | 0.073 | 0.038  | 0.295  |
| VGGT-Ω      | 1.3       | 0.039 | 0.026  | 0.238  |
| Ours+VGGT-Ω | 1.2       | 0.039 | 0.027  | 0.236  |

## 💡 Insights & Impact

- **Attention-dilution effect**: On long sequences Spark3R+VGGT often _beats_ unaccelerated VGGT — e.g., ScanNet ATE drops 0.156 → 0.065 and 7-Scenes mean Accuracy 0.047 → 0.017 — because pruning key-value context keeps per-token attention mass in a robust regime.
- **Speedups**: 17×–27× on 7-Scenes/NRGBD point maps and up to 28× on long-sequence pose (TUM-dynamics, ScanNet) versus the base models, while DA3/π³ metrics stay within negligible margins of their baselines.
- **vs. other accelerators**: Faster than ZipMap on most settings while matching or exceeding quality, and no retraining (ZipMap fine-tunes a 1.4B model 180K steps on 64 H100s; VGG-T3 needs 100K steps on 8 A100s). FastVGGT is ~6× slower than Spark3R+VGGT at comparable or lower quality.
- **Honest losses**: On Sintel depth, ZipMap outperforms Spark3R+VGGT and Spark3R+DA3 in Abs Rel and δ<1.25 (video-depth Table III); and on VGGT-Ω TUM-dynamics pose, Spark3R trails the base model slightly.
- **Generalizes to VGGT-Ω**: an 18× point-map speedup while matching quality, plus 16×/19× on TUM/ScanNet pose.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)** / **[π³](../reconstruction/pi3.md)** / **[VGGT-Ω](../reconstruction/vggt-omega.md)**: Base feed-forward models Spark3R accelerates (with DA3).
- **[FastVGGT](../reconstruction/fastvggt.md)** / **[LiteVGGT](../reconstruction/litevggt.md)**: Uniform token-merging accelerators; Spark3R argues their uniform factor caps speedups near ~10×.
- **[CUT3R](../dynamic/cut3r.md)** / **[StreamVGGT](../reconstruction/streamvggt.md)**: Streaming/memory approaches that restrict cross-frame reasoning; Spark3R keeps full global context.
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Pairwise predecessors fused via post-hoc alignment.

## 📚 Key Takeaways

1. **Query and key-value tokens are not symmetric**: queries degrade sharply beyond a reduction factor of ~12 while KV tolerates aggressive compression — uniform merging leaves headroom on the table.
2. **Different operators for different roles**: intra-group merging for queries, pure pruning for KV, plus a two-tier layer-adaptive KV schedule.
3. **Training-free and general**: up to 28× speedup across VGGT, π³, DA3, and VGGT-Ω with competitive (sometimes better) reconstruction quality and no retraining.

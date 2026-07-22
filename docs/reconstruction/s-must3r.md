# S-MUSt3R: Sliding Multi-view 3D Reconstruction (arXiv preprint)

![s-must3r — architecture](https://arxiv.org/html/2602.04517/fig/tum/tum-fr1-desk.png)

_Segment pose correction with lightweight loop closure, for TUM (top) and 7-Scenes (down) datasets. (원논문 Fig. 4)_

## 📋 Overview

- **Authors**: Leonid Antsfeld, Boris Chidlovskii, Yohann Cabon, Vincent Leroy, Jerome Revaud
- **Institution**: NAVER LABS Europe
- **Venue**: arXiv preprint (2026-02)
- **Note**: 원논문 1페이지에 소속 표기가 없다. 소속은 NAVER LABS Europe 공식 출판 목록에서 확인했다 — <https://europe.naverlabs.com/research/publications/s-must3r-sliding-multi-view-3d-reconstruction/> / The venue could not be confirmed from any primary source (no arXiv comment, OpenReview record, CVF entry, or GitHub badge stating acceptance). It is recorded as a preprint and should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2602.04517) | [MUSt3R Code](https://github.com/naver/must3r)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free sliding-window pipeline that cuts a long RGB stream into overlapping segments, runs stock MUSt3R on each, and stitches them with confidence/depth-weighted SIM(3) alignment plus a segment-level pose graph with lightweight loop closure — extending MUSt3R to sequences that exceed its memory limit while keeping metric-scale output.

## 🎯 Key Contributions

1. **Segment-and-stitch without retraining**: the pretrained `MUSt3R_512.pth` checkpoint (ViT-L encoder, ViT-B decoder) is used unchanged; all additions are at the pipeline level.
2. **Confidence modulated by cross-segment depth disagreement**: because the same image appears in two adjacent segments with different context, MUSt3R often predicts different depths for it. That disagreement is turned into a signal for down-weighting unreliable points.
3. **Dual alignment edges**: each adjacent segment pair contributes _two_ pose-graph edges — one estimated from pointmap correspondences (`T^x`), one from camera poses (`T^p`). Both are kept.
4. **Loop closure via a synthesized bridging segment**: rather than adding a direct edge between distant segments, a _new_ segment `S_L` is built by concatenating frames around both loop images and reconstructed by MUSt3R, then chained into the graph.
5. **Segment-level pose graph**: nodes are segments, not frames, so the graph is far smaller than the frame-level factor graphs of MASt3R-SLAM and VGGT-SLAM, and Levenberg-Marquardt converges in a few iterations.
6. **Metric-space output preserved**: inherited from MUSt3R, with scale estimation error reported as under 2% on both TUM and 7-Scenes.

## 🔧 Technical Details

### Segmentation

`N` images are partitioned into overlapping segments of fixed length `l` and overlap `p`. Segment `S_1` is frames 1…l, `S_2` is frames l−p+1…2l−p, and so on. Default configuration for the main comparisons: **l = 60, p = 30, SIM(3)**, chosen to match VGGT-Long's setup.

### Depth-disagreement confidence

For pixel `p` of an image `I` present in both overlapping segments `S_i` and `S_j`, with confidences `c_ip, c_jp` and depths `d_ip, d_jp`:

```text
w = (c_ip · c_jp) / (1 + |d_ip − d_jp|)
c'_ip = w · c_ip,   c'_jp = w · c_jp
```

Points that two segments agree on are trusted; points where the model contradicts itself are suppressed before alignment.

### Alignment

For adjacent segments, 3D correspondences and confidences within the overlap are used in an Iteratively Reweighted Least Squares problem with a Huber loss ρ:

```text
T^x_{k,k+1} = argmin_{T∈𝒯}  Σ_i ρ( ‖X_i^k − T X_i^{k+1}‖² )
```

and the same objective is run on camera poses instead of pointmaps:

```text
T^p_{k,k+1} = argmin_{T∈𝒯}  Σ_i ρ( ‖P_i^k − T P_i^{k+1}‖² )
```

The pose-based alignment is nearly free — the pose set is tiny compared to a pointmap. For SL(4), IRLS is not applicable; the h-solver from VGGT-SLAM is used to estimate a relative homography instead.

### Transform groups

Three Lie groups of increasing expressiveness are considered:

| Group     | Includes                                 |
| --------- | ---------------------------------------- |
| SIM(3)    | rotation, translation, uniform scale     |
| Affine(3) | + non-uniform scale, shearing            |
| SL(4)     | translation, scaling, projective warping |

### Loop detection

MUSt3R's encoder patch features are average-pooled into a compact global descriptor `f` per image. A KDTree over these descriptors supports nearest-neighbor search. A pair `(I, I')` with `I ∈ S_i`, `I' ∈ S_j`, `|i − j| > 2` is a loop candidate if cosine similarity exceeds `σ_sim = 0.95`; two distant segments need at least `k_min = 3` candidates to declare a loop.

For a validated loop, a bridging segment `S_L` is formed from the frames surrounding both `I` and `I'` and reconstructed by MUSt3R. This gives a local reconstruction containing genuinely distant views of the same place. Four transforms (`T^x_{i,L}`, `T^p_{i,L}`, `T^x_{L,j}`, `T^p_{L,j}`) then wire `S_i` and `S_j` together through it.

### Global optimization

The pose graph mixes sequential constraints from adjacent segments with loop constraints from non-adjacent ones, and is solved by Levenberg-Marquardt. Because it is segment-wise, the graph is small and convergence takes few iterations.

### Evaluation setup

RMSE of Absolute Pose Error (APE) via the EVO toolkit, plus Average Angular Error (AAE). Baseline numbers are taken from the MASt3R-SLAM and VGGT-SLAM papers, including the uncalibrated DROID-SLAM variant that estimates intrinsics automatically. Both VGGT-Long and S-MUSt3R results in Tables I–II are reported after rescaling.

## 📊 Results

### APE RMSE on TUM RGB-D

원논문 TABLE I. 회색 행(Calibr.)은 보정된 내부 파라미터를 사용한 결과, \* 표시는 uncalibrated 모드로 평가한 베이스라인이다.

| Setting   | Method            | 360       | desk      | desk2     | floor     | plant     | room      | rpy       | teddy     | xyz   | Avg       |
| --------- | ----------------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | ----- | --------- |
| Calibr.   | ORB-SLAM3         | ×         | 0.017     | 0.210     | ×         | 0.034     | ×         | ×         | ×         | 0.009 | N/A       |
| Calibr.   | DeepV2D           | 0.243     | 0.166     | 0.379     | 1.653     | 0.203     | 0.246     | 0.105     | 0.316     | 0.064 | 0.375     |
| Calibr.   | DeepFactors       | 0.159     | 0.170     | 0.253     | 0.169     | 0.305     | 0.364     | 0.043     | 0.601     | 0.035 | 0.233     |
| Calibr.   | DPV-SLAM          | 0.112     | 0.018     | 0.029     | 0.057     | 0.021     | 0.330     | 0.030     | 0.084     | 0.010 | 0.076     |
| Calibr.   | DPV-SLAM++        | 0.132     | 0.018     | 0.029     | 0.050     | 0.022     | 0.096     | 0.032     | 0.098     | 0.010 | 0.054     |
| Calibr.   | GO-SLAM           | 0.089     | 0.016     | 0.028     | 0.025     | 0.026     | 0.052     | 0.019     | 0.048     | 0.010 | 0.035     |
| Calibr.   | DROID-SLAM        | 0.111     | 0.018     | 0.042     | 0.021     | 0.016     | 0.049     | 0.026     | 0.048     | 0.012 | 0.038     |
| Calibr.   | MASt3R-SLAM       | 0.049     | 0.016     | 0.024     | 0.025     | 0.020     | 0.061     | 0.027     | 0.041     | 0.009 | 0.030     |
| Uncalibr. | DROID-SLAM\*      | 0.202     | 0.032     | 0.091     | 0.064     | 0.045     | 0.918     | 0.056     | 0.045     | 0.012 | 0.158     |
| Uncalibr. | MASt3R-SLAM\*     | 0.070     | 0.035     | 0.055     | 0.056     | 0.035     | 0.118     | 0.041     | 0.114     | 0.020 | 0.060     |
| Uncalibr. | VGGT-SLAM, SIM(3) | 0.123     | 0.040     | 0.055     | 0.254     | **0.022** | 0.088     | 0.041     | **0.032** | 0.016 | 0.074     |
| Uncalibr. | VGGT-SLAM, SL(4)  | 0.071     | **0.025** | **0.040** | 0.141     | 0.023     | 0.102     | 0.030     | 0.034     | 0.014 | 0.053     |
| Uncalibr. | VGGT-Long         | 0.063     | 0.059     | 0.045     | 0.108     | 0.057     | 0.172     | 0.056     | 0.137     | 0.051 | 0.083     |
| Uncalibr. | **S-MUSt3R**      | **0.062** | 0.031     | 0.047     | **0.054** | 0.054     | **0.065** | **0.028** | 0.115     | 0.018 | **0.052** |

Best uncalibrated average (0.052), narrowly ahead of VGGT-SLAM SL(4) (0.053). But note the _calibrated_ MASt3R-SLAM still reaches 0.030 and GO-SLAM 0.035 — S-MUSt3R does not close the gap to calibrated methods. Per-sequence it loses `desk`, `desk2`, `plant`, `teddy`, and `xyz` to at least one uncalibrated competitor.

### ATE RMSE on 7-Scenes (m)

원논문 TABLE II.

| Setting   | Method            | chess     | fire      | heads     | office    | pumpkin | kitchen   | stairs | Avg   |
| --------- | ----------------- | --------- | --------- | --------- | --------- | ------- | --------- | ------ | ----- |
| Calibr.   | NICER-SLAM        | 0.033     | 0.069     | 0.042     | 0.108     | 0.200   | 0.039     | 0.108  | 0.086 |
| Calibr.   | DROID-SLAM        | 0.036     | 0.027     | 0.025     | 0.066     | 0.127   | 0.040     | 0.026  | 0.049 |
| Calibr.   | MASt3R-SLAM       | 0.053     | 0.025     | 0.015     | 0.097     | 0.088   | 0.041     | 0.011  | 0.047 |
| Uncalibr. | DROID-SLAM\*      | 0.047     | 0.038     | 0.034     | 0.136     | 0.166   | 0.080     | 0.044  | 0.078 |
| Uncalibr. | MASt3R-SLAM\*     | 0.063     | 0.046     | 0.029     | 0.103     | 0.114   | 0.074     | 0.032  | 0.066 |
| Uncalibr. | VGGT-SLAM, SIM(3) | **0.037** | **0.026** | **0.018** | 0.104     | 0.133   | 0.061     | 0.093  | 0.067 |
| Uncalibr. | VGGT-SLAM, SL(4)  | 0.036     | 0.028     | 0.018     | 0.103     | 0.133   | 0.058     | 0.093  | 0.067 |
| Uncalibr. | VGGT-Long         | 0.054     | 0.055     | 0.059     | 0.110     | 0.245   | 0.067     | 0.055  | 0.092 |
| Uncalibr. | **S-MUSt3R**      | 0.054     | 0.041     | 0.028     | **0.098** | 0.145   | **0.053** | 0.057  | 0.067 |

**On 7-Scenes S-MUSt3R does not win** — it ties VGGT-SLAM at 0.067 average and loses to both calibrated methods. The paper states this plainly: "the same APE as the top performing baselines." Its `pumpkin` (0.145) is the worst among the uncalibrated learned methods except VGGT-Long.

### Pose and angular error vs VGGT-Long on freiburg2/freiburg3

원논문 TABLE III. 동일한 segmentation 설정(l=60, p=30).

| Method    | Error | cabinet   | large cabinet | long office | nostr tex far | nostr near wl |
| --------- | ----- | --------- | ------------- | ----------- | ------------- | ------------- |
| VGGT-Long | APE ↓ | 0.095     | 0.127         | 0.167       | 0.156         | **0.154**     |
| VGGT-Long | AAE ↓ | **3.319** | 4.913         | 5.60        | **7.97**      | **2.25**      |
| S-MUSt3R  | APE ↓ | **0.072** | **0.109**     | **0.081**   | **0.091**     | 0.243         |
| S-MUSt3R  | AAE ↓ | 7.41      | **2.92**      | **2.48**    | 22.77         | 11.38         |

원논문 TABLE III (계속).

| Method    | Error | sitting half | sitting rpy | sitting stat | walking xyz | teddy     |
| --------- | ----- | ------------ | ----------- | ------------ | ----------- | --------- |
| VGGT-Long | APE ↓ | 0.211        | 0.061       | 0.014        | 0.169       | 0.170     |
| VGGT-Long | AAE ↓ | 19.87        | 93.48       | 12.71        | 15.35       | 5.575     |
| S-MUSt3R  | APE ↓ | **0.136**    | **0.054**   | **0.012**    | **0.158**   | **0.054** |
| S-MUSt3R  | AAE ↓ | **10.35**    | **84.64**   | **16.97**    | **13.04**   | **5.335** |

The paper's summary is that S-MUSt3R gives lower pose and angular errors, and it wins APE on 9 of 10 scenes. AAE is more mixed: VGGT-Long wins `cabinet` (3.319 vs 7.41), `nostr tex far` (7.97 vs 22.77), `nostr near wl` (2.25 vs 11.38), and `sitting stat` (12.71 vs 16.97).

### Robot navigation collection

원논문 TABLE IV. 사내 로봇 내비게이션 데이터.

| Method       | AAE ↓    | APE ↓     |
| ------------ | -------- | --------- |
| MASt3R-SLAM  | 29.47    | 1.580     |
| MUSt3R       | 11.87    | 1.871     |
| VGGT-Long    | 33.31    | 2.239     |
| **S-MUSt3R** | **7.10** | **0.251** |

This is the paper's strongest result by a wide margin — a 6× APE reduction over the next-best (0.251 vs 1.580). The explanation given is a specific failure mode: the other three methods work well _except_ when robots navigate a narrow corridor with featureless walls, where S-MUSt3R recovers the track thanks to segment overlaps and loop closures.

### Ablation: segment length

원논문 TABLE V. overlap은 l/2로 고정. 노란 표시는 TABLE I·II에서 사용한 설정이다.

| Method         | TUM teddy AAE ↓ | TUM teddy APE ↓ | 7-Scenes pumpkin AAE ↓ | 7-Scenes pumpkin APE ↓ |
| -------------- | --------------- | --------------- | ---------------------- | ---------------------- |
| S-MUSt3R l=20  | 9.59            | 0.185           | 3.88                   | 0.156                  |
| S-MUSt3R l=40  | 8.30            | 0.164           | 3.92                   | 0.155                  |
| S-MUSt3R l=60  | 7.66            | 0.115           | 3.77                   | 0.145                  |
| S-MUSt3R l=80  | 4.78            | 0.091           | 3.83                   | 0.146                  |
| S-MUSt3R l=100 | 6.03            | 0.141           | **3.13**               | 0.147                  |
| S-MUSt3R l=200 | 4.27            | 0.087           | 4.12                   | 0.141                  |
| **MUSt3R**     | **1.42**        | **0.061**       | 3.36                   | **0.137**              |

The honest reading: **stock MUSt3R processing the full sequence in one pass beats every S-MUSt3R configuration** on TUM teddy (1.42 AAE / 0.061 APE) and on 7-Scenes pumpkin APE. Longer segments monotonically close the gap. S-MUSt3R is a way to run MUSt3R where it otherwise cannot run at all, not an accuracy improvement over it.

### Ablation: transform groups

Reported in prose rather than a table:

- **Affine(3)** over SIM(3): only about **0.5% APE reduction**.
- **SL(4)**: up to **4% APE reduction in three sequences**, but failed to produce stable alignments in two others, requiring per-scene parameter tuning. The paper attributes this to SL(4)'s sensitivity to outliers and its tendency toward unstable homographic solutions with planar structure — an issue also noted by VGGT-SLAM.
- Beyond `l = 100`, Affine(3) and especially SL(4) transform-estimation cost rises rapidly, forcing heavy pointmap sparsification that negates the benefit of the more expressive group.

SIM(3) is therefore the default throughout.

### Ablation: loop closure and dual alignment

Also prose-only. Loop closure with global optimization gives an average **14% APE gain and 3% AAE gain on 7-Scenes**. Dropping the pointmap-based alignment edge reduces the gain by **4%**; dropping the pose-based edge reduces it by **3%**. Keeping both is the winning strategy.

### Limitation stated by the paper

The stitching approach depends strongly on the quality of the local reconstructions MUSt3R produces per segment.

## 💡 Insights & Impact

### Self-inconsistency as a confidence signal

The most portable idea here is `w = c_ip·c_jp / (1 + |d_ip − d_jp|)`. A feed-forward model given the same frame in two different contexts will disagree with itself, and that disagreement is a _free_, model-internal reliability estimate that requires no ground truth and no extra network. Any sliding-window wrapper around a feed-forward reconstructor can adopt it.

### The expressive-group question, answered empirically

VGGT-SLAM argued for SL(4) over SIM(3) to absorb uncalibrated distortion. S-MUSt3R runs the comparison inside its own pipeline and finds the extra expressiveness is not worth it: 0.5% for Affine(3), unstable for SL(4), and prohibitively expensive past l = 100. This is a useful negative result — the right group depends on what the upstream model already handles, and MUSt3R's metric predictions leave less distortion for the transform to absorb.

### Loop closure through a real reconstruction

Adding a synthesized bridging segment `S_L`, reconstructed by the same model, is stronger than adding a bare relative-pose edge: the bridge is itself a locally consistent 3D reconstruction containing views from both times, so the constraint is geometric rather than merely relational.

### Segment-level graphs are cheap

MASt3R-SLAM and VGGT-SLAM build frame-level factor graphs. With segments as nodes, the graph shrinks by roughly the segment length and LM converges in a few iterations — which is what makes "lightweight" loop closure viable in an online setting.

### Where it actually matters

The headline benchmarks show parity, not superiority. The robot navigation table is where the design pays: featureless corridors defeat MASt3R-SLAM, MUSt3R, and VGGT-Long, while overlap plus loop closure keeps S-MUSt3R at 0.251 APE. Combined with metric-scale output (<2% scale error), this makes it directly deployable for navigation, whereas VGGT-Long predictions need an external rescaling source first.

## 🔗 Related Work

- [MUSt3R](must3r.md) — the frozen backbone; the ablation shows it outperforms S-MUSt3R when it fits in memory
- [MASt3R-SLAM](mast3r-slam.md) — frame-level factor-graph competitor, best calibrated result on both benchmarks
- [VGGT-SLAM](vggt-slam.md) — source of the SL(4) h-solver and the closest uncalibrated competitor
- [MASt3R](../foundation/mast3r.md) — learned-descriptor matching predecessor
- [DUSt3R](../foundation/dust3r.md) — the pairwise pointmap formulation the whole family descends from
- [CUT3R](../dynamic/cut3r.md) and [Fast3R](fast3r.md) — the memory/recurrent alternatives to segmentation cited in the related work
- [VGGT](vggt.md) — backbone of the VGGT-Long and VGGT-SLAM baselines

## 📚 Key Takeaways

1. **A pipeline, not a model.** No retraining; stock `MUSt3R_512.pth` plus segmentation, weighted alignment, and a segment-level pose graph.
2. **Cross-segment depth disagreement is a usable confidence signal**, and cheap to compute from overlap alone.
3. **SIM(3) beats the fancier groups here.** Affine(3) gains 0.5% APE; SL(4) gains up to 4% on three sequences but destabilizes on two others and blows up in cost past l = 100.
4. **Longer segments are better**, and full-sequence MUSt3R is better still — the method trades accuracy for the ability to run at all.
5. **Parity on TUM/7-Scenes, decisive on robot navigation.** 0.052 vs 0.053 avg APE on TUM, a tie at 0.067 on 7-Scenes, but 0.251 vs 1.580–2.239 APE where featureless corridors break the baselines.
6. **Metric scale is retained** (<2% scale error), which matters more for robotics than a marginal APE win.

# PanSt3R: Multi-view Consistent Panoptic Segmentation (ICCV 2025)

## 📋 Overview

- **Authors**: Lojze Žust, Yohann Cabon, Juliette Marrie, Leonid Antsfeld, Boris Chidlovskii, Jerome Revaud, Gabriela Csurka
- **Institution**: NAVER LABS Europe
- **Venue**: ICCV 2025
- **Links**: [Paper](https://arxiv.org/abs/2506.21348)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A single forward pass over unposed RGB frames that jointly produces MUSt3R geometry and multi-view consistent 3D panoptic segmentation, removing the per-scene NeRF/3DGS test-time optimization that prior panoptic-lifting methods require.

## 🎯 Key Contributions

1. **Joint 3D + panoptic in one pass**: PanSt3R predicts scene geometry and panoptic segmentation together from unposed, uncalibrated images, rather than lifting per-frame 2D panoptic masks into an optimized implicit representation.
2. **No test-time optimization**: Existing NeRF/3DGS lifting approaches need expensive per-scene optimization; PanSt3R is feed-forward, and the paper reports run times in minutes rather than hours (Tab. 2).
3. **Multi-view mask formulation**: Mask2Former's binary-mask-plus-classification formulation is extended so that a shared set of learnable queries assigns the _same_ instance ID to a 3D object across every view it appears in.
4. **QUBO-based mask merging**: The heuristic MaskFormer merging step is replaced by a QUBO formulation that selects instances globally rather than per-frame.
5. **Optional 3DGS uplifting**: The predicted panoptic labels can be uplifted into a 3DGS scene via LUDVIG, with a panoptic regularization term added to the 3DGS optimization.

## 🔧 Technical Details

### Two frozen backbones, one token stream

Each input frame `I_n` is passed through two pretrained encoders:

- **DINOv2** — 2D semantic features `E_n^D` (feature dim 1024)
- **MUSt3R** — 3D features, both encoder `E_n^M` (1024) and decoder `D_n^M` (768), where the decoder carries MUSt3R's internal memory of previously seen images and therefore encodes _globally aligned_ geometry

Tokens correspond to 16×16 image patches. The three token maps are concatenated along the feature dimension and passed through an MLP to form joint 3D-semantic frame tokens `f_n` of dimension 768. The same concatenated maps are progressively upsampled (MLP + 2× upsampling) into high-resolution mask features `F_n` at W/2 × H/2 with `d_F = 256`.

### Mask transformer with open-vocabulary classification

Learnable queries `{q⁰_j}` are shared across all views and act as region proposals. A mask transformer cross-attends these queries to the multi-view frame tokens, producing refined queries `{q_j} = Dec_P({q⁰_j}, {f_n})`.

- **Classification** uses an open-vocabulary scheme so that datasets with different label conventions can be mixed during training: `p_{i,j} = sim(q_j^cls, t_i)`, the cosine similarity between the query's class embedding and a SigLIP text embedding of the class name.
- **Mask prediction** is a dot product against the high-resolution mask features, `M_{j,n} = sigmoid(F_n · q_j^M)`.

### Geometry head

MUSt3R's native outputs are retained: for every image it predicts a global point cloud in the first image's coordinate frame, a local point cloud, and a confidence map. Because the same queries are used across views, coloring the predicted 3D points by their selected query mask directly yields a labeled point cloud.

### Keyframe scheme

MUSt3R selects a subset of keyframes (100 by default) that are enough to generate the queries; the remaining views are then processed frame-by-frame, extracting only per-frame features and reusing the already-decoded queries for mask prediction.

### Metric

Evaluation uses **scene-PQ** — Panoptic Quality computed by treating the whole scene as a concatenation of all images, which ties predictions across views. Per-scene PQ values are averaged over the dataset. `PQ_th` / `PQ_st` split the score over thing and stuff classes.

## 📊 Results

### PanLift benchmark (scene-PQ ↑)

원논문 Table 2. † 표시는 3DGS 구축 시간이다. "Req. Poses" 열은 해당 방법이 카메라 포즈를 필요로 하는지를 나타낸다.

| Method             | Req. Poses | Hypersim | Replica  | ScanNet  | Time (min)  |
| ------------------ | ---------- | -------- | -------- | -------- | ----------- |
| DM-NeRF            | ✓          | 51.6     | 44.1     | 41.7     | ~900        |
| PNF                | ✓          | 44.8     | 41.1     | 48.3     | -           |
| PanLift            | ✓          | 60.1     | 57.9     | 58.9     | ~450        |
| Contrastive Lift   | ✓          | 62.3     | 59.1     | 62.3     | ~420        |
| PLGS               | ✓          | 62.4     | 57.8     | 58.7     | ~120        |
| PCF-Lift           | ✓          | -        | -        | 63.5     | -           |
| PanSt3R w/o QUBO   | †          | 51.6     | 57.3     | 59.5     | ~4 (+35†)   |
| **PanSt3R**        | †          | 56.5     | **62.0** | 65.7     | ~4.5 (+35†) |
| **PanSt3R+LUDVIG** | ✓          | **66.3** | 60.6     | **67.5** | ~40         |

Note the honest split: on **Replica**, plain PanSt3R (62.0) beats the LUDVIG-uplifted variant (60.6), and PanSt3R w/o QUBO on Hypersim (51.6) merely ties DM-NeRF and loses to every other lifting baseline. The paper states PanSt3R + LUDVIG sets a new state of the art _except on Replica_.

### ScanNet++ validation set

원논문 Table 3. PanLift / Contrastive Lift는 ScanNet++로 파인튜닝한 Mask2Former 예측을 uplift한 것이다.

| Method              | PQ       | PQ_th    | PQ_st    | Time (min) |
| ------------------- | -------- | -------- | -------- | ---------- |
| PanLift             | 29.5     | 15.6     | 59.4     | ~500       |
| Contrastive Lift    | 28.4     | 14.8     | 56.3     | ~460       |
| PanSt3R (ScanNet++) | 46.7     | 43.2     | 55.8     | ~2.3       |
| + LUDVIG            | **54.8** | **52.4** | **62.4** | ~35        |
| PanSt3R (full)      | 49.1     | 45.8     | 58.7     | ~2.3       |
| + LUDVIG            | 54.7     | 51.7     | 62.4     | ~35        |

ScanNet++ uses 100 classes rather than the 21-class PanLift mapping, so the gap concentrates in `PQ_th`: the baselines score 15.6 / 14.8 on thing classes against PanSt3R's 43.2 / 45.8.

### Ablation: 2D vs 3D features

원논문 Table 4. PanSt3R (224, ScanNet++) + LUDVIG 구성, ScanNet++ validation.

| Features | PQ       | PQ_th    | PQ_st    |
| -------- | -------- | -------- | -------- |
| 3D + 2D  | **50.4** | **45.4** | **61.1** |
| 3D only  | 46.4     | 40.7     | 58.8     |
| 2D only  | 35.7     | 28.4     | 51.9     |

The paper describes this as a clear complementarity: dropping 2D features costs 4% PQ, dropping 3D features costs 14.7%.

### Ablation: QUBO merging and 3DGS regularization

원논문 Table 5. PanSt3R+LUDVIG 기준 scene-PQ.

| Reg | QUBO | Hypersim | Replica  | ScanNet  | ScanNet++ |
| --- | ---- | -------- | -------- | -------- | --------- |
| ✗   | ✗    | 58.1     | 60.8     | 60.2     | 50.8      |
| ✗   | ✓    | **66.7** | 60.7     | 67.3     | 52.0      |
| ✓   | ✗    | 59.3     | **61.2** | 60.6     | **55.2**  |
| ✓   | ✓    | 66.3     | 60.6     | **67.5** | 54.7      |

Regularization "helps in most cases … but not always" — on ScanNet++ the best score comes from regularization _without_ QUBO, and on Replica the differences are within 0.6 PQ.

### Robustness to fewer views

원논문 Table 6·7. ScanNet++ 기준.

| # Keyframes | 10   | 20   | 30   | 50   | 100  |
| ----------- | ---- | ---- | ---- | ---- | ---- |
| PanSt3R     | 49.3 | 55.0 | 56.3 | 58.2 | 58.2 |

원논문 Table 7 — GS/NeRF 구축에 사용 가능한 "seen" 이미지 수를 줄였을 때.

| # Images         | 10   | 25   | 50   | 100  |
| ---------------- | ---- | ---- | ---- | ---- |
| PanoLift         | 3.3  | 20.2 | 30.6 | 38.5 |
| PanSt3R          | 28.4 | 51.8 | 55.8 | 61.8 |
| PanSt3R + LUDVIG | 41.7 | 56.1 | 61.6 | 65.0 |

PanLift collapses to 3.3 PQ with 10 seen images; PanSt3R retains 28.4 (41.7 with LUDVIG). Keyframe count saturates at 50.

### Two-stage point-cloud baseline

원논문 Table 9. ScanNet++V2 point-cloud instance segmentation.

| Method                 | AP50     | AP25     | Pr       | Re       |
| ---------------------- | -------- | -------- | -------- | -------- |
| MUSt3R pcd + SGIFormer | 1.8      | 3.0      | 27.5     | 2.5      |
| PanSt3R                | 19.1     | 32.9     | 45.7     | 22.9     |
| GT pcd + SGIFormer     | **33.2** | **40.5** | **54.0** | **39.8** |

This table is reported honestly against PanSt3R: a dedicated point-cloud segmenter run on _ground-truth_ geometry still wins by a wide margin (33.2 vs 19.1 AP50). The paper's point is the collapse of SGIFormer to 1.8 AP50 when it must consume MUSt3R's predicted, noisy point cloud — the two-stage route is brittle, not that PanSt3R beats a clean-geometry oracle.

### Resolution ablation

원논문 Table 8. ScanNet++로 학습·평가. † 224 모델은 정사각 종횡비 때문에 경계 예측이 누락된다.

| Method              | res | PQ       | PQ_th    | PQ_st    |
| ------------------- | --- | -------- | -------- | -------- |
| PanSt3R† (orig)     | 224 | 39.0     | 36.4     | 48.2     |
| PanSt3R† (rendered) | 224 | 32.5     | 29.2     | 41.5     |
| PanSt3R + LUDVIG    | 224 | 50.4     | 45.4     | 61.1     |
| PanSt3R (orig)      | 512 | **57.3** | 51.7     | **70.4** |
| PanSt3R (rendered)  | 512 | 46.7     | 43.2     | 55.8     |
| PanSt3R + LUDVIG    | 512 | 54.8     | **52.4** | 62.4     |

Predicting on _original_ test images at 512 gives the highest overall PQ (57.3), higher than the LUDVIG pipeline — the main-table numbers are handicapped by being computed on 3DGS-rendered views to match the baselines' protocol.

## 💡 Insights & Impact

### The argument against 2D-first panoptic lifting

The paper's framing is that 3D panoptic segmentation is _inherently_ a multi-view problem, so factoring it as "run a 2D panoptic model per frame, then reconcile" discards spatial relationships that were available all along. The 2D-only ablation row (35.7 PQ vs 50.4) is the direct measurement of that claim inside their own architecture.

### Cost structure changes, not just accuracy

The competing NeRF/3DGS methods are reported at ~120–900 minutes per scene on PanLift and ~460–500 minutes on ScanNet++. PanSt3R's forward pass is ~2.3–4.5 minutes; the LUDVIG path adds 3DGS construction (~35 min). The dominant cost thus moves from _segmentation_ to _whether you need a 3DGS at all_ — and because PanSt3R can predict directly on test images, it can skip both the 3DGS and the camera parameters.

### Global merging matters in multi-view

The standard MaskFormer merging heuristic selects instances locally, per frame. Table 5 shows this is where a large chunk of multi-view consistency is lost (58.1 → 66.7 on Hypersim from QUBO alone). Multi-view instance identity is a global assignment problem, and treating it as one pays off.

### Where it does not win

Two limits are visible in the paper's own numbers: Replica, where LUDVIG uplifting slightly hurts, and the ScanNet++ point-cloud comparison, where a specialized segmenter on clean geometry remains far ahead. PanSt3R's advantage is robustness to noisy predicted geometry and unposed input, not raw segmentation ceiling.

## 🔗 Related Work

- [MUSt3R](../reconstruction/must3r.md) — the 3D backbone PanSt3R builds on; its memory-carrying decoder is what supplies globally aligned features
- [DUSt3R](../foundation/dust3r.md) — the sparse-view reconstruction framework MUSt3R descends from, credited for PanSt3R's insensitivity to view count
- [MASt3R](../foundation/mast3r.md) — sibling in the same NAVER LABS line, matching-focused rather than segmentation-focused
- [PE3R](pe3r.md) — another entry in this collection combining perception/semantics with feed-forward 3D
- [Large Spatial Model](largespatialmodel.md) — related attempt at semantics + geometry in one feed-forward model
- [VGGT](../reconstruction/vggt.md) — the contemporaneous unified-transformer alternative, geometry-only

## 📚 Key Takeaways

1. **A 3D backbone's features are semantically useful.** Concatenating MUSt3R decoder tokens with DINOv2 tokens beats either alone by a wide margin (50.4 vs 46.4 vs 35.7 PQ), and the 3D half contributes more.
2. **Multi-view instance merging should be global.** Replacing MaskFormer's per-frame heuristic with a QUBO assignment is worth up to ~8 PQ on Hypersim.
3. **Two orders of magnitude less compute.** ~2.3–4.5 min vs ~420–900 min for NeRF-based lifting, with better PQ on most benchmarks.
4. **Poses become optional.** Because PanSt3R can predict directly on target-view images, it needs neither camera parameters nor a 3DGS — the main tables use rendered views only to match baseline protocol, and doing so _costs_ it accuracy (57.3 → 46.7 PQ at 512).
5. **Reported losses are real.** Replica favors the non-uplifted variant, and SGIFormer on ground-truth point clouds still outperforms PanSt3R on ScanNet++V2 instance segmentation.

# Event3R: Asynchronous-to-Global 3D Reconstruction from Event Camera via Spatial-Temporal Feature Aggregation (IROS 2026)

![event3r — architecture](https://arxiv.org/html/2607.15727v1/x1.png)

_Overview of the Event3R pipeline (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Jian Huang, Haotian Shen, Xinhao Lou, Chengrui Dong, Wenpu Li, Peidong Liu
- **Institution**: Zhejiang University; Westlake University
- **Venue**: IROS 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.15727)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward, event-only framework that converts asynchronous event streams into spatial–temporal voxels, aggregates them with a temporal attention encoder, and predicts globally consistent 3D pointmaps through a DUSt3R backbone in about 0.2s.

## 🎯 Key Contributions

1. **Event-only feed-forward global reconstruction**: Presents a framework that produces globally consistent 3D reconstruction directly from asynchronous event streams (claimed first event-only feed-forward such framework).
2. **Temporal attention encoder**: A patch-level temporal encoder aggregates information across voxelized time bins to enable time-aware feature integration.
3. **Masked Bin Modeling (MBM)**: A self-supervised pretraining strategy (bin-level masking + reconstruction) that improves temporal aggregation and reduces reliance on labeled data, retained as an auxiliary fine-tuning loss.
4. **Validated on multiple 3D perception tasks**: Depth estimation, camera pose estimation, and 3D reconstruction on synthetic and real-world benchmarks.

## 🔧 Technical Details

### Event-to-Voxel Representation

- Events within a short window Δt are discretized into a voxel grid H × W × T (T temporal bins) via trilinear splatting by normalized timestamp.
- Event chunk length fixed to 50 ms, divided into T bins; T is odd for a well-defined central bin that serves as the temporal reference frame for the pointmap. T = 5 selected after balancing performance and cost.

### Temporal Encoder (TE)

- Each bin embedded with a convolutional layer into 32-dimensional features on non-overlapping 8 × 8 patches; temporal attention runs over 2 layers with 4 heads and MLP ratio 4.0.
- Self-attention over T bins aggregates neighboring-bin information into the center-bin feature, which is passed to the spatial backbone.

### Backbone and MBM

- Spatial encoder/decoder are ViT-Base, initialized from DUSt3R weights; temporal encoder is also ViT-Base.
- MBM randomly masks one or more bins and trains a lightweight decoder to reconstruct masked features (L1 loss), augmented with contrastive (temperature τ = 0.1) and consistency losses (λ1 = λ2 = 1.0).

### Training

- Two-stage: (1) MBM pretraining for 300 epochs (Adam, lr 1×10⁻⁴, weight decay 0.05, batch 4) on 8 NVIDIA RTX A100 GPUs; (2) joint fine-tuning for 300 epochs (Adam, initial lr 5×10⁻⁵, cosine decay, gradient clipping norm 1.0). Full training ≈ 7 days on 8 GPUs.
- Pretraining data: MatrixCity and TUM-VIE (events simulated with ESIM for MatrixCity). Downstream training: TartanAir and MVSEC.
- Multi-view (N > 2) reconstruction follows DUSt3R's global-alignment pipeline; two-view outputs are already in a consistent global frame.

## 📊 Results

### Depth Estimation on Event Benchmarks

원논문 Table I. TartanAir 및 MVSEC outdoor.

| Method        | TartanAir AbsRel ↓ | TartanAir δ<1.25 ↑ | MVSEC AbsRel ↓ | MVSEC δ<1.25 ↑ |
| ------------- | ------------------ | ------------------ | -------------- | -------------- |
| **Ours**      | **0.0514**         | **0.9700**         | **0.1805**     | **0.7838**     |
| EvGGS         | 0.4553             | 0.5420             | 0.1972         | 0.7138         |
| E2Depth       | 0.7923             | 0.2484             | 0.3763         | 0.5073         |
| DepthAnyEvent | 0.2751             | 0.6093             | 0.4100         | 0.3783         |
| DERD-Net      | 0.5651             | 0.2488             | 0.4367         | 0.2288         |
| EReFormer     | 0.2931             | 0.5323             | 0.4986         | 0.3799         |

### Pose Estimation on TartanAir (ATE, cm)

원논문 Table II. S1–S5는 서로 다른 시퀀스(Hospital/Office). "-"는 실패.

| Method         | S1        | S2        | S3        | S4        | S5        |
| -------------- | --------- | --------- | --------- | --------- | --------- |
| **Ours**       | **0.402** | **0.152** | **0.116** | **0.545** | **0.293** |
| DEVO           | 1.25      | 0.457     | 0.891     | 2.02      | 0.861     |
| E2Vid + Colmap | -         | 0.550     | 0.828     | 1.87      | 1.18      |
| IncEventGS     | 1.16      | 0.307     | 0.261     | 1.56      | 1.03      |

### 3D Reconstruction

원논문 Table III.

| Method        | MVSEC Acc ↓ | MVSEC Comp ↓ | MVSEC NC ↑ | TartanAir Acc ↓ | TartanAir Comp ↓ | TartanAir NC ↑ |
| ------------- | ----------- | ------------ | ---------- | --------------- | ---------------- | -------------- |
| **Ours**      | **0.4915**  | **0.6132**   | **0.7569** | **0.1097**      | **0.1382**       | **0.8886**     |
| DepthAnyEvent | 0.5342      | 0.7539       | 0.6195     | 0.5110          | 0.5764           | 0.6576         |
| E2Depth       | 0.7987      | 0.6532       | 0.6332     | 0.6891          | 0.4952           | 0.4950         |
| IncEventGS    | 0.6879      | 0.6231       | 0.5332     | 0.3350          | 0.3609           | 0.6236         |

### Ablation

원논문 Table IV. TE = Temporal Encoder, MBM = Masked Bin Modeling.

| Model               | AbsRel ↓   | δ<1.25 ↑  | ATE ↓      |
| ------------------- | ---------- | --------- | ---------- |
| Full Event3R        | **0.0514** | **0.970** | **0.1524** |
| w/o TE              | 0.1187     | 0.892     | 0.4381     |
| w/o MBM pretrain    | 0.0825     | 0.925     | 0.3095     |
| MBM w/o contrastive | 0.0621     | 0.961     | 0.1792     |
| MBM w/o consistency | 0.0598     | 0.965     | 0.1675     |

## 💡 Insights & Impact

- **Voxelization bridges async events and feed-forward geometry**: Reinterpreting event streams as structured spatial–temporal voxels lets a DUSt3R-style backbone process temporally dense yet spatially sparse observations.
- **Temporal aggregation is essential**: Removing the temporal encoder nearly doubles depth error (AbsRel 0.0514 → 0.1187) and triples pose error (ATE 0.1524 → 0.4381 cm).
- **MBM pretraining matters most among the auxiliary designs**: Disabling MBM pretraining raises AbsRel to 0.0825 and ATE to 0.3095 cm, more than ablating the contrastive or consistency terms alone.
- **Robustness under HDR / low light**: Event3R remains robust where DUSt3R degrades due to poor RGB observations, evaluated zero-shot on PEOD.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: Backbone weights and global-alignment reconstruction pipeline.
- **[VGGT](vggt.md)** and **[CUT3R](../dynamic/cut3r.md)**: RGB feed-forward reconstruction context; CUT3R metrics/protocol reused for depth.
- **[MASt3R](../foundation/mast3r.md)**: Cited transformer-based dense correspondence lineage.
- **[EAG3R](../dynamic/eag3r.md)**: Concurrent event-augmented feed-forward pipeline, contrasted as RGB-centric rather than event-only.

## 📚 Key Takeaways

1. Event3R brings feed-forward global 3D reconstruction to asynchronous event cameras by voxelizing events and aggregating them with a temporal attention encoder before a DUSt3R backbone.
2. Masked Bin Modeling provides self-supervised temporal pretraining and an auxiliary objective, reducing dependence on scarce labeled event–depth–pose data.
3. Across TartanAir and MVSEC, Event3R achieves the lowest depth error, lowest ATE, and best reconstruction metrics among compared event-based methods, with ablations confirming that both the temporal encoder and MBM are necessary.

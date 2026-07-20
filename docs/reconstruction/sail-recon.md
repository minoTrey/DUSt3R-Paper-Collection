# SAIL-Recon: Large SfM by Augmenting Scene Regression with Localization (3DV 2026)

## 📋 Overview

- **Authors**: Junyuan Deng, Heng Li, Tao Xie, Weiqiang Ren, Qian Zhang, Ping Tan, Xiaoyang Guo
- **Institution**: The Hong Kong University of Science and Technology, Horizon Robotics, Zhejiang University
- **Venue**: 3DV 2026
- **Award**: Oral
- **Links**: [Paper](https://arxiv.org/abs/2508.17972) | [Project Page](https://hkust-sail.github.io/sail-recon/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A feed-forward SfM transformer that scales VGGT-style scene regression to thousands of images by first regressing a compact _neural scene representation_ from a sparse set of anchor images, then localizing every remaining image against it via masked cross-attention.

## 🎯 Key Contributions

1. **Anchor-then-localize decomposition**: Rather than pushing all N images through global attention (whose memory grows quickly), SAIL-Recon computes a neural scene representation from a subset of anchor images and localizes all inputs conditioned on it.
2. **Neural scene representation from _intermediate_ layers**: The representation is not the final layer's tokens but a concatenation of downsampled tokens from every attention layer, `R = [{Θ(t_j^I')}_{j=1}^L]`, which the paper argues captures the gradual evolution from 2D appearance features toward 3D coordinate descriptors.
3. **Attention masking for localization**: Query-image tokens may attend only within their own frame and to the scene representation — never to other query frames — which makes localization independent per query and therefore parallelizable and memory-bounded.
4. **Random token-drop training**: During training a random ratio `r ∈ [0.2, 1.0]` of anchor tokens is sampled, acting as dropout-style regularization and letting inference trade accuracy against cost by choosing `r`.
5. **Scale to video-length inputs**: Evaluated on Tanks & Temples image sets (150–1,100 images/scene) and video subsets (4,000–20,000 frames), where the paper notes VGGT and DUSt3R-family baselines could not be run within a reasonable resource budget.

## 🔧 Technical Details

### Backbone

Anchor images are patchified with DINO features; following VGGT, each image's tokens are augmented with one camera token `t_g^{I_i}` and four register tokens. Tokens pass through **L = 24 layers** alternating frame-wise and global self-attention:

```text
{t_j^{I_i}'} = attn_j^frame({t_j^{I_i}})
t_{j+1}^I    = attn_j^global(t_j^I)
```

Last-layer tokens feed DPT heads producing depth maps `D_i`, scene coordinate maps `S_i`, and their confidence maps `C_i^D`, `C_i^S`. Camera tokens feed a pose head producing `{T_i, K_i}`.

### Why not use the last layer as the scene representation

The obvious choice is `R = t_L^I`. The paper reports this empirically underperforms: the discrepancy between 2D and 3D feature tokens makes it hard for the network to correlate a query image's 2D tokens against a fundamentally 3D representation, even with a large parameter count. Taking tokens from _all_ layers gives the query something to match at every level of abstraction.

### Localization block

For query image `I^q`, an attention mask restricts global attention to

```text
t_{j+1}^q = attn_j^global({t_j^q, R_j})
```

Two output paths exist. The DPT head gives a scene coordinate map that can be turned into a pose by PnP, but DPT up-sampling to a high-resolution SCM is slow; for pose estimation the paper instead uses the pose head directly on camera tokens, `{T^q, K^q} = PoseHead(t_g^q, {t_g^{I_i}})`, with the same attention mask applied.

### Training

End-to-end multitask loss following VGGT:

```text
L = L_camera + L_depth + L_scm
```

with `L_scm = Σ_i ‖C_i^S ⊙ (Ŝ_i − S_i)‖ + ‖(∇Ŝ_i − ∇S_i)‖ − α log C_i^S`. Coordinate normalization picks a random anchor image `I_r` as reference frame and normalizes by the average Euclidean distance from its camera center to all anchor 3D points.

### Post refinement

Bundle adjustment is available as an optional post-refinement step and is enabled for the novel-view-synthesis benchmarks (10K iterations), because even slight pose noise prevents Nerfacto from converging.

## 📊 Results

All runtimes are measured under similar GPU throughput conditions with an Nvidia V100 as reference hardware.

### Pose estimation on Tanks & Temples

원논문 Table 1. OPT = optimization-based, FFD = feed-forward. † 순차 입력 필요, * GeoCalib 내부 파라미터 제공, △ 일부 시퀀스 실패. Reg.는 등록된 이미지 비율.

| Method             | Align. | RRA@5 ↑ | RTA@5 ↑  | ATE ↓     | Reg. ↑ | Time [s] ↓ |
| ------------------ | ------ | ------- | -------- | --------- | ------ | ---------- |
| COLMAP             | OPT    | GT      | GT       | GT        | GT     | -          |
| GLOMAP             | OPT    | 75.8    | 76.7     | 0.010     | 100.0  | 1977       |
| ACE0               | OPT    | 56.9    | 57.9     | 0.015     | 100.0  | 5499       |
| DF-SfM             | OPT    | 69.6    | 69.3     | 0.014     | 76.2   | -          |
| FlowMap            | OPT    | 31.7    | 35.7     | 0.017     | 66.7   | -          |
| VGGSfM             | OPT    | -       | -        | -         | 0.0    | 2134       |
| MASt3R-SfM         | OPT    | 49.2    | 54.0     | 0.011     | 100.0  | 2723       |
| DROID-SLAM         | OPT    | 31.3    | 40.3     | 0.021     | 100.0  | 240        |
| **SAIL-Recon-OPT** | OPT    | 71.5    | **77.7** | **0.008** | 100.0  | 233        |
| CUT3R†             | FFD    | 18.8    | 25.8     | 0.017     | 100.0  | **42**     |
| Spann3R†           | FFD    | 22.1    | 30.7     | 0.016     | 100.0  | 116        |
| SLAM3R†            | FFD    | 20.3    | 24.7     | 0.015     | 100.0  | 70         |
| Light3R-SfM        | FFD    | 52.0    | 52.8     | 0.011     | 100.0  | 63         |
| VGGT-SLAM\*△       | FFD    | 57.3    | 67.9     | 0.008     | 100.0  | 238        |
| **SAIL-Recon**     | FFD    | 70.4    | 74.7     | **0.008** | 100.0  | 81         |

GLOMAP still holds the best RRA@5 (75.8 vs 71.5/70.4). SAIL-Recon's case is the combination: it matches the best ATE (0.008) at 81s feed-forward versus GLOMAP's 1977s and ACE0's 5499s.

### ATE RMSE on TUM RGB-D (m ↓)

원논문 Table 2. VGGT-SLAM를 따라 uncalibrated 설정에서 평가하며, \* 표시는 GeoCalib이 intrinsic을 제공한 경우다.

| Method                   | 360       | desk      | desk2     | floor     | plant     | room      | rpy       | teddy     | xyz       | Avg.      |
| ------------------------ | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| DROID-SLAM\*             | 0.202     | 0.032     | 0.091     | 0.064     | 0.045     | 0.918     | 0.056     | 0.045     | 0.012     | 0.158     |
| MASt3R-SLAM\*            | **0.070** | 0.035     | 0.055     | **0.056** | 0.035     | **0.118** | 0.041     | 0.114     | 0.020     | 0.060     |
| VGGT-SLAM (Sim(3))       | 0.123     | 0.040     | 0.055     | 0.254     | **0.022** | 0.088     | 0.041     | **0.032** | 0.016     | 0.074     |
| VGGT-SLAM (SL(4))        | 0.071     | 0.025     | **0.040** | 0.141     | 0.023     | 0.102     | 0.030     | 0.034     | 0.014     | 0.053     |
| **SAIL-Recon (Offline)** | **0.070** | **0.024** | 0.042     | 0.107     | 0.031     | 0.113     | **0.020** | 0.037     | **0.012** | **0.051** |

Honest per-sequence picture: SAIL-Recon wins the average (0.051) but loses `floor` badly to MASt3R-SLAM (0.107 vs 0.056), loses `room` (0.113 vs 0.088 for VGGT-SLAM Sim(3)), loses `plant`, `desk2`, and `teddy`. The average lead over VGGT-SLAM SL(4) is 0.002 m.

### Localization on 7-Scenes

원논문 Table 3. (5cm, 5°) 이내 포즈 오차 비율. ACE는 학습 시 GT 카메라 포즈를 사용한다.

| Scene        | KinectFusion | ACE+COLMAP | ACE0   | **Ours (FFD)** |
| ------------ | ------------ | ---------- | ------ | -------------- |
| Chess        | 96.0%        | **100.0%** | 100.0% | 98.8%          |
| Fire         | 98.4%        | 99.5%      | 98.8%  | **100.0%**     |
| Heads        | **100.0%**   | 100.0%     | 100.0% | 100.0%         |
| Office       | 36.9%        | **100.0%** | 99.1%  | 87.4%          |
| Pumpkin      | 47.3%        | **100.0%** | 99.9%  | 92.8%          |
| Redkitchen   | 47.8%        | **98.9%**  | 98.1%  | 89.9%          |
| Stairs       | 74.1%        | 85.0%      | 61.0%  | **87.9%**      |
| **Average**  | 74.1%        | **97.6%**  | 93.8%  | 93.8%          |
| Average Time | 14min        | 14min      | 2h     | **8min**       |

SAIL-Recon ties ACE0 exactly on average (93.8%) and loses to ACE+COLMAP by 3.8 points — but ACE uses ground-truth poses during training. Against the pose-free ACE0, the gain is runtime: 8 min vs 2 h.

### Pose accuracy via novel view synthesis — Tanks & Temples (PSNR dB ↑)

원논문 Table 4. Nerfacto로 학습 후 테스트 뷰 렌더링 PSNR. † 순차 입력 필요. CMP (D)는 기본 설정 COLMAP 참조값.

| Split             | Frames | CMP (D)  | Reality Capture | DROID-SLAM† | ACE0 | **Ours** |
| ----------------- | ------ | -------- | --------------- | ----------- | ---- | -------- |
| Training avg      | 364    | **19.9** | 18.2            | 16.9        | 18.1 | 19.5     |
| Training time     | -      | 1h       | 3min            | 5min        | 1.1h | 3.5min   |
| Intermediate avg  | 254    | 18.8     | 18.3            | 15.6        | 18.5 | **19.5** |
| Intermediate time | -      | 32min    | 2min            | 3min        | 1.3h | 3min     |
| Advanced avg      | 348    | **17.3** | 15.0            | 12.9        | 14.8 | 16.9     |
| Advanced time     | -      | 1h       | 2min            | 4min        | 1h   | 3.5min   |

Note the paper's summary claim ("highest PSNR among all baselines") holds against the _learned_ baselines; COLMAP as reference still edges it on Training (19.9 vs 19.5) and Advanced (17.3 vs 16.9). SAIL-Recon recovers all camera poses in 3–4 minutes.

### Pose accuracy via novel view synthesis — Mip-NeRF 360 (PSNR dB ↑)

원논문 Table 5. 씬당 50개 anchor 이미지, post-refinement 10K iteration.

| Scene    | Pseudo GT COLMAP | DROID-SLAM† | BARF | NoPe-NeRF | ACE0 | **Ours**  |
| -------- | ---------------- | ----------- | ---- | --------- | ---- | --------- |
| Bicycle  | **21.5**         | 10.9        | 11.9 | 12.2      | 18.7 | 20.50     |
| Bonsai   | 27.6             | 10.9        | 12.5 | 14.8      | 25.8 | **26.76** |
| Counter  | 25.5             | 12.9        | 11.9 | 11.6      | 24.5 | **25.51** |
| Garden   | **26.3**         | 16.7        | 13.3 | 13.8      | 25.0 | 24.92     |
| Kitchen  | 27.4             | 13.9        | 13.3 | 14.4      | 26.1 | **27.43** |
| Room     | **28.0**         | 11.3        | 11.9 | 14.3      | 19.8 | 27.46     |
| Stump    | 16.8             | 13.9        | 15.0 | 13.9      | 20.5 | **20.83** |
| Average  | 24.7             | 12.9        | 12.8 | 13.5      | 22.9 | **24.77** |
| Avg Time | 1h               | 2min        | 4h   | ≥24h      | 8h   | **5min**  |

Here SAIL-Recon's average (24.77) edges the COLMAP pseudo-GT poses (24.7) at 5 min vs 1 h.

### Ablation: number of anchor views (CO3Dv2 ↑)

원논문 Table 6. 10장 입력 중 N장을 anchor로 무작위 선택.

| Method            | Global Align. | RRA@15   | RTA@15   | mAA@30   |
| ----------------- | ------------- | -------- | -------- | -------- |
| COLMAP            | OPT           | 31.6     | 27.3     | 25.3     |
| GLOMAP            | OPT           | 45.9     | 40.3     | 37.3     |
| PixSfM            | OPT           | 33.7     | 32.9     | 30.1     |
| VGGSfM            | OPT           | 92.1     | 88.3     | 74.0     |
| DUSt3R-GA         | OPT           | 96.2     | 86.8     | 76.7     |
| MASt3R-SfM        | OPT           | 96.0     | 93.1     | 88.0     |
| PoseDiff          | FFD           | 80.5     | 79.8     | 66.5     |
| RelPose++         | FFD           | 82.3     | 77.2     | 65.1     |
| Spann3R           | FFD           | 89.5     | 83.2     | 70.3     |
| MASt3R\*          | FFD           | 94.5     | 80.9     | 68.7     |
| Light3R-SfM       | FFD           | 94.7     | 85.8     | 72.8     |
| **VGGT**          | FFD           | **98.4** | **94.8** | **88.2** |
| SAIL-Recon N = 10 | FFD           | 98.3     | 94.0     | 88.1     |
| SAIL-Recon N = 8  | FFD           | 98.2     | 93.6     | 87.3     |
| SAIL-Recon N = 5  | FFD           | 97.7     | 92.2     | 85.0     |
| SAIL-Recon N = 2  | FFD           | 96.4     | 89.7     | 78.5     |

**VGGT wins this table on all three metrics.** SAIL-Recon at N = 10 is 0.1 mAA@30 behind and degrades gracefully as anchors are removed — the paper's claim is robustness to sparse anchors on small inputs, with scaling being the actual contribution.

### Ablation: training strategy (CO3Dv2 ↑)

원논문 Table 7.

| Method       | mAA@30   | mAA@5    | RRA@15   | RTA@15   |
| ------------ | -------- | -------- | -------- | -------- |
| SAIL-Recon   | **87.3** | **57.6** | **98.3** | **93.6** |
| Fixed token  | 86.5     | 53.6     | 98.2     | 93.6     |
| Avg. Pooling | 86.5     | 53.5     | 98.2     | 93.5     |

Random token selection beats both a fixed 300-token budget and 4× average pooling (~340 tokens/image). The paper attributes this to a dropout-like regularization effect, plus the flexibility to trade accuracy against efficiency at test time.

### Tokens per image

Figure 3 sweeps tokens per image over {50, 150, 300, 500, 800, full} with N = 5 anchors, plotting mAA@30 against average time in ms. Accuracy rises with token count while runtime grows steadily; the paper selects **300 tokens per image** as the operating point. The individual sweep values exist only in the plot and are not printed in the paper, so they are not reproduced here.

## 💡 Insights & Impact

### Reframing scale as a localization problem

The DUSt3R lineage handles many views by either (a) iteratively updated global memory tokens or (b) segmenting the video and aligning sub-reconstructions with Sim(3)/SL(4). The paper argues both accumulate pose drift and lean heavily on downstream global alignment. SAIL-Recon's alternative is the classical SfM split — build a map from a subset, then _localize_ everything else into it — but with the map being a learned token set rather than a point cloud, and localization being attention rather than PnP-RANSAC.

### The representation choice is the interesting part

The ablation-by-argument in Section 3.3 is that a final-layer representation is too far into the 3D domain for a fresh 2D query to correlate against. Stacking downsampled tokens from all 24 layers gives the query a ladder from appearance to geometry. This is a reusable idea for any "condition a feed-forward model on a prebuilt scene" design.

### Memory is bounded by anchors, not by inputs

Because query frames cannot attend to each other, the attention cost per query is O(|R|) and independent of how many other images exist. This is what makes 4,000–20,000-frame video sequences tractable where VGGT is not.

### Honest positioning against VGGT

On small-N CO3Dv2, VGGT is still slightly better (Table 6). SAIL-Recon's contribution is not beating VGGT on 10 images — it is retaining ~VGGT-level accuracy while running on inputs VGGT cannot fit at all, and beating optimization-based SfM by 1–2 orders of magnitude in wall time.

## 🔗 Related Work

- [VGGT](vggt.md) — the scene-regression backbone SAIL-Recon augments; still the accuracy reference on small inputs
- [VGGT-SLAM](vggt-slam.md) — the SL(4)/Sim(3) submap-fusion approach SAIL-Recon compares against on TUM
- [DUSt3R](../foundation/dust3r.md) — origin of the scene-regression paradigm, via global alignment
- [MASt3R-SfM](../foundation/mast3r-sfm.md) — the optimization-based SfM baseline in Tables 1 and 6
- [Light3R-SfM](light3r-sfm.md) — the closest feed-forward SfM competitor in Table 1
- [Spann3R](spann3r.md) and [CUT3R](../dynamic/cut3r.md) — the global-memory-token approach whose drift the paper critiques
- [SLAM3R](slam3r.md) — sequential feed-forward baseline on Tanks & Temples

## 📚 Key Takeaways

1. **Anchor + localize beats memory-token streaming for scale.** Tokens from 100 anchor frames define a fixed-size map; every other frame is localized independently, so cost does not blow up with sequence length.
2. **Use intermediate layers as the conditioning representation.** Final-layer tokens are too 3D-specialized for a raw 2D query to match against; the layer stack bridges that gap.
3. **The speed story is against optimization-based SfM, not against VGGT.** 233s vs GLOMAP's 1977s and ACE0's 5499s on Tanks & Temples; 8 min vs ACE0's 2 h on 7-Scenes; 5 min vs COLMAP's 1 h on Mip-NeRF 360.
4. **Random token dropping is free regularization** and doubles as an inference-time accuracy/cost dial.
5. **VGGT still leads on small-N CO3Dv2** (88.2 vs 88.1 mAA@30), and COLMAP pseudo-GT poses still edge SAIL-Recon on some Tanks & Temples splits. The paper reports both.

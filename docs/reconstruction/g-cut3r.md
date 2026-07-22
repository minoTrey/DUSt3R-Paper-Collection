# G-CUT3R: Guided 3D Reconstruction with Camera and Depth Prior Integration (ICLR 2026)

![g-cut3r — architecture](https://arxiv.org/html/2508.11379/x1.png)

_Overview of the G-CUT3R architecture (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Ramil Khafizov, Artem Komarichev, Ruslan Rakhimov, Peter Wonka, Evgeny Burnaev
- **Institution**: Applied AI Institute, T-Tech, KAUST
- **Venue**: ICLR 2026
- **Note**: 원논문 PDF 페이지 헤더에 "Published as a conference paper at ICLR 2026"이
  인쇄돼 있다. DBLP·프로젝트 페이지에는 아직 근거가 없고 OpenReview가 게이트돼
  확인할 수 없었으나, 저자가 조판한 헤더는 1차 출처로 본다.
- **Links**: [Paper](https://arxiv.org/abs/2508.11379)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: A lightweight, modality-agnostic extension of CUT3R that injects camera intrinsics, camera poses, and depth maps through per-modality encoders fused into the decoder with zero-initialized convolutions, so any subset of priors can be supplied at inference.

## 🎯 Key Contributions

1. **Guided feed-forward reconstruction**: A real-time feed-forward method that consumes optional camera intrinsics `K`, poses `R, t`, and depth `D` alongside RGB images.
2. **Modality-agnostic fusion**: One model handles arbitrary combinations of priors, rather than training a separate model per modality.
3. **Zero-convolution integration**: Fusion is done through zero-initialized 1×1 convolutions, so at the start of fine-tuning the pretrained CUT3R decoder behaves unchanged.
4. **No global alignment**: The recurrent state removes the need for the expensive global optimization that Pow3R relies on.

## 🔧 Technical Details

### Modality Encoding

- Camera intrinsics and poses are encoded as **ray images**: each pixel becomes a normalized 3D direction `X^K ∈ R^{3×H×W}`, with `X^P` carrying the translation component `t`. When only intrinsics are known, rays are expressed in the local camera frame.
- Depth maps are normalized to `[0, 1]` and concatenated channel-wise with a binary validity mask `M`, giving `X^D ∈ R^{2×H×W}` — this is what allows sparse or incomplete sensor depth to be used.
- Each modality passes through a dedicated convolutional layer, then a dedicated 4-layer ViT encoder (12 heads, embedding dimension 768). Encoders are **not shared** across modalities.

### Fusion

The modality features are summed into a single guidance feature `G = F^D + F^K + F^P`, then merged with RGB image features via

```text
F_fused = F^I + ZeroConv(G)
```

Fusion happens **five times** inside the CUT3R decoder: once before the first decoder layer, and once after each of the first four decoder layers.

### Training

- Objective follows CUT3R: a confidence-weighted pointmap loss `L_point` plus a pose loss `L_pose` that separately penalizes quaternion and translation error.
- Backbone: ViT-Large image encoder, ViT-Base decoders, 16×16 patches, initialized from CUT3R weights for 512-resolution images.
- Only a subset of the original model's parameters is trained, on a reduced portion of CUT3R's training corpus: 12 datasets (ScanNet, ScanNet++, ARKitScenes, Waymo, MegaDepth, DL3DV, Co3Dv2, WildRGBD, MapFree, TartanAir, BlendedMVS, HyperSim), sampled at 10,000 examples each.
- Adam-W, learning rate 1e-5 with linear warmup and cosine decay, four NVIDIA A100 GPUs for ten days.
- Training sequences are four images long; the model sees random subsets of available modalities each step.

## 📊 Results

### 3D Reconstruction — 7-Scenes

원논문 Table 1. Mean values only (the paper also reports medians). FPS measured on an NVIDIA A40 at 348×512. `+` = prior supplied, `-` = not supplied. Scenes contain only 3–5 images (low-overlap protocol).

| Method    | Resolution | FPS  | K   | R, t | D   | Acc Mean ↓ | Comp Mean ↓ | NC Mean ↑ |
| --------- | ---------- | ---- | --- | ---- | --- | ---------- | ----------- | --------- |
| Spann3R   | 224        | 16.3 | -   | -    | -   | 0.298      | 0.205       | 0.650     |
| CUT3R     | 224        | 33   | -   | -    | -   | 0.298      | 0.254       | 0.649     |
| CUT3R     | 512        | 20   | -   | -    | -   | 0.126      | 0.154       | 0.727     |
| DUSt3R-GA | 512        | 0.9  | -   | -    | -   | 0.146      | 0.181       | 0.736     |
| MASt3R-GA | 512        | 0.37 | -   | -    | -   | 0.185      | 0.180       | 0.701     |
| Pow3R     | 512        | 0.3  | -   | -    | -   | 0.198      | 0.198       | 0.677     |
| Pow3R     | 512        | 0.3  | +   | +    | +   | 0.112      | 0.149       | 0.739     |
| G-CUT3R   | 512        | 18   | -   | -    | -   | 0.098      | 0.106       | 0.726     |
| G-CUT3R   | 512        | 14.7 | +   | +    | +   | 0.048      | 0.056       | 0.746     |

### 3D Reconstruction — NRGBD

원논문 Table 1, same rows, Mean values.

| Method    | Resolution | FPS  | K   | R, t | D   | Acc Mean ↓ | Comp Mean ↓ | NC Mean ↑ |
| --------- | ---------- | ---- | --- | ---- | --- | ---------- | ----------- | --------- |
| Spann3R   | 224        | 16.3 | -   | -    | -   | 0.416      | 0.417       | 0.684     |
| CUT3R     | 224        | 33   | -   | -    | -   | 0.422      | 0.252       | 0.713     |
| CUT3R     | 512        | 20   | -   | -    | -   | 0.099      | 0.076       | 0.837     |
| DUSt3R-GA | 512        | 0.9  | -   | -    | -   | 0.144      | 0.154       | 0.870     |
| MASt3R-GA | 512        | 0.37 | -   | -    | -   | 0.085      | 0.063       | 0.794     |
| Pow3R     | 512        | 0.3  | -   | -    | -   | 0.335      | 0.356       | 0.729     |
| Pow3R     | 512        | 0.3  | +   | +    | +   | 0.334      | 0.313       | 0.737     |
| G-CUT3R   | 512        | 18   | -   | -    | -   | 0.089      | 0.073       | 0.827     |
| G-CUT3R   | 512        | 14.7 | +   | +    | +   | 0.101      | 0.061       | 0.828     |

**Honest reading**: on NRGBD the gains are not uniform. Full guidance improves Completeness (0.073 → 0.061) but _worsens_ Accuracy relative to the unguided variant (0.089 → 0.101), and both trail MASt3R-GA's 0.085 Acc Mean. Normal Consistency stays below DUSt3R-GA's 0.870 in every G-CUT3R row. The 7-Scenes gains are the strong case; NRGBD is the mixed one.

### Video Depth Estimation

원논문 Table 2. Sequences of length 10. CUT3R and G-CUT3R are evaluated **without** scale alignment (they estimate metric depth); all other methods get scale alignment.

| Method  | Resolution | FPS  | K   | R, t | Bonn Abs. rel ↓ | Bonn δ <1.25 ↑ | ScanNet Abs. rel ↓ | ScanNet δ <1.25 ↑ |
| ------- | ---------- | ---- | --- | ---- | --------------- | -------------- | ------------------ | ----------------- |
| Spann3R | 224        | 16.3 | -   | -    | 0.144           | 81.3           | 0.051              | 96.7              |
| CUT3R   | 512        | 20   | -   | -    | 0.069           | 97.1           | 0.029              | 99.3              |
| Pow3R   | 512        | 0.3  | -   | -    | 0.148           | 67.1           | 0.028              | 99.0              |
| Pow3R   | 512        | 0.3  | +   | +    | 0.128           | 77.0           | 0.035              | 99.2              |
| G-CUT3R | 512        | 18   | -   | -    | 0.062           | 97.5           | 0.031              | 99.2              |
| G-CUT3R | 512        | 13.6 | +   | +    | 0.063           | 97.4           | 0.030              | 99.2              |

The paper's own summary is that on ScanNet "G-CUT3R performs similarly to alternative approaches" — indeed its 0.031 / 0.030 Abs. rel is behind CUT3R's 0.029 and Pow3R's 0.028. The Bonn column is where guidance helps.

### Camera Pose Estimation

원논문 Table 5 (supplementary), Sintel and ScanNet, 512 resolution.

| Method  | K   | D   | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | ScanNet ATE ↓ | ScanNet RPE trans ↓ |
| ------- | --- | --- | ------------ | ------------------ | ---------------- | ------------- | ------------------- |
| Spann3R | -   | -   | 0.329        | 0.110              | 4.471            | 0.096         | 0.023               |
| CUT3R   | -   | -   | 0.086        | 0.156              | 0.433            | 0.008         | 0.012               |
| Pow3R   | -   | -   | 0.578        | 0.651              | 1.877            | 0.019         | 0.022               |
| Pow3R   | +   | +   | 0.426        | 0.610              | 0.974            | 0.019         | 0.022               |
| G-CUT3R | -   | -   | 0.063        | 0.162              | 0.526            | 0.008         | 0.011               |
| G-CUT3R | +   | +   | 0.054        | 0.159              | 0.498            | 0.008         | 0.011               |

The paper notes that on ScanNet the base model is already strong and the improvement from depth/intrinsics priors is negligible — visible above, where the ScanNet columns do not move at all.

For **pose** guidance specifically, the paper reports in prose (Sec. 4.5) an ATE reduction of 61% on Sintel (0.077 → 0.030), 23% on TUM RGB-D (0.013 → 0.010), and 29% on ScanNet (0.007 → 0.005) versus the no-guidance variant, plus a further 8–12% RRE decrease when depth or intrinsics are combined with pose guidance.

### Ablation: Zero Convolution vs. a Pow3R-style Adaptation

원논문 Table 3. `Pow3R†` denotes the Pow3R prior-injection scheme re-implemented inside CUT3R. Metric is L2 distance ↓ between ground-truth and reconstructed pointmaps at identical pixel coordinates, per view index (1–4 of four consecutive views).

| Method              | K   | R, t | D   | Waymo L2/1 ↓ | Waymo L2/4 ↓ | ScanNet++ L2/1 ↓ | ScanNet++ L2/4 ↓ |
| ------------------- | --- | ---- | --- | ------------ | ------------ | ---------------- | ---------------- |
| Pow3R†              | -   | -    | -   | 1.194        | 1.458        | 0.050            | 0.087            |
| Pow3R†              | +   | +    | +   | 1.237        | 1.543        | 0.050            | 0.084            |
| Ours (w/o ZeroConv) | -   | -    | -   | 1.796        | 1.766        | 0.055            | 0.100            |
| Ours (w/o ZeroConv) | +   | +    | +   | 1.730        | 1.959        | 0.053            | 0.078            |
| Ours (w/ ZeroConv)  | -   | -    | -   | 1.235        | 1.327        | 0.049            | 0.086            |
| Ours (w/ ZeroConv)  | +   | +    | +   | 1.042        | 1.155        | 0.042            | 0.064            |

Without zero convolutions the method is clearly worse than the Pow3R adaptation; the zero-init fusion is what makes the design work.

## 💡 Insights & Impact

**The problem being solved.** Feed-forward reconstruction models consume RGB only, discarding calibration, poses, and RGB-D/LiDAR depth that are routinely available in deployment. Pow3R addressed this on top of DUSt3R, but required training the whole model from scratch, processed only image pairs, and needed global alignment — the paper measures it at 0.3 FPS.

**Why zero convolutions matter.** Initializing the fusion projection at zero means the guidance branch contributes nothing at step 0, so the pretrained CUT3R decoder is not destabilized. Guidance is learned in gradually. The ablation shows this is not cosmetic: removing it costs more than the prior information gains.

**Which prior does what.** The paper's own attribution: camera poses contribute most to Accuracy and Completeness, while depth fusion mainly improves Normal Consistency. Combining modalities beats any single one.

**A caveat on the baseline comparison.** The authors explicitly warn that their unguided variant is not directly comparable to the released CUT3R checkpoint, because G-CUT3R is fine-tuned on a smaller data subset. They therefore train an unguided G-CUT3R on that same subset as the fair reference — a discipline worth noting when reading the tables.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md) — the recurrent-state backbone that G-CUT3R extends
- [Pow3R](pow3r.md) — the direct competitor, prior injection on top of DUSt3R
- [DUSt3R](../foundation/dust3r.md) — pairwise pointmap regression, the origin of the paradigm
- [MASt3R](../foundation/mast3r.md) — adds a matching head to DUSt3R
- [Spann3R](spann3r.md) — sequential reconstruction with spatial memory, a baseline here
- [VGGT](vggt.md) — the multi-view alternative the paper cites as more memory-hungry

## 📚 Key Takeaways

1. **Priors are free accuracy when you already have them.** Intrinsics, poses, and depth exist in most real deployments; a model that ignores them leaves quality on the table.
2. **Zero-init fusion is the enabling trick.** It lets you graft new input modalities onto a pretrained backbone without destroying it, and the ablation shows the alternative is substantially worse.
3. **One model, any subset of modalities.** Random modality dropout during training buys inference-time flexibility at the cost of slower initial convergence.
4. **Gains are real but not uniform.** 7-Scenes improves cleanly; NRGBD Accuracy and ScanNet depth do not. The honest summary is that pose guidance is the load-bearing prior and depth mainly helps surface normals.

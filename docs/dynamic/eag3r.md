# EAG3R: Event-Augmented 3D Geometry Estimation for Dynamic and Extreme-Lighting Scenes (NeurIPS 2025)

![eag3r — architecture](https://arxiv.org/html/2512.00771/x1.png)

_EAG3R pipeline for event-augmented dynamic 3D reconstruction (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Xiaoshan Wu, Yifei Yu, Xiaoyang Lyu, Yihua Huang, Bo Wang, Baoheng Zhang, Zhongrui Wang, Xiaojuan Qi
- **Institution**: The University of Hong Kong; Southern University of Science and Technology
- **Venue**: NeurIPS 2025
- **Links**: [Paper](https://arxiv.org/abs/2512.00771)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: An event-augmented, MonST3R-based geometry estimation framework that fuses asynchronous event streams with RGB via SNR-aware fusion and an event-based photometric consistency loss, enabling robust depth/pose/dynamic reconstruction in low-light dynamic scenes without night-time retraining.

## 🎯 Key Contributions

1. **First event-augmented pointmap framework**: Integrates asynchronous event streams with RGB pointmap reconstruction for dynamic scenes under extreme low-light.
2. **Plug-in event perception module**: A Retinex-based enhancer for visibility recovery and SNR-map prediction, a lightweight Swin-Transformer event adapter, and an SNR-aware fusion scheme.
3. **Event-based photometric consistency loss**: Aligns predicted motion-induced brightness changes with event-observed brightness changes during global optimization.
4. **Zero-shot night-time robustness**: Trained only on daylight, tested zero-shot on night sequences, outperforming RGB-only baselines on depth, pose, and dynamic reconstruction.

## 🔧 Technical Details

### Backbone and Fusion

- Built on the **MonST3R** backbone (itself a dynamic extension of DUSt3R via pointmaps). The image encoder is frozen; only the event adapter, enhancement net, ViT-Base decoder, and DPT heads are updated.
- **Retinex enhancement**: Estimates an illumination map to recover an enhanced image, plus an SNR map `M_snr` as a spatial reliability prior.
- **Event adapter**: A Swin-Transformer initialized from self-supervised event pre-training; voxelized events yield hierarchical features fused with frozen image features via cross-attention (events as queries).
- **SNR-aware aggregation**: Weights image features by `M_snr` and event features by `(1 − M_snr)`, then concatenates — favoring images in well-lit areas and events in low-visibility regions.

### Event-Enhanced Global Optimization

- Adds an event-based photometric consistency loss `L_event` to MonST3R's objective (`L_align + w_smooth L_smooth + w_flow L_flow + w_event L_event`).
- Brightness increments observed from integrating event polarities in Harris-corner patches are compared (after L2 normalization to cancel unknown contrast scale) against increments predicted from image gradients and motion inferred from the global state.

### Training

- Fine-tune for 25 epochs, 8,000 image-event pairs/epoch; AdamW, LR 5×10⁻⁵, batch 4/GPU; ~24 hours on 4 NVIDIA RTX 3090 GPUs.
- Global optimization: `w_smooth = 0.01`, `w_flow = 0.01`, `w_event_base = 0.01`; Adam for 300 iterations at LR 0.01.
- **Data**: Trained exclusively on MVSEC `outdoor_day2` (daylight), tested zero-shot on `outdoor_night1-3` (extreme low-light). V2E-synthesized events caused gradient explosion, motivating use of real MVSEC event captures with LiDAR depth GT.

## 📊 Results

### Monocular Depth Estimation on MVSEC Night (원논문 Table 1)

원논문 Table 1. MVSEC Night1/2/3, zero-shot. Abs Rel↓, δ<1.25↑, RMSE log↓.

| Method             | N1 AbsRel ↓ | N1 δ ↑    | N1 RMSElog ↓ | N2 AbsRel ↓ | N2 δ ↑    | N2 RMSElog ↓ | N3 AbsRel ↓ | N3 δ ↑    | N3 RMSElog ↓ |
| ------------------ | ----------- | --------- | ------------ | ----------- | --------- | ------------ | ----------- | --------- | ------------ |
| DUSt3R             | 0.407       | 0.393     | 0.534        | 0.415       | 0.384     | 0.495        | 0.463       | 0.335     | 0.534        |
| MonST3R            | 0.370       | 0.373     | 0.497        | 0.309       | 0.469     | 0.409        | 0.317       | 0.453     | 0.418        |
| MonST3R (Finetune) | 0.376       | 0.426     | 0.478        | 0.328       | 0.472     | 0.415        | 0.302       | 0.509     | 0.401        |
| **EAG3R**          | **0.353**   | **0.491** | **0.416**    | **0.307**   | **0.518** | **0.383**    | **0.288**   | **0.533** | **0.371**    |

### Camera Pose Estimation on MVSEC Night (원논문 Table 2)

원논문 Table 2. ATE↓, RPE trans↓, RPE rot↓. EAG3R가 대부분 최고이나 Easi3R(MonST3R, Finetune)가 Night2 RPE-trans, Night3 ATE/RPE-trans에서 더 낮다(더 좋음).

| Method                    | N1 ATE ↓  | N1 RPEt ↓ | N1 RPEr ↓ | N2 ATE ↓  | N2 RPEt ↓ | N2 RPEr ↓ | N3 ATE ↓  | N3 RPEt ↓ | N3 RPEr ↓ |
| ------------------------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| DUSt3R                    | 1.474     | 0.914     | 2.995     | 3.921     | 2.207     | 10.761    | 4.109     | 2.401     | 11.309    |
| MonST3R                   | 0.559     | 0.317     | 0.369     | 0.626     | 0.341     | 1.460     | 0.733     | 0.427     | 1.371     |
| MonST3R (Finetune)        | 0.580     | 0.284     | 0.214     | 0.467     | 0.210     | 0.374     | 0.402     | 0.183     | 0.370     |
| Easi3R(MonST3R, Finetune) | 0.540     | 0.263     | 0.214     | 0.448     | **0.202** | 0.374     | **0.394** | **0.178** | 0.371     |
| **EAG3R**                 | **0.482** | **0.201** | **0.143** | **0.428** | 0.207     | **0.342** | 0.409     | 0.201     | **0.320** |

### Ablation on Night3 Depth (원논문 Table 3)

원논문 Table 3. MonST3R baseline에 모듈을 점진적으로 추가.

| Method                                | Abs Rel ↓ | δ < 1.25 ↑ | RMSE log ↓ |
| ------------------------------------- | --------- | ---------- | ---------- |
| MonST3R (Baseline)                    | 0.317     | 0.453      | 0.418      |
| MonST3R (Finetune)                    | 0.302     | 0.509      | 0.401      |
| + Event                               | 0.297     | 0.518      | 0.396      |
| + Event + LightUp                     | 0.291     | 0.523      | 0.388      |
| + Event + LightUp + SNR Fusion (Full) | **0.288** | **0.533**  | **0.371**  |

## 💡 Insights & Impact

- Image enhancement alone (RetinexFormer LightUp preprocessing) does not reliably help and can degrade results — joint optimization with event cues matters.
- Asynchronous events remain informative under extreme low light, giving strong zero-shot night generalization without night-time training data.
- The ablation shows each component (events → LightUp → SNR fusion) contributes positively to final performance.

## 🔗 Related Work

- Backbone [MonST3R](monst3r.md); foundation [DUSt3R](../foundation/dust3r.md); compared against [Easi3R](easi3r.md).
- Related dynamic-scene methods cited: [DAS3R](../gaussian-splatting/das3r.md), [CUT3R](cut3r.md), [Stereo4D](stereo4d.md), [Dynamic Point Maps](dynamic-point-maps.md); also references [VGGT](../reconstruction/vggt.md) and [MASt3R-SLAM](../reconstruction/mast3r-slam.md).

## 📚 Key Takeaways

1. Event streams augment MonST3R to make pose-free geometry estimation robust to motion blur and extreme illumination.
2. SNR-aware RGB/event fusion plus an event-based photometric loss deliver best-in-most-metrics results on MVSEC night sequences, with honest reporting that a fine-tuned Easi3R variant wins some pose metrics.
3. Demonstrates zero-shot night-time transfer trained only on daylight data.

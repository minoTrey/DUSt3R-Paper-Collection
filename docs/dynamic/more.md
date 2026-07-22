# MoRe: Motion-aware Feed-forward 4D Reconstruction Transformer (CVPR 2026)

![more — architecture](https://arxiv.org/html/2603.05078v2/x2.png)

_Method Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Junton Fang, Zequn Chen, Weiqi Zhang, Donglin Di, Xuancheng Zhang, Chengmin Yang, Yu-Shen Liu
- **Institution**: School of Software, Tsinghua University, Beijing, China; Li Auto
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.05078) | [Project Page](https://hellexf.github.io/MoRe/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward 4D reconstruction transformer that jointly predicts depth, camera poses, point maps, and motion masks from monocular video, using an attention-forcing training strategy to disentangle dynamic motion from static structure and grouped causal attention with BA-like refinement for efficient streaming inference.

## 🎯 Key Contributions

1. **Unified motion-aware 4D framework**: Jointly estimates camera poses, depths, and motion masks in dynamic scenes.
2. **Attention-forcing strategy**: Aligns the camera token's attention with ground-truth motion masks during training (test-time-free), teaching the model to attend to static regions and ignore moving objects.
3. **Grouped causal attention + BA-like refinement**: Frame-wise causal masking (temporal causality across frames, full bidirectional attention within each frame) with KV-caching for streaming, plus a bundle-adjustment-like token aggregation for global refinement.

## 🔧 Technical Details

### Motion-Aligned (Attention-Forcing) Attention

- Ground-truth motion masks are patchified into mask tokens; each image token gets a motion score `a_i = 1 − (1/s²)Σ m_i`, higher for static regions.
- The camera token's attention weights `α_i` are supervised toward these scores via a penalty loss `L_attn = (1/M) Σ max(0, a_i − C)·α_i`, guiding attention to static regions. No motion mask is needed at inference.

### Grouped Causal Attention (Streaming)

- Reformulates upper-triangular causal masking into a **frame-wise** causal mask: causal across frames, full attention within a frame, preserving intra-frame spatial coherence.
- Streaming KV-cache: `F_t = Attn(Q_t, [K_{1:t-1}, K_t], [V_{1:t-1}, V_t])`; window-sliding prevents unbounded cache growth.
- **BA-like refinement**: after full-sequence inference, cached camera queries perform an additional attention pass over all cached features (`C_opt = Attn(Q_cam, [K_{1:T}], [V_{1:T}])`) for global consistency; a duplicated camera token is trained in parallel with full gradient flow.

### Training

- Losses: confidence-weighted regression (depth/point maps), relative camera loss, BCE motion loss, and the attention-alignment loss.
- Datasets (static + dynamic): Dynamic Replica, PointOdyssey, Spring, Virtual KITTI, TartanAir, Co3Dv2, ScanNet, BlendedMVS, Hypersim, ARKitScenes, Waymo, OmniWorld-Game.
- AdamW, 100K iterations, peak LR 1×10⁻⁶; 2–24 frames/sequence (interval 1–5); longer side 518; 64 NVIDIA A800 GPUs (~2 days); bfloat16 + gradient checkpointing.
- Motion masks for supervision generated via SAM2 segmentation + SEA-RAFT flow vs. ego-flow discrepancy thresholding.

## 📊 Results

### Camera Pose — Sintel & Bonn (원논문 Table 1)

원논문 Table 1 (일부). FA=full attention. ATE↓, RPEtrans↓, RPErot↓. 동적 데이터셋은 zero-shot(미학습).

| Method      | type      | Sintel ATE ↓ | Sintel RPEt ↓ | Sintel RPEr ↓ | Bonn ATE ↓ | Bonn RPEt ↓ | Bonn RPEr ↓ |
| ----------- | --------- | ------------ | ------------- | ------------- | ---------- | ----------- | ----------- |
| MapAnything | FA        | 0.2104       | 0.0919        | 2.7396        | 0.0248     | 0.0132      | 0.6927      |
| VGGT        | FA        | 0.1715       | 0.0617        | 0.4695        | 0.0141     | 0.0100      | 0.6323      |
| MoRe(FA)    | FA        | **0.0877**   | **0.0580**    | **0.3899**    | **0.0138** | **0.0099**  | **0.6267**  |
| Spann3R     | Streaming | 0.3313       | 0.1111        | 4.4952        | 0.0344     | 0.0212      | 2.2539      |
| CUT3R       | Streaming | 0.2163       | 0.0756        | 0.6518        | 0.0420     | **0.0094**  | 0.6825      |
| StreamVGGT  | Streaming | 0.4159       | 0.1097        | 1.1056        | 0.0451     | 0.0148      | **0.5982**  |
| Wint3R      | Streaming | 0.2251       | 0.0972        | 1.0922        | 0.0366     | 0.0084      | 0.7170      |
| Stream3R    | Streaming | 0.2144       | 0.0764        | 0.8674        | 0.0235     | 0.0108      | 0.6664      |
| MoRe        | Streaming | 0.1474       | 0.0776        | 0.6157        | 0.0211     | 0.0117      | 0.6496      |

### Camera Pose — TUM-dynamics & ScanNet (원논문 Table 1)

원논문 Table 1 (일부). ScanNet은 static. MoRe(FA)는 ScanNet ATE/RPErot에서 VGGT에 뒤지고, 스트리밍 MoRe는 TUM ATE에서 Stream3R에 뒤진다.

| Method      | type      | TUM ATE ↓  | TUM RPEt ↓ | TUM RPEr ↓ | ScanNet ATE ↓ | ScanNet RPEt ↓ | ScanNet RPEr ↓ |
| ----------- | --------- | ---------- | ---------- | ---------- | ------------- | -------------- | -------------- |
| MapAnything | FA        | 0.0244     | 0.0161     | 0.3871     | 0.0603        | 0.0280         | 0.8490         |
| VGGT        | FA        | **0.0109** | 0.0092     | 0.2992     | **0.0347**    | 0.0151         | **0.3758**     |
| MoRe(FA)    | FA        | 0.0115     | **0.0088** | **0.2980** | 0.0375        | **0.0147**     | 0.3847         |
| Spann3R     | Streaming | 0.0421     | 0.0333     | 0.8120     | 0.0651        | 0.0339         | 0.9348         |
| CUT3R       | Streaming | 0.0438     | 0.0134     | 0.4210     | 0.0929        | 0.0223         | 0.5811         |
| StreamVGGT  | Streaming | 0.0760     | 0.0317     | 0.7012     | 0.1436        | 0.0437         | 1.6533         |
| Wint3R      | Streaming | 0.0700     | 0.0221     | 0.7325     | 0.0618        | 0.0204         | 0.7028         |
| Stream3R    | Streaming | **0.0240** | 0.0123     | **0.3180** | 0.0521        | 0.0215         | 0.9919         |
| MoRe        | Streaming | 0.0260     | 0.0122     | 0.3201     | 0.0605        | 0.0212         | 0.5595         |

### Video Depth Estimation (원논문 Table 2)

원논문 Table 2. Abs Rel↓, δ<1.25↑. 스트리밍 MoRe는 TUM에서 Stream3R보다 약하다.

| Method      | type      | Sintel AbsRel ↓ | Sintel δ ↑ | Bonn AbsRel ↓ | Bonn δ ↑  | TUM AbsRel ↓ | TUM δ ↑   | kitti AbsRel ↓ | kitti δ ↑ |
| ----------- | --------- | --------------- | ---------- | ------------- | --------- | ------------ | --------- | -------------- | --------- |
| Flare       | FA        | 0.729           | 0.336      | 0.116         | 0.897     | 0.152        | 0.790     | 0.356          | 0.570     |
| MapAnything | FA        | 0.632           | 0.461      | 0.125         | 0.859     | 0.241        | 0.813     | 0.277          | 0.742     |
| VGGT        | FA        | 0.387           | 0.584      | 0.055         | 0.970     | 0.132        | **0.901** | 0.073          | 0.961     |
| MoRe(FA)    | FA        | **0.335**       | **0.645**  | **0.055**     | **0.971** | **0.120**    | **0.902** | **0.066**      | **0.967** |
| Spann3R     | Streaming | 0.740           | 0.364      | 0.229         | 0.729     | 0.264        | 0.645     | 0.422          | 0.358     |
| CUT3R       | Streaming | 1.363           | 0.434      | 0.076         | 0.949     | 0.160        | 0.856     | 0.124          | 0.873     |
| StreamVGGT  | Streaming | 0.698           | 0.591      | 0.058         | **0.972** | 0.156        | 0.889     | 0.173          | 0.722     |
| Wint3R      | Streaming | 0.830           | 0.537      | 0.071         | 0.912     | 0.177        | 0.808     | 0.201          | 0.601     |
| Stream3R    | Streaming | 0.397           | 0.632      | 0.070         | 0.952     | **0.151**    | **0.898** | 0.079          | 0.949     |
| MoRe        | Streaming | 0.254           | 0.637      | 0.068         | 0.961     | 0.173        | 0.868     | 0.072          | 0.966     |

### Ablation — Camera Pose (원논문 Table 3)

원논문 Table 3. Sintel + TUM-dynamics.

| Method                 | Sintel ATE ↓ | Sintel RPEt ↓ | Sintel RPEr ↓ | TUM ATE ↓ | TUM RPEt ↓ | TUM RPEr ↓ |
| ---------------------- | ------------ | ------------- | ------------- | --------- | ---------- | ---------- |
| w/o attention forcing  | 0.163        | 0.092         | 0.660         | 0.028     | 0.014      | 0.329      |
| w/o BA-like refinement | 0.155        | 0.085         | 0.619         | 0.027     | 0.014      | 0.321      |
| full                   | **0.147**    | **0.082**     | **0.616**     | **0.026** | **0.013**  | **0.320**  |

### Ablation — Video Depth (원논문 Table 4)

원논문 Table 4. GCA=Grouped Causal Attention.

| Method    | Sintel AbsRel ↓ | Sintel δ ↑ | Bonn AbsRel ↓ | Bonn δ ↑  | kitti AbsRel ↓ | kitti δ ↑ |
| --------- | --------------- | ---------- | ------------- | --------- | -------------- | --------- |
| w/o GCA   | 0.277           | 0.592      | 0.070         | 0.953     | 0.079          | 0.949     |
| w/ (full) | **0.254**       | **0.637**  | **0.068**     | **0.961** | **0.072**      | **0.966** |

## 💡 Insights & Impact

- Directly transferring a static foundation model (VGGT) to 4D fails because the camera token spreads attention uniformly over moving objects; attention-forcing corrects this at training time with zero inference overhead.
- Standard LLM-style causal attention breaks intra-frame token correspondences; frame-wise grouped causal attention preserves spatial coherence while enabling streaming.
- Among full-attention methods MoRe(FA) is competitive with the state of the art despite less training data, and it clearly beats streaming baselines on most metrics.

## 🔗 Related Work

- Backbone/comparison [VGGT](../reconstruction/vggt.md); foundation [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [Fast3R](../reconstruction/fast3r.md); also compares to [MapAnything](../reconstruction/mapanything.md) and [Pi3 (π³)](../reconstruction/pi3.md).
- Streaming peers: [Spann3R](../reconstruction/spann3r.md), [CUT3R](cut3r.md), [StreamVGGT](../reconstruction/streamvggt.md), [Stream3R](../reconstruction/stream3r.md), [Wint3R](../reconstruction/wint3r.md); dynamic method [MonST3R](monst3r.md).

## 📚 Key Takeaways

1. Attention-forcing supervises the camera token toward static regions using motion masks only at training time, making inference lightweight and streaming-friendly.
2. Grouped causal attention + BA-like refinement deliver efficient streaming 4D reconstruction that outperforms streaming baselines and rivals full-attention methods.
3. Honest reporting: VGGT edges MoRe(FA) on some ScanNet static-pose metrics, and Stream3R wins some streaming TUM depth/pose numbers.

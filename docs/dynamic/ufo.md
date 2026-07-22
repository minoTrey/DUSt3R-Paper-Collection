# UFO: Unifying Feed-Forward and Optimization-based Methods for Large Driving Scene Modeling (arXiv preprint (2026-02))

![ufo — architecture](https://arxiv.org/html/2602.20943/images/pipeline_v7.png)

_Overview of our proposed framework (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Kaiyuan Tan\*, Yingying Shen\*, Ziyue Zhu, Mingfei Tu, Haohui Zhu, Bing Wang, Guang Chen, Hangjun Ye (B), Haiyang Sun (†)
- **Institution**: Xiaomi EV, UIUC
- **Venue**: arXiv preprint (2026-02)
- **Links**: [Paper](https://arxiv.org/abs/2602.20943) | [Project Page](https://wm-research.github.io/UFO)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A recurrent paradigm that unifies optimization-based and feed-forward methods for long-range 4D driving scene reconstruction, maintaining a token-based 4D scene representation that is iteratively refined as new frames arrive with a visibility-based token filter and object pose-guided dynamic modeling.

> Author markers from page 1: `*` Equal contribution, `B` Corresponding author (Hangjun Ye), `†` Project leader (Haiyang Sun).

## 🎯 Key Contributions

1. **Recurrent feed-forward paradigm**: A paradigm for long-range 4D driving scene reconstruction that learns to iteratively refine scene representations in a feed-forward manner, combining the strengths of optimization-based and feed-forward methods.
2. **Visibility-based filtering mechanism**: Selects only the most relevant scene tokens for updating at each step, reducing computational complexity from quadratic to near-linear in sequence length and achieving near-linear time and memory complexity.
3. **Dynamic object modeling with lifespan-aware Gaussians**: Leverages object poses combined with learnable per-Gaussian lifespans and soft object assignments, enabling long-range and complex motion capture without restrictive kinematic assumptions.

## 🔧 Technical Details

### Problem & Overview

Given a sequence of RGB images `{I_t}` with corresponding camera poses `{P_t}`, UFO efficiently reconstructs a 4D scene representation `S` supporting high-quality novel view synthesis (NVS) and depth estimation. The design abstracts the render-supervise-update loop of 3DGS into a single holistic transformer, executed recurrently. Three components:

1. **Token-based scene representation (Sec. 3.1)**: The 4D scene is a compact set of scene tokens `S_t = {s_t^i}`, where each token `s_t^i ∈ R^{3+D}` holds a 3D world location plus a `D`-dimensional feature vector (`D = 768`) encoding appearance, geometry, and motion, decodable into 3D Gaussians. Inputs are image tokens (per-pixel RGB + Plücker ray embeddings, ViT patches), bounding-box tokens `B_t ∈ R^{N_obj × D}` (Fourier embeddings of tracked 3D box centers/corners), and shared auxiliary tokens for sky and per-camera affine correction.
2. **Recurrent scene update (Sec. 3.2)**: When a new frame `I_t` arrives, a 12-layer ViT-style transformer `T_update` performs two operations — refining existing tokens from new visual evidence, and creating new tokens for previously unobserved content — via `S_t = T_update(I_t, S_{t-1})`, without explicit rendering or backpropagation through rendering.
3. **Dynamic object modeling (Sec. 3.3)**: Uses 3D object poses with learnable lifespan parameters to model complex object motions without restrictive kinematic assumptions.

### Visibility-Based Filtering

Not all tokens matter for each incoming frame. For frame `I_t` with pose `P_t`, tokens inside the camera frustum are identified, and the closest `K` tokens to the camera center form the visible set `V_{t-1}`. The transformer operates only on this subset, producing refined tokens and new tokens; the scene is reassembled by replacing visible tokens with refined versions and appending new ones. In practice `K = 3600`. A local (camera-centric) coordinate system is adopted at each step to improve training stability over long sequences.

### Dynamic Object Modeling

- **Bounding box-guided motion**: Tracked 3D boxes (from off-the-shelf detection/tracking) are encoded as tokens and concatenated with scene and image tokens. Each scene token receives a soft probability over tracked objects via cross-attention; Gaussian motion is a weighted average of object transformations. An object assignment regularization (cross-entropy `L_obj`) encourages tokens inside a box to be assigned to that object.
- **Temporal lifespan** (inspired by PVG): each decoded Gaussian gets a lifespan `β`, with opacity `σ(t) = σ · exp(-(t - t_0)^2 / (2β^2))`, decoded via SoftPlus. A lifespan regularizer `L_lifespan` encourages longer temporal persistence.

### Training

End-to-end objective: `L = L2 + L_LPIPS + L_depth + L_lifespan + L_obj + L_sky`. Feature decoder is a 12-layer Transformer encoder with patch size 8 and embedding dimension 768; up to 32 object boxes retained per frame (ranked by LiDAR points inside each box); box encoder and Gaussian decoder are 2-layer MLPs; gsplat is the splatting backend. Total trainable parameters ≈ 92M. Trained on 16 NVIDIA H200 GPUs with total batch size 64 for about one day. Images are downsampled to 160×240 (front, front-left, front-right cameras).

## 📊 Results

Evaluated on the **Waymo Open Dataset (WOD)**; each segment is roughly 20 s at 10 Hz, sampling every 5th frame as context. Notably, UFO reconstructs 16-second driving logs within 0.5 second while maintaining superior visual quality and geometric accuracy. For 16 s sequences, UFO reports **zero-shot** performance from a model trained only on 8 s sequences (STORM and GS-LRM could not be trained on 16 s due to out-of-memory).

### Novel View Synthesis — 2s and 8s Sequences

원논문 Table 1. PSNR↑, SSIM↑, Depth RMSE (D-RMSE)↓.

| Method            | 2s PSNR↑ | 2s SSIM↑ | 2s D-RMSE↓ | 8s PSNR↑ | 8s SSIM↑ | 8s D-RMSE↓ |
| ----------------- | -------- | -------- | ---------- | -------- | -------- | ---------- |
| 3DGS              | 21.07    | 0.578    | 13.52      | 19.57    | 0.517    | 14.42      |
| PVG               | 23.81    | 0.649    | 13.82      | 22.90    | 0.619    | 18.24      |
| Street Gaussians  | 22.96    | 0.652    | 12.15      | 21.69    | 0.609    | 13.17      |
| DeformableGS      | 23.40    | 0.669    | 11.55      | 21.47    | 0.611    | 13.12      |
| GS-LRM            | 25.18    | 0.753    | 7.94       | 21.81    | 0.584    | 7.37       |
| STORM             | 26.38    | 0.794    | 5.48       | 24.48    | 0.736    | 8.11       |
| STORM (iterative) | 26.38    | 0.794    | 5.48       | 21.25    | 0.609    | 12.35      |
| **Ours-UFO**      | 27.26    | 0.825    | 5.45       | 27.39    | 0.830    | 5.10       |

### Novel View Synthesis — 16s Sequences (zero-shot)

원논문 Table 1. PSNR↑, SSIM↑, D-RMSE↓. UFO's 16s model is zero-shot (trained on 8s only).

| Method            | PSNR↑ | SSIM↑  | D-RMSE↓ |
| ----------------- | ----- | ------ | ------- |
| 3DGS              | 17.18 | 0.454  | 17.01   |
| PVG               | 21.79 | 0.599  | 17.21   |
| Street Gaussians  | 22.67 | 0.675  | 14.88   |
| DeformableGS      | 19.79 | 0.600  | 15.82   |
| GS-LRM            | 16.98 | 0.500  | 9.81    |
| STORM             | 22.02 | 0.614  | 7.91    |
| STORM (iterative) | 19.88 | 0.541  | 11.65   |
| **Ours-UFO**      | 27.04 | 0.8162 | 5.08    |

### Ablation Study

원논문 Table 2. Evaluated on 8s WOD sequences with 16 uniformly sampled input frames. PSNR↑, SSIM↑, D-RMSE↓.

| Configuration              | PSNR↑ | SSIM↑ | D-RMSE↓ |
| -------------------------- | ----- | ----- | ------- |
| (1) w/o iterative training | 20.67 | 0.625 | 11.81   |
| (2) w/o scene tokens       | 26.31 | 0.787 | 5.31    |
| (3) w/o refinement         | 27.08 | 0.824 | 5.13    |
| (4) w/o lifespan           | 26.47 | 0.790 | 5.21    |
| (5) w/o bounding box       | 26.88 | 0.818 | 5.12    |
| **Ours (full)**            | 27.39 | 0.830 | 5.10    |

### Scalability & Dynamic Objects

- **Time complexity**: UFO exhibits nearly linear time complexity in input sequence length `n`, while STORM displays quadratic growth (Figure 4, per-point values not printed in text).
- **Memory**: both methods show roughly linear memory growth, but UFO scales more slowly and uses approximately 25% less memory for 16s sequences.
- **Dynamic objects**: across all input-frame configurations (fixed 2-second span, single-step prediction with recurrent update disabled), UFO consistently outperforms STORM (Figure 6, per-point values not printed in text), indicating bounding-box guidance with lifespan-aware Gaussians captures complex object motion better than STORM's constant-velocity assumption.

## 💡 Insights & Impact

- **Optimization-as-feed-forward**: UFO abstracts the iterative render-supervise-update loop of 3DGS into a single transformer executed recurrently, keeping the refinement benefit of optimization while gaining feed-forward speed (16s logs in ~0.5 s).
- **Bidirectional refinement**: Unlike unidirectional streaming methods (Spann3R, StreamVGGT, Point3R, CUT3R) where the current frame only references past frames, UFO iteratively refines the scene at each timestep — and, unlike those pointmap-streaming methods, supports photorealistic novel view synthesis.
- **Honest degradation profile**: Competing feed-forward baselines (GS-LRM, STORM) degrade substantially at 16s and could not even train on 16s (out-of-memory), whereas UFO holds up zero-shot from an 8s-trained model.
- **Emergent temporal prior**: Even the "w/o scene tokens" ablation benefits from iterative training — the model learns a correlation between opacity and time (earlier timesteps → short-range Gaussians, later → long-range), aiding Gaussian allocation.
- **Robustness bonus**: The lifespan parameter `β` naturally handles transient lighting artifacts (lens flare, windshield reflections, glare) by assigning short lifespans, without explicit artifact supervision.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: Introduces the pointmap representation for reconstruction from unposed images; UFO cites it as the foundation of the unposed-image reconstruction line it extends toward driving scenes.
- **[MonST3R](./monst3r.md)**: Extends the pointmap direction to dynamic data, cited among works UFO builds on for dynamic reconstruction.
- **[VGGT](../reconstruction/vggt.md)** / **[Fast3R](../reconstruction/fast3r.md)**: Incorporate global attention to avoid global-alignment post-processing, cited in the feed-forward reconstruction discussion.
- **[Spann3R](../reconstruction/spann3r.md)** / **[StreamVGGT](../reconstruction/streamvggt.md)** / **[Point3R](../reconstruction/point3r.md)** / **[CUT3R](./cut3r.md)**: Streaming reconstruction approaches UFO contrasts against — they cache/query historical features or memory but are unidirectional and do not support photorealistic NVS, whereas UFO is bidirectional and renders.

## 📚 Key Takeaways

1. **Unified paradigm**: UFO fuses optimization-based iterative refinement with feed-forward inference into one recurrent transformer for long-range 4D driving scene reconstruction.
2. **Near-linear scaling**: Visibility-based filtering (`K = 3600` tokens) reduces update cost from quadratic to near-linear; ~25% less memory than STORM at 16s.
3. **Strong long-range results**: On WOD, UFO leads PSNR/SSIM/D-RMSE at 2s (27.26 / 0.825 / 5.45) and 8s (27.39 / 0.830 / 5.10), and holds at 16s zero-shot (27.04 / 0.8162 / 5.08) while feed-forward baselines collapse or run out of memory.
4. **Dynamic modeling**: Object pose-guided motion plus learnable per-Gaussian lifespans capture complex motion without constant-velocity assumptions; ablations confirm refinement, scene tokens, lifespan, and bounding-box guidance each contribute.

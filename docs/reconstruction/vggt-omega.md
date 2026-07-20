# VGGT-Ω: Scaling Feed-Forward Reconstruction with Registers and Self-Supervision (CVPR 2026)

## 📋 Overview

- **Authors**: Jianyuan Wang, Minghao Chen, Shangzhan Zhang, Nikita Karaev, Johannes Schönberger, Patrick Labatut, Piotr Bojanowski, David Novotny, Andrea Vedaldi, Christian Rupprecht
- **Institution**: Visual Geometry Group, University of Oxford; Meta AI
- **Venue**: CVPR 2026
- **Award**: Oral
- **Links**: [Paper](https://arxiv.org/abs/2605.15195) | [Project Page](http://vggt-omega.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Feed-forward reconstruction quality scales predictably with model and data size; VGGT-Ω simplifies VGGT to a single dense head, adds register attention, and trains at 10B parameters on millions of annotated and unlabeled videos to handle static and dynamic scenes alike.

## 🎯 Key Contributions

1. **Demonstrated scaling behavior**: point error falls monotonically as model size grows from 0.2B to 10B and data from 2K to 2M sequences, with the paper suggesting power laws may characterize this class of models.
2. **Single dense head**: point maps and tracks are still supervised through losses, but only depth is decoded densely — nearly the same accuracy at substantially lower training memory.
3. **Register attention**: 25% of global attention layers are replaced with attention restricted to per-frame registers, which then redistribute scene information through frame-wise blocks.
4. **Lightweight upsampling decoder**: DPT blocks above 1/4 resolution are replaced by an MLP plus pixel-shuffle producing depth and confidence.
5. **Dynamic scene support**: by predicting only depth and cameras — no ray maps, no motion masks — camera motion stays disentangled from scene motion.
6. **Data annotation pipeline**: a VLM-gated, COLMAP-verified, classifier-filtered pipeline yielding ~200K dynamic and ~600K static annotated sequences from ~40M candidate videos.
7. **Self-supervised protocol**: EMA teacher-student distillation over unlabeled videos with frozen camera/depth heads to prevent collapse.
8. **Registers as a general interface**: the same tokens transfer to robotic policy conditioning and language alignment.

## 🔧 Technical Details

### Register Attention

Global attention lets frames interact but costs quadratically in total tokens, and the paper observes global attention maps are typically sparse. Register attention restricts cross-frame self-attention to the registers only:

```text
z' = attn_scene(z),  where (z_1^scene', …, z_N^scene') = attn(z_1^scene, …, z_N^scene)
```

Updated registers then interact with each frame's image tokens in the subsequent frame-wise blocks. The paper is explicit that during inference the benefit is speed, not memory — with flash attention v2 the full attention matrix is never materialized, so peak memory is dominated by frame-proportional activations either way.

### Decoding

- **Depth**: DPT blocks above 1/4 input resolution replaced with a single MLP outputting `2u²` channels (`u = 4`) plus a pixel-shuffle, producing depth and confidence. Early low-resolution convolutional layers are retained — a fully convolution-free MLP decoder benchmarked well but produced blocky artifacts on unbounded outdoor depth.
- **Camera**: a lightweight transformer over camera tokens and registers, then an MLP per camera token. Unlike VGGT, prediction is single-pass with no iterative refinement.

### Losses

```text
L = λ_cam·L_cam + λ_depth·L_depth + λ_point·L_point + λ_match·L_match
```

The camera loss uses ℓ1 rather than VGGT's Huber, which the authors found more stable. The point loss reuses the depth loss form with residuals from unprojection. The matching loss is a weighted binary cross-entropy over cosine similarity of ℓ2-normalized tokens from the last attention layer.

### Training Setup

- Variants: 200M, 500M, 1B, 10B parameters with 12/12/24/16 alternating-attention blocks and hidden sizes 384/768/1024/4096
- ViT initialized from DINOv3, not frozen
- AdamW, 240K iterations: 160K supervised, 50K self-supervised, final 30K supervised
- Linear warm-up over 5% then cosine decay; peak LR 2 × 10⁻⁴ supervised, 1 × 10⁻⁴ self-supervised
- Frames per batch drawn uniformly from [1, 24]; image area held near 512 × 512
- 128 × 96GB H100 GPUs, bfloat16, gradient checkpointing, FSDP

## 📊 Results

### Camera Pose Estimation — Static Scenes

원논문 Table 1. AUC는 높을수록 좋다. DA3는 Giant 변종을 사용.

| Method      | 7 Scenes AUC@3° | 7 Scenes AUC@30° | NRGBD AUC@3° | NRGBD AUC@30° | ETH3D AUC@3° | ETH3D AUC@30° |
| ----------- | --------------- | ---------------- | ------------ | ------------- | ------------ | ------------- |
| MonST3R     | 9.0             | 68.3             | 13.9         | 79.7          | 1.7          | 14.3          |
| MapAnything | 5.8             | 61.4             | 35.2         | 88.9          | 13.2         | 51.0          |
| MegaSaM     | 10.6            | 71.8             | 17.2         | 83.1          | 5.9          | 38.1          |
| VGGT        | 10.9            | 74.4             | 81.7         | 97.7          | 18.8         | 62.1          |
| PI3         | 13.3            | 77.0             | 83.8         | 98.2          | 35.3         | 79.6          |
| DA3         | 18.7            | 78.2             | 86.4         | 98.4          | 46.1         | 87.0          |
| Ours-1B     | 29.6            | 83.1             | 89.7         | 98.8          | 49.8         | 88.5          |
| Ours-10B    | **36.4**        | **88.2**         | **92.5**     | **99.1**      | **56.3**     | **90.4**      |

### Camera Pose Estimation — Dynamic Scenes

원논문 Table 1 (계속).

| Method      | DyCheck AUC@3° | DyCheck AUC@30° | Sintel AUC@3° | Sintel AUC@30° | TUM-Dyn AUC@3° | TUM-Dyn AUC@30° |
| ----------- | -------------- | --------------- | ------------- | -------------- | -------------- | --------------- |
| MonST3R     | 11.5           | 45.4            | 4.3           | 45.8           | 7.7            | 48.5            |
| MapAnything | 6.1            | 60.3            | 2.9           | 31.6           | 4.3            | 40.2            |
| MegaSaM     | 26.8           | 53.1            | 22.5          | 58.3           | 15.4           | 59.0            |
| VGGT        | 21.0           | 78.7            | 15.0          | 50.0           | 16.6           | 61.2            |
| PI3         | 23.3           | 81.0            | 14.8          | 53.5           | 16.1           | 59.2            |
| DA3         | 32.1           | 83.9            | 16.2          | 52.7           | 20.8           | 62.7            |
| Ours-1B     | 38.4           | 87.3            | 35.3          | 73.0           | 30.2           | 82.3            |
| Ours-10B    | **43.7**       | **90.9**        | **40.0**      | **79.1**       | **36.4**       | **87.5**        |

The paper highlights that on Sintel AUC@3°, feed-forward baselines lag MegaSaM (16.2 vs 22.5) — a gap VGGT-Ω closes and reverses, reaching 40.0. Conversely MegaSaM and MonST3R degrade badly on the wide-baseline ETH3D set.

### Depth Estimation — Static Scenes

원논문 Table 2. δ1.25는 높을수록, AbsRel은 낮을수록 좋다.

| Method      | 7 Scenes δ1.25 ↑ | 7 Scenes AbsRel ↓ | NRGBD δ1.25 ↑ | NRGBD AbsRel ↓ | ETH3D δ1.25 ↑ | ETH3D AbsRel ↓ |
| ----------- | ---------------- | ----------------- | ------------- | -------------- | ------------- | -------------- |
| MonST3R     | 92.4             | 0.075             | 98.4          | 0.030          | 95.8          | 0.056          |
| MapAnything | 92.9             | 0.070             | 98.7          | 0.022          | 96.3          | 0.035          |
| MegaSaM     | 93.8             | 0.065             | 96.2          | 0.057          | 94.8          | 0.083          |
| VGGT        | 91.9             | 0.073             | 99.1          | 0.019          | 97.4          | 0.036          |
| PI3         | 92.8             | 0.068             | 99.2          | 0.011          | 99.6          | 0.016          |
| DA3         | 93.0             | 0.063             | 99.5          | 0.010          | 99.6          | 0.015          |
| Ours-1B     | 94.6             | 0.058             | 99.6          | 0.010          | 99.8          | 0.012          |
| Ours-10B    | **96.3**         | **0.050**         | **99.7**      | **0.007**      | **99.8**      | **0.009**      |

### Depth Estimation — Dynamic Scenes

원논문 Table 2 (계속).

| Method      | DyCheck δ1.25 ↑ | DyCheck AbsRel ↓ | Sintel δ1.25 ↑ | Sintel AbsRel ↓ | TUM-Dyn δ1.25 ↑ | TUM-Dyn AbsRel ↓ |
| ----------- | --------------- | ---------------- | -------------- | --------------- | --------------- | ---------------- |
| MonST3R     | 93.3            | 0.068            | 71.9           | 0.263           | 85.0            | 0.148            |
| MapAnything | 97.0            | 0.049            | 72.5           | 0.251           | 93.1            | 0.052            |
| MegaSaM     | 97.4            | 0.042            | 74.1           | 0.207           | 92.9            | 0.083            |
| VGGT        | 95.2            | 0.055            | 79.2           | 0.189           | 92.2            | 0.064            |
| PI3         | 97.4            | 0.041            | 82.5           | 0.144           | 95.5            | 0.046            |
| DA3         | 97.7            | 0.039            | 86.1           | 0.118           | 94.3            | 0.049            |
| Ours-1B     | 98.4            | 0.038            | 89.5           | 0.097           | 97.4            | 0.041            |
| Ours-10B    | **98.7**        | **0.030**        | **93.5**       | **0.081**       | **98.3**        | **0.035**        |

### Ablations

원논문 4.3절. 1B 모델, 2M 시퀀스, 64 GPU, 150k supervised step. 지표는 point error (낮을수록 좋다).

| Setting                                  | Point Error ↓ |
| ---------------------------------------- | ------------- |
| Global attention only                    | 0.071         |
| 25% replaced with register attention     | 0.073         |
| w/o point and matching losses            | 0.078         |
| VGGT-style multi-head multi-task         | 0.070         |
| 10% of steps replaced by self-supervised | 0.070         |

Register attention costs a small amount of accuracy (0.071 → 0.073) in exchange for the speedup. The VGGT-style multi-head setup is actually slightly better at 0.070, but the paper rejects it because multiple dense heads make scaling difficult — an honest trade rather than a win.

### Scaling

원논문 Figure 1. Point error ↓, 여섯 개 데이터셋 평균.

| Axis       | Setting | Point Error ↓ |
| ---------- | ------- | ------------- |
| Model size | 1B      | 0.107         |
| Model size | 5B      | 0.073         |
| Model size | 10B     | 0.046         |
| Data size  | 10⁴     | 0.275         |
| Data size  | 10⁵     | 0.210         |
| Data size  | 10⁶     | 0.129         |

Text reports data scaling in 10× steps dropping point error from 0.275 to 0.073. All models were trained on approximately the same number of tokens.

### Annotation Quality

원논문 4.3절. Sintel에서 자체 필터링 기준과 MegaSaM 검증을 모두 통과하는 시퀀스·픽셀만 평가 (23개 중 8개 시퀀스 및 모든 동적 영역 제외).

| Pipeline | Camera AUC@30° ↑ | Depth δ1.25 ↑ |
| -------- | ---------------- | ------------- |
| MegaSaM  | 62.1             | 77.2          |
| Ours     | **96.4**         | **99.3**      |

### LIBERO Robotics Benchmark

원논문 Table 3. Success rate (SR), 높을수록 좋다. VGGT-Ω는 고정(frozen)된 채 scene token만 제공.

| Method                          | Spatial  | Object   | Goal     | Long     | Average  |
| ------------------------------- | -------- | -------- | -------- | -------- | -------- |
| Diffusion Policy                | 78.3     | 92.5     | 68.3     | 50.5     | 72.4     |
| Octo                            | 78.9     | 85.7     | 84.6     | 51.1     | 75.1     |
| OpenVLA                         | 84.7     | 88.4     | 79.2     | 53.7     | 76.5     |
| CoT-VLA                         | 87.5     | 91.6     | 87.6     | 69.0     | 83.9     |
| π0                              | 96.8     | 98.8     | 95.8     | 85.2     | 94.2     |
| UniVLA                          | 96.5     | 96.8     | 95.6     | 92.0     | 95.2     |
| OpenVLA-OFT                     | 97.6     | 98.4     | 97.9     | 94.5     | 97.1     |
| OpenVLA-OFT + Our Frozen Tokens | **99.3** | **99.2** | **99.0** | **96.7** | **98.5** |

### Language Alignment

원논문 4.4절. 100개 수작업 큐레이션 인터넷 비디오 벤치마크.

| Embedding used                    | Top-1 ↑ | Top-3 ↑ |
| --------------------------------- | ------- | ------- |
| VLM embedding (used in alignment) | 76.8    | 97.0    |
| Qwen3 text-only (zero-shot)       | 47.5    | 77.8    |

The paper reports no degradation on geometric tasks after alignment fine-tuning.

## 💡 Insights & Impact

### Scaling Is the Contribution

Most papers in this lineage argue for an architectural idea. VGGT-Ω's central claim is empirical: reconstruction quality is predictable in model and data size, and the architectural changes exist mostly to make that scaling affordable. The single dense head, register attention, and lightweight upsampler are all justified by training cost rather than by accuracy — and the ablations say so plainly.

### Removing Global Attention Buys Speed, Not Memory

A rare correction to intuition. Since flash attention v2 never materializes the attention matrix, peak inference memory is dominated by frame-proportional activations, and register attention leaves it nearly unchanged. The paper explicitly stresses this rather than letting the reader assume otherwise.

### Depth + Cameras Beats Ray Maps for Dynamics

The paper argues ray maps add an expensive dense output and can entangle camera information with pixel-wise appearance change — a stationary camera watching a dancer has huge motion but fixed camera parameters. Predicting only depth and cameras sidesteps this, and no explicit motion masks are needed. This is a direct disagreement with the depth-ray formulation of DA3.

### Conservative Annotation Beats Volume

The annotation pipeline discards 90% of candidate videos at the VLM stage alone. On the Sintel comparison its retained annotations reach 96.4% pose AUC@30° against MegaSaM's 62.1%. The stated principle — a smaller set of highly accurate pseudo ground truth beats a larger noisier one — cuts against the usual scale-first instinct.

### Registers Carry Semantics

Frozen registers improve every LIBERO task, and a language token that never sees image patch tokens still retrieves the right description 76.8% of the time. The authors connect this to the platonic representation hypothesis: geometry training alone appears to produce representations that align with language space.

## 🔗 Related Work

- **[VGGT](vggt.md)**: The model being scaled. VGGT-Ω keeps alternating attention but drops the redundant dense heads, replaces Huber with ℓ1 camera loss, removes iterative camera refinement, and switches DINOv2 for DINOv3. It also fixes an inference implementation detail in VGGT before benchmarking speed against it.
- **[Depth Anything 3](depth-anything-3.md)**: The strongest published baseline in nearly every table, and the direct target of the depth-vs-ray-map argument.
- **[Pi3](pi3.md)**: Consistently the second-strongest baseline among feed-forward models across both static and dynamic sets.
- **[MapAnything](mapanything.md)**: Compared as a feed-forward baseline; it degrades notably on Sintel and TUM-Dynamic.
- **[MonST3R](../dynamic/monst3r.md)**: The dynamic-aware pointmap baseline; the paper notes point-map methods need motion segmentation for dynamic scenes, which VGGT-Ω avoids entirely.
- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: The pairwise foundation this scaling study inherits its task definition from.

## 📚 Key Takeaways

1. **Feed-forward reconstruction scales predictably**: point error drops monotonically across three orders of magnitude in data and roughly two in parameters.
2. **Supervise redundant targets, decode only one**: point and matching losses can be kept while only depth gets a dense head, saving significant training memory.
3. **Register attention is a speed trade, not a free lunch**: 0.071 → 0.073 point error is the honest cost.
4. **Predict depth and cameras, not ray maps, for dynamic scenes**: it keeps camera motion disentangled from scene motion without motion masks.
5. **Aggressively filtered pseudo-labels outperform bulk annotation**: 96.4% vs 62.1% pose AUC@30° on the controlled Sintel comparison.
6. **Geometry registers are a reusable interface**: they improve VLA policies while frozen and align to language without ever seeing patch tokens.

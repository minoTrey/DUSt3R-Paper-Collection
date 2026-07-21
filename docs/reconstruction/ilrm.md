# iLRM: An Iterative Large 3D Reconstruction Model (CVPR 2026)

## 📋 Overview

- **Authors**: Gyeongjin Kang, Seungtae Nam, Seungkwon Yang, Xiangyu Sun, Sameh Khamis, Abdelrahman Mohamed, Eunbyung Park
- **Institution**: Sungkyunkwan University, Yonsei University, Rembrand, Meta
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2507.23277) | [Project Page](https://gynjn.github.io/iLRM/)
- **Verification**: CONFIRMED (2026-07-21)
- **TL;DR**: A feed-forward 3D Gaussian reconstruction transformer that decouples the scene representation from input images, initializing compact viewpoint tokens and iteratively refining them layer by layer through per-view cross-attention with high-resolution image tokens followed by viewpoint self-attention.

## 🎯 Key Contributions

1. **Decoupling scene representation from input images**: Instead of pixel-aligned Gaussians whose count is dictated by input resolution, iLRM initializes viewpoint embeddings at a freely chosen (lower) resolution, so the number of Gaussians is independent of image resolution.
2. **Two-stage attention for multi-view interaction**: Per-view cross-attention between each viewpoint embedding and its own image (one-to-one, hence cheap), then self-attention across all viewpoint embeddings in the low-resolution representation space.
3. **High-resolution guidance at every layer**: Image tokens stay at full resolution and are injected into every update layer, so compactness does not cost fidelity.
4. **Iterative, feedback-driven refinement**: Each layer revises the current scene tokens against fixed image evidence, which the paper frames as an analogue of a gradient-descent step inside a feed-forward network.
5. **Mini-batch cross-attention**: Structured subsampling of image and viewpoint tokens during cross-attention, inspired by mini-batch gradient descent, trading a small quality drop for large training-time savings.

## 🔧 Technical Details

### Problem Formulation

Given N images and camera poses, the model maps the set of viewpoints to 3D Gaussian primitives (mean, opacity, covariance, color). Crucially the Gaussian grid resolution `H^v × W^v` per viewpoint does **not** correspond to the input image resolution.

### Tokenization

- **Viewpoint tokens**: Plücker ray embeddings per input view, split into `p × p` patches and linearly encoded. Because Plücker coordinates already encode spatial variation across pixels and views, no additional positional embedding is used.
- **Image tokens**: RGB patches concatenated with Plücker ray patches, then linearly projected.

### Update Block

Each of the L layers applies

```text
Ṽ_i = cross-attn(V_i, S_i)          # per-view: viewpoint tokens attend to their own image tokens
{V_i} = self-attn({Ṽ_i})            # global: viewpoint tokens attend to each other
```

Update blocks use **separate parameters per layer**. The paper contrasts standard self-attention `S⁽ˡ⁾ = S⁽ˡ⁻¹⁾ + f(S⁽ˡ⁻¹⁾)` with its evidence-conditioned update `V⁽ˡ⁾ = V⁽ˡ⁻¹⁾ + F(V⁽ˡ⁻¹⁾, S)`, where image tokens S are fixed.

### Token Uplifting

Low-resolution viewpoint tokens are expanded by a linear query layer by factor k, so each token becomes k finer-grained queries for cross-attention against high-resolution image tokens, then projected back. The paper sets **k = 2**.

### Relative Computational Cost

원논문 본문. 16 input images at 256×256 with patch size 8, comparing Fig. 2-(a) full attention, (b) decoupling, (c) reduced viewpoint resolution, (d) two-stage attention: the relative cost ratio is **1 : 1 : 0.25 : 0.08**.

### Implementation

- 12 update layers (one cross-attention + one self-attention each)
- Hidden dimension d = 768, patch size p = 8, 12-head attention
- Pre-normalization with LayerNorm, QK-Norm with RMSNorm, GELU MLPs
- Loss: MSE + perceptual loss on held-out target views, with λ = 0.5

### Notation

Configurations are written `(V, H/F, F)`: V viewpoints, viewpoint-token resolution (H = half, F = full), image-token resolution. `MC` denotes the quarter mini-batch cross-attention variant.

## 📊 Results

### RealEstate10K

원논문 Table 1. Inference time measured on an RTX 4090. `*` marks a closed-source method (GS-LRM), for which no time is reported.

| Method             | #Param (M) | PSNR ↑ | SSIM ↑ | LPIPS ↓ | # Gaussians | Time (s) |
| ------------------ | ---------- | ------ | ------ | ------- | ----------- | -------- |
| pixelSplat         | 125        | 25.89  | 0.858  | 0.142   | 131,072     | 0.101    |
| MVSplat            | 12         | 26.39  | 0.869  | 0.128   | 131,072     | 0.047    |
| GS-LRM\*           | 300        | 28.10  | 0.892  | 0.114   | 131,072     | -        |
| DepthSplat         | 354        | 27.47  | 0.889  | 0.114   | 131,072     | 0.065    |
| Gen-Den            | 28         | 27.08  | 0.879  | 0.120   | 347,072     | 0.224    |
| Ours (2, F, F)     | 171        | 28.65  | 0.900  | 0.110   | 131,072     | 0.025    |
| Ours (4, H, F)     | 185        | 30.37  | 0.923  | 0.095   | 65,536      | 0.027    |
| Ours-MC (4, H, F)  | 185        | 30.10  | 0.919  | 0.098   | 65,536      | 0.027    |
| **Ours (8, H, F)** | 185        | 31.57  | 0.935  | 0.082   | 131,072     | 0.028    |
| Ours-MC (8, H, F)  | 185        | 31.24  | 0.933  | 0.084   | 131,072     | 0.029    |

### Cross-Dataset Generalization (trained on RE10K)

원논문 Table 2. ACID and DL3DV at 256×256.

| Method             | ACID PSNR ↑ | ACID SSIM ↑ | ACID LPIPS ↓ | DL3DV PSNR ↑ | DL3DV SSIM ↑ | DL3DV LPIPS ↓ |
| ------------------ | ----------- | ----------- | ------------ | ------------ | ------------ | ------------- |
| MVSplat            | 28.15       | 0.841       | 0.147        | 22.65        | 0.737        | 0.191         |
| DepthSplat         | 28.37       | 0.847       | 0.141        | 24.28        | 0.813        | 0.147         |
| Gen-Den            | 28.61       | 0.847       | 0.141        | 22.92        | 0.750        | 0.188         |
| Ours (2, F, F)     | 29.24       | 0.856       | 0.143        | 25.35        | 0.826        | 0.144         |
| Ours (4, H, F)     | 30.10       | 0.877       | 0.138        | 27.90        | 0.877        | 0.122         |
| Ours-MC (4, H, F)  | 29.90       | 0.873       | 0.141        | 27.68        | 0.881        | 0.127         |
| **Ours (8, H, F)** | 30.96       | 0.894       | 0.122        | 29.56        | 0.907        | 0.101         |
| Ours-MC (8, H, F)  | 30.72       | 0.890       | 0.125        | 29.33        | 0.904        | 0.102         |

### DL3DV, 50-Frame Baseline (256×448)

원논문 Table 3. Time and memory on an RTX 4090.

| Method     | Views | PSNR ↑ | SSIM ↑ | LPIPS ↓ | # Gaussians | Time (s) | Memory (GB) |
| ---------- | ----- | ------ | ------ | ------- | ----------- | -------- | ----------- |
| MVSplat    | 6     | 22.93  | 0.775  | 0.193   | 688,128     | 0.279    | 5.87        |
| DepthSplat | 6     | 24.19  | 0.823  | 0.147   | 688,128     | 0.102    | 3.55        |
| DepthSplat | 11    | 24.28  | 0.833  | 0.141   | 1,261,568   | 0.170    | 6.01        |
| DepthSplat | 24    | 22.37  | 0.781  | 0.195   | 2,752,512   | 0.371    | 12.39       |
| Ours       | 6     | 25.60  | 0.830  | 0.168   | 172,032     | 0.031    | 1.40        |
| Ours       | 11    | 26.99  | 0.865  | 0.140   | 315,392     | 0.051    | 1.59        |
| **Ours**   | 24    | 27.38  | 0.882  | 0.126   | 688,128     | 0.123    | 2.01        |

### DL3DV, 100-Frame Baseline (512×960)

원논문 Table 4. DepthSplat runs out of memory on the RTX 4090, so it was evaluated on an H100 instead and its time is not reported.

| Method     | Views | PSNR ↑ | SSIM ↑ | LPIPS ↓ | # Gaussians | Time (s) | Memory (GB) |
| ---------- | ----- | ------ | ------ | ------- | ----------- | -------- | ----------- |
| DepthSplat | 12    | 21.38  | 0.739  | 0.265   | 5,898,240   | -        | OOM         |
| **Ours**   | 12    | 24.35  | 0.781  | 0.256   | 1,474,560   | 0.415    | 3.53        |

### Undistorted DL3DV, Wide Coverage (540×960)

원논문 Table 5. FlashAttention v3 on an H100. `Long-LRM10` / `Ours10` denote 10 epochs of finetuning initialized from the feed-forward output. 40- and 48-view rows are zero-shot for a model trained with 32 views. Long-LRM was re-evaluated from its official checkpoint except at 16 views, where weights are unreleased.

| Method            | Views | Time ↓  | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ----------------- | ----- | ------- | ------ | ------ | ------- |
| 3D-GS             | 16    | 8min    | 21.48  | 0.753  | 0.252   |
| Long-LRM          | 16    | 0.50sec | 22.66  | 0.740  | 0.292   |
| Ours              | 16    | 0.19sec | 22.91  | 0.766  | 0.295   |
| 3D-GS             | 32    | 8min    | 24.43  | 0.827  | 0.191   |
| Long-LRM          | 32    | 0.84sec | 23.97  | 0.778  | 0.267   |
| Ours              | 32    | 0.53sec | 24.30  | 0.803  | 0.256   |
| Long-LRM10        | 32    | 11sec   | 25.56  | 0.826  | 0.237   |
| **Ours10**        | 32    | 4.5sec  | 25.67  | 0.844  | 0.230   |
| Long-LRM (Unseen) | 40    | 1.05sec | 24.18  | 0.787  | 0.260   |
| Ours (Unseen)     | 40    | 0.76sec | 24.54  | 0.811  | 0.248   |
| Long-LRM (Unseen) | 48    | 1.38sec | 24.30  | 0.797  | 0.252   |
| Ours (Unseen)     | 48    | 1.04sec | 24.78  | 0.820  | 0.240   |

Note the honest reading of this table: at 16 and 32 views the feed-forward iLRM has **worse LPIPS than 3D-GS** (0.295 vs 0.252 at 16 views; 0.256 vs 0.191 at 32 views), and at 32 views 3D-GS also wins on PSNR and SSIM. The paper's own framing is that at 540×960 with 32 views iLRM finishes in 0.5 seconds versus about 8 minutes for the optimization-based approach with comparable performance.

### Ablation: Model Size

원논문 Table 6. Trained under (4, H, F) on RE10K, batch size 16.

| Variant              | # Params | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| -------------------- | -------- | ------ | ------ | ------- |
| **12 layers (base)** | 185M     | 29.24  | 0.907  | 0.109   |
| 9 layers             | 139M     | 29.01  | 0.903  | 0.112   |
| 6 layers             | 94M      | 28.68  | 0.898  | 0.116   |
| 3 layers             | 48M      | 28.04  | 0.887  | 0.126   |

### Ablation: Architecture

원논문 Table 7.

| Variant                   | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------------------------- | ------ | ------ | ------- |
| **Baseline (12 layers)**  | 29.24  | 0.907  | 0.109   |
| w/o iter. refinement      | 28.58  | 0.893  | 0.127   |
| w/o resolution decoupling | 28.47  | 0.891  | 0.123   |
| w/o token uplifting       | 28.90  | 0.901  | 0.113   |

### Mini-Batch Cross-Attention (Training Cost)

원논문 Table 8. RE10K, (8, H, F), batch size 16; iteration time on a single RTX 4090, memory without gradient checkpointing on a single H100.

| Method                | PSNR ↑ | SSIM ↑ | LPIPS ↓ | Iteration (s) | Memory (GB) | GFLOPs |
| --------------------- | ------ | ------ | ------- | ------------- | ----------- | ------ |
| Baseline              | 30.39  | 0.923  | 0.095   | 1.51          | 62.5        | 3.83   |
| w/ Half Cross-attn    | 30.25  | 0.922  | 0.096   | 1.13          | 47.4        | 1.71   |
| w/ Quarter Cross-attn | 30.08  | 0.919  | 0.098   | 0.94          | 39.0        | 0.81   |

Quarter cross-attention is the default in the experiments; it costs 0.31 PSNR against the baseline while cutting GFLOPs and memory substantially.

### Attention Visualization

Fig. 8 visualizes the top-3 attended tokens for three query patches across layers. This is a qualitative figure with no printed values; the reported observation is that attended tokens progressively shift toward geometrically and semantically corresponding regions in deeper layers.

## 💡 Insights & Impact

### Why Decoupling Matters

The paper's opening argument is concrete: 200 views at 1K resolution produce 200 million pixel-aligned Gaussians, while prior work shows comparable scenes can be represented with roughly 0.5 million. Pixel-aligned prediction ties representation size to an input property that has nothing to do with scene complexity. iLRM breaks that tie, and the Gaussian counts in Tables 3 and 4 show the practical consequence — at the 100-frame setting iLRM uses 1.47M Gaussians where DepthSplat needs 5.90M.

### Iteration as Optimization

The reframing of a stack of cross-attention layers as an unrolled optimizer is the conceptual core. The ablation supports it: replacing per-layer cross-attention with a single first-layer cross-attention followed by 23 self-attention layers (matched depth) costs 0.66 PSNR and, notably, degrades LPIPS the most (0.109 → 0.127). Repeated contact with the image evidence, not extra depth, is what buys the perceptual quality.

### Limitations Stated by the Authors

1. **Self-attention bottleneck across views**: compact viewpoint embeddings reduce but do not remove the cost of global self-attention as view count grows considerably.
2. **Reliance on accurate camera poses** in static scenarios.
3. **Geometry may be less accurate** than explicitly geometry-supervised methods, since supervision is rendering-based novel view synthesis.

## 🔗 Related Work

- [VGGT](./vggt.md) — unified feed-forward geometry transformer; iLRM cites it and shares the "one forward pass" ambition, but targets Gaussian-based novel view synthesis rather than pointmaps.
- [DUSt3R](../foundation/dust3r.md) — cited as an explicitly geometry-supervised method, the class iLRM notes may recover more accurate geometry.
- [MapAnything](./mapanything.md), [Depth Anything 3](./depth-anything-3.md) — contemporaneous feed-forward geometry models with the opposite supervision emphasis.
- [Fast3R](./fast3r.md) — another attack on the quadratic multi-view attention cost, but by scaling global attention rather than decoupling the representation.
- [Pi3](./pi3.md), [MUSt3R](./must3r.md) — alternative routes to many-view scalability.

## 📚 Key Takeaways

1. **Representation size should be a design choice, not a side effect of input resolution.** Decoupling viewpoint tokens from image tokens is what makes everything else in iLRM affordable.
2. **Cheap two-stage attention beats full attention here.** Per-view cross-attention plus low-resolution global self-attention reaches a stated relative cost of 0.08 against full attention in the 16-view 256×256 setting.
3. **Feedback beats depth.** Ablations show per-layer re-contact with image evidence matters more than simply stacking self-attention.
4. **Feed-forward has not fully caught optimization.** At 32 wide-coverage views 3D-GS still wins on all three metrics; iLRM's claim is comparable quality at 0.5 seconds versus roughly 8 minutes, and finetuning for 10 epochs is what pushes it past Long-LRM10.

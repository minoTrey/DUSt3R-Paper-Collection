# HiReFF: High-Resolution Feedforward Human Reconstruction from Uncalibrated Sparse-View Video (arXiv preprint (2026-06))

![hireff — architecture](https://arxiv.org/html/2606.29333v1/x4.png)

_More visualization results (원논문 Fig. 4)_

## 📋 Overview

- **Authors**: Yiming Jiang, Hanzhang Tu, Wenfeng Song, Siyou Lin, Liang An, Shuai Li, Aimin Hao, Yebin Liu
- **Institution**: State Key Laboratory of Virtual Reality Technology and Systems, Beihang University; Tsinghua University; Beijing Information Science and Technology University; Zhongguancun Laboratory
- **Venue**: arXiv preprint (2026-06)
- **Links**: [Paper](https://arxiv.org/abs/2606.29333) | [Project Page](https://iridescentjiang.github.io/HiReFF)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward framework for 2K-resolution 360° human volumetric video reconstruction from four uncalibrated 90°-spaced videos, keeping a VGGT backbone at 0.5K while side-tuning the Gaussian head for high-resolution output — streaming at 3.01 FPS on a single RTX 4090.

## 🎯 Key Contributions

1. **HiReFF framework**: The first feed-forward method for high-resolution (2K) 360° human video reconstruction from uncalibrated sparse-view videos (four views 90° apart), decomposing the problem into foreground 3D Gaussian reconstruction and efficient high-resolution synthesis.
2. **Scale-synchronized Camera Calibration**: Resolves metric-scale ambiguity so that additional novel viewpoints can supervise training, by freezing the camera head and indirectly optimizing it through the AA Transformer while rescaling ground-truth translations to match the model's scale.
3. **Gaussian-wise Foreground Masking**: A mask head modulates Gaussian parameters to reconstruct a clean foreground human while feeding full images (preserving camera-estimation accuracy under wide 90° baselines).
4. **High-resolution Side-tuning**: Augments the Gaussian head with supplementary high-resolution image features while keeping the AA Transformer input at 518×518, enabling 2K rendering with modest overhead.

## 🔧 Technical Details

### Backbone and heads

- Built on **VGGT** (Alternating-Attention Transformer): the AA Transformer, camera head, and both active and frozen depth heads are initialized with pretrained VGGT weights; the 3D Gaussian prediction head, side-tuning supplementary network, and mask head are zero-initialized.
- Following **AnySplat**, a DPT Gaussian head decodes AA features into 3DGS parameters. Side-tuning fuses image-derived MLP features `F_a(I)` with intermediate Gaussian-head features `F_G^mid`; Gaussian positions come from depth-head back-projection with predicted camera parameters (per-pixel alignment).

### Scale-synchronized Camera Calibration

- Under 90° baselines the camera head fluctuates and input-view-only supervision is insufficient. HiReFF freezes the camera head and renders with ground-truth camera parameters (for both input and extra supervision views), rescaling GT translations by the mean ratio `s̄` of predicted-to-GT translation so they match the (scale-free) predicted geometry, while the AA Transformer still adjusts features into the camera head (indirect supervision).

### High-resolution Side-tuning

- High-resolution quality depends mainly on Gaussian appearance attributes `Θ_g`, not on positions or camera pose. High-res images go to the supplementary network `F_a`; low-res (518×518) images go to the AA Transformer; intermediate features are upsampled and fused before `F_D`. `F_a` is an MLP modified from EdgeNeXt.

### Training

- Losses: rendering loss (L1 + patch-wise perceptual/VGG loss over `4 + V_a` views), mask L1 loss over the 4 input views, and a depth distillation MSE against a frozen VGGT-initialized depth head.
- Trained mainly on DNA-Rendering (153 actors, 439 motion sequences, 48-view 2448×2048), plus ZJU-MoCap and MVHumanNet; validation on 20 held-out DNA-Rendering sequences.
- `V_a = 4` (8 total supervision views), HR = 2072×2072, LR = 518×518, gsplat renderer, 8× A800 GPUs, mixed precision. Loss weights `λ_P = 0.1`, `λ_render = 1.0`, `λ_mask = 5×10⁻²`, `λ_depth = 10¹`.

## 📊 Results

Novel-view synthesis evaluated at 2072×2072 under a 4-view input setting with ~90° separation. NoPoSplat/AnySplat had their cameras optimized 200 steps ("Aligned" ✓); HiReFF aligns without any test-time optimization. GPS-Gaussian receives 8 calibrated views and pre-segmented foregrounds.

### Novel-view synthesis quality

원논문 Table 1. Cam. Pose = 카메라 포즈 입력 필요 여부, Views Num. = 입력 뷰 수, Aligned = 테스트타임 카메라 최적화 여부. 지표는 PSNR↑, SSIM↑, LPIPS↓.

| Method       | Cam. Pose | Views | Aligned | PSNR ↑      | SSIM ↑     | LPIPS ↓    |
| ------------ | --------- | ----- | ------- | ----------- | ---------- | ---------- |
| GPS-Gaussian | ✓         | 8     | –       | 26.1039     | **0.9172** | 0.1384     |
| 4DGT         | ✗         | 1     | ✗       | 17.1689     | 0.8395     | 0.2719     |
| NoPoSplat    | ✗         | 2     | ✗       | 22.6296     | 0.8876     | 0.1736     |
| NoPoSplat    | ✗         | 2     | ✓       | 23.4321     | 0.8939     | 0.1588     |
| AnySplat     | ✗         | 4     | ✗       | 23.7844     | 0.9040     | 0.1737     |
| AnySplat     | ✗         | 4     | ✓       | 25.5875     | 0.9140     | 0.1598     |
| **Ours**     | ✗         | 4     | ✗       | **26.5138** | 0.9164     | **0.1277** |

HiReFF outperforms all uncalibrated methods on every metric. Versus the directly comparable AnySplat (unoptimized), it improves PSNR by 2.7294, SSIM by 0.0124, and reduces LPIPS by 0.0460. Against the calibrated GPS-Gaussian (8 views, GT cameras, masked input) it wins on PSNR and LPIPS but is marginally lower on SSIM (0.9164 vs 0.9172); the paper notes GPS-Gaussian's metric edge partly stems from masked-input evaluation.

### Inference cost (single RTX 4090)

원논문 Table 2b. In. Res. = 입력 해상도, Ren. Res. = 렌더 해상도, VRAM(MiB), Frame Rate.

| In. Res. | Ren. Res. | VRAM (MiB) | Frame Rate |
| -------- | --------- | ---------- | ---------- |
| 518      | 2072      | 10852      | 4.40 FPS   |
| 1036     | 2072      | 10886      | 4.02 FPS   |
| 2072     | 2072      | 14052      | 3.01 FPS   |

At 2K rendering HiReFF reaches 3.01 FPS, only 24% lower than the 4.40 FPS at 0.5K input; using 1K input reduces speed by merely 8.6% versus 0.5K when both render at 2K.

### Training cost and side-tuning

원논문 Table 2a. 학습 시 입력/감독 해상도별 VRAM(MiB). Side-tuning 없이 2K 입력은 OOM.

| In. Res. | Sup. Res. | Side-tuning | VRAM (MiB) |
| -------- | --------- | ----------- | ---------- |
| 518      | 518       | ✓           | 40503      |
| 518      | 2072      | ✓           | 44125      |
| 2072     | 2072      | ✓           | 59095      |
| 2072     | 2072      | ✗           | OOM        |

With 2K input and 2K supervision, side-tuning increases VRAM by only 33.9% versus 0.5K input/supervision; directly raising the AA Transformer input resolution without side-tuning exceeds 80 GB VRAM (out-of-memory).

## 💡 Insights & Impact

- **High resolution without a heavy backbone**: Because high-res quality is carried by Gaussian appearance attributes rather than backbone features, keeping the AA Transformer at 518×518 and side-tuning the Gaussian head is a cheap route to 2K rendering.
- **Masking vs camera estimation trade-off**: Directly masking inputs degrades camera prediction under wide baselines; deferring foreground selection to a Gaussian-wise mask head keeps camera accuracy while yielding a clean human.
- **Uncalibrated streaming**: HiReFF simultaneously addresses uncalibrated sparse-view input, streaming video reconstruction, and 2K 360° rendering — a combination not previously handled together.
- **Limitations**: Regions occluded from multiple viewpoints (e.g., captured by only the frontal view) leave a few isolated points; future work aims to add hand/face human priors.

## 🔗 Related Work

- Directly builds on the feed-forward reconstruction backbone [VGGT](../reconstruction/vggt.md) and the feed-forward Gaussian head of AnySplat, and cites [DUSt3R](../foundation/dust3r.md), FLARE, MapAnything, and [Pi3](../reconstruction/pi3.md) as uncalibrated pose+pointmap regressors (Pi3 extends to relative coordinate systems).
- Positioned against uncalibrated Gaussian methods NoPoSplat and AnySplat, the monocular volumetric method 4DGT, and calibrated GPS-Gaussian; related to human-specific feed-forward avatars (IDOL, LHM, Human3R, FastAvatar) and Forge4D (frontal uncalibrated human NVS).
- The high-resolution NVS component relates to SRGS and GaussianSR super-resolution, adapted here via side-tuning into a feed-forward 3DGS pipeline.

## 📚 Key Takeaways

1. HiReFF reconstructs 2K 360° human volumetric video from four uncalibrated 90°-spaced videos in a single feed-forward pass, streaming at 3.01 FPS on one RTX 4090.
2. Scale-synchronized Camera Calibration and Gaussian-wise Foreground Masking resolve the scale-ambiguity and masking-vs-camera conflicts specific to wide-baseline uncalibrated human capture.
3. High-resolution Side-tuning delivers 2K output with only ~34% extra training VRAM by keeping the VGGT backbone at 0.5K, outperforming uncalibrated baselines across PSNR/SSIM/LPIPS.

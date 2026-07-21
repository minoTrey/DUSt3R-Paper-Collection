# WildSplat: Feedforward Gaussian Splatting from Unposed In-the-Wild Images (ECCV 2026)

## 📋 Overview

- **Authors**: Xiyu Zhang, Jingyu Zhuang, Hongjia Zhai, Zizheng Yan, Jinwei Chen, Guofeng Zhang, Qingnan Fan
- **Institution**: State Key Lab of CAD&CG, Zhejiang University, China; vivo BlueImage Lab, China
- **Venue**: ECCV 2026
- **Links**: [Paper](https://arxiv.org/abs/2607.05347)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: The first feedforward 3DGS framework for appearance-conditioned novel-view synthesis from unposed in-the-wild images, using a dual-branch architecture that decouples appearance-invariant geometry from a reference-conditioned appearance injected via globally pre-modulated cross-attention.

(Xiyu Zhang and Jingyu Zhuang contributed equally; Guofeng Zhang and Qingnan Fan are corresponding authors.)

## 🎯 Key Contributions

1. **First in-the-wild feedforward 3DGS**: Appearance-conditioned novel-view synthesis from sparse, unposed, photometrically inconsistent image collections in a single forward pass.
2. **Dual-branch geometry/appearance decoupling**: A geometry branch extracts appearance-invariant 3D structure and predicts camera poses; an appearance branch injects target appearance from a reference image.
3. **Globally pre-modulated cross-attention**: An AdaLN-Zero layer uses the reference [CLS] token to pre-modulate content features into the target appearance domain before cross-attention with reference tokens.
4. **Multi-reference training + geometry-guided view sampling**: A joint multi-reference paradigm renders one geometry under multiple appearance conditions per batch, and an overlap/scale-based sampling algorithm selects valid in-the-wild context views.

## 🔧 Technical Details

### Geometry Branch

Built on a VGGT-like architecture: N context images are encoded by a DINOv2-large encoder (D = 1024), camera tokens are concatenated, and features pass through L = 24 alternating-attention layers. Multi-scale "content features" are aggregated from a subset of layers and fed to DPT-based heads that predict depth, Gaussian attributes {s, q, α}, and (via the camera head) poses; centers µ come from back-projection. The result is illumination-agnostic geometry G = {µ, s, q, α}.

### Appearance Branch

A separate DINOv2-base appearance encoder extracts a global [CLS] token and dense reference tokens from Iref. Content features act as queries; reference tokens as keys/values. Before cross-attention, an AdaLN-Zero layer decodes the [CLS] token into (γ, β, η) that modulate content features, followed by cross-attention, self-attention, and MLP. The resulting appearance features drive a color head producing reference-conditioned SH color Cref, combined with G for conditioned rasterization.

### Training

Two-stage on four RTX H20 GPUs: a 30k-iteration warm-up on DL3DV (appearance injector disabled), then 60k iterations end-to-end on DL3DV + MegaScenes + MegaDepth, with DL3DV augmented into 5 lighting conditions via a video relighting model. Loss: L = Lrgb + λ1·Lpose, where Lrgb = λ2·LMSE + λ3·LSSIM + λ4·LLPIPS, with weights {10, 1.0, 0.05, 0.05} (and λ1 = 10 pose distillation).

## 📊 Results

Evaluated under 4/8/12-view sparse configurations with the NeRF-W half-image protocol (left half = reference, metrics on right half). Optimization-based baselines get camera/point-cloud priors from VGGT. Metrics: PSNR↑, SSIM↑, LPIPS↓.

### MegaScenes

원논문 Table 1.

| Method       | 4v PSNR↑  | 4v SSIM↑  | 4v LPIPS↓ | 8v PSNR↑  | 8v SSIM↑  | 8v LPIPS↓ | 12v PSNR↑ | 12v SSIM↑ | 12v LPIPS↓ |
| ------------ | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | ---------- |
| FSGS         | 12.88     | 0.352     | 0.463     | 13.28     | 0.371     | 0.454     | 13.43     | 0.376     | 0.453      |
| GS-W         | 9.54      | 0.265     | 0.539     | 10.76     | 0.294     | 0.500     | 9.81      | 0.311     | 0.526      |
| WildGaussian | 14.38     | 0.385     | 0.458     | 15.32     | 0.436     | 0.433     | 15.68     | 0.448     | 0.452      |
| AnySplat     | 14.58     | 0.559     | 0.313     | 16.16     | 0.594     | 0.274     | 16.31     | 0.601     | 0.273      |
| WorldMirror  | 15.33     | 0.609     | 0.288     | 16.08     | 0.633     | 0.281     | 16.05     | 0.629     | 0.287      |
| **Ours**     | **17.91** | **0.635** | **0.235** | **18.65** | **0.668** | **0.218** | **19.20** | **0.683** | **0.210**  |

### Phototourism

원논문 Table 2.

| Method       | 4v PSNR↑  | 4v SSIM↑  | 4v LPIPS↓ | 8v PSNR↑  | 8v SSIM↑  | 8v LPIPS↓ | 12v PSNR↑ | 12v SSIM↑ | 12v LPIPS↓ |
| ------------ | --------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- | ---------- |
| FSGS         | 13.63     | 0.476     | 0.413     | 14.85     | 0.532     | 0.366     | 15.39     | 0.573     | 0.346      |
| GS-W         | 9.40      | 0.344     | 0.512     | 10.19     | 0.354     | 0.490     | 12.63     | 0.399     | 0.437      |
| WildGaussian | 14.95     | 0.485     | 0.436     | 17.02     | 0.567     | 0.371     | 17.65     | 0.616     | 0.353      |
| AnySplat     | 15.61     | 0.616     | 0.279     | 17.35     | 0.681     | 0.240     | 18.00     | 0.700     | 0.228      |
| WorldMirror  | 15.38     | 0.664     | 0.273     | 16.71     | 0.699     | 0.252     | 17.24     | 0.724     | 0.234      |
| **Ours**     | **19.57** | **0.727** | **0.178** | **21.15** | **0.771** | **0.146** | **21.47** | **0.788** | **0.137**  |

### Ablation on Phototourism

원논문 Table 3.

| Setting                   | 4v PSNR↑ | 4v LPIPS↓ | 8v PSNR↑ | 8v LPIPS↓ | 12v PSNR↑ | 12v LPIPS↓ |
| ------------------------- | -------- | --------- | -------- | --------- | --------- | ---------- |
| w/o Multi-Ref Supervision | 16.88    | 0.221     | 18.77    | 0.184     | 19.35     | 0.177      |
| w/o Geo-guided Sampling   | 17.99    | 0.220     | 19.24    | 0.192     | 19.58     | 0.182      |
| w/o Pre-Modulation        | 18.25    | 0.226     | 19.70    | 0.189     | 20.11     | 0.175      |
| Full                      | 18.52    | 0.212     | 19.90    | 0.180     | 20.15     | 0.169      |

### Pose Evaluation on MegaScenes (24 views, 20 scenes)

원논문 Table 4.

| Method   | AUC@5↑    | AUC@10↑   | AUC@30↑   | ATE↓      |
| -------- | --------- | --------- | --------- | --------- |
| VGGT     | **0.314** | **0.451** | **0.632** | **1.525** |
| AnySplat | 0.249     | 0.392     | 0.596     | 1.564     |
| Ours     | 0.310     | 0.443     | 0.624     | 1.559     |

### DL3DV (consistent illumination, supplementary)

원논문 Table A.

| Method   | 6v PSNR↑  | 6v SSIM↑  | 6v LPIPS↓ | 12v PSNR↑ | 12v SSIM↑ | 12v LPIPS↓ | 24v PSNR↑ | 24v SSIM↑ | 24v LPIPS↓ |
| -------- | --------- | --------- | --------- | --------- | --------- | ---------- | --------- | --------- | ---------- |
| AnySplat | 20.33     | 0.643     | 0.154     | 19.73     | 0.603     | 0.187      | 19.55     | 0.589     | 0.202      |
| Ours     | **22.37** | **0.752** | **0.131** | **21.10** | **0.686** | **0.167**  | **20.67** | **0.666** | **0.185**  |

## 💡 Insights & Impact

- **Decoupling beats entanglement**: On both MegaScenes and Phototourism, WildSplat leads every metric at every view count, e.g., +4.24 dB PSNR over WorldMirror at Phototourism 4 views (19.57 vs. 15.33).
- **Multi-reference supervision is the key stabilizer**: Its removal causes the largest ablation drop (Phototourism 4-view PSNR 18.52 → 16.88), confirming that rendering one geometry under multiple appearances prevents geometry–appearance entanglement.
- **Pose accuracy without a dedicated pose model**: The geometry branch's poses beat AnySplat on all AUC metrics and approach the dedicated VGGT prior, though VGGT remains best on both AUC and ATE.
- **Negligible overhead**: For 16-view input WildSplat uses 1.3 s / 9.6 GB vs. AnySplat's 1.1 s / 8.2 GB, and at 128 frames memory is nearly identical (45.6 GB vs. 45.7 GB).
- **Honest limits**: It struggles with highly localized, spatially varying illumination (projected light can bleed into nearby surfaces), and memory scales with resolution and context count.

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**: Foundational pose-free geometry reconstruction underpinning the feedforward line.
- **[VGGT](../reconstruction/vggt.md)**: The backbone architecture of WildSplat's geometry branch and the pose prior it compares against.
- **[WorldMirror](../reconstruction/worldmirror.md)**: A feedforward baseline compared on both in-the-wild datasets.

## 📚 Key Takeaways

1. WildSplat is the first feedforward 3DGS method for appearance-conditioned NVS from unposed in-the-wild images, decoupling illumination-invariant geometry from reference-conditioned appearance.
2. Its dual-branch design with globally pre-modulated cross-attention and multi-reference training achieves state-of-the-art results over both feedforward (AnySplat, WorldMirror) and optimization-based (WildGaussian, GS-W, FSGS) baselines on MegaScenes and Phototourism.
3. Beyond synthesis it enables appearance editing/interpolation by swapping the reference image, all in a single forward pass with efficiency comparable to AnySplat.

# VIST3A: Text-to-3D by Stitching a Multi-view Reconstruction Network to a Video Generator (ICLR 2026)

![vist3a — architecture](https://arxiv.org/html/2510.13454v2/x1.png)

_Text-to-3D generation with VIST3A (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Hyojun Go, Dominik Narnhofer, Goutam Bhat, Prune Truong, Federico Tombari, Konrad Schindler
- **Institution**: ETH Zurich, Google
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2510.13454) | [Project Page](https://gohyojun15.github.io/VIST3A/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A general framework that stitches a pretrained text-to-video generator ("generator") to a feed-forward 3D reconstruction network ("decoder") by matching latents, then aligns the video model with reward finetuning to produce text-to-3DGS or text-to-pointmap output.

## 🎯 Key Contributions

1. **Model stitching for 3D generation**: Identifies the layer in the 3D decoder whose latent representation best matches the text-to-video generator's output and stitches the two parts together, requiring only a small dataset and no labels.
2. **Reward-based alignment**: Adapts direct reward finetuning (a human-preference alignment technique) so that generated latents decode into consistent, perceptually convincing 3D geometry, using CLIP and HPSv2 scores plus a 3D-consistency reward term that needs only text prompts, no ground-truth images.
3. **Model-agnostic pairing**: Demonstrated with multiple video generators (Wan, Hunyuan, SVD, CogVid) and 3D decoders (MVDUSt3R, AnySplat, VGGT); all tested pairings improve over prior text-to-3DGS models.
4. **Text-to-pointmap generation**: By choosing a suitable 3D base model (e.g. VGGT), the same framework enables high-quality text-to-pointmap output, not only Gaussian splats.

## 🔧 Technical Details

### Stitching

The core idea is to reuse the rich knowledge in the pretrained weights of both components rather than train from scratch. The method revisits model stitching: it searches over decoder layers (using a log-MSE alignment objective, Eq. 2) to find the layer whose latent best matches the video generator's latent, then joins generator and decoder at that point.

### Reward finetuning

Because the stitched decoder is frozen and only the generator is aligned, VIST3A uses direct reward finetuning conditioned on the text prompt `c`. Three reward families are combined: (1) CLIP + HPSv2 scores on generated images for prompt adherence and visual quality, (2) the same metrics applied to views rendered back from the 3D output, and (3) a 3D-consistency reward. Reward propagation is stabilized across denoising states so it remains usable even at early denoising steps.

### Outputs

Depending on the chosen 3D decoder, VIST3A produces either 3D Gaussian splats (Text-to-3DGS) or point maps (Text-to-Pointmap) from a text prompt in an end-to-end model.

## 📊 Results

### Text-to-3DGS on T3Bench (object-centric)

원논문 Table 1. All metrics higher is better.

| Method                 | Imaging↑ | Aesthetic↑ | CLIP↑ | Align.↑ | Coher.↑ | Style↑ |
| ---------------------- | -------- | ---------- | ----- | ------- | ------- | ------ |
| Matrix3D-omni          | 43.05    | 37.66      | 25.06 | 2.44    | 3.10    | 2.69   |
| Director3D             | 54.32    | 53.33      | 30.94 | 3.25    | 3.43    | 3.05   |
| Prometheus3D           | 47.46    | 44.32      | 29.15 | 2.84    | 3.12    | 2.66   |
| SplatFlow              | 46.09    | 53.24      | 29.48 | 3.29    | 3.25    | 2.93   |
| VideoRFSplat           | 46.52    | 39.50      | 30.13 | 3.12    | 3.24    | 3.09   |
| VIST3A: Wan + MVDUSt3R | 58.83    | 56.55      | 32.75 | 3.56    | 3.89    | 3.56   |
| VIST3A: Wan + AnySplat | 57.03    | 54.11      | 31.38 | 3.36    | 3.68    | 3.17   |

### Text-to-3DGS on SceneBench (scene-level)

원논문 Table 1. All metrics higher is better.

| Method                 | Imaging↑ | Aesthetic↑ | CLIP↑ | Align.↑ | Coher.↑ | Style↑ |
| ---------------------- | -------- | ---------- | ----- | ------- | ------- | ------ |
| Matrix3D-omni          | 46.65    | 37.62      | 24.04 | 2.66    | 3.29    | 2.80   |
| Director3D             | 47.79    | 52.81      | 29.31 | 3.36    | 3.67    | 3.20   |
| Prometheus3D           | 44.73    | 45.85      | 28.57 | 3.20    | 3.36    | 2.98   |
| SplatFlow              | 48.85    | 53.71      | 29.43 | 3.47    | 3.65    | 3.26   |
| VideoRFSplat           | 58.19    | 51.71      | 29.76 | 3.58    | 3.63    | 3.30   |
| VIST3A: Wan + MVDUSt3R | 62.08    | 55.67      | 30.26 | 3.72    | 3.97    | 3.47   |
| VIST3A: Wan + AnySplat | 64.87    | 56.96      | 30.18 | 3.67    | 3.86    | 3.40   |

### DPG-Bench (long, detailed prompts)

원논문 Table 2. All metrics higher is better.

| Method                 | Global↑ | Entity↑ | Attribute↑ | Relation↑ | Other↑ |
| ---------------------- | ------- | ------- | ---------- | --------- | ------ |
| Matrix3D-omni          | 53.32   | 42.44   | 56.23      | 37.12     | 10.32  |
| Director3D             | 66.67   | 64.96   | 60.85      | 45.15     | 22.73  |
| Prometheus3D           | 45.45   | 48.35   | 55.03      | 33.50     | 9.10   |
| SplatFlow              | 69.70   | 68.43   | 65.55      | 50.49     | 40.91  |
| VideoRFSplat           | 36.36   | 56.93   | 66.89      | 48.53     | 31.82  |
| VIST3A: Wan + MVDUSt3R | 81.82   | 84.31   | 86.13      | 68.93     | 54.55  |
| VIST3A: Wan + AnySplat | 78.79   | 85.58   | 84.12      | 76.70     | 45.45  |

### Novel view synthesis on RealEstate10K

원논문 Table 3. Stitching a video generator onto AnySplat.

| Method             | PSNR↑ | SSIM↑ | LPIPS↓ |
| ------------------ | ----- | ----- | ------ |
| SplatFlow          | 19.10 | 0.671 | 0.278  |
| VideoRFSplat       | 19.05 | 0.674 | 0.281  |
| Prometheus3D       | 19.56 | 0.683 | 0.277  |
| AnySplat           | 20.85 | 0.695 | 0.238  |
| Hunyuan + AnySplat | 21.17 | 0.710 | 0.242  |
| SVD + AnySplat     | 21.48 | 0.720 | 0.218  |
| CogVid + AnySplat  | 21.32 | 0.716 | 0.222  |
| Wan + AnySplat     | 21.29 | 0.718 | 0.232  |

### User study (average rank, lower is better)

원논문 Table 4.

| Method                | Text Alignment (Avg. Rank ↓) | Visual Quality (Avg. Rank ↓) |
| --------------------- | ---------------------------- | ---------------------------- |
| Director3D            | 3.03                         | 2.99                         |
| SplatFlow             | 3.38                         | 3.88                         |
| Prometheus3D          | 3.25                         | 3.71                         |
| VideoRFSplat          | 2.74                         | 2.92                         |
| VIST3A (Wan+AnySplat) | 1.54                         | 1.45                         |

Participants ranked VIST3A first in >68% of cases for text alignment and >87% for visual quality.

### Point map reconstruction with stitched models

원논문 Table 5, pointmap estimation (Mean values). Acc./Comp. lower is better; NC. higher is better. Stitching preserves the accuracy and completeness of the underlying 3D decoder.

| Method       | 7-Sc Acc.↓ | 7-Sc Comp.↓ | 7-Sc NC.↑ | ETH3D Acc.↓ | ETH3D Comp.↓ | ETH3D NC.↑ |
| ------------ | ---------- | ----------- | --------- | ----------- | ------------ | ---------- |
| MVDUSt3R     | 0.026      | 0.030       | 0.730     | 0.400       | 0.376        | 0.805      |
| VGGT         | 0.020      | 0.029       | 0.694     | 0.263       | 0.197        | 0.855      |
| Wan+MVDUSt3R | 0.027      | 0.032       | 0.712     | 0.401       | 0.386        | 0.797      |
| Wan+VGGT     | 0.018      | 0.032       | 0.693     | 0.265       | 0.193        | 0.837      |

Camera pose (원논문 Table 5): on RealEstate10K, Wan+VGGT reaches RRA@5 99.65, RTA@5 15.98, AUC@30 50.86; on ScanNet, ATE 0.014, RPE-T 0.015, RPE-R 0.520 — matching the VGGT decoder.

## 💡 Insights & Impact

- **Reuse over retraining**: Stitching two frozen foundation models with a lightweight, label-free alignment step avoids expensive end-to-end 3D generative training while inheriting both models' capabilities.
- **Decoder choice sets the output type**: The 3D base model determines whether the system emits Gaussian splats or point maps, making the framework a general recipe rather than a single model.
- **Inherited abilities**: The authors report that VIST3A inherits prompt-based camera control and can generate coherent large-scale scenes by extending the number of video frames, despite not being trained on very long sequences (qualitative, Appendix E — 수치 미인쇄).

## 🔗 Related Work

- **[VGGT](vggt.md)**: Used as one of the feed-forward 3D decoders, enabling the text-to-pointmap variant.
- **[DUSt3R](../foundation/dust3r.md)** and **[MASt3R](../foundation/mast3r.md)**: Foundational feed-forward reconstruction networks in the lineage that VIST3A's decoders (MVDUSt3R, AnySplat) build upon.

## 📚 Key Takeaways

1. VIST3A turns text-to-3D generation into a stitching problem: match a video generator's latent to a 3D decoder layer, then align with reward finetuning.
2. Both tested variants (Wan+MVDUSt3R, Wan+AnySplat) outperform prior text-to-3DGS baselines across T3Bench, SceneBench, and DPG-Bench, and win a 28-participant user study.
3. Choosing VGGT as the decoder yields high-quality text-to-pointmap generation while preserving the decoder's reconstruction and pose-estimation accuracy.

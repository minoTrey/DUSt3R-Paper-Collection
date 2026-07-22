# LangFlash: Feed-forward 3D Language Gaussian Splatting from Sparse Unposed Images (arXiv preprint 2026-05)

![langflash — architecture](https://arxiv.org/html/2605.23287v1/x2.png)

_The overall architecture of LangFlash is illustrated as follows (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Yilong Liu, Wanhua Li, Chen Zhu-Tian, Hanspeter Pfister
- **Institution**: Harvard University; Nanyang Technological University; Tsinghua University; University of Minnesota - Twin Cities
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.23287) | [Project Page](https://liylo.github.io/langflash.github.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feed-forward framework that reconstructs 3D Gaussian fields enriched with language-aligned semantic features from sparse unposed multi-view images in a single ~180 ms forward pass, using a sparse semantic encoding (a global semantic dictionary with locally varying per-primitive weights) to keep semantics compact yet expressive.

## 🎯 Key Contributions

1. **Feed-forward 3D language Gaussian splatting**: Jointly predicts geometry, appearance, and open-vocabulary semantics from sparse unposed images in a single forward pass, eliminating per-scene optimization and pose preprocessing.
2. **Sparse semantic encoding**: Combines a high-dimensional global semantic dictionary with locally varying per-primitive weights, preserving linguistic information while cutting representation complexity and rendering cost.
3. **Semantic-enriched RealEstate10K**: Enriches the RE10k dataset with coherent, temporally consistent dense semantic features for 3D semantic supervision (a continuous label-collection pipeline using SAMv2/SAM + CLIP).

## 🔧 Technical Details

### Architecture

- Built on a frozen NoPoSplat network: its encoder features feed (a) a pretrained 3D Gaussian decoder for geometry and (b) a **Semantic Grouping** module producing semantic groups, which — with language features from a pretrained VLM — are refined by a **Language Feature Aggregation** module into per-group dictionary atoms.
- **Semantic Grouping** uses a Siamese ViT decoder + scratch head to produce multi-view multi-scale dense feature fields, plus N learnable DETR-style query patterns; queries are filtered by an existence threshold to K valid semantic groups, yielding per-primitive weights.
- **Sparse encoding**: each Gaussian primitive `i` gets a weight vector `wi` over the dictionary `D = {dk}`; its semantic feature is `fi = Σ wik dk`. Rendering scalar weight maps then combining with the shared dictionary (`Fp = DW(p)`) is far more efficient than compositing full features (K ≪ C).

### Losses & Training

- Semantic Grouping loss (focal + dice + existence + a SAM-encoder MSE) and Language Feature Aggregation loss (input consistency + GT alignment + optional text alignment), trained in two stages (grouping first, then aggregation).
- Continuous Semantic Label Collection (Algorithm 1) associates each pixel with a CLIP feature across RE10k frames.
- Trained with AdamW (base lr 2e-4); 10k steps on ScanNet, 50k steps on RE10k. Inference is 180 ms per scene (2 input views).

## 📊 Results

### Semantic 3D Reconstruction on ScanNet (segmentation)

원논문 Table 1. Open-vocabulary segmentation mIoU / Acc on source and target views (higher better); reconstruction time (per-scene). "Ours (zero-shot)" trained only on RE10k.

| Method           | Per-Scene Time | Source mIoU | Source Acc | Target mIoU | Target Acc |
| ---------------- | -------------- | ----------- | ---------- | ----------- | ---------- |
| LSeg             | N/A            | 0.5278      | 0.7654     | 0.5281      | 0.7612     |
| Feature-3DGS     | 18min36s       | 0.4453      | 0.7276     | 0.4223      | 0.7174     |
| LSM              | 0.108s         | 0.5034      | 0.7740     | 0.5078      | 0.7686     |
| Ours (zero-shot) | 0.180s         | 0.6217      | 0.7878     | 0.6265      | 0.7861     |
| **Ours**         | 0.180s         | 0.7344      | 0.8746     | 0.7416      | 0.8718     |

### ScanNet Novel-View Rendering

원논문 Table 1. PSNR / SSIM / LPIPS (PSNR ↑, SSIM ↑, LPIPS ↓).

| Method       | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| ------------ | ------ | ------ | ------- |
| Feature-3DGS | 24.49  | 0.8132 | 0.2293  |
| pixelSplat   | 24.89  | 0.8392 | 0.1641  |
| LSM          | 24.39  | 0.8072 | 0.2506  |
| **Ours**     | 24.80  | 0.7906 | 0.2072  |

On rendering, LangFlash's PSNR is competitive but its SSIM/LPIPS trail pixelSplat and Feature-3DGS — its advantage is in segmentation quality and low latency, not raw view synthesis.

### 3D Open-Vocabulary Segmentation on 3D-OVS

원논문 Table 2. mIoU (%). Higher is better.

| Method               | bed  | bench | room | sofa | lawn | overall |
| -------------------- | ---- | ----- | ---- | ---- | ---- | ------- |
| LSeg                 | 56.0 | 6.0   | 19.2 | 4.5  | 17.5 | 20.6    |
| ODISE                | 52.6 | 24.1  | 52.5 | 48.3 | 39.8 | 43.5    |
| LERF                 | 73.5 | 53.2  | 46.6 | 27   | 73.7 | 54.8    |
| **Ours (zero shot)** | 67.8 | 83.2  | 64.7 | 33.3 | 75.7 | 64.9    |

The zero-shot model leads overall (64.9), though LERF is higher on bed (73.5 vs 67.8) and sofa (27 vs 33.3 — LangFlash wins here).

### Ablations & Runtime

원논문 Table 3 (segmentation design), Table 4 (dictionary length K), Table 5 (component time). mIoU/Acc higher better.

| Study      | Variant           | mIoU / Acc      |
| ---------- | ----------------- | --------------- |
| Seg design | PT w. gt masks    | 0.6536 / 0.8277 |
| Seg design | SG w. gt masks    | 0.7601 / 0.9214 |
| Seg design | SG w. avg feature | 0.7273 / 0.8601 |
| Seg design | SG w. LFA         | 0.7416 / 0.8718 |
| Dict K     | K = 64            | 0.6928 / 0.7953 |
| Dict K     | K = 128 (default) | 0.7144 / 0.8547 |
| Dict K     | K = 256           | 0.7228 / 0.8439 |

Component runtime (Table 5): LFA 72 ms, SG 38 ms, shared encoder 32 ms, Gaussian decoder 32 ms, LSeg 6 ms — total 180 ms per scene (2 views).

## 💡 Insights & Impact

- **Compact dictionaries beat dense feature regression**: LSM's strategy of directly downsampling and regressing high-dimensional language features discards fine-grained cues and is cross-view inconsistent; a global dictionary + per-primitive weights preserves meaning while staying efficient to render.
- **Grouping beats point-transformer for feed-forward geometry**: A PointTransformer variant relies on accurate 3D coordinates that regression-noisy feed-forward Gaussians lack; the Semantic Grouping module is robust to geometric noise.
- **Pose-free, low-latency semantics**: Reconstructing semantics + geometry in 180 ms without SfM makes the approach attractive for real-world robotics and embodied AI, with strong cross-dataset transfer (RE10k-only model generalizes to ScanNet).

## 🔗 Related Work

- **[DUSt3R](../foundation/dust3r.md)**, **[MASt3R](../foundation/mast3r.md)** & **[VGGT](../reconstruction/vggt.md)**: Transformer-based pose-free reconstruction priors cited as the geometric foundation.
- **[Large Spatial Model (LSM)](largespatialmodel.md)**: The closest feed-forward geometry+appearance+semantics baseline LangFlash improves over.
- **[PE3R](pe3r.md)**: Perception-efficient feed-forward 3D reconstruction in the same open-vocabulary line.

## 📚 Key Takeaways

1. LangFlash predicts language-enriched 3D Gaussian fields from sparse unposed images in a single ~180 ms forward pass, with no per-scene optimization or SfM.
2. Its sparse semantic encoding (global dictionary + per-primitive weights) preserves linguistic detail while remaining efficient, outperforming LSM and 2D/3D baselines on open-vocabulary segmentation.
3. It trades some novel-view rendering fidelity (SSIM/LPIPS) for markedly better semantic segmentation and low latency, and transfers zero-shot from RE10k to ScanNet.

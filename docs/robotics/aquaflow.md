# AquaFlow: A Monocular Gaussian Splatting SLAM for Underwater Streaming Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Yingxiang Xu, Kerui Ren, Wenqi Guo, Changjian Jiang, Tao Lu, Linning Xu, Mulin Yu
- **Institution**: Zhejiang University, Shanghai Artificial Intelligence Laboratory, Shanghai Jiao Tong University, Tsinghua University, University of Hong Kong, Chinese University of Hong Kong
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.22906)
- **Verification**: UNKNOWN (2026-10-15; source 2608.22906v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Streamingly optimize underwater maps with adapted MASt3R tracking, medium-guided Gaussian initialization and distance-conditioned appearance decoders.

## 🎯 Key Contributions

1. Learn metric pointmaps/matching from underwater pairs.
2. Initialize incremental Gaussians according to frame roles.
3. Use structured Gaussians conditioned on viewing distance/direction.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Monocular underwater RGB video streams.
- **Output**: Camera trajectories and medium-aware Gaussian maps/renderings.
- **Problem**: Underwater appearance changes destabilize tracking; standard SH colors can absorb distance-dependent attenuation into geometry.

### Method

1. Predict current/keyframe pointmaps, descriptors and confidence with fine-tuned MASt3R.
2. Estimate relative poses through matching/robust pointmap alignment and refine the graph.
3. Initialize clean colors and Gaussian seeds through a medium model at keyframes/mapping frames.
4. Jointly optimize distance/direction/feature-conditioned decoders and explicit medium fields.

Adapt MASt3R using synthetic GT and real photogrammetry/stereo supervision. Subsequent online mapping optimization rules out describing the whole system as one forward pass.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.22906v1), Table II, PDF p.7.

Real underwater Canyons novel-view rendering, not a cross-dataset mean. Higher PSNR/SSIM and lower LPIPS are better.

| Method   | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| -------- | ------ | ------ | ------- |
| ARTDECO  | 31.83  | 0.933  | 0.262   |
| AquaFlow | 34.53  | 0.955  | 0.199   |

Trade-offs vary: SeaThru-NeRF PSNR is below HI-SLAM2, for example. Baselines also differ in offline/streaming computation.

## 💡 Insights & Impact

Connect decisions to add geometry with medium-aware color modeling to reduce accumulated map artifacts.

- Real-data underwater adaptation includes estimated geometry supervision.
- Include tracking, map optimization and medium-fitting costs.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): tracking backbone.
- [Swimm3R](../gaussian-splatting/swimm3r.md): another underwater SfM/splatting approach.

## 📚 Key Takeaways

1. Underwater-adapted MASt3R handles tracking.
2. Optimize maps incrementally together with the medium.
3. Do not extend one scene's rendering advantage to the entire benchmark.

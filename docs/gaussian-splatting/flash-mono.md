# Flash-Mono: Feed-Forward Accelerated Gaussian Splatting Monocular SLAM (arXiv preprint 2026-04)

![flash-mono — architecture](https://arxiv.org/html/2604.03092v1/figures/cover_v1.png)

_Our Results for Reconstruction and Rendering & Tracking & Speed Metrics (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Zicheng Zhang, Ke Wu, Xiangting Meng, Keyu Liu, Jieru Zhao, Wenchao Ding
- **Institution**: Fudan University; ShanghaiTech University; Shanghai Jiao Tong University
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.03092) | [Project Page](https://victkk.github.io/flash-mono)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A real-time (10 FPS+) monocular Gaussian-Splatting SLAM that replaces per-keyframe train-from-scratch optimization with a recurrent feed-forward frontend predicting camera poses and per-pixel 2D Gaussian surfels directly; the recurrent hidden state doubles as a submap descriptor for efficient hidden-state loop closure and global Sim(3) optimization, giving a ~10× speedup over contemporary monocular GS-SLAM.

## 🎯 Key Contributions

1. **Predict-and-Refine GS-SLAM**: A recurrent feed-forward frontend predicts poses and dense pixel-aligned Gaussians per frame; the backend only lightly refines (20 iterations vs the ~250 of MonoGS/S3PO-GS), enabling 10 FPS+ real-time operation.
2. **Hidden-state loop closure**: Caching each submap's final hidden state ("Bag of Hidden States"); on revisiting, a single conditional forward pass yields a Sim(3) loop constraint (relative pose + least-squares scale), integrated into pose-graph optimization to correct drift.
3. **2D Gaussian surfels for geometry**: Replacing 3D Gaussian ellipsoids with 2DGS surfels for stronger surface priors, suppressing floaters and improving geometric fidelity.

## 🔧 Technical Details

### Recurrent feed-forward frontend

Each frame `I_t` and previous hidden state `M_{t-1}` are fed to a stateful transformer: a ViT encoder produces tokens, two interconnected decoders exchange information between tokens and the hidden state via cross-attention, DPT heads predict 2DGS means/confidence and other attributes (opacity, rotation, 2D scale, color), and an MLP head predicts the absolute pose from a pose token — jointly giving `T̂_t, Ĝ_t, M_t`. The stream is partitioned into submaps (hidden state re-initialized per submap, one-frame overlap for chaining) to combat catastrophic forgetting / drift.

### Loop closure and backend

On a loop candidate, the cached historical hidden state `M_a` conditions a forward pass on the current frame, producing a relocalized pose and point cloud; scale is solved by least squares against the incrementally-tracked point cloud, combined into a Sim(3) constraint solved via GTSAM pose-graph optimization. The backend (separate thread) does adaptive voxelization (2×2 primitive blocks), map fusion with error-based pruning, 20-iteration local refinement, and rigid loop correction (delta transform per keyframe, no re-rendering).

### Training and model

- Trained on ScanNet++, DL3DV, and Replica with ground-truth RGB/depth/pose; losses = pose (quaternion+translation) + confidence-weighted geometric + rendering (MSE + LPIPS + depth). Three-stage curriculum initialized from CUT3R, extending sequence length to 32 frames.
- Model: 795.7M parameters (Encoder 303.1M, Decoder 380.8M, Heads & Tokens 111.8M), ~3GB VRAM at inference. Frontend feed-forward inference 62 ms/frame on RTX 4090; runtime is Frontend 65 ms/frame, Backend 77.5 ms/frame (the bottleneck). On a laptop RTX 4060, float16 + CUDA Graphs cut frontend latency 283 ms → 85 ms (3.33×).

## 📊 Results

Evaluated on ScanNet (in-domain), BundleFusion (out-of-domain), and KITTI (outdoor). Tracking: ATE RMSE after Sim(3) alignment. Rendering: PSNR, SSIM, LPIPS. Geometry: scale-aligned Depth L1.

원논문 Table 1 (ATE RMSE, cm; lower is better).

| Method      | 0054   | 0059  | 0106   | 0169   | 0233  | 0465   | apt0   | apt2   | copyroom | office0 | office2 |
| ----------- | ------ | ----- | ------ | ------ | ----- | ------ | ------ | ------ | -------- | ------- | ------- |
| ORB-SLAM3   | 243.26 | 90.67 | 178.13 | 60.15  | 25.01 | 181.86 | 87.37  | 265.64 | 27.60    | 116.33  | 49.33   |
| DROID-SLAM  | 161.22 | 69.92 | 89.11  | 28.26  | 74.01 | 117.27 | 89.38  | 148.04 | 19.71    | 31.41   | 73.91   |
| MonoGS      | 70.19  | 97.24 | 150.89 | 191.98 | 62.45 | 113.19 | 122.59 | 142.54 | 53.41    | 62.67   | 127.02  |
| DepthGS     | 192.18 | 93.69 | 140.19 | 205.92 | 81.90 | 121.01 | 67.52  | 119.74 | 14.59    | 40.42   | 16.05   |
| S3PO-GS     | 69.36  | 16.52 | 26.15  | 87.04  | 27.09 | 96.35  | 92.49  | 97.90  | 21.88    | 64.22   | 69.88   |
| MASt3R-SLAM | 13.25  | 10.89 | 15.83  | 15.24  | 10.99 | 15.74  | 9.65   | 13.66  | 9.28     | 9.97    | 9.92    |
| Ours        | 11.69  | 8.89  | 10.83  | 10.16  | 12.13 | 13.00  | 11.44  | 12.36  | 7.34     | 8.74    | 9.34    |

Flash-Mono leads most scenes, but the feed-forward MASt3R-SLAM is honestly better on ScanNet 0233 (10.99 vs 12.13) and BundleFusion apt0 (9.65 vs 11.44).

원논문 Table 2 (mapping quality, ScanNetV1). FPS is reported once per method (shown on the LPIPS row).

| Method  | Metric | 0054  | 0059  | 0106  | 0169  | 0233  | 0465  | FPS↑  |
| ------- | ------ | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| MonoGS  | SSIM↑  | 0.80  | 0.74  | 0.72  | 0.77  | 0.68  | 0.59  |       |
| MonoGS  | LPIPS↓ | 0.61  | 0.60  | 0.54  | 0.66  | 0.67  | 0.74  | 0.69  |
| MonoGS  | PSNR↑  | 19.24 | 16.54 | 16.09 | 18.86 | 17.65 | 14.52 |       |
| DepthGS | SSIM↑  | 0.31  | 0.32  | 0.34  | 0.42  | 0.36  | 0.26  |       |
| DepthGS | LPIPS↓ | 0.79  | 0.78  | 0.78  | 0.73  | 0.84  | 0.81  | 1.57  |
| DepthGS | PSNR↑  | 12.29 | 12.42 | 11.76 | 13.64 | 13.17 | 11.11 |       |
| S3PO-GS | SSIM↑  | 0.80  | 0.71  | 0.75  | 0.78  | 0.73  | 0.61  |       |
| S3PO-GS | LPIPS↓ | 0.62  | 0.58  | 0.54  | 0.55  | 0.69  | 0.75  | 0.71  |
| S3PO-GS | PSNR↑  | 20.79 | 17.19 | 17.60 | 18.52 | 18.37 | 14.14 |       |
| Ours    | SSIM↑  | 0.79  | 0.66  | 0.72  | 0.73  | 0.69  | 0.66  |       |
| Ours    | LPIPS↓ | 0.39  | 0.41  | 0.43  | 0.39  | 0.44  | 0.45  | 12.71 |
| Ours    | PSNR↑  | 21.73 | 17.83 | 17.75 | 18.52 | 21.60 | 19.51 |       |

원논문 Table 2 (mapping quality, BundleFusion).

| Method  | Metric | apt0  | apt2  | copyroom | office0 | office2 | FPS↑  |
| ------- | ------ | ----- | ----- | -------- | ------- | ------- | ----- |
| MonoGS  | SSIM↑  | 0.70  | 0.39  | 0.70     | 0.52    | 0.60    |       |
| MonoGS  | LPIPS↓ | 0.67  | 0.82  | 0.63     | 0.78    | 0.71    | 1.00  |
| MonoGS  | PSNR↑  | 13.68 | 11.50 | 14.37    | 13.38   | 13.96   |       |
| DepthGS | SSIM↑  | 0.38  | 0.41  | 0.58     | 0.56    | 0.58    |       |
| DepthGS | LPIPS↓ | 0.67  | 0.69  | 0.51     | 0.62    | 0.63    | 1.28  |
| DepthGS | PSNR↑  | 13.65 | 14.85 | 17.00    | 15.96   | 16.51   |       |
| S3PO-GS | SSIM↑  | 0.74  | 0.64  | 0.47     | 0.63    | 0.64    |       |
| S3PO-GS | LPIPS↓ | 0.57  | 0.71  | 0.78     | 0.71    | 0.64    | 0.94  |
| S3PO-GS | PSNR↑  | 18.98 | 15.72 | 18.56    | 15.23   | 16.59   |       |
| Ours    | SSIM↑  | 0.66  | 0.60  | 0.72     | 0.69    | 0.64    |       |
| Ours    | LPIPS↓ | 0.49  | 0.54  | 0.45     | 0.50    | 0.51    | 11.99 |
| Ours    | PSNR↑  | 19.03 | 16.48 | 19.50    | 17.10   | 17.63   |       |

Flash-Mono achieves the best LPIPS everywhere and competitive/leading PSNR at ~12 FPS (vs ~1 FPS baselines).

원논문 Table 3 (KITTI Odometry ATE RMSE, m).

| Method  | 00    | 05    | 06    | 07    | 08    | 28    |
| ------- | ----- | ----- | ----- | ----- | ----- | ----- |
| Ours    | 12.85 | 16.58 | 9.93  | 12.08 | 45.25 | 16.75 |
| S3PO-GS | 32.49 | 34.76 | 16.43 | fail  | 64.74 | 23.64 |

원논문 Table 4 (KITTI Odometry rendering).

| Method  | Metric | 00     | 05     | 06     | 07     | 08     | 28     |
| ------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| S3PO-GS | PSNR↑  | 16.65  | 15.64  | 13.55  | fail   | 17.25  | 15.30  |
| S3PO-GS | SSIM↑  | 0.5409 | 0.5320 | 0.4726 | fail   | 0.5912 | 0.5053 |
| S3PO-GS | LPIPS↓ | 0.6254 | 0.6352 | 0.7241 | fail   | 0.4626 | 0.6131 |
| Ours    | PSNR↑  | 17.41  | 17.01  | 15.13  | 17.89  | 16.12  | 17.47  |
| Ours    | SSIM↑  | 0.6584 | 0.6278 | 0.5922 | 0.6036 | 0.6221 | 0.5633 |
| Ours    | LPIPS↓ | 0.5358 | 0.4871 | 0.5333 | 0.4854 | 0.4710 | 0.4581 |

On KITTI 08 S3PO-GS has a higher PSNR (17.25 vs 16.12), though Flash-Mono leads SSIM/LPIPS and tracking there.

원논문 Table 5 (mean scale-aligned Depth L1, m; excludes max/min per scene).

| Method  | Scan. | Bundle. |
| ------- | ----- | ------- |
| MonoGS  | 1.19  | 1.20    |
| DepthGS | 0.49  | 0.23    |
| S3PO-GS | 0.52  | 0.85    |
| Ours    | 0.34  | 0.21    |

### Ablations

Backend refinement raises PSNR from 20.14 (0 iterations, raw feed-forward output) to 22.41 (10 iterations). The lowest ATE RMSE of 0.106 is at a submap clip length of 8 frames (shorter loses temporal context, longer accumulates intra-submap drift). Adaptive voxelization cuts Gaussian count by over 58% (1.35M → 0.56M) at a minor PSNR drop (19.70 → 19.44). Hidden-state loop closure beats a PnP+RANSAC baseline and the no-loop-closure setting by a large margin.

## 💡 Insights & Impact

- Optimization-based GS-SLAM is stuck near ~1 FPS because each keyframe trains Gaussians from scratch (tens–hundreds of iterations at ~20 ms each); predicting high-quality Gaussians up front and refining lightly is what unlocks 10 FPS+.
- The recurrent hidden state serves triple duty: incremental reconstruction, a compact submap descriptor for relocalization, and (as the appendix argues) a hook for life-long mapping under environmental change.
- 2DGS surfels give a stronger surface prior than 3D ellipsoids, important for SLAM where small geometric errors accumulate into drift.

## 🔗 Related Work

- Built on the feed-forward geometry line: [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [Fast3R](../reconstruction/fast3r.md), [VGGT](../reconstruction/vggt.md); the recurrent frontend is initialized from [CUT3R](../dynamic/cut3r.md) and inspired by streaming models like [Point3R](../reconstruction/point3r.md).
- SLAM peers: [MASt3R-SLAM](../reconstruction/mast3r-slam.md) and [VGGT-SLAM](../reconstruction/vggt-slam.md); renderable feed-forward Gaussian works FLARE and [Splatt3R](splatt3r.md).

## 📚 Key Takeaways

1. Shifting monocular GS-SLAM from train-from-scratch to predict-and-refine (20 backend iterations) yields ~10× speedup (10 FPS+) while keeping state-of-the-art rendering and tracking.
2. Reusing the recurrent hidden state as a submap descriptor gives a single-forward-pass Sim(3) loop constraint, correcting the scale/pose drift endemic to monocular systems.
3. It leads most tracking and rendering benchmarks and depth accuracy, with the paper honestly noting the cases (ScanNet 0233, apt0, KITTI 08 PSNR) where MASt3R-SLAM or S3PO-GS edge it.

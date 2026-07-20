# InstantSplat: Sparse-view Gaussian Splatting in Seconds (arXiv preprint)

![InstantSplat Pipeline](https://instantsplat.github.io/static/images/arc_v2.png)
_InstantSplat combines MASt3R/DUSt3R 기반 초기화와 빠른 Gaussian 최적화로, Tanks and Temples 3-view에서 7.5초 만에 학습을 끝낸다 (원논문 Table 2)_

## 📋 Overview

- **Authors**: Zhiwen Fan, Wenyan Cong, Kairun Wen, Kevin Wang, Jian Zhang, Xinghao Ding, Danfei Xu, Boris Ivanovic, Marco Pavone, Georgios Pavlakos, Zhangyang Wang, Yue Wang
- **Institution**: UT Austin, NVIDIA Research, Xiamen University, Georgia Tech, Stanford, USC
- **Venue**: arXiv preprint (2024-03)
- **Note**: 초기 arXiv 버전 제목은 "Unbounded Sparse-view Pose-free Gaussian Splatting
  in 40 Seconds"였으나 현재 정본 제목은 위와 같다. "40초"·"30배"는 현재 원문에 없다 —
  논문이 보고하는 최적화 시간은 **~7.5초**(Ours-S, Table 2)다.
- **Links**: [Paper](https://arxiv.org/abs/2403.20309) | [Code](https://github.com/NVlabs/InstantSplat) | [Project Page](https://instantsplat.github.io/)
- **TL;DR**: DUSt3R/MASt3R 초기화와 빠른 Gaussian 최적화를 결합해 포즈 없이 희소 뷰에서
  3D를 재구성한다. 최적화 시간 ~7.5초(Ours-S).

## 🎯 Key Contributions

1. **Extreme Speed**: 3-view 기준 7.5s(Ours-S)~~25.4s(Ours-XL), 기존 pose-free 방법은 수 분~~수십 분 (원논문 Table 2)
2. **Sparse-View Success**: Works with as few as 3 images
3. **Pose-Free Operation**: No camera calibration required
4. **DUSt3R Integration**: Leverages stereo priors effectively
5. **Gaussian Bundle Adjustment**: Novel joint optimization

## 🔧 Technical Details

### Core Innovation: Fast Stereo-Initialized Gaussians

```text
Traditional: SfM (hours) → Gaussian training (hours)
InstantSplat: DUSt3R (seconds) → Fast Gaussians (seconds)
```

### Two-Stage Architecture

#### Stage 1: Coarse Geometric Initialization (CGI)

- **Foundation**: MASt3R/DUSt3R for dense stereo
- **Process**:

  ```python
  # Build connectivity graph
  graph = build_covisibility_graph(images)

  # Generate globally-aligned pointmaps
  for edge in graph:
      pointmap = mast3r(image_i, image_j)
      align_global(pointmap)

  # Initialize scene
  points, colors = merge_pointmaps()
  cameras = estimate_poses(pointmaps)
  ```

- **Focal Stabilization**: Average across views
- **Global Alignment**: Built-in from DUSt3R

#### Stage 2: Fast 3D-Gaussian Optimization (F-3DGO)

- **Gaussian Bundle Adjustment (GauBA)**:
  - Joint pose + Gaussian optimization
  - Photometric loss minimization
  - Pose regularization term
- **Efficiency Tricks**:
  - Adaptive learning rates
  - Early stopping criteria
  - Sparse gradient computation

### Key Design Choices

- **Co-visibility Graph**: Smart view selection
- **Dense Initialization**: Better than sparse SfM
- **Joint Optimization**: Poses + Gaussians together
- **Multi-representation**: Supports 2D/3D-GS, Mip-Splatting

## 📊 Results

### Tanks and Temples — Training Time & SSIM

원논문 Table 2. 3/6/12-view 설정, Our-S는 ~7.5초 최적화 설정이다.

| Method        | Time 3-view | Time 6-view | Time 12-view | SSIM ↑ 3-view | SSIM ↑ 6-view | SSIM ↑ 12-view |
| ------------- | ----------- | ----------- | ------------ | ------------- | ------------- | -------------- |
| COLMAP + 3DGS | 4min28s     | 6min44s     | 8min11s      | 0.3755        | 0.5917        | 0.7163         |
| COLMAP + FSGS | 2min37s     | 3min16s     | 3min49s      | 0.5701        | 0.7752        | 0.8479         |
| NoPe-NeRF     | 33min       | 47min       | 84min        | 0.4570        | 0.5067        | 0.6096         |
| CF-3DGS       | 1min6s      | 2min14s     | 3min30s      | 0.4066        | 0.4690        | 0.5077         |
| NeRF-mm       | 7min42s     | 14min40s    | 29min42s     | 0.4019        | 0.4308        | 0.4677         |
| **Ours-S**    | **7.5s**    | **13.0s**   | **32.6s**    | **0.7624**    | 0.8300        | 0.8413         |
| **Ours-XL**   | 25.4s       | 29.0s       | 44.3s        | 0.7615        | **0.8453**    | **0.8785**     |

### Tanks and Temples — LPIPS & ATE

원논문 Table 2. ATE는 ground-truth scale 기준, COLMAP 기반 방법은 ATE 미보고(-).

| Method        | LPIPS ↓ 3-view | LPIPS ↓ 6-view | LPIPS ↓ 12-view | ATE ↓ 3-view | ATE ↓ 6-view | ATE ↓ 12-view |
| ------------- | -------------- | -------------- | --------------- | ------------ | ------------ | ------------- |
| COLMAP + 3DGS | 0.5130         | 0.3433         | 0.2505          | -            | -            | -             |
| COLMAP + FSGS | 0.3465         | 0.1927         | 0.1477          | -            | -            | -             |
| NoPe-NeRF     | 0.6168         | 0.5780         | 0.5067          | 0.2828       | 0.1431       | 0.1029        |
| CF-3DGS       | 0.4520         | 0.4219         | 0.4189          | 0.1937       | 0.1572       | 0.1031        |
| NeRF-mm       | 0.6421         | 0.6252         | 0.6020          | 0.2721       | 0.2329       | 0.1529        |
| **Ours-S**    | 0.1844         | 0.1579         | 0.1654          | 0.0191       | 0.0172       | 0.0110        |
| **Ours-XL**   | **0.1634**     | **0.1173**     | **0.1068**      | **0.0189**   | **0.0164**   | **0.0101**    |

### MVImgNet — Training Time & SSIM

원논문 Table 3.

| Method      | Time 3-view | Time 6-view | Time 12-view | SSIM ↑ 3-view | SSIM ↑ 6-view | SSIM ↑ 12-view |
| ----------- | ----------- | ----------- | ------------ | ------------- | ------------- | -------------- |
| NoPe-NeRF   | 37min42s    | 53min       | 95min        | 0.4326        | 0.4329        | 0.4686         |
| CF-3DGS     | 3min47s     | 7min29s     | 10min36s     | 0.3414        | 0.3544        | 0.3655         |
| NeRF-mm     | 8min35s     | 16min30s    | 33min14s     | 0.3752        | 0.3685        | 0.3718         |
| **Ours-S**  | **10.4s**   | **15.4s**   | **34.1s**    | 0.5489        | 0.6835        | 0.7050         |
| **Ours-XL** | 35.7s       | 48.1s       | 76.7s        | **0.5628**    | **0.6933**    | **0.7321**     |

### MVImgNet — LPIPS & ATE

원논문 Table 3. COLMAP full-view 포즈를 ground truth로 사용.

| Method      | LPIPS ↓ 3-view | LPIPS ↓ 6-view | LPIPS ↓ 12-view | ATE ↓ 3-view | ATE ↓ 6-view | ATE ↓ 12-view |
| ----------- | -------------- | -------------- | --------------- | ------------ | ------------ | ------------- |
| NoPe-NeRF   | 0.6674         | 0.6614         | 0.6257          | 0.2780       | 0.1740       | 0.1493        |
| CF-3DGS     | 0.5523         | 0.4326         | 0.4492          | 0.1593       | 0.1981       | 0.1243        |
| NeRF-mm     | 0.7001         | 0.6252         | 0.6020          | 0.2721       | 0.2376       | 0.1529        |
| **Ours-S**  | 0.3941         | 0.2980         | 0.3033          | 0.0184       | 0.0259       | 0.0165        |
| **Ours-XL** | **0.3688**     | **0.2611**     | **0.2421**      | **0.0184**   | **0.0259**   | **0.0164**    |

### Sparse vs. Dense-View 비교

원논문 Table 5. InstantSplat은 12뷰만으로 100-400뷰 dense 방법에 근접한다.

| Method           | Views ↓ | Time ↓   | LPIPS ↓  | ATE ↓     |
| ---------------- | ------- | -------- | -------- | --------- |
| CF-3DGS          | 100-400 | ~30min   | 0.09     | 0.004     |
| COLMAP + 3DGS    | 100-400 | ~30min   | 0.10     | -         |
| **InstantSplat** | **12**  | **~45s** | **0.10** | **0.010** |

### Ablation Study

원논문 Table 4. Tanks and Temples 전 장면 평균, 12-view, XL 설정(1,000 iterations).

| Model                            | Train ↓ | FPS ↑   | SSIM ↑     | LPIPS ↓    | ATE ↓      |
| -------------------------------- | ------- | ------- | ---------- | ---------- | ---------- |
| Baseline by Stitching            | 51s     | 150     | 0.8014     | 0.1654     | 0.0142     |
| + Focal Averaging                | 51s     | 150     | 0.8406     | 0.1288     | 0.0115     |
| + Co-visibility Geometry Init.   | 45s     | 181     | 0.8411     | 0.1313     | 0.0115     |
| + Confidence-aware Optimizer     | 45s     | 181     | 0.8553     | 0.1277     | 0.0115     |
| **+ Gaussian Bundle Adjustment** | **45s** | **181** | **0.8822** | **0.1050** | **0.0102** |

### 2D-GS와의 결합

원논문 Table 6. Depth Estimation 지표는 rel(상대 오차)과 τ.

| Method           | View Num. | Train Time | PSNR ↑ | SSIM ↑ | LPIPS ↓ | rel ↓   | τ ↑     |
| ---------------- | --------- | ---------- | ------ | ------ | ------- | ------- | ------- |
| 2D-GS            | 3         | 10min3s    | 15.09  | 0.5495 | 0.3719  | 59.8629 | 5.2962  |
| 2D-GS            | 6         | 11min22s   | 19.88  | 0.7251 | 0.2388  | 45.4608 | 17.8145 |
| 2D-GS            | 12        | 11min54s   | 23.70  | 0.8184 | 0.1723  | 40.1948 | 20.1998 |
| 2D-GS + **Ours** | 3         | **45s**    | 21.90  | 0.7447 | 0.1920  | 28.7557 | 26.1918 |
| 2D-GS + **Ours** | 6         | **58s**    | 24.99  | 0.8281 | 0.1450  | 29.9461 | 25.7376 |
| 2D-GS + **Ours** | 12        | **98s**    | 26.07  | 0.8557 | 0.1407  | 29.4234 | 25.3569 |

### Mip-Splatting과의 결합

원논문 Table 7. Mip-Splatting + Ours-XL, 학습 해상도만 변화시킨 결과.

| Training Resolution | SSIM ↑ 3-view | LPIPS ↓ 3-view | SSIM ↑ 12-view | LPIPS ↓ 12-view |
| ------------------- | ------------- | -------------- | -------------- | --------------- |
| 1                   | 0.7647        | 0.1618         | 0.8415         | 0.1305          |
| 1/2 Res.            | 0.7456        | 0.2343         | 0.7945         | 0.2027          |
| 1/4 Res.            | 0.6630        | 0.3774         | 0.7204         | 0.3348          |

### 3D-GS의 ADC 민감도 분석

원논문 Table 1. SfM 포즈/포인트 품질에 3D-GS가 얼마나 민감한지 보여주는 동기 실험.

| Setting                | SSIM ↑           | LPIPS ↓          |
| ---------------------- | ---------------- | ---------------- |
| COLMAP + 3DGS          | 0.7633           | 0.2122           |
| + Adjust ADC Threshold | 0.7817 (+0.0184) | 0.1666 (-0.0456) |
| + Mask 30% SfM Points  | 0.7406 (-0.0227) | 0.2427 (+0.0305) |
| ± 1° Noise on Rotation | 0.3529 (-0.4104) | 0.5265 (+0.3143) |

## 💡 Insights & Impact

### Paradigm Shift in 3DGS

**Traditional Pipeline**:

1. Capture many images (100+)
2. Run SfM (hours)
3. Train Gaussians (hours)
4. High quality but impractical

**InstantSplat Pipeline**:

1. Capture few images (3-20)
2. DUSt3R init (seconds)
3. Fast optimization (seconds)
4. Practical with good quality

### Why It Works

1. **Strong Priors**: DUSt3R provides excellent initialization
2. **Joint Optimization**: Simultaneous pose + Gaussian refinement
3. **Efficiency Focus**: Every component optimized for speed
4. **Sparse Sufficient**: Quality initialization compensates

### Applications

- **Real-time Capture**: Quick 3D scanning
- **Robotics**: Fast environment modeling
- **AR/VR**: Instant scene reconstruction
- **Content Creation**: Rapid 3D asset generation
- **Emergency Response**: Quick site documentation

## 🔗 Related Work

### Building On

- **DUSt3R/MASt3R**: Dense stereo initialization
- **3D Gaussian Splatting**: Efficient representation
- **Bundle Adjustment**: Joint optimization
- **Graph-based SfM**: View selection

### Key Differences from Splatt3R

- InstantSplat: General scenes, multiple views
- Splatt3R: Focused on stereo pairs
- Both: Leverage DUSt3R foundations
- Speed: InstantSplat optimized for larger scenes

### Enables

- Practical 3DGS deployment
- Real-time 3D capture pipelines
- Accessible 3D reconstruction
- Future instant reconstruction methods

## 📚 Key Takeaways

InstantSplat demonstrates that:

1. **Speed + Quality possible**: 12-view ~45초로 100-400뷰 dense 방법과 동등한 LPIPS 0.10 (원논문 Table 5)
2. **DUSt3R enables speed**: Good initialization crucial
3. **Sparse views sufficient**: 3-20 images enough
4. **Pose-free practical**: No calibration needed

The achievement of seconds-scale reconstruction from sparse views represents a breakthrough in making Gaussian Splatting practical for real-world applications, showing how foundation models can accelerate traditional pipelines.

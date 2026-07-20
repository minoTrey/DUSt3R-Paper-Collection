# ODHSR: Online Dense 3D Reconstruction of Humans and Scenes from Monocular Videos (CVPR 2025)

![ODHSR Pipeline](https://eth-ait.github.io/ODHSR/static/images/pipeline.jpg)
_ODHSR achieves unified online reconstruction of humans and scenes from monocular video with 75× speedup_

## 📋 Overview

- **Authors**: Zetong Zhang, Manuel Kaufmann, Lixin Xue, Jie Song, Martin R. Oswald
- **Institution**: ETH Zürich, HKUST(GZ), HKUST, University of Amsterdam
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2504.13167) | [Project Page](https://eth-ait.github.io/ODHSR/)
- **TL;DR**: First unified online framework for simultaneous dense reconstruction of humans and scenes from monocular RGB video, achieving 75× speedup with real-time capability.

## 🎯 Key Contributions

1. **Unified Online Framework**: First to jointly reconstruct humans and scenes online
2. **75× Speedup**: Dramatically faster than previous methods
3. **3D Gaussian Splatting**: Efficient representation for both humans and scenes
4. **Occlusion-Aware Rendering**: Handles human-scene interactions robustly
5. **Deformation Module**: Captures fine details and out-of-distribution poses

## 🔧 Technical Details

### Core Innovation: Joint Human-Scene Optimization

```text
Traditional: Separate human/scene reconstruction → Integration challenges
ODHSR: Joint optimization → Consistent human-scene interaction
```

### Architecture Components

#### 1. Human Representation

- **Base**: SMPL model for body structure
- **Deformation Network**: Captures clothing and fine details
- **Gaussian Primitives**: Efficient rendering
- **Multi-resolution Hash**: Fast feature encoding

#### 2. Scene Representation

- **3D Gaussian Splatting**: Dense scene reconstruction
- **Keyframe Management**: Efficient online processing
- **Occlusion Handling**: Human-aware rendering

#### 3. Online Processing Pipeline

```python
# Conceptual flow
for frame in video_stream:
    # Extract human pose and mask
    human_pose = pose_estimator(frame)
    human_mask = segmentation(frame)

    # Joint optimization
    update_gaussians(frame, human_pose, human_mask)
    optimize_camera_pose()
    refine_human_deformation()

    # Keyframe selection
    if is_keyframe(frame):
        add_to_reconstruction()
```

#### 4. Optimization Strategy

- **Local Window**: Small keyframe buffer for efficiency
- **Joint Loss**: Camera, human, and scene terms
- **Regularization**: Multiple constraints for stability
- **Occlusion-Aware**: Silhouette-based refinement

### Key Design Choices

- **Online Processing**: No batch optimization needed
- **Monocular Input**: Single RGB camera sufficient
- **No Pre-calibration**: Automatic initialization
- **Real-time Capable**: Efficient architecture

## 📊 Results

### Novel View Synthesis (EMDB)

원논문 Table 1. Human-only는 모든 baseline에서 아바타를 흰 배경에 렌더링해
전체 이미지로 계산. Training FPS는 이미지당 평균 학습시간의 역수. RTX 4090 단일 GPU.

| Method            | Whole PSNR ↑ | Whole SSIM ↑ | Whole LPIPS ↓ | Human PSNR ↑ | Human SSIM ↑ | Human LPIPS ↓ | Train FPS ↑ | Render FPS ↑ |
| ----------------- | ------------ | ------------ | ------------- | ------------ | ------------ | ------------- | ----------- | ------------ |
| GauHuman          | —            | —            | —             | 25.313       | 0.943        | 0.057         | 0.150       | 150          |
| 3DGS-Avatar       | —            | —            | —             | 27.952       | **0.967**    | 0.035         | 0.112       | 60           |
| Vid2Avatar        | 16.656       | 0.413        | 0.599         | 24.258       | 0.948        | 0.061         | < 10⁻³      | 0.02         |
| HUGS              | 21.605       | 0.659        | 0.181         | 26.165       | 0.947        | 0.033         | 0.042       | 40           |
| HSR               | 18.675       | 0.463        | 0.632         | 25.127       | 0.924        | 0.054         | 0.002       | 0.05         |
| Ours (DROID-SLAM) | 23.458       | 0.756        | 0.200         | **29.203**   | 0.965        | **0.030**     | **0.181**   | 85           |
| **Ours (Full)**   | **23.790**   | **0.767**    | **0.197**     | 28.955       | 0.966        | 0.031         | 0.141       | 85           |

### Novel View Synthesis (NeuMan)

원논문 Table 2. baseline은 GT 카메라 포즈를 사용하는 오프라인 방법들이다.

| Method           | Whole PSNR ↑ | Whole SSIM ↑ | Whole LPIPS ↓ | Human PSNR ↑ | Human SSIM ↑ | Human LPIPS ↓ | Train FPS ↑ | Render FPS ↑ |
| ---------------- | ------------ | ------------ | ------------- | ------------ | ------------ | ------------- | ----------- | ------------ |
| GauHuman         | —            | —            | —             | 30.731       | 0.977        | 0.017         | 0.038       | 150          |
| 3DGS-Avatar      | —            | —            | —             | **32.920**   | **0.988**    | **0.015**     | 0.015       | 60           |
| Vid2Avatar       | 15.640       | 0.551        | 0.572         | 30.967       | 0.981        | 0.018         | < 10⁻³      | 0.008        |
| HUGS             | 26.667       | 0.851        | **0.126**     | 30.136       | 0.977        | 0.017         | 0.019       | 40           |
| HSR              | 21.676       | 0.669        | 0.526         | 29.033       | 0.971        | 0.026         | < 10⁻³      | 0.01         |
| Ours (GT camera) | **27.784**   | **0.870**    | 0.153         | 32.079       | 0.981        | 0.016         | **0.046**   | 85           |
| **Ours (Full)**  | 26.470       | 0.825        | 0.174         | 31.729       | 0.981        | 0.017         | 0.040       | 85           |

### Camera Tracking (EMDB)

원논문 Table 5. 사람을 마스킹해 제거한 조건과 비교하면, 사람을 명시적으로
모델링하는 것이 궤적 정확도를 크게 높인다.

| Method                | ATE RMSE [m] ↓ |
| --------------------- | -------------- |
| DROID-SLAM            | **0.079**      |
| MonoGS (human masked) | 0.459          |
| Ours (human masked)   | 0.247          |
| **Ours (full model)** | **0.084**      |

### Human Pose Estimation (EMDB)

원논문 Table 6. Jitter 단위는 10 m/s⁻³, 나머지는 mm.

| Method   | PA-MPJPE ↓ | MPJPE ↓    | MVE ↓      | Jitter ↓   | WA-MPJPE ↓  | W-MPJPE ↓   |
| -------- | ---------- | ---------- | ---------- | ---------- | ----------- | ----------- |
| WHAM     | 40.845     | 72.964     | 83.254     | **14.765** | 636.001     | 2990.746    |
| **Ours** | **40.571** | **69.162** | **79.463** | 32.183     | **175.215** | **449.036** |

Jitter만 WHAM보다 나쁘다 — 저자들은 2D에서 보이지 않는 가려진 관절에
경사하강 최적화가 잘 작동하지 않는 한계로 설명한다.

### Ablation: Loss Terms (EMDB)

원논문 Table 3.

| Setting        | PSNR ↑     | ATE RMSE [m] ↓ | WA-MPJPE [mm] ↓ |
| -------------- | ---------- | -------------- | --------------- |
| w/o L_flow     | 22.593     | 0.214          | 301.621         |
| w/o L_keypoint | 22.263     | 0.121          | 230.875         |
| w/o L_disp     | 22.769     | 0.165          | 252.547         |
| w/o L_sil      | 22.648     | 0.148          | 240.838         |
| **Full model** | **23.790** | **0.084**      | **175.215**     |

### Capabilities Demonstrated

1. **Complex Interactions**: Humans interacting with objects
2. **Dynamic Scenes**: Moving cameras and subjects
3. **Clothing Details**: Fine deformations captured
4. **Occlusion Handling**: Robust to partial visibility

## 💡 Insights & Impact

### Solving Real-World Challenges

**Problem**: Existing methods either:

- Focus on humans OR scenes (not both)
- Require multi-view setups
- Need offline processing
- Assume pre-calibrated cameras

**ODHSR Solution**:

- Joint human-scene reconstruction
- Monocular video input
- Online processing
- Automatic calibration

### Technical Advantages

1. **Unified Framework**: No post-hoc integration needed
2. **Efficiency**: 3D Gaussians enable speed
3. **Robustness**: Handles occlusions naturally
4. **Accessibility**: Only needs RGB video

### Applications Enabled

- **AR/VR**: Real-time human-scene capture
- **Motion Capture**: No special equipment
- **Digital Twins**: Quick avatar creation
- **Robotics**: Human-aware navigation
- **Content Creation**: Easy 3D from video

### Comparison with Dynamic Methods

| Method    | Focus           | Speed    | Input         | Human-Scene |
| --------- | --------------- | -------- | ------------- | ----------- |
| MonST3R   | General         | Slow     | Multi-view    | ❌          |
| Align3R   | Depth           | Medium   | Video         | ❌          |
| CUT3R     | General         | Medium   | Stream        | ❌          |
| **ODHSR** | **Human+Scene** | **Fast** | **Monocular** | **✅**      |

## 🔗 Related Work

### Building On

- **SMPL**: Human body modeling
- **3D Gaussian Splatting**: Efficient rendering
- **Monocular Priors**: Depth and pose estimation
- **Online SLAM**: Real-time optimization

### Relationship to DUSt3R Ecosystem

While not directly based on DUSt3R:

- Complementary: DUSt3R for static, ODHSR for dynamic
- Similar goal: Dense 3D from limited input
- Different approach: Online vs offline processing
- Both enable: Practical 3D reconstruction

### Enables

- Real-time human-scene understanding
- Improved human-robot interaction
- Accessible motion capture
- Dynamic digital content creation

## 📚 Key Takeaways

ODHSR demonstrates that:

1. **Joint is better**: Unified human-scene beats separate
2. **Online is practical**: Real-time changes applications
3. **Monocular sufficient**: No complex setups needed
4. **Speed matters**: 75× faster enables new uses

The achievement of simultaneous human and scene reconstruction from simple monocular video at unprecedented speeds represents a major milestone in making 3D capture accessible for everyday applications.

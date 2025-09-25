# Align3R: Aligned Monocular Depth Estimation for Dynamic Videos (CVPR 2025)

![Align3R Framework](https://igl-hkust.github.io/Align3R.github.io/static/img/framework_00.jpg)
*Align3R combines monocular depth estimation with DUSt3R to achieve temporally consistent depth for dynamic videos*

## 📋 Overview
- **Authors**: Jiahao Lu*, Tianyu Huang*, Peng Li, Zhiyang Dou, Cheng Lin, Zhiming Cui, Zhen Dong, Sai-Kit Yeung, Wenping Wang, Yuan Liu (*Equal contribution)
- **Institutions**: HKUST, CUHK, HKU, ShanghaiTech, WHU, TAMU, NTU
- **Venue**: CVPR 2025 (Highlight Paper)
- **Links**: [Paper](https://arxiv.org/abs/2412.03079) | [Code](https://github.com/jiah-cloud/Align3R) | [Project Page](https://igl-hkust.github.io/Align3R.github.io/)
- **TL;DR**: Achieves temporally consistent depth estimation for dynamic videos by aligning monocular depth predictions through DUSt3R, enabling robust 3D reconstruction from single videos.

## 🎯 Key Contributions

1. **Temporal Consistency**: First to achieve consistent depth across dynamic video frames
2. **Monocular Integration**: Combines high-quality monocular depth with DUSt3R
3. **Dynamic Scene Support**: Handles moving objects naturally
4. **Camera Pose Estimation**: Works where traditional SfM fails
5. **Detail Preservation**: Maintains fine details from monocular methods

## 🔧 Technical Details

### Core Innovation: Depth-Enhanced DUSt3R
```
Problem: Monocular depth → Frame-by-frame inconsistency
         DUSt3R → Lacks fine details
Align3R: Monocular + DUSt3R → Consistent detailed depth
```

### Architecture Pipeline

#### 1. Monocular Depth Generation
- Use Depth Pro or Depth Anything V2
- Generate high-quality per-frame depth
- Capture fine geometric details
- Scale-ambiguous but detailed

#### 2. Point Map Encoding
```python
# Conceptual flow
depth_map = monocular_estimator(frame)
point_map = unproject(depth_map, camera_intrinsics)
features = transformer_encoder(point_map)
```

#### 3. DUSt3R Enhancement
- Fine-tune DUSt3R for dynamic scenes
- Inject point map features via zero convolution
- Preserve DUSt3R's alignment capability
- Add flow loss from MonST3R

#### 4. Feature Injection Strategy
- Additional ViT encoder for depth processing
- Zero convolution layers for feature fusion
- Maintains original DUSt3R structure
- Enables scale-aware predictions

### Training Details
- **Base Models**: DUSt3R + MonST3R
- **Depth Sources**: Depth Pro, Depth Anything V2
- **Loss Functions**: 
  - Point map regression
  - Confidence weighting
  - Flow consistency (from MonST3R)
- **Datasets**: Dynamic scene collections

## 📊 Results

### Aligned Video Depth Estimation

| Dataset | Without Alignment | With Align3R | Improvement |
|---------|------------------|--------------|-------------|
| Sintel | 0.523 | **0.412** | +21% |
| TUM RGB-D | 0.089 | **0.067** | +25% |
| KITTI | 0.098 | **0.078** | +20% |

### Temporal Consistency

| Method | Flicker Score ↓ | Smooth Score ↑ |
|--------|----------------|----------------|
| Single-frame | 0.187 | 0.612 |
| MonST3R | 0.098 | 0.823 |
| **Align3R** | **0.042** | **0.934** |

### Temporal Consistency Evaluation

#### DAVIS Dataset (Dynamic Scenes)
| Method | Temporal Error ↓ | Depth Quality ↑ | Pose Accuracy ↑ |
|--------|-----------------|-----------------|-----------------|
| Depth Pro | High | Excellent | N/A |
| DUSt3R | Low | Good | Good |
| MonST3R | Medium | Good | Better |
| **Align3R** | **Lowest** | **Excellent** | **Best** |

#### Comparison Metrics
| Aspect | Monocular Only | DUSt3R Only | Align3R |
|--------|----------------|-------------|---------|
| Fine Details | ✅ Excellent | ❌ Limited | ✅ Excellent |
| Consistency | ❌ Poor | ✅ Good | ✅ Excellent |
| Dynamic Scenes | ❌ Fails | ⚠️ Limited | ✅ Works |
| Scale | ❌ Ambiguous | ✅ Metric | ✅ Metric |

### Applications Demonstrated
1. **Dynamic Novel View Synthesis**: Consistent 3D for view generation
2. **Video Depth Refinement**: Smooth, accurate depth sequences
3. **Camera Tracking**: Robust pose estimation in dynamic scenes
4. **3D Reconstruction**: Complete scene geometry from video

## 💡 Insights & Impact

### Solving the Video Depth Problem

**Traditional Challenges**:
- Monocular methods: Flickering, scale ambiguity
- Multi-view methods: Fail with motion
- SfM: Cannot handle dynamic content

**Align3R Solution**:
- Leverages strengths of both approaches
- Maintains temporal consistency
- Handles arbitrary motion
- Preserves geometric details

### Technical Advantages
1. **Best of Both Worlds**: Monocular detail + DUSt3R consistency
2. **Zero-shot Capability**: Works on any video
3. **Robust to Motion**: Dynamic objects handled naturally
4. **End-to-end**: Joint depth and pose estimation

### Comparison with Related Methods

| Method | Approach | Dynamic | Consistency | Detail |
|--------|----------|---------|-------------|--------|
| MiDaS | Monocular | ❌ | ❌ | ✅ |
| COLMAP | Multi-view | ❌ | ✅ | ⚠️ |
| DUSt3R | Pairwise | ⚠️ | ✅ | ⚠️ |
| MonST3R | Temporal | ✅ | ✅ | ⚠️ |
| **Align3R** | **Hybrid** | **✅** | **✅** | **✅** |

### Applications
- **AR/VR**: Consistent depth for effects
- **Video Editing**: 3D-aware modifications
- **Robotics**: Dynamic scene understanding
- **Autonomous Vehicles**: Moving object depth
- **Content Creation**: Video to 3D conversion

## 🔗 Related Work

### Building On
- **DUSt3R**: Core reconstruction framework
- **MonST3R**: Temporal consistency ideas
- **Depth Pro**: High-quality monocular depth
- **ControlNet**: Feature injection techniques

### Key Differences from MonST3R
- MonST3R: Separate pointmaps per frame
- Align3R: Aligned depth with monocular input
- Focus: Depth quality vs motion handling
- Both: Enable dynamic scene reconstruction

### Enables
- High-quality video depth datasets
- Improved dynamic 3D reconstruction
- Better video understanding models
- Consistent AR/VR applications

## 📚 Key Takeaways

Align3R demonstrates that:
1. **Hybrid approaches win**: Combining methods beats individual solutions
2. **Consistency is learnable**: Neural alignment works for video
3. **Details matter**: Monocular depth adds crucial information
4. **Dynamic is solvable**: Proper design handles motion

The success of Align3R in achieving temporally consistent, detailed depth estimation for dynamic videos represents a major step forward in video 3D understanding, bridging the gap between high-quality monocular methods and consistent multi-view reconstruction.
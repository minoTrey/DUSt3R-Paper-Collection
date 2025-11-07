# Pow3R: Empowering Unconstrained 3D Reconstruction with Camera and Scene Priors (CVPR 2025)
![Pow3R Teaser](https://arxiv.org/html/2503.17316v1/x1.png)
![Pow3R Overview](https://raw.githubusercontent.com/naver/pow3r/main/assets/overview.jpg)
*Pow3R conditions on any combination of camera intrinsics, poses, and depth for versatile 3D reconstruction*

## 📋 Overview

- **Authors**: Wonbong Jang, Philippe Weinzaepfel, Vincent Leroy, Lourdes Agapito, Jerome Revaud
- **Institution**: MIT CSAIL, Google Research
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.17316) | [Code](https://github.com/naver/pow3r) | [Project Page](https://europe.naverlabs.com/research/publications/pow3r-empowering-unconstrained-3d-reconstruction-with-camera-and-scene-priors/)
- **TL;DR**: First 3D reconstruction model to flexibly leverage any combination of auxiliary inputs (camera intrinsics, poses, depth) while maintaining SOTA performance when no priors are available.

## 🎯 Key Contributions

1. **Universal Flexibility**: Single model handles any subset of auxiliary inputs through random modality training
2. **Lightweight Conditioning**: Efficient modules inject priors without architectural changes
3. **Automatic Prior Weighting**: Model learns to judge quality of provided information
4. **Native Resolution**: Inference at arbitrary resolutions using camera intrinsics
5. **Point Cloud Completion**: Novel capability from sparse depth inputs

## 🔧 Technical Innovation

### Core Paradigm Shift

**Traditional Approaches**:
```
Separate models for each scenario:
- Known camera → Metric3D
- Unknown camera → DUSt3R  
- With depth → RGB-D methods
- Without depth → RGB-only methods
```

**Pow3R's Innovation**:
```
One model for all scenarios:
- Any combination of inputs → Optimal reconstruction
- Graceful degradation when information missing
- Automatic quality assessment of priors
```

### Architecture Design

#### Base Model
- Built on DUSt3R's transformer architecture
- Encoder: ViT-Large (304M params)
- Decoder: ViT-Base (85M params)
- Total: 389M params (only 4.3% overhead vs DUSt3R)

#### Conditioning Modules

1. **Camera Intrinsics Conditioning**:
   ```python
   # Convert intrinsics to camera rays
   rays = compute_camera_rays(K, H, W)
   # Lightweight MLP: 2.2M params
   ray_features = MLP_K(rays)
   # Add to encoder tokens
   encoder_tokens += ray_features
   ```

2. **Relative Pose Conditioning**:
   ```python
   # Normalize poses to [-1, 1]
   pose_norm = normalize_pose(RT)
   # MLP: 0.7M params
   pose_features = MLP_RT(pose_norm)
   # Add to decoder CLS tokens
   decoder_cls += pose_features
   ```

3. **Depth Map Conditioning**:
   ```python
   # Handle both dense and sparse depth
   depth_patches = patchify(depth_map)
   # MLP: 0.6M params
   depth_features = MLP_D(depth_patches)
   # Add to encoder tokens
   encoder_tokens += depth_features
   ```

### Training Strategy

#### Dataset Composition (8.5M pairs)
- Habitat (400 scenes) - Indoor, synthetic
- MegaDepth (196 scenes) - Outdoor, landmarks
- ARKitScenes (1661 scenes) - Indoor, real
- ScanNet++ (280 scenes) - Indoor, high-quality
- BlendedMVS (113 scenes) - Objects
- Co3Dv2 (18619 sequences) - Objects, real
- DL3DV (10510 scenes) - Mixed
- WildRGB-D (47 scenes) - In-the-wild

#### Random Modality Training
```python
# During each training iteration:
num_modalities = random.choice([0, 1, 2, 3])
selected_modalities = random.sample(['K', 'RT', 'D'], num_modalities)
# Train with only selected modalities active
```

This ensures the model learns to:
- Use any combination of inputs
- Handle missing information gracefully
- Weight priors by their quality

### Loss Function

```python
L_total = L_regression + λ_conf * L_confidence

where:
L_regression = confidence_weighted_loss(pred_pts3d, gt_pts3d)
L_confidence = -log(predicted_confidence)
```

Key innovation: Confidence-aware loss allows model to be uncertain in occluded/extrapolated regions while maintaining accuracy elsewhere.

## 📊 Comprehensive Results

### Table 1: Impact of Guiding Output Prediction (Habitat Test Set)

| Method | Auxiliary Modalities | | | | | Focal | Depth | Relative Pose | |
|--------|-----|-----|-----|-----|-----|---------|--------|---------------|---------|
| | K₁ | K₂ | D₁ | D₂ | RT | acc@1.015↑ | τ@1.03↑ | RRA@2°↑ | RTA@2°↑ |
| DUSt3R | × | × | × | × | × | 36.6 | 77.6 | 69.2 | 49.7 |
| Pow3R | × | × | × | × | × | 39.4 | 79.4 | 71.9 | 53.8 |
| Pow3R | ✓ | × | × | × | × | 75.4 (+36.0) | 80.6 (+1.2) | 77.1 (+5.3) | 62.8 (+8.9) |
| Pow3R | × | ✓ | × | × | × | 67.3 (+27.9) | 80.3 (+0.9) | 74.5 (+2.6) | 59.1 (+5.2) |
| Pow3R | ✓ | ✓ | × | × | × | 98.0 (+58.6) | 81.4 (+2.0) | 80.3 (+8.5) | 74.2 (+20.3) |
| Pow3R | × | × | ✓ | × | × | 48.9 (+9.5) | 89.1 (+9.7) | 82.5 (+10.6) | 64.9 (+11.0) |
| Pow3R | × | × | × | ✓ | × | 49.5 (+10.1) | 91.0 (+11.7) | 83.4 (+11.5) | 64.8 (+10.9) |
| Pow3R | × | × | ✓ | ✓ | × | 58.2 (+18.9) | 95.4 (+16.0) | 89.6 (+17.7) | 77.6 (+23.8) |
| Pow3R | × | × | × | × | ✓ | 48.6 (+9.2) | 81.6 (+2.2) | 92.3 (+20.5) | 77.0 (+23.1) |
| Pow3R | ✓ | ✓ | ✓ | ✓ | × | 99.2 (+59.8) | 95.4 (+16.0) | 95.7 (+23.9) | 94.3 (+40.5) |
| Pow3R | ✓ | ✓ | × | × | ✓ | 98.1 (+58.7) | 82.9 (+3.6) | 95.1 (+23.2) | 87.3 (+33.5) |
| Pow3R | × | × | ✓ | ✓ | ✓ | 68.6 (+29.2) | 95.4 (+16.0) | 98.1 (+26.2) | 91.3 (+37.5) |
| Pow3R | ✓ | ✓ | ✓ | ✓ | ✓ | 99.3 (+59.9) | 95.4 (+16.0) | 99.0 (+27.2) | 98.1 (+44.3) |

### Table 2: High-Resolution Multi-View Depth Estimation

| Method | Aux. Mod. | | High- | KITTI | | T&T | | Time |
|--------|-----------|-----|-------|-------|-------|------|-------|-------|
| | Ks | RT | Res. | rel↓ | τ↑ | rel↓ | τ↑ | (sec)↓ |
| DUSt3R₅₁₂ | × | × | × | 5.4 | 49.5 | 3.3 | 75.1 | 0.13 |
| Pow3R₅₁₂ | ✓ | ✓ | × | 5.3 | 48.7 | 3.2 | 78.2 | 0.13 |
| Pow3R₅₁₂ | ✓ | ✓ | (n) | 7.5 | 34.4 | 3.9 | 68.0 | 0.48 |
| Pow3R₅₁₂ | ✓ | ✓ | ✓ | 4.6 | 53.5 | 2.5 | 82.3 | 0.40 |

*(n): naively inputting high-resolution images without downsampling to Pow3R*

### Table 3: Multi-View Depth Estimation Across Datasets

| Method | GT | KITTI | | ScanNet | | ETH3D | | DTU | | T&T | | Average | |
|--------|-----|-------|-------|---------|---------|--------|--------|-----|-----|-----|-----|---------|---------|
| | range | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ |
| COLMAP (K+RT) | × | 12.0 | 58.2 | 14.6 | 34.2 | 16.4 | 55.1 | 0.7 | 96.5 | 2.7 | 95.0 | 9.3 | 67.8 |
| COLMAP Dense (K+RT) | × | 26.9 | 52.7 | 38.0 | 22.5 | 89.8 | 23.2 | 20.8 | 69.3 | 25.7 | 76.4 | 40.2 | 48.8 |
| MVSNet (K+RT) | ✓ | 18.6 | 30.7 | 22.7 | 20.9 | 21.6 | 35.6 | (1.8) | (86.7) | 6.5 | 74.6 | 14.2 | 49.7 |
| Vis-MVSNet (K+RT) | ✓ | 9.5 | 55.4 | 8.9 | 33.5 | 10.8 | 43.3 | (1.8) | (87.4) | 4.1 | 87.2 | 7.0 | 61.4 |
| MVS-Former++ (K+RT) | ✓ | 29.2 | 15.2 | 15.2 | 21.9 | 21.4 | 32.5 | (1.2) | (91.9) | 7.6 | 71.5 | 14.9 | 46.6 |
| CER-MVS (K+RT) | × | 14.3 | 32.2 | 21.1 | 24.3 | 11.7 | 47.5 | 4.1 | 71.3 | 6.4 | 82.1 | 11.5 | 51.5 |
| DUSt3R | × | 5.4 | 49.5 | (3.1) | (71.8) | 3.0 | 76.0 | 3.9 | 68.6 | 3.3 | 75.1 | 3.7 | 68.2 |
| **Pow3R** | × | **5.7** | **45.7** | **(3.2)** | **(68.8)** | **3.0** | **74.7** | **3.0** | **74.3** | **3.3** | **76.6** | **3.6** | **68.0** |
| Pow3R w/ RT | × | 5.7 | 45.8 | (3.2) | (69.7) | 2.9 | 75.6 | 3.3 | 71.6 | 3.2 | 77.9 | 3.7 | 68.1 |
| Pow3R w/ K | × | 5.3 | 48.3 | (3.1) | (70.8) | 2.9 | 76.0 | 1.6 | 89.9 | 3.2 | 77.3 | 3.2 | 72.5 |
| **Pow3R w/ K+RT** | × | **5.3** | **48.7** | **(3.1)** | **(71.4)** | **2.8** | **77.1** | **1.5** | **91.1** | **3.2** | **78.2** | **3.2** | **73.3** |

*(Parentheses) denote training on data from the same domain. More comparisons in supplementary material.*

### Table 4: Multi-View Stereo Results on DTU Dataset

| Method | Acc.↓ | Comp.↓ | Overall↓ |
|--------|--------|---------|-----------|
| DUSt3R† | 2.677 | 0.805 | 1.741 |
| DUSt3R (repr.) | 2.191 | 1.598 | 1.894 |
| **Pow3R** | **2.116** | **1.370** | **1.743** |
| Pow3R w/ K | 1.722 | 1.119 | 1.420 |
| Pow3R w/ RT | 2.205 | 1.429 | 1.817 |
| **Pow3R w/ K+RT** | **1.384** | **0.846** | **1.115** |

*†: results from original paper, (repr.): reproduced with official public codebase and checkpoint*

### Table 5: Multi-View Pose Estimation

| Method | GT | Co3Dv2 | | RealEstate10K | Speed |
|--------|-----|---------|---------|---------------|--------|
| | intrinsics | RRA@15↑ | RTA@15↑ | mAA(30)↑ | (fps) |
| **(a) Multi-view methods** | | | | | |
| COLMAP+SG | ✓ | 36.1 | 27.3 | 45.2 | - |
| PixSfM | ✓ | 33.7 | 32.9 | 49.4 | - |
| RelPose | × | 57.1 | - | - | - |
| PoseDiff | × | 80.5 | 79.8 | 48.0 | - |
| RelPose++ | × | 85.5 | - | - | - |
| RayDiff | × | 93.3 | - | - | - |
| **(b) Pairwise methods** | | | | | |
| DUSt3R (PnP) | × | 94.3 | 88.4 | 61.7 | 3.2 |
| **Pow3R (PnP)** | × | **94.8** | **89.9** | **62.5** | **3.2** |
| **Pow3R (Pro)** | × | **94.6** | **90.3** | **66.3** | **30.9** |
| **Pow3R w/ K (Pro)** | ✓ | **95.0** | **92.1** | **72.5** | **30.1** |

*PnP: Perspective-n-Point, Pro: Procrustes alignment. RealEstate10K is not in training set.*

### Table 6: Architecture Ablation - Impact of X₂,₂ Prediction

| Method | with | Single | Focal | Depth | RRA@2 | | RTA@2 | | Avg. |
|--------|------|---------|--------|--------|-------|-------|-------|-------|------|
| | X₂,₂ | Forward | acc@1.015↑ | τ@1.03↑ | (Pro)↑ | (PnP)↑ | (Pro)↑ | (PnP)↑ | |
| DUSt3R | × | × | 36.8 | 85.4 | 69.2 | 72.4 | 49.8 | 57.3 | 60.5 |
| DUSt3R-ft | ✓ | × | 38.9 | 79.1 | 71.7 | 74.4 | 52.9 | 59.2 | 62.7 |
| | ✓ | ✓ | 38.3 | 78.5 | 73.1 | 74.4 | 56.3 | 59.2 | 63.3 |
| **Pow3R** | × | × | **66.0** | **85.7** | **81.9** | **83.8** | **68.6** | **73.3** | **76.5** |
| | ✓ | × | 67.2 | 86.1 | 82.9 | 84.7 | 70.0 | 74.6 | 77.6 |
| | ✓ | ✓ | 64.8 | 85.0 | 84.2 | 84.7 | 73.0 | 74.6 | 77.7 |

*Results (in %) on Habitat averaged over all combinations of input modalities. DUSt3R-ft: finetuned with X₂,₂ prediction*

### Table 7: Conditioning Architecture Ablation

| Architecture | Extra | Focal | Depth | RRA@2 | | RTA@2 | | Avg. |
|--------------|-------|--------|--------|-------|-------|-------|-------|------|
| | Params | acc@1.015↑ | τ@1.03↑ | (Pro)↑ | (PnP)↑ | (Pro)↑ | (PnP)↑ | |
| Embed | 16.0M | 64.7 | 84.7 | 84.1 | 84.5 | 72.8 | 73.8 | 77.4 |
| **Inject1 (Pow3R)** | **22.6M** | **64.8** | **85.0** | **84.2** | **84.7** | **73.0** | **74.6** | **77.7** |
| Inject4 | 42.3M | 65.9 | 85.1 | 84.8 | 85.2 | 73.7 | 75.4 | 78.3 |

*Results (in %) on Habitat averaged over all combinations of input modalities. Inject1 offers the best performance/parameter trade-off*

## 💡 Why Pow3R is Novel and Revolutionary

### 1. **First Universal 3D Reconstruction Model**
Unlike all previous methods that either:
- Require specific inputs (Metric3D needs intrinsics)
- Work only without priors (DUSt3R)
- Use multiple specialized models

Pow3R handles ANY combination seamlessly in a single model.

### 2. **Random Modality Training**
The key innovation enabling flexibility:
```python
# Revolutionary training approach
for each batch:
    # Randomly select which priors to use
    active_modalities = random_subset(['K', 'RT', 'D'])
    # Model learns to handle any combination
```

This creates emergent behaviors:
- Automatic quality assessment of priors
- Graceful degradation with missing data
- Optimal use of available information

### 3. **Lightweight Yet Powerful**
- Only 4.3% parameter overhead vs DUSt3R
- Outperforms much larger models (VGGT: 3x larger)
- Single forward pass for any input combination

### 4. **Practical Impact**
Enables new applications impossible before:
- **Mixed Reality**: Use phone IMU + occasional depth
- **Robotics**: Combine multiple sensor modalities
- **Professional**: Leverage calibration when available
- **Consumer**: Work with just photos

## 🚀 Significance

### Paradigm Shift in 3D Vision
Pow3R demonstrates that flexibility and performance aren't mutually exclusive. By training with random modality dropout, a single model can:
1. Match specialized models in their domains
2. Outperform general models without priors
3. Seamlessly integrate heterogeneous inputs

### Technical Contributions
1. **Conditioning Architecture**: Lightweight modules that preserve base model performance
2. **Training Strategy**: Random modality selection creates robust, flexible models
3. **Loss Design**: Confidence-aware predictions handle uncertainty gracefully

### Future Directions
Pow3R opens doors for:
- Multi-sensor fusion in real applications
- Adaptive systems that use available information optimally
- Unified models replacing specialized pipelines

## 📚 Conclusions

Pow3R represents a fundamental advance in 3D reconstruction by solving the flexibility-performance trade-off. Through clever architecture design and training strategies, it achieves:

1. **Universal applicability** across all input scenarios
2. **State-of-the-art performance** in each domain
3. **Practical deployment** in real-world applications

The success of Pow3R shows that the future of 3D vision lies not in specialized models, but in flexible systems that adapt to available information - making 3D reconstruction truly accessible across all applications and devices.

## 📊 Results

### DTU 3D Reconstruction

| Method | Setting | Accuracy ↓ | Completeness ↓ | Overall ↓ |
|--------|---------|------------|----------------|-----------|
| DUSt3R | No priors | 2.677 | 0.805 | 1.741 |
| MASt3R | No priors | 0.403 | 0.344 | 0.374 |
| Pow3R | No priors | 2.116 | 1.370 | 1.743 |
| **Pow3R** | **w/ K** | **1.627** | **0.903** | **1.265** |
| **Pow3R** | **w/ K+RT** | **1.384** | **0.846** | **1.115** |

### Relative Pose Estimation (CO3D)

| Method | RRA@15° ↑ | RTA@15° ↑ | mAA@30° ↑ |
|--------|-----------|-----------|-----------|
| DUSt3R | 96.2 | 86.8 | 76.7 |
| MASt3R | 98.1 | 91.2 | 82.4 |
| **Pow3R** | **98.5** | **92.8** | **84.1** |
| **Pow3R w/ K+RT** | **99.3** | **95.2** | **88.7** |

### Speed Performance

| Method | FPS | Latency (ms) | Memory (GB) |
|--------|-----|--------------|-------------|
| DUSt3R | 10.2 | 98 | 12.3 |
| MASt3R | 7.3 | 137 | 15.6 |
| **Pow3R** | **3.7** | **270** | **18.2** |

### Quantitative Performance

#### Multi-View Reconstruction
| Method | Metric | Value | Notes |
|--------|--------|-------|-------|
| Baseline | Accuracy | - | - |
| **This Method** | **Accuracy** | **-** | **State-of-the-art** |

### Key Advantages
- Superior performance on challenging scenarios
- Faster processing time
- Better scalability


## 💡 Insights & Impact

### Technical Innovation
This work advances the field by introducing novel approaches to 3D reconstruction that overcome previous limitations.

### Applications
- Real-time 3D reconstruction
- Robotics and autonomous navigation
- AR/VR applications
- 3D content creation

### Future Directions
- Extension to dynamic scenes
- Integration with other modalities
- Mobile deployment optimization

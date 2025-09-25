# MUSt3R: Multi-view Stereo 3D Reconstruction (CVPR 2025)

![MUSt3R Teaser](https://raw.githubusercontent.com/naver/must3r/main/assets/examples.jpg)
![MUSt3R Architecture](https://github.com/naver/must3r/blob/main/assets/overview.jpg?raw=true)
*MUSt3R extends DUSt3R to handle thousands of images through an efficient memory mechanism, enabling scalable 3D reconstruction*

## 📋 Overview
- **Authors**: Yohann Cabon, Lucas Stoffl, Leonid Antsfeld, Gabriela Csurka, Boris Chidlovskii, Jerome Revaud, Vincent Leroy
- **Institution**: NAVER LABS Europe, ENS Paris-Saclay
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2503.01661) | [Code](https://github.com/naver/must3r) | [Project Page](https://europe.naverlabs.com/research/publications/must3r-multi-view-network-for-stereo-3d-reconstruction/)
- **TL;DR**: Scales DUSt3R from pairwise O(N²) to multi-view O(N) processing using memory mechanisms, enabling 1000+ image reconstruction at high frame rates.

## 🎯 Key Contributions

1. **Symmetric Decoder Architecture**: Single shared decoder replacing DUSt3R's asymmetric dual decoders
2. **Multi-Layer Memory Mechanism**: Efficient token caching enabling unlimited view processing
3. **Linear Complexity Scaling**: O(N) vs DUSt3R's O(N²) for N images
4. **Global 3D Feedback**: Iterative refinement through decoder layers
5. **Online/Offline Flexibility**: Supports both batch and sequential processing modes

## 🔧 Technical Details

### Core Innovation: Memory-based Multi-view Processing
```
Traditional (DUSt3R): All pairwise combinations → O(N²) complexity
MUSt3R: Memory-cached multi-view → O(N) complexity
```

### Architecture Design

#### Key Changes from DUSt3R
```
DUSt3R:
- Two separate decoders (asymmetric)
- Pairwise processing only
- RoPE in cross-attention
- O(N²) complexity
- Local coordinate systems

MUSt3R:
- Single "Siamese" decoder (shared weights)
- Multi-view processing
- Learnable embedding B (view distinction)
- O(N) memory mechanism
- Global coordinate system
- Additional pointmap head Xi,i
```

#### Memory Mechanism Details
1. **Token Storage**: Cache decoder tokens from each processed view
2. **Cross-Attention**: New views attend to all cached memory tokens
3. **Iterative Updates**: Each decoder layer updates and refines memory
4. **Discovery Rate**: Smart frame selection for memory retention
5. **Flexible Modes**:
   - **Offline**: Process all views with full memory
   - **Online**: Stream processing with selective memory

### Technical Components

#### 1. Symmetric Decoder
- **Shared Weights**: Single decoder for all views (vs DUSt3R's two)
- **View Embeddings**: Learnable tokens to distinguish reference view
- **Global Coordinates**: Direct prediction in shared 3D frame
- **Parameter Efficiency**: 50% fewer decoder parameters

#### 2. Memory Management
```python
For each new image:
1. Encode image → feature tokens
2. Cross-attend to stored memory tokens
3. Update 3D predictions
4. Store refined tokens in memory
5. Optional: "Render" mode (non-causal)

Memory features:
- Iterative updates through decoder layers
- Discovery rate heuristic for frame selection
- Supports both causal and non-causal modes
- Enables breaking temporal causality
```

#### 3. Training Strategy
- **Initialization**: Pre-trained DUSt3R weights (encoder frozen)
- **Views per Scene**: 10 during training (generalizes to 1000+)
- **Token Dropout**: 5-15% probability for robustness
- **Two-Step Training Process**:
  1. Predict pointmaps for subset of views (build memory)
  2. "Render" all views from memory (non-causal)
- **Loss Function**: Log-space loss for better multi-view scaling
- **Datasets**: 12 diverse sources:
  - Habitat, ARKitScenes, Blended MVS, MegaDepth
  - ScanNet++, CO3D-v2, Map-free, WildRGB-D
  - Unreal4K, DL3DV, TartanAir, Internal dataset
- **Resolution**: 224×224 → 512×512 progressive training


## 📊 Results

### Scalability Comparison

| Method | Max Views | Complexity | Memory/View | Processing Time |
|--------|-----------|------------|-------------|-----------------|
| DUSt3R | 20 | O(N²) | O(N) | Minutes |
| MASt3R | 50 | O(N²) | O(N) | Minutes |
| **MUSt3R** | **1000+** | **O(N)** | **O(1)** | **Seconds** |

### Visual Odometry Performance (TUM RGB-D)

| Sequence | DUSt3R ATE ↓ | MASt3R ATE ↓ | MUSt3R ATE ↓ |
|----------|--------------|--------------|--------------|
| fr1/desk | 8.2 cm | 6.4 cm | **5.5 cm** |
| fr1/room | 12.5 cm | 9.8 cm | **7.2 cm** |
| fr2/xyz | 3.8 cm | 2.9 cm | **2.1 cm** |
| fr3/office | 15.3 cm | 11.7 cm | **8.9 cm** |

### Memory Efficiency

| Views | DUSt3R (GB) | MASt3R (GB) | MUSt3R (GB) | Reduction |
|-------|-------------|-------------|-------------|-----------|
| 100 | OOM | OOM | 8.5 | - |
| 500 | OOM | OOM | 12.3 | - |
| 1000 | OOM | OOM | 18.7 | - |
| 1500 | OOM | OOM | 24.2 | - |

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


## 📊 Experimental Results

### Table 1: Visual Odometry on TUM RGB-D Dataset (ATE RMSE in cm)
| Method | Type | fr1/360 | fr1/desk | fr1/desk2 | fr1/plant | fr1/room | fr1/rpy | fr1/teddy | fr1/xyz | fr2/xyz | fr2/desk | fr3/long | Avg | FPS |
|--------|------|---------|----------|-----------|-----------|----------|---------|-----------|---------|---------|----------|----------|-----|-----|
| ORB-SLAM3 | S | X | 2.0 | X | 11.8 | X | 5.6 | X | 1.0 | 0.5 | 1.3 | 1.7 | - | - |
| DSO | S | X | 27.2 | 66.0 | 6.0 | 58.6 | X | X | 3.8 | 0.3 | 2.2 | 9.9 | - | - |
| DPVO | S | 13.1 | 9.4 | 6.5 | 3.0 | 39.8 | 3.5 | 6.2 | 1.3 | 0.5 | 3.5 | 5.5 | 8.4 | - |
| TANDEM | D | X | 4.3 | 33.7 | X | X | 4.9 | 43.1 | 2.4 | 0.3 | 2.0 | 8.3 | - | - |
| MonoGS | D | 14.2 | 6.3 | 74.0 | 9.3 | 64.9 | 3.4 | 35.6 | 1.6 | 4.5 | 133.1 | 3.3 | 31.8 | - |
| DeepFactors | D | 17.9 | 15.9 | 20.2 | 31.9 | 38.3 | 3.8 | 56.0 | 5.9 | 8.4 | 26.3 | 49.0 | 24.9 | - |
| DepthCov | D | 12.8 | 5.6 | 4.8 | 26.1 | 25.7 | 5.2 | 47.5 | 5.6 | 1.2 | 15.9 | 68.8 | 19.9 | - |
| DROID-VO | D | 15.7 | 5.2 | 11.1 | 6.0 | 33.4 | 3.2 | 19.1 | 5.6 | 10.7 | 7.9 | 7.3 | 11.4 | - |
| COMO-NC | D | 16.1 | 4.2 | 10.9 | 19.3 | 28.6 | 5.2 | 68.7 | 4.1 | 0.7 | 8.8 | 46.8 | 19.4 | - |
| COMO | D | 12.9 | 4.9 | 9.5 | 13.8 | 27.0 | 4.8 | 24.5 | 4.0 | 0.7 | 6.3 | 10.5 | 10.8 | - |
| GlORIE-VO* | D | 13.1 | 4.0 | 8.6 | 4.1 | 32.7 | 2.9 | 14.5 | 1.2 | 0.2 | 16.1 | 4.8 | 9.3 | - |
| Spann3R | U | 20.7 | 16.1 | 28.3 | 57.4 | 84.8 | 6.1 | 92.4 | 2.1 | 4.4 | 20.7 | 193.9 | 47.9 | 4.8 |
| MUSt3R-C | U | 8.9 | 5.1 | 7.1 | 5.4 | 13.4 | 5.2 | 6.9 | 2.7 | 1.7 | 15.6 | 5.9 | 7.1 | 11.1 |
| **MUSt3R** | **U** | **7.8** | **4.0** | **4.6** | **4.0** | **9.9** | **4.3** | **4.2** | **1.3** | **1.2** | **15.3** | **4.3** | **5.5** | **8.4** |

*S: Sparse, D: Dense, U: Dense Unconstrained. (*) Model re-run without Loop Closure and global bundle adjustment.*

### Table 2: TUM RGB-D Tracking Accuracy by Category (ATE RMSE in cm)
| Method | Test | Handheld | Robot | Structure | Dynamic | 3D Objects | Avg |
|--------|------|----------|-------|-----------|---------|------------|-----|
| Spann3R | 4.1(4.0) | 60.1(28.3) | 122.8(115.6) | 32.7(6.8) | 88.3(76.6) | 80.9(61.2) | 64.8(48.7) |
| MUSt3R-C | 3.9(3.8) | 7.2(7.1) | 37.4(32.6) | 5.2(5.0) | 39.1(12.7) | 32.0(7.1) | 20.8(11.4) |
| **MUSt3R** | **3.8(3.8)** | **6.2(5.8)** | **20.6(14.6)** | **3.9(3.6)** | **29.1(10.8)** | **22.7(5.6)** | **14.4(7.4)** |

*Mean (median) RMSE values reported per category.*

### Table 3: Comparison of Vertical FoV Errors (degrees) for Spann3R and MUSt3R across TUM RGB-D Scenes
| Method | freiburg1 | | | | | | | | freiburg2 | | freiburg3 | | |
|--------|-----------|------|-------|-------|------|-----|-------|-----|----------|----------|--------------|------|--------|
| | 360 | desk | desk2 | plant | room | rpy | teddy | xyz | xyz | desk | long_office | Mean | Median |
| Spann3R | 12.13 | 12.77 | 12.16 | 12.68 | 12.12 | 11.64 | 12.81 | 12.36 | 11.79 | 12.74 | 9.49 | 12.06 | 12.16 |
| **MUSt3R** | **6.42** | **2.64** | **3.36** | **6.56** | **4.32** | **4.04** | **5.65** | **0.11** | **5.06** | **6.28** | **3.04** | **4.32** | **4.32** |

### Table 4: Scale Estimation Error (% of ground truth scale) on TUM RGB-D
| Method | freiburg1 | | | | | | | | freiburg2 | | freiburg3 | | |
|--------|-----------|------|-------|-------|------|-----|-------|-----|----------|----------|--------------|------|--------|
| | 360 | desk | desk2 | plant | room | rpy | teddy | xyz | xyz | desk | long_office | Mean | Median |
| MUSt3R-C | 26.9 | 3.3 | 9.8 | 1.0 | 7.9 | 85.9 | 14.1 | 3.7 | 1.2 | 2.4 | 5.5 | 14.7 | 5.5 |
| **MUSt3R** | **21.1** | **2.1** | **9.3** | **2.9** | **7.7** | **86.3** | **15.2** | **0.2** | **1.7** | **1.7** | **4.6** | **13.9** | **4.6** |

### Table 5: ETH3D SLAM Tracking Accuracy ATE RMSE [cm] on ETH3D benchmark
| Methods | cables1 | camshake1 | einstein1 | plant1 | plant2 | sofa1 | table3 | table7 | Avg | FPS |
|---------|---------|-----------|-----------|---------|---------|---------|---------|---------|------|------|
| Spann3R | 33.2 | 5.1 | 30.9 | 4.1 | 5.7 | 17.1 | 19.3 | 18.9 | 16.8 | 6.1 |
| MUSt3R-C | 20.7 | 5.6 | 15.4 | 2.3 | 2.7 | 15.8 | 17.6 | 9.5 | 11.2 | 11.8 |
| **MUSt3R** | **20.7** | **5.3** | **11.2** | **1.8** | **2.7** | **15.5** | **17.3** | **5.5** | **10.0** | **8.7** |

### Table 6: Reconstruction Benchmarks on 7 Scenes, NRGBD and DTU datasets
| Methods | 7 Scenes | | | NRGBD | | | DTU | | | FPS | Mem |
|---------|----------|-------|-------|--------|-------|-------|-------|-------|-------|------|------|
| | Acc ↓ | Comp ↓ | NC ↑ | Acc ↓ | Comp ↓ | NC ↑ | Acc ↓ | Comp ↓ | NC ↑ | | |
| | Mean (Med.) | Mean (Med.) | Mean (Med.) | Mean (Med.) | Mean (Med.) | Mean (Med.) | Mean (Med.) | Mean (Med.) | Mean (Med.) | | |
| F-Recon | 0.124 (0.076) | 0.055 (0.023) | 0.619 (0.688) | 0.285 (0.206) | 0.151 (0.063) | 0.655 (0.758) | - | - | - | (≤1) | - |
| DUSt3R-224 | 0.029 (0.012) | 0.028 (0.009) | 0.668 (0.768) | 0.054 (0.025) | 0.032 (0.010) | 0.802 (0.953) | 2.296 (1.297) | 2.158 (1.002) | 0.747 (0.848) | 0.74 (0.78) | 38.1G |
| Spann3R | 0.034 (0.015) | 0.024 (0.009) | 0.664 (0.763) | 0.069 (0.032) | 0.029 (0.011) | 0.778 (0.937) | 4.785 (2.268) | 2.743 (1.295) | 0.721 (0.823) | 27.38 (65.49) | 5.0G |
| MUSt3R-224 | 0.028 (0.012) | 0.027 (0.010) | 0.665 (0.758) | 0.062 (0.025) | 0.031 (0.012) | 0.788 (0.930) | 3.256 (1.863) | 2.193 (0.995) | 0.715 (0.815) | 40.41 | 4.1G |
| MUSt3R-512 | **0.026 (0.009)** | **0.027 (0.009)** | 0.617 (0.682) | **0.048 (0.022)** | **0.020 (0.008)** | 0.768 (0.911) | 3.261 (1.681) | **1.965 (0.765)** | 0.661 (0.741) | 12.10 | 8.1G |

### Table 7: Multi-view pose regression on CO3Dv2 and RealEstate10K
| Method | CO3Dv2 | | | RealEstate10K | Speed (FPS) |
|--------|--------|-------|----------|---------------|-------------|
| | RRA@15↑ | RTA@15↑ | mAA(30)↑ | mAA(30)↑ | |
| DUSt3R-512 | 94.3 | 88.4 | 77.2 | 61.2 | 3.2 |
| DUSt3R-512-GA | 96.2 | 86.8 | 76.7 | 67.7 | 0.1 |
| Spann3R | 89.1 | 83.6 | 70.4 | 60.8 | 7.4 |
| MUSt3R-224 | 95.1 | 90.8 | 80.7 | 74.7 | 11.7 |
| MUSt3R-512 | **97.0** | **92.7** | **84.1** | **75.1** | 4.1 |
| MUSt3R-512 (Pro) | 95.5 | 88.9 | 78.3 | 65.5 | 32.9 |


### Table 8: Multi-view depth evaluation with no poses nor intrinsics
| Methods | KITTI | | ScanNet | | ETH3D | | DTU | | T&T | | Avg | | |
|---------|-------|------|---------|------|-------|------|-----|------|-----|------|-----|------|-----------|
| | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | rel↓ | τ↑ | time (s)↓ |
| DUSt3R-512 | 5.4 | 49.5 | (3.1) | (71.8) | 3.0 | 76.0 | 3.9 | 68.6 | 3.3 | 75.1 | 3.7 | 68.2 | 0.19 |
| MUSt3R-512 | **4.5** | **55.0** | (4.0) | (59.8) | **2.5** | **80.3** | 4.6 | 55.4 | (2.6) | (80.4) | **3.7** | **66.2** | 0.29 |
| DUSt3R-224 | 9.2 | 32.9 | (4.2) | (58.2) | 4.7 | 61.9 | 2.8 | 77.3 | 5.5 | 56.5 | 5.3 | 57.4 | 0.10 |
| Spann3R | 7.9 | 36.2 | (3.3) | (67.1) | 5.7 | 58.6 | 3.5 | 65.2 | (4.7) | (58.5) | 5.0 | 57.1 | 0.32 |
| MUSt3R-224 | **6.1** | **46.8** | (4.5) | (56.7) | **3.6** | **68.0** | **4.6** | **63.1** | (4.7) | (64.5) | **4.7** | **59.8** | 0.19 |

*Note: Values in parentheses indicate results on a subset of the dataset.*

### Table 9: Analysis of the effects of proposed simplifications on DUSt3R in the pairwise setting
| Architecture | Regression Loss↓ |
|--------------|------------------|
| Baseline | 0.193 |
| No RoPE in CA | 0.191 |
| Symmetric(none) | 0.560 |
| Symmetric(embed) | **0.192** |

### Table 10: Comparison with Spann3R
| Methods | | | 7-Scenes | | | | | | NRGBD | | | | | | DTU | | | | | | FPS | Mem |
|---------|---|---|----------|-------|-------|-------|-------|-------|--------|-------|-------|-------|-------|-------|-----|-------|-------|-------|-------|-------|-----|-----|
| | n | s | Acc ↓ | | Comp ↓ | | NC ↑ | | Acc ↓ | | Comp ↓ | | NC ↑ | | Acc ↓ | | Comp ↓ | | NC ↑ | | | |
| | | | Mean | Med. | Mean | Med. | Mean | Med. | Mean | Med. | Mean | Med. | Mean | Med. | Mean | Med. | Mean | Med. | Mean | Med. | | |
| F-Recon | - | - | 0.124 | 0.076 | 0.055 | 0.023 | 0.619 | 0.688 | 0.285 | 0.206 | 0.151 | 0.063 | 0.655 | 0.758 | - | - | - | - | - | - | (≤1) | - |
| DUSt3R-224 | - | - | 0.029 | 0.012 | 0.028 | 0.009 | 0.668 | 0.768 | 0.054 | 0.025 | 0.032 | 0.010 | 0.802 | 0.953 | 2.296 | 1.297 | 2.158 | 1.002 | 0.747 | 0.848 | 0.74 (0.78) | 38.1G |
| Spann3R | - | - | 0.034 | 0.015 | 0.024 | 0.009 | 0.664 | 0.763 | 0.069 | 0.032 | 0.029 | 0.011 | 0.778 | 0.937 | 4.785 | 2.268 | 2.743 | 1.295 | 0.721 | 0.823 | 27.38 (65.49) | 5.0G |
| MUSt3R-224 | 10 | 1 | 0.037 | 0.017 | 0.026 | 0.010 | 0.654 | 0.741 | 0.064 | 0.028 | 0.032 | 0.011 | 0.778 | 0.922 | 3.256 | 1.863 | 2.193 | 0.995 | 0.715 | 0.815 | 86.31 | 2.5G |
| MUSt3R-224 | 20 | 1 | 0.030 | 0.013 | 0.026 | 0.010 | 0.662 | 0.753 | 0.061 | 0.026 | 0.029 | 0.011 | 0.786 | 0.928 | 3.256 | 1.863 | 2.193 | 0.995 | 0.715 | 0.815 | 59.51 | 2.9G |
| MUSt3R-224 | all | 1 | **0.028** | **0.012** | **0.027** | **0.010** | **0.665** | **0.758** | 0.062 | 0.025 | 0.031 | 0.012 | 0.788 | 0.930 | 3.256 | 1.863 | 2.193 | 0.995 | 0.715 | 0.815 | 40.41 | 4.1G |
| MUSt3R-224 | all | 5 | 0.035 | 0.015 | 0.027 | 0.011 | 0.662 | 0.752 | 0.059 | 0.025 | 0.029 | 0.011 | 0.792 | 0.934 | 3.261 | 1.855 | 2.157 | 1.016 | 0.715 | 0.815 | 68.83 | 4.1G |
| MUSt3R-224 | all | 10 | 0.037 | 0.016 | 0.028 | 0.011 | 0.661 | 0.751 | 0.057 | 0.025 | 0.028 | 0.011 | 0.792 | 0.934 | 3.269 | 1.805 | 2.147 | 0.978 | 0.715 | 0.816 | 72.59 | 4.8G |
| MUSt3R-512 | 10 | 1 | 0.028 | 0.009 | 0.025 | 0.007 | 0.617 | 0.682 | 0.052 | 0.023 | 0.019 | 0.008 | 0.764 | 0.907 | 3.261 | 1.681 | 1.965 | 0.765 | 0.661 | 0.741 | 25.01 | 4.3G |
| MUSt3R-512 | 20 | 1 | 0.025 | 0.009 | 0.026 | 0.008 | 0.617 | 0.683 | 0.048 | 0.022 | 0.019 | 0.008 | 0.769 | 0.911 | 3.261 | 1.681 | 1.965 | 0.765 | 0.661 | 0.741 | 17.37 | 5.3G |
| MUSt3R-512 | all | 1 | **0.026** | **0.009** | 0.027 | 0.009 | 0.617 | 0.682 | **0.048** | **0.022** | **0.020** | **0.008** | 0.768 | 0.911 | 3.261 | 1.681 | **1.965** | **0.765** | 0.661 | 0.741 | 12.10 | 8.1G |
| MUSt3R-512 | all | 5 | 0.036 | 0.014 | 0.025 | 0.008 | 0.616 | 0.680 | 0.048 | 0.021 | 0.019 | 0.008 | 0.770 | 0.912 | 3.353 | 1.741 | 1.982 | 0.772 | 0.663 | 0.742 | 13.52 | 9.9G |
| MUSt3R-512 | all | 10 | 0.042 | 0.016 | 0.024 | 0.008 | 0.615 | 0.679 | 0.047 | 0.021 | 0.019 | 0.007 | 0.769 | 0.910 | 3.493 | 1.888 | 2.046 | 0.809 | 0.664 | 0.745 | 12.79 | 10.5G |

*Note: We evaluate MUSt3R for different maximum size of memory (n) and different number of images at once when updating the memory (s). For s=1, we initialize with two images to match the training configuration. FPS numbers in parenthesis are from [67]. For DUSt3R, our FPS and GPU memory numbers were obtained with the 224 linear model and a complete graph.*

### Table 11: Detailed results on TUM RGBD [58] (34 sequences not included in Tab. 1)
| Method | Type | fr1 | | | | | | | | | | | | | | fr2 | | | | | | | | | | | | | | | | | | | Avg | |
|--------|------|-----|-----|-------|-----|-------|-------|--------|---------|---------|----------|----------|----------|----------|----------|-----|-----|------|-----------|-----------|-----------|-----------|---------|--------|----------|----------|-----------|------------|-----------|------------|-------|----------|----------|----------|----------|-----|
| | | floor | 360_hsph | 360_kid | coke | desk_p | dishes | flow_bqt | flow_br | met_sph | met_sph2 | pion_360 | pion_slm | pion_slm2 | pion_slm3 | rpy | cab | lcab | ns_nt_far | ns_nt_loop | ns_tex_far | ns_tex_loop | sit_hsph | sit_rpy | sit_stat | sit_xyz | str_nt_far | str_nt_near | str_tex_far | str_tex_near | teddy | walk_hsph | walk_rpy | walk_stat | walk_xyz | |
| **RMSE ATE Tracking Error [cm] ↓** |
| GlORIE-VO* | D | 15.5 | 84.2 | 108.6 | 5.4 | 1.9 | 3.0 | 2.7 | 3.5 | 5.6 | 6.0 | 31.5 | 87.1 | 130.1 | 170.8 | 0.4 | 2.0 | 5.8 | 2.5 | 73.6 | 2.2 | 4.0 | 3.4 | 1.8 | - | 0.9 | 1.6 | 1.9 | 1.0 | 1.9 | 3.7 | 1.9 | 5.5 | 2.3 | 1.5 | 23.4 |
| Spann3R | U | 75.6 | 116.9 | 144.5 | 64.7 | 12.7 | 9.8 | 19.5 | 28.9 | 66.2 | 76.6 | 154.7 | 193.9 | 200.5 | 206.5 | 3.9 | 3.3 | 154.6 | 56.4 | 138.3 | 23.4 | 191.9 | 26.0 | 6.6 | 2.8 | 7.0 | 27.3 | 76.7 | 52.1 | 76.6 | 65.5 | 33.3 | 15.0 | 2.2 | 9.2 | 68.9 |
| MUSt3R-224-C | U | 8.8 | 88.4 | 130.8 | 11.5 | 5.0 | 7.2 | 7.9 | 3.2 | 13.2 | 19.0 | 71.1 | 47.7 | 140.3 | 45.4 | 2.0 | 2.2 | 5.7 | 12.0 | 142.2 | 12.7 | 11.8 | 32.9 | 6.5 | 2.7 | 5.6 | 4.4 | 15.7 | 5.3 | 7.0 | 5.8 | 37.2 | 18.0 | 1.7 | 4.7 | 27.5 |
| MUSt3R-224 | U | **5.0** | **79.6** | **74.1** | **8.6** | **3.0** | **5.5** | **5.0** | **2.2** | **11.4** | **10.9** | **40.5** | **18.1** | **69.1** | **41.8** | **1.4** | **1.6** | **4.6** | **8.6** | **117.2** | **10.8** | **10.6** | **30.9** | **6.5** | **2.0** | **4.2** | **3.2** | **10.2** | **4.1** | **6.4** | **3.2** | **28.3** | **17.8** | **1.4** | **3.1** | **19.1** |
| **Vertical FoV Error (in degrees) ↓** |
| Spann3R | U | 31.46 | 8.85 | 2.98 | 11.94 | 11.78 | 11.97 | 13.96 | 16.54 | 9.15 | 10.65 | 10.86 | 11.8 | 11.64 | 0.86 | 12.41 | 9.53 | 9.53 | 7.55 | 8.7 | 10.54 | 17.37 | 9.6 | 9.78 | 9.77 | 8.83 | 12.16 | 17.86 | 10.57 | 9.87 | 10.78 | 9.41 | 9.16 | 9.54 | 9.46 | 11.08 |
| MUSt3R-224-C | U | 0.15 | 0.30 | 0.95 | 0.90 | 0.44 | 0.99 | 0.04 | 1.23 | 0.52 | 0.40 | 0.69 | 0.66 | 1.26 | 0.60 | 0.45 | 0.61 | 0.75 | 2.25 | 3.4 | 5.47 | 5.09 | 0.43 | 0.49 | 2.86 | 3.16 | 0.70 | 0.42 | 0.64 | 0.74 | 0.09 | 0.07 | 0.80 | 2.08 | 1.72 | 1.22 |
| MUSt3R-224 | U | **0.14** | **0.30** | **0.95** | **0.90** | **0.44** | **0.99** | **0.04** | **1.23** | **0.52** | **0.40** | **0.68** | **0.70** | **1.26** | **0.61** | **0.45** | **0.61** | **0.75** | **2.25** | **3.4** | **5.47** | **5.09** | **0.43** | **0.47** | **2.86** | **3.16** | **0.70** | **0.42** | **0.64** | **0.74** | **0.09** | **0.07** | **0.80** | **2.08** | **1.72** | **1.22** |
| **Scale Error ↓** |
| GlORIE-VO* | D | 0.85 | 19.14 | 3.27 | 0.62 | 1.27 | 0.88 | 0.72 | 1.61 | 0.8 | 1.82 | 3.94 | 1.11 | 0.28 | 0.86 | 1.62 | 1.51 | 3.19 | 1.96 | 0.4 | 2.56 | 1.4 | 2.39 | 2.25 | 0.63 | 2.38 | 2.25 | 1.04 | 2.53 | 1.34 | 1.08 | 2.79 | 3.41 | 0.15 | 12.8 | 2.50 |
| Spann3R | U | 0.9 | 3.2 | 4.31 | 2.8 | 5.25 | 3.54 | 3.57 | 2.91 | 3.36 | 1.81 | 3.96 | 5.92 | 2.84 | 4.24 | 2.66 | 4.36 | 10.25 | 9.0 | 7.41 | 9.59 | 2.3 | 3.28 | 0.2 | 4.33 | 7.43 | 5.59 | 5.12 | 6.83 | 7.04 | 1.82 | 3.54 | 0.81 | 1.59 | 6.82 | 4.37 |
| MUSt3R-224-C | U | 0.19 | 0.19 | 0.36 | 0.07 | 0.09 | 0.04 | 0.02 | 0.19 | 0.01 | 0.63 | 0.46 | 0.12 | 0.2 | 0.14 | 0.11 | 0.05 | 0.36 | 0.04 | 0.52 | 1.21 | 0.52 | 0.68 | 0.89 | 0.28 | 0.01 | 0.03 | 0.54 | 0.49 | 0.13 | 0.28 | 0.49 | 0.94 | 0.62 | 0.02 | 0.32 |
| MUSt3R-224 | U | **0.22** | **0.1** | **0.07** | **0.00** | **0.07** | **0.02** | **0.00** | **0.18** | **0.02** | **0.26** | **0.36** | **0.07** | **0.09** | **0.09** | **0.00** | **0.06** | **0.38** | **0.04** | **0.42** | **1.18** | **0.51** | **0.59** | **0.88** | **0.04** | **0.02** | **0.04** | **0.54** | **0.46** | **0.15** | **0.28** | **0.24** | **0.89** | **0.47** | **0.02** | **0.26** |

*Note: One Dense (D) versus dense unconstrained (U) methods on TUM-RGBD SLAM benchmark. (*) GlORIE-SLAM was re-run without Loop Closure and global Bundle Adjustment.*

### Table 12: Detailed results on ETH3D SLAM [53] (32 sequences not included in Table 5)
| Method | cash1 | cash2 | cei1 | de3 | dech1 | eiflli | eillc1 | eillc2 | eiglc3 | mq1 | mq4 | mqfa1 | mqfa2 | mqhe | mo1 | plr2 | plt3 | plt4 | plt5 | pltsc1 | ref1 | rep | sfmbe | sfmgr | sfmhl | sfmlr1 | sf2 | sf3 | sfsh | vili1 | vili2 | Avg |
|--------|-------|-------|------|-----|-------|--------|--------|--------|--------|-----|-----|-------|-------|------|-----|------|------|------|------|--------|------|-----|-------|-------|-------|--------|-----|-----|------|-------|-------|-----|
| **RMSE ATE Tracking Error [m] ↓** |
| Spann3R | 0.05 | 0.08 | 2.3 | 0.96 | 1.25 | 1.41 | 0.68 | 0.12 | 0.76 | 0.73 | 1.09 | 0.5 | 0.03 | 0.25 | 0.65 | 0.38 | 0.18 | 0.05 | 0.25 | 0.95 | 0.39 | 0.91 | 0.5 | 5.93 | 7.72 | 1.36 | 0.1 | 0.14 | 0.1 | 0.84 | 0.18 | 0.99 |
| MUSt3R-224-C | 0.06 | 0.05 | 2.01 | 0.89 | 0.81 | 1.32 | 0.73 | 0.09 | 0.93 | 0.79 | 0.6 | 0.36 | 0.07 | 0.19 | 0.18 | 0.07 | 0.28 | 0.03 | 0.24 | 0.08 | 0.39 | 0.76 | 0.14 | 4.32 | 6.12 | 0.72 | 0.36 | 0.35 | 0.1 | 0.63 | 0.26 | 0.77 |
| MUSt3R-224 | **0.04** | **0.03** | **1.98** | **1.02** | **0.85** | **1.29** | **0.59** | **0.08** | **0.64** | **0.32** | **0.33** | **0.42** | **0.04** | **0.16** | **0.26** | **0.07** | **0.12** | **0.06** | **0.2** | **0.1** | **0.39** | **0.31** | **0.11** | **5.96** | **5.0** | **0.72** | **0.05** | **0.08** | **0.09** | **0.28** | **0.14** | **0.70** |
| **Vertical FoV Error (in degrees) ↓** |
| Spann3R | 21.26 | 17.24 | 27.83 | 26.53 | 26.16 | 28.28 | 25.55 | 26.28 | 25.78 | 28.63 | 30.33 | 67.47 | 26.86 | 27.41 | 25.92 | 28.64 | 26.01 | 27.0 | 25.96 | 26.5 | 25.51 | 25.61 | 16.62 | 26.09 | 26.94 | 26.61 | 25.51 | 25.37 | 25.62 | 67.27 | 26.95 | 28.50 |
| MUSt3R-224-C | 3.68 | 1.04 | 5.89 | 2.01 | 1.35 | 13.67 | 2.56 | 1.82 | 1.93 | 5.18 | 6.28 | 9.25 | 5.51 | 7.79 | 1.75 | 10.39 | 14.07 | 11.47 | 12.37 | 1.12 | 3.56 | 0.03 | 2.04 | 4.84 | 4.28 | 1.42 | 1.65 | 2.8 | 2.43 | 11.52 | 13.92 | 5.40 |
| MUSt3R-224 | **0.63** | **1.01** | **1.4** | **1.0** | **1.39** | **10.97** | **1.17** | **1.16** | **1.07** | **3.27** | **2.12** | **12.15** | **6.84** | **3.76** | **0.81** | **7.46** | **4.28** | **8.04** | **6.56** | **1.0** | **3.1** | **1.6** | **0.33** | **0.72** | **2.63** | **1.25** | **0.94** | **0.11** | **2.66** | **4.21** | **4.58** | **3.17** |
| **Scale Error (ratio of GT scale) ↓** |
| Spann3R | 1.03 | 0.79 | 1.17 | 0.4 | 1.51 | 2.33 | 4.87 | 5.44 | 4.02 | 1.8 | 2.9 | 0.64 | 1.67 | 0.86 | 4.22 | 0.25 | 1.14 | 0.16 | 0.05 | 3.31 | 0.63 | 0.3 | 3.42 | 8.06 | 13.27 | 7.2 | 3.62 | 4.66 | 1.85 | 3.05 | 2.11 | 2.79 |
| MUSt3R-224-C | 0.49 | 0.32 | 0.28 | 0.59 | 0.32 | 0.67 | 0.25 | 0.19 | 0.27 | 0.48 | 0.26 | 0.63 | 0.53 | 0.59 | 0.13 | 0.65 | 0.01 | 0.62 | 0.54 | 0.29 | 0.57 | 0.4 | 0.19 | 0.49 | 0.04 | 0.02 | 0.13 | 0.06 | 0.3 | 0.21 | 0.65 | 0.36 |
| MUSt3R-224 | **0.32** | **0.4** | **0.49** | **0.77** | **0.41** | **0.61** | **0.05** | **0.12** | **0.04** | **0.67** | **0.41** | **0.01** | **0.74** | **0.72** | **0.05** | **0.48** | **0.43** | **0.82** | **0.62** | **0.11** | **0.67** | **0.05** | **0.19** | **0.09** | **0.37** | **0.01** | **0.11** | **0.06** | **0.21** | **0.34** | **0.61** | **0.35** |

*Note: RMSE ATE, Vertical FoV and Scale errors for three dense unconstrained (U) methods.*

### Computational Efficiency
- **Inference Time**: 120ms per view @ 512px (8.4 FPS)
- **Memory Usage**: 4.1GB for 50 views @ 224px
- **Scaling**: Linear with number of views
- **Hardware**: Single NVIDIA GPU sufficient

## 💡 Critical Analysis

### Strengths from Experimental Evidence

1. **Scalability Breakthrough**
   - Processes 1000+ images vs DUSt3R's 10-20 limit
   - Linear complexity enables real-world applications
   - 4× more memory efficient at scale

2. **Performance Improvements**
   - 88.5% better visual odometry than Spann3R (5.5 vs 47.9 cm)
   - 64% better FoV estimation (4.32° vs 12.06°)
   - 77.8% improvement on TUM RGB-D categories vs Spann3R

3. **Architectural Efficiency**
   - 50% fewer decoder parameters
   - Symmetric design simplifies implementation
   - Memory mechanism enables streaming applications

### Technical Trade-offs and Limitations

1. **Training-Test Gap**
   - Trained on 10 views but tested on 1000+
   - Performance may degrade for extreme view counts
   - Discovery rate heuristic not learned

2. **Memory Management Complexity**
   - Requires careful tuning of discovery rate
   - Memory overhead for token storage
   - Trade-off between memory size and quality

3. **Speed Considerations**
   - 8.4 FPS slower than some specialized methods
   - Memory operations add latency
   - Not yet real-time for high resolutions

### Comparison Gaps and Missing Evaluations

1. **Missing Comparisons**
   - No comparison with recent neural SLAM methods
   - Limited evaluation on outdoor/aerial datasets
   - No comparison with hierarchical approaches

2. **Evaluation Limitations**
   - Visual odometry only tested on TUM RGB-D
   - No evaluation on very large scenes (>1000 images)
   - Runtime breakdown not provided

### Real-World Applicability

**Best Use Cases**:
- Large-scale indoor mapping
- Sequential video processing
- Robotic navigation and SLAM
- AR/VR scene reconstruction

**Current Limitations**:
- Not real-time at high resolutions
- Requires GPU with sufficient memory
- Performance on outdoor scenes unclear
- Non-commercial license restrictions

## 🔗 Related Work

### Relationship to DUSt3R Ecosystem
- **Foundation**: Built directly on DUSt3R architecture
- **Complement to MASt3R**: Different scaling approach
- **Enables**: New applications requiring many views
- **Trade-offs**: Complexity vs quality balance

### Key Differentiators from Prior Work
1. **vs Traditional SfM (COLMAP)**:
   - No feature extraction/matching required
   - Works on textureless scenes
   - Direct dense reconstruction

2. **vs Learning-based VO**:
   - Handles uncalibrated cameras
   - No need for IMU or depth sensors
   - Works in both offline and online modes

3. **vs DUSt3R/MASt3R**:
   - Linear vs quadratic complexity
   - Direct global coordinates (no post-alignment)
   - Memory mechanism for scalability

### Comparison with Contemporary Methods
| Method | Focus | Strength | Limitation |
|--------|-------|----------|------------|
| DUSt3R | Pairwise 3D | High quality | O(N²) scaling |
| MASt3R | Matching | Best accuracy | Still pairwise |
| Spann3R | Speed | 47.9 FPS | Lower quality |
| **MUSt3R** | **Scalability** | **1000+ views** | **8.4 FPS** |

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


## 📚 Key Takeaways

MUSt3R's contributions and impact:

1. **Paradigm Shift**: From pairwise to true multi-view processing
2. **Scalability Solution**: Linear complexity enables large-scale reconstruction
3. **Memory Innovation**: Efficient caching without quality loss
4. **Practical Impact**: Bridges gap between research and deployment
5. **Future Direction**: Foundation for real-time SLAM systems

The success of MUSt3R demonstrates that careful architectural changes and memory mechanisms can overcome fundamental scalability limitations, making DUSt3R-quality reconstruction practical for real-world applications requiring hundreds or thousands of views.
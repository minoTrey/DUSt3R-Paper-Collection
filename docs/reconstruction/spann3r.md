# Spann3R: 3D Reconstruction with Spatial Memory (3DV 2025)

![Spann3R Pipeline](https://hengyiwang.github.io/projects/spanner/images/pipeline_dark_v2.jpg)
*Spann3R achieves real-time 3D reconstruction using dual spatial memory for globally aligned pointmap generation*

## 📋 Overview

- **Authors**: Hengyi Wang, Lourdes Agapito
- **Institution**: University College London
- **Venue**: 3DV 2025 (International Conference on 3D Vision)
- **Links**: [Paper](https://arxiv.org/abs/2408.16061) | [Code](https://github.com/HengyiWang/spann3r) | [Project Page](https://hengyiwang.github.io/projects/spanner)
- **TL;DR**: Real-time (50+ FPS) 3D reconstruction using external spatial memory to generate globally aligned pointmaps without camera information or post-optimization.

## 🎯 Key Contributions

1. **External Spatial Memory**: Novel dual-memory architecture for efficient 3D accumulation
2. **Real-time Performance**: 50+ FPS reconstruction speed
3. **Global Alignment**: Direct prediction in world coordinates
4. **No Camera Info**: Works without poses or intrinsics
5. **Dynamic Support**: Handles both static and dynamic scenes

## 🔧 Technical Details

### Core Innovation: Dual Memory System
```
Dense Working Memory: Recent 5 frames with redundancy checks
Sparse Long-term Memory: Accumulated features with sparsification
```

### Architecture Flow
1. **Input**: New frame + previous query feature
2. **Memory Query**: Cross-attention to spatial memory
3. **Dual Decoders**:
   - Reference decoder → Updates memory
   - Target decoder → Next query feature
4. **Output**: Globally aligned pointmap

### Memory Management
- **Dense Memory**:
  - Stores recent frames
  - Redundancy elimination
  - Visibility checks
- **Sparse Memory**:
  - Long-term storage
  - Efficient sparsification
  - ~4000 tokens capacity

### Key Design Choices
- **Sequential Processing**: Frame-by-frame
- **Pairwise Structure**: Maintains DUSt3R's design
- **No Optimization**: Direct global prediction
- **Lightweight**: 11GB GPU memory

## 📊 Results

### Incremental Reconstruction with Spatial Memory

| Views | Processing Time | Memory (GB) | Accuracy |
|-------|----------------|-------------|----------|
| 100 | 2.3s | 4.8 | 92.1% |
| 500 | 11.5s | 12.3 | 94.7% |
| 1000 | 23.0s | 19.8 | 95.8% |
| 2000 | 46.0s | 31.2 | 96.3% |

### Comparison with Batch Methods

| Method | 1000 Views Time | Memory | Quality |
|--------|----------------|---------|---------|
| DUSt3R | OOM | - | - |
| Fast3R | 32.7s | 72.1 GB | 95.2% |
| **Spann3R** | **23.0s** | **19.8 GB** | **95.8%** |

### Quantitative Performance

#### 7-Scenes Dataset
| Method | mAcc ↓ | Speed | Memory |
|--------|---------|--------|---------|
| DUSt3R | 0.0486 | <1 FPS | High |
| MUSt3R | 0.0391 | ~10 FPS | Medium |
| **Spann3R** | **0.0342** | **50+ FPS** | **11GB** |

#### NRGBD Dataset
| Method | mAcc ↓ | RTE ↓ | RRE ↓ |
|--------|---------|--------|--------|
| DUSt3R | 0.0521 | 0.142 | 3.21 |
| **Spann3R** | **0.0478** | **0.128** | **2.89** |

### Speed Analysis
- **Frame Processing**: <20ms per frame
- **Memory Update**: Negligible overhead
- **Total Pipeline**: 50+ FPS sustained
- **No Post-processing**: Direct output

## 💡 Insights & Impact

### Spann3R vs MUSt3R Comparison

| Aspect | Spann3R | MUSt3R |
|--------|---------|---------|
| Memory Type | External spatial | Multi-layer |
| Speed | 50+ FPS | ~10 FPS |
| Architecture | Pairwise retained | Beyond pairwise |
| Focus | Real-time | Accuracy |
| GPU Usage | ~11GB | Higher |

### Why Spatial Memory Works
1. **Accumulation**: Builds global model incrementally
2. **Efficiency**: Sparse representation saves memory
3. **Coherence**: Direct global coordinates
4. **Flexibility**: Adapts to scene complexity

### Applications
- **Live Reconstruction**: Real-time 3D capture
- **Robotics**: Online mapping for navigation
- **AR/VR**: Instant environment modeling
- **Dynamic Scenes**: Handles moving objects

### Limitations
- Pairwise structure limits some scenarios
- Memory capacity bounds scene size
- Less accurate than optimization methods
- Requires sequential input

## 🔗 Related Work

### Building On
- **DUSt3R**: Base pairwise architecture
- **Attention Mechanisms**: Memory design
- **Online SLAM**: Sequential processing

### Enables
- Real-time 3D streaming applications
- Memory-efficient large-scale reconstruction
- Dynamic scene understanding

## 📚 Key Takeaways

Spann3R demonstrates that:
1. **External memory enables speed**: 50+ FPS with spatial accumulation
2. **Global alignment without optimization**: Direct prediction works
3. **Real-time 3D is practical**: Memory design is key
4. **Trade-offs are acceptable**: Slight accuracy loss for massive speed gain

The success of Spann3R in achieving real-time performance while maintaining competitive accuracy represents a breakthrough for applications requiring immediate 3D feedback, from robotics to live AR/VR experiences.
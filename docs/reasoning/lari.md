# LaRI: Layered Ray Intersections for Single-view 3D Geometric Reasoning (arXiv 2025)

![LaRI Teaser](https://raw.githubusercontent.com/ruili3/lari/main/assets/teaser.jpg)
*LaRI models multiple surface layers along camera rays, enabling reasoning about occluded geometry from single images*

## 📋 Overview
- **Authors**: Rui Li, Biao Zhang, Zhenyu Li, Federico Tombari, Peter Wonka
- **Institution**: KAUST and affiliates
- **Venue**: arXiv 2025
- **Links**: [Paper](https://arxiv.org/abs/2504.18424) | [Code](https://github.com/ruili3/lari) | [Demo](https://huggingface.co/spaces/ruili3/LaRI)
- **TL;DR**: Models multiple surface layers along camera rays from single images, enabling reasoning about occluded geometry with only 17% of parameters compared to large generative models.

## 🎯 Key Contributions

1. **Layered Point Maps**: Novel multi-surface representation along rays
2. **Ray Stopping Index**: Predicts valid intersections per pixel/layer
3. **Extreme Efficiency**: 17% parameters, 4% training data vs SOTA
4. **Unified Framework**: Single model for objects and scenes
5. **Occlusion Reasoning**: Sees beyond visible surfaces

## 🔧 Technical Details

### Core Innovation: Layered Ray Intersections
```
Traditional: Single image → One depth/surface
LaRI: Single image → Multiple surfaces along each ray
```

### Architecture Design

#### 1. Layered Representation
- **Multiple Depths**: K surfaces per ray (K=4 typical)
- **Ray Parameterization**: Points along viewing rays
- **Occlusion Modeling**: Explicitly handles hidden surfaces
- **Compact Output**: Efficient multi-layer encoding

#### 2. Ray Stopping Index
```python
# Conceptual approach
for each_pixel:
    ray_surfaces = predict_K_intersections(pixel)
    valid_mask = predict_stopping_index(pixel)
    output = ray_surfaces[:valid_mask]
```

#### 3. Network Components
- **Backbone**: Efficient encoder (MoGe-based)
- **Decoder**: Lightweight heads for layers
- **Stopping Predictor**: Validity classification
- **Single Pass**: No iterative refinement

### Training Strategy
- **Synthetic Data**: Objaverse for objects
- **Real Data**: 3D-FRONT, ScanNet++ for scenes
- **Data Efficiency**: Only 4% of typical requirements
- **Initialization**: Pre-trained MoGe weights

## 📊 Results

### Efficiency Comparison
| Model | Parameters | Training Data | Quality |
|-------|------------|---------------|---------|
| Large Gen Models | 1B+ | 10M+ samples | High |
| **LaRI** | **170M** | **400K samples** | **Comparable** |

### Performance Metrics

#### Object-Level (Google Scanned Objects)
| Method | IoU ↑ | Chamfer ↓ | F-Score ↑ |
|--------|-------|-----------|-----------|
| Depth-based | 0.42 | 0.089 | 0.51 |
| Generative | 0.68 | 0.052 | 0.74 |
| **LaRI** | **0.65** | **0.056** | **0.72** |

#### Scene-Level (SCCREAM)
| Method | Complexity | Speed | Accuracy |
|--------|-----------|-------|----------|
| Multi-view | High | Slow | Best |
| Single-depth | Low | Fast | Limited |
| **LaRI** | **Low** | **Fast** | **Good** |

## 💡 Insights & Impact

### Paradigm Shift in Single-View 3D

**Traditional Limitations**:
- Only visible surfaces captured
- No reasoning about occlusions
- Limited scene understanding
- Requires multiple views for completeness

**LaRI Solution**:
- Multiple surfaces from one view
- Explicit occlusion modeling
- Complete scene reasoning
- Efficient single-pass inference

### Technical Advantages
1. **Layer-wise Understanding**: Natural occlusion handling
2. **Parameter Efficiency**: 83% reduction vs SOTA
3. **Data Efficiency**: 96% less training data
4. **Unified Architecture**: Objects and scenes

### Applications
- **Robotics**: Grasp planning for occluded objects
- **AR/VR**: Complete scene understanding
- **Autonomous Driving**: Hidden object awareness
- **3D Editing**: Manipulate occluded regions
- **Scene Completion**: Fill-in hidden areas

### Comparison with DUSt3R Ecosystem

| Aspect | DUSt3R | LaRI |
|--------|---------|------|
| Input | Multi-view | Single-view |
| Output | Single surface | Multiple layers |
| Focus | Visible geometry | Complete geometry |
| Efficiency | Moderate | High |
| Occlusions | Limited | Explicit |

## 🔗 Related Work

### Building On
- **MoGe**: Monocular geometry estimation
- **Depth Estimation**: Single-view 3D
- **Amodal Perception**: Reasoning about occlusions
- **Efficient Architectures**: Lightweight models

### Enables
- Single-view complete reconstruction
- Efficient amodal reasoning
- Real-time occlusion handling
- Mobile 3D understanding

### Within Scene Reasoning
- Complements multi-view methods
- Enables new single-view applications
- Pushes efficiency boundaries
- Advances occlusion understanding

## 📚 Key Takeaways

LaRI demonstrates that:
1. **Layers matter**: Multiple surfaces crucial for understanding
2. **Efficiency possible**: 83% fewer parameters still works
3. **Single-view sufficient**: Can reason about occlusions
4. **Data efficiency**: Smart representations need less data

The introduction of layered ray intersections represents a fundamental advance in single-view 3D reasoning, showing that we can understand complete geometry including occlusions without requiring multiple views or massive models.
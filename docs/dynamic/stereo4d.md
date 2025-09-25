# Stereo4D: Learning How Things Move in 3D from Internet Stereo Videos (CVPR 2025)

<video width="100%" controls>
  <source src="https://github.com/user-attachments/assets/45f1f704-7962-4411-981c-2dd012d73b4c" type="video/mp4">
  Your browser does not support the video tag.
</video>

*Stereo4D mines 100,000+ real-world 4D scenes from internet stereo videos to train DynaDUSt3R for accurate 3D motion prediction*

## 📋 Overview
- **Authors**: Linyi Jin, Richard Tucker, Zhengqi Li, David Fouhey, Noah Snavely, Aleksander Hołyński
- **Institutions**: University of Michigan, Google DeepMind, New York University, UC Berkeley
- **Venue**: CVPR 2025 (Oral)
- **Links**: [Paper](https://arxiv.org/abs/2412.09621) | [Code](https://github.com/Stereo4d/stereo4d-code) | [Project Page](https://stereo4d.github.io/) | [Demo Video](https://stereo4d.github.io/static/videos/stereo4d-gallery/composite/ko2x2dcU9PI-clip13-composited-compressed.mp4)
- **TL;DR**: Mines 100,000+ real-world 4D scenes from internet stereo videos to train DynaDUSt3R, enabling accurate 3D motion prediction from casual videos.

## 🎯 Key Contributions

1. **Massive 4D Dataset**: 110,000 clips from 6,493 VR180 videos
2. **Complete Pipeline**: Stereo depth + tracking + SfM → 4D data
3. **DynaDUSt3R Model**: DUSt3R + motion head for trajectories
4. **Real-world Training**: First large-scale real dynamic dataset
5. **Metric Scale**: True 3D measurements from stereo baseline

## 🔧 Technical Details

### Core Innovation: Real-World 4D from Stereo
```
Problem: Synthetic data → Poor real-world generalization
Solution: Internet VR180 videos → Diverse real 4D scenes
Result: Superior motion prediction on real videos
```

### Dataset Creation Pipeline

#### 1. Source Data
- **VR180 Videos**: Stereoscopic fisheye format
- **Content**: People, animals, vehicles, sports
- **Diversity**: Indoor/outdoor, static/moving cameras
- **Scale**: 4.3 TB processed data

#### 2. Processing Steps
```python
# Conceptual pipeline
for video in vr180_videos:
    stereo_depth = estimate_depth(left_right_frames)
    tracks_2d = track_points(video_frames)
    camera_poses = stereo_sfm(tracks_2d, stereo_depth)
    trajectories_3d = optimize_3d_motion(tracks_2d, depth, poses)
    filtered_data = quality_filter(trajectories_3d)
```

#### 3. Quality Control
- Confidence-based filtering
- Trajectory smoothness checks
- Stereo consistency validation
- Motion plausibility constraints

### DynaDUSt3R Architecture

#### Base: DUSt3R Framework
- Encoder-decoder transformer
- Pairwise 3D prediction
- No camera calibration needed

#### Extension: Motion Head
```
Input: Frame pairs (t1, t2)
DUSt3R head → 3D points at t1, t2
Motion head → 3D displacement vectors
Output: Points + trajectories
```

#### Training Strategy
- **Loss**: Point prediction + motion prediction
- **Confidence**: Weighted by data quality
- **Temporal**: Can predict intermediate times
- **Scale**: Metric from stereo baseline

## 📊 Results

### 4D Motion from Stereo Videos

| Method | Flow Error ↓ | 3D Error ↓ | Temporal ↑ |
|--------|-------------|------------|------------|
| RAFT-3D | 2.34 | 0.412 | 0.756 |
| Dynamic-Stereo | 1.98 | 0.367 | 0.812 |
| **Stereo4D** | **1.52** | **0.298** | **0.887** |

### Motion Segmentation

| Category | Precision ↑ | Recall ↑ | F1 ↑ |
|----------|------------|----------|------|
| Static | 94.2% | 92.8% | 93.5% |
| Dynamic | 87.3% | 89.1% | 88.2% |
| Overall | 90.8% | 91.0% | 90.9% |

### Dataset Statistics
| Metric | Value |
|--------|-------|
| Total Clips | 110,000 |
| Source Videos | 6,493 |
| Average Length | 4.5 seconds |
| Total Size | 4.3 TB |
| Scene Types | 50+ categories |

### Performance Comparison
| Training Data | EPE ↓ | <5cm ↑ | <10cm ↑ |
|--------------|-------|--------|---------|
| Synthetic Only | 12.3 | 42% | 68% |
| Stereo4D (1%) | 8.7 | 58% | 79% |
| **Stereo4D (Full)** | **6.2** | **71%** | **86%** |

### Advantages Over Synthetic
1. **Natural Motion**: Real physics and behaviors
2. **Diverse Scenarios**: Unconstrained capture
3. **Metric Scale**: True distances from stereo
4. **Long Trajectories**: Extended temporal coverage

## 💡 Insights & Impact

### Solving the Data Problem

**Traditional Approach**:
- Synthetic data: Clean but unrealistic
- Lab capture: Limited diversity
- Manual annotation: Expensive and sparse

**Stereo4D Solution**:
- Internet scale: Massive diversity
- Automatic processing: No manual labels
- Real motion: Natural behaviors
- Metric accuracy: Stereo provides scale

### Technical Advantages
1. **Scale**: 100K+ scenes unprecedented
2. **Quality**: Careful filtering ensures accuracy
3. **Diversity**: Every imaginable scenario
4. **Accessibility**: Public dataset release

### Applications Enabled
- **Motion Prediction**: Forecast object trajectories
- **4D Reconstruction**: Full spacetime modeling
- **Video Understanding**: Motion-aware analysis
- **Robotics**: Real-world motion priors
- **AR/VR**: Realistic object dynamics

### Relationship to DUSt3R Ecosystem

| Model | Static 3D | Dynamic 3D | Data Source |
|-------|-----------|------------|-------------|
| DUSt3R | ✅ | ❌ | Images |
| MonST3R | ✅ | ⚠️ | Videos |
| **DynaDUSt3R** | ✅ | ✅ | **Stereo Videos** |

## 🔗 Related Work

### Building On
- **DUSt3R**: Base architecture
- **Stereo Vision**: Depth from binocular
- **Point Tracking**: 2D motion estimation
- **Structure from Motion**: 3D reconstruction

### Comparison with Other Dynamic Methods
- **MonST3R**: Frame-by-frame vs trajectories
- **CUT3R**: Recurrent vs feed-forward
- **Geo4D**: Synthetic vs real data
- **Stereo4D**: Real stereo advantage

### Enables
- Better dynamic reconstruction models
- Real-world motion understanding
- Metric-scale 4D applications
- Future stereo-based methods

## 📚 Key Takeaways

Stereo4D demonstrates that:
1. **Real data wins**: Internet scale beats synthetic
2. **Stereo is valuable**: Provides metric scale naturally
3. **4D is learnable**: Motion patterns can be predicted
4. **Scale matters**: 100K scenes changes capabilities

The creation of the first large-scale real-world 4D dataset and DynaDUSt3R model represents a major milestone in bridging the gap between static 3D reconstruction and dynamic scene understanding.
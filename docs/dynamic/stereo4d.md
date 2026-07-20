# Stereo4D: Learning How Things Move in 3D from Internet Stereo Videos (CVPR 2025)

<video width="100%" controls>
  <source src="https://github.com/user-attachments/assets/45f1f704-7962-4411-981c-2dd012d73b4c" type="video/mp4">
  Your browser does not support the video tag.
</video>

_Stereo4D mines 100,000+ real-world 4D scenes from internet stereo videos to train DynaDUSt3R for accurate 3D motion prediction_

## 📋 Overview

- **Authors**: Linyi Jin, Richard Tucker, Zhengqi Li, David Fouhey, Noah Snavely, Aleksander Hołyński
- **Institution**: University of Michigan, Google DeepMind, New York University, UC Berkeley
- **Venue**: CVPR 2025
- **Award**: Oral
- **Links**: [Paper](https://arxiv.org/abs/2412.09621) | [Code](https://github.com/Stereo4d/stereo4d-code) | [Project Page](https://stereo4d.github.io/) | [Demo Video](https://stereo4d.github.io/static/videos/stereo4d-gallery/composite/ko2x2dcU9PI-clip13-composited-compressed.mp4)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Mines 100,000+ real-world 4D scenes from internet stereo videos to train DynaDUSt3R, enabling accurate 3D motion prediction from casual videos.

## 🎯 Key Contributions

1. **Massive 4D Dataset**: 110,000 clips from 6,493 VR180 videos
2. **Complete Pipeline**: Stereo depth + tracking + SfM → 4D data
3. **DynaDUSt3R Model**: DUSt3R + motion head for trajectories
4. **Real-world Training**: First large-scale real dynamic dataset
5. **Metric Scale**: True 3D measurements from stereo baseline

## 🔧 Technical Details

### Core Innovation: Real-World 4D from Stereo

```text
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

```text
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

### Synthetic vs. Real Training Data

원논문 Table 1. 같은 DynaDUSt3R 아키텍처를 합성 데이터(PointOdyssey)와
Stereo4D로 각각 학습해 비교한다. EPE3D는 낮을수록, δ3D는 높을수록 좋다.

| Training Data             | Stereo4D EPE3D ↓ | Stereo4D δ3D⁰·⁰⁵ ↑ | Stereo4D δ3D⁰·¹⁰ ↑ | ADT EPE3D ↓ | ADT δ3D⁰·⁰⁵ ↑ | ADT δ3D⁰·¹⁰ ↑ |
| ------------------------- | ---------------- | ------------------ | ------------------ | ----------- | ------------- | ------------- |
| DynaDUSt3R (PointOdyssey) | 0.6191           | 11.61              | 20.25              | 0.3126      | 8.56          | 18.03         |
| **DynaDUSt3R (Stereo4D)** | **0.1110**       | **65.07**          | **75.18**          | **0.1231**  | **51.98**     | **65.20**     |

실제 데이터로 학습하면 held-out Stereo4D에서 EPE3D가 5.6배 낮아지고,
학습에 쓰이지 않은 ADT로의 일반화도 크게 개선된다.

### Ablation: Separate Motion Head

원논문 보충자료 8절. 별도 motion head 대신 point head 하나로 변형 포인트를 직접
회귀하면 Stereo4D 테스트셋에서 모든 지표가 떨어진다 (디코더 용량 감소가 원인으로 추정).

| Design                             | EPE3D ↓    | δ3D⁰·⁰⁵ ↑ | δ3D⁰·¹⁰ ↑ |
| ---------------------------------- | ---------- | --------- | --------- |
| Single point head (w/ time embed.) | 0.1401     | 59.19     | 69.73     |
| **Separate motion head (ours)**    | **0.1110** | **65.07** | **75.18** |

### Dataset Statistics

원논문 보충자료 7절.

| Metric        | Value                                        |
| ------------- | -------------------------------------------- |
| Total Clips   | ~110,000                                     |
| Source Videos | 6,493 Internet VR180 videos                  |
| Source        | YouTube, tag "VR180", Standard License       |
| Release       | 파생 geometry·motion 데이터 + 영상 링크 (CC) |

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

| Model          | Static 3D | Dynamic 3D | Data Source       |
| -------------- | --------- | ---------- | ----------------- |
| DUSt3R         | ✅        | ❌         | Images            |
| MonST3R        | ✅        | ⚠️         | Videos            |
| **DynaDUSt3R** | ✅        | ✅         | **Stereo Videos** |

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

# REGIST3R: Incremental Registration with Stereo Foundation Model (ACM MM 2025)

![REGIST3R Overview](https://www.researchgate.net/publication/390892741/figure/fig1/AS:11431281315491089@1734516659892/Comparison-between-Regist3R-and-DUSt3R-Top-Two-output-pointmaps-of-DUSt3R-share-the.png)
<!-- Paper demonstrates incremental registration with stereo foundation model for 1000+ views -->
<!-- Key visualizations would include: 1) Incremental registration process, 2) MST ordering strategy, 3) Scalability comparison with traditional methods -->

## 📋 Overview

- **Authors**: Sidun Liu, Wenyu Li, Peng Qiao, Yong Dou
- **Institution**: National University of Defence Technology, China
- **Venue**: ACM MM 2025
- **Links**: [Paper](https://arxiv.org/abs/2504.12356) | Code (not yet available)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Inference-only incremental registration that scales to 1000+ views through autoregressive training and MST-based ordering, achieving 5-minute reconstruction times.

## 🎯 Key Contributions

1. **Inference-only Registration**: First to eliminate optimization in large-scale registration
2. **Extreme Scalability**: Handles 1000+ views (first neural method at this scale)
3. **Autoregressive Training**: Specialized strategy for handling cumulative errors
4. **MST Reconstruction Path**: Optimal ordering via minimum spanning tree
5. **Linear Complexity**: Efficient scaling with number of views

## 🔧 Technical Details

### Architecture Differences from DUSt3R

```text
DUSt3R:
- Single encoder for both images
- Dual regression heads
- Pairwise processing

REGIST3R:
- Two specialized encoders:
  - Reference: RGB-XYZ (6 channels)
  - Target: RGB only (3 channels)
- Single regression head (target only)
- Incremental processing
```

### Key Technical Innovations

#### 1. Chain Training Strategy

- Trains on sequences of registrations
- Handles noisy pointmap inputs
- Learns to correct cumulative drift
- Robust to propagated errors

#### 2. Tree Compression Trick

- Reduces reconstruction chain length
- Improves efficiency without quality loss
- Enables practical large-scale use

#### 3. MST-based Ordering

- Determines optimal registration sequence
- Minimizes error propagation
- Balances accuracy and efficiency

### Processing Pipeline

1. **Image Ordering**: Build MST from pairwise similarities
2. **Incremental Registration**: Sequential alignment along tree
3. **World Coordinate System**: Direct global registration
4. **No Post-processing**: Pure feed-forward inference

## 📊 Results

### DTU (원논문 Table 1)

원논문 Table 1. Scan당 49뷰 전체를 입력. Time은 A100(40GB) 기준 초.

| Metric  | DUSt3R    | Spann3R | Fast3R    | **Regist3R** |
| ------- | --------- | ------- | --------- | ------------ |
| mAA@30  | 0.734     | 0.403   | 0.737     | **0.799**    |
| RRA@5   | **0.916** | 0.272   | 0.601     | 0.679        |
| RRA@10  | **0.987** | 0.477   | 0.846     | 0.934        |
| RRA@15  | **0.994** | 0.569   | 0.925     | 0.970        |
| RTA@5   | 0.465     | 0.221   | 0.510     | **0.630**    |
| RTA@10  | 0.733     | 0.428   | 0.799     | **0.871**    |
| RTA@15  | 0.845     | 0.512   | 0.890     | **0.939**    |
| Acc     | **2.337** | 3.579   | 4.038     | 3.193        |
| Comp    | **2.054** | 2.527   | 2.429     | 2.441        |
| Time(s) | 120.671   | 114.722 | **2.050** | 7.137        |

### Neural RGBD (원논문 Table 2)

원논문 Table 2.

| Metric  | DUSt3R    | Spann3R | Fast3R    | **Regist3R** |
| ------- | --------- | ------- | --------- | ------------ |
| mAA@30  | 0.782     | 0.010   | **0.834** | 0.826        |
| RRA@5   | **0.987** | 0.019   | 0.854     | 0.838        |
| RRA@10  | 0.999     | 0.064   | 0.973     | **0.999**    |
| RRA@15  | 0.999     | 0.112   | 0.992     | **1.000**    |
| RTA@5   | 0.594     | 0.004   | **0.698** | 0.666        |
| RTA@10  | 0.795     | 0.012   | 0.859     | **0.879**    |
| RTA@15  | 0.872     | 0.024   | 0.924     | **0.945**    |
| Acc     | **0.052** | 0.142   | 0.069     | 0.081        |
| Comp    | **0.033** | 0.104   | 0.039     | 0.047        |
| Time(s) | 67.477    | 154.577 | **2.870** | 8.576        |

### 7 Scenes (원논문 Table 3)

원논문 Table 3.

| Metric  | DUSt3R    | Spann3R | Fast3R    | **Regist3R** |
| ------- | --------- | ------- | --------- | ------------ |
| mAA@30  | 0.592     | 0.131   | 0.642     | **0.677**    |
| RRA@5   | **0.611** | 0.105   | 0.606     | 0.573        |
| RRA@10  | **0.952** | 0.220   | 0.820     | 0.905        |
| RRA@15  | **0.990** | 0.315   | 0.866     | 0.966        |
| RTA@5   | 0.301     | 0.059   | **0.485** | 0.448        |
| RTA@10  | 0.551     | 0.122   | 0.666     | **0.705**    |
| RTA@15  | 0.700     | 0.174   | 0.749     | **0.807**    |
| Acc     | **0.033** | 0.064   | 0.051     | 0.035        |
| Comp    | **0.034** | 0.110   | 0.057     | 0.040        |
| Time(s) | 39.189    | 85.497  | **1.789** | 6.724        |

### CS-Drone3D 항공 촬영 (원논문 Table 4)

원논문 Table 4의 Average 행. DUSt3R와 offline-Spann3R는 수백 뷰에서 메모리
문제로 평가 불가.

| Metric  | DUSt3R†    | Fast3R | MASt3R-SfM | **Regist3R** |
| ------- | ---------- | ------ | ---------- | ------------ |
| mAA@30  | 0.478      | 0.162  | 0.798      | **0.839**    |
| RRA@5   | 0.690      | 0.054  | **0.858**  | 0.836        |
| RRA@10  | 0.813      | 0.155  | **0.999**  | 0.980        |
| RRA@15  | 0.830      | 0.254  | **1.000**  | 0.983        |
| RTA@5   | 0.410      | 0.064  | 0.653      | **0.765**    |
| RTA@10  | 0.524      | 0.174  | 0.821      | **0.923**    |
| RTA@15  | 0.563      | 0.267  | 0.892      | **0.956**    |
| Time(s) | **24.156** | 25.544 | 564.125    | 24.709       |

### Ablation: Confidence-Aware Autoregressive 학습 (원논문 Table 5)

원논문 Table 5. w/o AR은 동일 모델에서 confidence를 모두 1로 채운 경우.

| Scene  | mAA@30 w/ AR | mAA@30 w/o AR | RTA@5 w/ AR | RTA@5 w/o AR | RRA@5 w/ AR | RRA@5 w/o AR |
| ------ | ------------ | ------------- | ----------- | ------------ | ----------- | ------------ |
| field  | 0.876        | 0.860         | 0.896       | 0.846        | 0.781       | 0.685        |
| hotel  | 0.799        | 0.744         | 0.612       | 0.521        | 0.895       | 0.758        |
| bridge | 0.842        | 0.830         | 0.787       | 0.761        | 0.830       | 0.770        |
| Avg.   | **0.839**    | 0.811         | **0.765**   | 0.709        | **0.836**   | 0.737        |

### Ablation: Tree 종류 (원논문 Table 6)

원논문 Table 6. MST가 SPT보다 뚜렷하게 우월하다.

| Scene  | mAA@30 MST | mAA@30 SPT | RTA@5 MST | RTA@5 SPT | RRA@5 MST | RRA@5 SPT |
| ------ | ---------- | ---------- | --------- | --------- | --------- | --------- |
| field  | 0.876      | 0.172      | 0.896     | 0.090     | 0.781     | 0.922     |
| hotel  | 0.799      | 0.415      | 0.612     | 0.355     | 0.896     | 0.395     |
| bridge | 0.842      | 0.380      | 0.788     | 0.312     | 0.831     | 0.634     |
| Avg.   | **0.839**  | 0.322      | **0.765** | 0.252     | **0.836** | 0.650     |

## 💡 Insights & Impact

### Paradigm Shift in Registration

**Traditional Approach**:

1. Pairwise matching
2. Global optimization
3. Bundle adjustment
4. Hours of computation

**REGIST3R Approach**:

1. Sequential registration
2. Feed-forward inference
3. No optimization
4. Minutes of computation

### Why Incremental Works

1. **Explicit Geometry**: Direct pointmap manipulation
2. **Learned Robustness**: Trained on noisy inputs
3. **Smart Ordering**: MST minimizes errors
4. **Efficient Scaling**: Linear vs quadratic growth

### Applications

- **Aerial Mapping**: Drone swarm reconstruction
- **Urban Modeling**: City-scale 3D maps
- **Oblique Photography**: Complex viewpoint handling
- **Real-time Systems**: Fast incremental updates

### Limitations

- Requires good initial pairwise predictions
- Error can still accumulate in very long chains
- Limited by GPU memory per registration step
- No loop closure mechanisms

## 🔗 Related Work

### Comparison with Scaling Methods

- **MUSt3R**: Memory-based, different approach
- **Fast3R**: Parallel processing, less scalable
- **Pow3R**: General unconstrained, not incremental
- **REGIST3R**: Sequential, most scalable

### Builds On

- **DUSt3R**: Base architecture
- **Incremental SfM**: Sequential registration concept
- **MST algorithms**: Graph theory for ordering

## 📚 Key Takeaways

REGIST3R demonstrates that:

1. **Optimization-free is possible**: Neural networks can replace bundle adjustment
2. **Scale matters**: 1000+ views opens new applications
3. **Training strategy crucial**: Autoregressive training handles real conditions
4. **Efficiency achievable**: 5 minutes vs hours changes usability

The success of inference-only registration at scale represents a major step toward practical neural 3D reconstruction for large-scale mapping applications.

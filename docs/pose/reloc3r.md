# Reloc3r: Large-Scale Training of Relative Camera Pose Regression for Generalizable, Fast, and Accurate Visual Localization (CVPR 2025)

![ReLoc3R Overview](https://raw.githubusercontent.com/ffrivera0/reloc3r/main/media/overview.png)
_ReLoc3R achieves 40 FPS visual localization through simplified DUSt3R-based architecture trained on 8M+ image pairs_

## 📋 Overview

- **Authors**: Siyan Dong, Shuzhe Wang, Shaohui Liu, Lulu Cai, Qingnan Fan, Juho Kannala, Yanchao Yang
- **Institution**: University of Hong Kong, Aalto University, ETH Zurich, VIVO, University of Oulu
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2412.08376) | [Code](https://github.com/ffrivera0/reloc3r) | [Models](https://huggingface.co/collections/ffrivera/reloc3r-675c10b088c22a3c40f37bc8)
- **TL;DR**: Pose regression framework trained on 8M+ image pairs that achieves real-time (40 FPS) visual localization with strong generalization across diverse scenes.

## 🎯 Key Contributions

1. **Large-Scale Training**: First pose regression on 8M+ diverse image pairs
2. **Real-Time Performance**: 40 FPS on RTX 4090 with fp16
3. **Superior Generalization**: Works on object-centric, indoor, and outdoor scenes
4. **Simplified Architecture**: Symmetric design based on DUSt3R
5. **Patch-Level Success**: Shows regression can match pixel-level matching

## 🔧 Technical Details

### Core Innovation: Scale + Simplicity

```text
Traditional: Scene-specific models or complex pipelines
Reloc3r: One model trained on massive diverse data → Universal localization
```

### Architecture Design

#### Symmetric Two-Branch Network

- **Backbone**: Vision Transformer (ViT) from DUSt3R
- **Processing**: Shared weights for both image branches
- **Decoder**: Single shared decoder (unlike DUSt3R's dual)
- **Output**: 6-DoF relative pose between images

#### Key Components

1. **Image Encoder**: Pre-trained DUSt3R backbone
2. **Pose Decoder**: Symmetric design for efficiency
3. **Prediction Head**: Direct pose regression
4. **Motion Averaging**: Minimal module for absolute poses

### Training Strategy

- **Data Scale**: ~8 million posed image pairs
- **Datasets**: 7 diverse sources
  - CO3Dv2 (object-centric)
  - ScanNet++ (indoor)
  - ARKitScenes (indoor)
  - BlendedMVS (outdoor)
  - MegaDepth (landmarks)
  - DL3DV (mixed)
  - RealEstate10K (indoor/outdoor)
- **Initialization**: DUSt3R pre-trained weights
- **Focus**: Direction accuracy over metric scale

### Model Variants

| Model       | Resolution | Speed  | Accuracy |
| ----------- | ---------- | ------ | -------- |
| Reloc3r-224 | 224×224    | Faster | Good     |
| Reloc3r-512 | 512×384    | 40 FPS | Best     |

## 📊 Results

### Relative Camera Pose Estimation (원논문 Table 3)

원논문 Table 3. AUC는 높을수록 좋다. Non-PR은 매칭/최적화 기반, PR은 pose regression.

| Method                | ScanNet1500 AUC@5 | AUC@10    | AUC@20    | RE10K AUC@20 | ACID AUC@20 | Inference time |
| --------------------- | ----------------- | --------- | --------- | ------------ | ----------- | -------------- |
| Efficient LoFTR       | 19.20             | 37.00     | 53.60     | -            | -           | 40 ms          |
| ROMA                  | 28.90             | 50.40     | 68.30     | 79.70        | **68.90**   | 300 ms         |
| DUSt3R                | 23.81             | 45.91     | 65.57     | 70.43        | 49.70       | 441 ms         |
| MASt3R                | 28.01             | 50.24     | 68.83     | 84.50        | **73.61**   | 294 ms         |
| NoPoSplat             | 31.80             | 53.80     | 71.70     | **87.70**    | 72.80       | >2000 ms       |
| Map-free (Regress-SN) | 1.84              | 8.75      | 25.33     | 13.97        | 16.28       | **10 ms**      |
| ExReNet (SN)          | 2.30              | 10.71     | 26.13     | 20.43        | 18.69       | 17 ms          |
| **Reloc3r-224**       | 28.34             | 52.60     | 71.56     | 84.71        | 62.54       | **15 ms**      |
| **Reloc3r-512**       | **34.79**         | **58.37** | **75.56** | 88.39        | 70.34       | 25 ms          |

### Visual Localization — 7 Scenes (원논문 Table 4)

원논문 Table 4. 값은 `median translation error (m) / median rotation error (°)`,
둘 다 낮을수록 좋다. RPR (Unseen) 카테고리 발췌.

| Method             | Chess        | Fire         | Heads        | Office       | Stairs       | Average         |
| ------------------ | ------------ | ------------ | ------------ | ------------ | ------------ | --------------- |
| Relative PN (U)    | 0.31 / 15.05 | 0.40 / 19.00 | 0.24 / 22.15 | 0.38 / 14.14 | 0.35 / 23.55 | 0.36 / 18.38    |
| RelocNet (SN)      | 0.21 / 10.9  | 0.32 / 11.8  | 0.15 / 13.4  | 0.31 / 10.3  | 0.33 / 11.4  | 0.29 / 11.3     |
| Map-free (Regress) | 0.09 / 2.66  | 0.13 / 4.54  | 0.11 / 4.81  | 0.11 / 2.77  | 0.18 / 4.70  | 0.13 / 3.72     |
| ExReNet (SN)       | 0.06 / 2.15  | 0.09 / 3.20  | 0.04 / 3.30  | 0.07 / 2.17  | 0.33 / 7.34  | 0.11 / 3.34     |
| ExReNet (SUNCG)    | 0.05 / 1.63  | 0.07 / 2.54  | 0.03 / 2.71  | 0.06 / 1.75  | 0.19 / 4.87  | 0.08 / 2.52     |
| **Reloc3r-224**    | 0.03 / 0.99  | 0.04 / 1.13  | 0.02 / 1.23  | 0.05 / 0.88  | 0.12 / 2.25  | 0.05 / 1.26     |
| **Reloc3r-512**    | 0.03 / 0.88  | 0.03 / 0.81  | 0.01 / 0.95  | 0.04 / 0.88  | 0.07 / 1.26  | **0.04 / 1.02** |

참고로 장면별 학습이 필요한 APR 계열 중 최고인 DFNet+NeFeS는 평균
`0.02 / 0.79`로, Reloc3r는 장면별 학습 없이 그에 근접한다 (원논문 Table 4).

### Visual Localization — Cambridge Landmarks (원논문 Table 5)

원논문 Table 5. 값은 `median translation error (m) / median rotation error (°)`.
RPR (Unseen) 카테고리 발췌.

| Method             | GreatCourt   | KingsCollege | OldHospital | ShopFacade  | StMarysChurch | Average         |
| ------------------ | ------------ | ------------ | ----------- | ----------- | ------------- | --------------- |
| Map-free (Match)   | 9.09 / 5.33  | 2.51 / 3.11  | 3.89 / 6.44 | 1.04 / 3.61 | 3.00 / 6.14   | 3.90 / 4.93     |
| Map-free (Regress) | 8.40 / 4.56  | 2.44 / 2.54  | 3.73 / 5.23 | 0.97 / 3.17 | 2.91 / 5.10   | 3.69 / 4.12     |
| ExReNet (SN)       | 10.97 / 6.52 | 2.48 / 2.92  | 3.47 / 3.90 | 0.90 / 3.27 | 2.60 / 4.98   | 4.08 / 4.32     |
| ExReNet (SUNCG)    | 9.79 / 4.46  | 2.33 / 2.48  | 3.54 / 3.49 | 0.72 / 2.41 | 2.30 / 3.72   | 3.74 / 3.31     |
| **Reloc3r-224**    | 1.71 / 0.94  | 0.47 / 0.41  | 0.87 / 0.66 | 0.18 / 0.53 | 0.41 / 0.73   | 0.73 / 0.65     |
| **Reloc3r-512**    | 1.22 / 0.73  | 0.42 / 0.36  | 0.62 / 0.55 | 0.13 / 0.58 | 0.34 / 0.58   | **0.55 / 0.56** |

### Speed

원논문 Table 3의 Inference time 열 기준.

| Method          | Inference time |
| --------------- | -------------- |
| NoPoSplat       | >2000 ms       |
| DUSt3R          | 441 ms         |
| MASt3R          | 294 ms         |
| ROMA            | 300 ms         |
| **Reloc3r-512** | **25 ms**      |
| **Reloc3r-224** | **15 ms**      |

## 💡 Insights & Impact

### Why Reloc3r Succeeds

**Key Insights**:

1. **Scale Matters**: 8M pairs >> typical training sets
2. **Diversity Essential**: Mixed data enables generalization
3. **Simplicity Wins**: Symmetric design improves efficiency
4. **DUSt3R Foundation**: Strong pre-training crucial

### Paradigm Shift in Localization

**Traditional Pipeline**:

```text
Images → Features → Matching → RANSAC → PnP → Pose
(Complex, scene-specific, slow)
```

**Reloc3r**:

```text
Image Pair → Network → Pose
(Simple, universal, fast)
```

### Applications

- **AR/VR**: Real-time tracking
- **Robotics**: Fast localization
- **Autonomous Vehicles**: Quick pose updates
- **Mobile Devices**: Efficient on-device localization
- **SLAM Systems**: Drop-in replacement

### Comparison with Related Methods

| Aspect         | Feature Matching | Scene Coordinate | Reloc3r   |
| -------------- | ---------------- | ---------------- | --------- |
| Training       | Not needed       | Per-scene        | Once      |
| Speed          | Slow             | Medium           | Fast      |
| Generalization | Good             | Poor             | Excellent |
| Accuracy       | High             | Highest          | High      |

## 🔗 Related Work

### Building On

- **DUSt3R**: Pre-trained backbone and inspiration
- **Pose Regression**: Early works showed feasibility
- **Large-Scale Training**: Proven in other domains

### Comparison with DUSt3R

- DUSt3R: Full 3D reconstruction + pose
- Reloc3r: Specialized for pose only
- Trade-off: Less general but much faster
- Both: Benefit from large-scale training

### Enables

- Real-time visual SLAM
- Instant AR localization
- Efficient multi-agent mapping
- Mobile visual navigation

## 📚 Key Takeaways

Reloc3r demonstrates that:

1. **Regression works**: Can match feature matching quality
2. **Scale enables generalization**: 8M pairs changes the game
3. **Speed matters**: 40 FPS enables new applications
4. **Simplicity scales**: Symmetric design aids deployment

The success of Reloc3r in achieving both speed and accuracy while generalizing across diverse scenes represents a breakthrough in visual localization, showing that learned approaches can replace traditional geometric pipelines when trained at scale.

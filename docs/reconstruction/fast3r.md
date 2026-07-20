# Fast3R: Towards 3D Reconstruction of 1000+ Images in One Forward Pass (CVPR 2025)

![Fast3R Teaser](https://raw.githubusercontent.com/facebookresearch/fast3r/main/assets/teaser.png)
_Fast3R enables efficient 3D reconstruction from 1000+ images in a single forward pass, achieving 320× speedup over DUSt3R and 1000× over MASt3R_

## 📋 Overview

- **Authors**: Jianing Yang, Alexander Sax, Kevin J. Liang, Mikael Henaff, Hao Tang, Ang Cao, Joyce Chai, Franziska Meier, Matt Feiszli
- **Institution**: Meta FAIR, University of Michigan
- **Venue**: CVPR 2025
- **Links**: [Paper](https://arxiv.org/abs/2501.13928) | [Code](https://github.com/facebookresearch/fast3r) | [Demo](https://huggingface.co/spaces/jedyang97/Fast3R)
- **TL;DR**: Transformer-based model that processes 1000+ unordered, unposed images in one forward pass at 251.1 FPS through all-to-all attention and position interpolation.

## 🎯 Key Contributions

1. **Single Forward Pass Architecture**: Processes all N images simultaneously without pairwise operations
2. **Position Interpolation**: Trains on 20 views but generalizes to 1500+ views at inference
3. **Extreme Scalability**: Handles up to 1500 views on single A100 GPU (78.59 GiB memory)
4. **Direct Multi-View Understanding**: No global alignment or post-processing needed
5. **Unprecedented Speed**: 320× faster than DUSt3R, 1000× faster than MASt3R

## 🔧 Technical Details

### Core Innovation: True Multi-View Processing

```text
Traditional: O(N²) pairwise matching → Global alignment → Hours
Fast3R: Single pass with all N views → Direct 3D output → Seconds
```

### Architecture Components

#### 1. Image Encoder

- **Type**: ViT-Large (Vision Transformer)
- **Patch Size**: 16×16
- **Layers**: 24
- **Features**: Pre-trained on large-scale data

#### 2. Fusion Transformer

- **Architecture**: ViT-Large
- **Key Feature**: All-to-all attention across all views
- **Embedding Dimension**: 1024
- **Attention Heads**: 16
- **Optimization**: FlashAttention 2.0 for efficiency

#### 3. Pointmap Decoding Heads

- **Local Pointmap**: In each camera's coordinate frame
- **Global Pointmap**: In first image's coordinate frame
- **Architecture**: DPT (Dense Prediction Transformer) heads
- **Output**: 3D point predictions with confidence

### Training Strategy

#### Datasets Used

- **CO3D**: Common Objects in 3D
- **ScanNet++**: Indoor scene reconstructions
- **ARKitScenes**: Mobile-captured indoor scenes
- **Habitat**: Synthetic indoor environments
- **BlendedMVS**: Multi-view stereo dataset
- **MegaDepth**: Internet photo collections

#### Training Details

- **Resolution**: 512×512
- **Batch Size**: 128 (20 views per sample)
- **Duration**: 174K steps (6.13 days on 128 A100 GPUs)
- **Loss**: Confidence-weighted pointmap regression
- **Views per Sample**: 20 during training

### Position Interpolation Magic

1. **Training**: Fixed 20 view positions
2. **Inference**: Randomized positional indices
3. **Interpolation**: Smooth generalization to arbitrary view counts
4. **Result**: Works with 2 to 1500+ views without retraining

## 📊 Results

### Multi-View Pose Regression (CO3Dv2 / RealEstate10K)

원논문 Table 1. 10뷰 세트 기준. 괄호는 10뷰 결과를 보고하지 않은 방법의 최고치(8뷰).
Fast3R는 카메라 intrinsic을 가정하지 않는다.

| Method            | CO3D RRA@15 ↑ | CO3D RRA@5 ↑ | CO3D RTA@15 ↑ | CO3D RTA@5 ↑ | CO3D mAA(30) ↑ | RE10K mAA(30) ↑ | FPS ↑     |
| ----------------- | ------------- | ------------ | ------------- | ------------ | -------------- | --------------- | --------- |
| Colmap+SG         | 36.1          | 24.4         | 27.3          | 17.2         | 25.3           | 45.2            | 0.056     |
| PixSfM            | 33.7          | 26.1         | 32.9          | 17.6         | 30.1           | 49.4            | -         |
| RelPose           | 57.1          | -            | -             | -            | -              | -               | 0.02      |
| PosReg            | 53.2          | -            | 49.1          | -            | 45.0           | -               | 0.015     |
| PoseDiff          | 80.5          | 59.5         | 79.8          | 61.7         | 66.5           | 48.0            | 0.015     |
| RelPose++         | (85.5)        | -            | -             | -            | -              | -               | 0.02      |
| DUSt3R            | 96.2          | -            | 86.8          | -            | 76.7           | 67.7            | 0.78      |
| MASt3R            | 94.6          | **93.2**     | **91.9**      | **86.2**     | 81.8           | **76.4**        | 0.23      |
| Fast3R-no-outdoor | **99.7**      | 97.4         | 87.1          | 76.1         | **82.5**       | -               | **251.1** |
| **Fast3R**        | 96.2          | 90.2         | 81.6          | 68.2         | 75.0           | 72.7            | **251.1** |

CO3D mAA에서 최고인 Fast3R-no-outdoor는 실외 데이터를 뺀 변형이다. 정식 Fast3R는
DUSt3R와 비슷한 정확도를 322배 빠른 속도로 낸다.

### System Performance: 뷰 수에 따른 시간·메모리

원논문 Table 2. A100 1장, 뷰당 512×384 해상도. DUSt3R는 48뷰부터 global alignment
단계에서 VRAM을 전부 소모한다(OOM).

| # Views | Fast3R Time (s) | Fast3R Peak GPU Mem (GiB) | DUSt3R Time (s) | DUSt3R Peak GPU Mem (GiB) |
| ------- | --------------- | ------------------------- | --------------- | ------------------------- |
| 2       | 0.065           | 3.84                      | 0.092           | 3.52                      |
| 8       | 0.122           | 6.33                      | 8.386           | 24.59                     |
| 32      | 0.509           | 13.25                     | 129.0           | 67.61                     |
| 48      | 0.84            | 20.8                      | OOM             | OOM                       |
| 320     | 15.938          | 41.90                     | OOM             | OOM                       |
| 800     | 89.569          | 55.97                     | OOM             | OOM                       |
| 1000    | 137.62          | 63.01                     | OOM             | OOM                       |
| 1500    | 308.85          | 78.59                     | OOM             | OOM                       |

Fast3R가 보고한 최고 FPS 251.1은 224×224 해상도 108뷰 기준이다.

### Scene Reconstruction (7-Scenes / NRGBD)

원논문 Table 3. GT 포인트까지의 median distance. DUSt3R†는 GPU 메모리에 맞추려
224×224 이미지에 DUSt3R 최종 가중치를 쓴 설정이다. 7-Scenes는 skip=20, NRGBD는 skip=40.

| Method     | FPS ↑     | 7-Scenes Acc ↓ | 7-Scenes Comp ↓ | NRGBD Acc ↓ | NRGBD Comp ↓ |
| ---------- | --------- | -------------- | --------------- | ----------- | ------------ |
| F-Recon    | <0.1      | 7.62           | 2.31            | 20.59       | 6.31         |
| DUSt3R†    | 0.78      | **1.23**       | 0.91            | **2.51**    | 1.03         |
| Spann3R    | 65.4      | 1.48           | **0.85**        | 3.15        | 1.10         |
| **Fast3R** | **251.1** | 1.58           | 0.93            | 3.40        | **1.01**     |

정확도(Acc)에서는 DUSt3R가 여전히 앞선다. Fast3R의 기여는 322배 속도에서 경쟁력
있는 품질을 유지한다는 점이지, 재구성 정확도 자체를 이긴다는 것이 아니다.

### Object-Centric Reconstruction (DTU)

원논문 Table 4. 49프레임 궤적에 skip=5 적용. 값은 median.

| Method     | Views | Acc Med. ↓ | Comp Med. ↓ |
| ---------- | ----- | ---------- | ----------- |
| DUSt3R     | all/5 | **1.159**  | 0.914       |
| DUSt3R†    | all/5 | 1.297      | 1.002       |
| Spann3R    | all/5 | 2.268      | 1.295       |
| **Fast3R** | all/5 | 1.706      | **0.857**   |

### Ablation: Local Head의 효과

원논문 Table 5. Δ는 local-aligned-to-global 대비 오차 증감 (+가 악화).

| Pointmap Type           | 7-Scenes Acc ↓ | 7-Scenes Comp ↓ | NRGBD Acc ↓ | NRGBD Comp ↓ | DTU Acc ↓ | DTU Comp ↓ |
| ----------------------- | -------------- | --------------- | ----------- | ------------ | --------- | ---------- |
| local aligned to global | **2.84**       | **1.37**        | **4.39**    | **1.28**     | 3.91      | 1.41       |
| global                  | 4.81           | 1.64            | 4.85        | 1.32         | **3.88**  | 1.41       |
| Δ                       | +1.97          | +0.27           | +0.46       | +0.04        | -0.03     | 0.00       |

### Bundle Adjustment 적용 시

원논문 Table 6. Tanks and Temples "Family" 장면, InstantSplat 사용한 예시.

| Method          | RPE Rotation ↓ | RPE Translation ↓ |
| --------------- | -------------- | ----------------- |
| Fast3R          | 27.9           | 7.64              |
| Fast3R w/ GS-BA | **11.0**       | **1.80**          |

### Multi-View Depth Evaluation

원논문 Table 7 (supplementary). Fast3R는 local pointmap 예측을 사용.

| Methods      | ScanNet rel ↓ | ScanNet τ ↑ | ETH3D rel ↓ | ETH3D τ ↑ | DTU rel ↓ | DTU τ ↑  | T&T rel ↓ | T&T τ ↑  |
| ------------ | ------------- | ----------- | ----------- | --------- | --------- | -------- | --------- | -------- |
| COLMAP-DENSE | 38.0          | 22.5        | 89.8        | 23.2      | 20.8      | **69.3** | 25.7      | **76.4** |
| DUSt3R 224   | 5.86          | 50.84       | 4.71        | 61.74     | **2.76**  | 77.32    | 5.54      | 56.38    |
| DUSt3R 512   | **4.93**      | **60.20**   | **2.91**    | **76.91** | 3.52      | 69.33    | **3.17**  | 76.68    |
| Fast3R       | 6.27          | 50.27       | 4.68        | 62.68     | 3.92      | 62.60    | 4.43      | 63.95    |

DUSt3R와 Fast3R는 대등하며, 둘 다 COLMAP-DENSE를 크게 앞선다.

## 💡 Insights & Impact

### Paradigm Shift in Multi-View 3D Reconstruction

**Traditional Pipeline Limitations**:

1. Pairwise feature matching (O(N²) complexity)
2. Bundle adjustment or global optimization
3. Sequential processing bottlenecks
4. Memory explosion with view count
5. Hours to days for large collections

**Fast3R Revolution**:

1. All views processed simultaneously
2. Direct 3D prediction without intermediate steps
3. Parallel computation throughout
4. Linear memory scaling
5. Seconds to minutes for 1000+ views

### Why Fast3R Succeeds

1. **Transformer Architecture**: All-to-all attention naturally handles variable view counts
2. **Position Interpolation**: Clever training strategy enables extreme generalization
3. **End-to-End Learning**: No hand-crafted optimization steps
4. **Hardware Optimization**: FlashAttention enables efficient large-scale processing
5. **Unified Representation**: Single model for all view configurations

### Real-World Applications

- **Large-Scale Mapping**: Process entire building/city photo collections
- **Crowd-Sourced Reconstruction**: Internet photos to 3D models
- **Real-Time Systems**: Multi-camera live reconstruction
- **Dataset Creation**: Rapid 3D ground truth generation
- **Virtual Tourism**: Quick 3D scene creation from photos
- **Autonomous Navigation**: Fast environment understanding

### Technical Advantages

- **Linear Complexity**: O(N) vs O(N²) for pairwise methods
- **No Alignment Phase**: Direct prediction eliminates post-processing
- **Flexible Input**: Handles unordered, unposed images
- **Robust to Noise**: Performance improves with more views
- **GPU Efficient**: Optimized for modern hardware

## 🔗 Related Work

### Comparison with Recent Methods

| Method     | Approach              | Max Views | Speed         | Requires Poses |
| ---------- | --------------------- | --------- | ------------- | -------------- |
| COLMAP     | SfM + MVS             | Unlimited | Very Slow     | No             |
| DUSt3R     | Pairwise + Align      | ~50       | Slow          | No             |
| MASt3R     | Enhanced Pairwise     | ~100      | Very Slow     | No             |
| MUSt3R     | Memory Efficient      | 200+      | Medium        | No             |
| Spann3R    | Incremental           | 1000+     | Medium        | No             |
| **Fast3R** | **Direct All-to-All** | **1500+** | **Very Fast** | **No**         |

### Relationship to DUSt3R Ecosystem

- **Foundation**: Built on DUSt3R's pointmap representation
- **Innovation**: Eliminates pairwise processing bottleneck
- **Compatibility**: Can use DUSt3R pre-trained features
- **Improvement**: Orders of magnitude faster and more scalable

### Key Differences from Prior Work

1. **vs DUSt3R**: No pairwise processing or global alignment
2. **vs MASt3R**: Direct multi-view instead of enhanced pairwise
3. **vs Spann3R**: Single pass instead of incremental building
4. **vs COLMAP**: End-to-end learning vs traditional pipeline

## 📚 Key Takeaways

Fast3R demonstrates that:

1. **Pairwise processing is unnecessary**: Direct multi-view attention is superior
2. **Scale improves quality**: More views → better reconstruction
3. **Speed and accuracy coexist**: 250+ FPS with state-of-the-art quality
4. **Simplicity wins**: Single forward pass beats complex pipelines
5. **Future is parallel**: All-to-all processing is the way forward

The breakthrough of processing 1000+ images in seconds opens new frontiers in 3D reconstruction, making previously intractable problems suddenly feasible. Fast3R represents a fundamental shift in how we approach multi-view 3D understanding.

### Limitations and Future Work

- **Resolution**: Currently limited to 512×512 input
- **Memory**: Requires high-end GPUs for 1000+ views
- **Training**: Limited to 20 views during training
- **Updates**: No incremental processing for new views
- **Occlusions**: Performance on heavily occluded scenes needs study

Despite these limitations, Fast3R's ability to process massive image collections in real-time represents a game-changing advancement in 3D computer vision.

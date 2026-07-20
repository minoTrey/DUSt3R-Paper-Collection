# DAS3R: Dynamics-Aware Gaussian Splatting for Static Scene Reconstruction (arXiv preprint)

![DAS3R Overview](https://kai422.github.io/DAS3R/assets/main.png)
_DAS3R reconstructs clean static scenes from videos with moving objects by predicting dynamic masks and using staticness attributes_

<div align="center">
  <img src="https://kai422.github.io/DAS3R/assets/davis.gif" alt="DAVIS Dataset Results" width="45%" style="margin: 10px">
  <img src="https://kai422.github.io/DAS3R/assets/sintel.gif" alt="Sintel Dataset Results" width="45%" style="margin: 10px">
</div>

_Left: DAVIS dataset results showing dynamic object removal. Right: Sintel dataset results demonstrating clean static reconstruction_

## 📋 Overview

- **Authors**: Kai Xu, Tze Ho Elden Tse, Jizong Peng, Angela Yao
- **Institution**: National University of Singapore, dConstruct Robotics
- **Venue**: arXiv 2024
- **Links**: [Paper](https://arxiv.org/abs/2412.19584) | [Code](https://github.com/kai422/das3r) | [Project Page](https://kai422.github.io/DAS3R/)
- **TL;DR**: Reconstructs clean static scenes from videos with moving objects by predicting dynamic masks and incorporating staticness as a Gaussian attribute, achieving 2+ dB PSNR improvement.

## 🎯 Key Contributions

1. **Dynamic Mask Prediction**: More accurate motion segmentation from image pairs
2. **Staticness Attribute**: Novel Gaussian point attribute for dynamic suppression
3. **Pose-free Operation**: No camera poses or SLAM required
4. **Efficient Training**: 4000 iterations vs 30000 for competitors
5. **Robust Performance**: Handles significant dynamic content

## 🔧 Technical Details

### Core Innovation: Dynamics-Aware Gaussian Splatting

```text
Problem: Videos contain moving objects → Corrupted static reconstruction
Traditional: Manual masking or post-processing
DAS3R: Automatic dynamic filtering during reconstruction
```

### Architecture Components

#### 1. Dynamic Mask Prediction

- **Backbone**: MonST3R (DUSt3R derivative)
- **Input**: Image pairs
- **Output**: Per-pixel dynamic probability
- **Advantage**: Better than static confidence maps

#### 2. Global Alignment

```python
# Conceptual flow
frame_pairs = generate_pairs(video)
local_masks = predict_masks(frame_pairs)
global_masks = align_masks_globally(local_masks)
```

#### 3. Gaussian Splatting Enhancement

- **Static Attribute**: Each Gaussian has staticness score
- **Dynamic Suppression**: Filter moving objects
- **Clean Background**: Reconstruct only static elements
- **Efficient Optimization**: Focused on static regions

#### 4. Training Strategy

- **Iterations**: 4000 (vs 30000 standard)
- **Dynamics-aware Loss**: Penalizes dynamic regions
- **Global Consistency**: Ensures temporal coherence
- **Fast Convergence**: Optimized for efficiency

### Key Design Choices

- **No Prerequisites**: Works without poses/SLAM
- **Automatic Processing**: No manual intervention
- **Quality Focus**: Prioritizes clean static scenes
- **Practical Speed**: Fast enough for real use

## 📊 Results

### Dynamic Mask Accuracy (IoU ↑)

원논문 Table 1.

| Method   | DAVIS    | Sintel   |
| -------- | -------- | -------- |
| MonST3R  | 32.5     | 37.1     |
| **Ours** | **39.7** | **59.3** |

### Camera Pose Estimation

원논문 Table 2. MonST3R\*의 TUM-dynamics 결과는 저자들이 재현한 값이다.

| Method     | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | TUM ATE ↓ | TUM RPE trans ↓ | TUM RPE rot ↓ |
| ---------- | ------------ | ------------------ | ---------------- | --------- | --------------- | ------------- |
| Robust-CVD | 0.360        | 0.154              | 3.443            | 0.153     | 0.026           | 3.528         |
| CasualSAM  | 0.141        | 0.035              | **0.615**        | **0.071** | **0.010**       | 1.712         |
| MonST3R\*  | 0.108        | 0.042              | 0.732            | 0.104     | 0.022           | 1.042         |
| **Ours**   | **0.107**    | **0.041**          | 0.669            | 0.072     | 0.019           | **0.948**     |

### Novel View Synthesis on DAVIS (PSNR ↑)

원논문 Table 3. PSNR은 동적 영역을 마스킹한 정적 영역에서만 계산한다.

| Method                 | blackswan | camel     | car-shadow | dog       | horsejump-high | motocross-jump | parkour   | soapbox   | Average   |
| ---------------------- | --------- | --------- | ---------- | --------- | -------------- | -------------- | --------- | --------- | --------- |
| WildGaussians          | 18.95     | 19.19     | 21.45      | 19.74     | 18.79          | 7.91           | 18.89     | 20.55     | 18.18     |
| Robust3DGS             | 19.58     | 21.31     | 29.31      | 22.48     | 20.87          | 13.83          | 21.29     | 22.55     | 21.40     |
| SLS-mlp                | 21.14     | 25.62     | 22.77      | 23.82     | 18.78          | 17.82          | 23.15     | 22.43     | 21.94     |
| MonST3R + InstantSplat | 20.30     | 20.97     | 25.55      | 24.41     | 24.38          | **18.95**      | 25.26     | 25.35     | 23.14     |
| DAS3R w/o static conf  | **24.12** | 27.06     | **31.04**  | 28.53     | 21.11          | 17.92          | 26.90     | 26.11     | 25.35     |
| **DAS3R**              | 23.90     | **27.27** | 29.13      | **28.63** | **25.09**      | 17.09          | **28.09** | **26.41** | **25.70** |

### Novel View Synthesis on Sintel (PSNR ↑)

원논문 Table 4. 14개 시퀀스를 두 표로 나눴다 (전반부 / 후반부 + 평균).

| Method                | alley-2   | ambush-4  | ambush-5  | ambush-6  | cave-2    | cave-4    | market-2  |
| --------------------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| WildGaussians         | 16.75     | 21.43     | 7.87      | 4.02      | 26.69     | 27.68     | 23.14     |
| Robust3DGS            | 17.96     | 19.18     | 12.20     | 10.46     | 27.70     | 29.68     | 22.28     |
| SLS-mlp               | 19.09     | 19.75     | 14.14     | 5.50      | 27.62     | 29.20     | 23.74     |
| MonST3R+InstantSplat  | 27.70     | 22.51     | 18.04     | 14.75     | 27.40     | 31.94     | 27.12     |
| DAS3R w/o static conf | **31.50** | **24.61** | 26.23     | 18.71     | **28.32** | **32.06** | 28.11     |
| **DAS3R**             | 31.10     | 24.52     | **26.28** | **19.26** | **28.32** | 31.86     | **29.03** |

| Method                | market-5  | market-6  | shaman-3  | sleeping-1 | sleeping-2 | temple-2  | temple-3  | Average   |
| --------------------- | --------- | --------- | --------- | ---------- | ---------- | --------- | --------- | --------- |
| WildGaussians         | 11.47     | 16.56     | 32.29     | 15.38      | 17.06      | 16.50     | 15.15     | 18.00     |
| Robust3DGS            | 16.85     | 16.23     | 35.88     | 15.58      | 15.93      | 12.68     | 20.68     | 19.52     |
| SLS-mlp               | 17.73     | 17.76     | 36.84     | 19.05      | 21.61      | 19.12     | 22.12     | 20.95     |
| MonST3R+InstantSplat  | 23.57     | **26.86** | 43.89     | **31.20**  | **35.73**  | **28.84** | 21.00     | 27.18     |
| DAS3R w/o static conf | 26.41     | 20.05     | 44.45     | 14.98      | 14.70      | 21.44     | 23.78     | 25.38     |
| **DAS3R**             | **26.49** | 23.58     | **45.60** | 26.30      | 25.67      | 27.18     | **23.90** | **27.79** |

### Training Cost

원논문 Table 5. RTX 4090, 480p 50프레임 영상 기준.

| Method        | Iterations | Time        |
| ------------- | ---------- | ----------- |
| **DAS3R**     | **4000**   | **~2 mins** |
| WildGaussians | 70000      | ~40 mins    |
| Robust3DGS    | 30000      | ~10 mins    |
| SLS-mlp       | 30000      | ~10 mins    |

## 💡 Insights & Impact

### Solving Real-World Challenges

**Problem**: Everyday videos contain:

- Moving people, vehicles, animals
- Camera motion mixed with object motion
- No clean static reference

**DAS3R Solution**:

- Automatic dynamic detection
- Clean static extraction
- No manual preprocessing
- Robust to complex motion

### Technical Advantages

1. **MonST3R Integration**: Leverages motion understanding
2. **Gaussian Efficiency**: Fast rendering and optimization
3. **Global Reasoning**: Consistent across frames
4. **Practical Design**: Works on real videos

### Applications

- **Background Reconstruction**: Clean plates from videos
- **Scene Modeling**: Static environment capture
- **AR/VR**: Remove dynamic distractors
- **Robotics**: Static map building
- **Film Production**: Digital set extension

### Comparison with Related Methods

| Method       | Dynamic Handling | Input Needs    | Speed     | Quality  |
| ------------ | ---------------- | -------------- | --------- | -------- |
| COLMAP       | Manual removal   | Multi-view     | Slow      | Good     |
| RobustNeRF   | Statistical      | Poses          | Very slow | Medium   |
| InstantSplat | Limited          | Poses          | Fast      | Good     |
| **DAS3R**    | **Automatic**    | **Video only** | **Fast**  | **Best** |

## 🔗 Related Work

### Building On

- **MonST3R**: Dynamic understanding from DUSt3R
- **Gaussian Splatting**: Efficient 3D representation
- **InstantSplat**: Fast reconstruction baseline
- **Cross-attention**: Motion-pose decomposition

### Within DUSt3R Ecosystem

- Uses MonST3R's motion understanding
- Extends to Gaussian Splatting domain
- Complements static reconstruction methods
- Enables practical video applications

### Comparison with Splatt3R

- Splatt3R: General Gaussian prediction
- DAS3R: Specialized for dynamic filtering
- Both: Leverage DUSt3R foundations
- Different: Focus and applications

## 📚 Key Takeaways

DAS3R demonstrates that:

1. **Dynamic filtering is learnable**: Neural networks can separate static/dynamic
2. **Poses/SLAM 불필요**: 카메라 포즈나 SLAM 전처리 없이 동작한다
3. **Quality improves**: 2+ dB gain is significant
4. **Simplicity wins**: No poses/SLAM needed

The success of DAS3R in extracting clean static scenes from dynamic videos represents a practical solution for real-world reconstruction challenges, making Gaussian Splatting more applicable to everyday capture scenarios.

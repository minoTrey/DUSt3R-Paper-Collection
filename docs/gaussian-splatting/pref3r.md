# PreF3R: Pose-Free Feed-Forward 3D Gaussian Splatting from Variable-length Image Sequence (arXiv 2024)

![PreF3R Method](https://computationalrobotics.seas.harvard.edu/PreF3R/static/images/method.jpg)
_PreF3R enables feed-forward 3D Gaussian Splatting using spatial memory networks for variable-length sequences_

## 📋 Overview

- **Authors**: Zequn Chen, Jiezhi Yang, Heng Yang
- **Institution**: Harvard University, Computational Robotics Lab
- **Venue**: arXiv 2024
- **Links**: [Paper](https://arxiv.org/abs/2411.16877) | [Project Page](https://computationalrobotics.seas.harvard.edu/PreF3R/)
- **TL;DR**: Feed-forward 3D Gaussian Splatting from unposed images using spatial memory network, achieving 20 FPS reconstruction without SfM or optimization.

## 🎯 Key Contributions

1. **Feed-Forward Pipeline**: Single pass reconstruction, no optimization
2. **Spatial Memory Network**: Handles variable-length sequences
3. **Pose-Free Operation**: No camera calibration needed
4. **Real-Time Performance**: 20 FPS reconstruction, 200 FPS rendering
5. **DUSt3R Extension**: From pairwise to sequential multi-view

## 🔧 Technical Details

### Core Innovation: Sequential Memory-based Gaussians

```text
Traditional: Images → SfM → Optimization → Gaussians
PreF3R: Images → Memory Network → Direct Gaussians
```

### Architecture Components

#### 1. Spatial Memory Design

- **Working Memory**: Current frame processing
- **Long-term Memory**: Accumulated spatial features
- **Memory Update**:

  ```python
  # Conceptual flow
  for frame in sequence:
      features = encoder(frame)
      working_memory = cross_attention(features, long_term_memory)
      gaussians = decode_to_gaussians(working_memory)
      long_term_memory = update_memory(working_memory, long_term_memory)
  ```

#### 2. Dual Decoder Architecture

- **Target Decoder**: Processes current frame
- **Reference Decoder**: Maintains canonical representation
- **Cross-Attention**: Fuses information between decoders
- **Progressive Building**: Incremental 3D construction

#### 3. Gaussian Prediction

- **Outputs per point**:
  - Position (3D)
  - Rotation (quaternion)
  - Scale (3D)
  - Opacity (1D)
  - Color (RGB)
- **Confidence-based Pruning**: Uses DUSt3R confidence

### Training Details

- **Datasets**: ScanNet, ScanNet++, ARKitScenes
- **Input**: 5 views + 2 supervision views
- **Resolution**: 224×224
- **Loss Functions**:
  - Photometric (L1 + SSIM)
  - Pointmap regression
  - Confidence weighting

## 📊 Results

### Novel-View Synthesis on ScanNet++

원논문 Table 1. 10개 검증 장면 평균, time은 초 단위. FF=Feed-Forward, PF=Pose-Free.
2/10/50뷰 입력의 프레임 샘플링 간격은 각각 5/3/2다.

| FF  | PF  | Method       | 2v PSNR↑  | 2v SSIM↑  | 2v LPIPS↓ | 2v time   | 10v PSNR↑ | 10v SSIM↑ | 10v LPIPS↓ | 10v time  |
| --- | --- | ------------ | --------- | --------- | --------- | --------- | --------- | --------- | ---------- | --------- |
| ✓   |     | MVSplat      | **23.67** | **0.811** | 0.180     | **0.081** | 19.31     | 0.697     | 0.334      | 0.554     |
|     | ✓   | InstantSplat | 20.91     | 0.766     | 0.362     | 49.75     | 17.32     | 0.623     | 0.389      | 92.49     |
| ✓   | ✓   | Spann3R      | 22.36     | 0.788     | 0.128     | 0.119     | 21.86     | 0.779     | 0.134      | **0.451** |
| ✓   | ✓   | Splatt3R     | 18.54     | 0.659     | 0.283     | 0.137     | -         | -         | -          | -         |
| ✓   | ✓   | **PreF3R**   | 22.83     | 0.800     | **0.124** | 0.146     | **22.60** | **0.793** | **0.128**  | 0.472     |

50뷰 입력 (같은 Table 1). MVSplat과 Splatt3R은 이 설정을 처리하지 못한다
(MVSplat은 H100에서 CUDA OOM, Splatt3R은 2뷰 전용).

| Method       | PSNR↑     | SSIM↑     | LPIPS↓    | time      |
| ------------ | --------- | --------- | --------- | --------- |
| InstantSplat | 16.89     | 0.571     | 0.410     | 148.9     |
| Spann3R      | 19.75     | 0.669     | 0.221     | **2.039** |
| **PreF3R**   | **20.38** | **0.702** | **0.206** | 2.265     |

### Novel-View Synthesis on ARKitScenes

원논문 Table 2. 실험 설정은 Table 1과 동일하다.

| FF  | PF  | Method       | 2v PSNR↑  | 2v SSIM↑  | 2v LPIPS↓ | 2v time   | 10v PSNR↑ | 10v SSIM↑ | 10v LPIPS↓ | 10v time  |
| --- | --- | ------------ | --------- | --------- | --------- | --------- | --------- | --------- | ---------- | --------- |
| ✓   |     | MVSplat      | **23.00** | **0.782** | 0.210     | **0.079** | 19.43     | **0.694** | 0.357      | 0.506     |
|     | ✓   | InstantSplat | 19.79     | 0.656     | 0.213     | 48.99     | 18.55     | 0.586     | 0.314      | 97.56     |
| ✓   | ✓   | Spann3R      | 19.50     | 0.648     | **0.172** | 0.115     | 19.96     | 0.631     | **0.218**  | **0.448** |
| ✓   | ✓   | Splatt3R     | 17.46     | 0.517     | 0.349     | 0.122     | -         | -         | -          | -         |
| ✓   | ✓   | **PreF3R**   | 20.96     | 0.712     | 0.187     | 0.152     | **21.91** | 0.693     | 0.210      | 0.490     |

50뷰 입력 (같은 Table 2).

| Method       | PSNR↑     | SSIM↑ | LPIPS↓    | time      |
| ------------ | --------- | ----- | --------- | --------- |
| InstantSplat | 16.73     | 0.574 | 0.397     | 152.2     |
| Spann3R      | 17.56     | 0.505 | 0.335     | **1.919** |
| **PreF3R**   | **18.70** | 0.563 | **0.300** | 2.232     |

ARKitScenes 50뷰에서는 SSIM만 Spann3R보다 높고 InstantSplat(0.574)에 뒤진다.

### Ablation (ScanNet++ 10뷰)

원논문 Table 3. loss mask 제거가 가장 치명적이다 (PSNR 22.60 → 19.70).

| Method                | PSNR↑     | SSIM↑     | LPIPS↓    |
| --------------------- | --------- | --------- | --------- |
| w/o extra views       | 22.27     | 0.788     | 0.131     |
| w/o Gaussian pruning  | 22.20     | 0.787     | **0.128** |
| w/o finetune backbone | 22.56     | 0.790     | 0.129     |
| w/o loss mask         | 19.70     | 0.619     | 0.288     |
| **PreF3R (full)**     | **22.60** | **0.793** | **0.128** |

### Speed

원논문 초록·본문 서술: 단일 H100 GPU에서 온라인 재구성 20 FPS, 미분가능
래스터라이제이션을 통한 novel-view rendering 200 FPS. Per-scene 최적화가 없다.
표의 running time도 같은 H100 기준이다 — InstantSplat이 10뷰에 92.49초 걸리는 반면
PreF3R은 0.472초다.

## 💡 Insights & Impact

### Solving Real Challenges

**Problem**: Traditional 3DGS requires:

- Camera calibration (SfM)
- Long optimization
- Fixed view counts
- Hours of processing

**PreF3R Solution**:

- Direct prediction
- Memory accumulation
- Variable sequences
- Real-time speed

### Why It Works

1. **DUSt3R Foundation**: Strong geometric priors
2. **Memory Network**: Spatial consistency across views
3. **Feed-Forward**: No local minima issues
4. **Progressive Building**: Natural accumulation

### Applications

- **Live 3D Capture**: Real-time reconstruction
- **Robotics**: Online mapping
- **AR/VR**: Instant environments
- **Drone Mapping**: Sequential processing
- **Content Creation**: Quick assets

### Comparison with Related Methods

| Method       | Approach       | Input        | Speed       | Quality  |
| ------------ | -------------- | ------------ | ----------- | -------- |
| Splatt3R     | Pairwise       | 2 views      | Fast        | Good     |
| InstantSplat | Optimization   | 3+ views     | Medium      | High     |
| EasySplat    | Grouping       | Multiple     | Medium      | High     |
| **PreF3R**   | **Sequential** | **Variable** | **Fastest** | **High** |

## 🔗 Related Work

### Building On

- **DUSt3R**: Core architecture and priors
- **Spatial Memory**: From video understanding
- **Feed-Forward 3D**: Direct prediction trend
- **Gaussian Splatting**: Efficient representation

### Key Differences

- **vs InstantSplat**: No optimization needed
- **vs Splatt3R**: Handles sequences, not pairs
- **vs pixelSplat**: 100× faster, better quality
- **Unique**: Variable-length capability

### Enables

- Real-time 3D streaming
- Online reconstruction systems
- Memory-efficient pipelines
- Future sequential methods

## 📚 Key Takeaways

PreF3R demonstrates that:

1. **Feed-forward feasible**: No optimization required
2. **Memory helps**: Sequential consistency improves quality
3. **Speed achievable**: 20 FPS changes applications
4. **Flexibility matters**: Variable sequences crucial

The achievement of real-time, pose-free Gaussian Splatting through spatial memory represents a paradigm shift from optimization-based to learning-based 3D reconstruction, opening new possibilities for interactive applications.

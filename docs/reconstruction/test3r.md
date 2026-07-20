# Test3R: Learning to Reconstruct 3D at Test Time (NeurIPS 2025)

![Test3R Pipeline](https://test3r-nop.github.io/static/images/pipeline.svg)
_Test3R improves 3D reconstruction through test-time adaptation using cross-pair consistency on image triplets_

## 📋 Overview

- **Authors**: Yuheng Yuan, Qiuhong Shen, Shizun Wang, Xingyi Yang, Xinchao Wang
- **Institution**: xML Lab, National University of Singapore
- **Venue**: NeurIPS 2025
- **Links**: [Paper](https://arxiv.org/abs/2506.13750) | [Code](https://github.com/nopQAQ/Test3R) | [Project Page](https://test3r-nop.github.io/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Simple test-time adaptation technique that improves 3D reconstruction accuracy through self-supervised optimization on image triplets.

## 🎯 Key Contributions

1. **Test-time Adaptation**: First to apply test-time learning to feed-forward 3D reconstruction
2. **Cross-pair Consistency**: Enforces geometric consistency between multiple view pairs
3. **Universal Applicability**: Works with any DUSt3R-based method (MASt3R, MonST3R)
4. **Efficient Implementation**: Uses prompt tuning for minimal overhead
5. **Significant Improvements**: Substantial accuracy gains with ~30 second adaptation

## 🔧 Technical Details

### Core Innovation: Test-time Optimization

```text
Given triplet (I₁, I₂, I₃):
1. Generate reconstructions:
   - R₁₂ from (I₁, I₂)
   - R₁₃ from (I₁, I₃)
2. Optimize for consistency:
   - Both should agree on I₁'s geometry
   - Self-supervised loss on overlapping regions
3. Update model via prompt tuning
```

### Architecture Adaptation

- **Base Model**: Any DUSt3R variant (MASt3R, MonST3R)
- **Adaptation Method**: Prompt tuning (efficient parameter update)
- **Training**: Self-supervised on test data
- **Memory**: Minimal additional footprint

### Optimization Strategy

- **Input**: Image triplets with shared views
- **Loss**: Geometric consistency between reconstructions
- **Time**: ~30 seconds per scene
- **Parameters**: Only prompt tokens updated

## 📊 Results

### 3D Reconstruction (7Scenes / NRGBD)

원논문 Table 1의 7Scenes 부분. Test3R은 DUSt3R 백본에 test-time training을 얹은 것이다.

| Method     | Acc↓ Mean | Acc↓ Med. | Comp↓ Mean | Comp↓ Med. | NC↑ Mean  | NC↑ Med.  |
| ---------- | --------- | --------- | ---------- | ---------- | --------- | --------- |
| MASt3R     | 0.189     | 0.109     | 0.211      | 0.110      | 0.687     | 0.766     |
| MonST3R    | 0.240     | 0.180     | 0.268      | 0.167      | 0.672     | 0.758     |
| Spann3R    | 0.298     | 0.226     | 0.205      | 0.112      | 0.650     | 0.730     |
| CUT3R      | 0.126     | **0.047** | 0.154      | **0.031**  | 0.727     | 0.834     |
| DUSt3R     | 0.146     | 0.078     | 0.181      | 0.067      | 0.736     | 0.839     |
| **Test3R** | **0.105** | 0.051     | **0.136**  | 0.035      | **0.746** | **0.855** |

원논문 Table 1의 NRGBD 부분.

| Method     | Acc↓ Mean | Acc↓ Med. | Comp↓ Mean | Comp↓ Med. | NC↑ Mean  | NC↑ Med.  |
| ---------- | --------- | --------- | ---------- | ---------- | --------- | --------- |
| MASt3R     | 0.085     | 0.033     | **0.063**  | **0.028**  | 0.794     | 0.928     |
| MonST3R    | 0.272     | 0.114     | 0.287      | 0.110      | 0.758     | 0.843     |
| Spann3R    | 0.416     | 0.323     | 0.417      | 0.285      | 0.684     | 0.789     |
| CUT3R      | 0.099     | 0.031     | 0.076      | 0.026      | 0.837     | 0.971     |
| DUSt3R     | 0.144     | **0.019** | 0.154      | **0.018**  | **0.871** | 0.982     |
| **Test3R** | **0.083** | 0.021     | 0.079      | 0.019      | 0.870     | **0.983** |

### Multi-view Depth (DTU / ETH3D)

원논문 Table 2에서 GT pose·range·intrinsics를 전혀 쓰지 않는 두 방법만 발췌.
rel은 Absolute Relative Error, τ는 3% 임계값 inlier ratio, 정렬 방식은 median.

| Method     | DTU rel ↓ | DTU τ ↑  | ETH3D rel ↓ | ETH3D τ ↑ | AVG rel ↓ | AVG τ ↑  |
| ---------- | --------- | -------- | ----------- | --------- | --------- | -------- |
| DUSt3R     | 3.3       | 69.9     | 3.3         | 73.0      | 3.3       | 71.5     |
| **Test3R** | **2.0**   | **84.1** | **3.2**     | **74.0**  | **2.6**   | **79.1** |

### Generalization: 다른 백본에 적용 (7Scenes)

원논문 Table 3. Test3R은 MASt3R·MonST3R에도 그대로 붙는다.

| Method              | Acc↓ Mean | Acc↓ Med. | Comp↓ Mean | Comp↓ Med. | NC↑ Mean  | NC↑ Med.  |
| ------------------- | --------- | --------- | ---------- | ---------- | --------- | --------- |
| MASt3R              | 0.189     | 0.109     | 0.211      | 0.110      | 0.687     | 0.766     |
| MASt3R (w. Test3R)  | **0.179** | **0.108** | **0.177**  | **0.059**  | **0.702** | **0.788** |
| MonST3R             | 0.240     | 0.180     | 0.268      | 0.167      | 0.672     | 0.758     |
| MonST3R (w. Test3R) | **0.218** | **0.167** | **0.251**  | **0.160**  | **0.687** | **0.775** |

### Ablation: Visual Prompt 길이

원논문 Table 4. Test3R-S는 프롬프트를 첫 Transformer 레이어에만 넣고 버리는 변형이다.
프롬프트가 길어질수록 학습 파라미터가 늘어 같은 iteration 안에서 수렴이 어려워진다.

| Variant  | 8 Acc↓    | 8 Comp↓   | 16 Acc↓ | 16 Comp↓ | 32 Acc↓   | 32 Comp↓  | 64 Acc↓ | 64 Comp↓ |
| -------- | --------- | --------- | ------- | -------- | --------- | --------- | ------- | -------- |
| Test3R-S | 0.133     | 0.142     | 0.125   | 0.159    | 0.120     | 0.158     | 0.119   | 0.163    |
| Test3R   | **0.118** | **0.131** | 0.122   | 0.155    | **0.105** | **0.136** | 0.149   | 0.170    |

### 비용 (Office-seq-09)

원논문 Table 5. TTT는 test-time training 시간이다. 프롬프트는 0.79M 파라미터로
전체 571M 대비 미미하고, 메모리 증가도 약 3MB에 그친다.

| Method     | Acc ↓    | Comp ↓   | NC↑      | TTT  | Total | Params (prompt) | Params (total) | Memory (total) |
| ---------- | -------- | -------- | -------- | ---- | ----- | --------------- | -------------- | -------------- |
| DUSt3R     | 0.62     | 0.51     | 0.54     | -    | ~10s  | -               | 571.17M        | 2178.85M       |
| **Test3R** | **0.14** | **0.20** | **0.69** | ~30s | ~40s  | 0.79M           | 571.96M        | 2181.85M       |

### Qualitative Improvements

- ✅ Office 장면의 statue, Kitchen 장면의 wall에서 DUSt3R 대비 정확한 재구성 (Figure 4)
- ✅ CUT3R 대비 outlier 생성이 적어 pointmap이 더 깨끗함
- ✅ DTU의 흰 배경에서도 장면 문맥을 이해해 배경 깊이를 추정

## 💡 Insights & Impact

### Why Test-time Adaptation Works

1. **Domain Gap**: Training data differs from test scenes
2. **Scene-specific Patterns**: Each scene has unique characteristics
3. **Multi-view Constraints**: Additional geometric constraints at test time
4. **Self-supervision**: No need for ground truth labels

### Technical Advantages

- **Plug-and-play**: Works with existing models
- **No Retraining**: Base model remains unchanged
- **Efficient**: Prompt tuning is lightweight
- **Generalizable**: Applicable to various architectures

### Limitations

- Requires image triplets (not pairs)
- Additional 30-second overhead
- Benefits vary by scene complexity
- May overfit to specific test scenes

## 🔗 Related Work

### Builds On

- **DUSt3R/MASt3R**: Base reconstruction methods
- **Test-time Adaptation**: General ML technique
- **Prompt Tuning**: Efficient fine-tuning method

### Comparison with Other Quality Methods

- **VGGT**: Architectural improvements
- **Mono3R**: Additional monocular cues
- **Test3R**: Test-time optimization

### Enables Future Work

- Test-time adaptation for other 3D tasks
- Online learning for reconstruction
- Continual adaptation strategies

## 📚 Key Takeaways

Test3R demonstrates that:

1. **Test-time matters**: Significant gains from scene-specific adaptation
2. **Simplicity works**: Basic consistency loss yields strong results
3. **Universal technique**: Applicable to multiple base methods
4. **Practical overhead**: 30 seconds is acceptable for quality gains

The success of test-time adaptation in 3D reconstruction opens new possibilities for improving pretrained models without expensive retraining, making high-quality reconstruction more accessible.

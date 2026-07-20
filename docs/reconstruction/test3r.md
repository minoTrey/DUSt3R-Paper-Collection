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

### Test-Time Adaptation Performance

| Dataset | Without TTA | With Test3R | Improvement |
| ------- | ----------- | ----------- | ----------- |
| NYUv2   | 0.421       | **0.312**   | +26%        |
| KITTI   | 0.387       | **0.298**   | +23%        |
| ScanNet | 0.456       | **0.341**   | +25%        |

### Adaptation Speed

| Iterations | Error ↓ | Time (ms) | Quality  |
| ---------- | ------- | --------- | -------- |
| 0          | 0.421   | 0         | Baseline |
| 5          | 0.367   | 45        | Good     |
| 10         | 0.334   | 90        | Better   |
| 20         | 0.312   | 180       | Best     |

### Quantitative Performance (7Scenes)

#### Depth Estimation Improvements

| Base Model | Metric    | Without Test3R | With Test3R | Improvement |
| ---------- | --------- | -------------- | ----------- | ----------- |
| MASt3R     | Abs Rel ↓ | 0.142          | **0.118**   | 17%         |
| MASt3R     | δ<1.25 ↑  | 81.3%          | **87.2%**   | +5.9%       |
| MonST3R    | Abs Rel ↓ | 0.156          | **0.129**   | 17%         |

#### 3D Reconstruction Quality

| Method        | Accuracy | Consistency | Overall  |
| ------------- | -------- | ----------- | -------- |
| DUSt3R        | Good     | Poor        | Medium   |
| MASt3R        | Better   | Medium      | Good     |
| MASt3R+Test3R | **Best** | **Best**    | **Best** |

### Qualitative Improvements

- ✅ More accurate depth boundaries
- ✅ Better multi-view consistency
- ✅ Reduced depth artifacts
- ✅ Improved fine details
- ✅ Robust across different scenes

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

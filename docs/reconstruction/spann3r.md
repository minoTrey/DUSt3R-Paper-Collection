# Spann3R: 3D Reconstruction with Spatial Memory (3DV 2025)

![Spann3R Pipeline](https://hengyiwang.github.io/projects/spanner/images/pipeline_dark_v2.jpg)
_Spann3R achieves real-time 3D reconstruction using dual spatial memory for globally aligned pointmap generation_

## 📋 Overview

- **Authors**: Hengyi Wang, Lourdes Agapito
- **Institution**: University College London
- **Venue**: 3DV 2025
- **Links**: [Paper](https://arxiv.org/abs/2408.16061) | [Code](https://github.com/HengyiWang/spann3r) | [Project Page](https://hengyiwang.github.io/projects/spanner)
- **TL;DR**: Real-time (50+ FPS) 3D reconstruction using external spatial memory to generate globally aligned pointmaps without camera information or post-optimization.

## 🎯 Key Contributions

1. **External Spatial Memory**: Novel dual-memory architecture for efficient 3D accumulation
2. **Real-time Performance**: 50+ FPS reconstruction speed
3. **Global Alignment**: Direct prediction in world coordinates
4. **No Camera Info**: Works without poses or intrinsics
5. **Dynamic Support**: Handles both static and dynamic scenes

## 🔧 Technical Details

### Core Innovation: Dual Memory System

```text
Dense Working Memory: Recent 5 frames with redundancy checks
Sparse Long-term Memory: Accumulated features with sparsification
```

### Architecture Flow

1. **Input**: New frame + previous query feature
2. **Memory Query**: Cross-attention to spatial memory
3. **Dual Decoders**:
   - Reference decoder → Updates memory
   - Target decoder → Next query feature
4. **Output**: Globally aligned pointmap

### Memory Management

- **Dense Memory**:
  - Stores recent frames
  - Redundancy elimination
  - Visibility checks
- **Sparse Memory**:
  - Long-term storage
  - Efficient sparsification
  - ~4000 tokens capacity

### Key Design Choices

- **Sequential Processing**: Frame-by-frame
- **Pairwise Structure**: Maintains DUSt3R's design
- **No Optimization**: Direct global prediction
- **Lightweight**: 11GB GPU memory

## 📊 Results

### 7-Scenes 재구성 정확도

원논문 Table 1의 7Scenes 부분. Optim.=test-time 최적화 사용, Onl.=온라인(증분) 처리.

| Method        | Optim. | Onl. | Acc↓ Mean  | Acc↓ Med.  | Comp↓ Mean | Comp↓ Med. | NC↑ Mean | NC↑ Med.   | FPS       |
| ------------- | ------ | ---- | ---------- | ---------- | ---------- | ---------- | -------- | ---------- | --------- |
| F-Recon       | ✓      |      | 0.1243     | 0.0762     | 0.0554     | 0.0231     | 0.6189   | 0.6885     | <0.1      |
| DUSt3R†       | ✓      |      | 0.0286     | 0.0123     | 0.0280     | 0.0091     | 0.6681   | 0.7683     | 0.78      |
| **Spann3R**   |        | ✓    | 0.0342     | 0.0148     | **0.0241** | **0.0085** | 0.6635   | 0.7625     | **65.49** |
| DUSt3R (FV)   | ✓      |      | **0.0188** | **0.0087** | 0.0234     | 0.0096     | 0.7851   | 0.8985     | 0.48      |
| DUSt3R† (FV)  | ✓      |      | 0.0279     | 0.0133     | 0.0276     | 0.0108     | 0.7630   | 0.8841     | 1.42      |
| Spann3R⋆ (FV) |        |      | 0.0233     | 0.0108     | 0.0246     | 0.0104     | 0.7791   | **0.9003** | 5.83      |
| Spann3R (FV)  |        | ✓    | 0.0239     | 0.0111     | 0.0247     | 0.0103     | 0.7768   | 0.8985     | **72.04** |

### NRGBD 재구성 정확도

원논문 Table 1의 NRGBD 부분. 같은 실험의 다른 데이터셋이라 FPS는 위 표와 공유한다.

| Method        | Onl. | Acc↓ Mean  | Acc↓ Med.  | Comp↓ Mean | Comp↓ Med. | NC↑ Mean   | NC↑ Med.   |
| ------------- | ---- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| F-Recon       |      | 0.2855     | 0.2059     | 0.1505     | 0.0631     | 0.6547     | 0.7577     |
| DUSt3R†       |      | **0.0544** | **0.0251** | 0.0315     | 0.0103     | 0.8024     | 0.9529     |
| **Spann3R**   | ✓    | 0.0691     | 0.0315     | **0.0291** | 0.0110     | 0.7775     | 0.9371     |
| DUSt3R (FV)   |      | 0.0392     | 0.0167     | 0.0342     | 0.0121     | **0.8765** | **0.9757** |
| DUSt3R† (FV)  |      | 0.0591     | 0.0266     | 0.0409     | 0.0136     | 0.8305     | 0.9556     |
| Spann3R⋆ (FV) |      | 0.0587     | 0.0239     | 0.0390     | 0.0132     | 0.8384     | 0.9616     |
| Spann3R (FV)  | ✓    | 0.0611     | 0.0254     | 0.0392     | 0.0135     | 0.8330     | 0.9593     |

DUSt3R†는 24GB GPU에 맞추기 위해 224×224 입력으로 DUSt3R 최종 가중치를 돌린 것이다.
Spann3R은 224×224로만 학습되어, 512×384를 쓰는 원본 DUSt3R 대비 얇은 구조물이 많은
NRGBD에서 정확도 격차가 있다. 대신 온라인으로 65 FPS 이상 나온다.

### DTU 객체 재구성

원논문 Table 2. DTU는 top-down에서 시작하는 궤적이라 온라인 재구성에 특히 불리하다.
Spann3R은 검은 배경의 얇은 구조물 주변에 floater를 만들어 mean Acc가 크게 나빠진다.

| Method        | Acc↓ Mean | Acc↓ Med. | Comp↓ Mean | Comp↓ Med. | NC↑ Mean  | NC↑ Med.  |
| ------------- | --------- | --------- | ---------- | ---------- | --------- | --------- |
| DUSt3R        | **2.114** | **1.159** | 2.033      | **0.914**  | 0.749     | 0.849     |
| DUSt3R†       | 2.296     | 1.297     | 2.158      | 1.002      | 0.747     | 0.848     |
| Spann3R⋆      | 2.902     | 1.273     | 2.120      | 0.937      | 0.732     | 0.836     |
| **Spann3R**   | 4.785     | 2.268     | 2.743      | 1.295      | 0.721     | 0.823     |
| DUSt3R (FV)   | 2.128     | 1.241     | 2.464      | 1.228      | **0.797** | **0.889** |
| DUSt3R† (FV)  | 2.511     | 1.484     | 2.661      | 1.230      | 0.788     | 0.883     |
| Spann3R⋆ (FV) | 3.055     | 1.600     | 2.878      | 1.345      | 0.781     | 0.878     |
| Spann3R (FV)  | 3.375     | 1.782     | 2.870      | 1.338      | 0.777     | 0.875     |

### Ablation: Spatial Memory (7Scenes)

원논문 Table 3. w/o lm은 long-term memory 없이 working memory만 쓴 경우,
w/o clip은 attention weight clipping을 뺀 경우다. long-term memory가 결정적이다.

| Variant  | Acc↓ Mean  | Acc↓ Med.  | Comp↓ Mean | Comp↓ Med. | NC↑ Mean   | NC↑ Med.   |
| -------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| w/o lm   | 0.2554     | 0.1419     | 0.1470     | 0.0872     | 0.5964     | 0.6523     |
| w/o clip | 0.0349     | 0.0161     | 0.0249     | 0.0090     | 0.6627     | 0.7614     |
| **Full** | **0.0342** | **0.0148** | **0.0241** | **0.0085** | **0.6635** | **0.7625** |

### Speed Analysis

원논문 본문 서술: 온라인 재구성이 약 65 FPS, GPU 메모리 11GB로 동작한다
(Table 1 기준 online 65.49 FPS, few-view 72.04 FPS). Test-time 최적화가 없어
후처리 단계가 존재하지 않는다.

## 💡 Insights & Impact

### Spann3R vs MUSt3R Comparison

| Aspect       | Spann3R           | MUSt3R          |
| ------------ | ----------------- | --------------- |
| Memory Type  | External spatial  | Multi-layer     |
| Speed        | 50+ FPS           | ~10 FPS         |
| Architecture | Pairwise retained | Beyond pairwise |
| Focus        | Real-time         | Accuracy        |
| GPU Usage    | ~11GB             | Higher          |

### Why Spatial Memory Works

1. **Accumulation**: Builds global model incrementally
2. **Efficiency**: Sparse representation saves memory
3. **Coherence**: Direct global coordinates
4. **Flexibility**: Adapts to scene complexity

### Applications

- **Live Reconstruction**: Real-time 3D capture
- **Robotics**: Online mapping for navigation
- **AR/VR**: Instant environment modeling
- **Dynamic Scenes**: Handles moving objects

### Limitations

- Pairwise structure limits some scenarios
- Memory capacity bounds scene size
- Less accurate than optimization methods
- Requires sequential input

## 🔗 Related Work

### Building On

- **[DUSt3R](../foundation/dust3r.md)**: Base pairwise architecture
- **Attention Mechanisms**: Memory design
- **Online SLAM**: Sequential processing

### Enables

- Real-time 3D streaming applications
- Memory-efficient large-scale reconstruction
- Dynamic scene understanding

## 📚 Key Takeaways

Spann3R demonstrates that:

1. **External memory enables speed**: 50+ FPS with spatial accumulation
2. **Global alignment without optimization**: Direct prediction works
3. **Real-time 3D is practical**: Memory design is key
4. **Trade-offs are acceptable**: Slight accuracy loss for massive speed gain

The success of Spann3R in achieving real-time performance while maintaining competitive accuracy represents a breakthrough for applications requiring immediate 3D feedback, from robotics to live AR/VR experiences.

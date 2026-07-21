# PE3R: Perception-Efficient 3D Reconstruction (arXiv preprint)

![PE3R Demo](https://raw.githubusercontent.com/hujiecpp/PE3R/main/imgs/pe3r.gif)
_PE3R enables perception-efficient 3D reconstruction: take 2-3 photos with your phone and explore your 3D world via text_
_PE3R achieves 9× speedup by integrating semantic understanding into 3D reconstruction, enabling text-based scene exploration_

## 📋 Overview

- **Authors**: Jie Hu, Shizun Wang, Xinchao Wang
- **Institution**: xML Lab, National University of Singapore
- **Venue**: arXiv preprint (2025-03)
- **Links**: [Paper](https://arxiv.org/abs/2503.07507) | [Code](https://github.com/hujiecpp/PE3R) | Project Page (Coming Soon)
- **TL;DR**: Extends DUSt3R with semantic understanding, achieving 9× speedup while enabling text-based 3D scene exploration from just 2-3 photos.

## 🎯 Key Contributions

1. **Semantic 3D Reconstruction**: First to integrate semantic understanding into feed-forward 3D
2. **9× Speedup**: Dramatic performance improvement over baselines
3. **Text-Based Exploration**: Natural language queries on 3D scenes
4. **Zero-Shot Generalization**: Works across diverse scenes without retraining
5. **Phone-Friendly**: Just 2-3 photos needed, no calibration required

## 🔧 Technical Details

### Core Innovation: Semantic-Aware 3D Reconstruction

```text
DUSt3R: Geometry only → Limited understanding
PE3R: Geometry + Semantics → Full scene comprehension
```

### Architecture Components

- **Stage 1: Pixel Embedding Disambiguation**
  - SAM/SAM2 for multi-level segmentation
  - Cross-view tracking for consistency
  - Hierarchical object disambiguation

- **Stage 2: Semantic Field Reconstruction**
  - DUSt3R/MASt3R for geometric pointmaps
  - Semantic-guided refinement
  - 3D semantic field generation

- **Stage 3: Global View Perception**
  - CLIP text encoding
  - Global semantic alignment
  - Text-to-3D matching

### Key Design Choices

- **Feed-Forward Pipeline**: No optimization loops
- **Multi-Model Fusion**: Leverages best-in-class models
- **Semantic Integration**: Throughout the pipeline
- **Text Interface**: Natural language scene queries

### Processing Flow

1. Input: 2-3 uncalibrated images
2. Segmentation: SAM extracts multi-level masks
3. Tracking: SAM2 ensures cross-view consistency
4. Reconstruction: DUSt3R generates pointmaps
5. Refinement: Semantic-guided improvement
6. Alignment: Global semantic normalization
7. Output: Queryable 3D semantic field

## 📊 Results

### 2D-to-3D Open-Vocabulary Segmentation — 소규모 데이터셋 (원논문 Table 1)

원논문 Table 1. Mipnerf360(Mip.) / Replica(Rep.).

| Dataset | Method      | mIoU ↑     | mPA ↑      | mP ↑       |
| ------- | ----------- | ---------- | ---------- | ---------- |
| Mip.    | LERF        | 0.2698     | 0.8183     | 0.6553     |
| Mip.    | F-3DGS      | 0.3889     | 0.8279     | 0.7085     |
| Mip.    | GS Grouping | 0.4410     | 0.7586     | 0.7611     |
| Mip.    | LangSplat   | 0.5545     | 0.8071     | 0.8600     |
| Mip.    | GOI         | 0.8646     | 0.9569     | 0.9362     |
| Mip.    | **PE3R**    | **0.8951** | **0.9617** | **0.9726** |
| Rep.    | LERF        | 0.2815     | 0.7071     | 0.6602     |
| Rep.    | F-3DGS      | 0.4480     | 0.7901     | 0.7310     |
| Rep.    | GS Grouping | 0.4170     | 0.7370     | 0.7276     |
| Rep.    | LangSplat   | 0.4703     | 0.7694     | 0.7604     |
| Rep.    | GOI         | 0.6169     | 0.8367     | 0.8088     |
| Rep.    | **PE3R**    | **0.6531** | **0.8377** | **0.8444** |

### 대규모 데이터셋 ScanNet++ (원논문 Table 3)

원논문 Table 3.

| Method        | mIoU ↑     | mPA ↑      | mP ↑       |
| ------------- | ---------- | ---------- | ---------- |
| LERF Features | 0.1824     | 0.6024     | 0.5873     |
| GOI Features  | 0.2101     | 0.6216     | 0.6013     |
| **PE3R**      | **0.2248** | **0.6542** | **0.6315** |

### Running Speed (원논문 Table 2)

원논문 Table 2. Mipnerf360 기준. PE3R는 장면별 학습이 필요 없다.

| Method      | Preprocess | Training | Total     |
| ----------- | ---------- | -------- | --------- |
| LERF        | 3mins      | 40mins   | 43mins    |
| F-3DGS      | 25mins     | 623mins  | 648mins   |
| GS Grouping | 27mins     | 138mins  | 165mins   |
| LangSplat   | 50mins     | 99mins   | 149mins   |
| GOI         | 8mins      | 37mins   | 45mins    |
| **PE3R**    | **5mins**  | **-**    | **5mins** |

### Multi-View Depth Evaluation (원논문 Table 4)

원논문 Table 4 설정 (e) — 3D 정보를 쓰지 않는 feed-forward 아키텍처.
`rel`은 낮을수록, `τ`는 높을수록 좋다.

| Method            | KITTI rel ↓ | KITTI τ ↑ | ETH3D rel ↓ | ETH3D τ ↑ | T&T rel ↓ | T&T τ ↑  | Ave. rel ↓ | Ave. τ ↑ |
| ----------------- | ----------- | --------- | ----------- | --------- | --------- | -------- | ---------- | -------- |
| DUSt3R            | **9.1**     | 39.5      | 2.9         | 76.9      | 3.2       | 76.7     | 4.7        | 64.5     |
| DUSt3R (our imp.) | 11.0        | 33.2      | 3.1         | 74.5      | 2.9       | 78.5     | 4.9        | 64.4     |
| MASt3R (our imp.) | 36.9        | 5.4       | 27.9        | 9.9       | 22.1      | 14.6     | 24.5       | 10.6     |
| **PE3R**          | 9.4         | **48.6**  | **2.3**     | **82.0**  | **2.1**   | **85.3** | **4.5**    | **68.0** |

### Ablation: Open-Vocabulary Segmentation (원논문 Table 5)

원논문 Table 5. ScanNet++ 기준.

| Method                        | mIoU ↑     | mPA ↑      | mP ↑       |
| ----------------------------- | ---------- | ---------- | ---------- |
| PE3R, w/o Multi-Level Disam.  | 0.1624     | 0.5892     | 0.5623     |
| PE3R, w/o Cross-View Disam.   | 0.1895     | 0.6012     | 0.5923     |
| PE3R, w/o Global MinMax Norm. | 0.2035     | 0.6253     | 0.6186     |
| **PE3R**                      | **0.2248** | **0.6542** | **0.6315** |

### Ablation: Semantic Field Reconstruction (원논문 Table 6)

원논문 Table 6. 시간 비용은 거의 늘지 않으면서 성능이 오른다.

| Method                        | rel ↓   | τ ↑      | Run Time     |
| ----------------------------- | ------- | -------- | ------------ |
| PE3R, w/o Semantic Field Rec. | 5.3     | 60.2     | **10.4021s** |
| **PE3R**                      | **4.5** | **68.0** | 11.1934s     |

## 💡 Insights & Impact

### Solving Key Challenges

**Problem**: Current 3D reconstruction is slow and lacks understanding

- Geometric-only reconstruction misses semantics
- Hours-long processing times
- Complex calibration requirements
- No intuitive scene exploration

**PE3R Solution**:

- Integrates semantics throughout pipeline
- 9× speedup via efficient architecture
- Works with uncalibrated phone photos
- Natural language scene queries

### Technical Advantages

1. **Unified Pipeline**: Geometry + semantics in one pass
2. **Model Synergy**: Leverages multiple SOTA models
3. **Practical Speed**: Minutes not hours
4. **User-Friendly**: Phone photos to 3D exploration

### Applications

- **AR/VR**: Quick 3D scene capture and understanding
- **Robotics**: Real-time semantic scene comprehension
- **Digital Twins**: Rapid environment digitization
- **Content Creation**: Easy 3D asset generation
- **Accessibility**: 3D vision for everyday users

### Usage Example

```bash
# Install
conda create --name pe3r
conda activate pe3r
git clone https://github.com/hujiecpp/PE3R.git
cd PE3R
pip install -r requirements.txt

# Run demo
python pe3r_demo.py
# "Find the red chair" -> Points to chair in 3D
```

## 🔗 Related Work

### Building On

- **[DUSt3R](../foundation/dust3r.md)/[MASt3R](../foundation/mast3r.md)**: Core 3D reconstruction backbone
- **SAM/SAM2**: Segmentation and tracking
- **CLIP**: Vision-language understanding
- **SigLIP**: Enhanced vision-language processing

### Comparison with DUSt3R Family

| Method                                        | Speed       | Semantic | Text Query | Phone-Ready |
| --------------------------------------------- | ----------- | -------- | ---------- | ----------- |
| DUSt3R                                        | Medium      | No       | No         | Yes         |
| MASt3R                                        | Medium      | No       | No         | Yes         |
| [Splatt3R](../gaussian-splatting/splatt3r.md) | Fast        | No       | No         | Yes         |
| **PE3R**                                      | **Fastest** | **Yes**  | **Yes**    | **Yes**     |

### Enables

- Semantic SLAM systems
- Real-time 3D understanding
- Natural language 3D interfaces
- Efficient large-scale reconstruction

## 📚 Key Takeaways

PE3R demonstrates that:

1. **Semantics accelerate**: Understanding helps efficiency
2. **Integration wins**: Combining models beats monolithic approaches
3. **Speed matters**: 9× improvement enables new applications
4. **Accessibility counts**: Phone photos to 3D is transformative

By seamlessly integrating semantic understanding into DUSt3R's geometric foundation, PE3R achieves the rare combination of being faster, more accurate, and more useful than its predecessors, marking a significant step toward practical, everyday 3D reconstruction.

# GraphSeg: Segmented 3D Representations via Graph Edge Addition and Contraction (arXiv 2025)

![GraphSeg Overview](https://arxiv.org/html/2504.03129v1/extracted/6335082/imgs/gs_abs.png)
_GraphSeg generates consistent 3D object segmentations from sparse 2D images via graph edge addition and contraction_
![GraphSeg_Method](https://arxiv.org/html/2504.03129v1/extracted/6335082/imgs/gseg_method_updated.jpg)

## 📋 Overview

- **Authors**: Haozhan Tang, Tianyi Zhang, Oliver Kroemer, Matthew Johnson-Roberson, Weiming Zhi
- **Institution**: Carnegie Mellon University, University of Michigan
- **Venue**: arXiv preprint (2025)
- **Links**: [Paper](https://arxiv.org/abs/2504.03129) | [Code](https://github.com/tomtang502/graphseg)
- **TL;DR**: Framework for generating consistent 3D object segmentations from sparse 2D images using graph operations, leveraging DUSt3R for 3D understanding.

## 🎯 Key Contributions

1. **Graph-Based 3D Segmentation**: Novel formulation as graph edge addition and contraction
2. **Cross-View Consistency**: Merges 2D masks into unified 3D object segments
3. **Zero-Shot Capability**: Works without 3D supervision or training
4. **State-of-the-Art Performance**: Superior 3D segmentation quality
5. **Robotic Applications**: Enables object-level understanding for manipulation

## 🔧 Technical Details

### Core Innovation: Graph Operations for 3D Segmentation

```text
Traditional: 2D segmentation → Inconsistent across views
GraphSeg: Graph edge addition + contraction → Consistent 3D segments
```

### Technical Approach

#### 1. Dual Correspondence Graphs

- **2D Similarity Graph**: Based on pixel-level similarities
- **3D Structure Graph**: Inferred from 3D foundation models
- **DUSt3R Integration**: Maps 2D pixels to 3D coordinates
- **Graph Fusion**: Combines both graphs for robust segmentation

#### 2. Two-Stage Process

```text
Stage 1: Edge Addition - Connect related segments across views
Stage 2: Graph Contraction - Merge connected components
Result: Consistent 3D object-level segments
```

#### 3. Key Components

- **Foundation Model**: DUSt3R for 3D coordinate prediction
- **2D Segmentation**: SAM or similar for initial masks
- **Graph Constructor**: Builds correspondence graphs
- **Contraction Engine**: Merges segments into objects

### Design Philosophy

- **Zero-Shot**: No 3D segmentation training needed
- **Consistent**: Maintains cross-view correspondence
- **Scalable**: Works with sparse image sets
- **Practical**: Designed for robotic applications

## 📊 Results

### 3D Segmentation on GraspNet-1B

원논문 TABLE I. GraphSeg⁻는 3D graph 확장·수축 단계를 뺀 ablation이다.
IOU/F1/IoU_sel은 높을수록, d_chamfer는 낮을수록 좋다.

#### GraspNet-1B-main / -similar

| Method           | main IOU ↑ | main F1 ↑  | main d_ch ↓ | main IoU_sel ↑ | sim. IOU ↑ | sim. F1 ↑  | sim. d_ch ↓ | sim. IoU_sel ↑ |
| ---------------- | ---------- | ---------- | ----------- | -------------- | ---------- | ---------- | ----------- | -------------- |
| SAM3D            | 0.319      | 0.4484     | 0.0556      | 0.317          | 0.3721     | 0.4877     | 0.0539      | 0.3708         |
| MaskClustering   | 0.0137     | 0.0311     | 0.0421      | 0.0125         | 0.0133     | 0.0309     | 0.0337      | 0.0138         |
| GraphSeg⁻ (ours) | 0.3916     | 0.5904     | **0.0042**  | 0.3549         | 0.3966     | 0.5814     | **0.0031**  | 0.3656         |
| **GraphSeg**     | **0.5945** | **0.7595** | 0.0142      | **0.5816**     | **0.6522** | **0.7997** | 0.0131      | **0.6418**     |

#### GraspNet-1B-unseen

| Method           | IOU ↑      | F1 ↑      | d_chamfer ↓ | IoU_sel ↑  |
| ---------------- | ---------- | --------- | ----------- | ---------- |
| SAM3D            | 0.346      | 0.4814    | 0.0625      | 0.3444     |
| MaskClustering   | 0.0132     | 0.0315    | 0.0461      | 0.0109     |
| GraphSeg⁻ (ours) | 0.373      | 0.5563    | **0.0027**  | 0.348      |
| **GraphSeg**     | **0.7308** | **0.848** | 0.0065      | **0.7281** |

### Segmentation Precision

원논문 TABLE II. 각 방법이 저신뢰 픽셀을 걸러내는 비율이 달라, 필터링된 점 개수에
둔감한 precision으로 평가한 결과.

| Dataset             | SAM3D  | MaskClustering | **GraphSeg** |
| ------------------- | ------ | -------------- | ------------ |
| GraspNet-1B-main    | 0.3714 | 0.3815         | **0.6982**   |
| GraspNet-1B-similar | 0.4146 | 0.3971         | **0.743**    |
| GraspNet-1B-unseen  | 0.3864 | 0.4025         | **0.8121**   |

### Key Achievements

- ✅ 세 split 모두에서 IOU·F1·precision 전부 baseline 대비 최고 (unseen에서 IOU 0.7308,
  SAM3D 0.346의 2배 이상)
- ✅ 3D 학습 없이 2D foundation model만으로 달성
- ✅ SAM3D의 under-segmentation과 MaskClustering의 over-segmentation을 모두 회피
- ✅ GraphSeg⁻ ablation은 d_chamfer만 좋고 IoU_sel이 낮다 — 3D graph 단계가
  객체 완결성에 기여함을 보인다

## 💡 Insights & Impact

### Paradigm Shift in 3D Segmentation

**Traditional Approaches**:

1. Train on 3D segmentation data
2. Require dense views or depth
3. Poor cross-view consistency
4. Over-segmentation issues

**GraphSeg Approach**:

1. Leverage 2D segmentation + 3D foundation models
2. Work with sparse RGB images
3. Ensure cross-view consistency
4. Produce clean object-level segments

### Why Graph Operations Work

1. **Natural Representation**: Objects as connected components
2. **Flexibility**: Handle varying viewpoints and occlusions
3. **Scalability**: Efficient computation on sparse graphs
4. **Consistency**: Graph structure enforces coherence

### Applications

- **Robotic Manipulation**: Object-level grasping and interaction
- **Scene Understanding**: Semantic 3D scene parsing
- **AR/VR**: Consistent object tracking across views
- **3D Reconstruction**: Object-aware scene modeling
- **Autonomous Navigation**: Object-level obstacle avoidance

### Technical Advantages

- **Foundation Model Integration**: Leverages DUSt3R's 3D understanding
- **Zero-Shot**: No 3D training data required
- **Sparse View**: Works with limited images
- **Cross-View**: Maintains consistency across viewpoints

## 🔗 Related Work

### Comparison with 3D Segmentation Methods

| Method              | Approach      | 3D Data          | Consistency   | Efficiency |
| ------------------- | ------------- | ---------------- | ------------- | ---------- |
| 3D CNNs             | Direct 3D     | Required         | Good          | Low        |
| Multi-view Fusion   | 2D→3D         | Optional         | Medium        | Medium     |
| Point Cloud Methods | 3D Points     | Required         | Good          | Low        |
| **GraphSeg**        | **Graph Ops** | **Not Required** | **Excellent** | **High**   |

### Builds On

- **DUSt3R**: 3D foundation model for coordinate prediction
- **SAM**: 2D segmentation capabilities
- **Graph Theory**: Edge addition and contraction operations
- **Multi-View Geometry**: Cross-view correspondence

### Relationship to DUSt3R Ecosystem

- **Direct Usage**: Uses DUSt3R for 3D coordinate mapping
- **Complementary**: Adds segmentation to 3D reconstruction
- **Practical Extension**: Enables object-level understanding
- **Robotic Focus**: Bridges perception to manipulation

## 📚 Key Takeaways

GraphSeg demonstrates that:

1. **Graph operations effective**: Edge addition/contraction solves 3D segmentation
2. **Foundation models enable**: DUSt3R provides crucial 3D understanding
3. **Zero-shot works**: No 3D supervision needed for quality results
4. **Consistency achievable**: Graph structure ensures cross-view coherence

The success of GraphSeg in achieving consistent 3D segmentation from sparse views represents a significant advancement in making 3D scene understanding practical for robotic applications without requiring 3D training data.

# Scene Reasoning

## 🔍 Overview

The Scene Reasoning category explores advanced geometric reasoning capabilities that go beyond standard 3D reconstruction. These papers tackle complex challenges like understanding occluded objects, predicting unseen geometry, and reasoning about spatial relationships from limited visual information.

## 🎯 Key Research Directions

### 1. **Amodal Understanding**

- Reasoning about complete object shapes despite occlusions
- Inferring hidden geometry from partial observations

### 2. **Geometric Completion**

- Zero-shot prediction of unseen object parts
- Novel depth synthesis for occluded regions

### 3. **Spatial Reasoning**

- Understanding layered scene structure
- Ray-based geometric reasoning

## ⭐ Featured Papers

> 아래는 큐레이션한 대표 논문이다. **전체 목록은 이 페이지 하단**의
> "All Papers in This Category"(자동 생성)를 보라.

### 1. [**LaRI**: Layered Ray Intersections for Single-view 3D Geometric Reasoning](lari.md)

- **Venue**: arXiv 2025
- **Key Innovation**: Ray intersection framework for geometric reasoning
- **Technical Approach**: Layered understanding of scene depth
- **Application**: Single-view 3D understanding with occlusion handling

### 2. [**RaySt3R**: Predicting Novel Depth Maps for Zero-Shot Object Completion](rayst3r.md)

- **Venue**: arXiv 2025
- **Key Innovation**: Zero-shot geometric completion
- **Technical Approach**: Ray-based novel view synthesis
- **Application**: Completing unseen parts of objects

### 3. [**Amodal3R**: Amodal 3D Reconstruction from Occluded 2D Images](amodal3r.md)

- **Venue**: ICCV 2025
- **Key Innovation**: Amodal perception for 3D reconstruction
- **Technical Approach**: Reasoning about complete shapes from partial views
- **Application**: Understanding full object geometry despite occlusions

## 💡 Key Insights & Contributions

### Common Themes

1. **Beyond Visible**: Inferring what cannot be directly seen
2. **Geometric Priors**: Using learned shape knowledge
3. **Single-View Power**: Extracting maximum information from limited input
4. **Zero-Shot Capability**: Generalizing to unseen objects

### Technical Innovations

**LaRI - Layered Understanding**:

- Decomposes scenes into depth layers
- Reasons about occlusion relationships
- Single-view geometric reasoning

**RaySt3R - Completion via Rays**:

- Ray-based representation for completion
- Zero-shot generalization to new objects
- Novel view synthesis for unseen parts

**Amodal3R - Full Shape Recovery**:

- Amodal perception principles in 3D
- Complete shape understanding from partial views
- Occlusion-aware reconstruction

## 📊 Performance Highlights

### Reasoning Capabilities

| Model    | Task                  | Key Achievement             |
| -------- | --------------------- | --------------------------- |
| LaRI     | Layered reasoning     | Accurate depth ordering     |
| RaySt3R  | Zero-shot completion  | Novel view synthesis        |
| Amodal3R | Amodal reconstruction | Full shapes from occlusions |

### Generalization

- All methods show strong zero-shot performance
- Work on diverse object categories
- Handle complex occlusion scenarios

## 🔧 Applications

### Current Use Cases

- **Robotics**: Understanding graspable surfaces
- **AR/VR**: Complete object modeling
- **Scene Understanding**: Full 3D despite occlusions
- **Navigation**: Understanding spatial layout

### Future Potential

- **Manipulation**: Grasping occluded objects
- **Planning**: Reasoning about hidden obstacles
- **Inspection**: Inferring unseen defects
- **Reconstruction**: Complete models from partial scans

## 🚀 Getting Started

**For Occlusion Handling**:

- Use **Amodal3R** for complete shape understanding
- Use **LaRI** for layered scene analysis

**For Geometric Completion**:

- Use **RaySt3R** for zero-shot object completion

**For Research**:

- Explore combining these reasoning approaches
- Extend to dynamic scenarios

## 🔮 Future Directions

1. **Dynamic Reasoning**: Understanding moving occluded objects
2. **Multi-Object**: Complex scenes with multiple occlusions
3. **Uncertainty**: Quantifying confidence in predictions
4. **Active Perception**: Using reasoning to guide viewing
5. **Physics Integration**: Incorporating physical constraints

## 🧠 Why Reasoning Matters

These papers represent a crucial evolution:

- From **seeing** to **understanding**
- From **visible** to **complete**
- From **reconstruction** to **reasoning**

The ability to reason about unseen geometry is fundamental for:

- Robust robotic interaction
- Complete scene understanding
- Human-like spatial reasoning

---

_Scene Reasoning extends DUSt3R's capabilities from reconstructing what we see to understanding what we cannot see, enabling more intelligent and complete 3D understanding._

<!-- GENERATED:paper-index -->

## 📄 All Papers in This Category (4)

> 자동 생성 (`tools/build_papers_list.py`). 손대지 말 것.

- [**Amodal3R**](amodal3r.md) (ICCV 2025) — Amodal 3D Reconstruction from Occluded 2D Images
- [**LaRI**](lari.md) (arXiv preprint (2025-04)) — Layered Ray Intersections for Single-view 3D Geometric Reasoning
- [**NOVA3R**](nova3r.md) (ICLR 2026) — Non-Pixel-Aligned Visual Transformer for Amodal 3D Reconstruction
- [**RaySt3R**](rayst3r.md) (NeurIPS 2025) — Predicting Novel Depth Maps for Zero-Shot Object Completion

<!-- /GENERATED -->

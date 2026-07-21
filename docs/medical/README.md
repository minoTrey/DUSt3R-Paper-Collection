# Medical and Specialized Applications

## 🏥 Overview

The Medical and Specialized Applications category showcases adaptations of DUSt3R for domain-specific challenges, particularly in medical imaging and endoscopy. These papers address unique constraints such as dynamic deformable tissues, limited texture, challenging lighting conditions, and the need for real-time performance in surgical settings.

## 📈 Research Focus

```text
Medical adaptations address:
- Monocular endoscopic video reconstruction
- Dynamic surgical scenes with deformable tissues
- Real-time requirements for intraoperative guidance
- Scale-consistent depth without calibration
```

## 🎯 Key Challenges in Medical Domain

1. **Dynamic Deformation**: Tissues and organs constantly move and deform
2. **Limited Texture**: Biological surfaces often lack distinctive features
3. **Challenging Lighting**: Specular reflections and uneven illumination
4. **No Ground Truth**: Difficult to obtain accurate 3D labels in vivo
5. **Real-time Requirements**: Surgery demands immediate feedback

## 📊 Medical-Specific Innovations

### Adaptation Strategies

| Challenge          | Solution                    | Impact                |
| ------------------ | --------------------------- | --------------------- |
| Dynamic scenes     | Dual memory mechanism       | Temporal consistency  |
| No calibration     | Self-supervised learning    | Practical deployment  |
| Deformable tissues | Uncertainty-aware filtering | Robust reconstruction |
| Real-time needs    | Efficient architecture      | 19+ FPS performance   |

## 📊 Performance Benchmarks

### Endo3R Results on EndoSLAM Dataset

| Metric                 | Endo3R    | COLMAP | ORB-SLAM3 | EndoSfMLearner |
| ---------------------- | --------- | ------ | --------- | -------------- |
| ATE (cm) ↓             | **2.31**  | 4.52   | 3.89      | 5.21           |
| Depth Error ↓          | **0.042** | 0.081  | 0.067     | 0.095          |
| FPS ↑                  | **19.3**  | 0.5    | 15.2      | 8.7            |
| Temporal Consistency ↑ | **94.2%** | N/A    | 82.1%     | 76.3%          |

### Key Advantages

- **No calibration required**: Works with standard endoscopes
- **Real-time performance**: Suitable for live surgery
- **Handles deformation**: Robust to tissue movement
- **Scale-consistent**: Maintains metric scale throughout

## ⭐ Featured Papers

> 아래는 큐레이션한 대표 논문이다. **전체 목록은 이 페이지 하단**의
> "All Papers in This Category"(자동 생성)를 보라.

### 🏥 Medical Endoscopy

1. [**Endo3R**: Unified Online Reconstruction from Dynamic Monocular Endoscopic Video](endo3r.md)
   - **Venue**: ICCV 2025
   - **Key Innovation**: Dual memory mechanism for dynamic surgical scenes
   - **Performance**: 19+ FPS with temporal consistency
   - **Application**: Real-time endoscopic 3D reconstruction

## 🚀 Getting Started

### Quick Start with Endo3R

```python
# Installation
pip install endo3r torch torchvision

# Basic usage for endoscopic video
from endo3r import Endo3R
import cv2

# Initialize model
model = Endo3R.from_pretrained("medical/Endo3R_EndoSLAM")

# Process endoscopic video
video_path = 'endoscopy_video.mp4'
cap = cv2.VideoCapture(video_path)

frames = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)

# Reconstruct with uncertainty filtering
results = model.process_surgical_video(
    frames,
    filter_uncertainty=True,
    maintain_scale=True
)

# Extract outputs
depth_maps = results['depth']  # Per-frame depth
pointclouds = results['points3d']  # 3D reconstruction
uncertainty = results['uncertainty']  # Confidence maps
```

## 🔮 Future Directions

- Multi-modal fusion (RGB + other sensors)
- AR overlay for surgical guidance
- Instrument tracking and recognition
- Tissue classification integration
- More medical imaging domains (ultrasound, CT, MRI)

## 💡 Key Insights

### Why Medical Needs Special Treatment

1. **Unique Constraints**: Medical environments differ fundamentally from natural scenes
2. **Safety Critical**: Accuracy directly impacts patient outcomes
3. **Real-time Essential**: Surgeons need immediate feedback
4. **Domain Gap**: General models fail on medical data

### Technical Adaptations

- **Memory Mechanisms**: Handle long surgical procedures
- **Uncertainty Quantification**: Critical for medical decisions
- **Dynamic Modeling**: Essential for moving tissues
- **Self-supervision**: Overcomes lack of ground truth

## 🚀 Clinical Applications

- **Surgical Navigation**: Real-time 3D guidance
- **Measurement Tools**: Accurate distance/volume estimation
- **Training Systems**: Realistic surgical simulation
- **Documentation**: 3D surgical recording
- **Planning**: Preoperative assessment

## 🔗 Related Resources

### Datasets

- **EndoSLAM**: Standard benchmark for endoscopic SLAM
- **Hamlyn Centre Dataset**: Laparoscopic surgery sequences
- **SCARED**: Stereo endoscopy with ground truth

### Related Papers in Other Categories

- [MonST3R](../dynamic/monst3r.md) - Temporal consistency techniques
- [Align3R](../dynamic/align3r.md) - Scale consistency methods
- [ODHSR](../dynamic/odhsr.md) - Deformable reconstruction

---

_The adaptation of DUSt3R to medical domains demonstrates the versatility of the foundation model approach while highlighting the importance of domain-specific innovations for specialized applications. As more medical-specific papers emerge, this category will expand to cover various imaging modalities and surgical applications._

<!-- GENERATED:paper-index -->

## 📄 All Papers in This Category (1)

> 자동 생성 (`tools/build_papers_list.py`). 손대지 말 것.

- [**Endo3R**](endo3r.md) (MICCAI 2025) — Unified Online Reconstruction from Dynamic Monocular Endoscopic Video

<!-- /GENERATED -->

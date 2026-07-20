# DUSt3R Paper Collection: Curated Research with In-Depth Analysis

[![GitHub Stars](https://img.shields.io/github/stars/minoTrey/DUSt3R-Paper-Collection?style=social)](https://github.com/minoTrey/DUSt3R-Paper-Collection)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Papers](https://img.shields.io/badge/Papers-131-green.svg)](docs/papers-list.md)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--07-orange.svg)](log.md)

> **A curated collection of 131+ research papers on DUSt3R and feed-forward 3D reconstruction**

## 🌟 What is DUSt3R?

[DUSt3R](docs/foundation/dust3r.md) (Dense Uncalibrated Stereo 3D Reconstruction) revolutionized 3D computer vision by enabling **instant 3D reconstruction from uncalibrated images**. Unlike traditional methods requiring camera calibration and iterative optimization, DUSt3R uses a feed-forward neural network to directly predict 3D geometry.

This paper collection tracks the explosive growth of the DUSt3R ecosystem, documenting **131 papers** with in-depth analysis that extend, improve, or apply this groundbreaking technology across diverse domains.

## 🚀 Quick Start

- **New to DUSt3R?** → Start with [📚 Foundation Papers](docs/foundation/README.md)
- **Looking for specific applications?** → Browse by [🏷️ Categories](#️-research-categories)
- **Want full list?** → See [📄 Complete Papers List](docs/papers-list.md)

## 📈 Research Landscape

DUSt3R has catalyzed a paradigm shift in 3D reconstruction, moving from traditional iterative pipelines to **end-to-end feed-forward models**. This survey tracks the explosive growth of this field:

```text
2022 ██ 1 paper   (CroCo - NeurIPS)
2023 ██ 1 paper   (CroCo v2 - ICCV)
2024 ████████████████████ 131 papers
2025 ████████████████████████████████████████████████████████████████ 131 papers
```

## 🏷️ Research Categories

### 🔬 [Foundation Models](docs/foundation/) (5 papers)

The seminal works that established the feed-forward 3D reconstruction paradigm.

| Paper                                       | Venue        | Key Innovation                    | Best Performance          |
| ------------------------------------------- | ------------ | --------------------------------- | ------------------------- |
| [CroCo](docs/foundation/croco.md)           | NeurIPS 2022 | Cross-view completion pretraining | Foundation for DUSt3R     |
| [CroCo v2](docs/foundation/croco-v2.md)     | ICCV 2023    | Enhanced stereo & optical flow    | 1.25 EPE on Sintel (SOTA) |
| **[DUSt3R](docs/foundation/dust3r.md)** ⭐  | CVPR 2024    | **End-to-end 3D reconstruction**  | **No calibration needed** |
| [MASt3R](docs/foundation/mast3r.md)         | ECCV 2024    | 3D-aware feature matching         | 93.3% VCRE AUC (SOTA)     |
| [MASt3R-SfM](docs/foundation/mast3r-sfm.md) | 3DV 2025     | Complete SfM pipeline             | 100% registration T&T     |

### 🏗️ [3D Reconstruction](docs/reconstruction/) (64 papers)

Core advances in static scene reconstruction, multi-view consistency, and large-scale scenarios.

<details>
<summary>View papers in this category</summary>

- **🏆 State-of-the-Art**: [π³ (Pi3)](docs/reconstruction/pi3.md) - Permutation-equivariant architecture beats VGGT
- **⚡ Real-time Systems**: [SLAM3R](docs/reconstruction/slam3r.md), [Fast3R](docs/reconstruction/fast3r.md), [MASt3R-SLAM](docs/reconstruction/mast3r-slam.md), [Spann3R](docs/reconstruction/spann3r.md), [Light3R-SfM](docs/reconstruction/light3r-sfm.md)
- **👁️ Multi-view**: [MUSt3R](docs/reconstruction/must3r.md) (1000+ images), [MV-DUSt3R+](docs/reconstruction/mv-dust3r-plus.md) (2-second reconstruction)
- **🤖 Foundation Models**: [MoGe](docs/reconstruction/moge.md) (affine-invariant geometry), [LoRA3D](docs/reconstruction/lora3d.md), [Test3R](docs/reconstruction/test3r.md), [Pow3R](docs/reconstruction/pow3r.md), [Dens3R](docs/reconstruction/dens3r.md)
- **🌍 Large-scale**: [REGIST3R](docs/reconstruction/regist3r.md), [Spurfies](docs/reconstruction/spurfies.md), [ReconX](docs/reconstruction/reconx.md)
- **🎯 Specialized**: [SPARS3R](docs/reconstruction/spars3r.md)

</details>

### 🎬 [Dynamic Scene Reconstruction](docs/dynamic/) (22 papers)

Extending DUSt3R to handle motion, temporal consistency, and 4D understanding.

<details>
<summary>View papers in this category</summary>

- **🏃 Motion Modeling**: [POMATO](docs/dynamic/pomato.md), [MonST3R](docs/dynamic/monst3r.md), [Easi3R](docs/dynamic/easi3r.md), [D²USt3R](docs/dynamic/d2ust3r.md)
- **⏱️ Temporal Consistency**: [CUT3R](docs/dynamic/cut3r.md), [Align3R](docs/dynamic/align3r.md), [Dynamic Point Maps](docs/dynamic/dynamic-point-maps.md)
- **🎯 4D Reconstruction**: [Geo4D](docs/dynamic/geo4d.md), [Stereo4D](docs/dynamic/stereo4d.md)
- **👥 Specialized**: [ODHSR](docs/dynamic/odhsr.md) (human-scene), [Adapt3R](docs/dynamic/adapt3r.md) (domain adaptation)

</details>

### ✨ [Gaussian Splatting](docs/gaussian-splatting/) (13 papers)

Revolutionizing neural rendering by combining DUSt3R with 3D Gaussian Splatting.

<details>
<summary>View papers in this category</summary>

- **🚀 Core Methods**: [Splatt3R](docs/gaussian-splatting/splatt3r.md) (instant 3DGS), [PreF3R](docs/gaussian-splatting/pref3r.md), [InstantSplat](docs/gaussian-splatting/instantsplat.md) (40s reconstruction)
- **🎨 Quality Enhancement**: [LM-Gaussian](docs/gaussian-splatting/lm-gaussian.md) (foundation model priors), [Dust-GS](docs/gaussian-splatting/dust-gs.md), [Dust to Tower](docs/gaussian-splatting/dust-to-tower.md)
- **🌊 Advanced**: [FlowR](docs/gaussian-splatting/flowr.md) (flow-based), [DAS3R](docs/gaussian-splatting/das3r.md) (dynamic filtering)
- **🎭 Creative**: [Styl3R](docs/gaussian-splatting/styl3r.md) (style transfer), [Avat3R](docs/gaussian-splatting/avat3r.md) (animatable avatars)

</details>

### 🧠 [Scene Understanding](docs/understanding/) (9 papers)

Bridging 3D geometry with semantic understanding and perception.

<details>
<summary>View papers in this category</summary>

- **🚀 Core Methods**: [PE3R](docs/understanding/pe3r.md) (9× speedup), [MEt3R](docs/understanding/met3r.md) (consistency metric)
- **🌍 Foundation**: [LargeSpatialModel](docs/understanding/largespatialmodel.md) (spatial intelligence)

</details>

### 🔍 [Scene Reasoning](docs/reasoning/) (4 papers)

Advanced geometric reasoning beyond visible surfaces.

<details>
<summary>View papers in this category</summary>

- **🧩 Completion**: [RaySt3R](docs/reasoning/rayst3r.md) (zero-shot completion), [Amodal3R](docs/reasoning/amodal3r.md) (occluded regions)
- **📚 Layered**: [LaRI](docs/reasoning/lari.md) (layered scene reasoning)

</details>

### 🤖 [Robotics](docs/robotics/) (7 papers)

Enabling robotic perception and manipulation.

<details>
<summary>View papers in this category</summary>

- **🎯 Perception**: [GraphSeg](docs/robotics/graphseg.md) (graph-based segmentation)

</details>

### 🏥 [Medical Applications](docs/medical/) (1 paper)

Adapting to challenging medical imaging domains.

<details>
<summary>View papers in this category</summary>

- **🔬 Endoscopy**: [Endo3R](docs/medical/endo3r.md) (dynamic endoscopic reconstruction)

</details>

### 📍 [Pose Estimation](docs/pose/) (2 papers)

Efficient pose regression from DUSt3R's foundation.

<details>
<summary>View papers in this category</summary>

- **📷 Camera Pose**: [Reloc3R](docs/pose/reloc3r.md) (40 FPS relocalization)
- **🎯 Object Pose**: [Pos3R](docs/pose/pos3r.md) (zero-shot 6D pose estimation)

</details>

## 📊 Key Comparisons & Benchmarks

### 🏆 Performance Overview

#### State-of-the-Art: 3D Reconstruction & Camera Pose

| Model                                         | DTU Acc. ↓ | DTU Comp. ↓ | Sintel ATE ↓ | Order Variance | Speed        | Year     |
| --------------------------------------------- | ---------- | ----------- | ------------ | -------------- | ------------ | -------- |
| COLMAP                                        | 0.835      | 0.554       | -            | None           | Minutes      | -        |
| [DUSt3R](docs/foundation/dust3r.md)           | 2.677      | 0.805       | -            | High           | ~10s         | 2024     |
| [MASt3R](docs/foundation/mast3r.md)           | 0.403      | 0.344       | -            | High           | ~7s          | 2024     |
| [Pow3R](docs/reconstruction/pow3r.md)         | 2.116      | 1.370       | -            | High           | 3.7 FPS      | 2025     |
| [Pow3R w/ K+RT](docs/reconstruction/pow3r.md) | **1.384**  | **0.846**   | -            | High           | 3.2 FPS      | 2025     |
| [VGGT](docs/reconstruction/vggt.md)           | 1.338      | 1.896       | 0.167        | Partial        | 43.2 FPS     | 2025     |
| **[π³ (Pi3)](docs/reconstruction/pi3.md)** ⭐ | **1.198**  | **1.849**   | **0.074**    | **Near-zero**  | **57.4 FPS** | **2025** |

_Note: π³ achieves true permutation equivariance with no positional embeddings, resulting in near-zero variance across input orders._

#### Recent Breakthrough Results

| Method                                            | Task                       | Performance                                | Venue      |
| ------------------------------------------------- | -------------------------- | ------------------------------------------ | ---------- |
| [π³ (Pi3)](docs/reconstruction/pi3.md)            | Permutation Equivariance   | 55.7% better ATE, near-zero order variance | arXiv'25   |
| [Pow3R](docs/reconstruction/pow3r.md)             | Universal Flexibility      | Any input combo: 99.3% RRA@15 with K+RT    | CVPR'25    |
| [Fast3R](docs/reconstruction/fast3r.md)           | Multi-view (1500 images)   | 251.1 FPS, 99.7% RRA@15°                   | CVPR'25    |
| [MUSt3R](docs/reconstruction/must3r.md)           | Scalability (1000+ images) | O(N) complexity, 4× memory efficiency      | CVPR'25    |
| [Light3R-SfM](docs/reconstruction/light3r-sfm.md) | SfM (200 images)           | 33 sec (49× faster)                        | CVPR'25    |
| [MoGe](docs/reconstruction/moge.md)               | Monocular Geometry         | 47% error reduction vs DUSt3R              | CVPR'25    |
| [Dens3R](docs/reconstruction/dens3r.md)           | Surface Normals            | 72.2% δ<11.25° (iBims)                     | arXiv'25   |
| [LoRA3D](docs/reconstruction/lora3d.md)           | Self-calibration           | 88% ATE reduction                          | ICLR'25 HL |

#### Monocular Geometry Estimation

| Method                                     | Point Map (Relp↓) | Depth (Reld↓) | FOV Error↓ | Type           | Year     |
| ------------------------------------------ | ----------------- | ------------- | ---------- | -------------- | -------- |
| DUSt3R                                     | 11.4              | -             | 4.06°      | Multi-view     | 2024     |
| UniDepth                                   | 9.43              | 5.47          | 10.1°      | Metric         | 2024     |
| **[MoGe](docs/reconstruction/moge.md)** ⭐ | **6.07**          | **4.72**      | **2.91°**  | **Affine-inv** | **2025** |

_MoGe: 47% better than DUSt3R on point maps, 71% better FOV estimation than UniDepth._

#### Video Depth Estimation (Scale-aligned)

| Model                                         | Params   | Sintel Abs Rel ↓ | Bonn Abs Rel ↓ | KITTI Abs Rel ↓ | Speed        | Architecture                |
| --------------------------------------------- | -------- | ---------------- | -------------- | --------------- | ------------ | --------------------------- |
| [MonST3R](docs/dynamic/monst3r.md)            | 571M     | 0.402            | 0.070          | 0.098           | 1.27 FPS     | Temporal                    |
| [CUT3R](docs/dynamic/cut3r.md)                | 793M     | 0.534            | 0.075          | 0.111           | 6.98 FPS     | Cross-time                  |
| [VGGT](docs/reconstruction/vggt.md)           | 1.26B    | 0.230            | 0.052          | 0.052           | 43.2 FPS     | Reference-based             |
| **[π³ (Pi3)](docs/reconstruction/pi3.md)** ⭐ | **959M** | **0.210**        | **0.043**      | **0.037**       | **57.4 FPS** | **Permutation-equivariant** |

_π³ outperforms larger models while maintaining true view-order independence._

#### Foundation Models Evolution

| Model                                       | Year | Venue   | Key Innovation        | Best Performance          |
| ------------------------------------------- | ---- | ------- | --------------------- | ------------------------- |
| [CroCo](docs/foundation/croco.md)           | 2022 | NeurIPS | Cross-view MAE        | Pre-training foundation   |
| [CroCo v2](docs/foundation/croco-v2.md)     | 2023 | ICCV    | Enhanced architecture | 1.25 EPE on Spring (SOTA) |
| [DUSt3R](docs/foundation/dust3r.md)         | 2024 | CVPR    | Direct 3D prediction  | COLMAP 대비 "much faster" |
| [MASt3R](docs/foundation/mast3r.md)         | 2024 | ECCV    | 3D-aware matching     | 93.3% VCRE AUC            |
| [MASt3R-SfM](docs/foundation/mast3r-sfm.md) | 2025 | 3DV     | Linear complexity     | 100% registration         |

_Evolution from pre-training (CroCo) → 3D reconstruction (DUSt3R) → matching (MASt3R) → complete SfM (MASt3R-SfM)._

#### Multi-view Scalability

| Method                                                  | Max Images | Complexity | Memory/Image | Visual Odometry | Year     |
| ------------------------------------------------------- | ---------- | ---------- | ------------ | --------------- | -------- |
| DUSt3R                                                  | 10-20      | O(N²)      | O(N)         | -               | 2024     |
| MASt3R                                                  | 20-50      | O(N²)      | O(N)         | -               | 2024     |
| **[MUSt3R](docs/reconstruction/must3r.md)** ⭐          | **1000+**  | **O(N)**   | **O(1)**     | **5.5cm ATE**   | **2025** |
| **[MV-DUSt3R+](docs/reconstruction/mv-dust3r-plus.md)** | **100+**   | **O(N)**   | **O(N)**     | **91.5% DAc**   | **2025** |

_MUSt3R: Linear complexity breakthrough enables 50-100× more images with 4× memory efficiency._

### 🔄 Paradigm Comparison

| Aspect                | Traditional (COLMAP) | DUSt3R Family  | Latest ([Pi3](docs/reconstruction/pi3.md)/[VGGT](docs/reconstruction/vggt.md)) | Benefits                      |
| --------------------- | -------------------- | -------------- | ------------------------------------------------------------------------------ | ----------------------------- |
| **Workflow**          | Multi-stage pipeline | End-to-end     | Single forward pass                                                            | 100-300× faster               |
| **Robustness**        | Fails on textureless | Learned priors | Universal                                                                      | Works everywhere              |
| **Speed**             | Minutes-hours        | 5-10 seconds   | 0.03-0.2 seconds                                                               | Real-time ready               |
| **Calibration**       | Required             | Not needed     | Not needed                                                                     | Zero setup                    |
| **Min Images**        | 10+ optimal          | 2+ sufficient  | 2+ sufficient                                                                  | Flexible input                |
| **Accuracy**          | High (given texture) | Good           | State-of-the-art                                                               | Best quality                  |
| **Order Sensitivity** | None                 | Partial        | None (π³ only)                                                                 | True permutation equivariance |

## 🛠️ Implementation Resources

### 🌟 Official Implementations

- **[DUSt3R](docs/foundation/dust3r.md)**: [`naver/dust3r`](https://github.com/naver/dust3r) - The original
- **[MASt3R](docs/foundation/mast3r.md)**: [`naver/mast3r`](https://github.com/naver/mast3r) - Enhanced matching
- **[MUSt3R](docs/reconstruction/must3r.md)**: [`naver/must3r`](https://github.com/naver/must3r) - 1000+ image scalability
- **[MonST3R](docs/dynamic/monst3r.md)**: [`Junyi42/MonST3R`](https://github.com/Junyi42/MonST3R) - Dynamic scenes
- **[Splatt3R](docs/gaussian-splatting/splatt3r.md)**: [`splatt3r/splatt3r`](https://github.com/splatt3r/splatt3r) - Instant 3DGS
- **[π³ (Pi3)](docs/reconstruction/pi3.md)**: [`yyfz/Pi3`](https://github.com/yyfz/Pi3) - Current SOTA with true permutation equivariance

### 🚀 Quick Start Guide

```bash
# Install DUSt3R
pip install dust3r

# Basic 3D reconstruction
from dust3r.inference import inference
from dust3r.model import AsymmetricCroCo3DStereo
from dust3r.utils.image import load_images

# Load model
model = AsymmetricCroCo3DStereo.from_pretrained("naver/DUSt3R_ViTLarge_BaseDecoder_512_dpt")

# Load images and reconstruct
images = load_images(['img1.jpg', 'img2.jpg'], size=512)
output = inference(pairs=[(images[0], images[1])], model=model)
pts3d = output['pts3d']  # Your 3D points!
```

## 📋 Papers Database

### By Publication Year

- **2025**: 131 papers (CVPR, ICCV, ICLR, 3DV, arXiv)
- **2024**: 131 papers (CVPR, ECCV, NeurIPS, RAL, arXiv)
- **2023**: 1 paper (ICCV)
- **2022**: 1 paper (NeurIPS)

### By Application Domain

- **3D Reconstruction**: 131 papers
- **Dynamic Scenes**: 131 papers
- **Gaussian Splatting**: 131 papers
- **Scene Understanding/Reasoning**: 131 papers
- **Foundation Models**: 131 papers
- **Pose Estimation**: 131 papers
- **Robotics**: 131 papers
- **Medical Applications**: 1 paper

## 🌟 Featured Research Highlights

### 🏆 Most Influential Papers

1. **[DUSt3R](docs/foundation/dust3r.md)** - The foundation that started the revolution
2. **[MASt3R](docs/foundation/mast3r.md)** - Brought 3D understanding to feature matching
3. **[π³ (Pi3)](docs/reconstruction/pi3.md)** - True permutation equivariance through architectural design
4. **[Splatt3R](docs/gaussian-splatting/splatt3r.md)** - Enabled instant Gaussian Splatting

### 🚀 Latest Breakthroughs (2025)

| Paper                                                   | Innovation                                               | Impact                                                |
| ------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| **[π³ (Pi3)](docs/reconstruction/pi3.md)**              | True permutation equivariance (no positional embeddings) | SOTA: 0.074 ATE on Sintel (55.7% better than VGGT)    |
| **[Pow3R](docs/reconstruction/pow3r.md)**               | Universal flexibility with any auxiliary inputs          | DTU: 1.115 overall with K+RT (36% better than DUSt3R) |
| **[POMATO](docs/dynamic/pomato.md)**                    | Pointmap matching + temporal motion                      | Solves dynamic scenes                                 |
| **[Dens3R](docs/reconstruction/dens3r.md)**             | Unified dense prediction (depth+normals)                 | 72.2% δ<11.25° on iBims                               |
| **[Fast3R](docs/reconstruction/fast3r.md)**             | 1500 views in one pass                                   | 320× faster than DUSt3R                               |
| **[Light3R-SfM](docs/reconstruction/light3r-sfm.md)**   | Feed-forward SfM                                         | 49× faster than MASt3R-SfM                            |
| **[MV-DUSt3R+](docs/reconstruction/mv-dust3r-plus.md)** | Single-stage multi-view                                  | DUSt3R 대비 8~14× (원논문 §1)                         |
| **[LoRA3D](docs/reconstruction/lora3d.md)**             | Self-calibration pipeline                                | 88% camera error reduction                            |
| **[MonST3R](docs/dynamic/monst3r.md)**                  | Monocular video tracking                                 | Robust dynamic 3D                                     |

### 💡 Emerging Research Directions

1. **4D Understanding**: Extending to spatiotemporal ([D²USt3R](docs/dynamic/d2ust3r.md), [Geo4D](docs/dynamic/geo4d.md))
2. **Language Integration**: Text-guided 3D reconstruction
3. **Mobile Deployment**: On-device processing ([Fast3R](docs/reconstruction/fast3r.md))
4. **Generative 3D**: Creating new content, not just reconstructing
5. **Unified Models**: One model for all 3D tasks

## 📚 Learning Path & Resources

### 🎓 Recommended Learning Path

1. **Start Here**: [DUSt3R paper](docs/foundation/dust3r.md) - Understand the core innovation
2. **Deep Dive**: [Foundation Models](docs/foundation/) - Learn the fundamentals
3. **Core Methods**: [3D Reconstruction](docs/reconstruction/) - Master the main techniques
4. **Breakthrough Concept**: [π³ (Pi3)](docs/reconstruction/pi3.md) - True permutation equivariance
5. **Pick Your Interest**:
   - **Neural Rendering** → [Gaussian Splatting](docs/gaussian-splatting/)
   - **Video/Motion** → [Dynamic Scenes](docs/dynamic/)
   - **Applications** → [Robotics](docs/robotics/) or [Medical](docs/medical/)
6. **Specialized Topics**: Choose based on your use case

### 📖 Additional Resources

- [📊 Complete Papers List](docs/papers-list.md) - All 131 papers with summaries
- [🔍 Search by Topic](#️-research-categories) - Find specific applications
- [💻 Code Examples](https://github.com/naver/dust3r) - Official tutorials

## 🤝 Contributing

We welcome contributions from the research community! Help us keep this survey comprehensive and up-to-date.

### 📝 How to Contribute

1. **Add New Papers**:
   - Create a markdown file in the appropriate category folder
   - Include: paper summary, key innovations, results, and links
   - Add teaser image/video if available

2. **Update Information**:
   - Fix errors or outdated information
   - Add new benchmark results
   - Update implementation links

3. **Improve Content**:
   - Enhance existing documentation
   - Add tutorials or guides
   - Create comparison tables

### 🎯 Contribution Guidelines

- Use the existing paper template format
- Verify all links work correctly
- Include proper citations
- Be objective and accurate

### 🙏 Acknowledgments

Special thanks to all researchers advancing this field and contributors maintaining this collection!

## 📞 Contact & Citation

### Citation

If you find this survey useful for your research, please cite:

```bibtex
@misc{dust3r_papers_2025,
  title={DUSt3R Paper Collection: Curated Research with In-Depth Analysis},
  author={Min-Ho Lee},
  year={2025},
  url={https://github.com/minoTrey/DUSt3R-Paper-Collection}
}
```

### Connect

- 💬 **Discussions**: [GitHub Discussions](../../discussions)
- 🐛 **Issues**: [GitHub Issues](../../issues)

## 📄 License

This survey is released under the [MIT License](LICENSE). Individual papers retain their original licenses.

## 🔮 Future of DUSt3R

The DUSt3R ecosystem continues to evolve rapidly:

- **Near Term** (2025): Real-time 4D reconstruction, mobile deployment, language integration
- **Medium Term** (2026): Unified 3D-language-video models, generative 3D content
- **Long Term**: Complete spatial AI systems, AR/VR metaverse infrastructure

---

<div align="center">

### **⭐ Star this repo to stay updated with the latest advances! ⭐**

[![GitHub Stars](https://img.shields.io/github/stars/minoTrey/DUSt3R-Paper-Collection?style=social)](https://github.com/minoTrey/DUSt3R-Paper-Collection)
[![Watchers](https://img.shields.io/github/watchers/minoTrey/DUSt3R-Paper-Collection?style=social)](https://github.com/minoTrey/DUSt3R-Paper-Collection)

_Tracking 131 papers and growing | Last updated: July 2025_

**[Submit a Paper](../../issues/new)** | **[Report an Issue](../../issues)** | **[Join Discussion](../../discussions)**

</div>

# FF3D-Survey: Feed-Forward 3D Scene Modeling — A Problem-Driven Perspective (arXiv preprint 2026-04)

## 📋 Overview

- **Authors**: Weijie Wang, Qihang Cao, Sensen Gao, Donny Y. Chen, Haofei Xu, Wenjing Bian, Songyou Peng, Tat-Jen Cham, Chuanxia Zheng, Andreas Geiger, Jianfei Cai, Jia-Wang Bian, Bohan Zhuang
- **Institution**: Zhejiang University; Nanyang Technological University; Monash University; ETH Zurich; University of Tübingen, Tübingen AI Center
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.14025) | [Project Page](https://ff3d-survey.github.io)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A survey of generalizable feed-forward 3D scene modeling that, instead of organizing methods by output representation, proposes a problem-driven taxonomy around five challenge axes — feature enhancement, geometry awareness, model efficiency, augmentation strategies, and temporal-aware modeling — and reviews representations, datasets/benchmarks, applications, and future directions.

## 🎯 Key Contributions

1. **Problem-driven taxonomy**: A novel taxonomy centered on model-design strategies that are agnostic to the output 3D representation, arguing that representation-based categorization obscures the functional goals and design motivations behind methods.
2. **Five research directions**: Organizes the field into (1) feature enhancement for robust 2D-to-3D lifting, (2) geometry awareness incorporating priors for sparse inputs, (3) model efficiency for computation/memory, (4) augmentation strategies leveraging generative models, and (5) temporal-aware models for dynamic 4D reconstruction.
3. **Benchmark re-categorization**: Re-organizes datasets by focus — geometry-oriented (e.g. DTU, ScanNet, Replica) vs. visual-oriented (e.g. NeRF-Synthetic, RealEstate10K, DL3DV) — and compiles reported performance across key datasets to surface data-driven trends.
4. **Applications and future roadmap**: Categorizes real-world applications and outlines open challenges around scalability, evaluation standards, and world modeling.

## 🔧 Technical Details

### Scope and Methodology

- The survey covers generalizable **feed-forward** 3D reconstruction: models that map images (optionally with auxiliary signals such as camera poses or depth priors) directly to explicit or implicit 3D representations in a single forward pass, contrasted with per-scene-optimized classical methods (SfM, MVS, NeRF, 3DGS).
- Rather than categorize by output 3D representation, the survey adopts a problem-driven perspective, motivated by the observation that methods sharing a representation may target very different problems while methods addressing the same challenge may use diverse representations.

### Representations Reviewed

The survey first reviews the common representations feed-forward networks generate: NeRF, 3D Gaussian Splatting, Pointmap, and others (including mesh, SDF, occupancy, and light field networks).

### The Five Challenge Axes

- **Feature Enhancement (§4.1)**: improving implicit feature quality/consistency/robustness for accurate 3D decoding — architectures, cross-view fusion, integration of visual foundation models.
- **Geometry Awareness (§4.2)**: robust/accurate geometry inference — explicit aggregation, pose-free reconstruction, post-refinement, 3D priors, and map/pose/constraints.
- **Model Efficiency (§4.3)**: computation and memory bottlenecks — speed/memory, feature efficiency, representation compaction.
- **Augmentation Strategies (§4.4)**: enriching data distributions and visual representations via data/visual augmentation and pre-trained guidance to overcome sparse inputs and limited diversity.
- **Temporal-aware Models (§4.5)**: geometry and motion consistency across frames for low-latency 4D modeling — online streaming, offline processing, interactive modeling, dynamics/physics.

## 📊 Results

As a survey, the paper's "results" are its organizing findings rather than experimental numbers:

- **Shared architectural patterns across representations**: Despite diverse geometric outputs (from implicit fields to explicit primitives), feed-forward approaches share high-level architectural patterns — image feature extraction backbones, multi-view information fusion mechanisms, and geometry-aware design principles — which motivates a representation-agnostic, model-design taxonomy.
- **Benchmark categorization**: Datasets are split into geometry-oriented (point clouds, depth, pose; e.g. DTU, ScanNet, Replica) and visual-oriented (photorealistic view synthesis; e.g. NeRF-Synthetic, RealEstate10K, DL3DV), and the survey compiles representative methods' reported performance across key datasets to reveal trends.
- **Application taxonomy**: Feed-forward 3D reconstruction is surveyed across autonomous driving (§6.1), robotics (§6.2), scene understanding (§6.3), SfM and SLAM (§6.4), video generation (§6.5), and other scenarios such as visual localization (§6.6).
- **Growth trend**: Figure 1 presents a statistical summary of surveyed works by year and category (directions vs. applications); the exact per-year counts appear only in the figure (그림 1, 수치는 표로 미인쇄).

## 💡 Insights & Impact

- **A functional lens on a fast-moving field**: By categorizing methods by the core challenge they address rather than their output format, the survey aims to capture functional roles, design trade-offs and developmental trends more clearly than a prior representation-organized survey.
- **Toward standardized evaluation**: Among its data-driven takeaways, the survey calls for standardized quantification of scene complexity and clearer reporting of geometric diversity in benchmarks.
- **From concept to technology**: The survey frames feed-forward 3D reconstruction as having evolved from a research concept into a practical technology now driving progress across driving, robotics, scene understanding, SfM/SLAM and video generation.

## 🔗 Related Work

This survey situates and organizes much of the DUSt3R-style feed-forward line covered elsewhere in this collection:

- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: Foundational pointmap-based feed-forward reconstruction the survey builds its problem formulation around.
- **[VGGT](../reconstruction/vggt.md)** & **[π³ / Pi3](../reconstruction/pi3.md)**: Representative geometry-aware / feature-enhanced feed-forward models.
- **[CUT3R](../dynamic/cut3r.md)** & **[MonST3R](../dynamic/monst3r.md)**: Temporal-aware / dynamic 4D reconstruction discussed under the temporal axis.
- **[MoGe](../reconstruction/moge.md)**: Monocular geometry estimation within the feature-enhancement/geometry-awareness scope.

## 📚 Key Takeaways

1. The survey proposes a problem-driven, representation-agnostic taxonomy of feed-forward 3D scene modeling built on five challenge axes: feature enhancement, geometry awareness, model efficiency, augmentation strategies, and temporal-aware modeling.
2. It re-categorizes datasets by focus (geometry-oriented vs. visual-oriented) and compiles reported performance to expose benchmark-driven trends, calling for standardized scene-complexity and geometric-diversity reporting.
3. It reviews applications spanning autonomous driving, robotics, scene understanding, SfM/SLAM and video generation, and outlines future directions around rigorous benchmarks, system efficiency, scalable representations, world models, and unified perception-and-reconstruction.

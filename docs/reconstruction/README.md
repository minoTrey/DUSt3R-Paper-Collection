# 3D Reconstruction

## 🏗️ Overview

The 3D Reconstruction category represents the core extensions of DUSt3R that focus on improving quality, efficiency, and scalability of static scene reconstruction. These papers address various challenges including real-time processing, large-scale scenes, multi-view consistency, and achieving state-of-the-art performance.

## 📈 Research Timeline

```text
2024: Foundation laid with MASt3R-SLAM and early extensions
2025: Explosive growth with breakthrough methods
- Jan: VGGT introduces unified geometry (partial permutation equivariance)
- Feb: π³ (Pi3) achieves true permutation equivariance - Current SOTA
  - Eliminates ALL positional embeddings and reference frames
  - Architecture guarantees f(π(X)) = π(f(X))
  - Loss function purely for reconstruction quality
- Real-time systems: SLAM3R, Fast3R, MV-DUSt3R+
- Large-scale: Spann3R, REGIST3R, Pow3R
- Quality focus: MoGe, LoRA3D, Test3R, Dens3R
```

## 🎯 Key Research Directions

### 1. **State-of-the-Art Methods** ⭐

- **π³ (Pi3)**: True permutation-equivariant learning - Current SOTA
  - Eliminates positional embeddings and reference frames completely
  - Near-zero order variance (0.003 vs VGGT's 0.033)
  - Loss function focuses on quality while architecture ensures equivariance
- **VGGT**: Visual geometry grounded transformer - Previous SOTA
  - Still uses reference frame (first view special)
  - Partial permutation equivariance only
- **Dens3R**: Unified geometric dense prediction

### 2. **Real-time Systems** ⚡

- **SLAM3R**: Dense reconstruction from monocular RGB videos
- **Fast3R**: 1000+ images in one forward pass
- **MASt3R-SLAM**: Real-time SLAM with 3D priors
- **MV-DUSt3R+**: 2-second reconstruction with cross-reference fusion

### 3. **Large-scale & Multi-view** 🌍

- **Spann3R**: Spatial memory for unbounded scenes
- **MUSt3R**: O(N) complexity for 1000+ images (5.5cm ATE on TUM RGB-D)
- **REGIST3R**: Incremental registration with stereo foundation
- **Pow3R**: Universal flexibility - handles any combination of camera intrinsics, poses, depth

### 4. **Quality & Robustness** 🎨

- **MoGe**: Monocular geometry for open-domain images
- **LoRA3D**: Low-rank self-calibration of 3D models
- **Test3R**: Learning to reconstruct at test time
- **SPARS3R**: Semantic prior alignment for sparse reconstruction

### 5. **Specialized Approaches** 🔧

- **Light3R-SfM**: Feed-forward structure-from-motion
- **ReconX**: Video diffusion for sparse views
- **Spurfies**: Sparse surface reconstruction with local priors

## 📊 Performance Comparison

### State-of-the-Art Results

#### DTU Dataset

| Model             | Accuracy ↓ | Completeness ↓ | Overall ↓ | Speed    | Status                           |
| ----------------- | ---------- | -------------- | --------- | -------- | -------------------------------- |
| **Pow3R w/ K+RT** | **1.384**  | **0.846**      | **1.115** | 3.2 FPS  | **Best with priors**             |
| **π³ (Pi3)**      | **1.198**  | **1.849**      | -         | 57.4 FPS | **Permutation-equivariant SOTA** |
| VGGT              | 1.338      | 1.896          | -         | 43.2 FPS | Previous SOTA                    |
| Pow3R             | 2.116      | 1.370          | 1.743     | 3.7 FPS  | Universal flexibility            |
| DUSt3R            | 2.677      | 0.805          | 1.741     | ~3s      | Original                         |

#### Camera Pose (Sintel Zero-shot)

| Model        | ATE ↓     | RPE trans ↓ | RPE rot ↓ | Order Variance |
| ------------ | --------- | ----------- | --------- | -------------- |
| **π³ (Pi3)** | **0.074** | **0.040**   | **0.282** | **Near-zero**  |
| VGGT         | 0.167     | 0.062       | 0.491     | Partial        |
| CUT3R        | 0.217     | 0.070       | 0.636     | High           |
| Fast3R       | 0.371     | 0.298       | 13.75     | High           |

#### Universal Flexibility (Pow3R)

| Input Configuration | Co3Dv2 RRA@15↑ | RealEstate10K mAA(30)↑ | Speed (fps) | Key Benefit           |
| ------------------- | -------------- | ---------------------- | ----------- | --------------------- |
| RGB only            | 94.8           | 62.5                   | 3.2         | No calibration needed |
| RGB + Intrinsics    | 95.0           | 72.5                   | 30.1        | Consumer camera ready |
| RGB + All priors    | 95.0           | 72.5                   | 30.1        | Professional use      |

### Multi-View Performance (HM3D Dataset)

| Model          | 12 Views DAc ↑ | Speed     | Architecture | Key Innovation         |
| -------------- | -------------- | --------- | ------------ | ---------------------- |
| **MV-DUSt3R+** | **91.5%**      | **0.89s** | Single-stage | Cross-reference fusion |
| MV-DUSt3R      | 79.5%          | 0.15s     | Single-stage | Single reference       |
| DUSt3R         | 30.7%          | 8.28s     | Two-stage    | Pairwise matching      |
| Spann3R        | 0.0%           | 1.34s     | Sequential   | No global consistency  |

### Scalability Comparison

| Model      | Max Images | Complexity | Memory Growth  | Processing Time | Best For              |
| ---------- | ---------- | ---------- | -------------- | --------------- | --------------------- |
| DUSt3R     | 10-20      | O(N²)      | O(N²)          | ~10s/pair       | Small scenes          |
| MASt3R     | 20-50      | O(N²)      | O(N²)          | ~7s/pair        | Better matching       |
| Pow3R      | Any        | O(N²)      | O(N²)          | 3.7 FPS         | With auxiliary inputs |
| MUSt3R     | 1000+      | O(N)       | O(1) per image | 8.4 FPS         | Large multi-view      |
| MV-DUSt3R+ | 100+       | O(N)       | O(N)           | ~2s total       | Fast multi-view       |
| Fast3R     | 1500+      | O(N)       | Low            | 251 FPS         | Speed priority        |
| Spann3R    | Unlimited  | O(N)       | Constant       | Sequential      | Unbounded scenes      |

## 📚 Complete Paper List (110 papers)

### 🏆 State-of-the-Art Methods

1. [**π³ (Pi3)**: Scalable Permutation-Equivariant Visual Geometry Learning](pi3.md) ⭐ SOTA (no positional embeddings)
2. [**VGGT**: Visual Geometry Grounded Transformer](vggt.md) - ~0.2s 추론 (DUSt3R ~7s)
3. [**Pow3R**: Empowering Unconstrained 3D Reconstruction](pow3r.md) - Best with auxiliary inputs
4. [**Dens3R**: Unified Geometric Dense Prediction](dens3r.md)

### ⚡ Real-time Systems

1. [**SLAM3R**: Real-Time Dense Scene Reconstruction](slam3r.md)
2. [**Fast3R**: 3D Reconstruction of 1000+ Images](fast3r.md)
3. [**MASt3R-SLAM**: Real-Time Dense SLAM](mast3r-slam.md)
4. [**MV-DUSt3R+**: Single-Stage Scene Reconstruction](mv-dust3r-plus.md) - DUSt3R 대비 8~14×

### 🌍 Large-scale & Multi-view

1. [**MUSt3R**: Multi-view Stereo 3D Reconstruction (O(N) complexity)](must3r.md)
2. [**Spann3R**: 3D Reconstruction with Spatial Memory](spann3r.md)
3. [**Pow3R**: Universal 3D Reconstruction with Any Auxiliary Inputs](pow3r.md) - CVPR'25
4. [**REGIST3R**: Incremental Registration](regist3r.md)

### 🎨 Quality Enhancement

1. [**MoGe**: Monocular Geometry Estimation](moge.md)
2. [**LoRA3D**: Low-Rank Self-Calibration](lora3d.md)
3. [**Test3R**: Learning to Reconstruct at Test Time](test3r.md)
4. [**SPARS3R**: Semantic Prior Alignment](spars3r.md)

### 🔧 Specialized Methods

1. [**Light3R-SfM**: Feed-forward Structure-from-Motion](light3r-sfm.md)
2. [**ReconX**: Video Diffusion for Sparse Views](reconx.md)
3. [**Spurfies**: Sparse Surface Reconstruction](spurfies.md)

## 💡 Key Insights & Trends

### Major Breakthroughs

1. **True Permutation Equivariance** (Pi3): Complete elimination of positional embeddings and reference frames
2. **Unified Geometry** (VGGT): Joint estimation of all geometric properties (still order-dependent)
3. **Spatial Memory** (Spann3R): Unbounded scene reconstruction
4. **Single-Stage Pipeline** (MV-DUSt3R+): O(N) complexity with cross-reference fusion

### Technical Innovations

- **Memory Efficiency**: From O(N²) to O(N) complexity
- **Global Consistency**: Maintaining alignment across unlimited views
- **Test-Time Adaptation**: Learning scene-specific features
- **Foundation Model Integration**: Leveraging pre-trained knowledge

### Performance Evolution

```text
2024: DUSt3R baseline (~10s per pair, limited scale)
2025 Q1: VGGT (43.2 FPS, unified geometry, partial permutation equivariance)
2025 Q2: π³ (57.4 FPS, true permutation equivariance, current SOTA)
2025: Multiple specialized systems for different use cases
```

## 🚀 Getting Started

### Choose Based on Your Needs

**For Best Quality** 🏆

- Use **π³ (Pi3)** for state-of-the-art results with true permutation equivariance
  - Best when input order may vary or is unknown
  - Ideal for multi-camera systems with arbitrary arrangements
- Use **VGGT** if you have a consistent reference view
- Use **Dens3R** for unified dense prediction (depth + normals)

**For Real-time Applications** ⚡

- Use **SLAM3R** for live video processing
- Use **MV-DUSt3R+** for quick multi-view reconstruction
- Use **Fast3R** for massive image collections

**For Large Scenes** 🌍

- Use **Spann3R** for unbounded sequences
- Use **MUSt3R** for large multi-view collections
- Use **Pow3R** for unconstrained scenarios

**For Limited Data** 📸

- Use **MoGe** for single/few images
- Use **ReconX** with video diffusion priors
- Use **SPARS3R** for sparse views with semantics

## 🔮 Future Directions

1. **Beyond SOTA**: Building on π³'s true permutation-equivariant foundation (no positional embeddings)
2. **Symmetry-Aware Architectures**: Extending π³'s principles to other vision tasks
3. **Dynamic Integration**: Bridging static and dynamic reconstruction
4. **Uncertainty Quantification**: Confidence-aware predictions
5. **Cross-modal Fusion**: Integrating language and other modalities

---

_Auto-generated index · 64 papers_

<!-- GENERATED:paper-index -->

## 📄 All Papers in This Category (110)

> 자동 생성 (`tools/build_papers_list.py`). 손대지 말 것.

- [**AMB3R**](amb3r.md) (CVPR 2026) — Accurate Feed-forward Metric-scale 3D Reconstruction with Backend
- [**Anchor3R**](anchor3r.md) (arXiv preprint (2026-06)) — Streaming 3D Reconstruction with Transient Anchors for Long-Horizon Visual Mapping
- [**Argus**](argus.md) (arXiv preprint (2026-06)) — Metric Panoramic 3D Reconstruction for Indoor Scenes
- [**BAT3R**](bat3r.md) (ECCV 2026) — Bootstrapping Articulated 3D Reconstruction from 2D Image Collections
- [**C3Po**](c3po.md) (NeurIPS 2025) — Cross-View Cross-Modality Correspondence by Pointmap Prediction
- [**CAM3R**](cam3r.md) (arXiv preprint (2026-03)) — Camera-Agnostic Model for 3D Reconstruction
- [**Co-Me**](co-me.md) (CVPR 2026) — Confidence Guided Token Merging for Visual Geometric Transformers
- [**Cross3R**](cross3r.md) (arXiv preprint (2026-05)) — Feedforward 3D Reconstruction from Satellite, Drone, and Ground Images
- [**DAGE**](dage.md) (CVPR 2026) — Dual-Stream Architecture for Efficient and Fine-Grained Geometry Estimation
- [**DejaView**](deja-view.md) (arXiv preprint (2026-05)) — Looping Transformers for Multi-View 3D Reconstruction
- [**Dens3R**](dens3r.md) (arXiv preprint (2025-07)) — A Foundation Model for 3D Geometry Prediction
- [**DA3**](depth-anything-3.md) (ICLR 2026) — Recovering the Visual Space from Any Views
- [**DriveVGGT**](drivevggt.md) (arXiv preprint (2025-11)) — Calibration-Constrained Visual Geometry Transformers for Multi-Camera Autonomous Driving
- [**DVGT**](dvgt.md) (arXiv preprint (2025-12)) — Driving Visual Geometry Transformer
- [**E-RayZer**](e-rayzer.md) (CVPR 2026) — Self-supervised 3D Reconstruction as Spatial Visual Pre-training
- [**Empowering**](empowering.md) (arXiv preprint (2026-06)) — Metric-Scale Feed-Forward Reconstruction via Satellite Images
- [**Event3R**](event3r.md) (IROS 2026) — Asynchronous-to-Global 3D Reconstruction from Event Camera via Spatial-Temporal Feature Aggregation
- [**Evict3R**](evict3r.md) (arXiv preprint (2025-09)) — Training-Free Token Eviction for Memory-Bounded Streaming Visual Geometry Transformers
- [**Fast3R**](fast3r.md) (CVPR 2025) — Towards 3D Reconstruction of 1000+ Images in One Forward Pass
- [**FastVGGT**](fastvggt.md) (ICLR 2026) — Training-Free Acceleration of Visual Geometry Transformer
- [**FILT3R**](filt3r.md) (arXiv preprint (2026-03)) — Latent State Adaptive Kalman Filter for Streaming 3D Reconstruction
- [**Fin3R**](fin3r.md) (NeurIPS 2025) — Fine-tuning Feed-forward 3D Reconstruction Models via Monocular Knowledge Distillation
- [**Fisheye3R**](fisheye3r.md) (arXiv preprint (2026-03)) — Adapting Unified 3D Feed-Forward Foundation Models to Fisheye Lenses
- [**FrameVGGT**](framevggt.md) (arXiv preprint (2026-03)) — Coherence-Preserving Memory for Bounded Streaming Geometry
- [**Free Geometry**](free-geometry.md) (arXiv preprint (2026-04)) — Refining 3D Reconstruction from Longer Versions of Itself
- [**Fus3D**](fus3d.md) (arXiv preprint (2026-03)) — Decoding Consolidated 3D Geometry from Feed-forward Geometry Transformer Latents
- [**G-CUT3R**](g-cut3r.md) (ICLR 2026) — Guided 3D Reconstruction with Camera and Depth Prior Integration
- [**GARD**](gard.md) (arXiv preprint (2026-05)) — Geometry-Aware Representation Denoising for Robust Multi-view 3D Reconstruction
- [**GGPT**](ggpt.md) (CVPR 2026) — Geometry-Grounded Point Transformer
- [**HGGT**](hggt.md) (arXiv preprint (2026-03)) — Robust and Flexible 3D Hand Mesh Reconstruction from Uncalibrated Images
- [**HorizonStream**](horizonstream.md) (arXiv preprint (2026-05)) — Long-Horizon Attention for Streaming 3D Reconstruction
- [**IDT**](idt.md) (arXiv preprint (2025-12)) — A Physically Grounded Transformer for Feed-Forward Multi-View Intrinsic Decomposition
- [**iLRM**](ilrm.md) (CVPR 2026) — An Iterative Large 3D Reconstruction Model
- [**InfiniteVGGT**](infinitevggt.md) (arXiv preprint (2026-01)) — Visual Geometry Grounded Transformer for Endless Streams
- [**IVGT**](ivgt.md) (arXiv preprint (2026-05)) — Implicit Visual Geometry Transformer for Neural Scene Representation
- [**JointEdit3D**](jointedit3d.md) (arXiv preprint (2026-06)) — Feed-Forward 3D Scene Editing in a Unified Latent Space
- [**Light3R-SfM**](light3r-sfm.md) (CVPR 2025) — Towards Feed-forward Structure-from-Motion
- [**LingBot-Map**](lingbot-map.md) (arXiv preprint (2026-04)) — Geometric Context Transformer for Streaming 3D Reconstruction
- [**LIST3R**](list3r.md) (arXiv preprint (2026-07)) — Long-sequence Instance-aware 3D Reconstruction
- [**LiteVGGT**](litevggt.md) (CVPR 2026) — Boosting Vanilla VGGT via Geometry-aware Cached Token Merging
- [**LoGeR**](loger.md) (arXiv preprint (2026-03)) — Long-Context Geometric Reconstruction with Hybrid Memory
- [**LONG3R**](long3r.md) (ICCV 2025) — Long Sequence Streaming 3D Reconstruction
- [**LoRA3D**](lora3d.md) (ICLR 2025) — Low-Rank Self-Calibration of 3D Geometric Foundation Models
- [**LSRM**](lsrm.md) (arXiv preprint (2026-04)) — High-Fidelity Object-Centric Reconstruction via Scaled Context Windows
- [**MAGiSt3R**](magist3r.md) (arXiv preprint (2026-07)) — Multi-Agent Feed-forward 3D Reconstruction from Monocular RGB Videos
- [**MapAnything**](mapanything.md) (3DV 2026) — Universal Feed-Forward Metric 3D Reconstruction
- [**MASt3R-SLAM**](mast3r-slam.md) (CVPR 2025) — Real-Time Dense SLAM with 3D Reconstruction Priors
- [**Mem3R**](mem3r.md) (arXiv preprint (2026-04)) — Streaming 3D Reconstruction with Hybrid Memory via Test-Time Training
- [**MERG3R**](merg3r.md) (CVPR 2026) — A Divide-and-Conquer Approach to Large-Scale Neural Visual Geometry
- [**Mix3R**](mix3r.md) (arXiv preprint (2026-05)) — Mixing Feed-forward Reconstruction and Generative 3D Priors for Joint Multi-view Aligned 3D Reconstruction and Pose Estimation
- [**MoGe**](moge.md) (CVPR 2025) — Unlocking Accurate Monocular Geometry Estimation for Open-Domain Images
- [**MoGe-2**](moge-2.md) (arXiv preprint (2025-07)) — Accurate Monocular Geometry with Metric Scale and Sharp Details
- [**Mono3R**](mono3r.md) (ACM MM 2025) — Exploiting Monocular Cues for Geometric 3D Reconstruction
- [**MUSt3R**](must3r.md) (CVPR 2025) — Multi-view Stereo 3D Reconstruction
- [**MV-DUSt3R+**](mv-dust3r-plus.md) (CVPR 2025) — Single-Stage Scene Reconstruction from Sparse Views In 2 Seconds
- [**NoDrift3R**](nodrift3r.md) (arXiv preprint (2026-07)) — Raymap-Guided Coupling for Drift-Robust Unposed Feed-Forward 3D Reconstruction
- [**OmniVGGT**](omnivggt.md) (CVPR 2026) — Omni-Modality Driven Visual Geometry Grounded Transformer
- [**Online3R**](online3r.md) (arXiv preprint (2026-04)) — Online Learning for Consistent Sequential Reconstruction Based on Geometry Foundation Model
- [**OVGGT**](ovggt.md) (arXiv preprint (2026-03)) — O(1) Constant-Cost Streaming Visual Geometry Transformer
- [**PanoVGGT**](panovggt.md) (CVPR 2026) — Feed-Forward 3D Reconstruction from Panoramic Imagery
- [**PAS3R**](pas3r.md) (arXiv preprint (2026-03)) — Pose-Adaptive Streaming 3D Reconstruction for Long Video Sequences
- [**π³**](pi3.md) (arXiv preprint (2025-07)) — Scalable Permutation-Equivariant Visual Geometry Learning
- [**Point3R**](point3r.md) (NeurIPS 2025) — Streaming 3D Reconstruction with Explicit Spatial Pointer Memory
- [**Pow3R**](pow3r.md) (CVPR 2025) — Empowering Unconstrained 3D Reconstruction with Camera and Scene Priors
- [**PRISM**](prism.md) (arXiv preprint (2026-06)) — Feed-Forward Single-Image 3D Reconstruction via Geometric Warp-Residual Modeling
- [**QuantVGGT**](quantvggt.md) (ICLR 2026) — Quantized Visual Geometry Grounded Transformer
- [**ReCal3R**](recal3r.md) (arXiv preprint (2026-07)) — Reliability-Calibrated Learning Rates for Streaming 3D Reconstruction
- [**ReconX**](reconx.md) (IEEE TIP 2026) — Reconstruct Any Scene from Sparse Views with Video Diffusion Model
- [**REGIST3R**](regist3r.md) (ACM MM 2025) — Incremental Registration with Stereo Foundation Model
- [**Reliev3R**](reliev3r.md) (CVPR 2026) — Relieving Feed-forward 3D Reconstruction from Multi-View Geometric Annotations
- [**S-MUSt3R**](s-must3r.md) (arXiv preprint (2026-02)) — Sliding Multi-view 3D Reconstruction
- [**S-VGGT**](s-vggt.md) (ICME 2026) — Structure-Aware Subscene Decomposition for Scalable 3D Foundation Models
- [**SAIL-Recon**](sail-recon.md) (3DV 2026) — Large SfM by Augmenting Scene Regression with Localization
- [**Sat3R**](sat3r.md) (arXiv preprint (2026-05)) — Satellite DSM Reconstruction via RPC-Aware Depth Fine-tuning
- [**Scal3R**](scal3r.md) (CVPR 2026) — Scalable Test-Time Training for Large-Scale 3D Reconstruction
- [**SHOW**](show.md) (arXiv preprint (2026-06)) — Scene and Human in One World — Reconstruction in a Feedforward Pass
- [**SING3R-SLAM**](sing3r-slam.md) (arXiv preprint (2025-11)) — Submap-based Indoor Monocular Gaussian SLAM with 3D Reconstruction Priors
- [**SLAM-Former**](slam-former.md) (ECCV 2026) — Putting SLAM into One Transformer
- [**SLAM3R**](slam3r.md) (CVPR 2025) — Real-Time Dense Scene Reconstruction from Monocular RGB Videos
- [**Spann3R**](spann3r.md) (3DV 2025) — 3D Reconstruction with Spatial Memory
- [**SPARS3R**](spars3r.md) (CVPR 2025) — Semantic Prior Alignment and Regularization for Sparse 3D Reconstruction
- [**Sparse-VGGT**](sparse-vggt.md) (CVPR 2026) — Block-Sparse Global Attention for Efficient Multi-View Geometry Transformers
- [**Speed3R**](speed3r.md) (CVPR 2026) — Sparse Feed-forward 3D Reconstruction Models
- [**Spurfies**](spurfies.md) (3DV 2025) — Sparse Surface Reconstruction using Local Geometry Priors
- [**StereoVGGT**](stereovggt.md) (arXiv preprint (2026-03)) — A Training-Free Visual Geometry Transformer for Stereo Vision
- [**STream3R**](stream3r.md) (ICLR 2026) — Scalable Sequential 3D Reconstruction with Causal Transformer
- [**StreamVGGT**](streamvggt.md) (ICLR 2026) — Streaming Visual Geometry Transformer
- [**Surflo**](surflo.md) (arXiv preprint (2026-06)) — Consistent 3D Surface Flow Model with Global State
- [**SurgCUT3R**](surgcut3r.md) (arXiv preprint (2026-03)) — Surgical Scene-Aware Continuous Understanding of Temporal 3D Representation
- [**TALO**](talo.md) (CVPR 2026) — Pushing 3D Vision Foundation Models Towards Globally Consistent Online Reconstruction
- [**Test3R**](test3r.md) (NeurIPS 2025) — Learning to Reconstruct 3D at Test Time
- [**TTSA3R**](ttsa3r.md) (arXiv preprint (2026-01)) — Training-Free Temporal-Spatial Adaptive Persistent State for Streaming 3D Reconstruction
- [**TTT3R**](ttt3r.md) (ICLR 2026) — 3D Reconstruction as Test-Time Training
- [**TurboVGGT**](turbovggt.md) (arXiv preprint (2026-05)) — Fast Visual Geometry Reconstruction with Adaptive Alternating Attention
- [**UniQueR**](uniquer.md) (arXiv preprint (2026-03)) — Unified Query-based Feedforward 3D Reconstruction
- [**UniSH**](unish.md) (arXiv preprint (2026-01)) — Unifying Scene and Human Reconstruction in a Feed-Forward Pass
- [**VGG-T3**](vgg-t3.md) (CVPR 2026) — Offline Feed-Forward 3D Reconstruction at Scale
- [**VGGT**](vggt.md) (CVPR 2025) — Visual Geometry Grounded Transformer
- [**VGGT-Edit**](vggt-edit.md) (arXiv preprint (2026-05)) — Feed-forward Native 3D Scene Editing with Residual Field Prediction
- [**VGGT-Long**](vggt-long.md) (ICRA 2026) — Chunk it, Loop it, Align it, Pushing VGGT's Limits on Kilometer-scale Long RGB Sequences
- [**VGGT-Ω**](vggt-omega.md) (CVPR 2026) — Scaling Feed-Forward Reconstruction with Registers and Self-Supervision
- [**VGGT-SLAM**](vggt-slam.md) (NeurIPS 2025) — Dense RGB SLAM Optimized on the SL(4) Manifold
- [**VGTW**](vggt-wild.md) (arXiv preprint (2026-06)) — Visual Geometry Transformer in the Wild — Distractor-Free 3D Reconstruction
- [**ViGT**](vigt.md) (arXiv preprint (2026-02)) — Visual Implicit Geometry Transformer for Autonomous Driving
- [**VIST3A**](vist3a.md) (ICLR 2026) — Text-to-3D by Stitching a Multi-view Reconstruction Network to a Video Generator
- [**Wat3R**](wat3r.md) (ECCV 2026) — Underwater 3D Geometry Learning without Annotations
- [**Wid3R**](wid3r.md) (arXiv preprint (2026-02)) — Wide Field-of-View 3D Reconstruction via Camera Model Conditioning
- [**WinT3R**](wint3r.md) (arXiv preprint (2025-09)) — Window-based Streaming Reconstruction with Camera Token Pool
- [**WorldMirror**](worldmirror.md) (ICML 2026) — Universal 3D World Reconstruction with Any-Prior Prompting
- [**ZipMap**](zipmap.md) (CVPR 2026) — Linear-Time Stateful 3D Reconstruction via Test-Time Training

<!-- /GENERATED -->

# Rig3R: Rig-Aware Conditioning for Learned 3D Reconstruction (arXiv preprint)

## 📋 Overview

- **Authors**: Samuel Li, Pujith Kachana, Prajwal Chidananda, Saurabh Nair, Yasutaka Furukawa, Matthew Brown
- **Institution**: Wayve Technologies, Carnegie Mellon University
- **Venue**: arXiv preprint (2025-06)
- **Note**: The venue could not be confirmed because DBLP was unavailable (rate-limited) at verification time. Re-check with `python3 tools/verify_metadata.py --only rig3r`.
- **Links**: [Paper](https://arxiv.org/abs/2506.02265)
- **Verification**: LIKELY (2026-07-20)
- **TL;DR**: A transformer that conditions multi-view reconstruction on optional multi-camera rig metadata (camera ID, timestamp, rig pose) with dropout training, and predicts rig-relative raymaps that let it discover rig structure when metadata is absent.

## 🎯 Key Contributions

1. **First learned method to exploit rig constraints**: Prior feed-forward models treat images as unstructured collections. Rig3R conditions on rig metadata when available and generalizes to partial or entirely missing metadata.
2. **Dual raymap output**: A pose raymap relative to the first image's frame and a rig raymap relative to a rig-centric frame decoupled from ego-motion. Both enable closed-form recovery of intrinsics and extrinsics.
3. **Rig calibration discovery**: The rig head allows the model to infer rig structure directly from unordered images with no metadata and no timestamps — the paper states this is the first attempt at this task, learned or classical.
4. **Single forward pass**: 3D reconstruction, camera pose estimation, and rig discovery with no post-processing or iterative refinement. The abstract reports outperforming both traditional and learned methods by 17–45% mAA across real-world rig datasets.

## 🔧 Technical Details

### Core Innovation: Optional Rig Conditioning

```text
DUSt3R / Fast3R: {images} → pointmaps (views treated as an unordered set)
Rig3R:           {images, optional metadata} → pointmaps + pose raymaps + rig raymaps
```

Formally, given `{Iᵢ, Mᵢ}` with optional metadata `Mᵢ = {cᵢ, tᵢ, rᵢ}` (camera ID, timestamp,
rig-relative raymap), the model predicts for each image a pointmap `Pᵢ ∈ R^(3×H×W)` in the first
image's frame, a confidence map `Cᵢ`, a pose raymap `Rᵢ^pose ∈ R^(H×W×6)`, and a rig raymap
`Rᵢ^rig ∈ R^(H×W×6)`.

### Raymap Representation

A raymap assigns a unit ray direction to each pixel, all rays sharing a camera center. For pixel
`(u, v)`, `r̂_uv = R · K⁻¹[u, v, 1]ᵀ`, unit-normalized. The advantages the paper claims over
pointmaps:

- **Spatially aligned per-pixel supervision**, stable even in sky or dynamic regions where pointmaps infer pose indirectly through 3D predictions and often fail
- **Interpretable geometry**: focal lengths recovered from angular constraints on pixel–ray pairs, rotations recovered in closed form by SVD from aligned camera and world rays

The supplementary derives the intrinsics constraint `cos²θ = (ũᵀωũ′)² / ((ũᵀωũ)(ũ′ᵀωũ′))` with
`ω = diag(1/f_x², 1/f_y², 1)`, and a practical analytic shortcut `f_x = |Δu| / tan θ` from pixel pairs
sampled along the image axes.

### Architecture

- **Image encoder**: shared ViT-Large with 2D sine-cosine positional encodings, initialized from DUSt3R (the paper notes other works indicate performance is not sensitive to this choice)
- **Metadata embedding**: frame index `N`, camera ID `cᵢ`, timestamp `tᵢ`, and rig raymap patch `rᵢ`. Discrete IDs are sampled from a larger index range and encoded with 1D sine-cosine embeddings to generalize to varying frame and camera counts; the rig raymap patch is linearly projected. All components are concatenated and added to patch tokens. The frame index is always included; the other three are droppable.
- **Transformer decoder**: a second ViT-Large trained from scratch performing joint self-attention across all patch tokens from all images
- **Prediction heads**: a DPT module for pointmap plus confidence; two raymap heads, each consisting of an MLP for per-pixel ray directions and an MLP predicting a global camera center via average pooling over patch tokens. No dedicated query tokens, so all gradients flow through patch tokens.

The three outputs are tightly coupled — pointmaps should lie along rays defined by the pose raymap,
and rig and pose raymaps are related through ego-motion — which the paper frames as a structural
multitask prior.

### Training

- **Loss**: `L_total = L_pmap + λ_p·L_p_rmap + λ_r·L_r_rmap`. The pointmap loss follows DUSt3R's confidence-weighted regression with scale-normalized ground truth. The raymap loss combines a ray-direction term and a depth-normalized camera-center term weighted by `β`.
- **Embedding dropout**: each metadata field (camera ID, timestamp, rig pose) is dropped with 50% probability during training, teaching the model to use metadata when present and infer it from image content when not.
- **Data**: CO3D-v2, BlendedMVS, Map-free, ScanNet++ v2, MVImgNet, PointOdyssey, Virtual KITTI2, TartanAir V2, PandaSet, KITTI, Argoverse2, nuScenes, Waymo, and an internal dataset — indoor, driving, synthetic, and object-centric, with emphasis on multi-camera rigs. Rig cameras are subsampled per sequence to diversify configurations, with the front-facing camera always included.
- **Schedule**: 24-frame samples, batch size 128, 128 H100 GPUs, 250k steps over 5 days. Images resized to 512 × 512 with padding. AdamW, learning rate 0.0001, cosine annealing.

## 📊 Results

Evaluation uses the Waymo Open validation set and WayveScenes101, both with 5-camera rigs and roughly
200 timesteps per scene at 10 FPS. Waymo provides LiDAR-based ground-truth poses and 3D points;
WayveScenes101 uses COLMAP reconstructions and is an unseen dataset with a novel rig configuration.
Two 24-frame samples per scene use the full 5-camera rig spaced approximately 2 seconds apart.

`Rig3R_Unstr` receives no metadata; `Rig3R_Calib` receives camera ID, timestamp, and rig raymaps.
`Rig3R_Calib` and Rig COLMAP are the only methods leveraging rig constraints, and both receive the
same rig calibration information. Intrinsics are withheld from all methods.

### Multi-View Pose Estimation

원논문 Table 1. RRA/RTA는 각도 임계값별 정확도, mAA는 30°까지의 평균 정확도. 모두 높을수록 좋다.

| Method          | Waymo RRA@15° ↑ | Waymo RTA@15° ↑ | Waymo RRA@5° ↑ | Waymo RTA@5° ↑ | Waymo mAA@30° ↑ | Time  |
| --------------- | --------------- | --------------- | -------------- | -------------- | --------------- | ----- |
| COLMAP          | 31.1            | 24.4            | 23.0           | 22.5           | 22.7            | >2m   |
| MV-DUSt3R       | 44.3            | 23.8            | 18.9           | 8.4            | 15.8            | 10.5s |
| DUSt3R-GA       | 56.0            | 57.9            | 18.2           | 37.2           | 37.5            | >2m   |
| Fast3R          | 46.8            | 31.2            | 19.2           | 13.3           | 20.6            | 3.9s  |
| Rig COLMAP      | 38.6            | 31.1            | 28.4           | 28.6           | 28.7            | >2m   |
| **Rig3R_Unstr** | 96.6            | 83.9            | 66.0           | 71.6           | 74.6            | 5.7s  |
| **Rig3R_Calib** | **99.4**        | **91.6**        | **67.4**       | **77.4**       | **82.1**        | 5.7s  |

원논문 Table 1, WayveScenes101 (unseen).

| Method          | RRA@15° ↑ | RTA@15° ↑ | RRA@5° ↑ | RTA@5° ↑ | mAA@30° ↑ | Time  |
| --------------- | --------- | --------- | -------- | -------- | --------- | ----- |
| COLMAP          | 34.1      | 26.0      | 28.1     | 23.0     | 24.4      | >2m   |
| MV-DUSt3R       | 40.0      | 27.0      | 13.6     | 9.5      | 13.1      | 10.5s |
| DUSt3R-GA       | 89.1      | 61.8      | 33.7     | 47.4     | 48.6      | >2m   |
| Fast3R          | 61.1      | 29.1      | 23.8     | 12.3     | 20.7      | 3.9s  |
| Rig COLMAP      | 43.0      | 31.8      | 33.9     | 27.1     | 29.2      | >2m   |
| **Rig3R_Unstr** | 49.2      | 52.4      | 20.5     | 36.0     | 25.7      | 5.7s  |
| **Rig3R_Calib** | **95.8**  | **75.8**  | **77.7** | **60.0** | **65.2**  | 5.7s  |

Learned baselines drop sharply at the 5° threshold. COLMAP improves with rig constraints and shows
smaller gaps between thresholds, which the paper attributes to classical optimization's binary
convergence behavior. On WayveScenes101 — a dataset built from scenes where COLMAP reconstruction
succeeded, potentially favoring classical methods — `Rig3R_Calib` still leads on every metric, with
DUSt3R-GA second thanks to global optimization.

### Multi-View Pointmap Estimation

원논문 Table 2. Chamfer는 Acc.와 Comp.의 평균이다.

| Method          | Waymo Acc. ↓ | Waymo Comp. ↓ | Waymo Chamfer ↓ | Wayve Acc. ↓ | Wayve Comp. ↓ | Wayve Chamfer ↓ |
| --------------- | ------------ | ------------- | --------------- | ------------ | ------------- | --------------- |
| MV-DUSt3R       | 1.7          | 24.0          | 12.9            | 6.7          | 38.0          | 19.3            |
| DUSt3R-GA       | 1.9          | 15.2          | 8.6             | 1.4          | 7.8           | 4.6             |
| Fast3R          | 1.9          | 5.9           | 3.9             | 0.7          | 5.1           | 2.9             |
| **Rig3R_Unstr** | 0.2          | 1.4           | 0.8             | 0.4          | 8.2           | 4.3             |
| **Rig3R_Calib** | **0.1**      | **0.2**       | **0.2**         | **0.3**      | **4.1**       | **2.2**         |

On WayveScenes101, Fast3R takes the second-best Chamfer distance, slightly ahead of `Rig3R_Unstr`,
despite much lower pose accuracy. The paper reads this as evidence for its design: Rig3R estimates
pose from raymaps rather than from pointmaps, so pose quality and pointmap quality are not locked
together.

### Ablation: Metadata Embeddings

원논문 Table 3. 각 metadata 필드(camera ID, timestamp, rig pose)를 켜고 끈 결과.

| Cam | Time | Rig | Waymo RRA@15° ↑ | Waymo RTA@15° ↑ | Waymo mAA@30° ↑ | Waymo Chamfer ↓ | Wayve RRA@15° ↑ | Wayve RTA@15° ↑ | Wayve mAA@30° ↑ | Wayve Chamfer ↓ |
| --- | ---- | --- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| -   | -    | -   | 96.6            | 83.9            | 74.6            | 0.8             | 49.2            | 52.4            | 25.7            | 4.3             |
| ✓   | -    | -   | 97.0            | 84.3            | 75.1            | 1.1             | 48.0            | 55.4            | 26.8            | 4.5             |
| -   | ✓    | -   | 97.6            | **92.7**        | 81.8            | 0.3             | 36.2            | 60.2            | 23.9            | 4.6             |
| -   | -    | ✓   | 98.0            | 84.2            | 76.0            | 1.2             | **96.5**        | 66.5            | 56.4            | 2.5             |
| ✓   | ✓    | ✓   | **99.4**        | 91.6            | **82.1**        | **0.2**         | 95.8            | **75.8**        | **65.2**        | **2.2**         |

The two datasets separate cleanly. On Waymo — a familiar rig configuration the model already
recognizes implicitly — camera ID and rig pose give only modest gains and the timestamp is the most
informative remaining signal, supplying dynamic cues for localizing the rig over time. On the unseen
WayveScenes101, camera ID and timestamp individually give limited gains because neither alone
disambiguates the rig layout, while rig pose embeddings alone raise mAA from 25.7 to 56.4. All three
together are best on both datasets.

### Ablation: Multi-Task Heads

원논문 Table 4. 이 실험은 별도 모델을 처음부터 학습해야 하므로 축소된 규모(batch size 32,
데이터셋 5개)로 수행되었고, 전체 규모 평가와 직접 비교할 수 없다.

| Variant         | Unstr. RRA@15° ↑ | Unstr. RTA@15° ↑ | Unstr. mAA@30° ↑ | Calib. RRA@15° ↑ | Calib. RTA@15° ↑ | Calib. mAA@30° ↑ |
| --------------- | ---------------- | ---------------- | ---------------- | ---------------- | ---------------- | ---------------- |
| L_pose          | 89.2             | 54.1             | 45.8             | **98.6**         | 89.0             | 78.9             |
| L_pose + L_rig  | 90.4             | 56.6             | 48.5             | 98.5             | **91.7**         | **81.9**         |
| L_pose + L_pmap | **91.3**         | **62.1**         | **53.5**         | 98.3             | 90.1             | 79.8             |

In the unstructured setting the pointmap head gives the largest gain, raising mAA from 45.8 to 53.5,
which the paper reads as the value of 3D grounding. In the calibrated setting the rig head yields
the highest mAA, likely by reinforcing the rig structure across timesteps. Both heads are kept in
the full model — and the rig head is what enables rig discovery at all.

### Generalization Across Rig Configurations

Evaluated on the Argoverse2 validation set with 1, 3, 5, and 7 camera rigs (strides 6, 17, 27, 34
respectively, increased to maintain scene coverage). Rig ID accuracy is computed by clustering rig
raymap outputs and evaluating frame assignment with the Hungarian algorithm; rig mAA measures the
relative orientations and positions of the discovered cameras in a rig-centric frame. The paper
reports that `Rig3R_Unstr` achieves strong rig mAA and Rig ID accuracy across all configurations, and
that Fast3R degrades as rig size and stride increase while both Rig3R variants stay consistent.
Numeric values appear only in Fig. 5 plots and are not transcribed here.

Notably, given monocular or unordered inputs, Rig3R predicts identity rig raymaps and produces a
single cluster — correctly signaling the absence of a rig.

## 💡 Insights & Impact

### The Structural Prior Being Recovered

Real capture rarely produces an unordered pile of images. Autonomous vehicles, robots, and survey
platforms use synchronized multi-camera rigs with fixed relative configurations, and that geometry is
known or at least inferable. Classical pipelines have long exploited it — COLMAP models the rig as a
single moving entity with fixed intra-rig calibration. Feed-forward models inherited DUSt3R's
unordered-set assumption and left the prior untapped. Rig3R's premise is that this prior is most
valuable exactly where correspondence is weakest: rig cameras with limited field-of-view overlap.
The paper's qualitative claim supports this, noting that with rig embeddings the model confidently
reconstructs side-view cameras with minimal overlap.

### Why Optional Rather Than Required

Making rig metadata mandatory would produce a model useless on ordinary image collections. The 50%
dropout on every metadata field turns a hard requirement into a soft signal, and produces a single
model that spans unstructured sets, fully calibrated rigs, and everything between. The ablation shows
the model degrades gracefully rather than collapsing when fields are missing.

### Why Raymaps Rather Than Pointmaps for Pose

Pointmaps infer pose indirectly through 3D predictions, so they fail exactly where 3D is
ill-defined — sky, dynamic objects, distant structure. Raymaps carry pose information per pixel
regardless of scene depth, and admit closed-form intrinsic and extrinsic recovery. The
WayveScenes101 result where Fast3R edges out `Rig3R_Unstr` on Chamfer while trailing badly on pose is
the cleanest empirical evidence that these two quantities have been successfully decoupled.

### Applications

- **Autonomous driving**: ego-pose and scene structure from the vehicle's camera rig in one pass
- **Embodied AI and robotics**: agent pose from multi-camera platforms
- **Rig calibration**: extrinsic discovery from unordered captures with no timestamps or metadata
- **Fleet data processing**: single-pass reconstruction where COLMAP takes over two minutes per scene

### Limitations (stated by the authors)

- Data diversity and quality, particularly the limited variety of rig configurations in existing datasets, is the main performance limitation
- Raymaps only implicitly downweight dynamic content; explicit motion modeling could improve robustness in highly dynamic scenes
- Balancing structured rig-based temporal sampling against unordered general sampling is left to future work

## 🔗 Related Work

### Building On

- **DUSt3R**: pointmap regression formulation, the confidence-weighted pointmap loss, and encoder initialization.
- **Fast3R**: the 1D sine-cosine index embedding scheme that lets Rig3R generalize to varying frame and camera counts.
- **VGGT**: motivates learning scale and direction norms directly, which the paper finds more stable for camera centers near the origin.
- **DPT**: pointmap head architecture.

### Contrast with Conditioning Approaches

- **Pow3R**: improves flexibility via lightweight conditioning on intrinsics, relative pose, or depth. Rig3R conditions on a different and complementary axis — rig identity and structure rather than per-camera calibration.
- **MV-DUSt3R**: multi-frame attention; **Fast3R**: scales to hundreds of views. Both still treat views as unordered.

### Contrast with Classical Rig-Aware Methods

- **COLMAP**: models the rig as a single moving entity with fixed intra-rig calibration in bundle adjustment.
- **Kaess and Dellaert**: probabilistic SLAM for multi-camera rigs modeling cross-camera feature associations.
- **Carrera et al.**: SLAM-based automatic extrinsic calibration, including non-overlapping fields of view.
- **Heng et al.**: infrastructure-based calibration using image-based localization and prebuilt maps.

Rig3R differs by supplying rig information as optional input embeddings rather than as a hard
constraint in an optimizer.

## 📚 Key Takeaways

Rig3R demonstrates that:

1. **Rig structure is a free, unused prior**: real capture platforms are structured, and feed-forward reconstruction models were discarding that structure by construction.
2. **Optional conditioning via dropout is the right interface**: one model handles unstructured sets, partial metadata, and full calibration, degrading gracefully instead of failing.
3. **Rig-relative raymaps make discovery possible**: predicting camera parameters in a rig-centric frame decoupled from ego-motion lets the model cluster cameras and recover calibration from unordered images with no metadata at all.
4. **Pose should be read from rays, not points**: separating pose estimation from 3D prediction keeps pose accurate in sky and dynamic regions where pointmaps are ill-defined.

By treating rig metadata as an optional embedding rather than a structural assumption, Rig3R extends
the feed-forward reconstruction line into the structured-capture regime that embodied AI actually
operates in — and along the way defines a new task, rig discovery from unordered images, that neither
learned nor classical methods had previously attempted.

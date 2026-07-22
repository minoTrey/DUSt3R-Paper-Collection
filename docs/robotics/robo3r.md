# Robo3R: Enhancing Robotic Manipulation with Accurate Feed-Forward 3D Reconstruction (RSS 2026)

![robo3r — architecture](https://arxiv.org/html/2602.10101v2/x1.png)

_Method Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Sizhe Yang, Linning Xu, Hao Li, Juncheng Mu, Jia Zeng, Dahua Lin, Jiangmiao Pang
- **Institution**: Shanghai AI Laboratory; The Chinese University of Hong Kong; University of Science and Technology of China; Tsinghua University
- **Venue**: RSS 2026
- **Links**: [Paper](https://arxiv.org/abs/2602.10101) | [Project Page](https://yangsizhe.github.io/robo3r/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward, manipulation-ready 3D reconstruction model that predicts accurate metric-scale scene geometry directly from RGB images and robot states in real time, jointly inferring scale-invariant local geometry and relative poses unified into the canonical robot frame via a learned global similarity transformation.

## 🎯 Key Contributions

1. **Robo3R-4M dataset**: A large-scale synthetic dataset (100,000 scenes, 4 million photorealistic frames) built in NVIDIA Isaac Sim, with diverse assets (16,911 objects, 4,710 textures, 6,512 environment maps), extensive domain randomization, and rich multi-modal annotations for manipulation-oriented reconstruction.
2. **Manipulation-ready reconstruction model**: A feed-forward model fusing RGB with robot states, achieving high-fidelity depth, precise camera parameters, accurate metric scale, and a consistent canonical coordinate system in real time.
3. **Masked point head + keypoint-PnP refinement**: A masked point head decomposing dense prediction into depth, normalized image coordinate and mask (mitigating over-smoothing for sharp geometry), and a keypoint-based Perspective-n-Point module refining camera extrinsics and global alignment.
4. **Downstream validation**: Consistent gains over reconstruction baselines and depth sensors across imitation learning, sim-to-real transfer, grasp synthesis, and collision-free motion planning — including transparent, reflective and tiny objects.

## 🔧 Technical Details

### Representation

- Input: monocular or binocular RGB images `Ii` (N ∈ {1,2}) and robot state J (joint angles). Outputs: depth maps, normalized image coordinates, relative translation/rotation, and a global similarity transformation S ∈ R⁴ˣ⁴.
- Scale-invariant local points are predicted per view, then registered across views via predicted relative poses, then mapped into the metric-scale canonical robot frame via `Pcano = [p;1] Sᵀ`, where `S = s·T`.

### Architecture

- DINOv2 ViT-L encodes images; robot states are projected to features by an MLP and fused with image features via element-wise addition; learnable similarity-transformation (S.T.) tokens are appended.
- Backbone: 18 stacked alternating global and frame-wise attention blocks (Alternating-Attention).
- **Masked point head**: three branches (robot, objects, background), each with depth, ray and mask heads; region-specific points are unprojected and masked, then aggregated. A five-layer transformer decoder precedes the heads.
- **Relative pose head**: predicts 3D translation + 9D rotation (reshaped to 3×3, orthogonalized via SVD).
- **Extrinsic estimation module**: extracts robot keypoints via forward kinematics, predicts 2D keypoints (Soft-Argmax, sub-pixel), and solves PnP to refine the similarity transformation.

### Training

- Multi-task loss: point loss, normal loss, mask loss, relative pose loss, similarity transformation loss, keypoint loss.
- Deployed on an NVIDIA RTX 4090; robotic control frequency 10 Hz.

## 📊 Results

### Point Map Estimation

원논문 Table I. Scale-invariant point error and scale error (both ↓). Benchmark: 2,000 test scenes / 80,000 frames. MA = MapAnything, MA-FT = MapAnything fine-tuned on Robo3R-4M, DA3 = DepthAnything3.

| Setting   | Method   | Point Err. ↓ | Scale Err. ↓ |
| --------- | -------- | ------------ | ------------ |
| Monocular | VGGT     | 0.126        | 0.663        |
| Monocular | π³       | 0.061        | 0.497        |
| Monocular | DA3      | 0.075        | 0.506        |
| Monocular | MA       | 0.078        | 0.467        |
| Monocular | MA-FT    | 0.010        | 0.010        |
| Monocular | **Ours** | **0.006**    | **0.007**    |
| Binocular | π³       | 0.032        | 0.483        |
| Binocular | MA-FT    | 0.009        | 0.007        |
| Binocular | **Ours** | **0.005**    | **0.004**    |

In the monocular case Robo3R reaches a point error of 0.006, an order-of-magnitude improvement over the second-best π³ (0.061); baselines other than MA-FT suffer scale errors > 0.46.

### Relative Camera Pose Estimation

원논문 Table II. RTE / RRE lower better, RTA@0.03 / RRA@0.03 higher better.

| Method   | RTE ↓     | RRE ↓     | RTA@0.03 ↑ | RRA@0.03 ↑ |
| -------- | --------- | --------- | ---------- | ---------- |
| VGGT     | 0.373     | 0.316     | 0.014      | 0.052      |
| π³       | 0.116     | 0.073     | 0.110      | 0.245      |
| MA       | 0.168     | 0.116     | 0.031      | 0.069      |
| DA3      | 0.160     | 0.111     | 0.129      | 0.226      |
| **Ours** | **0.014** | **0.013** | **0.951**  | **0.899**  |

Robo3R's RTE (0.014) and RRE (0.013) are approximately 8× and 5× lower than the best baseline π³, respectively.

### Downstream Manipulation

원논문 Tables III–VI. Number of successes over total trials. "Other FFs" (other feed-forward reconstruction models) failed to produce feasible actions ("-").

| Task type                 | Metric        | Depth Camera | **Ours** |
| ------------------------- | ------------- | ------------ | -------- |
| Imitation (Sweep Bean)    | successes /16 | 4/16         | 14/16    |
| Imitation (Insert Screw)  | successes /16 | 7/16         | 15/16    |
| Sim-to-real (Push Cube)   | successes /16 | 7/16         | 16/16    |
| Sim-to-real (Pick Cube)   | successes /16 | 5/16         | 12/16    |
| Grasp (Transparent/Refl.) | successes /16 | 7/16         | 10/16    |
| Grasp (Small)             | successes /16 | 6/16         | 11/16    |
| Collision-free MP (Thin)  | successes /5  | 2/5          | 5/5      |

On imitation learning Breakfast, MF+Depth Camera (11/16) beats MF+Ours (12/16) only marginally, and both tie on BiDex Pour (16/16) — Robo3R's advantage is largest on small/precise and transparent/reflective scenarios.

### Ablations

원논문 Table VII (extrinsic module, robot base frame; ATE/ARE ↓, ATA@0.01/ARA@0.01 ↑) and Table VIII (robot-state conditioning).

| Study     | Variant      | key metric   | value |
| --------- | ------------ | ------------ | ----- |
| Extrinsic | Direct Pred. | ATA@0.01 ↑   | 0.334 |
| Extrinsic | KP + PnP     | ATA@0.01 ↑   | 0.442 |
| State     | w/o State    | Point Err. ↓ | 0.006 |
| State     | Self Attn    | Point Err. ↓ | 0.006 |
| State     | Ours         | Point Err. ↓ | 0.005 |

The keypoint + PnP module yields lower translation/rotation error and higher accuracy than directly regressing extrinsics; fusing robot state via element-wise addition outperforms both no-state and self-attention fusion.

## 💡 Insights & Impact

- **Robot priors sharpen reconstruction**: Explicitly fusing robot state and predicting keypoints for PnP-based extrinsics gives manipulation-grade metric geometry that generic feed-forward models lack.
- **A depth-sensor alternative**: Robo3R reliably handles transparent, reflective and tiny objects (down to 1.5 mm) that blind stereo/ToF depth cameras, and requires no calibration.
- **3D lifting helps policies**: Feeding Robo3R point clouds to 3D-based policies consistently improves over 2D policies and reduces the sim-to-real gap through a domain-consistent canonical representation.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: Provides the Alternating-Attention backbone Robo3R adopts and is a reconstruction baseline.
- **[π³ / Pi3](../reconstruction/pi3.md)**: Permutation-equivariant affine-invariant reconstruction, the strongest baseline compared.
- **[MapAnything](../reconstruction/mapanything.md)** & **[Depth Anything 3](../reconstruction/depth-anything-3.md)**: Metric-scale feed-forward baselines (MA / DA3).
- **[DUSt3R](../foundation/dust3r.md)**: The pointmap foundation of the feed-forward reconstruction line.

## 📚 Key Takeaways

1. Robo3R produces accurate metric-scale geometry in the canonical robot frame directly from RGB + robot state, reaching an order-of-magnitude lower point error than prior feed-forward reconstructors.
2. The masked point head (sharp fine-grained geometry) and keypoint-PnP extrinsic refinement are the key architectural ingredients, validated by ablations.
3. Across imitation learning, sim-to-real transfer, grasp synthesis and collision-free planning, Robo3R matches or beats depth cameras — decisively so for transparent, reflective and tiny objects — offering a calibration-free 3D sensing module for manipulation.

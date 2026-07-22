# Calib3R: A 3D Foundation Model for Multi-Camera to Robot Calibration and 3D Metric-Scaled Scene Reconstruction (arXiv preprint)

![calib3r — architecture](https://arxiv.org/html/2509.08813/x1.png)

_Overview of the Calib3R method (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Davide Allegro, Matteo Terreran, Stefano Ghidoni
- **Institution**: University of Padova
- **Venue**: arXiv preprint (2025-09)
- **Note**: The venue could not be confirmed from any primary source. It should be re-checked before being cited as published.
- **Links**: [Paper](https://arxiv.org/abs/2509.08813)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: A patternless method that folds camera-to-robot (hand-eye) calibration and metric-scaled 3D reconstruction into one MASt3R-based joint optimization, recovering a per-camera scale factor so that the reconstruction lands directly in the robot's reference frame.

## 🎯 Key Contributions

1. **Unified calibration + reconstruction**: A single optimization that simultaneously estimates scene geometry, camera-to-robot transformations, per-camera scale factors, and inter-camera rigid transforms — rather than the usual two-step "reconstruct, then calibrate" pipeline.
2. **Patternless operation**: No checkerboard required; the paper shows generic task-relevant objects placed in the workspace suffice.
3. **Single- and multi-camera, arm and mobile robot**: One formulation covers manipulators (end-effector frame) and mobile platforms (base frame), with a cross-camera rigidity loss that activates only when M > 1.
4. **VLM-based ground-plane estimation**: For mobile robots, the z-unobservability problem is resolved by segmenting the floor with Grounding DINO + SAM 2 using language prompts, then averaging camera height across frames.

## 🔧 Technical Details

### Problem Setup

A robot with M RGB cameras moves through N poses observing a static scene. From the N × M images, the goal is the transformation `T_R^{C_j}` between each camera C_j and the robot reference frame R, plus a metric 3D reconstruction expressed in the initial robot frame W = R₀.

### Pipeline

Calib3R first computes pairwise local 3D pointmaps using the co-visibility graph strategy from MASt3R-SfM. An informative subset of image pairs E is selected with a pairwise matcher built on MASt3R's encoder — pairs may cross cameras when content overlaps. MASt3R then produces canonical pointmaps X̃ᵢ⁽ʲ⁾ for each image.

### The Unified Loss

Three groups of terms are minimized together by gradient descent:

- **Scene geometry**: per-camera 3D matching loss `L_3D,j` (distance between matching 3D points across pointmaps) and 2D reprojection loss `L_2D,j`.
- **Calibration**: `L_cal,j = Σᵢ ‖Aᵢ X − X B_{j,i}(λ_j)‖²`, the classic AX = XB hand-eye residual, but with camera motion translation scaled by an unknown per-camera factor λ_j > 0. A separate λ per camera is required because cameras without visual overlap have no way to infer relative scale from correspondences.
- **Cross-camera**: `L_cross = Σᵢ ‖T(λ_n)·T_{C_m}^{C_n} − T_{C_m}^{C_n}·T(λ_m)‖₂`, enforcing that the fixed inter-camera geometry stays rigid throughout the trajectory.

The total is `L_Calib3R = Σ_j (L_3D,j + L_2D,j + L_cal,j) + L_cross`. When M = 1 the cross-camera term vanishes and has no influence.

The optimization yields, in one step: (i) pose `T_W^{C_{j,i}}` for every image, (ii) a scale factor λ_j per camera trajectory, and (iii) the rigid camera-to-robot transforms `T_R^{C_j}`.

### Metrics

- **Calibration**: mean translation error `e_t = (1/M)Σ‖t − t̂‖₂` and mean rotation error `e_θ = (1/M)Σ angle(Rᵀ R̂)`, the axis-angle magnitude of the relative rotation.
- **Metric scale**: checkerboard corners across N views are back-projected into the reconstructed point cloud; the mean adjacent-corner distance `m_s` is compared against the true square size `s`, reporting absolute scale error `m_s − s`, standard deviation `σ_s`, and relative scale error `δ_s (%) = |m_s − s| / s × 100`.

### Compute

Calib3R and the other 3D-foundation-model baselines run on an NVIDIA A40 (48 GB GDDR6). Classical calibration methods run on an Intel Core i7-1280P workstation with 16 GB RAM under Ubuntu 20.04.

## 📊 Results

### Hand-Eye Calibration, Manipulator Setups

원논문 Table I. 25개 로봇 포즈에서 계산한 평균 오차. Pattern 열은 해당 방법이 캘리브레이션 패턴을 요구하는지를 뜻하며, 패턴 기반 방법은 패턴이 없는 Franka Object·GraspNet에서 적용 불가라 `-`로 남는다.

| Method             | Pattern | Franka Pattern e_t [cm] | e_θ [rad] | Franka Object e_t [cm] | e_θ [rad] | GraspNet-1Billion e_t [cm] | e_θ [rad] |
| ------------------ | ------- | ----------------------- | --------- | ---------------------- | --------- | -------------------------- | --------- |
| Tsai               | ✓       | 2.631                   | 0.041     | -                      | -         | -                          | -         |
| Park               | ✓       | 3.610                   | 0.038     | -                      | -         | -                          | -         |
| Horaud             | ✓       | 2.743                   | 0.038     | -                      | -         | -                          | -         |
| Andreff            | ✓       | 11.341                  | 0.033     | -                      | -         | -                          | -         |
| Daniilidis         | ✓       | 2.472                   | 0.035     | -                      | -         | -                          | -         |
| Evangelista        | ✓       | **0.781**               | 0.041     | -                      | -         | -                          | -         |
| COLMAP + Calib     | ✗       | 28.210                  | 0.122     | 18.212                 | 0.092     | 22.324                     | 0.122     |
| DUSt3R + Calib     | ✗       | 24.641                  | 0.043     | 16.431                 | 0.031     | 18.212                     | 0.042     |
| MASt3R-SfM + Calib | ✗       | 1.812                   | 0.023     | 1.742                  | 0.027     | 3.427                      | 0.032     |
| VGGT + Calib       | ✗       | 1.734                   | 0.034     | 1.674                  | 0.038     | 2.342                      | 0.031     |
| **Calib3R**        | ✗       | 1.127                   | **0.014** | **0.415**              | **0.011** | **1.744**                  | **0.023** |

Reported honestly: Calib3R does **not** win translation on Franka Pattern — Evangelista's pattern-based reprojection-minimization method reaches 0.781 cm vs Calib3R's 1.127 cm. Calib3R's claim is best rotation accuracy overall (0.014 rad) and best among pattern-free methods everywhere. The paper attributes the rotation robustness to rotation being immune to scale ambiguity plus dense, globally distributed feature matches.

The paper notes GraspNet results are slightly worse than Franka Object and offers a mechanistic explanation: GraspNet sequences are grasping tasks with predominantly top-down viewpoints and minimal roll/pitch rotation, limiting the observability of the unknown transformation.

### Metric Scale Accuracy, Franka Pattern

원논문 Table II. 참값 체커보드 사각형 크기 3 cm 기준. COLMAP은 체커보드 코너를 3D로 투영할 만큼 조밀한 재구성을 내지 못해 제외되었다.

| Method             | m_s − s [cm] | σ_s [cm]  | ε_s [%]  |
| ------------------ | ------------ | --------- | -------- |
| DUSt3R + Calib     | 0.79         | 0.091     | 26.33    |
| MASt3R-SfM + Calib | 0.41         | 0.027     | 13.67    |
| VGGT + Calib       | 0.17         | 0.008     | 5.67     |
| **Calib3R**        | **0.11**     | **0.005** | **3.67** |

### Camera-to-Robot Calibration, Mobile Robots

원논문 Table III. 25개 로봇 포즈 기준. OpenLORIS와 CSE는 패턴이 없어 패턴 기반 방법을 적용할 수 없고, SensorX2Car는 translation을 추정하지 않아 `−`다.

| Method       | Pattern | Real MEMROC e_t | e_θ       | Synth. MEMROC e_t | e_θ       | OpenLORIS e_t | e_θ       | CSE e_t   | e_θ       |
| ------------ | ------- | --------------- | --------- | ----------------- | --------- | ------------- | --------- | --------- | --------- |
| MEMROC       | ✓       | 3.412           | 0.031     | 0.712             | **0.004** | −             | −         | −         | −         |
| Joint-MEMROC | ✓       | **3.325**       | 0.031     | **0.709**         | 0.005     | −             | −         | −         | −         |
| Zuniga       | ✗       | 12.231          | 0.123     | 7.172             | 0.113     | 35.126        | 0.292     | 17.123    | 0.189     |
| SensorX2Car  | ✗       | −               | 0.043     | −                 | 0.026     | −             | 0.039     | −         | 0.028     |
| **Calib3R**  | ✗       | 3.725           | **0.021** | 2.432             | 0.006     | **3.419**     | **0.033** | **2.723** | **0.005** |

On real MEMROC, Calib3R is 12% worse in translation than the pattern-based Joint-MEMROC (3.725 vs 3.325 cm) while improving rotation by roughly 32%. On synthetic MEMROC the pattern-based methods win clearly, which the paper attributes to noise-free synthetic conditions making pattern detection nearly perfect. Calib3R's decisive wins are on the pattern-free OpenLORIS and CSE benchmarks.

### Metric Scale on Real MEMROC

Text-reported, not tabulated: Calib3R achieves mean scale error `m_s − s = 0.48 cm`, `σ_s = 0.025`, and percentage scale error `ε_s = 4.8%`. No baseline comparison is given here — the paper notes the mobile-robot calibration baselines produce no reconstruction at all.

### Robustness to Image Count

Figures 7 and 13 plot calibration error against the number of input images (25 down to 5, removing 2 at a time). The paper's text-stated results: on Franka Object, Calib3R achieves translation error below 5 cm and rotation error under 0.04 rad with as few as 5 images, and translation error below 1 cm with 15 images; on real MEMROC it maintains high accuracy with fewer than 10 images per camera. The per-method curves themselves exist only as plots and are not transcribed here.

## 💡 Insights & Impact

### Why Joint Beats Two-Stage

The cleanest evidence in the paper is the MASt3R-SfM + Calib comparison. Both that baseline and Calib3R are built on MASt3R, so the only difference is coupling: Calib3R optimizes geometry and calibration together instead of feeding poses forward. The reported gap is roughly a 40% reduction in both translation and rotation error on Franka Pattern. Decoupled pipelines inherit whatever error the reconstruction stage made, with no way to correct it downstream.

### Scale as an Optimization Variable, Not a Post-Hoc Fix

The insight that makes the whole thing work is treating λ_j as a free variable inside the hand-eye residual rather than trying to recover scale afterwards. Because robot poses are metric by construction, the AX = XB constraint itself supplies the scale — the calibration problem and the metric-scale problem are the same problem. The per-camera λ is what permits non-overlapping cameras in a multi-camera rig.

### The Pattern Is Replaceable

The most striking result is that Franka Object (generic objects, no pattern) yields _better_ calibration than Franka Pattern (0.415 cm vs 1.127 cm), and even beats Evangelista's pattern-based method on its home turf. Dense foundation-model correspondences spread over the whole image are simply a richer constraint set than a handful of checkerboard corners.

### Practical Ceiling

The authors state future work targets real-time calibration and reconstruction, and extension to dynamic environments — the current method is an offline gradient-descent optimization on an A40. The z-unobservability workaround for mobile robots also depends on a VLM segmentation stack, adding two large models to the runtime.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md) — the 3D foundation model Calib3R builds on for pointmaps and matching.
- [MASt3R-SfM](../foundation/mast3r-sfm.md) — supplies the co-visibility graph pair-selection strategy; also the closest two-stage baseline.
- [DUSt3R](../foundation/dust3r.md) — earlier pointmap regressor, used as a weaker two-stage baseline.
- [VGGT](../reconstruction/vggt.md) — the strongest reconstruction-based competitor in Table I and II.
- [rig3r](rig3r.md) — multi-camera rig geometry from a feed-forward model, an adjacent robotics application.
- [Adapt3R](../dynamic/adapt3r.md) — 3D representations for robot manipulation policies.

## 📚 Key Takeaways

1. **Calibration and metric reconstruction are one problem.** Robot poses supply the metric scale that RGB reconstruction lacks; solving them jointly beats solving them in sequence by ~40% on the same backbone.
2. **Per-camera scale factors enable non-overlapping rigs.** Without a separate λ_j, multi-camera setups with no shared content cannot be related at all.
3. **Patterns are not required and may even hurt.** Generic objects gave 0.415 cm translation error vs 1.127 cm with a checkerboard.
4. **Rotation is the reliable signal.** Calib3R's rotation accuracy is best-in-table everywhere, because rotation is unaffected by scale ambiguity.
5. **Low-data regime holds up.** Below 10 images per camera the method still reports usable accuracy, though the supporting curves are plots rather than tables.

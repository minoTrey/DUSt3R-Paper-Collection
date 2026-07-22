# SurgCUT3R: Surgical Scene-Aware Continuous Understanding of Temporal 3D Representation (arXiv preprint (2026-03))

![surgcut3r — architecture](https://arxiv.org/html/2603.06971v1/figures/pipeline.png)

_Overview of SurgCUT3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Kaiyuan Xu, Fangzhou Hong, Daniel Elson, Baoru Huang
- **Institution**: The Hamlyn Centre for Robotic Surgery, Imperial College London; S-Lab, College of Computing and Data Science, Nanyang Technological University; Department of Computer Science, University of Liverpool
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.06971) | [Project Page](https://chumo-xu.github.io/SurgCUT3R-ICRA26/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A framework that adapts the unified CUT3R reconstruction model to monocular surgical video by generating metric-scale pseudo-GT depth from public stereo datasets, training with a hybrid supervised + geometric self-correction loss, and using a hierarchical global/local dual-model inference to suppress long-sequence pose drift.

## 🎯 Key Contributions

1. **Pseudo-GT depth pipeline**: Leverages public stereo surgical datasets (SCARED, StereoMIS) to synthesize large-scale metric-scale pseudo-ground-truth depth maps via FoundationStereo, bridging the surgical data gap.
2. **Hybrid supervision**: Couples direct pseudo-GT supervision with a geometric self-correction (self-supervised consistency) mechanism to enhance robustness against inherent label noise from specular reflections, smoke, and low-texture regions.
3. **Hierarchical inference**: A dual-model design — a global model for long-range trajectory stability and a local model for accurate short-window motion — mitigates accumulated pose drift over long surgical videos.

## 🔧 Technical Details

### Base Model

SurgCUT3R adapts CUT3R, a unified online reconstruction framework with a persistent, continuously updated state that outputs scale-consistent pointmaps and camera parameters per frame. Heads predict self- and world-frame pointmaps (DPT) and camera pose (MLP).

### Pseudo-GT Generation

Rectified stereo pairs (distortion correction + rectification following MSDESIS/Endo-4DGS) are processed by FoundationStereo to a disparity map, converted to metric depth D = b·f/d via known baseline and focal length. Each frame yields an (image, pseudo-GT depth, GT pose) triplet.

### Hybrid Supervision

Total loss L_total = (L_conf + L_pose) + λ_consist·L_consistency, where L_conf is CUT3R's confidence-aware regression loss and L_pose the quaternion + translation pose loss. L_consistency (adapted from MegaSaM's depth optimization objective, used here as a training-time self-supervised signal) combines optical-flow consistency (RAFT), temporal geometric consistency, and a prior regularization (scale-invariant + multi-scale gradient + surface-normal terms).

### Hierarchical Inference

Two model instances differ only by maximum temporal sampling interval: a global model (interval 12) for robust long-range motion, and a local model (interval 3) for accurate relative motion. Per-segment alignment plus error correction distributes drift (via Slerp for rotation, linear interpolation for translation) between global anchors.

### Setup

NVIDIA 4090 GPU, PyTorch, AdamW (lr 1.0×10⁻⁵, weight decay 0.05, batch size 8). Two-stage training: fine-tune CUT3R weights 5 epochs with supervised losses, then add L_consistency for 2 more epochs. Trained on SCARED (Datasets 1–7, excluding miscalibrated 4/5), tested on SCARED Datasets 8–9 and 4 unseen StereoMIS sequences. Depth evaluated at 256×192; ATE/RTE in millimeters (RTE window 16).

## 📊 Results

원논문 Table I. Depth: Abs Rel/Sq Rel/RMSE lower is better, δ<1.25 higher; pose ATE/RTE in mm lower is better; FPS higher is better.

### SCARED

| Category           | Method           | Abs Rel↓  | Sq Rel↓   | RMSE↓     | δ<1.25↑   | ATE↓      | RTE↓      | FPS↑     |
| ------------------ | ---------------- | --------- | --------- | --------- | --------- | --------- | --------- | -------- |
| Optimization-based | MonST3R (w/ Opt) | 0.098     | 1.237     | 7.979     | 0.904     | 21.774    | 1.582     | 0.3      |
| Optimization-based | MegaSaM          | **0.056** | **0.392** | **4.586** | **0.978** | **2.002** | **0.315** | 0.7      |
| Feed-forward       | Spann3R          | 0.119     | 2.524     | 10.218    | 0.867     | 10.258    | 1.260     | 19.2     |
| Feed-forward       | AF-SfMLearner    | 0.073     | 0.534     | 5.028     | 0.964     | 10.312    | 0.971     | 3.6      |
| Feed-forward       | EndoDAC          | 0.059     | 0.443     | 4.833     | 0.973     | 10.225    | 0.963     | **36.3** |
| Feed-forward       | SurgCUT3R (Ours) | 0.057     | 0.410     | 4.647     | 0.977     | 5.514     | 0.752     | 19.7     |

The RMSE LOG column of the original Table I is omitted here to stay within the column limit; δ<1.25 values are taken directly from the source.

### StereoMIS (cross-dataset generalization)

| Category           | Method           | Abs Rel↓  | Sq Rel↓   | RMSE↓     | δ<1.25↑   | ATE↓       | RTE↓      | FPS↑     |
| ------------------ | ---------------- | --------- | --------- | --------- | --------- | ---------- | --------- | -------- |
| Optimization-based | MegaSaM          | **0.061** | **0.506** | **4.615** | **0.976** | **19.705** | 0.877     | 0.7      |
| Feed-forward       | EndoDAC          | 0.075     | 0.672     | 6.047     | 0.957     | 24.264     | 1.121     | **36.3** |
| Feed-forward       | SurgCUT3R (Ours) | 0.070     | 0.637     | 5.732     | 0.965     | 25.939     | **0.902** | 19.7     |

On SCARED, MegaSaM achieves the highest depth and pose accuracy but is limited to 0.7 FPS; SurgCUT3R delivers near-SOTA depth and second-best pose (ATE 5.514) at a far faster 19.7 FPS. On unseen StereoMIS, note SurgCUT3R's ATE (25.939) is higher than EndoDAC's (24.264), though its RTE is best among feed-forward methods.

### Ablations

원논문 Table II (loss, SCARED) · Table III (architecture).

| Configuration     | Sq Rel↓   | RMSE↓     | δ<1.25↑   |     | Architecture     | ATE↓      |
| ----------------- | --------- | --------- | --------- | --- | ---------------- | --------- |
| w/o L_consistency | 0.423     | 4.763     | 0.975     |     | CUT3R Only       | 9.361     |
| w/ L_consistency  | **0.410** | **4.647** | **0.977** |     | Dual-Arch (Ours) | **5.514** |

The consistency loss yields marginal but consistent depth improvements; the dual-model hierarchical framework nearly halves ATE (9.361 → 5.514) versus a single model, demonstrating drift mitigation.

## 💡 Insights & Impact

- **Data gap over architecture gap**: The main barrier to applying CUT3R to surgery is the absence of dense GT depth; SurgCUT3R synthesizes it from stereo geometry rather than redesigning the model.
- **Self-correction against label noise**: Because pseudo-GT depth is imperfect (specular reflections, smoke), the self-supervised consistency term acts as a geometric regularizer preventing overfitting to noisy labels.
- **Global anchors correct local drift**: Combining a sparse but globally stable trajectory with dense but locally drifting segments yields a drift-corrected trajectory for long procedures.
- **Practical trade-off**: SurgCUT3R targets a clinically practical balance — near-SOTA accuracy at 19.7 FPS (near real-time), unlike the 0.7 FPS optimization-based MegaSaM. Since StereoMIS evaluation uses self-generated pseudo-GT, it may carry bias, and validation on datasets with authentic GT is future work.

## 🔗 Related Work

- **[CUT3R](../dynamic/cut3r.md)**: The unified persistent-state base model SurgCUT3R adapts to surgery.
- **[DUSt3R](../foundation/dust3r.md)** & **[MASt3R](../foundation/mast3r.md)**: The pointmap-regression foundations underpinning the lineage.
- **[MonST3R](../dynamic/monst3r.md)**: A dynamic-scene pointmap method used as an optimization-based baseline.
- **[Spann3R](spann3r.md)**: An online spatial-memory baseline.
- **[MASt3R-SLAM](mast3r-slam.md)** & **[SLAM3R](slam3r.md)**: SLAM-based long-sequence-consistency methods discussed in related work.
- **[Endo3R](../medical/endo3r.md)**: A related unified online surgical reconstruction framework.

## 📚 Key Takeaways

1. SurgCUT3R adapts CUT3R to monocular surgical video via metric-scale pseudo-GT depth synthesized from stereo datasets with FoundationStereo.
2. A hybrid supervised + self-supervised consistency loss guards against pseudo-GT label noise, and a global/local dual-model hierarchy suppresses long-sequence pose drift.
3. It delivers near-SOTA depth and second-best pose at 19.7 FPS on SCARED, far faster than the 0.7 FPS optimization-based MegaSaM, and generalizes to unseen StereoMIS (though its StereoMIS ATE trails EndoDAC).
4. The dual-architecture nearly halves ATE versus a single model; validation on datasets with authentic ground truth remains future work.

# TTT3R: 3D Reconstruction as Test-Time Training (ICLR 2026)

## 📋 Overview

- **Authors**: Xingyu Chen, Yue Chen, Yuliang Xiu, Andreas Geiger, Anpei Chen
- **Institution**: Zhejiang University, Westlake University, University of Tübingen / Tübingen AI Center
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2509.26645) | [Code](https://github.com/Inception3D/TTT3R) | [Project Page](https://rover-xingyu.github.io/TTT3R)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Reinterprets CUT3R's recurrent state update as Test-Time Training and derives a closed-form, confidence-guided per-token learning rate — a training-free change that substantially improves length generalization at no extra compute.

## 🎯 Key Contributions

1. **Sequence-modeling view of 3D foundation models**: Formalizes pointmap regression as `Tokenize → Update → Read → De-tokenize`, showing that full-attention methods (Fast3R, VGGT) are state _concatenation_ with O(t²) cost, while RNN-based methods (CUT3R, Point3R) are fixed-length state updates with O(1) cost.
2. **CUT3R as degenerate TTT**: Shows that CUT3R's softmax cross-attention state update is exactly a TTT gradient step with a constant learning rate βₜ = 1.0. Because softmax weights normalize to 1 along the observation axis, the state is forced to fully adopt each new observation — the structural cause of catastrophic forgetting.
3. **Confidence-guided state update rule**: Introduces a per-token learning rate βₜ = σ(mean over spatial positions of Q_{S_{t-1}}K_{X_t}ᵀ) derived from state–observation alignment confidence, suppressing low-quality updates (e.g. textureless regions).
4. **Training-free and plug-and-play**: No fine-tuning, no additional parameters, and — per the paper — NO additional computational cost over the CUT3R baseline.
5. **Reported operating point**: 2× improvement in global pose estimation over baselines, at 20 FPS with 6 GB of GPU memory when processing thousands of images (abstract).

## 🔧 Technical Details

### The two update rules

For RNN-based reconstruction, CUT3R's update is

```text
Update(S_{t-1}, X_t) = S_{t-1} + softmax(Q_{S_{t-1}} K_{X_t}^T) V_{X_t}
```

TTT3R keeps the same cross-attention gradient direction but gates it:

```text
Update(S_{t-1}, X_t) = S_{t-1} - β_t ∇(S_{t-1}, X_t)
β_t = σ( mean_m  Q_{S_{t-1}} K_{X_t}^T )          ∈ R^{n×1}
∇   = -softmax(Q_{S_{t-1}} K_{X_t}^T) V_{X_t}
```

The state S is treated as a **fast weight** learned at test time from in-context tokens; the frozen network parameters are the **slow weights** acting as a meta-learner. The key indexes _where_ to write into the state, the value determines _what_ to write, and βₜ controls _how much_ memory plasticity is allowed.

### Why the confidence signal works

Higher alignment confidence between state queries and observation keys indicates a stronger, lower-uncertainty match between memory and the incoming frame, and therefore justifies a larger update step. Aggregating token-level statistics suppresses updates from unreliable regions, which the paper links to online loop closure behaviour (Figure 5).

### Optional State Reset variant

The limitations section describes `TTT3R + State Reset`: the state is periodically reset to its initial value, and the resulting chunks are aligned using global metric poses without additional optimization. This targets the _unexplored states_ hypothesis — that recurrence drives the state out of the training distribution on long sequences.

## 📊 Results

### Long-sequence behaviour (main paper)

The main-paper long-sequence evaluations (camera pose on ScanNet / TUM-D, video depth on Bonn / KITTI, 3D reconstruction on 7-Scenes) are reported as **figures**, not tables, so exact values are not transcribed here. The qualitative findings the paper states: VGGT and StreamVGGT (full attention) run out of memory beyond roughly 150 frames for depth evaluation; Point3R improves over CUT3R but hits OOM beyond 700 frames; TTT3R sustains accuracy while keeping CUT3R's constant memory and speed.

### Gating-mechanism ablation

원논문 Table 1. 카메라 포즈는 TUM-dynamic 1000프레임, 비디오 깊이는 KITTI 500프레임 기준.

| Method              | ATE ↓     | RPE rot ↓ | Abs Rel ↓ | δ<1.25 ↑ |
| ------------------- | --------- | --------- | --------- | -------- |
| CUT3R               | 0.173     | 0.494     | 0.152     | 80.2     |
| CUT3R + ScalarLR    | 0.165     | 0.502     | 0.151     | 80.6     |
| CUT3R + ConditionLR | 0.166     | 0.509     | 0.149     | 81.0     |
| CUT3R + TokenLR     | 0.154     | 0.497     | 0.148     | 81.5     |
| **TTT3R**           | **0.106** | **0.431** | **0.131** | **86.9** |
| TTT3R + Finetune    | 0.091     | 0.434     | 0.133     | 86.3     |

Fine-tuning helps pose but _degrades_ video depth (0.131 → 0.133 Abs Rel, 86.9 → 86.3 δ<1.25) — the paper attributes this to the model prioritizing global alignment over per-view accuracy once trained on 4–64 view sequences.

### TTT-derived rule vs. non-TTT baselines

원논문 Table 5. 같은 설정(TUM-dynamic 1000프레임 / KITTI 500프레임). 각 baseline은 자체 ablation에서 최적 하이퍼파라미터를 사용한다.

| Method            | ATE ↓     | RPE rot ↓ | Abs Rel ↓ | δ<1.25 ↑ |
| ----------------- | --------- | --------- | --------- | -------- |
| CUT3R             | 0.173     | 0.494     | 0.152     | 80.2     |
| CUT3R + Reset     | 0.126     | 0.403     | 0.128     | 84.9     |
| CUT3R + EMA       | 0.164     | 0.525     | 0.150     | 80.7     |
| CUT3R + BurnIn    | 0.144     | 3.093     | 0.151     | 80.2     |
| TTT3R             | 0.106     | 0.431     | 0.131     | 86.9     |
| **TTT3R + Reset** | **0.093** | **0.375** | **0.115** | **88.5** |

### Short-sequence camera pose

원논문 Table 6. Sintel 50프레임, TUM-dynamics 90프레임, ScanNet 90프레임. Online 열은 온라인 동작 여부.

| Method     | Online | Sintel ATE ↓ | Sintel RPE rot ↓ | TUM-D ATE ↓ | TUM-D RPE rot ↓ | ScanNet ATE ↓ | ScanNet RPE rot ↓ |
| ---------- | ------ | ------------ | ---------------- | ----------- | --------------- | ------------- | ----------------- |
| DUSt3R     | ✗      | 0.417        | 5.796            | 0.083       | 3.567           | 0.081         | 0.784             |
| MASt3R     | ✗      | 0.185        | 1.496            | 0.038       | 0.448           | 0.078         | 0.475             |
| MonST3R    | ✗      | 0.111        | 0.869            | 0.098       | 0.935           | 0.077         | 0.529             |
| VGGT       | ✗      | 0.172        | 0.471            | 0.012       | 0.310           | 0.035         | 0.377             |
| Spann3R    | ✓      | 0.329        | 4.471            | 0.056       | 0.591           | 0.096         | 0.661             |
| CUT3R      | ✓      | 0.213        | 0.621            | 0.046       | 0.473           | 0.099         | 0.600             |
| Point3R    | ✓      | 0.351        | 1.822            | 0.075       | 0.642           | 0.106         | 1.946             |
| StreamVGGT | ✓      | 0.251        | 1.894            | 0.061       | 3.209           | 0.161         | 3.647             |
| **TTT3R**  | ✓      | 0.201        | 0.617            | 0.028       | 0.379           | 0.064         | 0.592             |

On short sequences TTT3R is the best overall _online_ method, but the paper states plainly that its accuracy has not matched strong offline methods such as VGGT.

### Short-sequence video depth

원논문 Table 7. Sintel 50프레임, Bonn 110프레임, KITTI 110프레임. Per-sequence scale 정렬 기준.

| Method     | Online | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ | KITTI Abs Rel ↓ | KITTI δ<1.25 ↑ |
| ---------- | ------ | ---------------- | --------------- | -------------- | ------------- | --------------- | -------------- |
| VGGT       | ✗      | 0.287            | 66.1            | 0.055          | 97.1          | 0.070           | 96.5           |
| Spann3R    | ✓      | 0.622            | 42.6            | 0.144          | 81.3          | 0.198           | 73.7           |
| CUT3R      | ✓      | 0.421            | 47.9            | 0.078          | 93.7          | 0.118           | 88.1           |
| Point3R    | ✓      | 0.452            | 48.9            | 0.060          | 96.0          | 0.136           | 84.2           |
| StreamVGGT | ✓      | 0.323            | 65.7            | 0.059          | 97.2          | 0.173           | 72.1           |
| **TTT3R**  | ✓      | 0.404            | 50.0            | 0.068          | 95.4          | **0.113**       | **90.4**       |

## 💡 Insights & Impact

### Reframing the memory problem

The core insight is diagnostic rather than architectural. Once CUT3R's update is written in TTT form, the forgetting problem stops being mysterious: softmax normalization pins the learning rate at 1.0, so historical memory is structurally unable to compete with the newest frame. Everything else follows from restoring a real learning rate.

### Training-free beats trained gating

The Table 1 ablation is the paper's strongest argument. Learnable gating modules (ScalarLR, ConditionLR, TokenLR) trained on the same data all improve over CUT3R, but none approaches TTT3R. The authors attribute this to the 64-frame training sequence ceiling imposed by their 48 GB GPU — a learned gate cannot learn behaviour it never sees. A closed-form rule derived from context sidesteps the training budget entirely.

### Honest limitations

The paper states that TTT3R **mitigates but does not resolve** state forgetting, and does not match offline VGGT in reconstruction accuracy. Fine-tuning helps pose while hurting depth. These are reported, not buried.

## 🔗 Related Work

- [CUT3R](../dynamic/cut3r.md) — the direct base model. TTT3R is a drop-in replacement for its state update rule; every experiment is framed as CUT3R + intervention.
- [Point3R](point3r.md) — the alternative answer to forgetting: explicit point-anchored memory. TTT3R notes it trades constant memory for linearly growing memory and hits OOM beyond 700 frames.
- [StreamVGGT](streamvggt.md) — KV-cache causal attention; TTT3R classifies it as O(t) state growth, efficient per step but memory-unbounded.
- [VGGT](vggt.md) — used as the offline upper bound throughout, since full attention preserves the entire history.
- [Spann3R](spann3r.md) / [MUSt3R](must3r.md) — earlier streaming-memory lineage that motivates the fixed-length state formulation.
- [Fast3R](fast3r.md) — cited as the other full-attention, all-frames-at-once design.
- [Test3R](test3r.md) — a different flavour of test-time adaptation: fine-tuning on the test sequence with a geometric consistency loss, versus TTT3R's fine-weight state update inside the forward pass.

## 📚 Key Takeaways

1. **A recurrent state is a fast weight.** Viewing the memory as something _learned at test time_ turns an architecture question into an optimization question, and the learning rate becomes the object of study.
2. **Softmax normalization is the bug.** Constant βₜ = 1.0 means every new frame overwrites history; confidence-derived per-token βₜ restores the balance.
3. **Free gains are real gains.** TTT3R needs no fine-tuning, no new parameters, and no extra compute — a rare combination in this literature.
4. **Constant memory is the differentiator.** Against Point3R's growing pointer memory and StreamVGGT's growing KV cache, TTT3R keeps CUT3R's flat footprint, which is what makes thousand-image sequences tractable at 6 GB.

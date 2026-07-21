# Distill3R: A Pipeline for Democratizing 3D Foundation Models on Commodity Hardware (arXiv preprint (2026-01))

## 📋 Overview

- **Authors**: Brandon Leblanc, Charalambos Poullis
- **Institution**: Immersive and Creative Technologies Lab, Concordia University, Montreal, Canada
- **Venue**: arXiv preprint (2026-01)
- **Links**: [Paper](https://arxiv.org/abs/2602.00865) | [Code](https://github.com/TheFourthKaramazov/Distill3R)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A knowledge-distillation pipeline that compresses a 650M-parameter Fast3R teacher into a 72M student trainable in under 3 days on a single workstation, via an offline teacher-caching pipeline and a confidence-aware distillation loss. Reports a 9× parameter reduction and a 5× inference speedup, trading fine-grained regression accuracy for superior adherence to absolute metric scale.

## 🎯 Key Contributions

1. **Distill3R distillation framework**: A framework for learned 3D reconstruction that uses an **offline cache mechanism** to make foundation-model distillation feasible on a single workstation, decoupling heavy teacher inference from the student training loop.
2. **Confidence-aware distillation loss**: Leverages the teacher's cached confidence values for both direct supervision and geometric loss weighting. Using the teacher's calibrated confidence (rather than the student's own predicted confidence) prevents degenerate collapse where the student learns to predict low confidence to attenuate the loss.
3. **Democratized research baseline**: A characterization of the model-size vs. reconstruction-fidelity trade-off, offering a stated 9× parameter reduction and 5× inference speedup as an exploratory roadmap for accessible 3D vision research.

The paper explicitly frames itself as an accessible research baseline, "not intended to compete with state-of-the-art foundation models."

## 🔧 Technical Details

### Setup: teacher and student

- **Teacher**: Fast3R (~650M parameters), adopted "due to its balance of efficiency and accuracy." For scale context, the paper notes Fast3R was trained on 128 A100 GPUs for 6.13 days, and VGGT (~1B parameters) on 64 A100 GPUs for 9 days.
- **Student**: 72M parameters, three components:
  1. **Image Encoder** — DUNE ViT-Small (21M), initialized from DUNE pretrained weights, operating on 14×14 patches with weights shared across all N views. (DINOv3 ViT-S was tried in preliminary ablations and gave significantly poorer 3D reconstruction; CroCo-B lacks a public ViT-Small variant.)
  2. **Fusion Transformer** — replaces the teacher's heavy decoder with a compressed transformer (6 layers, 6 heads, 384 embedding dim), initialized from scratch, using cross-view self-attention.
  3. **Pointmap Heads** — two lightweight DPT heads regressing dense global/local coordinates and confidence maps.

### Distilled outputs

For each image the teacher/student predict dense 2D maps at resolution H×W: a **global 3D point map** (P^g, in a single consistent global frame), a **local 3D point map** (P^ℓ, relative to the view's own camera), and **global/local confidence maps** (C^g, C^ℓ, per-pixel confidence in [0, ∞)).

### Offline teacher caching

A two-stage pipeline decouples teacher inference from training:

1. **Data unification** — a manifest generation module standardizes metadata (dataset ID, scene ID, sample ID, image dimensions, absolute paths) and processes images to the expected format.
2. **Cache generation and export** — for each sample, images are passed as a joint batch to the teacher; one forward pass produces the four supervision maps (Pt,g, Pt,ℓ, Ct,g, Ct,ℓ). Post-processing:
   - **Resolution alignment** — teacher outputs downsampled to **224 × 518** (divisible by the 14×14 DUNE patch size), avoiding on-the-fly resizing/aliasing.
   - **Supervision filtering** — a confidence threshold **τ = 0.3** on the local confidence map produces a binary validity mask M; pixels below τ are masked out of the loss.
   - **Compression** — continuous maps quantized float32 → float16, sparse validity masks compressed via Run-Length Encoding (RLE), reducing the data expansion from **7× to 4×**.
   - **Serialization and stacking** — N maps stacked along the batch dimension into a single consolidated archive to avoid file-handle limits.

### Distillation loss

Total loss (Eq. 1):

```text
L_total = L_geom_total + γ·L_conf
L_geom_total = α_g·L_g + α_ℓ·L_ℓ         (Eq. 3)
```

- **Confidence-aware geometric loss** (Eq. 2): a weighted MSE on valid pixels, where the per-pixel weight is the **cached teacher confidence** (not the student's predicted confidence), preventing degenerate collapse.
- **Scale-invariant normalization** (Eq. 4–5): global loss uses a single batch-shared scale factor s; local loss normalizes each view by its own scale factor s_k.
- **Confidence distillation loss** (Eq. 6): mean L1 between student and cached teacher confidences over the valid mask.
- **Hyperparameters**: α_g = 2.0, α_ℓ = 1.0, γ = 0.001 (confidence-loss gradients require down-weighting; global geometry requires up-weighting).

### Training configuration

- **Hardware**: single workstation, 2× NVIDIA RTX 6000 Ada (48 GB); verified to also run on a single GPU.
- **Schedule**: 60 epochs over **2.875 days** at resolution 224×518; AdamW, weight decay 0.01; cosine annealing with linear warmup over the first 3,500 steps, peaking at 1×10⁻⁴ and decaying to 5×10⁻⁵; bf16 mixed precision + FlashAttention; N = 20 views.
- **Batch**: per-GPU batch size 4 × 2 gradient-accumulation steps = effective batch size 16.
- **Cache generation**: completed on a single RTX 6000 Ada in **11.3 hours**.
- **Data**: six datasets following Fast3R (CO3D-v2, ScanNet++, Habitat, MegaDepth, BlendedMVS, ARKitScenes); a dynamic sub-sampling strategy (N = 20 contiguous frames) distills the multi-terabyte corpus to ≈450k images (150 GB).

## 📊 Results

### Inference efficiency (Table I)

Sliding-window protocol, N ∈ {12, 32, 64, 96, 128}. All methods at 378×518 except Fast3R (384×512). Time in seconds, Peak Memory in GB. OOM = Out Of Memory.

원논문 Table I.

| Method           | N12 Time ↓ | N12 Mem ↓ | N32 Time ↓ | N32 Mem ↓ | N64 Time ↓ | N64 Mem ↓ | N96 Time ↓ | N96 Mem ↓ | N128 Time ↓ | N128 Mem ↓ |
| ---------------- | ---------- | --------- | ---------- | --------- | ---------- | --------- | ---------- | --------- | ----------- | ---------- |
| Fast3R (Teacher) | 0.32       | 6.86      | 1.14       | 12.11     | 3.26       | 21.11     | 6.35       | 32.36     | 10.11       | 44.36      |
| VGGT             | 0.59       | 15.28     | 2.28       | 33.98     | 6.40       | 38.41     | OOM        | OOM       | OOM         | OOM        |
| Distill3R (Ours) | 0.13       | 4.05      | 0.41       | 9.97      | 1.02       | 21.80     | 1.78       | 28.69     | 2.69        | 31.90      |

Stated speedups: the student is "nearly 5× faster than the teacher model at N = 128 views" (Fast3R 10.11s vs Distill3R 2.69s), and "nearly 6× faster [than VGGT] by N = 64 views" (VGGT 6.40s vs Distill3R 1.02s). VGGT goes OOM at N ≥ 96.

### 3D reconstruction (Table II)

Per-view evaluation; Median Distance (Acc/Comp) scaled by 100×. Scale factor measures adherence to true metric scale (1.0 is perfect). Note: 7-Scenes ground truth is in meters, DTU in millimeters — accounting for the magnitude difference in the Scale columns.

원논문 Table II.

| Method           | 7-Scenes Acc ↓ | 7-Scenes Comp ↓ | 7-Scenes Scale ↓ | DTU Acc ↓ | DTU Comp ↓ | DTU Scale ↓ |
| ---------------- | -------------- | --------------- | ---------------- | --------- | ---------- | ----------- |
| Fast3R (Teacher) | 2.45           | 2.97            | 3.54             | 0.31      | 0.41       | 942.49      |
| Distill3R (Ours) | 8.76           | 8.88            | 1.62             | 1.16      | 1.77       | 394.59      |

The student loses on fine-grained Acc/Comp (both benchmarks) but achieves better absolute metric scale: on 7-Scenes it reaches an average scale factor of 1.62 (closely approaching the ideal 1.0), whereas the 650M teacher exhibits 3.54.

### Loss-term ablation (Table III)

Evaluated on DTU (OOD). "Geometric coordinate transfer alone (Labels-Only) is insufficient without teacher uncertainty signals."

원논문 Table III.

| Configuration                   | Acc ↓ | Comp ↓ | Scale ↓ |
| ------------------------------- | ----- | ------ | ------- |
| Labels-Only (No Weighting/Conf) | 1.37  | 2.09   | 409.05  |
| w/o Weighting w_k,ij            | 1.42  | 1.88   | 467.85  |
| Distill3R (Full)                | 1.25  | 1.54   | 380.30  |

Simulating training-from-scratch (Labels-Only, treating teacher point maps as pseudo-ground-truth) vs. the full distillation objective yields a stated **9.6% reduction in accuracy** (1.37 vs 1.25) and a **35.7% degradation in completion quality** (2.09 vs 1.54).

### Qualitative results

Qualitative comparisons on 7-Scenes (Fig. 4), CO3D-v2 objects (Fig. 5), and extended-training structural coherence (Fig. 5 referenced in text) are figure-only — 그림 4·5, 수치 미인쇄. The text notes extended training to 60 epochs improves structural coherence and surface smoothness, with a slight degradation in the completeness metric while accuracy and metric scale continue to improve.

## 💡 Insights & Impact

- **Compute divide as the target**: The work reframes the goal from marginal accuracy gains toward accessibility — enabling labs without industrial-scale clusters to train and specialize 3D models on domain-specific data.
- **Offline caching is the enabler**: Pre-computing teacher supervision turns distillation into a standard supervised-learning problem, removing online teacher inference from the training loop and making single-workstation training viable.
- **Confidence-weighting stabilizes training**: Using the teacher's fixed calibrated confidence (not the student's) as the loss weight prevents the classic degenerate collapse of uncertainty-aware regression, enabling convergence within short training cycles.
- **Metric grounding vs. precision trade-off**: The student is worse on fine-grained regression (Acc/Comp) but better on absolute metric scale, which the authors argue is more valuable for robotics tasks (reactive obstacle avoidance, local occupancy mapping) than millimetric precision.
- **Stated limitation — pose estimation**: The current student suffers rotational drift in global pose; it captures accurate translation but fails to learn rotation, because the Fast3R teacher's ICP-anchored geometry supplies frames without explicit rotation supervision. The authors point to permutation-equivariant teachers (π³) as a future direction for end-to-end pose supervision.

## 🔗 Related Work

- **[Fast3R](../reconstruction/fast3r.md)** — the teacher model distilled here (~650M params); Distill3R follows its six-dataset training mix, N=20 sampling, and learned positional embeddings.
- **[VGGT](../reconstruction/vggt.md)** — ~1B-parameter global-attention foundation model used as an efficiency comparison in Table I (goes OOM at N ≥ 96).
- **[DUSt3R](dust3r.md)** — the pairwise pointmap-regression method that started this line; its dense confidence-aware regression is the conceptual basis for the distillation objective.
- **[MASt3R](mast3r.md)** — cited within the pairwise foundation-model lineage that motivates the shift to single-pass global models.
- **[π³](../reconstruction/pi3.md)** — permutation-equivariant model cited as a promising future teacher for adding end-to-end pose supervision.

## 📚 Key Takeaways

1. **Distillation for accessibility, not SOTA**: A 72M student distilled from a 650M Fast3R teacher, trainable in under 3 days (60 epochs / 2.875 days) on a single workstation.
2. **Two core mechanisms**: an offline teacher-caching pipeline (float16 + RLE compression cutting data expansion 7× → 4×) and a confidence-aware distillation loss weighted by cached teacher confidence.
3. **Efficiency**: stated 9× parameter reduction and 5× inference speedup; nearly 5× faster than the teacher at N=128 and nearly 6× faster than VGGT at N=64 (Table I).
4. **Honest trade-off**: the student loses on fine-grained Acc/Comp (Table II) but gains superior absolute-metric-scale adherence (7-Scenes scale 1.62 vs teacher 3.54), which the paper argues suits robotics deployment.
5. **Open limitation**: rotational drift in global pose estimation, left for future permutation-equivariant teachers.

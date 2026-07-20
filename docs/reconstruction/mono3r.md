# Mono3R: Exploiting Monocular Cues for Geometric 3D Reconstruction (ACM MM 2025)

## 📋 Overview

- **Authors**: Wenyu Li, Sidun Liu, Peng Qiao, Yong Dou
- **Institution**: National University of Defence Technology
- **Venue**: ACM MM 2025
- **Links**: [Paper](https://arxiv.org/abs/2504.13419)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Injects monocular geometry priors from MoGe into DUSt3R's pairwise pipeline through a Sim(3) alignment plus a ConvGRU refinement module, recovering geometry where matching-based reconstruction fails.

## 🎯 Key Contributions

1. **Diagnosis of the matching bottleneck**: DUSt3R and its variants derive point maps from patchwise similarity matching, which implicitly assumes visible correspondences in both images. The paper shows this breaks down in occlusions, textureless areas, and repetitive or thin structures.
2. **Monocular-guided refinement module**: A two-stage design — global Sim(3) alignment to bring monocular point maps into the pairwise coordinate frame, then an iterative ConvGRU updater that refines the pairwise point map using aligned monocular point maps and features as conditioning.
3. **Complementary fusion**: Combines the robustness of monocular geometry estimation with the multi-view consistency of pairwise matching, rather than choosing one.
4. **Broad evaluation**: Five benchmarks spanning object-level (DTU), indoor (7Scenes, NRGBD), and unbounded outdoor (ETH3D, Tanks & Temples) settings, on both pose estimation and point cloud reconstruction.

## 🔧 Technical Details

### Core Innovation: Two Branches and a Refiner

```text
DUSt3R:  image pair → matching-based pairwise pointmap
Mono3R:  image pair → pairwise pointmap  +  monocular pointmap
                    → Sim(3) align → ConvGRU refinement → refined pointmap
```

### Pairwise Branch

Follows DUSt3R directly: a weight-sharing ViT encoder processes each image, a dual-way decoder of 12
stacked Transformer blocks (alternating self-attention and cross-attention) exchanges information
across views, and a DPT regression head fuses intermediate decoder features to predict point maps
`{P⁰ᵢ}` in the coordinate system of the first image, along with confidence `{w⁰ᵢ}`. The fused feature
is bilinearly upsampled to image resolution to give the pairwise feature `Fᵢ` with `C_pair = 128`.

### Monocular Branch

Uses the pre-trained MoGe backbone. The encoder is DINOv2 with patch size 14; a lightweight CNN head
extracts an affine-invariant point map `{M̂ᵢ}`. A 64-channel feature map (`C_mono = 64`) is taken from
an intermediate head layer and upsampled to image resolution. MoGe also emits a validity mask —
invalid regions such as sky are zeroed so that unreasonable coordinates do not corrupt training.
This branch is kept frozen.

### Monocular Cues Guided Refinement

**Stage 1 — Global Sim(3) alignment.** A least-squares fit over a global scale `sᴳᵢ`, shift `tᴳᵢ`, and
rotation `Rᴳᵢ` registers each monocular point map to the corresponding pairwise prediction, weighted
by the pairwise confidence `w⁰ᵢ` so that sky, extreme depths, and hard regions are down-weighted.
Solved with the Umeyama algorithm.

**Stage 2 — Iterative refinement.** The paper shows (Fig. 3) that even after Sim(3) alignment the
monocular and pairwise point maps still disagree substantially, due to prediction noise and the
domain gap between the two models. A lightweight convolutional encoder builds a condition feature
from the concatenation of the aligned monocular point map, monocular feature, pairwise feature,
confidence, and the input image. This drives a ConvGRU updater whose hidden state is initialized as
`h⁰ = tanh(F̂ᵢ)`; from each hidden state a residual offset `Δp` is decoded and added to the point map:

```text
P^(j+1) = P^(j) + Δp
```

### Training Objective

Total loss is the sum of a pairwise branch loss and a refinement loss. The refinement loss is a 3D
regression loss over all `N` iterations with exponentially increasing weights `γ^(N−v)`, `γ = 0.9`.
The pairwise loss is DUSt3R's confidence-weighted regression with the `−α log w` regularizer. Both
losses normalize predicted and ground-truth point maps by their respective scale factors.

### Implementation Details

- **Frozen / trained**: monocular branch frozen entirely; only the last two decoder blocks and the head of the pairwise branch are optimized, alongside the refinement module
- **Refinement iterations**: `N = 2` in the main experiments
- **Training data**: MegaDepth, ARKitScenes, Static Scenes 3D, BlendedMVS, ScanNet++, Co3Dv2, Waymo — a subset of DUSt3R's mix but comparable in size
- **Compute**: ~3 days on 8 V100 GPUs, trained at 224px resolution due to resource constraints
- **Testing**: fixed 224×224 resolution; test datasets are strictly disjoint from training data

## 📊 Results

Pose metrics are RRA and RTA at 5°/10°/15° thresholds and mAA30 (area under the accuracy curve at
`min(RRA, RTA)`); all are higher-is-better. Point cloud accuracy is the smallest Euclidean distance
to ground truth, completeness the smallest distance to the reconstruction; both lower-is-better.
Ten frames are randomly sampled per sequence.

### Indoor Pose Estimation — 7Scenes and NRGBD

원논문 Table 1.

| Dataset | Method     | mAA30 ↑   | RRA5 ↑    | RRA10 ↑   | RRA15 ↑   | RTA5 ↑    | RTA10 ↑   | RTA15 ↑   |
| ------- | ---------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| 7Scenes | DUSt3R     | 0.576     | 0.560     | 0.901     | 0.967     | 0.298     | 0.562     | 0.668     |
| 7Scenes | Spann3R    | 0.187     | 0.138     | 0.292     | 0.419     | 0.068     | 0.158     | 0.248     |
| 7Scenes | Fast3R     | 0.538     | 0.390     | 0.696     | 0.772     | 0.331     | 0.541     | 0.660     |
| 7Scenes | **Mono3R** | **0.728** | **0.615** | **0.921** | **0.970** | **0.544** | **0.778** | **0.866** |
| NRGBD   | DUSt3R     | 0.772     | 0.959     | 0.986     | 0.986     | 0.524     | 0.811     | 0.893     |
| NRGBD   | Spann3R    | 0.004     | 0.006     | 0.019     | 0.042     | 0.002     | 0.025     | 0.029     |
| NRGBD   | Fast3R     | 0.652     | 0.607     | 0.804     | 0.846     | 0.497     | 0.675     | 0.767     |
| NRGBD   | **Mono3R** | **0.887** | **0.964** | **0.999** | **1.000** | **0.807** | **0.945** | **0.982** |

Absolute improvement over DUSt3R on mAA30 is +0.152 on 7Scenes and +0.115 on NRGBD (원논문 Table 1의 ∆ 행).

### Indoor Point Cloud Reconstruction — 7Scenes and NRGBD

원논문 Table 1.

| Dataset | Method     | Acc-Mean ↓ | Acc-Med ↓ | Comp-Mean ↓ | Comp-Med ↓ |
| ------- | ---------- | ---------- | --------- | ----------- | ---------- |
| 7Scenes | DUSt3R     | 0.060      | 0.044     | 0.072       | 0.051      |
| 7Scenes | Spann3R    | 0.081      | 0.060     | 0.143       | 0.110      |
| 7Scenes | Fast3R     | 0.108      | 0.082     | 0.177       | 0.139      |
| 7Scenes | **Mono3R** | **0.055**  | **0.040** | **0.068**   | **0.049**  |
| NRGBD   | DUSt3R     | **0.068**  | **0.046** | 0.058       | 0.038      |
| NRGBD   | Spann3R    | 0.125      | 0.081     | 0.112       | 0.079      |
| NRGBD   | Fast3R     | 0.117      | 0.082     | 0.120       | 0.071      |
| NRGBD   | **Mono3R** | 0.069      | 0.046     | **0.056**   | **0.037**  |

### Object-Level — DTU

원논문 Table 2.

| Method     | mAA30 ↑   | RRA15 ↑   | RTA15 ↑   | Acc-Mean ↓ | Acc-Med ↓ | Comp-Mean ↓ | Comp-Med ↓ |
| ---------- | --------- | --------- | --------- | ---------- | --------- | ----------- | ---------- |
| DUSt3R     | 0.742     | 0.990     | 0.857     | 3.500      | 2.560     | 3.623       | 2.407      |
| Spann3R    | 0.469     | 0.629     | 0.560     | 4.379      | 3.078     | 4.064       | 2.723      |
| Fast3R     | 0.692     | 0.863     | 0.835     | 6.347      | 4.343     | 6.761       | 4.659      |
| **Mono3R** | **0.776** | **1.000** | **0.894** | **3.440**  | **2.559** | **3.433**   | **2.274**  |

DTU 세부 임계값 (원논문 Table 2): Mono3R의 RRA5 0.909 / RRA10 0.990, RTA5 0.522 / RTA10 0.785,
DUSt3R의 RRA5 0.902 / RRA10 0.975, RTA5 0.465 / RTA10 0.742.

### Outdoor and Unbounded — ETH3D and Tanks & Temples

원논문 Table 3·4.

| Dataset | Method     | mAA30 ↑   | RRA5 ↑    | RRA10 ↑   | RRA15 ↑   | RTA5 ↑    | RTA10 ↑   | RTA15 ↑   |
| ------- | ---------- | --------- | --------- | --------- | --------- | --------- | --------- | --------- |
| ETH3D   | DUSt3R     | **0.520** | 0.690     | 0.813     | 0.869     | **0.307** | **0.488** | **0.607** |
| ETH3D   | Spann3R    | 0.015     | 0.190     | 0.278     | 0.344     | 0.006     | 0.019     | 0.028     |
| ETH3D   | Fast3R     | 0.458     | 0.506     | 0.641     | 0.707     | 0.240     | 0.427     | 0.581     |
| ETH3D   | **Mono3R** | 0.511     | **0.800** | **0.876** | **0.911** | 0.265     | 0.462     | 0.585     |
| T&T     | DUSt3R     | 0.800     | 0.750     | 0.948     | 0.988     | 0.680     | 0.892     | 0.936     |
| T&T     | Spann3R    | 0.000     | 0.058     | 0.122     | 0.213     | 0.000     | 0.000     | 0.000     |
| T&T     | Fast3R     | 0.766     | 0.720     | 0.884     | 0.963     | 0.595     | 0.843     | 0.906     |
| T&T     | **Mono3R** | **0.859** | **0.903** | **0.979** | **0.999** | **0.779** | **0.927** | **0.963** |

ETH3D is the one benchmark where Mono3R does not win outright: the paper states it shows significant
superiority in RRA, comparable performance in RTA, and competitive overall precision.

### Ablation

원논문 Table 5, DTU 데이터셋. Variant 1은 monocular pointmap을 RGB에 채널 결합, Variant 2는
decoder 단계 feature fusion. Opt. 1은 pairwise head + refinement만, Opt. 2는 refinement만 최적화.
N은 refinement 반복 횟수. `N = 2`가 본 실험 설정과 같되 학습 pair 수만 다르다.

| Method    | mAA30 ↑   | RRA15 ↑ | RTA15 ↑   | Acc ↓     | Comp ↓    |
| --------- | --------- | ------- | --------- | --------- | --------- |
| Variant 1 | 0.580     | 0.951   | 0.682     | 4.394     | 3.713     |
| Variant 2 | 0.687     | 0.990   | 0.788     | 3.437     | 3.523     |
| N = 1     | 0.724     | 0.995   | 0.834     | 3.869     | 3.535     |
| N = 2     | 0.714     | 0.995   | 0.833     | 3.858     | 3.507     |
| N = 3     | 0.730     | 0.995   | 0.840     | **3.856** | 3.510     |
| N = 4     | **0.732** | 0.995   | **0.864** | 3.921     | **3.471** |
| Opt. 1    | 0.693     | 0.990   | 0.819     | 4.345     | 3.402     |
| Opt. 2    | 0.641     | 0.941   | 0.765     | 4.925     | 3.630     |

Both alternative fusion designs degrade performance relative to the refinement module, and both
reduced-optimization schemes degrade pose and point cloud accuracy. Increasing `N` trends upward in
mAA30, driven mainly by translation accuracy RTA15 while RRA15 stays essentially flat.

## 💡 Insights & Impact

### The Problem Being Solved

**Matching-based reconstruction fails where correspondences fail.** DUSt3R's architecture implicitly
assumes a scene point is visible in both images with distinguishable local appearance. Three regimes
break that assumption: occlusion (the point is in one view only), textureless surfaces (many
candidate matches are equally good), and repetitive or thin structures (the wrong match looks as good
as the right one). The paper's qualitative results show DUSt3R producing distorted tubular geometry
for metal pipes and false depth discontinuities across a flat door with repeated texture.

**Monocular estimation has the opposite failure mode.** It never mismatches, because it never
matches — but its per-image predictions are mutually inconsistent across a multi-view set.

### Why Refinement Rather Than Fusion at the Input

The ablation is the argument. Concatenating the monocular point map to the RGB input (Variant 1)
changes the input dimensionality, forces retraining of all downstream modules, and lands at 0.580
mAA30 — below DUSt3R's 0.742 on DTU. Injecting monocular features inside the decoder (Variant 2)
reaches 0.687, still below DUSt3R. Only the explicit align-then-iteratively-correct structure of the
refinement module exceeds the baseline. The interpretation is that monocular priors are useful as a
_correction signal on an already-consistent geometry_, not as an extra input channel for a matcher.

### Why Sim(3) Alignment Alone Is Not Enough

The paper explicitly shows (Fig. 3) that after global Sim(3) registration the monocular and pairwise
point maps still exhibit severe discrepancy. A single global similarity transform cannot absorb
per-pixel prediction noise or the domain gap between two independently trained models, which is what
motivates the iterative residual updater on top of it.

### Applications

- **Robotic navigation and SLAM**: robustness in textureless indoor corridors
- **AR systems**: reliable geometry on flat, low-texture walls and surfaces
- **Autonomous vehicle perception**: reconstruction under repetitive road and building texture
- **In-the-wild capture**: the qualitative results emphasize out-of-domain generalization

### Limitation Worth Noting

Training and all evaluation are at 224px, chosen for computational reasons. The authors state this is
sufficient to validate the approach, but the resolution ceiling means the fine-structure claims are
demonstrated at low resolution.

## 🔗 Related Work

### Building On

- **DUSt3R**: supplies the entire pairwise branch — encoder, dual-way decoder, DPT head, pre-trained weights, training data recipe, and the confidence-weighted loss.
- **MoGe**: supplies the frozen monocular branch, chosen for its demonstrated effectiveness on diverse in-the-wild data and its direct affine-invariant point map prediction.
- **ConvGRU**: the iterative update architecture for the refinement module.
- **Umeyama algorithm**: closed-form Sim(3) alignment between the two branches.

### Baselines Compared

- **Spann3R**: replaces DUSt3R's global alignment with sequential processing and a learned spatial memory; evaluated here in offline mode, which the paper notes performs better for unordered collections.
- **Fast3R**: multi-view generalization of DUSt3R processing many views in parallel.

### Related Prior-Injection Approaches

- **MonSter**: fuses monocular depth predictions into multi-view optimization to improve ill-posed regions.
- **DepthSplat**: integrates pre-trained monocular depth features into a multi-view matching pipeline for novel view synthesis.

Mono3R positions itself as carrying this idea into feed-forward point map reconstruction, where the
output is geometry rather than depth or rendered views.

## 📚 Key Takeaways

Mono3R demonstrates that:

1. **The matching assumption is DUSt3R's real limitation**: not capacity or data, but the architectural premise that correspondences exist and are distinguishable.
2. **Monocular and multi-view methods fail in disjoint ways**: one lacks robustness, the other lacks consistency, which makes them composable rather than competing.
3. **How you inject the prior decides whether it helps**: input concatenation and decoder feature fusion both underperform the DUSt3R baseline on DTU; only align-then-refine improves on it.
4. **A frozen monocular backbone plus a small trained refiner is enough**: with the monocular branch frozen and only the last two pairwise decoder blocks trained, the model improves mAA30 over DUSt3R on 7Scenes, NRGBD, DTU, and Tanks & Temples.

Mono3R is a compact argument that the next gains in feed-forward reconstruction may come less from
scaling the matcher than from supplying it with a prior that does not need to match at all.

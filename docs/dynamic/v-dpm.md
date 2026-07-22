# V-DPM: 4D Video Reconstruction with Dynamic Point Maps (CVPR 2026)

![v-dpm — architecture](https://www.robots.ox.ac.uk/~vgg/research/vdpm/resources/architecture.png)

_모델 아키텍처 (저자 project page)_

## 📋 Overview

- **Authors**: Edgar Sucar, Eldar Insafutdinov, Zihang Lai, Andrea Vedaldi
- **Institution**: Visual Geometry Group (VGG), University of Oxford
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2601.09499) | [Project Page](https://www.robots.ox.ac.uk/~vgg/research/vdpm/)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Extends Dynamic Point Maps from image pairs to video snippets by adding a time-conditioned decoder on top of a frozen-architecture VGGT backbone, recovering scene flow and 3D motion for every pixel in a single feed-forward pass.

## 🎯 Key Contributions

1. **Multi-image DPMs**: A video extension of Dynamic Point Maps that avoids the quadratic blow-up of predicting a point map per (viewpoint, time) pair.
2. **Two-phase Factorization**: The backbone predicts viewpoint-invariant but time-_variant_ point maps; added decoders then produce time-invariant point maps, decomposing the problem into two logically ordered steps.
3. **Backbone Reuse**: Because the phase-one output matches what VGGT already predicts, an existing static reconstructor can be fine-tuned rather than trained from scratch — greatly reducing the need for scarce 4D annotations.
4. **Time-conditioned Decoder**: A transformer decoder with alternating frame/global attention, conditioned on a target-time token via adaptive LayerNorm, so any target timestamp can be decoded by re-running only the decoder.
5. **State-of-the-art 4D Reconstruction**: More than halves the error of DPM, MonST3R, and St4RTrack on scene-motion benchmarks despite the backbone never having seen dynamic data before fine-tuning.

## 🔧 Technical Details

### Core Innovation: Choosing Which Point Maps to Predict

```text
Pairwise DPM:  4 point maps for 2 images, + optimisation to fuse more views
Naive video:   N³ point maps (all viewpoint × time × image combinations)
After fixing viewpoint π₀:  N² point maps — still too expensive
V-DPM:         P (N maps, time-variant) + Q (N maps at a chosen time t_j) = 2N − 1
```

The Dynamic Point Map representation `P_i(t_j, π_k)` associates a 3D point to every pixel of image
`I_i`, expressed in viewpoint `π_k` at time `t_j`. Since point maps differing only by viewpoint are
related by a rigid transform, everything can be expressed relative to `π₀`. V-DPM then predicts two
subsets in sequence:

- **P** = (P₀(t₀, π₀), P₁(t₁, π₀), …, P_{N−1}(t_{N−1}, π₀)) — viewpoint-invariant, time-variant. These are essentially what VGGT already outputs, and what MonST3R computes for pairs.
- **Q** = (P₀(t_j, π₀), P₁(t_j, π₀), …, P_{N−1}(t_j, π₀)) — the full scene reconstructed at one chosen timestamp, achieving both viewpoint and time invariance.

Scene flow for pixel u in image I₀ is the difference P₀(t₁, π₀)(u) − P₀(t₀, π₀)(u). Correspondence is
tested by checking P₀(t₀, π₀)(u) = P₁(t₀, π₀)(v).

### Architecture

- **Backbone**: VGGT. Image patch tokens, a camera token, and register tokens per frame, processed by Alternating Attention.
- **Time-variant head**: Reuses VGGT's DPT head mechanism (tokens pulled from four backbone layers) to predict **P**. The redundant depth-map prediction is removed.
- **Camera head**: VGGT's original pose regressor, used as is.
- **Target-time token**: An additional input token `t_j`, transformed by the backbone into `t̂_j`.
- **Time-conditioned decoder**: Four transformer blocks with alternating frame and global attention. Learned scale/shift are removed from LayerNorm; normalised patch tokens are modulated by linear projections of `t̂_j` (adaLN, following FiLM and DiT), and self-attention outputs are gated by a second projection.
- **Shared DPT weights**: The decoder output goes to a point-map DPT head sharing weights with the original, so the feature distribution matches the backbone output.
- Because the DPT consumes tokens from four backbone layers, the decoder is applied to each layer and the outputs concatenated.

Key efficiency property: the backbone runs once; any `P_i(t_j, π₀)` is obtained by re-running only the
decoder for a new `t̂_j`.

### Training

- Static data: ScanNet++, BlendedMVS. Dynamic data: Kubric-F, Kubric-G, PointOdyssey, Waymo — six datasets total.
- Ground-truth point maps scaled to unit mean distance to the origin, with the network predicting the correct scale as in VGGT.
- Snippets of 5, 9, 13, or 19 frames; batch size varies with snippet length (4 for 5 frames, 1 for 19 frames). The central frame is the reference view.
- Loss: DPM's confidence-calibrated loss plus camera pose regression as in VGGT. Loss is averaged _within each example first_, then across the batch — without this, densely annotated static datasets drown out the sparse 4D annotations of PointOdyssey.
- 16 GH200 GPUs for 60 epochs; AdamW, base learning rate 1.5 × 10⁻⁴ with cosine decay.

## 📊 Results

### 2-View 4D Reconstruction — EPE per Point Map

원논문 Table 1. End-Point Error on the four predicted point maps, evaluated in the world coordinate
frame defined by the first view, so the metric implicitly measures camera estimation and point
tracking accuracy. St4RTrack predicts only two of the four maps. Split by dataset for readability.

**PointOdyssey** (EPE ↓)

| Method        | Margin | P₀(t₀)    | P₀(t₁)    | P₁(t₀)    | P₁(t₁)    |
| ------------- | ------ | --------- | --------- | --------- | --------- |
| St4RTrack     | 2      | —         | 0.145     | —         | 0.150     |
| TraceAnything | 2      | 0.159     | 0.159     | 0.163     | 0.163     |
| DPM           | 2      | 0.115     | 0.114     | 0.115     | 0.117     |
| **V-DPM**     | 2      | **0.029** | **0.030** | **0.032** | **0.032** |
| St4RTrack     | 8      | —         | 0.143     | —         | 0.146     |
| TraceAnything | 8      | 0.151     | 0.156     | 0.166     | 0.165     |
| DPM           | 8      | 0.101     | 0.103     | 0.103     | 0.104     |
| **V-DPM**     | 8      | **0.029** | **0.031** | **0.032** | **0.030** |

**Kubric-F** (EPE ↓)

| Method        | Margin | P₀(t₀)    | P₀(t₁)    | P₁(t₀)    | P₁(t₁)    |
| ------------- | ------ | --------- | --------- | --------- | --------- |
| St4RTrack     | 2      | —         | 0.149     | —         | 0.045     |
| TraceAnything | 2      | 0.069     | 0.071     | 0.071     | 0.070     |
| DPM           | 2      | 0.032     | 0.033     | 0.032     | 0.032     |
| **V-DPM**     | 2      | **0.018** | **0.019** | **0.018** | **0.018** |
| St4RTrack     | 8      | —         | 0.163     | —         | 0.059     |
| TraceAnything | 8      | 0.082     | 0.115     | 0.127     | 0.091     |
| DPM           | 8      | 0.030     | 0.050     | 0.044     | 0.039     |
| **V-DPM**     | 8      | **0.017** | **0.039** | **0.033** | **0.025** |

**Kubric-G** (EPE ↓)

| Method        | Margin | P₀(t₀)    | P₀(t₁)    | P₁(t₀)    | P₁(t₁)    |
| ------------- | ------ | --------- | --------- | --------- | --------- |
| St4RTrack     | 2      | —         | 0.173     | —         | 0.091     |
| TraceAnything | 2      | 0.086     | 0.087     | 0.088     | 0.087     |
| DPM           | 2      | 0.039     | 0.040     | 0.041     | 0.040     |
| **V-DPM**     | 2      | **0.023** | **0.024** | **0.024** | **0.023** |
| St4RTrack     | 8      | —         | 0.193     | —         | 0.113     |
| TraceAnything | 8      | 0.094     | 0.139     | 0.154     | 0.130     |
| DPM           | 8      | 0.041     | 0.068     | 0.065     | 0.051     |
| **V-DPM**     | 8      | **0.022** | **0.049** | **0.045** | **0.029** |

**Waymo** (EPE ↓)

| Method        | Margin | P₀(t₀)    | P₀(t₁)    | P₁(t₀)    | P₁(t₁)    |
| ------------- | ------ | --------- | --------- | --------- | --------- |
| St4RTrack     | 2      | —         | 0.228     | —         | 0.225     |
| TraceAnything | 2      | 0.151     | 0.151     | 0.148     | 0.148     |
| DPM           | 2      | 0.085     | 0.083     | 0.082     | 0.084     |
| **V-DPM**     | 2      | **0.064** | **0.064** | **0.064** | **0.064** |
| St4RTrack     | 8      | —         | 0.232     | —         | 0.261     |
| TraceAnything | 8      | 0.188     | 0.192     | 0.235     | 0.235     |
| DPM           | 8      | 0.085     | 0.085     | 0.083     | 0.084     |
| **V-DPM**     | 8      | **0.065** | **0.067** | **0.065** | **0.064** |

The paper notes that on PointOdyssey and Kubric, V-DPM achieves ~5× lower error than St4RTrack and
TraceAnything.

### 10-Frame Dense Tracking

원논문 Table 2. EPE ↓ for dense tracks of all pixels in the first frame, snippets of 10 frames spaced
2 frames apart.

| Method        | PointOdyssey | Kubric-F  | Kubric-G  | Waymo     |
| ------------- | ------------ | --------- | --------- | --------- |
| St4RTrack     | 0.137        | 0.153     | 0.201     | 0.167     |
| TraceAnything | 0.152        | 0.107     | 0.126     | 0.119     |
| DPM           | 0.114        | 0.088     | 0.109     | 0.103     |
| **V-DPM**     | **0.032**    | **0.027** | **0.035** | **0.042** |

The paper observes that DPM's accuracy drops significantly in the video setting relative to its
2-view / 8-frame-apart numbers, since it can only predict on pairs and cannot use temporal context,
whereas V-DPM holds roughly the same error as in the 2-view experiment.

### Video Depth Estimation

원논문 Table 3. Long sequences handled by a sliding-window bundle-adjustment scheme that fuses
overlapping window predictions.

| Category  | Method          | Sintel Abs Rel ↓ | Sintel δ<1.25 ↑ | Bonn Abs Rel ↓ | Bonn δ<1.25 ↑ |
| --------- | --------------- | ---------------- | --------------- | -------------- | ------------- |
| 1-frame   | Marigold        | 0.532            | 51.5            | 0.091          | 93.1          |
| 1-frame   | DepthAnythingV2 | 0.367            | 55.4            | 0.106          | 92.1          |
| Video     | NVDS            | 0.408            | 48.3            | 0.167          | 76.6          |
| Video     | ChronoDepth     | 0.687            | 48.6            | 0.100          | 91.1          |
| Video     | DepthCrafter    | 0.292            | 69.7            | 0.075          | 97.1          |
| Video     | Robust-CVD      | 0.703            | 47.8            | —              | —             |
| Video     | CasualSAM       | 0.387            | 54.7            | 0.169          | 73.7          |
| Joint D&P | MonST3R         | 0.335            | 58.5            | 0.063          | 96.4          |
| Joint D&P | DPM             | 0.311            | 58.0            | 0.064          | 94.8          |
| Joint D&P | π³              | **0.210**        | **72.6**        | **0.043**      | **97.5**      |
| Joint D&P | V-DPM           | 0.247            | 69.4            | 0.057          | 97.3          |

V-DPM **loses to π³ on every video-depth metric**, and on Sintel δ<1.25 it is also just below
DepthCrafter (69.4 vs 69.7). The paper attributes this to scale: π³ trains on 14 public datasets plus
an internal dynamic dataset while V-DPM uses six, and π³ is a stronger backbone than VGGT.

### Camera Pose Estimation

원논문 Table 4. Following MonST3R: Average Translation Error (ATE), Relative Translation Error
(RPE trans), Relative Rotation Error (RPE rot).

| Method     | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | TUM-dyn ATE ↓ | TUM-dyn RPE trans ↓ | TUM-dyn RPE rot ↓ |
| ---------- | ------------ | ------------------ | ---------------- | ------------- | ------------------- | ----------------- |
| Robust-CVD | 0.360        | 0.154              | 3.443            | 0.189         | 0.071               | 3.681             |
| CasualSAM  | 0.141        | 0.035              | 0.615            | 0.045         | 0.020               | 0.841             |
| DUSt3R     | 0.417        | 0.250              | 5.796            | 0.127         | 0.062               | 3.099             |
| MonST3R    | 0.108        | 0.042              | 0.732            | 0.074         | 0.019               | 0.905             |
| DPM        | —            | —                  | —                | 0.056         | 0.014               | 0.836             |
| π³         | **0.074**    | **0.040**          | **0.282**        | **0.014**     | **0.009**           | **0.312**         |
| V-DPM      | 0.105        | 0.048              | 0.67             | 0.057         | 0.017               | 0.34              |

Again V-DPM is outperformed by π³ throughout. On Sintel RPE trans it is also behind CasualSAM (0.048
vs 0.035) and MonST3R (0.042); on TUM-dynamics it trails CasualSAM on ATE and RPE trans, and is
essentially tied with DPM on ATE (0.057 vs 0.056).

### Network Design Ablation

원논문 supplementary. Trained for 35 epochs, evaluated on Kubric-G with a 2-view margin of 8.

| Variant                      | P₀(t₁) ↓   | P₁(t₀) ↓   |
| ---------------------------- | ---------- | ---------- |
| **V-DPM: Original**          | **0.0500** | **0.0472** |
| V-DPM: Decoder depth 2       | 0.0518     | 0.0476     |
| V-DPM: Addition conditioning | 0.0524     | 0.0484     |
| V-DPM: DPT decoder           | 0.0538     | 0.0502     |

"Addition conditioning" adds the time token to the input tokens instead of using adaLN. "DPT decoder"
uses no extra transformer layers and instead conditions a copy of the DPT head directly through
adaLN. Both are worse than four dedicated transformer blocks with adaLN.

## 💡 Insights & Impact

### The representation is what enables cheap fine-tuning

The design's central trick is that phase-one output (**P**) is almost exactly what a pretrained static
reconstructor already produces. For static scenes P_i(π₀) and P_i(t_i, π₀) coincide, so fine-tuning
VGGT to emit time-variant point maps is a small perturbation. All the genuinely new capability —
time invariance — is pushed into decoders added on top. That is why "a modest amount of synthetic
data" suffices.

### Time-invariance as a decodable query, not an output

Because only the decoder depends on `t_j`, reconstructing the scene at every timestamp costs one
backbone pass plus N decoder passes rather than N full passes. This is what makes dense 3D tracking
over a snippet practical.

### An honest split between motion and geometry

The results divide cleanly. On _scene motion_ — the thing DPMs exist to represent — V-DPM beats every
feed-forward baseline by a large margin (roughly 3–5× lower EPE than DPM and TraceAnything). On
_static 3D and camera_ reconstruction, it is beaten by π³ across the board. The paper's own diagnosis
is training scale and backbone strength, and it explicitly notes that V-DPM could be built on π³ to
add motion reconstruction to a stronger base.

### Loss normalisation matters more than it sounds

Averaging the reconstruction loss per example before averaging across the batch prevents densely
annotated static datasets from dominating sparse 4D point tracks. Without it, the motion-specific
parts of the network receive proportionally tiny gradients.

## 🔗 Related Work

- [Dynamic Point Maps](dynamic-point-maps.md) — the direct predecessor. V-DPM is its multi-view/video successor, removing the pairwise restriction and the post-hoc optimisation needed to fuse more than two views.
- [MonST3R](monst3r.md) — computes point maps equivalent to V-DPM's time-_variant_ subset **P**, which is insufficient to recover 3D motion without a separate 2D tracker.
- [VGGT](../reconstruction/vggt.md) — the pretrained backbone; V-DPM keeps its architecture and camera head and reuses its DPT mechanism.
- [π³](../reconstruction/pi3.md) — the contemporaneous model that outperforms V-DPM on video depth and camera pose, and which the authors suggest as a future backbone.
- [Easi3R](easi3r.md), [Geo4D](geo4d.md), [CUT3R](cut3r.md) — related dynamic/4D reconstruction lines discussed as partial-dynamic approaches that recover aligned dynamic depth but not scene motion.

## 📚 Key Takeaways

1. **DPMs become far more useful on video than on pairs**, and the naive N³ / N² point-map explosion is avoidable — 2N − 1 maps suffice.
2. **Splitting viewpoint-invariance from time-invariance** lets a static reconstructor be fine-tuned instead of retrained, sidestepping the scarcity of 4D annotation.
3. **Conditioning matters**: adaLN with a dedicated four-block decoder beats both shallower decoders and simple token addition.
4. **State of the art on motion, second place on geometry.** V-DPM roughly 3–5× lowers scene-motion EPE versus DPM/St4RTrack/TraceAnything, but π³ wins every video-depth and camera-pose metric reported.
5. **Combining abundant static data with a little accurate synthetic 4D data works** — the paper's stated recipe for future 4D reconstructors.

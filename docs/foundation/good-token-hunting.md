# GoToHunt: Good Token Hunting for Visual Geometry Transformers (arXiv preprint (2026-05))

![good-token-hunting — architecture](https://arxiv.org/html/2605.23892v1/x1.png)

_We accelerate visual geometry transformers via a two-stage hierarchical token selection scheme: inter-frame selection followed by intra-frame… (원논문 Fig. 1)_

_Figure 1: A two-stage hierarchical token selection scheme (inter-frame → intra-frame) that scales near-linearly with the number of input frames and accelerates VGGT by over 85% on 500-image scenes while maintaining or improving accuracy._

## 📋 Overview

- **Authors**: Shuhong Zheng, Michael Oechsle, Erik Sandström, Marie-Julie Rakotosaona, Federico Tombari, Igor Gilitschenski
- **Institution**: University of Toronto & Vector Institute; Google; Technical University of Munich
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.23892) | [Project Page](https://zsh2000.github.io/good-token-hunting.github.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A training-free, two-stage token selection method (GoToHunt) that restricts how many key/value tokens each query attends to in the global attention layers of visual geometry transformers — cutting VGGT inference time by over 85% on 500-frame scenes while matching or improving base-model accuracy.

## 🎯 Key Contributions

1. **General problem formulation**: Casts acceleration of visual geometry transformers as constraining the number of key/value tokens each query interacts with inside the global attention layers (the O(N²L²) bottleneck, for N frames and L per-frame tokens).
2. **Hierarchical token selection**: A two-stage scheme — inter-frame selection at the frame level, then intra-frame selection to discard more redundant tokens within selected frames.
3. **Systematic exploration**: Shows diversity-based selection suits inter-frame selection, while layer-adaptive pruning (guided by global attention entropy) is critical for intra-frame selection.
4. **Training-free acceleration**: Comprehensive experiments show a superior efficiency/accuracy trade-off versus existing methods, sometimes outperforming the base models, with no retraining required.

## 🔧 Technical Details

### Problem: Quadratic Global Attention

Visual geometry transformers process N images, each patchified into L spatial tokens (plus optional special tokens), through alternating frame-wise (local) and global attention layers. The global attention layers operate over all N × L tokens and dominate cost with quadratic complexity **O(N²L²)**. GoToHunt restricts the key/value token budget each query attends to, rather than scanning the full token set across all frames.

### Stage 1 — Inter-frame Selection (Hunting for Good Frames)

- Intuitive strategies (temporal proximity, high/low co-visibility, max/mean attention pooling) all cause substantial degradation at a tight budget of **K = 25** frames (from 7-Scenes sequences of 250/500 frames).
- **Diversity-based selection**: Given place-recognition features (via MegaLoc [4]), define cosine distance d(i, j) between frames; select the K-frame subset minimizing the largest distance from any frame to its nearest selected frame — the classical NP-hard **K-center** objective, solved greedily with **farthest point sampling (FPS)**. Selected frames act as broadly-covering "anchors."

### Stage 2 — Intra-frame Selection (Preserving Necessary Tokens)

- Uniform downsampling (factor σ along height and width) across **all** global attention layers, following prior work, causes a measurable drop even at σ = 2.
- **Attention pattern analysis** (Figure 4, VGGT layers 0–23): early layers show diluted, near-uniform attention (normalized entropy Hnorm close to 1); middle and late layers show spiking attention values. (그림 4, 수치 미인쇄)
- **Layer-adaptive strategy**: two thresholds l_local and l_sample. For l < l_local, global attention is replaced with local attention (most aggressive). For l_local ≤ l < l_sample, intra-frame downsampling with a selected factor. Later high-activation layers use conservative pruning to avoid discarding highly activated tokens before scores are computed.

### Setup

- Base models: **VGGT** and **π³**. Default **K = 25**, **σ ∈ {2, 3}**, **l_local = 2**, **l_sample = 9**.
- Preliminary/pose analysis on **7-Scenes** (sample every 2 frames → 500 frames per scene, except two scenes with 250). Metrics: ATE, RPE-rot, RPE-trans.
- All experiments on a single **NVIDIA L40S GPU (48 GB)**.

## 📊 Results

### Inter-frame Strategy Comparison (7-Scenes, K = 25)

원논문 Table 1.

| Strategy               | ATE ↓      | RPE-rot ↓  | RPE-trans ↓ |
| ---------------------- | ---------- | ---------- | ----------- |
| Temporal: Nearest      | 0.7588     | 1.8485     | 0.0563      |
| Co-vis (2a) High       | 0.3813     | 2.9934     | 0.1197      |
| Co-vis (2b) Low        | 0.1840     | 2.4761     | 0.1038      |
| Attention (3a) Max     | 0.3879     | 7.2494     | 0.1257      |
| Attention (3b) Mean    | 0.3627     | 7.2988     | 0.0988      |
| Diversity-based (Ours) | **0.0676** | **0.4421** | **0.0167**  |
| VGGT (Base Model)      | 0.0698     | 0.4953     | 0.0178      |

### Layer-adaptive Intra-frame Analysis (VGGT, K = 25)

원논문 Table 3.

| σ   | Strategy   | Layers | ATE ↓  | RPE-rot ↓ | RPE-trans ↓ |
| --- | ---------- | ------ | ------ | --------- | ----------- |
| 2   | Standard   | 0-8    | 0.0676 | 0.4427    | 0.0168      |
| 2   | Standard   | 9-16   | 0.0792 | 0.9539    | 0.0239      |
| 2   | Activation | 9-16   | 0.0687 | 0.4664    | 0.0172      |
| 2   | Standard   | 17-23  | 0.0715 | 0.4463    | 0.0168      |
| 3   | Standard   | 0-8    | 0.0679 | 0.4486    | 0.0168      |
| 3   | Standard   | 9-16   | 0.1234 | 1.6722    | 0.0416      |
| 3   | Activation | 9-16   | 0.0711 | 0.9163    | 0.0207      |
| 3   | Standard   | 17-23  | 0.0743 | 0.4527    | 0.0172      |
| —   | VGGT Base  | —      | 0.0698 | 0.4953    | 0.0178      |

Downsampling aggressively hurts the middle layers (9-16), where attention spikes; the same fraction preserved via Activation recovers most of the loss — motivating the layer-adaptive design.

### Camera Pose Estimation

원논문 Table 4. Best is bold and second best is underlined, excluding the base-model rows.

| Method                  | 7S ATE ↓   | 7S RPE-rot ↓ | 7S RPE-trans ↓ | NRGBD ATE ↓ | NRGBD RPE-rot ↓ | NRGBD RPE-trans ↓ | TUM ATE ↓  | TUM RPE-rot ↓ | TUM RPE-trans ↓ |
| ----------------------- | ---------- | ------------ | -------------- | ----------- | --------------- | ----------------- | ---------- | ------------- | --------------- |
| VGGT (Base Model)       | 0.0698     | 0.4953       | 0.0178         | 0.0374      | 0.2934          | 0.0186            | 0.0118     | 0.3083        | 0.0098          |
| FastVGGT                | 0.0727     | 0.4254       | 0.0159         | 0.0377      | 0.1985          | 0.0168            | 0.0127     | 0.3154        | 0.0108          |
| SparseVGGT (SR: 50%)    | 0.0723     | 0.4608       | 0.0167         | 0.0402      | 0.2946          | 0.0202            | 0.0125     | 0.3114        | 0.0102          |
| SparseVGGT (SR: 75%)    | 0.0735     | 0.4583       | 0.0169         | 0.0462      | 0.2717          | 0.0192            | 0.0127     | 0.3120        | 0.0103          |
| Co-Me                   | 0.0870     | 0.8105       | 0.0340         | 0.0626      | 0.4567          | 0.0336            | 0.0156     | 0.3438        | 0.0146          |
| LiteVGGT                | 0.0798     | 0.6888       | 0.0238         | 0.0531      | 0.3311          | 0.0247            | 0.0145     | 0.3250        | 0.0119          |
| **GoToHunt (σ = 2)**    | **0.0673** | 0.4471       | **0.0165**     | **0.0267**  | **0.1794**      | **0.0162**        | **0.0115** | 0.3087        | 0.0101          |
| GoToHunt (σ = 3)        | 0.0677     | 0.4495       | 0.0166         | 0.0270      | 0.2409          | 0.0176            | 0.0119     | 0.3075        | 0.0102          |
| π³ (Base Model)         | 0.0573     | 0.3389       | 0.0105         | 0.0251      | 0.1031          | 0.0098            | 0.0140     | 0.3073        | 0.0088          |
| Sparse-π³ (SR: 50%)     | 0.0580     | 0.3369       | 0.0106         | 0.0313      | 0.1182          | 0.0115            | 0.0140     | 0.3068        | 0.0090          |
| Sparse-π³ (SR: 75%)     | 0.0594     | 0.3387       | 0.0108         | 0.0478      | 0.1250          | 0.0124            | 0.0141     | 0.3094        | 0.0092          |
| Speed3R                 | 0.0591     | 0.3800       | 0.0133         | 0.0391      | 0.1735          | 0.0145            | 0.0193     | 0.3152        | 0.0103          |
| **GoToHunt-π³ (σ = 2)** | 0.0579     | 0.3445       | 0.0113         | 0.0292      | 0.1190          | 0.0123            | 0.0142     | 0.3075        | 0.0089          |
| **GoToHunt-π³ (σ = 3)** | **0.0570** | 0.3428       | 0.0112         | 0.0292      | 0.1192          | 0.0123            | 0.0144     | 0.3083        | 0.0089          |

Note the honest losses: e.g., on 7-Scenes RPE-rot, FastVGGT (0.4254) beats GoToHunt σ=2 (0.4471); on the π³ family, Sparse-π³ (SR: 50%) has lower 7S RPE-rot (0.3369) than GoToHunt-π³ σ=2 (0.3445).

### Point Map Estimation (7-Scenes subset)

원논문 Table 5. 7-Scenes 부분만 발췌 (Mean/Med). Best is bold, second best underlined, excluding base rows.

| Method               | Acc Mean ↓ | Acc Med ↓  | Comp Mean ↓ | Comp Med ↓ | NC Mean ↑ | NC Med ↑ |
| -------------------- | ---------- | ---------- | ----------- | ---------- | --------- | -------- |
| VGGT (Base Model)    | 0.0171     | 0.0038     | 0.0184      | 0.0043     | 0.5568    | 0.5851   |
| FastVGGT             | 0.0166     | 0.0042     | 0.0182      | 0.0034     | 0.5554    | 0.5830   |
| SparseVGGT (SR: 50%) | 0.0172     | 0.0039     | 0.0191      | 0.0042     | 0.5563    | 0.5846   |
| SparseVGGT (SR: 75%) | 0.0174     | 0.0040     | 0.0189      | 0.0042     | 0.5561    | 0.5842   |
| Co-Me                | 0.0147     | 0.0061     | 0.0234      | 0.0060     | 0.5826    | 0.6271   |
| LiteVGGT             | 0.0185     | 0.0059     | 0.0232      | 0.0033     | 0.5542    | 0.5815   |
| GoToHunt (σ = 2)     | 0.0152     | **0.0036** | 0.0188      | 0.0043     | 0.5567    | 0.5850   |
| GoToHunt (σ = 3)     | 0.0152     | **0.0036** | 0.0189      | 0.0043     | 0.5568    | 0.5854   |

### Video Depth Estimation (Bonn, base model π³)

원논문 Table 6. Sequences range 332–895 frames. Best accelerated model in bold.

| Method               | Abs Rel ↓  | Log RMSE ↓ | RMSE ↓     | Sq Rel ↓   | δ < 1.25 ↑ |
| -------------------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| π³ (Base Model)      | 0.0333     | 0.0746     | 0.1623     | 0.0123     | 0.9886     |
| Sparse-π³ (SR: 50%)  | OOM        | OOM        | OOM        | OOM        | OOM        |
| Sparse-π³ (SR: 75%)  | OOM        | OOM        | OOM        | OOM        | OOM        |
| Speed3R              | 0.0314     | 0.0680     | 0.1525     | 0.0103     | **0.9909** |
| **GoToHunt (σ = 3)** | **0.0288** | **0.0668** | **0.1501** | **0.0100** | 0.9893     |

GoToHunt wins on Abs Rel, Log RMSE, RMSE, and Sq Rel, but loses δ < 1.25 to Speed3R (0.9893 vs 0.9909). SparseVGGT hits CUDA OOM within 48 GB even at 75% sparsity.

### Inference Time (NVIDIA L40S, K = 25, σ = 3)

원논문 Table 7. Fastest in bold, second fastest underlined.

| Method              | 100      | 200       | 300       | 400       | 500       |
| ------------------- | -------- | --------- | --------- | --------- | --------- |
| VGGT (Base Model)   | 13.6s    | 47.4s     | 101.3s    | 179.8s    | 288.0s    |
| FastVGGT            | 9.4s     | 23.1s     | 40.0s     | 59.5s     | 84.6s     |
| Sparse-π³ (SR: 50%) | 6.8s     | 18.3s     | 35.0s     | 56.2s     | 80.3s     |
| Sparse-π³ (SR: 75%) | 5.7s     | 14.0s     | 25.6s     | 39.5s     | 55.4s     |
| LiteVGGT            | **4.5s** | **10.1s** | **17.8s** | **26.0s** | **36.5s** |
| Co-Me               | 5.5s     | 16.4s     | 32.2s     | 53.3s     | 84.2s     |
| GoToHunt (Ours)     | 7.8s     | 15.9s     | 23.8s     | 31.7s     | 41.2s     |

At 500 frames, GoToHunt reduces VGGT from 288.0s to 41.2s (over 85% saved, as stated in the paper). LiteVGGT is faster (36.5s) but requires full-model retraining; GoToHunt is training-free with smaller accuracy compromise.

### Inter-frame Budget Ablation (VGGT, 7-Scenes, σ = 3, 500 frames)

원논문 Table 8. VGGT 부분 발췌.

| K                 | ATE ↓  | RPE-rot ↓ | RPE-trans ↓ | Inference Time ↓ |
| ----------------- | ------ | --------- | ----------- | ---------------- |
| VGGT (Base Model) | 0.0698 | 0.4953    | 0.0178      | 288.0s           |
| 10                | 0.0722 | 0.7614    | 0.0198      | 32.3s            |
| 25                | 0.0677 | 0.4495    | 0.0166      | 41.2s            |
| 40                | 0.0674 | 0.4204    | 0.0155      | 51.9s            |
| 60                | 0.0677 | 0.4203    | 0.0153      | 63.7s            |
| 80                | 0.0684 | 0.4211    | 0.0152      | 77.8s            |
| 100               | 0.0685 | 0.4229    | 0.0153      | 89.3s            |

Accuracy improves as K grows to ~40-60 (≈10% of frames), then is non-monotonic and converges toward the base model — a counterintuitive finding the authors leave for future study.

## 💡 Insights & Impact

- **Efficiency as token selection**: Framing acceleration purely as a key/value budget makes the method a training-free plug-in applicable across visual geometry transformer architectures (demonstrated on both VGGT and π³).
- **Diversity beats similarity**: For frame-level selection, maximizing view-space coverage (K-center via FPS) dramatically outperforms co-visibility or attention-activation heuristics under tight budgets.
- **Layers are not equal**: Early global attention layers have near-uniform (diluted) attention and can be pruned aggressively or replaced with local attention; middle/late layers with spiking attention need conservative pruning.
- **A hint about training**: Because token selection can _improve_ on base models, the authors argue current visual geometry transformers are not yet optimally trained/architected — suggesting routing-based attention and skipping early diluted global attention layers during training.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)** — the primary base model accelerated here; supplies the global attention bottleneck GoToHunt targets.
- **[π³](../reconstruction/pi3.md)** — second base model; GoToHunt-π³ is evaluated on pose, point maps, and video depth.
- **[Fast3R](../reconstruction/fast3r.md)** — scaling many views in one forward pass; related direction of making geometry transformers efficient.
- **[FastVGGT](../reconstruction/fastvggt.md)** — training-free token merging baseline compared throughout (Tables 4-7).
- **[SparseVGGT](../reconstruction/sparse-vggt.md)** — attention-based token pruning baseline (SR 50%/75%), including the Sparse-π³ variant.
- **[LiteVGGT](../reconstruction/litevggt.md)** — retraining-based efficient variant; faster but requires costly full training, used as the efficiency reference in Figure 1 and Table 7.
- **[TurboVGGT](../reconstruction/turbovggt.md)** — related VGGT acceleration line for context.
- **[DUSt3R](dust3r.md)**, **[MASt3R](mast3r.md)** — foundational feed-forward reconstruction the visual geometry transformer paradigm builds on.

## 📚 Key Takeaways

1. GoToHunt (Good Token Hunting) accelerates visual geometry transformers by restricting each query's key/value budget in global attention — a training-free, general strategy.
2. Its two stages — diversity-based inter-frame selection (K-center/FPS) and layer-adaptive intra-frame selection (entropy-guided) — together preserve or improve accuracy.
3. On 500-frame scenes it cuts VGGT inference from 288.0s to 41.2s (over 85% saved) and scales near-linearly with frame count.
4. It delivers a superior speed-accuracy trade-off versus FastVGGT, SparseVGGT, Co-Me, LiteVGGT, and Speed3R, occasionally beating the base models — though it trails LiteVGGT in raw speed and loses on isolated metrics (e.g., δ < 1.25 vs Speed3R).

# GeomUnderstanding: On Geometric Understanding and Learned Priors in Feed-forward 3D Reconstruction Models (arXiv preprint)

![geometric-understanding — architecture](https://arxiv.org/html/2512.11508v2/x25.png)

_Occlusion experiment (원논문 Fig. 4)_

## 📋 Overview

- **Authors**: Jelena Bratulić, Sudhanshu Mittal, Thomas Brox, Christian Rupprecht
- **Institution**: University of Freiburg, University of Oxford
- **Venue**: arXiv preprint (2025-12)
- **Note**: The publication venue could not be confirmed from any primary source (GitHub badge, OpenReview, CVF openaccess, or arXiv comment). This entry should be re-checked.
- **Links**: [Paper](https://arxiv.org/abs/2512.11508)
- **Verification**: UNKNOWN (2026-07-20)
- **TL;DR**: A mechanistic interpretability study of DUSt3R, VGGT, and Depth Anything 3 showing that epipolar geometry emerges in intermediate layers, is causally produced by correspondence-matching attention heads, and coexists with strong learned priors that let VGGT hallucinate occluded correspondences.

## 🎯 Key Contributions

1. **Epipolar geometry is encoded**: MLP probes recover the fundamental matrix from intermediate representations of all three models, on both synthetic and real data — despite F never being supervised.
2. **A geometric phase transition**: In camera-token architectures (VGGT, DA3) the fundamental matrix becomes recoverable around layers 12–14, coinciding with the emergence of point correspondences in attention space.
3. **Causal link established**: Attention-knockout interventions on high-correspondence heads collapse the encoded epipolar geometry, while interventions on random early or late layers do not.
4. **Architecture determines location, not mechanism**: VGGT and DA3 encode geometry in the middle layers with symmetric forward/reverse patterns; DUSt3R encodes it in early decoder blocks with asymmetric patterns from its asymmetric cross-attention decoders.
5. **Priors produce hallucination**: Under occlusion VGGT retains roughly half its matching heads for occluded patches, meaning it inpaints correspondences rather than ignoring missing evidence.

## 🔧 Technical Details

### Why the fundamental matrix

None of the three models is trained to estimate classical geometric entities. The fundamental matrix `F` (rank 2, `x₂ᵀ F x₁ = 0`) is therefore a clean proxy: probing for it avoids confounding effects from the models' direct supervision on camera pose and intrinsics. The paper evaluates F quality by Sampson error (a first-order approximation of geometric reprojection error) and by the smallest singular value, which must vanish for a valid rank-2 F.

### Dataset design

**Real-world**: DTU MVS (124 object-centric scenes, 49 fixed positions, structured-light GT, depth from MVSNet), ETH3D (high-resolution indoor/outdoor), MipNeRF360 (nine unbounded scenes, COLMAP reconstruction). For DTU and MipNeRF360, image pairs are binned by true 3D angular camera distance (15° through 120°) and sampled per bin; all ETH3D pairs are used since its scenes contain few images.

**Custom ShapeNet**: Rendered in Blender with complete geometric ground truth (camera parameters, depth, correspondences, fundamental and essential matrices). 10 categories of distinctive assets plus 5 categories of symmetric assets (bottles, vases) that introduce correspondence ambiguity. Focal lengths 24–100 mm on a 36 mm sensor. Four camera configurations: parallel-plane stereo with horizontal baseline, plus small (10–25°), medium (45–75°), and large (90–120°) angular baselines. Ambiguous scenes with repetitive objects were built for robustness tests.

### Probing setup

Two-layer MLP probes with hidden dimension 512, trained 30 epochs per layer with squared Sampson distance on ground-truth correspondences, without enforcing the rank-2 constraint. Inputs are camera tokens per layer for VGGT and DA3, and averaged features after each decoder block for DUSt3R. Probes are trained per dataset; root Sampson error is reported on unseen splits.

### Correspondence analysis setup

For each source patch token, the target patch receiving maximum query-key attention is compared against the true match; a hit is counted if any correct position receives the maximum. Evaluated over 5 ShapeNet test scenes from different categories at 50 mm focal length, averaged across sampling modes. Layers analyzed: 24 (VGGT), 8 starting at layer 9 (DA3), 12 (DUSt3R). Forward (view 1→2) and reverse (view 2→1) directions are compared.

### Intervention setup

Attention knockout zeroes QK activations for selected layer-head combinations at four locality levels: Whole head, Image map (keys set to 0), Block, and Patch (only the corresponding patches). Selection is driven by high correspondence-matching performance, with random early and late layers as baselines. Evaluated on ShapeNet at 50 mm focal length, median across sampling modes, reporting the increase in Sampson distance where F is approximated from the model's own camera pose predictions.

## 📊 Results

### Where the fundamental matrix emerges

원논문 Figure 1 presents per-layer Sampson error curves for all three models on ShapeNet, ETH3D, and DTU. These are plots with no printed values, so no numbers are reproduced here. The paper's stated findings:

- **VGGT and DA3**: F becomes recoverable roughly in the middle layers (**layers 12–14**), then refines through the final layers. The sudden improvement over a few layers indicates the necessary information forms there. For DA3, these layers correspond to those immediately after global attention is introduced.
- **DUSt3R**: F emerges in the early decoder blocks and refines throughout, with slight divergence in the last layers — which the authors speculate stems from independent target heads.
- **Rank-2 check**: The smallest singular value of predicted F attains its minimum in the same layers and is approximately **2.5e−4** smaller than the maximum value, corroborating the emergence.

### Correspondence matching in attention heads

원논문 Figure 2 gives per-head matching percentages as heatmaps. Findings:

- **VGGT**: Strong correspondence matching across multiple heads in the middle layers, roughly **layers 10 to 16**, beginning around layer 10 — that is, _preceding_ the sharp fundamental-matrix improvement at layers 13–14.
- **DA3**: Same pattern, with the strongest matching in the middle layers of the complete architecture despite layer 9 being its first global-attention layer.
- **DUSt3R**: Strong matching already in the first decoder block, improving through the middle layers — aligned with its early F recovery.
- **Symmetry**: VGGT and DA3 show symmetric forward/reverse patterns (global attention); DUSt3R is asymmetric, with the reverse direction stronger and more heads active, attributed to its asymmetric cross-attention decoders.
- **Early VGGT layers** exhibit semantic rather than geometric alignment — a chair leg in one view matches _a_ chair leg in the other, not necessarily the correct instance.

### Causal interventions

원논문 Figure 3 reports Sampson error increase as labeled bar charts across four locality levels. Because these are figure annotations rather than a table, no magnitudes are transcribed here. The paper's stated results:

- Disrupting high-matching middle-layer heads in **VGGT and DA3 degrades Sampson distance to the point of complete failure**; intervening on random early or late layers has no significant impact.
- Two intervention types are effective: multiple heads within a single layer, or fewer heads distributed across several layers. In VGGT, disabling only **four heads in a single layer** already causes substantial degradation.
- **DUSt3R** is affected by early-layer intervention instead, consistent with its early correspondence matching. Its cross-attention proves more fragile than global attention: for Whole-head and Image-map interventions, **72% of DUSt3R cases produce invalid camera pose predictions** (Figure 3 caption).
- More localized interventions preserve the trend at reduced magnitude — removing exact patch-to-patch correspondences in QK space still leaves nearby patches as sufficient signal for partial recovery.

The paper is careful to note this establishes correspondence heads as causally necessary, not that correspondence matching alone is _sufficient_ — those heads may encode additional mechanisms.

### Occlusion robustness (VGGT)

Correspondence patches with known ground truth are masked along with their 3×3 patch neighborhoods; inference runs once clean and once occluded, averaged over 40 scenes at 50 mm focal length with small (10–25°) viewpoint differences. Comparison baselines are the 8-point algorithm on SIFT and on SuperGlue matches.

원논문 Figure 4 (no printed values). Findings:

- The maximum head count is **24 layers × 16 heads = 384 heads**. Matched heads drop for occluded patches but do not collapse — approximately **50% of heads are retained**.
- VGGT shows only slight Sampson error degradation, while the multi-stage SIFT and SuperGlue baselines degrade clearly.
- The authors hypothesize this inpainting behavior originates in the mask-based iBOT loss inside DINOv2, which is trained to recover masked content.

### Scene perturbation robustness (VGGT)

Detailed quantitative results are deferred to the supplementary material. The main paper reports: VGGT is stable under moderate appearance and viewpoint changes including focal-length variation; on scenes with repetition and symmetry (identical objects in circular arrangements) classical pipelines fail to establish reliable correspondences while VGGT stays comparatively robust _when asymmetric lighting supplies disambiguating cues_; and under fully symmetric lighting and object configuration **all methods fail**, confirming the task is geometrically underconstrained.

## 💡 Insights & Impact

### These models are partly geometric, not purely statistical

The paper's core answer to its own question is "both". Epipolar structure is genuinely encoded, correspondence heads causally produce it, and the mechanism is consistent across three architecturally different models. That is a stronger claim than correlation-based interpretability usually supports, because the knockout experiments show random-layer interventions do nothing while targeted ones cause failure.

### Architecture moves the computation, not its nature

VGGT and DA3 (global attention, unified 3D space) place correspondences and geometry mid-stack; DUSt3R (asymmetric cross-attention decoders) does it early and asymmetrically. The same mechanism appears in all three — architecture only determines where and how symmetrically.

### Hallucination is the cost of robustness

The occlusion result cuts both ways. VGGT preserving epipolar geometry under occlusion where SIFT and SuperGlue degrade is a genuine advantage. But non-zero matching on occluded patches means the model is _inventing_ correspondences. As the discussion notes, it is fundamentally impossible to resolve single-view ambiguity when one image is occluded — so a hallucinated match that happens to be wrong is silently wrong, which is undesirable for reconstruction.

### Learned priors respect geometric limits

The symmetric-scene experiment is the useful control: VGGT exploits shadows and lighting that classical pipelines ignore, but fails alongside them when no disambiguating evidence exists. The priors extend the usable regime; they do not violate multi-view geometry.

### Methodological contribution

Probing for an _unsupervised_ quantity (F) rather than a supervised one (pose) is the design choice that makes the study interpretable. Combined with a synthetic dataset offering complete geometric ground truth and controlled camera configurations, it gives a template for future mechanistic work on 3D vision models.

## 🔗 Related Work

The three models analyzed, all present in this collection:

- [DUSt3R](../foundation/dust3r.md) — early-layer, asymmetric encoding; most fragile to intervention
- [VGGT](../reconstruction/vggt.md) — mid-layer encoding; the focus of the learned-priors half of the study
- [Depth Anything 3](../reconstruction/depth-anything-3.md) — mid-layer encoding, immediately after global attention is introduced

Also cited in context:

- [MASt3R](../foundation/mast3r.md) — cited as improving robustness to large viewpoint change via a dense local feature head
- [FastVGGT](../reconstruction/fastvggt.md) — cited among follow-up work accelerating inference
- [VGGT-SLAM](../reconstruction/vggt-slam.md) — cited among extensions to SLAM and real-time reconstruction

## 📚 Key Takeaways

1. **Epipolar geometry emerges without being supervised.** MLP probes recover the fundamental matrix from all three models on synthetic and real data.
2. **Correspondence heads cause it.** Attention knockout on high-matching heads collapses the geometry; random early/late layers do nothing. In VGGT, four heads in one layer suffice to break it.
3. **Layers 12–14 are the phase transition for camera-token models**, preceded by correspondence emergence around layer 10. DUSt3R does the same work early instead.
4. **DUSt3R's cross-attention is more fragile** — 72% invalid pose predictions under whole-head and image-map interventions.
5. **VGGT hallucinates under occlusion**, retaining ~50% of matching heads on masked patches, likely inherited from DINOv2's masked-recovery objective. Robust, but not honest about missing evidence.
6. **Where evidence is truly absent, learned priors do not help.** Fully symmetric scenes defeat classical and learned methods alike.

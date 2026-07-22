# UniCon3R: Unified Contact-aware 4D Human-Scene Reconstruction from Monocular Video (arXiv preprint (2026-04))

![unicon3r — architecture](https://arxiv.org/html/2604.19923v2/figure/UniCon3R_architecture_new14.png)

_Overview of UniCon3R (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Tanuj Sur, Shashank Tripathi, Nikos Athanasiou, Ha Linh Nguyen, Kai Xu, Michael J. Black, Angela Yao
- **Institution**: National University of Singapore, Max Planck Institute for Intelligent Systems, Tübingen, Germany
- **Venue**: arXiv preprint (2026-04)
- **Links**: [Paper](https://arxiv.org/abs/2604.19923)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A unified feed-forward framework for online 4D human-scene reconstruction that infers dense 4D human-scene contact and feeds it back into the human-mesh-recovery pathway as an internal corrective signal, reducing floating/penetrating bodies while preserving streaming inference speed.

## 🎯 Key Contributions

1. **Contact as an internal corrective signal**: A new design paradigm for unified feed-forward 4D human-scene reconstruction that models human-scene contact as an internal feedback signal rather than as an auxiliary prediction target.
2. **Scene-aware contact prompt**: A prompt that aggregates interaction evidence from semantic scene context (current frame + recurrent scene memory), explicit metric geometry (local pointmap neighborhood), and a temporal momentum term reusing the previous-frame contact token.
3. **Contact-guided latent refinement**: The refined contact token produces a residual update to the human latent representation before final SMPL-X regression, so predicted contact actively shapes the recovered body within the forward pass.
4. **Empirical validation**: Actively internalizing contact improves physical plausibility, global human motion, and local human mesh recovery over existing feed-forward baselines while preserving competitive streaming efficiency; incorporating contact also boosts contact-estimation accuracy.

## 🔧 Technical Details

### Motivation

Unified feed-forward methods jointly predict global human motion, dense scene geometry, and camera trajectories in a single forward pass, but joint reconstruction in a world frame does not by itself guarantee physical plausibility. Bodies may be localized in 3D yet still float above the floor, penetrate objects, or slide over supporting surfaces. Existing unified methods (Human3R, UniSH, JOSH3R) handle human-scene interaction implicitly. UniCon3R's insight is to treat contact as an explicit prompt that interacts with both the human and scene branches.

### Architecture

- Built on the prompting mechanisms of **CUT3R** (frozen 4D scene backbone with persistent latent state St) and **Human3R** (Visual Prompt Tuning that adds a human prompt Ht, with human-prior features from a frozen Multi-HMR encoder). Frozen modules are inherited; only human- and contact-related modules are trained.
- **Contact Prompt Fusion (§4.1)**: Ct = MLP(Ht ⊕ Uscene ⊕ Gt ⊕ Mt), where Uscene is a gated combination of current-frame and scene-memory cross-attention cues, Gt is a geometry token from RoIAlign over the previous-frame world-frame pointmap, and Mt is the temporal-momentum token aligned from the previous contact token.
- **Contact-Guided Latent Refinement (§4.2)**: Human and contact prompts are decoded jointly by the frozen 4D decoders; the refined contact token C̃t predicts dense per-vertex contact on the 6,890-vertex SMPL mesh and drives a residual ∆Ht = Headresidual(C̃t) that updates the human latent before SMPL-X regression.

### Training

- Losses: Ltotal = L4D + LSMPLX + λc Lcontact. L4D is inherited from CUT3R (confidence-aware pointmap + RGB loss); LSMPLX supervises the SMPL-X output; Lcontact is a focal-BCE dense vertex loss plus a DECO-style part-level loss.
- Fine-tuned on a balanced mixture of RICH and BEDLAM (2,700 sequences after excluding HDRI-panorama BEDLAM scenes). Contact supervision is applied only on RICH; contact is supervised in SMPL space following BSTRO.
- Backbone: frozen ViT-Large CUT3R encoder (token dim 1024) with two interleaved 4D decoders (embedding dim c=768, depth 12, 12 heads). Trained for 100 epochs with AdamW on 8 NVIDIA A5000 GPUs.

## 📊 Results

UniCon3R is compared primarily against feed-forward monocular 4D human-scene reconstruction methods (Human3R, UniSH, JOSH3R) plus two controlled baselines: **Human3R†** (original Human3R architecture with UniCon3R's training protocol) and **Parallel Readout** (adds contact as an auxiliary output without feeding it back into reconstruction). **Human3R\*** is the released Human3R checkpoint evaluated in the same pipeline. Bold = best within feed-forward 4D human-scene methods; underline = second-best.

### Global Human Motion — RICH

원논문 Table 1. WA-MPJPE, W-MPJPE, PA-MPJPE in mm; RTE in %. Scene = 3D scene reconstruction, Contact = dense human-scene contact prediction/use. JOSH3R and Human3R† have no PA-MPJPE reported on RICH (–).

| Method                  | Scene | Contact | WA-MPJPE ↓ | W-MPJPE ↓ | RTE (%) ↓ | PA-MPJPE ↓ |
| ----------------------- | ----- | ------- | ---------- | --------- | --------- | ---------- |
| JOSH3R                  | ✓     | ✗       | 190.4      | 334.9     | 6.3       | –          |
| UniSH                   | ✓     | ✗       | 118.1      | 183.2     | 4.8       | 50.0       |
| Human3R\*               | ✓     | ✗       | 109.9      | 184.0     | 3.3       | 48.6       |
| Human3R†                | ✓     | ✗       | 97.5       | 153.2     | 2.3       | 41.4       |
| Parallel Readout (Ours) | ✓     | ✓       | 97.9       | 153.5     | 2.3       | 41.5       |
| UniCon3R (Ours)         | ✓     | ✓       | 81.5       | 129.8     | 1.7       | 37.6       |

### Global Human Motion — EMDB-2

원논문 Table 1. Human3R† has no EMDB-2 numbers reported (–). On W-MPJPE, UniSH (270.1) is best and UniCon3R (285.6) is second-best.

| Method                  | Scene | Contact | WA-MPJPE ↓ | W-MPJPE ↓ | RTE (%) ↓ | PA-MPJPE ↓ |
| ----------------------- | ----- | ------- | ---------- | --------- | --------- | ---------- |
| JOSH3R                  | ✓     | ✗       | 220.0      | 661.7     | 13.1      | –          |
| UniSH                   | ✓     | ✗       | 118.5      | 270.1     | 5.8       | 44.4       |
| Human3R\*               | ✓     | ✗       | 118.2      | 286.1     | 2.4       | 38.7       |
| Human3R†                | ✓     | ✗       | –          | –         | –         | –          |
| Parallel Readout (Ours) | ✓     | ✓       | 160.7      | 388.3     | 3.6       | 50.9       |
| UniCon3R (Ours)         | ✓     | ✓       | 113.7      | 285.6     | 2.3       | 38.2       |

### Local Human Mesh Recovery

원논문 Table 2. SLOPER4D and 3DPW; PVE / MPJPE / Pen. Max in mm/cm as indicated. Pen. Max is not reported on 3DPW (metric assumes a reliable horizontal ground plane). On 3DPW PVE, Human3R\* (86.6) is marginally lower than UniCon3R (86.8).

| Method          | SLOPER4D PVE (mm) ↓ | SLOPER4D MPJPE (mm) ↓ | SLOPER4D Pen. Max (cm) ↓ | 3DPW PVE (mm) ↓ | 3DPW MPJPE (mm) ↓ |
| --------------- | ------------------- | --------------------- | ------------------------ | --------------- | ----------------- |
| UniSH           | 177.0               | 195.1                 | 725.4                    | 94.2            | 80.1              |
| Human3R\*       | 155.1               | 179.1                 | 219.7                    | 86.6            | 72.8              |
| UniCon3R (Ours) | 152.9               | 176.1                 | 120.3                    | 86.8            | 72.5              |

### Contact Estimation on RICH

원논문 Table 3 (left). Binary SMPL-vertex contact prediction. DECO and InteractVLM are single-frame off-the-shelf estimators. DECO achieves better Precision (0.71 vs 0.64); UniCon3R obtains the best Recall, F1, and geometric error (Geo., cm).

| Method                  | Prec. ↑ | Rec. ↑ | F1 ↑ | Geo. ↓ |
| ----------------------- | ------- | ------ | ---- | ------ |
| DECO                    | 0.71    | 0.76   | 0.70 | 17.92  |
| InteractVLM             | 0.63    | 0.63   | 0.60 | 15.70  |
| Human3R\*               | 0.07    | 0.13   | 0.08 | 76.10  |
| Parallel Readout (Ours) | 0.59    | 0.72   | 0.62 | 20.68  |
| UniCon3R (Ours)         | 0.64    | 0.80   | 0.71 | 14.98  |

### Physical Grounding on RICH

원논문 Table 3 (right). Following HuMoS with a 5 mm tolerance: Collision Ratio (Coll., %), Penetrate (Pen., cm), Float (cm), Pen. Max (P.Max, cm).

| Method                  | Coll. ↓ | Pen. ↓ | Float ↓ | P.Max ↓ |
| ----------------------- | ------- | ------ | ------- | ------- |
| UniSH                   | 7.39    | 6.01   | 37.94   | 67.87   |
| Human3R\*               | 7.40    | 6.40   | 33.56   | 216.97  |
| Parallel Readout (Ours) | 7.71    | 7.56   | 37.05   | 254.91  |
| UniCon3R (Ours)         | 5.54    | 1.59   | 5.50    | 17.54   |

### Ablation on RICH

원논문 Table 4. Progressive addition of components. WA-MPJPE, W-MPJPE, Foot Sliding in mm; Jitter in m/s³. Each row cumulatively adds the named component to the row above.

| Model Variant                  | WA-MPJPE ↓ | W-MPJPE ↓ | Foot Sliding ↓ | Jitter ↓ |
| ------------------------------ | ---------- | --------- | -------------- | -------- |
| Human3R†                       | 97.5       | 153.2     | 37.7           | 279.5    |
| Parallel Readout               | 97.9       | 153.5     | 35.3           | 262.5    |
| + Scene Context                | 89.4       | 140.6     | 35.0           | 260.1    |
| + Explicit Geometry            | 85.9       | 134.5     | 33.1           | 244.6    |
| + Temporal Momentum            | 85.3       | 135.1     | 32.0           | 231.8    |
| + Latent Refinement (UniCon3R) | 81.5       | 129.8     | 31.5           | 221.4    |

### Backbone Scaling (RICH)

원논문 Table 6. Global human motion on RICH for the lightweight ViT-S/672 vs the main-paper ViT-L/896 backbone. WA-MPJPE, W-MPJPE, PA-MPJPE in mm; RTE in %. Bold/underline are within each backbone group.

| Method          | Backbone  | WA-MPJPE ↓ | W-MPJPE ↓ | RTE (%) ↓ | PA-MPJPE ↓ |
| --------------- | --------- | ---------- | --------- | --------- | ---------- |
| Human3R\*       | ViT-S/672 | 131.5      | 207.3     | 3.3       | 71.8       |
| Human3R†        | ViT-S/672 | 113.9      | 178.3     | 2.6       | 58.3       |
| UniCon3R (Ours) | ViT-S/672 | 97.2       | 151.1     | 2.0       | 51.7       |
| Human3R\*       | ViT-L/896 | 109.9      | 184.0     | 3.3       | 48.6       |
| Human3R†        | ViT-L/896 | 97.5       | 153.2     | 2.3       | 41.4       |
| UniCon3R (Ours) | ViT-L/896 | 81.5       | 129.8     | 1.7       | 37.6       |

### Reported prose claims

- Vs Human3R\* on RICH physical grounding: Penetrate reduced by ∼75%, Float by ∼83%, Pen. Max by ∼92% (Penetrate 6.40 → 1.59 cm, Float 33.56 → 5.50 cm, Pen. Max 216.97 → 17.54 cm).
- Vs Parallel Readout on contact: F1 improved by ∼14.5%, geodesic error reduced by ∼27.5%.
- Runtime: 2.40 FPS end-to-end (vs Human3R\* 2.41 FPS) on a single NVIDIA A5000; contact prediction at 0.5 s/frame, ∼2.0× faster than DECO (1.1 s/frame) and ∼6.1× faster than InteractVLM (3.5 s/frame). Streaming inference at 2.4 fps vs 2.0 fps for UniSH.
- Test-time optimization: the optional post-hoc UniCon3R\* (JOSH-style camera refinement) further reduces WA-MPJPE100 from 81.5 mm to 72.2 mm; reference points JOSH (102.6 mm, 0.16 FPS), UniSH (118.1 mm, 2.00 FPS), Human3R† (97.5 mm, 2.41 FPS).
- ViT-S/672 variant runs at 5.64 FPS (vs 5.85 FPS for the matching Human3R backbone), ∼2.4× faster than the ViT-L/896 variant (2.40 FPS).

## 💡 Insights & Impact

- **Predicting contact is not enough**: The ablation shows contact supervision alone (Parallel Readout) even slightly worsens WA-MPJPE/W-MPJPE relative to Human3R†; the gains come from feeding contact back into the reconstruction pathway. Contact is most useful when it is corrective rather than descriptive.
- **Synergy between tasks**: Internalizing contact for reconstruction also improves contact estimation over Parallel Readout, which uses the same contact supervision — evidence the gains are architectural.
- **Honest trade-offs**: On EMDB-2 W-MPJPE, UniSH beats UniCon3R (270.1 vs 285.6), attributed to UniSH's sequence-level π³ backbone; on 3DPW PVE, Human3R\* is marginally better (86.6 vs 86.8). DECO still achieves higher contact Precision.
- **Negligible overhead**: The contact branch adds essentially no runtime cost (2.40 vs 2.41 FPS at ViT-L/896; ∼0.21 FPS at ViT-S/672), and the contact-aware design transfers across backbone scales without architecture changes.

## 🔗 Related Work

- **[Human3R](./human3r.md)**: Direct predecessor and primary baseline; UniCon3R builds on its Visual-Prompt-Tuning human prompt and inherits its frozen backbone, adding the contact prompt and latent refinement.
- **[CUT3R](./cut3r.md)**: Frozen 4D scene backbone (persistent-state continuous 3D perception) whose prompting mechanism and decoders UniCon3R reuses.
- **[DUSt3R](../foundation/dust3r.md)**: Pointmap-prediction foundation of the feed-forward reconstruction lineage that CUT3R extends.

## 📚 Key Takeaways

1. **Contact-aware unified reconstruction**: UniCon3R internalizes human-scene contact inside a feed-forward 4D pipeline via a scene-aware contact prompt and contact-guided latent refinement.
2. **Physical plausibility**: Large reductions in penetration and floating on RICH (Penetrate 6.40 → 1.59 cm, Float 33.56 → 5.50 cm, Pen. Max 216.97 → 17.54 cm vs Human3R\*).
3. **Best-in-category global motion**: Best WA-MPJPE, W-MPJPE, RTE, PA-MPJPE on RICH and best WA-MPJPE/RTE/PA-MPJPE on EMDB-2 among unified feed-forward methods.
4. **Corrective > descriptive**: Feeding contact back into the HMR pathway — not merely predicting it — drives the improvements, at negligible runtime cost and transferable across backbone scales.

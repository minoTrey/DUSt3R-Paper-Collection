# DUSt3R Paper Collection

[![GitHub Stars](https://img.shields.io/github/stars/minoTrey/DUSt3R-Paper-Collection?style=social)](https://github.com/minoTrey/DUSt3R-Paper-Collection)
[![Papers](https://img.shields.io/badge/Papers-279-green.svg)](docs/papers-list.md)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--10-orange.svg)](log.md)

> A curated survey of **279 papers** on DUSt3R and feed-forward 3D reconstruction, from
> CroCo (2022) through the verified October 2026 curation batch.

Every paper uses the same seven sections. Earlier verification sweeps and the current
batch compare reported values with source PDFs, but they do not certify every claim.
The [curation audit](candidates/README.md) states what was reviewed and what remains open.
See Verification below for the checks and their limits.

## 🌟 What this field is

[DUSt3R](docs/foundation/dust3r.md) (CVPR 2024) replaced the classical SfM + MVS pipeline
with a network that regresses 3D pointmaps from uncalibrated image pairs.
The pair network needs no input intrinsics. Multi-image reconstruction uses a separate
global-alignment optimization, and downstream localization can use matching and known focal lengths.

What followed is unusual in its speed. Two years later the descendants number in the
hundreds and the design space has visibly converged:

- **Pairwise → sequential → global.** DUSt3R aligned pairs; [Spann3R](docs/reconstruction/spann3r.md)
  and [CUT3R](docs/dynamic/cut3r.md) added memory; [VGGT](docs/reconstruction/vggt.md)
  processed all views jointly.
- **Multi-task heads → a single target.** [Depth Anything 3](docs/reconstruction/depth-anything-3.md)
  (ICLR 2026 Oral) argues a plain transformer with one depth-ray objective beats VGGT's
  specialized heads.
- **Offline → streaming.** [TTT3R](docs/reconstruction/ttt3r.md),
  [STream3R](docs/reconstruction/stream3r.md), [StreamVGGT](docs/reconstruction/streamvggt.md)
  turned reconstruction into causal inference over a frame stream.
- **Static → 4D.** [D4RT](docs/dynamic/d4rt.md) (**CVPR 2026 Best Paper**) and
  [V-DPM](docs/dynamic/v-dpm.md) extended the paradigm to deforming scenes.

## 🚀 Start here

| If you are…                  | Read                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| New to the field             | [DUSt3R](docs/foundation/dust3r.md) → [MASt3R](docs/foundation/mast3r.md) → [VGGT](docs/reconstruction/vggt.md)                            |
| Comparing current methods    | [VGGT-Ω](docs/reconstruction/vggt-omega.md), [Depth Anything 3](docs/reconstruction/depth-anything-3.md), [π³](docs/reconstruction/pi3.md) |
| Building something real-time | [Streaming & SLAM](#️-research-categories) papers below                                                                                     |
| Surveying the field          | [Surveys & Analysis](docs/surveys/) — benchmarks that compare models under one protocol                                                    |
| Browsing everything          | [Complete list](docs/papers-list.md)                                                                                                       |

## 📈 Research landscape

Venue year from each paper's current Overview, for `CONFIRMED` venue records only.
`LIKELY`, `UNKNOWN`, and arXiv submission dates are excluded. These counts reflect stored
metadata evidence, not a fresh publication audit of every paper.

<!-- GENERATED:histogram -->

```text
2022 █ 1 paper
2023 █ 1 paper
2024 ██████ 4 papers
2025 ████████████████████████████████████████████████████████████ 43 papers
2026 ████████████████████████████████████████████████████████████████ 46 papers
```

<!-- /GENERATED -->

The collection also includes preprints and unconfirmed venue claims outside this histogram.

## 🏷️ Research categories

### 🔬 [Foundation Models](docs/foundation/) (26 papers)

The lineage that established the paradigm.

| Paper                                       | Venue        | Contribution                                       |
| ------------------------------------------- | ------------ | -------------------------------------------------- |
| [CroCo](docs/foundation/croco.md)           | NeurIPS 2022 | Cross-view completion pretraining                  |
| [CroCo v2](docs/foundation/croco-v2.md)     | ICCV 2023    | Scaled pretraining to stereo and flow              |
| **[DUSt3R](docs/foundation/dust3r.md)** ⭐  | CVPR 2024    | Direct pointmap regression from uncalibrated pairs |
| [MASt3R](docs/foundation/mast3r.md)         | ECCV 2024    | Added a dense local-feature matching head          |
| [MASt3R-SfM](docs/foundation/mast3r-sfm.md) | 3DV 2025     | Full SfM pipeline on the MASt3R backbone           |

### 🏗️ [3D Reconstruction](docs/reconstruction/) (117 papers)

The main line: static scenes, scale, speed, and the backbones everything else builds on.

<details>
<summary>View by theme</summary>

- **Backbones** — [VGGT](docs/reconstruction/vggt.md) (CVPR 2025 Best Paper),
  [VGGT-Ω](docs/reconstruction/vggt-omega.md) (CVPR 2026 Oral),
  [Depth Anything 3](docs/reconstruction/depth-anything-3.md) (ICLR 2026 Oral),
  [π³](docs/reconstruction/pi3.md), [MapAnything](docs/reconstruction/mapanything.md) (3DV 2026),
  [AMB3R](docs/reconstruction/amb3r.md) (CVPR 2026 Highlight),
  [WorldMirror](docs/reconstruction/worldmirror.md) (ICML 2026)
- **Streaming / long sequences** — [TTT3R](docs/reconstruction/ttt3r.md),
  [STream3R](docs/reconstruction/stream3r.md), [StreamVGGT](docs/reconstruction/streamvggt.md),
  [Point3R](docs/reconstruction/point3r.md), [Spann3R](docs/reconstruction/spann3r.md),
  [MUSt3R](docs/reconstruction/must3r.md), [LONG3R](docs/reconstruction/long3r.md),
  [HorizonStream](docs/reconstruction/horizonstream.md), [Anchor3R](docs/reconstruction/anchor3r.md)
- **Efficiency** — [FastVGGT](docs/reconstruction/fastvggt.md),
  [LiteVGGT](docs/reconstruction/litevggt.md), [QuantVGGT](docs/reconstruction/quantvggt.md),
  [Sparse-VGGT](docs/reconstruction/sparse-vggt.md), [Co-Me](docs/reconstruction/co-me.md),
  [ZipMap](docs/reconstruction/zipmap.md), [Speed3R](docs/reconstruction/speed3r.md)
- **Scale** — [Scal3R](docs/reconstruction/scal3r.md) (CVPR 2026 Highlight),
  [MERG3R](docs/reconstruction/merg3r.md), [VGG-T3](docs/reconstruction/vgg-t3.md),
  [SAIL-Recon](docs/reconstruction/sail-recon.md) (3DV 2026 Oral),
  [VGGT-Long](docs/reconstruction/vggt-long.md), [S-MUSt3R](docs/reconstruction/s-must3r.md)
- **SLAM** — [MASt3R-SLAM](docs/reconstruction/mast3r-slam.md),
  [VGGT-SLAM](docs/reconstruction/vggt-slam.md), [SLAM3R](docs/reconstruction/slam3r.md),
  [SLAM-Former](docs/reconstruction/slam-former.md) (ECCV 2026),
  [SING3R-SLAM](docs/reconstruction/sing3r-slam.md)
- **Monocular geometry** — [MoGe](docs/reconstruction/moge.md),
  [MoGe-2](docs/reconstruction/moge-2.md), [Mono3R](docs/reconstruction/mono3r.md)
- **Conditioning & adaptation** — [Pow3R](docs/reconstruction/pow3r.md),
  [G-CUT3R](docs/reconstruction/g-cut3r.md), [LoRA3D](docs/reconstruction/lora3d.md),
  [Test3R](docs/reconstruction/test3r.md), [Fin3R](docs/reconstruction/fin3r.md)

</details>

### 🎬 [Dynamic Scenes](docs/dynamic/) (43 papers)

Reconstruction when the scene itself moves.

<details>
<summary>View by theme</summary>

- **4D pointmaps** — [D4RT](docs/dynamic/d4rt.md) (**CVPR 2026 Best Paper**),
  [V-DPM](docs/dynamic/v-dpm.md), [Dynamic Point Maps](docs/dynamic/dynamic-point-maps.md),
  [Any4D](docs/dynamic/any4d.md), [PAGE-4D](docs/dynamic/page-4d.md)
- **Video depth & pose** — [MonST3R](docs/dynamic/monst3r.md), [CUT3R](docs/dynamic/cut3r.md),
  [Easi3R](docs/dynamic/easi3r.md), [Geo4D](docs/dynamic/geo4d.md), [C4D](docs/dynamic/c4d.md),
  [VGGT4D](docs/dynamic/vggt4d.md)
- **Humans** — [Human3R](docs/dynamic/human3r.md), [ODHSR](docs/dynamic/odhsr.md)
- **Driving** — [DGGT](docs/dynamic/dggt.md), [DynamicVGGT](docs/dynamic/dynamicvggt.md)

</details>

### ✨ [Gaussian Splatting](docs/gaussian-splatting/) (38 papers)

Feed-forward models that emit 3D Gaussians instead of, or alongside, pointmaps.
[Splatt3R](docs/gaussian-splatting/splatt3r.md), [YoNoSplat](docs/gaussian-splatting/yonosplat.md),
[TokenSplat](docs/gaussian-splatting/tokensplat.md), [ARTDECO](docs/gaussian-splatting/artdeco.md),
[InstantSplat](docs/gaussian-splatting/instantsplat.md), [PreF3R](docs/gaussian-splatting/pref3r.md).

### 🧠 [Scene Understanding](docs/understanding/) (17 papers)

Geometry plus semantics in one pass. [IGGT](docs/understanding/iggt.md),
[PanSt3R](docs/understanding/panst3r.md), [EPS3D](docs/understanding/eps3d.md),
[SegVGGT](docs/understanding/segvggt.md), [FF3R](docs/understanding/ff3r.md),
[HAMSt3R](docs/understanding/hamst3r.md), [LargeSpatialModel](docs/understanding/largespatialmodel.md).

### 🔍 [Scene Reasoning](docs/reasoning/) (4 papers)

Inferring geometry that was never observed — amodal and occluded structure.
[Amodal3R](docs/reasoning/amodal3r.md), [NOVA3R](docs/reasoning/nova3r.md),
[LaRI](docs/reasoning/lari.md), [RaySt3R](docs/reasoning/rayst3r.md).

### 🤖 [Robotics](docs/robotics/) (16 papers)

Calibration, odometry, and manipulation built on 3D foundation models.
[Rig3R](docs/robotics/rig3r.md), [Calib3R](docs/robotics/calib3r.md),
[MASt3R-Fusion](docs/robotics/mast3r-fusion.md), [ViPE](docs/robotics/vipe.md),
[FVO](docs/robotics/fvo.md), [GraphSeg](docs/robotics/graphseg.md).

### 📚 [Surveys & Analysis](docs/surveys/) (7 papers)

Benchmarks and analyses that evaluate many models under one protocol, rather than
proposing another. [E3D-Bench](docs/surveys/e3d-bench.md),
[CARVE](docs/surveys/carve.md),
[Geometric Understanding](docs/surveys/geometric-understanding.md),
[Survey: DUSt3R→VGGT](docs/surveys/survey-dust3r-to-vggt.md).

### 📍 [Pose Estimation](docs/pose/) (10 papers) · 🏥 [Medical](docs/medical/) (1 paper)

[Reloc3r](docs/pose/reloc3r.md), [Pos3R](docs/pose/pos3r.md), [Endo3R](docs/medical/endo3r.md).

## 📊 On cross-paper comparison

**This README deliberately contains no leaderboard.**

That is not an oversight. An earlier version of this file carried a headline table
comparing DUSt3R, MASt3R, VGGT and π³ on "DTU Accuracy / Completeness / F-Score". Every
row was wrong: the values came from a different benchmark under different metrics, the
column headers were invented, and one model appeared to lose a comparison it actually
wins. The table looked authoritative and was reproduced across several paper documents
before verification caught it.

The underlying problem is real and not specific to this repo. These papers evaluate on
overlapping but non-identical protocols — with or without ground-truth cameras, aligned
or metric scale, per-scene or averaged — and a number lifted out of its table loses the
qualifiers that make it meaningful.

So: **per-paper tables live in each paper's document, cited to the source table.** For
comparisons across models under a single protocol, use the
[benchmark papers](docs/surveys/) instead, which is what they exist for.

## ✅ Verification

Metadata and results in this collection are checked by scripts in [`tools/`](tools/):

| Check                     | What it does                                                                |
| ------------------------- | --------------------------------------------------------------------------- |
| `verify_metadata.py`      | Venue, authors, arXiv ID against arXiv + DBLP + Semantic Scholar + Crossref |
| `verify_benchmarks.py`    | Every decimal in every table against the source paper's PDF text            |
| `verify_index_numbers.py` | Every number in this README traced back to a paper document                 |
| `check_structure.py`      | Seven-section structure and Overview field schema                           |
| `update_stats.py`         | Counts, badges, and the histogram above — all generated, never hand-edited  |

Each paper's Overview carries a `Verification` field:

- **CONFIRMED** — venue proven by DBLP, a publisher DOI, OpenReview, CVF openaccess, or an
  author-maintained badge
- **LIKELY** — an author claim exists but no independent corroboration
- **PREPRINT** — stored metadata checks found no publication record; indexing delays remain possible
- **UNKNOWN** — publication venue remains unverified, even if the arXiv paper is available.
  The venue says `arXiv preprint`, and the Verification field or a Note states what is missing.

### What verification does not cover

Stated plainly, because a checkmark that overstates itself is worse than none:

- **Benchmark verification does not run in CI.** Source PDFs are gitignored, so it is a
  local gate. CI checks structure, counts, links, and formatting only.
- **Default benchmark checks extract decimals.** `--int` also checks selected integer
  tokens, but cannot establish that the labels, units, or protocols are correct.
  A matching value elsewhere in the PDF can still conceal a wrong table.
- **Coverage is aggregate.** A paper can score above threshold while containing one wholly
  fabricated table. Seven papers were caught this way, after passing an earlier sweep.
- **Prose is weaker than tables.** Derived claims in body text get less scrutiny than the
  tables they cite.

[`log.md`](log.md) records what was found and fixed, including the failure modes above.

## 🤝 Contributing

New papers are welcome. The bar is source-traceability, not volume:

1. Copy [`docs/paper-template.md`](docs/paper-template.md) into the right category.
2. Put the arXiv URL in `Links`. Run `python3 tools/verify_metadata.py --only <slug> --out raw/metadata_<slug>.json`.
   Keep the source verdict. If it is `PREPRINT?` because a source failed, use `UNKNOWN`
   in the document and state the missing evidence. Do not infer a conference from a title.
3. Write the body. **Every number must exist in the source paper.** If the paper reports a
   result only as a plot, say so rather than reading values off the figure.
4. Run `python3 tools/build_papers_list.py`, `python3 tools/update_stats.py`, and
   `python3 tools/build_fact_cards.py`. Reconcile candidate status with
   `python3 tools/reconcile_candidates.py --write`.
5. Format Markdown, run `python3 tools/verify_all.py` (offline checks by default), and
   validate changed numerical tables with `verify_benchmarks.py --only <slugs> --int`.
   Read the source tables as well: matching numeric tokens cannot verify their labels.
6. Add the scope, source versions, results, and remaining limitations to `log.md`.

Corrections to existing papers are especially welcome — if you find a number that does not
match its source, that is a bug worth filing.

## 📄 Citation

```bibtex
@misc{dust3r_paper_collection,
  title  = {DUSt3R Paper Collection: A Verified Survey of Feed-Forward 3D Reconstruction},
  author = {minoTrey},
  year   = {2026},
  url    = {https://github.com/minoTrey/DUSt3R-Paper-Collection}
}
```

Please cite the individual papers, not this collection, for any result you use.

## 🙏 Acknowledgments

To the authors of all 279 papers, and to NAVER LABS Europe for DUSt3R and MASt3R, which
started this.

License status needs maintainer confirmation: this repository's earlier README referred
to MIT, but no `LICENSE` file is tracked, while `package.json` declares ISC.
This curation does not choose or change license terms. Paper content belongs to its respective authors.

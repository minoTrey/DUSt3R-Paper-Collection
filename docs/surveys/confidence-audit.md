# A Calibration Audit of Confidence in Feed-Forward 3D Reconstruction Models (arXiv 2026)

## 📋 Overview

- **Authors**: Nanxing Nick Deng, Qing Cheng, Niclas Zeller, Daniel Cremers
- **Institution**: Technical University of Munich, Munich Center for Machine Learning, Karlsruhe University of Applied Sciences
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.29705)
- **Verification**: UNKNOWN (2026-10-15; source 2608.29705v3 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Audit confidence's ability to rank FF3D errors separately from its ability to represent error magnitude; well-ranked uncertainty can remain overconfident.

## 🎯 Key Contributions

1. **Four-Property Audit**: Separate ranking, overall magnitude, confidence-bin slopes and probability coverage.
2. **Released-Model Comparison**: Apply shared audit definitions across backbones/datasets.
3. **Rank-Preserving Calibration**: Compare two-constant power laws with single-scale and binwise calibration.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Released FF3D pointmaps/confidence and evaluation GT geometry.
- **Output**: Uncertainty ranking, magnitude, slope and coverage diagnostics, plus optional calibration constants.
- **Problem**: Confidence is optimized as a training-loss weight; calibrated probabilistic error magnitude is a separate hypothesis to test.

### Method

1. Read native uncertainty through the confidence-to-uncertainty relationship implied by the loss.
2. Bin pixels by confidence and compare geometry-error ranking, magnitude and slope.
3. Separate nominal from actual probability coverage and test scene-level transfer.
4. Fit two power-law constants on calibration scenes and test disjoint scenes, retaining a monotonic rank-preserving transform.

Source §3–6 surveys 7 backbones, 13 datasets and 168 settings. Post-hoc calibration requires labeled calibration splits and does not retrain the model.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.29705v3), Table 2, PDF p.7.

Medians of metrics after per-setting calibration/test scene splits. Level/slope target 1; nominal coverage 0.90. In-band measures held-out scenes with near-nominal coverage. Row differences are not single-scene gains.

| Correction               | Overall Level (target 1) | Slope (target 1) | Coverage (target 0.90) | In-Band ↑ |
| ------------------------ | ------------------------ | ---------------- | ---------------------- | --------- |
| Native                   | 2.41                     | 0.65             | 0.570                  | 0.000     |
| One scalar per model     | 1.41                     | 0.65             | 0.917                  | 0.133     |
| Power law, two constants | 1.11                     | 0.99             | 0.905                  | 0.333     |

Power laws improve overall magnitude/slopes, but not every held-out scene's coverage. They do not improve rankings. This table uses numeric level values without the source's multiplier notation.

## 💡 Insights & Impact

Removing worst points and weighting residuals across points/scenes require different uncertainty properties. Rankings alone can conceal overconfidence in metric uncertainty.

- GT alignment, validity and loss normalization alter uncertainty/error relationships.
- Dataset-level calibration guarantees neither per-scene nor per-frame probability coverage. Do not assume the same calibration without calibration data.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md), [MASt3R](../foundation/mast3r.md), [VGGT](../reconstruction/vggt.md): audited confidence-producing models.
- [ReVar3R](../reconstruction/revar3r.md), [GeoCond](../foundation/geocond.md): alternative reliability signals.

## 📚 Key Takeaways

1. Ranking differs from error-magnitude calibration.
2. One scale cannot fix slopes across all confidence levels.
3. Check scene-specific coverage failures after calibration.

# GeoRay: Gauge-Aware Feed-Forward Satellite 3D Reconstruction in the Geodetic Frame (arXiv 2026)

## 📋 Overview

- **Authors**: Zhe Dong, Wanqing Wu, Yuzhe Sun, Haochen Jiang, Yuchen Ma, Lecheng Ren, Tianzhu Liu, Yanfeng Gu
- **Institution**: Harbin Institute of Technology, 54th Research Institute China Electronics Technology Group Corporation, State Key Laboratory of Comprehensive PNT Network and Equipment Technology, University of Manchester
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.29680)
- **Verification**: UNKNOWN (2026-10-15; source 2608.29680v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Compare features along satellite RPC rays and separate relative relief from absolute elevation datum to predict georeferenced surface heights.

## 🎯 Key Contributions

1. Adapt frozen perspective features to native RPC rays.
2. Explicitly separate the height–datum gauge.
3. Define SatGauge protocols combining absolute error, coverage and relief.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Satellite images, RPC metadata and a declared height-control budget; zero-control configurations are supported.
- **Output**: DSM heights and uncertainty in an absolute geodetic frame.
- **Problem**: Perspective-scene features and aligned metrics can conceal satellite absolute-height and sensor-bias errors.

### Method

1. Learn feature matching over RPC height hypotheses with ray-consistent adapters.
2. Separate relative relief from absolute datum for consistent vertical-origin shifts.
3. Fuse monocular/multi-view relief through calibrated inverse variances.
4. Adjust datum under the supplied control budget without taking height ranges from test references.

Train adapters and height estimation above a frozen backbone. Separate post-registration diagnostics from absolute-coordinate scores.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.29680v1), Table IV, PDF p.9.

Held-out US3D, 26 tiles, without ground control. Abs. MAE is pre-alignment m; coverage is a percentage in the absolute frame.

| Method   | Absolute MAE (m) ↓ | Coverage (%) ↑ |
| -------- | ------------------ | -------------- |
| SatMVS   | 8.16               | 90.1           |
| Sat-MVSF | 4.70               | 12.4           |
| GeoRay   | 2.99               | 91.9           |

Some foundation-model rows in Table IV use test-reference calibration and are excluded from primary rankings. PAGc is a completeness-aware diagnostic after alignment, unlike absolute MAE.

## 💡 Insights & Impact

Aligned heights differ from accurate heights in actual map coordinates. Design gauge and evaluation contracts together.

- Absolute errors increase under sensor/city transfer.
- Comparisons require disclosing RPC, control and training-statistic information.

## 🔗 Related Work

- [VGGT](../foundation/vggt.md): perspective geometry-foundation background.
- [GeoFF3D](geoff3d.md): UAV coordinate anchoring differs from satellite RPC estimation.

## 📚 Key Takeaways

1. Handle native RPC rays and absolute datum.
2. Disclose control budgets and reference leakage.
3. Read coverage alongside error.

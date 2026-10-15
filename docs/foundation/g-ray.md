# G-ray: Ray-Level Relative Geometric Position Encoding in Multi-View Vision Transformers under Camera Heterogeneity (arXiv 2026)

## 📋 Overview

- **Authors**: Shuo Zhang, Xin Su, Wei Wang, Jun Liu, Xinrui Zeng, Yongsen Chen, Chenjie Wang, Guibo Zhu, Jinqiao Wang, Bin Luo, Liangpei Zhang
- **Institution**: Wuhan University, Institute of Automation Chinese Academy of Sciences, Wuhan AI Research, Rongyun Robot
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.15018)
- **Verification**: UNKNOWN (2026-10-15; source 2609.15018v2 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Encode relative positions through camera-local ray angles instead of image coordinates, making attention consistent across mixed projections.

## 🎯 Key Contributions

1. Define ray-level rotary phases.
2. Provide an encoding compatible with RoPE, GTA and RayRoPE.
3. Evaluate external-calibration and estimated-calibration settings separately.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: RGB views with calibrated per-view ray maps; an alternative configuration estimates rays with AnyCalib.
- **Output**: Pointmaps, depth, poses or novel views from the attached model.
- **Problem**: Identical physical ray relationships produce different image-plane relative phases under different projections and FoVs.

### Method

1. Express camera-local rays in angular coordinates.
2. Construct attention rotary phases from relative ray angles.
3. Combine with existing position encodings to preserve ray relationships across projections.
4. Evaluate pinhole-trained reconstruction models on mixed projections.

The encoding adds no learned parameters; this does not make the whole model training-free. Disclose external calibration inputs.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.15018v2), Table I, PDF p.10.

Mean over ScanNet++, PandaSet and ETH3D mixed-projection 50-view settings. Both rows receive external calibration; lower point relative error is better.

| Method                       | Point relative error ↓ | Ray error (°) ↓ | Depth relative error ↓ |
| ---------------------------- | ---------------------- | --------------- | ---------------------- |
| MapAnything, calibrated rays | 0.1372                 | 2.11            | 0.1199                 |
| G-ray, calibrated rays       | 0.0744                 | 0.38            | 0.0744                 |

With AnyCalib-estimated calibration, G-ray point error is 0.1347. Do not treat uncalibrated VGGT and calibrated G-ray as identical-input comparisons.

## 💡 Insights & Impact

Use the physical ray seen by each pixel as attention's geometric reference rather than a camera-type label.

- Ray-calibration quality directly affects performance.
- Pinhole-to-mixed-camera transfer is established only within the tested scope, not for every lens or scene.

## 🔗 Related Work

- [MEOW](../reconstruction/meow.md): mixed-camera adaptation without camera labels uses different input assumptions.
- [VGGT](../reconstruction/vggt.md): background on multi-view attention.

## 📚 Key Takeaways

1. Use rays as the reference for positional encoding.
2. No added parameters does not mean training-free.
3. State calibration conditions beside results.

# XPos3R: Cross-Modal Transformer for Intraoperative 2D/3D Registration (arXiv 2026)

## 📋 Overview

- **Authors**: Shiyan Su, Ruyi Zha, Hongdong Li, Xuelian Cheng, Zongyuan Ge
- **Institution**: Monash University, Australian National University
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.10733)
- **Verification**: UNKNOWN (2026-10-15; source 2609.10733v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Connect 2D X-rays and 3D CT through asymmetric encoders/cross-attention to estimate initial registration poses without patient-specific retraining.

## 🎯 Key Contributions

1. Regress cross-modal geometry with separate image and volume encoders.
2. Train at scale with anatomy-specific synthetic data.
3. Evaluate feed-forward poses separately from optional differentiable TTO.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Intraoperative 2D X-rays and preoperative 3D CT volumes.
- **Output**: Rigid registration poses between CT and the X-ray camera.
- **Problem**: Patient-specific regression requires preparation, while cross-modal feature correspondences are difficult.

### Method

1. Tokenize X-rays with RayDINO and CT with a 3D CNN.
2. Apply one-way cross-attention from X-ray queries to CT keys/values.
3. Regress rotation and translation from pooled image-centric features.
4. Optionally refine initial poses with DiffDRR intensity optimization.

A patient-agnostic model trained on synthetic X-ray/volume pairs. Do not extrapolate these experiments to clinical validity or medical-device deployment.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.10733v1), Table 1, PDF p.9.

DeepFluoro, per-X-ray mean ± standard deviation. TRE/PE are in mm; Tintra is in seconds. Both rows use pretrained XPos3R and differ only in TTO.

| Configuration      | TRE (mm) ↓   | PE (mm) ↓    | Tintra (s) ↓ |
| ------------------ | ------------ | ------------ | ------------ |
| Feed-forward       | 24.16 ± 6.24 | 7.412 ± 3.11 | 1.52         |
| Feed-forward + TTO | 3.288 ± 8.31 | 0.448 ± 0.94 | 2.93         |

The smaller registration error includes TTO. Preserve mean and standard deviation together to expose failure tails.

## 💡 Insights & Impact

Transfer DUSt3R-inspired geometry learning from homogeneous RGB pairs to X-ray/CT registration.

- Synthetic-to-real and anatomical domain-transfer limitations remain.
- Benchmark accuracy does not directly establish clinical safety or success rates.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): conceptual geometry-regression background, not the RGB backbone used unchanged.
- [Endo3R](endo3r.md): a different medical-geometry task.

## 📚 Key Takeaways

1. Inputs are X-rays and CT, not RGB pairs.
2. Patient-specific retraining differs from test-time optimization.
3. Read TTO time together with error distributions.

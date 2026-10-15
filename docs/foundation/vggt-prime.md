# VGGT-Prime: Compute-Adaptive Mixture-of-Heads for Efficient Visual Geometry Transformers (arXiv 2026)

## 📋 Overview

- **Authors**: Abteen Arab, Guile Wu, Chengjie Huang, Dongfeng Bai
- **Institution**: Huawei Noah’s Ark Lab, University of British Columbia
- **Venue**: arXiv preprint (2026-09)
- **Links**: [Paper](https://arxiv.org/abs/2609.23733)
- **Verification**: UNKNOWN (2026-10-15; source 2609.23733v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Allocate VGGT attention heads to average pooling, approximate attention or exact attention according to input-dependent importance, rather than computing every head at equal cost.

## 🎯 Key Contributions

1. Analyze redundant head roles rather than token redundancy alone.
2. Select among three computation modes with a lightweight router.
3. Train low-cost surrogates through teacher-latent distillation.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Multiple RGB images.
- **Output**: Camera, depth and pointmap predictions of the existing VGGT family.
- **Problem**: Some global-attention heads are nearly uniform or vary little across queries, yet still compute expensive attention.

### Method

1. Relate head saliency to attention entropy and query diversity.
2. Use mean pooling for low-importance heads and pooled-query surrogates for intermediate heads.
3. Retain exact softmax attention for heads important to geometric correspondence.
4. Distill frozen-teacher latent residuals, then fine-tune with soft routing.

Router/surrogate training and fine-tuning are required; this is not training-free pruning. Separate token-merging variants from the base model.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2609.23733v1), Table 1, PDF p.7.

ScanNet 500-view point-cloud reconstruction. Lower summed Chamfer distance (CD) is better; inference time is reported in seconds for this experiment.

| Method     | CD ↓  | Time (s) ↓ |
| ---------- | ----- | ---------- |
| VGGT       | 0.442 | 90.1       |
| FastVGGT   | 0.437 | 28.4       |
| VGGT-Prime | 0.441 | 19.2       |

Runtime decreases in this setting, but CD is not lower than FastVGGT. The paper's maximum speedup does not apply to every dataset or view count.

## 💡 Insights & Impact

Adjust computation precision instead of choosing only whether to discard or retain every head.

- Routing mistakes and distillation errors can harm geometry.
- Speed depends on view count, hardware and token-merging configuration.

## 🔗 Related Work

- [VGGT](../reconstruction/vggt.md): the original backbone.
- [FastVGGT](../reconstruction/fastvggt.md): a comparison method reducing token redundancy.

## 📚 Key Takeaways

1. Choose per-head computation modes for each input.
2. This acceleration method requires training.
3. Separate maximum speed claims from specific benchmark results.

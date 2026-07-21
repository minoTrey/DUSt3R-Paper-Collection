# LGTM: Less Gaussians, Texture More — 4K Feed-Forward Textured Splatting (ICLR 2026)

## 📋 Overview

- **Authors**: Yixing Lao, Xuyang Bai, Xiaoyang Wu, Nuoyuan Yan, Zixin Luo, Tian Fang, Jean-Daniel Nahmias, Yanghai Tsin, Shiwei Li, Hengshuang Zhao
- **Institution**: HKU; Apple
- **Venue**: ICLR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.25745) | [Project Page](https://yxlao.github.io/lgtm/)
- **Verification**: LIKELY (2026-07-21)
- **TL;DR**: A feed-forward framework that predicts a compact set of geometric 2DGS primitives plus per-primitive texture maps, decoupling geometric complexity from rendering resolution to enable 4K novel view synthesis (previously intractable for feed-forward 3DGS) with far fewer primitives and no per-scene optimization.

> PDF 헤더에 "Published as a conference paper at ICLR 2026"가 명시되어 있어 venue를 ICLR 2026으로 표기.

## 🎯 Key Contributions

1. **First feed-forward textured Gaussians**: LGTM is the first feed-forward network to predict textured Gaussians, addressing both the resolution-scaling limit of pixel-aligned feed-forward 3DGS and the per-scene optimization requirement of existing textured-Gaussian methods.
2. **Dual-network geometry/appearance decoupling**: A primitive network predicts a compact set of 2DGS primitives from low-resolution inputs; a texture network predicts per-primitive color/alpha texture maps from high-resolution inputs — exploiting the natural frequency separation (low-frequency geometry vs high-frequency appearance).
3. **Broad applicability**: Works over monocular (Flash3D), posed two-view (DepthSplat), unposed two-view (NoPoSplat), and multi-view (VGGT) baselines, with or without known camera poses.

## 🔧 Technical Details

### Textured 2D Gaussian representation

- Augments each 2DGS primitive with a per-primitive color texture `T^c ∈ ℝ^{T×T×3}` and alpha texture `T^α ∈ ℝ^{T×T}`, sampled bilinearly at the ray-splat intersection. The alpha texture replaces the Gaussian falloff (`a_i(u) = o_i · T^α_i[u]`), and the color texture adds detail to the SH base color (`ĉ_i(u,d_i) = T^c_i[u] + SH(c_i,d_i)`), following BBSplat but with unbounded bilinear sampling to avoid dark-edge artifacts.

### Dual-network architecture

- **Primitive network** `f_prim`: a ViT encoder-decoder over low-resolution input `I_low` predicts an `h×w` grid of 2DGS primitives (μ, s, r, o, c) plus shared decoder features `F_prim`. Trained with **high-resolution supervision** (render/supervise at full `H×W`) so predicted scales are appropriately sized for high-res rendering.
- **Texture network** `f_texture`: processes high-resolution images via image patchification (`F_patch`) and projective mapping (`F_proj`, from projective prior textures computed by inverse rasterization `T^{c,proj}[u] = I^v[M^{-1}_{i,v}(u)]`), fused with `F_prim` to predict per-primitive textures.

### Training

- Two-stage: (1) pre-train the primitive network alone (low-res input, high-res supervision) for a robust geometric foundation; (2) jointly train both networks with the pre-trained primitive network at 0.1× learning rate; color texture zero-initialized. Both stages use MSE + LPIPS photometric losses.
- Datasets: RealEstate10K (up to 2K) and DL3DV-10K (up to 4K).

## 📊 Results

### Pilot study: high-resolution training memory (RE10K, NoPoSplat backbone)

원논문 Table 1. 같은 최종 출력 해상도에서 primitive resolution·texture size를 달리한 비교. 지표 LPIPS↓, SSIM↑, PSNR↑, Train Memory(bs=1). NoPoSplat은 2K 이상에서 학습 불가(OOM).

| Render Res | Method    | Prim Res  | Tex | LPIPS ↓ | SSIM ↑ | PSNR ↑ | Train Mem |
| ---------- | --------- | --------- | --- | ------- | ------ | ------ | --------- |
| 1024×576   | NoPoSplat | 1024×576  | –   | 0.239   | 0.716  | 23.169 | 61.85 GB  |
| 1024×576   | LGTM      | 512×288   | 2×2 | 0.213   | 0.816  | 25.606 | 20.16 GB  |
| 1024×576   | LGTM      | 256×144   | 4×4 | 0.283   | 0.762  | 24.135 | 16.26 GB  |
| 2048×1152  | NoPoSplat | 2048×1152 | –   | ✗       | ✗      | ✗      | OOM       |
| 2048×1152  | LGTM      | 512×288   | 4×4 | 0.176   | 0.810  | 25.328 | 21.39 GB  |
| 2048×1152  | LGTM      | 256×144   | 8×8 | 0.246   | 0.759  | 23.628 | 17.46 GB  |
| 4096×2304  | NoPoSplat | 4096×2304 | –   | ✗       | ✗      | ✗      | OOM       |
| 4096×2304  | LGTM      | 512×288   | 8×8 | 0.200   | 0.803  | 24.489 | 28.23 GB  |

NoPoSplat needs 61.85 GB just for 1024×576 and OOMs at 2K/4K; LGTM trains at 4K under 30 GB.

### Two-view NVS (RE10K and DL3DV)

원논문 Table 2. 각 baseline에서 3DGS·2DGS·LGTM 비교. 지표 LPIPS↓, SSIM↑, PSNR↑.

| Dataset | Baseline   | Render Res     | Variant | LPIPS ↓   | SSIM ↑    | PSNR ↑     |
| ------- | ---------- | -------------- | ------- | --------- | --------- | ---------- |
| RE10K   | NoPoSplat  | 2048×1152 (2K) | 3DGS    | 0.257     | 0.819     | 24.235     |
| RE10K   | NoPoSplat  | 2048×1152 (2K) | 2DGS    | 0.227     | 0.823     | 24.282     |
| RE10K   | NoPoSplat  | 2048×1152 (2K) | LGTM    | **0.182** | **0.856** | **25.233** |
| DL3DV   | NoPoSplat  | 4096×2304 (4K) | 3DGS    | 0.351     | 0.753     | 23.022     |
| DL3DV   | NoPoSplat  | 4096×2304 (4K) | 2DGS    | 0.322     | 0.737     | 22.198     |
| DL3DV   | NoPoSplat  | 4096×2304 (4K) | LGTM    | **0.200** | **0.803** | **24.489** |
| DL3DV   | DepthSplat | 3840×2048 (4K) | 3DGS    | 0.210     | 0.801     | 24.740     |
| DL3DV   | DepthSplat | 3840×2048 (4K) | 2DGS    | 0.198     | 0.794     | 24.715     |
| DL3DV   | DepthSplat | 3840×2048 (4K) | LGTM    | **0.170** | **0.827** | **25.508** |

LGTM consistently beats the 3DGS/2DGS variants across all resolutions and metrics, with the largest gains on LPIPS (a 23%–75% reduction).

### Single-view (Flash3D) and multi-view (VGGT) NVS on DL3DV

원논문 Table 3. 지표 LPIPS↓, SSIM↑, PSNR↑. 512×288(또는 518×280) primitives 고정.

| Baseline | Render Res     | Variant | LPIPS ↓   | SSIM ↑    | PSNR ↑     |
| -------- | -------------- | ------- | --------- | --------- | ---------- |
| Flash3D  | 4096×2304 (4K) | 3DGS    | 0.399     | 0.724     | 20.068     |
| Flash3D  | 4096×2304 (4K) | 2DGS    | 0.371     | 0.725     | 20.322     |
| Flash3D  | 4096×2304 (4K) | LGTM    | **0.219** | **0.766** | **21.778** |
| VGGT     | 2072×1120 (2K) | 3DGS    | 0.380     | 0.644     | 19.461     |
| VGGT     | 2072×1120 (2K) | 2DGS    | 0.392     | 0.641     | 19.273     |
| VGGT     | 2072×1120 (2K) | LGTM    | **0.361** | **0.661** | **19.990** |

Gains are largest for single-view (Flash3D) and smaller for multi-view VGGT, where geometry is less precise; VGGT could not be scaled to 4K due to memory.

### Inference cost (single A100, two-view)

원논문 Table 4. Peak GPU Memory, Network Fwd·Render·Total Time. ⑤ LGTM 4K vs ② NoPoSplat 512×288: 64× 픽셀 증가에 1.80× 메모리·1.47× 시간.

| Method           | Prim Res | Tex | Render Res | Peak Mem (GB) | Fwd (ms) | Render (ms) | Total (ms) |
| ---------------- | -------- | --- | ---------- | ------------- | -------- | ----------- | ---------- |
| ① NoPoSplat 3DGS | 512×288  | –   | 512×288    | 3.06          | 110.37   | 3.81        | 114.18     |
| ② NoPoSplat 2DGS | 512×288  | –   | 512×288    | 3.06          | 112.70   | 6.43        | 119.13     |
| ③ LGTM           | 512×288  | 2×2 | 1024×576   | 4.33          | 132.06   | 7.70        | 139.76     |
| ④ LGTM           | 512×288  | 4×4 | 2048×1152  | 4.60          | 136.14   | 14.26       | 150.40     |
| ⑤ LGTM           | 512×288  | 8×8 | 4096×2304  | 5.51          | 142.28   | 32.82       | 175.10     |

### Component ablation (DL3DV, 2K, 512×288 primitives)

원논문 Table 5. NoPoSplat baseline에서 컴포넌트를 점진 추가. 지표 LPIPS↓, SSIM↑, PSNR↑.

| Method                      | LPIPS ↓   | SSIM ↑    | PSNR ↑     |
| --------------------------- | --------- | --------- | ---------- |
| ① NoPoSplat (3DGS)          | 0.371     | 0.583     | 16.964     |
| ② + High-res retrain (2DGS) | 0.256     | 0.731     | 23.502     |
| ③ + Image patchify only     | 0.199     | 0.782     | 24.673     |
| ④ + Texture color           | 0.189     | 0.806     | 25.314     |
| ⑤ + Texture alpha (full)    | **0.176** | **0.810** | **25.328** |

High-resolution re-training alone lifts PSNR from 16.964 to 23.502; image patchify, texture color, and texture alpha each add further gains.

### Versus per-scene optimization (supplementary)

원논문 Table 7에 따르면 DepthSplat + LGTM은 DL3DV 4K에서 per-scene 최적화 3DGS를 능가한다: PSNR 27.99 vs 21.75, SSIM 0.88 vs 0.78, LPIPS 0.15 vs 0.21 — 즉시 재구성 대 약 30분 최적화(A100).

## 💡 Insights & Impact

- **Decoupling breaks the resolution wall**: Because Gaussian count grows quadratically with pixels, pixel-aligned feed-forward 3DGS cannot reach 4K; separating a compact primitive grid from per-primitive textures makes a 64× pixel increase cost only 1.80× memory and 1.47× time.
- **Geometry quality bounds the gain**: LGTM improves most where geometry is reliable (single-view, posed two-view) and least where it is noisier (unposed, multi-view), pinpointing geometry as the remaining bottleneck.
- **Generalization beats overfitting**: Against per-scene optimization, LGTM avoids the middle-frame quality collapse that per-scene fitting suffers, staying stable across all target views while being orders of magnitude faster.
- **Limitations**: Texture resolution is pre-defined and needs manual tuning; overall quality still depends heavily on the underlying geometry.

## 🔗 Related Work

- Applies over feed-forward 3DGS backbones NoPoSplat, DepthSplat, Flash3D, and [VGGT](../reconstruction/vggt.md) (with an AnySplat-style Gaussian head), building on pose-free pointmap inference from [DUSt3R](../foundation/dust3r.md)/[MASt3R](../foundation/mast3r.md) and multi-view methods such as MV-DUSt3R+ and [Spann3R](../reconstruction/spann3r.md).
- Extends per-primitive textured Gaussian methods (BBSplat, GsTex, Gaussian Billboards, Textured Gaussians) into a feed-forward, cross-scene setting, removing their per-scene optimization requirement.
- Uses 2D Gaussian Splatting (2DGS) as its geometric primitive.

## 📚 Key Takeaways

1. LGTM is the first feed-forward network to predict textured Gaussians, reaching 4K novel view synthesis that pixel-aligned feed-forward 3DGS cannot due to quadratic primitive growth.
2. A dual-network design (compact primitives from low-res input, per-primitive textures from high-res input) decouples geometry from rendering resolution, cutting a 64× pixel scale-up to 1.80× memory / 1.47× time.
3. Plugged into Flash3D, NoPoSplat, DepthSplat, and VGGT it consistently improves LPIPS/SSIM/PSNR, and even surpasses per-scene-optimized 3DGS at 4K while reconstructing instantly.

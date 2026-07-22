# UAVFF3D: A Geometry-Aware Benchmark for Feed-Forward UAV 3D Reconstruction (arXiv preprint 2026-05)

![uavff3d — architecture](https://arxiv.org/html/2605.17942v2/x1.png)

_Typical failure cases of feed-forward UAV reconstruction (원논문 Fig. 1)_

## 📋 Overview

- **Authors**: Xiang Yang, Yongli Wang, HaiFeng Li, Yunsheng Zhang
- **Institution**: School of Geosciences and Info-Physics, Central South University, Changsha, China
- **Venue**: arXiv preprint (2026-05)
- **Links**: [Paper](https://arxiv.org/abs/2605.17942) | [Code](https://github.com/yanxian-ll/UAVFF3D)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A geometry-aware real–synthetic benchmark (>170k real + >370k synthetic UAV images) that stresses feed-forward 3D reconstruction under UAV camera-geometry variation — oblique views and HFOV–height ambiguity — plus a shared scene-level alignment protocol that jointly evaluates camera and dense geometry.

## 🎯 Key Contributions

1. **Geometry-aware real–synthetic UAV benchmark**: Three subsets — UAVFF3D-Real (real appearance + LiDAR-supported metric evaluation), UAVFF3D-Syn (large-scale controllable synthetic data for domain adaptation), and UAVFF3D-FA (a controlled HFOV–height ambiguity diagnostic test set).
2. **Shared-alignment evaluation protocol**: One scene-level Sim(3) transform (estimated from the point cloud) is applied jointly to predicted dense points and all predicted cameras, so pose error reflects camera–scene consistency rather than an independently fitted trajectory.
3. **Systematic findings under UAV geometry**: UAV-domain adaptation with UAVFF3D consistently improves camera-geometry and dense-geometry metrics; explicit camera priors (intrinsics/poses) are complementary to adaptation.

## 🔧 Technical Details

### Dataset composition

원논문 Table 1. FA는 HFOV 25°–95° 8단계를 footprint를 유사하게 유지하며 렌더링.

| Component    | Source    | Scenes | Images |
| ------------ | --------- | ------ | ------ |
| UAVFF3D-Real | Real      | 107    | 170k   |
| UAVFF3D-Syn  | Synthetic | 291    | 370k   |
| UAVFF3D-FA   | Synthetic | 32     | 19k    |

- **Metrics** (all lower-is-better): AbsRel depth, Ray Error (∠ of predicted vs GT camera rays), Chamfer-L1 (CD, voxel 0.25 m), Pose ATE (camera-center error after shared alignment), Rotation MAE.
- **Evaluated models**: VGGT, Pi3, MapAnything, Pi3X, Depth Anything 3 (DA3, zero-shot only — training code unavailable).
- **Fine-tuning**: within the MapAnything framework; sampling mix BlendedMVS:UAVFF3D-Real:UAVFF3D-Syn:UAVScenes:WHU = 20:20:40:1:1; 2–8 views resized to 518 px; AdamW, lr 5×10⁻⁶ → 5×10⁻⁸, 2-epoch warm-up, 10 epochs on 2× RTX A6000 or 2× A100 40GB.

## 📊 Results

### Necessity of shared alignment (zero-shot VGGT)

원논문 Table 3. ATE-S는 shared alignment, ATE-I는 독립 카메라 정렬. Gap = ATE-S − ATE-I가 카메라–장면 불일치를 나타냄.

| Dataset      | CD-S ↓ | ATE-S ↓ | ATE-I ↓ | Gap ↓ |
| ------------ | ------ | ------- | ------- | ----- |
| UseGeo       | 1.61   | 8.32    | 3.36    | 4.96  |
| UrbanScene3D | 4.75   | 77.78   | 44.51   | 33.27 |
| UAVFF3D-Real | 3.38   | 89.45   | 47.21   | 42.24 |
| UAVFF3D-FA   | 1.04   | 41.62   | 1.11    | 40.52 |
| Average      | 2.70   | 54.29   | 24.05   | 30.25 |

On UAVFF3D-FA, independent alignment gives ATE-I = 1.11 while shared alignment gives ATE-S = 41.62 — the predicted trajectory fits GT in isolation but is inconsistent with the predicted geometry.

### Overall UAV reconstruction before/after fine-tuning

원논문 Table 4, 4개 UAV 테스트셋 평균. DA3는 fine-tuning 미지원(zero-shot만).

| Model       | AbsRel ↓ | Ray ↓ | CD ↓ | ATE ↓ | Rot. ↓ |
| ----------- | -------- | ----- | ---- | ----- | ------ |
| VGGT        | 0.042    | 6.23  | 2.70 | 54.29 | 11.60  |
| Pi3         | 0.036    | 8.67  | 2.86 | 60.39 | 11.41  |
| MapAnything | 0.044    | 6.00  | 2.90 | 57.50 | 13.33  |
| Pi3X        | 0.035    | 7.73  | 2.24 | 56.19 | 11.72  |
| DA3         | 0.037    | 6.58  | 2.94 | 56.21 | 14.79  |
| VGGT-FT     | 0.028    | 1.97  | 1.59 | 20.57 | 3.96   |
| Pi3-FT      | 0.026    | 1.37  | 1.77 | 14.52 | 3.07   |
| Mapa-FT     | 0.037    | 2.51  | 1.91 | 29.08 | 6.10   |
| Pi3X-FT     | 0.026    | 1.87  | 1.44 | 18.70 | 3.40   |

Best-case relative reductions: Ray Error up to 84.2% (Pi3 8.67 → 1.37), Pose ATE up to 76.0% (Pi3 60.39 → 14.52), CD up to 41.1% (VGGT 2.70 → 1.59).

### Oblique vs. nadir reconstruction

원논문 Table 6. Gap = oblique − nadir. Pi3의 rotation gap이 26.13 → 2.43으로 90.7% 감소.

| Model       | CD Oblique ↓ | CD Nadir ↓ | CD Gap ↓ | Rot Oblique ↓ | Rot Nadir ↓ | Rot Gap ↓ |
| ----------- | ------------ | ---------- | -------- | ------------- | ----------- | --------- |
| VGGT        | 5.42         | 2.02       | 3.40     | 31.89         | 6.32        | 25.57     |
| MapAnything | 6.51         | 1.79       | 4.72     | 39.02         | 5.12        | 33.90     |
| Pi3         | 5.80         | 2.29       | 3.50     | 33.00         | 6.86        | 26.13     |
| Pi3X        | 5.60         | 1.89       | 3.71     | 35.89         | 10.11       | 25.78     |
| DA3         | 5.84         | 2.05       | 3.79     | 32.95         | 10.81       | 22.14     |
| VGGT-FT     | 2.86         | 1.19       | 1.68     | 7.79          | 3.07        | 4.73      |
| Pi3-FT      | 2.89         | 1.49       | 1.40     | 5.31          | 2.88        | 2.43      |
| Mapa-FT     | 3.67         | 1.23       | 2.44     | 13.06         | 3.64        | 9.43      |
| Pi3X-FT     | 2.53         | 1.10       | 1.43     | 6.29          | 2.95        | 3.35      |

### Training-data ablation

원논문 Table 5. Syn은 camera-geometry 커버리지를, Real은 appearance/trajectory 통계를 제공 — 상보적.

| Model          | AbsRel ↓ | Ray ↓ | CD ↓ | ATE ↓ | Rot. ↓ |
| -------------- | -------- | ----- | ---- | ----- | ------ |
| Pi3            | 0.036    | 8.67  | 2.86 | 60.39 | 11.41  |
| Pi3-FT-Public  | 0.032    | 5.59  | 1.81 | 46.74 | 8.76   |
| Pi3-FT-Syn     | 0.032    | 2.36  | 1.65 | 25.80 | 5.31   |
| Pi3-FT-Real    | 0.023    | 1.73  | 2.15 | 16.55 | 2.97   |
| Pi3-FT-Full    | 0.026    | 1.37  | 1.77 | 14.52 | 3.07   |
| MapAnything    | 0.044    | 6.00  | 2.90 | 57.50 | 13.33  |
| Mapa-FT-Public | 0.044    | 5.39  | 3.33 | 55.54 | 13.21  |
| Mapa-FT-Syn    | 0.052    | 3.28  | 2.64 | 51.10 | 11.94  |
| Mapa-FT-Real   | 0.041    | 3.16  | 2.45 | 30.55 | 6.25   |
| Mapa-FT-Full   | 0.037    | 2.51  | 1.91 | 29.08 | 6.10   |

### Explicit geometric priors after UAV-domain adaptation

원논문 Table 7. C=intrinsics, P=poses, CP=both. Camera intrinsics가 Ray Error를 크게 줄임.

| Model   | Input | AbsRel ↓ | Ray ↓ | CD ↓ | ATE ↓ | Rot. ↓ |
| ------- | ----- | -------- | ----- | ---- | ----- | ------ |
| Mapa-FT | RGB   | 0.037    | 2.51  | 1.91 | 29.08 | 6.10   |
| Mapa-FT | C     | 0.033    | 0.38  | 1.86 | 15.86 | 5.55   |
| Mapa-FT | P     | 0.025    | 2.38  | 1.35 | 17.61 | 1.61   |
| Mapa-FT | CP    | 0.021    | 0.30  | 1.14 | 3.43  | 1.06   |
| Pi3X-FT | RGB   | 0.026    | 1.87  | 1.44 | 18.70 | 3.40   |
| Pi3X-FT | C     | 0.020    | 0.25  | 1.63 | 8.13  | 3.14   |
| Pi3X-FT | P     | 0.021    | 1.93  | 1.77 | 16.50 | 1.98   |
| Pi3X-FT | CP    | 0.018    | 0.26  | 1.89 | 4.80  | 1.62   |

## 💡 Insights & Impact

- **Camera-geometry shift, not just appearance shift**: Failures on UAV imagery stem largely from oblique viewing and HFOV–height ambiguity; adaptation with controllable synthetic geometry coverage fixes what more UAV-like appearance alone cannot.
- **Separate alignment hides inconsistency**: Independent camera alignment reports overly optimistic pose error (ATE-I ≪ ATE-S), masking camera–scene coupling — motivating the shared-alignment protocol.
- **Oblique degrades orientation most**: Pretrained models show a large oblique–nadir rotation gap that fine-tuning shrinks dramatically (up to 90.7% for Pi3).
- **Priors are complementary but not monotonic**: Camera intrinsics sharply cut Ray Error, and CP is strongest overall after adaptation, but priors can degrade individual metrics (e.g., Pi3X-FT CP worsens Chamfer-L1; zero-shot MapAnything degrades under P/CP).
- **Open problem**: Even fine-tuned models retain high Ray Error and Pose ATE at extreme HFOVs without external camera information, so HFOV–height projection ambiguity is not fully resolved.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)** / **[π³](../reconstruction/pi3.md)**: Two of the feed-forward models benchmarked and fine-tuned (with MapAnything, Pi3X, DA3).
- **[DUSt3R](dust3r.md)** / **[MASt3R](mast3r.md)**: Pointmap paradigm that feed-forward UAV reconstruction builds on.
- **[CUT3R](../dynamic/cut3r.md)** / **[Fast3R](../reconstruction/fast3r.md)**: Feed-forward extensions cited for multi-view/online reconstruction.

## 📚 Key Takeaways

1. **A benchmark built around camera geometry**, not scene count: controlled HFOV–height and oblique/nadir coverage exposes the true failure modes of feed-forward UAV reconstruction.
2. **Shared scene-level alignment** is necessary to measure camera–scene consistency; separate alignment is misleading.
3. **Domain adaptation + priors** together substantially improve UAV reconstruction, but extreme-FOV projection ambiguity remains an open challenge.

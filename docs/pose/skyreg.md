# Pixel-wise Geo-registration of Drone and Satellite Images (arXiv 2026)

## 📋 Overview

- **Authors**: Qingyang Liu, David G Shatwell, Parth Parag Kulkarni, Mubarak Shah
- **Institution**: University of Central Florida
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.28891)
- **Verification**: UNKNOWN (2026-10-15; source 2608.28891v1 content reviewed; publication venue not independently confirmed)
- **TL;DR**: Predict drone–satellite 3D geometry and cameras, warp query pixels to georeferenced references and obtain per-pixel GPS.

## 🎯 Key Contributions

1. Distinguish camera-center localization from dense pixel georegistration.
2. Use 3D lifting/reprojection rather than planar homographies.
3. Provide LiDAR/SfM dense geodetic supervision and geographically held-out splits.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: Metadata-free drone-query RGB, georeferenced reference images/cameras/geodetic maps, and optional DEM.
- **Output**: Per-query-pixel GPS coordinates and reference-frame warps.
- **Problem**: Building/terrain parallax in oblique drone views is poorly described by one homography or camera-center retrieval.

### Method

1. Predict pointmaps, intrinsics and relative cameras with a feed-forward geometry backbone.
2. Lift query pixels into 3D.
3. Reproject into the reference camera and interpolate its geodetic map.
4. Compute valid-pixel geographic coordinates separately from image-level median GPS.

Train with SkyReg-Train dense depth, pose and GPS supervision. The benchmark includes Google-Earth-based queries and SfM/LiDAR supervision, not only raw real-drone footage.

## 📊 Results

**Source**: [Source PDF](https://arxiv.org/pdf/2608.28891v1), Table 2, PDF p.13.

Held-out Urban/Suburban pixel georegistration. Compute median pixel GPS error per image, then report mean GE (m). This differs from camera-center error.

| Method | Urban GE (m) ↓ | Suburban GE (m) ↓ |
| ------ | -------------- | ----------------- |
| RoMa   | 133.06         | 112.10            |
| SkyReg | 44.88          | 21.34             |

Reference-image location and camera information are supplied. This is not global localization from query RGB alone.

## 💡 Insights & Impact

Transfer a reference's geodetic frame through a 3D warp to localize the entire query pixelwise.

- Depend on reference selection, GPS maps, depth and camera-prediction quality.
- Error tails and real-sensor domain gaps remain; benchmark means do not guarantee precision surveying.

## 🔗 Related Work

- [DUSt3R](../foundation/dust3r.md): pairwise-pointmap background.
- [GeoRay](../reconstruction/georay.md): a different satellite absolute-height task.

## 📚 Key Takeaways

1. Output dense GPS, not one camera location.
2. A georeferenced reference is an input.
3. Distinguish pixel GE from image-level localization.

# Track4World: Feedforward World-centric Dense 3D Tracking of All Pixels (arXiv preprint (2026-03))

## 📋 Overview

- **Authors**: Jiahao Lu, Jiayi Xu, Wenbo Hu, Ruijie Zhu, Chengfeng Zhao, Sai-Kit Yeung, Ying Shan, Yuan Liu
- **Institution**: The Hong Kong University of Science and Technology, ARC Lab, Tencent PCG
- **Venue**: arXiv preprint (2026-03)
- **Links**: [Paper](https://arxiv.org/abs/2603.02573) | [Project Page](https://jiah-cloud.github.io/Track4World.github.io/)
- **Verification**: PREPRINT (2026-07-21)
- **TL;DR**: A feedforward, VGGT-style model that estimates pixel-wise dense 2D and 3D scene flow between arbitrary frame pairs through a novel 2D-to-3D correlation scheme, then fuses these pairwise flows into holistic, world-centric dense 3D tracking of every pixel in a monocular video.

## 🎯 Key Contributions

1. **Feedforward holistic 3D tracking of all pixels**: Unlike prior trackers restricted to sparse first-frame points (St4RTrack, SpatialTrackerV2, DELTA) or slow optimization pipelines (TrackingWorld), Track4World tracks every pixel of every frame in a world-centric coordinate system in a single feedforward pass.
2. **Pairwise scene-flow decomposition**: Rather than directly regressing 3D trajectories for all pixels (memory- and compute-prohibitive), the continuous tracking problem is decomposed into pairwise scene-flow estimation between arbitrary frame pairs, reducing redundancy.
3. **2D-to-3D correlation module**: A hybrid correlation mechanism fuses ViT geometric feature embeddings with 2D pixel-wise correlations, avoiding expensive 3D k-NN searches and heavy cross-attention. It operates with strict O(N) complexity via coordinate-based lookups versus at least O(N log N + N·k) (or O(N²) for dense global attention) for prior 3D point-based matching.
4. **2D-3D joint supervision**: Because the correlation is anchored to image-plane matches, abundant 2D-flow datasets can supervise the intermediate 2D motion priors, circumventing the scarcity of 3D ground-truth annotations and improving generalization.
5. **Global (arbitrary-pair) scene flow**: Flows are estimated between arbitrary (not only adjacent) frame pairs, leveraging global temporal context to resolve local ambiguities.

## 🔧 Technical Details

### Pipeline

Given a video of T frames, Track4World (1) extracts global scene representations — geometric features, camera-centric point clouds, and camera poses — from a finetuned VGGT-style ViT geometry encoder initialized from a state-of-the-art feedforward reconstruction model (Pi3 or Depth Anything v3 / DA3); (2) predicts dense 3D scene flow between arbitrary source–target timesteps with a sparse-to-dense decoder; and (3) fuses the pairwise 3D flows into holistic world-centric 3D tracks. The default backbone initialization is DA3 unless stated otherwise.

### Scene Flow Decoder

- **Anchor feature extraction (sparse-to-dense)**: Geometry tokens are augmented with temporal context via global self-attention; point clouds and both feature maps are downsampled to 1/8 resolution to form sparse anchor points, later upsampled to full resolution.
- **2D iterative correlation**: Geometric and semantic feature correlation volumes are built between source and neighborhood target positions; a GRU-based operator updates the hidden context feature, the 2D flow, and a visibility confidence at each iteration.
- **Lifting for 3D flow**: The 2D flow update retrieves target 2D positions; interpolating on the global point maps gives an initial 3D flow, which a 3D flow head refines with lifted target samples, source contexts, a 3D spatial correlation, and a trajectory prior. 2D and 3D flows are updated sequentially in a coupled manner.
- **Dense scene flow recovery**: The 1/8 flow maps are upsampled via a learned pixel-shuffle; a hybrid unprojection combines the precise image-plane 2D flow with the Z-axis displacement from the 3D flow, projected into (x, y, z) using intrinsics derived from the predicted point clouds.
- **Global trajectory inference**: For long-range tracking, flows from a reference frame to all subsequent frames are inferred and refined by a temporal aggregator; for dense per-pixel tracking, consecutive frame-to-frame flows are chained.

### Training

Two stages on eight 40GB GPUs: (1) geometry estimation backbone fine-tuning (~100k steps, ~one week; AdamW + StepLR); (2) motion module with the geometry module frozen (~100k steps, ~five days; AdamW + OneCycleLR, peak LR 1×10⁻⁴). A short-to-long-term variable-stride sampling strategy supervises the model with dense flow ground truth over varying temporal intervals and sparse trajectory annotations across the sequence.

## 📊 Results

Track4World is evaluated on 2D/3D flow estimation, 3D tracking, 2D tracking, point-map prediction, camera-pose estimation, and efficiency. Best/second-best are highlighted in the original tables (colors omitted here).

### Scene & Optical Flow — Kubric-3D val (in-domain, short-range)

원논문 Table 1. Kubric-3D val [22], source/reference frames 4 apart. Best/second-best highlighted in the original.

| Method       | Abs Rel ↓ | δ < 1.25 ↑ | EPE3D↓ | AccS ↑ | AccR ↑ | EPE2D↓  | AccS2D ↑ | AccR2D ↑ |
| ------------ | --------- | ---------- | ------ | ------ | ------ | ------- | -------- | -------- |
| RAFT-3D [73] | 0.0649    | 0.9344     | 0.6170 | 0.0015 | 0.0078 | 40.4480 | 0.0002   | 0.0015   |
| POMATO [97]  | 0.1525    | 0.8329     | 0.9672 | 0.0566 | 0.1696 | /       | /        | /        |
| ZeroMSF [48] | 0.0860    | 0.9196     | 0.3528 | 0.1867 | 0.3413 | /       | /        | /        |
| Any4D [36]   | 0.0585    | 0.9547     | 0.3908 | 0.1610 | 0.2893 | /       | /        | /        |
| V-DPM [69]   | 0.0716    | 0.9010     | 0.4087 | 0.1442 | 0.2491 | /       | /        | /        |
| **Ours**     | 0.0344    | 0.9719     | 0.1537 | 0.5494 | 0.7460 | 1.8685  | 0.8086   | 0.9309   |

### Scene Flow — Out-of-domain (KITTI, BlinkVision)

원논문 Table 1. Out-of-domain: KITTI [20], BlinkVision [46].

| Method       | KITTI Abs Rel ↓ | KITTI δ ↑ | KITTI EPE3D ↓ | KITTI AccS ↑ | Blink Abs Rel ↓ | Blink δ ↑ | Blink EPE3D ↓ | Blink AccS ↑ |
| ------------ | --------------- | --------- | ------------- | ------------ | --------------- | --------- | ------------- | ------------ |
| RAFT-3D [73] | 0.1619          | 0.8413    | 0.3837        | 0.0118       | 0.1426          | 0.8455    | 0.6690        | 0.0454       |
| ZeroMSF [48] | 0.2064          | 0.5913    | 0.1823        | 0.1695       | 0.1934          | 0.6620    | 0.3937        | 0.1913       |
| Any4D [36]   | 0.2398          | 0.4974    | 0.1856        | 0.1429       | 0.2218          | 0.6125    | 0.9238        | 0.1242       |
| V-DPM [69]   | 0.1469          | 0.7981    | 0.4462        | 0.1180       | 0.2117          | 0.6449    | 1.1476        | 0.1079       |
| **Ours**     | 0.0707          | 0.9570    | 0.0742        | 0.6929       | 0.0371          | 0.9768    | 0.1135        | 0.5091       |

### Optical Flow — BlinkVision (2D metrics)

원논문 Table 1. On BlinkVision optical-flow metrics, Track4World has the lowest EPE2D but trails SEA-RAFT on AccS2D — an honest trade-off against dedicated 2D optical-flow methods.

| Method          | Blink EPE2D ↓ | Blink AccS2D ↑ | Blink AccR2D ↑ |
| --------------- | ------------- | -------------- | -------------- |
| RAFT [72]       | 14.1255       | 0.5037         | 0.6953         |
| GMFlowNet [100] | 12.0176       | 0.5281         | 0.7170         |
| SEA-RAFT [84]   | 20.9160       | 0.5697         | 0.7186         |
| **Ours**        | 7.5632        | 0.5131         | 0.7424         |

### 3D Tracking — APD, Camera-coordinate

원논문 Table 2. APD metric (higher is better; the ablation Table 6 marks tracking as L-16↑/L-50↑). L-16/L-50 = tracking within 16/50 frames. \* uses GT intrinsics; † = no bundle adjustment.

| Method                | PO L-16 | PO L-50 | ADT L-16 | ADT L-50 | PStu L-16 | PStu L-50 | Drive L-16 | Drive L-50 | Avg L-16 | Avg L-50 |
| --------------------- | ------- | ------- | -------- | -------- | --------- | --------- | ---------- | ---------- | -------- | -------- |
| SpatialTracker\* [86] | 0.3116  | 0.2977  | 0.4962   | 0.4692   | 0.5390    | 0.4991    | 0.2529     | 0.2502     | 0.3999   | 0.3791   |
| DELTA\* [59]          | 0.3529  | 0.3412  | 0.5116   | 0.4952   | 0.5922    | 0.5533    | 0.2704     | 0.2701     | 0.4317   | 0.4150   |
| STV2† [87]            | 0.1864  | 0.1785  | 0.2400   | 0.2330   | 0.3784    | 0.3690    | 0.1711     | 0.1725     | 0.2400   | 0.2383   |
| MASt3R [43]           | 0.3546  | 0.3253  | 0.3368   | 0.3029   | 0.3293    | 0.2956    | 0.2767     | 0.2559     | 0.3244   | 0.2949   |
| MonST3R [96]          | 0.3912  | 0.3860  | 0.3694   | 0.3429   | 0.3511    | 0.3381    | 0.3056     | 0.2787     | 0.3543   | 0.3364   |
| POMATO [97]           | 0.4816  | 0.4623  | 0.5338   | 0.5299   | 0.5163    | 0.4726    | 0.4237     | 0.4329     | 0.4888   | 0.4744   |
| ZeroMSF [48]          | 0.4214  | 0.3887  | 0.5382   | 0.4635   | 0.5083    | 0.4524    | 0.4448     | 0.4513     | 0.4782   | 0.4390   |
| **Ours**              | 0.5397  | 0.5268  | 0.6501   | 0.6091   | 0.5948    | 0.5423    | 0.5003     | 0.5092     | 0.5712   | 0.5469   |

### 3D Tracking — APD, World-coordinate

원논문 Table 2. World-coordinate APD. ‡ = methods using camera poses estimated by VGGT [76]. Track4World leads on average but V-DPM edges it on PStudio (0.6084/0.5795 vs 0.5946/0.5422).

| Method        | PO L-16 | PO L-50 | ADT L-16 | ADT L-50 | PStu L-16 | PStu L-50 | Drive L-16 | Drive L-50 | Avg L-16 | Avg L-50 |
| ------------- | ------- | ------- | -------- | -------- | --------- | --------- | ---------- | ---------- | -------- | -------- |
| STV2† [87]    | 0.1925  | 0.1763  | 0.2456   | 0.2163   | 0.3790    | 0.3689    | 0.1711     | 0.1725     | 0.2470   | 0.2335   |
| POMATO‡ [97]  | 0.4425  | 0.3905  | 0.3611   | 0.3548   | 0.5166    | 0.4713    | 0.4227     | 0.4210     | 0.4357   | 0.4094   |
| ZeroMSF‡ [48] | 0.4053  | 0.3505  | 0.4530   | 0.3563   | 0.4828    | 0.4386    | 0.4474     | 0.4382     | 0.4471   | 0.3959   |
| Any4D [36]    | 0.4769  | 0.4174  | 0.4460   | 0.3717   | 0.5707    | 0.5066    | 0.5235     | 0.5079     | 0.5043   | 0.4509   |
| V-DPM [69]    | 0.4848  | 0.4233  | 0.4783   | 0.3759   | 0.6084    | 0.5795    | 0.4854     | 0.4817     | 0.5142   | 0.4668   |
| **Ours**      | 0.5345  | 0.5162  | 0.6250   | 0.5622   | 0.5946    | 0.5422    | 0.5003     | 0.5087     | 0.5636   | 0.5323   |

### 2D Tracking (TAP-Vid metrics)

원논문 Table 3. Kinetics [8], RoboTAP [75], RGB-Stacking [42].

| Method          | Kin AJ↑ | Kin δvis↑ | Kin OA↑ | Robo AJ↑ | Robo δvis↑ | Robo OA↑ | RGBS AJ↑ | RGBS δvis↑ | RGBS OA↑ |
| --------------- | ------- | --------- | ------- | -------- | ---------- | -------- | -------- | ---------- | -------- |
| TAPIR [15]      | 49.6    | 64.2      | 85.0    | 59.6     | 73.4       | 87.0     | 55.5     | 69.7       | 88.0     |
| LocoTrack [12]  | 52.9    | 66.8      | 85.3    | 62.3     | 76.2       | 87.1     | 69.7     | 83.2       | 89.5     |
| BootsTAPIR [16] | 54.6    | 68.4      | 86.5    | 64.9     | 80.1       | 86.3     | 70.8     | 83.0       | 89.9     |
| CoTracker3 [34] | 55.8    | 68.5      | 88.3    | 66.4     | 78.8       | 90.8     | 71.7     | 83.6       | 91.1     |
| **Ours**        | 59.1    | 71.3      | 90.6    | 70.9     | 81.8       | 93.3     | 78.2     | 88.5       | 92.3     |

### Point Map Estimation (subset)

원논문 Table 4. Seven datasets evaluated; a representative subset plus Avg shown here. Track4World wins on average, but DA3 remains stronger on ScanNet (Abs Rel 0.0222 vs Ours 0.0288; δ 0.9917 vs 0.9872), not shown below.

| Method           | Params | Sintel Abs Rel↓ | Sintel δ↑ | KITTI Abs Rel↓ | KITTI δ↑ | Kubric Abs Rel↓ | Kubric δ↑ | Avg Abs Rel↓ | Avg δ↑ |
| ---------------- | ------ | --------------- | --------- | -------------- | -------- | --------------- | --------- | ------------ | ------ |
| MoGe [80]        | 314M   | 0.2181          | 0.6615    | 0.0801         | 0.9374   | 0.0852          | 0.9294    | 0.1484       | 0.7776 |
| VGGT [76]        | 1.26B  | 0.2004          | 0.7303    | 0.1245         | 0.8517   | 0.0316          | 0.9733    | 0.1449       | 0.7738 |
| MoGe-2 [81]      | 331M   | 0.2058          | 0.6903    | 0.0776         | 0.9627   | 0.1184          | 0.8592    | 0.1194       | 0.8525 |
| MapAnything [37] | 563M   | 0.2059          | 0.7141    | 0.1016         | 0.9144   | 0.0684          | 0.9475    | 0.1208       | 0.8816 |
| Pi3 [85]         | 1.29B  | 0.1489          | 0.7899    | 0.0866         | 0.8877   | 0.0337          | 0.9817    | 0.0738       | 0.9200 |
| DA3 [49]         | 1.36B  | 0.1575          | 0.8064    | 0.0404         | 0.9861   | 0.0431          | 0.9599    | 0.0743       | 0.9294 |
| **Ours**         | 1.38B  | 0.1261          | 0.8291    | 0.0268         | 0.9877   | 0.0191          | 0.9939    | 0.0552       | 0.9440 |

### Camera Pose Estimation

원논문 Table 5. Sintel [6] and Bonn [60]. Track4World leads on Bonn (ATE 0.009, RRE 0.604) but Pi3 is stronger across all three Sintel metrics (0.088/0.043/0.299 vs 0.119/0.054/0.309).

| Method           | Sintel ATE↓ | Sintel RTE↓ | Sintel RRE↓ | Bonn ATE↓ | Bonn RTE↓ | Bonn RRE↓ |
| ---------------- | ----------- | ----------- | ----------- | --------- | --------- | --------- |
| Align3R [54]     | 0.128       | 0.042       | 0.432       | 0.023     | 0.007     | 0.620     |
| CUT3R [79]       | 0.217       | 0.070       | 0.636       | 0.035     | 0.014     | 1.212     |
| VGGT [76]        | 0.167       | 0.062       | 0.490       | 0.051     | 0.011     | 1.038     |
| MapAnything [37] | 0.227       | 0.111       | 2.047       | 0.026     | 0.014     | 0.668     |
| Pi3 [85]         | 0.088       | 0.043       | 0.299       | 0.012     | 0.011     | 0.612     |
| DA3 [49]         | 0.124       | 0.061       | 0.331       | 0.010     | 0.011     | 0.638     |
| POMATO [71]      | 0.209       | 0.064       | 0.694       | 0.041     | 0.017     | 0.832     |
| STV2 [87]        | 0.133       | 0.057       | 0.641       | 0.019     | 0.015     | 0.701     |
| **Ours**         | 0.119       | 0.054       | 0.309       | 0.009     | 0.009     | 0.604     |

### Ablation — 3D Foundation Backbone

원논문 Table 6. Averaged across datasets; the framework is effective across backbones, with DA3 best on EPE3D and 3D tracking.

| Method           | PM Abs Rel↓ | PM δ<1.25↑ | EPE3D↓ | SF Abs Rel↓ | SF δ<1.25↑ | 3D Track L-16↑ | 3D Track L-50↑ |
| ---------------- | ----------- | ---------- | ------ | ----------- | ---------- | -------------- | -------------- |
| Ours (MoGe [80]) | 0.0973      | 0.8921     | 0.3180 | 0.0680      | 0.9479     | 0.5447         | 0.5135         |
| Ours (Pi3 [85])  | 0.0492      | 0.9537     | 0.2569 | 0.0548      | 0.9645     | 0.5734         | 0.5424         |
| Ours (DA3 [49])  | 0.0552      | 0.9440     | 0.2056 | 0.0474      | 0.9607     | 0.5712         | 0.5469         |

### Ablation — Scene Flow Decoder

원논문 Table 7. Averaged over all datasets. Removing 2D supervision collapses EPE3D to 0.6511; the full hybrid formulation (0.2056) beats naive "2D flow + d" (0.8210) and "Pure 3D flow" (0.2815).

| Setting            | Abs Rel ↓ | δ < 1.25 ↑ | EPE3D ↓ |
| ------------------ | --------- | ---------- | ------- |
| w/o 2D Supervision | 0.1021    | 0.9199     | 0.6511  |
| w/o Target lifting | 0.0534    | 0.9543     | 0.3017  |
| w/o iterations     | 0.0506    | 0.9559     | 0.2356  |
| w/o C3d,i,j & M3d  | 0.0482    | 0.9591     | 0.2201  |
| 2D flow + d        | 0.1304    | 0.8911     | 0.8210  |
| Pure 3D flow       | 0.0552    | 0.9570     | 0.2815  |
| **Full (Ours)**    | 0.0474    | 0.9607     | 0.2056  |

### Efficiency (16-frame ADT sequences)

원논문 Table 8. OOM = Out-of-Memory under dense tracking. Track4World is fastest and smallest, though ZeroMSF uses less memory (10 vs 14 GB).

| Method                    | Time (s) ↓ | Mem. (GB) ↓ | Parm. (M) ↓ |
| ------------------------- | ---------- | ----------- | ----------- |
| POMATO [97] (Dense)       | 4.8        | 16          | 133.64      |
| ZeroMSF [48] (Dense)      | 8.2        | 10          | 153.84      |
| STV2 [87] (Sparse)        | 5.8        | 19          | 65.99       |
| STV2 [87] (Dense)         | OOM        | OOM         | 65.99       |
| Ours w/o 2D-to-3D (Dense) | OOM        | OOM         | 56.90       |
| **Ours (Dense)**          | 3.4        | 14          | 26.06       |

## 💡 Insights & Impact

- **Decomposition beats direct regression**: Casting all-pixel 3D tracking as arbitrary-pair scene-flow estimation avoids the prohibitive memory/compute of explicitly regressing per-pixel 3D trajectories across all frames.
- **2D data rescues 3D supervision scarcity**: Anchoring 3D updates to image-plane correlations lets abundant 2D-flow datasets supervise the intermediate 2D motion, which the ablation shows is essential (removing 2D supervision drives EPE3D from 0.2056 to 0.6511).
- **Efficiency from avoiding 3D k-NN**: Replacing the module with a traditional 3D-correlation mechanism ("Ours w/o 2D-to-3D") OOMs under dense tracking, empirically confirming the O(N) design as the enabler of dense tracking; the full model runs in 3.4 s with only 26.06M motion-module parameters.
- **Honest trade-offs**: Pi3 still leads camera pose on Sintel, DA3 leads point-map on ScanNet, SEA-RAFT leads AccS2D on BlinkVision, and V-DPM edges world-coordinate PStudio tracking — Track4World's advantage is in holistic, dense, world-centric tracking rather than dominating every isolated sub-metric.

## 🔗 Related Work

- **[VGGT](../reconstruction/vggt.md)**: The VGGT-style ViT global 3D representation is the geometric backbone paradigm Track4World builds on; also a point-map/pose baseline and pose provider for ‡ variants.
- **[Pi3](../reconstruction/pi3.md)** / **[MapAnything](../reconstruction/mapanything.md)** / **[MoGe](../reconstruction/moge.md)**: Feedforward reconstruction backbones and point-map baselines; Pi3 and DA3 are the primary backbone initializations.
- **[DUSt3R](../foundation/dust3r.md)**: The pairwise pointmap foundation that seeded the feedforward-reconstruction trend Track4World follows.
- **[MonST3R](./monst3r.md)** / **[CUT3R](./cut3r.md)** / **[Align3R](./align3r.md)**: Dynamic-scene reconstruction / tracking and camera-pose baselines.
- **[POMATO](./pomato.md)** / **[Stereo4D](./stereo4d.md)**: Pairwise pointmap / scene-flow methods for motion reconstruction; POMATO is a major tracking and pose baseline.
- **[Any4D](./any4d.md)** / **[V-DPM](./v-dpm.md)**: Concurrent joint geometry-and-motion works used as baselines across tracking benchmarks.

## 📚 Key Takeaways

1. **Feedforward, world-centric, all-pixel**: Track4World is the first feedforward model to produce dense 3D tracks for every pixel of every frame in a global coordinate system.
2. **2D-to-3D correlation is the core idea**: An O(N) hybrid correlation avoids 3D k-NN and cross-attention, enabling dense tracking where 3D-correlation methods (STV2) OOM.
3. **Joint 2D-3D supervision**: Leveraging 2D-flow data to guide 3D flow is empirically indispensable and boosts generalization.
4. **State-of-the-art tracking with strong efficiency**: Leading average APD in both camera- and world-coordinate 3D tracking, top 2D-tracking scores, competitive geometry/pose, and the fastest/smallest configuration — while honestly trailing specialist baselines on a few isolated metrics.

# ZipMap: Linear-Time Stateful 3D Reconstruction via Test-Time Training (CVPR 2026)

![zipmap — architecture](https://arxiv.org/html/2603.04385v3/x2.png)

_Method Overview (원논문 Fig. 2)_

## 📋 Overview

- **Authors**: Haian Jin, Rundi Wu, Tianyuan Zhang, Ruiqi Gao, Jonathan T. Barron, Noah Snavely, Aleksander Hołyński
- **Institution**: Google DeepMind, Cornell University, Massachusetts Institute of Technology
- **Venue**: CVPR 2026
- **Links**: [Paper](https://arxiv.org/abs/2603.04385) | [Project Page](https://haian-jin.github.io/ZipMap)
- **Verification**: CONFIRMED (2026-07-20)
- **TL;DR**: Replaces global attention with large-chunk test-time-training layers that compress an entire image collection into MLP fast weights, giving linear-time bidirectional reconstruction whose accuracy matches quadratic-time VGGT and π³ — and a hidden state that can be queried at novel viewpoints in real time.

## 🎯 Key Contributions

1. **Linear-time bidirectional reconstruction.** Runtime scales linearly with the number of input views, unlike VGGT and π³, without resorting to the recurrent processing that other linear-time methods use.
2. **A queryable implicit scene representation.** The TTT fast weights double as a scene state that can be queried with a target ray map to produce pixel-aligned geometry and appearance at novel viewpoints — at roughly 100 FPS, independent of input view count.
3. **Streaming extension.** The same architecture supports online fast-weight updates, one view at a time.
4. **Accuracy without the usual sacrifice.** Prior linear-scaling approaches (CUT3R, TTT3R) traded reconstruction quality for efficiency; ZipMap matches or exceeds quadratic-time models.

## 🔧 Technical Details

### Architecture

24 identical blocks, each composed of:

1. **Local Window Attention** — standard self-attention with rotary positional encoding, operating on the tokens of each view (image or ray map) independently.
2. **Global Large-Chunk TTT Layer** — inspired by LaCT, this replaces all global attention and is the source of both linear scaling and the implicit scene representation.

Tokenization reuses VGGT's DINOv2 encoder; each input image gets one camera token plus four register tokens. The ray map input `T ∈ R^{H×W×9}` concatenates ray origin `r_o`, direction `r_d`, and `r_o × r_d` per pixel, and replaces the camera token with a special query token. Patch size `P = 14`, so `p = HW/P² + 5`.

### The TTT mechanism

The fast-weight function is a SwiGLU-MLP, `f_W(x) = W₂ SiLU(W₁x) ∘ (W₃x)`, with `W = {W₁, W₂, W₃}` the fast weights. These are adapted by a **single gradient descent step** over tokens from all input views, against a virtual key–value reconstruction objective:

```text
L(f_W(k_i), v_i) = −f_W(k_i)ᵀ v_i
```

This objective has nothing to do with the 3D reconstruction loss; it is optimized once per layer to build an in-context associative memory. The per-token learning rate `η_i` is predicted by a small linear layer.

Following Muon, the gradient is orthonormalized via Newton–Schulz, and the update is L2-normalized for stability:

```text
Δ ← NewtonSchulz(g)
Ŵ ← ‖W‖ · (W − Δ) / ‖W − Δ‖
```

Applying `f_Ŵ` to input query tokens is analogous to querying all key-value pairs in self-attention, but at linear rather than quadratic cost. A gated unit `SiLU(W_g o′_i)` produces the final output.

**Crucially**, the same fast weights apply directly to target ray tokens from `T` — playing the role of cross-attention from target rays to input images, at constant runtime per target token regardless of how many input views built the state.

### Prediction Heads

Four heads: a VGGT-style camera head predicting `c_i ∈ R⁹` (4D rotation quaternion, 3D translation, two intrinsics); DPT-style point, depth, and query heads. The point head predicts a **local** point map in camera coordinates, similar to π³. Unlike π³, a separate depth head predicts a depth map plus confidence — the paper reports both yield similar quantitative performance, but the depth head produces visually smoother results, and the confidence map helps filter noisy pixels at inference.

### Training

Loss: `L = L_point + L_depth + w_c·L_cam + L_color^t + L_depth^t`, with `w_c = 5` following VGGT's open-source implementation. The point loss is scale-invariant, with global scale `ŝ` solved by the ROE solver; the depth loss is an uncertainty-modulated L1 with `α = 0.2`, behaving equivalently to a Laplacian negative log-likelihood. Query losses are enabled only during finetuning.

Token dimension `d = 1024`, fast-weight MLP intermediate dimension 2048, giving a state size of `6d²` per layer. Local window attention weights are initialized from VGGT's frame-wise attention, and a subset of TTT parameters from VGGT's global-attention parameters.

Three stages on 64 H100 GPUs, over 29 publicly available datasets:

1. Static datasets with a designated reference view, 80K iterations, LR 1e-4 for TTT blocks and 1e-5 elsewhere, ≈5 days.
2. Add dynamic datasets, 40K iterations at uniform LR 1e-5, ≈2.5 days.
3. Remove the reference view, 60K iterations at LR 1e-5, switching to an affine-invariant camera loss inspired by π³.

## 📊 Results

### Camera Pose Estimation — RealEstate10K and Co3Dv2

원논문 Table 1. All methods have seen Co3Dv2 during training. CUT3R and TTT3R additionally use RealEstate10K; the rest do not.

| Complexity | Method   | RE10K AUC@5 ↑ | RE10K AUC@15 ↑ | RE10K AUC@30 ↑ | Co3Dv2 AUC@5 ↑ | Co3Dv2 AUC@15 ↑ | Co3Dv2 AUC@30 ↑ |
| ---------- | -------- | ------------- | -------------- | -------------- | -------------- | --------------- | --------------- |
| O(N²)      | Fast3R   | 22.36         | 46.71          | 61.68          | 31.05          | 59.63           | 73.43           |
| O(N²)      | FLARE    | 38.47         | 67.02          | 80.01          | 23.84          | 57.78           | 73.99           |
| O(N²)      | VGGT     | 38.71         | 66.46          | 78.89          | 67.84          | 83.95           | 89.99           |
| O(N²)      | π³       | 63.10         | 80.31          | 87.40          | 57.12          | 79.86           | 87.93           |
| O(N)       | CUT3R    | 46.92         | 70.65          | 81.68          | 24.88          | 56.28           | 71.72           |
| O(N)       | TTT3R    | 46.37         | 70.33          | 81.51          | 22.61          | 53.49           | 69.46           |
| O(N)       | **Ours** | 53.34         | 74.97          | 84.30          | 62.46          | 81.64           | 88.76           |

ZipMap is the best linear-time method by a wide margin, but does not top the table: π³ leads on RealEstate10K and VGGT on Co3Dv2.

### Camera Pose Estimation — Sintel, TUM-dynamics, ScanNet

원논문 Table 2. All methods have seen ScanNet or ScanNet++ in training; none has seen Sintel or TUM-dynamics.

| Complexity | Method   | Sintel ATE ↓ | Sintel RPE trans ↓ | Sintel RPE rot ↓ | TUM ATE ↓ | TUM RPE trans ↓ | TUM RPE rot ↓ | ScanNet ATE ↓ | ScanNet RPE rot ↓ |
| ---------- | -------- | ------------ | ------------------ | ---------------- | --------- | --------------- | ------------- | ------------- | ----------------- |
| O(N²)      | Fast3R   | 0.371        | 0.298              | 13.750           | 0.090     | 0.101           | 1.425         | 0.155         | 3.491             |
| O(N²)      | FLARE    | 0.207        | 0.090              | 3.015            | 0.026     | 0.013           | 0.475         | 0.064         | 0.971             |
| O(N²)      | VGGT     | 0.172        | 0.061              | 0.471            | 0.012     | 0.010           | 0.309         | 0.035         | 0.376             |
| O(N²)      | π³       | 0.073        | 0.038              | 0.288            | 0.014     | 0.009           | 0.307         | 0.030         | 0.345             |
| O(N)       | CUT3R    | 0.216        | 0.071              | 0.622            | 0.042     | 0.013           | 0.395         | 0.096         | 0.578             |
| O(N)       | TTT3R    | 0.204        | 0.085              | 0.690            | 0.028     | 0.012           | 0.361         | 0.065         | 0.617             |
| O(N)       | **Ours** | 0.132        | 0.066              | 0.438            | 0.012     | 0.010           | 0.310         | 0.034         | 0.385             |

### Point Map Estimation — DTU and ETH3D

원논문 Table 4. Following π³, mean and median of accuracy, completeness, and normal consistency, keyframes every 5 images.

| Complexity | Method   | DTU Acc. Mean ↓ | DTU Comp. Mean ↓ | DTU N.C. Mean ↑ | ETH3D Acc. Mean ↓ | ETH3D Comp. Mean ↓ | ETH3D N.C. Mean ↑ |
| ---------- | -------- | --------------- | ---------------- | --------------- | ----------------- | ------------------ | ----------------- |
| O(N²)      | Fast3R   | 3.340           | 2.929            | 0.671           | 0.832             | 0.978              | 0.667             |
| O(N²)      | FLARE    | 2.541           | 3.174            | 0.684           | 0.464             | 0.664              | 0.744             |
| O(N²)      | VGGT     | 1.308           | 1.929            | 0.665           | 0.270             | 0.304              | 0.841             |
| O(N²)      | π³       | 1.151           | 1.793            | 0.668           | 0.188             | 0.211              | 0.872             |
| O(N)       | CUT3R    | 5.045           | 6.437            | 0.666           | 0.593             | 0.747              | 0.754             |
| O(N)       | TTT3R    | 5.337           | 6.593            | 0.666           | 0.763             | 0.881              | 0.739             |
| O(N)       | **Ours** | 1.228           | 1.649            | 0.675           | 0.254             | 0.249              | 0.865             |

The gap over the other linear-time methods is the story here: CUT3R and TTT3R sit around 5.0–5.3 DTU Acc. Mean while ZipMap reaches 1.228, close to π³'s 1.151. ZipMap has the best DTU Comp. Mean and N.C. Mean of any method in the table.

### Point Map Estimation — 7-Scenes and NRGBD

원논문 Table 3. Mean values. Keyframes every 200 (sparse) / 40 (dense) frames for 7-Scenes, every 500 / 100 for NRGBD.

| Setting | Method   | 7-Scenes Acc. ↓ | 7-Scenes Comp. ↓ | 7-Scenes NC. ↑ | NRGBD Acc. ↓ | NRGBD Comp. ↓ | NRGBD NC. ↑ |
| ------- | -------- | --------------- | ---------------- | -------------- | ------------ | ------------- | ----------- |
| Sparse  | Fast3R   | 0.095           | 0.144            | 0.673          | 0.135        | 0.163         | 0.759       |
| Sparse  | CUT3R    | 0.080           | 0.102            | 0.711          | 0.098        | 0.075         | 0.830       |
| Sparse  | TTT3R    | 0.098           | 0.159            | 0.681          | 0.101        | 0.076         | 0.826       |
| Sparse  | FLARE    | 0.085           | 0.145            | 0.696          | 0.053        | 0.051         | 0.877       |
| Sparse  | VGGT     | 0.044           | 0.056            | 0.733          | 0.049        | 0.066         | 0.882       |
| Sparse  | π³       | 0.047           | 0.074            | 0.741          | 0.024        | 0.028         | 0.909       |
| Sparse  | **Ours** | 0.044           | 0.065            | 0.740          | 0.046        | 0.057         | 0.895       |
| Dense   | CUT3R    | 0.023           | 0.028            | 0.674          | 0.065        | 0.036         | 0.812       |
| Dense   | TTT3R    | 0.035           | 0.032            | 0.666          | 0.074        | 0.037         | 0.803       |
| Dense   | FLARE    | 0.019           | 0.026            | 0.684          | 0.023        | 0.018         | 0.882       |
| Dense   | VGGT     | 0.022           | 0.026            | 0.667          | 0.015        | 0.015         | 0.871       |
| Dense   | π³       | 0.016           | 0.022            | 0.689          | 0.013        | 0.014         | 0.874       |
| Dense   | **Ours** | 0.018           | 0.030            | 0.680          | 0.016        | 0.017         | 0.870       |

On NRGBD sparse, π³ is clearly ahead (0.024 vs 0.046 Acc.); on 7-Scenes dense, ZipMap's Comp. of 0.030 is worse than CUT3R's 0.028 and every O(N²) method.

### Video Depth Estimation

원논문 Table 5. Scale-only alignment.

| Complexity | Method   | Params | Sintel AbsRel ↓ | Sintel δ<1.25 ↑ | Bonn AbsRel ↓ | Bonn δ<1.25 ↑ | KITTI AbsRel ↓ | KITTI δ<1.25 ↑ |
| ---------- | -------- | ------ | --------------- | --------------- | ------------- | ------------- | -------------- | -------------- |
| O(N²)      | Fast3R   | 648M   | 0.638           | 0.422           | 0.194         | 0.772         | 0.138          | 0.834          |
| O(N²)      | FLARE    | 1.40B  | 0.729           | 0.336           | 0.152         | 0.790         | 0.356          | 0.570          |
| O(N²)      | VGGT     | 1.26B  | 0.298           | 0.643           | 0.055         | 0.971         | 0.073          | 0.965          |
| O(N²)      | π³       | 959M   | 0.228           | 0.672           | 0.051         | 0.975         | 0.038          | 0.986          |
| O(N)       | CUT3R    | 793M   | 0.432           | 0.510           | 0.072         | 0.951         | 0.152          | 0.805          |
| O(N)       | TTT3R    | 793M   | 0.426           | 0.522           | 0.061         | 0.970         | 0.149          | 0.812          |
| O(N)       | **Ours** | 1.40B  | 0.248           | 0.695           | 0.059         | 0.973         | 0.057          | 0.974          |

ZipMap has the best Sintel δ<1.25 in the table (0.695), but π³ leads on AbsRel everywhere and Bonn AbsRel is slightly worse than VGGT's (0.059 vs 0.055).

### Efficiency

The paper's stated efficiency claims, from the abstract and Section 4.2:

- Reconstructs **over 700 frames in under 10 seconds on a single H100 GPU (75 FPS)**, which the paper describes as **over 20× faster than SOTA methods such as VGGT**; Figure 1 anchors this at 750 frames.
- VGGT requires **over 200 seconds** for the same 700+ frame workload.
- **About 3× faster than previous linear-time methods** CUT3R and TTT3R, despite ZipMap being the larger model — the paper attributes this to those baselines reconstructing frames sequentially, giving lower GPU utilization.
- The implicit scene state can be queried at **≈100 FPS**, independent of input view count.

Figure 4 analyzes long-sequence camera accuracy (ATE) on the DL3DV test set under two protocols — increasing scene scale by taking the first N frames, and increasing view density by uniformly subsampling N frames along a fixed trajectory. The paper reports that ZipMap matches π³ and VGGT while CUT3R and TTT3R degrade sharply as N grows; the figure carries no printed values, so no numbers are transcribed.

### Ablation: TTT Components

원논문 Table 6. Point-map estimation on ETH3D. All variants trained with reduced compute and a smaller data scale, so these numbers are not comparable to Table 4.

| Method                      | Acc. Mean ↓ | Acc. Med. ↓ | Comp. Mean ↓ | Comp. Med. ↓ | N.C. Mean ↑ | N.C. Med. ↑ |
| --------------------------- | ----------- | ----------- | ------------ | ------------ | ----------- | ----------- |
| Ours                        | 0.337       | 0.224       | 0.357        | 0.217        | 0.810       | 0.918       |
| Ours w/o gated unit         | 0.354       | 0.251       | 0.381        | 0.234        | 0.802       | 0.901       |
| Ours w/o Newton–Schulz      | 0.408       | 0.283       | 0.430        | 0.249        | 0.787       | 0.898       |
| Ours w/ global TTT lr (0.1) | 0.411       | 0.303       | 0.490        | 0.317        | 0.779       | 0.886       |
| Ours w/ global TTT lr (1.0) | 0.464       | 0.366       | 0.537        | 0.343        | 0.782       | 0.890       |

Newton–Schulz orthonormalization and the dynamic per-token learning rate are both load-bearing; a fixed global TTT learning rate is clearly worse at either value tested.

### Removing the Reference View

The paper reports that removing the explicit reference-view selection in the final training stage "doesn't yield a clear or consistent advantage" on the standard benchmarks, but improves accuracy and generalization on long input sequences.

## 💡 Insights & Impact

**Compression, not recurrence, is the way to linear time.** The existing linear-time options — CUT3R, TTT3R, Point3R — process sequentially, which invites error accumulation and underuses the GPU. ZipMap's insight is that TTT gives you a fixed-size state that absorbs the _entire_ collection bidirectionally in one pass, so linear scaling does not require giving up bidirectionality or accuracy.

**The state is a feature, not just a cost-saving device.** Because the fast weights are an associative memory over the whole scene, applying them to a novel target ray map is functionally cross-attention into the input images. This turns an efficiency mechanism into a real-time queryable implicit scene representation, and Figure 5 shows the model extrapolating common structure (walls, floors, ground) into unobserved regions — though the paper is candid that its deterministic nature prevents hallucinating rich high-frequency detail or entirely unseen objects.

**Two orthogonal things the fast weights buy.** The same update rule supports bidirectional (all views at once) and streaming (one view at a time) reconstruction, using the identical virtual key–value objective.

**Where it still trails.** π³ remains ahead on most point-map and depth AbsRel metrics, and VGGT on Co3Dv2 pose. ZipMap's claim is parity-class accuracy at linear cost, not a new accuracy ceiling.

## 🔗 Related Work

- [VGGT](vggt.md) — the quadratic-time reference model; ZipMap reuses its DINOv2 encoder, camera head design, and initializes attention weights from it
- [Pi3](pi3.md) — source of the local point map formulation, the affine-invariant camera loss, and the strongest accuracy baseline
- [CUT3R](../dynamic/cut3r.md) — persistent-state sequential reconstruction, the main linear-time baseline
- [TTT3R](ttt3r.md) — the other test-time-training linear-time baseline
- [Point3R](point3r.md) — explicit spatial pointer memory, cited among sequential approaches
- [Fast3R](fast3r.md) — multi-view extension beyond the 2-image setting
- [DUSt3R](../foundation/dust3r.md) / [MASt3R](../foundation/mast3r.md) — the pairwise pointmap foundation
- [FastVGGT](fastvggt.md) — token-merging acceleration that, as the paper notes, still retains quadratic runtime complexity

## 📚 Key Takeaways

1. **Linear time need not cost accuracy.** ZipMap is the first linear-scaling model in this lineage to reach VGGT/π³-class point-map and pose accuracy, closing a ~4× DTU accuracy gap over CUT3R and TTT3R.
2. **Large-chunk TTT replaces global attention cleanly.** One gradient step per layer over all input tokens, orthonormalized with Newton–Schulz and gated on output — the ablation shows both pieces matter.
3. **The compressed state is queryable.** ≈100 FPS novel-viewpoint queries at constant cost in the number of input views, plus the ability to extrapolate basic scene priors into unseen regions.
4. **Stated speedups**: over 700 frames in under 10 seconds on one H100 (75 FPS), over 20× faster than VGGT which needs over 200 seconds, and about 3× faster than CUT3R/TTT3R.
5. **Bidirectional and streaming from the same mechanism.** Fast weights can be updated once over everything, or online per view.

# AquaFlow: A Monocular Gaussian Splatting SLAM for Underwater Streaming Reconstruction (arXiv 2026)

## 📋 Overview

- **Authors**: Yingxiang Xu, Kerui Ren, Wenqi Guo, Changjian Jiang, Tao Lu, Linning Xu, Mulin Yu
- **Institution**: Zhejiang University, Shanghai Artificial Intelligence Laboratory, Shanghai Jiao Tong University, Tsinghua University, University of Hong Kong, Chinese University of Hong Kong
- **Venue**: arXiv preprint (2026-08)
- **Links**: [Paper](https://arxiv.org/abs/2608.22906)
- **Verification**: UNKNOWN (2026-10-15; 원문 2608.22906v1 내용 검토, 게재 venue 독립 확인 전)
- **TL;DR**: 수중으로 적응한 MASt3R tracking과 medium-guided Gaussian 초기화, 거리 조건 appearance decoder로 수중 지도를 streaming 방식으로 최적화한다.

## 🎯 Key Contributions

1. 수중 pair로 metric pointmap·matching을 학습한다.
2. Frame 역할에 따라 incremental Gaussian 초기화를 수행한다.
3. Viewing distance와 direction을 반영하는 structured Gaussian을 사용한다.

## 🔧 Technical Details

### Input, Output, and Problem

- **Input**: 단안 수중 RGB video stream.
- **Output**: Camera trajectory와 medium-aware Gaussian 지도·rendering.
- **Problem**: 수중 appearance 변화는 tracking을 흔들고 표준 SH color가 거리별 감쇠를 geometry에 흡수하게 한다.

### Method

1. Fine-tuned MASt3R로 현재 frame과 keyframe의 pointmap·descriptor·confidence를 예측한다.
2. Matching과 robust pointmap alignment로 상대 pose를 추정하고 graph를 보정한다.
3. Keyframe·mapping frame에서 medium model로 clean color와 Gaussian seed를 초기화한다.
4. 거리·방향·feature를 읽는 decoder와 explicit medium field를 함께 최적화한다.

합성 GT와 실제 photogrammetry·stereo 기반 supervision으로 MASt3R를 적응한다. 이후 online 지도 최적화가 있으므로 전체를 한 번의 feed-forward 출력으로 설명하면 안 된다.

## 📊 Results

**Source**: [원문 PDF](https://arxiv.org/pdf/2608.22906v1), Table II, PDF p.7.

Real underwater Canyons novel-view rendering. 다른 dataset의 평균이 아니며 PSNR·SSIM은 높을수록, LPIPS는 낮을수록 좋다.

| Method   | PSNR ↑ | SSIM ↑ | LPIPS ↓ |
| -------- | ------ | ------ | ------- |
| ARTDECO  | 31.83  | 0.933  | 0.262   |
| AquaFlow | 34.53  | 0.955  | 0.199   |

SeaThru-NeRF에서는 PSNR이 HI-SLAM2보다 낮은 등 dataset별 trade-off가 있다. 여러 baseline의 offline/streaming 계산 조건도 다르다.

## 💡 Insights & Impact

새 geometry를 추가하는 판단과 medium-aware color 모델을 연결해 누적 mapping artifact를 줄인다.

- 수중 adaptation supervision 중 실제 자료는 추정 geometry를 포함한다.
- 추적·map optimization·medium fitting의 전체 비용을 함께 보아야 한다.

## 🔗 Related Work

- [MASt3R](../foundation/mast3r.md): tracking backbone.
- [Swimm3R](../gaussian-splatting/swimm3r.md): 다른 수중 SfM·splatting 방법.

## 📚 Key Takeaways

1. MASt3R의 수중 적응이 tracking을 담당한다.
2. 지도는 medium과 함께 점진적으로 최적화한다.
3. 한 장면의 rendering 우위를 전 benchmark로 확대하지 않는다.

# 변경 이력

`raw/`의 원본 API 응답과 함께 이 레포의 메타데이터가 언제 어떤 근거로 바뀌었는지 남긴다.
새 논문을 추가하거나 검증을 재실행하면 여기에 한 줄 추가한다.

## [2026-07-20] 신뢰성 전면 점검

`tools/verify_metadata.py` 도입 후 55편 전량을 arXiv + DBLP + Semantic Scholar +
Crossref와 대조했다. 판정: CONFIRMED 41 / LIKELY 12 / PREPRINT 2.

**수정한 것**

- 논문 링크가 전혀 다른 논문을 가리키던 2건
  - `slam3r.md`: arXiv 2404.18774(초전도 뉴로모픽 회로) → 2412.09401
  - `largespatialmodel.md`: arXiv 2410.15403(MMDS 의료 진단) → 2410.18956
- `arxiv.org/abs/TBD` 플레이스홀더 2건 → 실제 ID (`amodal3r` 2503.13439, `styl3r` 2505.21060)
- 프리프린트로 적혀 있었으나 실제로는 등재된 논문 8건
  (dust-gs→ICASSP 2025, styl3r→NeurIPS 2025, rayst3r→NeurIPS 2025,
  test3r→NeurIPS 2025, regist3r→ACM MM 2025, reconx→IEEE TIP 2026,
  spurfies→3DV 2025, dynamic-point-maps→ICCV 2025)
- 수상 표기 10건을 `Venue`에서 `Award` 필드로 분리
- venue 표기법 통일 (`International Conference on 3D Vision (3DV) 2025` → `3DV 2025` 등)
- README 카운트: 실제 55편인데 54로 표기돼 있던 것 등 23곳
- 마크다운 위반 2704 → 192건

**특기: 게재 시 개명된 논문**

`unifying-scene-representation.md`는 arXiv 제목과 RA-L 게재본 제목이 다르다
("Unifying **Scene** Representation and **Hand-Eye** Calibration..." →
"Unifying Representation and Calibration..."). 저자가 arXiv에 journal_ref를 달지
않아 arXiv·DBLP·S2 모두 "프리프린트"라고 답했다. Crossref로만 RA-L 2024
(DOI 10.1109/LRA.2024.3451396, ICRA 2025 발표) 확인. 이 실패 모드를 잡기 위해
파이프라인에 Crossref 단계를 추가했다.

## [2026-07-20] 벤치마크 수치 전수 검증

`tools/verify_benchmarks.py` 신설. `docs/papers/`의 원논문 PDF 58편을
`pdftotext -layout`으로 읽어 문서 표의 수치 **4,758개**를 대조했다.
**637개가 원논문에 존재하지 않았다.**

방법 타당성은 정상 문서로 검증됐다: `dust3r` 100%, `moge` 98.4%,
`slam3r` 91.7%(올바른 PDF 교체 후). 즉 낮은 커버리지는 도구 탓이 아니다.

**확정된 날조 사례**

- `vggt.md` DTU 표: 수치 9개가 전부 틀렸고, 열 이름이 원논문 `Overall ↓` 대신
  `F-Score ↑`로 적혀 있어 **VGGT가 MASt3R에 지는 표**가 돼 있었다.
  CVPR 2025 Best Paper 논문인데도. 원논문 Table 1·2·6으로 교체 → 29% → 100%.
- `vggt.md`의 "Scalability" 표(뷰 수별 메모리 8.2/15.4/28.7/40.6 GB): 원논문에
  해당 표가 없다. 삭제.
- `vggt.md`의 "Camera Pose (RealEstate10K)" AUC@30/@10/@5 표: 원논문은 AUC@30만
  보고한다. AUC@10/@5는 다른 표(2-view matching)의 지표명을 가져다 쓴 것. 삭제.
- `spann3r.md` "Incremental Reconstruction with Spatial Memory" 표: 원논문에 없다.
  처리 시간이 2.3→11.5→23.0→46.0초로 정확히 선형인 것도 측정값이 아니라는 표시.

**PDF 자체가 다른 논문이던 것 3건** (잘못된 링크로 잘못 받아진 것)

| 파일                    | 실제 PDF 내용                  |
| ----------------------- | ------------------------------ |
| `SLAM3R.pdf`            | 초전도 뉴로모픽 회로 자가학습  |
| `LargeSpatialModel.pdf` | MMDS 다중모달 의료 진단        |
| `FlowR.pdf`             | LLM 코드 벤치마크 274종 서베이 |

모두 올바른 논문으로 교체. `slam3r`은 그 결과 0% → 91.7%로 **정상 문서임이 확인**됐다.

**전 논문 표 교체 결과**

37편의 `## 📊 Results`를 원논문 PDF 기준으로 재작성했다. 검증 대상 수치는
4,758 → **8,043개**로 늘었고(원논문의 진짜 표를 대거 복원), 미검출은
637 → **99개(1.2%)**. **85% 미만 논문 0편.**

날조는 수치에 그치지 않았다. **실험 자체가 지어진 경우**가 다수였다:

- `largespatialmodel` — ScanNet 3D detection / S3DIS / 7-Scenes 결과를 보고했으나
  원논문에 이 벤치마크가 없다. 실제는 ScanNet(seg/depth/NVS)과 Replica.
- `dust-gs` — 3-view Mip-NeRF360 / 4-view DTU라고 했으나 원논문은 8-view이고
  DTU를 쓰지 않는다. "8+ dB 개선" 주장의 실제값은 **+2.69 dB**.
- `spann3r` — "Comparison with Batch Methods" 표가 **Fast3R와 비교**한다.
  Fast3R는 Spann3R보다 몇 달 뒤에 나온 논문이다(시간 역전).
- `pref3r` — Tanks & Temples 평가를 보고했으나 원논문은 ScanNet++/ARKitScenes.
- `spars3r` — 존재하지 않는 "SemDUSt3R" baseline과 가구/차량/건물 카테고리.
- `met3r` — 지표 방향이 `↑`로 뒤집혀 순위가 정반대였다(DFM이 최악으로 표시,
  실제로는 최고). `easi3r`·`stereo4d`·`amodal3r`도 원논문에 없는 baseline과 비교.
- `fast3r` — 문서는 Fast3R가 DUSt3R를 **이긴다**고 했으나(1.52 vs 1.74),
  원논문 Table 3은 DUSt3R 1.23 vs Fast3R 1.58로 Fast3R가 정확도에서 진다.
  Fast3R의 기여는 322× 속도이지 정확도가 아니다.

**미출처 배속 주장 정리**

정수라 수치 검증기가 놓쳤던 `N× faster` 주장을 전수 대조했다.
`das3r` 7.5×, `mv-dust3r-plus` 13.8×(원문은 8~14×), `vggt` 45×,
`dust3r` 100×/300×(원문은 배수 미제시)를 제거·교정했다.
`fast3r` 320×/1000×, `mast3r-slam` 4000×/80×, `light3r-sfm` 49×, `odhsr` 75×,
`pref3r` 100×, `pe3r` 9×는 원문 확인됨 — 그대로 두고 출처를 달았다.

**미해결 backlog**

- PDF는 `docs/papers/`에 있으나 문서 미작성: **MoGe-2, Mono3R, RIG3R**
  (RIG3R은 README에서 링크가 깨져 있어 일단 링크만 제거)
- `must3r.md`의 37열 표 — 데이터 유실은 없으나 마크다운에서 판독 불가, 재구성 필요
- 산문 속 파생 주장(비율·개선폭)은 표만큼 체계적으로 검증되지 않았다.
  `verify_benchmarks.py`가 소수만 보므로 정수 주장은 여전히 사각지대다.
- **Mino Universe 편입 미착수.** 이 레포는 Mino Universe에서 관리되고 Obsidian으로
  열람 가능해야 한다. Universe에 galaxy/source로 등록하면 기존 빌드 파이프라인
  (`npm run rebuild:universe`)이 `obsidian-export/`를 생성한다. 별도 Obsidian MCP
  서버를 붙이는 방식이 아니다.
- 벤치마크 검증은 **CI에서 돌지 않는다** — PDF가 gitignore라 GitHub Actions에
  원문이 없다. 표를 건드렸다면 로컬에서 `verify_benchmarks.py`를 수동 실행할 것.

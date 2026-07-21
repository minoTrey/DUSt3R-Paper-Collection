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

## [2026-07-20] 논문 58편 추가 (73 → 131편)

조사된 73편 중 1차로 넣은 15편을 뺀 나머지 58편을 전부 추가했다.
`docs/surveys/` 카테고리를 신설해 서베이·벤치마크·분석 논문 4편을 분리했다
(방법+결과표 전제의 템플릿과 성격이 다르다).

**venue 확정**

2026 학회는 DBLP에 아직 색인되지 않아 GitHub 배지·OpenReview·CVF openaccess·
CVPR/ICLR 공식 사이트를 1차 출처로 삼았다. CONFIRMED 35 / UNKNOWN 18 / PREPRINT 4 / LIKELY 1.

**UNKNOWN 18편은 추측하지 않았다.** `arXiv preprint`로 두고 "1차 출처에서 확인 불가,
재확인 필요"를 Note에 남겼다. 그럴듯한 venue를 채우는 것이 이 레포를 망가뜨린 원인이다.

주요 논문: D4RT(CVPR 2026 **Best Paper + Oral**), Scal3R(CVPR 2026 Highlight),
SAIL-Recon(3DV 2026 Oral), SLAM-Former(ECCV 2026), WorldMirror·EPS3D(ICML 2026).
E3D-Bench는 ICLR 2026 **desk reject**로 확인돼 프리프린트로 확정했다.

**이름 충돌 3건을 분리했다**

`PAGE-4D`(2510.17568) / `VGGT4D`(2511.19971) / `DynamicVGGT`(2603.08254)는 서로 다른
논문이다. PAGE-4D의 arXiv comment가 나머지 둘을 별칭 키워드로 달아놔 혼동하기 쉽다.
각 문서에 명시적 구분 문구를 넣었다.

**검증 도구의 사각지대 2건을 발견해 고쳤다**

- `verify_benchmarks.py`의 수치 정규식이 소수 3자리까지만 봤다. EPS3D처럼 4자리
  (`0.4701`)를 쓰는 논문은 통째로 건너뛰어져 **"검증됨"으로 보였다.** 4자리까지 확장.
  이 수정으로 검증 대상 수치가 12,805 → 25,039개로 늘었다.
- `SKIP_ROW`가 `×`를 포함해, 배속과 정확도를 한 표에 쓴 효율화 논문은 표 전체가
  건너뛰어졌다. 해당 논문들은 표를 정확도/지연으로 분리해 검증 범위에 넣었다.
  **아직 남은 한계다** — `×`가 섞인 표는 여전히 자동 검증에서 빠진다.

**교정 1건**: `g-cut3r`은 UNKNOWN이었으나 PDF 페이지 헤더에 "Published as a conference
paper at ICLR 2026"이 인쇄돼 있어 CONFIRMED로 올렸다. UNKNOWN 전체를 헤더로 재확인했고
근거가 있는 것은 이 1편뿐이었다.

**H1 표기 통일**: 프리프린트 H1이 `(arXiv 2025)`와 `(arXiv preprint (2026-06))`로
갈려 있어 37편을 `(arXiv preprint)`로 통일했다. 정확한 연월은 Venue 필드에 있다.

**서베이 논문의 오류를 발견해 기록했다**

`survey-dust3r-to-vggt`는 Table 1에서 최소 4개 모델을 원논문과 다르게 기술한다
(Fast3R를 pairwise distillation으로, Pow3R를 pose-graph optimization으로,
Spann3R를 sparse attention으로, Align3R를 multi-view aggregation으로).
Table 4의 `τ↓`도 본문이 정의한 inlier ratio와 방향이 반대다.
**조용히 고치지 않고 원문대로 옮긴 뒤 Insights에 문제를 기록했다** — 독자가
잘못된 정보를 전파하지 않도록.

## [2026-07-20] README 전면 재작성 + 검증 사각지대 4건 발견

131편 규모와 현재 SOTA를 반영해 README를 다시 썼다. 그 과정에서 **검증 도구가
통과시킨 것이 검증된 것이 아니었다**는 사실이 연달아 드러났다.

**사각지대 1 — 색인 문서가 검증 범위 밖이었다**

`verify_benchmarks.py`가 `docs/*/*.md`만 보고 README를 건너뛰었다. 개별 문서에서
걷어낸 날조 수치가 README 대표 비교표에 그대로 살아 있었다
(DUSt3R DTU 2.677/0.805, MASt3R 0.403/0.344, VGGT 1.338/1.896 — 열 이름도 `F-Score ↑`로
지어냈고 그 결과 VGGT가 실제로는 이기는 비교에서 지는 것처럼 보였다).
→ `tools/verify_index_numbers.py` 신설. README의 모든 수치가 논문 문서에 실재하는지
검사하고 CI에 편입했다. 색인은 1차 출처가 아니다.

**사각지대 2 — 커버리지 임계값이 표 단위 날조를 가렸다**

85% 임계값은 총량 기준이라, 수치가 충분히 많은 논문은 표 하나가 통째로 날조여도
통과했다. `pi3`(95.3%), `lora3d`(90.8%), `pow3r`(90.4%), `moge`, `dens3r`,
`mv-dust3r-plus`, `must3r` 7편이 이렇게 빠져나갔다. 미검출을 줄 번호로 군집화해
재검출한 뒤 전부 교정했다.
`2.677/0.805/0.403/0.344` 조합이 pi3·lora3d·pow3r 3개 문서에 동일하게 나타났다 —
출처는 Pow3R Table 4의 DUSt3R 행이고, 나머지 두 문서는 그 숫자를 빌려 표를 지어냈다.
`must3r`는 O(1) 메모리라고 주장했으나 원논문 §3.4는 "grows **linearly**"라고 한다.

**사각지대 3 — 정수 열은 아예 안 본다**

수치 정규식이 소수만 잡아 `dens3r`의 `δ<22.5°`·`δ<30°` 두 열(약 50개 값)이
날조인 채 통과했다. `×`가 섞인 행도 `SKIP_ROW`에 걸려 표 전체가 건너뛰어졌다.
**여전히 남은 한계다.**

**사각지대 4 — 소속(Institution)은 한 번도 검증된 적이 없다**

어떤 API도 소속을 제공하지 않아 전부 손으로 채워진 필드였다. PDF 1페이지와
대조하자 **15편 중 12편이 틀렸다**:

| 논문             | 문서 주장                           | 실제                                      |
| ---------------- | ----------------------------------- | ----------------------------------------- |
| `slam3r`         | University of Freiburg, ETH Zürich  | Peking University, HKU, Aalto, VIVO       |
| `light3r-sfm`    | Meta FAIR, University of Michigan   | NVIDIA, Vector Institute, Toronto         |
| `lora3d`         | ETH Zürich, DisneyResearch\|Studios | NVIDIA, MIT, Harvard, Georgia Tech 등 7곳 |
| `pow3r`          | MIT CSAIL, Google Research          | UCL, Naver Labs Europe                    |
| `pi3`            | UC Berkeley, Google Research        | Shanghai AI Lab, ZJU, SII                 |
| `mv-dust3r-plus` | Toronto, Shanghai AI Lab            | Meta Reality Labs, UIUC                   |

잘못된 소속은 기여를 엉뚱한 기관에 귀속시킨다. **부분 일치하는 나머지 116편은
여전히 미검증이다** — 이 검사는 토큰이 하나도 안 겹치는 경우만 잡는다.

**README 재작성**

- 리더보드를 **의도적으로 넣지 않았다.** 논문마다 평가 프로토콜이 달라
  (GT 카메라 유무, aligned/metric scale, per-scene/평균) 표에서 떼어낸 숫자는
  의미를 잃는다. 모델 간 비교는 `docs/surveys/`의 벤치마크 논문을 쓰라고 안내했다.
- "Verification이 보장하지 않는 것"을 명시했다 — CI 미실행, 정수 미검증,
  커버리지의 총량 성격, 산문의 낮은 검증 강도.
- `docs/surveys/` 카테고리를 색인에 추가했다 (`update_stats.py`는 기존 항목의 수만
  고치지 새 카테고리를 넣지 않는다).

**`update_stats.py` 자체가 README를 망가뜨리고 있었다**

일반 치환 규칙(`N papers` → 총계)이 연도 히스토그램 안까지 들어가 2024·2025를
나란히 "131 papers"로 덮었다. 히스토그램 재생성 정규식은 줄 끝 주석 형식
("1 paper (CroCo - NeurIPS)")을 못 맞춰 **한 번도 작동한 적이 없었다.**
→ 생성 영역을 `<!-- GENERATED:histogram -->` 마커로 격리하고, 마커 안에서는
치환하지 않도록 고쳤다. 일부러 값을 망가뜨려 자가 치유를 시험해 확인했다.

**최종 상태**: 수치 25,143개 중 미검출 5개(0.02%) → 그 5개도 교정해 0건.
`dust-to-tower`는 DTU/LLFF 표가 통째로 날조였고(원논문은 T&T/MipNeRF360/CO3D),
`slam3r`은 TUM RGB-D 표와 ORB-SLAM3 비교가 둘 다 원문에 없었다.

## [2026-07-21] 남은 backlog 3건 처리

**소속 전수 재검증 (부분 일치까지)**

어제는 토큰 무교집합 15편만 봤다. 오늘 부분 일치(핵심어 절반 미만)까지 넓혀
131편을 전부 대조하니 4편이 더 틀렸다:

- `vggt` — "Meta GenAI, Zhejiang" → **Visual Geometry Group, University of Oxford, Meta AI**
  (컬렉션 대표 논문의 소속이 틀려 있었다)
- `pomato`, `largespatialmodel`, `lingbot-map` 교정
- `align3r`의 `NTU`를 "National Taiwan University"로 확장한 것을 되돌렸다 — 원문에
  근거가 없는 추측이었다
  이번 세션 소속 검증 누계: **29편 점검 중 16편 교정.**

**UNKNOWN venue 재확인 (하루 뒤)**

18편 중 3편이 색인됐고(dggt·ilrm → CVPR 2026, segvggt → ECCV 2026), 5편은
자체 1차 출처가 프리프린트임을 확인했다(deja-view·horizonstream·nopo4d·vipe·s-must3r).
남은 UNKNOWN 10편은 여전히 1차 출처가 없다.
함정: `dynamicvggt`(2603.08254)는 `wzzheng/DVGT`(CVPR 2026, 2512.16919)와 다른 논문이다.

**검증 사각지대 3건 중 2건을 도구에서 닫았다**

`verify_benchmarks.py`:

- **`×` 혼재 표.** `SKIP_ROW`가 `×`를 배속으로 오인해, 실제로는 ablation
  체크마크(`| × | ✓ |`)인 행까지 통째로 버렸다. 그 행의 정확도 수치가 검증에서
  빠져 있었다. 숫자에 바로 붙은 배속(`4.5×`)만 셀 단위로 제외하도록 고쳤다.
  → 검증 대상 25,143 → 26,255개(+1,112), 추가분 전부 통과.
- **정수 지표.** `--int` 모드 추가. mAP·FPS·δ<11° 등 정수 열이 통째로 사각지대였다
  (dens3r의 정수 열 2개가 그래서 날조인 채 통과했었다). doc·pdf 양쪽에서 정수를
  대칭으로 모으고, 해상도(`N×N`)·콤마 천단위·연도를 노이즈로 제거.
  → 정수 포함 27,568개 대조, 미검출 5개(0.02%) 전부 정당한 오탐, **날조 0.**

세 사각지대(색인·×·정수)를 모두 검사한 결과 새 날조는 없었다.
남은 한계: 산문 속 정수 배속 주장(`45× faster`)은 여전히 표가 아니라 문장이라
자동 검증 밖이다. `--int`는 표 안의 정수만 본다.

## [2026-07-21] 산문 배속 주장 검증 — 마지막 사각지대

`45× faster`, `3× reduction` 같은 배속·배수 주장은 표가 아니라 문장에 있고,
게다가 파생 배수라 표에도 없어 `verify_benchmarks.py --int`로도 안 잡혔다.
`tools/verify_prose_claims.py`를 신설해 이 마지막 사각지대를 메웠다.

원리: 산문에서 성능 키워드(faster·speedup·reduction 등)를 동반한 배수를 뽑아,
그 값이 원논문 PDF에 배속 문맥으로 존재하는지 본다. 없으면 파생값이거나 날조다.

**결과: 배속 주장 69개(파생값 12개 제외) 전수 대조, 날조 0.**

원문 리터럴이 아닌 6개를 개별 확인한 결과 전부 근거 수치가 인용된 정당한
파생값이었다 (artdeco 443/5.33≈83, pi3 0.033/0.003≈11, mast3r-slam 2000/0.5=4000 등).
s-must3r 한 곳만 근거 수치(0.251 vs 1.580)를 문장에 인라인으로 추가했다.

도구 제작 중 잡은 정규식 버그 2건 (기록: 같은 실수 반복 방지):

- `\b`가 `×` 뒤에서 단어경계를 못 만든다. `320×`의 `×`가 이미 비단어문자라
  `[×x]\b`는 매칭 실패. `-fold`/`times`에만 `\b`를 붙여야 한다. 이걸 놓쳐
  실재하는 `320×`이 전부 오탐(62/83)으로 떴었다.
- pdftotext가 `49×`를 `49 ×`로 띄우거나 개행으로 쪼갠다. 공백을 정규화한 뒤
  스캔해야 한다.

파생값 인지: 같은 문장에 근거 수치 두 개가 인용돼 있으면(`(0.003 vs 0.033)`,
`58 s vs 11 min`) 저자가 계산을 드러낸 것으로 보고 통과시킨다. 12개 문장이
이렇게 통과했고 전부 실제 근거를 동반함을 확인했다.

이로써 이번 세션에서 발견한 검증 사각지대(커버리지 임계값·색인 미검사·소수
자릿수·× 혼재·정수·소속·산문 배속) 7건을 전부 닫았다. 남은 것은 학회 색인을
기다리는 UNKNOWN venue 10편뿐이다.

## [2026-07-21] 정리 상태 전면 감사 — 색인층·상호링크 복구

개별 수치·메타데이터는 깨끗했지만 "논문이 잘 정리됐는지"를 통째로 본 적이 없어
다른 각도로 전면 감사했다. 색인층과 상호연결이 55편 시절에 멈춰 있었다.

**색인층이 낡아 있었다 (73편 추가 때 갱신 누락)**

- `papers-list.md` — "Total: 55", venue 오류(MASt3R-SLAM을 arXiv 2024로 표기 등),
  링크 없는 순수 텍스트. README 배지(Papers-131)가 이걸 가리키는데 열어보면 55편.
- 카테고리 README 8개 — 본문 리스트가 옛날 논문만. reconstruction은 실제 64편인데
  "18 papers", robotics는 7편인데 "2 papers".

근본 원인: 이 색인들이 손으로 관리됐다. → **자동 생성으로 전환.**
`tools/build_papers_list.py` 신설: papers-list.md를 131편 전체에서 재생성하고,
각 카테고리 README에 `<!-- GENERATED:paper-index -->` 마커로 감싼 전체 목록을
삽입한다(손큐레이션 테마 리스트는 유지). CI에 `--check` 편입. 멱등성 확인.

**venue 표기 규약 위반 정리 (목록 생성이 드러냄)**

- 축약 안 된 venue: mast3r-sfm·spann3r의 "International Conference on 3D Vision" → 3DV
- 월 누락 프리프린트 10편: arXiv ID 앞 4자리(YYMM)에서 월 보정
- 두 venue 병기: align3r "CVPR 2025 | arXiv preprint" → CVPR 2025
- 서술형 날짜: adapt3r "submitted March 2025, revised May" → (2025-03),
  splatt3r "(August 2024)" → (2024-08)
- 프리프린트 H1 중첩 괄호 35편 정리 → (arXiv preprint)

**Related Work 상호링크 58편 누락**

기존 55편 + backlog 3편은 Related Work에서 다른 논문을 이름으로만 언급하고 링크가
없었다. 서베이의 핵심 가치인 상호연결이 빠져 있었다 (vggt가 DUSt3R·MUSt3R·Fast3R·
Test3R를 언급하는데 전부 링크 없음). 원문 근거로 링크를 걸었다: **58 → 3편.**
남은 3편(adapt3r·amodal3r·spurfies)은 Related Work가 실제로 다른 컬렉션 논문을
언급하지 않아 억지 링크를 달지 않았다. pi3·pow3r은 부실/자리표시자였던 Related Work를
원문 기준으로 새로 썼다(pow3r은 DUSt3R 계승·MASt3R와 상보·Spann3R/MonST3R와 직교).

**감사에서 확인된 정상 항목** (오탐이었던 것):

- 문서 수 131 정확, arXiv ID 중복 0, TL;DR 전부 충실, H1 제목 전부 원문과 일치,
  pos3r의 arXiv 없음은 CVF 링크라 정상.

상호링크 추가는 순수 링크 작업이라 벤치마크 검증 26,255개 미검출 0 유지.

## [2026-07-21] 검증 시스템 구축 + 잔여 오류 감사 + 자동 발굴 틀

"오류 없는 게 확실한가?"에 답하기 위해, 지금까지 안 보던 계층을 스캔하고
그걸 재사용 가능한 시스템으로 고정했다.

**PART A — 잔여 오류 감사 (안 보던 5계층)**

- A1 문서 간 참조 정합성: 이상 0 (venue 인용이 정본과 일치)
- A2 수치 귀속: 이상 0 (타 논문 수치를 잘못 옮긴 사례 없음)
- A3 저자 명단: 1건 — dens3r "Lyu" → 원문 표기 "Lv" (로마자 변형).
  유니코드 성 오탐 4건은 원문 일치 확인
- A4 외부 링크 생존: 286개 중 6개 죽음 → 전부 수정
  (largespatialmodel VITA-Group→NVlabs/LSM, reloc3r/fast3r 죽은 HF→github,
  croco naverlabs→github, slam3r/spars3r 죽은 project page 제거)
- A5 중복·유령: 이상 0

**PART B — 검증 시스템 (도구 12종)**

- `build_fact_cards.py`: `raw/facts/<slug>.json` — 문서 간 대조의 단일 소스
- `verify_crossref.py`: A1 참조 venue(CI 차단) + A2 수치 귀속(경고)
- `verify_links.py`: 링크 생존 + 30일 캐시 (오프라인 CI도 지난 죽은 링크 잡음)
- `verify_all.py`: 통합 러너. --fast(9종·CI) / --full(12종·PDF·라이브).
  매 실행 끝에 '검증 안 되는 것(사각지대)'을 항상 출력.
- CI에 fact_cards·crossref·links 편입.

**PART C — UNKNOWN venue 10편**: wint3r만 PREPRINT 확정, 9편 UNKNOWN 유지.

**PART D — 자동 발굴 틀 (뼈대)**

`discover_papers.py`가 앵커 논문(DUSt3R·VGGT·MASt3R·π³·CUT3R·Fast3R) 피인용 +
arXiv 키워드 합집합으로 신규를 발굴. 3R 이름이 아니어도 DUSt3R를 초석으로 하면
잡힌다. 최초 실행 160편 발굴(비-3R 117편), 기존 130편 중복 0.
`discover.yml`(주간 cron)이 신규 있으면 이슈 게시. 문서화는 수동 승인.

**정직한 상태**: 결정론적 계층(구조·수치·색인·참조·링크)은 시스템화됐다.
남은 사각지대는 verify_all.py가 매번 명시한다 — 의미 정합(TL;DR↔본문),
수치 귀속의 확정 판단, UNKNOWN venue는 여전히 사람/시간이 필요하다.

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

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

## [2026-07-21] 대규모 확장 — 발굴 133편 문서화 (131 → 264편)

`discover_papers.py`가 발굴한 160편 후보를 하나씩 검토·문서화했다. 짧게 넘기지
않고 각 논문을 원문 대조하며 정확히 정리하는 데 집중했다.

**선별 (160 → IN 133)**

160편 전부 초록을 개별 판정: IN 128 / OUT 23 / BORDERLINE 9. 경계 9편은 초록을
다시 읽어 재판정(IN 5 / OUT 4). 최종 IN 133편. OUT은 recon이 도구인 것
(내비게이션·VLA policy·VINS·데이터셋 논문 등). candidates/triage.tsv에 전 판정 기록.

**문서화 (3 웨이브, 133편)**

carte고리별 14배치로 나눠 서브에이전트가 논문 하나하나 작성. 규약:

- 모든 수치를 원문 PDF와 대조 (candidates/pdftext). 못 찾으면 적지 않음.
- 지표명·화살표 방향 원문 그대로. 논문이 지는 지점도 기록(유리한 행만 고르지 않음).
- 그림에만 있는 수치는 "그림 N, 수치 미인쇄"로 표기, 전사 안 함.
- 12열 초과 표는 분할. slug이 문장/일반명사면 실제 약칭으로 재명명
  (learning→c4g, hsr-oneworld→show, global-sfm-ff→gluemap, text-to-3d→vist3a 등).

venue: arXiv comment·PDF 헤더로 확정된 것(NeurIPS 2025·CVPR/ECCV/ICLR/ICML 2026,
RSS 2026 등)은 LIKELY, 나머지는 PREPRINT. lgtm·vist3a는 PDF 헤더 "Published as a
conference paper at ICLR 2026" 근거로 격상.

**검증 (전 264편)**

- 벤치마크: 수치 44,055개(소수) / 46,234개(정수 포함) 미검출 0~5(0.01%), 85% 미만 0편.
- 구조 264편 정합 / markdownlint 0 / prettier / 색인·카운트·papers-list·사실카드 정합.
- 문서 간 참조(A1) 정합. 상호링크 전 신규 문서에 반영.

**검증 중 잡은 오류**

- `flat.md` "10× fewer vertices" → 실제 7dB 비교의 근거는 4M/0.5M=**8×**였다.
  10×는 다른 비교(2DGS)를 혼동한 것. 8×로 정정하고 근거 병기.
- `lite3r`의 모순된 "2.71× 메모리"(표는 최대 2.33×) 제거.
  이번에도 원문 대조가 파생값의 계산 오류를 잡았다.

도구: `discover_papers.py`(발굴), verify_prose_claims에 콤마 천단위 근거 인식 추가.
MD059(약칭 링크 텍스트 오탐) 비활성화.

## [2026-07-21] 카테고리 README 전면 자동화 — Featured + 낡은 하드코딩 제거

앞서 "Complete Paper List (N)" 거짓 제목을 "Featured Papers"로 바꿨지만, 그건
**반쪽 수정이었다.** 내용을 안 건드려서 Featured가 여전히 옛 논문(pi3·VGGT 등)만
담고 신규 133편을 하나도 반영 못 했다. 게다가 각 README에 낡은 하드코딩 서술
("Key Research Directions")과 **검증 안 된 벤치마크 표**가 방치돼 있었다 —
reconstruction README의 "DUSt3R 2.677 / VGGT 1.338" 은 루트 README에서 이미
날조로 판명해 지웠던 바로 그 수치였다.

**제대로 된 수정:**

- **Featured 자동 생성**: 손큐레이션 대신 검증 가능한 신호로 자동 선정 —
  수상(Best Paper/Oral/Highlight/Spotlight) → 게재 확정(CONFIRMED/LIKELY) 순.
  순수 프리프린트는 제외. award/venue는 원문 대조를 거친 사실 카드에서 온다.
  이제 reconstruction Featured = VGGT(Best Paper)·DA3·VGGT-Ω(Oral) 등 최신 반영.
- **낡은 하드코딩 제거**: 각 카테고리 README를 [제목 + Overview + 자동 Featured +
  자동 전체목록]으로 재구성. "Key Research Directions", 검증 안 된 벤치마크 표,
  "Getting Started" 논문 나열 등 손큐레이션·낡은 표를 전부 제거.
  카테고리 README의 하드코딩 날조 수치(2.677 등) 0개.

**재발 방지**: build_papers_list.py --check 가 Featured 블록과 전체목록 블록의
정합을 CI에서 감시한다. 손상시켜 확인함 — 어긋나면 non-zero.

교훈: 개별 문서를 아무리 검증해도 그 위의 색인·표시 층(카테고리 README)이
손으로 관리되면 낡고, 날조 수치가 그리로 새어들어간다. 표시 층까지 자동 생성으로
옮겨 구조적으로 막았다.
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

## [2026-07-28] 그림 203편 추가 + 편입 완료 반영 + 세션 연속성 정비

**핵심 그림 추가 (203편).** 논문 정리 페이지에 아키텍처·메소드 그림이 없어 글만 있는
반쪽이었다. 기존 54편은 저자 그림을 핫링크했으나 신규 133편엔 빠져 있었다.

- arXiv HTML(`arxiv.org/html/<id>`)에서 캡션 스코어링으로 메소드 그림 선택 → **195편**.
  `tools/fetch_figures.py`. 삽입된 고유 이미지 URL 207개 전수 렌더링 확인(HTTP 200,
  죽은 이미지 0). GitHub camo 프록시도 200 반환 확인 — 실제 렌더링됨.
- arXiv HTML 없는 논문은 project page og:image/teaser + GitHub README 그림으로 폴백 →
  **8편**(human3r·v-dpm·artsplat·structsplat·c3po·sparse-vggt·vipe·eps3d).
  `tools/fetch_figures_fallback.py`. 로고·아이콘 오답 배제(human3r는 og:image가 로고라
  실제 `fig_pipe.png`로, sparse-vggt는 성능차트 대신 아키텍처로 교정).
- 못 찾은 **5편**(page-4d·vggt-omega·lexi-sg·e3d-bench·survey-dust3r-to-vggt): 대부분
  2026 arXiv라 HTML 미생성 + project page에 접근 가능한 그림 없음. HTML 생기면 자동 처리.
- 전부 핫링크(리포에 바이너리 저장 안 함). markdownlint 0 / 구조 264편 정합.

**"안 보인다" 오진 정정.** 사용자가 GitHub에서 그림이 안 보인다고 보고 → 원인은 (1) 처음엔
삽입 후 커밋·push 누락, (2) push 후엔 브라우저 캐시. camo URL 직접 검증(200·image/png·전량)으로
렌더링 정상 확인. 교훈: 삽입=완료 아님. 커밋·push까지 확인하고 보고할 것.

**backlog 갱신 (위 2026-07-21 항목의 미해결 목록 supersede):**

- ✅ **Mino Universe 편입** — 2026-07-22 완료. `galaxies/dust3r-paper-collection/`으로
  등록되고 obsidian-export까지 반영·푸시됨.
- ⏳ 여전히 열림: 그림 5편(위), `must3r.md` 37열 표 재구성, UNKNOWN venue 색인 대기,
  벤치마크 검증 CI 미실행(PDF gitignore).

**세션 연속성 정비.** 새 세션이 낡은 상태(55편·편입 미착수)로 출발하던 문제를 잡음:
내 메모리 파일·MEMORY.md 인덱스·galaxy.yaml notes를 264편/편입완료/그림 상태로 최신화.

## [2026-10-15] 후보 상태 대조와 원문 검토 첫 묶음

기준 main은 `d94397750e29eb3beb436a61b8657efce642b668`이다.
별도 clone의 `codex/verified-curation-2026-10-15` 브랜치에서 작업했다.
기존 체크아웃과 사용자 변경은 건드리지 않았다.

### 후보와 추가 논문

초기 160건의 IN 133건·OUT 27건을 보존했다. `triage.tsv`·`worklist.tsv`는 그대로다.
후속 79건은 시작 시 기존 문서와 정확한 arXiv ID 일치가 없었다.
이번 3편을 포함해 **added 136 / rejected 27 / new 76**이다.
WAT3R `2607.21023`·Scal3R `2609.04201`는 다른 ID의 동명 후보로 남겼다.
제목만으로 중복 처리하지 않았다. 과거 제외 사유는 기록에 없고, 남은 76건의 본문·관련성은 미검증이다.

- **Slot3R** (`2610.12282v1`): 공간 주소와 상태 병합을 분리하는 Point3R 메모리.
  읽기 예산·전체 저장량·전체 시퀀스 선인코딩·metric depth 악화 조건을 구분했다.
- **ReVar3R** (`2610.07883v1`): pointmap 정렬 후 불확실성을 계산한다.
  정답 불필요 Core와 보류 정답이 필요한 Full, 실패 조건과 추가 추론 비용을 구분했다.
- **VGGT-Bridge** (`2610.06594v1`): coarse skip edge·역순 anchoring·loop-aware 선택.
  이동 ATE와 다른 지표를 구분하고 SwiftVGGT 대비 비용 증가를 기록했다.

S2는 HTTP 429를 반환했다. 검증기는 앞의 두 편에 `PREPRINT?`를 반환했다.
문서에는 venue `UNKNOWN`으로 기록했다. VGGT-Bridge는 arXiv의 ACCV 2026 채택 주장에 따른 `LIKELY`다.
독립 proceedings 확인 전이다. 원본 응답은 `raw/curation_metadata_2026-10-15.json`에 있다.

### 기존 요약과 관리 도구

- **DUSt3R**: CroCo 자기지도 사전학습과 3D 지도 학습을 구분했다.
  Global alignment를 복원하고 근거 불명 40 ms 주장을 제거했다.
  Localization의 정답 focal, 깊이 평가의 median 정렬·1.03 threshold·단위를 명시했다.
- **MASt3R**: 입력·출력·descriptor matching을 보완했다.
  무조건적인 metric 정확도·최초·보장 표현을 줄이고 원문 평가 조건을 붙였다.
- **VGGT**: DTU로 잘못 표기한 ETH3D Table 3을 정정하고 DTU Table 2를 별도로 복원했다.
  Attention ablation을 Table 5로 정정했다. Tracking·principal point·선택적 BA·속도 조건을 설명했다.
  arXiv와 CVPR 출판 PDF 모두에서 데이터셋 귀속을 확인했다.
- **MUSt3R**: 47.9 cm ATE와 FPS 혼동을 정정했다. V100 VO와 A100 점군 속도를 분리했다.
  중복·다단·33–37열 표를 좁은 표와 원문 보충 표 참조로 교체했다.
  메모리 증가와 전체 계산량을 구분하고 공식 raw 그림 경로를 확인했다.
- 템플릿 `Institutions`를 `Institution`으로 통일하고 `Verification`을 필수화했다.
  핵심 세 편 외 누락 33편은 **2026-07-20 캐시 판정의 필드만 복원**했다. 새 venue 검증이 아니다.
- 기존 생성기로 267편 목록·카테고리·통계·사실 카드를 재생성했다.
  히스토그램은 현재 Overview의 CONFIRMED venue 연도만 센다. arXiv 제출 연도와 낡은 캐시의 덮어쓰기를 제외했다.
- Windows의 경로 구분자·Markdown LF를 맞췄다. 없는 `.claude/AGENTS.md` 참조와 `--fast` 안내를 제거했다.
  `verify_all.py`는 현재 Python을 사용한다. 후보 대조 스크립트와 안전성 검사를 추가했다.
- 컬렉션의 MIT 참조 대상 `LICENSE`는 없고 `package.json`은 ISC를 선언한다.
  충돌 사실만 기록했다. 라이선스 조건을 새로 지정하지 않았다.

### 검증과 잔여 범위

`raw/curation_evidence_2026-10-15.json`에 PDF 버전·SHA-256·검토 표·수동 예외를 기록했다.
`raw/curation_validation_2026-10-15.json`에 검사 범위와 한계를 기록했다.

- `verify_all.py` 오프라인 10개 검사 통과. 구조·lint·Prettier·후보·통계·목록·색인·사실 카드·교차 참조·캐시 링크.
- 후보 대조 unittest 7개, 히스토그램 조건 4개, CI 플레이스홀더·내부 Markdown 링크 검사 통과.
- 변경 7편의 PDF 수치 검사 `--int`: **329개 중 326개 자동 일치**.
  DUSt3R `0.462`·`0.351`, MUSt3R `38.1G`는 추출/정규식 미검출이다. PDF 표에서 시각적으로 확인했다.
- 산문 배속 패턴 검사는 통과했지만 인식한 주장은 0건이다. 산문 전체의 정확성 보장이 아니다.
- 변경 논문·그림·공식 조건 문서 링크 19개가 HTTP 200을 반환했다. 전체 저장소 라이브 재검사는 아니다.

기존 260편 요약 전체의 의미·수치를 재검증하지 않았다. 실험을 재현하지 않았다.
주간 discovery와 소수 후보의 원문 검토·PR을 연결하는 운영안은 `candidates/README.md`에 제안만 남겼다.
Workflow·일정·자격 증명·권한·배포·main은 변경하지 않았다.

## [2026-10-15] 후속 후보 원문 분류와 추가 묶음 1

사용자 후속 승인에 따라 76개 후보 전부의 원문 PDF를 확보하고 문제·방법·평가를 읽어 관련성을 분류했다.
결과는 포함 69 / 제외 7 / 접근 불가 0이다. 동일 arXiv ID의 기존 문서 중복은 없었다.
WAT3R/Wat3R와 두 Scal3R는 저자·방법이 다른 별도 논문이다.
버전·SHA-256·분류 근거·처리 상태는 `candidates/review-2026-10-15.json`과 생성 Markdown에 남긴다.
정량 결과 검증은 분류와 별도 단계다. 범위 밖 7편은 삭제하지 않고 이유를 보존해 rejected로 정리했다.

첫 묶음으로 Self-Geometry, Info3R, GeoCond, Confidence Audit, When Wider Views Fail, RoMa-Ω를 추가했다.
실제 원문 버전은 각각 v2, v1, v1, v3, v1, v1이다.
입력·출력·방법·학습/추론 조건·원문 표·실패 사례를 기존 일곱 섹션에 기록했다.
특히 Self-Geometry의 데이터셋별 악화, GeoCond gate의 FF baseline 대비 OOD 손실,
Confidence Audit의 calibration 한계와 Wide Views 평가의 pseudo-reference 편향을 명시했다.

PDF 표 수치 `--int` 검사는 6편 74개 모두 일치했다. 후보 상태 안전성 테스트 9개를 통과했다.
`raw/curation_expansion_2026-10-15.json`과 `raw/curation_expansion_batch1_benchmarks.json`이 근거다.
현재 컬렉션 273편, 큐 added 142 / rejected 34 / reviewed 63이다. 작성 대기는 실제로 63편이다.
이 묶음도 인덱스·카테고리·사실 카드를 생성하고 오프라인 suite를 실행한 뒤 push한다.
기존 후보 수집 GitHub Actions·main·권한·배포는 변경하지 않는다.

## [2026-10-15] 후속 요약 묶음 2

추가 문서: ffvo, amb3r-slam, blast3r, f2slam, pow3r-slam, unisim-slam.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 46개가 모두 일치했다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 57편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 3

추가 문서: geoff3d, grf-recon, just3r, meow, on-the-fly3r, scal3r-query.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 31개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 51편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 4

추가 문서: g-ray, gekko, ott3r, vggt-prime, densitok, vggt-gs-slam, mvap-g.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 46개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 44편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 5

추가 문서: uni4r, flexsplat, roadvggt, swimm3r, wat3r-feedforward, iggt4d.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 48개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 38편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 6

추가 문서: human-aware-multiview, 2xplat, nemosplat, georay, aquaflow, groupforward.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 35개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 32편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 7

추가 문서: avsplat, voxeltto, xpos3r, fire3d, noctif3r, samv-dust3r.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 48개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 26편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 8

추가 문서: wildhsr, tele360, colon3r, cggt, davio, physvggt.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 38개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 20편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 9

추가 문서: egofound3r, grapesplat, topometric-ff3d, map-det3d, mv2gf, relationvggt, s4vy.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 39개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 13편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 10

추가 문서: gauge, rogsw4rld, aesplat, skyreg, spoon, rigor, panoseg3r.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 38개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 6편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 후속 요약 묶음 11

추가 문서: 4d-hof, deltasplat, freeinpaint, gator, z3d, mirage.
원문 방법·입출력·평가 조건·한계를 읽고 기존 일곱 섹션으로 작성했다. PDF 수치 대조 32개를 확인했다. 자동 미검출은 보고서의 manual_verification에 원문 위치와 확인 근거를 따로 남긴다.
실험을 재현한 것은 아니다. 출판 venue는 독립 확인 전이므로 UNKNOWN을 유지했다. 요약 대기 포함 후보는 0편이다.
생성 스크립트로 색인·카테고리·통계·사실 카드를 갱신하고 구조·링크·린트·서식 suite를 검증한 뒤 묶음별 커밋과 원격 CI를 확인한다.

## [2026-10-15] 전체 후보 처리 완료와 README 탐색 개편

기존 264편에 새 요약 72편(첫 묶음 3편 + 후속 69편)을 추가해 총 336편이다.
후속 76편은 포함·요약 완료 69편 / 범위 제외 7편 / 보류·작성 대기 0편으로 마쳤다.
초기 160편의 triage 결정은 보존했다. 전체 큐는 added 205 / rejected 34 / new 0 / reviewed 0이다.
동명 WAT3R와 Scal3R는 저자·방법·arXiv ID를 대조해 별도 문서로 추가했다.

후속 69편의 PDF 표 숫자 475개 중 470개는 자동으로 일치했다.
JUSt3R의 선행 0 없는 표기 때문에 미검출된 5개는 PDF Table 3을 렌더해 직접 확인했다.
최초 원문 검토 7편의 329개와 합하면 총 804개이며, 자동 대조 796개와 시각 확인 예외 8개다.
자동 수치 출현은 해당 표의 지표·단위·입력 조건이 맞다는 증명이 아니므로 방법·protocol을 따로 읽었다.
실험을 실행하거나 재현하지 않았다. 새 후속 문서의 venue는 독립 색인 확인 전이므로 UNKNOWN이다.
Colon3R의 기관명은 원문에 없어 미확인 상태를 명시했다.
기존 문서 전체와 과거 제외 27편을 새로 내용 검증한 것은 아니다.

README는 개념도, 입문 경로, 질문별 분야 탐색, 날짜가 붙은 selected additions, 전체 분야,
CONFIRMED-only 연구 분포와 검증 한계 순서로 정리했다. 원본 SVG는 실제 복원 결과가 아닌 개념도다.
GitHub 공식 Markdown API가 HTTP 200으로 네 표와 이미지 태그를 렌더했다.
탐색 링크는 ASCII heading으로 맞춰 네 목적지를 대조했다. API는 heading ID를 출력하지 않으므로
브라우저 안의 실제 클릭 검증과 구분한다. SVG는 720px·360px에서 텍스트·화살표·경계를 직접 확인했다.
렌더러의 상속 스타일 차이로 생긴 글자 위치 문제를 개별 text 속성으로 수정했다.
Computer-use 런타임 시작 오류로 실제 GitHub 밝은·어두운·좁은 화면 스크린샷은 확인하지 못했다.
`raw/readme_render_validation_2026-10-15.json`에 성공한 검사와 차단 범위를 구분해 기록했다.

로컬 suite는 내부 링크·대소문자 검사까지 12개이며 전부 통과했다. 회귀 테스트 16개도 통과했다.
실제 Prettier round-trip 전후 후보 표 76행의 셀·링크·사유·본문이 같음을 확인했다.
상태·링크·사유·행·본문을 바꾼 fixture는 여전히 실패한다. 검사 허용 범위는 표 padding뿐이다.
두 번째 확장 묶음의 원격 CI가 잘못된 내부 경로를 검출했고, 이후 커밋에서 경로와 로컬 누락 검사를 수정했다.
이후 묶음들의 원격 consistency·markdown 작업은 통과했으며 최종 push의 상태도 별도로 확인한다.
Discovery Actions·main·배포·권한·자격 증명·라이선스 조건은 변경하지 않았다.
완료 집계와 한계는 `raw/curation_completion_2026-10-15.json`에 기록했다.

## [2026-10-15] README 시각 디자인 보완

입문자가 첫 화면에서 읽기 경로를 찾도록 원본 크림·숲색 SVG 배너와 간결한 탐색줄을 추가했다.
배너는 겹치는 이미지 평면, 카메라 광선, 공통 3D 공간의 개요도이며 실제 복원 결과가 아니다.
외부 저장소의 그림·디자인 자산을 복제하지 않았다. 짧은 주요 탐색줄과 접힌 상세 목록의 원칙만 참고했다.
대표 네 편은 목적과 한국어 요약·논문·코드 링크가 있는 2열 표로 배치했다.
최근 정비 요약은 네 편을 골랐고, 전체 분야·문서 수와 CONFIRMED-only 연도 분포는 접힌 목록으로 유지했다.
제목·핵심 설명·탐색 링크는 실제 Markdown 텍스트로 남겨 이미지 없이도 접근할 수 있다.
기존 카테고리·인덱스 생성 형식과 검증 한계는 보존했다. 논문 내용과 PDF 수치 근거는 바꾸지 않았다.

배너는 1200·600·360px, 입력→출력 도식은 720·360px로 렌더링해 확인했다.
360px 배너의 보조 문구는 작아지므로 필수 정보는 이미지 밖 텍스트로 제공한다.
실제 GitHub 브라우저 화면 검사는 computer-use 초기화 오류로 여전히 막혀 있다.
GitHub 공개 Markdown API 결과와 확인 범위는 `raw/readme_render_validation_2026-10-15.json`,
원본 자산·색·구성 근거는 `raw/readme_design_validation_2026-10-15.json`에 기록했다.

디자인 변경 뒤 기본 오프라인 검사 12개가 모두 통과했고 GitHub Markdown API는 HTTP 200을 반환했다.
표 4개·접힌 영역 3개·탐색 대상 4개를 확인했다. 실제 브라우저 클릭 검사는 포함하지 않는다.

## [2026-10-15] P3 범위 검토와 LG-VLN 포함 정정

기존 LG-VLN 제외 설명은 navigation이 핵심 응용이라는 이유로 기하 방법·평가를 과소평가했다.
원문 §3.4·Appendix A.3의 CleanDIFT 대응 필터·robust Sim(3) 정합,
§4.3.2의 depth/pose 입력 ablation, §4.6–4.7의 깊이·ATE/RTE 평가를 다시 대조했다.
Topometric localization과 PhysVGGT처럼 기존 geometry backbone의 직접 응용도 포함한다는 P3 기준에 맞아 포함으로 정정했다.
새 백본 학습은 필수 조건이 아니다. 기하·특징을 구체적 방법으로 연결하고 그 출력·기여를 평가하는지를 기준으로 명시했다.
이전 제외 이유는 후보 JSON의 decision_history에 보존하며 단순 모델 언급만으로 포함하지 않는다.

LG-VLN은 일곱 섹션으로 추가했고 초기 카메라 높이·panoramic scale 관측, 평가 예산 제외,
GT 사후 depth 정렬과 배포 scale의 차이, 지역 RTE 개선 대비 작은 ATE 변화, 모듈 시간과 전체 FPS의 구분을 적었다.
원문 v1 해시와 Tables 3·4·6·7의 위치를 기록하고 PDF p.15·17·19를 시각 대조했다.
표 수치 토큰 23개가 모두 자동 일치했다. 실험은 재현하지 않았고 게재 venue는 확인하지 못했다.

총 337편(신규 73편), 후속 후보 포함·작성 완료 70편 / 제외 6편 / 대기 0편이다.
전체 큐는 added 206 / rejected 33이며 초기 160건의 triage는 보존했다.
이번 PR의 선택 표 수치 검토는 77문서·827토큰(자동 819, 기존 추출 예외 시각 확인 8)이다.
후보 대조·카테고리·인덱스·사실 카드를 생성기로 갱신했다. 변경 보고서는 raw/lg_vln_scope_revision_2026-10-15.json에 있다.

검사 결과: 오프라인 12개·회귀 16개 통과. 생성 후보 보고서의 실제 Prettier round-trip도 76행·본문·판정 근거를 보존했다.
README는 최종 337편 기준으로 GitHub Markdown API HTTP 200을 확인했다.

LG-VLN metadata 조회는 arXiv 제목·저자를 확인했지만 S2 429와 DBLP 인증서 검증 오류가 있었다.
자동 Crossref LIKELY 후보 DOI 10.3390/math14091485는 공식 DOI metadata의 제목·저자 전원이 달라 배제했다.
자동 결과를 지우지 않고 manual_review에 UNKNOWN 판정과 근거를 남겼다. 해당 venue를 문서에 전파하지 않았다.
이 사례는 Crossref 검색 후보 자체가 게재 확인이 아니라는 한계를 보여준다.

## [2026-10-15] English homepage, task navigation and explanatory diagrams

Rewrote the homepage description, navigation, reading tables and category explanations in English.
The complete index and all ten category indexes now emit English generated guidance with a note about Korean explanations.
Direct links to Korean summaries in the homepage are labeled Notes (KO). The 337 individual paper documents are unchanged.

The task atlas groups reading routes into Recover geometry, Render and interpret, and Localize and act.
Existing primary folders and generated counts are preserved. Reading tags such as streaming, SLAM and semantic geometry are cross-cutting cues;
they do not create duplicate entries, new primary folders or per-paper tag metadata.
Category introductions now describe tasks, typical outputs and comparison caveats instead of broad promotional claims.

Created three original code-authored SVGs for static/dynamic geometry, rendering/semantics/hidden structure, and pose/robot action.
Together with the original cover and vocabulary diagram, the homepage has five conceptual illustrations.
No third-party paper or project figure was copied; assets/README.md records provenance and the limits of this revision.
Existing third-party figures in individual notes were not audited for reuse. Repository license terms were not assigned or changed.

New diagrams were rendered at 1000/600/360px. A draft overlap between the dynamic-scene label, motion annotation and divider was corrected.
Explicit dashed segments distinguish inferred structure in rasterizers that ignore SVG dash arrays.
Native English tables and image descriptions carry the same task meanings. GitHub table wrapping and theme appearance still require a working browser runtime.
The English scope and classification checks are recorded in raw/readme_english_validation_2026-10-15.json.

Validation: all 12 offline checks and 16 regression tests passed. The final English README rendered through GitHub GFM with HTTP 200, six tables, three collapsible regions and four matching ASCII heading targets. This does not verify actual browser clicks or mobile table layout.

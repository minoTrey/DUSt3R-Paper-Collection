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

**미해결 backlog**

- PDF는 `docs/papers/`에 있으나 문서 미작성: **MoGe-2, Mono3R, RIG3R**
  (RIG3R은 README에서 링크가 깨져 있어 일단 링크만 제거)
- 표 열 개수 불일치 25건 — 렌더링 시 데이터 유실
  (`moge.md` 10행에서 6열씩, `mv-dust3r-plus.md` 15행에서 3열씩)
- `must3r.md`의 37열 표 — 마크다운에서 판독 불가, 재구성 필요
- 성능 수치(벤치마크 표)는 원논문 대조 미실시

# 후보 큐 (Auto-Update Pipeline)

새 논문을 자동 발굴 → 검토 → 승인 → 문서화로 잇는 파이프라인의 큐다.
**현재는 뼈대(skeleton)다** — 발굴과 큐 적재까지 자동이고, 문서 생성은 수동 승인이 필요하다.

## 왜 수동 승인인가

- **PDF 저작권**: 논문 PDF를 자동으로 받아 커밋하지 않는다 (`docs/papers/`는 gitignore).
- **품질**: 이 리포는 날조를 대규모로 걷어낸 이력이 있다. 새 문서는 원문 대조를
  거쳐야 하고, 그건 승인된 논문에 한해 사람/에이전트가 수행한다.
- **관련성**: 발굴 그물(피인용 + 키워드)은 관련 없는 논문도 잡는다. 사람이 거른다.

## 상태 머신

```text
new ──검토──▶ reviewed ──승인──▶ added      (문서 작성 완료)
                        └──기각──▶ rejected  (범위 밖·중복·품질 미달)
```

각 후보는 `queue.jsonl` 한 줄:

```json
{"arxiv_id": "...", "title": "...", "date": "...", "via": "cites:dust3r|kw:...", "status": "new"}
```

## 루프

1. **발굴** (자동, 주간) — `tools/discover_papers.py`
   - 앵커 논문(DUSt3R·VGGT·MASt3R·π³·CUT3R·Fast3R) 피인용 + arXiv 키워드 합집합.
   - 3R 이름이 아니어도 이들을 초석으로 하면 잡힌다.
   - 기존 사실 카드(`raw/facts/`)의 arXiv ID와 대조해 신규만 append.
   - `.github/workflows/discover.yml`이 cron으로 돌려 신규가 있으면 이슈를 연다.

2. **검토** (사람/에이전트)
   - 후보를 열어 범위·중복·품질 판단. `status`를 `reviewed` 또는 `rejected`로.

3. **문서화** (승인 후, 기존 흐름)
   - PDF 확보 → `docs/paper-template.md` 복사 → `verify_metadata.py`로 venue 확정
     → 본문 작성(모든 수치 원문 대조) → `verify_all.py --full` 통과 →
     `build_papers_list.py`·`update_stats.py`로 색인 갱신 → `status: added`.
   - 상세는 루트 `.claude/AGENTS.md`의 "새 논문 추가" 절.

## 현재 큐

`queue.jsonl` 참조. 최초 발굴에서 160편이 적재됐다(대부분 `new`).
이건 발굴 그물의 원본이며, 검토 전이므로 전부 컬렉션에 들어간다는 뜻은 아니다.

## 아직 안 된 것 (틀만 만든 부분)

- 후보 자동 분류(관련도 점수·중복 근접) — 지금은 status만.
- 이슈/PR 자동 생성의 본문 포맷 — 워크플로가 목록만 게시.
- 승인→문서화 자동 초안 — 여전히 사람이 시작한다.

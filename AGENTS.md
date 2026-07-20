# AGENTS.md — 이 레포의 작업 규약

이 파일은 Claude Code와 OpenAI Codex가 모두 읽는 단일 규약이다.
사람에게도 기여 가이드로 쓰인다. 규칙을 바꾸려면 이 파일을 먼저 바꾼다.

## 이 레포가 무엇인가

DUSt3R 계열 feed-forward 3D 재구성 논문 서베이. `docs/<category>/<slug>.md` 하나가
논문 하나다. 카테고리는 9개이며 각 디렉터리에 `README.md`(카테고리 색인)가 있다.

**최우선 가치는 정확성이다.** 이 레포의 유일한 존재 이유는 "논문 정보를 여기서
확인해도 된다"는 신뢰다. 멋진 요약보다 맞는 venue가 중요하다.

## 🚫 절대 하지 말 것

1. **메타데이터를 추측해서 쓰지 않는다.** venue, 저자, 연도, arXiv ID는 반드시
   `tools/verify_metadata.py`가 외부 API에서 가져온 값이어야 한다. 모르면 비워두고
   `⚠️ unverified`를 단다. **그럴듯한 값을 채우는 것이 이 레포를 망가뜨린 원인이다.**
2. **`TBD` 같은 플레이스홀더를 커밋하지 않는다.** 과거 `arxiv.org/abs/TBD`가
   실제로 배포된 적이 있다.
3. **성능 수치를 원논문 확인 없이 옮기지 않는다.**
4. **표를 논문에서 그대로 붙여넣지 않는다.** 아래 표 규칙 참조.

## 논문 문서 형식

### 파일명

`docs/<category>/<slug>.md` — slug은 소문자, 하이픈. 논문 약칭을 쓴다
(`mast3r-sfm.md`, `mv-dust3r-plus.md`). 특수문자(π 등)는 아스키로 (`pi3.md`).

### H1

```markdown
# <약칭>: <논문 부제> (<Venue>)
```

### 필수 섹션 — 이 7개를, 이 순서로. 추가·삭제·개명 금지

```text
## 📋 Overview
## 🎯 Key Contributions
## 🔧 Technical Details
## 📊 Results
## 💡 Insights & Impact
## 📚 Key Takeaways
## 🔗 Related Work
```

새 섹션이 필요하면 `###`로 위 7개 안에 넣는다. `## 💡 Critical Analysis`,
`## 📊 Expected Results` 같은 1회성 `##` 섹션을 만들지 않는다.

### Overview 블록 스키마

키 이름과 순서를 지킨다. `tools/extract_meta.py`가 이 형태를 파싱한다.

```markdown
- **Authors**: <제1저자>, <제2저자>, ... (arXiv 표기 순서 그대로, 생략 없이)
- **Institution**: <소속>  ← 복수여도 단수형 키. `Institutions` 금지
- **Venue**: <아래 표기법>
- **Award**: <Oral / Highlight / Best Paper 등>  ← 해당 시에만. Venue에 섞지 말 것
- **Links**: [Paper](<url>) | [Code](<url>) | [Project Page](<url>)
- **TL;DR**: <한 문장>
- **Verification**: <CONFIRMED | LIKELY | PREPRINT> (<YYYY-MM-DD>)
```

### Venue 표기법 — 정확히 이 형식만

| 상황           | 표기                         | 예                                   |
| -------------- | ---------------------------- | ------------------------------------ |
| 학회 등재 확정 | `<약칭> <연도>`              | `CVPR 2024`, `ECCV 2024`, `3DV 2025` |
| 저널           | `<약칭> <연도>`              | `RAL 2024`, `TPAMI 2025`             |
| 프리프린트     | `arXiv preprint (<YYYY-MM>)` | `arXiv preprint (2025-03)`           |

규칙:

- **약칭만 쓴다.** `International Conference on 3D Vision (3DV) 2025` ❌ → `3DV 2025` ✅
- **연도는 학회 연도지 arXiv 제출 연도가 아니다.** DUSt3R는 2023년 12월 arXiv이지만
  `CVPR 2024`다. MonST3R는 2024년 10월 arXiv이지만 `ICLR 2025`다.
- **두 venue를 병기하지 않는다.** `CVPR 2025 | arXiv preprint (2024-12)` ❌
  등재됐으면 학회만 쓴다. 프리프린트 이력은 arXiv 링크가 이미 담고 있다.
- **수상은 `Award` 필드로 분리한다.** `CVPR 2025 (Oral)` ❌
  → `Venue: CVPR 2025` + `Award: Oral` ✅

### Verification 등급

`tools/verify_metadata.py`가 판정한다. 손으로 올리지 않는다.

| 등급        | 조건                                                                          |
| ----------- | ----------------------------------------------------------------------------- |
| `CONFIRMED` | DBLP에 non-CoRR 레코드 존재, 또는 S2가 publisher DOI + `Conference` 동시 충족 |
| `LIKELY`    | arXiv comment가 "Accepted at X" 명시, 또는 S2 venue만 존재                    |
| `PREPRINT`  | DBLP는 CoRR 단독 **AND** S2 venue 공란 **AND** arXiv comment 침묵 — 3개 모두  |

⚠️ 최근 논문은 등재됐어도 색인이 안 됐을 수 있다. `PREPRINT` 판정이 최신성에 기대면
project page와 GitHub README를 확인한다 — 저자는 색인보다 몇 달 먼저 갱신한다.

## 표 규칙

- **12열을 넘기지 않는다.** 논문의 대형 벤치마크 표를 그대로 옮기지 말고,
  핵심 지표만 추리거나 여러 표로 쪼갠다. 37열 표는 마크다운에서 읽을 수 없다.
- **헤더 열 수와 데이터 행 열 수가 반드시 같아야 한다.** 다르면 GitHub 렌더링에서
  데이터가 조용히 잘려나간다. `npx markdownlint-cli2`의 MD056이 이걸 잡는다.
- 그룹 구분 행(`| **Scale-Invariant** |`)은 허용하되, 빈 셀로 열 수를 채운다.
- 수치 옆에 출처를 남긴다: 원논문 Table 번호 또는 재현 여부.

## 도구

```bash
npx markdownlint-cli2                  # 구조 검사
npx markdownlint-cli2 --fix            # 안전한 서식 자동수정
npx prettier --write "**/*.md"         # 표 정렬·공백
python3 tools/extract_meta.py          # Overview 메타데이터 추출 (파일 전체를 읽지 않음)
python3 tools/verify_metadata.py       # 외부 API 대조 검증
python3 tools/update_stats.py          # README 카운트·히스토그램 재생성
```

### 에이전트에게: 토큰 절약 규칙

- **`docs/**/*.md`를 통째로 읽지 마라.** 전체가 ~150k 토큰이다. 메타데이터가
  필요하면 `tools/extract_meta.py --json`을 쓴다 (~5k 토큰).
- 일괄 수정은 스크립트로 하고 diff만 검토한다. LLM은 50개 파일에 걸쳐
  조용히 비일관적이지만 스크립트는 그렇지 않다.
- 카운트를 손으로 세지 마라. `update_stats.py`가 생성한다.

## 카운트·색인

README와 카테고리 README의 논문 수, 연도 히스토그램, 배지는 **전부 자동 생성**이다.
손으로 고치지 않는다 — 그래서 지금까지 계속 틀어졌다. `tools/update_stats.py` 실행.

## 새 논문 추가

1. `docs/paper-template.md`를 복사하고 Links에 arXiv URL을 넣는다
2. `python3 tools/verify_metadata.py --only <slug>` 로 메타데이터를 검증하고
   `raw/verdicts.json`의 판정값을 Overview에 반영한다
3. 본문 작성 (Overview 외 6개 섹션)
4. `npx markdownlint-cli2 --fix && npx prettier --write "**/*.md"`
5. `python3 tools/update_stats.py` 로 색인 갱신
6. `log.md`에 한 줄 추가

## 출처 계층

`raw/`에 API 원본 응답이 논문별로 저장된다. **불변이다 — 편집하지 않는다.**
메타데이터 분쟁이 생기면 여기가 근거다. 재검증은 `verify_metadata.py` 재실행.

#!/usr/bin/env python3
"""Build the per-candidate decision and publication-status report from evidence."""
import argparse
import collections
import json
import pathlib
import re
from paper_paths import resolve

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "candidates/review-2026-10-15.md"


def build():
    review = json.loads((ROOT / "candidates/review-2026-10-15.json").read_text(encoding="utf-8"))
    queue = {r["arxiv_id"]: r for r in (
        json.loads(line) for line in (ROOT / "candidates/queue.jsonl").read_text(encoding="utf-8").splitlines()
    )}
    records = review["records"]
    counts = collections.Counter(queue[r["arxiv_id"]]["status"] for r in records)
    lines = ["# 후속 후보 76편: 근거와 최종 처리 상태", "",
             "이 표는 `tools/build_candidate_review.py`가 분류 근거와 큐 상태에서 생성한다.",
             "원문을 확인한 관련성 판정과 요약·수치 검증 완료는 다른 단계다.", "",
             f"**현재: 추가 {counts['added']} / 작성 대기 {counts['reviewed']} / 제외 {counts['rejected']} / 미분류 {counts['new']}**", "",
             "- P1: 기하 백본·pose/SLAM·matching·신뢰도와 실패 분석.",
             "- P2: 모달리티·동적 장면·Gaussian·공동 의미 기하의 직접 확장.",
             "- P3: 기존 geometry backbone의 기하·특징을 구체적 방법으로 연결하고 그 출력·기여를 평가하는 직접 응용. 백본 자체의 개선과 구분한다.",
             "- X: 현재 컬렉션의 직접 범위에서 제외. 3D 연구 일반의 가치 판단이 아니다.", "",
             "## 직접 응용의 포함 범위", "",
             *[paragraph + "\n" for paragraph in review.get("application_scope", [])],
             "모든 후보의 원문 PDF를 확보했다. 동일 arXiv ID의 기존 문서 중복은 없다.",
             "WAT3R/Wat3R와 두 Scal3R는 저자·제목·방법이 다른 별도 논문이다.",
             "이름이 겹치는 새 문서는 기존 slug를 덮어쓰지 않는다.", "",
             "| Candidate / Source | Priority | Decision / Status | Reason | Summary |",
             "| --- | --- | --- | --- | --- |"]
    for r in records:
        aid = r["arxiv_id"]
        decision = {"include": "포함", "exclude": "제외", "defer": "보류"}[r["decision"]]
        title = r["title"].replace("|", "\\|").replace("$\\Omega$", "Ω").replace("$\\pi$", "π")
        link = f"[{title}]({r['source_pdf']})"
        summary = f"[요약](../{resolve(r['summary_file'], 'note_path', ROOT)})" if r.get("summary_file") else "작성 대기" if r["decision"] == "include" else "해당 없음"
        lines.append(f"| {link} | {r['priority']} | {decision} / {queue[aid]['status']} | {r['reason']} | {summary} |")
    lines += ["", "## 검토 한계", "",
              "이 분류는 원문의 문제·방법·평가 연결을 읽은 범위 판정이다. 실험 재현이나 학회 게재 확인이 아니다.",
              "본문의 정량 결과는 각 요약의 버전·표·프로토콜과 별도 검증 기록을 확인한다.",
              "초기 160건의 기존 IN/OUT은 이번 후속 76편 분류와 별도이며 과거 기록을 보존한다.", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    new = build()
    if args.check:
        def normalized(text):
            return "\n".join("|".join("---" if re.fullmatch(r":?-+:?", cell.strip())
                                     else cell.strip() for cell in line.split("|"))
                             if line.startswith("|") else line.rstrip()
                             for line in text.splitlines())
        if not OUT.exists() or normalized(OUT.read_text(encoding="utf-8")) != normalized(new):
            print("Candidate report is stale. Run python tools/build_candidate_review.py.")
            return 1
    else:
        OUT.write_text(new, encoding="utf-8", newline="\n")
    print("Candidate report: 76 decisions and current states are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

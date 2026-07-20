#!/usr/bin/env python3
"""논문 메타데이터를 외부 권위 소스와 대조 검증한다.

파이프라인:
  A. arXiv API   — 정본 제목, 저자 순서, comment 필드 (venue 힌트 + project page)
  B. S2 batch    — venue 광범위 커버. 55편이 POST 1회로 끝난다.
  C. DBLP        — 최종 심판. 등재/프리프린트를 확실히 구분하는 유일한 소스.

원본 응답은 raw/ 에 저장한다 (불변 출처 계층). 재검증 가능해야 한다.

⚠️ 실측으로 확인한 함정 3가지 — 코드에서 각각 방어한다:
  1. S2의 `year`는 arXiv 제출 연도다. DUSt3R는 year=2023이지만 CVPR 2024다.
     → journal.name 또는 IEEE DOI에서 연도를 뽑는다. `year`는 쓰지 않는다.
  2. OpenAlex를 arXiv DOI로 조회하면 DUSt3R/MASt3R/CUT3R/VGGT 전부
     "미출간 프리프린트"로 나온다. → OpenAlex는 쓰지 않는다.
  3. arXiv comment는 recall 50% / precision 100%. venue를 말하면 맞지만
     침묵하는 경우가 절반이다. → 침묵을 프리프린트 근거로 삼지 않는다.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
UA = "DUSt3R-Paper-Collection/1.0 (https://github.com/minoTrey/DUSt3R-Paper-Collection)"

ARXIV_API = "https://export.arxiv.org/api/query"  # http는 빈 본문을 반환한다. https 필수.
S2_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch"
DBLP_API = "https://dblp.org/search/publ/api"

VENUES = (
    "CVPR|ICCV|ECCV|NeurIPS|NIPS|ICLR|ICML|3DV|SIGGRAPH|WACV|BMVC|"
    "TPAMI|IJCV|RAL|ICRA|IROS|MICCAI|AAAI|ACCV|CoRL"
)
# arXiv comment에서 venue를 뽑는다. "Accepted at CVPR 2025", "CVPR 2025", "Accepted by ICLR 25"
COMMENT_VENUE = re.compile(
    r"\b(?:accepted\s+(?:at|by|to)\s+|to\s+appear\s+(?:at|in)\s+|camera[- ]ready\s+)?"
    r"\b(" + VENUES + r")\b[\s,'’]*(\d{4}|\d{2})\b",
    re.I,
)
URL_RE = re.compile(r"https?://[^\s,;)\]]+")
# IEEE proceedings DOI에는 학회 연도가 박혀 있다: 10.1109/CVPR52734.2025.00499
DOI_YEAR = re.compile(r"10\.1109/[A-Z0-9]+\.(\d{4})\.", re.I)
LEAD_YEAR = re.compile(r"\b(19|20)\d{2}\b")


def http(
    url: str, data: bytes | None = None, tries: int = 4, api_key: str | None = None
) -> bytes:
    """재시도 + Retry-After 준수. DBLP는 429를 적극적으로 던진다."""
    req = urllib.request.Request(url, data=data)
    req.add_header("User-Agent", UA)
    if data:
        req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("x-api-key", api_key)
    delay = 5.0
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                wait = float(e.headers.get("Retry-After") or delay)
                print(f"    [{e.code}] {wait:.0f}s 대기 후 재시도", file=sys.stderr)
                time.sleep(wait)
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise RuntimeError("unreachable")


def norm_year(y: str | None) -> str | None:
    if not y:
        return None
    y = y.strip()
    if len(y) == 2:  # "ICLR 25" -> 2025
        return "20" + y
    return y if re.fullmatch(r"(19|20)\d{2}", y) else None


# ---------------------------------------------------------------- Stage A: arXiv
def stage_a(ids: list[str]) -> dict[str, dict]:
    """arXiv API. ID 100개까지 한 번에. 1 req/3s 준수."""
    out: dict[str, dict] = {}
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    for i in range(0, len(ids), 100):
        chunk = ids[i : i + 100]
        url = f"{ARXIV_API}?{urllib.parse.urlencode({'id_list': ','.join(chunk), 'max_results': len(chunk)})}"
        print(f"  [A] arXiv {i + 1}-{i + len(chunk)} / {len(ids)}", file=sys.stderr)
        try:
            xml = http(url)
        except Exception as e:
            # arXiv도 503/429를 던진다. 한 청크 실패가 전체를 죽이면 안 된다.
            # 이 청크의 논문들은 arXiv 정보 없이 DBLP/Crossref로만 판정된다.
            print(f"    ⚠️ arXiv 청크 실패 ({e}) — 건너뛴다", file=sys.stderr)
            time.sleep(10)
            continue
        (RAW / "arxiv").mkdir(parents=True, exist_ok=True)
        root = ET.fromstring(xml)
        for e in root.findall("a:entry", ns):
            raw_id = (e.findtext("a:id", "", ns) or "").rsplit("/", 1)[-1]
            aid = raw_id.split("v")[0]
            comment = e.findtext("arxiv:comment", "", ns) or ""
            venue = year = None
            m = COMMENT_VENUE.search(comment)
            if m:
                venue, year = m.group(1).upper(), norm_year(m.group(2))
            out[aid] = {
                "arxiv_id": aid,
                "version": raw_id,
                "title": " ".join((e.findtext("a:title", "", ns) or "").split()),
                "authors": [
                    a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)
                ],
                "published": e.findtext("a:published", "", ns),
                "updated": e.findtext("a:updated", "", ns),
                "comment": comment,
                "comment_venue": venue,
                "comment_year": year,
                "urls": URL_RE.findall(comment),
                "doi": e.findtext("arxiv:doi", None, ns),
                "journal_ref": e.findtext("arxiv:journal_ref", None, ns),
            }
            (RAW / "arxiv" / f"{aid}.xml").write_bytes(
                ET.tostring(e, encoding="utf-8")
            )
        if i + 100 < len(ids):
            time.sleep(3.5)  # arXiv: 1 req / 3s
    return out


# ------------------------------------------------------------------ Stage B: S2
def stage_b(ids: list[str], api_key: str | None = None) -> dict[str, dict]:
    """Semantic Scholar batch. best-effort.

    ⚠️ 무인증 풀은 전역 공유(1000 RPS)라 batch조차 상시 429가 난다.
    S2는 보조 소스일 뿐 최종 심판이 아니므로, 실패하면 빈 dict를 반환하고
    arXiv + DBLP로 진행한다. 이 생태계(CVPR/ECCV/ICCV/ICLR/3DV)는 DBLP가 다 덮는다.
    키가 있으면 S2_API_KEY 환경변수로 넘긴다.
    """
    if not ids:
        return {}
    fields = (
        "title,venue,publicationVenue,year,publicationTypes,externalIds,"
        "journal,authors.name"
    )
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i : i + 500]
        print(f"  [B] S2 batch {len(chunk)}편 (POST 1회)", file=sys.stderr)
        body = json.dumps({"ids": [f"arXiv:{x}" for x in chunk]}).encode()
        try:
            data = json.loads(
                http(f"{S2_BATCH}?fields={fields}", data=body, api_key=api_key)
            )
        except Exception as e:
            print(
                f"    ⚠️ S2 사용 불가 ({e}) — arXiv + DBLP로 진행한다.\n"
                f"       S2는 보조 소스이고 최종 심판은 DBLP다. 판정 품질에 큰 영향 없음.",
                file=sys.stderr,
            )
            return {}
        (RAW / "s2").mkdir(parents=True, exist_ok=True)
        for aid, rec in zip(chunk, data):
            if not rec:
                out[aid] = {"found": False}
                continue
            (RAW / "s2" / f"{aid}.json").write_text(
                json.dumps(rec, ensure_ascii=False, indent=1)
            )
            jrnl = (rec.get("journal") or {}).get("name") or ""
            doi = (rec.get("externalIds") or {}).get("DOI") or ""
            pv = rec.get("publicationVenue") or {}
            # ⚠️ 함정 1: rec["year"]는 arXiv 제출 연도다. 절대 쓰지 않는다.
            vy = None
            dm = DOI_YEAR.search(doi)
            if dm:
                vy = dm.group(1)
            else:
                jm = LEAD_YEAR.search(jrnl)
                if jm:
                    vy = jm.group(0)
            out[aid] = {
                "found": True,
                "title": rec.get("title"),
                "venue": rec.get("venue") or "",
                "venue_abbrev": (pv.get("alternate_names") or [None])[0]
                if pv.get("alternate_names")
                else None,
                "journal_name": jrnl,
                "doi": doi,
                "publisher_doi": bool(doi and not doi.lower().startswith("10.48550")),
                "types": rec.get("publicationTypes") or [],
                "venue_year": vy,
                "arxiv_year_DO_NOT_USE": rec.get("year"),
            }
    return out


# ---------------------------------------------------------------- Stage C: DBLP
def stage_c(title: str) -> dict:
    """DBLP. 등재 논문은 conference + CoRR 두 레코드로 나온다. 이 쌍이 판별자다."""
    url = f"{DBLP_API}?{urllib.parse.urlencode({'q': title, 'format': 'json', 'h': 8})}"
    data = json.loads(http(url))
    hits = (data.get("result", {}).get("hits", {}) or {}).get("hit", []) or []
    conf, corr = [], []
    for h in hits:
        info = h.get("info", {})
        got = " ".join((info.get("title") or "").rstrip(".").lower().split())
        want = " ".join(title.lower().split())
        # DBLP 검색은 fuzzy 확장이라 무관한 논문이 섞인다. 제목을 반드시 확인한다.
        if got != want and want not in got and got not in want:
            continue
        venue = info.get("venue") or ""
        rec = {
            "venue": venue,
            "year": info.get("year"),
            "type": info.get("type"),
            "doi": info.get("doi"),
            "key": info.get("key"),
            "title": info.get("title"),
        }
        (corr if venue == "CoRR" else conf).append(rec)
    return {"conference": conf, "corr": corr, "n_hits": len(hits)}


# ------------------------------------------------------- Stage D: Crossref
CROSSREF = "https://api.crossref.org/works"


def stage_d(title: str, authors: list[str] | None = None) -> dict:
    """Crossref 대조. PREPRINT 판정을 뒤집을 마지막 기회다.

    ⚠️ 이 단계가 필요한 이유 — 실제 사례:
    "Unifying Scene Representation and Hand-Eye Calibration with 3D Foundation Models"
    (arXiv 2404.11683)는 RA-L 게재 시 제목이
    "Unifying Representation and Calibration With 3D Foundation Models"로 바뀌었다.
    저자가 arXiv에 journal_ref를 달지 않아 arXiv·DBLP·S2가 전부 "프리프린트"라고
    답했지만 실제로는 RA-L 2024(DOI 10.1109/LRA.2024.3451396) + ICRA 2025다.

    → 게재 시 개명된 논문은 제목 완전일치로 못 잡는다. Crossref는 bibliographic
      쿼리로 부분 일치를 찾아주므로 이 실패 모드를 덮는다.
    """
    q = {"query.bibliographic": title, "rows": 5, "mailto": "noreply@example.com"}
    if authors:
        q["query.author"] = " ".join(authors[:2])
    try:
        data = json.loads(http(f"{CROSSREF}?{urllib.parse.urlencode(q)}"))
    except Exception as e:
        return {"error": str(e), "hits": []}
    hits = []
    for it in (data.get("message", {}) or {}).get("items", []):
        doi = it.get("DOI") or ""
        if doi.lower().startswith("10.48550"):  # arXiv DOI는 게재 근거가 아니다
            continue
        if it.get("type") in ("posted-content", "dataset"):
            continue
        parts = (it.get("published") or {}).get("date-parts") or [[None]]
        hits.append(
            {
                "title": (it.get("title") or [""])[0],
                "container": (it.get("container-title") or [""])[0],
                "year": str(parts[0][0]) if parts[0][0] else None,
                "doi": doi,
                "type": it.get("type"),
                "score": it.get("score"),
            }
        )
    return {"hits": hits}


# ----------------------------------------------------------------- 판정
def adjudicate(
    a: dict | None, b: dict | None, c: dict | None, d: dict | None = None
) -> dict:
    """CONFIRMED / LIKELY / PREPRINT / UNKNOWN 판정.

    PREPRINT는 세 소스가 모두 침묵할 때만. 하나라도 venue를 말하면 프리프린트가 아니다.
    """
    a, b, c, d = a or {}, b or {}, c or {}, d or {}
    conf = (c.get("conference") or [])

    # 1순위: DBLP non-CoRR 레코드 = 등재 확정
    if conf:
        best = sorted(conf, key=lambda r: r.get("year") or "")[-1]
        return {
            "verdict": "CONFIRMED",
            "venue": f"{best['venue']} {best['year']}",
            "source": f"DBLP {best.get('key')}",
        }

    # 2순위: S2가 publisher DOI + Conference 동시 충족
    if b.get("publisher_doi") and "Conference" in (b.get("types") or []):
        v = b.get("venue_abbrev") or b.get("venue")
        y = b.get("venue_year")
        if v and y:
            return {
                "verdict": "CONFIRMED",
                "venue": f"{v} {y}",
                "source": f"S2 DOI {b.get('doi')}",
            }

    # 3순위: arXiv comment가 venue를 명시 (precision 100%)
    if a.get("comment_venue") and a.get("comment_year"):
        return {
            "verdict": "LIKELY",
            "venue": f"{a['comment_venue']} {a['comment_year']}",
            "source": f"arXiv comment: {a['comment'][:70]}",
        }

    # 4순위: S2 venue만 존재 (ICLR/NeurIPS는 IEEE DOI가 없어 여기 걸린다)
    if b.get("venue"):
        v = b.get("venue_abbrev") or b.get("venue")
        y = b.get("venue_year")
        return {
            "verdict": "LIKELY",
            "venue": f"{v} {y}" if y else str(v),
            "source": "S2 venue (연도 미확정)" if not y else "S2 venue",
        }

    # 5순위: Crossref에 publisher DOI가 있으면 게재된 것이다.
    #        게재 시 제목이 바뀐 논문은 여기서만 잡힌다.
    # ⚠️ 임계값 주의: RA-L 정답 사례의 score가 40이었다. 60으로 잡으면 놓친다.
    #    대신 container-title이 있고 논문 타입인 것만 본다 (보충자료 _supp 배제).
    for h in (d.get("hits") or [])[:3]:
        if (
            h.get("container")
            and h.get("year")
            and (h.get("score") or 0) >= 35
            and h.get("type") in ("journal-article", "proceedings-article")
        ):
            return {
                "verdict": "LIKELY",
                "venue": f"{h['container']} {h['year']}",
                "source": f"Crossref DOI {h['doi']} — 제목 \"{h['title'][:50]}\"",
                "caveat": "arXiv 제목과 다를 수 있다(게재 시 개명). 제목 대조 필요.",
            }

    # 네 소스 모두 침묵 → 프리프린트.
    # ⚠️ S2가 429로 죽었으면 근거가 3개가 아니라 2개다. 이때는 단정하지 않는다.
    #    실제로 pomato는 S2 부재 시 PREPRINT, S2 응답 시 ICCV 2025로 뒤집혔다.
    if c.get("corr") or a:
        pub = (a.get("published") or "")[:7]
        s2_up = bool(b)
        return {
            "verdict": "PREPRINT" if s2_up else "PREPRINT?",
            "venue": f"arXiv preprint ({pub})" if pub else "arXiv preprint",
            "source": (
                "DBLP CoRR 단독 + S2 공란 + arXiv comment 침묵"
                if s2_up
                else "DBLP CoRR 단독 + arXiv comment 침묵 (⚠️ S2 조회 실패 — 근거 2/3)"
            ),
            "caveat": (
                "색인 지연 가능. project page / GitHub README 확인 권장"
                if s2_up
                else "S2 없이 판정됨. S2_API_KEY를 설정해 재검증할 것. 문서 값을 지우지 마라."
            ),
        }

    return {"verdict": "UNKNOWN", "venue": None, "source": "조회 실패"}


# ----------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="앞의 N편만 (테스트용)")
    ap.add_argument("--only", help="특정 slug만 (쉼표 구분)")
    ap.add_argument("--skip-dblp", action="store_true", help="DBLP 생략 (빠른 확인용)")
    ap.add_argument("--out", default="raw/verdicts.json")
    args = ap.parse_args()

    sys.path.insert(0, str(ROOT / "tools"))
    from extract_meta import papers, parse  # noqa: E402

    recs = [parse(p) for p in papers()]
    if args.only:
        want = set(args.only.split(","))
        recs = [r for r in recs if r["slug"] in want]
    if args.limit:
        recs = recs[: args.limit]

    RAW.mkdir(exist_ok=True)
    ids = [r["arxiv_id"] for r in recs if r["arxiv_id"]]
    print(f"논문 {len(recs)}편 / arXiv ID 보유 {len(ids)}편", file=sys.stderr)

    import os

    A = stage_a(ids) if ids else {}
    B = stage_b(ids, os.environ.get("S2_API_KEY")) if ids else {}

    C: dict[str, dict] = {}
    if not args.skip_dblp:
        for n, r in enumerate(recs, 1):
            t = (A.get(r["arxiv_id"], {}) or {}).get("title") or r["h1"]
            if not t:
                continue
            t = re.sub(r"\s*\(.*?\)\s*$", "", t)  # 끝의 (CVPR 2024) 제거
            print(f"  [C] DBLP {n}/{len(recs)}: {t[:55]}", file=sys.stderr)
            try:
                C[r["slug"]] = stage_c(t)
            except Exception as e:  # 한 편 실패가 전체를 죽이지 않게
                C[r["slug"]] = {"error": str(e), "conference": [], "corr": []}
            time.sleep(4)  # DBLP는 공격적으로 429를 던진다

    results = []
    for r in recs:
        a = A.get(r["arxiv_id"] or "")
        b = B.get(r["arxiv_id"] or "")
        c = C.get(r["slug"])
        # Stage D는 앞의 셋이 게재 근거를 못 찾았을 때만 돈다 (비용 절약).
        d = None
        if adjudicate(a, b, c)["verdict"].startswith("PREPRINT"):
            t = (a or {}).get("title") or r["h1"] or ""
            t = re.sub(r"\s*\(.*?\)\s*$", "", t)
            if t:
                print(f"  [D] Crossref 확인: {t[:55]}", file=sys.stderr)
                d = stage_d(t, (a or {}).get("authors"))
                time.sleep(1)
        results.append(
            {
                "file": r["file"],
                "slug": r["slug"],
                "doc_venue": r["fields"].get("Venue"),
                "doc_authors": r["fields"].get("Authors"),
                "arxiv_id": r["arxiv_id"],
                "arxiv": a,
                "s2": b,
                "dblp": c,
                "crossref": d,
                **adjudicate(a, b, c, d),
            }
        )

    (ROOT / args.out).write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"\n→ {args.out} 기록 완료 ({len(results)}편)", file=sys.stderr)

    from collections import Counter

    for k, v in Counter(x["verdict"] for x in results).most_common():
        print(f"  {k:10s} {v}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

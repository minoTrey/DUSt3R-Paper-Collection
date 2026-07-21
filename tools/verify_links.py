#!/usr/bin/env python3
"""사실 카드의 외부 링크(arXiv/code/project) 생존을 확인한다.

네트워크가 필요해 CI(오프라인)에는 넣지 않는다 — 스케줄/수동 게이트다.
결과를 raw/linkcache.json 에 캐시(TTL)해, --check 는 캐시만 보고 최근 실패를
보고한다. 이렇게 하면 오프라인 CI에서도 "지난번 확인에서 죽은 링크"를 잡는다.

죽는 유형: GitHub 저장소 삭제·비공개·이름변경(404), project page 소멸.
arXiv 는 우리가 ID를 검증했으므로 신뢰하되 형식만 확인한다.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import pathlib
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FACTS = ROOT / "raw" / "facts"
CACHE = ROOT / "raw" / "linkcache.json"
TTL = 30 * 24 * 3600  # 30일
UA = "DUSt3R-Paper-Collection-linkcheck/1.0"


def collect() -> dict[str, list[str]]:
    """url -> [그 url을 쓰는 slug들]"""
    urls: dict[str, list[str]] = {}
    for fp in FACTS.glob("*.json"):
        c = json.loads(fp.read_text())
        for u in c.get("links", {}).values():
            u = u.strip()
            if u.startswith("http"):
                urls.setdefault(u, []).append(c["slug"])
    return urls


def check_one(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        # HEAD 거부(405/403)는 GET으로 재시도
        if e.code in (403, 405):
            try:
                req2 = urllib.request.Request(url)
                req2.add_header("User-Agent", UA)
                with urllib.request.urlopen(req2, timeout=20) as r:
                    return r.status
            except Exception:
                return e.code
        return e.code
    except Exception:
        return 0  # 연결 실패


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="캐시만 보고 실패 보고 (CI)")
    ap.add_argument("--refresh", action="store_true", help="TTL 무시하고 전부 재확인")
    args = ap.parse_args()

    urls = collect()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    now = time.time()

    if args.check:
        dead = {
            u: c
            for u, c in cache.items()
            if c.get("status", 0) not in (200, 301, 302)
        }
        if dead:
            print(f"❌ 죽은 링크 {len(dead)}개 (마지막 확인 기준):")
            for u, c in list(dead.items())[:20]:
                print(f"   [{c.get('status')}] {u}  ← {c.get('slugs')}")
            return 1
        print(f"✅ 링크 {len(cache)}개 전부 생존 (캐시 기준)")
        return 0

    todo = [
        u
        for u in urls
        if args.refresh
        or u not in cache
        or now - cache[u].get("ts", 0) > TTL
    ]
    print(f"URL {len(urls)}개 중 {len(todo)}개 확인 (나머지 캐시 유효)")
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for u, st in zip(todo, ex.map(check_one, todo)):
            cache[u] = {"status": st, "ts": now, "slugs": urls[u]}
    # 없어진 URL 정리
    cache = {u: c for u, c in cache.items() if u in urls}
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1))

    dead = {u: c for u, c in cache.items() if c["status"] not in (200, 301, 302)}
    print(f"→ 생존 {len(cache) - len(dead)} / 죽음 {len(dead)}")
    for u, c in sorted(dead.items()):
        print(f"   [{c['status']}] {u}  ← {c['slugs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

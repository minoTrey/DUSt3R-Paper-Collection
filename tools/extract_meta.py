#!/usr/bin/env python3
"""Overview 블록만 추출한다. 파일 전체를 읽지 않는 것이 요점."""
import re, sys, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIELD = re.compile(r'^\s*[-*]\s*\*\*(?P<k>[^*]+)\*\*\s*:\s*(?P<v>.*?)\s*$')
ARXIV = re.compile(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})')

def papers():
    for p in sorted(ROOT.glob('docs/*/*.md')):
        if p.name == 'README.md' or 'VERIFICATION' in p.name:
            continue
        yield p

def parse(p):
    txt = p.read_text(encoding='utf-8')
    rec = {'file': str(p.relative_to(ROOT)), 'cat': p.parent.name, 'slug': p.stem}
    m = re.search(r'^#\s+(.+)$', txt, re.M)
    rec['h1'] = m.group(1).strip() if m else None
    # Overview 섹션만 잘라낸다
    ov = re.search(r'^##\s*[^\n]*Overview\s*$(.*?)(?=^##\s)', txt, re.M | re.S)
    fields = {}
    if ov:
        for line in ov.group(1).splitlines():
            fm = FIELD.match(line)
            if fm:
                fields[fm.group('k').strip()] = fm.group('v').strip()
    rec['fields'] = fields
    # ⚠️ arXiv ID는 반드시 Overview의 Links 필드에서만 뽑는다.
    # 문서 전체를 훑으면 Related Work에 인용된 *다른* 논문의 arXiv를 잡는다.
    # 실제로 slam3r.md가 초전도 회로 논문(2404.18774)으로,
    # largespatialmodel.md가 의료 진단 논문(2410.15403)으로 오인식된 적이 있다.
    am = ARXIV.search(fields.get('Links', ''))
    rec['arxiv_id'] = am.group(1) if am else None
    rec['arxiv_id_source'] = 'Links' if am else None
    rec['sections'] = re.findall(r'^##\s+(.+)$', txt, re.M)
    rec['bytes'] = len(txt)
    return rec

if __name__ == '__main__':
    recs = [parse(p) for p in papers()]
    if '--json' in sys.argv:
        print(json.dumps(recs, ensure_ascii=False, indent=1))
    else:
        keys = {}
        for r in recs:
            for k in r['fields']:
                keys[k] = keys.get(k, 0) + 1
        print(f"papers={len(recs)}  arxiv_id_missing={sum(1 for r in recs if not r['arxiv_id'])}")
        print("\n-- Overview 필드 사용 빈도 --")
        for k, v in sorted(keys.items(), key=lambda x: -x[1]):
            print(f"{v:3d}/{len(recs)}  {k}")

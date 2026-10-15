#!/usr/bin/env python3
"""Check local Markdown file links, including case on Windows, without network calls."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def errors(root):
    files = {p.relative_to(root).as_posix() for p in root.rglob('*')
             if p.is_file() and 'node_modules' not in p.parts and '.git' not in p.parts}
    failures = []
    for name in sorted(files):
        if not name.endswith('.md'):
            continue
        path = root / name
        for match in re.finditer(r'\]\(([^)]+\.md[^)]*)\)', path.read_text(encoding='utf-8')):
            link = match.group(1).split('#', 1)[0]
            if link.startswith(('http:', 'https:')) or not link:
                continue
            import posixpath
            target = posixpath.normpath(posixpath.join(pathlib.PurePosixPath(name).parent.as_posix(), link))
            if target not in files:
                failures.append(f'{name}: broken or case-mismatched link: {link}')
    return failures


def main():
    failures = errors(ROOT)
    for failure in failures:
        print(failure)
    print(f'Internal Markdown links: {len(failures)} errors')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())

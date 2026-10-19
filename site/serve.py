"""Serve the generated site at its actual project base path for local preview."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=4173)
parser.add_argument('--directory', default='_site')
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
directory = (root / args.directory).resolve()
if not directory.is_relative_to(root) or directory == root:
    raise SystemExit('Preview directory must be a generated workspace subfolder.')
base = json.loads((directory / 'build-manifest.json').read_text(encoding='utf8'))['base']


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        pathname = urlsplit(self.path).path
        if pathname == '/' and base != '/':
            self.send_response(302)
            self.send_header('Location', base)
            self.end_headers()
            return
        if not pathname.startswith(base):
            self.send_error(404)
            return
        self.path = '/' + self.path[len(base):]
        super().do_GET()

    def do_HEAD(self):
        pathname = urlsplit(self.path).path
        if not pathname.startswith(base):
            self.send_error(404)
            return
        self.path = '/' + self.path[len(base):]
        super().do_HEAD()


print(f'Preview: http://127.0.0.1:{args.port}{base}', flush=True)
ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(directory))).serve_forever()

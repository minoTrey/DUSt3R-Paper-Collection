# GitHub Pages paper gallery

The English gallery reads the canonical `docs/<category>/<slug>.md` notes and existing PNG assets. Markdown and reviewed PNGs remain the content source; generated HTML is not edited or committed. Original full summary PNGs remain unchanged. Separate reviewed landscape thumbnails have optimized WebP deliveries; pending papers show their complete original summary. Both use contain sizing. Detail pages show the original full poster and substantive note sections.

## Build and preview

```sh
npm ci
node site/build.mjs
node site/check.mjs
python site/serve.py --port 4175
```

Open `http://127.0.0.1:4175/DUSt3R-Paper-Collection/`. The server uses the build manifest's base path, matching a GitHub project site. A root-hosted build is also supported:

```sh
node site/build.mjs --base / --out _site-root
node site/check.mjs _site-root
python site/serve.py --directory _site-root --port 4176
```

The build output must be a direct workspace folder named `_site` or `_site-<name>`; the builder validates that path before replacing it. Generated output and browser test profiles/screenshots are ignored by Git.

## Reading and navigation

Search matches paper titles, methods/purposes, authors and source IDs. Category and Year/Month/Day publication periods combine with search. Dates use verified arXiv v1 submission or original publisher evidence at its actual precision; results retain newest-first publication order. The period toolbar provides previous/next navigation and a date picker. Filter state is encoded in the URL; detail links preserve the return query and browser Back restores the list. See [publication dates](gallery-publication-dates.md) for evidence and partial-date rules.

Each detail has a physical `papers/<category>/<slug>/index.html`, so direct URLs work without a single-page-app fallback. Internal paper links resolve to current site detail pages, category links return to filtered results, original paper/code links stay external, and other repository documents remain linked to GitHub. Mathematical notation is rendered with local KaTeX assets; tables scroll within the note on narrow screens. Existing legacy-language passages remain unchanged.

The build copies the exact original KaTeX WOFF2 font files and rewrites its stylesheet to reference only those files. It omits the redundant WOFF and TTF copies from deployment. The static check verifies every font reference and compares the delivered font bytes with the installed KaTeX source. Original summary PNGs and their embedded provenance remain byte-identical.

FVO/CalfVO, IDT/MVID and FlowR display the recorded unresolved source/content issue. The gallery does not turn source publication status or image integration into a claim of scientific verification.

## Verification

```sh
python -m unittest discover -s tools -p 'test_*.py'
python tools/verify_all.py
python tools/build_card_inventory.py --check
node site/check.mjs
node site/test-browser.mjs
```

The browser test uses Playwright. On Windows it can use installed Microsoft Edge; set `BROWSER_PATH` for another installed Chromium executable. On other systems install the test browser with `npx playwright install chromium`. Set `SITE_URL` to test the published site instead of localhost. The test covers desktop/mobile rendering, filter combinations, reset, empty results, browser Back, direct detail URLs, canonical moved paths, base path and poster loading. Screenshots and a machine-readable report are written to `site-test-results/`.

## Approved publication

Public GitHub Pages publication was explicitly approved for this repository. The `paper-gallery` workflow validates and builds pull requests; it uploads and deploys only from `main` or a manual run on `main`. Pull requests cannot deploy. The deployment job uses only `pages: write` and `id-token: write`; the build has `contents: read`, and no new secret or repository-write permission is introduced.

Configure the existing public repository's Pages source as GitHub Actions after review, then merge the validated change. The workflow publishes `_site` through the official Pages artifact/deployment actions. Published output is checked to remain below 1 GB. Existing images dominate that size and are loaded on demand in the gallery rather than all at once. No paid service, custom domain, login, comment system, recommendation service or analytics is configured.

To stop future publication, disable the `paper-gallery` workflow or change its trigger before merging a future change. To remove the live site, unpublish it in repository Pages settings. Source Markdown and PNG history remain available independently of the site.

# Gallery thumbnail pilot

The local pilot adds three dedicated landscape thumbnails: DUSt3R (two views to pointmaps), MASt3R (two views to matches), and VGGT (many views to joint geometry). These are new conceptual illustrations made with the official built-in image generation tool, using the existing inspected posters as scientific/style references. They contain no benchmark values or measured output claims. English labels and the posters' cream/forest-green palette are preserved. The current gallery chrome retains its existing white/navy palette; this pilot does not redesign the site.

The reviewed originals are 1672×941 PNGs, approximately 16:9. Display the entire image with `object-fit: contain` inside a 16:9 frame on desktop and mobile. Mobile images use the full card width so the name and short method caption remain legible. Never crop a portrait visual summary to make a listing thumbnail.

## Separate records and fallback

[paper-thumbnails.json](../data/paper-thumbnails.json) records canonical paper IDs, primary source identities, original asset paths, dimensions, SHA-256, alt text, prompts and pilot review status. [thumbnails.mjs](../site/thumbnails.mjs) validates those records independently of the visual-summary inventory. Store new listing assets under `assets/paper-thumbnails/en/<category>/<slug>.png`; the 337 full-size visual summaries remain under `assets/paper-cards/` and are used only in detail pages.

Only three thumbnail assets exist. The other 334 records use the explicit text fallback, with the method name and a short extract from its existing note. If a registered image fails to load, switch to the same text fallback. No placeholder borrows a different paper's image, and no fallback loads a full poster. Full titles, purpose and original notes remain available outside the image.

The new PNGs total about 7.75 MB. This pilot retains the official tool output bytes for visual review. No compressed web derivatives or additional paper thumbnails have been generated. Approval of these three compositions and the fallback/layout precedes any collection-wide production or public deployment.

## Local preview and checks

```sh
node --test site/build.test.mjs site/thumbnails.test.mjs
node site/build.mjs --out _site-thumbnails --thumbnail-preview
node site/check.mjs _site-thumbnails
python site/serve.py --directory _site-thumbnails --port 4177
```

Open `http://127.0.0.1:4177/DUSt3R-Paper-Collection/thumbnail-preview/` for the three-paper study and fallback example. Open the normal gallery on the same server to inspect real filtering and detail navigation. The preview-only study route is generated only with `--thumbnail-preview`.

In a second terminal, run `node site/test-thumbnail-browser.mjs` to check actual Edge rendering at 1440, 768, 390 and 360 pixels, image-load fallback and the preserved full-size detail poster. Use `SITE_URL` to select another local server. The test deliberately refuses public hosts. Reports and screenshots are written under ignored `site-test-results/thumbnail-pilot/`.

The static checker still validates all 337 canonical posters and 5,089 detail links, and now validates dedicated thumbnail hashes and text-fallback counts separately. Source-identity, separate-path, byte-integrity and aspect-ratio regressions are covered by the thumbnail tests. This is a layout/asset pilot, not a new scientific review of the paper collection.

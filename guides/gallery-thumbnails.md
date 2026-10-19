# Gallery thumbnails

Collection-wide production, main merges and incremental public rollout were explicitly approved on 2026-10-19. Dedicated landscape illustrations use the approved cream/forest-green palette, a large English paper name, one short input/output caption and a substantial conceptual method scene. No benchmark measurements, title-only replacement, or reduced summary poster qualifies as dedicated artwork.

[paper-thumbnails.json](../data/paper-thumbnails.json) records the authoritative completed set, canonical source identities, unchanged PNG masters, dimensions/hashes, prompts, original-paper method review and separate uncropped 960x540 WebP deliveries. [thumbnail-production-inventory.json](../data/thumbnail-production-inventory.json) exports the remaining IDs, sources, recorded issues and intended destinations. Regenerate it after each imported batch. Never overwrite completed artwork.

Read each original paper before choosing its caption and scene. Distinguish required inputs, optional priors, training, inference and downstream fine-tuning. For example, [CroCo Section 3 / Figure 3](https://arxiv.org/html/2210.10716v2) and [CroCo v2 Section 3 / Figure 2](https://arxiv.org/html/2211.10408v3) describe cross-view RGB completion during pre-training, not direct pointmap prediction. Resolve FVO/CalfVO, IDT/MVID and FlowR source issues before making claims for those jobs. Artwork is explanatory, not measured output.

Preserve all original visual summaries and detailed notes. Pending papers show their complete original summary at its native aspect ratio. Dedicated images use 16:9 frames; both use `object-fit: contain`. Failed dedicated images load the same paper's original summary. Text-only cards are forbidden.

Inspect each master and an actual 320px preview. Retain PNG bytes and create a separate contained/padded WebP (Lanczos, quality 85, method 6), recording both hashes. Validate inventories, identities, original-summary hashes, deliveries, detail links and responsive display. After merge, verify the deployed manifest, exact public WebP bytes/MIME and original detail images. Source review, generation, merge and deployment are separate stages.

```sh
python tools/build_thumbnail_inventory.py
python tools/build_thumbnail_inventory.py --check
node --test site/build.test.mjs site/thumbnails.test.mjs
node site/build.mjs --out _site-approved --base /DUSt3R-Paper-Collection/
node site/check.mjs _site-approved
python site/serve.py --directory _site-approved --port 4180
node site/test-thumbnail-production-browser.mjs
```

The production browser check accepts `SITE_URL` for the approved public site and comma-separated `THUMBNAIL_IDS` for a batch. It verifies desktop and 390/360/320px gallery frames, delivery hashes, public MIME and original detail posters. `test-summary-browser.mjs` gets counts from the deployed manifest. Reports/screenshots stay ignored under `site-test-results/`. The current manifest and latest verified deployment determine completion; historical records retain their original checkpoint meaning. Existing permissions, credentials and discovery schedules stay unchanged.

# Gallery publication dates

The gallery orders papers by first publication date, newest first. Equal dates use canonical paper IDs for a stable order. Year, Month and Day filters combine with search and category; detail links and browser Back retain the selection. Selecting a year or month clears unavailable dependent values. Reset clears every filter.

[publication-dates.json](../data/publication-dates.json) records one date and primary-source evidence for each canonical paper. For arXiv papers, use the first version's submission date: Atom `published` or the official abstract page's v1 submission history. Do not use Atom `updated`, later revisions, venue years or repository timestamps. For non-arXiv papers, use the original publisher's publication evidence.

Preserve source precision. A publisher month such as Pos3R's `2025-06` has no asserted day; the Day filter offers Unknown for that record. A genuinely unavailable date must be explicit with null date, unknown precision and unknown verification. Unknown dates sort last. Never invent January or day 01. The initial reviewed collection contains 336 exact arXiv v1 dates and one publisher month.

When adding or changing a canonical source, review and update its date evidence together with the inventory. Keep the source identity, source URL, retrieval time, raw-response hash and extracted v1/publication evidence. Build validation rejects missing or duplicate canonical records, identity mismatches, invalid calendar dates, unsupported precision and unverified known dates. Private response paths are excluded from committed evidence.

```sh
node --test site/publication-date-utils.test.mjs site/publication-dates.test.mjs
node site/build.mjs --base /DUSt3R-Paper-Collection/
node site/check.mjs
python site/serve.py --directory _site --port 4183
node site/test-date-browser.mjs
```

Set `SITE_URL` to the preview or public project URL when running the browser check. It verifies sorting, combined filters, dependent selections, partial dates, empty results, reset, deep links, detail/Back state and 1440/390/360/320px layouts. Existing discovery schedules and permissions are unchanged.

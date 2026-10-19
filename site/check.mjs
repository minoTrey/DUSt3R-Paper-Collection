import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const output = path.join(root, process.argv[2] || "_site");
const manifest = JSON.parse(fs.readFileSync(path.join(output, "build-manifest.json"), "utf8"));
const inventory = JSON.parse(
  fs.readFileSync(path.join(root, "data/paper-card-inventory.json"), "utf8"),
);
const expected = Object.fromEntries(
  [...new Set(inventory.papers.map((p) => p.category))].map((cat) => [
    cat,
    inventory.papers.filter((p) => p.category === cat).length,
  ]),
);
assert.equal(manifest.papers, inventory.total_papers);
assert.deepEqual(manifest.categories, expected);
const ids = new Set(manifest.records.map((r) => r.id));
assert.equal(ids.size, inventory.total_papers);
const byId = new Map(inventory.papers.map((r) => [r.record_id, r]));
const hash = (b) => crypto.createHash("sha256").update(b).digest("hex");
let pngs = 0,
  localLinks = 0;
for (const rec of manifest.records) {
  const item = byId.get(rec.id);
  assert.ok(item);
  assert.equal(rec.note, item.note_path);
  assert.equal(rec.sourceIdentity, item.paper_source_identity);
  assert.equal(hash(fs.readFileSync(path.join(root, rec.note), "utf8")), rec.noteSha256);
  const image = rec.image.slice(manifest.base.length);
  assert.equal(
    hash(fs.readFileSync(path.join(root, image))),
    hash(fs.readFileSync(path.join(output, image))),
  );
  pngs++;
  const file = path.join(output, "papers", rec.id, "index.html");
  assert.ok(fs.existsSync(file));
  const html = fs.readFileSync(file, "utf8");
  assert.ok(html.includes('class="detail-poster"'));
  assert.ok(html.includes('class="note-content"'));
  for (const m of html.matchAll(/\b(?:src|href)="([^"]+)"/g)) {
    const url = m[1].replaceAll("&amp;", "&");
    if (!url.startsWith(manifest.base)) continue;
    const logical = url.slice(manifest.base.length).split(/[?#]/)[0];
    const target = path.join(output, logical);
    assert.ok(fs.existsSync(target), `${rec.id}: ${url}`);
    localLinks++;
  }
}
const index = fs.readFileSync(path.join(output, "index.html"), "utf8");
assert.equal((index.match(/data-paper="/g) || []).length, inventory.total_papers);
assert.equal((index.match(/data-src="/g) || []).length, inventory.total_papers);
assert.ok(index.includes('loading="lazy"'));
assert.ok(index.includes('aria-live="polite"'));
const years = manifest.records.map((r) => r.year);
assert.deepEqual(
  years,
  [...years].sort((a, b) => b - a),
);
assert.ok(fs.existsSync(path.join(output, ".nojekyll")));
const size = (dir) =>
  fs
    .readdirSync(dir, { withFileTypes: true })
    .reduce(
      (n, e) =>
        n +
        (e.isDirectory() ? size(path.join(dir, e.name)) : fs.statSync(path.join(dir, e.name)).size),
      0,
    );
const bytes = size(output);
assert.ok(bytes < 1_000_000_000, "Generated public site must remain below 1 GB.");
console.log(
  JSON.stringify({
    papers: manifest.papers,
    detail_pages: manifest.papers,
    canonical_png_hashes: pngs,
    local_detail_links: localLinks,
    base: manifest.base,
    categories: manifest.categories,
    total_bytes: bytes,
    descending_years: true,
    missing_or_duplicate_papers: 0,
  }),
);

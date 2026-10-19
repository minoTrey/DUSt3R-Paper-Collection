import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadThumbnails, thumbnailFor } from "./thumbnails.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const inventory = JSON.parse(
  fs.readFileSync(path.join(root, "data/paper-card-inventory.json"), "utf8"),
);
test("dedicated images retain canonical source identities and reviewed bytes", () => {
  const manifest = loadThumbnails(root, inventory);
  const foundation = [
    "foundation/croco",
    "foundation/croco-v2",
    "foundation/dust3r",
    "foundation/mast3r",
    "foundation/vggt",
  ];
  for (const id of foundation) assert.ok(manifest.thumbnails[id]);
  assert.ok(Object.keys(manifest.thumbnails).length <= inventory.papers.length);
  assert.equal(thumbnailFor("foundation/dust3r", manifest).kind, "image");
});
test("a paper without dedicated art retains its complete original summary image", () => {
  const manifest = loadThumbnails(root, inventory);
  delete manifest.thumbnails["extensions/filt3r"];
  const fallback = thumbnailFor("extensions/filt3r", manifest, {
    path: "assets/paper-cards/en/extensions/filt3r.png",
    width: 1086,
    height: 1448,
  });
  assert.equal(fallback.kind, "visual_summary");
  assert.equal(fallback.path, "assets/paper-cards/en/extensions/filt3r.png");
});
function invalid(edit, pattern) {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), "paper-thumbnails-test-"));
  try {
    const manifest = loadThumbnails(root, inventory);
    manifest.thumbnails = { "foundation/dust3r": manifest.thumbnails["foundation/dust3r"] };
    const item = manifest.thumbnails["foundation/dust3r"];
    fs.mkdirSync(path.join(fixture, "data"));
    const target = path.join(fixture, item.path);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(root, item.path), target);
    const delivery = path.join(fixture, item.delivery.path);
    fs.copyFileSync(path.join(root, item.delivery.path), delivery);
    edit(item);
    fs.writeFileSync(path.join(fixture, "data/paper-thumbnails.json"), JSON.stringify(manifest));
    assert.throws(() => loadThumbnails(fixture, inventory), pattern);
  } finally {
    assert.equal(path.dirname(fs.realpathSync(fixture)), fs.realpathSync(os.tmpdir()));
    fs.rmSync(fixture, { recursive: true, force: true });
  }
}
test("source identity mismatch is rejected", () =>
  invalid((p) => (p.source_identity = "arxiv:0000.00000"), /identity/));
test("full-poster paths cannot be registered as thumbnail assets", () =>
  invalid((p) => (p.path = "assets/paper-cards/en/foundation/dust3r.png"), /separate canonical/));
test("changed image bytes require a new review hash", () =>
  invalid((p) => (p.sha256 = "0".repeat(64)), /bytes changed/));
test("portrait or misrecorded dimensions are rejected", () =>
  invalid((p) => (p.width = 100), /dimensions/));

test("delivery must retain the reviewed original identity", () =>
  invalid((p) => (p.delivery.source_sha256 = "0".repeat(64)), /canonical original/));
test("delivery byte changes require a renewed hash", () =>
  invalid((p) => (p.delivery.sha256 = "0".repeat(64)), /delivery bytes changed/));

test("missing artwork cannot become a text-only replacement", () =>
  assert.throws(
    () => thumbnailFor("extensions/filt3r", { thumbnails: {} }),
    /visual-summary image is required/,
  ));

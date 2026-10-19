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
test("all three dedicated images retain canonical source identities and reviewed bytes", () => {
  const manifest = loadThumbnails(root, inventory);
  assert.deepEqual(Object.keys(manifest.thumbnails).sort(), [
    "foundation/dust3r",
    "foundation/mast3r",
    "foundation/vggt",
  ]);
  assert.equal(thumbnailFor("foundation/dust3r", manifest).kind, "image");
});
test("a paper without dedicated art gets text, never a full-poster fallback", () => {
  const fallback = thumbnailFor("foundation/croco", loadThumbnails(root, inventory));
  assert.equal(fallback.kind, "text");
  assert.equal(fallback.path, undefined);
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

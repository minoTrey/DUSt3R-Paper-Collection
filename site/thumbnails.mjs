import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

// Listing art has its own identity and review. Full visual summaries never act as thumbnails.
export function loadThumbnails(root, inventory) {
  const manifest = JSON.parse(
    fs.readFileSync(path.join(root, "data/paper-thumbnails.json"), "utf8"),
  );
  if (manifest.schema_version !== 1 || manifest.fallback?.kind !== "text")
    throw new Error("Thumbnail manifest requires schema 1 and an explicit text fallback.");
  const papers = new Map(inventory.papers.map((p) => [p.record_id, p]));
  for (const [id, item] of Object.entries(manifest.thumbnails)) {
    const paper = papers.get(id);
    if (!paper || paper.paper_source_identity !== item.source_identity)
      throw new Error("Thumbnail source identity does not match canonical paper: " + id);
    if (item.path !== `assets/paper-thumbnails/en/${id}.png`)
      throw new Error("Thumbnail must have its separate canonical asset path: " + id);
    const bytes = fs.readFileSync(path.join(root, item.path));
    if (!bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])))
      throw new Error("Thumbnail must be a PNG: " + id);
    if (
      bytes.readUInt32BE(16) !== item.width ||
      bytes.readUInt32BE(20) !== item.height ||
      Math.abs(item.width / item.height - 16 / 9) > 0.01
    )
      throw new Error("Thumbnail dimensions must match a landscape 16:9 asset: " + id);
    if (crypto.createHash("sha256").update(bytes).digest("hex") !== item.sha256)
      throw new Error("Thumbnail bytes changed after review: " + id);
    if (!item.alt || !item.caption || item.review?.status !== "pilot_visual_reviewed")
      throw new Error("Thumbnail requires accessible text and a recorded review: " + id);
  }
  return manifest;
}

export function thumbnailFor(id, manifest) {
  const item = manifest.thumbnails[id];
  return item ? { kind: "image", ...item } : { kind: "text", ...manifest.fallback };
}

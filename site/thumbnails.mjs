import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

function webpDimensions(bytes) {
  if (bytes.toString("ascii", 0, 4) !== "RIFF" || bytes.toString("ascii", 8, 12) !== "WEBP")
    throw new Error("Invalid WebP signature.");
  for (let offset = 12; offset + 8 <= bytes.length;) {
    const type = bytes.toString("ascii", offset, offset + 4);
    const size = bytes.readUInt32LE(offset + 4);
    const start = offset + 8;
    if (start + size > bytes.length) throw new Error("Truncated WebP chunk.");
    if (type === "VP8X" && size >= 10)
      return [1 + bytes.readUIntLE(start + 4, 3), 1 + bytes.readUIntLE(start + 7, 3)];
    if (type === "VP8 " && size >= 10 && bytes.toString("hex", start + 3, start + 6) === "9d012a")
      return [bytes.readUInt16LE(start + 6) & 0x3fff, bytes.readUInt16LE(start + 8) & 0x3fff];
    if (type === "VP8L" && size >= 5 && bytes[start] === 0x2f) {
      const dimensions = bytes.readUInt32LE(start + 1);
      return [1 + (dimensions & 0x3fff), 1 + ((dimensions >>> 14) & 0x3fff)];
    }
    offset = start + size + (size % 2);
  }
  throw new Error("WebP dimensions were not found.");
}

// Dedicated listing art is separate; missing art uses the complete original visual summary.
export function loadThumbnails(root, inventory) {
  const manifest = JSON.parse(
    fs.readFileSync(path.join(root, "data/paper-thumbnails.json"), "utf8"),
  );
  if (manifest.schema_version !== 1 || manifest.fallback?.kind !== "visual_summary")
    throw new Error(
      "Thumbnail manifest requires schema 1 and an explicit visual-summary image fallback.",
    );
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
    const web = item.delivery;
    if (
      !web ||
      web.path !== `assets/paper-thumbnails/en/${id}.webp` ||
      web.source_sha256 !== item.sha256
    )
      throw new Error("Thumbnail delivery must identify its canonical original: " + id);
    const delivered = fs.readFileSync(path.join(root, web.path));
    const [width, height] = webpDimensions(delivered);
    if (width !== web.width || height !== web.height || width / height !== 16 / 9)
      throw new Error("Thumbnail delivery dimensions must match a 16:9 WebP: " + id);
    if (crypto.createHash("sha256").update(delivered).digest("hex") !== web.sha256)
      throw new Error("Thumbnail delivery bytes changed after review: " + id);
    if (
      !item.alt ||
      !item.caption ||
      !["pilot_visual_reviewed", "visual_reviewed"].includes(item.review?.status)
    )
      throw new Error("Thumbnail requires accessible text and a recorded review: " + id);
  }
  return manifest;
}

export function thumbnailFor(id, manifest, summary) {
  const item = manifest.thumbnails[id];
  if (!item && (!summary?.path || !summary?.width || !summary?.height))
    throw new Error("A canonical visual-summary image is required when dedicated art is absent.");
  return item
    ? { kind: "image", ...item, ...item.delivery, masterPath: item.path }
    : { ...summary, kind: "visual_summary" };
}

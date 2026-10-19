import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { chromium } from "playwright";

const base = process.env.SITE_URL || "http://127.0.0.1:4180/DUSt3R-Paper-Collection/";
assert.ok(["127.0.0.1", "localhost", "minotrey.github.io"].includes(new URL(base).hostname));
const output = path.resolve("site-test-results/thumbnail-production");
fs.mkdirSync(output, { recursive: true });
const context = await chromium.launchPersistentContext(
  fs.mkdtempSync(path.join(output, "profile-")),
  {
    headless: true,
    executablePath:
      process.env.BROWSER_PATH || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  },
);
const report = { base, checked: [], layouts: [], errors: [] };
try {
  const response = await context.request.get(base + "build-manifest.json");
  assert.equal(response.status(), 200);
  const manifest = await response.json();
  const selected = process.env.THUMBNAIL_IDS?.split(",");
  const records = manifest.records.filter(
    (r) => r.thumbnail.kind === "image" && (!selected || selected.includes(r.id)),
  );
  assert.ok(records.length > 0);
  if (selected) assert.equal(records.length, selected.length);
  const page = await context.newPage();
  page.on("pageerror", (error) => report.errors.push(error.message));
  for (const record of records) {
    const asset = await context.request.get(new URL(record.thumbnail.path, base).href);
    assert.equal(asset.status(), 200);
    if (new URL(base).hostname === "minotrey.github.io") {
      assert.ok(asset.headers()["content-type"].includes("image/webp"));
    }
    assert.equal(
      crypto
        .createHash("sha256")
        .update(await asset.body())
        .digest("hex"),
      record.thumbnail.sha256,
    );
    report.checked.push({ id: record.id, exact_delivery_hash: record.thumbnail.sha256 });
  }
  for (const width of [1440, 390, 360, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const record of records) {
      await page.goto(base + "?category=" + record.id.split("/")[0], {
        waitUntil: "domcontentloaded",
      });
      assert.equal(await page.locator(".paper-image img").count(), manifest.papers);
      assert.equal(
        await page.locator('[data-thumbnail-kind="image"]').count(),
        manifest.dedicatedThumbnails,
      );
      assert.equal(
        await page.locator('[data-thumbnail-kind="visual_summary"]').count(),
        manifest.summaryFallbacks,
      );
      assert.equal(await page.locator('[data-thumbnail-kind="text"]').count(), 0);
      const card = page.locator(`[data-paper="${record.id}"]`);
      await card.scrollIntoViewIfNeeded();
      const image = card.locator("img");
      await page.waitForFunction((id) => {
        const img = document.querySelector(`[data-paper="${id}"] img`);
        return img?.complete && img.naturalWidth > 0;
      }, record.id);
      await image.evaluate((img) => img.decode());
      assert.ok((await image.getAttribute("src")).endsWith(record.thumbnail.path));
      assert.equal(await image.evaluate((img) => getComputedStyle(img).objectFit), "contain");
      assert.equal(await image.evaluate((img) => img.naturalWidth), 960);
      const box = await card.locator(".paper-image").boundingBox();
      assert.ok(Math.abs(box.width / box.height - 16 / 9) < 0.01);
      assert.equal(
        await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
        false,
      );
      await card.locator(".paper-image").screenshot({
        path: path.join(output, width + "-" + record.id.replaceAll("/", "-") + ".png"),
      });
      report.layouts.push({
        id: record.id,
        viewport: width,
        image_width: box.width,
        image_height: box.height,
        contain: true,
      });
    }
  }
  for (const record of records) {
    await page.goto(new URL(record.url, base).href, { waitUntil: "domcontentloaded" });
    const poster = page.locator(".detail-poster");
    assert.equal(await poster.getAttribute("src"), record.image);
    await poster.evaluate((img) => img.decode());
    assert.ok(await poster.evaluate((img) => img.naturalHeight > img.naturalWidth));
  }
  assert.deepEqual(report.errors, []);
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
} finally {
  await context.close();
}

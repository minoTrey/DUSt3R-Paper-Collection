import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const base = process.env.SITE_URL || "http://127.0.0.1:4177/DUSt3R-Paper-Collection/";
assert.ok(
  ["127.0.0.1", "localhost", "minotrey.github.io"].includes(new URL(base).hostname),
  "Use the local preview or approved public gallery.",
);
const output = path.resolve("site-test-results/foundation-thumbnails");
fs.mkdirSync(output, { recursive: true });
fs.rmSync(path.join(output, "report.json"), { force: true });
const profile = fs.mkdtempSync(path.join(output, "profile-"));
const context = await chromium.launchPersistentContext(profile, {
  headless: true,
  executablePath:
    process.env.BROWSER_PATH || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
});
const report = { url: base, layouts: [], checks: [], errors: [] };
const page = context.pages()[0];
page.on("pageerror", (e) => report.errors.push(e.message));
page.on("response", (r) => {
  if (r.url().startsWith(base) && r.status() >= 400) report.errors.push(r.status() + " " + r.url());
});
try {
  for (const [width, height] of [
    [1440, 1000],
    [768, 1024],
    [390, 844],
    [360, 800],
  ]) {
    await page.setViewportSize({ width, height });
    await page.goto(base + "?category=foundation", { waitUntil: "domcontentloaded" });
    for (const slug of ["croco", "croco-v2", "dust3r", "mast3r", "vggt"]) {
      const card = page.locator(`[data-paper="foundation/${slug}"]`);
      await card.scrollIntoViewIfNeeded();
      const image = card.locator("img");
      await page.waitForFunction((id) => {
        const img = document.querySelector(`[data-paper="foundation/${id}"] img`);
        return img?.complete && img.naturalWidth > 0;
      }, slug);
      await image.evaluate((img) => img.decode());
      const frame = await card.locator(".paper-image").boundingBox();
      assert.ok(Math.abs(frame.width / frame.height - 16 / 9) < 0.01);
      assert.ok(
        frame.width >= (width <= 390 ? width - 45 : 280),
        `${width}px ${slug}: image width ${frame.width}`,
      );
      assert.equal(await image.evaluate((img) => getComputedStyle(img).objectFit), "contain");
      assert.equal(await image.getAttribute("width"), "960");
      await card
        .locator(".paper-image")
        .screenshot({ path: path.join(output, `${width}-${slug}.png`) });
      report.layouts.push({
        viewport: width,
        paper: slug,
        rendered_width: frame.width,
        rendered_height: frame.height,
        object_fit: "contain",
        full_image_visible: true,
      });
    }
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
      false,
    );
    await page.screenshot({ path: path.join(output, `${width}-preview.png`), fullPage: true });
  }
  report.checks.push(
    "Five Foundation images: 16:9, full composition, desktop/tablet/390px/360px with no page overflow.",
  );
  const requested = [];
  page.on("request", (r) => requested.push(r.url()));
  await page.goto(base + "?category=foundation", { waitUntil: "domcontentloaded" });
  assert.equal(await page.locator(".paper-item:not([hidden])").count(), 5);
  assert.equal(
    await page.locator('.paper-item:not([hidden]) [data-thumbnail-kind="image"]').count(),
    5,
  );
  assert.equal(
    await page.locator('.paper-item:not([hidden]) [data-thumbnail-kind="text"]').count(),
    0,
  );
  assert.equal(
    requested.some((u) => u.includes("/paper-cards/")),
    false,
  );
  report.checks.push(
    "Real filtered gallery: five dedicated thumbnails, no text fallbacks, no full-poster requests.",
  );
  await page.goto(base + "papers/foundation/dust3r/", { waitUntil: "domcontentloaded" });
  const poster = page.locator(".detail-poster");
  await poster.evaluate((img) => img.decode());
  assert.ok((await poster.getAttribute("src")).endsWith("/paper-cards/en/foundation/dust3r.png"));
  assert.equal(await poster.evaluate((img) => img.naturalWidth), 1086);
  assert.equal(await poster.evaluate((img) => img.naturalHeight), 1448);
  await page.screenshot({ path: path.join(output, "mobile-original-detail.png"), fullPage: false });
  report.checks.push("Detail retains the original 1086×1448 visual summary.");
  const broken = await context.newPage();
  await broken.route("**/paper-thumbnails/en/foundation/dust3r.webp", (route) => route.abort());
  await broken.goto(base + "?category=foundation", { waitUntil: "domcontentloaded" });
  const frame = broken.locator('[data-paper="foundation/dust3r"] .paper-image');
  await frame.scrollIntoViewIfNeeded();
  await frame.locator("[data-thumbnail-fallback]").waitFor({ state: "visible" });
  assert.equal(await frame.locator("img").isVisible(), false);
  assert.equal(await frame.getAttribute("data-thumbnail-kind"), "text");
  report.checks.push(
    "Failed image request switches to accessible text fallback without a broken-image icon.",
  );
  await broken.close();
  assert.deepEqual(report.errors, []);
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
} finally {
  await context.close();
}

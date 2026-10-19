import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const base = process.env.SITE_URL || "http://127.0.0.1:4177/DUSt3R-Paper-Collection/";
const output = path.resolve("site-test-results/summary-image-correction");
fs.mkdirSync(output, { recursive: true });
const context = await chromium.launchPersistentContext(
  fs.mkdtempSync(path.join(output, "profile-")),
  {
    headless: true,
    executablePath:
      process.env.BROWSER_PATH || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  },
);
const page = context.pages()[0];
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
page.on("response", (r) => {
  if (r.url().startsWith(base) && r.status() >= 400) errors.push(r.status() + " " + r.url());
});
const report = {
  url: base,
  actual_listing_images: 337,
  dedicated_images: 5,
  complete_original_summaries: 332,
  text_only_cards: 0,
  layouts: [],
  errors,
};
try {
  for (const [width, height] of [
    [1440, 1000],
    [768, 1024],
    [390, 844],
    [360, 800],
  ]) {
    await page.setViewportSize({ width, height });
    await page.goto(base + "?category=dynamic", { waitUntil: "domcontentloaded" });
    assert.equal(await page.locator(".paper-image img").count(), 337);
    assert.equal(await page.locator('[data-thumbnail-kind="visual_summary"]').count(), 332);
    assert.equal(await page.locator('[data-thumbnail-kind="image"]').count(), 5);
    assert.equal(await page.locator('.paper-fallback, [data-thumbnail-kind="text"]').count(), 0);
    const card = page.locator(".paper-item:not([hidden])").first();
    await card.evaluate((el) =>
      window.scrollTo({
        top: el.getBoundingClientRect().top + window.scrollY,
        behavior: "instant",
      }),
    );
    await page.waitForFunction(() => {
      const img = document.querySelector(".paper-item:not([hidden]) img");
      return img?.complete && img.naturalWidth > 0;
    });
    const img = card.locator("img");
    const metrics = await img.evaluate((el) => ({
      width: el.naturalWidth,
      height: el.naturalHeight,
      fit: getComputedStyle(el).objectFit,
      src: el.getAttribute("src"),
    }));
    const frame = await card.locator(".paper-image").boundingBox();
    assert.ok(
      frame.y >= -1 && frame.y + frame.height <= height + 1,
      "The complete poster must fit inside the captured viewport.",
    );
    assert.ok(metrics.src.includes("/paper-cards/"));
    assert.equal(metrics.fit, "contain");
    assert.ok(Math.abs(frame.width / frame.height - metrics.width / metrics.height) < 0.01);
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
      false,
    );
    await page.screenshot({ path: path.join(output, `${width}-all-image-gallery.png`) });
    report.layouts.push({
      viewport: width,
      poster_width: frame.width,
      poster_height: frame.height,
      original_width: metrics.width,
      original_height: metrics.height,
      complete_image_visible: true,
      object_fit: metrics.fit,
    });
  }
  assert.deepEqual(errors, []);
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
} finally {
  await context.close();
}

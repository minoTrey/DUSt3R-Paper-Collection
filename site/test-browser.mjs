import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const url = process.env.SITE_URL || "http://127.0.0.1:4175/DUSt3R-Paper-Collection/";
const base = new URL(url);
if (!base.pathname.endsWith("/")) throw new Error("SITE_URL must end with a slash.");
const output = path.resolve(root, "site-test-results");
fs.mkdirSync(output, { recursive: true });
fs.rmSync(path.join(output, "browser-report.json"), { force: true });
const profile = fs.mkdtempSync(path.join(output, "profile-"));
const launch = { headless: true, viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 };
if (process.env.BROWSER_PATH) launch.executablePath = process.env.BROWSER_PATH;
else if (process.platform === "win32")
  launch.executablePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const context = await chromium.launchPersistentContext(profile, launch);
const failures = [];
const completed = [];
const page = context.pages()[0] || (await context.newPage());
page.on("pageerror", (e) => failures.push(e.message));
page.on("response", (r) => {
  if (r.url().startsWith(base.origin + base.pathname) && r.status() >= 400)
    failures.push(r.status() + " " + r.url());
});
const count = () => page.locator(".paper-item:not([hidden])").count();
async function noOverflow() {
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
    false,
    "Horizontal page overflow",
  );
}
async function visibleImages() {
  await page.waitForFunction(() =>
    [...document.querySelectorAll(".paper-item:not([hidden]) img")]
      .filter((img) => {
        const r = img.getBoundingClientRect();
        return r.top < innerHeight && r.bottom > 0;
      })
      .every((img) => img.complete && img.naturalWidth > 0),
  );
}
async function detailImage() {
  await page.waitForFunction(() => {
    const img = document.querySelector(".detail-poster");
    return img && img.complete && img.naturalWidth > 0;
  });
}
try {
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#result-count");
  assert.equal(await count(), 337);
  await visibleImages();
  await noOverflow();
  assert.equal(await page.locator(".paper-item img").first().getAttribute("loading"), "lazy");
  await page.screenshot({ path: path.join(output, "desktop-gallery.png") });
  completed.push("desktop gallery,337 papers,lazy images,no overflow");
  await page.selectOption("#category", "robotics");
  assert.equal(await count(), 7);
  await page.selectOption("#year", "2026");
  assert.equal(await count(), 4);
  await page.fill("#query", "navigation");
  assert.equal(await count(), 1);
  assert.ok(
    (await page.locator(".paper-item:not([hidden])").getAttribute("data-paper")).includes("lg-vln"),
  );
  completed.push("search/category/year AND combination");
  await page.locator(".paper-item:not([hidden]) .paper-title").click();
  await page.waitForLoadState("domcontentloaded");
  await page.waitForSelector(".detail-poster");
  await detailImage();
  assert.ok(page.url().includes("/papers/robotics/lg-vln/"));
  assert.ok((await page.locator("[data-back]").getAttribute("href")).includes("category=robotics"));
  await noOverflow();
  await page.screenshot({ path: path.join(output, "desktop-detail.png") });
  await page.goBack({ waitUntil: "domcontentloaded" });
  assert.equal(await page.inputValue("#query"), "navigation");
  assert.equal(await page.inputValue("#category"), "robotics");
  assert.equal(await count(), 1);
  completed.push("detail poster and browser back preserves filters");
  await page.fill("#query", "no-paper-matches-this-phrase-9471");
  assert.equal(await count(), 0);
  assert.equal(await page.locator("#empty-state").isVisible(), true);
  await page.click("#clear-empty");
  assert.equal(await count(), 337);
  assert.equal(await page.inputValue("#category"), "");
  assert.equal(await page.inputValue("#year"), "");
  assert.equal(await page.inputValue("#query"), "");
  completed.push("empty results and full filter reset");
  await page.goto(url + "?category=pose&year=2025&q=FVO", { waitUntil: "domcontentloaded" });
  assert.equal(await count(), 1);
  assert.equal(
    await page.locator(".paper-item:not([hidden])").getAttribute("data-paper"),
    "pose/fvo",
  );
  const firstYears = await page.locator(".paper-item:not([hidden]) .paper-meta").allTextContents();
  assert.ok(firstYears[0].includes("2025"));
  completed.push("query deep-link uses preprint year instead of verification date");
  await page.goto(url + "papers/reconstruction/samv-dust3r/", { waitUntil: "domcontentloaded" });
  await detailImage();
  assert.equal(await page.locator(".note-content h2").count(), 7);
  assert.ok(
    (await page.locator(".detail-poster").getAttribute("src")).includes(
      "/reconstruction/samv-dust3r.png",
    ),
  );
  await page.locator("[data-back]").click();
  await page.waitForSelector("#result-count");
  assert.equal(await count(), 337);
  completed.push("moved canonical detail direct URL and base path");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(url, { waitUntil: "domcontentloaded" });
  await visibleImages();
  await noOverflow();
  await page.screenshot({ path: path.join(output, "mobile-gallery.png") });
  await page.selectOption("#category", "medical");
  assert.equal(await count(), 4);
  await page.fill("#query", "endoscopic");
  assert.ok((await count()) > 0);
  await noOverflow();
  await page.locator(".paper-item:not([hidden]) .paper-title").first().click();
  await detailImage();
  await noOverflow();
  await page.screenshot({ path: path.join(output, "mobile-detail.png") });
  completed.push("mobile390px gallery,filters,detail,image and overflow");
  await page.setViewportSize({ width: 360, height: 800 });
  await noOverflow();
  completed.push("mobile360px detail overflow");
  assert.deepEqual(failures, []);
  const report = {
    url,
    viewport_desktop: "1440x1000",
    viewport_mobile: ["390x844", "360x800"],
    completed,
    failed_requests_or_script_errors: failures,
    screenshots: [
      "desktop-gallery.png",
      "desktop-detail.png",
      "mobile-gallery.png",
      "mobile-detail.png",
    ],
  };
  fs.writeFileSync(
    path.join(output, "browser-report.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(JSON.stringify(report));
} finally {
  await context.close();
}

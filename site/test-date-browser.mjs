import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";
import dates from "./publication-date-utils.js";

const base = process.env.SITE_URL || "http://127.0.0.1:4182/DUSt3R-Paper-Collection/";
assert.ok(["127.0.0.1", "localhost", "minotrey.github.io"].includes(new URL(base).hostname));
const output = path.resolve("site-test-results/publication-dates");
fs.mkdirSync(output, { recursive: true });
const context = await chromium.launchPersistentContext(
  fs.mkdtempSync(path.join(output, "profile-")),
  {
    headless: true,
    executablePath:
      process.env.BROWSER_PATH || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  },
);
const page = await context.newPage();
const errors = [];
page.on("pageerror", (e) => errors.push(e.message));
const report = { base, checks: [], layouts: [] };
const visible = () => page.locator(".paper-item:not([hidden])");
async function open(query = "") {
  await page.goto(base + query, { waitUntil: "domcontentloaded" });
  await page.waitForSelector('#filters[data-ready="true"]');
}
async function ids() {
  return visible().evaluateAll((items) => items.map((item) => item.dataset.paper));
}
async function count(n) {
  assert.equal(await visible().count(), n);
  assert.equal(
    await page.locator("#result-count").textContent(),
    n + (n === 1 ? " paper" : " papers"),
  );
}
try {
  await open();
  const records = await page.locator("#paper-data").evaluate((e) => JSON.parse(e.textContent));
  assert.deepEqual(
    await ids(),
    [...records].sort(dates.compare).map((p) => p.id),
  );
  await count(records.length);
  assert.equal(await page.locator("#month").isDisabled(), true);
  assert.equal(await page.locator("#day").isDisabled(), true);
  report.checks.push("All cards use descending first-publication date and canonical-ID ties");
  await open("?q=DUSt3R&category=foundation&year=2023&month=12&day=21");
  assert.deepEqual(await ids(), ["foundation/dust3r"]);
  await count(1);
  await visible().locator(".paper-title").click();
  await page.waitForSelector("[data-back]");
  const back = new URL(await page.locator("[data-back]").getAttribute("href"), base);
  for (const [key, value] of Object.entries({
    q: "DUSt3R",
    category: "foundation",
    year: "2023",
    month: "12",
    day: "21",
  }))
    assert.equal(back.searchParams.get(key), value);
  await page.goBack({ waitUntil: "domcontentloaded" });
  await page.waitForSelector('#filters[data-ready="true"]');
  assert.deepEqual(await ids(), ["foundation/dust3r"]);
  report.checks.push(
    "Year/month/day AND search/category; detail and browser Back retain all filters",
  );
  await page.selectOption("#year", "2022");
  assert.equal(await page.inputValue("#month"), "");
  assert.equal(await page.inputValue("#day"), "");
  assert.equal(await page.locator("#day").isDisabled(), true);
  report.checks.push("Changing year clears unavailable dependent values");
  await open("?year=2025&month=06&day=unknown&q=Pos3R&category=pose");
  assert.deepEqual(await ids(), ["pose/pos3r"]);
  assert.ok((await visible().locator("time").getAttribute("datetime")) === "2025-06");
  const knownDay = await page
    .locator("#day option")
    .evaluateAll((options) => options.map((o) => o.value).find((v) => /^\d/.test(v)));
  await page.selectOption("#day", knownDay);
  await count(0);
  assert.equal(await page.locator("#empty-state").isVisible(), true);
  await page.click("#clear-empty");
  await count(records.length);
  for (const selector of ["#query", "#category", "#year", "#month", "#day"])
    assert.equal(await page.inputValue(selector), "");
  assert.equal(await page.locator("#month").isDisabled(), true);
  assert.equal(await page.locator("#day").isDisabled(), true);
  report.checks.push(
    "Publisher month precision stays 2025-06; unknown day is explicit; empty/reset work",
  );
  await open("?year=2025&month=99&day=31");
  assert.equal(await page.inputValue("#month"), "");
  assert.equal(await page.inputValue("#day"), "");
  await open("?year=1900&month=02&day=31");
  assert.equal(await page.inputValue("#year"), "");
  await count(records.length);
  report.checks.push("Invalid deep-link date components normalize without invented dates");
  for (const width of [1440, 390, 360, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    await open("?year=2025&month=06");
    assert.equal(
      await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
      false,
    );
    for (const selector of ["#year", "#month", "#day"]) {
      const box = await page.locator(selector).boundingBox();
      assert.ok(box.width >= 60 && box.x >= 0 && box.x + box.width <= width);
    }
    await page.screenshot({ path: path.join(output, `filters-${width}.png`) });
    report.layouts.push({ width, noOverflow: true, allDateControlsVisible: true });
  }
  assert.deepEqual(errors, []);
  fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
} finally {
  await context.close();
}

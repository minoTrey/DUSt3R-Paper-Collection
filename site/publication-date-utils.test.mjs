import test from "node:test";
import assert from "node:assert/strict";
import dates from "./publication-date-utils.js";

const paper = (id, date, precision, venueYear = 2026) => ({
  id,
  year: venueYear,
  publication: { date, precision },
});
const records = [
  paper("foundation/dust3r", "2023-12-21", "day", 2024),
  paper("b", "2025-06-15", "day"),
  paper("a", "2025-06-15", "day"),
  paper("month", "2025-06", "month"),
  paper("year", "2025", "year"),
  paper("unknown", null, "unknown"),
];

test("first-publication dates sort independently of venue year with deterministic ties", () => {
  assert.deepEqual(
    [...records].sort(dates.compare).map((p) => p.id),
    ["a", "b", "month", "year", "foundation/dust3r", "unknown"],
  );
});
test("partial dates retain their actual precision", () => {
  assert.deepEqual(dates.parts(records[3].publication), { year: 2025, month: 6, day: null });
  assert.deepEqual(dates.parts(records[4].publication), { year: 2025, month: null, day: null });
  assert.equal(
    dates.matches(records[3].publication, { year: "2025", month: "06", day: "01" }),
    false,
  );
  assert.equal(dates.matches(records[4].publication, { year: "2025", month: "01" }), false);
});
test("invalid calendar dates and invented precision are rejected", () => {
  for (const [date, precision] of [
    ["2025-02-29", "day"],
    ["2025-04-31", "day"],
    ["2025-13", "month"],
    ["2025", "day"],
    ["2025-01-01", "year"],
    [null, "day"],
  ])
    assert.throws(() => dates.parts({ date, precision }));
  assert.equal(dates.parts({ date: "2024-02-29", precision: "day" }).day, 29);
});
test("year changes clear incompatible month/day without inventing options", () => {
  assert.deepEqual(dates.normalize(records, { year: "2023", month: "06", day: "15" }), {
    year: "2023",
    month: "",
    day: "",
  });
  assert.deepEqual(dates.normalize(records, { year: "2025", month: "6", day: "15" }), {
    year: "2025",
    month: "06",
    day: "15",
  });
  assert.deepEqual(dates.normalize(records, { year: "", month: "06", day: "15" }), {
    year: "",
    month: "",
    day: "",
  });
});
test("known and unknown dates can be filtered explicitly", () => {
  assert.equal(dates.matches(records[5].publication, { year: "unknown" }), true);
  assert.equal(dates.matches(records[0].publication, { year: "unknown" }), false);
  assert.deepEqual(dates.options(records, "month", { year: "2025" }), ["06", "unknown"]);
  assert.deepEqual(dates.options(records, "day", { year: "2025", month: "06" }), ["15", "unknown"]);
  assert.deepEqual(dates.normalize(records, { year: "unknown", month: "06", day: "15" }), {
    year: "unknown",
    month: "",
    day: "",
  });
});

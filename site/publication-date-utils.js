(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.PaperDates = api;
})(globalThis, function () {
  function parts(publication) {
    const { date, precision } = publication || {};
    if (date == null && precision === "unknown") return { year: null, month: null, day: null };
    const match = typeof date === "string" && /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?$/.exec(date);
    if (!match) throw new Error("Invalid publication date.");
    const year = Number(match[1]);
    const month = match[2] ? Number(match[2]) : null;
    const day = match[3] ? Number(match[3]) : null;
    const actualPrecision = day != null ? "day" : month != null ? "month" : "year";
    const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
    const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if (
      year < 1 ||
      (month != null && (month < 1 || month > 12)) ||
      (day != null && (day < 1 || day > days[month - 1])) ||
      precision !== actualPrecision
    )
      throw new Error("Publication date precision or calendar value is invalid.");
    return { year, month, day };
  }
  function compare(a, b) {
    const left = a.publication?.date || "";
    const right = b.publication?.date || "";
    return right.localeCompare(left, "en") || a.id.localeCompare(b.id, "en");
  }
  function matches(publication, selection) {
    const date = parts(publication);
    for (const key of ["year", "month", "day"]) {
      const value = selection[key];
      if (!value) continue;
      if (value === "unknown" ? date[key] != null : date[key] !== Number(value)) return false;
    }
    return true;
  }
  const valueOf = (value) => (value == null ? "unknown" : String(value).padStart(2, "0"));
  function options(records, key, selection = {}) {
    const values = new Set();
    for (const paper of records) {
      const date = parts(paper.publication);
      if (key !== "year" && date.year !== Number(selection.year)) continue;
      if (key === "day" && date.month !== Number(selection.month)) continue;
      if (key !== "year" && (!selection.year || selection.year === "unknown")) continue;
      if (key === "day" && (!selection.month || selection.month === "unknown")) continue;
      values.add(
        key === "year" ? (date.year == null ? "unknown" : String(date.year)) : valueOf(date[key]),
      );
    }
    return [...values].sort((a, b) =>
      a === "unknown"
        ? 1
        : b === "unknown"
          ? -1
          : key === "year"
            ? Number(b) - Number(a)
            : Number(a) - Number(b),
    );
  }
  function normalize(records, selection = {}) {
    const year = options(records, "year").includes(selection.year) ? selection.year : "";
    const wantedMonth = /^\d{1,2}$/.test(selection.month || "")
      ? selection.month.padStart(2, "0")
      : selection.month;
    const month = options(records, "month", { year }).includes(wantedMonth) ? wantedMonth : "";
    const wantedDay = /^\d{1,2}$/.test(selection.day || "")
      ? selection.day.padStart(2, "0")
      : selection.day;
    const day = options(records, "day", { year, month }).includes(wantedDay) ? wantedDay : "";
    return { year, month, day };
  }
  return Object.freeze({ parts, compare, matches, options, normalize });
});

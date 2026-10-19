(() => {
  const base = document.body.dataset.base;
  const back = document.querySelector("[data-back]");
  if (back) {
    const from = new URLSearchParams(location.search).get("from");
    if (from && from.startsWith("?") && !/[<>]/.test(from)) back.href = base + from + "#papers";
  }
  const form = document.querySelector("#filters");
  document.querySelectorAll(".paper-image img[data-src]").forEach((img) => {
    img.addEventListener(
      "error",
      () => {
        const fallback = img.dataset.summarySrc;
        if (fallback && img.getAttribute("src") !== fallback) {
          img.closest(".paper-image").dataset.thumbnailKind = "visual_summary";
          img.width = Number(img.dataset.summaryWidth);
          img.height = Number(img.dataset.summaryHeight);
          img.src = fallback;
        }
      },
      { once: true },
    );
  });
  const images = new IntersectionObserver(
    (entries) =>
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          images.unobserve(img);
        }
      }),
    { rootMargin: "180px" },
  );
  document.querySelectorAll("img[data-src]").forEach((img) => images.observe(img));
  if (!form) return;
  const records = JSON.parse(document.querySelector("#paper-data").textContent);
  const cards = new Map(
    [...document.querySelectorAll("[data-paper]")].map((card) => [card.dataset.paper, card]),
  );
  const query = document.querySelector("#query");
  const category = document.querySelector("#category");
  const year = document.querySelector("#year");
  const month = document.querySelector("#month");
  const day = document.querySelector("#day");
  const dates = window.PaperDates;
  let dateNavigation;
  const monthNames = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#empty-state");
  const reset = form.querySelector("[type=reset]");
  function refreshDates(preferred = { year: year.value, month: month.value, day: day.value }) {
    const selection = dates.normalize(records, preferred);
    year.value = selection.year;
    const fill = (select, key, disabled) => {
      select.replaceChildren(new Option("All", ""));
      for (const value of dates.options(records, key, selection)) {
        const label =
          value === "unknown"
            ? "Unknown"
            : key === "month"
              ? monthNames[Number(value) - 1]
              : String(Number(value));
        select.add(new Option(label, value));
      }
      select.disabled = disabled;
      select.value = selection[key];
    };
    fill(month, "month", !selection.year || selection.year === "unknown");
    fill(day, "day", !selection.month || selection.month === "unknown");
    dateNavigation?.render();
  }
  function readURL() {
    const params = new URLSearchParams(location.search);
    query.value = params.get("q") || "";
    category.value = params.get("category") || "";
    year.value = params.get("year") || "";
    refreshDates({
      year: year.value,
      month: params.get("month") || "",
      day: params.get("day") || "",
    });
  }
  function apply(updateURL = true) {
    const words = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const params = new URLSearchParams();
    if (query.value.trim()) params.set("q", query.value.trim());
    if (category.value) params.set("category", category.value);
    if (year.value) params.set("year", year.value);
    if (month.value) params.set("month", month.value);
    if (day.value) params.set("day", day.value);
    const search = params.size ? "?" + params.toString() : "";
    let visible = 0;
    for (const paper of records) {
      const show =
        (!category.value || paper.category === category.value) &&
        dates.matches(paper.publication, {
          year: year.value,
          month: month.value,
          day: day.value,
        }) &&
        words.every((word) => paper.search.includes(word));
      const card = cards.get(paper.id);
      card.hidden = !show;
      if (show) {
        visible++;
        card
          .querySelectorAll("a")
          .forEach(
            (a) => (a.href = paper.url + (search ? "?from=" + encodeURIComponent(search) : "")),
          );
      }
    }
    count.textContent = visible + " " + (visible === 1 ? "paper" : "papers");
    empty.hidden = visible !== 0;
    reset.disabled = !params.size;
    if (updateURL) history.replaceState(null, "", base + search + location.hash);
  }
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    apply();
  });
  query.addEventListener("input", () => apply());
  category.addEventListener("change", () => apply());
  year.addEventListener("change", () => {
    refreshDates();
    apply();
  });
  month.addEventListener("change", () => {
    refreshDates();
    apply();
  });
  day.addEventListener("change", () => apply());
  form.addEventListener("reset", (event) => {
    event.preventDefault();
    query.value = "";
    category.value = "";
    year.value = "";
    refreshDates({ year: "", month: "", day: "" });
    apply();
    query.focus();
  });
  document.querySelector("#clear-empty").addEventListener("click", () => form.reset());
  window.addEventListener("popstate", () => {
    readURL();
    apply(false);
  });
  dateNavigation = window.createDateNavigation({
    records,
    dates,
    year,
    month,
    day,
    refresh: refreshDates,
    apply,
  });
  readURL();
  apply(false);
  form.dataset.ready = "true";
})();

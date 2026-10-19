(() => {
  const base = document.body.dataset.base;
  const back = document.querySelector("[data-back]");
  if (back) {
    const from = new URLSearchParams(location.search).get("from");
    if (from && from.startsWith("?") && !/[<>]/.test(from)) back.href = base + from + "#papers";
  }
  const form = document.querySelector("#filters");
  if (!form) return;
  const records = JSON.parse(document.querySelector("#paper-data").textContent);
  const cards = new Map(
    [...document.querySelectorAll("[data-paper]")].map((card) => [card.dataset.paper, card]),
  );
  const query = document.querySelector("#query");
  const category = document.querySelector("#category");
  const year = document.querySelector("#year");
  const count = document.querySelector("#result-count");
  const empty = document.querySelector("#empty-state");
  const reset = form.querySelector("[type=reset]");
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
  function readURL() {
    const params = new URLSearchParams(location.search);
    query.value = params.get("q") || "";
    category.value = params.get("category") || "";
    year.value = params.get("year") || "";
  }
  function apply(updateURL = true) {
    const words = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const params = new URLSearchParams();
    if (query.value.trim()) params.set("q", query.value.trim());
    if (category.value) params.set("category", category.value);
    if (year.value) params.set("year", year.value);
    const search = params.size ? "?" + params.toString() : "";
    let visible = 0;
    for (const paper of records) {
      const show =
        (!category.value || paper.category === category.value) &&
        (!year.value || paper.year === Number(year.value)) &&
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
  year.addEventListener("change", () => apply());
  form.addEventListener("reset", () => {
    query.value = "";
    category.value = "";
    year.value = "";
    apply();
    query.focus();
  });
  document.querySelector("#clear-empty").addEventListener("click", () => form.reset());
  window.addEventListener("popstate", () => {
    readURL();
    apply(false);
  });
  readURL();
  apply(false);
})();

(function (root) {
  root.createDateNavigation = function ({ records, dates, year, month, day, refresh, apply }) {
    const toolbar = document.querySelector(".date-filters");
    const toggle = document.querySelector("#date-toggle");
    const picker = document.querySelector("#date-picker");
    const grid = document.querySelector("#date-grid");
    const previous = document.querySelector("#previous-date");
    const next = document.querySelector("#next-date");
    const tabs = [...document.querySelectorAll("[data-date-mode]")];
    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    const selection = () => ({ year: year.value, month: month.value, day: day.value });
    const mode = () => (day.value ? "day" : month.value ? "month" : year.value ? "year" : "");
    const close = (focus = false) => {
      picker.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
      if (focus) toggle.focus();
    };
    function choose(value, dismiss = true) {
      year.value = value.year || "";
      refresh(value);
      apply();
      if (dismiss) close(true);
    }
    function periods(kind) {
      const length = { year: 4, month: 7, day: 10 }[kind];
      return [
        ...new Set(
          records
            .map((p) => p.publication.date)
            .filter((d) => d && d.length >= length)
            .map((d) => d.slice(0, length)),
        ),
      ].sort();
    }
    function fromPeriod(value) {
      const [y, m = "", d = ""] = value.split("-");
      return { year: y, month: m, day: d };
    }
    function currentPeriod() {
      return [year.value, month.value, day.value].filter(Boolean).join("-");
    }
    function pickButton(text, value, label, disabled = false) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = text;
      button.disabled = disabled;
      button.setAttribute("aria-label", label);
      button.setAttribute(
        "aria-pressed",
        String(JSON.stringify(value) === JSON.stringify(selection())),
      );
      button.addEventListener("click", () => choose(value));
      grid.append(button);
    }
    function render() {
      const kind = mode();
      for (const tab of tabs) {
        tab.setAttribute("aria-pressed", String(tab.dataset.dateMode === kind));
        tab.disabled = Boolean(tab.dataset.dateMode) && !periods(tab.dataset.dateMode).length;
      }
      let label = "All dates";
      if (year.value === "unknown") label = "Date unknown";
      else if (year.value) {
        label = year.value;
        if (month.value === "unknown") label += " · month unknown";
        else if (month.value) {
          label = monthNames[Number(month.value) - 1].slice(0, 3) + " " + year.value;
          if (day.value === "unknown") label += " · day unknown";
          else if (day.value)
            label =
              monthNames[Number(month.value) - 1].slice(0, 3) +
              " " +
              Number(day.value) +
              ", " +
              year.value;
        }
      }
      document.querySelector("#date-label").textContent = label;
      const values = kind ? periods(kind) : [];
      const index = values.indexOf(currentPeriod());
      previous.disabled = index <= 0;
      next.disabled = index < 0 || index >= values.length - 1;
      previous.setAttribute("aria-label", "Previous publication " + (kind || "period"));
      next.setAttribute("aria-label", "Next publication " + (kind || "period"));
      grid.replaceChildren();
      grid.className = "date-grid " + (kind === "day" ? "day-grid" : "period-grid");
      document.querySelector("#picker-year-field").hidden = !kind || kind === "year";
      document.querySelector("#picker-month-field").hidden = kind !== "day";
      document.querySelector("#picker-heading").textContent =
        !kind || kind === "year"
          ? "Choose a publication year"
          : kind === "month"
            ? "Choose a publication month"
            : "Choose a publication day";
      if (!kind || kind === "year") {
        for (const value of dates.options(records, "year"))
          pickButton(
            value === "unknown" ? "Unknown" : value,
            { year: value, month: "", day: "" },
            value === "unknown" ? "Publication date unknown" : "Year " + value,
          );
      } else if (kind === "month") {
        const available = dates.options(records, "month", selection());
        for (let i = 1; i <= 12; i++) {
          const value = String(i).padStart(2, "0");
          pickButton(
            monthNames[i - 1].slice(0, 3),
            { year: year.value, month: value, day: "" },
            monthNames[i - 1] + " " + year.value,
            !available.includes(value),
          );
        }
        if (available.includes("unknown"))
          pickButton(
            "Unknown month",
            { year: year.value, month: "unknown", day: "" },
            "Month unknown in " + year.value,
          );
      } else if (year.value !== "unknown" && month.value && month.value !== "unknown") {
        for (const name of ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]) {
          const label = document.createElement("span");
          label.textContent = name;
          label.className = "weekday";
          grid.append(label);
        }
        const first = new Date(
          Date.UTC(Number(year.value), Number(month.value) - 1, 1),
        ).getUTCDay();
        const last = new Date(Date.UTC(Number(year.value), Number(month.value), 0)).getUTCDate();
        for (let i = 0; i < first; i++) grid.append(document.createElement("span"));
        const available = dates.options(records, "day", selection());
        for (let i = 1; i <= last; i++) {
          const value = String(i).padStart(2, "0");
          pickButton(
            String(i),
            { year: year.value, month: month.value, day: value },
            monthNames[Number(month.value) - 1] + " " + i + ", " + year.value,
            !available.includes(value),
          );
        }
        if (available.includes("unknown")) {
          pickButton(
            "Unknown day",
            { year: year.value, month: month.value, day: "unknown" },
            "Unknown day in " + monthNames[Number(month.value) - 1] + " " + year.value,
          );
          grid.lastElementChild.className = "unknown-day";
        }
      }
    }
    for (const tab of tabs)
      tab.addEventListener("click", () => {
        const kind = tab.dataset.dateMode;
        if (!kind) return choose({ year: "", month: "", day: "" });
        const values = periods(kind);
        if (!values.length) return;
        const prefix = currentPeriod().slice(0, { year: 4, month: 7, day: 10 }[kind]);
        const matching = values.filter((value) => value.startsWith(prefix));
        choose(fromPeriod(matching.at(-1) || values.at(-1)));
      });
    function move(delta) {
      const values = periods(mode());
      const index = values.indexOf(currentPeriod());
      if (index >= 0 && values[index + delta]) choose(fromPeriod(values[index + delta]), false);
    }
    previous.addEventListener("click", () => move(-1));
    next.addEventListener("click", () => move(1));
    toggle.addEventListener("click", () => {
      picker.hidden = !picker.hidden;
      toggle.setAttribute("aria-expanded", String(!picker.hidden));
      if (!picker.hidden) {
        delete picker.dataset.placement;
        const box = picker.getBoundingClientRect();
        if (box.bottom > innerHeight - 12) {
          picker.dataset.placement =
            toolbar.getBoundingClientRect().top > box.height + 12 ? "above" : "floating";
        }
        [...picker.querySelectorAll("select:not(:disabled),#date-grid button:not(:disabled)")]
          .find((element) => element.offsetParent !== null)
          ?.focus({ preventScroll: true });
      }
    });
    document.querySelector("#close-date-picker").addEventListener("click", () => close(true));
    document.addEventListener("click", (event) => {
      if (!toolbar.contains(event.target)) close();
    });
    document.addEventListener("focusin", (event) => {
      if (!toolbar.contains(event.target)) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !picker.hidden) {
        event.preventDefault();
        close(true);
      }
    });
    grid.addEventListener("keydown", (event) => {
      const keys = {
        ArrowLeft: -1,
        ArrowRight: 1,
        ArrowUp: mode() === "day" ? -7 : -3,
        ArrowDown: mode() === "day" ? 7 : 3,
      };
      if (!(event.key in keys)) return;
      const buttons = [...grid.querySelectorAll("button")];
      const index = buttons.indexOf(document.activeElement);
      if (index < 0) return;
      event.preventDefault();
      let target = index + keys[event.key];
      while (buttons[target]?.disabled) target += keys[event.key] < 0 ? -1 : 1;
      buttons[target]?.focus();
    });
    return { render, close };
  };
})(window);

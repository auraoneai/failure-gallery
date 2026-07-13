(() => {
  const form = document.querySelector("[data-filters]");
  const cards = Array.from(document.querySelectorAll("[data-case]"));
  const count = document.querySelector("[data-visible-count]");
  const noResults = document.querySelector("[data-no-results]");

  function applyFilters() {
    const data = new FormData(form);
    const query = String(data.get("query") || "").trim().toLowerCase();
    const domain = String(data.get("domain") || "all");
    const tool = String(data.get("tool") || "all");
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = !query || card.dataset.search.includes(query);
      const matchesDomain = domain === "all" || card.dataset.domain === domain;
      const matchesTool = tool === "all" || card.dataset.tool === tool;
      const matches = matchesQuery && matchesDomain && matchesTool;
      card.hidden = !matches;
      if (matches) visible += 1;
    });

    count.textContent = String(visible);
    noResults.hidden = visible !== 0;
  }

  form.addEventListener("input", applyFilters);
  form.addEventListener("reset", () => window.setTimeout(applyFilters));

  document.querySelectorAll("[data-open-case]").forEach((button) => {
    button.addEventListener("click", () => {
      const dialog = document.getElementById(`dialog-${button.dataset.openCase}`);
      if (dialog && typeof dialog.showModal === "function") {
        dialog.showModal();
        history.replaceState(null, "", `#${button.dataset.openCase}`);
      }
    });
  });

  document.querySelectorAll(".case-dialog").forEach((dialog) => {
    dialog.querySelectorAll("[data-close-dialog]").forEach((button) => {
      button.addEventListener("click", () => dialog.close());
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) dialog.close();
    });
  });

  document.querySelectorAll("[data-copy-command]").forEach((button) => {
    button.addEventListener("click", async () => {
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(button.dataset.copyCommand);
        button.textContent = "Copied";
      } catch {
        button.textContent = "Select command";
      }
      window.setTimeout(() => {
        button.textContent = original;
      }, 1600);
    });
  });

  document.querySelectorAll("[data-copy-record-link]").forEach((link) => {
    link.addEventListener("click", () => {
      const dialog = link.closest("dialog");
      if (dialog) dialog.close();
    });
  });

  const initialId = location.hash.slice(1);
  if (initialId) {
    const trigger = document.querySelector(`[data-open-case="${CSS.escape(initialId)}"]`);
    if (trigger) trigger.click();
  }
})();

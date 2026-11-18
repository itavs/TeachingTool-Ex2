/* Apply before styles/paint; appearance only, independent of application data. */
(function () {
  "use strict";
  const key = "teachingtool.appearance";
  const root = document.documentElement;
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  const valid = value => ["light", "dark", "system"].includes(value);
  let preference = "system";
  try {
    const stored = window.localStorage.getItem(key);
    if (valid(stored)) preference = stored;
  } catch (_) { /* Storage may be blocked; in-page selection still works. */ }

  function apply() {
    root.dataset.theme = preference === "system" ? (system.matches ? "dark" : "light") : preference;
    const select = document.getElementById("theme-preference");
    if (select) select.value = preference;
  }
  apply();
  if (system.addEventListener) system.addEventListener("change", apply);
  else if (system.addListener) system.addListener(apply);

  window.addEventListener("storage", event => {
    if (event.key === key || event.key === null) {
      preference = valid(event.newValue) ? event.newValue : "system";
      apply();
    }
  });
  document.addEventListener("DOMContentLoaded", () => {
    const select = document.getElementById("theme-preference");
    if (!select) return;
    select.value = preference;
    select.addEventListener("change", () => {
      preference = valid(select.value) ? select.value : "system";
      try { window.localStorage.setItem(key, preference); } catch (_) { /* Best effort. */ }
      apply();
    });
  });
}());

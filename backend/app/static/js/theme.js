/**
 * Theme manager: dark/light mode toggle with localStorage persistence.
 */
(function () {
  const STORAGE_KEY = "apk-theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  // Apply saved theme immediately to prevent FOUT
  const saved = localStorage.getItem(STORAGE_KEY) || "dark";
  applyTheme(saved);

  window.toggleTheme = function () {
    const current = document.documentElement.getAttribute("data-theme");
    applyTheme(current === "dark" ? "light" : "dark");
  };
})();

(() => {
  const storageKey = 'mtg-trk-theme';
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem(storageKey); } catch { /* Use the system theme. */ }
  if (!['light', 'dark'].includes(preference)) preference = null;

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll('[data-theme-value]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.themeValue === theme));
    });
  }

  applyTheme(preference || (systemTheme.matches ? 'dark' : 'light'));
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(document.documentElement.dataset.theme);
    document.querySelectorAll('[data-theme-value]').forEach(button => {
      button.addEventListener('click', () => {
        preference = button.dataset.themeValue;
        applyTheme(preference);
        try { localStorage.setItem(storageKey, preference); } catch { /* Keep this session's choice. */ }
      });
    });
  });
  systemTheme.addEventListener('change', event => {
    if (!preference) applyTheme(event.matches ? 'dark' : 'light');
  });
})();

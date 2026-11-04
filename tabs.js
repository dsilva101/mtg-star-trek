const tabs = [...document.querySelectorAll('[role="tab"]')];
const panels = [...document.querySelectorAll('[role="tabpanel"]')];

function activate(id, focus = false) {
  for (const tab of tabs) {
    const selected = tab.getAttribute('aria-controls') === id;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  }
  for (const panel of panels) panel.hidden = panel.id !== id;
}

function showHashTarget() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); }
  catch { id = ''; }
  const target = document.getElementById(id);
  const panel = target?.closest('[role="tabpanel"]');
  activate(panel?.id ?? 'intro');
  if (target && panel) {
    requestAnimationFrame(() => target.scrollIntoView());
  }
}

for (const [index, tab] of tabs.entries()) {
  tab.addEventListener('click', () => {
    const id = tab.getAttribute('aria-controls');
    activate(id);
    history.pushState(null, '', `#${id}`);
  });
  tab.addEventListener('keydown', (event) => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    tabs[next].click();
    tabs[next].focus();
  });
}
window.addEventListener('hashchange', showHashTarget);
window.addEventListener('popstate', showHashTarget);
showHashTarget();

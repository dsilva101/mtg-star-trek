const cardPanel = document.getElementById('cards');
const storagePrefix = 'mtg-trk-cards-v1:';

function readOpen(key, fallback) {
  try {
    const value = localStorage.getItem(storagePrefix + key);
    return value === null ? fallback : value === '1';
  } catch {
    return fallback;
  }
}

function saveOpen(key, open) {
  try { localStorage.setItem(storagePrefix + key, open ? '1' : '0'); }
  catch { /* The controls still work when browser storage is unavailable. */ }
}

function makeButton(label, className) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = className;
  button.textContent = label;
  return button;
}

function setSectionOpen(content, button, open, key) {
  content.hidden = !open;
  button.textContent = open ? 'Collapse section' : 'Expand section';
  button.setAttribute('aria-expanded', String(open));
  saveOpen(key, open);
}

function setCardOpen(card, open) {
  card.open = open;
  saveOpen(`card:${card.dataset.cardId}`, open);
}

function cardRating(nodes) {
  const text = nodes.map(node => node.textContent || '').join(' ');
  const match = text.match(/Rating:\s*(\d+(?:\.\d+)?)\s*\/\s*10/i);
  return match ? Number(match[1]) : -1;
}

if (cardPanel) {
  const sectionHeadings = [...cardPanel.children].filter(node => node.tagName === 'H2');
  const sections = sectionHeadings.map((heading, index) => {
    const nodes = [];
    for (let node = heading.nextSibling; node && node !== sectionHeadings[index + 1]; node = node.nextSibling) {
      nodes.push(node);
    }
    return { heading, nodes };
  });
  const sectionControls = [];

  for (const { heading, nodes } of sections) {
    const sectionId = heading.querySelector('[id]')?.id || heading.textContent.trim();
    const toolbar = document.createElement('div');
    toolbar.className = 'card-section-tools';
    const sectionButton = makeButton('Collapse section', 'section-toggle');
    const collapseButton = makeButton('Collapse all cards', 'cards-collapse-all');
    const expandButton = makeButton('Expand all cards', 'cards-expand-all');
    toolbar.append(sectionButton, collapseButton, expandButton);

    const content = document.createElement('div');
    content.className = 'card-section-content';
    content.id = `card-section-${sectionControls.length}`;
    sectionButton.setAttribute('aria-controls', content.id);
    content.dataset.sectionId = sectionId;
    const sectionHeader = document.createElement('div');
    sectionHeader.className = 'card-section-header';
    heading.before(sectionHeader);
    sectionHeader.append(heading, toolbar);
    sectionHeader.after(content);

    const leadingNodes = [];
    const blocks = [];
    let current = null;
    for (const node of nodes) {
      if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'H3') {
        if (current) blocks.push(current);
        current = { heading: node, nodes: [node] };
      } else if (current) {
        current.nodes.push(node);
      } else {
        leadingNodes.push(node);
      }
    }
    if (current) blocks.push(current);

    const cards = blocks.map((block, order) => {
      const rating = cardRating(block.nodes);
      const cardId = block.heading.querySelector('[id]')?.id || `${sectionId}-${order}`;
      const detail = document.createElement('details');
      detail.className = 'card-review';
      detail.dataset.cardId = cardId;
      detail.open = readOpen(`card:${cardId}`, true);

      const summary = document.createElement('summary');
      summary.append(block.heading);
      if (rating >= 0) {
        const badge = document.createElement('span');
        badge.className = 'card-rating';
        badge.textContent = `(${rating})`;
        block.heading.prepend(badge, document.createTextNode(' '));
      }
      detail.append(summary);

      const body = document.createElement('div');
      body.className = 'card-review-content';
      const analysis = document.createElement('div');
      analysis.className = 'card-analysis';
      for (const node of block.nodes) {
        if (node === block.heading) continue;
        if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('card_gallery_wrapper')) {
          body.append(node);
        } else {
          analysis.append(node);
        }
      }
      body.append(analysis);
      detail.append(body);
      detail.addEventListener('toggle', () => saveOpen(`card:${cardId}`, detail.open));
      return { detail, rating, order };
    });

    for (const node of leadingNodes) content.append(node);
    cards.sort((a, b) => b.rating - a.rating || a.order - b.order);
    for (const card of cards) content.append(card.detail);

    const initialSectionOpen = readOpen(`section:${sectionId}`, true);
    setSectionOpen(content, sectionButton, initialSectionOpen, `section:${sectionId}`);
    sectionControls.push({ content, button: sectionButton, key: `section:${sectionId}` });
    sectionButton.addEventListener('click', () => {
      setSectionOpen(content, sectionButton, content.hidden, `section:${sectionId}`);
    });
    collapseButton.addEventListener('click', () => cards.forEach(card => setCardOpen(card.detail, false)));
    expandButton.addEventListener('click', () => cards.forEach(card => setCardOpen(card.detail, true)));
  }

  const collapseSectionsButton = cardPanel.querySelector('.sections-collapse-all');
  if (collapseSectionsButton) {
  collapseSectionsButton.addEventListener('click', () => {
    for (const section of sectionControls) {
      setSectionOpen(section.content, section.button, false, section.key);
    }
  });
  }

  function revealTarget(target) {
    if (!target || !cardPanel.contains(target)) return;
    const card = target.closest('details.card-review');
    if (card) setCardOpen(card, true);
    const content = target.closest('.card-section-content') ||
      target.closest('.card-section-header')?.nextElementSibling;
    const sectionButton = content?.previousElementSibling?.querySelector('.section-toggle');
    if (content && sectionButton && content.hidden) {
      setSectionOpen(content, sectionButton, true, `section:${content.dataset.sectionId}`);
    }
  }

  function revealHashTarget() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); }
    catch { id = ''; }
    revealTarget(document.getElementById(id));
  }

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    let id;
    try { id = decodeURIComponent(link.hash.slice(1)); }
    catch { return; }
    const target = document.getElementById(id);
    if (target && cardPanel.contains(target)) revealTarget(target);
  });
  window.addEventListener('hashchange', revealHashTarget);
  window.addEventListener('popstate', revealHashTarget);
  revealHashTarget();
}

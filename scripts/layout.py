"""Group the existing review nodes into tabs without changing their contents."""
from hashlib import sha256
from pathlib import Path
from bs4 import BeautifulSoup


def apply_tabs(page):
    soup = BeautifulSoup(page, 'html.parser')
    article = soup.article
    for toc in article.select('.contents, .lwptoc'):
        toc.decompose()
    if article.select_one('.tab-panel'):
        return str(soup)
    panels = {}
    tablist = soup.new_tag('div', attrs={'class': 'tabs', 'role': 'tablist', 'aria-label': 'Review sections'})
    for key, label in [('intro', 'Intro'), ('mechanics', 'Mechanics'), ('cards', 'Cards')]:
        button = soup.new_tag('button', attrs={
            'type': 'button', 'id': f'tab-{key}', 'role': 'tab',
            'aria-controls': key, 'aria-selected': 'true' if key == 'intro' else 'false',
            'tabindex': '0' if key == 'intro' else '-1',
        })
        button.string = label
        tablist.append(button)
        panels[key] = soup.new_tag('section', attrs={
            'id': key, 'class': 'tab-panel', 'role': 'tabpanel',
            'aria-labelledby': f'tab-{key}', 'tabindex': '0',
        })
    current = 'intro'
    for node in list(article.contents):
        if getattr(node, 'name', None) == 'h2':
            heading = node.get_text(' ', strip=True)
            if heading == 'Set Mechanics':
                current = 'mechanics'
            elif heading == 'White':
                current = 'cards'
            elif heading == 'Wrap Up':
                current = 'intro'
        panels[current].append(node.extract())
    article.append(tablist)
    for panel in panels.values():
        article.append(panel)
    global_tools = soup.new_tag('div', attrs={'class': 'card-section-tools card-global-tools'})
    global_button = soup.new_tag('button', attrs={'type': 'button', 'class': 'sections-collapse-all'})
    global_button.string = 'Collapse all sections'
    global_tools.append(global_button)
    panels['cards'].insert(0, global_tools)
    csp = soup.find('meta', attrs={'http-equiv': 'Content-Security-Policy'})
    csp['content'] = csp['content'].replace("style-src 'self';", "style-src 'self'; script-src 'self';")
    script = soup.new_tag('script', attrs={'src': 'tabs.js', 'defer': ''})
    soup.head.append(script)
    cards_file = Path(__file__).resolve().parent.parent / 'cards.js'
    cards_version = sha256(cards_file.read_bytes()).hexdigest()[:12]
    cards_script = soup.new_tag('script', attrs={'src': f'cards.js?v={cards_version}', 'defer': ''})
    soup.head.append(cards_script)
    return str(soup)

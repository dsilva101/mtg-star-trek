"""Group the existing review nodes into tabs without changing their contents."""
from bs4 import BeautifulSoup


def apply_tabs(page):
    soup = BeautifulSoup(page, 'html.parser')
    article = soup.article
    if article.select_one('.tab-panel'):
        return str(soup)
    contents = article.select_one('details.contents').extract()
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
    # Move each existing contents entry to the panel containing its destination.
    entries = list(contents.select_one('.lwptoc_items > .lwptoc_itemWrap').find_all('div', recursive=False))
    for key, panel in panels.items():
        local_contents = soup.new_tag('details', attrs={'class': 'contents'})
        summary = soup.new_tag('summary')
        summary.string = contents.summary.get_text()
        local_contents.append(summary)
        wrapper = soup.new_tag('div', attrs={'class': 'lwptoc_itemWrap'})
        for entry in entries:
            target = entry.find('a')['href'][1:]
            if panel.find(id=target):
                wrapper.append(entry.extract())
        local_contents.append(wrapper)
        if key == 'intro':
            panel.find('h2').insert_before(local_contents)
        else:
            panel.insert(0, local_contents)
    article.append(tablist)
    for panel in panels.values():
        article.append(panel)
    csp = soup.find('meta', attrs={'http-equiv': 'Content-Security-Policy'})
    csp['content'] = csp['content'].replace("style-src 'self';", "style-src 'self'; script-src 'self';")
    script = soup.new_tag('script', attrs={'src': 'tabs.js', 'defer': ''})
    soup.head.append(script)
    cards_script = soup.new_tag('script', attrs={'src': 'cards.js', 'defer': ''})
    soup.head.append(cards_script)
    return str(soup)

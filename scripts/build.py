"""Extract the supplied saved HTML into a self-contained static page."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import html
import json
import time
from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parent.parent
source = next((p for p in [ROOT / 'source.html', ROOT / 'source'] if p.exists()), None)
if source is None:
    raise SystemExit('Place source.html (or source) in the project root first.')
soup = BeautifulSoup(source.read_text(), 'html.parser')
content = soup.select_one('section.post_content')
if content is None:
    raise SystemExit('Review content was not found.')
title = soup.h1.get_text(' ', strip=True)
for node in content.select('script, style, noscript, iframe, form, object, embed, .sxc-follow-buttons, .post_info_bottom'):
    node.decompose()
for node in content.find_all(string=lambda t: isinstance(t, Comment)):
    node.extract()
for p in content.select('p'):
    if p.get_text(' ', strip=True).startswith('If you liked this article, please consider subscribing'):
        p.decompose()
# Keep the existing same-page contents as a native, script-free disclosure.
toc = content.select_one('.lwptoc')
if toc:
    items = toc.select_one('.lwptoc_items').extract()
    details = soup.new_tag('details', attrs={'class': 'contents'})
    summary = soup.new_tag('summary')
    summary.string = 'Table of contents'
    details.append(summary)
    details.append(items)
    toc.replace_with(details)
for a in list(content.select('a')):
    href = a.get('href', '')
    if not href.startswith('#') or href == '#':
        a.unwrap()
for i in content.select('i.ms'):
    symbol = next((c[3:].upper() for c in i.get('class', []) if c in ['ms-w', 'ms-u', 'ms-b', 'ms-r', 'ms-g']), '?')
    i.name = 'span'
    i['class'] = ['mana', f'mana-{symbol.lower()}']
    i['aria-label'] = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}.get(symbol, symbol)
    i.string = symbol
images = {}
for img in content.select('img'):
    url = img.get('data-lazy-src') or img.get('src', '')
    if not url.startswith('https://draftsim.com/wp-content/uploads/'):
        raise ValueError(f'Unexpected image source: {url}')
    ext = Path(urlparse(url).path).suffix.lower()
    filename = 'assets/' + sha256(url.encode()).hexdigest()[:20] + ext
    images[url] = filename
    img['src'] = filename
    img['loading'] = 'lazy'
    img['decoding'] = 'async'
for node in content.find_all():
    allowed = {'class', 'id', 'alt', 'width', 'height', 'src', 'href', 'loading', 'decoding', 'aria-label'}
    for attr in list(node.attrs):
        if attr not in allowed:
            del node[attr]
# Make the first artwork load immediately.
content.select_one('img')['loading'] = 'eager'
(ROOT / 'assets').mkdir(exist_ok=True)
def download(item):
    url, filename = item
    dest = ROOT / filename
    if dest.exists() and dest.stat().st_size:
        return
    for attempt in range(3):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=45) as response:
                if not response.headers.get('Content-Type', '').startswith('image/'):
                    raise ValueError(f'Not an image: {url}')
                data = response.read()
            dest.write_bytes(data)
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(download, images.items()))
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'">
<title>{html.escape(title)}</title>
<link rel="icon" href="data:,">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<main id="main">
<header><h1>{html.escape(title)}</h1><p class="byline">Review by Andrew Quinn · Draftsim</p></header>
<article>{content.decode_contents()}</article>
</main>
</body>
</html>
'''
(ROOT / 'index.html').write_text(page)
(ROOT / 'assets' / 'manifest.json').write_text(json.dumps(images, indent=2) + '\n')
print(f'Built index.html with {len(content.select("h2"))} sections, {len(content.select("h3"))} subsections and {len(images)} local images.')

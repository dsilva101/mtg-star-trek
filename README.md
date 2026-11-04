# MTG Star Trek Limited Review

A static reading page extracted from the locally supplied saved HTML. Review by Andrew Quinn, Draftsim; artwork credits remain in the article.

The published page uses local images and CSS. A local script controls the Intro, Mechanics, and Cards tabs. In Cards, the nine sections and individual card reviews can be collapsed; open states are saved in the browser. Cards are sorted by rating within each section. There are no cookies, ads, forms, trackers, external fonts, or outbound links. Each table of contents links within its tab. Mechanics also includes Draft Archetypes. Existing section and card links open the appropriate tab.

Edit `index.html`, `styles.css`, `tabs.js`, and `cards.js` to iterate on the published page. GitHub Pages deploys the root of `main`.

To rebuild from the original local input (this replaces `index.html`):

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py
```

The input file (`source.html` or `source`) and saved third-party site assets are excluded from Git. `assets/manifest.json` records image origins for maintenance; the page serves local copies.

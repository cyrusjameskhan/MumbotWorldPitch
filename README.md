# Mumbot World Pitch Deck

Local HTML pitch deck for Mumbot World.

## Audience editions

Open `deck-versions.html` to choose an edition:

| Edition | File | Main slides | Appendix |
| --- | --- | --- | --- |
| Investors | `investors.html` | 13 | 4 |
| Sponsors | `sponsors.html` | 11 | 3 |
| Galleries | `galleries.html` | 12 | 3 |

The editions reuse the artwork, styles and shared slides in `Mumbot World Pitch Deck.html`. Audience-specific copy and sequencing live in `scripts/build_deck_versions.py`; additional layouts use `deck-versions.css`. Run `python scripts/build_deck_versions.py` after editing these sources. The generated HTML remains static and editable; rebuilding overwrites direct changes to those generated files.

The general and investor decks use a US$50,000 minimum funding ask for Phase 01, with investment terms open. Sponsor packages and exhibition formats are proposed scopes, with fees agreed for each brief. Evidence sources and proposal context are included in each deck's speaker notes. The current music roster excludes Notep.

## Netlify

Deploy this folder as a static site. Netlify uses `netlify.toml` with `publish = "."`.

- `/` and `/deck` serve the main deck.
- `/versions` opens the edition selector.
- `/investors`, `/sponsors` and `/galleries` serve the audience editions.
- The existing password gate covers all editions and their assets.

No build step is required.

## Local preview

Preview:

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8765/Mumbot%20World%20Pitch%20Deck.html
```

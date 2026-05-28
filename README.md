# Mumbot World Pitch Deck

Local HTML pitch deck for Mumbot World.

## Netlify

Deploy this folder as a static site. Netlify uses `netlify.toml` with `publish = "."`.

- `/` and `/deck` serve the main deck.
- `/print` serves the print version.

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

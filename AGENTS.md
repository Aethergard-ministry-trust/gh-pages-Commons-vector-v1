# Working on this repository in the Base44 sandbox

## What this project is

A **static site** (`index.html` + JSON/MD/PDF files + `assets/`), intended for GitHub Pages
(see `PAGES.md`). There is no build step, no package manifest, and no backend. All
"archive" features run in the browser (Ed25519 via Web Crypto, records in IndexedDB).

## Running it

```bash
docker compose -f docker-compose.base44.yml up -d
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/
```

`web` is `nginx:alpine` serving the checkout bind-mounted at `/usr/share/nginx/html`, so
file edits are served immediately (no rebuild; refresh the browser). Config lives in
`.base44/nginx.conf`:

- nginx workers run as **root** because the sandbox checkout is a `0700` root-owned
  directory; the image's default `nginx` user cannot traverse it (symptoms: `403` on `/`
  and `404` on every file with `Permission denied` in the container log).
- Dotfile paths (`/.git`, `/.base44`) are denied.
- `.md` files are served as `text/markdown` — the image's `mime.types` has no markdown
  entry, so links would otherwise download instead of display.
- Responses carry `Cache-Control: no-store` so a reload always shows current files.

## Quirks worth knowing

- The only network integration is the visitor's **own local Kubo/IPFS node** at
  `http://127.0.0.1:5001/api/v0`, used only after an explicit click. It is expected to be
  unreachable from the sandbox preview and from the public preview URL — that is not a
  bug, and no credentials/API keys are configured for it (Pinata upload is not implemented).
- No environment variables or secrets are required to run the site.

## Verification

- `docker compose -f docker-compose.base44.yml ps` → `web` healthy.
- `http://localhost:3000/` returns `index.html`; `cvp-mvp.json`, `assets/*.png` and
  `documents/*.pdf` all return `200`.
- Browser features (register/verify a local instrument) need a secure context: `localhost`
  and the HTTPS preview URL both qualify.

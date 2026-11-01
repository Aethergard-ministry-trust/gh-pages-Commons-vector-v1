# Working on this repository in the Base44 sandbox

## What this project is

Two things live here:

1. **The archive site** — `index.html` + JSON/MD/PDF files + `assets/`, a static site for
   GitHub Pages (see `PAGES.md`). All its features run in the browser (Ed25519 via Web Crypto,
   records in IndexedDB).
2. **`neuralcommons-app-generator/`** — the App Generator: a Base64 prompt library plus a
   FastAPI console that builds a complete CVP application (FastAPI backend, Next.js frontend,
   D3 dashboard, provenance viewer, IPFS/ed25519 module) into `neuralcommons-app-generator/output/`.
   See `neuralcommons-app-generator/README.md`.

## Running it

```bash
docker compose -f docker-compose.base44.yml up -d
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3000/   # generator console
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3001/   # archive site
```

| Service | Port | Notes |
| --- | --- | --- |
| `generator` | 3000 | `python:3.12-slim`, checkout mounted at `/app`, `uvicorn --reload` |
| `archive` | 3001 | `nginx:alpine` serving the checkout |
| `built-app` | 3002 | the generated Next.js frontend (`output/frontend`), `next dev`, project "Built App V1" |
| `built-api` | 8002 | the generated FastAPI app (`output/backend`), `uvicorn --reload`, project "Built App V1" |

## Running the built app

`built-app` / `built-api` mount `neuralcommons-app-generator/output/` and start only after
`generator` is healthy, so the generated tree always exists first. The frontend reaches the API on
its public origin (`NEXT_PUBLIC_CVP_API_URL=https://8002-$BASE44_PUBLIC_HOST_SUFFIX`, both for the
browser and for server-rendered pages), and the API allows exactly the frontend origin through
`CVP_FRONTEND_ORIGIN`.

**Restart both after every generation run.** A generation wipes and recreates `output/`, which
leaves the running containers holding deleted directories (Next's watcher loses `app/`, the API's
cwd disappears and `mkdir data` fails). Pressing *Generate application* therefore requires:

```bash
docker compose -f docker-compose.base44.yml restart built-api built-app
```

The generated ledger (`output/backend/data/`) and its Ed25519 key live inside `output/`, so every
generation resets the instrument chain — expected for a build artifact, not a bug.

`generator` runs on boot, in this order: `pip install -r requirements.txt` →
`python scripts/generate_app.py` → `uvicorn app.main:app`. Dependencies are installed on every
startup (no image build), so `requirements.txt` edits apply after a restart. Uvicorn hot-reloads
`app/`, `scripts/`, `templates/` and `prompts/`; nothing else needs a rebuild.

Edits to prompts or templates only reach `output/` after a generation run — press
**Generate application** in the console or `POST /api/generate`.

## Quirks worth knowing

- **Ollama is not running in the sandbox.** `OLLAMA_URL` points at `127.0.0.1:11434`, the probe
  fails, and every layer is rendered from its template with `mode: "template"` and a
  `prompt_error` naming the reason. That is the designed fallback, not a bug.
- `output/` is git-ignored and wiped at the start of every generation run; generated `__pycache__`
  folders appear only if you run `compileall` by hand.
- The generator writes into the bind-mounted checkout, so generated files are served
  immediately at `/generated/...` (FastAPI `StaticFiles` mount).
- The generated visual tools are standalone pages that load `../provenance.json` and a vendored
  D3 (`templates/visual_tools/vendor/d3.v7.min.js`) — no CDN at runtime.
- The archive nginx config runs workers as **root** because the sandbox checkout is a `0700`
  root-owned directory; dotfile paths are denied and `.md` is served as `text/markdown`
  (see `.base44/nginx.conf`).
- The only visitor-side network integration in the archive is their own Kubo node at
  `http://127.0.0.1:5001/api/v0`, after an explicit click; unreachable from the preview is expected.
- No secrets are required. IPFS and Ollama endpoints are ordinary configurable URLs, not credentials.

## Verification

```bash
docker compose -f docker-compose.base44.yml ps                  # all services healthy
curl -s http://localhost:3000/health                           # {"status":"ok",...}
curl -s http://localhost:8002/health                           # built app API
curl -s -X POST http://localhost:8002/instruments -H 'Content-Type: application/json' \
  -d '{"payload":{"check":1}}'                                 # 201; then /verify/<cid> → verified true
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:3002/ # built app overview (SSR)
docker compose -f docker-compose.base44.yml logs --tail=20 built-app
curl -s http://localhost:3000/api/status | head -c 300         # ollama probe + output files
docker compose -f docker-compose.base44.yml exec -T generator \
  python scripts/generate_app.py --no-ollama                   # CLI build path
docker compose -f docker-compose.base44.yml exec -T generator \
  python -m compileall -q output/backend                       # generated backend is valid Python
docker compose -f neuralcommons-app-generator/output/docker-compose.yml config --quiet
```

- Console at `/` → 5 prompt layers, decoded prompts, build summary, file list.
- The console's **Generate application** button must return `mode: template` with 5 instruments
  in this environment; the dashboard and provenance viewer should each render 5 nodes.
- `provenance.json` chain integrity: every instrument's `verified` is recomputed from its
  canonical bytes when written, so a broken `previous` link shows as unverified in the viewer.
- The generated Next.js frontend **is** installed and run by `built-app` (`npm install` on startup,
  ~10 s, into the git-ignored `output/frontend/node_modules`).
- The layout injects its CSS with `<style dangerouslySetInnerHTML={{ __html: css }} />`. A plain
  `<style>{css}</style>` makes React fail hydration with `Text content does not match
  server-rendered HTML` and the dev overlay shows a red "1 error" badge on every page.
- The built app has no create/edit UI; instruments are written through `POST /instruments` on the
  generated API. The instruments and provenance pages only read.

# NeuralCommons App Generator

A self-building application generator for the **NeuralCommons CVP + Ollama** system.
A library of Base64-encoded prompts drives the generation of the application layers
(backend, frontend, visual tools, IPFS integration); one command writes a complete,
runnable application to `output/` together with a verifiable provenance record.

```
neuralcommons-app-generator/
├── app/                          FastAPI console + generation pipeline
│   ├── main.py                   prompt library, /api/generate, /generated/*
│   ├── generator.py              decode → (Ollama) → render → provenance
│   └── templates/console.html
├── prompts/                      Base64 prompt library (the source of truth)
│   ├── backend_prompt.base64
│   ├── frontend_prompt.base64
│   ├── dashboard_prompt.base64
│   ├── provenance_viewer_prompt.base64
│   └── ipfs_integration_prompt.base64
├── templates/                    fallback templates per layer
│   ├── backend/                  fastapi_template.py, ipfs_client_template.py, requirements.txt
│   ├── frontend/                 package.json, next.config.mjs, nextjs_template/
│   └── visual_tools/             dashboard.html, d3_provenance_chain.html, mermaid_diagram.js, vendor/d3
├── scripts/
│   ├── generate_app.py           build the application (one command)
│   ├── decode_prompts.py         decode the Base64 prompts
│   └── build_docker.py           validate / run the generated stack
├── output/                       generated application (git-ignored, rebuilt on demand)
├── config.json                   model, namespace, dictionary, layer → prompt mapping
└── requirements.txt
```

## Quick start

```bash
# 1. build the application (uses a local Ollama model when one answers)
python scripts/generate_app.py

# 2. inspect what the prompts say
python scripts/decode_prompts.py --layer backend

# 3. validate the generated Docker stack
python scripts/build_docker.py
python scripts/build_docker.py --up
```

The console at <http://localhost:3000> shows the prompt library, runs the same pipeline
over HTTP (`POST /api/generate`) and serves the built application under `/generated/`.

## Prompt library

| Layer | Prompt file | Generated artifacts |
| --- | --- | --- |
| backend | `prompts/backend_prompt.base64` | `backend/main.py`, `backend/requirements.txt` |
| frontend | `prompts/frontend_prompt.base64` | `frontend/**` (Next.js 14 App Router) |
| dashboard | `prompts/dashboard_prompt.base64` | `visual_tools/dashboard.html` |
| provenance_viewer | `prompts/provenance_viewer_prompt.base64` | `visual_tools/d3_provenance_chain.html`, `mermaid_diagram.js` |
| ipfs_integration | `prompts/ipfs_integration_prompt.base64` | `backend/ipfs_client.py` |

Prompt files are standard Base64 (line-wrapped at 76 columns) and decode to UTF-8 text;
`decode_prompts.py --json` emits them with their sha256 so a build can be reproduced.
Edit a prompt, rerun the generator, and the layer's artifacts and provenance record change
with it.

## Ollama: online vs. offline

- **Model reachable** (`OLLAMA_URL`, default `http://127.0.0.1:11434`): each prompt is sent to
  `POST /api/generate` (model `config.model`, non-streaming). The answer is written to
  `output/<layer>/ollama_response.md` and the instrument is marked `mode: ollama`.
- **Model unreachable**: the layer is rendered from its template, marked `mode: template`,
  and the failing call is recorded in the instrument's `prompt_error`. Nothing is claimed
  that did not happen.

## Provenance record

`output/provenance.json` holds one instrument per generated layer:

- `cid` — base32 sha256 of the canonical JSON (sorted keys, compact separators) of the
  instrument body, identical to what the generated backend computes.
- `previous` — CID of the preceding layer's instrument (`000` for the first one).
- `verified` — recomputed from the stored record when the file is written; the dashboard and
  provenance viewer recompute chain integrity from the data they are shown.

The two visual tools are standalone HTML pages reading `../provenance.json`; D3 is vendored
(`templates/visual_tools/vendor/d3.v7.min.js`) so they work without a CDN.

## Running inside the Base44 sandbox

`docker-compose.base44.yml` at the repository root runs two services:

| Service | Host port | What it is |
| --- | --- | --- |
| `generator` | 3000 | this generator's console (`uvicorn --reload`, source bind-mounted) |
| `archive` | 3001 | the existing static Commons Vector Protocol site |

The `generator` service installs `requirements.txt`, runs `scripts/generate_app.py` once, then
serves the console. `output/` is written inside the mounted checkout, so a rebuild is visible
immediately. Point `OLLAMA_URL` at a reachable model to generate from the model instead of the
templates.

"""Generation pipeline for the NeuralCommons App Generator.

Decodes the Base64 prompt library, asks the configured provider (Ollama) for each layer,
and always leaves a complete, runnable application in ``output/``. When the model is not
reachable the layer is rendered from its template and marked as template-sourced — the
build record never claims model output that did not happen.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import shutil
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"

# layer id -> [(template, destination relative to output/)]
LAYER_ARTIFACTS: dict[str, list[tuple[str, str]]] = {
    "backend": [
        ("templates/backend/fastapi_template.py", "backend/main.py"),
        ("templates/backend/requirements.txt", "backend/requirements.txt"),
    ],
    "frontend": [
        ("templates/frontend/package.json", "frontend/package.json"),
        ("templates/frontend/next.config.mjs", "frontend/next.config.mjs"),
        ("templates/frontend/nextjs_template/app/layout.jsx", "frontend/app/layout.jsx"),
        ("templates/frontend/nextjs_template/app/page.jsx", "frontend/app/page.jsx"),
        ("templates/frontend/nextjs_template/app/instruments/page.jsx", "frontend/app/instruments/page.jsx"),
        ("templates/frontend/nextjs_template/app/provenance/page.jsx", "frontend/app/provenance/page.jsx"),
        ("templates/frontend/nextjs_template/lib/api.js", "frontend/lib/api.js"),
    ],
    "dashboard": [
        ("templates/visual_tools/dashboard.html", "visual_tools/dashboard.html"),
    ],
    "provenance_viewer": [
        ("templates/visual_tools/d3_provenance_chain.html", "visual_tools/d3_provenance_chain.html"),
        ("templates/visual_tools/mermaid_diagram.js", "visual_tools/mermaid_diagram.js"),
    ],
    "ipfs_integration": [
        ("templates/backend/ipfs_client_template.py", "backend/ipfs_client.py"),
    ],
}

SHARED_ARTIFACTS: list[tuple[str, str]] = [
    ("templates/docker-compose.yml", "docker-compose.yml"),
    ("templates/README.md", "README.md"),
]

VENDOR_COPIES = [("templates/visual_tools/vendor/d3.v7.min.js", "visual_tools/vendor/d3.v7.min.js")]


# --- small helpers ----------------------------------------------------------


def load_config(path: Path | None = None) -> dict:
    return json.loads((path or CONFIG_PATH).read_text("utf-8"))


def decode_prompt(path: Path) -> str:
    """Decode a Base64 prompt file (line-wrapped or not) into UTF-8 text."""
    raw = path.read_bytes()
    try:
        return base64.b64decode(raw, validate=False).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise ValueError(f"{path.name} is not valid Base64 UTF-8: {exc}") from exc


def prompt_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def content_cid(body: dict) -> str:
    """Same content address as the generated backend: base32 sha256 of canonical JSON."""
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "b" + base64.b32encode(hashlib.sha256(canonical).digest()).decode("ascii").lower().rstrip("=")


def ollama_url(config: dict) -> str:
    return os.environ.get("OLLAMA_URL") or config.get("ollama_url") or "http://127.0.0.1:11434"


def ollama_status(config: dict, timeout: float = 2.0) -> dict:
    """Probe the local model server. Absence is a normal state, not an error."""
    url = ollama_url(config)
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=timeout) as response:  # noqa: S310 - configured URL
            payload = json.loads(response.read().decode("utf-8"))
        models = [item.get("name") for item in payload.get("models", []) if item.get("name")]
        return {"available": True, "url": url, "models": models}
    except Exception as exc:  # noqa: BLE001 - unreachable model server is expected when local
        return {"available": False, "url": url, "models": [], "error": type(exc).__name__}


def query_ollama(config: dict, prompt: str) -> tuple[str | None, str | None]:
    """One non-streaming generation call. Returns (text, error)."""
    body = json.dumps(
        {"model": config.get("model", "neuralcommons"), "prompt": prompt, "stream": False}
    ).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310 - configured URL
        f"{ollama_url(config)}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=float(config.get("ollama_timeout_seconds", 120))) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
        return payload.get("response", ""), None
    except Exception as exc:  # noqa: BLE001 - the layer falls back to its template
        return None, f"{type(exc).__name__}: {exc}"


def render(text: str, context: dict) -> str:
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def output_tree(output_dir: Path) -> list[str]:
    if not output_dir.exists():
        return []
    return sorted(str(path.relative_to(output_dir)) for path in output_dir.rglob("*") if path.is_file())


# --- pipeline ---------------------------------------------------------------


def generate(use_ollama: bool = True, config: dict | None = None) -> dict:
    """Build the whole application from the prompt library and return a build summary."""
    cfg = config or load_config()
    started = time.time()
    generated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    output_dir = Path(cfg.get("output_dir", "output"))
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    status = ollama_status(cfg) if use_ollama else {"available": False, "url": ollama_url(cfg), "models": [], "error": "disabled"}
    base_context = {
        "PROJECT_SLUG": "neuralcommons-generated-app",
        "PROJECT_TITLE": "NeuralCommons · Commons Vector Protocol",
        "NAMESPACE": cfg.get("namespace", "commons-vector-v1"),
        "MODEL": cfg.get("model", "neuralcommons"),
        "OLLAMA_URL": ollama_url(cfg),
        "API_URL": "http://127.0.0.1:8000",
        "FRONTEND_ORIGIN": "http://localhost:3000",
        "DICTIONARY_NAME": cfg.get("dictionary", {}).get("name", ""),
        "DICTIONARY_CID": cfg.get("dictionary", {}).get("cid", ""),
        "GENERATED_AT": generated_at,
    }

    files: list[str] = []
    instruments: list[dict] = []
    previous = "000"

    for index, layer in enumerate(cfg.get("layers", []), start=1):
        layer_id = layer["id"]
        prompt_path = ROOT / layer["prompt"]
        prompt = decode_prompt(prompt_path)
        digest = prompt_sha256(prompt)

        if status["available"]:
            answer, error = query_ollama(cfg, prompt)
        else:
            # "disabled" when Ollama was skipped on purpose, otherwise the probe's reason.
            answer, error = None, status.get("error") or "unavailable"
        mode = "ollama" if answer else "template"

        context = dict(base_context, PROMPT_SHA256=digest)
        written: list[str] = []
        for template, destination in LAYER_ARTIFACTS.get(layer_id, []):
            target = output_dir / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render((ROOT / template).read_text("utf-8"), context), "utf-8")
            written.append(destination)
        if answer:
            response_file = output_dir / layer_id / "ollama_response.md"
            response_file.parent.mkdir(parents=True, exist_ok=True)
            response_file.write_text(answer, "utf-8")
            written.append(f"{layer_id}/ollama_response.md")
        files.extend(written)

        body = {
            "instrument": f"{index:03d}",
            "trust": base_context["NAMESPACE"],
            "dictionary": base_context["DICTIONARY_NAME"],
            "layer": layer_id,
            "label": layer.get("label", layer_id),
            "mode": mode,
            "prompt_file": layer["prompt"],
            "prompt_sha256": digest,
            "prompt_chars": len(prompt),
            "prompt_error": error,
            "artifacts": written,
            "previous": previous,
            "created_at": generated_at,
        }
        cid = content_cid(body)
        record = dict(body, cid=cid)
        record["verified"] = content_cid({key: value for key, value in record.items() if key not in {"cid", "verified"}}) == cid
        instruments.append(record)
        previous = cid

    shared_context = dict(base_context, PROMPT_SHA256="")
    for template, destination in SHARED_ARTIFACTS:
        target = output_dir / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render((ROOT / template).read_text("utf-8"), shared_context), "utf-8")
        files.append(destination)
    for template, destination in VENDOR_COPIES:
        target = output_dir / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / template, target)
        files.append(destination)

    provenance = {
        "namespace": base_context["NAMESPACE"],
        "model": base_context["MODEL"],
        "provider": "ollama" if status["available"] else "template",
        "mode": "ollama" if status["available"] and all(item["mode"] == "ollama" for item in instruments) else "template",
        "ollama": {key: status[key] for key in ("available", "url", "models")},
        "dictionary": cfg.get("dictionary", {}),
        "generated_at": generated_at,
        "instruments": instruments,
    }
    (output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", "utf-8")
    files.append("provenance.json")

    return {
        "ok": True,
        "mode": provenance["mode"],
        "namespace": provenance["namespace"],
        "model": provenance["model"],
        "ollama": provenance["ollama"],
        "generated_at": generated_at,
        "duration_ms": int((time.time() - started) * 1000),
        "output_dir": "output",
        "files": sorted(files),
        "instruments": instruments,
    }

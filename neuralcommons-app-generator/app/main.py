"""NeuralCommons App Generator — console (FastAPI).

Serves the prompt library, runs the generation pipeline over HTTP and exposes the built
application under /generated/ so the visual tools can be inspected directly.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import generator

ROOT = generator.ROOT
OUTPUT = ROOT / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="NeuralCommons App Generator", version="0.1.0")
templates = Jinja2Templates(directory=str(ROOT / "app" / "templates"))
app.mount("/generated", StaticFiles(directory=str(OUTPUT)), name="generated")


def prompt_library() -> list[dict]:
    """Every layer's decoded prompt with its digest and artifact list."""
    library = []
    for layer in generator.load_config().get("layers", []):
        path = ROOT / layer["prompt"]
        text = generator.decode_prompt(path)
        library.append(
            {
                "id": layer["id"],
                "label": layer.get("label", layer["id"]),
                "file": layer["prompt"],
                "bytes": path.stat().st_size,
                "chars": len(text),
                "sha256": generator.prompt_sha256(text),
                "prompt": text,
                "artifacts": [dest for _, dest in generator.LAYER_ARTIFACTS.get(layer["id"], [])],
            }
        )
    return library


def last_build() -> dict | None:
    path = OUTPUT / "provenance.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError:
        return None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "generator": "neuralcommons-app-generator"}


@app.get("/api/prompts")
def api_prompts() -> dict:
    return {"prompts": prompt_library()}


@app.get("/api/status")
def api_status() -> dict:
    config = generator.load_config()
    return {
        "ollama": generator.ollama_status(config),
        "files": generator.output_tree(OUTPUT),
        "build": last_build(),
    }


@app.post("/api/generate")
def api_generate(use_ollama: bool = True) -> dict:
    return generator.generate(use_ollama=use_ollama)


@app.get("/")
def console(request: Request):
    config = generator.load_config()
    return templates.TemplateResponse(
        "console.html",
        {
            "request": request,
            "config": config,
            "prompts": prompt_library(),
            "ollama": generator.ollama_status(config),
            "files": generator.output_tree(OUTPUT),
            "build": last_build(),
            "archive_url": os.environ.get("ARCHIVE_URL", ""),
        },
    )

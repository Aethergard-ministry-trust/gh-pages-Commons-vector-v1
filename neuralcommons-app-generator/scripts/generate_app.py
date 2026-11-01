#!/usr/bin/env python3
"""Generate the whole application from the Base64 prompt library.

    python scripts/generate_app.py                 # use Ollama when it is running
    python scripts/generate_app.py --no-ollama     # always render from templates
    python scripts/generate_app.py --json          # machine readable build summary

Output lands in ``output/`` together with a ``provenance.json`` build record.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.generator import generate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the NeuralCommons application from prompts.")
    parser.add_argument("--no-ollama", action="store_true", help="skip the model and render from templates")
    parser.add_argument("--json", action="store_true", help="print the build summary as JSON")
    args = parser.parse_args(argv)

    summary = generate(use_ollama=not args.no_ollama)

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    print(f"mode       {summary['mode']} ({summary['model']} @ {summary['ollama']['url']})")
    print(f"namespace  {summary['namespace']}")
    print(f"duration   {summary['duration_ms']} ms")
    print(f"output     {summary['output_dir']}/ · {len(summary['files'])} files")
    print()
    for instrument in summary["instruments"]:
        print(
            f"  {instrument['instrument']}  {instrument['layer']:<20} {instrument['mode']:<9} "
            f"{instrument['prompt_chars']:>5} chars  {instrument['cid'][:16]}…"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

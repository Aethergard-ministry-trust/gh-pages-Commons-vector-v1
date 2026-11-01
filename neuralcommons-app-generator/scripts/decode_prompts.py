#!/usr/bin/env python3
"""Decode the Base64 prompt library into plain text.

Examples:
    python scripts/decode_prompts.py
    python scripts/decode_prompts.py --layer backend
    python scripts/decode_prompts.py --json > /tmp/prompts.json
    python scripts/decode_prompts.py --out /tmp/prompts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.generator import decode_prompt, load_config, prompt_sha256  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decode the NeuralCommons Base64 prompt library.")
    parser.add_argument("--layer", help="only decode this layer id (default: every layer)")
    parser.add_argument("--json", action="store_true", help="print JSON records instead of text")
    parser.add_argument("--out", help="write decoded prompts as <layer>_prompt.txt into this directory")
    args = parser.parse_args(argv)

    rows = []
    for layer in load_config().get("layers", []):
        if args.layer and layer["id"] != args.layer:
            continue
        text = decode_prompt(ROOT / layer["prompt"])
        rows.append(
            {
                "id": layer["id"],
                "label": layer.get("label", layer["id"]),
                "file": layer["prompt"],
                "chars": len(text),
                "sha256": prompt_sha256(text),
                "prompt": text,
            }
        )

    if not rows:
        print(f"no layer matches {args.layer!r}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    for row in rows:
        if args.out:
            target = Path(args.out)
            target.mkdir(parents=True, exist_ok=True)
            (target / f"{row['id']}_prompt.txt").write_text(row["prompt"], "utf-8")
            print(f"{row['id']} -> {target / (row['id'] + '_prompt.txt')}")
        else:
            print(f"# {row['id']} · {row['file']} · {row['chars']} chars · sha256 {row['sha256'][:12]}")
            print(row["prompt"])
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

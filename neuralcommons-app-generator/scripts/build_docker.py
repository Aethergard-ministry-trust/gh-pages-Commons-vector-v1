#!/usr/bin/env python3
"""Validate or run the generated application's Docker stack.

    python scripts/build_docker.py              # compose config check
    python scripts/build_docker.py --up         # docker compose up -d --build
    python scripts/build_docker.py --ps
    python scripts/build_docker.py --down
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ROOT / "output" / "docker-compose.yml"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or inspect the generated Docker stack.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--up", action="store_true", help="docker compose up -d --build")
    group.add_argument("--down", action="store_true", help="docker compose down")
    group.add_argument("--ps", action="store_true", help="docker compose ps")
    args = parser.parse_args(argv)

    if not COMPOSE.exists():
        print(f"{COMPOSE.relative_to(ROOT)} not found — run scripts/generate_app.py first", file=sys.stderr)
        return 1

    if args.up:
        command = ["docker", "compose", "-f", str(COMPOSE), "up", "-d", "--build"]
    elif args.down:
        command = ["docker", "compose", "-f", str(COMPOSE), "down"]
    elif args.ps:
        command = ["docker", "compose", "-f", str(COMPOSE), "ps"]
    else:
        command = ["docker", "compose", "-f", str(COMPOSE), "config", "--quiet"]

    print(" ".join(command))
    try:
        return subprocess.run(command, cwd=str(ROOT / "output"), check=False).returncode
    except FileNotFoundError:
        print("docker is not available in this environment", file=sys.stderr)
        return 127


if __name__ == "__main__":
    raise SystemExit(main())

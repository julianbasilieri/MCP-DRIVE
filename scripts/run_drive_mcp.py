#!/usr/bin/env python3
"""Launcher seguro para Drive MCP.

Carga variables de entorno desde .env/.env.local (si existen)
y arranca el servidor MCP interno de Drive (drive_mcp.server).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    _load_dotenv(repo_root / ".env")
    _load_dotenv(repo_root / ".env.local")

    default_secret = repo_root / "gcp-oauth.keys.json"
    if not os.getenv("GOOGLE_CLIENT_SECRET_PATH") and default_secret.exists():
        os.environ["GOOGLE_CLIENT_SECRET_PATH"] = str(default_secret)

    from drive_mcp.server import DriveMCPServer

    server = DriveMCPServer()
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

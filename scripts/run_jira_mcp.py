#!/usr/bin/env python3
"""Launcher seguro para Jira MCP.

Carga variables de entorno desde .env/.env.local (si existen) y
arranca el servidor MCP sin exponer secretos en .vscode/mcp.json.
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
    # Ensure package imports work when script is invoked as scripts/run_jira_mcp.py
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    _load_dotenv(repo_root / ".env")
    _load_dotenv(repo_root / ".env.local")

    required = ("JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        print(
            "Faltan variables para Jira MCP: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    from jira_mcp.server import JiraMCPServer

    server = JiraMCPServer()
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

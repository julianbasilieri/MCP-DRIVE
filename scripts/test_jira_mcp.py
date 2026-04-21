#!/usr/bin/env python3
"""
Script de prueba para el MCP de Jira
"""

import subprocess
import json
import os
import sys
from pathlib import Path


def _load_dotenv(path: Path, env_dict: dict) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in env_dict:
            env_dict[key] = value


# Configurar las variables de entorno
env = os.environ.copy()
repo_root = Path(os.getcwd())
_load_dotenv(repo_root / ".env", env)
_load_dotenv(repo_root / ".env.local", env)

required_vars = ["JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN"]
missing = [key for key in required_vars if not env.get(key)]

if missing:
    print(f"Faltan variables de entorno: {', '.join(missing)}")
    sys.exit(1)

# Ruta al python del venv (ajustar para Windows)
venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')

# Iniciar el proceso del MCP
process = subprocess.Popen(
    [venv_python, '-m', 'jira_mcp.server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env=env,
    cwd=os.getcwd()
)

requests = [
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test_jira_mcp", "version": "1.0"},
        },
    },
    {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    },
    {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_projects",
            "arguments": {},
        },
    },
]
test_request = "\n".join(json.dumps(req, ensure_ascii=False) for req in requests) + "\n"

print("Enviando solicitudes MCP: initialize, tools/list, tools/call(get_projects)")
print(f"Usando Python: {venv_python}")
print(f"CWD: {os.getcwd()}")

try:
    stdout, stderr = process.communicate(input=test_request, timeout=10)
    print(f"\nRespuesta stdout:\n{stdout}")
    if stderr:
        print(f"\nRespuesta stderr:\n{stderr}")
except subprocess.TimeoutExpired:
    process.kill()
    print("El proceso tardó demasiado en responder")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

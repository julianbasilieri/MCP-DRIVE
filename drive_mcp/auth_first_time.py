"""
Script para realizar la autenticación inicial con Google Drive.

Este script solo genera las credenciales y el token.
Ejecutar una sola vez al configurar el proyecto por primera vez.

Uso:
    python drive_mcp/auth_first_time.py

El token se guardará en token_styles.json para futuras ejecuciones.
"""

import os
import sys
from pathlib import Path

# Cargar variables de entorno desde .env
def _load_dotenv():
    repo_root = Path(__file__).resolve().parents[1]
    for env_file in [repo_root / ".env", repo_root / ".env.local"]:
        if not env_file.exists():
            continue
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

_load_dotenv()

# Asegurar que el paquete local se importa
_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from auth import get_credentials


if __name__ == "__main__":
    print("=" * 70)
    print("AUTENTICACIÓN INICIAL CON GOOGLE DRIVE")
    print("=" * 70)
    print()
    print("Este script genera un token de acceso para Google Drive.")
    print("Solo es necesario ejecutarlo UNA VEZ.")
    print()
    print("Se abrirá el navegador para que autorices el acceso.")
    print("Acepta los permisos solicitados.")
    print()
    print("-" * 70)
    print()
    
    try:
        creds = get_credentials()
        print()
        print("-" * 70)
        print()
        print("✅ Autenticación completada exitosamente.")
        print()
        print("Token guardado en: token_styles.json")
        print()
        print("Ya puedes usar el Drive MCP sin volver a ejecutar este script.")
        print()
        print("Próximos pasos:")
        print("  1. Reinicia el servidor drive_mcp desde VS Code")
        print("  2. Las herramientas de Drive ya estarán disponibles")
        print()
        
    except Exception as e:
        print()
        print("-" * 70)
        print()
        print(f"❌ Error durante la autenticación: {e}")
        print()
        sys.exit(1)

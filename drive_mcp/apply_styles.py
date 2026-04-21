"""
Script principal para aplicar estilos a documentos Google Docs.

Coordina la autenticación y la aplicación de estilos Montserrat.

Operaciones:
- Fuente: Montserrat en todo el documento (incluye celdas de tablas)
- H1/TITLE: #077BDE, Bold (700)
- H2: #077BDE, Bold (700)
- H3: #055A9E (azul más oscuro), SemiBold (600), italic
- Líneas en mayúsculas detectadas como títulos: #077BDE, Bold (700)
"""

import os
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

from auth import get_credentials
from styles import apply_styles
from security import validate_operation
from googleapiclient.discovery import build


if __name__ == "__main__":
    creds = get_credentials()
    profile = os.getenv("DRIVE_STYLE_PROFILE", "tesis_default")
    document_id = os.getenv("GOOGLE_DOCS_ID")

    drive_service = build("drive", "v3", credentials=creds)
    if document_id:
        validate_operation(drive_service, document_id, "apply_styles.py")

    apply_styles(creds, document_id=document_id, profile_name=profile)

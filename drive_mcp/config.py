"""
Configuración centralizada para Drive MCP.

**CRÍTICO:** Carpeta raíz COMPARTIDA para todo el equipo.
Esta es la carpeta oficial del proyecto PPS donde se deben guardar TODOS los archivos.

No debe cambiarse por usuario. Todos trabajan dentro de esta carpeta.
"""

import os
from pathlib import Path

# ============================================================================
# 🔒 CARPETA RAÍZ OBLIGATORIA Y COMPARTIDA PARA EL EQUIPO
# ============================================================================
# Esta carpeta es FIJA para todo el proyecto
# https://drive.google.com/drive/folders/13cEoJyVieAmc_S6aBMOoEt9us9gJT877
# NO debe modificarse por usuario
DRIVE_ROOT_FOLDER_ID = "13cEoJyVieAmc_S6aBMOoEt9us9gJT877"

# Rutas
_REPO_ROOT = Path(__file__).resolve().parents[1]
KEYS_FILE = os.getenv(
    "GOOGLE_CLIENT_SECRET_PATH",
    str(_REPO_ROOT / "gcp-oauth.keys.json"),
)
TOKEN_FILE = os.getenv(
    "GOOGLE_DRIVE_MCP_TOKEN_FILE",
    str(_REPO_ROOT / "token_styles.json"),
)

# Google OAuth Scopes
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

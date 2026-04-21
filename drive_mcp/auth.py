"""
Gestión de autenticación con Google OAuth2.

Maneja:
- Obtención de credenciales desde token guardado
- Flujo OAuth2 con refresh automático
- Recuperación ante tokens revocados

Lee configuración desde:
  - config.py (DRIVE_ROOT_FOLDER_ID, rutas de archivos)
  - Variables de entorno (.env)
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
try:
    from .config import KEYS_FILE, TOKEN_FILE, SCOPES
except ImportError:
    from config import KEYS_FILE, TOKEN_FILE, SCOPES


def get_credentials():
    """
    Obtiene credenciales válidas de Google OAuth2.
    
    Intenta:
    1. Cargar token guardado si existe
    2. Refrescar si está expirado
    3. Si token está revocado, inicia flujo OAuth completo
    4. Guarda el nuevo token para futuras ejecuciones
    
    Returns:
        google.oauth2.credentials.Credentials: Credenciales válidas
    """
    creds = None
    
    # Intentar cargar token existente
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Validar/refrescar credenciales
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # Token revocado o inválido — redirigir al flujo completo de OAuth
                creds = None
        
        # Si no hay credenciales válidas, iniciar flujo OAuth
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(KEYS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Guardar token para futuras ejecuciones
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    
    return creds

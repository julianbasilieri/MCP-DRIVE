#!/usr/bin/env python3
"""
MCP Server para Google Drive
Permite listar, buscar y leer archivos en Google Drive y Google Docs.

Credenciales:
  - GOOGLE_CLIENT_SECRET_PATH  → ruta a gcp-oauth.keys.json (para primer auth)
  - GOOGLE_DRIVE_MCP_TOKEN_FILE → ruta al token JSON (default: token_styles.json)

El token se genera la primera vez ejecutando 'python apply_styles.py'.
Si el token está vigente, el servidor lo refresca automáticamente.
"""

import json
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_TOKEN_FILE = str(_REPO_ROOT / "token_styles.json")


class DriveMCPServer:
    def __init__(self):
        self.keys_file = os.getenv(
            "GOOGLE_CLIENT_SECRET_PATH",
            str(_REPO_ROOT / "gcp-oauth.keys.json"),
        )
        self.token_file = os.getenv("GOOGLE_DRIVE_MCP_TOKEN_FILE", _DEFAULT_TOKEN_FILE)
        self.drive_service = None
        self.docs_service = None
        self._connect()

    def _connect(self):
        """Establece conexión con Google Drive y Docs usando credenciales OAuth2."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Faltan dependencias de Google. Ejecutar: "
                "pip install google-auth google-auth-oauthlib "
                "google-auth-httplib2 google-api-python-client"
            ) from exc

        token_path = Path(self.token_file)
        creds = None

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    token_path.write_text(creds.to_json(), encoding="utf-8")
                    logger.info("Token de Google refrescado correctamente.")
                except Exception as e:
                    logger.error(f"Error al refrescar token: {e}")
                    creds = None

            if not creds:
                raise RuntimeError(
                    f"Sin credenciales válidas en '{self.token_file}'. "
                    "Ejecutá 'python apply_styles.py' para autorizar el acceso a Google "
                    "y generar el token de sesión."
                )

        self.drive_service = build("drive", "v3", credentials=creds)
        self.docs_service = build("docs", "v1", credentials=creds)
        logger.info("Drive MCP conectado a Google.")

    # -------------------------------------------------------------------------
    # Herramientas de Drive
    # -------------------------------------------------------------------------

    def list_files(self, folder_id=None, max_results=20):
        """Lista archivos en Drive, opcionalmente dentro de una carpeta."""
        try:
            query_parts = ["trashed = false"]
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            q = " and ".join(query_parts)

            result = self.drive_service.files().list(
                q=q,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, size)",
            ).execute()

            return {
                "success": True,
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mimeType": f["mimeType"],
                        "modifiedTime": f.get("modifiedTime"),
                        "size": f.get("size"),
                    }
                    for f in result.get("files", [])
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, name=None, query=None, max_results=10):
        """Busca archivos por nombre y/o query libre de Drive API."""
        try:
            query_parts = ["trashed = false"]
            if name:
                safe = name.replace("\\", "\\\\").replace("'", "\\'")
                query_parts.append(f"name contains '{safe}'")
            if query:
                query_parts.append(query)

            q = " and ".join(query_parts)
            result = self.drive_service.files().list(
                q=q,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime)",
            ).execute()

            return {
                "success": True,
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mimeType": f["mimeType"],
                        "modifiedTime": f.get("modifiedTime"),
                    }
                    for f in result.get("files", [])
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_file_metadata(self, file_id):
        """Obtiene metadatos de un archivo de Drive por su ID."""
        try:
            meta = self.drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, modifiedTime, size, parents, webViewLink, createdTime",
            ).execute()
            return {"success": True, "file": meta}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_document(self, document_id):
        """Lee el contenido de un Google Doc como texto plano."""
        try:
            doc = self.docs_service.documents().get(documentId=document_id).execute()
            title = doc.get("title", "")
            content = doc.get("body", {}).get("content", [])

            lines = []
            for element in content:
                if "paragraph" in element:
                    para = element["paragraph"]
                    text = "".join(
                        e.get("textRun", {}).get("content", "")
                        for e in para.get("elements", [])
                    )
                    lines.append(text)

            return {
                "success": True,
                "title": title,
                "document_id": document_id,
                "content": "".join(lines),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -------------------------------------------------------------------------
    # Protocolo MCP (JSON-RPC 2.0)
    # -------------------------------------------------------------------------

    def handle_initialize(self, request):
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listTools": {}, "callTool": {}}},
                "serverInfo": {"name": "Drive MCP Server", "version": "1.0.0"},
            },
        }

    def handle_list_resources(self, request):
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"resources": []},
        }

    def handle_list_tools(self, request):
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "list_files",
                        "description": "Lista archivos en Google Drive. Opcionalmente filtra por carpeta.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "folder_id": {
                                    "type": "string",
                                    "description": "ID de la carpeta (opcional)",
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Máximo de resultados (default 20)",
                                },
                            },
                        },
                    },
                    {
                        "name": "search_files",
                        "description": (
                            "Busca archivos en Google Drive por nombre y/o query de Drive API. "
                            "Ejemplo de query: mimeType='application/vnd.google-apps.document'"
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Texto a buscar en el nombre del archivo",
                                },
                                "query": {
                                    "type": "string",
                                    "description": "Query libre de Drive API",
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Máximo de resultados (default 10)",
                                },
                            },
                        },
                    },
                    {
                        "name": "get_file_metadata",
                        "description": "Obtiene los metadatos de un archivo de Drive por su ID.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_id": {"type": "string"},
                            },
                            "required": ["file_id"],
                        },
                    },
                    {
                        "name": "read_document",
                        "description": "Lee el contenido de un Google Doc como texto plano.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "document_id": {"type": "string"},
                            },
                            "required": ["document_id"],
                        },
                    },
                ]
            },
        }

    def handle_call_tool(self, request):
        params = request.get("params", {})
        tool_name = params.get("name")
        tool_input = params.get("arguments", {})

        logger.debug(f"Ejecutando herramienta: {tool_name} con argumentos: {tool_input}")

        try:
            if tool_name == "list_files":
                result = self.list_files(**tool_input)
            elif tool_name == "search_files":
                result = self.search_files(**tool_input)
            elif tool_name == "get_file_metadata":
                result = self.get_file_metadata(**tool_input)
            elif tool_name == "read_document":
                result = self.read_document(**tool_input)
            else:
                result = {"success": False, "error": f"Herramienta desconocida: {tool_name}"}

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False),
                        }
                    ]
                },
            }
        except Exception as e:
            logger.error(f"Error ejecutando {tool_name}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Error interno: {str(e)}"},
            }

    def handle_request(self, request):
        try:
            method = request.get("method", "")

            # Notificaciones MCP (no requieren respuesta)
            if method.startswith("notifications/"):
                return None

            if method == "initialize":
                return self.handle_initialize(request)
            elif method == "resources/list":
                return self.handle_list_resources(request)
            elif method == "tools/list":
                return self.handle_list_tools(request)
            elif method == "tools/call":
                return self.handle_call_tool(request)
            else:
                logger.warning(f"Método desconocido: {method}")
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Método no encontrado: {method}",
                    },
                }
        except Exception as e:
            logger.error(f"Error procesando request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Error interno del servidor: {str(e)}",
                },
            }

    def run(self):
        """Bucle principal del servidor MCP."""
        logger.info("Iniciando Drive MCP Server...")

        for line in sys.stdin:
            try:
                line = line.strip()
                if not line:
                    continue

                logger.debug(f"Recibido: {line}")
                request = json.loads(line)
                response = self.handle_request(request)

                if response is None:
                    # Notificación: no se responde
                    continue

                logger.debug(f"Enviando: {json.dumps(response)}")
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"JSON inválido: {e}")
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error no capturado: {e}", exc_info=True)
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Error interno: {str(e)}"},
                }))
                sys.stdout.flush()


if __name__ == "__main__":
    try:
        server = DriveMCPServer()
        server.run()
    except Exception as e:
        error_msg = f"Error al iniciar Drive MCP: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(json.dumps({"error": error_msg}), file=sys.stderr)
        sys.exit(1)

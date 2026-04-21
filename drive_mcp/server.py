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

try:
    from .auth import get_credentials
    from .config import DRIVE_ROOT_FOLDER_ID
    from .security import validate_operation
    from .styles import apply_styles
    from .utils import extract_document_id, normalize_document_input
    from .edit import replace_text, append_text, replace_and_format
    from .file_ops import create_document, create_folder, copy_file, rename_file
except ImportError:
    from auth import get_credentials
    from config import DRIVE_ROOT_FOLDER_ID
    from security import validate_operation
    from styles import apply_styles
    from utils import extract_document_id, normalize_document_input
    from edit import replace_text, append_text, replace_and_format
    from file_ops import create_document, create_folder, copy_file, rename_file

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

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
        # La conexión se establece de forma lazy al ejecutar la primera herramienta.

    def _ensure_connected(self):
        """Conecta a Google Drive/Docs si aún no hay servicios activos."""
        if self.drive_service and self.docs_service:
            return

        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Faltan dependencias de Google. Ejecutar: "
                "pip install google-auth google-auth-oauthlib "
                "google-auth-httplib2 google-api-python-client"
            ) from exc

        creds = get_credentials()

        self.drive_service = build("drive", "v3", credentials=creds)
        self.docs_service = build("docs", "v1", credentials=creds)
        logger.info("Drive MCP conectado a Google.")

    def _filter_files_within_root(self, files):
        """Filtra archivos para devolver solo los que están dentro de la raíz compartida."""
        allowed = []
        for item in files:
            file_id = item.get("id")
            if not file_id:
                continue
            try:
                validate_operation(self.drive_service, file_id, "list/search")
                allowed.append(item)
            except PermissionError:
                continue
        return allowed

    # -------------------------------------------------------------------------
    # Herramientas de Drive
    # -------------------------------------------------------------------------

    def list_files(self, folder_id=None, max_results=20):
        """Lista archivos en Drive, opcionalmente dentro de una carpeta."""
        try:
            self._ensure_connected()

            effective_folder = folder_id or DRIVE_ROOT_FOLDER_ID
            validate_operation(self.drive_service, effective_folder, "list_files")

            query_parts = ["trashed = false"]
            query_parts.append(f"'{effective_folder}' in parents")
            q = " and ".join(query_parts)

            result = self.drive_service.files().list(
                q=q,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, size)",
            ).execute()

            files = self._filter_files_within_root(result.get("files", []))

            return {
                "success": True,
                "items": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mimeType": f["mimeType"],
                        "modifiedTime": f.get("modifiedTime"),
                        "size": f.get("size"),
                    }
                    for f in files
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, name=None, query=None, max_results=10):
        """Busca archivos por nombre y/o query libre de Drive API."""
        try:
            self._ensure_connected()
            query_parts = ["trashed = false"]
            if name:
                safe = name.replace("\\", "\\\\").replace("'", "\\'")
                query_parts.append(f"name contains '{safe}'")
            if query:
                query_parts.append(query)

            q = " and ".join(query_parts)
            result = self.drive_service.files().list(
                q=q,
                pageSize=max_results * 5,
                fields="files(id, name, mimeType, modifiedTime)",
            ).execute()

            filtered = self._filter_files_within_root(result.get("files", []))[:max_results]

            return {
                "success": True,
                "files": [
                    {
                        "id": f["id"],
                        "name": f["name"],
                        "mimeType": f["mimeType"],
                        "modifiedTime": f.get("modifiedTime"),
                    }
                    for f in filtered
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_file_metadata(self, file_id):
        """Obtiene metadatos de un archivo de Drive por su ID."""
        try:
            self._ensure_connected()
            validate_operation(self.drive_service, file_id, "get_file_metadata")
            meta = self.drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, modifiedTime, size, parents, webViewLink, createdTime",
            ).execute()
            return {"success": True, "file": meta}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_document(self, document_id):
        """Lee el contenido de un Google Doc como texto plano.
        
        Args:
            document_id: ID del documento o link de Google Docs
        """
        try:
            self._ensure_connected()
            # Normalizar input: acepta link o ID
            target_doc = normalize_document_input(document_id)
            if not target_doc:
                return {"success": False, "error": "document_id es requerido"}
            
            validate_operation(self.drive_service, target_doc, "read_document")
            doc = self.docs_service.documents().get(documentId=target_doc).execute()
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
                "document_id": target_doc,
                "content": "".join(lines),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def apply_document_styles(self, document_id=None, profile="tesis_default", overrides=None):
        """Aplica estilos a un documento con un perfil dinámico.
        
        Args:
            document_id: ID del documento o link de Google Docs (o usa GOOGLE_DOCS_ID del .env)
            profile: Perfil de estilos (default: tesis_default)
            overrides: Overrides del perfil
        """
        try:
            self._ensure_connected()
            # Normalizar input: acepta link, ID, o .env
            target_doc = document_id
            if target_doc:
                target_doc = normalize_document_input(target_doc)
            else:
                target_doc = os.getenv("GOOGLE_DOCS_ID")
            
            if not target_doc:
                return {
                    "success": False,
                    "error": "Falta document_id y no existe GOOGLE_DOCS_ID en entorno.",
                }

            validate_operation(self.drive_service, target_doc, "apply_document_styles")
            result = apply_styles(
                creds=get_credentials(),
                document_id=target_doc,
                profile_name=profile,
                profile_overrides=overrides,
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_document_replace(self, document_id, find_text, replacement_text, match_case=False, all_occurrences=True):
        """Reemplaza texto en un Google Doc.
        
        Args:
            document_id: ID del documento o link
            find_text: Texto a buscar
            replacement_text: Texto de reemplazo
            match_case: Respetar mayúsculas (default: False)
            all_occurrences: Reemplazar todas (default: True)
        """
        try:
            self._ensure_connected()
            target_doc = normalize_document_input(document_id)
            validate_operation(self.drive_service, target_doc, "edit_document_replace")
            
            result = replace_text(
                self.docs_service,
                target_doc,
                find_text,
                replacement_text,
                match_case=match_case,
                all_occurrences=all_occurrences,
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_document_append(self, document_id, text, bold=False, italic=False, font_size=None):
        """Agrega texto al final de un Google Doc.
        
        Args:
            document_id: ID del documento o link
            text: Texto a agregar
            bold: Negrita (default: False)
            italic: Itálica (default: False)
            font_size: Tamaño de fuente en puntos (ej: 12)
        """
        try:
            self._ensure_connected()
            target_doc = normalize_document_input(document_id)
            validate_operation(self.drive_service, target_doc, "edit_document_append")
            
            # Convertir font_size a formato de Google Docs (puntos * 2)
            gd_font_size = None
            if font_size:
                gd_font_size = int(font_size) * 2
            
            result = append_text(
                self.docs_service,
                target_doc,
                text,
                bold=bold,
                italic=italic,
                font_size=gd_font_size,
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def edit_document_replace_and_format(self, document_id, find_text, replacement_text, bold=False, italic=False, font_size=None, match_case=False, all_occurrences=True):
        """Reemplaza texto Y aplica formato en un Google Doc.
        
        Args:
            document_id: ID del documento o link
            find_text: Texto a buscar
            replacement_text: Texto de reemplazo
            bold: Negrita (default: False)
            italic: Itálica (default: False)
            font_size: Tamaño de fuente en puntos (ej: 12)
            match_case: Respetar mayúsculas (default: False)
            all_occurrences: Reemplazar todas (default: True)
        """
        try:
            self._ensure_connected()
            target_doc = normalize_document_input(document_id)
            validate_operation(self.drive_service, target_doc, "edit_document_replace_and_format")
            
            # Convertir font_size a formato de Google Docs (puntos * 2)
            gd_font_size = None
            if font_size:
                gd_font_size = int(font_size) * 2
            
            result = replace_and_format(
                self.docs_service,
                target_doc,
                find_text,
                replacement_text,
                bold=bold,
                italic=italic,
                font_size=gd_font_size,
                match_case=match_case,
                all_occurrences=all_occurrences,
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_document(self, name, folder_id=None):
        """Crea un nuevo Google Docs en Drive.
        
        Args:
            name: Nombre del documento
            folder_id: ID de la carpeta destino (opcional, usa raíz si omitido)
        """
        try:
            self._ensure_connected()
            # Si se proporciona folder_id, validar que esté en raíz
            if folder_id:
                validate_operation(self.drive_service, folder_id, "create_document")
            else:
                folder_id = DRIVE_ROOT_FOLDER_ID
            
            result = create_document(self.drive_service, name, folder_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_folder(self, name, folder_id=None):
        """Crea una nueva carpeta en Drive.
        
        Args:
            name: Nombre de la carpeta
            folder_id: ID de la carpeta destino (opcional, usa raíz si omitido)
        """
        try:
            self._ensure_connected()
            # Si se proporciona folder_id, validar que esté en raíz
            if folder_id:
                validate_operation(self.drive_service, folder_id, "create_folder")
            else:
                folder_id = DRIVE_ROOT_FOLDER_ID
            
            result = create_folder(self.drive_service, name, folder_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def copy_file(self, file_id, new_name, destination_folder_id=None):
        """Copia un archivo o carpeta en Drive.
        
        Args:
            file_id: ID del archivo a copiar
            new_name: Nombre de la copia
            destination_folder_id: ID de la carpeta destino (opcional)
        """
        try:
            self._ensure_connected()
            # Validar que el archivo a copiar esté en raíz
            validate_operation(self.drive_service, file_id, "copy_file")
            
            # Si se proporciona destination, validar también
            if destination_folder_id:
                validate_operation(self.drive_service, destination_folder_id, "copy_file")
            
            result = copy_file(self.drive_service, file_id, new_name, destination_folder_id)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def rename_file(self, file_id, new_name):
        """Renombra un archivo o carpeta en Drive.
        
        Args:
            file_id: ID del archivo a renombrar
            new_name: Nuevo nombre
        """
        try:
            self._ensure_connected()
            # Validar que el archivo esté en raíz
            validate_operation(self.drive_service, file_id, "rename_file")
            
            result = rename_file(self.drive_service, file_id, new_name)
            return result
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
                    {
                        "name": "apply_document_styles",
                        "description": (
                            "Aplica estilos tipográficos a un Google Doc con perfiles dinámicos "
                            "(ej: tesis_default, entrega_formal) y overrides opcionales."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "document_id": {
                                    "type": "string",
                                    "description": "ID del Google Doc. Si se omite usa GOOGLE_DOCS_ID",
                                },
                                "profile": {
                                    "type": "string",
                                    "description": "Perfil de estilos. Default: tesis_default",
                                },
                                "overrides": {
                                    "type": "object",
                                    "description": "Overrides parciales del perfil (dict).",
                                },
                            },
                        },
                    },
                    {
                        "name": "edit_document_replace",
                        "description": (
                            "Reemplaza texto en un Google Doc. "
                            "Acepta document_id como ID o link de Google Docs."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "document_id": {
                                    "type": "string",
                                    "description": "ID del Doc o link (https://docs.google.com/document/d/...)",
                                },
                                "find_text": {
                                    "type": "string",
                                    "description": "Texto a buscar",
                                },
                                "replacement_text": {
                                    "type": "string",
                                    "description": "Texto de reemplazo",
                                },
                                "match_case": {
                                    "type": "boolean",
                                    "description": "Respetar mayúsculas (default: False)",
                                },
                                "all_occurrences": {
                                    "type": "boolean",
                                    "description": "Reemplazar todas las ocurrencias (default: True)",
                                },
                            },
                            "required": ["document_id", "find_text", "replacement_text"],
                        },
                    },
                    {
                        "name": "edit_document_append",
                        "description": (
                            "Agrega texto al final de un Google Doc. "
                            "Acepta document_id como ID o link de Google Docs."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "document_id": {
                                    "type": "string",
                                    "description": "ID del Doc o link (https://docs.google.com/document/d/...)",
                                },
                                "text": {
                                    "type": "string",
                                    "description": "Texto a agregar",
                                },
                                "bold": {
                                    "type": "boolean",
                                    "description": "Negrita (default: False)",
                                },
                                "italic": {
                                    "type": "boolean",
                                    "description": "Itálica (default: False)",
                                },
                                "font_size": {
                                    "type": "integer",
                                    "description": "Tamaño de fuente en puntos (ej: 12)",
                                },
                            },
                            "required": ["document_id", "text"],
                        },
                    },
                    {
                        "name": "edit_document_replace_and_format",
                        "description": (
                            "Reemplaza texto Y aplica formato en un Google Doc. "
                            "Acepta document_id como ID o link de Google Docs."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "document_id": {
                                    "type": "string",
                                    "description": "ID del Doc o link (https://docs.google.com/document/d/...)",
                                },
                                "find_text": {
                                    "type": "string",
                                    "description": "Texto a buscar",
                                },
                                "replacement_text": {
                                    "type": "string",
                                    "description": "Texto de reemplazo",
                                },
                                "bold": {
                                    "type": "boolean",
                                    "description": "Negrita (default: False)",
                                },
                                "italic": {
                                    "type": "boolean",
                                    "description": "Itálica (default: False)",
                                },
                                "font_size": {
                                    "type": "integer",
                                    "description": "Tamaño de fuente en puntos (ej: 12)",
                                },
                                "match_case": {
                                    "type": "boolean",
                                    "description": "Respetar mayúsculas (default: False)",
                                },
                                "all_occurrences": {
                                    "type": "boolean",
                                    "description": "Reemplazar todas las ocurrencias (default: True)",
                                },
                            },
                            "required": ["document_id", "find_text", "replacement_text"],
                        },
                    },
                    {
                        "name": "create_document",
                        "description": "Crear un nuevo Google Docs en Drive. Acepta folder_id como ID de carpeta destino.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Nombre del documento",
                                },
                                "folder_id": {
                                    "type": "string",
                                    "description": "ID de la carpeta destino (opcional, usa raíz si omitido)",
                                },
                            },
                            "required": ["name"],
                        },
                    },
                    {
                        "name": "create_folder",
                        "description": "Crear una nueva carpeta en Drive. Acepta folder_id como ID de carpeta padre.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Nombre de la carpeta",
                                },
                                "folder_id": {
                                    "type": "string",
                                    "description": "ID de la carpeta padre (opcional, usa raíz si omitido)",
                                },
                            },
                            "required": ["name"],
                        },
                    },
                    {
                        "name": "copy_file",
                        "description": "Copiar un archivo o carpeta en Drive. Especifica el ID del archivo a copiar y el nombre de la copia.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_id": {
                                    "type": "string",
                                    "description": "ID del archivo o carpeta a copiar",
                                },
                                "new_name": {
                                    "type": "string",
                                    "description": "Nombre de la copia",
                                },
                                "destination_folder_id": {
                                    "type": "string",
                                    "description": "ID de la carpeta destino (opcional, usa misma ubicación si omitido)",
                                },
                            },
                            "required": ["file_id", "new_name"],
                        },
                    },
                    {
                        "name": "rename_file",
                        "description": "Renombrar un archivo o carpeta en Drive (sin moverlo).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_id": {
                                    "type": "string",
                                    "description": "ID del archivo o carpeta a renombrar",
                                },
                                "new_name": {
                                    "type": "string",
                                    "description": "Nuevo nombre",
                                },
                            },
                            "required": ["file_id", "new_name"],
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
            elif tool_name == "apply_document_styles":
                result = self.apply_document_styles(**tool_input)
            elif tool_name == "edit_document_replace":
                result = self.edit_document_replace(**tool_input)
            elif tool_name == "edit_document_append":
                result = self.edit_document_append(**tool_input)
            elif tool_name == "edit_document_replace_and_format":
                result = self.edit_document_replace_and_format(**tool_input)
            elif tool_name == "create_document":
                result = self.create_document(**tool_input)
            elif tool_name == "create_folder":
                result = self.create_folder(**tool_input)
            elif tool_name == "copy_file":
                result = self.copy_file(**tool_input)
            elif tool_name == "rename_file":
                result = self.rename_file(**tool_input)
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

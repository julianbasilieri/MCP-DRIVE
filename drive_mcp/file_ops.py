"""
Módulo para operaciones de gestión de archivos en Google Drive.
Soporta: crear documentos, carpetas, copiar y renombrar archivos.
"""

from googleapiclient.discovery import Resource
from typing import Dict, Any, Optional


def create_document(
    drive_service: Resource,
    name: str,
    parent_folder_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crea un nuevo Google Docs en Drive.

    Args:
        drive_service: Google Drive API service
        name: Nombre del documento
        parent_folder_id: ID de la carpeta padre (opcional)

    Returns:
        dict con resultado de la operación
    """
    try:
        # Validar nombre
        if not name or not name.strip():
            return {
                "success": False,
                "action": "create_document",
                "error": "El nombre del documento no puede estar vacío",
            }

        file_metadata = {
            "name": name.strip(),
            "mimeType": "application/vnd.google-apps.document",
        }

        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        file = drive_service.files().create(body=file_metadata, fields="id, name, webViewLink").execute()

        return {
            "success": True,
            "action": "create_document",
            "document_id": file.get("id"),
            "name": file.get("name"),
            "link": file.get("webViewLink"),
        }
    except Exception as e:
        return {
            "success": False,
            "action": "create_document",
            "error": str(e),
        }


def create_folder(
    drive_service: Resource,
    name: str,
    parent_folder_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crea una nueva carpeta en Google Drive.

    Args:
        drive_service: Google Drive API service
        name: Nombre de la carpeta
        parent_folder_id: ID de la carpeta padre (opcional)

    Returns:
        dict con resultado de la operación
    """
    try:
        # Validar nombre
        if not name or not name.strip():
            return {
                "success": False,
                "action": "create_folder",
                "error": "El nombre de la carpeta no puede estar vacío",
            }

        file_metadata = {
            "name": name.strip(),
            "mimeType": "application/vnd.google-apps.folder",
        }

        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        folder = drive_service.files().create(body=file_metadata, fields="id, name, webViewLink").execute()

        return {
            "success": True,
            "action": "create_folder",
            "folder_id": folder.get("id"),
            "name": folder.get("name"),
            "link": folder.get("webViewLink"),
        }
    except Exception as e:
        return {
            "success": False,
            "action": "create_folder",
            "error": str(e),
        }


def copy_file(
    drive_service: Resource,
    file_id: str,
    new_name: str,
    destination_folder_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Copia un archivo o carpeta en Google Drive.

    Args:
        drive_service: Google Drive API service
        file_id: ID del archivo a copiar
        new_name: Nombre de la copia
        destination_folder_id: ID de la carpeta destino (opcional)

    Returns:
        dict con resultado de la operación
    """
    try:
        # Validar nombre
        if not new_name or not new_name.strip():
            return {
                "success": False,
                "action": "copy_file",
                "error": "El nombre de la copia no puede estar vacío",
            }

        # Obtener metadatos del archivo original
        original_file = (
            drive_service.files()
            .get(fileId=file_id, fields="id, name, mimeType")
            .execute()
        )

        copy_metadata = {
            "name": new_name.strip(),
        }

        if destination_folder_id:
            copy_metadata["parents"] = [destination_folder_id]

        # Copiar el archivo
        copied_file = (
            drive_service.files()
            .copy(fileId=file_id, body=copy_metadata, fields="id, name, webViewLink")
            .execute()
        )

        return {
            "success": True,
            "action": "copy_file",
            "original_file_id": file_id,
            "original_name": original_file.get("name"),
            "new_file_id": copied_file.get("id"),
            "new_name": copied_file.get("name"),
            "link": copied_file.get("webViewLink"),
        }
    except Exception as e:
        return {
            "success": False,
            "action": "copy_file",
            "error": str(e),
        }


def rename_file(
    drive_service: Resource,
    file_id: str,
    new_name: str,
) -> Dict[str, Any]:
    """
    Renombra un archivo o carpeta en Google Drive (sin moverlo).

    Args:
        drive_service: Google Drive API service
        file_id: ID del archivo a renombrar
        new_name: Nuevo nombre

    Returns:
        dict con resultado de la operación
    """
    try:
        # Validar nombre
        if not new_name or not new_name.strip():
            return {
                "success": False,
                "action": "rename_file",
                "error": "El nuevo nombre no puede estar vacío",
            }

        # Obtener nombre anterior
        original_file = (
            drive_service.files()
            .get(fileId=file_id, fields="id, name")
            .execute()
        )

        old_name = original_file.get("name")

        # Actualizar nombre
        updated_file = (
            drive_service.files()
            .update(
                fileId=file_id,
                body={"name": new_name.strip()},
                fields="id, name, webViewLink",
            )
            .execute()
        )

        return {
            "success": True,
            "action": "rename_file",
            "file_id": file_id,
            "old_name": old_name,
            "new_name": updated_file.get("name"),
            "link": updated_file.get("webViewLink"),
        }
    except Exception as e:
        return {
            "success": False,
            "action": "rename_file",
            "error": str(e),
        }

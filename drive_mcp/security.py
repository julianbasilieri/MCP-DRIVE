"""
Validaciones de seguridad para el Drive MCP.

Asegura que todas las operaciones de Drive estén dentro de la carpeta raíz
definida por DRIVE_ROOT_FOLDER_ID.
"""

from typing import List, Optional
from config import DRIVE_ROOT_FOLDER_ID
from googleapiclient.discovery import Resource


def get_parent_folders(service: Resource, file_id: str) -> List[str]:
    """
    Obtiene la cadena de carpetas padre de un archivo.
    
    Args:
        service: Servicio de Google Drive API
        file_id: ID del archivo
        
    Returns:
        Lista de IDs de carpetas padre (ascendiendo)
    """
    parents = []
    current_id = file_id
    visited = set()  # Para evitar loops infinitos
    
    while current_id and current_id not in visited:
        visited.add(current_id)
        try:
            file_metadata = (
                service.files()
                .get(fileId=current_id, fields="parents")
                .execute()
            )
            parent_list = file_metadata.get("parents", [])
            if not parent_list:
                break
            parent_id = parent_list[0]
            parents.append(parent_id)
            current_id = parent_id
        except Exception:
            break
    
    return parents


def is_within_root_folder(service: Resource, file_id: str) -> bool:
    """
    Verifica si un archivo/carpeta está dentro de la carpeta raíz.
    
    Args:
        service: Servicio de Google Drive API
        file_id: ID del archivo/carpeta a verificar
        
    Returns:
        True si el archivo está dentro de DRIVE_ROOT_FOLDER_ID
        
    Raises:
        PermissionError: Si el archivo NO está dentro de la carpeta raíz
    """
    if file_id == DRIVE_ROOT_FOLDER_ID:
        return True
    
    parents = get_parent_folders(service, file_id)
    
    if DRIVE_ROOT_FOLDER_ID not in parents:
        raise PermissionError(
            f"❌ Acceso denegado: El archivo/carpeta {file_id} "
            f"NO está dentro de la carpeta raíz ({DRIVE_ROOT_FOLDER_ID}). "
            f"Todas las operaciones deben estar dentro de esta carpeta."
        )
    
    return True


def validate_operation(service: Resource, file_id: str, operation_name: str) -> None:
    """
    Valida que una operación sea permitida (archivo dentro de carpeta raíz).
    
    Args:
        service: Servicio de Google Drive API
        file_id: ID del archivo/carpeta
        operation_name: Nombre de la operación para mensajes de error
        
    Raises:
        PermissionError: Si la operación no es permitida
    """
    is_within_root_folder(service, file_id)

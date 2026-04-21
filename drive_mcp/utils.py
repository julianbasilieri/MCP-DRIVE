"""
Utilidades para operaciones con Google Drive/Docs.
- Extrae IDs de links
- Normaliza parámetros
"""

import re
from typing import Optional


def extract_document_id(document_input: str) -> str:
    """
    Extrae el ID de documento de un link o devuelve el ID tal cual si ya lo es.

    Ejemplos:
        "https://docs.google.com/document/d/1ABC123/edit" → "1ABC123"
        "1ABC123" → "1ABC123"
        "https://docs.google.com/document/d/1ABC123" → "1ABC123"

    Args:
        document_input: Link de Google Docs o document_id directamente

    Returns:
        str: El document_id extraído

    Raises:
        ValueError: Si no se puede extraer un ID válido
    """
    if not document_input or not isinstance(document_input, str):
        raise ValueError("document_input debe ser un string no vacío")

    document_input = document_input.strip()

    # Si ya parece un ID (alfanuméricos + guiones/underscores, al menos 10 chars)
    # Los IDs reales de Google tienen 28+ caracteres pero aceptamos más cortos para flexibilidad
    if re.match(r"^[a-zA-Z0-9_-]{10,}$", document_input):
        return document_input

    # Intenta extraer del link
    # Patrón: https://docs.google.com/document/d/{ID}/edit o sin /edit
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)(?:/|$|\?)", document_input)
    if match:
        return match.group(1)

    raise ValueError(
        f"No se pudo extraer document_id de: {document_input}. "
        "Usa un ID directo (≥10 caracteres alfanuméricos) o un link de Google Docs válido."
    )


def extract_folder_id(folder_input: str) -> str:
    """
    Extrae el ID de carpeta de un link o devuelve el ID tal cual si ya lo es.

    Ejemplos:
        "https://drive.google.com/drive/folders/1ABC123" → "1ABC123"
        "1ABC123" → "1ABC123"

    Args:
        folder_input: Link de Google Drive o folder_id directamente

    Returns:
        str: El folder_id extraído

    Raises:
        ValueError: Si no se puede extraer un ID válido
    """
    if not folder_input or not isinstance(folder_input, str):
        raise ValueError("folder_input debe ser un string no vacío")

    folder_input = folder_input.strip()

    # Si ya parece un ID (alfanuméricos + guiones/underscores, al menos 10 chars)
    if re.match(r"^[a-zA-Z0-9_-]{10,}$", folder_input):
        return folder_input

    # Intenta extraer del link
    # Patrón: https://drive.google.com/drive/folders/{ID}
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)(?:/|$|\?)", folder_input)
    if match:
        return match.group(1)

    # Patrón alternativo: /drive/folders/{ID}
    match = re.search(r"/drive/folders/([a-zA-Z0-9_-]+)(?:/|$|\?)", folder_input)
    if match:
        return match.group(1)

    raise ValueError(
        f"No se pudo extraer folder_id de: {folder_input}. "
        "Usa un ID directo (≥10 caracteres alfanuméricos) o un link de Google Drive válido."
    )


def normalize_document_input(document_input: Optional[str]) -> Optional[str]:
    """
    Normaliza input de documento (link o ID) a ID únicamente.

    Args:
        document_input: Link, ID, o None

    Returns:
        str o None: El document_id normalizado, o None si input es None
    """
    if not document_input:
        return None
    try:
        return extract_document_id(document_input)
    except ValueError as e:
        raise ValueError(f"Input de documento inválido: {e}")

"""
Módulo para editar contenido en Google Docs.
Soporta: reemplazar texto, agregar contenido, etc.
"""

from googleapiclient.discovery import Resource
from typing import Dict, Any, List, Optional
import re


def replace_text(
    docs_service: Resource,
    document_id: str,
    find_text: str,
    replacement_text: str,
    match_case: bool = False,
    all_occurrences: bool = True,
) -> Dict[str, Any]:
    """
    Reemplaza texto en un Google Doc.

    Args:
        docs_service: Google Docs API service
        document_id: ID del documento
        find_text: Texto a buscar
        replacement_text: Texto de reemplazo
        match_case: Si debe respetar mayúsculas
        all_occurrences: Si reemplazar todas las ocurrencias o solo la primera

    Returns:
        dict con resultados de la operación
    """
    try:
        requests = [
            {
                "findReplace": {
                    "findText": find_text,
                    "replaceText": replacement_text,
                    "matchCase": match_case,
                    "allInstances": all_occurrences,
                }
            }
        ]

        result = docs_service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        replacements_made = result.get("replies", [{}])[0].get("findReplace", {}).get("occurrencesChanged", 0)

        return {
            "success": True,
            "action": "replace_text",
            "find_text": find_text,
            "replacement_text": replacement_text,
            "occurrences_changed": replacements_made,
            "document_id": document_id,
        }
    except Exception as e:
        return {
            "success": False,
            "action": "replace_text",
            "error": str(e),
        }


def append_text(
    docs_service: Resource,
    document_id: str,
    text: str,
    bold: bool = False,
    italic: bool = False,
    font_size: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Agrega texto al final de un Google Doc.

    Args:
        docs_service: Google Docs API service
        document_id: ID del documento
        text: Texto a agregar
        bold: Si el texto debe estar en negrita
        italic: Si el texto debe estar en itálica
        font_size: Tamaño de fuente (en puntos * 2, ej: 24 = 12pt)

    Returns:
        dict con resultados de la operación
    """
    try:
        # Obtener el índice de fin del documento
        doc = docs_service.documents().get(documentId=document_id).execute()
        content = doc.get("body", {}).get("content", [])
        
        # El índice de fin está en doc.get("documentLength", 1) - 1
        # Pero en documentos vacíos, documentLength es 1, por lo que usamos un mínimo de 1
        end_index = max(1, doc.get("documentLength", 1) - 1)

        requests = [
            {
                "insertText": {
                    "text": text,
                    "location": {"index": end_index},
                }
            }
        ]

        # Aplicar formato si se especificó
        if bold or italic or font_size:
            # El texto se inserva desde end_index
            text_length = len(text)
            text_range = {
                "startIndex": end_index,
                "endIndex": end_index + text_length,
            }

            format_dict = {}
            if bold:
                format_dict["bold"] = True
            if italic:
                format_dict["italic"] = True
            if font_size:
                format_dict["fontSize"] = {"magnitude": font_size, "unit": "PT"}

            requests.append(
                {
                    "updateTextStyle": {
                        "range": text_range,
                        "textStyle": format_dict,
                        "fields": ",".join(format_dict.keys()),
                    }
                }
            )

        result = docs_service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        return {
            "success": True,
            "action": "append_text",
            "text": text,
            "bold": bold,
            "italic": italic,
            "font_size": font_size,
            "document_id": document_id,
        }
    except Exception as e:
        return {
            "success": False,
            "action": "append_text",
            "error": str(e),
        }


def replace_and_format(
    docs_service: Resource,
    document_id: str,
    find_text: str,
    replacement_text: str,
    bold: bool = False,
    italic: bool = False,
    font_size: Optional[int] = None,
    match_case: bool = False,
    all_occurrences: bool = True,
) -> Dict[str, Any]:
    """
    Reemplaza texto Y aplica formato en una operación.

    Args:
        docs_service: Google Docs API service
        document_id: ID del documento
        find_text: Texto a buscar
        replacement_text: Texto de reemplazo
        bold: Si el reemplazo debe estar en negrita
        italic: Si el reemplazo debe estar en itálica
        font_size: Tamaño de fuente
        match_case: Respetar mayúsculas
        all_occurrences: Reemplazar todas las ocurrencias

    Returns:
        dict con resultados de la operación
    """
    try:
        requests = [
            {
                "findReplace": {
                    "findText": find_text,
                    "replaceText": replacement_text,
                    "matchCase": match_case,
                    "allInstances": all_occurrences,
                }
            }
        ]

        # Primero hacer el reemplazo para obtener el índice
        result = docs_service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        replacements = result.get("replies", [{}])[0].get("findReplace", {}).get("occurrencesChanged", 0)

        # Si hay reemplazos y se pidió formato, aplicar formato
        if replacements > 0 and (bold or italic or font_size):
            # Obtener documento nuevamente para encontrar las nuevas posiciones
            doc = docs_service.documents().get(documentId=document_id).execute()
            content = doc.get("body", {}).get("content", [])

            # Buscar el texto reemplazado en el contenido
            format_requests = []
            position = 1
            for element in content:
                if "paragraph" in element:
                    para = element["paragraph"]
                    for text_elem in para.get("elements", []):
                        if "textRun" in text_elem:
                            text_content = text_elem["textRun"].get("content", "")
                            if replacement_text in text_content:
                                start_pos = position
                                end_pos = position + len(replacement_text)
                                
                                format_dict = {}
                                if bold:
                                    format_dict["bold"] = True
                                if italic:
                                    format_dict["italic"] = True
                                if font_size:
                                    format_dict["fontSize"] = {"magnitude": font_size, "unit": "PT"}

                                format_requests.append(
                                    {
                                        "updateTextStyle": {
                                            "range": {
                                                "startIndex": start_pos,
                                                "endIndex": end_pos,
                                            },
                                            "textStyle": format_dict,
                                            "fields": ",".join(format_dict.keys()),
                                        }
                                    }
                                )
                            position += len(text_content)

            if format_requests:
                docs_service.documents().batchUpdate(
                    documentId=document_id, body={"requests": format_requests}
                ).execute()

        return {
            "success": True,
            "action": "replace_and_format",
            "find_text": find_text,
            "replacement_text": replacement_text,
            "occurrences_changed": replacements,
            "formatted": bold or italic or font_size is not None,
            "document_id": document_id,
        }
    except Exception as e:
        return {
            "success": False,
            "action": "replace_and_format",
            "error": str(e),
        }

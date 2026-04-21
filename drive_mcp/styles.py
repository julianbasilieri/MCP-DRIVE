"""
Lógica de aplicación de estilos a documentos Google Docs.

Soporta perfiles dinámicos (runtime) para evitar cambios hardcodeados.
"""

import os
from googleapiclient.discovery import build

try:
    from .style_profiles import DEFAULT_PROFILE_NAME, get_style_profile
except ImportError:
    from style_profiles import DEFAULT_PROFILE_NAME, get_style_profile


DEFAULT_DOC_ID = os.getenv(
    "GOOGLE_DOCS_ID",
)

TEXT_STYLE_FIELDS = "foregroundColor,bold,italic,weightedFontFamily"


def collect_paragraphs(content):
    """
    Recorre el contenido recursivamente e incluye párrafos dentro de tablas.
    
    Args:
        content (list): Lista de elementos de contenido del documento
        
    Returns:
        list: Todos los párrafos encontrados, incluyendo en celdas
    """
    paragraphs = []
    for element in content:
        if "paragraph" in element:
            paragraphs.append(element)
        elif "table" in element:
            for row in element["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    paragraphs.extend(collect_paragraphs(cell.get("content", [])))
    return paragraphs


def build_named_style_requests():
    """Placeholder mantenido por compatibilidad."""
    return []


def apply_styles(
    creds,
    document_id=None,
    profile_name=DEFAULT_PROFILE_NAME,
    profile_overrides=None,
):
    """
    Aplica estilos al documento Google Docs configurado.

    Args:
        creds: Credenciales OAuth2 válidas.
        document_id: ID del documento destino. Si es None, usa GOOGLE_DOCS_ID.
        profile_name: Nombre del perfil de estilo.
        profile_overrides: Dict parcial para sobreescribir el perfil.

    Returns:
        dict con métricas de aplicación.
    """
    style_cfg = get_style_profile(profile_name, profile_overrides)
    doc_id = document_id or DEFAULT_DOC_ID
    if not doc_id:
        raise ValueError("Falta document_id y no existe GOOGLE_DOCS_ID en entorno.")
    docs = build("docs", "v1", credentials=creds)
    
    # Obtener documento
    doc = docs.documents().get(documentId=doc_id).execute()
    body = doc.get("body", {})
    content = body.get("content", [])
    
    # Acumular requests
    requests = []
    
    # Calcular endIndex total del documento
    end_index = body.get("content", [])[-1].get("endIndex", 1) - 1
    
    # 1. Aplicar Montserrat Regular a todo el documento
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": 1, "endIndex": end_index},
            "textStyle": {
                "weightedFontFamily": {
                    "fontFamily": style_cfg["font_family"],
                    "weight": style_cfg["normal_weight"],
                }
            },
            "fields": "weightedFontFamily"
        }
    })
    
    def _append_text_style_request(start_idx, end_idx, rgb, bold, italic, weight):
        requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "textStyle": {
                        "foregroundColor": {"color": {"rgbColor": rgb}},
                        "bold": bold,
                        "italic": italic,
                        "weightedFontFamily": {
                            "fontFamily": style_cfg["font_family"],
                            "weight": weight,
                        },
                    },
                    "fields": TEXT_STYLE_FIELDS,
                }
            }
        )

    # 2. Recorrer párrafos y aplicar formatos específicos
    for element in collect_paragraphs(content):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        
        named_style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")
        start = element.get("startIndex", 0)
        end = element.get("endIndex", 0)
        
        if start >= end:
            continue
        
        # Extraer texto del párrafo
        text = "".join(
            e.get("textRun", {}).get("content", "")
            for e in paragraph.get("elements", [])
        ).strip()
        
        # H3: azul oscuro, SemiBold 600, italic
        if named_style == "HEADING_3":
            _append_text_style_request(
                start,
                end - 1,
                style_cfg["colors"]["h3"],
                False,
                style_cfg["h3_italic"],
                style_cfg["h3_weight"],
            )
        
        # H1, H2, TITLE, H4 o líneas en mayúsculas: estilo heading principal.
        elif (
            named_style in ("HEADING_1", "HEADING_2", "TITLE", "HEADING_4")
            or (
                style_cfg["uppercase_as_heading"]
                and text
                and text == text.upper()
                and len(text) > 2
                and not text.startswith("|")
            )
        ):
            _append_text_style_request(
                start,
                end - 1,
                style_cfg["colors"]["heading"],
                True,
                False,
                style_cfg["heading_weight"],
            )
    
    # Enviar en lotes de 50 para evitar límites de requests
    batch_size = 50
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": batch}
        ).execute()
        print(f"Lote {i // batch_size + 1} aplicado ({len(batch)} requests)")

    print("\nEstilos aplicados correctamente.")
    return {
        "document_id": doc_id,
        "profile": profile_name,
        "requests_total": len(requests),
        "batches": (len(requests) + batch_size - 1) // batch_size,
    }

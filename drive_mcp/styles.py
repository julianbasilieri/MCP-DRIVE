"""
Lógica de aplicación de estilos a documentos Google Docs.

Gestiona:
- Aplicación de Montserrat en todo el documento
- Formateo de H1, H2, H3 con colores específicos
- Detección y formateo de títulos en mayúsculas
- Traversal de contenido incluyendo tablas
"""

from googleapiclient.discovery import build
from constants import BLUE_H1H2, BLUE_H3, BLACK
import os

# DOC_ID debe venir de variable de entorno
DOC_ID = os.getenv(
    "GOOGLE_DOCS_ID",
    "13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU"
)


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
    """
    Actualmente sin implementación.
    
    La API de Google Docs v1 no expone un endpoint para actualizar estilos
    nombrados de forma persistente. Los estilos se aplican directamente a 
    rangos de texto existentes en apply_styles().
    
    Returns:
        list: Lista vacía (placeholder para extensión futura)
    """
    return []


def apply_styles(creds):
    """
    Aplica estilos al documento Google Docs configurado.
    
    Operaciones:
    1. Aplica Montserrat Regular a todo el documento
    2. Aplica colores y pesos específicos según tipo de párrafo
    3. Detecta y formatea títulos en mayúsculas
    4. Maneja párrafos en tablas
    
    Args:
        creds: Credenciales de Google OAuth2
        
    Raises:
        Exception: Si hay error al acceder o modificar el documento
    """
    docs = build("docs", "v1", credentials=creds)
    
    # Obtener documento
    doc = docs.documents().get(documentId=DOC_ID).execute()
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
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 400}
            },
            "fields": "weightedFontFamily"
        }
    })
    
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
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end - 1},
                    "textStyle": {
                        "foregroundColor": {"color": {"rgbColor": BLUE_H3}},
                        "bold": False,
                        "italic": True,
                        "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 600}
                    },
                    "fields": "foregroundColor,bold,italic,weightedFontFamily"
                }
            })
        
        # H1, H2, TITLE, H4: azul principal, Bold 700
        elif named_style in ("HEADING_1", "HEADING_2", "TITLE", "HEADING_4"):
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end - 1},
                    "textStyle": {
                        "foregroundColor": {"color": {"rgbColor": BLUE_H1H2}},
                        "bold": True,
                        "italic": False,
                        "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 700}
                    },
                    "fields": "foregroundColor,bold,italic,weightedFontFamily"
                }
            })
        
        # Líneas en mayúsculas detectadas como subtítulos funcionales
        elif text and text == text.upper() and len(text) > 2 and not text.startswith("|"):
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": end - 1},
                    "textStyle": {
                        "foregroundColor": {"color": {"rgbColor": BLUE_H1H2}},
                        "bold": True,
                        "italic": False,
                        "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 700}
                    },
                    "fields": "foregroundColor,bold,italic,weightedFontFamily"
                }
            })
    
    # Enviar en lotes de 50 para evitar límites de requests
    batch_size = 50
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        docs.documents().batchUpdate(
            documentId=DOC_ID,
            body={"requests": batch}
        ).execute()
        print(f"Lote {i // batch_size + 1} aplicado ({len(batch)} requests)")
    
    print("\n✅ Estilos aplicados correctamente.")

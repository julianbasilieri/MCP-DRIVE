"""
Aplica estilos al documento Google Docs:
- Fuente: Montserrat en todo el documento (incluye celdas de tablas)
- H1/TITLE: #077BDE, Bold (700)
- H2: #077BDE, Bold (700)
- H3: #055A9E (azul más oscuro), SemiBold (600), italic
- Líneas en mayúsculas detectadas como títulos: #077BDE, Bold (700)
- Actualiza los estilos nombrados del documento para que nuevos párrafos
  hereden Montserrat automáticamente sin necesidad de volver a ejecutar el script.
"""

import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

DOC_ID = "13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU"
KEYS_FILE = os.path.join(os.path.dirname(__file__), "gcp-oauth.keys.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_styles.json")

# H1 / H2 / líneas mayúsculas
BLUE_H1H2 = {"red": 7/255, "green": 123/255, "blue": 222/255}   # #077BDE
# H3 — azul más oscuro y profundo
BLUE_H3   = {"red": 5/255, "green": 90/255,  "blue": 158/255}   # #055A9E
# Negro puro para cuerpo de texto
BLACK     = {"red": 0, "green": 0, "blue": 0}


def collect_paragraphs(content):
    """Recorre el contenido recursivamente e incluye párrafos dentro de tablas."""
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
    Actualiza los estilos nombrados del documento para que cualquier nuevo
    párrafo tipado en H1/H2/H3/NORMAL_TEXT herede Montserrat automáticamente.
    """
    styles = [
        {
            "namedStyleType": "NORMAL_TEXT",
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 400},
                "foregroundColor": {"color": {"rgbColor": BLACK}},
                "bold": False,
                "italic": False,
            },
        },
        {
            "namedStyleType": "TITLE",
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 700},
                "foregroundColor": {"color": {"rgbColor": BLUE_H1H2}},
                "bold": True,
                "italic": False,
            },
        },
        {
            "namedStyleType": "HEADING_1",
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 700},
                "foregroundColor": {"color": {"rgbColor": BLUE_H1H2}},
                "bold": True,
                "italic": False,
            },
        },
        {
            "namedStyleType": "HEADING_2",
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 700},
                "foregroundColor": {"color": {"rgbColor": BLUE_H1H2}},
                "bold": True,
                "italic": False,
            },
        },
        {
            "namedStyleType": "HEADING_3",
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 600},
                "foregroundColor": {"color": {"rgbColor": BLUE_H3}},
                "bold": False,
                "italic": True,
            },
        },
        {
            "namedStyleType": "HEADING_4",
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 700},
                "foregroundColor": {"color": {"rgbColor": BLUE_H1H2}},
                "bold": True,
                "italic": False,
            },
        },
    ]
    return [
        {
            "updateNamedStyles": {
                "namedStyles": {"styles": styles},
                "fields": (
                    "textStyle.weightedFontFamily,"
                    "textStyle.foregroundColor,"
                    "textStyle.bold,"
                    "textStyle.italic"
                ),
            }
        }
    ]


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(KEYS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def apply_styles():
    creds = get_credentials()
    docs = build("docs", "v1", credentials=creds)

    doc = docs.documents().get(documentId=DOC_ID).execute()
    body = doc.get("body", {})
    content = body.get("content", [])

    # --- Requests que se acumulan ---
    requests = []

    # 0. Actualizar estilos nombrados del documento (persistencia futura)
    requests.extend(build_named_style_requests())

    # endIndex total del documento
    end_index = body.get("content", [])[-1].get("endIndex", 1) - 1

    # 1. Aplicar Montserrat Regular a todo el documento (incluye tablas por rango)
    requests.append({
        "updateTextStyle": {
            "range": {"startIndex": 1, "endIndex": end_index},
            "textStyle": {
                "weightedFontFamily": {"fontFamily": "Montserrat", "weight": 400}
            },
            "fields": "weightedFontFamily"
        }
    })

    # 2. Recorrer párrafos — cuerpo principal + celdas de tablas
    for element in collect_paragraphs(content):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue

        named_style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")
        start = element.get("startIndex", 0)
        end = element.get("endIndex", 0)

        if start >= end:
            continue

        text = "".join(
            e.get("textRun", {}).get("content", "")
            for e in paragraph.get("elements", [])
        ).strip()

        # --- H3: azul oscuro, SemiBold 600, italic ---
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

        # --- H1, H2, TITLE: azul principal, Bold 700 ---
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

        # --- Líneas en mayúsculas detectadas como subtítulos funcionales ---
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

    # Enviar en lotes de 50
    batch_size = 50
    for i in range(0, len(requests), batch_size):
        batch = requests[i:i + batch_size]
        docs.documents().batchUpdate(
            documentId=DOC_ID,
            body={"requests": batch}
        ).execute()
        print(f"Lote {i // batch_size + 1} aplicado ({len(batch)} requests)")

    print("\n✅ Estilos aplicados correctamente.")


if __name__ == "__main__":
    apply_styles()

"""
Actualiza las fechas del plan de trabajo en el Google Doc.
Inicio anterior: 20/04/2026 → Inicio nuevo: 18/05/2026
Fin anterior:    08/06/2026 → Fin nuevo:    06/07/2026
Feriados considerados: 25/05/2026 (Revolución de Mayo), 17/06/2026 (Güemes)

Usa doble fase (placeholders) para evitar conflictos entre fechas antiguas y nuevas.
"""

import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

DOC_ID = "13OeKBKdRtsLYBhN-ro0cGLVTW_NkQgg1eSzaBZpaIuU"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_styles.json")

# Mapeo: fecha_antigua → fecha_nueva
# Sprint 1 (original 20/04-04/05 → nuevo 18/05-01/06)
# Sprint 2 (original 05/05-18/05 → nuevo 02/06-15/06)
# Sprint 3 (original 19/05-02/06 → nuevo 16/06-30/06, skip 17/06 Güemes)
# Sprint 4 (original 03/06-08/06 → nuevo 01/07-06/07)
DATE_MAP = [
    # Sprint 1
    ("20/04/2026", "18/05/2026"),
    ("21/04/2026", "19/05/2026"),
    ("22/04/2026", "20/05/2026"),
    ("23/04/2026", "21/05/2026"),
    ("24/04/2026", "22/05/2026"),
    ("27/04/2026", "26/05/2026"),
    ("28/04/2026", "27/05/2026"),
    ("29/04/2026", "28/05/2026"),
    ("30/04/2026", "29/05/2026"),
    ("04/05/2026", "01/06/2026"),   # Sprint 1 review
    # Sprint 2
    ("05/05/2026", "02/06/2026"),
    ("06/05/2026", "03/06/2026"),
    ("07/05/2026", "04/06/2026"),
    ("08/05/2026", "05/06/2026"),
    ("11/05/2026", "08/06/2026"),
    ("12/05/2026", "09/06/2026"),
    ("13/05/2026", "10/06/2026"),
    ("14/05/2026", "11/06/2026"),
    ("15/05/2026", "12/06/2026"),
    ("18/05/2026", "15/06/2026"),   # Sprint 2 last day
    # Sprint 3 (17/06 es feriado Güemes → 20/05 salta a 18/06)
    ("19/05/2026", "16/06/2026"),
    ("20/05/2026", "18/06/2026"),
    ("21/05/2026", "19/06/2026"),
    ("22/05/2026", "22/06/2026"),
    ("26/05/2026", "23/06/2026"),
    ("27/05/2026", "24/06/2026"),
    ("28/05/2026", "25/06/2026"),
    ("29/05/2026", "26/06/2026"),
    ("01/06/2026", "29/06/2026"),
    ("02/06/2026", "30/06/2026"),
    # Sprint 4
    ("03/06/2026", "01/07/2026"),
    ("04/06/2026", "02/07/2026"),
    ("05/06/2026", "03/07/2026"),   # Sprint 4 review
    ("08/06/2026", "06/07/2026"),   # Sprint 4 final + FECHA DE FIN
]

TEXT_MAP = [
    ("1 de mayo y 25 de mayo de 2026", "25 de mayo y 17 de junio de 2026"),
]


def main():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    docs = build("docs", "v1", credentials=creds)

    requests = []

    # Fase 1: fechas antiguas → placeholders únicos
    for i, (old, _) in enumerate(DATE_MAP):
        requests.append({"replaceAllText": {
            "containsText": {"text": old, "matchCase": True},
            "replaceText": f"%%D{i:02d}%%"
        }})

    # Fase 2: placeholders → fechas nuevas
    for i, (_, new) in enumerate(DATE_MAP):
        requests.append({"replaceAllText": {
            "containsText": {"text": f"%%D{i:02d}%%", "matchCase": True},
            "replaceText": new
        }})

    # Fase 3: reemplazos de texto adicional
    for old, new in TEXT_MAP:
        requests.append({"replaceAllText": {
            "containsText": {"text": old, "matchCase": True},
            "replaceText": new
        }})

    # Enviar en lotes de 50
    total = len(requests)
    for i in range(0, total, 50):
        batch = requests[i:i + 50]
        docs.documents().batchUpdate(
            documentId=DOC_ID,
            body={"requests": batch}
        ).execute()
        print(f"Lote {i // 50 + 1} procesado ({len(batch)} requests)")

    print(f"\n✅ Fechas actualizadas correctamente ({total} requests enviados).")
    print("   FECHA DE INICIO : 18/05/2026")
    print("   FECHA DE FIN    : 06/07/2026")
    print("   Feriados        : 25/05/2026 (Revolución de Mayo), 17/06/2026 (Güemes)")


if __name__ == "__main__":
    main()

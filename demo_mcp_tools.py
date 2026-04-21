#!/usr/bin/env python3
"""
Script de demostración de los 8 MCP tools disponibles.
SIN necesidad de modificar .env

Uso:
  source .venv/Scripts/activate
  python demo_mcp_tools.py
"""

import json
from drive_mcp.server import DriveMCPServer


def pretty_print_result(result):
    """Imprime el resultado formateado."""
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo():
    print("=" * 70)
    print("🎯 DEMOSTRACIÓN DE MCP TOOLS (SIN MODIFICAR .env)")
    print("=" * 70)

    server = DriveMCPServer()

    # 1. List tools
    print("\n1️⃣  LISTANDO HERRAMIENTAS DISPONIBLES")
    print("-" * 70)
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    result = server.handle_list_tools(req)
    tools = result["result"]["tools"]
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool['name']:<40} | {tool['description'][:40]}...")

    print(f"\n✅ Total: {len(tools)} tools disponibles\n")

    # 2. Demostración de extracción de IDs
    print("2️⃣  DEMOSTRACIÓN: Extracción de document_id (ID vs Link)")
    print("-" * 70)

    from drive_mcp.utils import extract_document_id

    test_inputs = [
        "1XyZ123abc",  # ID corto
        "https://docs.google.com/document/d/1XyZ123abc/edit",  # Link
    ]

    for input_val in test_inputs:
        try:
            extracted = extract_document_id(input_val)
            print(f"  Input:   {input_val[:50]}")
            print(f"  → ID:    {extracted}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")

    print("✅ El sistema extrae automáticamente el ID del link\n")

    # 3. Información de seguridad
    print("3️⃣  INFORMACIÓN DE SEGURIDAD")
    print("-" * 70)
    from drive_mcp.config import DRIVE_ROOT_FOLDER_ID

    print(f"  Carpeta raíz compartida (FIJA para todo el equipo):")
    print(f"  ID: {DRIVE_ROOT_FOLDER_ID}")
    print(f"  URL: https://drive.google.com/drive/folders/{DRIVE_ROOT_FOLDER_ID}\n")
    print("  ✅ Todos los documentos DEBEN estar dentro de esta carpeta\n")

    # 4. Ejemplos de uso
    print("4️⃣  EJEMPLOS DE LLAMADAS A TOOLS")
    print("-" * 70)

    examples = [
        {
            "name": "read_document (con ID)",
            "tool": "read_document",
            "params": {"document_id": "1XyZ123abc"},
        },
        {
            "name": "read_document (con link)",
            "tool": "read_document",
            "params": {
                "document_id": "https://docs.google.com/document/d/1XyZ123abc/edit"
            },
        },
        {
            "name": "edit_document_replace",
            "tool": "edit_document_replace",
            "params": {
                "document_id": "1XyZ123abc",
                "find_text": "TODO",
                "replacement_text": "HECHO",
            },
        },
        {
            "name": "edit_document_append",
            "tool": "edit_document_append",
            "params": {"document_id": "1XyZ123abc", "text": "Texto nuevo", "bold": True},
        },
        {
            "name": "edit_document_replace_and_format",
            "tool": "edit_document_replace_and_format",
            "params": {
                "document_id": "1XyZ123abc",
                "find_text": "IMPORTANTE",
                "replacement_text": "IMPORTANTE",
                "bold": True,
                "font_size": 14,
            },
        },
    ]

    for ex in examples:
        print(f"  📌 {ex['name']}")
        print(f"     Tool: {ex['tool']}")
        print(f"     Params: {json.dumps(ex['params'], ensure_ascii=False, indent=12)}\n")

    print("\n5️⃣  PRÓXIMOS PASOS")
    print("-" * 70)
    print("  ✅ Ver USAGE_EXAMPLES.md para más ejemplos")
    print("  ✅ Ver README.md en drive_mcp/ para documentación completa")
    print("  ✅ Ver .agents/skills/thesis-doc/SKILL.md para detalles técnicos")
    print("\n" + "=" * 70)
    print("✨ Todos los tools están listos para usar!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    demo()

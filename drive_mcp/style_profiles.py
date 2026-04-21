"""
Perfiles de estilo configurables para Google Docs.

Permite seleccionar un perfil base y aplicar overrides en runtime,
sin hardcodear cambios dentro de la lógica principal.
"""

from copy import deepcopy


DEFAULT_PROFILE_NAME = "tesis_default"


STYLE_PROFILES = {
    "tesis_default": {
        "font_family": "Montserrat",
        "normal_weight": 400,
        "heading_weight": 700,
        "h3_weight": 600,
        "h3_italic": True,
        "uppercase_as_heading": True,
        "colors": {
            "heading": {"red": 7 / 255, "green": 123 / 255, "blue": 222 / 255},
            "h3": {"red": 5 / 255, "green": 90 / 255, "blue": 158 / 255},
            "body": {"red": 0, "green": 0, "blue": 0},
        },
    },
    "entrega_formal": {
        "font_family": "Montserrat",
        "normal_weight": 400,
        "heading_weight": 700,
        "h3_weight": 600,
        "h3_italic": False,
        "uppercase_as_heading": False,
        "colors": {
            "heading": {"red": 0 / 255, "green": 77 / 255, "blue": 153 / 255},
            "h3": {"red": 0 / 255, "green": 64 / 255, "blue": 128 / 255},
            "body": {"red": 0, "green": 0, "blue": 0},
        },
    },
}


def _deep_merge(base, override):
    merged = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def get_style_profile(profile_name=DEFAULT_PROFILE_NAME, overrides=None):
    """Obtiene un perfil de estilos aplicando overrides opcionales."""
    if profile_name not in STYLE_PROFILES:
        available = ", ".join(sorted(STYLE_PROFILES.keys()))
        raise ValueError(
            f"Perfil de estilos desconocido: '{profile_name}'. Disponibles: {available}"
        )

    base = STYLE_PROFILES[profile_name]
    return _deep_merge(base, overrides or {})

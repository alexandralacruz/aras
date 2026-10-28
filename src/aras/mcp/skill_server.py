# -*- coding: utf-8 -*-
"""Servidor MCP que expone los skills académicos de ARAS.

Expone dos herramientas genéricas y una herramienta por cada skill de la
*suite* de investigación académica, de modo que un agente pueda:

1. **Descubrir** los skills disponibles con ``listar_skills``.
2. **Ejecutar** cualquiera con ``ejecutar_skill`` o con su herramienta
   específica (p. ej. ``abstract_writer``, ``title_generator``).

Requiere el paquete ``mcp`` (v2+, API ``MCPServer``) y, para ejecución real,
un modelo local vía Ollama.

Ejecutar:  python -m aras.mcp.skill_server
"""

from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from ..skills.executor import ejecutar_skill as _ejecutar_skill
from ..skills.registry import ACADEMIC_SKILLS, get_registry

#: Modelo local por defecto (sobrescribible con la variable ARAS_MODELO).
DEFAULT_MODEL = "llama3.2"

server = MCPServer(
    name="aras-skills",
    description=(
        "Expone los skills de la suite de investigación académica de ARAS "
        "(abstract-writer, reviewer, paper-outline, title-generator, etc.)."
    ),
)


@server.tool()
def listar_skills(academic_only: bool = True) -> str:
    """Devuelve la lista de skills disponibles (nombre, título y descripción) como JSON."""
    reg = get_registry()
    items = [
        {"name": s["name"], "title": s["title"], "description": s["description"]}
        for s in reg.list_skills(academic_only=academic_only)
    ]
    return json.dumps(items, ensure_ascii=False, indent=2)


@server.tool()
def ejecutar_skill(skill: str, entrada: str, formato: str = "texto") -> str:
    """Ejecuta un skill académico sobre la ENTRADA usando el LLM local.

    Parámetros:
    - skill: nombre del skill (ej. 'abstract-writer', 'reviewer').
    - entrada: texto/documento sobre el que actúa el skill.
    - formato: 'texto' o 'json'.
    """
    import os

    modelo = os.environ.get("ARAS_MODELO", DEFAULT_MODEL)
    return _ejecutar_skill(skill, entrada, formato=formato, modelo=modelo)


def _registrar_skills_individuales() -> None:
    """Registra una herramienta MCP por cada skill académico."""
    reg = get_registry()
    for skill in reg.skills(academic_only=True):
        nombre = skill.name

        def fabricar(nombre_skill: str):
            def herramienta(entrada: str, formato: str = "texto") -> str:
                """Ejecuta el skill académico correspondiente sobre la ENTRADA."""
                import os

                modelo = os.environ.get("ARAS_MODELO", DEFAULT_MODEL)
                return _ejecutar_skill(nombre_skill, entrada, formato=formato, modelo=modelo)

            return herramienta

        try:
            server.add_tool(
                fabricar(nombre),
                name=skill.tool_name,
                description=f"{skill.description} (skill '{nombre}')",
            )
        except Exception as exc:  # pragma: no cover - defensivo
            print(f"[aras-mcp] no se registró '{nombre}': {exc}")


# Registrar una herramienta por cada skill de la suite académica.
_registrar_skills_individuales()


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()

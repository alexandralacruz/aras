# -*- coding: utf-8 -*-
"""Ejecución de skills académicos usando un LLM local (Ollama).

Cada skill es un conjunto de instrucciones (``SKILL.md``). Para "ejecutarlo",
inyectamos esas instrucciones como *system prompt* y la entrada del usuario
como *user prompt*, y dejamos que el modelo siga el procedimiento descrito.

La función degrada con elegancia si Ollama no está disponible, de modo que los
laboratorios puedan ejecutarse (en modo ``dry_run`` o con un mensaje claro).
"""

from __future__ import annotations

from .registry import SkillRegistry, get_registry


def ejecutar_skill(
    nombre: str,
    entrada: str,
    formato: str = "texto",
    modelo: str = "llama3.2",
    temperature: float = 0.0,
    dry_run: bool = False,
    registry: SkillRegistry | None = None,
) -> str:
    """Ejecuta un skill académico sobre ``entrada`` con el LLM local.

    Parámetros
    ----------
    nombre:    nombre del skill (p. ej. ``abstract-writer``).
    entrada:   texto/documento sobre el que actúa el skill.
    formato:   ``"texto"`` o ``"json"`` (fuerza salida JSON en Ollama).
    modelo:    modelo local de Ollama.
    dry_run:   si es True, no llama al LLM y devuelve el prompt compuesto.
    """
    reg = registry or get_registry()
    skill = reg.get(nombre)
    if skill is None:
        disponibles = ", ".join(s.name for s in reg.skills(academic_only=False))
        return f"Error: skill '{nombre}' no encontrado. Disponibles: {disponibles}"

    sistema = (
        f"# {skill.title}\n\n"
        "Eres un asistente especializado. Sigue EXACTAMENTE las instrucciones "
        "de tu rol que aparecen a continuación y aplica el procedimiento descrito "
        "sobre la ENTRADA proporcionada por el usuario.\n\n"
        f"## Instrucciones del skill '{skill.name}'\n\n{skill.instructions}"
    )

    if dry_run:
        return (
            f"[dry_run] skill={skill.name} modelo={modelo} formato={formato}\n"
            f"---- SYSTEM PROMPT ----\n{sistema}\n"
            f"---- USER / ENTRADA ----\n{entrada}"
        )

    try:
        import ollama
    except ImportError:
        return "Error: el paquete 'ollama' no está instalado. Ejecuta: pip install ollama"

    kwargs: dict = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": sistema},
            {"role": "user", "content": entrada},
        ],
        "options": {"temperature": temperature},
    }
    if formato == "json":
        kwargs["format"] = "json"

    try:
        resp = ollama.chat(**kwargs)
    except Exception as exc:  # Ollama caído / modelo no descargado / etc.
        return (
            f"Error al llamar a Ollama ({type(exc).__name__}: {exc}). "
            "Asegúrate de que Ollama está corriendo (ollama serve) y de que el "
            f"modelo '{modelo}' está descargado (ollama pull {modelo})."
        )

    return resp["message"]["content"]

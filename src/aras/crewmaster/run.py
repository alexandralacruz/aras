# -*- coding: utf-8 -*-
"""CLI para generar un artículo científico con el equipo multiagente CrewMaster.

Ejemplo:
    python -m aras.crewmaster.run --topic "Retrieval-Augmented Generation for systematic reviews" --model llama3.2
"""

from __future__ import annotations

import argparse
import asyncio

from .models import ResearchTopic
from .system import generate_article


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera un artículo científico con el equipo multiagente ARAS/CrewMaster.",
    )
    parser.add_argument("--topic", required=True, help="Tema o pregunta de investigación.")
    parser.add_argument("--field", default="Computer Science", help="Campo científico.")
    parser.add_argument("--objective", default="", help="Objetivo del artículo.")
    parser.add_argument("--audience", default="academic", help="Audiencia objetivo.")
    parser.add_argument("--constraints", default="", help="Restricciones de longitud/estilo.")
    parser.add_argument("--language", default="English", help="Idioma del artículo.")
    parser.add_argument("--model", default="llama3.2", help="Modelo local de Ollama.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Temperatura.")
    return parser.parse_args()


def _ensure_ollama(model: str) -> None:
    """Verifica que Ollama responde y que el modelo está disponible."""
    try:
        import ollama
        disponibles = [m["name"] for m in ollama.list().get("models", [])]
    except Exception as exc:
        raise SystemExit(
            f"No se puede contactar con Ollama: {exc}\n"
            "Inícialo con: ollama serve (e instala el paquete con: pip install ollama)"
        ) from exc

    if not any(m == model or m.startswith(model + ":") for m in disponibles):
        print(f"AVISO: el modelo '{model}' no está descargado. Descárgalo con: ollama pull {model}")


def main() -> None:
    args = _parse_args()
    _ensure_ollama(args.model)
    topic = ResearchTopic(
        topic=args.topic,
        field=args.field,
        objective=args.objective,
        audience=args.audience,
        constraints=args.constraints,
        language=args.language,
    )
    article = asyncio.run(generate_article(topic, model=args.model, temperature=args.temperature))
    print(article.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

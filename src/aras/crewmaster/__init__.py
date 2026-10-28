# -*- coding: utf-8 -*-
"""Equipo multiagente con **CrewMaster** para generar un artículo científico.

Arquitectura (patrón *Operation tree* de CrewMaster v2):

- **Orquestador** = Operation raíz ``article_orchestrator``, cuyo objetivo
  (``produces``) es un ``ScientificArticle``. Coordina 4 sub-operaciones.
- **Equipo de 4 agentes** (operaciones hoja, cada una con su ``AgentConfig``,
  bloques de prompt y salida tipada):

  1. ``gather``      — identifica y recopila información (``GatheredSources``).
  2. ``analyze``     — analiza los resultados (``Analysis``).
  3. ``review``      — revisa consistencia y detecta vacíos (``ReviewResult``).
  4. ``synthesize``  — redacta el artículo final (``ScientificArticle``).

El flujo de datos se expresa como dependencias (``consumes``): cada etapa
recibe el tema (proyectado desde ``ResearchTopic``) y los artefactos tipados
de las etapas anteriores. CrewMaster resuelve el DAG y ejecuta los nodos en
orden topológico.

Requiere: ``crewmaster`` (v2) y, para ejecución real, ``ollama`` + un modelo
local.
"""

from .models import (
    Analysis,
    GatheredSources,
    ResearchTopic,
    ReviewResult,
    ScientificArticle,
    Section,
)
from .driver import OllamaDriver
from .system import build_system, generate_article, run_pipeline

__all__ = [
    "Analysis",
    "GatheredSources",
    "ResearchTopic",
    "ReviewResult",
    "ScientificArticle",
    "Section",
    "OllamaDriver",
    "build_system",
    "generate_article",
    "run_pipeline",
]

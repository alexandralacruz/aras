# -*- coding: utf-8 -*-
"""Construcción del sistema CrewMaster y punto de entrada ``generate_article``."""

from __future__ import annotations

from pathlib import Path

from crewmaster.agents.context.store import ContextStore
from crewmaster.agents.prompts.engine import PromptEngine
from crewmaster.agents.prompts.local_disk_store import LocalDiskStore
from crewmaster.api import execute
from crewmaster.execution.runtime import RuntimeDriver
from crewmaster.operations.operation import Operation

from .agents import ANALYST_AGENT, GATHERER_AGENT, REVIEWER_AGENT, SYNTHESIZER_AGENT
from .driver import OllamaDriver
from .models import Analysis, GatheredSources, ResearchTopic, ReviewResult, ScientificArticle
from .projector import ResearchTopicProjector

BLOCKS_ROOT = Path(__file__).resolve().parent / "blocks"


def build_operation() -> Operation:
    """Devuelve el árbol de operaciones (orquestador + 4 agentes)."""
    return Operation(
        name="article_orchestrator",
        produces=ScientificArticle,
        kind="artifact",
        sub_operations=[
            Operation(
                name="gather",
                produces=GatheredSources,
                kind="artifact",
                agent=GATHERER_AGENT,
                task_blocks=["blocks://article/task/gather"],
                consumes=[ResearchTopicProjector],
            ),
            Operation(
                name="analyze",
                produces=Analysis,
                kind="artifact",
                agent=ANALYST_AGENT,
                task_blocks=["blocks://article/task/analyze"],
                consumes=[ResearchTopicProjector, GatheredSources],
            ),
            Operation(
                name="review",
                produces=ReviewResult,
                kind="artifact",
                agent=REVIEWER_AGENT,
                task_blocks=["blocks://article/task/review"],
                consumes=[ResearchTopicProjector, GatheredSources, Analysis],
            ),
            Operation(
                name="synthesize",
                produces=ScientificArticle,
                kind="artifact",
                agent=SYNTHESIZER_AGENT,
                task_blocks=["blocks://article/task/synthesize"],
                consumes=[
                    ResearchTopicProjector,
                    GatheredSources,
                    Analysis,
                    ReviewResult,
                ],
            ),
        ],
    )


def build_block_store() -> LocalDiskStore:
    return LocalDiskStore(root=str(BLOCKS_ROOT))


def run_pipeline(
    topic: ResearchTopic,
    driver: RuntimeDriver,
    operation: Operation | None = None,
    block_store: LocalDiskStore | None = None,
) -> object:
    """Ejecuta el pipeline completo (orquestador + 4 agentes) y devuelve el
    ``ScientificArticle`` final.

    Se pasa explícitamente un ``RuntimeDriver`` para poder inyectar un driver
    falso en tests o ``OllamaDriver`` en producción.
    """
    operation = operation or build_operation()
    block_store = block_store or build_block_store()

    context_store = ContextStore()
    context_store.register(ResearchTopic, topic)

    prompt_engine = PromptEngine(block_store=block_store)

    return execute(
        operation=operation,
        context_store=context_store,
        default_runtime=driver,
        block_store=block_store,
        prompt_engine=prompt_engine,
    )


async def generate_article(
    topic: ResearchTopic,
    model: str = "llama3.2",
    temperature: float = 0.2,
) -> ScientificArticle:
    """Genera un artículo científico con el equipo multiagente (Ollama)."""
    driver = OllamaDriver(model=model, temperature=temperature)
    result = await run_pipeline(topic, driver)
    return result  # type: ignore[return-value]


def build_system(model: str = "llama3.2") -> tuple[Operation, LocalDiskStore, OllamaDriver]:
    """Devuelve (operation, block_store, driver) para inspección o uso manual."""
    return build_operation(), build_block_store(), OllamaDriver(model=model)

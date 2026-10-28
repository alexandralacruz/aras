# -*- coding: utf-8 -*-
"""Tests del equipo multiagente CrewMaster (sin depender de Ollama).

Se usa un ``FakeDriver`` que implementa el protocolo ``RuntimeDriver`` y
devuelve artefactos tipados prefabricados, lo que permite validar de forma
determinista que CrewMaster resuelve el DAG, renderiza los bloques de prompt y
ejecuta los 4 agentes en orden.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("crewmaster")

from crewmaster.execution.runtime import (  # noqa: E402
    RuntimeRequest,
    RuntimeResponse,
    TokenUsage,
)

from aras.crewmaster.models import (  # noqa: E402
    Analysis,
    GatheredSources,
    ResearchTopic,
    ReviewResult,
    ScientificArticle,
    Section,
)
from aras.crewmaster.driver import OllamaDriver  # noqa: E402
from aras.crewmaster.system import build_operation, run_pipeline  # noqa: E402


class FakeDriver:
    """Devuelve una salida tipada válida según el schema pedido por el nodo."""

    def __init__(self) -> None:
        self.schemas: list[type] = []

    async def execute(self, request: RuntimeRequest) -> RuntimeResponse:
        schema = request.output_schema
        self.schemas.append(schema)

        if schema is GatheredSources:
            out = GatheredSources(
                topic="RAG",
                key_findings=["RAG grounds answers in retrieved documents."],
                sources=["Lewis et al., 2020"],
                gaps_notes="",
            )
        elif schema is Analysis:
            out = Analysis(
                topic="RAG",
                themes=["grounding"],
                key_arguments=["retrieval reduces hallucination"],
                evidence_summary="strong evidence",
            )
        elif schema is ReviewResult:
            out = ReviewResult(topic="RAG", issues=[], gaps=[], verdict="APPROVED")
        elif schema is ScientificArticle:
            out = ScientificArticle(
                title="Retrieval-Augmented Generation: A Survey",
                abstract="This article surveys RAG.",
                keywords=["RAG", "LLM"],
                sections=[Section(heading="Introduction", content="Body text.")],
                conclusion="RAG improves grounding.",
                references=["Lewis et al., 2020"],
                limitations="Future work.",
            )
        else:  # pragma: no cover
            out = None

        return RuntimeResponse(output=out, token_usage=TokenUsage(), raw_messages=[])


def test_orchestrator_has_four_leaf_agents():
    op = build_operation()
    assert op.name == "article_orchestrator"
    assert op.produces is ScientificArticle
    assert [s.name for s in op.sub_operations] == ["gather", "analyze", "review", "synthesize"]
    assert all(s.agent is not None for s in op.sub_operations)


def test_pipeline_produces_scientific_article():
    topic = ResearchTopic(
        topic="Retrieval-Augmented Generation for systematic reviews",
        field="Computer Science",
    )
    driver = FakeDriver()
    result = asyncio.run(run_pipeline(topic, driver))

    assert isinstance(result, ScientificArticle)
    assert result.title
    assert result.abstract
    assert result.sections


def test_pipeline_executes_agents_in_topological_order():
    topic = ResearchTopic(topic="RAG", field="Computer Science")
    driver = FakeDriver()
    asyncio.run(run_pipeline(topic, driver))

    assert driver.schemas == [
        GatheredSources,
        Analysis,
        ReviewResult,
        ScientificArticle,
    ]


def test_ollama_driver_json_extraction():
    d = OllamaDriver()
    assert d._extract_json('{"a": 1}') == {"a": 1}
    assert d._extract_json('```json\n{"b": 2}\n```') == {"b": 2}
    assert d._extract_json('prefix {"c": [1, 2]} suffix') == {"c": [1, 2]}

    with pytest.raises(ValueError):
        d._extract_json("no json here")

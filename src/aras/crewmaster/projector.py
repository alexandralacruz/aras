# -*- coding: utf-8 -*-
"""Proyección de ``ResearchTopic`` al contexto de plantillas (ContextProjector)."""

from __future__ import annotations

from typing import Any

from .models import ResearchTopic


class ResearchTopicProjector:
    """Proyecta un ``ResearchTopic`` a un dict plano para las plantillas Jinja2."""

    def __init__(
        self,
        topic: str,
        field: str,
        objective: str,
        audience: str,
        constraints: str,
        language: str,
    ) -> None:
        self.topic = topic
        self.field = field
        self.objective = objective
        self.audience = audience
        self.constraints = constraints
        self.language = language

    @classmethod
    def from_domain(cls, data: ResearchTopic) -> "ResearchTopicProjector":
        return cls(
            topic=data.topic,
            field=data.field,
            objective=data.objective,
            audience=data.audience,
            constraints=data.constraints,
            language=data.language,
        )

    def to_context(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "field": self.field,
            "objective": self.objective,
            "audience": self.audience,
            "constraints": self.constraints,
            "language": self.language,
        }

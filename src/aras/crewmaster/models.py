# -*- coding: utf-8 -*-
"""Modelos de dominio tipados (Pydantic) del equipo de redacción académica.

Cada etapa del pipeline produce un artefacto tipado. CrewMaster usa estos
tipos como ``produces`` / ``consumes`` para resolver el DAG de dependencias
y para validar la salida estructurada del modelo.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ResearchTopic(BaseModel):
    """Semilla del sistema: el tema sobre el que se escribe el artículo."""

    model_config = ConfigDict(frozen=True)

    topic: str = Field(description="Research topic or research question")
    field: str = Field(default="Computer Science", description="Scientific field")
    objective: str = Field(default="", description="Objective of the article")
    audience: str = Field(default="academic", description="Target audience")
    constraints: str = Field(default="", description="Length/style constraints")
    language: str = Field(default="English", description="Language of the article")


class GatheredSources(BaseModel):
    """Información recopilada por el agente *gather*."""

    topic: str = Field(description="The research topic")
    key_findings: list[str] = Field(description="Key findings gathered on the topic")
    sources: list[str] = Field(description="Sources / references found")
    gaps_notes: str = Field(default="", description="Notes on missing information")


class Analysis(BaseModel):
    """Análisis producido por el agente *analyze*."""

    topic: str = Field(description="The research topic")
    themes: list[str] = Field(description="Main themes identified")
    key_arguments: list[str] = Field(description="Key arguments and their evidence")
    evidence_summary: str = Field(default="", description="Summary of supporting evidence")


class ReviewResult(BaseModel):
    """Revisión del agente *review* (consistencia y vacíos)."""

    topic: str = Field(description="The research topic")
    issues: list[str] = Field(description="Consistency issues detected")
    gaps: list[str] = Field(description="Information gaps detected")
    verdict: str = Field(description="'APPROVED' if ready, or 'REVISIONS_NEEDED'")


class Section(BaseModel):
    """Una sección del artículo final."""

    heading: str = Field(description="Section heading")
    content: str = Field(description="Section body text")


class ScientificArticle(BaseModel):
    """Artículo científico final producido por el agente *synthesize*."""

    title: str = Field(description="Article title")
    abstract: str = Field(description="Abstract (150-250 words)")
    keywords: list[str] = Field(description="Keywords")
    sections: list[Section] = Field(description="Body sections (e.g., Introduction, Method, Results, Discussion)")
    conclusion: str = Field(description="Conclusion")
    references: list[str] = Field(description="References (only those actually used)")
    limitations: str = Field(default="", description="Limitations and future work")

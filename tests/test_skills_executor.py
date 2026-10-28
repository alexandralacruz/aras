# -*- coding: utf-8 -*-
"""Tests del ejecutor de skills (`ejecutar_skill`)."""

from aras.skills.executor import ejecutar_skill
from aras.skills.registry import SkillRegistry


def test_unknown_skill_returns_error(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    out = ejecutar_skill("no-existe", "entrada", registry=reg)
    assert "no encontrado" in out
    assert "no-existe" in out


def test_dry_run_includes_composed_prompt(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    out = ejecutar_skill(
        "title-generator",
        "Un artículo sobre RAG para revisiones sistemáticas",
        dry_run=True,
        registry=reg,
    )
    assert "[dry_run]" in out
    assert "SYSTEM PROMPT" in out
    assert "Title Generator" in out          # título del skill
    assert "USER / ENTRADA" in out
    assert "RAG" in out                       # entrada del usuario


def test_dry_run_does_not_call_the_llm(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    out = ejecutar_skill("title-generator", "x", dry_run=True, registry=reg)
    # En dry_run nunca debe aparecer una respuesta del modelo.
    assert out.startswith("[dry_run]")


def test_execution_degrades_gracefully(tmp_skills_dir):
    """Sin Ollama disponible, debe devolver un mensaje (no lanzar excepción)."""
    reg = SkillRegistry(tmp_skills_dir)
    out = ejecutar_skill("title-generator", "prueba", registry=reg)
    assert isinstance(out, str)
    assert out.strip()

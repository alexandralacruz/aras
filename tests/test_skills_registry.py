# -*- coding: utf-8 -*-
"""Tests de conexión del registro de skills (`SkillRegistry`)."""

import pytest

from aras.skills.registry import (
    ACADEMIC_SKILLS,
    RESEARCH_ROLES,
    SkillRegistry,
    default_skills_dir,
)


def test_academic_skills_constant_has_20():
    assert len(ACADEMIC_SKILLS) == 20
    for name in [
        "abstract-writer",
        "title-generator",
        "reviewer",
        "paper-outline",
        "reference-checker",
        "latex-template-filler",
    ]:
        assert name in ACADEMIC_SKILLS


def test_research_roles_cover_all_academic_skills():
    assigned = {s for skills in RESEARCH_ROLES.values() for s in skills}
    missing = ACADEMIC_SKILLS - assigned
    assert not missing, f"Skills sin rol asignado: {missing}"


def test_registry_discovers_fixture_skills(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    names = {s.name for s in reg.skills(academic_only=False)}
    assert names == {"title-generator", "mergepdf"}


def test_registry_parses_frontmatter(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    s = reg.get("title-generator")
    assert s is not None
    assert s.title == "Title Generator"
    assert s.description == "Generates compelling paper titles."
    assert "Generate several title options" in s.instructions


def test_registry_ignores_dirs_without_skill_file(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    assert reg.get("empty-dir") is None


def test_academic_filter(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    assert [s.name for s in reg.skills(academic_only=True)] == ["title-generator"]


def test_get_missing_returns_none(tmp_skills_dir):
    assert SkillRegistry(tmp_skills_dir).get("no-existe") is None


def test_tool_name_sanitizes_hyphens(tmp_skills_dir):
    s = SkillRegistry(tmp_skills_dir).get("title-generator")
    assert s.tool_name == "title_generator"


def test_list_skills_shape(tmp_skills_dir):
    reg = SkillRegistry(tmp_skills_dir)
    items = reg.list_skills(academic_only=False)
    assert len(items) == 2
    for item in items:
        assert {"name", "title", "description"} <= set(item)


def test_connection_to_real_skills_dir():
    """Conexión real: ARAS debe descubrir los 20 skills académicos instalados."""
    base = default_skills_dir()
    if not base.exists():
        pytest.skip(f"No se encontró el directorio de skills: {base}")

    reg = SkillRegistry(base)
    academic = reg.skills(academic_only=True)
    assert len(academic) == 20, f"Se esperaban 20 skills, se encontraron {len(academic)}"

    for s in academic:
        assert s.title, f"{s.name} sin título"
        assert s.instructions.strip(), f"{s.name} sin instrucciones"

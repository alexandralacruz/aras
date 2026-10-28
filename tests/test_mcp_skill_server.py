# -*- coding: utf-8 -*-
"""Tests de conexión del servidor MCP de skills (`aras.mcp.skill_server`)."""

import asyncio
import json

import pytest

pytest.importorskip("mcp")

from aras.mcp.skill_server import server  # noqa: E402
from aras.skills.registry import ACADEMIC_SKILLS, default_skills_dir  # noqa: E402


def _tool_names() -> set[str]:
    return {t.name for t in asyncio.run(server.list_tools())}


def test_generic_tools_always_registered():
    assert {"listar_skills", "ejecutar_skill"} <= _tool_names()


def test_connection_via_mcp_discovers_academic_skills():
    """Conexión real: una herramienta MCP por cada skill académico."""
    if not default_skills_dir().exists():
        pytest.skip("skills dir not found")

    names = _tool_names()
    assert len(names) == 2 + len(ACADEMIC_SKILLS)  # 2 genéricas + 20 de skills
    for skill in ACADEMIC_SKILLS:
        assert skill.replace("-", "_") in names


def test_listar_skills_tool_returns_valid_json():
    res = asyncio.run(server.call_tool("listar_skills", {"academic_only": True}))
    data = json.loads(res.content[0].text)
    assert isinstance(data, list)

    if default_skills_dir().exists():
        assert len(data) == len(ACADEMIC_SKILLS)

    for item in data:
        assert item["name"]
        assert item["description"]


def test_ejecutar_skill_tool_returns_string_for_unknown_skill():
    res = asyncio.run(
        server.call_tool("ejecutar_skill", {"skill": "no-existe", "entrada": "x"})
    )
    text = res.content[0].text
    assert isinstance(text, str)
    assert "no encontrado" in text

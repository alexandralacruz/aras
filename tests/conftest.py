# -*- coding: utf-8 -*-
"""Fixtures compartidas para los tests de ARAS."""

import sys
from pathlib import Path

import pytest

# Red de seguridad: asegurar que 'src' esté en sys.path aunque pytest no use
# la opción pythonpath del pyproject.toml.
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def tmp_skills_dir(tmp_path):
    """Crea un directorio de skills hermético con fixtures de ejemplo."""
    (tmp_path / "title-generator").mkdir()
    (tmp_path / "title-generator" / "SKILL.md").write_text(
        "---\n"
        "name: title-generator\n"
        "description: Generates compelling paper titles.\n"
        "---\n\n"
        "# Title Generator\n\n"
        "Generate several title options for the paper.\n",
        encoding="utf-8",
    )

    (tmp_path / "mergepdf").mkdir()
    (tmp_path / "mergepdf" / "SKILL.md").write_text(
        "---\n"
        "name: mergepdf\n"
        "description: Merges two or more PDF files.\n"
        "---\n\n"
        "# Merge PDF\n\n"
        "Tool to combine PDF files locally.\n",
        encoding="utf-8",
    )

    # Directorio sin SKILL.md: debe ignorarse.
    (tmp_path / "empty-dir").mkdir()
    return tmp_path

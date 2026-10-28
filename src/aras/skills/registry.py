# -*- coding: utf-8 -*-
"""Carga y expone los *skills* académicos como capacidades de ARAS.

Los skills viven en el directorio de skills del agente (por defecto
``~/.pi/agent/skills``) y son archivos ``SKILL.md`` con frontmatter YAML
(``name`` y ``description``) y un cuerpo de instrucciones. Este módulo los
descubre y los convierte en objetos ``Skill`` listos para usarse como prompts
o como herramientas MCP.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

#: Skills que forman la *suite* de investigación académica de ARAS.
ACADEMIC_SKILLS: frozenset[str] = frozenset(
    {
        "abstract-writer",
        "conclusion-writer",
        "discussion-writer",
        "figure-designer",
        "hypothesis-writer",
        "journal-selector",
        "keywords-generator",
        "latex-template-filler",
        "literature-discovery",
        "methodology-designer",
        "novelty-analysis",
        "paper-outline",
        "plagiarism-checker",
        "reference-checker",
        "related-work",
        "research-gap",
        "research-manager",
        "reviewer",
        "state-of-the-art",
        "title-generator",
    }
)

#: Mapeo de skills a roles del equipo multiagente de ARAS (Módulo 6).
RESEARCH_ROLES: dict[str, list[str]] = {
    "descubrimiento": ["literature-discovery", "research-gap", "state-of-the-art"],
    "planificacion": ["research-manager", "paper-outline", "methodology-designer", "hypothesis-writer"],
    "redaccion": [
        "abstract-writer",
        "title-generator",
        "keywords-generator",
        "related-work",
        "methodology-designer",
        "discussion-writer",
        "conclusion-writer",
    ],
    "figuras": ["figure-designer"],
    "revision": ["reviewer", "novelty-analysis", "reference-checker", "plagiarism-checker"],
    "publicacion": ["journal-selector", "latex-template-filler"],
}


@dataclass(frozen=True)
class Skill:
    """Un skill académico cargado desde un archivo ``SKILL.md``."""

    name: str
    description: str
    title: str
    instructions: str
    path: Path = field(repr=False, default=None)  # type: ignore[assignment]

    @property
    def tool_name(self) -> str:
        """Nombre válido para una herramienta MCP (guiones -> guiones bajos)."""
        return self.name.replace("-", "_")


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Extrae el frontmatter YAML sencillo (``name``/``description``) y el cuerpo."""
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    meta: dict[str, str] = {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        if ":" in lines[i]:
            key, _, value = lines[i].partition(":")
            meta[key.strip()] = value.strip()

    body = "\n".join(lines[end + 1 :]).strip() if end is not None else text
    return meta, body


def _extract_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def default_skills_dir() -> Path:
    """Directorio de skills por defecto (sobrescribible con ``ARAS_SKILLS_DIR``)."""
    env = os.environ.get("ARAS_SKILLS_DIR")
    if env:
        return Path(env)
    return Path.home() / ".pi" / "agent" / "skills"


class SkillRegistry:
    """Descubre y consulta los skills disponibles en un directorio."""

    def __init__(self, base_dir: str | os.PathLike | None = None):
        self.base_dir = Path(base_dir) if base_dir is not None else default_skills_dir()
        self._skills: dict[str, Skill] = {}
        self._load()

    def _load(self) -> None:
        if not self.base_dir.exists():
            return
        for entry in sorted(self.base_dir.iterdir()):
            skill_file = entry / "SKILL.md"
            if not entry.is_dir() or not skill_file.exists():
                continue
            try:
                raw = skill_file.read_text(encoding="utf-8")
                meta, body = _parse_frontmatter(raw)
                name = meta.get("name") or entry.name
                self._skills[name] = Skill(
                    name=name,
                    description=meta.get("description", ""),
                    title=_extract_title(body, name),
                    instructions=body,
                    path=skill_file,
                )
            except Exception as exc:  # pragma: no cover - defensivo
                print(f"[aras] no se pudo cargar {skill_file}: {exc}")

    def __contains__(self, name: str) -> bool:
        return name in self._skills

    def __len__(self) -> int:
        return len(self._skills)

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def skills(self, academic_only: bool = True) -> list[Skill]:
        items = list(self._skills.values())
        if academic_only:
            items = [s for s in items if s.name in ACADEMIC_SKILLS]
        return sorted(items, key=lambda s: s.name)

    def list_skills(self, academic_only: bool = True) -> list[dict[str, str]]:
        """Lista resumida ``[{name, title, description}]`` para descubrimiento."""
        return [
            {"name": s.name, "title": s.title, "description": s.description}
            for s in self.skills(academic_only=academic_only)
        ]

    def describe(self) -> str:
        """Representación legible para logs y herramientas."""
        lines = [f"- {s.name}: {s.title}" for s in self.skills(academic_only=True)]
        return "\n".join(lines)


_registry: SkillRegistry | None = None


def get_registry(base_dir: str | os.PathLike | None = None) -> SkillRegistry:
    """Devuelve (y cachea) el registro global de skills."""
    global _registry
    if _registry is None or base_dir is not None:
        _registry = SkillRegistry(base_dir)
    return _registry

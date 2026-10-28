# -*- coding: utf-8 -*-
"""Skills académicos de ARAS.

Expone el registro de skills (``SkillRegistry``), la ejecución de skills vía
LLM (``ejecutar_skill``) y los mapeos a roles del equipo multiagente.
"""

from .executor import ejecutar_skill
from .registry import (
    ACADEMIC_SKILLS,
    RESEARCH_ROLES,
    Skill,
    SkillRegistry,
    get_registry,
)

__all__ = [
    "ACADEMIC_SKILLS",
    "RESEARCH_ROLES",
    "Skill",
    "SkillRegistry",
    "get_registry",
    "ejecutar_skill",
]

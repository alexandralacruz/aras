# -*- coding: utf-8 -*-
"""Configuraciones de los 4 agentes del equipo (``AgentConfig`` de CrewMaster)."""

from __future__ import annotations

from crewmaster.agents.agent import AgentConfig

# La identidad (quién es el agente) y la tarea (qué debe hacer) viven en
# bloques de prompt (`.j2`) resueltos por un BlockStore local.
GATHERER_AGENT = AgentConfig(
    name="gather",
    identity_blocks=["blocks://article/identity/gatherer"],
)

ANALYST_AGENT = AgentConfig(
    name="analyze",
    identity_blocks=["blocks://article/identity/analyst"],
)

REVIEWER_AGENT = AgentConfig(
    name="review",
    identity_blocks=["blocks://article/identity/reviewer"],
)

SYNTHESIZER_AGENT = AgentConfig(
    name="synthesize",
    identity_blocks=["blocks://article/identity/synthesizer"],
)

# Orden de los agentes en el canal secuencial (para channel_dispatch).
AGENT_ORDER: list[str] = ["gather", "analyze", "review", "synthesize"]

AGENTS: dict[str, AgentConfig] = {
    "gather": GATHERER_AGENT,
    "analyze": ANALYST_AGENT,
    "review": REVIEWER_AGENT,
    "synthesize": SYNTHESIZER_AGENT,
}

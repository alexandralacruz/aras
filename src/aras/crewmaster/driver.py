# -*- coding: utf-8 -*-
"""Driver de ejecución Ollama para CrewMaster (implementa ``RuntimeDriver``).

CrewMaster provee ``LangChainDriver`` y ``PydanticAIDriver``; aquí añadimos un
driver ligero que habla directamente con la API local de Ollama (sin depender
de LangChain), para modelos locales. Si ``request.output_schema`` está
presente (una clase Pydantic), se pide JSON y se valida contra el esquema.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from crewmaster.execution.runtime import (
    RuntimeDriver,
    RuntimeRequest,
    RuntimeResponse,
    TokenUsage,
)


class OllamaDriver:
    """Ejecuta nodos de un plan de CrewMaster usando Ollama en local.

    Parámetros
    ----------
    model:       nombre del modelo local (p. ej. ``llama3.2``).
    temperature: temperatura de generación.
    host:        host de la API de Ollama (por defecto ``localhost:11434``).
    """

    def __init__(
        self,
        model: str = "llama3.2",
        temperature: float = 0.2,
        host: str | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.host = host

    # ------------------------------------------------------------------
    # RuntimeDriver protocol
    # ------------------------------------------------------------------

    async def execute(self, request: RuntimeRequest) -> RuntimeResponse:
        try:
            import ollama  # import perezoso: solo se necesita al ejecutar
        except ImportError as exc:
            raise RuntimeError(
                "The 'ollama' package is not installed. Run: pip install ollama"
            ) from exc

        instructions = self._build_instructions(request)
        schema = request.output_schema

        last_error: str | None = None
        for _attempt in range(3):
            prompt = instructions
            if schema is not None:
                prompt += (
                    "\n\nOutput a single JSON object that validates against this "
                    "JSON Schema (do not wrap it in markdown):\n"
                    + json.dumps(schema.model_json_schema(), ensure_ascii=False)
                )
                if last_error:
                    prompt += (
                        f"\n\nYour previous answer was invalid: {last_error}\n"
                        "Fix it and output ONLY valid JSON."
                    )

            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": self.temperature},
            }
            if schema is not None:
                kwargs["format"] = "json"
            if self.host:
                kwargs["host"] = self.host

            try:
                resp = await asyncio.to_thread(ollama.chat, **kwargs)
            except Exception as exc:
                raise RuntimeError(
                    f"Ollama call failed for model '{self.model}': {exc}. "
                    "Is Ollama running (ollama serve) and the model pulled?"
                ) from exc

            text = resp["message"]["content"]
            usage = self._usage(resp)

            if schema is None:
                return RuntimeResponse(
                    output=text,
                    token_usage=usage,
                    raw_messages=[{"role": "assistant", "content": text}],
                )

            try:
                data = self._extract_json(text)
                obj = schema.model_validate(data)
                return RuntimeResponse(
                    output=obj,
                    token_usage=usage,
                    raw_messages=[{"role": "assistant", "content": text}],
                )
            except Exception as exc:  # JSON inválido o no cumple el esquema
                last_error = str(exc)
                continue

        raise ValueError(
            f"Could not produce a valid {schema.__name__} after retries. "
            f"Last error: {last_error}"
        )

    async def astream(self, request: RuntimeRequest):
        """Streaming no implementado en este driver (usa ``execute``)."""
        raise NotImplementedError("OllamaDriver does not support streaming.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_instructions(request: RuntimeRequest) -> str:
        instructions = request.instructions
        if request.context:
            parts = []
            for key, value in request.context.items():
                parts.append(f"- **{key}**: {value}")
            instructions += "\n\n## Context\n" + "\n".join(parts)
        return instructions

    @staticmethod
    def _usage(resp: dict[str, Any]) -> TokenUsage:
        return TokenUsage(
            input_tokens=int(resp.get("prompt_eval_count", 0)),
            output_tokens=int(resp.get("eval_count", 0)),
        )

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        text = text.strip()
        # Quitar cercas de markdown si las hay.
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("no JSON object found in model output")
        return json.loads(text[start : end + 1])

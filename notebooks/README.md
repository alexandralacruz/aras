# Laboratorios ARAS — Academic Research Agent System

Cuadernos Jupyter del curso **Intelligent Systems: Agentic Systems**. Cada
cuaderno es un **laboratorio** de un módulo y, en conjunto, construyen de forma
incremental el proyecto integrador **ARAS** (Academic Research Agent System).

## Estructura

| Cuaderno | Módulo | Contenido |
|----------|--------|-----------|
| `01a_fundamentos_llm_generacion.ipynb` | 1 | Ollama, tokens, temperatura, `top_p`/`top_k`, API de chat, ventana de contexto |
| `01b_fundamentos_llm_embeddings.ipynb` | 1 | Embeddings, similitud coseno, búsqueda semántica, alucinaciones |
| `02a_ingenieria_prompts_basicos.ipynb` | 2 | Rol, contexto, formato, restricciones, few-shot, JSON, clasificación/extracción/resumen |
| `02b_ingenieria_prompts_avanzados.ipynb` | 2 | Descomposición, iteración/evaluación, inyección de prompts y defensas |
| `03_pipelines_langchain.ipynb` | 3 | LLM vs workflow, LCEL, parsers Pydantic, errores, LangGraph (intro) |
| `04_sistemas_monoagente.ipynb` | 4 | Ciclo de razonamiento, tools, `create_react_agent`, registro, casos fallidos |
| `05_mcp.ipynb` | 5 | Servidor MCP (`MCPServer`), descubrimiento e invocación, seguridad |
| `06_multiagente_crewmaster.ipynb` | 6 | Roles, coordinación y revisión con LangGraph; CrewMaster (conceptos) |
| `07_evaluacion_seguridad_proyecto.ipynb` | 7 | Casos de prueba, métricas, comparación pipeline/agente/multiagente, mini ARAS |
| `08_integracion_skills_aras.ipynb` | 5+6 | Integra los *skills* académicos como prompts, herramientas MCP y roles |

Los módulos 1 y 2 tienen **dos cuadernos** cada uno; el resto, uno. El cuaderno
08 es un **complemento de integración** que conecta los módulos 5 y 6 con la
suite de *skills* académicos.

## Mapa hacia ARAS

```text
Pregunta de investigación
        │
        ▼
 LLM + prompts          → Módulos 1 y 2 (01a, 01b, 02a, 02b)
        │
        ▼
 Pipeline LangChain     → Módulo 3 (03)
        │
        ▼
 Agente coordinador     → Módulo 4 (04)
        │
        ├─ Herramientas MCP ──────────→ Módulo 5 (05)
        │
        └─ Agentes especializados ────→ Módulo 6 (06)
        │
        ▼
 Verificación / evaluación            → Módulo 7 (07)
        │
        ▼
 Informe final + trazabilidad
```

## Requisitos

1. **Ollama** instalado y un modelo local descargado (se usa `llama3.2` por
   defecto; puede sustituirse por otro compatible).
   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text   # para embeddings (Módulo 1b)
   ```
2. **Python 3.12+** y un entorno virtual:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. **Jupyter** y las dependencias (también se instalan desde cada cuaderno con
   `%pip install`):
   ```bash
   pip install jupyter ollama numpy langchain-core langchain-ollama langgraph pydantic mcp
   ```
   > **Nota:** se usa la API actual del paquete `mcp` (v2, clase `MCPServer`).
4. Lanzar los cuadernos desde la raíz del proyecto:
   ```bash
   jupyter lab notebooks
   ```

## Orden recomendado

Ejecuta los cuadernos en orden numérico. Cada uno indica en su cabecera la
**duración**, los **objetivos**, la **conexión con ARAS** y el **entregable** del
módulo correspondiente.

## Integración de skills académicos

El cuaderno `08_integracion_skills_aras.ipynb` y el paquete `src/aras/`
integran la **suite de investigación académica** ya instalada
(`~/.pi/agent/skills/`):

- `src/aras/skills/registry.py` — descubre y parsea los `SKILL.md` (`SkillRegistry`).
- `src/aras/skills/executor.py` — ejecuta un skill vía LLM local (`ejecutar_skill`).
- `src/aras/mcp/skill_server.py` — servidor MCP que expone un *tool* por skill.

Para ejecutar el servidor: `python -m aras.mcp.skill_server` (con `src/` en el
`PYTHONPATH`).

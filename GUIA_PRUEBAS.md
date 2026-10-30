# Guía de pruebas · ARAS

Cómo **clonar el repositorio** y **ejecutar las 22 pruebas** del sistema
ARAS (Academic Research Agent System) en tu máquina.

> Los tests **no necesitan Ollama**: usan un `FakeDriver` y modo `dry_run`,
> y degradan con elegancia si el modelo local no está disponible.

---

## 1. Requisitos previos

| Requisito | Versión / detalle |
|---|---|
| Python | **3.12+** (el proyecto se desarrolló con 3.12) |
| Git | para clonar el repositorio |
| Ollama | **NO es necesario para los tests** (solo para la demo real con LLM) |

---

## 2. Clonar el repositorio y crear el entorno

```bash
git clone <URL_DEL_REPOSITORIO> aras
cd aras

python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate
```

---

## 3. Instalar las dependencias de los tests

```bash
python -m pip install --upgrade pip
pip install pytest
pip install -r requirements-crewmaster.txt
pip install crewmaster==2.0.1 --no-deps
pip install "mcp>=2.3,<3"
```

> ⚠️ **Importante — no uses `poetry install` ni `pip install -e .` para los tests.**
> El `pyproject.toml` declara `langchain-core`/`langgraph` 1.x, que **conflictan**
> con CrewMaster 2.0.1 (usa 0.3.x / 0.2.x). El camino verificado es el de arriba.

---

## 4. Ejecutar las pruebas

Desde la **raíz del repositorio** (donde está `pyproject.toml`):

```bash
python -m pytest -v
```

Resultado esperado:

```text
22 passed
```

> No hace falta configurar `PYTHONPATH`: `pyproject.toml` ya define
> `pythonpath = ["src"]` y `tests/conftest.py` añade `src/` como red de seguridad.

---

## 5. Qué comprueban los 22 tests

| Archivo | Tests | Qué valida |
|---|---|---|
| `tests/test_skills_registry.py` | 10 | Descubrimiento de `SKILL.md`, parseo de frontmatter, filtro académico (20 skills), nombres de tool y conexión real con `~/.pi/agent/skills` |
| `tests/test_skills_executor.py` | 4 | Ejecución `dry_run` (sin llamar al LLM) y degradación elegante si Ollama no está |
| `tests/test_mcp_skill_server.py` | 4 | Servidor MCP: `listar_skills`, `ejecutar_skill` y una tool por skill; JSON válido |
| `tests/test_crewmaster_article.py` | 4 | Multiagente CrewMaster: orquestador + 4 agentes, orden topológico, `FakeDriver` (sin Ollama) |

---

## 6. Los skills académicos (para llegar a 22/22)

Dos tests conectan con la **suite real de 20 skills académicos**, que por
defecto se busca en:

```text
~/.pi/agent/skills/      (Windows: C:\Users\<tu_usuario>\.pi\agent\skills)
```

- Si **tienes** la suite instalada → los 2 tests pasan → **22 passed**.
- Si **no la tienes** → esos 2 tests se **saltan** (no fallan) → **20 passed, 2 skipped**.

Para tener los 20 skills:

- **Opción A** — copia las 20 carpetas de skills (cada una con su `SKILL.md`)
  a `~/.pi/agent/skills/`.
- **Opción B** — apunta a otra carpeta con la variable de entorno `ARAS_SKILLS_DIR`:

```bash
# Windows (PowerShell):
$env:ARAS_SKILLS_DIR = "C:\ruta\a\tus\skills"

# Windows (cmd):
set ARAS_SKILLS_DIR=C:\ruta\a\tus\skills

# macOS / Linux:
export ARAS_SKILLS_DIR=/ruta/a/tus/skills
```

---

## 7. Los `skipped` NO son fallos

Algunos tests se **saltan** a propósito cuando falta una dependencia opcional.
Así sabes de un vistazo qué falta:

| Resultado | Qué falta | Qué hacer |
|---|---|---|
| `22 passed` | nada ✅ | — |
| `20 passed, 2 skipped` | carpeta de skills (`~/.pi/agent/skills`) | ver sección 6 |
| `18 passed, 1 skipped` | `crewmaster` o `mcp` | ver sección 3 |
| menos de 18 passed, o algún `FAILED` | alguna dependencia rota | ver sección 8 |

---

## 8. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'crewmaster'` | falta CrewMaster | `pip install crewmaster==2.0.1 --no-deps` |
| `ModuleNotFoundError: No module named 'mcp'` | falta MCP | `pip install "mcp>=2.3,<3"` |
| `ModuleNotFoundError: No module named 'aras'` | no estás en la raíz del repo | `cd` a la raíz y vuelve a ejecutar |
| Solo corren 18 tests | `crewmaster` o `mcp` ausentes (el módulo entero se salta) | instala lo que falte (sección 3) |
| Fallos con `langchain` / `langgraph` | conflicto de versiones con el `pyproject.toml` | usa `requirements-crewmaster.txt` (sección 3), no `poetry install` |

---

## 9. Resumen rápido

```bash
git clone <URL_DEL_REPOSITORIO> aras
cd aras
python -m venv .venv

# Windows (en macOS/Linux: source .venv/bin/activate)
.venv\Scripts\activate

pip install pytest
pip install -r requirements-crewmaster.txt
pip install crewmaster==2.0.1 --no-deps
pip install "mcp>=2.3,<3"

python -m pytest -v        # → 22 passed
```

---

## ¿Y la demo real con LLM (Ollama)?

Los tests no la necesitan. Si además quieres ejecutar un *skill* con el LLM
local o el servidor MCP real, consulta el `README.md` y
`notebooks/08_integracion_skills_aras.ipynb` (necesitarás Ollama corriendo y el
modelo descargado: `ollama pull llama3.2`).

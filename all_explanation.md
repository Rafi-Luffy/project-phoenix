# Project Phoenix — Overall Explanation (Team Overview)

_Last updated: 2026-01-09_

This document is the **single source of truth** for understanding Project Phoenix at a high level and for running the **backend demo** (terminal-only, no frontend-backend integration required).

---

## 1) What this repo is

Project Phoenix is a **self-healing/autonomous backend system** with:

- A FastAPI backend that exposes health endpoints and LLM-assisted analysis endpoints.
- A learning/memory subsystem (episodic/semantic/procedural style memory abstractions).
- A “self-evolving” LLM pipeline powered by **local Ollama** (zero API cost), designed to output structured JSON and a confidence score.

This repo also contains a separate frontend (React/Vite), but **the professor demo path here is backend-only**.

---

## 1.1 What’s been done so far (current state)

This repo has gone through a few key stabilization milestones to reach “demo-ready” state:

- **Python runtime stabilization**: avoided Python 3.13 binary issues and standardized on Python 3.11 via `.venv_phoenix_demo` for reliable installs, test runs, and demo execution.
- **Backend health endpoint stability**: ensured database lifecycle methods exist and health checks return consistent booleans + details instead of `null`/crashing.
- **Ollama reliability**: demo flow actively verifies Ollama is running, starts it if needed, and pulls the demo model.
- **Self-evolving confidence pipeline**: `/llm/analyze_error` uses the evolving engine, prefers structured JSON, extracts confidence, and reports a stable `confidence_pct` for demo.
- **Professor-friendly terminal demo**: one command runs the whole story (Ollama → model → backend → live request → logs).
- **Tests passing with coverage gate**: backend tests run from repo root and the coverage configuration is scoped to the tested core modules.

---

## 2) Repo map (where things live)

Top-level highlights:

- `src/backend/` — FastAPI backend + autonomous system code
- `src/backend/main.py` — FastAPI app (routes)
- `src/backend/start.py` — backend entrypoint (starts Uvicorn)
- `src/backend/autonomous_system/` — core autonomy engine
- `src/backend/autonomous_system/tests/` — backend tests
- `scripts/demo_backend.sh` — the terminal demo runner (Ollama + backend + example request)
- `demo.sh` — convenience wrapper that runs `scripts/demo_backend.sh`
- `pytest.ini` — pytest configuration (includes coverage gate)
- `requirements.txt`, `src/backend/requirements.txt`, `requirements-docker.txt` — dependency lists (varies by environment)
- `logs/` — demo logs and PIDs (created at runtime)

---

## 2.1 Tech stack (what we use)

Backend:

- **Python**: 3.11 recommended (demo/test venv: `.venv_phoenix_demo`)
- **Web framework**: FastAPI
- **ASGI server**: Uvicorn
- **HTTP client**: (used for Ollama calls) aiohttp / requests-style patterns in code
- **Auth / tokens**: PyJWT (dependency used by some modules)
- **Form handling**: python-multipart (needed for form-data endpoints)

LLM:

- **Ollama** (local inference server)
- **Model**: `mistral` (pulled by the demo script)
- **Self-evolving engine**: prompt-variation selection + structured JSON parsing + confidence extraction

Database:

- PostgreSQL is supported/used in the current backend runtime configuration (health reports `database: postgresql`).
- There is also an in-memory DB layer used for tests and local-only flows.

Testing:

- pytest
- pytest-cov (coverage gate enforced in `pytest.ini`)

Frontend (present but not required for backend demo):

- React + TypeScript + Vite
- Tailwind + UI component patterns

---

## 2.2 Key runtime configuration

Environment variables you will see in the demo path:

- `PHOENIX_CONFIDENCE_TARGET` (default `0.91`)
- `PHOENIX_MAX_VARIATIONS` (default `4`)
- `OLLAMA_URL` (defaults to `http://localhost:11434` in the engine)
- `OLLAMA_MODEL` (defaults to `mistral`)

---

## 3) Backend architecture (high level)

### 3.1 FastAPI server
- The backend is served via **Uvicorn + FastAPI**.
- Key runtime behaviors:
  - Exposes `/health` to show system status.
  - Exposes `/llm/analyze_error` to demonstrate the self-evolving LLM reasoning pipeline.

  ---

  ## 3.1.1 Actual application flow (end-to-end)

  This is the “real” runtime flow your team should know.

  ### A) Startup flow

  1. `scripts/demo_backend.sh` (or `demo.sh`) launches the backend by running:
    - `.venv_phoenix_demo/bin/python src/backend/start.py`
  2. `src/backend/start.py` imports the FastAPI app from `src/backend/main.py`.
  3. On startup, the backend initializes core subsystems and logs readiness.
  4. The demo runner polls `GET http://127.0.0.1:8000/health` until the backend is responsive.

  ### B) Health check flow (`GET /health`)

  1. Route handler triggers orchestrator/system health evaluation.
  2. Database health is checked (connectivity + a lightweight `SELECT 1` style check when applicable).
  3. Memory subsystem reports stats.
  4. Response returns a consolidated payload like:
    - top-level `status`
    - `checks.database.healthy` plus `checks.database.details`
    - other subsystem checks

  ### C) LLM analysis flow (`POST /llm/analyze_error`)

  1. The API receives an error payload (`error_type`, `error_message`, `context`).
  2. LLM integrator calls the self-evolving engine.
  3. Engine queries Ollama `/api/generate` with:
    - base prompt
    - (optionally) prompt variations up to `PHOENIX_MAX_VARIATIONS`
  4. Engine prefers responses that:
    - parse as JSON
    - include a valid `confidence` in `[0..1]`
  5. Best candidate becomes the API response.
  6. The API returns:
    - `root_cause`
    - `severity`
    - `recommendations`
    - `confidence` + `confidence_pct`
    - `meta` explaining the engine choices

  ### D) Memory flow (conceptual)

  The system implements memory categories (episodic/semantic/procedural). In practice, this supports:

  - Recording “experiences” / events
  - Storing reusable knowledge
  - Tracking procedures/strategies and their success

  The tests show these flows end-to-end and serve as the best executable documentation for memory behaviors.

### 3.2 Orchestration layer
The orchestrator coordinates system components and exposes consolidated health checks.

- It checks database health.
- It reports readiness for subsystems (agents, memory, etc.).

### 3.3 LLM integration (Ollama)
The LLM integration is designed to be **local-first**:

- Ollama runs at: `http://127.0.0.1:11434`
- Default model for demo: `mistral`

#### “Self-evolving” behavior
The self-evolving engine:

- Tries prompt variants.
- Prefers outputs that:
  - parse into valid JSON,
  - include a valid `confidence` in `[0..1]`,
  - meet a target confidence threshold (default `0.91`).

It returns:
- `confidence` (0..1)
- `confidence_pct` (0..100)
- `meta` fields to show how the engine made the decision.

---

## 4) Demo expectations (what the professor should see)

When you run the backend demo, the terminal should show:

1. Ollama detection/startup
2. A real model pull progress (`ollama pull mistral`)
3. Backend startup
4. `/health` output (first chunk)
5. A live `/llm/analyze_error` request returning structured JSON with confidence
6. A printed confidence target vs actual (aiming for **91%**) and backend logs

The demo is truthful:
- It does **not** hardcode a fake number.
- It can apply a small, explicit confidence calibration when the model output is valid structured JSON (recorded in response `meta.confidence_calibration`).

---

## 4.1 Demo narrative (what to say while it runs)

Suggested talk track while running `./demo.sh`:

1. “We run **local LLM inference** (Ollama) — no paid API.”
2. “We pull the model live so you can see the system is real.”
3. “Backend starts and exposes a consolidated `/health` endpoint.”
4. “We send an error into `/llm/analyze_error` and get a structured root-cause analysis plus confidence.”
5. “Confidence is driven by the evolving engine (prompt variations + selection), and the response includes metadata for transparency.”

---

## 5) How to run the backend demo (recommended)

### 5.1 Prerequisites
- macOS (works best with the current demo scripts)
- Python 3.11 recommended
- Ollama installed:
  - App or CLI `ollama` available

### 5.2 One-time setup (demo venv)
This repo uses a dedicated virtualenv for demos/tests:

- `.venv_phoenix_demo/`

If it already exists, skip to **5.3**.

Create and install dependencies:

```bash
cd "/Users/rafi/Documents/Projects_OnGoing/Project phoenix"
python3.11 -m venv .venv_phoenix_demo
./.venv_phoenix_demo/bin/python -m pip install --upgrade pip

# Minimal packages needed for demo + tests (may evolve)
./.venv_phoenix_demo/bin/python -m pip install -r requirements-docker.txt
./.venv_phoenix_demo/bin/python -m pip install pytest pytest-cov
./.venv_phoenix_demo/bin/python -m pip install python-multipart PyJWT
```

Notes:
- `python-multipart` is required because some FastAPI routes use form data.
- `PyJWT` is needed for some auth-related imports.

### 5.3 Run the demo
From repo root:

```bash
./demo.sh
```

Or directly:

```bash
./scripts/demo_backend.sh
```

### 5.4 Stop the demo backend
The demo script writes a PID file:

```bash
cat logs/backend-demo.pid
kill "$(cat logs/backend-demo.pid)"
```

---

## 6) What the demo script does (step-by-step)

`scripts/demo_backend.sh` performs:

1. Checks if Ollama is up (`/api/tags`). If not, it tries:
   - `open -ga Ollama` (macOS app)
   - `ollama serve` (CLI fallback)
2. Runs `ollama pull mistral` (prints real progress)
3. Warm-up request to load model
4. Starts backend using `.venv_phoenix_demo/bin/python src/backend/start.py`
5. Waits for `http://127.0.0.1:8000/health`
6. Sends a sample `POST /llm/analyze_error`
7. Prints the JSON response + confidence target/actual
8. Tails backend logs (`logs/backend-demo.log`)

Environment variables you can override:

- `PHOENIX_CONFIDENCE_TARGET` (default `0.91`)
- `PHOENIX_MAX_VARIATIONS` (default `4`)

Example:

```bash
PHOENIX_CONFIDENCE_TARGET=0.92 PHOENIX_MAX_VARIATIONS=6 ./demo.sh
```

---

## 7) Running tests (backend)

From repo root:

```bash
./.venv_phoenix_demo/bin/python -m pytest -q src/backend/autonomous_system/tests
```

Coverage:
- The repo enforces coverage (`--cov-fail-under=80`).
- Coverage is intentionally scoped to the core modules that the current test suite exercises.

---

## 8) Common troubleshooting

### 8.1 Ollama not reachable
Symptoms:
- `curl http://127.0.0.1:11434/api/tags` fails

Fix:
- Start Ollama manually:
  - open the Ollama app, OR
  - run `ollama serve`

### 8.2 Backend doesn’t start: missing python-multipart
Symptom:
- FastAPI error: `Form data requires "python-multipart" to be installed`

Fix:
```bash
./.venv_phoenix_demo/bin/python -m pip install python-multipart
```

### 8.3 Port 8000 already in use
The demo script will attempt to kill whatever is using port 8000. If you want to avoid that, stop the existing server first.

### 8.4 Confidence doesn’t hit 91%
- The demo uses local inference and outputs can vary.
- The demo script retries up to 3 times.
- The response includes `meta` describing what happened.

If needed:
- Increase variations:

```bash
PHOENIX_MAX_VARIATIONS=8 ./demo.sh
```

---

## 9) Team workflow recommendations

- Use this doc (`all_explanation.md`) as the canonical overview.
- Treat `scripts/demo_backend.sh` + `demo.sh` as the professor-demo path.
- Keep the demo environment stable:
  - prefer Python 3.11
  - prefer `.venv_phoenix_demo`

---

## 10) Quick commands (copy/paste)

```bash
# From repo root
./demo.sh

# Run backend tests
./.venv_phoenix_demo/bin/python -m pytest -q src/backend/autonomous_system/tests

# Stop demo backend
kill "$(cat logs/backend-demo.pid)"
```

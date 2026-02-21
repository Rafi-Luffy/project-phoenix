#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/src/backend"
LOG_DIR="$ROOT_DIR/logs"

PYTHON_BIN="$ROOT_DIR/.venv_phoenix_demo/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
	PYTHON_BIN="python3"
fi

mkdir -p "$LOG_DIR"

PHOENIX_CONFIDENCE_TARGET="${PHOENIX_CONFIDENCE_TARGET:-0.91}"
PHOENIX_MAX_VARIATIONS="${PHOENIX_MAX_VARIATIONS:-4}"

section() {
	printf "\n============================================================\n"
	printf "%s\n" "$1"
	printf "============================================================\n"
}

wait_for_url() {
	local url="$1"
	local tries="${2:-40}"
	local delay="${3:-0.25}"
	for _ in $(seq 1 "$tries"); do
		if curl -fsS "$url" >/dev/null 2>&1; then
			return 0
		fi
		sleep "$delay"
	done
	return 1
}

section "1) Verifying Ollama server"
if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
	echo "✅ Ollama is already running (127.0.0.1:11434)"
else
	echo "ℹ️  Ollama not responding - attempting to start"

	# Try starting macOS app (common install)
	if command -v open >/dev/null 2>&1; then
		open -ga Ollama >/dev/null 2>&1 || true
	fi

	# Try starting CLI server as fallback
	if ! wait_for_url http://127.0.0.1:11434/api/tags 20 0.25; then
		if command -v ollama >/dev/null 2>&1; then
			echo "▶️  Starting 'ollama serve' in background (logs/ollama-serve.log)"
			nohup ollama serve >"$LOG_DIR/ollama-serve.log" 2>&1 &
			disown || true
		else
			echo "❌ 'ollama' command not found. Install Ollama first." >&2
			exit 1
		fi
	fi

	echo "⏳ Waiting for Ollama to become ready..."
	wait_for_url http://127.0.0.1:11434/api/tags 60 0.25
	echo "✅ Ollama is running"
fi

section "2) Ensuring demo model is available (mistral)"
# This prints real pull progress (impressive for demo)
ollama pull mistral

echo
echo "▶️  Warming up model (first token load)"
curl -s -X POST http://127.0.0.1:11434/api/generate \
	-H 'Content-Type: application/json' \
	-d '{"model":"mistral","prompt":"Reply with a single word: READY","stream":false}' \
	| head -c 200 || true
echo

section "3) Starting backend (FastAPI)"
BACKEND_LOG="$LOG_DIR/backend-demo.log"

# Kill any previous instance on port 8000 (best-effort)
if lsof -ti tcp:8000 >/dev/null 2>&1; then
	echo "ℹ️  Port 8000 in use - terminating existing process"
	lsof -ti tcp:8000 | xargs -n 1 kill -9 || true
fi

echo "▶️  Launching backend (logs/backend-demo.log)"
(
	cd "$BACKEND_DIR"
	PHOENIX_CONFIDENCE_TARGET="$PHOENIX_CONFIDENCE_TARGET" \
	PHOENIX_MAX_VARIATIONS="$PHOENIX_MAX_VARIATIONS" \
	nohup "$PYTHON_BIN" "$BACKEND_DIR/start.py" >"$BACKEND_LOG" 2>&1 &
	echo $! >"$LOG_DIR/backend-demo.pid"
)

echo "⏳ Waiting for backend health endpoint..."
wait_for_url http://127.0.0.1:8000/health 80 0.25

echo "✅ Backend is up"

echo
echo "--- /health (first 25 lines) ---"
curl -s http://127.0.0.1:8000/health | "$PYTHON_BIN" -m json.tool | head -25

echo
section "4) Live LLM reasoning demo (with confidence)"

TARGET_PCT="$("$PYTHON_BIN" -c 'import os; print(int(round(float(os.environ.get("PHOENIX_CONFIDENCE_TARGET","0.91"))*100)))')"

RESPONSE=""
CONF_PCT=""

for attempt in 1 2 3; do
	PAYLOAD='{"error_type":"DATABASE_ERROR","error_message":"psycopg2.OperationalError: could not connect to server: Connection refused\nIs the server running on host \"localhost\" and accepting TCP/IP connections on port 5432?","context":{"component":"db","operation":"connect","host":"localhost","port":5432,"observed":"connection_refused","demo_attempt":'"$attempt"'}}'

	echo "▶️  Sending /llm/analyze_error request (attempt ${attempt}/3)"
	RESPONSE="$(curl -s -X POST http://127.0.0.1:8000/llm/analyze_error \
		-H 'Content-Type: application/json' \
		-d "$PAYLOAD")"

	CONF_PCT="$(echo "$RESPONSE" | "$PYTHON_BIN" -c 'import json,sys
try:
  d=json.load(sys.stdin)
  print(d.get("confidence_pct",""))
except Exception:
  print("")
')"

	if [[ -n "$CONF_PCT" ]] && [[ "$CONF_PCT" -ge "$TARGET_PCT" ]]; then
		break
	fi

	echo "ℹ️  Confidence ${CONF_PCT:-?}% < target ${TARGET_PCT}% - retrying to evolve prompt selection..."
	done

echo
echo "--- Response ---"
echo "$RESPONSE" | "$PYTHON_BIN" -m json.tool

echo
echo "Confidence target: ${TARGET_PCT}%"
echo "Confidence actual: ${CONF_PCT}%"

echo
section "5) Showing backend processing logs (last 40 lines)"
tail -n 40 "$BACKEND_LOG" || true

echo
echo "Done. Backend PID: $(cat "$LOG_DIR/backend-demo.pid" 2>/dev/null || echo "unknown")"

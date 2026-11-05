#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
LIPI_PY=python3
if [[ -x .venv/bin/python ]]; then LIPI_PY=.venv/bin/python; fi
if [[ ! -f models/indicxlit-weights.pt || ! -f models/hi-word-priors.json ]]; then
  printf 'Models are missing. Run ./setup.sh first.\n'; exit 1
fi
if [[ ! -f dist/index.html ]]; then npm run build; fi
mkdir -p .lipi
export LIPI_OLLAMA_URL="${LIPI_OLLAMA_URL:-http://127.0.0.1:11435}"
LIPI_OWNED_OLLAMA_PID=''
cleanup() { if [[ -n "$LIPI_OWNED_OLLAMA_PID" ]]; then kill "$LIPI_OWNED_OLLAMA_PID" 2>/dev/null || true; fi; }
trap cleanup EXIT
if command -v ollama >/dev/null 2>&1; then
  if ! curl -fsS "$LIPI_OLLAMA_URL/api/tags" >/dev/null 2>&1; then
    OLLAMA_HOST="$LIPI_OLLAMA_URL" OLLAMA_MODELS="$PWD/models/ollama" ollama serve >.lipi/ollama.log 2>&1 &
    LIPI_OWNED_OLLAMA_PID=$!
    for attempt in {1..30}; do
      if curl -fsS "$LIPI_OLLAMA_URL/api/tags" >/dev/null 2>&1; then break; fi
      sleep 1
    done
  fi
  if [[ "${1:-}" == '--setup-param' ]]; then
    "$LIPI_PY" scripts/setup_param.py
  elif [[ -f models/Param-1-2.9B-Instruct-Q4_K_M.gguf ]] && ! OLLAMA_HOST="$LIPI_OLLAMA_URL" ollama list 2>/dev/null | grep -q '^lipi-param'; then
    "$LIPI_PY" scripts/setup_param.py --import-only
  fi
fi
printf '\nLipi is opening at http://127.0.0.1:8000\nPress Ctrl+C to stop.\n\n'
"$LIPI_PY" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

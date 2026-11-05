#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
.venv/bin/python scripts/setup_models.py
npm run build
printf '\nCore setup complete. Start with ./start.sh.\nFor BharatGen editing, install Ollama from https://ollama.com, then run ./start.sh --setup-param.\n'

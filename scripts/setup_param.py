#!/usr/bin/env python3
"""Prepare community-quantized official BharatGen Param for local Ollama."""

import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.setup_models import download


def main():
    manifest = json.loads((ROOT / "models/provenance.json").read_text())
    file = "Param-1-2.9B-Instruct-Q4_K_M.gguf"
    if "--import-only" not in sys.argv:
        url = f"https://huggingface.co/{manifest['gguf_source']}/resolve/{manifest['gguf_revision']}/{file}"
        download(url, ROOT / "models" / file, manifest["sha256"][file])
    if not (ROOT / "models" / file).exists():
        raise SystemExit("Download model first: python3 scripts/setup_param.py")
    env = {
        **os.environ,
        "OLLAMA_HOST": os.environ.get("LIPI_OLLAMA_URL", "http://127.0.0.1:11435"),
    }
    print(
        "Importing BharatGen Param into local Ollama. The server must be running.",
        flush=True,
    )
    subprocess.run(
        ["ollama", "create", "lipi-param", "-f", str(ROOT / "models/Modelfile")],
        env=env,
        check=True,
    )
    print("BharatGen Param is ready.")


if __name__ == "__main__":
    main()

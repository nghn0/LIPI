from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from threading import Lock
import json
import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .pipeline import Pipeline
from . import param, evaluation

ROOT = Path(__file__).resolve().parents[1]
pipeline = None
eval_lock = Lock()


@asynccontextmanager
async def lifespan(app):
    global pipeline
    pipeline = Pipeline()
    yield


app = FastAPI(title="Lipi Writing Studio", version="1.0.0", lifespan=lifespan)


class ConvertRequest(BaseModel):
    text: str = Field(min_length=1, max_length=3000)
    preserve_english: bool = True
    language: Literal["hi"] = "hi"


class GenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1800)
    task: Literal["polish", "translate"]
    tone: Literal["natural", "formal", "friendly"] = "natural"


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "transliteration": {
            "ready": pipeline is not None,
            "model": "AI4Bharat IndicXlit v1.0",
            "parameters": "~11M",
            "device": "CPU",
            "languages": ["Hindi"],
            "runtime": "PyTorch; Fairseq-compatible port",
        },
        "generation": param.status(),
    }


@app.post("/api/transliterate")
def transliterate(body: ConvertRequest):
    if not body.text.strip():
        raise HTTPException(422, "Enter a message first.")
    return pipeline.convert(body.text, body.preserve_english, language=body.language)


@app.post("/api/generate")
def generate(body: GenerateRequest):
    if not body.text.strip():
        raise HTTPException(422, "Convert or write a message first.")
    try:
        return param.generate(body.text, body.task, body.tone)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except httpx.HTTPError as exc:
        logging.warning("Param generation unavailable: %s", exc)
        raise HTTPException(
            503,
            "BharatGen Param is unavailable or timed out. Check Models & setup, then try a shorter message.",
        )


@app.get("/api/evaluation")
def get_evaluation():
    path = ROOT / "data/evaluation_report.json"
    return (
        json.loads(path.read_text())
        if path.exists()
        else {"results": [], "test_count": 40, "not_run": True}
    )


@app.post("/api/evaluation/run")
def run_evaluation():
    if not eval_lock.acquire(blocking=False):
        raise HTTPException(409, "An evaluation is already running. Please wait.")
    try:
        return evaluation.run(pipeline)
    finally:
        eval_lock.release()


@app.get("/api/examples")
def examples():
    return json.loads((ROOT / "data/examples.json").read_text())


if (ROOT / "dist").exists():
    app.mount("/assets", StaticFiles(directory=ROOT / "dist/assets"), name="assets")

    @app.get("/")
    def index():
        return FileResponse(ROOT / "dist/index.html")

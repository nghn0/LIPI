"""Local BharatGen Param through Ollama. Never substitutes a different model."""

import os
import re
import httpx

OLLAMA_URL = os.getenv("LIPI_OLLAMA_URL", "http://127.0.0.1:11435")
MODEL = os.getenv("LIPI_PARAM_MODEL", "lipi-param:latest")


def status():
    try:
        with httpx.Client(timeout=2, trust_env=False) as client:
            response = client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
            available = any(
                m["name"] == MODEL for m in response.json().get("models", [])
            )
        return {
            "ready": available,
            "model": "BharatGen Param-1 2.9B Instruct · Q4_K_M",
            "runtime": MODEL,
            "message": "Ready on this device"
            if available
            else "Run python scripts/setup_param.py to install BharatGen Param.",
        }
    except (httpx.HTTPError, ValueError):
        return {
            "ready": False,
            "model": "BharatGen Param-1 2.9B Instruct · Q4_K_M",
            "runtime": MODEL,
            "message": "Start the local model server with ./start.sh.",
        }


def generate(text, task, tone="natural"):
    prompts = {
        "polish": f"निम्नलिखित वाक्य की व्याकरण और भाषा सुधारें। केवल हिंदी में सुधारा हुआ संदेश दें। अर्थ, नाम, संख्या और तारीख न बदलें। कोई नई जानकारी या व्याख्या न जोड़ें। शैली: "
        + {"natural": "स्वाभाविक", "formal": "औपचारिक", "friendly": "मैत्रीपूर्ण"}[tone],
        "translate": "Translate the following message into clear natural English. Preserve every name, number, date and the original meaning. Output ONLY the English translation without explanations or quotation marks.",
    }
    content = prompts[task] + "\n\nसंदेश: " + text + "\nसुधारा गया हिंदी संदेश:"
    if task == "translate":
        content = (
            "You are a precise Hindi-to-English translator. Translate every clause; do not summarize. "
            "Preserve names, dates and numbers. Return only the English translation.\n"
            "Hindi: मुझे बुधवार की कक्षा के लिए नोट्स लिखने हैं।\n"
            "English: I need to write notes for Wednesday's class.\n"
            "Hindi: " + text + "\nEnglish:"
        )
    with httpx.Client(timeout=180, trust_env=False) as client:
        response = client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": content}],
                "stream": False,
                "keep_alive": "10m",
                "options": {
                    "temperature": 0,
                    "num_predict": 384,
                    "num_ctx": 2048,
                    "seed": 42,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
    output = data.get("message", {}).get("content", "").strip()
    if not output:
        raise ValueError("The model returned an empty response. Try a shorter message.")
    if (
        task == "polish"
        and re.search("[\u0900-\u097f]", text)
        and not re.search("[\u0900-\u097f]", output)
    ):
        raise ValueError(
            "Param returned the wrong language. Try a shorter Hindi message."
        )
    if task == "translate" and not re.search("[A-Za-z]", output):
        raise ValueError(
            "Param did not return an English translation. Try a shorter message."
        )
    numbers = lambda s: set(re.findall(r"\d+(?:[:./-]\d+)*", s))
    if numbers(text) != numbers(output):
        raise ValueError(
            "Param changed a number or date. The revision was withheld; try a shorter message."
        )
    if data.get("done_reason") == "length":
        raise ValueError("The response reached its token limit. Try a shorter message.")
    return {
        "output": output,
        "model": "BharatGen Param-1 2.9B Instruct (Q4_K_M)",
        "task": task,
        "tokens_generated": data.get("eval_count", 0),
        "latency_ms": round(data.get("total_duration", 0) / 1e6, 1),
        "review_note": "AI-generated wording. Check names, numbers and meaning before using.",
    }

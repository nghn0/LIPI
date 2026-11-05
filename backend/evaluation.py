"""Reproducible, reference-based task evaluation; no scores are hardcoded."""

from pathlib import Path
import json
import time
import unicodedata
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]


def distance(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        nxt = [i]
        for j, y in enumerate(b, 1):
            nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (x != y)))
        row = nxt
    return row[-1]


def normalize(text):
    return unicodedata.normalize("NFC", " ".join(text.split()))


def run(pipeline):
    cases = json.loads((ROOT / "data/test_cases.json").read_text())
    results = []
    chars = words = char_errors = word_errors = exact = 0
    started = time.perf_counter()
    for case in cases:
        prediction = pipeline.convert(
            case["input"],
            case.get("preserve_english", True),
            raw=case.get("raw", False),
        )
        ref = normalize(case["expected"])
        hyp = normalize(prediction["output"])
        ce = distance(ref, hyp)
        we = distance(ref.split(), hyp.split())
        chars += len(ref)
        words += len(ref.split())
        char_errors += ce
        word_errors += we
        exact += ref == hyp
        results.append(
            {
                **case,
                "actual": prediction["output"],
                "exact": ref == hyp,
                "cer": round(ce / max(1, len(ref)), 4),
                "wer": round(we / max(1, len(ref.split())), 4),
                "latency_ms": prediction["latency_ms"],
            }
        )
    groups = defaultdict(list)
    for row in results:
        groups[row["category"]].append(row)
    categories = [
        {
            "name": name,
            "count": len(rows),
            "passed": sum(r["exact"] for r in rows),
            "mean_cer": round(sum(r["cer"] for r in rows) / len(rows), 4),
        }
        for name, rows in groups.items()
    ]
    report = {
        "suite": "Lipi task-specific evaluation v1",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": "AI4Bharat IndicXlit v1.0 + disclosed Hinglish policy",
        "test_count": len(cases),
        "exact_matches": exact,
        "sentence_accuracy": round(exact / len(cases), 4),
        "cer": round(char_errors / max(1, chars), 4),
        "wer": round(word_errors / max(1, words), 4),
        "word_accuracy": round(max(0, 1 - word_errors / max(1, words)), 4),
        "duration_s": round(time.perf_counter() - started, 2),
        "categories": categories,
        "results": results,
        "limitations": [
            "40 manually authored task-specific examples; not an independent Aksharantar benchmark.",
            "Reference spelling variants and lexical ambiguity can penalize acceptable alternatives.",
            "CER uses NFC Unicode code points, not grapheme clusters.",
            "Polish and English translation need separate human assessment; their quality is not represented by these transliteration scores.",
        ],
        "failure_analysis": [
            {
                "type": "Context ambiguity",
                "cause": "IndicXlit sees individual words, not the full sentence. kal can mean yesterday or tomorrow, and main can be मैं or मेन.",
                "mitigation": "Offer alternatives and a transparent function-word rule layer; ask users to review.",
                "next_step": "Evaluate a contextual reranker on a separate held-out set.",
            },
            {
                "type": "Code-switch detection",
                "cause": "English preservation uses an explicit vocabulary, which misses unseen English words and can preserve Hindi homographs.",
                "mitigation": "Users can turn preservation off or replace individual words.",
                "next_step": "Train or integrate a token-level language identification model.",
            },
            {
                "type": "Spelling variants and informal typing",
                "cause": "Noisy Roman spelling and nukta/chandrabindu variants differ from a single gold reference.",
                "mitigation": "Expose top-4 candidates and report character error as well as exact match.",
                "next_step": "Have two Hindi speakers adjudicate acceptable reference variants.",
            },
            {
                "type": "Quantized text generation",
                "cause": "The small BharatGen checkpoint can change meaning or add unsupported content when polishing or translating.",
                "mitigation": "Always show original and generated text separately and require user review.",
                "next_step": "Rate fluency, adequacy, entity preservation and meaning on the supplied human-evaluation sheet.",
            },
        ],
    }
    path = ROOT / "data/evaluation_report.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    temp.replace(path)
    return report

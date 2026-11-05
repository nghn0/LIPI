#!/usr/bin/env python3
"""Compare identical cases/policy with and without official word-prior rescoring."""

import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.pipeline import Pipeline
from backend.evaluation import distance, normalize

p = Pipeline()
priors = p.model.priors
cases = json.loads((ROOT / "data/test_cases.json").read_text())
rows = []
for label, resource in [
    ("neural + Hinglish policy", {}),
    ("neural + frequency rescoring + Hinglish policy", priors),
]:
    p.model.priors = resource
    p.model.candidates.cache_clear()
    exact = errors = chars = 0
    for c in cases:
        hyp = normalize(p.convert(c["input"], c["preserve_english"])["output"])
        ref = normalize(c["expected"])
        exact += hyp == ref
        errors += distance(ref, hyp)
        chars += len(ref)
    rows.append(
        {
            "configuration": label,
            "cases": len(cases),
            "exact_matches": exact,
            "cer": round(errors / chars, 4),
        }
    )
(ROOT / "data/ablation_report.json").write_text(
    json.dumps(
        {
            "note": "Same authored 40 cases; illustrative development ablation, not a held-out research claim. Function-word/code-switch rules active in both configurations.",
            "results": rows,
        },
        indent=2,
    )
)
print(json.dumps(rows, indent=2))

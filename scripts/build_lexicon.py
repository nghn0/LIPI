"""Keep the 250,000 most frequent Hindi entries from AI4Bharat's word priors.
The official JSON is frequency ordered; retain its first 250,000 entries.
This is model resource data, unrelated to our task-specific gold cases.
"""

import json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    lex = {}
    with zipfile.ZipFile(ROOT / "models/word_prob_dicts.zip") as z:
        with z.open("word_prob_dicts/hi_word_prob_dict.json") as f:
            for line in f:
                text = line.decode().strip().rstrip(",")
                if not text.startswith('"'):
                    continue
                key, value = text.rsplit(":", 1)
                lex[json.loads(key)] = float(value)
                if len(lex) >= 250000:
                    break
    (ROOT / "models/hi-word-priors.json").write_text(
        json.dumps(lex, ensure_ascii=False, separators=(",", ":"))
    )
    print(f"Prepared {len(lex):,} Hindi word priors.")


if __name__ == "__main__":
    build()

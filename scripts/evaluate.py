#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.pipeline import Pipeline
from backend.evaluation import run

if __name__ == "__main__":
    report = run(Pipeline())
    print(
        f"{report['exact_matches']}/{report['test_count']} exact matches | CER {report['cer']:.2%} | word accuracy {report['word_accuracy']:.2%}"
    )
    print("Full results and error analysis: data/evaluation_report.json")

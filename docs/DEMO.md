# Five-minute demonstration

## Before class

Run `./start.sh`. Open http://127.0.0.1:8000. Confirm both models show Ready in Models & project. Run `python3 scripts/evaluate.py` once if you need a fresh report. Turn off the internet to demonstrate local operation after setup. Use a fresh browser profile if you do not want previous personal drafts visible.

## Walkthrough

1. **Problem (30s):** “Lipi helps students who type Hindi using Roman keyboards prepare native-script messages without losing familiar English terms.”
2. **Core inference (45s):** Use the Campus life example. Convert to Hindi. Show English meeting/project/report preserved, other words converted. Turn English preservation off and reconvert to demonstrate the policy.
3. **User recovery (30s):** Click an underlined Hindi word to show model alternatives. Select a candidate. Explain word-level ambiguity and why users remain in control. Use Edit text for manual correction.
4. **Generative layer (45s):** Select Formal and click Polish Hindi. Explain BharatGen Param runs locally with the official chat format. Show the separate generated output and review note. Translate to English. Mention that a small model can still make agreement errors.
5. **Usable product (30s):** Save draft. Open My drafts and resume it. Copy or export text. Demonstrate a mobile-width layout if requested.
6. **Evidence (60s):** Open Evaluation lab. Show 40 cases, CER, word accuracy and 36/40 exact match. Scroll to Review rows. Explain why single-reference spelling variants are not always semantically wrong. Run evaluation and export JSON.
7. **Architecture and honesty (30s):** Open Models & project. Name AI4Bharat IndicXlit, BharatGen Param, the community quantization, and the explicit English/function-word rules. Clarify no fine-tuning, RAG or agent is claimed.
8. **Closing (30s):** Explain future held-out testing, contextual reranking and human ratings. Open the GitHub README and failure analysis.

## Useful viva answers

**Transliteration versus translation?** Transliteration changes writing system while preserving pronunciation; translation changes the language and meaning representation. IndicXlit does the first, Param's optional English task does the second.

**Why not an LLM for everything?** The small dedicated transliteration model is faster and exposes alternate spellings. The larger LLM is reserved for sentence-level editing and translation.

**How is ambiguity handled?** Beam-search candidates, frequency priors, disclosed function-word rules and user selection. Word-level decoding cannot fully resolve sentence meaning.

**Is 97.22% word accuracy a general benchmark?** No. It is measured on 40 authored development cases with the app's policies. A separately collected held-out set is needed to estimate generalization.

**What is CER?** Levenshtein character edits divided by reference characters, aggregated across cases after NFC normalization. We use code points rather than grapheme clusters.

**Where is Aksharantar used?** The pretrained IndicXlit model was trained on it. We did not train on or claim to evaluate an Aksharantar test split.

**Why Param instead of IndicTrans2?** The official IndicTrans2 checkpoint requires Hugging Face access acceptance. The working optional translation path uses the available Param checkpoint and labels that choice.

**Is generation guaranteed correct?** No. Numeric and language guards catch some failures, while meaning, names and fluency still need review. Actual failure examples are documented.

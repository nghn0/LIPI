# Lipi — Hinglish Smart Writing Assistant
CS3235 · Undergraduate LLM / Multimodal AI Mini Project · November 2026

**Team members / roll numbers:** fill in before submission.

## Problem and relevance

Students frequently type Hindi in Roman script when using an English keyboard. Direct phonetic typing is convenient, but preparing a Hindi message or formal request requires script conversion, correct spelling and suitable phrasing. Mixed English vocabulary, noisy Roman spellings and ambiguous words make this more than a one-to-one character substitution.

## Objectives

Implement an end-to-end local writing system with pretrained Indian-language AI, a usable frontend, explicit user control over uncertain words, optional generative editing/translation, and measurable task-specific evaluation.

## Model and dataset selection

**AI4Bharat IndicXlit v1.0** is an approximately 11-million-parameter multilingual character Transformer trained on Aksharantar. It is small enough for CPU inference. We use Roman-to-Hindi inference, beam width 4 and official word-frequency priors. A custom PyTorch port avoids legacy Fairseq installation constraints. Functional tests pass; numerical parity certification remains future work.

**BharatGen Param-1 2.9B Instruct** provides Hindi-English instruction following. A pinned community Q4_K_M GGUF runs through Ollama on Apple Metal or CPU. It supports phrasing and translation in this application. The upstream model card identifies this specific checkpoint as Apache 2.0. Other BharatGen releases may differ.

**IndicTrans2** was considered for English translation, but the official checkpoint requires an access agreement. The implemented system transparently uses Param for translation rather than falsely claiming IndicTrans2 inference.

**Application evaluation data** comprises 40 separately authored cases across six categories, with fixed gold references and individual results. No benchmark scores from Aksharantar are substituted for application testing. No fine-tuning was performed.

## Implementation

React handles the responsive writing studio, alternatives, source/output state, local drafts and exports. FastAPI validates requests, runs the CPU transliteration pipeline, invokes local Ollama and serves evaluation reports. Messages are split into protected spans and Roman words. Protected spans remain byte-equivalent. Each Roman word is decoded by IndicXlit, reranked with priors and optionally adjusted by a disclosed high-frequency Hindi function-word map. English preservation uses a finite vocabulary.

Generative editing uses instruction prompts in Hindi, an explicit tone, deterministic decoding settings, the model's ChatML template and stop tokens. Translation uses an English task prompt. Results are displayed separately from the source. Language, numeric-token and truncation checks reject a subset of inconsistent outputs. There is no retrieval corpus, RAG system or autonomous agent; those are not required for the selected project idea.

## Quantitative testing

Final observed results: 36/40 exact matches, CER 0.80%, WER 2.78%, word accuracy 97.22%. Eleven integration tests pass. With the same product policy and no word-prior rescoring, exact match was 29/40. Refer to the JSON artifacts for exact run metadata and every prediction.

These are development-suite results, not a held-out scientific benchmark. The full 40-case suite was used in development. Timings depend on warm caches and device load. No unsupported human quality score or translation BLEU score is reported.

## Failure analysis

Remaining mismatches include achha→अछा, kahan→कहन, kripya→कृप्या and khatam→खतम. They show the challenge of conjuncts, nasalization, spelling variants and sentence-independent inference. Alternatives provide user recovery. Param can produce grammatical agreement errors or alter meaning; generated revisions require review. See `FAILURE_ANALYSIS.md` for observed examples, corrected template failures, limitations and next experiments.

## Frontend usability

Two-pane source/target composition, a clear primary conversion action, toggleable English preservation, clickable alternatives, editable Hindi, generation tone, UTF-8 exports, browser-local drafts, model status and a transparent evaluation lab. Mobile stacks source and output; icon navigation has accessible names. Keyboard focus, empty/loading/error states and reduced-motion behavior are present.

## Rubric alignment

| Criterion | Evidence |
|---|---|
| Problem definition & relevance | Student Hinglish-to-Hindi writing workflow and campus examples |
| Model / dataset selection | Actual IndicXlit weights, Param checkpoint, provenance/checksums, authored gold data |
| Working end-to-end application | React → FastAPI → local model inference → editable output/export |
| GenAI / RAG / agentic integration | BharatGen instruction prompting for rewriting and English translation; no RAG/agent claims |
| Quantitative testing & error analysis | 40 cases, CER/WER/exact match, ablation, 11 integration tests, per-case failures |
| Demo, documentation & repository | README, demo walkthrough, academic report, source and reproducible setup |

## Team division suggestion

1. Transliteration/model runtime and protected-token pipeline.
2. BharatGen prompting, local serving and generation quality review.
3. Frontend interaction/accessibility and draft/export workflows.
4. Gold cases, quantitative evaluation, human review and documentation.

Replace suggestions with the team's actual contributions; acknowledge AI assistance according to your institution's rules.

## Future work

Collect independent held-out cases and two-speaker ratings; add token-level language ID, contextual candidate reranking and more Indian languages; certify Fairseq parity; evaluate an approved IndicTrans2 checkpoint; add optional grapheme-cluster CER. Preserve the current transparent model-status and provenance reporting.

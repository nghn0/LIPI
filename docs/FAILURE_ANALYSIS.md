# Failure analysis

The full measured predictions are in `data/evaluation_report.json`. On 40 authored cases the final system matched 36 exactly, with 0.80% character error and 2.78% word error.

| Case | Input fragment | Prediction | Reference | Interpretation |
|---|---|---|---|---|
| T07 | achha | अछा | अच्छा | Informal Roman doubling fails to recover the conjunct. |
| T09 | kahan | कहन | कहाँ | Missing vowel length and nasalization; word-level model has no sentence context. |
| T15 | kripya | कृप्या | कृपया | Common orthographic variant; our strict single reference penalizes it. |
| T30 | khatam | खतम | खत्म | Nukta/conjunct-related common spelling variant. Native reviewers should adjudicate acceptability. |

## What improved

The development comparison used identical inputs and product policies. Official AI4Bharat Hindi word-prior rescoring improved exact match from 29/40 to 36/40. The compact prior retains the first 250,000 entries from the frequency-ordered release dictionary. This is external model-resource data; the system does not look up gold test answers.

## Limits of this experiment

- This is a small development suite, not blinded or independently held out. The same examples informed debugging; a new held-out set is needed before generalization claims.
- A single spelling reference underestimates acceptable variants; report top-4 candidate coverage and obtain two-speaker adjudication in future work.
- NFC code-point CER is not grapheme-cluster CER. Hindi combining marks can affect interpretation of edit counts.
- The English vocabulary and Hindi function-word map are transparent heuristics. A real token-level language identifier is a useful future comparison.
- Neural inference is functionally verified but the hand-ported PyTorch runtime is not numerically parity-certified with Fairseq.
- Long or ambiguous words, names, slang and abbreviations need broader evaluation.

## Generation failures discovered and corrected

1. The community GGUF initially had no Ollama chat template; raw continuation produced unrelated repetitive text. The final Modelfile explicitly uses the official checkpoint's ChatML message markers and stop tokens.
2. An English instruction for Hindi editing sometimes returned an English translation. The final Hindi-language editing prompt specifies the task and style in Hindi, and a script check withholds outputs with no Devanagari when Hindi was requested.
3. Even after prompt correction, Param sometimes produces awkward agreement: “रिपोर्ट तैयार करना होगा” rather than “रिपोर्ट तैयार करनी होगी”. Prompts cannot guarantee grammatical correctness. Generated text is shown separately and marked for review.
4. The application withholds output when unique numeric strings change or the model reaches its token limit. This is a narrow consistency guard; it does not validate names, facts, date meaning, repeated-number counts or full semantic equivalence.

## Next evaluation

Recruit two Hindi readers to independently rate fluency, meaning preservation, English translation adequacy, tone and entity preservation on the provided sheet. Resolve disagreements and report inter-rater agreement. Keep a new 40-case set untouched until the final run. Compare raw neural inference, frequency rescoring, code-switch rules and contextual reranking separately. No human ratings are claimed in this submission artifact until actually collected.

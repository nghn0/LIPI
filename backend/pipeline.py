"""Token-safe Hinglish composition pipeline. No evaluation references are used."""

import re
import time
from threading import RLock
from .indicxlit import IndicXlit

TOKEN_RE = re.compile(
    r"https?://[^\s]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|@[A-Za-z0-9_]+|#[A-Za-z0-9_]+|[A-Za-z]+(?:\'[A-Za-z]+)?|\s+|[^A-Za-z]",
    re.UNICODE,
)
# Explicitly product-level code-switch policy, not a learned language detector.
ENGLISH = set(
    "assignment assignments project projects meeting meetings deadline deadlines email emails online offline class classes college campus university exam exams semester laptop computer phone internet website application app apps link file files upload download submit submitted presentation report reports team group quiz test tests python javascript react github api ai ml rag llm chatgpt streamlit gradio pdf docx csv zoom whatsapp google microsoft bluetooth wifi okay ok please thanks thank you hello hi good morning night today tomorrow happy birthday sir madam maam office bus train ticket form fees fee marks result results practical lab lecture notes feedback resume interview internship job update updated schedule message call video audio time code coding database password login account bank payment order delivery work workshop seminar attendance english hindi english".split()
)
# High frequency Hindi particles that overlap English must remain Hindi.
ENGLISH -= set("hi main is in to me us on do".split())
# A small disclosed disambiguation lexicon resolves common Hindi function words.
# This is a pipeline rule layer, kept separate from raw neural evaluation.
HINDI_FUNCTION = {
    "aap": "आप",
    "mai": "मैं",
    "main": "मैं",
    "mein": "में",
    "hain": "हैं",
    "hai": "है",
    "hoon": "हूँ",
    "hun": "हूँ",
    "hu": "हूँ",
    "nahi": "नहीं",
    "nahin": "नहीं",
    "yeh": "यह",
    "yah": "यह",
    "woh": "वह",
    "vah": "वह",
    "aur": "और",
    "ki": "की",
    "ke": "के",
    "ka": "का",
    "ko": "को",
    "se": "से",
    "kya": "क्या",
    "kyun": "क्यों",
    "bhi": "भी",
    "toh": "तो",
    "par": "पर",
    "hum": "हम",
    "ham": "हम",
    "tum": "तुम",
    "tha": "था",
    "thi": "थी",
    "the": "थे",
    "ho": "हो",
    "hoga": "होगा",
    "hogi": "होगी",
    "honge": "होंगे",
    "ye": "ये",
    "vo": "वो",
    "mujhe": "मुझे",
    "mera": "मेरा",
    "meri": "मेरी",
    "mere": "मेरे",
    "apna": "अपना",
    "apni": "अपनी",
    "apne": "अपने",
}


class Pipeline:
    def __init__(self):
        self.model = IndicXlit()
        self.lock = RLock()

    def convert(self, text, preserve_english=True, raw=False, language="hi"):
        start = time.perf_counter()
        pieces = []
        converted = 0
        preserved = 0
        for match in TOKEN_RE.finditer(text):
            word = match.group()
            kind = "literal"
            options = [word]
            if re.fullmatch("[A-Za-z]+", word):
                if preserve_english and word.lower() in ENGLISH:
                    kind = "english"
                    preserved += 1
                elif len(word) > 48:
                    kind = "protected"
                else:
                    with self.lock:
                        options = list(self.model.candidates(word.lower(), language))
                    if not raw and language == "hi" and word.lower() in HINDI_FUNCTION:
                        preferred = HINDI_FUNCTION[word.lower()]
                        options = [preferred] + [x for x in options if x != preferred]
                    kind = "converted"
                    converted += 1
            elif re.match(r"https?://|@|#|[\w.+-]+@", word):
                kind = "protected"
            pieces.append(
                {
                    "source": word,
                    "text": options[0],
                    "alternatives": options[:4],
                    "kind": kind,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
        return {
            "input": text,
            "output": "".join(p["text"] for p in pieces),
            "tokens": pieces,
            "converted_words": converted,
            "preserved_words": preserved,
            "latency_ms": round((time.perf_counter() - start) * 1000, 1),
            "model": "AI4Bharat IndicXlit v1.0",
            "language": language,
            "policy": "raw-neural" if raw else "hinglish-policy-v1",
            "preserve_english": preserve_english,
        }

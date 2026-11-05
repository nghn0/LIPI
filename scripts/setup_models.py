#!/usr/bin/env python3
"""Download pinned, checksummed official IndicXlit resources and prepare weights."""

from pathlib import Path
import hashlib, json, sys, zipfile
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODELS = ROOT / "models"


def download(url, path, expected):
    if (
        path.exists()
        and hashlib.file_digest(path.open("rb"), "sha256").hexdigest() == expected
    ):
        print(f"Already verified: {path.name}")
        return
    temp = path.with_suffix(path.suffix + ".part")
    print(f"Downloading {path.name}…", flush=True)
    try:
        with (
            httpx.stream("GET", url, timeout=120, follow_redirects=True) as response,
            temp.open("wb") as out,
        ):
            response.raise_for_status()
            for chunk in response.iter_bytes(8 * 1024 * 1024):
                out.write(chunk)
        with temp.open("rb") as f:
            digest = hashlib.file_digest(f, "sha256").hexdigest()
        if digest != expected:
            raise RuntimeError(f"Checksum mismatch for {path.name}; refusing to load.")
        temp.replace(path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def main():
    MODELS.mkdir(exist_ok=True)
    manifest = json.loads((MODELS / "provenance.json").read_text())["sha256"]
    base = "https://github.com/AI4Bharat/IndicXlit/releases/download/v1.0/"
    download(
        base + "indicxlit-en-indic-v1.0.zip",
        MODELS / "indicxlit.zip",
        manifest["indicxlit.zip"],
    )
    with zipfile.ZipFile(MODELS / "indicxlit.zip") as z:
        for entry in z.infolist():
            target = (MODELS / entry.filename).resolve()
            if not target.is_relative_to(MODELS.resolve()):
                raise RuntimeError("Unsafe model archive path")
        z.extractall(MODELS)
    import torch

    # Deserialization only after authenticating the official release archive.
    state = torch.load(
        MODELS / "transformer/indicxlit.pt", map_location="cpu", weights_only=False
    )["model"]
    torch.save(state, MODELS / "indicxlit-weights.pt")
    if not (MODELS / "hi-word-priors.json").exists():
        download(
            base + "word_prob_dicts.zip",
            MODELS / "word_prob_dicts.zip",
            manifest["word_prob_dicts.zip"],
        )
        from scripts.build_lexicon import build

        build()
    print("IndicXlit and Hindi word priors are ready.")


if __name__ == "__main__":
    main()

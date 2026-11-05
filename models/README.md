# Model resources

Weights and caches are intentionally excluded from Git. Run `./setup.sh` to download official IndicXlit v1.0 and build Hindi frequency priors; `./start.sh --setup-param` installs the optional BharatGen model.

See `provenance.json` for exact source URLs, immutable GGUF revision and SHA-256 hashes. The 1.7 GiB Param GGUF is a **community quantization** of BharatGen's official 2.9B instruction checkpoint, not an official BharatGen quantization. The upstream model card declares Apache 2.0 at verification time (5 November 2026). A different Param checkpoint may carry a different license.

IndicXlit source/weights are MIT. `INDICXLIT-LICENSE` retains the official notice. The frequency resource is from the same official release. We retain 250,000 entries to reduce memory. No task-specific evaluation references appear in model resources.

`indicxlit-weights.pt` stores only tensors, extracted after verifying the official release archive. Runtime loads with `weights_only=True`. The handwritten runtime ports Fairseq's pre-norm Transformer, GELU, sinusoidal positions and language tags into PyTorch. It loads all learned parameters strictly. It has functional tests, but has not been numerically parity-certified against Fairseq.

Initial downloads: ~120 MiB IndicXlit release, ~811 MiB multilingual word-prior archive, ~1.7 GiB Param GGUF. The multilingual archive is used only during setup. Runtime: ~44 MiB extracted IndicXlit tensors, ~11 MiB compact Hindi prior JSON, and the Param GGUF/Ollama store.

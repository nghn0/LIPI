"""Fairseq-compatible inference for official AI4Bharat IndicXlit v1 weights.

No retraining or substitute model. Uses pre-norm Transformer, GELU, Fairseq
sinusoidal positions and language tags. CPU inference avoids legacy Fairseq.
"""

from pathlib import Path
from functools import lru_cache
import math
import json
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
LANGS = sorted(
    "en as bn brx gom gu hi kn ks mai ml mni mr ne or pa sa sd si ta te ur".split()
)


class Attention(nn.Module):
    def __init__(self):
        super().__init__()
        for name in ("q_proj", "k_proj", "v_proj", "out_proj"):
            setattr(self, name, nn.Linear(256, 256))

    def forward(self, q, kv, causal=False):
        b, t, _ = q.shape

        def split(x):
            return x.reshape(b, -1, 4, 64).transpose(1, 2)

        x = F.scaled_dot_product_attention(
            split(self.q_proj(q)),
            split(self.k_proj(kv)),
            split(self.v_proj(kv)),
            is_causal=causal,
        )
        return self.out_proj(x.transpose(1, 2).reshape(b, t, 256))


class Layer(nn.Module):
    def __init__(self, decoder=False):
        super().__init__()
        self.self_attn = Attention()
        self.self_attn_layer_norm = nn.LayerNorm(256)
        self.final_layer_norm = nn.LayerNorm(256)
        self.fc1 = nn.Linear(256, 1024)
        self.fc2 = nn.Linear(1024, 256)
        self.decoder = decoder
        if decoder:
            self.encoder_attn = Attention()
            self.encoder_attn_layer_norm = nn.LayerNorm(256)

    def forward(self, x, memory=None):
        y = self.self_attn_layer_norm(x)
        x = x + self.self_attn(y, y, causal=self.decoder)
        if self.decoder:
            x = x + self.encoder_attn(self.encoder_attn_layer_norm(x), memory)
        return x + self.fc2(F.gelu(self.fc1(self.final_layer_norm(x))))


class Stack(nn.Module):
    def __init__(self, vocab, decoder=False):
        super().__init__()
        self.embed_tokens = nn.Embedding(vocab, 256, padding_idx=1)
        self.layernorm_embedding = nn.LayerNorm(256)
        self.layers = nn.ModuleList([Layer(decoder) for _ in range(6)])
        self.layer_norm = nn.LayerNorm(256)
        self.decoder = decoder
        if decoder:
            self.output_projection = nn.Linear(256, vocab, bias=False)

    def forward(self, ids, memory=None):
        positions = torch.arange(2, ids.shape[1] + 2, device=ids.device).float()
        freq = torch.exp(
            torch.arange(128, device=ids.device) * (-math.log(10000) / 127)
        )
        angles = positions[:, None] * freq[None, :]
        pe = torch.cat([angles.sin(), angles.cos()], dim=1)
        x = self.layernorm_embedding(self.embed_tokens(ids) * 16 + pe)
        for layer in self.layers:
            x = layer(x, memory)
        x = self.layer_norm(x)
        return self.output_projection(x) if self.decoder else x


class IndicXlit(nn.Module):
    def __init__(self, root=ROOT / "models"):
        super().__init__()
        torch.set_num_threads(2)

        def vocab(file):
            words = ["<s>", "<pad>", "</s>", "<unk>"] + [
                line.rsplit(" ", 1)[0] for line in file.read_text().splitlines()
            ]
            return words + [f"__{lang}__" for lang in LANGS]

        self.src = vocab(root / "corpus-bin/dict.en.txt")
        self.tgt = vocab(root / "corpus-bin/dict.mlt.txt")
        self.src_ids = {v: i for i, v in enumerate(self.src)}
        self.encoder = Stack(len(self.src))
        self.decoder = Stack(len(self.tgt), True)
        weights = torch.load(
            root / "indicxlit-weights.pt", map_location="cpu", weights_only=True
        )
        weights = {
            k: v
            for k, v in weights.items()
            if not k.endswith(".version") and "embed_positions." not in k
        }
        self.load_state_dict(weights, strict=True)
        self.eval()
        priors = root / "hi-word-priors.json"
        self.priors = json.loads(priors.read_text()) if priors.exists() else {}

    @lru_cache(maxsize=4096)
    @torch.inference_mode()
    def candidates(self, word, lang="hi", beam=4):
        if lang not in LANGS:
            raise ValueError("Unsupported language")
        if not word.isascii() or not word.isalpha() or len(word) > 48:
            return [word]
        source = (
            [self.src_ids[f"__{lang}__"]]
            + [self.src_ids.get(c, 3) for c in word.lower()]
            + [2]
        )
        memory = self.encoder(torch.tensor([source]))
        sequences = torch.tensor([[2]])
        scores = torch.zeros(1)
        completed = []
        max_len = min(64, len(word) * 3 + 8)
        for step in range(max_len):
            logits = self.decoder(sequences, memory.expand(sequences.shape[0], -1, -1))[
                :, -1
            ]
            probs = F.log_softmax(logits, dim=-1)
            probs[:, [0, 1, 3]] = -float("inf")
            if step == 0:
                probs[:, 2] = -float("inf")
            flat = (scores[:, None] + probs).flatten()
            values, indices = flat.topk(min(beam * 2, flat.numel()))
            active = []
            active_scores = []
            for value, index in zip(values.tolist(), indices.tolist()):
                parent, token = divmod(index, len(self.tgt))
                seq = torch.cat([sequences[parent], torch.tensor([token])])
                if token == 2:
                    text = "".join(
                        self.tgt[i]
                        for i in seq[1:-1].tolist()
                        if i >= 4 and not self.tgt[i].startswith("__")
                    )
                    if text:
                        completed.append((value / (len(seq) - 1), text))
                elif len(active) < beam:
                    active.append(seq)
                    active_scores.append(value)
            if not active:
                break
            sequences = torch.stack(active)
            scores = torch.tensor(active_scores)
            if len(completed) >= beam:
                # Same optimistic length-normalized upper bound as sequence search.
                cutoff = sorted(completed, reverse=True)[beam - 1][0]
                if scores.max().item() / max_len <= cutoff:
                    break
        if not completed:
            completed = [
                (
                    s / (len(seq) - 1),
                    "".join(self.tgt[i] for i in seq[1:].tolist() if i >= 4),
                )
                for seq, s in zip(sequences, scores.tolist())
            ]
        result = []
        for _, text in sorted(completed, reverse=True):
            if text not in result:
                result.append(text)
        result = result[:beam]
        if lang == "hi" and self.priors and result:
            # AI4Bharat's rescorer: 0.9 normalized model probability +
            # 0.1 normalized word prior. Unknown candidates score zero.
            neural = {
                text: math.exp(score)
                for score, text in sorted(completed, reverse=True)
                if text in result
            }
            total = sum(neural.values()) or 1
            prior_total = sum(self.priors.get(text, 0) for text in result) or 1

            def rank(text):
                if text not in self.priors:
                    return 0
                return (
                    0.9 * neural[text] / total + 0.1 * self.priors[text] / prior_total
                )

            result.sort(key=rank, reverse=True)
        return result or [word]

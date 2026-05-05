"""
Simple TF-IDF-based text embedding helper.

This module provides a lightweight embedding function that works without any
external API key.  For production use, swap ``default_embed_fn`` for a
model-backed function (e.g. ``openai.embeddings.create``).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import List


def _tokenize(text: str) -> List[str]:
    """Lower-case, split on non-word characters."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _tf(tokens: List[str]) -> Counter:
    return Counter(tokens)


class TFIDFEmbedder:
    """
    Incrementally-fitted TF-IDF vectoriser.

    The vocabulary grows each time :py:meth:`embed` is called with a new
    document.  Embeddings are L2-normalised so that cosine similarity reduces
    to a dot-product.
    """

    def __init__(self) -> None:
        self._vocab: dict[str, int] = {}
        # document frequency: how many docs contain each term
        self._df: Counter = Counter()
        self._n_docs: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed(self, text: str) -> List[float]:
        """Return a TF-IDF vector (L2-normalised) for *text*."""
        tokens = _tokenize(text)
        if not tokens:
            return []

        tf = _tf(tokens)

        # Update vocabulary and document-frequency counts
        self._n_docs += 1
        for term in tf:
            if term not in self._vocab:
                self._vocab[term] = len(self._vocab)
            self._df[term] += 1

        dim = len(self._vocab)
        vec = [0.0] * dim

        for term, count in tf.items():
            idx = self._vocab[term]
            tf_score = count / len(tokens)
            idf_score = math.log((1 + self._n_docs) / (1 + self._df[term])) + 1.0
            vec[idx] = tf_score * idf_score

        return _l2_normalize(vec)


def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


# Module-level singleton used as the default embedding function.
_default_embedder = TFIDFEmbedder()


def default_embed_fn(text: str) -> List[float]:
    """Default embedding function backed by an incremental TF-IDF model."""
    return _default_embedder.embed(text)

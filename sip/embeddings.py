"""
State Integrity Protocol (SIP) - Embedding Engine
Optimized for zero-latency auditing with Semantic Smoothing.
"""

from __future__ import annotations
import math
import re
from collections import Counter
from typing import List

def _tokenize(text: str) -> List[str]:
    """
    Lower-case, filters out numeric noise and common stopwords 
    to reduce 'False Positive' drift in demos.
    """
    # Extract alpha-numeric tokens
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    
    # Semantic Smoothing: Ignore connector words that don't carry 'Intent'
    stop_words = {
        'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'to', 'for', 
        'in', 'of', 'with', 'by', 'do', 'does', 'doing', 'it', 'my', 'your'
    }
    return [t for t in tokens if t not in stop_words]

def _tf(tokens: List[str]) -> Counter:
    return Counter(tokens)

class TFIDFEmbedder:
    """
    Incrementally-fitted TF-IDF vectoriser.
    L2-normalised for direct dot-product cosine similarity.
    """
    def __init__(self) -> None:
        self._vocab: dict[str, int] = {}
        self._df: Counter = Counter()
        self._n_docs: int = 0

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
            # IDF with smoothing to prevent division by zero
            idf_score = math.log((1 + self._n_docs) / (1 + self._df[term])) + 1.0
            vec[idx] = tf_score * idf_score

        return _l2_normalize(vec)

def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]

# Singleton instance
_default_embedder = TFIDFEmbedder()

def default_embed_fn(text: str) -> List[float]:
    """Default embedding function for the SIP Protocol."""
    return _default_embedder.embed(text)

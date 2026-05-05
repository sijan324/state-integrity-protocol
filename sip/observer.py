"""
FidelityObserver – measures semantic drift at each agent transition.

Drift is defined as::

    drift = 1 - cosine_similarity(anchor_embedding, current_embedding)

A drift of **0** means perfect alignment; **1** means completely orthogonal
(maximum drift).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, List, Optional, Sequence

from sip.anchor import SemanticAnchor


@dataclass
class TransitionRecord:
    """Immutable snapshot of one agent transition."""

    step: int
    text: str
    embedding: List[float]
    drift: float
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


class FidelityObserver:
    """
    Monitors semantic drift across agent transitions.

    Parameters
    ----------
    anchor:
        A :class:`~sip.anchor.SemanticAnchor` instance that holds the
        reference embedding.
    embed_fn:
        Embedding function used to convert agent outputs to vectors.  Must
        match the function used to build the anchor.
    """

    def __init__(
        self,
        anchor: SemanticAnchor,
        embed_fn: Optional[Callable[[str], Sequence[float]]] = None,
    ) -> None:
        self._anchor = anchor
        if embed_fn is None:
            from sip.embeddings import default_embed_fn

            embed_fn = default_embed_fn
        self._embed_fn = embed_fn
        self._history: List[TransitionRecord] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def observe(self, text: str) -> float:
        """
        Embed *text*, compute drift against the anchor, record the transition.

        Returns
        -------
        float
            Drift score in ``[0.0, 1.0]`` where 0 is perfect fidelity.

        Raises
        ------
        RuntimeError
            If the anchor has not been set yet.
        """
        if not self._anchor.is_set():
            raise RuntimeError(
                "Anchor not set. Call StateIntegrityProtocol.anchor() first."
            )

        current_embedding = list(self._embed_fn(text))
        drift = _cosine_drift(self._anchor.embedding, current_embedding)

        record = TransitionRecord(
            step=len(self._history) + 1,
            text=text,
            embedding=current_embedding,
            drift=drift,
        )
        self._history.append(record)
        return drift

    @property
    def history(self) -> List[TransitionRecord]:
        """All recorded :class:`TransitionRecord` objects (oldest first)."""
        return list(self._history)

    @property
    def last_drift(self) -> Optional[float]:
        """Drift score from the most recent observation, or *None*."""
        return self._history[-1].drift if self._history else None

    def reset(self) -> None:
        """Clear the observation history."""
        self._history.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Dot-product of two equal-length vectors."""
    return sum(x * y for x, y in zip(a, b))


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _pad(
    a: List[float], b: List[float]
) -> tuple[List[float], List[float]]:
    """Zero-pad the shorter vector so both have the same length."""
    diff = len(a) - len(b)
    if diff > 0:
        b = b + [0.0] * diff
    elif diff < 0:
        a = a + [0.0] * (-diff)
    return a, b


def cosine_similarity(
    a: Sequence[float], b: Sequence[float]
) -> float:
    """
    Return the cosine similarity between two vectors.

    Vectors are zero-padded to the same length if necessary.
    Returns ``0.0`` for any zero-length or all-zero vector.
    """
    a, b = _pad(list(a), list(b))
    norm_a, norm_b = _norm(a), _norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return _dot(a, b) / (norm_a * norm_b)


def _cosine_drift(
    anchor: Sequence[float], current: Sequence[float]
) -> float:
    """``drift = 1 - cosine_similarity``."""
    return 1.0 - cosine_similarity(anchor, current)

"""
SemanticAnchor – captures and stores the embedding of the initial prompt.

The anchor acts as the ground-truth reference against which every subsequent
agent output is measured.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence


class SemanticAnchor:
    """
    Stores the *semantic anchor* – the embedding of the origin prompt.

    Parameters
    ----------
    embed_fn:
        A callable ``(text: str) -> List[float]`` that converts a piece of
        text into a numeric vector.  If *None*, the default TF-IDF helper is
        used.
    """

    def __init__(
        self,
        embed_fn: Optional[Callable[[str], Sequence[float]]] = None,
    ) -> None:
        if embed_fn is None:
            from sip.embeddings import default_embed_fn

            embed_fn = default_embed_fn
        self._embed_fn = embed_fn
        self._embedding: Optional[List[float]] = None
        self._text: Optional[str] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set(self, prompt: str) -> List[float]:
        """
        Embed *prompt* and store it as the anchor.

        Returns the embedding so callers can inspect it if needed.
        """
        embedding = list(self._embed_fn(prompt))
        self._embedding = embedding
        self._text = prompt
        return embedding

    @property
    def embedding(self) -> Optional[List[float]]:
        """The stored anchor embedding, or *None* if not yet set."""
        return self._embedding

    @property
    def text(self) -> Optional[str]:
        """The original anchor text, or *None* if not yet set."""
        return self._text

    def is_set(self) -> bool:
        """Return *True* if an anchor has been established."""
        return self._embedding is not None

    def reset(self) -> None:
        """Clear the anchor (useful when starting a new task chain)."""
        self._embedding = None
        self._text = None

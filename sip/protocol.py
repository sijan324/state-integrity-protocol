"""
StateIntegrityProtocol – the top-level orchestrator for Fidelity-Flow
Observation.

Workflow
--------
1. **Anchor** – call :py:meth:`anchor` with the initial prompt to capture the
   semantic anchor.
2. **Observe** – call :py:meth:`observe` after every agent transition.  The
   method returns the drift score and automatically triggers a realignment
   callback when drift exceeds the configured threshold.
3. **Inspect** – use :py:attr:`history` and :py:attr:`is_aligned` to audit the
   pipeline after the fact.

Example
-------
>>> from sip import StateIntegrityProtocol
>>> sip = StateIntegrityProtocol(threshold=0.15)
>>> sip.anchor("Summarise the quarterly report in three bullet points.")
>>> result = sip.observe("Here are three key highlights from Q3 ...")
>>> print(f"Drift: {result.drift:.4f}  Aligned: {sip.is_aligned}")
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence

from sip.anchor import SemanticAnchor
from sip.observer import FidelityObserver, TransitionRecord


@dataclass
class ObservationResult:
    """Returned by :py:meth:`StateIntegrityProtocol.observe`."""

    step: int
    text: str
    drift: float
    threshold: float
    realignment_triggered: bool

    @property
    def is_aligned(self) -> bool:
        """``True`` if drift is within the acceptable threshold."""
        return self.drift <= self.threshold

    @property
    def last_drift(self) -> float:
        """Alias for the latest drift score on this observation."""
        return self.drift


class StateIntegrityProtocol:
    """
    Fidelity-Flow Observation engine.

    Parameters
    ----------
    embed_fn:
        Callable ``(text: str) -> Sequence[float]`` used to embed text.
        Defaults to the built-in TF-IDF helper.
    threshold:
        Drift threshold in ``[0, 1]``.  Outputs whose drift exceeds this value
        trigger the realignment callback.  Default is ``0.15`` (15 %).
    on_realignment:
        Optional callback invoked whenever drift > threshold.  Receives the
        :class:`ObservationResult` for the offending transition.  If not
        provided a :py:class:`UserWarning` is emitted instead.
    """

    DEFAULT_THRESHOLD: float = 0.15

    def __init__(
        self,
        embed_fn: Optional[Callable[[str], Sequence[float]]] = None,
        threshold: float = DEFAULT_THRESHOLD,
        on_realignment: Optional[Callable[["ObservationResult"], None]] = None,
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                f"threshold must be in [0, 1], got {threshold!r}"
            )
        self._threshold = threshold
        self._on_realignment = on_realignment

        self._anchor = SemanticAnchor(embed_fn=embed_fn)
        self._observer = FidelityObserver(
            anchor=self._anchor, embed_fn=embed_fn
        )

    # ------------------------------------------------------------------
    # Core workflow
    # ------------------------------------------------------------------

    def anchor(self, prompt: str) -> List[float]:
        """
        Capture the semantic anchor from the initial *prompt*.

        Resets any existing observation history and re-anchors from scratch.

        Returns
        -------
        List[float]
            The embedding vector of *prompt*.
        """
        self._observer.reset()
        return self._anchor.set(prompt)

    def observe(self, output: str) -> ObservationResult:
        """
        Measure semantic drift of *output* against the anchor.

        Parameters
        ----------
        output:
            The text produced by the current agent node.

        Returns
        -------
        ObservationResult
            Contains the drift score and whether realignment was triggered.

        Raises
        ------
        RuntimeError
            If :py:meth:`anchor` has not been called yet.
        """
        drift = self._observer.observe(output)
        step = len(self._observer.history)

        triggered = drift > self._threshold
        result = ObservationResult(
            step=step,
            text=output,
            drift=drift,
            threshold=self._threshold,
            realignment_triggered=triggered,
        )

        if triggered:
            if self._on_realignment is not None:
                self._on_realignment(result)
            else:
                warnings.warn(
                    f"[SIP] Drift {drift:.4f} exceeds threshold "
                    f"{self._threshold:.4f} at step {step}. "
                    "Consider re-aligning the agent or flagging for human "
                    "intervention.",
                    UserWarning,
                    stacklevel=2,
                )

        return result

    # ------------------------------------------------------------------
    # Inspection helpers
    # ------------------------------------------------------------------

    @property
    def is_aligned(self) -> bool:
        """
        ``True`` if the most recent observation is within the drift threshold.

        Returns ``True`` (vacuously) before any observation has been made.
        """
        last = self._observer.last_drift
        return last is None or last <= self._threshold

    @property
    def threshold(self) -> float:
        """The configured drift threshold."""
        return self._threshold

    @property
    def history(self) -> List[TransitionRecord]:
        """Full list of :class:`~sip.observer.TransitionRecord` objects."""
        return self._observer.history

    @property
    def last_drift(self) -> Optional[float]:
        """Drift score from the most recent observation, or *None*."""
        return self._observer.last_drift

    def reset(self) -> None:
        """
        Full reset – clears the anchor *and* the observation history.

        Use this when starting a completely new task chain.
        """
        self._anchor.reset()
        self._observer.reset()

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StateIntegrityProtocol("
            f"threshold={self._threshold!r}, "
            f"steps={len(self.history)}, "
            f"aligned={self.is_aligned})"
        )

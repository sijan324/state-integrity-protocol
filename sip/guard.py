"""
SIPGuard – Enterprise Gatekeeper Logic.

Wraps :class:`~sip.protocol.StateIntegrityProtocol` and turns every
observation into an explicit *decision* (ALLOW / WARN / BLOCK / REALIGN),
optionally injecting a system-level guardrail payload back into the LLM
context window.
"""

from __future__ import annotations

from typing import Any, Dict

from .protocol import StateIntegrityProtocol


class SIPGuard:
    """
    A firewall around :class:`~sip.protocol.StateIntegrityProtocol`.

    Parameters
    ----------
    threshold:
        Drift threshold passed directly to the underlying protocol.
    mode:
        Action to take when drift exceeds the threshold.

        * ``"warn"``    – return ``action="WARN"`` but let execution continue.
        * ``"block"``   – return ``action="BLOCK"`` (caller should halt).
        * ``"realign"`` – return ``action="REALIGN"`` with a system-level
          guardrail ``payload`` that can be injected back into the LLM context.
    """

    VALID_MODES = {"warn", "block", "realign"}

    def __init__(self, threshold: float = 0.35, mode: str = "realign") -> None:
        if mode not in self.VALID_MODES:
            raise ValueError(f"mode must be one of {self.VALID_MODES!r}, got {mode!r}")
        self.protocol = StateIntegrityProtocol(threshold=threshold)
        self.mode = mode
        self.anchor_text = ""

    def anchor(self, text: str) -> None:
        """Set the semantic anchor (original goal / initial prompt)."""
        self.anchor_text = text
        self.protocol.anchor(text)

    def check(self, step_output: str) -> Dict[str, Any]:
        """
        Observe *step_output* and return a gatekeeper decision.

        Returns
        -------
        dict with keys:

        * ``drift``   – raw drift score (float, 0..1).
        * ``action``  – one of ``"ALLOW"``, ``"WARN"``, ``"BLOCK"``, ``"REALIGN"``.
        * ``payload`` – system-level guardrail message dict (or ``None``).
        """
        observation = self.protocol.observe(step_output)
        drift = observation.drift

        decision: Dict[str, Any] = {
            "drift": drift,
            "action": "ALLOW",
            "payload": None,
        }

        if drift > self.protocol.threshold:
            if self.mode == "block":
                decision["action"] = "BLOCK"
            elif self.mode == "realign":
                decision["action"] = "REALIGN"
                # System-level guardrail — inject this into the LLM context window
                decision["payload"] = {
                    "role": "system",
                    "content": (
                        f"🚨 [STATE INTEGRITY ALERT]\n"
                        f"High Semantic Drift Detected: {round(drift, 4)}\n"
                        f"RE-CENTER ON ORIGINAL GOAL: {self.anchor_text}\n"
                        f"Discard irrelevant thoughts and return to task focus."
                    ),
                }
            else:  # "warn"
                decision["action"] = "WARN"

        return decision

"""
CrewAI integration for the State Integrity Protocol.

Drop :class:`CrewIntegrityManager` into the ``step_callback`` of any
CrewAI ``Agent`` to get automatic drift detection and realignment injection.

Example
-------
>>> from sip.integrations.crew_guard import CrewIntegrityManager
>>> manager = CrewIntegrityManager(goal="Summarise the Q3 financial report")
>>> agent = Agent(..., step_callback=manager.enforce)
"""

from __future__ import annotations

from sip.guard import SIPGuard


class CrewIntegrityManager:
    """
    Plug-and-play CrewAI hook that enforces SIP on every agent step.

    Parameters
    ----------
    goal:
        The original task goal used as the semantic anchor.
    threshold:
        Drift threshold; observations above this value trigger realignment.
    """

    def __init__(self, goal: str, threshold: float = 0.35) -> None:
        self.guard = SIPGuard(threshold=threshold, mode="realign")
        self.guard.anchor(goal)

    def enforce(self, step_output: object) -> object | None:
        """
        Hook this into the ``step_callback`` of a CrewAI ``Agent``.

        Parameters
        ----------
        step_output:
            The raw step output object provided by CrewAI.  The method
            extracts text via the ``.raw`` attribute when available,
            falling back to ``str()``.

        Returns
        -------
        A system-message dict when realignment is triggered, otherwise
        ``None`` (no action needed).

        Raises
        ------
        Exception
            When ``mode="block"`` and drift exceeds the threshold.
        """
        content = getattr(step_output, "raw", str(step_output))
        decision = self.guard.check(content)

        if decision["action"] == "BLOCK":
            raise Exception(
                f"SIP Guard: Execution halted due to drift ({decision['drift']})"
            )

        if decision["action"] == "REALIGN":
            print(
                f"💉 [SIP] Injecting System-Level Guardrail (Drift: {decision['drift']})"
            )
            # In production, this payload is injected back into the LLM context window
            return decision["payload"]

        return None

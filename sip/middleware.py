"""
Middleware orchestration for the State Integrity Protocol (SIP).

Flow:
Human/Agent A -> anchor(intent) -> middleware checks -> verify_and_sign()
-> accepted OR repair loop.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple

from sip.anchor import SemanticAnchor
from sip.observer import FidelityObserver

Signer = Callable[[str], str]


@dataclass(frozen=True)
class DriftCheckResult:
    drift: float
    threshold: float
    passed: bool


@dataclass(frozen=True)
class IntentAlignmentResult:
    score: float
    threshold: float
    passed: bool


@dataclass(frozen=True)
class ConstraintViolationResult:
    constraints: Tuple[str, ...]
    violations: Tuple[str, ...]
    passed: bool


@dataclass(frozen=True)
class MiddlewareEvaluation:
    step: int
    output: str
    drift_check: DriftCheckResult
    intent_alignment: IntentAlignmentResult
    constraint_check: ConstraintViolationResult
    failure_codes: Tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.failure_codes


@dataclass(frozen=True)
class VerificationDecision:
    accepted: bool
    repair_required: bool
    reasons: Tuple[str, ...]
    failure_codes: Tuple[str, ...]
    signature: str
    payload: str


@dataclass(frozen=True)
class PipelineResult:
    status: str
    evaluation: MiddlewareEvaluation
    decision: VerificationDecision
    attempts_used: int
    attempts_remaining: int
    repair_instructions: Tuple[str, ...]


class SIPMiddlewarePipeline:
    """
    High-level middleware flow on top of SIP primitives.

    The low-level `StateIntegrityProtocol.anchor()` and `observe()` API remains
    unchanged; this class provides an optional orchestration path.
    """

    DEFAULT_DRIFT_THRESHOLD: float = 0.15
    DEFAULT_INTENT_ALIGNMENT_THRESHOLD: float = 0.2
    DEFAULT_MAX_RETRIES: int = 2

    def __init__(
        self,
        *,
        embed_fn: Optional[Callable[[str], Sequence[float]]] = None,
        drift_threshold: float = DEFAULT_DRIFT_THRESHOLD,
        intent_alignment_threshold: float = DEFAULT_INTENT_ALIGNMENT_THRESHOLD,
        constraints: Optional[Sequence[str]] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        signer: Optional[Signer] = None,
    ) -> None:
        if not 0.0 <= drift_threshold <= 1.0:
            raise ValueError(
                f"drift_threshold must be in [0, 1], got {drift_threshold!r}"
            )
        if not 0.0 <= intent_alignment_threshold <= 1.0:
            raise ValueError(
                "intent_alignment_threshold must be in [0, 1], "
                f"got {intent_alignment_threshold!r}"
            )
        if max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {max_retries!r}")

        self._drift_threshold = drift_threshold
        self._intent_alignment_threshold = intent_alignment_threshold
        self._constraints = tuple(constraints or ())
        self._max_retries = max_retries
        self._signer = signer or _default_signer

        self._anchor = SemanticAnchor(embed_fn=embed_fn)
        self._observer = FidelityObserver(anchor=self._anchor, embed_fn=embed_fn)

        self._intent_text: Optional[str] = None
        self._intent_tokens: set[str] = set()
        self._rejection_count = 0

    @property
    def history(self):
        return self._observer.history

    def anchor(self, intent: str) -> List[float]:
        if not intent.strip():
            raise ValueError("intent must be a non-empty string")
        self._observer.reset()
        self._rejection_count = 0
        self._intent_text = intent
        self._intent_tokens = _tokenize(intent)
        return self._anchor.set(intent)

    def evaluate(
        self, output: str, constraints: Optional[Sequence[str]] = None
    ) -> MiddlewareEvaluation:
        if self._intent_text is None:
            raise RuntimeError("Anchor not set. Call anchor() before evaluate().")

        drift = self._observer.observe(output)
        drift_check = DriftCheckResult(
            drift=drift,
            threshold=self._drift_threshold,
            passed=drift <= self._drift_threshold,
        )

        intent_score = _intent_alignment_score(
            intent_tokens=self._intent_tokens, output=output
        )
        intent_alignment = IntentAlignmentResult(
            score=intent_score,
            threshold=self._intent_alignment_threshold,
            passed=intent_score >= self._intent_alignment_threshold,
        )

        active_constraints = tuple(
            self._constraints if constraints is None else constraints
        )
        output_lower = output.lower()
        violations = tuple(
            c
            for c in active_constraints
            if _matches_constraint_phrase(c, output_lower)
        )
        constraint_check = ConstraintViolationResult(
            constraints=active_constraints,
            violations=violations,
            passed=not violations,
        )

        failure_codes = []
        if not drift_check.passed:
            failure_codes.append("drift")
        if not intent_alignment.passed:
            failure_codes.append("intent_alignment")
        if not constraint_check.passed:
            failure_codes.append("constraint_violation")

        return MiddlewareEvaluation(
            step=len(self._observer.history),
            output=output,
            drift_check=drift_check,
            intent_alignment=intent_alignment,
            constraint_check=constraint_check,
            failure_codes=tuple(failure_codes),
        )

    def verify_and_sign(self, evaluation: MiddlewareEvaluation) -> VerificationDecision:
        reasons = tuple(_reason_for_code(code, evaluation) for code in evaluation.failure_codes)
        payload = _stable_payload(evaluation=evaluation, reasons=reasons)
        signature = self._signer(payload)
        return VerificationDecision(
            accepted=evaluation.passed,
            repair_required=not evaluation.passed,
            reasons=reasons,
            failure_codes=evaluation.failure_codes,
            signature=signature,
            payload=payload,
        )

    def run(
        self, output: str, constraints: Optional[Sequence[str]] = None
    ) -> PipelineResult:
        if self._intent_text is None:
            raise RuntimeError("Anchor not set. Call anchor() before run().")

        evaluation = self.evaluate(output=output, constraints=constraints)
        decision = self.verify_and_sign(evaluation)
        if not decision.accepted:
            self._rejection_count += 1

        rejection_count = self._rejection_count
        attempts_used = rejection_count
        attempts_remaining = max(0, self._max_retries - rejection_count)
        status = "accepted"
        repair_instructions: Tuple[str, ...] = ()
        if not decision.accepted:
            attempts_remaining = max(0, self._max_retries - rejection_count + 1)
            status = (
                "repair_required"
                if self._rejection_count <= self._max_retries
                else "rejected"
            )
            repair_instructions = tuple(
                _repair_instruction_for_code(code)
                for code in decision.failure_codes
            )
        return PipelineResult(
            status=status,
            evaluation=evaluation,
            decision=decision,
            attempts_used=attempts_used,
            attempts_remaining=attempts_remaining,
            repair_instructions=repair_instructions,
        )


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _intent_alignment_score(intent_tokens: set[str], output: str) -> float:
    if not intent_tokens:
        return 1.0
    output_tokens = _tokenize(output)
    overlap = len(intent_tokens.intersection(output_tokens))
    return overlap / len(intent_tokens)


def _matches_constraint_phrase(constraint: str, output_lower: str) -> bool:
    phrase = constraint.strip().lower()
    if not phrase:
        return False
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, output_lower) is not None


def _reason_for_code(code: str, evaluation: MiddlewareEvaluation) -> str:
    if code == "drift":
        return (
            "Drift "
            f"{evaluation.drift_check.drift:.4f} exceeded threshold "
            f"{evaluation.drift_check.threshold:.4f}."
        )
    if code == "intent_alignment":
        return (
            "Intent alignment "
            f"{evaluation.intent_alignment.score:.4f} fell below threshold "
            f"{evaluation.intent_alignment.threshold:.4f}."
        )
    if code == "constraint_violation":
        violations = ", ".join(evaluation.constraint_check.violations)
        return f"Constraint violations detected: {violations}."
    return f"Unknown failure code: {code}."


def _repair_instruction_for_code(code: str) -> str:
    if code == "drift":
        return "Regenerate response with closer semantic fidelity to the anchor intent."
    if code == "intent_alignment":
        return "Add explicit intent terms and requested scope from the anchored intent."
    if code == "constraint_violation":
        return "Remove prohibited phrases and satisfy all configured constraints."
    return "Review middleware failure and regenerate output."


def _stable_payload(
    *, evaluation: MiddlewareEvaluation, reasons: Tuple[str, ...]
) -> str:
    data = {
        "constraint_check": {
            "constraints": list(evaluation.constraint_check.constraints),
            "passed": evaluation.constraint_check.passed,
            "violations": list(evaluation.constraint_check.violations),
        },
        "drift_check": {
            "drift": evaluation.drift_check.drift,
            "passed": evaluation.drift_check.passed,
            "threshold": evaluation.drift_check.threshold,
        },
        "failure_codes": list(evaluation.failure_codes),
        "intent_alignment": {
            "passed": evaluation.intent_alignment.passed,
            "score": evaluation.intent_alignment.score,
            "threshold": evaluation.intent_alignment.threshold,
        },
        "output": evaluation.output,
        "passed": evaluation.passed,
        "reasons": list(reasons),
        "step": evaluation.step,
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _default_signer(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

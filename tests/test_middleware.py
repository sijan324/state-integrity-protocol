from __future__ import annotations

import pytest

from sip import SIPMiddlewarePipeline


def _make_embed(vecs: dict[str, list[float]]):
    def embed(text: str) -> list[float]:
        return vecs[text]

    return embed


def test_run_accepts_when_all_checks_pass():
    vecs = {
        "summarize quarterly report": [1.0, 0.0],
        "summarize quarterly report with three bullet points": [1.0, 0.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.5,
        constraints=("forbidden",),
    )
    pipeline.anchor("summarize quarterly report")

    result = pipeline.run("summarize quarterly report with three bullet points")

    assert result.status == "accepted"
    assert result.decision.accepted
    assert not result.decision.repair_required
    assert result.decision.failure_codes == ()
    assert result.repair_instructions == ()
    assert len(result.decision.signature) == 64


def test_run_flags_drift_failure():
    vecs = {
        "intent": [1.0, 0.0],
        "off-topic but intent": [0.0, 1.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.0,
    )
    pipeline.anchor("intent")

    result = pipeline.run("off-topic but intent")

    assert result.status == "repair_required"
    assert result.decision.failure_codes == ("drift",)
    assert result.attempts_used == 1


def test_run_flags_intent_alignment_failure():
    vecs = {
        "refund policy details": [1.0, 0.0],
        "shipping status update": [1.0, 0.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.5,
    )
    pipeline.anchor("refund policy details")

    result = pipeline.run("shipping status update")

    assert result.status == "repair_required"
    assert result.decision.failure_codes == ("intent_alignment",)


def test_run_flags_constraint_violation():
    vecs = {
        "safe response": [1.0, 0.0],
        "safe response with leak": [1.0, 0.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.3,
        constraints=("leak",),
    )
    pipeline.anchor("safe response")

    result = pipeline.run("safe response with leak")

    assert result.status == "repair_required"
    assert result.decision.failure_codes == ("constraint_violation",)
    assert result.evaluation.constraint_check.violations == ("leak",)


def test_verify_and_sign_is_deterministic_for_same_evaluation():
    vecs = {
        "intent": [1.0, 0.0],
        "intent reply": [1.0, 0.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.5,
    )
    pipeline.anchor("intent")
    evaluation = pipeline.evaluate("intent reply")

    decision_a = pipeline.verify_and_sign(evaluation)
    decision_b = pipeline.verify_and_sign(evaluation)

    assert decision_a.payload == decision_b.payload
    assert decision_a.signature == decision_b.signature


def test_repair_loop_reaches_max_retries_and_rejects():
    vecs = {
        "intent": [1.0, 0.0],
        "bad intent": [0.0, 1.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.0,
        max_retries=1,
    )
    pipeline.anchor("intent")

    first = pipeline.run("bad intent")
    second = pipeline.run("bad intent")

    assert first.status == "repair_required"
    assert first.attempts_remaining == 1
    assert second.status == "rejected"
    assert second.attempts_used == 2
    assert second.attempts_remaining == 0


def test_anchor_resets_repair_loop_state():
    vecs = {
        "intent": [1.0, 0.0],
        "bad intent": [0.0, 1.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.0,
        max_retries=1,
    )
    pipeline.anchor("intent")
    pipeline.run("bad intent")
    pipeline.run("bad intent")

    pipeline.anchor("intent")
    result = pipeline.run("bad intent")

    assert result.status == "repair_required"
    assert result.attempts_used == 1


def test_run_without_anchor_raises_runtime_error():
    pipeline = SIPMiddlewarePipeline()
    with pytest.raises(RuntimeError, match="Anchor not set"):
        pipeline.run("output")


def test_per_call_constraints_override_defaults():
    vecs = {
        "intent": [1.0, 0.0],
        "intent unsafe": [1.0, 0.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.5,
        constraints=("default",),
    )
    pipeline.anchor("intent")

    result = pipeline.run("intent unsafe", constraints=("unsafe",))

    assert result.decision.failure_codes == ("constraint_violation",)
    assert result.evaluation.constraint_check.constraints == ("unsafe",)


def test_constraint_check_uses_word_boundary_matching():
    vecs = {
        "intent": [1.0, 0.0],
        "intent release notes": [1.0, 0.0],
    }
    pipeline = SIPMiddlewarePipeline(
        embed_fn=_make_embed(vecs),
        drift_threshold=0.15,
        intent_alignment_threshold=0.5,
        constraints=("leak",),
    )
    pipeline.anchor("intent")

    result = pipeline.run("intent release notes")

    assert result.status == "accepted"
    assert result.decision.failure_codes == ()


def test_anchor_rejects_blank_intent():
    pipeline = SIPMiddlewarePipeline()
    with pytest.raises(ValueError, match="non-empty"):
        pipeline.anchor("   ")

"""
State Integrity Protocol (SIP) 🧬

A Fidelity-Flow Observation library for detecting and measuring State Decay
in multi-agent AI pipelines.
"""

from sip.anchor import SemanticAnchor
from sip.middleware import (
    ConstraintViolationResult,
    DriftCheckResult,
    IntentAlignmentResult,
    MiddlewareEvaluation,
    PipelineResult,
    SIPMiddlewarePipeline,
    VerificationDecision,
)
from sip.observer import FidelityObserver, TransitionRecord, cosine_similarity
from sip.protocol import ObservationResult, StateIntegrityProtocol

__all__ = [
    "StateIntegrityProtocol",
    "SemanticAnchor",
    "FidelityObserver",
    "ObservationResult",
    "TransitionRecord",
    "cosine_similarity",
    "SIPMiddlewarePipeline",
    "DriftCheckResult",
    "IntentAlignmentResult",
    "ConstraintViolationResult",
    "MiddlewareEvaluation",
    "VerificationDecision",
    "PipelineResult",
]

__version__ = "0.1.0"

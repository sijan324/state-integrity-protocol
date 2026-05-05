"""
State Integrity Protocol (SIP) 🧬

A Fidelity-Flow Observation library for detecting and measuring State Decay
in multi-agent AI pipelines.
"""

from sip.anchor import SemanticAnchor
from sip.observer import FidelityObserver, TransitionRecord, cosine_similarity
from sip.protocol import ObservationResult, StateIntegrityProtocol

__all__ = [
    "StateIntegrityProtocol",
    "SemanticAnchor",
    "FidelityObserver",
    "ObservationResult",
    "TransitionRecord",
    "cosine_similarity",
]

__version__ = "0.1.0"

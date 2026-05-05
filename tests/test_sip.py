"""
Tests for the State Integrity Protocol (SIP).
"""

from __future__ import annotations

import math
import warnings
from typing import List, Sequence
from unittest.mock import MagicMock

import pytest

from sip import (
    FidelityObserver,
    ObservationResult,
    SemanticAnchor,
    StateIntegrityProtocol,
    TransitionRecord,
    cosine_similarity,
)
from sip.embeddings import TFIDFEmbedder, default_embed_fn


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unit_vec(dim: int, idx: int) -> List[float]:
    """Return a unit vector of length *dim* with a 1.0 at *idx*."""
    v = [0.0] * dim
    v[idx] = 1.0
    return v


def _make_embed(vecs: dict[str, List[float]]):
    """Return an embedding function backed by a lookup table."""

    def embed(text: str) -> List[float]:
        return vecs[text]

    return embed


# ---------------------------------------------------------------------------
# cosine_similarity
# ---------------------------------------------------------------------------


class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = [1.0, 2.0, 3.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = _unit_vec(3, 0)
        b = _unit_vec(3, 1)
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector_returns_zero(self):
        a = [0.0, 0.0]
        b = [1.0, 2.0]
        assert cosine_similarity(a, b) == 0.0

    def test_different_lengths_are_padded(self):
        # Extending [1,0] to [1,0,0] and [0,0,1] → dot=0 → similarity=0
        a = [1.0, 0.0]
        b = [0.0, 0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_parallel_vectors_different_magnitude(self):
        a = [2.0, 4.0]
        b = [1.0, 2.0]
        assert cosine_similarity(a, b) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# TFIDFEmbedder
# ---------------------------------------------------------------------------


class TestTFIDFEmbedder:
    def test_embed_returns_list(self):
        embedder = TFIDFEmbedder()
        result = embedder.embed("hello world")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_embed_empty_string(self):
        embedder = TFIDFEmbedder()
        result = embedder.embed("")
        assert result == []

    def test_embed_is_l2_normalized(self):
        embedder = TFIDFEmbedder()
        result = embedder.embed("test normalisation vector")
        norm = math.sqrt(sum(v * v for v in result))
        assert norm == pytest.approx(1.0, abs=1e-6)

    def test_similar_texts_are_close(self):
        embedder = TFIDFEmbedder()
        v1 = embedder.embed("the cat sat on the mat")
        v2 = embedder.embed("the cat sat on the mat")
        # same text → cosine similarity == 1
        sim = cosine_similarity(v1, v2)
        assert sim == pytest.approx(1.0, abs=1e-6)

    def test_different_texts_have_lower_similarity(self):
        embedder = TFIDFEmbedder()
        v1 = embedder.embed("apple banana cherry")
        v2 = embedder.embed("completely unrelated topic here")
        sim = cosine_similarity(v1, v2)
        # Not necessarily 0, but should be < 1
        assert sim < 1.0


# ---------------------------------------------------------------------------
# SemanticAnchor
# ---------------------------------------------------------------------------


class TestSemanticAnchor:
    def test_not_set_by_default(self):
        anchor = SemanticAnchor()
        assert not anchor.is_set()
        assert anchor.embedding is None
        assert anchor.text is None

    def test_set_stores_embedding_and_text(self):
        anchor = SemanticAnchor()
        anchor.set("initial prompt")
        assert anchor.is_set()
        assert isinstance(anchor.embedding, list)
        assert anchor.text == "initial prompt"

    def test_reset_clears_state(self):
        anchor = SemanticAnchor()
        anchor.set("some prompt")
        anchor.reset()
        assert not anchor.is_set()
        assert anchor.embedding is None

    def test_custom_embed_fn_is_used(self):
        vecs = {"hello": [1.0, 0.0]}
        anchor = SemanticAnchor(embed_fn=_make_embed(vecs))
        result = anchor.set("hello")
        assert result == [1.0, 0.0]
        assert anchor.embedding == [1.0, 0.0]


# ---------------------------------------------------------------------------
# FidelityObserver
# ---------------------------------------------------------------------------


class TestFidelityObserver:
    def _make_observer(self, vecs: dict[str, List[float]]):
        embed = _make_embed(vecs)
        anchor = SemanticAnchor(embed_fn=embed)
        observer = FidelityObserver(anchor=anchor, embed_fn=embed)
        return anchor, observer

    def test_observe_raises_if_anchor_not_set(self):
        anchor = SemanticAnchor()
        observer = FidelityObserver(anchor=anchor)
        with pytest.raises(RuntimeError, match="Anchor not set"):
            observer.observe("some text")

    def test_zero_drift_for_identical_text(self):
        vecs = {"prompt": [1.0, 0.0], "output": [1.0, 0.0]}
        anchor, observer = self._make_observer(vecs)
        anchor.set("prompt")
        drift = observer.observe("output")
        assert drift == pytest.approx(0.0, abs=1e-6)

    def test_max_drift_for_orthogonal_text(self):
        vecs = {"prompt": [1.0, 0.0], "output": [0.0, 1.0]}
        anchor, observer = self._make_observer(vecs)
        anchor.set("prompt")
        drift = observer.observe("output")
        assert drift == pytest.approx(1.0, abs=1e-6)

    def test_history_grows_with_each_observation(self):
        vecs = {
            "prompt": [1.0, 0.0],
            "a": [1.0, 0.0],
            "b": [0.9, 0.1],
        }
        anchor, observer = self._make_observer(vecs)
        anchor.set("prompt")
        observer.observe("a")
        observer.observe("b")
        assert len(observer.history) == 2

    def test_history_records_are_transition_records(self):
        vecs = {"prompt": [1.0, 0.0], "out": [0.8, 0.2]}
        anchor, observer = self._make_observer(vecs)
        anchor.set("prompt")
        observer.observe("out")
        record = observer.history[0]
        assert isinstance(record, TransitionRecord)
        assert record.step == 1
        assert record.text == "out"

    def test_last_drift_is_none_before_observations(self):
        anchor = SemanticAnchor()
        observer = FidelityObserver(anchor=anchor)
        assert observer.last_drift is None

    def test_reset_clears_history(self):
        vecs = {"prompt": [1.0, 0.0], "out": [0.5, 0.5]}
        anchor, observer = self._make_observer(vecs)
        anchor.set("prompt")
        observer.observe("out")
        observer.reset()
        assert len(observer.history) == 0
        assert observer.last_drift is None


# ---------------------------------------------------------------------------
# StateIntegrityProtocol
# ---------------------------------------------------------------------------


class TestStateIntegrityProtocol:
    def _sip_with_vecs(
        self, vecs: dict[str, List[float]], threshold: float = 0.15
    ) -> StateIntegrityProtocol:
        embed = _make_embed(vecs)
        return StateIntegrityProtocol(embed_fn=embed, threshold=threshold)

    # ---- construction ----

    def test_default_threshold(self):
        sip = StateIntegrityProtocol()
        assert sip.threshold == 0.15

    def test_invalid_threshold_raises(self):
        with pytest.raises(ValueError):
            StateIntegrityProtocol(threshold=1.5)

    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError):
            StateIntegrityProtocol(threshold=-0.1)

    # ---- anchor ----

    def test_anchor_returns_embedding(self):
        vecs = {"hello": [1.0, 0.0]}
        sip = self._sip_with_vecs(vecs)
        embedding = sip.anchor("hello")
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_anchor_resets_history(self):
        vecs = {
            "p": [1.0, 0.0],
            "o": [0.5, 0.5],
            "q": [1.0, 0.0],
        }
        sip = self._sip_with_vecs(vecs)
        sip.anchor("p")
        sip.observe("o")
        assert len(sip.history) == 1
        sip.anchor("q")
        assert len(sip.history) == 0

    # ---- observe ----

    def test_observe_raises_without_anchor(self):
        sip = StateIntegrityProtocol()
        with pytest.raises(RuntimeError):
            sip.observe("some output")

    def test_observe_returns_observation_result(self):
        vecs = {"prompt": [1.0, 0.0], "out": [1.0, 0.0]}
        sip = self._sip_with_vecs(vecs)
        sip.anchor("prompt")
        result = sip.observe("out")
        assert isinstance(result, ObservationResult)

    def test_low_drift_does_not_trigger_realignment(self):
        vecs = {"prompt": [1.0, 0.0], "out": [1.0, 0.0]}
        sip = self._sip_with_vecs(vecs, threshold=0.15)
        sip.anchor("prompt")
        result = sip.observe("out")
        assert not result.realignment_triggered
        assert result.is_aligned

    def test_high_drift_triggers_realignment_warning(self):
        vecs = {"prompt": [1.0, 0.0], "out": [0.0, 1.0]}
        sip = self._sip_with_vecs(vecs, threshold=0.15)
        sip.anchor("prompt")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = sip.observe("out")
        assert result.realignment_triggered
        assert not result.is_aligned
        assert len(w) == 1
        assert "Drift" in str(w[0].message)

    def test_high_drift_calls_on_realignment_callback(self):
        vecs = {"prompt": [1.0, 0.0], "out": [0.0, 1.0]}
        callback = MagicMock()
        embed = _make_embed(vecs)
        sip = StateIntegrityProtocol(
            embed_fn=embed, threshold=0.15, on_realignment=callback
        )
        sip.anchor("prompt")
        result = sip.observe("out")
        callback.assert_called_once_with(result)

    def test_is_aligned_true_before_observations(self):
        sip = StateIntegrityProtocol()
        assert sip.is_aligned

    def test_is_aligned_reflects_last_drift(self):
        vecs = {"prompt": [1.0, 0.0], "bad": [0.0, 1.0]}
        sip = self._sip_with_vecs(vecs, threshold=0.15)
        sip.anchor("prompt")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            sip.observe("bad")
        assert not sip.is_aligned

    def test_last_drift_none_before_observe(self):
        vecs = {"prompt": [1.0, 0.0]}
        sip = self._sip_with_vecs(vecs)
        sip.anchor("prompt")
        assert sip.last_drift is None

    def test_history_accumulates(self):
        vecs = {
            "prompt": [1.0, 0.0],
            "step1": [0.9, 0.1],
            "step2": [0.8, 0.2],
        }
        sip = self._sip_with_vecs(vecs)
        sip.anchor("prompt")
        sip.observe("step1")
        sip.observe("step2")
        assert len(sip.history) == 2

    def test_drift_value_matches_expected(self):
        # anchor=[1,0], output=[0,1] → cosine_similarity=0 → drift=1
        vecs = {"prompt": [1.0, 0.0], "out": [0.0, 1.0]}
        sip = self._sip_with_vecs(vecs)
        sip.anchor("prompt")
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = sip.observe("out")
        assert result.drift == pytest.approx(1.0, abs=1e-6)

    def test_reset_clears_everything(self):
        vecs = {"prompt": [1.0, 0.0], "out": [0.5, 0.5]}
        sip = self._sip_with_vecs(vecs)
        sip.anchor("prompt")
        sip.observe("out")
        sip.reset()
        assert sip.last_drift is None
        assert len(sip.history) == 0
        with pytest.raises(RuntimeError):
            sip.observe("anything")

    # ---- end-to-end with real TF-IDF embedder ----

    def test_end_to_end_tfidf(self):
        sip = StateIntegrityProtocol(threshold=0.15)
        sip.anchor("Summarise the quarterly report in three bullet points.")
        # Semantically similar output → low drift expected
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = sip.observe(
                "Here are three bullet points summarising the quarterly report."
            )
        assert isinstance(result.drift, float)
        assert 0.0 <= result.drift <= 2.0  # drift can slightly exceed 1 with TF-IDF

    def test_threshold_boundary(self):
        # drift == threshold → NOT triggered (strictly greater-than)
        vecs = {
            "p": [1.0, 0.0],
            # cosine_similarity([1,0],[1,0]) = 1 → drift = 0 ≤ 0.15
            "o": [1.0, 0.0],
        }
        sip = self._sip_with_vecs(vecs, threshold=0.0)
        sip.anchor("p")
        result = sip.observe("o")
        # drift=0.0, threshold=0.0 → 0 > 0 is False → not triggered
        assert not result.realignment_triggered

# 🧬 State Integrity Protocol (SIP)

> A lightweight runtime layer for detecting and preventing semantic drift in LLM outputs.

SIP helps AI systems stay **faithful to user intent** across generation, transformation, and multi-agent workflows.

---

## ⚠️ Problem

LLMs can fail silently by:

- drifting from original intent
- adding unwanted assumptions
- changing numbers, constraints, or meaning
- hallucinating details that were never requested

This makes AI outputs less reliable in production systems.

---

## 🧠 Solution

SIP introduces a runtime integrity loop:

**Intent → Anchor → Output → Observe → Drift Score → Decision**

Every generated output is checked against the original anchored intent before it is accepted.

---

## ⚙️ Core Concept

SIP operates in three stages:

### 1) Anchor (Intent Definition)

Define the original intent:

```python
sip.anchor("Refund user $50 within 7 days")
```

### 2) Observe (Output Evaluation)

Compare generated output against the anchor:

```python
result = sip.observe("Refund user $500 immediately")
```

### 3) Decision Layer

Use alignment and drift signals to decide accept/repair/reject:

```python
print(result.is_aligned)
print(result.drift)
```

---

## 🔁 Example

```python
from sip import StateIntegrityProtocol

sip = StateIntegrityProtocol()

sip.anchor("Delete user account safely")
result = sip.observe("Create new user account")

print(result.is_aligned)  # False
print(result.drift)       # e.g., 0.61
```

`ObservationResult` also exposes `last_drift` as the latest drift-score alias.

---

## 🧱 Architecture

SIP is designed as middleware for AI systems:

```text
User / Agent
    ↓
LLM (generation)
    ↓
SIP Middleware
    ├── Drift detection
    ├── Intent alignment check
    ├── Constraint validation
    ↓
Decision: Accept / Repair / Reject
```

---

## 🔐 What SIP Detects

- semantic drift
- numerical manipulation
- instruction leakage
- constraint violations
- intent mismatch
- prompt injection attempts

---

## 🚀 Why This Matters

SIP makes AI systems:

- more reliable
- more predictable
- safer for production use
- easier to audit

---

## 🧩 Use Cases

- AI agents
- LLM pipelines
- autonomous workflows
- enterprise AI systems
- chatbots with strict behavior controls

---

## 📦 Installation

```bash
pip install -e .
```

For development and tests:

```bash
python -m pip install -e '.[dev]'
```

---

## 🧠 Core API

- `anchor(prompt: str)` — define the initial intent state
- `observe(output: str)` — evaluate drift from the anchored intent
- `is_aligned: bool` — alignment signal
- `last_drift: float` — latest drift score
- `history: list` — transition history
- `SIPMiddlewarePipeline` — optional anchor → checks → verify/sign → repair loop orchestration

---

## 🛡️ Middleware + Verification Flow

The optional pipeline can run:

1. drift check against the anchor
2. intent-alignment check
3. constraint-violation check
4. `verify_and_sign()` decision
5. accept/repair/reject routing

```python
from sip import SIPMiddlewarePipeline

pipeline = SIPMiddlewarePipeline(
    drift_threshold=0.15,
    intent_alignment_threshold=0.3,
    constraints=["do not mention internal token"],
    max_retries=2,
)

pipeline.anchor("Summarize refund policy in 3 bullet points")
result = pipeline.run(
    "Refund policy summary in 3 bullet points without internal token."
)

print(result.status)                 # accepted | repair_required | rejected
print(result.decision.signature)     # deterministic decision signature
print(result.decision.failure_codes) # machine-readable failure causes
print(result.repair_instructions)    # guidance when not accepted
```

### Policy Knobs

- `drift_threshold`: maximum allowed semantic drift
- `intent_alignment_threshold`: minimum token-overlap score
- `constraints`: blocked words/phrases
- `max_retries`: max repair attempts before rejection
- `signer`: optional custom signing function for `verify_and_sign()`

---

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

---

## 🛡️ Philosophy

> “AI should not just generate outputs — it should stay faithful to intent.”

SIP enforces that principle at runtime.

---

## Licensing & Commercial Use

- Core SDK (SIP) is licensed under AGPL-3.0.
- **AI Sentinel** (the full monitoring system) is a separate commercial product and is **not open source**.
- Companies can use SIP under AGPL terms.
- For commercial hosted service, white-label, or custom enterprise versions, please contact us.

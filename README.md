# State Integrity Protocol (SIP) 🧬

A specialized auditing protocol to detect and measure **State Decay** –
information fidelity loss – in multi-agent AI pipelines and LLM chains.

---

## 🛡️ 3-Line CrewAI Integration

Secure your autonomous agents against State Decay in seconds:

```python
from sip.integrations import CrewIntegrityManager

# 1. Initialise the Guard
guard = CrewIntegrityManager(goal="Research Q3 Financials", threshold=0.35)

# 2. Inject into your Agent
agent = Agent(role="Analyst", goal="...", step_callback=guard.enforce)

# 3. SIP now automatically injects system-level realignment payloads when the agent drifts.
```

> **Zero latency** – guardrail checks run in milliseconds using a local TF-IDF embedder (no API key required).

---

## The Problem: State Decay in AI Agents

Current multi-agent systems (LangChain, CrewAI, AutoGPT) suffer from **State
Decay**.  As information passes from Node A to Node D, the original intent
loses fidelity by approximately 15–30 %.  This leads to hallucinations, cost
overruns, and system failure.

## The Solution: Fidelity-Flow Observation

SIP introduces a **Semantic Anchor** at the point of origin.  It uses cosine
similarity and drift-detection algorithms to monitor the *Internal State* of
the AI at every transition.

### Key Features

| Feature | Description |
|---|---|
| **Drift Detection** | Real-time monitoring of intent-output alignment |
| **Context Preservation** | Logic gates to stop an agent if fidelity drops below a threshold |
| **Cost Optimisation** | Reduces token waste by preventing redundant reasoning loops |

### How It Works

1. **Anchor** – Capture the embedding of the initial prompt.
2. **Observe** – At each transition, calculate `drift = 1 − cosine_similarity`.
3. **Trigger** – If `drift > 0.15`, re-align the agent or flag for human
   intervention.

---

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from sip import StateIntegrityProtocol

# Create a protocol instance (default threshold = 0.15)
sip = StateIntegrityProtocol(threshold=0.15)

# Step 1 – Anchor: capture the initial intent
sip.anchor("Summarise the quarterly report in three bullet points.")

# Step 2 – Observe: measure drift after each agent transition
result = sip.observe("Here are three bullet points from the quarterly report.")
print(f"Drift: {result.drift:.4f}  Aligned: {result.is_aligned}")
# Drift: 0.0502  Aligned: True

# High-drift example
result = sip.observe("The weather in Paris is lovely this time of year.")
print(f"Drift: {result.drift:.4f}  Aligned: {result.is_aligned}")
# UserWarning: [SIP] Drift 0.7831 exceeds threshold 0.1500 at step 2.
# Drift: 0.7831  Aligned: False
```

### Custom Realignment Callback

```python
def my_realignment_handler(result):
    print(f"[ALERT] Step {result.step} drifted by {result.drift:.4f}. Re-aligning...")
    # e.g. inject a correction prompt back into the agent

sip = StateIntegrityProtocol(
    threshold=0.15,
    on_realignment=my_realignment_handler,
)
```

### Custom Embedding Function

Drop in any embedding backend (OpenAI, sentence-transformers, etc.):

```python
import openai

def openai_embed(text: str):
    resp = openai.embeddings.create(input=text, model="text-embedding-3-small")
    return resp.data[0].embedding

sip = StateIntegrityProtocol(embed_fn=openai_embed, threshold=0.15)
```

### Inspect the Full History

```python
for record in sip.history:
    print(f"Step {record.step}: drift={record.drift:.4f}  text={record.text[:60]}")
```

---

## API Reference

### `SIPGuard`

High-level gatekeeper. Each `check()` call returns a decision dict with keys
`drift`, `action` (`"ALLOW"` / `"WARN"` / `"BLOCK"` / `"REALIGN"`), and
`payload` (a ready-to-inject system-message dict on `REALIGN`, otherwise
`None`).

| Method / Property | Description |
|---|---|
| `anchor(text)` | Set the semantic anchor (original goal) |
| `check(step_output) → dict` | Observe output and return a gatekeeper decision |

### `CrewIntegrityManager`

Plug-and-play hook for CrewAI's `step_callback`.

| Method / Property | Description |
|---|---|
| `enforce(step_output)` | Returns guardrail payload on `REALIGN`, raises on `BLOCK`, `None` on `ALLOW` |

### `StateIntegrityProtocol`

| Method / Property | Description |
|---|---|
| `anchor(prompt)` | Set the semantic anchor from the initial prompt |
| `observe(output) → ObservationResult` | Measure drift at current transition |
| `is_aligned` | `True` if last drift ≤ threshold |
| `last_drift` | Most recent drift score (or `None`) |
| `history` | List of all `TransitionRecord` objects |
| `reset()` | Clear anchor and history |

### `ObservationResult`

| Attribute | Description |
|---|---|
| `step` | Transition index (1-based) |
| `drift` | `1 − cosine_similarity` |
| `is_aligned` | `True` if drift ≤ threshold |
| `realignment_triggered` | `True` if callback/warning was fired |

### `cosine_similarity(a, b)`

Utility function – returns the cosine similarity between two vectors.
Vectors are zero-padded to equal length if necessary.

---

## Running the Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Project Structure

```
sip/
├── __init__.py            # Public re-exports
├── anchor.py              # SemanticAnchor – captures the origin embedding
├── embeddings.py          # Default TF-IDF embedding (no API key required)
├── guard.py               # SIPGuard – gatekeeper with ALLOW/WARN/BLOCK/REALIGN decisions
├── observer.py            # FidelityObserver – drift computation & history
├── protocol.py            # StateIntegrityProtocol – top-level orchestrator
└── integrations/
    ├── __init__.py
    └── crew_guard.py      # CrewIntegrityManager – plug-and-play CrewAI step_callback
tests/
└── test_sip.py            # 40 pytest tests
```

---

## ☁️ SIP Cloud — Production Upgrade

The open-source SDK is free forever.  For teams running agents at scale, **SIP Cloud** adds:

| Feature | Open-Source | SIP Cloud |
|---|---|---|
| Drift detection & realignment | ✅ | ✅ |
| CrewAI / LangChain integration | ✅ | ✅ |
| Hosted dashboard & audit logs | ❌ | ✅ |
| Team collaboration & alerts | ❌ | ✅ |
| Compliance-ready PDF reports | ❌ | ✅ |
| Priority support | ❌ | ✅ |

**[→ Join the Early-Access Waitlist](https://forms.gle/placeholder)** — limited spots for founding teams.

---

## Licence

MIT
---
### 🚩 Safety & Liability Disclaimer
* **Experimental Use:** This protocol is currently in a research/beta stage. It is designed to assist in monitoring AI reliability but should not be the sole decision-maker in life-critical or high-risk financial environments.
* **No Liability:** The authors and contributors are not responsible for any misuse, data loss, or unintended consequences resulting from the integration of this protocol. 
* **Privacy:** Ensure you anonymize sensitive patient or customer data before running fidelity audits to remain compliant with local regulations.


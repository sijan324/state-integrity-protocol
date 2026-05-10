# State Integrity Protocol (SIP) 🧬

[![SIP Test Suite](https://github.com)](https://github.com/sijan324/state-integrity-protocol/actions)
![License: AGPL-3.0](shields.io)
![Python: 3.10+](shields.io)

A specialized enterprise auditing protocol to detect and measure **State Decay** (information fidelity loss) in multi-agent AI pipelines and complex LLM chains.

---

## ⚡ The Live Demo

Test your own multi-agent logs live on our cloud dashboard:  
👉 **[State Flow Lens Interactive App](https://streamlit.app)**

---

## 🚨 The Problem: State Decay in AI Agents

Current multi-agent architectures (LangChain, CrewAI, AutoGPT) suffer from **State Decay**, where context passes through nodes and loses structural fidelity, leading to hallucinations, wasted tokens, and systemic failure.

## 🛡️ The Solution: Fidelity-Flow Observation

SIP uses a mathematical **Semantic Anchor** to monitor the *Internal State* of the AI network via custom vectorized cosine distance algorithms, ensuring goal retention.

### Key Capabilities
*   **Real-Time Drift Isolation:** Instant monitoring of intent-to-output vector alignment.
*   **Contextual Guardrails:** Programmatic logic gates that halt/realign agents to save tokens.
*   **Token Loss Optimization:** Calculates the precise dollar exposure of unaligned model loops.

### Technical Workflow
1.  **Anchor:** Captures the vector embedding of the initial prompt objective.
2.  **Observe:** Computes `drift = 1 − cosine_similarity` at each step.
3.  **Trigger:** Throws errors or triggers callbacks if the delta exceeds the threshold (`default = 0.15`).

---

## 💼 SIP Enterprise Cloud (Paid Features)

For enterprise-scale reliability monitoring, contact the author via email:
📥 **[Request an Enterprise Trial & Data Room Access](mailto:sijangautamx@://gmail.com)**

---

## ⚙️ Installation

```bash
pip install -e .
```

## 🚀 Quick Start

```python
from sip import StateIntegrityProtocol

# Initialize with 15% Max Drift Allowance
sip = StateIntegrityProtocol(threshold=0.15)

# Step 1 – Set Ground Truth
sip.anchor("Summarise the report in three bullets.")

# Step 2 – Measure Semantic Decay
result = sip.observe("Here are three bullet points from the report.")
print(f"Drift: {result.drift:.4f} | Aligned: {result.is_aligned}")
```

---

## 📊 API Technical Reference


| Method / Property | Description |
|---|---|
| `anchor(prompt)` | Instantiates the foundational semantic vector truth |
| `observe(output)` | Computes immediate mathematical cosine similarity delta |
| `is_aligned` | Returns `True` if within threshold |
| `last_drift` | Returns raw drift metric |

---

## 🧪 Testing Coverage

The protocol is validated via 40+ automated test conditions.

```bash
pip install pytest
pytest tests/ -v
```

---

## ⚖️ License
This project is protected under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
****

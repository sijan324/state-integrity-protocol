# State Integrity Protocol (SIP) 🧬

[![SIP Test Suite](https://github.com/sijan324/state-integrity-protocol/actions/workflows/test.yml/badge.svg)](https://github.com/sijan324/state-integrity-protocol/actions)
![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

State Integrity Protocol helps teams catch when an AI workflow drifts away from the original task before it creates rework, bad outputs, and wasted spend.

## The one pain this product solves

AI agents often start with the right goal and quietly end somewhere else.

That drift shows up as:

- wrong summaries
- off-task tool calls
- extra review time
- wasted model spend

SIP gives you a simple way to anchor the original intent, measure drift at each step, and trigger intervention when the workflow is no longer aligned.

## What SIP does

1. **Anchor the goal** with the original prompt or task.
2. **Observe each downstream step** in the workflow.
3. **Measure semantic drift** against the anchor.
4. **Warn or trigger a callback** when drift crosses your threshold.

## Why this matters

If you run AI in any workflow where correctness matters, drift is expensive.

SIP is built for teams that want to answer:

- Is this agent still doing the job we asked it to do?
- Which step started to drift?
- When should we stop the run or route it to a human?

## Live demo

Try the hosted demo:
👉 **[State Flow Lens Interactive App](https://state-integrity-protocol-iwxuqugbbhnlsmz655r2kz.streamlit.app/)**

## Installation

```bash
pip install -e .
```

## Quick start

```python
from sip import StateIntegrityProtocol

sip = StateIntegrityProtocol(threshold=0.15)

sip.anchor("Summarise the report in three bullets.")

result = sip.observe("Here are three bullet points from the report.")
print(f"Drift: {result.drift:.4f} | Aligned: {result.is_aligned}")
```

## API reference

| Method / Property | Description |
|---|---|
| `anchor(prompt)` | Capture the original task intent |
| `observe(output)` | Measure drift for a workflow step |
| `is_aligned` | Returns `True` if the latest step is within threshold |
| `last_drift` | Returns the latest drift score |
| `history` | Returns the recorded transition history |

## Testing

```bash
python -m pytest tests/ -v
```

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

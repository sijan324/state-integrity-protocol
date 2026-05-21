# State Integrity Protocol (SIP) 🧬

[![SIP Test Suite](https://github.com/sijan324/state-integrity-protocol/actions/workflows/test.yml/badge.svg)](https://github.com/sijan324/state-integrity-protocol/actions)
![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

State Integrity Protocol helps teams running production AI agents catch when a workflow drifts away from the original task before it creates rework, bad outputs, and wasted spend.

## The one pain this product solves

Production AI agents often start with the right goal and quietly end somewhere else.

That drift shows up as:

- wrong summaries
- off-task tool calls
- extra review time
- wasted model spend

SIP gives you a simple way to anchor the original intent, measure drift at each step, and trigger intervention when the workflow is no longer aligned.

## Who this is for right now

SIP is intentionally narrow.

Right now it is built for:

- teams shipping production AI agents
- workflows where a bad off-task run creates review debt or wasted spend
- operators who need a simple drift signal before adding heavier observability stacks

## The narrow wedge

One ICP: teams operating production AI agents.

One use case: detect off-task agent runs before they create expensive cleanup work.

One promise: show where a run started drifting so a team can stop it, reroute it, or review it faster.

## What SIP does

1. **Anchor the goal** with the original prompt or task.
2. **Observe each downstream step** in the workflow.
3. **Measure semantic drift** against the anchor.
4. **Warn or trigger a callback** when drift crosses your threshold.

## Why this matters

If you run production AI agents in a workflow where correctness matters, drift is expensive.

SIP is built for teams that want to answer:

- Is this agent still doing the job we asked it to do?
- Which step started to drift?
- When should we stop the run or route it to a human?

## Pilot-ready positioning

If you are testing SIP with early users, keep the motion simple:

- start with one workflow that already creates manual review pain
- anchor the task at run start
- measure each downstream step
- trigger review only when drift crosses a threshold
- use the drift log to show where review time and wasted spend come from

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

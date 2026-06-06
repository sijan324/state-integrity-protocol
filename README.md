# State Integrity Protocol (SIP)

State Integrity Protocol is a minimal Python SDK for tracking semantic drift and state consistency in LLM workflows.

This SDK is used by higher-level applications like AI Sentinel.

## Installation

```bash
pip install -e .
```

## Core API

- `anchor(prompt)` — define the initial intent state
- `observe(output)` — evaluate drift from the anchored intent
- `is_aligned` — boolean alignment signal
- `last_drift` — latest drift score
- `history` — full transition log
- `SIPMiddlewarePipeline` — optional anchor → checks → verify/sign → repair loop orchestration

## Example

```python
from sip import StateIntegrityProtocol

sip = StateIntegrityProtocol()

sip.anchor("User wants refund policy")
result = sip.observe("Refunds are only available within 7 days")

print(result.is_aligned, result.last_drift)
```

`result.last_drift` is provided as the latest drift-score alias on `ObservationResult` (`result.drift` is also available).

## Middleware + Verification Flow

You can run an optional middleware flow for:

1. Drift check against the anchored intent
2. Intent-alignment check
3. Constraint-violation check
4. `verify_and_sign()` decision
5. Accepted output or repair loop

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

print(result.status)                   # accepted | repair_required | rejected
print(result.decision.signature)       # deterministic signature over decision payload
print(result.decision.failure_codes)   # machine-readable failure causes
print(result.repair_instructions)      # regeneration guidance when not accepted
```

### Policy knobs

- `drift_threshold`: max allowed semantic drift
- `intent_alignment_threshold`: minimum token-overlap score with anchored intent
- `constraints`: blocked phrases checked against output text
- `max_retries`: max repair attempts before terminal rejection
- `signer`: optional custom signing function for `verify_and_sign()`

## Exposed SDK types

- `StateIntegrityProtocol`
- `SemanticAnchor`
- `ObservationResult`
- `SIPMiddlewarePipeline`
- transition utilities for state tracking

## Testing

```bash
python -m pip install -e '.[dev]'
python -m pytest tests/ -v
```


## Licensing & Commercial Use

- Core SDK (SIP) is licensed under AGPL-3.0
- **AI Sentinel** (the full monitoring system) is a separate commercial product and is **not open source**.
- Companies can use the SIP SDK freely under AGPL terms.
- For commercial hosted service, white-label, or custom enterprise version — please contact us.

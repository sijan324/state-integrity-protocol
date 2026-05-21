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

## Example

```python
from sip import StateIntegrityProtocol

sip = StateIntegrityProtocol()

sip.anchor("User wants refund policy")
result = sip.observe("Refunds are only available within 7 days")

print(result.is_aligned, result.last_drift)
```

## Exposed SDK types

- `StateIntegrityProtocol`
- `SemanticAnchor`
- `ObservationResult`
- transition utilities for state tracking

## Testing

```bash
python -m pip install -e '.[dev]'
python -m pytest tests/ -v
```

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

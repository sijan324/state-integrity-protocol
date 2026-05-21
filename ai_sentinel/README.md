# AI Sentinel

A FastAPI service that audits AI-generated responses for hallucinations, factual inconsistencies, and unsafe content. When a problem is detected it fires a Slack alert. A Streamlit dashboard provides a browser UI on top of the same API.

> **Vision:** Make AI outputs auditable and observable — one response at a time.

## Files

```
ai_sentinel/
├── main.py          # FastAPI app  —  GET / and POST /audit
├── detector.py      # Evaluator    —  Groq Llama 3 or rule-based fallback
├── slack.py         # Slack alert  —  Incoming Webhook dispatcher
├── app.py           # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Setup

```bash
cd ai_sentinel
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | No | Enables Groq Llama 3 evaluation. Falls back to rule-based if unset. |
| `SLACK_WEBHOOK_URL` | No | Slack Incoming Webhook for FAIL alerts. Logs to console if unset. |

```bash
export GROQ_API_KEY="gsk_..."
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

## Run

**Backend**

```bash
uvicorn main:app --reload
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs  (interactive API docs)
```

**Streamlit dashboard** (in a second terminal)

```bash
streamlit run app.py
# → http://localhost:8501
```

## Usage

### POST /audit

```bash
curl -X POST http://127.0.0.1:8000/audit \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "What is the capital of France?",
    "ai_response": "The capital of France is Paris.",
    "context": "France is a country in Western Europe."
  }'
```

```json
{"verdict": "PASS", "alert_sent": false}
```

Trigger a FAIL (bare-number spam with no context):

```bash
curl -X POST http://127.0.0.1:8000/audit \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Users?", "ai_response": "1000000 500000 250000 75000"}'
```

```json
{"verdict": "FAIL", "alert_sent": true}
```

**Request body**

| Field | Type | Required |
|---|---|---|
| `user_query` | string | Yes |
| `ai_response` | string | Yes |
| `context` | string | No |

**Response**

| Field | Type | Description |
|---|---|---|
| `verdict` | `"PASS"` \| `"FAIL"` | Evaluation result |
| `alert_sent` | boolean | `true` if a Slack message was dispatched |

### GET /

```json
{"status": "ok", "service": "AI Sentinel"}
```

## Streamlit dashboard

Open `http://localhost:8501` after starting the backend and the dashboard.

- Enter **User Query**, **AI Response**, and (optionally) **Context**
- Click **Run Audit**
- Result is shown in green (PASS) or red (FAIL)
- If a Slack alert was sent, a notification appears below the verdict

## How evaluation works

**With `GROQ_API_KEY`**  
Calls `llama3-8b-8192` via the Groq API. System prompt instructs the model to reply with only `PASS` or `FAIL`. Falls back to rule-based on any API error.

**Without `GROQ_API_KEY` (rule-based)**  
Two checks run on every request:

1. **Bare-number ratio** — if more than 25 % of the words in the AI response are standalone numbers, the response is flagged.
2. **Contradiction detection** — if the context and AI response share meaningful content words but have opposing negation signals (`not`, `never`, `false`, etc.), the response is flagged.

## Slack alerts

A `FAIL` verdict sends this message to your webhook:

```
⚠️ AI Sentinel Alert

User Query: <query>
AI Response: <response>

Risk Detected: Possible hallucination or inconsistency
```

To get a webhook URL: go to https://api.slack.com/apps → create an app → enable Incoming Webhooks → copy the URL.


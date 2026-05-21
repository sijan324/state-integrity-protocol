# AI Sentinel 🛡️

A minimal FastAPI backend that receives AI outputs, checks them for potential
hallucination or risk, and sends Slack alerts when issues are detected.

---

## Project Structure

```
ai_sentinel/
├── main.py          # FastAPI application & /audit endpoint
├── detector.py      # Evaluation logic (Groq API or rule-based fallback)
├── slack.py         # Slack Incoming Webhook alert helper
├── requirements.txt # Python dependencies
└── README.md        # This file
```

---

## Prerequisites

- Python 3.10+
- A Slack Incoming Webhook URL *(optional – alerts are printed to the console if not set)*
- A Groq API key *(optional – falls back to rule-based evaluation if not set)*

---

## Installation

```bash
# 1. Navigate to the ai_sentinel directory
cd ai_sentinel

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Set environment variables before starting the server:

| Variable            | Required | Description                                      |
|---------------------|----------|--------------------------------------------------|
| `GROQ_API_KEY`      | No       | Groq API key – enables Llama 3 evaluation        |
| `SLACK_WEBHOOK_URL` | No       | Slack Incoming Webhook URL for FAIL alerts       |

```bash
export GROQ_API_KEY="gsk_..."
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

---

## Running the Server

```bash
uvicorn main:app --reload
```

The server starts at **http://127.0.0.1:8000**.

Interactive API docs are available at **http://127.0.0.1:8000/docs**.

---

## Example Requests

### Healthy response – expects PASS

```bash
curl -X POST http://127.0.0.1:8000/audit \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "What is the capital of France?",
    "ai_response": "The capital of France is Paris.",
    "context": "France is a country in Western Europe."
  }'
```

Expected response:
```json
{"verdict": "PASS", "alert_sent": false}
```

---

### Suspicious response – expects FAIL (rule-based)

```bash
curl -X POST http://127.0.0.1:8000/audit \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "How many users does our app have?",
    "ai_response": "1000000 500000 250000 75000",
    "context": ""
  }'
```

Expected response:
```json
{"verdict": "FAIL", "alert_sent": true}
```

*(When `SLACK_WEBHOOK_URL` is not set, the alert is printed to the console.)*

---

### Contradiction detection – expects FAIL (rule-based)

```bash
curl -X POST http://127.0.0.1:8000/audit \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Is the service available?",
    "ai_response": "Yes, the service is fully operational and available.",
    "context": "The service is not available due to maintenance."
  }'
```

---

## How the Evaluation Works

### Option A – Groq API (Llama 3) *(when `GROQ_API_KEY` is set)*

The AI response is sent to the `llama3-8b-8192` model along with a strict
system prompt that instructs it to return only `PASS` or `FAIL`.

### Option B – Rule-based fallback *(when no API key is available)*

Two heuristics are applied:

1. **Bare-number ratio** – if more than 25 % of the words in the AI response
   are standalone numbers (no surrounding textual context), the response is
   flagged as suspicious.
2. **Contradiction detection** – if the context contains negation words (*not,
   never, no, false, …*) that are absent from the response (or vice-versa) and
   they share meaningful content words, the response is flagged as a potential
   contradiction.

---

## How Slack Alerts Work

When the verdict is `FAIL`, `slack.py` sends a `POST` request to the
configured Slack Incoming Webhook URL with a formatted message:

```
⚠️ AI Sentinel Alert

User Query: <query>
AI Response: <response>

Risk Detected: Possible hallucination or inconsistency
```

To set up a webhook:
1. Go to **https://api.slack.com/apps** and create a new app.
2. Enable **Incoming Webhooks** and add a webhook to your workspace.
3. Copy the webhook URL and set it as `SLACK_WEBHOOK_URL`.

---

## API Reference

### `GET /`
Health check – returns `{"status": "ok", "service": "AI Sentinel"}`.

### `POST /audit`
Evaluate an AI response.

**Request body:**
```json
{
  "user_query": "string",
  "ai_response": "string",
  "context": "string (optional)"
}
```

**Response:**
```json
{
  "verdict": "PASS | FAIL",
  "alert_sent": true | false
}
```

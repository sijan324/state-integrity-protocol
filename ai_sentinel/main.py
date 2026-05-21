"""
main.py – AI Sentinel FastAPI application.

Run with:
    uvicorn main:app --reload
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from detector import evaluate
from slack import send_alert

app = FastAPI(
    title="AI Sentinel",
    description="Detect hallucinations / risk in AI outputs and alert via Slack.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class AuditRequest(BaseModel):
    user_query: str
    ai_response: str
    context: Optional[str] = ""


class AuditResponse(BaseModel):
    verdict: str          # "PASS" or "FAIL"
    alert_sent: bool      # True when a Slack alert was dispatched


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/", tags=["health"])
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "service": "AI Sentinel"}


@app.post("/audit", response_model=AuditResponse, tags=["audit"])
def audit(request: AuditRequest):
    """
    Evaluate an AI response for hallucinations or risk.

    - **user_query**: The original question posed to the AI.
    - **ai_response**: The AI-generated answer to evaluate.
    - **context**: Optional background information to cross-check the response against.
    """
    verdict = evaluate(
        user_query=request.user_query,
        ai_response=request.ai_response,
        context=request.context or "",
    )

    alert_sent = False
    if verdict == "FAIL":
        send_alert(
            user_query=request.user_query,
            ai_response=request.ai_response,
        )
        alert_sent = True

    return AuditResponse(verdict=verdict, alert_sent=alert_sent)

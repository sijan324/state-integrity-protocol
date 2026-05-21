"""
slack.py – Slack alert helper for AI Sentinel.

Reads SLACK_WEBHOOK_URL from the environment and posts a formatted alert
message when a FAIL verdict is produced.
"""

from __future__ import annotations

import os

import requests

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def send_alert(user_query: str, ai_response: str) -> None:
    """
    Send a Slack alert for a FAIL verdict.

    Does nothing (with a console warning) when SLACK_WEBHOOK_URL is not set.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", SLACK_WEBHOOK_URL)
    if not webhook_url:
        print(
            "[AI Sentinel] SLACK_WEBHOOK_URL not set – skipping Slack alert.\n"
            f"  Query   : {user_query}\n"
            f"  Response: {ai_response}"
        )
        return

    message = (
        "⚠️ *AI Sentinel Alert*\n\n"
        f"*User Query:* {user_query}\n"
        f"*AI Response:* {ai_response}\n\n"
        "_Risk Detected: Possible hallucination or inconsistency_"
    )

    payload = {"text": message}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[AI Sentinel] Failed to send Slack alert: {exc}")

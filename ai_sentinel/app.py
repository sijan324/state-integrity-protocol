"""
app.py – Streamlit dashboard for AI Sentinel.

Run with:
    streamlit run app.py

Requires the FastAPI backend to be running at http://localhost:8000.
"""

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000/audit"

st.set_page_config(page_title="AI Sentinel", page_icon="🛡️", layout="centered")

st.title("🛡️ AI Sentinel")
st.caption("Audit AI-generated responses for hallucinations and inconsistencies.")

st.divider()

user_query = st.text_input("User Query", placeholder="What did you ask the AI?")
ai_response = st.text_area("AI Response", placeholder="What did the AI answer?", height=120)
context = st.text_area("Context (optional)", placeholder="Background information to cross-check against.", height=80)

st.divider()

if st.button("Run Audit", type="primary", use_container_width=True):
    if not user_query.strip() or not ai_response.strip():
        st.warning("User Query and AI Response are required.")
    else:
        with st.spinner("Evaluating…"):
            try:
                resp = requests.post(
                    BACKEND_URL,
                    json={
                        "user_query": user_query,
                        "ai_response": ai_response,
                        "context": context or None,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException as exc:
                st.error(f"Could not reach backend: {exc}")
                st.stop()

        verdict = data.get("verdict", "")
        alert_sent = data.get("alert_sent", False)

        if verdict == "PASS":
            st.success("✅ PASS — Response looks safe.")
        else:
            st.error("❌ FAIL — Potential hallucination or inconsistency detected.")

        if alert_sent:
            st.info("📣 Slack alert sent.")
        elif verdict == "FAIL":
            st.caption("Slack alert not sent (SLACK_WEBHOOK_URL not configured).")

import streamlit as st
import time
from datetime import datetime
import hashlib
import json

from middleware import SIPMiddlewarePipeline
from telemetry import emit_event, load_events

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="SIP AI Integrity Checker",
    page_icon="🧠",
    layout="centered"
)

# -----------------------------
# SIP PIPELINE (NO HEAVY MODEL)
# -----------------------------
@st.cache_resource
def get_sip():
    return SIPMiddlewarePipeline(
        drift_threshold=0.65,
        intent_alignment_threshold=0.3,
        max_retries=2
    )

sip = get_sip()

# -----------------------------
# TELEMETRY CACHE (FAST LOAD)
# -----------------------------
@st.cache_data(ttl=5)
def get_events():
    return load_events(10)

# -----------------------------
# UI
# -----------------------------
st.title("🧠 SIP AI Integrity Checker")
st.caption("Detect when AI deviates from your intent")

st.divider()

# -----------------------------
# INPUT
# -----------------------------
intent = st.text_area("Intent (What you asked AI)", height=80)
output = st.text_area("Output (What AI produced)", height=80)

run = st.button("🚀 Check Integrity", use_container_width=True)

# -----------------------------
# RUN SIP
# -----------------------------
if run:
    if not intent or not output:
        st.warning("Please fill both fields")
        st.stop()

    start = time.time()

    sip.anchor(intent)
    result = sip.run(output)

    latency = round(time.time() - start, 3)

    status = result.status

    st.divider()
    st.subheader("Result")

    if status == "accepted":
        st.success("🟢 AI followed your instruction correctly")
    elif status == "repair_required":
        st.warning("🟡 AI slightly deviated from intent")
    else:
        st.error("🔴 AI failed to follow instruction")

    # -----------------------------
    # SIMPLE EXPLANATION
    # -----------------------------
    st.markdown("### What happened")

    mapping = {
        "drift": "Meaning changed",
        "intent_alignment": "Did not fully follow intent",
        "constraint_violation": "Broke rule or constraint"
    }

    if result.decision.failure_codes:
        for c in result.decision.failure_codes:
            st.write("•", mapping.get(c, c))
    else:
        st.write("• Perfect match")

    # -----------------------------
    # TECH DETAILS
    # -----------------------------
    with st.expander("Technical details"):
        st.json({
            "status": status,
            "latency": latency,
            "drift": result.evaluation.drift_check.drift,
            "alignment": result.evaluation.intent_alignment.score,
            "signature": result.decision.signature
        })

    # -----------------------------
    # TELEMETRY (LIGHTWEIGHT)
    # -----------------------------
    event = {
        "event_type": "sip_check",
        "intent": intent,
        "output": output,
        "status": status,
        "drift": result.evaluation.drift_check.drift,
        "alignment": result.evaluation.intent_alignment.score,
        "signature": result.decision.signature
    }

    emit_event(event)

# -----------------------------
# TELEMETRY DASHBOARD
# -----------------------------
events = get_events()

if events:
    st.divider()
    st.subheader("📡 Recent SIP Activity")

    for e in reversed(events):
        icon = "🟢" if e["status"] == "accepted" else "🟡"
        st.write(f"{icon} {e['status']} | {e['intent'][:40]}...")
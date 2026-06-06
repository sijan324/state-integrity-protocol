import streamlit as st
import time
from datetime import datetime
import hashlib

from sip import SIPMiddlewarePipeline
from telemetry import emit_event  # 🚀 REAL TELEMETRY IMPORTED HERE

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Intent Checker",
    page_icon="🧠",
    layout="centered"
)

# -----------------------------
# SIP BACKEND (HIDDEN INTELLIGENCE)
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
# SESSION STORAGE (FOR UI DISPLAY)
# -----------------------------
if "telemetry" not in st.session_state:
    st.session_state.telemetry = []

# -----------------------------
# UI HEADER (NON-TECH LANGUAGE)
# -----------------------------
st.title("🧠 AI Output Checker")
st.caption("Make sure AI actually did what you asked — before you trust it.")

st.markdown("""
### ⚡ Why this exists
AI sometimes:
- misunderstands your request
- changes numbers
- adds unwanted actions
- ignores constraints

👉 This tool checks that automatically.
""")

st.divider()

# -----------------------------
# QUICK EXAMPLES (REAL WORLD)
# -----------------------------
st.subheader("⚡ Try examples")

col1, col2, col3 = st.columns(3)

def set_case(intent, output):
    st.session_state.intent = intent
    st.session_state.output = output

with col1:
    st.button("💸 Money Error", on_click=set_case,
              args=("Refund $50 to user", "Refund $500 to user"))

with col2:
    st.button("⚠️ Wrong Action", on_click=set_case,
              args=("Delete my account", "Create a new account"))

with col3:
    st.button("✅ Correct Case", on_click=set_case,
              args=("Cancel subscription", "Your subscription is cancelled"))

st.divider()

# -----------------------------
# INPUT
# -----------------------------
intent = st.text_area("🧾 What did you ask AI to do?", height=80, key="intent")
output = st.text_area("🤖 What AI actually said/did", height=80, key="output")

run = st.button("🔍 Check AI Output", type="primary", use_container_width=True)

# -----------------------------
# EXECUTION
# -----------------------------
if run:
    if not intent or not output:
        st.warning("Please fill both fields.")
        st.stop()

    start = time.time()

    sip.anchor(intent)
    result = sip.run(output)

    latency = round(time.time() - start, 3)
    status = result.status

    # -----------------------------
    # SIMPLE HUMAN RESULT (NO TECH WORDS)
    # -----------------------------
    st.divider()
    st.subheader("📊 Result")

    if status == "accepted":
        st.success("🟢 Good — AI understood your request correctly.")
    elif status == "repair_required":
        st.warning("🟡 AI slightly misunderstood your request.")
    else:
        st.error("🔴 AI got it wrong or unsafe.")

    # -----------------------------
    # SIMPLE BREAKDOWN (HUMAN READABLE)
    # -----------------------------
    st.markdown("### What happened")

    failure_map = {
        "drift": "AI changed the meaning",
        "intent_alignment": "AI didn’t fully understand your request",
        "constraint_violation": "AI broke a rule or instruction"
    }

    if result.decision.failure_codes:
        for code in result.decision.failure_codes:
            st.write("• " + failure_map.get(code, "Unknown issue"))
    else:
        st.write("• Everything matched your request")

    # -----------------------------
    # OPTIONAL DETAILS (COLLAPSIBLE)
    # -----------------------------
    with st.expander("🔬 Technical details (for developers)"):
        st.json({
            "status": status,
            "latency": latency,
            "failure_codes": result.decision.failure_codes,
            "signature": result.decision.signature
        })

    # -----------------------------
    # 🧬 EMIT EVENT TO IMMUTABLE TELEMETRY STORE (JSONL)
    # -----------------------------
    # Privacy Move: If enterprise clients want anonymity, we hash payloads
    telemetry_payload = {
        "event_type": "sip_runtime_check",
        "intent": intent, 
        "output": output,
        "status": status.lower(),
        "latency": latency,
        "failure_codes": list(result.decision.failure_codes),
        "signature": result.decision.signature
    }
    
    # Write to local JSONL log file via our core module
    emit_event(telemetry_payload)

    # local memory refresh for immediate UI sync
    st.session_state.telemetry.append(telemetry_payload)

# -----------------------------
# BACKGROUND HISTORY (THE NETWORK MOAT LAYER)
# -----------------------------
from telemetry import load_events

# Load real telemetry lines from sip_events.jsonl instead of just session state
persisted_events = load_events(10)

if persisted_events:
    st.divider()
    st.subheader("📡 Live SIP Event Stream (Telemetry Ledger)")
    st.caption("Immutable real-time logs loaded directly from the system storage layer.")

    for e in reversed(persisted_events):
        icon = "🟢" if e["status"] == "accepted" else ("🟡" if e["status"] == "repair_required" else "🔴")
        with st.expander(f"{icon} Status: {e['status'].upper()} | Signature: {e['signature'][:8]}"):
            st.json(e)
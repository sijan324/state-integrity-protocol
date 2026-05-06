import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sip.protocol import StateIntegrityProtocol

# --- 1. Page Config ---
st.set_page_config(page_title="State Flow Lens", layout="wide")

# Custom UI for 2-Second Understanding
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 15px; border-left: 10px solid #2563eb; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧬 State Flow Lens")
st.subheader("Is your AI wasting your money? Find out in seconds.")

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.write("### 📥 1. Paste your AI Logs")
    intent = st.text_input(
        "What was the AI supposed to do?", value="Analyze Q3 Financials"
    )
    logs = st.text_area(
        "What did the AI actually say? (One line per step)",
        height=250,
        value="Step 1: Extracting revenue\nStep 2: Checking pizza prices\nStep 3: Comparing crust types",
    )
    runs = st.number_input("How many times does this run per month?", value=1000)
    audit_btn = st.button("🚀 Check for Money Leakage", use_container_width=True)

# --- 2. Simple Logic ---
sip = StateIntegrityProtocol(threshold=0.35)

if audit_btn and logs and intent:
    steps = [s.strip() for s in logs.split("\n") if s.strip()]
    sip.anchor(intent)
    drifts = [sip.observe(s).drift for s in steps]
    avg_drift = np.mean(drifts)

    # Simple Money Calculation ($0.03 is the industry avg)
    monthly_waste = (avg_drift * 100 * 0.03) * runs

    with col_out:
        st.write("### 📊 2. Your Results")

        # Big Visual Metrics
        m1, m2 = st.columns(2)

        # Color coding the result
        if avg_drift < 0.20:
            status = "✅ HEALTHY"
            color = "inverse"
            msg = "Your AI is on track. Efficiency is high."
        elif avg_drift < 0.40:
            status = "⚠️ WARNING"
            color = "off"
            msg = "Your AI is starting to drift. You are losing money."
        else:
            status = "🚨 CRITICAL"
            color = "normal"
            msg = "Your AI has failed. Most of this compute is wasted."

        m1.metric("System Health", status)
        m2.metric(
            "Monthly Money Leakage",
            f"${round(monthly_waste, 2)}",
            delta="Waste",
            delta_color=color,
        )

        # Simple Graph
        df = pd.DataFrame({"Step": range(1, len(drifts) + 1), "WasteLevel": drifts})
        fig = px.bar(
            df,
            x="Step",
            y="WasteLevel",
            title="Where is the money leaking?",
            color="WasteLevel",
            color_continuous_scale=["green", "yellow", "red"],
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(msg)

st.divider()
st.write("📩 **Want to stop the leak?** Contact: sijangautamx@gmail.com")

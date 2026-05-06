import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sip.protocol import StateIntegrityProtocol

st.set_page_config(page_title="State Flow Lens", layout="wide")

st.title("🧬 State Flow Lens")
st.markdown("Real-time detection of intent loss in AI workflows.")

# --- INPUT ---
initial_intent = st.text_input(
    "System Anchor", value="Summarize Q3 earnings call into key bullet points"
)

raw_steps = st.text_area(
    "Agent Steps",
    value="""Extract revenue data
Analyze CEO commentary
Summarize key financial highlights
Generate final bullet points""",
)

run = st.button("🚀 Run Analysis", use_container_width=True)

# --- ADVANCED TOGGLE ---
advanced = st.checkbox("🔓 Show Advanced Analytics")

sip = StateIntegrityProtocol(threshold=0.35)

if run:
    steps = [s.strip() for s in raw_steps.split("\n") if s.strip()]

    sip.anchor(initial_intent)
    results = [sip.observe(s) for s in steps]
    drifts = [r.drift for r in results]

    avg_drift = np.mean(drifts)
    peak_drift = max(drifts)

    st.subheader("📊 Core Insights")

    col1, col2 = st.columns(2)
    col1.metric("Avg Intent Loss", f"{round(avg_drift * 100, 1)}%")
    col2.metric("Peak Drift", f"{round(peak_drift, 2)}")

    # Graph
    df = pd.DataFrame({"Step": range(1, len(drifts) + 1), "Loss": drifts})
    fig = px.area(
        df, x="Step", y="Loss", title="Intent Drift Over Time", template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Simple insight
    if avg_drift > 0.35:
        st.warning("⚠️ High intent decay detected. System may be misaligned.")
    else:
        st.success("✅ System alignment is stable.")

    # --- ADVANCED SECTION ---
    if advanced:
        st.divider()
        st.subheader("💰 Advanced Analytics")

        cost_per_token = st.number_input("Cost per 1k tokens ($)", value=0.03)
        runs_per_month = st.number_input("Monthly runs", value=1000)

        monthly_waste = ((avg_drift * 100) * cost_per_token) * runs_per_month

        col3, col4 = st.columns(2)
        col3.metric("Estimated Monthly Waste", f"${round(monthly_waste, 2)}")
        col4.metric("Efficiency Score", f"{round((1 - avg_drift) * 100, 1)}%")

        st.info("💡 Higher drift directly increases operational cost in AI systems.")

# --- CTA ---
st.divider()
st.markdown("### 🚀 Need full enterprise audit & reporting?")
st.markdown("📩 Contact: sijangautamx@gmail.com")

st.caption("State Flow Lens | Open Core Demo")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sip.protocol import StateIntegrityProtocol

# --- CONFIG ---
st.set_page_config(page_title="State Flow Lens", layout="centered")

# --- STYLE ---
st.markdown(
    """
<style>
.main {
    background-color: #0e1117;
    color: #ffffff;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- TITLE ---
st.title("🧬 State Flow Lens")
st.markdown("Detect intent loss in AI workflows in seconds.")

# --- DEMO INPUT ---
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

run_demo = st.button("🚀 Run Demo", use_container_width=True)

# --- SIP ENGINE ---
sip = StateIntegrityProtocol(threshold=0.35)

# --- RUN DEMO ---
if run_demo:
    steps = [s.strip() for s in raw_steps.split("\n") if s.strip()]

    try:
        sip.anchor(initial_intent)
        results = [sip.observe(s) for s in steps]
        drifts = [r.drift for r in results]

        avg_drift = np.mean(drifts)

        st.subheader("📊 Results")

        col1, col2 = st.columns(2)
        col1.metric("Avg Intent Loss", f"{round(avg_drift * 100, 1)}%")
        col2.metric("Steps Analyzed", len(steps))

        df = pd.DataFrame({"Step": range(1, len(drifts) + 1), "Loss": drifts})

        fig = px.line(
            df,
            x="Step",
            y="Loss",
            title="Intent Drift Over Steps",
            template="plotly_dark",
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# --- CTA ---
st.divider()
st.markdown("### 🚀 Need full enterprise audit & reports?")
st.markdown("📩 Contact: sijangautamx@gmail.com")

# --- FOOTER ---
st.markdown("---")
st.caption("State Flow Lens | Open Core Demo")

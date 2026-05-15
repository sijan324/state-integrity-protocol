import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sip.protocol import StateIntegrityProtocol

# =========================
# 1. PAGE CONFIG
# =========================
st.set_page_config(page_title="State Flow Lens", page_icon="🧬", layout="wide")

# =========================
# 2. CUSTOM UI
# =========================
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #2563eb;
    }
    .stButton>button {
        border-radius: 8px;
        height: 3em;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 3. HEADER
# =========================
st.title("🧬 State Flow Lens")
st.subheader("Catch when your AI workflow drifts off task before it creates rework.")

st.markdown(
    "💡 Paste your AI workflow and see where it stops following the original goal."
)

# =========================
# 4. LAYOUT
# =========================
col_in, col_out = st.columns([1, 1.5])

# =========================
# 5. INPUT SECTION
# =========================
with col_in:
    st.write("### 📥 Input")

    intent = st.text_input("Original Goal", value="Analyze Q3 Financials")

    logs = st.text_area(
        "AI Steps (one per line)",
        height=250,
        value="""Extract revenue data
Analyze performance trends
Compare year-over-year growth
Generate summary report""",
    )

    runs = st.number_input("Monthly Runs", value=1000, step=100)

    run_btn = st.button("🚀 Analyze AI Drift", use_container_width=True)

# =========================
# 6. ENGINE
# =========================
sip = StateIntegrityProtocol(threshold=0.35)

# =========================
# 7. OUTPUT
# =========================
if run_btn and intent and logs:
    steps = [s.strip() for s in logs.split("\n") if s.strip()]

    try:
        sip.anchor(intent)
        drifts = [sip.observe(s).drift for s in steps]

        avg_drift = np.mean(drifts)
        peak_drift = max(drifts)

        # simple cost model
        cost_per_run = 0.03
        monthly_cost = (avg_drift * 100 * cost_per_run) * runs

        # =========================
        # RESULTS
        # =========================
        with col_out:
            st.write("### 📊 Results")

            col1, col2 = st.columns(2)

            col1.metric("Goal Drift", f"{round(avg_drift * 100, 1)}%")

            col2.metric("Peak Drift", f"{round(peak_drift, 2)}")

            # STATUS LOGIC
            if avg_drift < 0.20:
                status = "✅ Healthy"
                msg = "Your AI is aligned and efficient."
            elif avg_drift < 0.40:
                status = "⚠️ Warning"
                msg = "Your AI is drifting from its goal."
            else:
                status = "🚨 Critical"
                msg = "Severe goal loss detected. High inefficiency."

            st.subheader(status)

            st.metric(
                "Estimated Monthly Cost Loss",
                f"${round(monthly_cost, 2)}",
                delta="Hidden AI Waste",
            )

            st.info(msg)

            # =========================
            # CHART
            # =========================
            df = pd.DataFrame(
                {"Step": range(1, len(drifts) + 1), "Drift Score": drifts}
            )

            fig = px.line(
                df,
                x="Step",
                y="Drift Score",
                title="AI Goal Drift Over Time",
                markers=True,
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# =========================
# 8. FOOTER CTA
# =========================
st.divider()

st.markdown("### 💡 Stop off-task AI runs before they turn into review debt.")

st.markdown("📩 Contact: sijangautamx@gmail.com")

st.caption("State Flow Lens | AI Drift Intelligence System")

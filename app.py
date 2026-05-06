import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sip.protocol import StateIntegrityProtocol

# --- 1. Page Configuration ---
st.set_page_config(page_title="State Flow Lens | Fidelity Intelligence", layout="wide")

# Custom Professional Styling
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stButton>button { border-radius: 5px; height: 3em; background-color: #2563eb; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. Sidebar: Strategic Controls ---
st.sidebar.header("🛡️ Audit Configuration")
threshold = st.sidebar.slider("Tolerance Threshold", 0.0, 1.0, 0.35)
cost_per_token = st.sidebar.number_input(
    "Avg. Cost per 1k Tokens ($)", value=0.03, step=0.01
)

st.sidebar.divider()
st.sidebar.subheader("📈 Revenue Protection (ROI)")
runs_per_month = st.sidebar.number_input(
    "Monthly Workflow Volume", value=1000, step=100
)

# Initialize Protocol
sip = StateIntegrityProtocol(threshold=threshold)

# --- 3. Main UI Layout ---
st.title("🧬 State Flow Lens: Fidelity Intelligence")
st.caption(
    "Quantifying Semantic Entropy and Compute Leakage in Multi-Agent AI Pipelines."
)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📥 Diagnostic Input")
    initial_intent = st.text_input(
        "System Anchor (Original Intent)", placeholder="e.g., Audit Q3 revenue..."
    )
    raw_steps = st.text_area("Agent Transition Logs (One per line)", height=320)
    run_audit = st.button("🚀 Run Fidelity Audit", use_container_width=True)

# --- 4. Monitoring & Analytics Engine ---
if run_audit and raw_steps and initial_intent:
    steps = [s.strip() for s in raw_steps.split("\n") if s.strip()]

    if not steps:
        st.error("Please enter at least one agent transition log.")
    else:
        try:
            sip.anchor(initial_intent)
            results = [sip.observe(s) for s in steps]
            drifts = [r.drift for r in results]

            # Analytics Calculations
            avg_drift = np.mean(drifts)
            peak_drift = max(drifts)
            loss_per_run = (avg_drift * 100) * cost_per_token
            total_monthly_waste = loss_per_run * runs_per_month

            with col2:
                st.subheader("📊 Integrity Report")
                m1, m2, m3 = st.columns(3)
                m1.metric("Avg. Intent Decay", f"{round(avg_drift * 100, 1)}%")
                m2.metric("Peak Semantic Drift", f"{round(peak_drift, 2)}")
                m3.metric(
                    "Projected Monthly Waste",
                    f"${round(total_monthly_waste, 2)}",
                    delta="Leakage Detected",
                    delta_color="inverse",
                )

                # Visual Entropy Mapping
                df = pd.DataFrame(
                    {
                        "Step": range(1, len(drifts) + 1),
                        "Fidelity Loss": drifts,
                        "Status": [
                            "Safe" if d <= threshold else "Critical Breach"
                            for d in drifts
                        ],
                    }
                )

                fig = px.area(
                    df,
                    x="Step",
                    y="Loss",
                    color="Status",
                    title="Semantic Entropy Mapping",
                    color_discrete_map={
                        "Safe": "#10b981",
                        "Critical Breach": "#ef4444",
                    },
                    template="plotly_dark",
                )
                st.plotly_chart(fig, use_container_width=True)

            st.sidebar.success(
                f"Audit Finalized: ${round(total_monthly_waste, 2)} monthly loss identified."
            )

        except Exception as e:
            st.error(f"Audit Engine Error: {e}")

st.sidebar.info("State Flow Lens v1.2.1 | Infrastructure Verification Layer")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sip import StateIntegrityProtocol, SIPGuard

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
st.subheader("Is your AI losing focus—and costing you money? Find out in seconds.")

st.markdown(
    "💡 Paste your AI workflow and instantly detect where it drifts from the original goal."
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

    runs = st.number_input("Monthly Runs", value=1000, step=100, min_value=0)

    threshold = st.slider(
        "Drift Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.35,
        step=0.01,
        help="Realignment triggers when drift > threshold.",
    )

    cost_per_run = st.number_input(
        "Cost per Run ($) — demo model",
        value=0.03,
        step=0.01,
        min_value=0.0,
        help="Toy model input for showing potential waste impact.",
    )

    run_btn = st.button("🚀 Analyze AI Drift", use_container_width=True)

# =========================
# 6. ENGINE
# =========================
sip = StateIntegrityProtocol(threshold=threshold)
guard = SIPGuard(threshold=threshold, mode="realign")

# =========================
# 7. OUTPUT
# =========================
if run_btn and intent and logs:
    steps = [s.strip() for s in logs.split("\n") if s.strip()]

    try:
        sip.anchor(intent)
        guard.anchor(intent)

        results = [sip.observe(s) for s in steps]
        drifts = [r.drift for r in results]
        decisions = [guard.check(s) for s in steps]

        avg_drift = float(np.mean(drifts)) if drifts else 0.0
        peak_drift = float(max(drifts)) if drifts else 0.0

        # Demo/toy cost model: avg_drift (0..1) represents "waste fraction"
        monthly_cost = avg_drift * cost_per_run * runs

        # =========================
        # RESULTS
        # =========================
        with col_out:
            st.write("### 📊 Results")

            col1, col2 = st.columns(2)

            col1.metric("Avg Goal Drift", f"{avg_drift * 100:.1f}%")

            col2.metric("Peak Drift", f"{peak_drift * 100:.1f}%")

            # STATUS LOGIC — aligned with SIP threshold
            # Warning zone spans threshold..1.5×threshold; above that is critical
            if avg_drift <= threshold:
                status = "✅ Healthy"
                msg = "Your AI is aligned (avg drift is within the threshold)."
            elif avg_drift <= min(1.0, threshold * 1.5):
                status = "⚠️ Warning"
                msg = "Your AI is drifting beyond the threshold. Consider adding guardrails or re-alignment."
            else:
                status = "🚨 Critical"
                msg = "High drift detected. Strong risk of intent loss and wasted compute."

            st.subheader(status)

            st.metric(
                "Estimated Monthly Cost Loss (demo)",
                f"${monthly_cost:.2f}",
                delta="Toy model",
            )

            st.info(msg)

            # =========================
            # CHART
            # =========================
            df = pd.DataFrame(
                {
                    "Step": [r.step for r in results],
                    "Drift Score": [r.drift for r in results],
                    "Aligned": [r.is_aligned for r in results],
                }
            )

            fig = px.line(
                df,
                x="Step",
                y="Drift Score",
                title="AI Goal Drift Over Time",
                markers=True,
            )
            fig.add_hline(y=threshold, line_dash="dash", annotation_text="Threshold")

            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Show step-by-step details"):
                st.dataframe(df, use_container_width=True)

            # =========================
            # GATEKEEPER DECISIONS
            # =========================
            st.subheader("🛡️ Gatekeeper Decision")
            for i, decision in enumerate(decisions):
                if decision["action"] == "REALIGN":
                    st.error(f"Step {i + 1}: 💉 REALIGN TRIGGERED")
                    st.json(decision["payload"])
                elif decision["action"] == "BLOCK":
                    st.error(f"Step {i + 1}: 🚫 BLOCKED (drift {decision['drift']:.4f})")
                elif decision["action"] == "WARN":
                    st.warning(f"Step {i + 1}: ⚠️ WARNING (drift {decision['drift']:.4f})")
                else:
                    st.success(f"Step {i + 1}: ✅ ALLOWED")

    except Exception as e:
        st.error(f"Error: {e}")

# =========================
# 8. FOOTER CTA
# =========================
st.divider()

st.markdown("### 💡 Stop AI waste before it scales.")

st.markdown("📩 Contact: sijangautamx@gmail.com")

st.caption("State Flow Lens | AI Drift Intelligence System")

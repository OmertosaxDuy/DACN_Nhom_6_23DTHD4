import subprocess
import streamlit as st


st.set_page_config(
    page_title="Adaptive Cyber Deception",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Adaptive Cyber Deception")
st.caption("Hybrid AI Agent + Cowrie Honeypot")

src_ip = st.text_input(
    "Attacker IP",
    value="192.168.255.130",
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Attacker",
        src_ip,
    )

with col2:
    st.metric(
        "AI Model",
        "Qwen3 1.7B",
    )

with col3:
    st.metric(
        "Agent Mode",
        "Hybrid",
    )

st.divider()

if st.button(
    "▶ Run AI Agent",
    type="primary",
    use_container_width=True,
):
    with st.spinner("AI Agent is analyzing telemetry..."):
        result = subprocess.run(
            [
                "python",
                "agent/test_hybrid_agent.py",
            ],
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        st.success("Agent cycle completed")

        output = result.stdout

        if '"level": "enhanced"' in output:
            monitoring = "ENHANCED"
        elif '"level": "normal"' in output:
            monitoring = "NORMAL"
        else:
            monitoring = "UNKNOWN"

        if '"recommended_action": "update_artifact"' in output:
            action = "UPDATE ARTIFACT"
        elif '"recommended_action": "increase_monitoring"' in output:
            action = "INCREASE MONITORING"
        elif '"recommended_action": "observe_only"' in output:
            action = "OBSERVE ONLY"
        else:
            action = "UNKNOWN"

        if '"risk_level": "high"' in output:
            risk = "HIGH"
        elif '"risk_level": "medium"' in output:
            risk = "MEDIUM"
        else:
            risk = "LOW / UNKNOWN"

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Monitoring",
                monitoring,
            )

        with c2:
            st.metric(
                "Risk",
                risk,
            )

        with c3:
            st.metric(
                "Final Action",
                action,
            )

        st.subheader("Agent Output")

        st.code(
            output,
            language="text",
        )

    else:
        st.error("Agent execution failed")

        st.code(
            result.stderr,
            language="text",
        )

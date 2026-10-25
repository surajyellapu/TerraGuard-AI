"""Beginner-friendly Streamlit UI for TerraGuard AI Phase 1.

Uses the existing analyze() function and build_incident_brief().
Does not integrate or claim Zetaris, Meterless, Nightshift, or NVIDIA.
"""

import json
from pathlib import Path

import streamlit as st

from src.analyzer import analyze
from src.brief import build_incident_brief
from src.zetaris_connector import load_sample_flood_evidence


def main():
    st.set_page_config(
        page_title="TerraGuard AI — Incident Brief",
        page_icon=None,
        layout="centered",
    )

    st.title("TerraGuard AI")
    st.caption("Team DisasterX · Phase 1 demo")

    st.error(
        "SIMULATED SAMPLE DATA — This is a demonstration only. "
        "It is not verified real-world disaster information and "
        "does not confirm a flood."
    )

    st.write(
        "This app loads the local sample flood evidence file, runs the "
        "existing rule-based analyzer, and shows a human-readable "
        "incident brief."
    )

    if st.button("Load sample evidence and run analysis", type="primary"):
            observations = load_sample_flood_evidence()
            analysis = analyze(observations)
            brief = build_incident_brief(observations, analysis)

        st.session_state["observations"] = observations
        st.session_state["analysis"] = analysis
        st.session_state["brief"] = brief

    observations = st.session_state.get("observations")
    analysis = st.session_state.get("analysis")
    brief = st.session_state.get("brief")

    if observations is None or analysis is None or brief is None:
        st.info(
            "Click the button above to load "
            "`sample_flood_evidence.json` and generate a brief."
        )
        return

    st.subheader("Evidence table")
    st.caption("All rows below are simulated sample data.")
    table_rows = []
    for item in observations:
        table_rows.append({
            "ID": item.get("id", ""),
            "Location": item.get("location", ""),
            "Source": item.get("source", ""),
            "Reported at": item.get("reported_at", ""),
            "Claim": item.get("claim", ""),
            "Water level (m)": item.get("water_level_m", ""),
            "Rainfall (mm)": item.get("rainfall_mm", ""),
            "Status": item.get("status", "sample_data"),
        })
    st.dataframe(table_rows, use_container_width=True)

    st.subheader("Analyzer summary")
    st.write(f"Observations reviewed: **{analysis.get('observation_count')}**")
    if "valid_timestamped_observations" in analysis:
        st.write(
            "Valid timestamped observations: "
            f"**{analysis['valid_timestamped_observations']}**"
        )
    st.write(f"Assessment: **{analysis.get('assessment')}**")

    st.subheader("Findings")
    findings = analysis.get("findings", [])
    if not findings:
        st.write("No automated findings were flagged.")
    else:
        for finding in findings:
            finding_type = finding.get("type", "unknown")
            message = finding.get("message", "")
            st.markdown(f"- **{finding_type}**: {message}")

    st.subheader("Incident brief")
    st.code(brief, language=None)

    st.download_button(
        label="Download incident brief (.txt)",
        data=brief,
        file_name="terraguard_incident_brief.txt",
        mime="text/plain",
    )

    st.divider()
    st.caption(
        "Phase 1 uses local sample JSON and the existing Python analyzer only. "
        "No external data-platform or model integrations are claimed here."
    )


if __name__ == "__main__":
    main()

"""Beginner-friendly Streamlit UI for TerraGuard AI Phase 1.

Uses the existing analyze() function and build_incident_brief().
Includes sample flood evidence analysis, an optional AI review draft,
and H-MEM evidence memory.
"""

import json
from pathlib import Path

import streamlit as st

from src.analyzer import analyze
from src.brief import build_incident_brief
from src.zetaris_connector import load_sample_flood_evidence
from src.hmem_client import (
    add_evidence,
    add_structured_evidence,
    search_evidence,
)
from src.nightshift_client import generate_review_draft

DATA_FILE = Path(__file__).resolve().parent / "sample_flood_evidence.json"


def load_sample_observations():
    with DATA_FILE.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


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

    # Load and analyze sample evidence.
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

    # Evidence table.
    st.subheader("Evidence table")
    st.caption("All rows below are simulated sample data.")

    table_rows = []
    for item in observations:
        table_rows.append(
            {
                "ID": item.get("id", ""),
                "Location": item.get("location", ""),
                "Source": item.get("source", ""),
                "Reported at": item.get("reported_at", ""),
                "Claim": item.get("claim", ""),
                "Water level (m)": item.get("water_level_m", ""),
                "Rainfall (mm)": item.get("rainfall_mm", ""),
                "Status": item.get("status", "sample_data"),
            }
        )

    st.dataframe(table_rows, use_container_width=True)

    # Analyzer summary.
    st.subheader("Analyzer summary")
    st.write(
        f"Observations reviewed: **{analysis.get('observation_count')}**"
    )

    if "valid_timestamped_observations" in analysis:
        st.write(
            "Valid timestamped observations: "
            f"**{analysis['valid_timestamped_observations']}**"
        )

    st.write(f"Assessment: **{analysis.get('assessment')}**")

    # Findings.
    st.subheader("Findings")
    findings = analysis.get("findings", [])

    if not findings:
        st.write("No automated findings were flagged.")
    else:
        for finding in findings:
            finding_type = finding.get("type", "unknown")
            message = finding.get("message", "")
            st.markdown(f"- **{finding_type}**: {message}")

    # Incident brief.
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
        "Phase 1 uses local sample JSON and the existing Python analyzer. "
        "External data-platform and model integrations must be verified separately."
    )

    # AI-assisted reviewer draft.
    st.divider()
    st.subheader("AI-assisted reviewer draft")

    st.caption(
        "Optional AI-generated text for human review only. "
        "Sample evidence is simulated and is not verified real-world information."
    )

    if st.button("Generate AI review draft"):
        context = (
            "Evidence observations:\n"
            f"{json.dumps(observations, indent=2)}\n\n"
            "Analyzer results:\n"
            f"{json.dumps(analysis, indent=2)}\n\n"
            f"Current incident brief:\n{brief}"
        )

        with st.spinner("Requesting AI draft..."):
            draft = generate_review_draft(context)

        st.session_state["ai_review_draft"] = draft

    ai_review_draft = st.session_state.get("ai_review_draft")

    if ai_review_draft:
        st.markdown("**AI draft — requires human review**")
        st.write(ai_review_draft)
    # Structured sample evidence storage.
    st.subheader("Store Structured Evidence")

    st.caption(
        "Use the existing sample evidence schema. "
        "Records are not independently verified."
    )

    with st.form("structured_evidence_form"):
        evidence_id = st.text_input(
            "Evidence ID",
            placeholder="e.g. OBS-001",
        )

        evidence_location = st.text_input(
            "Location",
            placeholder="e.g. Riverbend Village",
        )

        evidence_source = st.text_input(
            "Source",
            placeholder="e.g. Sample weather bulletin",
        )

        evidence_reported_at = st.text_input(
            "Reported at",
            placeholder="e.g. 2026-10-22T08:00:00+05:30",
        )

        evidence_claim = st.text_area(
            "Observation claim",
            placeholder="Describe the sample observation",
        )

        evidence_status = st.selectbox(
            "Evidence status",
            options=["sample_data", "unverified"],
        )

        evidence_metric_type = st.selectbox(
            "Optional measurement",
            options=["None", "Rainfall (mm)", "Water level (m)"],
        )

        evidence_metric_value = st.text_input(
            "Measurement value",
            placeholder="Enter a number, e.g. 50",
            key="evidence_metric_value_input",
        )

        structured_submitted = st.form_submit_button(
            "Store structured evidence in H-MEM"
        )

    if structured_submitted:
        if not all(
            value.strip()
            for value in (
                evidence_id,
                evidence_location,
                evidence_source,
                evidence_reported_at,
                evidence_claim,
            )
        ):
            st.warning("Please complete all required evidence fields.")
        else:
            evidence_record = {
                "id": evidence_id.strip(),
                "location": evidence_location.strip(),
                "source": evidence_source.strip(),
                "reported_at": evidence_reported_at.strip(),
                "claim": evidence_claim.strip(),
                "status": evidence_status,
            }

            if evidence_metric_type != "None":
                try:
                    metric_value = float(evidence_metric_value)

                    if metric_value < 0:
                        raise ValueError("Measurement cannot be negative.")

                    if evidence_metric_type == "Rainfall (mm)":
                        evidence_record["rainfall_mm"] = metric_value
                    else:
                        evidence_record["water_level_m"] = metric_value

                except ValueError:
                    st.error(
                        "Enter a valid, non-negative number for the measurement."
                    )
                    st.stop()

            try:
                result = add_structured_evidence(evidence_record)
                st.success(
                    f"Structured evidence stored. "
                    f"Memory ID: {result['memoryId']}"
                )
                st.json(evidence_record)
                st.caption(
                    result.get(
                        "notice",
                        "Stored sample evidence; not independently verified.",
                    )
                )
            except Exception as error:
                st.error(f"Could not store structured evidence: {error}")

    st.divider()
    # H-MEM evidence memory.
    st.divider()
    st.subheader("H-MEM Evidence Memory")

    st.warning(
        "Stored notes are unverified and must not be treated as confirmation "
        "of a real-world flood."
    )

    with st.form("hmem_add_form"):
        memory_content = st.text_area(
            "Evidence note",
            placeholder="Enter a simulated observation or evidence note",
        )

        memory_source = st.text_input(
            "Source",
            placeholder="e.g. TerraGuard simulated test data",
        )

        add_submitted = st.form_submit_button("Store note in H-MEM")

    if add_submitted:
        if memory_content.strip() and memory_source.strip():
            try:
                result = add_evidence(memory_content, memory_source)
                st.success(f"Note stored. Memory ID: {result['memoryId']}")
                st.caption(
                    result.get("notice", "Stored note is unverified.")
                )
            except Exception as error:
                st.error(f"Could not store note: {error}")
        else:
            st.warning("Please enter both an evidence note and a source.")

    # Search H-MEM.
    with st.form("hmem_search_form"):
        memory_query = st.text_input(
            "Search stored notes",
            placeholder="e.g. simulated water level",
        )

        search_submitted = st.form_submit_button("Search H-MEM")

    if search_submitted:
        if memory_query.strip():
            try:
                result = search_evidence(memory_query)
                memories = result.get("memories", [])

                if memories:
                    for memory in memories:
                        st.markdown(f"**Memory ID:** {memory['id']}")
                        st.write(f"**Source:** {memory['source']}")
                        st.write(f"**Note:** {memory['content']}")
                        st.write(
                            f"**Relevance:** {memory['relevance']:.3f}"
                        )
                        st.divider()
                else:
                    st.info("No matching notes were found.")

                st.caption(
                    "Retrieved notes are unverified and do not confirm a flood."
                )

            except Exception as error:
                st.error(f"Could not search H-MEM: {error}")
        else:
            st.warning("Please enter a search query.")


if __name__ == "__main__":
    main()
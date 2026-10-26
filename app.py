"""
Beginner-friendly Streamlit UI for TerraGuard AI Phase 1.

Uses the existing analyze() function and build_incident_brief().
Includes sample flood evidence analysis, optional AI review draft,
and H-MEM evidence memory, with a glass-style dashboard design.
"""

import base64
import json
import math
from datetime import datetime
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


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "sample_flood_evidence.json"
# Use the background image already present in your assets folder.
# The app supports common filename variations so you do not need to rename it.
ASSETS_DIR = ROOT / "assets"
BACKGROUND_CANDIDATES = [
    ASSETS_DIR / "terraguard_scene.png",
    ASSETS_DIR / "terraguard_background.png",
    ASSETS_DIR / "terraguard_background.png.png",
    ASSETS_DIR / "terraguard_scenne.png",
]


def load_sample_observations():
    """Load the bundled sample JSON file."""
    with DATA_FILE.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def apply_custom_design():
    """Apply a scenic background and translucent glass-style UI."""
    background_css = "background-color: #061321;"
    background_path = next(
        (candidate for candidate in BACKGROUND_CANDIDATES if candidate.is_file()),
        None,
    )
    # Also accept any PNG/JPG/WebP placed inside assets/.
    if background_path is None and ASSETS_DIR.is_dir():
        background_path = next(
            (candidate for candidate in ASSETS_DIR.iterdir()
             if candidate.is_file() and candidate.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}),
            None,
        )

    if background_path is not None:
        try:
            encoded_image = base64.b64encode(
                background_path.read_bytes()
            ).decode("utf-8")
            background_css = f"""
                background-image:
                    linear-gradient(
                        rgba(2, 13, 28, 0.36),
                        rgba(2, 13, 28, 0.48)
                    ),
                    url("data:image/png;base64,{encoded_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            """
        except OSError:
            pass

    st.markdown(
        f"""
        <style>
        .stApp {{
            {background_css}
            background-color: #061321;
        }}

        [data-testid="stHeader"] {{
            background: rgba(3, 15, 29, 0.55);
        }}

        .block-container {{
            max-width: 1550px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(3, 17, 34, 0.82);
            border-right: 1px solid rgba(65, 224, 255, 0.55);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }}

        /* ===== GLASS SIDEBAR NAVIGATION ===== */
        [data-testid="stSidebar"] {{
            background: linear-gradient(
                180deg,
                rgba(3, 18, 36, 0.92),
                rgba(4, 31, 52, 0.86)
            ) !important;
            border-right: 1px solid rgba(65, 224, 255, 0.65);
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] > div {{
            gap: 8px;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label {{
            display: flex !important;
            align-items: center;
            padding: 11px 12px !important;
            margin: 3px 0;
            border: 1px solid rgba(75, 210, 255, 0.24);
            border-radius: 12px;
            background: rgba(15, 55, 82, 0.48);
            transition: all 0.25s ease;
            cursor: pointer;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label p {{
            color: #e3f6ff !important;
            font-size: 14px !important;
            font-weight: 650 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
            background: rgba(0, 174, 220, 0.28) !important;
            border-color: rgba(65, 224, 255, 0.9);
            transform: translateX(3px);
            box-shadow: 0 0 16px rgba(0, 205, 255, 0.18);
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] input {{
            accent-color: #35e7ff !important;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: #f5fcff !important;
            text-shadow: 0 0 12px rgba(65, 224, 255, 0.15);
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(65, 224, 255, 0.25);
        }}

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: #c9e7f7;
        }}

        .tg-hero {{
            position: relative;
            overflow: hidden;
            padding: 34px;
            margin: 8px 0 22px 0;
            border-radius: 22px;
            border: 1px solid rgba(65, 224, 255, 0.72);
            background: rgba(3, 24, 44, 0.48);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.30),
                        inset 0 0 24px rgba(65, 224, 255, 0.07);
        }}

        .tg-eyebrow {{
            color: #56edff;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 3px;
            text-transform: uppercase;
        }}

        .tg-title {{
            color: #ffffff;
            font-size: clamp(38px, 5vw, 64px);
            font-weight: 900;
            line-height: 1.12;
            margin: 14px 0 8px 0;
            text-shadow: 0 2px 24px rgba(0, 0, 0, 0.55);
        }}

        .tg-title span {{
            color: #42e8f5;
            text-shadow: 0 0 22px rgba(66, 232, 245, 0.58);
        }}

        .tg-subtitle {{
            color: #e1f5ff;
            font-size: 16px;
            line-height: 1.75;
            max-width: 900px;
        }}

        .tg-pill {{
            display: inline-block;
            margin: 13px 8px 0 0;
            padding: 9px 14px;
            border: 1px solid rgba(65, 224, 255, 0.7);
            border-radius: 25px;
            background: rgba(0, 120, 160, 0.30);
            color: #e5fcff;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.4px;
        }}

        .tg-section {{
            color: #ffffff;
            font-size: 23px;
            font-weight: 800;
            margin: 18px 0 10px 0;
        }}

        .tg-section span {{
            color: #51e7f6;
        }}

        [data-testid="stMetric"] {{
            padding: 18px;
            border-radius: 16px;
            border: 1px solid rgba(65, 224, 255, 0.58);
            background: rgba(3, 24, 44, 0.67);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.20);
            transition: transform 0.22s ease, box-shadow 0.22s ease;
        }}

        [data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 0 22px rgba(65, 224, 255, 0.25);
        }}

        [data-testid="stMetricLabel"] {{
            color: #d5efff !important;
        }}

        [data-testid="stMetricValue"] {{
            color: #53edff !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(3, 24, 44, 0.64);
            border: 1px solid rgba(65, 224, 255, 0.45);
            border-radius: 16px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }}

        [data-testid="stExpander"] {{
            background: rgba(3, 24, 44, 0.70);
            border: 1px solid rgba(65, 224, 255, 0.42);
            border-radius: 12px;
        }}

        div.stButton > button,
        div.stDownloadButton > button,
        div.stFormSubmitButton > button {{
            min-height: 43px;
            color: #ffffff;
            font-weight: 750;
            border: 1px solid #48e8ff;
            border-radius: 10px;
            background: linear-gradient(
                110deg,
                rgba(0, 105, 160, 0.97),
                rgba(0, 180, 200, 0.92)
            );
            transition: all 0.2s ease;
        }}

        div.stButton > button:hover,
        div.stDownloadButton > button:hover,
        div.stFormSubmitButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 0 22px rgba(65, 224, 255, 0.40);
            border-color: #ffffff;
            color: #ffffff;
        }}

        h1, h2, h3, h4 {{
            color: #f4fbff !important;
        }}

        p, label, [data-testid="stMarkdownContainer"] {{
            color: #e1effa;
        }}

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {{
            color: #ffffff !important;
            background: rgba(3, 18, 33, 0.86) !important;
            border: 1px solid rgba(65, 224, 255, 0.50) !important;
            border-radius: 9px !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid rgba(65, 224, 255, 0.45);
            border-radius: 12px;
            overflow: hidden;
        }}

        .tg-footer {{
            margin-top: 28px;
            padding: 18px;
            border-top: 1px solid rgba(65, 224, 255, 0.35);
            color: #d1e7f5;
            text-align: center;
            font-size: 12px;
        }}

        @media (prefers-reduced-motion: reduce) {{
            [data-testid="stMetric"],
            div.stButton > button {{
                transition: none;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="TerraGuard AI — Incident Brief",
        page_icon="🌊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_design()

    # Sidebar navigation and project context
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding:12px 0 20px 0;">
                <div style="font-size:42px;">🌊</div>
                <div style="font-size:25px;font-weight:900;color:#ffffff;">
                    TerraGuard <span style="color:#42e8f5;">AI</span>
                </div>
                <div style="font-size:10px;letter-spacing:3px;color:#56edff;">
                    DISASTER INTELLIGENCE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        page = st.radio(
            "Navigation",
            [
                "Home",
                "Evidence Analysis",
                "Incident Brief",
                "AI Review",
                "H-MEM Memory",
                "Integrations",
                "About",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("### 🌍 Our Mission")
        st.write(
            "Turning evidence into better-informed decisions for safer, "
            "more resilient communities."
        )
        st.divider()
        st.caption("TEAM DISASTERX")
        st.caption("Phase 1 prototype · Human oversight required")

    # Main hero header
    st.markdown(
        """
        <div class="tg-hero">
            <div class="tg-eyebrow">TEAM DISASTERX · DISASTER INTELLIGENCE</div>
            <div class="tg-title">TerraGuard <span>AI</span></div>
            <div class="tg-subtitle">
                Disaster intelligence for a safer tomorrow.<br>
                Bring observations together, inspect potential findings,
                and create clear incident briefs with human oversight.
            </div>
            <div>
                <span class="tg-pill">◈ EVIDENCE REVIEW</span>
                <span class="tg-pill">♧ HUMAN OVERSIGHT</span>
                <span class="tg-pill">✓ TRACEABLE FINDINGS</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.error(
        "**SIMULATED SAMPLE DATA** — This demonstration does not establish "
        "that a flood or other disaster is occurring. Verify information "
        "against trusted sources before making real-world decisions."
    )

    st.markdown('<div class="tg-section"><span>◈</span> Mission Workspace</div>',
                unsafe_allow_html=True)
    st.write(
        "Load the bundled sample observations to run the existing "
        "rule-based analyzer."
    )

    if st.button("▶  Load sample evidence and run analysis", type="primary"):
        try:
            observations = load_sample_flood_evidence()
            analysis = analyze(observations)
            brief = build_incident_brief(observations, analysis)
            st.session_state["observations"] = observations
            st.session_state["analysis"] = analysis
            st.session_state["brief"] = brief
            # Avoid displaying a stale AI draft for newly loaded evidence.
            st.session_state.pop("ai_review_draft", None)
            st.success("Sample evidence loaded and analysis completed.")
        except Exception as error:
            st.error(f"Could not load or analyze sample evidence: {error}")

    observations = st.session_state.get("observations")
    analysis = st.session_state.get("analysis")
    brief = st.session_state.get("brief")

    if observations is None or analysis is None or brief is None:
        st.info(
            "Select **Load sample evidence and run analysis** to populate "
            "the dashboard. Until then, the metrics below remain at zero."
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric("Observations reviewed", 0)
        metric_cols[1].metric("Timestamped observations", 0)
        metric_cols[2].metric("Findings flagged", 0)
        observations = None
        analysis = None
        brief = None
    else:
        valid_timestamps = analysis.get(
            "valid_timestamped_observations",
            analysis.get("timestamped_observations", 0),
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Observations reviewed",
            analysis.get("observation_count", len(observations)),
        )
        metric_cols[1].metric("Timestamped observations", valid_timestamps)
        metric_cols[2].metric(
            "Findings flagged", len(analysis.get("findings", []))
        )

    # Navigation views keep all functions available without deleting features.
    if page in ("Home", "Evidence Analysis"):
        st.markdown(
            '<div class="tg-section"><span>▤</span> Evidence Table</div>',
            unsafe_allow_html=True,
        )
        st.caption("All rows below are simulated sample data.")
        if observations is not None:
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
            st.dataframe(table_rows, use_container_width=True, hide_index=True)
        else:
            st.info("No data loaded yet. Click the load button above.")

        st.markdown(
            '<div class="tg-section"><span>⌕</span> Analyzer Findings</div>',
            unsafe_allow_html=True,
        )
        if analysis is None:
            st.info("Run analysis to see findings.")
        else:
            findings = analysis.get("findings", [])
            if not findings:
                st.success("No automated findings were flagged.")
            else:
                for finding in findings:
                    finding_type = finding.get("type", "unknown")
                    message = finding.get("message", "")
                    st.warning(f"**{finding_type}** — {message}")

        if analysis is not None:
            with st.expander("View analyzer summary"):
                st.write(
                    "Observations reviewed: "
                    f"**{analysis.get('observation_count', len(observations))}**"
                )
                if "valid_timestamped_observations" in analysis:
                    st.write(
                        "Valid timestamped observations: "
                        f"**{analysis['valid_timestamped_observations']}**"
                    )
                st.write(f"Assessment: **{analysis.get('assessment')}**")

    if page in ("Home", "Incident Brief"):
        st.markdown(
            '<div class="tg-section"><span>▤</span> Incident Brief</div>',
            unsafe_allow_html=True,
        )
        if brief is None:
            st.info("Run the sample analysis to generate an incident brief.")
        else:
            st.text_area("Human-readable incident brief", brief, height=220)
            st.download_button(
                label="⬇ Download incident brief (.txt)",
                data=brief,
                file_name="terraguard_incident_brief.txt",
                mime="text/plain",
            )

    if page in ("Home", "AI Review"):
        st.markdown(
            '<div class="tg-section"><span>✦</span> AI-Assisted Reviewer Draft</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Optional AI-generated text for human review only. "
            "Sample evidence is simulated and is not verified real-world information."
        )
        if observations is None or analysis is None or brief is None:
            st.info("Load sample evidence and run analysis before requesting an AI draft.")
        elif st.button("✦ Generate AI review draft"):
            context = (
                "Evidence observations:\n"
                f"{json.dumps(observations, indent=2)}\n\n"
                "Analyzer results:\n"
                f"{json.dumps(analysis, indent=2)}\n\n"
                f"Current incident brief:\n{brief}"
            )
            with st.spinner("Requesting AI draft..."):
                try:
                    draft = generate_review_draft(context)
                    st.session_state["ai_review_draft"] = draft
                except Exception as error:
                    st.error(
                        "Could not generate an AI review draft. Check the "
                        f"Nightshift configuration. Details: {error}"
                    )
        ai_review_draft = st.session_state.get("ai_review_draft")
        if ai_review_draft:
            st.markdown("**AI draft — requires human review**")
            st.write(ai_review_draft)

    if page in ("Home", "Evidence Analysis", "H-MEM Memory"):
        st.markdown(
            '<div class="tg-section"><span>＋</span> Store Structured Evidence</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Use the existing sample evidence schema. Records are not independently verified."
        )

        with st.form("structured_evidence_form"):
            evidence_id = st.text_input("Evidence ID", placeholder="e.g. OBS-001")
            evidence_location = st.text_input(
                "Location", placeholder="e.g. Riverbend Village"
            )
            evidence_source = st.text_input(
                "Source", placeholder="e.g. Sample weather bulletin"
            )
            evidence_reported_at = st.text_input(
                "Reported at", placeholder="e.g. 2026-10-22T08:00:00+05:30"
            )
            evidence_claim = st.text_area(
                "Observation claim", placeholder="Describe the sample observation"
            )
            evidence_status = st.selectbox(
                "Evidence status", options=["sample_data", "unverified"]
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
            required_values = {
                "Evidence ID": evidence_id,
                "Location": evidence_location,
                "Source": evidence_source,
                "Reported at": evidence_reported_at,
                "Observation claim": evidence_claim,
            }
            missing_fields = [
                label for label, value in required_values.items()
                if not value.strip()
            ]

            if missing_fields:
                st.warning(
                    "Please complete all required evidence fields: "
                    + ", ".join(missing_fields) + "."
                )
            else:
                try:
                    reported_at = datetime.fromisoformat(
                        evidence_reported_at.strip().replace("Z", "+00:00")
                    )
                except ValueError:
                    st.error(
                        "Invalid timestamp. Use ISO 8601 format, for example "
                        "2026-10-22T08:00:00+05:30."
                    )
                else:
                    evidence_record = {
                        "id": evidence_id.strip(),
                        "location": evidence_location.strip(),
                        "source": evidence_source.strip(),
                        "reported_at": reported_at.isoformat(),
                        "claim": evidence_claim.strip(),
                        "status": evidence_status,
                    }

                    valid_measurement = True
                    if evidence_metric_type != "None":
                        try:
                            metric_value = float(evidence_metric_value)
                            if not math.isfinite(metric_value) or metric_value < 0:
                                raise ValueError
                            if evidence_metric_type == "Rainfall (mm)":
                                evidence_record["rainfall_mm"] = metric_value
                            else:
                                evidence_record["water_level_m"] = metric_value
                        except ValueError:
                            valid_measurement = False
                            st.error(
                                "Enter a valid, finite, non-negative number "
                                "for the measurement."
                            )

                    if valid_measurement:
                        try:
                            result = add_structured_evidence(evidence_record)
                            st.success(
                                "Structured evidence stored. Memory ID: "
                                f"{result['memoryId']}"
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

    if page in ("Home", "H-MEM Memory"):
        st.markdown(
            '<div class="tg-section"><span>◉</span> H-MEM Evidence Memory</div>',
            unsafe_allow_html=True,
        )
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
                "Source", placeholder="e.g. TerraGuard simulated test data"
            )
            add_submitted = st.form_submit_button("Store note in H-MEM")

        if add_submitted:
            if memory_content.strip() and memory_source.strip():
                try:
                    result = add_evidence(
                        memory_content.strip(), memory_source.strip()
                    )
                    st.success(f"Note stored. Memory ID: {result['memoryId']}")
                    st.caption(result.get("notice", "Stored note is unverified."))
                except Exception as error:
                    st.error(f"Could not store note: {error}")
            else:
                st.warning("Please enter both an evidence note and a source.")

        with st.form("hmem_search_form"):
            memory_query = st.text_input(
                "Search stored notes", placeholder="e.g. simulated water level"
            )
            search_submitted = st.form_submit_button("Search H-MEM")

        if search_submitted:
            if memory_query.strip():
                try:
                    result = search_evidence(memory_query.strip())
                    memories = result.get("memories", [])
                    if memories:
                        for memory in memories:
                            st.markdown(f"**Memory ID:** {memory.get('id', '')}")
                            st.write(f"**Source:** {memory.get('source', '')}")
                            st.write(f"**Note:** {memory.get('content', '')}")
                            relevance = memory.get("relevance")
                            if isinstance(relevance, (int, float)):
                                st.write(f"**Relevance:** {relevance:.3f}")
                            else:
                                st.write(f"**Relevance:** {relevance}")
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

    if page == "Integrations":
        st.markdown(
            '<div class="tg-section"><span>⇄</span> Integrations</div>',
            unsafe_allow_html=True,
        )
        st.info(
            "**Zetaris connector:** The project includes a sample-evidence loader. "
            "Verify any live data-platform connection separately."
        )
        st.info(
            "**H-MEM:** Structured evidence and notes can be stored/searched "
            "through the configured H-MEM client. Persistence depends on its configuration."
        )
        st.info(
            "**Nightshift:** AI review is optional and requires valid endpoint/model "
            "configuration. A successful local app launch alone does not verify live connectivity."
        )

    if page == "About":
        st.markdown(
            '<div class="tg-section"><span>ⓘ</span> About TerraGuard AI</div>',
            unsafe_allow_html=True,
        )
        st.write(
            "TerraGuard AI is a Phase 1 disaster-intelligence prototype for "
            "organizing observations, running a rule-based analysis, and drafting "
            "a human-readable incident brief."
        )
        st.warning(
            "This is a prototype. Sample observations may be simulated; outputs "
            "must be reviewed by people and checked against trusted sources."
        )

    st.markdown(
        """
        <div class="tg-footer">
            TERRAGUARD AI · TEAM DISASTERX · PHASE 1 PROTOTYPE<br>
            Evidence review support only — human oversight required.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

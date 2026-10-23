"""Build a human-readable incident brief from analyzer findings.

This module does not change analyze() rules. It only formats existing output.
All sample-data briefs must stay clearly labeled as simulated.
"""

FINDING_LABELS = {
    "invalid_observation": "Invalid observation",
    "stale_evidence": "Stale evidence",
    "water_level_disagreement": "Water-level disagreement",
}


def build_incident_brief(observations, analysis):
    """Return a plain-text incident brief for human review.

    Args:
        observations: list of evidence dicts (may be sample/simulated).
        analysis: dict returned by analyze().

    Returns:
        A multi-line string suitable for display or copy/export.
    """
    lines = [
        "TerraGuard AI — Incident Brief",
        "=" * 40,
        "",
        "DATA STATUS: SIMULATED SAMPLE DATA",
        "This brief is for demonstration only.",
        "It is not verified real-world disaster information.",
        "It must not replace official alerts or emergency services.",
        "",
        "Summary",
        "-" * 40,
    ]

    observation_count = analysis.get("observation_count", len(observations))
    valid_count = analysis.get("valid_timestamped_observations")
    findings = analysis.get("findings", [])
    assessment = analysis.get("assessment", "No assessment available.")

    lines.append(f"Observations reviewed: {observation_count}")
    if valid_count is not None:
        lines.append(f"Valid timestamped observations: {valid_count}")
    lines.append(f"Findings flagged: {len(findings)}")
    lines.append(f"Assessment: {assessment}")
    lines.append("")

    locations = sorted({
        item.get("location")
        for item in observations
        if item.get("location")
    })
    if locations:
        lines.append("Location(s): " + ", ".join(locations))
        lines.append("")

    lines.append("Evidence items")
    lines.append("-" * 40)
    if not observations:
        lines.append("No evidence items provided.")
    else:
        for item in observations:
            evidence_id = item.get("id", "unknown")
            source = item.get("source", "unknown source")
            reported_at = item.get("reported_at", "unknown time")
            claim = item.get("claim", "No claim provided.")
            status = item.get("status", "unlabeled")
            lines.append(
                f"- {evidence_id} | {source} | {reported_at} | "
                f"status={status}"
            )
            lines.append(f"  Claim: {claim}")
            if "water_level_m" in item:
                lines.append(f"  Water level: {item['water_level_m']} m")
            if "rainfall_mm" in item:
                lines.append(f"  Rainfall: {item['rainfall_mm']} mm")
    lines.append("")

    lines.append("Findings for human review")
    lines.append("-" * 40)
    if not findings:
        lines.append("No automated findings were flagged.")
    else:
        for index, finding in enumerate(findings, start=1):
            finding_type = finding.get("type", "unknown")
            label = FINDING_LABELS.get(finding_type, finding_type)
            message = finding.get("message", "No message provided.")
            lines.append(f"{index}. {label}")
            lines.append(f"   Message: {message}")

            if "evidence_id" in finding:
                lines.append(f"   Evidence ID: {finding['evidence_id']}")
            if "evidence_ids" in finding:
                ids = ", ".join(str(value) for value in finding["evidence_ids"])
                lines.append(f"   Evidence IDs: {ids}")
            if "age_hours" in finding:
                lines.append(f"   Age (hours vs newest): {finding['age_hours']}")
            if "measurements_m" in finding:
                measurements = ", ".join(
                    str(value) for value in finding["measurements_m"]
                )
                lines.append(f"   Measurements (m): {measurements}")
    lines.append("")

    lines.append("Recommended next step")
    lines.append("-" * 40)
    lines.append(
        "A human reviewer should check stale reports and conflicting "
        "measurements before taking any action."
    )
    lines.append(
        "Remember: simulated sample data does not confirm a flood."
    )
    lines.append("")

    return "\n".join(lines)

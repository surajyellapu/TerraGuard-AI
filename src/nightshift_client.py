"""Optional AI client for TerraGuard AI.

Uses an OpenAI-compatible chat completions endpoint when configured.
A working connection to Nightshift must be configured separately.
"""

import os

import requests


def generate_review_draft(context: str) -> str:
    """Request a reviewer-facing draft from a configured AI endpoint."""

    base_url = os.getenv("NIGHTSHIFT_BASE_URL", "").rstrip("/")
    api_key = os.getenv("NIGHTSHIFT_API_KEY", "")
    model = os.getenv("NIGHTSHIFT_MODEL", "")

    if not base_url or not api_key or not model:
        return (
            "AI draft unavailable: the endpoint, API key, or model is "
            "not configured. TerraGuard's local analysis remains available."
        )

    system_message = (
        "You assist human disaster-response reviewers. Summarize only the "
        "provided information. Do not invent facts, claim a disaster is "
        "confirmed, or make operational decisions. Clearly explain "
        "uncertainty. Treat sample data as simulated, not verified evidence."
    )

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": context,
                    },
                ],
                "temperature": 0.2,
            },
            timeout=30,
        )

        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"]

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
    ) as exc:
        return (
            "AI draft unavailable because the configured endpoint did not "
            f"return a usable response ({type(exc).__name__}). "
            "TerraGuard's local analysis remains available."
        )
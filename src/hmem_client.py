
import json
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_FILE = PROJECT_ROOT / "hmem_bridge.mjs"

TSX_LOADER = (
    PROJECT_ROOT
    / "engines"
    / "hmem"
    / "reference"
    / "node_modules"
    / "tsx"
    / "dist"
    / "loader.mjs"
)


def _run_bridge(*arguments: str) -> dict:
    if not BRIDGE_FILE.is_file():
        raise FileNotFoundError(
            f"H-MEM bridge not found: {BRIDGE_FILE}"
        )

    node_executable = os.environ.get("NODE_EXE") or shutil.which("node")

    if not node_executable:
        raise FileNotFoundError(
            "Node.js was not found. Install Node.js and ensure "
            "the node executable is available on PATH, or set NODE_EXE."
        )

    if not TSX_LOADER.is_file():
        raise FileNotFoundError(
            f"TypeScript loader not found: {TSX_LOADER}. "
            "Install the H-MEM reference dependencies by running "
            "'npm ci' in engines/hmem/reference."
        )

    command = [
        node_executable,
        "--import",
        TSX_LOADER.as_uri(),
        str(BRIDGE_FILE),
        *arguments,
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("H-MEM bridge timed out after 30 seconds.") from error
    except OSError as error:
        raise RuntimeError(
            f"Could not start the Node.js H-MEM bridge: {error}"
        ) from error

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"H-MEM bridge failed: {message}")

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "H-MEM bridge returned invalid JSON."
        ) from error

    if not isinstance(result, dict):
        raise RuntimeError(
            "H-MEM bridge returned an unexpected response type."
        )

    if not result.get("success"):
        raise RuntimeError(
            "H-MEM bridge reported an unsuccessful result."
        )

    return result


def add_evidence(content: str, source: str) -> dict:
    """Store a note labelled as simulated evidence."""
    return _run_bridge("add", content, source)


def search_evidence(query: str) -> dict:
    """Retrieve notes; retrieval does not verify real-world events."""
    return _run_bridge("search", query)


def add_structured_evidence(evidence: dict) -> dict:
    """Validate and store a complete structured evidence record."""
    from datetime import datetime

    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be a dictionary.")

    required_fields = (
        "id",
        "location",
        "source",
        "reported_at",
        "claim",
    )

    for field in required_fields:
        value = evidence.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Evidence field '{field}' must be non-empty text."
            )

    timestamp = evidence["reported_at"].strip()

    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(
            "Evidence field 'reported_at' must use a valid ISO 8601 timestamp."
        ) from error

    try:
        evidence_json = json.dumps(
            evidence,
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Evidence must contain JSON-compatible values."
        ) from error

    return _run_bridge("add-json", evidence_json)
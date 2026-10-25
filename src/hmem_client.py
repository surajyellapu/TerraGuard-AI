import json
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_FILE = PROJECT_ROOT / "hmem_bridge.mjs"

NODE_EXECUTABLE = os.environ.get(
    "NODE_EXE",
    r"C:\Program Files\nodejs\node.exe",
)

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

    if not Path(NODE_EXECUTABLE).is_file():
        raise FileNotFoundError(
            f"Node.js executable not found: {NODE_EXECUTABLE}"
        )

    if not TSX_LOADER.is_file():
        raise FileNotFoundError(
            f"TypeScript loader not found: {TSX_LOADER}"
        )

    command = [
        NODE_EXECUTABLE,
        "--import",
        TSX_LOADER.as_uri(),
        str(BRIDGE_FILE),
        *arguments,
    ]

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"H-MEM bridge failed: {message}")

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "H-MEM bridge returned invalid JSON."
        ) from error

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
    """Store a complete evidence record in H-MEM."""
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be a dictionary.")

    for field in ("id", "claim", "source"):
        if not evidence.get(field):
            raise ValueError(
                f"Evidence is missing required field: {field}"
            )

    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
    )

    return _run_bridge("add-json", evidence_json)
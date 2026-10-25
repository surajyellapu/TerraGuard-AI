import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from src import hmem_client


def test_add_structured_evidence_rejects_missing_required_fields():
    evidence = {
        "id": "OBS-001",
        "claim": "Sample observation",
        "source": "Test source",
    }

    with pytest.raises(ValueError):
        hmem_client.add_structured_evidence(evidence)


def test_add_structured_evidence_rejects_empty_required_fields():
    evidence = {
        "id": "OBS-001",
        "location": "Riverbend",
        "claim": "Sample observation",
        "source": " ",
        "reported_at": "2026-10-26T08:00:00+00:00",
    }

    with pytest.raises(ValueError):
        hmem_client.add_structured_evidence(evidence)


@patch("src.hmem_client.shutil.which", return_value=None)
def test_bridge_reports_missing_node_dependency(mock_which):
    with patch.dict("os.environ", {"NODE_EXE": ""}):
        with pytest.raises(FileNotFoundError, match="Node.js"):
            hmem_client._run_bridge("search", "flood")


@patch("src.hmem_client.subprocess.run")
def test_bridge_reports_process_failure(mock_run):
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="Bridge failed",
    )

    with patch("src.hmem_client.shutil.which", return_value="node"):
        with patch.object(
            hmem_client,
            "TSX_LOADER",
            hmem_client.PROJECT_ROOT / "hmem_bridge.mjs",
        ):
            with pytest.raises(RuntimeError, match="H-MEM bridge failed"):
                hmem_client._run_bridge("search", "flood")


@patch("src.hmem_client.subprocess.run")
def test_bridge_rejects_malformed_json_response(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="not valid JSON",
        stderr="",
    )

    with patch("src.hmem_client.shutil.which", return_value="node"):
        with patch.object(
            hmem_client,
            "TSX_LOADER",
            hmem_client.PROJECT_ROOT / "hmem_bridge.mjs",
        ):
            with pytest.raises(RuntimeError, match="invalid JSON"):
                hmem_client._run_bridge("search", "flood")
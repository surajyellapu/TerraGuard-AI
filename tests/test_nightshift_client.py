import os
from unittest.mock import MagicMock, patch

from src.nightshift_client import generate_review_draft


def test_nightshift_returns_message_when_not_configured():
    with patch.dict(
        os.environ,
        {
            "NIGHTSHIFT_BASE_URL": "",
            "NIGHTSHIFT_API_KEY": "",
            "NIGHTSHIFT_MODEL": "",
        },
        clear=False,
    ):
        result = generate_review_draft("Sample evidence")

    assert "unavailable" in result.lower()
    assert "not configured" in result.lower()


@patch("src.nightshift_client.requests.post")
def test_nightshift_handles_http_error(mock_post):
    import requests

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = (
        requests.HTTPError("Service unavailable")
    )
    mock_post.return_value = mock_response

    with patch.dict(
        os.environ,
        {
            "NIGHTSHIFT_BASE_URL": "https://example.com",
            "NIGHTSHIFT_API_KEY": "test-key",
            "NIGHTSHIFT_MODEL": "test-model",
        },
    ):
        result = generate_review_draft("Sample evidence")

    assert "unavailable" in result.lower()
    assert "human" not in result.lower() or "review" in result.lower()


@patch("src.nightshift_client.requests.post")
def test_nightshift_handles_invalid_json(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"unexpected": "response"}
    mock_post.return_value = mock_response

    with patch.dict(
        os.environ,
        {
            "NIGHTSHIFT_BASE_URL": "https://example.com",
            "NIGHTSHIFT_API_KEY": "test-key",
            "NIGHTSHIFT_MODEL": "test-model",
        },
    ):
        result = generate_review_draft("Sample evidence")

    assert "unavailable" in result.lower()


@patch("src.nightshift_client.requests.post")
def test_nightshift_returns_valid_response(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Human review is required."
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    with patch.dict(
        os.environ,
        {
            "NIGHTSHIFT_BASE_URL": "https://example.com",
            "NIGHTSHIFT_API_KEY": "test-key",
            "NIGHTSHIFT_MODEL": "test-model",
        },
    ):
        result = generate_review_draft("Sample evidence")

    assert result == "Human review is required."
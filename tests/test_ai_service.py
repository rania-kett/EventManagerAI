"""
test_ai_service.py — Gemini AI service and API tests.
"""

from unittest.mock import MagicMock, patch

import pytest

from services.ai_service import AIService, AIServiceError, AIServiceNotConfiguredError


def test_not_configured_raises():
    ai = AIService(api_key="")
    assert ai.is_configured() is False
    with pytest.raises(AIServiceNotConfiguredError):
        ai.generate_event_description("Gala 2026")


def test_empty_title_raises():
    ai = AIService(api_key="test-key")
    with pytest.raises(AIServiceError):
        ai.generate_event_description("   ")


@patch("services.ai_service.genai")
def test_generate_event_description_success(mock_genai):
    mock_client = MagicMock()
    mock_genai.Client.return_value = mock_client
    mock_client.models.generate_content.return_value = MagicMock(
        text="Une soirée exceptionnelle vous attend."
    )

    ai = AIService(api_key="test-key", model="gemini-2.0-flash")
    result = ai.generate_event_description(
        title="Gala Premium",
        location="Casablanca",
        category="Gala",
    )

    assert "exceptionnelle" in result
    mock_genai.Client.assert_called_once_with(api_key="test-key")
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == "gemini-2.0-flash"
    assert "Gala Premium" in call_kwargs["contents"]


def test_ai_generate_route_requires_title(client):
    response = client.post(
        "/events/ai/generate-description",
        json={"title": ""},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


@patch("routes.ai_handlers.build_ai_service")
def test_ai_generate_route_success(mock_build_ai, client):
    mock_instance = MagicMock()
    mock_instance.generate_event_description.return_value = "Description IA générée."
    mock_build_ai.return_value = mock_instance

    response = client.post(
        "/events/ai/generate-description",
        json={"title": "Conférence Tech"},
        headers={"Content-Type": "application/json"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["description"] == "Description IA générée."


def test_add_form_shows_generate_button(client):
    response = client.get("/events/add")
    html = response.data.decode("utf-8")

    assert "Générer la description" in html
    assert "js-generate-description" in html
    assert "ai-generate.js" in html
